#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#

import asyncio
import copy
import gc
import json
import logging
import math
import os
import pickle
import shutil
import socket
import sys
import tempfile
import time
import traceback
import uuid
import warnings
from collections import defaultdict
from contextlib import nullcontext
from enum import IntEnum
from enum import unique
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from pathlib import Path
import sqlite3


import numpy as np
import pandas as pd
import psutil
import torch
from torch.optim.lr_scheduler import LambdaLR
from featrix.neural.lr_timeline import LRTimeline
from torch.profiler import ProfilerActivity
from torch.utils.data import DataLoader
from torch.utils.data import Sampler

from datetime import datetime
from zoneinfo import ZoneInfo

from featrix.neural.data_frame_data_set import collate_tokens
from featrix.neural.data_frame_data_set import SuperSimpleSelfSupervisedDataset
from featrix.neural.dataloader_utils import create_dataloader_kwargs
from featrix.neural.gpu_utils import get_device
from featrix.neural.gpu_utils import (
    is_gpu_available,
    is_cuda_available,
    get_device_type,
    get_gpu_memory_allocated,
    get_gpu_memory_reserved,
    get_max_gpu_memory_allocated,
    get_gpu_device_properties,
    empty_gpu_cache,
    synchronize_gpu,
    set_device_cpu,
    reset_device,
    aggressive_clear_gpu_cache,
    log_gpu_memory,
    log_gpu_memory_detailed,
)
# from featrix.neural.encoders import create_lists_of_a_set_codec
from featrix.neural.encoders import create_scalar_codec
from featrix.neural.encoders import create_set_codec
from featrix.neural.encoders import create_string_codec
from featrix.neural.encoders import create_timestamp_codec
from featrix.neural.encoders import ColumnPredictor
# from featrix.neural.string_codec import set_string_cache_path
from featrix.neural.training_history_db import TrainingHistoryDB
from featrix.neural.encoders import create_vector_codec
from featrix.neural.encoders import FeatrixTableEncoder
from featrix.neural.encoders import ColumnPredictor
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.featrix_token import create_token_batch
from featrix.neural.featrix_token import set_marginal
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.model_config import ColumnType
from featrix.neural.model_config import CurriculumLearningConfig
from featrix.neural.model_config import CurriculumPhaseConfig
from featrix.neural.model_config import FeatrixTableEncoderConfig
from featrix.neural.model_config import JointEncoderConfig
from featrix.neural.model_config import LossFunctionConfig
from featrix.neural.model_config import RelationshipFeatureConfig
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.model_config import SpreadLossConfig
from featrix.neural.scalar_codec import AdaptiveScalarEncoder
from featrix.neural.scalar_codec import ScalarCodec
from featrix.neural.set_codec import SetCodec
from featrix.neural.set_codec import SetEncoder
from featrix.neural.string_codec import StringCodec
from featrix.neural.setlist_codec import ListOfASetEncoder
# from featrix.neural.stopwatch import StopWatch
# from featrix.neural.stopwatch import TimedIterator
from featrix.neural.string_codec import StringEncoder
from featrix.neural.simple_string_cache import _cached_encode
from featrix.neural.vector_codec import VectorEncoder
from featrix.neural.utils import ideal_batch_size
from featrix.neural.embedding_quality import (
    compute_embedding_quality_metrics,
    compare_embedding_spaces
)

# Import configuration management
from featrix.neural.sphere_config import get_d_model as get_default_d_model
from featrix.neural.sphere_config import get_config

# Import job_manager if available (for server environment)
# Tests and local environments may not have this module
try:
    from featrix.lib.job_manager import JobStatus, get_job_output_path
except ModuleNotFoundError:
    # Create minimal stubs for testing
    class JobStatus:
        QUEUED = "queued"
        RUNNING = "running"
        DONE = "done"
        FAILED = "failed"
    
    def get_job_output_path(session_id, job_id, job_type):
        """Minimal stub for testing - returns a basic path."""
        from pathlib import Path
        return Path(f"./featrix_output/{session_id}/{job_type}_{job_id}")

# WeightWatcher tracking is handled by weightwatcher_tracking.py module

# Import DropoutScheduler for dynamic dropout adjustment
from featrix.neural.dropout_scheduler import DropoutScheduler, create_dropout_scheduler

# Import exceptions for training control
from featrix.neural.exceptions import FeatrixTrainingAbortedException, FeatrixOOMRetryException

# from sklearn.model_selection import train_test_split

# Import standardized logging configuration
from featrix.neural.logging_config import configure_logging
configure_logging()

logger = logging.getLogger(__name__)

def _cleanup_dataloader_workers(dataloader, name: str = "DataLoader", expected_workers: int = None):
    """
    Cleanup DataLoader workers by force-killing them.
    
    CRITICAL: Do NOT try to gracefully shutdown workers via _shutdown_workers() or shutdown().
    These methods try to COMMUNICATE with workers via pipes. If a worker is dead (e.g., from OOM),
    the pipe buffer fills up and the shutdown call BLOCKS FOREVER, preventing the process from exiting.
    
    This caused stuck processes holding 96GB+ GPU memory for hours.
    
    The safe approach: just SIGKILL them immediately. Workers don't have important state to save.
    
    Args:
        dataloader: The DataLoader instance to cleanup (can be None)
        name: Descriptive name for logging
        expected_workers: Expected number of workers (for sanity check). If we find > 2x this,
                          emit a loud warning because something is spawning workers out of control.
    """
    if dataloader is None:
        return
    
    # DO NOT call _shutdown_workers() or shutdown() - they communicate via pipes and can block forever!
    # Just delete the reference and let psutil force-kill any remaining workers.
    
    # Step 1: Delete the dataloader reference to help garbage collection
    try:
        del dataloader
        logger.debug(f"   ✅ Deleted {name} reference")
    except:
        pass
    
    # Step 2: FORCE KILL any remaining worker processes using psutil - no graceful shutdown!
    # This is critical because persistent_workers=True keeps workers alive even after
    # DataLoader deletion, causing accumulation over time (especially during checkpoint resume)
    try:
        import psutil
        import os
        current_pid = os.getpid()
        parent_process = psutil.Process(current_pid)
        children = parent_process.children(recursive=True)
        
        # Find DataLoader worker processes (Python child processes)
        worker_pids = []
        total_worker_rss = 0.0
        for child in children:
            try:
                cmdline = ' '.join(child.cmdline()[:3]) if child.cmdline() else ''
                # DataLoader workers are typically Python processes spawned by the parent
                if 'python' in cmdline.lower() or 'torch' in cmdline.lower():
                    mem_info = child.memory_info()
                    rss_gb = mem_info.rss / (1024**3)
                    # Workers typically use 500-700MB each
                    if 0.3 < rss_gb < 2.0:  # Reasonable range for a worker
                        worker_pids.append((child.pid, rss_gb))
                        total_worker_rss += rss_gb
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if worker_pids:
            # RUNAWAY WORKER DETECTION: If we find way more workers than expected, something is very wrong
            if expected_workers is not None and len(worker_pids) > expected_workers * 2:
                logger.error("=" * 80)
                logger.error(f"🚨 RUNAWAY DATALOADER WORKERS DETECTED! 🚨")
                logger.error(f"   Expected: ~{expected_workers} workers")
                logger.error(f"   Found: {len(worker_pids)} workers ({len(worker_pids) / max(1, expected_workers):.1f}x expected)")
                logger.error(f"   Total RAM: {total_worker_rss:.2f}GB")
                logger.error(f"   This indicates workers are being spawned faster than they're being killed!")
                logger.error(f"   Context: {name}")
                logger.error("=" * 80)
            
            logger.warning(
                f"🔫 Found {len(worker_pids)} orphaned DataLoader worker process(es) after {name} cleanup "
                f"(total RSS={total_worker_rss:.2f}GB) - killing them to prevent accumulation"
            )
            for pid, rss_gb in worker_pids:
                try:
                    worker_proc = psutil.Process(pid)
                    logger.debug(f"   Killing worker PID {pid} (RSS={rss_gb:.2f}GB)")
                    worker_proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.debug(f"   Could not kill worker PID {pid}: {e}")
            
            # Wait up to 2 seconds for graceful termination
            try:
                psutil.wait_procs([psutil.Process(pid) for pid, _ in worker_pids], timeout=2)
            except:
                pass
            
            # Force kill any remaining workers
            killed_count = 0
            for pid, rss_gb in worker_pids:
                try:
                    worker_proc = psutil.Process(pid)
                    if worker_proc.is_running():
                        logger.warning(f"   Force killing worker PID {pid} (didn't terminate gracefully)")
                        worker_proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    killed_count += 1  # Already dead
            
            logger.info(
                f"✅ Killed {killed_count}/{len(worker_pids)} orphaned {name} worker process(es) "
                f"(freed {total_worker_rss:.2f}GB RAM)"
            )
    except ImportError:
        logger.debug(f"   psutil not available - cannot aggressively kill {name} workers")
    except Exception as e:
        logger.debug(f"   Could not aggressively cleanup {name} workers: {e}")
    
    # Log final string cache stats when dataloader shuts down
    try:
        from featrix.neural.string_codec import log_final_string_cache_stats_all
        log_final_string_cache_stats_all()
    except Exception as e:
        logger.debug(f"Could not log final string cache stats: {e}")


# Track max expected workers - set when DataLoader is created
# NOTE: Training + Validation DataLoaders each have their own workers
# With num_workers=8 for each, expect ~16-20 total (plus a few overhead processes)
_MAX_EXPECTED_WORKERS = 20  # Default: assume 2 DataLoaders × 8 workers + overhead


def _check_for_runaway_processes(context: str = "", max_expected: int = None):
    """
    Check if we have way more child processes/threads than expected.
    
    CRITICAL: Call this periodically during training to catch runaway worker spawning EARLY
    before it consumes all RAM/GPU memory. If we detect > 2x expected workers, log a loud warning.
    
    Args:
        context: Where this check is being called from (for debugging)
        max_expected: Max expected child processes. Default uses _MAX_EXPECTED_WORKERS.
        
    Returns:
        Number of child processes found
    """
    if max_expected is None:
        max_expected = _MAX_EXPECTED_WORKERS
    
    try:
        import psutil
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        num_children = len(children)
        
        # Count threads too
        num_threads = current_process.num_threads()
        
        if num_children > max_expected * 2:
            total_rss = 0
            for child in children:
                try:
                    total_rss += child.memory_info().rss / (1024**3)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            logger.error("=" * 80)
            logger.error(f"🚨 RUNAWAY CHILD PROCESSES DETECTED! 🚨")
            logger.error(f"   Context: {context}")
            logger.error(f"   Expected: ~{max_expected} children")
            logger.error(f"   Found: {num_children} children ({num_children / max(1, max_expected):.1f}x expected)")
            logger.error(f"   Threads: {num_threads}")
            logger.error(f"   Total child RSS: {total_rss:.2f}GB")
            logger.error(f"   This may indicate workers are spawning out of control!")
            logger.error("=" * 80)
        elif num_children > max_expected:
            logger.warning(
                f"⚠️  More children than expected: {num_children} (expected ~{max_expected}) "
                f"[{context}]"
            )
        
        return num_children
    except Exception as e:
        logger.debug(f"Could not check for runaway processes: {e}")
        return 0


def _check_and_cleanup_existing_workers(parent_pid: int = None, context: str = ""):
    """
    Check for existing DataLoader worker processes and log their memory usage.
    
    This helps prevent OOM by ensuring we're aware of existing workers before
    creating new ones (e.g., validation workers when training workers are still active).
    
    Args:
        parent_pid: Parent process ID (None = current process)
        context: Context string for logging
        
    Returns:
        Number of existing workers found
    """
    try:
        from lib.system_health_monitor import SystemHealthMonitor
        monitor = SystemHealthMonitor()
        workers = monitor.find_dataloader_workers(parent_pid=parent_pid)
        
        if workers:
            total_rss = sum(w['rss_gb'] for w in workers)
            logger.warning(
                f"⚠️  Found {len(workers)} existing DataLoader worker(s){context}: "
                f"total RSS={total_rss:.2f}GB"
            )
            for i, worker in enumerate(workers):
                logger.debug(
                    f"   Worker {i+1}: PID={worker['pid']}, RSS={worker['rss_gb']:.2f}GB, "
                    f"{worker['percent']:.1f}% RAM"
                )
            return len(workers)
        else:
            logger.debug(f"   No existing DataLoader workers found{context}")
            return 0
    except Exception as e:
        logger.debug(f"Could not check for existing workers: {e}")
        return 0

def _log_gpu_memory_embedded_space(context: str = ""):
    """Quick GPU memory logging for tracing memory usage in embedded_space."""
    try:
        if not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        logger.info(f"📊 GPU MEMORY [embedded_space: {context}]: Allocated={allocated:.3f} GB, Reserved={reserved:.3f} GB, Peak={max_allocated:.3f} GB")
    except Exception as e:
        logger.debug(f"Could not log GPU memory: {e}")

# Class-level cache for rate-limiting missing codec warnings across all EmbeddingSpace instances
# Key: frozenset of missing field names -> last logged timestamp
_MISSING_CODEC_WARNING_CACHE = {}


def check_abort_and_raise(job_id: str, output_dir: str = None, context: str = "training") -> None:
    """
    Check for ABORT file and exit cleanly if found (sends Slack notification and logs).
    
    Args:
        job_id: The job ID to check
        output_dir: The job's output directory
        context: Description of where the check is happening (for error message)
        
    Note:
        If ABORT file is found, sends Slack notification, logs message, and exits cleanly
        without raising an exception (to avoid traceback).
    """
    if not job_id:
        return
    
    abort_file_path = check_abort_files(job_id, output_dir=output_dir)
    if abort_file_path:
        message = f"Training aborted due to ABORT file during {context} at {abort_file_path} (job_id: {job_id})"
        
        # Log the abort message
        logger.info(f"🚫 {message}")
        
        # Try to send Slack notification
        try:
            # Add src/ to path for slack import (embedded_space.py is in src/lib/featrix/neural/)
            # Go up 4 levels: neural/ -> featrix/ -> lib/ -> src/
            _src_path = Path(__file__).resolve().parent.parent.parent.parent
            if str(_src_path) not in sys.path:
                sys.path.insert(0, str(_src_path))
            
            from slack import send_slack_message
            
            slack_msg = f"🚫 **Training Aborted**\n"
            slack_msg += f"Job ID: `{job_id}`\n"
            slack_msg += f"Context: {context}\n"
            slack_msg += f"ABORT file: `{abort_file_path}`"
            
            send_slack_message(slack_msg, throttle=False)
            logger.info("✅ Slack notification sent")
        except Exception as slack_error:
            logger.warning(f"⚠️  Failed to send Slack notification: {slack_error}")
        
        # Exit cleanly without traceback
        os._exit(1)


def check_pause_and_handle(
    job_id: str, 
    epoch_idx: int, 
    batch_idx: int,
    save_checkpoint_fn=None,
    context: str = "training"
) -> bool:
    """
    Check for PAUSE file and handle pausing if found.
    
    Args:
        job_id: The job ID to check
        epoch_idx: Current epoch index
        batch_idx: Current batch index  
        save_checkpoint_fn: Optional function to call to save checkpoint before pausing
        context: Description of where the check is happening
        
    Returns:
        True if PAUSE file found (caller should break), False otherwise
    """
    if not job_id or not check_pause_files(job_id):
        return False
    
    logger.warning(f"⏸️  PAUSE file detected for job {job_id} during {context} - pausing training")
    
    # Save checkpoint before pausing
    if save_checkpoint_fn:
        try:
            save_checkpoint_fn()
            logger.info(f"💾 Checkpoint saved before pause at epoch {epoch_idx}, batch {batch_idx}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save checkpoint before pause: {e}")
    
    # Mark job as PAUSED
    try:
        from lib.job_manager import update_job_status, JobStatus
        update_job_status(job_id, JobStatus.PAUSED, {
            "pause_reason": "PAUSE file detected by user",
            "paused_at": datetime.now(tz=ZoneInfo("America/New_York"))
        })
        logger.info(f"⏸️  Job {job_id} marked as PAUSED")
    except Exception as e:
        logger.error(f"Failed to update job status to PAUSED: {e}")
    
    logger.info(f"⏸️  Breaking out of training loop - job is paused. Remove PAUSE file and set status to READY to resume.")
    return True


def check_finish_and_signal(job_id: str, context: str = "training") -> bool:
    """
    Check for FINISH file and log if found.
    
    Args:
        job_id: The job ID to check
        context: Description of where the check is happening (for log message)
        
    Returns:
        True if FINISH file found (caller should break out of loops), False otherwise
    """
    if not job_id:
        return False
    
    if check_finish_files(job_id):
        logger.warning(f"🏁 FINISH file detected for job {job_id} during {context} - completing training gracefully")
        logger.info(f"🏁 Breaking out of training loop to save model and complete job")
        return True
    return False


def debug_check_encodings_for_nan(encodings: list, epoch_idx: int, batch_idx: int) -> None:
    """
    Check encoder outputs for NaN/Inf values (only runs on first 3 batches of first epoch).
    
    Args:
        encodings: List of encoding tensors from encoder forward pass
        epoch_idx: Current epoch index
        batch_idx: Current batch index
    """
    if epoch_idx != 0 or batch_idx >= 3:
        return
    
    logger.info(f"🔍 NaN DEBUG [e={epoch_idx},b={batch_idx}] AFTER ENCODER FORWARD:")
    for i, enc in enumerate(encodings):
        if isinstance(enc, torch.Tensor):
            has_nan = torch.isnan(enc).any().item()
            has_inf = torch.isinf(enc).any().item()
            if has_nan or has_inf:
                logger.error(f"   💥 encoding[{i}] has NaN={has_nan}, Inf={has_inf}")
                logger.error(f"      shape={enc.shape}, min={enc.min().item():.4f}, max={enc.max().item():.4f}")


def get_time_moving_loss_values(history: list, epoch_idx: int, prev_loss: float) -> list:
    """
    Get loss values at n-16, n-8, n-4, n-2, n-1, n epochs for time-moving display.
    
    Args:
        history: List of (epoch_idx, loss_value) tuples
        epoch_idx: Current epoch index
        prev_loss: Previous epoch's loss value
        
    Returns:
        List of formatted strings for display: [n-16, n-8, n-4, n-2, n-1, current]
    """
    loss_n16 = None
    loss_n8 = None
    loss_n4 = None
    loss_n2 = None
    loss_n1 = prev_loss
    
    # Search backwards through history (exclude current epoch)
    for hist_epoch, hist_loss in reversed(history[:-1] if history else []):
        epochs_ago = epoch_idx - hist_epoch
        if epochs_ago == 16 and loss_n16 is None:
            loss_n16 = hist_loss
        if epochs_ago == 8 and loss_n8 is None:
            loss_n8 = hist_loss
        if epochs_ago == 4 and loss_n4 is None:
            loss_n4 = hist_loss
        if epochs_ago == 2 and loss_n2 is None:
            loss_n2 = hist_loss
        if epochs_ago == 1 and loss_n1 is None:
            loss_n1 = hist_loss
        if all(v is not None for v in [loss_n16, loss_n8, loss_n4, loss_n2, loss_n1]):
            break
    
    # Format as strings
    nums = []
    nums.append(f"{loss_n16:8.6f}" if loss_n16 is not None else "     N/A")
    nums.append(f"{loss_n8:8.6f}" if loss_n8 is not None else "     N/A")
    nums.append(f"{loss_n4:8.6f}" if loss_n4 is not None else "     N/A")
    nums.append(f"{loss_n2:8.6f}" if loss_n2 is not None else "     N/A")
    nums.append(f"{loss_n1:8.6f}" if loss_n1 is not None else "     N/A")
    return nums


def update_gradient_stats(grad_clip_stats: dict, unclipped_norm, total_norm, was_clipped: bool, loss) -> None:
    """
    Update gradient clipping statistics and rolling history.
    
    Args:
        grad_clip_stats: Dictionary to update with gradient statistics
        unclipped_norm: Gradient norm before clipping
        total_norm: Gradient norm after clipping
        was_clipped: Whether gradients were clipped
        loss: Loss tensor (for history tracking)
    """
    grad_clip_stats["total_batches"] += 1
    if was_clipped:
        grad_clip_stats["clipped_batches"] += 1
    grad_clip_stats["max_unclipped_norm"] = max(grad_clip_stats["max_unclipped_norm"], unclipped_norm)
    grad_clip_stats["max_clipped_norm"] = max(grad_clip_stats["max_clipped_norm"], total_norm)
    grad_clip_stats["sum_unclipped_norms"] += unclipped_norm
    grad_clip_stats["sum_clipped_norms"] += total_norm
    
    # Keep rolling history of last 100 gradients and losses for analysis
    if len(grad_clip_stats["gradient_norms_history"]) >= 100:
        grad_clip_stats["gradient_norms_history"].pop(0)
        grad_clip_stats["loss_values_history"].pop(0)
    grad_clip_stats["gradient_norms_history"].append(float(unclipped_norm))
    grad_clip_stats["loss_values_history"].append(float(loss.item()))


def handle_nan_inf_gradients(encoder, optimizer, loss, epoch_idx: int, batch_idx: int, total_norm) -> bool:
    """
    Detect and handle NaN/Inf gradients before they corrupt parameters.
    
    If NaN/Inf detected, zeros out corrupted gradients and parameters,
    then zeros the optimizer gradients.
    
    Args:
        encoder: The encoder module to check
        optimizer: The optimizer (will be zeroed if NaN detected)
        loss: The loss tensor (for logging)
        epoch_idx: Current epoch index
        batch_idx: Current batch index
        total_norm: The computed gradient norm to check
        
    Returns:
        True if NaN/Inf detected (caller should skip batch), False otherwise
    """
    if not (torch.isnan(total_norm) or torch.isinf(total_norm)):
        return False
    
    logger.error(f"💥 FATAL: NaN/Inf gradients detected! total_norm={total_norm}")
    logger.error(f"   Loss value: {loss.item()}")
    logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
    
    # Check individual parameter gradients AND parameter values
    nan_grad_params = []
    nan_value_params = []
    for name, param in encoder.named_parameters():
        # Check gradients for NaN and ZERO THEM OUT immediately
        if param.grad is not None and (torch.isnan(param.grad).any() or torch.isinf(param.grad).any()):
            nan_grad_params.append(name)
            # CRITICAL: Set gradients to zero to prevent corruption
            param.grad.data.zero_()
        # Check parameter VALUES for NaN (from previous corrupted step)
        if torch.isnan(param.data).any() or torch.isinf(param.data).any():
            nan_value_params.append(name)
            # CRITICAL: Replace NaN parameters with zeros to prevent forward pass corruption
            param.data[torch.isnan(param.data) | torch.isinf(param.data)] = 0.0
    
    if nan_grad_params:
        logger.error(f"   Parameters with NaN/Inf GRADIENTS: {nan_grad_params[:5]}...")
    if nan_value_params:
        logger.error(f"   Parameters with NaN/Inf VALUES (zeroed): {nan_value_params[:5]}...")
    
    # CRITICAL: Zero out corrupted gradients and skip this step
    logger.error("   ⚠️  ZEROING corrupted gradients and parameters, SKIPPING optimizer step")
    optimizer.zero_grad()
    return True


def debug_log_gradient_flow(encoder, epoch_idx: int, batch_idx: int, 
                            predictor_norm_pre_scale: float = None,
                            predictor_norm_post_scale: float = None,
                            encoder_norm: float = None,
                            gradient_flow_log_ratio: float = None,
                            encoder_params_frozen: list = None) -> None:
    """
    Log gradient flow diagnostics for key epochs and batches.
    
    Only logs for epochs [0, 1, 5, 10, 25, 50] and first 3 batches.
    
    Args:
        encoder: The encoder module to check gradients on
        epoch_idx: Current epoch index
        batch_idx: Current batch index
        predictor_norm_pre_scale: Predictor gradient norm BEFORE scaling (if available)
        predictor_norm_post_scale: Predictor gradient norm AFTER scaling (if available)
        encoder_norm: Encoder global gradient norm (if available)
        gradient_flow_log_ratio: logR = log(enc_global) - log(pred_global) (if available)
        encoder_params_frozen: List of frozen encoder param names (for verification)
    """
    diagnostic_epochs = [0, 1, 5, 10, 25, 50]
    if epoch_idx not in diagnostic_epochs or batch_idx >= 3:
        return
    
    logger.info("=" * 80)
    logger.info(f"🔍 GRADIENT FLOW DIAGNOSTIC (Epoch {epoch_idx}, Batch {batch_idx})")
    logger.info("=" * 80)
    
    # Check column encoder gradients
    col_enc_grads = []
    col_enc_params_with_grad = 0
    col_enc_params_total = 0
    for name, param in encoder.column_encoder.named_parameters():
        col_enc_params_total += 1
        if param.grad is not None:
            col_enc_params_with_grad += 1
            grad_norm = param.grad.norm().item()
            col_enc_grads.append(grad_norm)
    
    # Check joint encoder gradients
    joint_enc_grads = []
    joint_enc_params_with_grad = 0
    joint_enc_params_total = 0
    for name, param in encoder.joint_encoder.named_parameters():
        joint_enc_params_total += 1
        if param.grad is not None:
            joint_enc_params_with_grad += 1
            grad_norm = param.grad.norm().item()
            joint_enc_grads.append(grad_norm)
    
    # Check predictor gradients
    pred_grads = []
    pred_params_with_grad = 0
    pred_params_total = 0
    for name, param in encoder.named_parameters():
        if 'predictor' in name:
            pred_params_total += 1
            if param.grad is not None:
                pred_params_with_grad += 1
                grad_norm = param.grad.norm().item()
                pred_grads.append(grad_norm)
    
    # Calculate statistics
    col_enc_mean = np.mean(col_enc_grads) if col_enc_grads else 0.0
    col_enc_max = np.max(col_enc_grads) if col_enc_grads else 0.0
    joint_enc_mean = np.mean(joint_enc_grads) if joint_enc_grads else 0.0
    joint_enc_max = np.max(joint_enc_grads) if joint_enc_grads else 0.0
    pred_mean = np.mean(pred_grads) if pred_grads else 0.0
    pred_max = np.max(pred_grads) if pred_grads else 0.0
    
    logger.info(f"   Column Encoders: {col_enc_params_with_grad}/{col_enc_params_total} params have gradients")
    logger.info(f"      Gradient norm: mean={col_enc_mean:.6f}, max={col_enc_max:.6f}")
    logger.info(f"   Joint Encoder: {joint_enc_params_with_grad}/{joint_enc_params_total} params have gradients")
    logger.info(f"      Gradient norm: mean={joint_enc_mean:.6f}, max={joint_enc_max:.6f}")
    logger.info(f"   Predictors: {pred_params_with_grad}/{pred_params_total} params have gradients")
    if predictor_norm_pre_scale is not None and predictor_norm_post_scale is not None:
        # Log both pre and post scale norms for clarity
        logger.info(f"      Gradient norm (PRE-SCALE): {predictor_norm_pre_scale:.6f}")
        logger.info(f"      Gradient norm (POST-SCALE {predictor_norm_post_scale/predictor_norm_pre_scale if predictor_norm_pre_scale > 0 else 0:.1f}×): {predictor_norm_post_scale:.6f}")
        logger.info(f"      Per-param gradient norm: mean={pred_mean:.6f}, max={pred_max:.6f} (POST-SCALE)")
    else:
        logger.info(f"      Gradient norm: mean={pred_mean:.6f}, max={pred_max:.6f}")
    
    # Log encoder global norm and logR (apples-to-apples with single_predictor)
    if encoder_norm is not None:
        logger.info(f"   Encoder global grad norm: {encoder_norm:.6e}")
        if predictor_norm_pre_scale is not None:
            logger.info(f"   Predictor global grad norm: {predictor_norm_pre_scale:.6e}")
            if gradient_flow_log_ratio is not None and not (math.isinf(gradient_flow_log_ratio) or math.isnan(gradient_flow_log_ratio)):
                logger.info(f"   Gradient Flow log R: {gradient_flow_log_ratio:+.2f} [log(||∇_encoder||) - log(||∇_predictor||)]")
                if gradient_flow_log_ratio < -2.3:
                    logger.warning(f"      ⚠️  Encoder dead (predictor > 10× encoder)")
                elif gradient_flow_log_ratio > 2.3:
                    logger.warning(f"      ⚠️  Encoder dominating (encoder > 10× predictor)")
                else:
                    logger.info(f"      ✅ Balanced learning (within 10×)")
    
    # Verify frozen params (check if they're expected: unused heads/gated ops, not core encoder blocks)
    if encoder_params_frozen is not None and len(encoder_params_frozen) > 0:
        logger.info(f"   Frozen encoder params: {len(encoder_params_frozen)} total")
        # Categorize frozen params
        frozen_core_blocks = []
        frozen_unused_heads = []
        frozen_gated_ops = []
        frozen_other = []
        
        for name in encoder_params_frozen:
            if 'transformer_encoder' in name or 'out_converter' in name or 'attention' in name:
                # Core encoder blocks - these should NOT be frozen
                frozen_core_blocks.append(name)
            elif 'head' in name and ('unused' in name.lower() or 'gate' in name.lower()):
                frozen_unused_heads.append(name)
            elif 'gate' in name.lower() or 'mixture' in name.lower():
                frozen_gated_ops.append(name)
            else:
                frozen_other.append(name)
        
        if frozen_core_blocks:
            logger.error(f"      ❌ CRITICAL: {len(frozen_core_blocks)} core encoder blocks are frozen!")
            logger.error(f"         These should NOT be frozen - check requires_grad settings")
            logger.error(f"         First 5: {frozen_core_blocks[:5]}")
        if frozen_unused_heads:
            logger.info(f"      ✅ Expected: {len(frozen_unused_heads)} unused heads/gates (OK to freeze)")
        if frozen_gated_ops:
            logger.info(f"      ✅ Expected: {len(frozen_gated_ops)} gated operations (OK to freeze)")
        if frozen_other:
            logger.warning(f"      ⚠️  {len(frozen_other)} other frozen params (verify if expected)")
            logger.warning(f"         First 5: {frozen_other[:5]}")
    
    # Check for problems
    if col_enc_params_with_grad == 0:
        logger.error("   💥 CRITICAL: Column encoders have NO GRADIENTS!")
        logger.error("   This means they are frozen or loss doesn't depend on them!")
    elif col_enc_mean < 1e-8:
        logger.error(f"   ⚠️  WARNING: Column encoder gradients are vanishingly small ({col_enc_mean:.2e})")
    
    if joint_enc_params_with_grad == 0:
        logger.error("   💥 CRITICAL: Joint encoder has NO GRADIENTS!")
        logger.error("   This means it is frozen or loss doesn't depend on it!")
    elif joint_enc_mean < 1e-8:
        logger.error(f"   ⚠️  WARNING: Joint encoder gradients are vanishingly small ({joint_enc_mean:.2e})")
    
    logger.info("=" * 80)


def check_abort_files(job_id: str, output_dir: str = None) -> Optional[str]:
    """
    Check for ABORT file in the job's output directory.
    
    For /sphere paths: Checks both job directory and parent directories (session-level control files)
    For other paths: ONLY checks the specific job's directory (same directory) to avoid false positives
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: The exact output directory for this job (e.g., /featrix-output/session/job_type/job_id)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        Optional[str]: Path to ABORT file if found (should exit), None otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return None
    
    # Use the job_manager function which handles /sphere vs non-/sphere paths correctly
    from lib.job_manager import _find_control_file
    abort_file = _find_control_file(job_id, "ABORT", output_dir)
    
    if abort_file:
        logger.warning(f"🚫 ABORT file detected: {abort_file}")
        logger.warning(f"🚫 Training job {job_id} will exit with code 2")
        logger.warning(f"🚫 ABORT file also prevents job restart after crashes")
        
        # Mark job as FAILED immediately when ABORT file is detected
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id, JobStatus.FAILED, {
                "error_message": f"Training aborted due to ABORT file at {abort_file}"
            })
            logger.info(f"🚫 Job {job_id} marked as FAILED due to ABORT file")
        except Exception as e:
            logger.error(f"Failed to update job status when ABORT file detected: {e}")
        
        return str(abort_file)
    
    return None


def check_no_stop_file(job_id: str, output_dir: str = None) -> bool:
    """
    Check for NO_STOP file in the job's output directory.
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        bool: True if NO_STOP file exists (disable early stopping), False otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return False
    
    from pathlib import Path
    
    # If output_dir is provided and is already the job directory, use it directly
    if output_dir and Path(output_dir).exists() and (Path(output_dir) / "NO_STOP").exists():
        no_stop_file = Path(output_dir) / "NO_STOP"
    elif output_dir:
        # output_dir is base directory, construct path (old structure fallback)
        job_output_dir = Path(output_dir) / job_id
        no_stop_file = job_output_dir / "NO_STOP"
    else:
        # Try to use helper function to find job directory (new structure)
        try:
            from lib.job_manager import get_job_output_path
            job_output_dir = get_job_output_path(job_id)  # Search only - will assert if not found
            no_stop_file = job_output_dir / "NO_STOP"
        except Exception:
            # Fallback to old structure
            output_dir = "/sphere/app/featrix_output"
            job_output_dir = Path(output_dir) / job_id
            no_stop_file = job_output_dir / "NO_STOP"
    
    # Check for NO_STOP file
    if no_stop_file.exists():
        return True
    
    return False


def check_publish_file(job_id: str, output_dir: str = None) -> bool:
    """
    Check for PUBLISH file in the job's output directory.
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        bool: True if PUBLISH file exists (should save embedding space), False otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return False
    
    from pathlib import Path
    
    # If output_dir is provided and is already the job directory, use it directly
    if output_dir and Path(output_dir).exists() and (Path(output_dir) / "PUBLISH").exists():
        publish_file = Path(output_dir) / "PUBLISH"
    elif output_dir:
        # output_dir is base directory, construct path (old structure fallback)
        job_output_dir = Path(output_dir) / job_id
        publish_file = job_output_dir / "PUBLISH"
    else:
        # Try to use helper function to find job directory (new structure)
        try:
            from lib.job_manager import get_job_output_path
            job_output_dir = get_job_output_path(job_id)  # Search only - will assert if not found
            publish_file = job_output_dir / "PUBLISH"
        except Exception:
            # Fallback to old structure
            output_dir = "/sphere/app/featrix_output"
            job_output_dir = Path(output_dir) / job_id
            publish_file = job_output_dir / "PUBLISH"
    
    # Check for PUBLISH file
    if publish_file.exists():
        return True
    
    return False


def check_pause_files(job_id: str, output_dir: str = None) -> bool:
    """
    Check for PAUSE file in the job's output directory.
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        bool: True if PAUSE file exists (should pause training and save checkpoint), False otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return False
    
    from pathlib import Path
    
    # Build list of all possible locations to check (similar to check_abort_files)
    paths_to_check = []
    
    # 1. If output_dir is provided and looks like a job directory
    if output_dir and Path(output_dir).exists():
        paths_to_check.append(Path(output_dir) / "PAUSE")
        parent = Path(output_dir).parent
        if parent.exists():
            paths_to_check.append(parent / "PAUSE")
    
    # 2. Try to use helper function to find job directory (new structure)
    try:
        from lib.job_manager import get_job_output_path
        job_output_dir = get_job_output_path(job_id)  # Search only - will assert if not found
        paths_to_check.append(job_output_dir / "PAUSE")
        if job_output_dir.parent.exists():
            paths_to_check.append(job_output_dir.parent / "PAUSE")
    except Exception as e:
        logger.debug(f"Could not use get_job_output_path: {e}")
    
    # 3. Common output directories
    common_dirs = [
        Path("/sphere/app/featrix_output") / job_id,
        Path("/sphere/featrix_data") / job_id,
    ]
    
    if output_dir:
        common_dirs.append(Path(output_dir) / job_id)
    
    for common_dir in common_dirs:
        if common_dir.exists():
            paths_to_check.append(common_dir / "PAUSE")
            if common_dir.parent.exists():
                paths_to_check.append(common_dir.parent / "PAUSE")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for p in paths_to_check:
        p_str = str(p.resolve())
        if p_str not in seen:
            seen.add(p_str)
            unique_paths.append(p)
    
    # Check all paths
    for pause_file in unique_paths:
        if pause_file.exists():
            logger.warning(f"⏸️  PAUSE file detected: {pause_file}")
            return True
    
    return False


def check_finish_files(job_id: str, output_dir: str = None) -> bool:
    """
    Check for FINISH file in the job's output directory.
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        bool: True if FINISH file exists (should finish training gracefully), False otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return False
    
    from pathlib import Path
    
    # If output_dir is provided and is already the job directory, use it directly
    if output_dir and Path(output_dir).exists() and (Path(output_dir) / "FINISH").exists():
        finish_file = Path(output_dir) / "FINISH"
    elif output_dir:
        # output_dir is base directory, construct path (old structure fallback)
        job_output_dir = Path(output_dir) / job_id
        finish_file = job_output_dir / "FINISH"
    else:
        # Try to use helper function to find job directory (new structure)
        try:
            from lib.job_manager import get_job_output_path
            job_output_dir = get_job_output_path(job_id)  # Search only - will assert if not found
            finish_file = job_output_dir / "FINISH"
        except Exception:
            # Fallback to old structure
            output_dir = "/sphere/app/featrix_output"
            job_output_dir = Path(output_dir) / job_id
            finish_file = job_output_dir / "FINISH"
    
    # Check for FINISH file
    if finish_file.exists():
        logger.warning(f"🏁 FINISH file detected: {finish_file}")
        logger.warning(f"🏁 Training job {job_id} will complete gracefully")
        logger.warning(f"🏁 Model will be saved and job marked as completed")
        return True
    
    return False


def check_restart_files(job_id: str, output_dir: str = None) -> bool:
    """
    Check for RESTART file in the job's output directory.
    
    Args:
        job_id: The job ID (e.g., 'abc123-20251005-221252'), or None to skip check
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
                   If None, attempts to use helper function to find job directory
        
    Returns:
        bool: True if RESTART file exists, False otherwise
    """
    # If no job_id, skip the check
    if job_id is None:
        return False
    
    from pathlib import Path
    
    # If output_dir is provided and is already the job directory, use it directly
    if output_dir and Path(output_dir).exists() and (Path(output_dir) / "RESTART").exists():
        restart_file = Path(output_dir) / "RESTART"
    elif output_dir:
        # output_dir is base directory, construct path (old structure fallback)
        job_output_dir = Path(output_dir) / job_id
        restart_file = job_output_dir / "RESTART"
    else:
        # Try to use helper function to find job directory (new structure)
        try:
            from lib.job_manager import get_job_output_path
            job_output_dir = get_job_output_path(job_id)  # Search only - will assert if not found
            restart_file = job_output_dir / "RESTART"
        except Exception:
            # Fallback to old structure
            output_dir = "/sphere/app/featrix_output"
            job_output_dir = Path(output_dir) / job_id
            restart_file = job_output_dir / "RESTART"
    
    # Check for RESTART file
    return restart_file.exists()


def remove_restart_file(job_id: str, output_dir: str = None) -> bool:
    """
    Remove the RESTART file from the job's output directory.
    
    Args:
        job_id: The job ID
        output_dir: Base output directory (defaults to /sphere/app/featrix_output)
        
    Returns:
        bool: True if file was removed, False if it didn't exist or couldn't be removed
    """
    if job_id is None:
        return False
    
    if output_dir is None:
        output_dir = "/sphere/app/featrix_output"
    
    from pathlib import Path
    job_output_dir = Path(output_dir) / job_id
    restart_file = job_output_dir / "RESTART"
    
    if restart_file.exists():
        try:
            restart_file.unlink()
            logger.info(f"🔄 Removed RESTART file: {restart_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove RESTART file {restart_file}: {e}")
            return False
    
    return False


@unique
class CallbackType(IntEnum):
    AFTER_BATCH = 0


# def compute_multicolumn_loss(codecs, predictors, targets, device):
#     loss = 0
#     for target_name, target_values in targets.items():
#         target = {"name": target_name, "value": target_values}
#         target_loss = compute_loss(codecs, predictors, target, device)
#         # print(f"target: {target_name}; loss: {target_loss}")
#         loss += target_loss

#     return loss


# def compute_loss(codecs, predictors, targets, device):
#     target_name = targets["name"]
#     target_values = targets["value"].value

#     target_codec = codecs[target_name]
#     decoded = target_codec.decode(predictors)
#     # print("target values:", target_values)
#     # print("decoded:", decoded)
#     # target_codec.to(get_device())
#     loss = target_codec.loss(decoded, target_values)

#     return loss


# def compute_loss_random_target(codecs, predictors, targets):
#     # Each element of the predictors tensor must form its own minibatch, so
#     # we unqueeze it.
#     # This is because each element of the predictors tensor is processed by a separate
#     # encoder, and each encoder expects a batch-shaped input.
#     predictors = predictors.unsqueeze(dim=1)
#     target_names = targets["name"]
#     target_values = targets["token"].value

#     loss = 0
#     n_preds = len(target_names)
#     for i, target_col_name in enumerate(target_names):
#         target_codec = codecs[target_col_name]
#         decoded = target_codec.decode(predictors[i])

#         # NOTE: the type of the target depends on what other variables types are targets
#         # in the same batch. If all targeted variables are categoricals, the targets
#         # will be ints, but if at least one targeted variable is a scalar, then all
#         # batch targets will be floats.
#         target_value = target_values[i]

#         # Use `loss_single` instead of `loss` because each element in the batch comes
#         # from a different variable, so they can't be decoded as a batch
#         # See note above re: efficiency.
#         loss += target_codec.loss_single(decoded, target_value)

#     # compute the average loss per prediction
#     return loss / n_preds


def flatten(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


class DataSegment:
    def __init__(self, row_meta):
        self.row_meta = row_meta
        self._indexes = None
        self._indexOffset = None
        self.reset()

    def reset(self):
        self._indexes = list(
            range(
                self.row_meta.row_idx_start,
                self.row_meta.row_idx_start + self.row_meta.num_rows,
            )
        )
        # print("INDEXES man", self._indexes)
        self._indexOffset = 0
        # random.shuffle(self._indexes)
        return

    def isExhausted(self):
        return self._indexOffset >= len(self._indexes)

    def grabNextBatchIndexes(self, batch_size):
        start = self._indexOffset
        end = start + batch_size
        if end > len(self._indexes):
            end = len(self._indexes)
        self._indexOffset = end
        return self._indexes[start:end]


class DataSpaceBatchSampler(Sampler[list[int]]):
    def __init__(self, batch_size, inputDataset: FeatrixInputDataSet):
        self.batch_size = batch_size
        assert isinstance(self.batch_size, int) and self.batch_size >= 0
        self.inputDataset = inputDataset
        self.shuffleList = None
        self.segmentList = []
        if inputDataset.project_row_meta_data_list is not None:
            for entry in inputDataset.project_row_meta_data_list:
                self.segmentList.append(DataSegment(entry))
        self.nextSegmentIndex = 0

    def __iter__(self):
        for entry in self.segmentList:
            entry.reset()
        # self.shuffleList = self.inputDataset.df.
        self.nextSegmentIndex = 0
        return self

    def __next__(self):
        # get the next batch... ALWAYS 32 things.
        # pick a segment.
        # get a batch out of that segment.
        nextSegment = None

        numLoops = 0
        while numLoops < (len(self.segmentList) * 2):
            if self.nextSegmentIndex >= len(self.segmentList):
                self.nextSegmentIndex = 0

            nextSegment = self.segmentList[self.nextSegmentIndex]
            if not nextSegment.isExhausted():
                break
            # it's exhausted, try the next one
            self.nextSegmentIndex += 1
            numLoops += 1

        if nextSegment.isExhausted():
            raise StopIteration()

        toReturn = nextSegment.grabNextBatchIndexes(self.batch_size)
        self.nextSegmentIndex += 1
        if len(toReturn) == 0:
            print("Backup protection -- should not get here")
            raise StopIteration()
        return toReturn

    def __len__(self):
        return len(self.inputDataset.df)

    def dump(self):
        # print(f"-------- {len(self.segmentList)} segments -------")
        # for s in self.segmentList:
        #     print(f"... {s._indexes}")
        # print("-----")
        return


def detect_es_training_failure(
    epoch_idx: int,
    train_loss: float,
    val_loss: float,
    train_loss_history: list,
    val_loss_history: list,
    gradient_norm: float = None,
    lr: float = None,
    gradient_norm_history: list = None
):
    """
    Detect and diagnose ES (Embedding Space) training failure modes.
    
    Args:
        epoch_idx: Current epoch number
        train_loss: Current training loss
        val_loss: Current validation loss
        train_loss_history: List of training losses from previous epochs
        val_loss_history: List of validation losses from previous epochs
        gradient_norm: Current unclipped gradient norm (if available)
        lr: Current learning rate (if available)
        gradient_norm_history: List of gradient norms from previous epochs (for relative comparisons)
    
    Returns:
        tuple: (has_failure: bool, failure_type: str, recommendations: list)
    """
    failures = []
    recommendations = []
    
    # Need at least 5 epochs of history for meaningful analysis
    if len(train_loss_history) < 5 or len(val_loss_history) < 5:
        return False, None, []
    
    # Calculate trends
    recent_train_losses = train_loss_history[-5:]
    recent_val_losses = val_loss_history[-5:]
    
    # Safely calculate improvement percentages (avoid division by zero)
    if recent_train_losses[0] > 0:
        train_improvement = (recent_train_losses[0] - recent_train_losses[-1]) / recent_train_losses[0]
    else:
        train_improvement = 0.0
    
    if recent_val_losses[0] > 0:
        val_improvement = (recent_val_losses[0] - recent_val_losses[-1]) / recent_val_losses[0]
    else:
        val_improvement = 0.0
    
    # Check if validation is diverging from training
    train_val_gap = val_loss - train_loss
    train_val_gap_pct = (train_val_gap / train_loss) * 100 if train_loss > 0 else 0
    
    # FAILURE MODE 1: Zero/tiny gradients (dead network)
    if gradient_norm is not None and gradient_norm < 1e-6:
        failures.append("DEAD_NETWORK")
        recommendations.extend([
            "🔥 CRITICAL: Network has zero gradients - not learning at all",
            "   → STOP TRAINING - Network is frozen",
            f"   → Current LR ({lr:.6e}) is likely too low" if lr else "   → Learning rate may be too low",
            "   → Increase learning rate by 10-100x and restart",
            "   → Check if parameters are accidentally frozen",
            "   → Verify loss function is differentiable"
        ])
    
    # FAILURE MODE 2: Very slow learning (minimal improvement over 5 epochs)
    elif abs(train_improvement) < 0.01 and gradient_norm is not None and gradient_norm < 0.01:
        failures.append("VERY_SLOW_LEARNING")
        recommendations.extend([
            f"⚠️  WARNING: Minimal learning progress ({train_improvement*100:.2f}% improvement over 5 epochs)",
            f"   → Gradient norm is very small: {gradient_norm:.6e}",
            f"   → Current LR: {lr:.6e}" if lr else "   → Learning rate may be too low",
            "   → Consider increasing learning rate by 3-5x",
            "   → Consider switching to constant LR or gentler schedule",
            "   → Verify self-supervised task is not too easy (loss should be challenging)"
        ])
    
    # FAILURE MODE 3: Severe overfitting (val loss diverging from train loss)
    elif val_improvement < -0.05 and train_improvement > 0.02 and epoch_idx > 10:
        failures.append("SEVERE_OVERFITTING")
        recommendations.extend([
            f"⚠️  WARNING: Severe overfitting detected (val loss increasing: {val_improvement*100:.1f}%)",
            f"   → Training/validation gap: {train_val_gap:.4f} ({train_val_gap_pct:.1f}%)",
            "   → Model is memorizing training data instead of learning generalizable features",
            "   → STOP TRAINING - Model quality is degrading",
            "   → Increase dropout (try 0.5 or higher)",
            "   → Increase weight_decay (try 1e-3 instead of 1e-4)",
            "   → Reduce model complexity (fewer layers, smaller d_model)",
            "   → For small datasets (<2000 rows), use constant high dropout"
        ])
    
    # FAILURE MODE 4: No learning at all (flat or increasing validation loss)
    # Only trigger if validation loss is NOT improving (val_improvement <= 0 or very small positive)
    # If loss is decreasing significantly, don't trigger NO_LEARNING even if recent change is small
    elif val_improvement <= 0.0005 and epoch_idx > 15:
        # Double-check: if loss is actually decreasing over the window, don't trigger
        # This prevents false positives when loss is improving but slowly
        if recent_val_losses[-1] < recent_val_losses[0]:
            # Loss is decreasing - check if improvement is meaningful
            absolute_improvement = recent_val_losses[0] - recent_val_losses[-1]
            relative_improvement_pct = (absolute_improvement / recent_val_losses[0]) * 100 if recent_val_losses[0] > 0 else 0
            
            # Only trigger if improvement is truly minimal (< 0.1% over 5 epochs)
            if relative_improvement_pct >= 0.1:
                # Loss is improving meaningfully, don't trigger NO_LEARNING
                pass
            else:
                failures.append("NO_LEARNING")
                recommendations.extend([
                    f"⚠️  WARNING: Minimal learning progress ({val_improvement*100:.2f}% change in validation loss over 5 epochs)",
                    f"   → Validation loss has plateaued at {val_loss:.4f}",
                    "   → Early stopping is now BLOCKED for 10 more epochs to allow recovery",
                    "   → Self-supervised task may be too easy or too hard",
                    "   → Consider adjusting learning rate (try increasing by 2-3x or using a different schedule)",
                    "   → Check if embeddings are varying (use tensorboard/visualization)",
                    "   → Verify masking strategy is appropriate",
                    "   → Consider if dataset has sufficient complexity to learn from"
                ])
        else:
            # Loss is not decreasing (flat or increasing) - this is truly NO_LEARNING
            failures.append("NO_LEARNING")
            recommendations.extend([
                f"⚠️  WARNING: No learning progress ({val_improvement*100:.2f}% change in validation loss over 5 epochs)",
                f"   → Validation loss has plateaued at {val_loss:.4f}",
                "   → Early stopping is now BLOCKED for 10 more epochs to allow recovery",
                "   → Self-supervised task may be too easy or too hard",
                "   → Consider adjusting learning rate (try increasing by 2-3x or using a different schedule)",
                "   → Check if embeddings are varying (use tensorboard/visualization)",
                "   → Verify masking strategy is appropriate",
                "   → Consider if dataset has sufficient complexity to learn from"
            ])
    
    # FAILURE MODE 5: Moderate overfitting (early warning)
    elif train_val_gap_pct > 10 and val_improvement < 0 and epoch_idx > 10:
        failures.append("MODERATE_OVERFITTING")
        recommendations.extend([
            f"⚠️  WARNING: Overfitting detected (train/val gap: {train_val_gap_pct:.1f}%)",
            "   → Validation loss is no longer improving while training loss decreases",
            "   → Consider early stopping soon if trend continues",
            "   → Increase regularization (dropout/weight_decay)",
            "   → This is acceptable for large datasets, but risky for small ones"
        ])
    
    # FAILURE MODE 6: Unstable training (loss oscillating wildly)
    # TIGHTENED: Require both high CV AND sign changes in loss deltas (oscillation pattern)
    elif len(recent_train_losses) >= 5:
        train_std = np.std(recent_train_losses)
        train_mean = np.mean(recent_train_losses)
        coef_variation = train_std / train_mean if train_mean > 0 else 0
        
        # Check for oscillation pattern: count sign changes in loss deltas
        loss_deltas = [recent_train_losses[i] - recent_train_losses[i-1] 
                      for i in range(1, len(recent_train_losses))]
        sign_changes = sum(1 for i in range(1, len(loss_deltas)) 
                          if (loss_deltas[i] > 0) != (loss_deltas[i-1] > 0))
        
        # Check for convergence exception (late training noise is natural)
        # Suppress instability warnings if all are true:
        # - LR is very low (converging)
        # - Gradient norm is small relative to history (converging)
        # - Val loss not diverging (stable)
        lr_min_threshold = 1e-4  # Very low LR suggests late-stage convergence
        convergence_exception = False
        if lr is not None and gradient_norm is not None:
            lr_is_low = lr < lr_min_threshold
            # Use relative gradient norm: current < 0.25 * median of last 50
            if gradient_norm_history and len(gradient_norm_history) > 0:
                recent_grads = gradient_norm_history[-50:]  # Last 50 epochs
                median_grad = np.median(recent_grads)
                grad_is_small = gradient_norm < 0.25 * median_grad
            else:
                # Fallback to absolute threshold if no history available
                grad_is_small = gradient_norm < 10.0
            val_not_diverging = val_improvement >= -0.02  # Val loss not getting worse (>2% increase)
            convergence_exception = lr_is_low and grad_is_small and val_not_diverging
        
        # Only trigger if BOTH conditions met: high CV AND oscillation pattern
        # AND not in convergence exception state
        if coef_variation > 0.1 and sign_changes >= 2 and not convergence_exception:
            failures.append("UNSTABLE_TRAINING")
            recommendations.extend([
                f"⚠️  WARNING: Training loss is highly unstable (CV={coef_variation:.3f}, {sign_changes} sign changes)",
                "   → Loss is oscillating instead of steadily decreasing",
                "   → Learning rate may be too high",
                "   → Consider switching to gentler schedule",
                "   → Try reducing learning rate by 2-3x",
                "   → Increase batch size for more stable gradients"
            ])
    
    # SUCCESS: Model seems to be learning well
    if not failures and train_improvement > 0.02 and val_improvement > 0:
        return False, "HEALTHY", ["✅ ES training appears healthy - both train and val losses improving"]
    
    # Return detected failures (let caller decide whether to log)
    if failures:
        failure_label = "_".join(failures)
        return True, failure_label, recommendations
    
    return False, None, []


def summarize_es_training_results(training_info: dict, loss_history: list, embedding_space=None):
    """
    Summarize ES training results with diagnostics and quality assessment.
    
    Args:
        training_info: Dictionary containing training metadata
        loss_history: List of loss entries from training
        embedding_space: Optional EmbeddingSpace instance to record quality checks
    
    Returns:
        dict: Summary with quality assessment and recommendations
    """
    logger.info("=" * 100)
    logger.info("📊 EMBEDDING SPACE TRAINING SUMMARY")
    logger.info("=" * 100)
    
    if not loss_history or len(loss_history) < 2:
        logger.warning("⚠️  Insufficient training history to analyze")
        return {"status": "insufficient_data"}
    
    # Extract training and validation losses
    # ES uses 'loss' key, not 'running_mean_training_loss' or 'total_loss'
    # Filter out None values - if a key exists but value is None, .get() returns None
    # Use 0 as default only if key doesn't exist, but filter out entries where value is explicitly None
    train_losses = []
    for entry in loss_history:
        if isinstance(entry, dict):
            loss = entry.get('loss')
            if loss is not None:
                train_losses.append(loss)
            elif 'loss' not in entry:
                train_losses.append(0)  # Key doesn't exist, use default
    
    val_losses = []
    for entry in loss_history:
        if isinstance(entry, dict):
            val_loss = entry.get('validation_loss')
            if val_loss is not None:
                val_losses.append(val_loss)
            elif 'validation_loss' not in entry:
                val_losses.append(0)  # Key doesn't exist, use default
    
    if not train_losses or not val_losses:
        logger.warning("⚠️  Could not extract loss data from history")
        return {"status": "no_loss_data"}
    
    # Calculate statistics
    initial_train_loss = train_losses[0]
    final_train_loss = train_losses[-1]
    initial_val_loss = val_losses[0]
    final_val_loss = val_losses[-1]
    
    # Ensure all values are not None (shouldn't happen with our filtering, but be safe)
    if initial_train_loss is None:
        logger.warning("⚠️  Initial training loss is None - defaulting to 0.0")
        initial_train_loss = 0.0
    if final_train_loss is None:
        logger.warning("⚠️  Final training loss is None - defaulting to 0.0")
        final_train_loss = 0.0
    if initial_val_loss is None:
        logger.warning("⚠️  Initial validation loss is None - defaulting to 0.0")
        initial_val_loss = 0.0
    if final_val_loss is None:
        logger.warning("⚠️  Final validation loss is None - defaulting to 0.0")
        final_val_loss = 0.0
    
    # Fix initial validation loss: use first non-inf value instead of inf
    # This ensures we can calculate meaningful improvement percentages
    if not math.isfinite(initial_val_loss):
        found_finite = False
        for val_loss in val_losses:
            if math.isfinite(val_loss):
                initial_val_loss = val_loss
                found_finite = True
                logger.debug(f"Fixed initial validation loss from inf to {initial_val_loss:.4f} (first finite value found)")
                break
        if not found_finite:
            # Fallback: use final validation loss if no finite values found (shouldn't happen)
            logger.warning("⚠️  No finite validation losses found in history - using final validation loss as initial")
            initial_val_loss = final_val_loss if (final_val_loss is not None and math.isfinite(final_val_loss)) else 0.0
    
    # Safely calculate improvement percentages (avoid division by zero and None)
    if initial_train_loss is not None and initial_train_loss > 0:
        train_improvement = ((initial_train_loss - final_train_loss) / initial_train_loss) * 100
    else:
        train_improvement = 0.0
    
    if initial_val_loss is not None and initial_val_loss > 0 and final_val_loss is not None:
        val_improvement = ((initial_val_loss - final_val_loss) / initial_val_loss) * 100
    else:
        val_improvement = 0.0
    
    best_train_loss = min(train_losses)
    best_val_loss = min(val_losses) if val_losses else 0.0
    
    # Safely calculate train/val gap (ensure no None values)
    if final_val_loss is not None and final_train_loss is not None:
        train_val_gap = final_val_loss - final_train_loss
        train_val_gap_pct = (train_val_gap / final_train_loss) * 100 if final_train_loss > 0 else 0
    else:
        train_val_gap = 0.0
        train_val_gap_pct = 0.0
    
    # Training duration
    start_time = training_info.get('start_time', 0)
    end_time = training_info.get('end_time', 0)
    duration_seconds = end_time - start_time if end_time > start_time else 0
    duration_minutes = duration_seconds / 60
    
    # Log summary
    logger.info(f"⏱️  Training Duration: {duration_minutes:.1f} minutes ({duration_seconds:.0f} seconds)")
    logger.info(f"📈 Total Epochs: {len(train_losses)}")
    logger.info("")
    logger.info("📉 LOSS PROGRESSION (Full Training History):")
    logger.info(f"   Initial Training:   {initial_train_loss:.4f}")
    logger.info(f"   Initial Validation: {initial_val_loss:.4f}")
    logger.info(f"   Final Training:     {final_train_loss:.4f} ({train_improvement:+.1f}%)")
    logger.info(f"   Final Validation:   {final_val_loss:.4f} ({val_improvement:+.1f}%)")
    logger.info(f"   Best Training Loss (in history):  {best_train_loss:.4f}")
    logger.info(f"   Best Validation Loss (in history): {best_val_loss:.4f}")
    logger.info("")
    logger.info(f"   ⚠️  Note: Training loss is curriculum-weighted and changes across phases")
    logger.info(f"   → Use VALIDATION loss and component losses for meaningful quality assessment")
    logger.info(f"   → Training loss improvement % is NOT a reliable metric for ES training")
    
    # Show loss component progression if available
    if loss_history and len(loss_history) > 0:
        first_entry = loss_history[0]
        last_entry = loss_history[-1]
        
        if first_entry and last_entry and 'spread' in first_entry and 'spread' in last_entry:
            logger.info("")
            logger.info("📊 LOSS COMPONENT BREAKDOWN:")
            
            # Initial components - handle None values explicitly
            init_spread = first_entry.get('spread') or 0
            init_joint = first_entry.get('joint') or 0
            init_marginal = first_entry.get('marginal') or 0
            init_marginal_w = first_entry.get('marginal_weighted') or 0
            
            # Final components - handle None values explicitly
            final_spread = last_entry.get('spread') or 0
            final_joint = last_entry.get('joint') or 0
            final_marginal = last_entry.get('marginal') or 0
            final_marginal_w = last_entry.get('marginal_weighted') or 0
            
            # Ensure all values are numeric (not None) before calculations
            init_spread = float(init_spread) if init_spread is not None else 0.0
            init_joint = float(init_joint) if init_joint is not None else 0.0
            init_marginal = float(init_marginal) if init_marginal is not None else 0.0
            init_marginal_w = float(init_marginal_w) if init_marginal_w is not None else 0.0
            final_spread = float(final_spread) if final_spread is not None else 0.0
            final_joint = float(final_joint) if final_joint is not None else 0.0
            final_marginal = float(final_marginal) if final_marginal is not None else 0.0
            final_marginal_w = float(final_marginal_w) if final_marginal_w is not None else 0.0
            
            # Calculate improvements
            spread_improv = ((init_spread - final_spread) / init_spread * 100) if init_spread > 0 else 0
            joint_improv = ((init_joint - final_joint) / init_joint * 100) if init_joint > 0 else 0
            marginal_improv = ((init_marginal - final_marginal) / init_marginal * 100) if init_marginal > 0 else 0
            
            logger.info(f"   Spread Loss:")
            logger.info(f"      Initial: {init_spread:.4f} → Final: {final_spread:.4f} ({spread_improv:+.1f}%)")
            logger.info(f"   Joint Loss:")
            logger.info(f"      Initial: {init_joint:.4f} → Final: {final_joint:.4f} ({joint_improv:+.1f}%)")
            logger.info(f"   Marginal Loss (unweighted):")
            logger.info(f"      Initial: {init_marginal:.4f} → Final: {final_marginal:.4f} ({marginal_improv:+.1f}%)")
            if init_marginal_w > 0 and final_marginal_w > 0:
                logger.info(f"   Marginal Loss (weighted contribution to total):")
                logger.info(f"      Initial: {init_marginal_w:.4f} → Final: {final_marginal_w:.4f}")
    
    logger.info("")
    
    # Check if best checkpoint was loaded
    best_checkpoint_loaded = training_info.get('best_checkpoint_loaded', False)
    if best_checkpoint_loaded:
        best_epoch = training_info.get('best_checkpoint_epoch', 'unknown')
        loaded_train_loss = training_info.get('best_checkpoint_train_loss', None)
        loaded_val_loss = training_info.get('best_checkpoint_val_loss', None)
        
        logger.info("🏆 BEST CHECKPOINT LOADED:")
        logger.info(f"   ✅ Successfully loaded best model from epoch {best_epoch}")
        if loaded_train_loss is not None and loaded_val_loss is not None:
            logger.info(f"   Training Loss:   {loaded_train_loss:.4f}")
            logger.info(f"   Validation Loss: {loaded_val_loss:.4f}")
            loaded_gap = loaded_val_loss - loaded_train_loss
            loaded_gap_pct = (loaded_gap / loaded_train_loss) * 100 if loaded_train_loss > 0 else 0
            logger.info(f"   Train/Val Gap: {loaded_gap:.4f} ({loaded_gap_pct:+.1f}%)")
            
            # Compare best checkpoint to final epoch
            # Ensure both values are not None before comparing
            if loaded_val_loss is not None and final_val_loss is not None and loaded_val_loss < final_val_loss:
                val_saved = ((final_val_loss - loaded_val_loss) / final_val_loss) * 100
                logger.info(f"   💡 Best checkpoint validation loss is {val_saved:.1f}% better than final epoch")
                logger.info(f"      (avoided overfitting by using best checkpoint)")
        logger.info(f"   📌 This is the model being used for all downstream tasks")
        logger.info("")
    else:
        logger.warning("⚠️  BEST CHECKPOINT NOT LOADED:")
        logger.warning(f"   Using final epoch model (may be suboptimal)")
        logger.warning(f"   Consider investigating why checkpoint loading failed")
        logger.info("")
    
    # Ensure all improvement values are not None before ANY comparisons
    if train_improvement is None:
        train_improvement = 0.0
    if val_improvement is None:
        val_improvement = 0.0
    if train_val_gap_pct is None:
        train_val_gap_pct = 0.0
    
    # Quality assessment
    quality_issues = []
    recommendations = []
    
    # CRITICAL: Use VALIDATION loss for quality assessment, NOT training loss
    # Training loss is curriculum-weighted and changes dramatically across phases
    # Validation loss uses consistent weights and is a reliable metric
    
    # Check 1: Did validation loss actually improve?
    if val_improvement < 1.0:
        quality_issues.append("MINIMAL_LEARNING")
        recommendations.append("⚠️  Validation loss barely improved (<1%) - model may not have learned meaningful representations")
        recommendations.append("   → Consider increasing learning rate")
        recommendations.append("   → Verify self-supervised task is appropriate")
        recommendations.append("   → Check if dataset has sufficient complexity")
    
    # Check 2: Validation got worse
    if val_improvement < 0:
        quality_issues.append("VAL_DEGRADATION")
        recommendations.append(f"⚠️  Validation loss got worse ({val_improvement:.1f}%)")
        recommendations.append("   → Model overfit the training data")
        if best_checkpoint_loaded:
            recommendations.append("   → ✅ Best checkpoint was loaded to mitigate this issue")
        else:
            recommendations.append("   → ❌ Best checkpoint should have been loaded but wasn't - investigate why")
        recommendations.append("   → Consider early stopping for future runs")
    
    # Check 3: Good training
    # Handle nan/inf values in val_improvement (e.g., when initial validation loss was inf)
    val_improvement_valid = math.isfinite(val_improvement) if val_improvement is not None else False
    
    if val_improvement_valid and val_improvement > 10:
        logger.info("✅ QUALITY ASSESSMENT: GOOD")
        logger.info(f"   → Validation loss improved significantly ({val_improvement:.1f}%)")
        logger.info("   → Embeddings should be high quality for downstream tasks")
    elif val_improvement_valid and val_improvement > 1:
        logger.info("⚠️  QUALITY ASSESSMENT: ACCEPTABLE")
        logger.info(f"   → Validation loss improved moderately ({val_improvement:.1f}%)")
        logger.info("   → Embeddings should be usable but could be better")
    elif val_improvement_valid and val_improvement > -2:
        logger.info("⚠️  QUALITY ASSESSMENT: MARGINAL")
        logger.info(f"   → Validation loss barely changed ({val_improvement:.1f}%)")
        logger.info("   → Embeddings may have limited utility")
    else:
        if not val_improvement_valid:
            logger.warning("⚠️  QUALITY ASSESSMENT: UNKNOWN")
            logger.warning("   → Validation improvement could not be calculated (initial validation loss was inf)")
            logger.warning("   → Cannot assess embedding quality reliably")
        else:
            logger.error("❌ QUALITY ASSESSMENT: POOR")
            logger.error(f"   → Validation loss got worse or barely improved ({val_improvement:.1f}%)")
            logger.error("   → Embeddings may not be useful for downstream tasks")
            logger.error("   → Review training logs for failure modes")
    
    # Log recommendations
    if recommendations:
        logger.info("")
        logger.info("💡 RECOMMENDATIONS:")
        for rec in recommendations:
            logger.info(rec)
    
    logger.info("=" * 100)
    
    # Record quality checks if embedding_space is provided
    if embedding_space is not None:
        try:
            from featrix.neural.customer_quality_tracker import QualityCheckName, QualityGrade
            final_epoch = len(train_losses) - 1 if train_losses else 0
            qt = embedding_space.get_quality_tracker(final_epoch)
            
            # Record validation improvement
            val_improvement_grade = QualityGrade.from_improvement_pct(val_improvement)
            qt.record_check(
                name=QualityCheckName.VALIDATION_IMPROVEMENT,
                graded_score=val_improvement_grade,
                metadata={
                    "val_improvement_pct": val_improvement,
                    "initial_val_loss": initial_val_loss,
                    "final_val_loss": final_val_loss,
                    "best_val_loss": best_val_loss,
                }
            )
            
            # Record overall quality assessment
            if val_improvement_valid and val_improvement > 10:
                overall_grade = QualityGrade.A
            elif val_improvement_valid and val_improvement > 1:
                overall_grade = QualityGrade.B
            elif val_improvement_valid and val_improvement > -2:
                overall_grade = QualityGrade.C
            else:
                overall_grade = QualityGrade.F
            
            qt.record_check(
                name=QualityCheckName.OVERALL_QUALITY,
                graded_score=overall_grade,
                metadata={
                    "val_improvement_pct": val_improvement,
                    "train_val_gap_pct": train_val_gap_pct,
                    "quality_issues": quality_issues,
                    "best_checkpoint_loaded": best_checkpoint_loaded,
                }
            )
            
            # Record training stability
            if train_val_gap_pct > 20:
                stability_grade = QualityGrade.D  # Significant overfitting
            elif train_val_gap_pct > 10:
                stability_grade = QualityGrade.C  # Some overfitting
            elif train_val_gap_pct > 5:
                stability_grade = QualityGrade.B  # Acceptable gap
            else:
                stability_grade = QualityGrade.A  # Good stability
            
            qt.record_check(
                name=QualityCheckName.TRAINING_STABILITY,
                graded_score=stability_grade,
                metadata={
                    "train_val_gap_pct": train_val_gap_pct,
                    "overfitting_detected": train_val_gap_pct > 10,
                    "degradation_detected": val_improvement < 0,
                    "best_checkpoint_loaded": best_checkpoint_loaded,
                }
            )
        except Exception as e:
            logger.warning(f"⚠️  Failed to record quality checks: {e}")
    
    summary = {
        "status": "completed",
        "duration_minutes": duration_minutes,
        "epochs": len(train_losses),
        "initial_train_loss": initial_train_loss,
        "final_train_loss": final_train_loss,
        "train_improvement_pct": train_improvement,
        "initial_val_loss": initial_val_loss,
        "final_val_loss": final_val_loss,
        "val_improvement_pct": val_improvement,
        "best_train_loss": best_train_loss,
        "best_val_loss": best_val_loss,
        "train_val_gap": train_val_gap,
        "train_val_gap_pct": train_val_gap_pct,
        "quality_issues": quality_issues,
        "recommendations": recommendations
    }
    
    return summary


def embedding_space_debug_training(debug_class=None, epoch=None, embedding_space=None):
    """
    We keep this out of embedding_space so it doesn't get sucked into the pickle file.

    Before training, the caller calls this ```embedding_space_debug_training(debug_class=cls)```
    where cls has an epoch_finished method

    Args:
        debug_class:
        epoch:
        embedding_space:

    Returns:
        nada
    """
    try:
        if debug_class is not None:
            setattr(embedding_space_debug_training, "debug_class", debug_class)
        else:
            td = getattr(embedding_space_debug_training, "debug_class", None)
            if td is not None and hasattr(td, "epoch_finished"):
                td.epoch_finished(epoch_index=epoch, es=embedding_space)
    except Exception:
        traceback.print_exc()


class EmbeddingSpace(object):
    def __init__(
        self,
        train_input_data: FeatrixInputDataSet,
        val_input_data: FeatrixInputDataSet,
        output_debug_label: str = "No debug label specified",
        n_epochs: int = None,
        d_model: int = None,  # Will use config.json default if None
        training_state_path: str = None,
        encoder_config: Optional[FeatrixTableEncoderConfig] = None,
        string_cache: str = None,
        json_transformations: dict = None,
        version_info: dict = None,
        output_dir: str = None,
        name: str = None,
        required_child_es_mapping: dict = None,  # {col_name: session_id} mapping for child ES's
        sqlite_db_path: str = None,  # Path to SQLite database for PCA initialization
        user_metadata: dict = None,  # User metadata - arbitrary dict for user identification (max 32KB when serialized)
        skip_pca_init: bool = False,  # Skip PCA initialization (e.g., when reconstructing from checkpoint)
        codec_vocabulary_overrides: dict = None,  # {col_name: set of vocabulary members} for SET columns when reconstructing from checkpoint
        n_transformer_layers: int = None,  # Number of transformer layers in joint encoder (default: 3)
        n_attention_heads: int = None,  # Number of attention heads in joint encoder (default: 16)
        min_mask_ratio: float = 0.40,  # Minimum fraction of columns to mask in marginal reconstruction (default: 0.40 for balanced 50/50 split)
        max_mask_ratio: float = 0.60,  # Maximum fraction of columns to mask in marginal reconstruction (default: 0.60 for balanced 50/50 split)
        relationship_features: Optional[RelationshipFeatureConfig] = None,  # Relationship feature configuration (None = disabled)
    ):  # df, column_spec):
        
        assert isinstance(train_input_data, FeatrixInputDataSet)
        assert isinstance(val_input_data, FeatrixInputDataSet)

        self.string_cache = string_cache
        
        # Store name for identification and tracking
        self.name = name
        
        # Initialize schema history tracking
        from featrix.neural.schema_history import SchemaHistory
        self.schema_history = SchemaHistory()
        
        # Record original columns from upload
        original_columns = list(train_input_data.df.columns)
        upload_date = datetime.now().isoformat()
        self.schema_history.add_original_columns(original_columns, upload_date=upload_date)
        
        if self.name:
            logger.info(f"🏷️  EmbeddingSpace initialized with name: {self.name}")
        
        # Store JSON transformation metadata for consistent encoding
        self.json_transformations = json_transformations or {}
        if self.json_transformations:
            logger.info(f"🔧 EmbeddingSpace initialized with JSON transformations for {len(self.json_transformations)} columns")
        
        # Store child ES mapping for JSON column dependencies
        self.required_child_es_mapping = required_child_es_mapping or {}
        if self.required_child_es_mapping:
            logger.info(f"🔗 EmbeddingSpace initialized with {len(self.required_child_es_mapping)} child ES dependencies: {list(self.required_child_es_mapping.keys())}")
        
        # Store version information for traceability 
        self.version_info = version_info
        if self.version_info:
            logger.info(f"📦 EmbeddingSpace initialized with version info: {self.version_info}")
        
        # Store user metadata for identification
        self.user_metadata = user_metadata
        if self.user_metadata:
            logger.info(f"🏷️  EmbeddingSpace initialized with user metadata: {len(str(self.user_metadata))} chars")
        
        # Store masking parameters for marginal reconstruction
        self.min_mask_ratio = min_mask_ratio
        self.max_mask_ratio = max_mask_ratio
        
        # Store relationship features configuration
        self.relationship_features = relationship_features
        
        # Store BF16 mixed precision flag from config (can be overridden in train())
        # This is read from /sphere/app/config.json and persisted with the embedding space
        from featrix.neural.sphere_config import get_config
        self.use_bf16 = get_config().get_use_bf16()
        if self.use_bf16:
            logger.info("🔋 BF16 mixed precision enabled from config.json")
        
        # Extract null distribution stats from training data for masking constraints
        self.mean_nulls_per_row = getattr(train_input_data, 'mean_nulls_per_row', None)
        self.max_nulls_per_row = getattr(train_input_data, 'max_nulls_per_row', None)
        
        if self.mean_nulls_per_row is not None:
            max_mask_from_nulls = self.mean_nulls_per_row / 3.0
            logger.info(f"🎭 Masking strategy: {min_mask_ratio:.0%}-{max_mask_ratio:.0%} (balanced={min_mask_ratio >= 0.35 and max_mask_ratio <= 0.65})")
            logger.info(f"📊 Null distribution: mean={self.mean_nulls_per_row:.2f} nulls/row, max={self.max_nulls_per_row}")
            if max_mask_from_nulls > 0:
                logger.info(f"🚫 Masking constraint ACTIVE: Will not mask more than {int(max_mask_from_nulls)} columns (mean_nulls/3)")
            else:
                logger.info(f"✅ Masking constraint DISABLED: No nulls in data, will mask {min_mask_ratio:.0%}-{max_mask_ratio:.0%} of columns normally")
        else:
            logger.warning("⚠️  No null distribution stats found in training data - using default masking strategy")
            logger.info(f"🎭 Masking strategy: {min_mask_ratio:.0%}-{max_mask_ratio:.0%} (balanced={min_mask_ratio >= 0.35 and max_mask_ratio <= 0.65})")
         
        self._warningEncodeFields = []
        self._gotControlC = False
        self.n_epochs = n_epochs
        
        # Track reconstruction error history for trend analysis
        # Format: {col_name: [(epoch, avg_relative_error), ...]}
        self._reconstruction_error_history = defaultdict(list)
        
        # Get d_model from neural config if not explicitly provided
        if d_model is None:
            # Auto-compute based on number of columns
            num_columns = len(train_input_data.df.columns)
            d_model = get_config().auto_compute_d_model(num_columns)
            logger.info(f"🔧 Auto-computed d_model={d_model} based on {num_columns} columns")
        else:
            logger.info(f"🔧 Using provided d_model={d_model}")
        self.d_model = d_model
        
        # Store transformer architecture parameters (with defaults)
        # Auto-scale layers based on dataset size
        if n_transformer_layers is not None:
            self.n_transformer_layers = n_transformer_layers
        else:
            num_columns = len(train_input_data.df.columns)
            # More columns = more complexity = need deeper network
            if num_columns < 10:
                default_layers = 3
            elif num_columns < 30:
                default_layers = 5
            elif num_columns < 60:
                default_layers = 7
            else:
                default_layers = 8  # Large datasets with 60+ columns
            self.n_transformer_layers = default_layers
            logger.info(f"🔧 Auto-configured n_transformer_layers={default_layers} based on {num_columns} columns")
        
        # Auto-configure attention heads based on column relationships if not specified
        if n_attention_heads is None:
            from featrix.neural.relationship_estimator import estimate_pairwise_dependency_count_fast
            
            logger.info("🔍 Auto-configuring attention heads based on column relationships...")
            
            # Scale sampling based on dataset size
            num_columns = len(train_input_data.df.columns)
            total_possible_pairs = num_columns * (num_columns - 1) // 2
            
            # Handle edge case: no pairs possible (0 or 1 columns)
            if total_possible_pairs == 0:
                # Can't analyze relationships with no pairs - use default
                n_heads = 8  # Doubled from 4
                logger.info(f"   ⚠️  No column pairs available (num_columns={num_columns}) → using default {n_heads} attention heads")
                self.n_attention_heads = n_heads
            else:
                # Sample at least 30% of pairs, more for smaller datasets
                if num_columns < 30:
                    sample_fraction = 0.8  # Small datasets: test most pairs
                elif num_columns < 60:
                    sample_fraction = 0.5  # Medium datasets: test half
                else:
                    sample_fraction = 0.3  # Large datasets: test at least 30%
                
                n_pairs_to_test = min(int(total_possible_pairs * sample_fraction), 5000)
                n_pairs_to_test = max(600, n_pairs_to_test)  # At least 600
                
                logger.info(f"   Testing {n_pairs_to_test} of {total_possible_pairs} possible pairs ({n_pairs_to_test/total_possible_pairs*100:.1f}%)")
                
                relationship_analysis = estimate_pairwise_dependency_count_fast(
                    train_input_data.df,
                    n_pairs=n_pairs_to_test,
                    repeat=5,  # More runs for better estimate
                    max_pairs=5000,
                    random_state=42
                )
                
                summary = relationship_analysis['summary']
                
                # This should never have 'error' key anymore - crashes if scipy missing
                assert 'error' not in summary, f"Relationship estimation returned error: {summary.get('error')}"
                
                estimated_edges = summary['estimated_edges_median']
                total_pairs = summary['total_pairs']
                n_cols = summary['n_cols']
                
                # More aggressive formula for large datasets with many columns
                # Large datasets have more subtle interactions that need more attention
                if n_cols >= 60:
                    relationships_per_head = 3  # More aggressive for large datasets
                else:
                    relationships_per_head = 5  # Conservative for small datasets
                
                # Minimum heads based on dataset size:
                # - > 10 columns: minimum 8 heads (never go below)
                # - <= 10 columns: minimum 4 heads (small datasets can use fewer)
                # Round to power of 2 for efficiency
                min_heads = 8 if n_cols > 10 else 4
                
                if estimated_edges == 0:
                    # Even with no detected relationships, use appropriate baseline
                    if n_cols >= 60:
                        n_heads = 16
                    elif n_cols > 10:
                        n_heads = 8  # Minimum for datasets with > 10 columns
                    else:
                        n_heads = 4  # Can use 4 for very small datasets (<= 10 columns)
                    logger.info(f"   📊 No significant relationships detected → using baseline {n_heads} heads for {n_cols} columns (min={min_heads})")
                else:
                    n_heads_raw = max(min_heads, estimated_edges // relationships_per_head)
                    n_heads = 2 ** int(np.log2(max(min_heads, n_heads_raw)))  # Round to power of 2, but never below min_heads
                    # Cap at 64 for large datasets (60+ columns), 32 for smaller ones (doubled from 32/16)
                    max_heads = 64 if n_cols >= 60 else 32
                    n_heads = min(max_heads, n_heads)
                    
                    logger.info(f"   📊 Columns: {n_cols}, Total pairs: {total_pairs}")
                    logger.info(f"   🔗 Dependent pairs: ~{estimated_edges} ({estimated_edges / total_pairs * 100:.1f}%)")
                    logger.info(f"   🎯 Configured {n_heads} attention heads (~{relationships_per_head} relationships per head)")
                    logger.info(f"   ⚙️  Formula: {estimated_edges} edges ÷ {relationships_per_head} = {n_heads_raw} → {n_heads} (rounded to power of 2, min={min_heads})")
                
                self.n_attention_heads = n_heads
        else:
            self.n_attention_heads = n_attention_heads
            logger.info(f"🔧 Using user-specified {self.n_attention_heads} attention heads")
        
        logger.info(f"🔧 Transformer architecture: {self.n_transformer_layers} layers, {self.n_attention_heads} attention heads")

        self.output_debug_label = output_debug_label
        self.train_input_data = train_input_data
        self.val_input_data = val_input_data

        self.col_codecs = {}
        self.column_spec = train_input_data.column_codecs()
        
        # Store codec vocabulary overrides (for checkpoint reconstruction)
        self.codec_vocabulary_overrides = codec_vocabulary_overrides or {}
        if self.codec_vocabulary_overrides:
            logger.info(f"📚 Using vocabulary overrides for {len(self.codec_vocabulary_overrides)} SET columns (checkpoint reconstruction)")

        self.availableColumns = list(self.column_spec.keys())
        self._create_codecs()
        
        # Filter out JSON columns that were skipped during codec creation
        # This prevents KeyError when creating encoder configs for columns that don't have codecs
        json_cols_to_remove = []
        for col_name in list(self.column_spec.keys()):
            if col_name not in self.col_codecs:
                json_cols_to_remove.append(col_name)
                logger.info(f"🔍 Removing '{col_name}' from column_spec (no codec created)")
                del self.column_spec[col_name]
        
        if json_cols_to_remove:
            logger.info(f"   ✅ Removed {len(json_cols_to_remove)} JSON columns from column_spec: {json_cols_to_remove}")

        # Construct the dataset for self-supervised training.
        colsForCodingCount = train_input_data.get_columns_with_codec_count()
        self.train_dataset = SuperSimpleSelfSupervisedDataset(
            self.train_input_data.df,
            codecs=self.col_codecs,
            row_meta_data=train_input_data.project_row_meta_data_list,
            casted_df=train_input_data.casted_df,
        )

        self.val_dataset = SuperSimpleSelfSupervisedDataset(
            self.val_input_data.df,
            codecs=self.col_codecs,
            row_meta_data=val_input_data.project_row_meta_data_list,
            casted_df=val_input_data.casted_df,
        )

        self.callbacks = defaultdict(dict)

        self.meta_from_dataspace = {}

        self.column_tree = self.train_input_data.column_tree()
        self.col_order = flatten(self.column_tree)
        
        # Filter out columns that don't have codecs (e.g., skipped JSON columns)
        # This ensures col_order only contains columns we actually have codecs for
        original_col_order_len = len(self.col_order)
        self.col_order = [col for col in self.col_order if col in self.col_codecs]
        self.n_all_cols = len(self.col_order)
        
        if len(self.col_order) < original_col_order_len:
            removed_count = original_col_order_len - len(self.col_order)
            logger.info(f"   ✅ Filtered {removed_count} columns from col_order (no codecs created)")
        
        # Initialize col_types from column_spec (maps col_name -> ColumnType)
        # This is used for model package metadata and feature inventory
        self.col_types = {}
        for col_name in self.col_order:
            # Try to get from column_spec first
            if col_name in self.column_spec:
                self.col_types[col_name] = self.column_spec[col_name]
            # Fallback: derive from codec if available
            elif col_name in self.col_codecs:
                codec = self.col_codecs[col_name]
                if hasattr(codec, 'get_codec_name'):
                    self.col_types[col_name] = codec.get_codec_name()
                else:
                    self.col_types[col_name] = "unknown"
            else:
                self.col_types[col_name] = "unknown"
        
        # Initialize mask distribution tracker
        self.mask_tracker = None  # Will be initialized in train() with output_dir
        
        # Initialize customer quality trackers (one per epoch)
        # Format: {epoch: CustomerQualityTracker}
        from featrix.neural.customer_quality_tracker import CustomerQualityTracker
        self.customer_quality_trackers: Dict[int, CustomerQualityTracker] = {}

        if encoder_config is None:
            self.encoder_config = self.get_default_table_encoder_config(
                d_model,
                self.col_codecs,
                self.col_order,
                self.column_spec,
                relationship_features=relationship_features,
            )
        else:
            self.encoder_config = encoder_config
            # Inject relationship_features into existing config if provided
            if relationship_features is not None:
                self.encoder_config.joint_encoder_config.relationship_features = relationship_features

        # Get hybrid groups from training data if available
        hybrid_groups = getattr(train_input_data, 'hybrid_groups', None) or {}
        if hybrid_groups:
            logger.info(f"🔗 HYBRID COLUMNS: Detected {len(hybrid_groups)} hybrid groups")
            merge_groups = [g for g in hybrid_groups.values() if g.get('strategy') == 'merge']
            rel_groups = [g for g in hybrid_groups.values() if g.get('strategy') == 'relationship']
            if merge_groups:
                logger.info(f"   └─ {len(merge_groups)} MERGE groups (addresses, coordinates)")
            if rel_groups:
                logger.info(f"   └─ {len(rel_groups)} RELATIONSHIP groups (entity attributes)")
            for group_name, group_info in hybrid_groups.items():
                logger.info(f"   {group_name}: {group_info['type']} ({group_info['strategy']}) - {len(group_info['columns'])} columns")
        else:
            logger.info(f"ℹ️  HYBRID COLUMNS: No hybrid groups detected (using standard column encoding)")
        
        # Store for later inspection
        self.hybrid_groups = hybrid_groups
        
        # Feature flag for hybrid encoders (default: True to enable the feature)
        enable_hybrid_encoders = getattr(train_input_data, 'enable_hybrid_detection', True)
        
        self.encoder = FeatrixTableEncoder(
            col_codecs=self.col_codecs,
            config=self.encoder_config,
            min_mask_ratio=self.min_mask_ratio,
            max_mask_ratio=self.max_mask_ratio,
            mean_nulls_per_row=self.mean_nulls_per_row,
            hybrid_groups=hybrid_groups,
            enable_hybrid_encoders=enable_hybrid_encoders,
        )
        self.encoder.to(get_device())
        self.model_param_count = self.encoder.count_model_parameters()
        
        # Log model parameter count as soon as we know it
        logger.info(f"📊 Model Parameters: {self.model_param_count['total_params']:,} total, "
                   f"{self.model_param_count['total_trainable_params']:,} trainable")
        
        # Column encoders with breakdown if available
        if 'column_encoders_params' in self.model_param_count:
            logger.info(f"   └─ Column encoders: {self.model_param_count['column_encoders_params']:,} params "
                   f"({self.model_param_count.get('column_encoders_trainable_params', 0):,} trainable)")
            
            # Show breakdown if hybrid encoders exist
            if 'column_encoders_breakdown' in self.model_param_count:
                breakdown = self.model_param_count['column_encoders_breakdown']
                logger.info(f"      ├─ Regular columns: {breakdown['regular_columns']:,} params "
                       f"({breakdown['regular_columns_trainable']:,} trainable)")
                if breakdown['hybrid_merge_encoders'] > 0:
                    logger.info(f"      └─ Hybrid MERGE encoders: {breakdown['hybrid_merge_encoders']:,} params "
                           f"({breakdown['hybrid_merge_trainable']:,} trainable) "
                           f"[{breakdown['hybrid_merge_count']} encoder(s)]")
        
        # Joint encoder with breakdown if available
        if 'joint_encoder_params' in self.model_param_count:
            logger.info(f"   └─ Joint encoder: {self.model_param_count['joint_encoder_params']:,} params "
                   f"({self.model_param_count.get('joint_encoder_trainable_params', 0):,} trainable)")
            
            # Show breakdown if relationship groups exist
            if 'joint_encoder_breakdown' in self.model_param_count:
                breakdown = self.model_param_count['joint_encoder_breakdown']
                logger.info(f"      ├─ Transformer: {breakdown['transformer']:,} params "
                       f"({breakdown['transformer_trainable']:,} trainable)")
                if breakdown['relationship_groups'] > 0:
                    logger.info(f"      └─ Relationship groups: {breakdown['relationship_groups']:,} params "
                           f"({breakdown['relationship_groups_trainable']:,} trainable) "
                           f"[{breakdown['relationship_group_count']} group(s)]")
        
        # Set embedding space on all JSON codecs now that EmbeddingSpace is fully initialized
        # This allows JsonCodec to cache embeddings (retry pre-caching if it was skipped)
        from featrix.neural.json_codec import JsonCodec
        for col_name, codec in self.col_codecs.items():
            if isinstance(codec, JsonCodec):
                # Only set if it doesn't have a child ES (child ES codecs use their own ES)
                if not hasattr(codec, 'child_es_session_id') or codec.child_es_session_id is None:
                    codec.set_embedding_space(self)
                    logger.info(f"🔗 Set embedding space on JsonCodec '{col_name}'")
                    # Retry pre-caching if it was skipped during init (when embedding_space was None)
                    # Get initial values from train_input_data (same as create_json_codec does)
                    if codec.json_cache and codec.json_cache.embedding_space is not None:
                        try:
                            df_col = self.train_input_data.df[col_name]
                            initial_values = df_col.dropna().tolist()[:1000]  # Limit to first 1000 for caching
                            if initial_values:
                                logger.info(f"🔄 Retrying pre-cache for JsonCodec '{col_name}' ({len(initial_values)} values)")
                                codec.json_cache.run_batch(initial_values)
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to retry pre-cache for JsonCodec '{col_name}': {e}")

        self.es_neural_attrs = {
            "name": self.name,
            "d_model": self.d_model,
            "col_order": self.col_order,
            "col_tree": self.column_tree,
            "n_all_cols": self.n_all_cols,
            "len_df": self.len_df(),
            "num_cols": len(self.train_input_data.df.columns),
            "ignore_cols": train_input_data.ignore_cols,
            "input_data_debug": train_input_data.detectorDebugInfo,
            # "self_supervised_config": asdict(self.train_dataset.config),
            "colsForCodingCount": colsForCodingCount,
            "codec_mapping": self.get_codec_meta(),
            "json_transformations": self.json_transformations,  # Include JSON transformation metadata
            "version_info": self.version_info if self.version_info else None,  # Include version info for traceability (already a dict)
            "kl_divergences": getattr(train_input_data, 'kl_divergences_vs_val', {}),  # Distribution match metrics
        }

        self.training_info = {}

        # Training state fields
        # Default to checkpoint_resume_training for clearer naming
        if training_state_path:
            self.training_state_path = training_state_path
        else:
            # Transform old "training_state" to new "checkpoint_resume_training" if present
            default_path = f"{os.getcwd()}/checkpoint_resume_training"
            self.training_state_path = default_path
        self.training_state = {}
        self.training_progress_data = {}
        
        # Training timeline tracking - initialize here to ensure it's always present
        self._training_timeline = []
        self._corrective_actions = []
        
        # Warning state tracking - track active warnings to detect start/stop
        self._active_warnings = {}  # {warning_type: {'start_epoch': int, 'details': dict}}
        self._tiny_grad_warned_this_epoch = False  # Track if we've warned about tiny gradients this epoch

        # Set output directory with fallback to config
        if output_dir is None:
            try:
                config_instance = get_config()
                self.output_dir = str(config_instance.output_dir)
            except:
                self.output_dir = "./featrix_output"  # Ultimate fallback
        else:
            self.output_dir = output_dir
        
        # Store SQLite database path for PCA initialization
        self.sqlite_db_path = sqlite_db_path
        
        # Initialize K-fold cross-validation tracking
        self._kv_fold_epoch_offset = None
        
        # Initialize curriculum learning and early stopping tracking
        self._forced_spread_finalization = False
        self._spread_only_tracker = {
            'spread_only_epochs_completed': 0,
            'in_spread_phase': False
        }
        
        # WEIGHT INITIALIZATION
        # Configurable via config.json: "es_weight_initialization": "random" or "pca_string"
        # Default is "random" (standard PyTorch init)
        # Note: get_config is already imported at top of file
        es_init_strategy = get_config().get_es_weight_initialization()
        
        if skip_pca_init:
            logger.info("⏭️  Skipping PCA initialization (reconstructing from checkpoint or explicitly disabled)")
        elif es_init_strategy == "pca_string":
            logger.info(f"🎲 Using PCA-based weight initialization (es_weight_initialization='{es_init_strategy}')")
            self._initialize_weights_from_pca(train_input_data)
        else:
            # Default: random initialization (standard PyTorch)
            logger.info(f"🎲 Using random weight initialization (es_weight_initialization='{es_init_strategy}')")
    
    @classmethod
    def extend_from_existing(
        cls,
        existing_es: 'EmbeddingSpace',
        enriched_train_df: pd.DataFrame,
        enriched_val_df: Optional[pd.DataFrame] = None,
        n_epochs: int = None,
        batch_size: int = None,
        output_dir: str = None,
        name: str = None,
        feature_metadata: Optional[Dict[str, Any]] = None
    ) -> 'EmbeddingSpace':
        """
        Extend an existing EmbeddingSpace with new feature columns.
        
        This method creates a new ES that includes both the original columns AND
        new engineered feature columns. The existing encoder weights are preserved
        and only the new columns are trained, making this much faster than retraining
        from scratch.
        
        WORKFLOW:
        1. Identify new columns (not in existing ES)
        2. Create InputDataSets with enriched data
        3. Initialize new ES with existing encoder weights
        4. Create codecs for new columns only
        5. Train for shorter period (default: original_epochs / 4)
        6. Return extended ES
        
        TRAINING STRATEGY:
        - Phase 1 (epochs/8): Freeze existing encoders, train only new column encoders
        - Phase 2 (epochs/8): Unfreeze everything, fine-tune jointly
        - Total: epochs/4 (much faster than full retraining)
        
        Args:
            existing_es: The EmbeddingSpace to extend
            enriched_train_df: Training DataFrame with new columns added
            enriched_val_df: Validation DataFrame with new columns (optional, will split if None)
            n_epochs: Training epochs for extension (default: original_epochs / 4)
            batch_size: Training batch size (default: use existing ES batch size)
            output_dir: Output directory for extended ES
            name: Name for extended ES (default: f"{existing_es.name}_extended")
            feature_metadata: Metadata about new features (for provenance tracking)
            
        Returns:
            New EmbeddingSpace with extended columns
            
        Example:
            # Load existing ES
            es_v1 = load_embedding_space("embedding_space.pkl")
            
            # Apply feature engineering to data
            engineer = FeatureEngineer.from_json("features.json")
            enriched_train_df = engineer.fit_transform(train_df)
            enriched_val_df = engineer.transform(val_df)
            
            # Extend ES with new features
            es_v2 = EmbeddingSpace.extend_from_existing(
                existing_es=es_v1,
                enriched_train_df=enriched_train_df,
                enriched_val_df=enriched_val_df,
                n_epochs=12,  # If original was 50, use 50/4 = 12
                feature_metadata={
                    "applied_features": ["younger_borrower", "high_debt_ratio"],
                    "source": "feature_suggestion_history.json"
                }
            )
            
            # Train predictor on extended ES
            sp = SinglePredictor(es_v2, predictor)
            sp.train()
        """
        from featrix.neural.input_data_set import FeatrixInputDataSet
        
        logger.info("=" * 80)
        logger.info("🔧 EXTENDING EMBEDDING SPACE WITH NEW FEATURES")
        logger.info("=" * 80)
        
        # Identify new columns
        existing_columns = set(existing_es.col_codecs.keys())
        enriched_columns = set(enriched_train_df.columns)
        new_columns = enriched_columns - existing_columns
        
        if not new_columns:
            logger.warning("⚠️  No new columns found - enriched DataFrame has same columns as existing ES")
            logger.warning(f"   Existing ES columns: {sorted(existing_columns)}")
            logger.warning(f"   Enriched DF columns: {sorted(enriched_columns)}")
            raise ValueError("Cannot extend ES: no new columns to add")
        
        logger.info(f"📊 Extension Analysis:")
        logger.info(f"   Existing columns: {len(existing_columns)}")
        logger.info(f"   New columns: {len(new_columns)}")
        logger.info(f"   Extended total: {len(enriched_columns)}")
        logger.info(f"")
        logger.info(f"🆕 New columns being added:")
        for col in sorted(new_columns):
            logger.info(f"   • {col}")
        logger.info("")
        
        # Determine training epochs (default: original / 4)
        if n_epochs is None:
            original_epochs = getattr(existing_es, 'n_epochs', 50)
            n_epochs = max(10, original_epochs // 4)  # At least 10 epochs
            logger.info(f"📅 Auto-determined training epochs: {n_epochs} (original: {original_epochs}, using 1/4)")
        
        # Use existing batch size if not specified
        if batch_size is None:
            batch_size = getattr(existing_es, 'batch_size', 128)
            logger.info(f"📦 Using existing batch size: {batch_size}")
        
        # Create name for extended ES
        if name is None:
            base_name = getattr(existing_es, 'name', 'unnamed')
            name = f"{base_name}_extended"
        
        # Split validation data if not provided
        if enriched_val_df is None:
            logger.info("📂 Splitting enriched data (80/20 train/val)")
            train_size = int(len(enriched_train_df) * 0.8)
            enriched_val_df = enriched_train_df.iloc[train_size:].copy()
            enriched_train_df = enriched_train_df.iloc[:train_size].copy()
        
        logger.info(f"   Train: {len(enriched_train_df)} rows")
        logger.info(f"   Val: {len(enriched_val_df)} rows")
        logger.info("")
        
        # Create InputDataSets from enriched DataFrames
        logger.info("🔧 Creating InputDataSets with enriched data...")
        
        # Get encoder overrides from existing ES for consistency
        existing_encoder_overrides = {}
        for col_name, codec in existing_es.col_codecs.items():
            if col_name in enriched_train_df.columns:
                existing_encoder_overrides[col_name] = existing_es.col_types.get(col_name, "unknown")
        
        train_input_data = FeatrixInputDataSet(
            df=enriched_train_df,
            ignore_cols=[],
            limit_rows=None,
            encoder_overrides=existing_encoder_overrides,
            dataset_title=f"{name}_train"
        )
        
        val_input_data = FeatrixInputDataSet(
            df=enriched_val_df,
            ignore_cols=[],
            limit_rows=None,
            encoder_overrides=existing_encoder_overrides,
            dataset_title=f"{name}_val"
        )
        
        logger.info(f"✅ InputDataSets created")
        logger.info("")
        
        # Create new ES instance (will create codecs for ALL columns including new ones)
        logger.info("🏗️  Creating extended EmbeddingSpace...")
        extended_es = cls(
            train_input_data=train_input_data,
            val_input_data=val_input_data,
            output_debug_label=f"Extended from {existing_es.name or 'unnamed'}",
            n_epochs=n_epochs,
            d_model=existing_es.d_model,
            output_dir=output_dir,
            name=name,
            string_cache=existing_es.string_cache,
            n_transformer_layers=getattr(existing_es.encoder.joint_encoder, 'num_layers', 3) if hasattr(existing_es, 'encoder') else 3,
            n_attention_heads=getattr(existing_es.encoder.joint_encoder.layers[0].self_attn, 'num_heads', 16) if hasattr(existing_es, 'encoder') and hasattr(existing_es.encoder, 'joint_encoder') else 16,  # Doubled from 8 to 16
            min_mask_ratio=getattr(existing_es, 'min_mask_ratio', 0.40),
            max_mask_ratio=getattr(existing_es, 'max_mask_ratio', 0.60),
        )
        
        # Copy encoder weights for existing columns
        logger.info("📋 Copying encoder weights from existing ES...")
        logger.info(f"   Existing ES has {len(existing_es.col_codecs)} column encoders")
        logger.info(f"   Extended ES has {len(extended_es.col_codecs)} column encoders")
        
        if hasattr(existing_es, 'encoder') and hasattr(extended_es, 'encoder'):
            # Copy weights for columns that exist in both
            copied_count = 0
            for col_name in existing_columns:
                if col_name in extended_es.col_codecs:
                    # Copy encoder weights for this column
                    try:
                        existing_encoder = existing_es.encoder.column_encoder.encoders.get(col_name)
                        extended_encoder = extended_es.encoder.column_encoder.encoders.get(col_name)
                        
                        if existing_encoder is not None and extended_encoder is not None:
                            extended_encoder.load_state_dict(existing_encoder.state_dict())
                            copied_count += 1
                    except Exception as e:
                        logger.warning(f"   ⚠️  Could not copy weights for '{col_name}': {e}")
            
            logger.info(f"   ✅ Copied weights for {copied_count}/{len(existing_columns)} existing columns")
            
            # Copy joint encoder weights (transformer layers)
            try:
                if hasattr(existing_es.encoder, 'joint_encoder') and hasattr(extended_es.encoder, 'joint_encoder'):
                    extended_es.encoder.joint_encoder.load_state_dict(existing_es.encoder.joint_encoder.state_dict())
                    logger.info(f"   ✅ Copied joint encoder (transformer) weights")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not copy joint encoder weights: {e}")
        
        logger.info("")
        
        # Store extension metadata
        extended_es.extension_metadata = {
            "extended_from_es_name": getattr(existing_es, 'name', 'unnamed'),
            "extended_from_es_version": getattr(existing_es, 'version_info', {}),
            "extension_date": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
            "new_columns_added": sorted(list(new_columns)),
            "original_column_count": len(existing_columns),
            "extended_column_count": len(enriched_columns),
            "training_epochs_used": n_epochs,
            "feature_metadata": feature_metadata or {}
        }
        
        logger.info(f"📝 Extension metadata stored:")
        logger.info(f"   Extended from: {extended_es.extension_metadata['extended_from_es_name']}")
        logger.info(f"   New columns: {len(new_columns)}")
        logger.info(f"   Training epochs: {n_epochs}")
        logger.info("=" * 80)
        logger.info("")
        
        return extended_es
    
    def compare_row_embeddings(
        self,
        other_es: 'EmbeddingSpace',
        rows_df: pd.DataFrame,
        row_id_column: Optional[str] = None,
        top_n_movers: int = 10
    ) -> Dict[str, Any]:
        """
        Compare row embeddings between this ES and another ES (typically extended version).
        
        This is useful for understanding how much embeddings change when features are added.
        Large movements indicate the new features are significantly changing the representation.
        
        Args:
            other_es: Another EmbeddingSpace to compare against (e.g., extended version)
            rows_df: DataFrame with rows to compare (should have columns from both ES versions)
            row_id_column: Column to use as row identifier (optional, uses index if None)
            top_n_movers: Number of top movers to return in results
            
        Returns:
            Dict with comparison statistics:
            {
                "mean_distance": float,  # Average L2 distance between embeddings
                "median_distance": float,
                "max_distance": float,
                "min_distance": float,
                "top_movers": [  # Rows that moved the most
                    {"row_id": ..., "distance": ..., "percentile": ...},
                    ...
                ],
                "row_distances": {row_id: distance, ...}  # All rows
            }
            
        Example:
            # Compare original vs extended ES
            es_v1 = load_embedding_space("es_v1.pkl")
            es_v2 = load_embedding_space("es_v2_extended.pkl")
            
            # Get embeddings for test rows
            comparison = es_v1.compare_row_embeddings(
                other_es=es_v2,
                rows_df=test_df,
                row_id_column='customer_id',
                top_n_movers=20
            )
            
            print(f"Mean embedding shift: {comparison['mean_distance']:.4f}")
            print("Top movers:")
            for mover in comparison['top_movers'][:5]:
                print(f"  Row {mover['row_id']}: moved {mover['distance']:.4f} (top {mover['percentile']:.1f}%)")
        """
        import numpy as np
        from scipy.spatial.distance import euclidean
        
        logger.info("=" * 80)
        logger.info("🔍 COMPARING ROW EMBEDDINGS BETWEEN ES VERSIONS")
        logger.info("=" * 80)
        
        if row_id_column and row_id_column not in rows_df.columns:
            raise ValueError(f"Row ID column '{row_id_column}' not found in DataFrame")
        
        # Get row identifiers
        if row_id_column:
            row_ids = rows_df[row_id_column].tolist()
        else:
            row_ids = rows_df.index.tolist()
        
        logger.info(f"Comparing embeddings for {len(rows_df)} rows")
        logger.info(f"ES 1 columns: {len(self.col_codecs)}")
        logger.info(f"ES 2 columns: {len(other_es.col_codecs)}")
        logger.info("")
        
        # Compute embeddings for each row in both ES versions
        distances = {}
        embeddings_v1 = []
        embeddings_v2 = []
        
        logger.info("Computing embeddings...")
        for idx, (_, row) in enumerate(rows_df.iterrows()):
            row_dict = row.to_dict()
            row_id = row_ids[idx]
            
            try:
                # Get embedding from both ES versions
                emb_v1 = self.encode_record(row_dict, squeeze=True)
                emb_v2 = other_es.encode_record(row_dict, squeeze=True)
                
                # Convert to numpy if tensors
                if hasattr(emb_v1, 'cpu'):
                    emb_v1 = emb_v1.cpu().detach().numpy()
                if hasattr(emb_v2, 'cpu'):
                    emb_v2 = emb_v2.cpu().detach().numpy()
                
                # Compute L2 distance
                distance = euclidean(emb_v1, emb_v2)
                distances[row_id] = float(distance)
                
                embeddings_v1.append(emb_v1)
                embeddings_v2.append(emb_v2)
                
            except Exception as e:
                logger.warning(f"Could not encode row {row_id}: {e}")
                distances[row_id] = None
        
        # Filter out failed rows
        valid_distances = {k: v for k, v in distances.items() if v is not None}
        
        if not valid_distances:
            raise ValueError("No valid embeddings could be computed for comparison")
        
        # Compute statistics
        distance_values = list(valid_distances.values())
        mean_dist = np.mean(distance_values)
        median_dist = np.median(distance_values)
        max_dist = np.max(distance_values)
        min_dist = np.min(distance_values)
        std_dist = np.std(distance_values)
        
        logger.info("")
        logger.info("📊 EMBEDDING DISTANCE STATISTICS:")
        logger.info(f"   Mean distance: {mean_dist:.4f}")
        logger.info(f"   Median distance: {median_dist:.4f}")
        logger.info(f"   Std deviation: {std_dist:.4f}")
        logger.info(f"   Min distance: {min_dist:.4f}")
        logger.info(f"   Max distance: {max_dist:.4f}")
        logger.info("")
        
        # Find top movers (rows with largest distance)
        sorted_distances = sorted(valid_distances.items(), key=lambda x: x[1], reverse=True)
        top_movers = []
        
        for rank, (row_id, distance) in enumerate(sorted_distances[:top_n_movers], 1):
            percentile = (1 - rank / len(valid_distances)) * 100
            top_movers.append({
                'row_id': row_id,
                'distance': distance,
                'rank': rank,
                'percentile': percentile
            })
        
        logger.info(f"🏃 TOP {min(top_n_movers, len(top_movers))} MOVERS (rows with biggest embedding shifts):")
        for mover in top_movers[:5]:
            logger.info(f"   #{mover['rank']}: Row {mover['row_id']} - distance {mover['distance']:.4f} (top {mover['percentile']:.1f}%)")
        
        logger.info("=" * 80)
        logger.info("")
        
        return {
            'mean_distance': mean_dist,
            'median_distance': median_dist,
            'std_distance': std_dist,
            'max_distance': max_dist,
            'min_distance': min_dist,
            'num_rows_compared': len(valid_distances),
            'top_movers': top_movers,
            'row_distances': valid_distances,
            'distance_distribution': {
                'quartiles': {
                    'q1': np.percentile(distance_values, 25),
                    'q2': np.percentile(distance_values, 50),
                    'q3': np.percentile(distance_values, 75)
                },
                'percentiles': {
                    'p90': np.percentile(distance_values, 90),
                    'p95': np.percentile(distance_values, 95),
                    'p99': np.percentile(distance_values, 99)
                }
            }
        }
    
    def _track_warning_in_timeline(self, epoch_idx, warning_type, is_active, details=None):
        """
        Track warnings in timeline - add entries when warnings start/stop.
        
        Args:
            epoch_idx: Current epoch number
            warning_type: Type of warning (e.g., 'NO_LEARNING', 'TINY_GRADIENTS', 'SEVERE_OVERFITTING')
            is_active: True if warning is currently active, False if resolved
            details: Dict with warning-specific details (loss values, gradients, etc.)
        """
        if not hasattr(self, '_active_warnings'):
            self._active_warnings = {}
        
        if details is None:
            details = {}
        
        was_active = warning_type in self._active_warnings
        
        if is_active and not was_active:
            # Warning just started
            warning_entry = {
                "epoch": epoch_idx,
                "timestamp": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
                "event_type": "warning_start",
                "warning_type": warning_type,
                "description": f"{warning_type} warning detected",
                "details": details.copy()
            }
            self._training_timeline.append(warning_entry)
            self._active_warnings[warning_type] = {
                'start_epoch': epoch_idx,
                'details': details.copy()
            }
            logger.info(f"📊 Timeline: {warning_type} warning started at epoch {epoch_idx}")
            
        elif not is_active and was_active:
            # Warning just resolved
            start_epoch = self._active_warnings[warning_type]['start_epoch']
            duration = epoch_idx - start_epoch
            
            warning_entry = {
                "epoch": epoch_idx,
                "timestamp": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
                "event_type": "warning_resolved",
                "warning_type": warning_type,
                "description": f"{warning_type} warning resolved",
                "start_epoch": start_epoch,
                "duration_epochs": duration,
                "details": details.copy() if details else {}
            }
            self._training_timeline.append(warning_entry)
            del self._active_warnings[warning_type]
            logger.info(f"📊 Timeline: {warning_type} warning resolved at epoch {epoch_idx} (duration: {duration} epochs)")
            
        elif is_active and was_active:
            # Warning still active - update details but don't add new entry
            self._active_warnings[warning_type]['details'].update(details)

    def _initialize_weights_from_pca(self, input_data):
        """Initialize network weights using PCA statistics from sentence transformer embeddings.
        
        This method tries multiple sources for embeddings:
        1. SQLite database (if sqlite_db_path provided and embeddings exist)
        2. Generate on-the-fly from input_data DataFrame (fallback)
        
        This decouples PCA initialization from SQLite format dependency.
        """
        logger.info("🔮 PCA-BASED WEIGHT INITIALIZATION ENABLED")
        
        # torch is already imported at module level, but ensure it's available
        # Import sklearn here since it's only needed for PCA
        from sklearn.decomposition import PCA
        embeddings_384d = None
        embedding_device = 'cpu'  # Default, will be updated if CUDA is available
        
        # Strategy 1: Try to load from SQLite database (if available)
        db_path = self.sqlite_db_path
        if db_path:
            try:
                if os.path.exists(db_path):
                    db_path_lower = db_path.lower()
                    if db_path_lower.endswith('.db') or db_path_lower.endswith('.sqlite') or db_path_lower.endswith('.sqlite3'):
                        logger.info(f"📂 Attempting to load embeddings from SQLite: {db_path}")
                        
                        # CRITICAL: Use read-only mode since we're only reading from an existing file
                        # This prevents creating an empty file if the path is wrong
                        conn = sqlite3.connect(f'file:///{os.path.realpath(db_path)}?mode=ro', uri=True)
                        cursor = conn.cursor()
                        
                        # Check if column exists (table name is "data" by default in csv_to_sqlite)
                        cursor.execute("PRAGMA table_info(data)")
                        columns = [row[1] for row in cursor.fetchall()]
                        
                        if '__featrix_sentence_embedding_384d' in columns:
                            # Load all embeddings
                            cursor.execute("SELECT __featrix_sentence_embedding_384d FROM data ORDER BY rowid")
                            rows = cursor.fetchall()
                            
                            embeddings_384d = []
                            for row in rows:
                                if row[0] is not None:
                                    embedding = pickle.loads(row[0])
                                    embeddings_384d.append(embedding)
                            
                            if embeddings_384d:
                                embeddings_384d = np.array(embeddings_384d, dtype=np.float32)
                                logger.info(f"✅ Loaded {len(embeddings_384d)} embeddings (384d) from SQLite")
                            else:
                                logger.info("ℹ️  SQLite database has embedding column but no embeddings found")
                        
                        conn.close()
            except Exception as e:
                logger.debug(f"Could not load embeddings from SQLite: {e}")
        
        # Strategy 2: Generate embeddings on-the-fly from input_data (if SQLite not available)
        if embeddings_384d is None:
            logger.info("📊 SQLite embeddings not available - generating embeddings on-the-fly from input data...")
            try:
                import pandas as pd
                # Note: No longer importing SentenceTransformer - using string server client instead
                # torch is already imported at the top of this function
                
                # Get DataFrame from input_data
                df = input_data.df
                if df is None or len(df) == 0:
                    logger.warning("⚠️  Input data is empty - skipping PCA initialization")
                    return
                
                # Convert records to text (same logic as in create_structured_data)
                records = df.to_dict('records')
                
                def json_to_text(record):
                    lines = []
                    for key, value in record.items():
                        if not key.startswith('__featrix'):
                            if value is None or (isinstance(value, float) and pd.isna(value)):
                                lines.append('-')
                            else:
                                lines.append(str(value))
                    return "\n".join(lines)
                
                texts = [json_to_text(record) for record in records]
                
                # Use string server client for PCA embeddings instead of loading local model
                logger.info(f"📚 Using string server client for PCA embeddings...")
                _log_gpu_memory_embedded_space("BEFORE getting embeddings from string server for PCA")
                
                # Initialize string server client
                from featrix.neural.string_codec import _init_string_server_client
                client = _init_string_server_client()
                
                if client is None:
                    logger.error("❌ String server client not available for PCA initialization. Set 'string_server_host' in config.json to 'taco', 'taco.local', or 'localhost'")
                    logger.warning("⚠️  Skipping PCA initialization - will use default weight initialization")
                    return
                
                _log_gpu_memory_embedded_space("AFTER initializing string server client for PCA")
                
                # Encode all texts using string server client (batch encoding is more efficient)
                logger.info(f"🔮 Generating {len(texts)} embeddings via string server...")
                # Use batch encoding for efficiency
                batch_size = 100  # String server handles batching internally
                embeddings_384d = []
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_embeddings = client.encode_batch(batch_texts)
                    embeddings_384d.extend(batch_embeddings)
                
                _log_gpu_memory_embedded_space("AFTER encoding texts for PCA")
                embeddings_384d = np.array(embeddings_384d, dtype=np.float32)
                logger.info(f"✅ Generated {len(embeddings_384d)} embeddings (384d) from input data")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not generate embeddings on-the-fly: {e}")
                logger.warning("⚠️  Skipping PCA-based weight initialization")
                return
        
        if embeddings_384d is None or len(embeddings_384d) == 0:
            logger.warning("⚠️  No embeddings available - skipping PCA initialization")
            return
        
        # Apply PCA to match d_model
        n_components = min(self.d_model, embeddings_384d.shape[1], embeddings_384d.shape[0])
        logger.info(f"📊 Applying PCA: 384d → {n_components}d")
        
        pca = PCA(n_components=n_components)
        pca_embeddings = pca.fit_transform(embeddings_384d)
        
        logger.info(f"   Explained variance: {pca.explained_variance_ratio_.sum()*100:.2f}%")
        
        # Log PCA component analysis
        logger.info(f"📊 PCA Component Analysis (first 10 components):")
        for i in range(min(10, n_components)):
            var_ratio = pca.explained_variance_ratio_[i] * 100
            var = pca.explained_variance_[i]
            logger.info(f"   PC{i+1}: {var_ratio:.2f}% variance (var={var:.4f})")
        
        # Extract statistics for weight initialization
        pca_std = pca_embeddings.std()
        pca_mean = pca_embeddings.mean()
        
        logger.info(f"📊 PCA statistics:")
        logger.info(f"   Mean: {pca_mean:.6f}")
        logger.info(f"   Std:  {pca_std:.6f}")
        
        # Log where 500 random points are in PCA space (actual PCA results)
        n_samples = min(500, len(pca_embeddings))
        sample_indices = np.random.choice(len(pca_embeddings), size=n_samples, replace=False)
        sample_embeddings = pca_embeddings[sample_indices]
        
        # Log first 3 principal components for visualization
        logger.info(f"📍 Sample of {n_samples} points in PCA space (first 3 PCs):")
        logger.info(f"   First 10 points:")
        for i in range(min(10, n_samples)):
            point = sample_embeddings[i]
            logger.info(f"      Point {sample_indices[i]}: PC1={point[0]:.4f}, PC2={point[1]:.4f}, PC3={point[2]:.4f}")
        
        # Log statistics across all principal components
        logger.info(f"   Statistics across all {n_components} principal components:")
        logger.info(f"      Min (first 5 PCs): {sample_embeddings.min(axis=0)[:5]}")
        logger.info(f"      Max (first 5 PCs): {sample_embeddings.max(axis=0)[:5]}")
        logger.info(f"      Mean (first 5 PCs): {sample_embeddings.mean(axis=0)[:5]}")
        logger.info(f"      Std (first 5 PCs): {sample_embeddings.std(axis=0)[:5]}")
        
        # Per-dimension variance across ALL PCs (not just first 5)
        per_dim_var = pca_embeddings.var(axis=0)
        logger.info(f"📊 Per-dimension variance (all {n_components} PCs):")
        logger.info(f"   Min var:  {per_dim_var.min():.6f} (PC {per_dim_var.argmin()+1})")
        logger.info(f"   Max var:  {per_dim_var.max():.6f} (PC {per_dim_var.argmax()+1})")
        logger.info(f"   Mean var: {per_dim_var.mean():.6f}")
        logger.info(f"   Total var: {per_dim_var.sum():.6f}")
        
        # Show variance decay across PCs (should decrease)
        if n_components >= 10:
            logger.info(f"   Variance decay: PC1={per_dim_var[0]:.4f} -> PC10={per_dim_var[9]:.4f} -> PC{n_components}={per_dim_var[-1]:.6f}")
        else:
            logger.info(f"   Variance decay: PC1={per_dim_var[0]:.4f} -> PC{n_components}={per_dim_var[-1]:.6f}")
        
        # Check for near-zero variance dimensions (dead PCs)
        near_zero_threshold = 1e-6
        dead_pcs = (per_dim_var < near_zero_threshold).sum()
        if dead_pcs > 0:
            logger.warning(f"   {dead_pcs} PCs have near-zero variance (<{near_zero_threshold}) - these dimensions carry no information")
        
        # Initialize network weights using PCA statistics
        logger.info(f"🎲 Initializing network weights with PCA-derived std={pca_std:.6f}")
        
        param_count = 0
        for name, param in self.encoder.named_parameters():
            if 'weight' in name and param.ndim >= 2:
                torch.nn.init.normal_(param, mean=0.0, std=pca_std)
                param_count += 1
        
        logger.info(f"✅ Initialized {param_count} weight tensors with PCA statistics")
        logger.info(f"✅ PCA-based initialization complete")

    # def set_string_cache_path(self, path):
    #     set_string_cache_path(path)
    #     return
    
    def hydrate_to_cpu_if_needed(self):
        if self.encoder:
            logger.info("encoder going to cpu")
            self.encoder.to(torch.device("cpu"))
        else:
            logger.info("no encoder for cpu")
        return

    def hydrate_to_gpu_if_needed(self):
        if self.encoder:
            logger.info(f"existing encoder going to {get_device()}")
            self.encoder.to(get_device())
        else:
            logger.info(f"no encoder!?")
        return

    def get_string_column_names(self):
        cols = []
        for c, codec in self.col_codecs.items():
            if isinstance(codec, StringCodec):
                cols.append(c)
        return cols

    def get_set_columns(self):
        # return all the columns using the set encoder:
        # { col_name: [possible values]}
        cols = {}
        for c, codec in self.col_codecs.items():
            if isinstance(codec, SetEncoder):
                # cols.append(c)
                if len(codec.members) <= 50:
                    cols[c] = codec.members
        return cols

    def get_scalar_columns(self):
        cols = {}
        for c, codec in self.col_codecs.items():
            if isinstance(codec, AdaptiveScalarEncoder):
                # cols.append(c)
                cols[c] = codec
        return cols


    def len_df(self):
        """Get total number of rows in training and validation data."""
        if self.train_input_data is None or self.val_input_data is None:
            # If input data not loaded (e.g., after unpickling), return 0
            # Caller should set train_input_data and val_input_data before calling this
            return 0
        return len(self.train_input_data.df) + len(self.val_input_data.df)
    
    def get_quality_tracker(self, epoch: int):
        """
        Get or create a CustomerQualityTracker for the specified epoch.
        
        Args:
            epoch: Epoch number
            
        Returns:
            CustomerQualityTracker instance for this epoch
        """
        from featrix.neural.customer_quality_tracker import CustomerQualityTracker
        if epoch not in self.customer_quality_trackers:
            self.customer_quality_trackers[epoch] = CustomerQualityTracker(epoch=epoch)
        return self.customer_quality_trackers[epoch]

    def get_default_table_encoder_config(
        self, d_model: int, col_codecs, col_order, col_types, relationship_features: Optional[RelationshipFeatureConfig] = None
    ):
        # The default configs for the column encoders have to be instantiatied in the EmbeddingSpace
        # object and not when initializign the respective encoder classes because they need info about
        # model dimension and e.g. set size (for set tokens), and otherwise this information would have
        # to be threaded down to the relevant codecs and make the configuration more difficult to manage.
        n_cols = len(col_order)

        dropout = 0.5

        col_encoder_configs = self.get_default_column_encoder_configs(
            d_model,
            col_codecs,
            dropout,
        )
        col_predictor_configs = self.get_default_column_predictor_configs(
            d_model,
            col_order,
            dropout,
        )
        column_predictors_short_config = SimpleMLPConfig(
            d_in=3,
            d_out=3,
            d_hidden=d_model,  # Use d_model to match embedding space dimension (was hardcoded 256)
            n_hidden_layers=1,
            dropout=dropout,
            normalize=False,  # predictors are NOT normalized
            residual=True,
            use_batch_norm=True,
        )
        joint_encoder_config = self.get_default_joint_encoder_config(
            d_model=d_model, n_cols=n_cols, col_order=col_order, dropout=dropout,
            relationship_features=relationship_features
        )
        joint_predictor_config = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=1024,  # Wider for better masked→unmasked mapping capacity
            n_hidden_layers=6,  # Deep reconstruction network
            dropout=dropout,
            normalize=False,  # predictors are NOT normalized
            residual=True,
            use_batch_norm=True,
        )
        joint_predictor_short_config = SimpleMLPConfig(
            d_in=3,
            d_out=3,
            d_hidden=256,
            n_hidden_layers=1,
            dropout=dropout,
            normalize=False,  # predictors are NOT normalized
            residual=True,
            use_batch_norm=True,
        )
        # Initial marginal weight - will be overridden by curriculum learning during training
        # Set to match first curriculum phase (spread_focus with marginal_weight=0.2)
        # NOTE: Curriculum learning updates this dynamically during training
        # Check if curriculum learning is disabled via config.json
        sphere_config = get_config()
        curriculum_disabled = sphere_config.get_disable_curriculum_learning()
        
        if curriculum_disabled:
            marginal_weight = 1.0
            logger.info("⚖️ Loss weights: FIXED at marginal=1.0, joint=1.0, spread=1.0 (curriculum learning DISABLED via config.json)")
        else:
            marginal_weight = 0.2
            logger.info(f"⚖️ Initial loss weights: marginal={marginal_weight:.4f}, joint=1.0, spread=1.0 (curriculum will modulate during training)")
        
        # Get default curriculum learning config
        default_curriculum = self._get_default_curriculum_config()
        
        loss_function_config = LossFunctionConfig(
            joint_loss_weight=1.0,
            marginal_loss_weight=marginal_weight,
            spread_loss_weight=1.0,
            spread_loss_config=SpreadLossConfig(),
            curriculum_learning=default_curriculum
        )
        return FeatrixTableEncoderConfig(
            d_model=d_model,
            n_cols=n_cols,
            cols_in_order=col_order,
            col_types=col_types,
            column_encoders_config=col_encoder_configs,
            column_predictors_config=col_predictor_configs,
            column_predictors_short_config=column_predictors_short_config,
            joint_encoder_config=joint_encoder_config,
            joint_predictor_config=joint_predictor_config,
            joint_predictor_short_config=joint_predictor_short_config,
            loss_config=loss_function_config,
        )

    def get_default_joint_encoder_config(
        self, d_model: int, n_cols: int, col_order, dropout: float, relationship_features: Optional[RelationshipFeatureConfig] = None
    ):
        # Check if relationships are explicitly disabled via environment variable
        disable_relationships = os.environ.get('FEATRIX_DISABLE_RELATIONSHIPS', '0').lower() in ('1', 'true', 'yes')
        
        if disable_relationships:
            relationship_features = None
            logger.info(
                f"🔗 Relationship extractor DISABLED (FEATRIX_DISABLE_RELATIONSHIPS=1)"
            )
        elif relationship_features is None:
            relationship_features = RelationshipFeatureConfig(
                exploration_epochs=10,
                top_k_fraction=0.25,
            )
            logger.info(
                f"🔗 Enabling dynamic relationship extractor with defaults "
                f"(exploration_epochs=10, top_k_fraction=0.25)"
            )
        
        in_converter_configs = dict()
        transformer_model_d = 256

        for col_name in col_order:
            in_converter_configs[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=transformer_model_d,
                d_hidden=256,
                n_hidden_layers=1,  # One hidden layer for non-linear preprocessing
                dropout=dropout,
                # Normalization controlled by batch_norm
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )

        out_converter_config = SimpleMLPConfig(
            d_in=transformer_model_d,
            d_out=d_model,
            d_hidden=256,
            n_hidden_layers=3,
            dropout=dropout,
            normalize=False,  # normalization is controlled inependently by JointEncoder
            residual=True,
            use_batch_norm=True,
        )

        return JointEncoderConfig(
            d_model=transformer_model_d,
            use_col_encoding=True,
            dropout=dropout,
            n_cols=n_cols,
            n_layers=self.n_transformer_layers,
            n_heads=self.n_attention_heads,
            relationship_features=relationship_features,
            in_converter_configs=in_converter_configs,
            out_converter_config=out_converter_config,
        )

    @staticmethod
    def get_default_column_encoder_configs(d_model: int, col_codecs, dropout: float):
        encoder_configs = dict()
        for col_name, codec in col_codecs.items():
            col_type = codec.get_codec_name()

            if col_type == ColumnType.SET:
                # Get sparsity ratio from codec if available
                sparsity_ratio = getattr(codec, 'sparsity_ratio', 0.0)
                encoder_configs[col_name] = SetEncoder.get_default_config(
                    d_model=d_model,
                    n_members=codec.n_members,
                    sparsity_ratio=sparsity_ratio,
                )
            elif col_type == ColumnType.SCALAR:
                # Use AdaptiveScalarEncoder config instead of old ScalarEncoder
                # CRITICAL: Set normalize=False to prevent double normalization
                # Column encoders should NOT normalize when using JointEncoder (which normalizes final output)
                # This preserves magnitude information that encodes numeric values
                from featrix.neural.model_config import ScalarEncoderConfig
                encoder_configs[col_name] = ScalarEncoderConfig(
                    d_out=d_model,
                    d_hidden=64,  # Used internally by AdaptiveScalarEncoder MLPs
                    n_hidden_layers=1,
                    dropout=dropout,
                    normalize=False,  # Let JointEncoder handle normalization to preserve numeric sensitivity
                    residual=False,
                    use_batch_norm=False,
                )
            elif col_type == ColumnType.FREE_STRING:
                # Adaptive architecture selection based on column analysis
                if hasattr(codec, '_adaptive_analysis'):
                    from featrix.neural.string_analysis import (
                        compute_info_density,
                        select_architecture_from_info_density
                    )
                    
                    analysis = codec._adaptive_analysis
                    
                    # Skip encoder config for random columns (zero contribution)
                    if analysis["is_random"]:
                        logger.info(f"   ⚠️  Skipping encoder config for random column '{col_name}'")
                        # Still create a minimal encoder but it will get zero inputs
                        encoder_configs[col_name] = StringEncoder.get_default_config(
                            d_in=codec.d_string_model,
                            d_out=d_model // 4,  # Minimal size for random column
                            d_model=d_model,  # Always project to d_model for stacking
                        )
                    else:
                        # Compute info density and select architecture
                        info_density = compute_info_density(analysis["precomputed"])
                        arch_config = select_architecture_from_info_density(info_density, d_model)
                        
                        logger.info(f"   🎯 Adaptive architecture for '{col_name}':")
                        logger.info(f"      Strategy: {arch_config['strategy']}")
                        logger.info(f"      d_out: {arch_config['d_out']} (info density: {info_density:.2f})")
                        logger.info(f"      n_hidden_layers: {arch_config['n_hidden_layers']}")
                        
                        encoder_configs[col_name] = StringEncoder.get_default_config(
                            d_in=codec.d_string_model,
                            d_out=arch_config['d_out'],
                            d_model=d_model,  # Always project to d_model for stacking
                        )
                        
                        # Store architecture details in encoder config for later reference
                        encoder_configs[col_name].n_hidden_layers = arch_config['n_hidden_layers']
                        encoder_configs[col_name].d_hidden = arch_config['d_hidden']
                else:
                    # Fallback: no adaptive analysis (backward compatibility)
                    encoder_configs[col_name] = StringEncoder.get_default_config(
                        d_in=codec.d_string_model,
                        d_out=d_model * 2,  # Default: 2x capacity
                        d_model=d_model,  # Always project to d_model for stacking
                    )
            elif col_type == ColumnType.LIST_OF_A_SET:
                encoder_configs[col_name] = ListOfASetEncoder.get_default_config(
                    d_in=d_model,
                    n_members=codec.n_members,
                )
            elif col_type == ColumnType.VECTOR:
                encoder_configs[col_name] = VectorEncoder.get_default_config(
                    d_in=codec.in_dim,
                    d_out=d_model,
                )
            elif col_type == ColumnType.JSON:
                # JSON codec already produces embeddings via JsonCodec.tokenize()
                # JsonEncoder just extracts values from tokens, so it needs minimal config
                from featrix.neural.model_config import SimpleMLPConfig
                encoder_configs[col_name] = SimpleMLPConfig(
                    d_in=codec.enc_dim,  # Input is the embedding from JsonCodec
                    d_out=d_model,  # Output to d_model for stacking
                    d_hidden=d_model,  # Simple pass-through, no hidden layers needed
                    n_hidden_layers=0,  # No hidden layers - just pass through
                    dropout=0.0,  # No dropout for pass-through
                    normalize=False,  # Normalization handled by JsonCodec
                    residual=False,
                    use_batch_norm=False,
                )
            elif col_type == ColumnType.URL:
                # URL codec handles its own encoding, encoder is just pass-through
                from featrix.neural.model_config import SimpleMLPConfig
                encoder_configs[col_name] = SimpleMLPConfig(
                    d_in=codec.enc_dim,
                    d_out=d_model,
                    d_hidden=d_model,
                    n_hidden_layers=0,
                    dropout=0.0,
                    normalize=False,
                    residual=False,
                    use_batch_norm=False,
                )
            elif col_type == ColumnType.TIMESTAMP:
                # TimestampEncoder takes 12 temporal features and encodes them
                from featrix.neural.model_config import TimestampEncoderConfig
                encoder_configs[col_name] = TimestampEncoderConfig(
                    d_out=d_model,
                    d_hidden=256,  # Default from TimestampEncoder.get_default_config
                    n_hidden_layers=2,  # Default from TimestampEncoder.get_default_config
                    dropout=dropout,
                    normalize=True,  # TimestampEncoder normalizes by default
                    residual=True,  # TimestampEncoder uses residual by default
                    use_batch_norm=True,  # TimestampEncoder uses batch norm by default
                )
            else:
                raise ValueError(f"Unknown column type: {col_type}")

        return encoder_configs

    @staticmethod
    def get_default_column_predictor_configs(
        d_model: int, col_names_in_order, dropout: float
    ):
        predictor_configs = dict()
        for col_name in col_names_in_order:
            config = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=d_model,  # Use d_model to match embedding space dimension (was hardcoded 200)
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,  # predictors are NOT normalized
                residual=True,
                use_batch_norm=True,
            )

            predictor_configs[col_name] = config

        return predictor_configs

    def _generate_candidate_predictor_architectures(self, d_model: int, dropout: float):
        """
        Generate candidate architectures for column predictors and joint predictor.
        
        Returns:
            List of dicts, each containing:
            - 'col_predictor_configs': dict of SimpleMLPConfig per column
            - 'joint_predictor_config': SimpleMLPConfig for joint predictor
            - 'description': str describing the architecture
        """
        candidates = []
        
        # Candidate 1: Very Small (64d, 1 layer)
        col_configs_1 = {}
        for col_name in self.col_order:
            col_configs_1[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=64,
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_1 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_1,
            'joint_predictor_config': joint_config_1,
            'description': 'Very Small (64d, 1 layer)'
        })
        
        # Candidate 2: Small, shallow (baseline)
        col_configs_2 = {}
        for col_name in self.col_order:
            col_configs_2[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=128,
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_2 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_2,
            'joint_predictor_config': joint_config_2,
            'description': 'Small (128d, 1 layer)'
        })
        
        # Candidate 3: Small-Medium (192d, 1 layer)
        col_configs_3 = {}
        for col_name in self.col_order:
            col_configs_3[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=192,
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_3 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_3,
            'joint_predictor_config': joint_config_3,
            'description': 'Small-Medium (192d, 1 layer)'
        })
        
        # Candidate 4: Medium, shallow
        col_configs_2 = {}
        for col_name in self.col_order:
            col_configs_2[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=256,
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_4 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_2,
            'joint_predictor_config': joint_config_4,
            'description': 'Medium (256d, 1 layer)'
        })
        
        # Candidate 5: Medium, deeper
        col_configs_5 = {}
        for col_name in self.col_order:
            col_configs_5[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=256,
                n_hidden_layers=2,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_5 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_5,
            'joint_predictor_config': joint_config_5,
            'description': 'Medium-Deep (256d, 2 layers)'
        })
        
        # Candidate 6: Large, shallow
        col_configs_4 = {}
        for col_name in self.col_order:
            col_configs_4[col_name] = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=512,
                n_hidden_layers=1,
                dropout=dropout,
                normalize=False,
                residual=True,
                use_batch_norm=True,
            )
        joint_config_6 = SimpleMLPConfig(
            d_in=d_model,
            d_out=d_model,
            d_hidden=512,
            n_hidden_layers=6,
            dropout=dropout,
            normalize=False,
            residual=True,
            use_batch_norm=True,
        )
        candidates.append({
            'col_predictor_configs': col_configs_4,
            'joint_predictor_config': joint_config_6,
            'description': 'Large (512d, 1 layer)'
        })
        
        return candidates

    def _select_best_predictor_architecture(
        self,
        batch_size: int,
        selection_epochs: int = 25,
        val_dataloader=None
    ):
        """
        Train multiple predictor architectures and select the best.
        
        Args:
            batch_size: Batch size for training
            selection_epochs: Number of epochs to train each candidate (default: 25)
                Since encoder is frozen, only predictor heads train - this is fast!
                More epochs = better signal about which architecture actually performs better.
            val_dataloader: Validation dataloader for evaluation
            
        Returns:
            dict: Best architecture config with keys:
            - 'col_predictor_configs': dict of SimpleMLPConfig per column
            - 'joint_predictor_config': SimpleMLPConfig for joint predictor
            - 'description': str describing the architecture
            - 'final_val_loss': float validation loss of winner
        """
        # Generate candidate architectures first (needed for logging)
        dropout = 0.5  # Use default dropout for selection
        if hasattr(self.encoder_config, 'loss_config') and hasattr(self.encoder_config.loss_config, 'spread_loss_config'):
            # Try to get dropout from config, but use default if not available
            pass
        all_candidates = self._generate_candidate_predictor_architectures(self.d_model, dropout)
        # Only test first 2 candidates to save time
        candidates = all_candidates[:2]
        
        logger.info("=" * 80)
        logger.info("🏗️  PREDICTOR HEAD ARCHITECTURE SELECTION")
        logger.info("=" * 80)
        logger.info(f"⚠️  IMPORTANT: Selecting PREDICTOR HEAD architectures, NOT embedding space architecture!")
        logger.info(f"   - Embedding space encoder (d_model={self.d_model}): FIXED - NOT part of selection")
        logger.info(f"   - Testing {len(candidates)} different PREDICTOR HEAD architectures (limited to first {len(candidates)} of {len(all_candidates)} total candidates)")
        logger.info(f"   - Candidate dimensions: 64d, 128d, 192d, 256d (these are PREDICTOR HEAD hidden dimensions, not embedding space dimension)")
        logger.info(f"   - Column predictors: Small MLPs that predict each column from joint embeddings (for self-supervised learning)")
        logger.info(f"   - Joint predictor: Small MLP that predicts joint embeddings (for self-supervised learning)")
        logger.info(f"   - EMBEDDING SPACE ENCODER (column_encoder + joint_encoder): FROZEN (not training, just using for forward pass)")
        logger.info(f"   - PREDICTOR HEADS (column_predictor + joint_predictor): TRAINING (only these small MLPs are being updated)")
        logger.info(f"   - Training {selection_epochs} epochs per candidate to compare validation loss")
        logger.info(f"   - Total overhead: {len(candidates)} candidates × {selection_epochs} epochs = {len(candidates) * selection_epochs} epochs")
        logger.info(f"   - ⚡ FAST: Encoder frozen means only small predictor head MLPs train - {selection_epochs} epochs is quick!")
        logger.info(f"   - Will only use better architecture if improvement > 5% or >5.0 absolute")
        logger.info(f"   - ✅ After selection completes, MAIN TRAINING will train the FULL EMBEDDING SPACE (encoder + selected predictor heads) for your requested epoch count")
        logger.info(f"📋 Generated {len(candidates)} candidate predictor head architectures")
        
        # Store original predictor state (we'll restore it later)
        original_col_predictor = self.encoder.column_predictor
        original_joint_predictor = self.encoder.joint_predictor
        
        # Create train dataloader using the same pattern as main training
        # FeatrixInputDataSet has a df attribute, and we need to use col_codecs
        train_dataset = SuperSimpleSelfSupervisedDataset(
            self.train_input_data.df,
            self.col_codecs
        )
        train_dl_kwargs = create_dataloader_kwargs(
            batch_size=batch_size,
            shuffle=True,
            drop_last=True,
            dataset_size=len(self.train_input_data.df),
            num_columns=len(self.train_input_data.df.columns),
        )
        train_dataloader = DataLoader(
            train_dataset,
            collate_fn=collate_tokens,
            **train_dl_kwargs
        )
        
        if val_dataloader is None:
            # Create validation dataloader
            val_dataset = SuperSimpleSelfSupervisedDataset(
                self.val_input_data.df,
                self.col_codecs
            )
            # CRITICAL: Reduce validation workers based on available VRAM to prevent OOM
            val_num_workers = None
            if is_gpu_available():
                try:
                    allocated = get_gpu_memory_allocated()
                    reserved = get_gpu_memory_reserved()
                    total_memory = (get_gpu_device_properties(0).total_memory / (1024**3)) if get_gpu_device_properties(0) else 0.0
                    free_vram = total_memory - reserved
                    
                    worker_vram_gb = 0.6
                    safety_margin_gb = 20.0
                    available_for_workers = max(0, free_vram - safety_margin_gb)
                    max_workers_by_vram = int(available_for_workers / worker_vram_gb)
                    
                    from featrix.neural.dataloader_utils import get_optimal_num_workers
                    default_workers = get_optimal_num_workers(dataset_size=len(self.val_input_data.df))
                    
                    # Cap based on total GPU memory: ≤16GB GPUs get max 2 workers, >16GB (4090=24GB) get max 4
                    max_val_workers = 2 if total_memory <= 16 else 4
                    val_num_workers = min(default_workers, max_workers_by_vram, max_val_workers)
                    val_num_workers = max(0, val_num_workers)
                    
                    logger.info(f"🔍 Validation worker calculation: free_vram={free_vram:.1f}GB, total_memory={total_memory:.1f}GB → {val_num_workers} workers (max {max_val_workers})")
                except Exception as e:
                    logger.warning(f"Could not calculate optimal validation workers: {e}, using 0")
                    val_num_workers = 0
            
            val_dl_kwargs = create_dataloader_kwargs(
                batch_size=batch_size,
                shuffle=False,
                drop_last=True,
                num_columns=len(self.val_input_data.df.columns),
                num_workers=val_num_workers,
                dataset_size=len(self.val_input_data.df),
            )
            val_dataloader = DataLoader(
                val_dataset,
                collate_fn=collate_tokens,
                **val_dl_kwargs
            )
        
        best_candidate = None
        best_val_loss = float('inf')
        candidate_results = []
        baseline_loss = None  # Will be set after first candidate
        
        # Train and evaluate each candidate
        for idx, candidate in enumerate(candidates):
            logger.info("")
            logger.info(f"🔬 Candidate {idx + 1}/{len(candidates)}: {candidate['description']}")
            logger.info("-" * 80)
            
            # Create new predictors with this architecture
            new_col_predictor = ColumnPredictor(
                cols_in_order=self.col_order,
                col_configs=candidate['col_predictor_configs']
            )
            new_joint_predictor = SimpleMLP(candidate['joint_predictor_config'])
            
            # Replace predictors in encoder
            self.encoder.column_predictor = new_col_predictor
            self.encoder.joint_predictor = new_joint_predictor
            self.encoder.column_predictor.to(get_device())
            self.encoder.joint_predictor.to(get_device())
            
            # FREEZE encoder - only train predictors for architecture selection
            # This dramatically reduces overhead while still allowing fair comparison
            for param in self.encoder.parameters():
                param.requires_grad = False
            # Unfreeze only predictors
            if hasattr(self.encoder, 'column_predictor') and self.encoder.column_predictor is not None:
                for param in self.encoder.column_predictor.parameters():
                    param.requires_grad = True
            if hasattr(self.encoder, 'joint_predictor') and self.encoder.joint_predictor is not None:
                for param in self.encoder.joint_predictor.parameters():
                    param.requires_grad = True
            
            # Only optimize predictor parameters (encoder frozen)
            predictor_params = []
            if hasattr(self.encoder, 'column_predictor') and self.encoder.column_predictor is not None:
                predictor_params.extend(self.encoder.column_predictor.parameters())
            if hasattr(self.encoder, 'joint_predictor') and self.encoder.joint_predictor is not None:
                predictor_params.extend(self.encoder.joint_predictor.parameters())
            
            # Use higher LR for architecture selection since we're only training small predictor heads
            # Encoder is frozen, so we can be more aggressive with LR to get better signal faster
            # 0.01 is 10× higher than main training (0.001) - helps small MLPs adapt quickly
            selection_lr = 0.01
            optimizer = torch.optim.AdamW(predictor_params, lr=selection_lr, weight_decay=1e-4)
            logger.info(f"      - Learning rate: {selection_lr} (10× higher than main training to quickly adapt small predictor heads)")
            
            # Train for selection_epochs - MUCH faster since encoder is frozen
            self.encoder.train()
            logger.info(f"   🚀 PREDICTOR HEAD SELECTION: Training candidate {idx + 1}/{len(candidates)} ({candidate['description']}) for {selection_epochs} epochs")
            logger.info(f"      - Embedding space encoder (d_model={self.d_model}): FROZEN (not training, just using for forward pass)")
            logger.info(f"      - Predictor heads ({candidate['description']}): TRAINING (only these small MLPs are being updated)")
            logger.info(f"      - ⚠️  This is NOT your main embedding space training - this is just evaluating predictor head architectures")
            logger.info(f"      - After selection, main training will train the FULL EMBEDDING SPACE (encoder + selected predictor heads) for your requested epoch count")
            for epoch in range(selection_epochs):
                epoch_loss = 0.0
                batch_count = 0
                
                for batch in train_dataloader:
                    optimizer.zero_grad()
                    
                    # Forward pass through full encoder (uses actual loss computation)
                    encodings = self.encoder(batch)
                    batch_loss, loss_dict = self.encoder.compute_total_loss(*encodings)
                    
                    batch_loss.backward()
                    optimizer.step()
                    
                    epoch_loss += batch_loss.item()
                    batch_count += 1
                
                avg_loss = epoch_loss / batch_count if batch_count > 0 else 0.0
                # Log every 5 epochs or last epoch
                if (epoch + 1) % 5 == 0 or epoch == selection_epochs - 1:
                    logger.info(f"   Epoch {epoch + 1}/{selection_epochs}: train_loss={avg_loss:.4f}")
            
            # Evaluate on validation set - single evaluation is enough (encoder frozen, so deterministic)
            logger.info(f"   🔍 Computing validation loss for candidate architecture...")
            val_loss, val_components = self.compute_val_loss(val_dataloader)
            val_loss_std = 0.0  # No variance when encoder is frozen
            
            logger.info(f"   ✅ Validation loss: {val_loss:.4f}")
            
            # Set baseline after first candidate
            if baseline_loss is None:
                baseline_loss = val_loss
                baseline_std = val_loss_std
            
            candidate_results.append({
                'candidate': candidate,
                'val_loss': val_loss,
                'val_loss_std': val_loss_std
            })
            
            # Track best
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_candidate = candidate.copy()
                best_candidate['final_val_loss'] = val_loss
                logger.info(f"   🏆 New best architecture!")
            
            # Early stopping: if we've tested at least 2 candidates and improvement is marginal,
            # stop early to save time. Check if current best improvement is below threshold.
            if idx >= 1:  # At least 2 candidates tested
                current_improvement_pct = ((baseline_loss - best_val_loss) / baseline_loss) * 100
                current_improvement_abs = baseline_loss - best_val_loss
                
                # If we've already found a good improvement, continue to see if we can do better
                # But if improvements are very marginal (< 2%), stop early
                if current_improvement_pct < 2.0 and current_improvement_abs < 2.0:
                    logger.info(f"   ⏹️  Early stopping: improvements are marginal ({current_improvement_pct:.2f}%, {current_improvement_abs:.4f} absolute)")
                    logger.info(f"   Continuing with {len(candidates) - idx - 1} remaining candidates would likely not justify overhead")
                    # Continue anyway to complete the comparison, but log the concern
            
            # Clean up GPU memory after each candidate
            # Move old predictors to CPU and delete them
            if hasattr(self.encoder, 'column_predictor') and self.encoder.column_predictor is not None:
                self.encoder.column_predictor.cpu()
                del self.encoder.column_predictor
            if hasattr(self.encoder, 'joint_predictor') and self.encoder.joint_predictor is not None:
                self.encoder.joint_predictor.cpu()
                del self.encoder.joint_predictor
            
            # Clear optimizer state
            del optimizer
            
            # Clear GPU cache
            if is_gpu_available():
                empty_gpu_cache()
        
        # Restore original predictors (we'll replace with winner after selection)
        self.encoder.column_predictor = original_col_predictor
        self.encoder.joint_predictor = original_joint_predictor
        
        # Check if improvement is meaningful
        baseline_loss = candidate_results[0]['val_loss']  # First candidate is baseline
        baseline_std = candidate_results[0].get('val_loss_std', 0.0)
        
        # Find best candidate's std from results
        best_std = 0.0
        for result in candidate_results:
            if result['candidate'] == best_candidate:
                best_std = result.get('val_loss_std', 0.0)
                break
        
        improvement_pct = ((baseline_loss - best_val_loss) / baseline_loss) * 100
        improvement_abs = baseline_loss - best_val_loss
        
        # Statistical significance check: is improvement > 2 standard deviations?
        # This accounts for variance in evaluation (though std=0 when encoder frozen)
        pooled_std = np.sqrt(baseline_std**2 + best_std**2) if baseline_std > 0 and best_std > 0 else 0.0
        z_score = improvement_abs / pooled_std if pooled_std > 0 else float('inf')
        # When encoder is frozen, variance is minimal, so we rely on absolute thresholds
        statistically_significant = z_score > 2.0 if pooled_std > 0 else True  # Always significant if no variance
        
        # Minimum thresholds: at least 5% relative improvement OR 5.0 absolute improvement
        # This prevents selecting a more complex architecture for marginal gains
        MIN_IMPROVEMENT_PCT = 5.0
        MIN_IMPROVEMENT_ABS = 5.0
        
        meaningful_improvement = (
            (improvement_pct >= MIN_IMPROVEMENT_PCT or improvement_abs >= MIN_IMPROVEMENT_ABS) and
            statistically_significant  # Must also be statistically significant
        )
        
        # Log results
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 ARCHITECTURE SELECTION RESULTS")
        logger.info("=" * 80)
        for idx, result in enumerate(candidate_results):
            marker = "🏆" if result['candidate'] == best_candidate else "  "
            logger.info(f"{marker} {idx + 1}. {result['candidate']['description']}: val_loss={result['val_loss']:.4f}")
        logger.info("")
        
        # Decision logic
        if not meaningful_improvement:
            # Use baseline (first candidate) - overhead not worth it
            baseline_candidate = candidate_results[0]['candidate'].copy()
            baseline_candidate['final_val_loss'] = baseline_loss
            logger.info(f"⚠️  Best architecture ({best_candidate['description']}) only improves by {improvement_pct:.2f}% ({improvement_abs:.4f} absolute)")
            if not statistically_significant:
                logger.info(f"   ⚠️  Improvement not statistically significant (z-score={z_score:.2f}, need >2.0)")
            if improvement_pct < MIN_IMPROVEMENT_PCT and improvement_abs < MIN_IMPROVEMENT_ABS:
                logger.info(f"   ⚠️  Improvement below threshold ({MIN_IMPROVEMENT_PCT}% or {MIN_IMPROVEMENT_ABS} absolute)")
            logger.info(f"   Using baseline architecture to avoid unnecessary overhead")
            logger.info(f"✅ Selected: {candidate_results[0]['candidate']['description']} (val_loss={baseline_loss:.4f} ± {baseline_std:.4f})")
            logger.info("=" * 80)
            return baseline_candidate
        else:
            logger.info(f"✅ Selected: {best_candidate['description']} (val_loss={best_val_loss:.4f} ± {best_std:.4f})")
            logger.info(f"   Improvement: {improvement_pct:.2f}% ({improvement_abs:.4f} absolute)")
            logger.info(f"   Statistical significance: z-score={z_score:.2f} (statistically significant)")
            logger.info(f"   Worth the overhead: improvement exceeds thresholds and is statistically significant")
            logger.info("=" * 80)
            return best_candidate
    
    def _replace_predictors_with_architecture(self, architecture_config):
        """
        Replace the column and joint predictors in the encoder with the selected architecture.
        
        Args:
            architecture_config: dict with 'col_predictor_configs' and 'joint_predictor_config'
        """
        new_col_predictor = ColumnPredictor(
            cols_in_order=self.col_order,
            col_configs=architecture_config['col_predictor_configs']
        )
        new_joint_predictor = SimpleMLP(architecture_config['joint_predictor_config'])
        
        self.encoder.column_predictor = new_col_predictor
        self.encoder.joint_predictor = new_joint_predictor
        self.encoder.column_predictor.to(get_device())
        self.encoder.joint_predictor.to(get_device())
        
        # CRITICAL: Unfreeze all encoder parameters for main training
        # During architecture selection, the encoder was frozen to speed up comparison.
        # Now that selection is complete, we need to unfreeze everything so the full
        # embedding space (encoder + predictor heads) can be trained together.
        for param in self.encoder.parameters():
            param.requires_grad = True
        logger.info(f"   🔓 Unfroze all encoder parameters for main training")
        
        # Update encoder_config to reflect the new architecture
        self.encoder_config.column_predictors_config = architecture_config['col_predictor_configs']
        self.encoder_config.joint_predictor_config = architecture_config['joint_predictor_config']
        
        # Store architecture selection metadata in training_info for reference
        if not hasattr(self, 'training_info'):
            self.training_info = {}
        self.training_info['selected_predictor_architecture'] = {
            'description': architecture_config['description'],
            'final_val_loss': architecture_config.get('final_val_loss'),
            'column_predictor_configs': {
                col_name: {
                    'd_hidden': config.d_hidden,
                    'n_hidden_layers': config.n_hidden_layers,
                    'dropout': config.dropout,
                }
                for col_name, config in architecture_config['col_predictor_configs'].items()
            },
            'joint_predictor_config': {
                'd_hidden': architecture_config['joint_predictor_config'].d_hidden,
                'n_hidden_layers': architecture_config['joint_predictor_config'].n_hidden_layers,
                'dropout': architecture_config['joint_predictor_config'].dropout,
            }
        }
        
        logger.info(f"✅ Replaced predictors with architecture: {architecture_config['description']}")
        logger.info(f"   Architecture stored in encoder_config.column_predictors_config and training_info")

    def free_memory(self):
        self.train_input_data.free_memory()
        self.val_input_data.free_memory()
        return

    def reset_training_state(self):
        """Reset training state and clean up DataLoader workers.
        
        CRITICAL: This is called before OOM retry to ensure DataLoader workers
        are properly shut down. Workers with persistent_workers=True do NOT
        automatically terminate when the DataLoader goes out of scope - they must
        be explicitly shut down or they'll accumulate and consume memory.
        """
        logger.info("🧹 reset_training_state: Cleaning up training state and DataLoader workers...")
        
        # Clean up DataLoaders if they exist (critical for OOM retry)
        # DataLoader workers with persistent_workers=True don't terminate on their own
        for attr_name in ['_current_data_loader', '_current_val_dataloader', 'data_loader', 'val_dataloader']:
            if hasattr(self, attr_name):
                dl = getattr(self, attr_name, None)
                if dl is not None:
                    _cleanup_dataloader_workers(dl, f"reset_training_state: {attr_name}")
                    setattr(self, attr_name, None)
        
        # Also clean up any orphaned worker processes
        try:
            _check_and_cleanup_existing_workers(context=" during reset_training_state")
        except Exception as e:
            logger.debug(f"Could not check for orphaned workers: {e}")
        
        self.training_state = {}
        self.training_progress_data = {}
        
        logger.info("🧹 reset_training_state: Complete")

    def gotInterrupted(self):
        return self._gotControlC

    def get_column_names(self):
        return list(self.col_codecs.keys())

    def get_codec_type_for_column(self, col):
        codec = self.col_codecs.get(col)
        # print(f"...col {col}...{codec}")

        if isinstance(codec, AdaptiveScalarEncoder):
            return "scalar"
        elif isinstance(codec, SetEncoder):
            return "set"

        return None

    def _create_codecs(self):
        # DEBUG: Log codec creation process
        logger.info(f"🔧 _create_codecs starting...")
        logger.info(f"   Column spec has {len(self.column_spec)} columns: {list(self.column_spec.keys())}")
        logger.info(f"   col_codecs currently has {len(self.col_codecs)} items")
        
        ts = time.time()
        needOutput = False
        colsSoFar = []
        for col_name, col_type in self.column_spec.items():
            logger.info(f"   Processing column '{col_name}' (type: {col_type})")
            tn = time.time()
            if (tn - ts) > 30 and not needOutput:
                needOutput = True
                logger.info("Codec creation is taking longer than expected...")
                logger.info("Already created codecs for:")
                for cc in colsSoFar:
                    logger.info(f"\t{cc.get('name')} [{cc.get('time')} seconds]")

            if needOutput:
                logger.info(f"Creating codec for {col_name}...")

            df_col_values = self.train_input_data.get_casted_values_for_column_name(
                col_name
            )
            assert (
                df_col_values is not None
            ), f'missing casted values for column "{col_name}"'

            codec = None

            if col_type == ColumnType.SET:
                # Get detector to access sparsity information
                setDetector = self.train_input_data.get_detector_for_col_name(col_name)
                # Use vocabulary override if available (for checkpoint reconstruction)
                vocabulary_override = self.codec_vocabulary_overrides.get(col_name)
                if vocabulary_override:
                    logger.info(f"   📚 Using checkpoint vocabulary for '{col_name}': {len(vocabulary_override)} members (current data has {len(set(df_col_values.astype(str).unique()))} unique values)")
                # Use CrossEntropyLoss for embedding space training (more stable)
                codec = create_set_codec(
                    df_col_values, 
                    embed_dim=self.d_model, 
                    loss_type="cross_entropy",
                    detector=setDetector,
                    string_cache=self.string_cache,
                    vocabulary_override=vocabulary_override
                )
            elif col_type == ColumnType.SCALAR:
                codec = create_scalar_codec(df_col_values, embed_dim=self.d_model)
            elif col_type == ColumnType.TIMESTAMP:
                codec = create_timestamp_codec(df_col_values, embed_dim=self.d_model)
            elif col_type == ColumnType.FREE_STRING:
                strDetector = self.train_input_data.get_detector_for_col_name(col_name)
                assert strDetector is not None
                
                # Note: SimpleStringCache is in-memory only and doesn't require a file path.
                # Workers can use SimpleStringCache by connecting to the string server.
                # The string_cache parameter is optional and mainly for compatibility.
                
                # Get validation column values to ensure all values are cached
                validation_df_col = None
                if col_name in self.val_input_data.df.columns:
                    validation_df_col = self.val_input_data.df[col_name]
                
                codec = create_string_codec(
                    df_col_values, 
                    detector=strDetector, 
                    embed_dim=self.d_model,
                    string_cache=self.string_cache,
                    # sentence_model removed - using string server instead
                    validation_df_col=validation_df_col  # Pass validation data to cache all values
                )
                # codec.debug_name = col_name
            elif col_type == ColumnType.VECTOR:
                vecDetector = self.train_input_data.get_detector_for_col_name(col_name)
                assert vecDetector is not None
                codec = create_vector_codec(
                    df_col_values, detector=vecDetector, embed_dim=self.d_model
                )
                # codec.debug_name = col_name
            elif col_type == ColumnType.URL:
                urlDetector = self.train_input_data.get_detector_for_col_name(col_name)
                assert urlDetector is not None
                from featrix.neural.encoders import create_url_codec
                codec = create_url_codec(
                    df_col_values, 
                    detector=urlDetector, 
                    embed_dim=self.d_model,
                    string_cache=self.string_cache
                )
            elif col_type == ColumnType.DOMAIN:
                domainDetector = self.train_input_data.get_detector_for_col_name(col_name)
                assert domainDetector is not None
                from featrix.neural.encoders import create_domain_codec
                codec = create_domain_codec(
                    df_col_values,
                    detector=domainDetector,
                    embed_dim=self.d_model,
                    string_cache=self.string_cache
                )
            elif col_type == ColumnType.JSON:
                # TEMPORARILY DISABLED: Skip JSON columns to save time
                logger.warning(f"⚠️  Skipping JSON column '{col_name}' - JSON columns are temporarily disabled")
                continue
                # jsonDetector = self.train_input_data.get_detector_for_col_name(col_name)
                # assert jsonDetector is not None
                # from featrix.neural.encoders import create_json_codec
                # # Use json_cache.sqlite3 in the same directory as string cache
                # json_cache_filename = "json_cache.sqlite3" if self.string_cache else None
                # # Get child ES session ID for this column if it's a dependency
                # child_es_session_id = self.required_child_es_mapping.get(col_name)
                # if child_es_session_id:
                #     logger.info(f"🔗 JSON column '{col_name}' will use child ES session: {child_es_session_id}")
                # codec = create_json_codec(
                #     df_col_values,
                #     detector=jsonDetector,
                #     embed_dim=self.d_model,
                #     json_cache_filename=json_cache_filename,
                #     child_es_session_id=child_es_session_id
                # )
            # elif col_type == ColumnType.LIST_OF_A_SET:
            #     listDetector = self.train_input_data.get_detector_for_col_name(col_name)
            #     assert listDetector is not None
            #     codec = create_lists_of_a_set_codec(
            #         df_col_values, detector=listDetector, embed_dim=self.d_model
            #     )
            else:
                raise ValueError(f"Unsupported codec type: {col_type}.")

            self.col_codecs[col_name] = codec

            if needOutput:
                logger.info(f"Finished codec for {col_name} [{time.time() - tn:.1f} seconds]")

            colsSoFar.append({"name": col_name, "time": time.time() - tn})

        if needOutput:
            logger.info("Finished creating all codecs")
        return

    def gotControlC(self):
        self._gotControlC = True

    def _get_base_token_dict(self):
        # Returns a base token batch dict where all tokens are missing.

        d = {}
        for col, codec in self.col_codecs.items():
            # NOTE: set the token to unknown instead of not present. this change was introduced
            # on 10/13/2023.
            d[col] = create_token_batch([set_marginal(codec.get_not_present_token())])

        return d

    # we want to have access to layers of encodings.
    # How to do that without having to process all the columns all the time?

    def explain(self, record, predictor_model, target_codec=None, class_idx: int = None, record_b: Dict = None) -> Dict[str, Any]:
        """
        Explain a prediction using gradient attribution.
        
        Supports multiple modes:
        - explain(record): Explain a single row
        - explain(record, record_b=other_record): Compare two rows
        - explain([record1, record2, ...]): Explain multiple rows (returns list of explanations)
        
        Returns what matters to Featrix in the given row(s):
        - Which features mattered for this prediction
        - Which relationships mattered for this prediction
        
        Args:
            record: Record dictionary (without target column), or list of records
            predictor_model: The predictor model (nn.Module) to use for attribution
            target_codec: Optional target codec to determine class_idx (if None, uses predicted class)
            class_idx: Target class index for attribution (default: predicted class)
            record_b: Optional second record for comparison (explain difference between record and record_b)
            
        Returns:
            For single record:
                Dictionary with:
                    - feature_scores: {col_name: score} - gradient norm per feature
                    - pair_scores: {(i, j): score} - gradient norm per relationship pair
                    - logit: The prediction logit
                    - target_class_idx: The class index used for attribution
            
            For two records (record_b provided):
                Dictionary with:
                    - record_a: Explanation for first record
                    - record_b: Explanation for second record
                    - difference: Difference in feature_scores and pair_scores
            
            For list of records:
                List of explanation dictionaries, one per record
        """
        import torch
        import logging
        from featrix.neural.featrix_token import create_token_batch
        from featrix.neural.set_codec import SetEncoder, SetCodec
        
        logger = logging.getLogger(__name__)
        
        # Handle list of records
        if isinstance(record, list):
            # Explain each record and return list
            explanations = []
            for rec in record:
                expl = self._explain_single_record(rec, predictor_model, target_codec, class_idx)
                explanations.append(expl)
            return explanations
        
        # Handle two records for comparison
        if record_b is not None:
            expl_a = self._explain_single_record(record, predictor_model, target_codec, class_idx)
            expl_b = self._explain_single_record(record_b, predictor_model, target_codec, class_idx)
            
            # Compute differences (using signed scores for heatmap)
            feature_diff = {}
            feature_diff_signed = {}
            all_features = set(expl_a['feature_scores'].keys()) | set(expl_b['feature_scores'].keys())
            for feat in all_features:
                score_a = expl_a['feature_scores'].get(feat, 0.0)
                score_b = expl_b['feature_scores'].get(feat, 0.0)
                feature_diff[feat] = score_b - score_a  # Difference: B - A
                
                # Signed difference for heatmap
                signed_a = expl_a.get('feature_signed_scores', {}).get(feat, 0.0)
                signed_b = expl_b.get('feature_signed_scores', {}).get(feat, 0.0)
                feature_diff_signed[feat] = signed_b - signed_a
            
            pair_diff = {}
            pair_diff_signed = {}
            all_pairs = set(expl_a['pair_scores'].keys()) | set(expl_b['pair_scores'].keys())
            for pair in all_pairs:
                score_a = expl_a['pair_scores'].get(pair, 0.0)
                score_b = expl_b['pair_scores'].get(pair, 0.0)
                pair_diff[pair] = score_b - score_a  # Difference: B - A
                
                # Signed difference for heatmap
                signed_a = expl_a.get('pair_signed_scores', {}).get(pair, 0.0)
                signed_b = expl_b.get('pair_signed_scores', {}).get(pair, 0.0)
                pair_diff_signed[pair] = signed_b - signed_a
            
            # Generate heatmap data
            heatmap_data = self._generate_heatmap_data(
                feature_diff_signed, pair_diff_signed, self.encoder
            )
            
            return {
                'record_a': expl_a,
                'record_b': expl_b,
                'difference': {
                    'feature_scores': feature_diff,
                    'feature_signed_scores': feature_diff_signed,
                    'pair_scores': pair_diff,
                    'pair_signed_scores': pair_diff_signed,
                },
                'heatmap': heatmap_data,
            }
        
        # Single record
        return self._explain_single_record(record, predictor_model, target_codec, class_idx)
    
    def _explain_single_record(self, record: Dict, predictor_model, target_codec=None, class_idx: int = None) -> Dict[str, Any]:
        """
        Internal method to explain a single record.
        """
        import torch
        import logging
        from featrix.neural.featrix_token import create_token_batch
        from featrix.neural.set_codec import SetEncoder, SetCodec
        
        logger = logging.getLogger(__name__)
        
        # Prepare record tokens (same as encode_record but with gradients enabled)
        record_tokens = {}
        for field, value in record.items():
            field = field.strip()
            if field.startswith('__featrix') or field not in self.col_codecs:
                continue
            codec = self.col_codecs[field]
            token = codec.tokenize(value)
            record_tokens[field] = token
        
        # Get base token dict
        batch_tokens = self._get_base_token_dict()
        for field, token in record_tokens.items():
            batch_tokens[field] = create_token_batch([token])
        
        # Set encoder to eval mode
        encoder = self.encoder
        was_training = encoder.training
        if was_training:
            encoder.eval()
        
        # Encode with gradients enabled (no torch.no_grad())
        # This allows us to compute gradients on intermediate values
        short_encoding, full_encoding = encoder.encode(batch_tokens)
        
        # Enable gradients on full encoding
        full_encoding.requires_grad_(True)
        full_encoding.retain_grad()
        
        # Enable gradients on column encodings (stored in encoder state during encode())
        if hasattr(encoder, 'column_encodings') and encoder.column_encodings is not None:
            col_encodings = encoder.column_encodings
            col_encodings.requires_grad_(True)
            col_encodings.retain_grad()
        
        # Forward pass through predictor
        logit = predictor_model(full_encoding)
        
        # Choose target class
        if class_idx is None:
            # Use predicted class
            if target_codec is not None and isinstance(target_codec, (SetEncoder, SetCodec)):
                # Classification: use argmax
                class_idx = logit.argmax(dim=-1).item()
            else:
                # Regression or no codec: use the single output
                class_idx = 0
        else:
            # Ensure class_idx is valid
            if target_codec is not None and isinstance(target_codec, (SetEncoder, SetCodec)):
                num_classes = logit.shape[-1]
                if class_idx >= num_classes:
                    raise ValueError(f"class_idx {class_idx} >= num_classes {num_classes}")
        
        target = logit[0, class_idx] if logit.dim() > 1 else logit[0]
        
        # Backprop
        target.backward()
        
        # Feature attribution: get column embeddings from encoder
        # Use signed contributions (sum of gradients) not just norms
        feature_scores = {}
        feature_signed_scores = {}  # For heatmap visualization
        if hasattr(encoder, 'column_encodings') and encoder.column_encodings is not None:
            col_encodings = encoder.column_encodings  # (batch_size, n_cols, d_model)
            if col_encodings.grad is not None:
                # Get gradient norms per column (magnitude)
                col_grads = col_encodings.grad  # (batch_size, n_cols, d_model)
                col_grad_norms = col_grads.norm(dim=-1).squeeze(0)  # (n_cols,)
                
                # Get signed contributions (sum of gradients) - direction matters
                col_grad_signed = col_grads.sum(dim=-1).squeeze(0)  # (n_cols,) - sum over embedding dim
                
                # Map to column names
                if hasattr(encoder, 'column_order'):
                    col_order = encoder.column_order
                elif hasattr(encoder, 'effective_col_order'):
                    col_order = encoder.effective_col_order
                else:
                    col_order = list(range(col_grad_norms.shape[0]))
                
                for idx, col_name in enumerate(col_order):
                    if idx < col_grad_norms.shape[0]:
                        feature_scores[col_name] = col_grad_norms[idx].item()
                        feature_signed_scores[col_name] = col_grad_signed[idx].item()
        
        # If we couldn't get column-level gradients, use encoding gradient as fallback
        if not feature_scores and full_encoding.grad is not None:
            # Fallback: use overall encoding gradient norm
            encoding_grad_norm = full_encoding.grad.norm().item()
            encoding_grad_signed = full_encoding.grad.sum().item()
            feature_scores['_joint_encoding'] = encoding_grad_norm
            feature_signed_scores['_joint_encoding'] = encoding_grad_signed
        
        # Pair attribution: get relationship extractor outputs
        # Use signed contributions (sum of gradients) not just norms
        pair_scores = {}
        pair_signed_scores = {}  # For heatmap visualization
        if hasattr(encoder, 'joint_encoder'):
            joint_encoder = encoder.joint_encoder
            if hasattr(joint_encoder, 'relationship_extractor'):
                rel_extractor = joint_encoder.relationship_extractor
                if rel_extractor is not None:
                    # Get active pairs from last forward pass
                    active_pairs = getattr(rel_extractor, '_last_step_active_pairs', set())
                    if not active_pairs:
                        # Fallback: get from pairs_to_compute
                        pairs_to_compute = getattr(rel_extractor, '_last_pairs_to_compute', [])
                        active_pairs = set(pairs_to_compute)
                    
                    # Try to get relationship token gradients
                    # Relationship tokens are stored in _tokens_for_gradient_check during forward
                    tokens_for_check = getattr(rel_extractor, '_tokens_for_gradient_check', [])
                    
                    for (i, j), token in tokens_for_check:
                        if token.grad is not None:
                            # Magnitude (norm)
                            pair_scores[(i, j)] = token.grad.norm().item()
                            # Signed contribution (sum)
                            pair_signed_scores[(i, j)] = token.grad.sum().item()
                    
                    # If no token gradients, use pair contributions as fallback
                    if not pair_scores and hasattr(rel_extractor, 'pair_contributions'):
                        for (i, j) in active_pairs:
                            if (i, j) in rel_extractor.pair_contributions:
                                pair_scores[(i, j)] = rel_extractor.pair_contributions[(i, j)]
                                # For fallback, we don't have signed scores, use magnitude
                                pair_signed_scores[(i, j)] = rel_extractor.pair_contributions[(i, j)]
        
        # Restore training mode if needed
        if was_training:
            encoder.train()
        
        return {
            'feature_scores': feature_scores,
            'feature_signed_scores': feature_signed_scores,  # Signed contributions for heatmap
            'pair_scores': pair_scores,
            'pair_signed_scores': pair_signed_scores,  # Signed contributions for heatmap
            'logit': logit.detach().cpu().numpy().tolist() if isinstance(logit, torch.Tensor) else logit,
            'target_class_idx': class_idx,
        }
    
    def _generate_heatmap_data(self, feature_signed_scores: Dict, pair_signed_scores: Dict, encoder) -> Dict[str, Any]:
        """
        Generate heatmap data structure for visualization.
        
        Returns a square matrix showing the contribution of each feature combination (i, j pairs).
        The matrix represents f_ij(x) - the causal contribution at inference time.
        
        Diagonal is set to zero (no self-interactions, or could use unary terms f_i(x_i)).
        
        Args:
            feature_signed_scores: Signed contributions per feature (for diagonal if desired)
            pair_signed_scores: Signed contributions per pair (i, j) -> score
            encoder: The encoder with column order information
            
        Returns:
            Dictionary with:
                - matrix: n_cols x n_cols matrix of signed contributions
                - column_names: List of column names in order
                - column_to_index: Mapping from column name to matrix index
                - description: Explanation of what the values mean
        """
        # Get column order from encoder
        if hasattr(encoder, 'idx_to_col_name'):
            # Use encoder's mapping (most reliable)
            idx_to_col = encoder.idx_to_col_name
            col_order = [idx_to_col[i] for i in sorted(idx_to_col.keys())]
        elif hasattr(encoder, 'column_order'):
            col_order = encoder.column_order
        elif hasattr(encoder, 'effective_col_order'):
            col_order = encoder.effective_col_order
        else:
            # Fallback: extract from feature scores
            col_order = list(feature_signed_scores.keys())
        
        n_cols = len(col_order)
        
        # Create mapping from column name to index
        col_to_idx = {col: idx for idx, col in enumerate(col_order)}
        
        # Initialize heatmap matrix (n_cols x n_cols)
        # Values are signed contributions: 
        # - Positive = pushes toward class B (rowB)
        # - Negative = pushes toward class A (rowA)
        # - Magnitude = strength of contribution
        heatmap_matrix = [[0.0 for _ in range(n_cols)] for _ in range(n_cols)]
        
        # Fill in pair contributions f_ij(x)
        for (i, j), signed_score in pair_signed_scores.items():
            # i and j are column indices from relationship extractor
            # They correspond to positions in encoder's column order
            if isinstance(i, int) and isinstance(j, int):
                if 0 <= i < n_cols and 0 <= j < n_cols:
                    # Set both (i,j) and (j,i) since relationships are symmetric
                    # Use the signed contribution directly
                    heatmap_matrix[i][j] = signed_score
                    heatmap_matrix[j][i] = signed_score  # Symmetric
        
        # Diagonal is zero (no self-interactions) - already initialized to 0.0
        # Could optionally use unary terms f_i(x_i) from feature_signed_scores here
        
        # Convert to numpy array for easier plotting (if available)
        try:
            import numpy as np
            matrix_array = np.array(heatmap_matrix)
        except ImportError:
            matrix_array = heatmap_matrix  # Fallback to list if numpy not available
        
        return {
            'data': matrix_array,  # n_cols x n_cols matrix ready for plotting
            'x_labels': col_order,  # Column names for x-axis
            'y_labels': col_order,  # Column names for y-axis (same as x)
            'column_names': col_order,  # Alias for compatibility
            'column_to_index': col_to_idx,  # Mapping for lookup
            'description': 'Signed contributions f_ij(x): positive = pushes toward class B (rowB), negative = pushes toward class A (rowA). Diagonal is zero (no self-interactions).',
            'color_interpretation': {
                'positive': 'Pushes toward class B (rowB)',
                'negative': 'Pushes toward class A (rowA)',
                'magnitude': 'Strength of contribution',
                'diagonal': 'Zero (no self-interactions)',
            },
            'plotting_hints': {
                'colormap': 'RdBu_r',  # Red-Blue diverging (red=negative, blue=positive)
                'center': 0.0,  # Center colormap at zero
                'vmin': None,  # Auto-scale based on data
                'vmax': None,  # Auto-scale based on data
                'mask_diagonal': True,  # Option to mask diagonal in visualization
            }
        }
    
    def encode_field(self, column_name, values):
        # Encode individual values using an encoder for a specific column.

        if column_name not in self.col_codecs:
            raise ValueError(f"Cannot encode values for column {column_name}.")

        col_codec = self.col_codecs[column_name]
        tokens = create_token_batch([col_codec.tokenize(value) for value in values])
        return col_codec.encode(tokens)

    # TODO: a function that converts an entire df column into a batch token, in a single go.

    def encode_record(self, record, squeeze=True, short=False, output_device=None):
        # Encode an entire record using the full joint encoder.
        # print("ENCODING!!", record)
        # print("... col_codecs = ", self.col_codecs)
        # print("...")
        # record is provided as a dictionary {field: value}
        
        # Get logger from the current module
        import logging
        logger = logging.getLogger(__name__)
        
        # CRITICAL: Check if encoder is None and try to recover
        if self.encoder is None:
            logger.error(f"🚨 CRITICAL: EmbeddingSpace.encoder is None - cannot encode records!")
            logger.error(f"   This usually means the encoder failed to load during unpickling.")
            logger.error(f"   Checking if we can recreate it...")
            
            # Try to recreate encoder if we have the necessary components
            if hasattr(self, 'col_codecs') and self.col_codecs and hasattr(self, 'encoder_config') and self.encoder_config:
                try:
                    logger.info(f"   Attempting to recreate encoder from col_codecs and encoder_config...")
                    from featrix.neural.encoders import FeatrixTableEncoder
                    # Use stored masking parameters or defaults for older models
                    min_mask = getattr(self, 'min_mask_ratio', 0.40)
                    max_mask = getattr(self, 'max_mask_ratio', 0.60)
                    mean_nulls = getattr(self, 'mean_nulls_per_row', None)
                    self.encoder = FeatrixTableEncoder(
                        col_codecs=self.col_codecs,
                        config=self.encoder_config,
                        min_mask_ratio=min_mask,
                        max_mask_ratio=max_mask,
                        mean_nulls_per_row=mean_nulls,
                    )
                    # Move to CPU to avoid GPU allocation issues
                    self.encoder = self.encoder.cpu()
                    logger.warning(f"   ⚠️  Recreated encoder structure, but it has UNTRAINED weights!")
                    logger.warning(f"   This encoder will not produce meaningful encodings without trained weights.")
                    logger.warning(f"   The embedding space file may be corrupted or incomplete.")
                    # Don't raise error yet - let it fail when trying to use untrained weights
                except Exception as e:
                    logger.error(f"   ❌ Failed to recreate encoder: {e}")
                    logger.error(traceback.format_exc())
                    raise AttributeError(
                        f"EmbeddingSpace.encoder is None and cannot be recreated. "
                        f"This usually means the embedding space file is corrupted or incomplete. "
                        f"Original error during unpickling may have been logged. "
                        f"Recreation attempt failed: {e}"
                    )
            else:
                missing = []
                if not hasattr(self, 'col_codecs') or not self.col_codecs:
                    missing.append('col_codecs')
                if not hasattr(self, 'encoder_config') or not self.encoder_config:
                    missing.append('encoder_config')
                raise AttributeError(
                    f"EmbeddingSpace.encoder is None and cannot be recreated. "
                    f"Missing required components: {', '.join(missing)}. "
                    f"This usually means the embedding space file is corrupted or incomplete. "
                    f"Original error during unpickling may have been logged."
                )
        
        # FIXME: we'll need to call out to the other ES for the json columns here to get the encoding of their fields, if any are here.
        
        # Debug counter for tracking problematic records
        # debug_count = getattr(self, '_encode_record_debug_count', 0)
        # should_debug = debug_count < 5  # Debug first 5 records
        
        # if should_debug:
        #     logger.info(f"🔍 ENCODE_RECORD DEBUG #{debug_count}: Starting record encoding")
        #     logger.info(f"   Record fields: {list(record.keys())}")
        #     logger.info(f"   Available codecs: {list(self.col_codecs.keys())}")
        
        record_tokens = {}
        for field, value in record.items():
            field = field.strip()
            
            # CRITICAL: __featrix* columns must NEVER be encoded!
            # If we find a codec for __featrix* fields, something went very wrong!
            if field.startswith('__featrix'):
                if field in self.col_codecs:
                    logger.error(f"🚨 CRITICAL ERROR: Found codec for internal field '{field}' - this should have been ignored during training!")
                    logger.error(f"🚨 This means __featrix* columns leaked into the training data!")
                    raise ValueError(f"CRITICAL: Internal column '{field}' has a codec! This should never happen. __featrix* columns must be excluded from training.")
                # Skip encoding internal fields regardless
                continue
            
            # print("record for loop: ", field, value)
            # If the field is not present in the codecs, it can't be tokenized,
            # and doesn't participate in the encoding, so we skip it
            if field not in self.col_codecs:
                if field not in self._warningEncodeFields:
                    self._warningEncodeFields.append(field)
                continue

            codec = self.col_codecs[field]
            token = codec.tokenize(value)
            
            # Check if this specific token has NaN values
            # if should_debug:
            #     if hasattr(token.value, 'isnan') and torch.isnan(token.value).any():
            #         logger.error(f"🚨 FIELD TOKENIZATION PRODUCED NaN: {field}='{value}' -> {token}")
            #         logger.error(f"   Token value shape: {token.value.shape if hasattr(token.value, 'shape') else 'No shape'}")
            #         logger.error(f"   Token status: {token.status}")
            #         logger.error(f"   Codec type: {type(codec).__name__}")
            #     else:
            #         logger.info(f"   ✅ Field '{field}': {type(codec).__name__} -> OK (shape: {token.value.shape if hasattr(token.value, 'shape') else 'No shape'})")
                
            #     # CRITICAL DEBUG: For SET encoders, check token status and values
            #     if type(codec).__name__ == 'SetCodec':
            #         logger.error(f"🔍 SET DEBUG '{field}': value='{value}' -> token.value={token.value} status={token.status}")
            #         if hasattr(codec, 'members_to_tokens'):
            #             logger.error(f"   Available members: {list(codec.members_to_tokens.keys())[:10]}...")  # First 10
            #             if str(value) in codec.members_to_tokens:
            #                 expected_token = codec.members_to_tokens[str(value)]
            #                 logger.error(f"   Expected token for '{value}': {expected_token}")
            #             else:
            #                 logger.error(f"   ❌ VALUE '{value}' NOT FOUND in codec members!")
            
            record_tokens[field] = token

        # Rate-limited logging for missing codec fields (once per hour)
        # Use global cache since each API request loads a fresh EmbeddingSpace instance from disk
        if self._warningEncodeFields:
            global _MISSING_CODEC_WARNING_CACHE
            current_time = time.time()
            
            # Create a unique key for this specific set of missing fields
            missing_fields_key = frozenset(self._warningEncodeFields)
            
            # Check if we've logged this combination recently
            last_logged = _MISSING_CODEC_WARNING_CACHE.get(missing_fields_key)
            should_log = (
                last_logged is None or
                (current_time - last_logged) >= 3600  # 3600 seconds = 1 hour
            )
            
            if should_log:
                logger.warning(f"encode_record: {len(self._warningEncodeFields)} field(s) without codecs (skipped): {', '.join(sorted(self._warningEncodeFields))}")
                _MISSING_CODEC_WARNING_CACHE[missing_fields_key] = current_time

        # print("record tokens:", record_tokens)

        # Get the dictionary that contains NOT_PRESENT tokens for all fields
        # that are expected by the encoder. This makes sure that even if the user
        # passes in a partial record, we can encode it. The values that are not in
        # the `record` dictionary just remain as NOT_PRESENT, and those that are present
        # are replaced with their correct values.
        batch_tokens = self._get_base_token_dict()
        
        # if should_debug:
        #     logger.info(f"   Base token dict fields: {list(batch_tokens.keys())}")
        
        # print("... record_tokens =", record_tokens)
        # print("batch tokens before:", batch_tokens)
        # Replace the default NOT_PRESENT tokens in the batch with
        # tokens corresponding to fields in the record.

        for field, token in record_tokens.items():
            # print("FIELD: __%s__, token: __%s__" % (field, token))
            batch_tokens[field] = create_token_batch([token])

        # CRITICAL: Check if batch_tokens is empty before encoding
        # This can happen if the query record has no fields that match the trained codecs
        if not batch_tokens:
            logger.error(f"💥 CRITICAL: batch_tokens is EMPTY - no columns to encode!")
            logger.error(f"   Query record fields: {list(record.keys()) if record else 'None'}")
            logger.error(f"   Available codecs: {list(self.col_codecs.keys()) if self.col_codecs else 'None'}")
            logger.error(f"   Fields with codecs found: {list(record_tokens.keys()) if record_tokens else 'None'}")
            logger.error(f"   Fields skipped (no codec): {list(self._warningEncodeFields) if hasattr(self, '_warningEncodeFields') else 'None'}")
            raise RuntimeError(
                f"No columns could be encoded from the query record. "
                f"Query record has {len(record)} field(s): {list(record.keys())[:10]}, "
                f"but no fields match the {len(self.col_codecs)} trained codec(s): {list(self.col_codecs.keys())[:10]}. "
                f"This usually means the query record field names don't match the training data column names."
            )

        # print("... batch_tokens  = ", batch_tokens)
        # encoding = self.encoder(batch_tokens)
        
        # CRITICAL FIX: Only change training mode if we're currently in training
        # This prevents interfering with the training loop
        was_training_es = self.encoder.training
        should_restore_training = False
        
        # Only set to eval if we're currently training
        if was_training_es:
            # logger.info("Setting encoder.eval()")     # very spammy
            self.encoder.eval()
            should_restore_training = True
        
        # CRITICAL: Check if we're in single predictor training (CPU mode)
        # Don't move encoder to device if it's already on CPU and we're forcing CPU
        force_cpu_env = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR')
        if force_cpu_env == '1':
            # Force CPU mode - don't move encoder to device
            if list(self.encoder.parameters()):
                encoder_device = next(self.encoder.parameters()).device
                if encoder_device.type != 'cpu':
                    self.encoder.cpu()
        else:
            # Normal mode - move to device
            self.encoder.to(get_device())
        
        # if should_debug:
        #     logger.info(f"   Encoder device: {next(self.encoder.parameters()).device}")
        #     logger.info(f"   Encoder training mode: {self.encoder.training}")
        #     logger.info(f"   Was training before: {was_training_es}")
        #     logger.info(f"   Will restore training: {should_restore_training}")
        
        # ROOT CAUSE DEBUGGING: Let's see what's going into the encoder
        # if should_debug:
        #     logger.info(f"🔍 DEBUGGING INPUT TO ENCODER:")
        #     for field_name, token_batch in batch_tokens.items():
        #         if hasattr(token_batch, 'values'):
        #             values = token_batch.values
        #             if hasattr(values, 'isnan'):
        #                 has_nan = torch.isnan(values).any()
        #                 has_inf = torch.isinf(values).any()
        #                 zero_tensor = torch.zeros_like(values)
        #                 is_zero = torch.allclose(values, zero_tensor)
        #                 logger.info(f"   Field '{field_name}': shape={values.shape}, has_nan={has_nan}, has_inf={has_inf}, all_zero={is_zero}")
        #                 if has_nan or has_inf:
        #                     logger.error(f"   🚨 PROBLEMATIC INPUT: {field_name} = {values}")
        
        with torch.no_grad():
            short_encoding, full_encoding = self.encoder.encode(batch_tokens)
        
        # CRITICAL: Crash hard if encoder produces NaN - no masking allowed
        if torch.isnan(short_encoding).any() or torch.isnan(full_encoding).any():
            short_nan_count = torch.isnan(short_encoding).sum()
            full_nan_count = torch.isnan(full_encoding).sum()
            
            logger.error(f"💥 FATAL: Encoder produced NaN values - MODEL IS BROKEN")
            logger.error(f"🔍 COMPREHENSIVE DIAGNOSTICS:")
            logger.error(f"   Short encoding NaN: {short_nan_count}/{short_encoding.numel()}")
            logger.error(f"   Full encoding NaN: {full_nan_count}/{full_encoding.numel()}")
            logger.error(f"   Input record: {record}")
            logger.error(f"   Record fields: {list(record.keys())}")
            
            # Show codec types for failing fields
            failing_codecs = {}
            for field_name in record.keys():
                if field_name in self.col_codecs:
                    codec = self.col_codecs[field_name]
                    failing_codecs[field_name] = type(codec).__name__
            logger.error(f"   Codec types: {failing_codecs}")
            
            # Find which fields might be problematic
            problematic_fields = []
            for field_name, token in record_tokens.items():
                if hasattr(token.value, 'isnan') and torch.isnan(token.value).any():
                    problematic_fields.append(field_name)
            
            if problematic_fields:
                logger.error(f"   Fields with NaN tokens: {problematic_fields}")
            
            # Check for enriched fields specifically 
            # enriched_fields = [f for f in record.keys() if '.dict.' in f]
            # if enriched_fields:
            #     logger.error(f"   Enriched (.dict.*) fields: {enriched_fields[:10]}...")  # First 10
            
            logger.error(f"💀 CRASHING: NaN encodings produce meaningless results")
            logger.error(f"    Fix the root cause - don't mask with random vectors!")
            logger.error(f"    Check: model parameters, tokenization, codec initialization")
            
            raise RuntimeError(
                f"FATAL MODEL FAILURE: Encoder produced {short_nan_count + full_nan_count} NaN values. "
                f"This indicates serious model corruption, bad parameters, or tokenization failure. "
                f"Record fields: {list(record.keys())[:5]}... "
            )
        # elif should_debug:
        #     logger.info(f"   ✅ Encoder output clean: short={short_encoding.shape}, full={full_encoding.shape}")
        
        # CRITICAL FIX: Only restore training mode if we changed it
        if should_restore_training:
            # logger.info("Setting encoder.train()")
            self.encoder.train()

        # If squeeze is True, we want just the encoding, and not a batch, so
        # squeeze the extra dimension out.
        if squeeze is True:
            short_encoding = short_encoding.squeeze(dim=0)
            full_encoding = full_encoding.squeeze(dim=0)

        output_device = output_device or torch.device("cpu")
        
        # if should_debug:
        #     logger.info(f"   Moving to output device: {output_device}")
        #     # Final check after device move
        #     result_short = short_encoding.detach().to(output_device)
        #     result_full = full_encoding.detach().to(output_device)
            
        #     if torch.isnan(result_short).any():
        #         logger.error(f"🚨 FINAL SHORT RESULT HAS NaN: {result_short}")
        #     if torch.isnan(result_full).any():
        #         logger.error(f"🚨 FINAL FULL RESULT HAS NaN: {result_full}")
            
        #     logger.info(f"   Final result shapes: short={result_short.shape}, full={result_full.shape}")
        #     self._encode_record_debug_count = debug_count + 1
        
        if short:
            return short_encoding.detach().to(output_device)
        else:
            return full_encoding.detach().to(output_device)

    def compute_field_similarity(self, query_record, result_record, distance_metric='euclidean'):
        """
        Compute field-level similarity between a query record and a result record.
        
        For each field that exists in both records, encode just that field's value
        and compute the distance between the query field embedding and the result field embedding.
        
        Args:
            query_record: Dictionary of query record fields {field: value}
            result_record: Dictionary of result record fields {field: value}
            distance_metric: Distance metric to use ('euclidean' or 'cosine')
        
        Returns:
            Dictionary with field-level distances: {field: distance}
        
        Raises:
            ValueError: If query_record is empty or has no valid fields
        """
        # Validate input
        if not query_record or len(query_record) == 0:
            raise ValueError("query_record is empty - cannot compute field similarity without query fields")
        
        if not result_record or len(result_record) == 0:
            raise ValueError("result_record is empty - cannot compute field similarity")
        
        field_distances = {}
        
        # Get the common fields that are in both records and have codecs
        common_fields = set(query_record.keys()) & set(result_record.keys()) & set(self.col_codecs.keys())
        
        # Filter out metadata fields
        common_fields = {f for f in common_fields if not f.startswith('__featrix_')}
        
        if not common_fields:
            raise ValueError(
                f"No common fields found between query and result. "
                f"Query fields: {list(query_record.keys())}, "
                f"Result fields: {list(result_record.keys())}, "
                f"Trained codecs: {list(self.col_codecs.keys())}"
            )
        
        for field in common_fields:
                
            try:
                # Create single-field records
                query_single_field = {field: query_record[field]}
                result_single_field = {field: result_record[field]}
                
                # Encode each field independently
                # Use full embeddings for better discrimination
                query_field_embedding = self.encode_record(query_single_field, short=False, output_device=torch.device("cpu"))
                result_field_embedding = self.encode_record(result_single_field, short=False, output_device=torch.device("cpu"))
                
                # Compute distance
                if distance_metric == 'euclidean':
                    distance = torch.dist(query_field_embedding, result_field_embedding, p=2).item()
                elif distance_metric == 'cosine':
                    # Cosine distance = 1 - cosine similarity
                    cos_sim = torch.nn.functional.cosine_similarity(
                        query_field_embedding.unsqueeze(0), 
                        result_field_embedding.unsqueeze(0)
                    ).item()
                    distance = 1.0 - cos_sim
                else:
                    raise ValueError(f"Unknown distance metric: {distance_metric}")
                
                field_distances[field] = distance
                
            except Exception as e:
                logger.warning(f"Failed to compute field similarity for field '{field}': {e}")
                # Store None to indicate this field couldn't be compared
                field_distances[field] = None
        
        return field_distances

    def compute_embedding_quality(
        self,
        sample_records: Optional[List[Dict]] = None,
        sample_size: int = 100,
        labels: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute comprehensive quality metrics for the embedding space.
        
        Args:
            sample_records: Optional list of records to encode. If None, uses validation data.
            sample_size: Number of samples to use for quality assessment (default: 100)
            labels: Optional list of labels for each record (for separation metrics)
            
        Returns:
            Dict with quality scores:
            - overall_score: Combined quality score [0, 1]
            - separation_score: Class separation quality [0, 1]
            - clustering_score: Clustering quality [0, 1]
            - interpolation_score: Interpolation smoothness [0, 1]
            - detailed_metrics: Dict with detailed sub-metrics
        """
        # Get sample records
        if sample_records is None:
            # Use validation data
            if hasattr(self, 'val_input_data') and self.val_input_data is not None:
                val_df = self.val_input_data.df
                sample_size = min(sample_size, len(val_df))
                sample_df = val_df.sample(n=sample_size, random_state=42) if len(val_df) > sample_size else val_df
                sample_records = sample_df.to_dict('records')
            else:
                raise ValueError("No sample_records provided and no validation data available")
        
        # Limit sample size
        sample_records = sample_records[:sample_size]
        
        # Encode all records
        embeddings_list = []
        for record in sample_records:
            try:
                embedding = self.encode_record(record, squeeze=True, short=False, output_device=torch.device("cpu"))
                embeddings_list.append(embedding)
            except Exception as e:
                logger.warning(f"Failed to encode record for quality assessment: {e}")
                continue
        
        if not embeddings_list:
            raise ValueError("No valid embeddings could be computed")
        
        # Stack into tensor
        embeddings = torch.stack(embeddings_list)
        
        # Compute quality metrics
        metadata = {
            'n_samples': len(embeddings_list),
            'd_model': embeddings.shape[1],
            'sample_size': sample_size
        }
        
        quality_metrics = compute_embedding_quality_metrics(
            embeddings=embeddings,
            labels=labels[:len(embeddings_list)] if labels else None,
            metadata=metadata
        )
        
        return quality_metrics

    def compare_with_other_embedding_space(
        self,
        other_embedding_space: 'EmbeddingSpace',
        sample_records: Optional[List[Dict]] = None,
        sample_size: int = 100,
        labels: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare this embedding space with another embedding space.
        
        Args:
            other_embedding_space: Another EmbeddingSpace instance to compare with
            sample_records: Optional list of records to encode. If None, uses validation data.
            sample_size: Number of samples to use for comparison (default: 100)
            labels: Optional list of labels for each record (for separation metrics)
            
        Returns:
            Dict with comparison metrics:
            - quality_scores_1: Quality metrics for this space
            - quality_scores_2: Quality metrics for other space
            - difference_score: Overall difference between spaces [0, 1]
            - embedding_difference: Direct embedding comparison metrics
            - recommendations: Suggestions based on comparison
        """
        # Get sample records
        if sample_records is None:
            # Use validation data from this space
            if hasattr(self, 'val_input_data') and self.val_input_data is not None:
                val_df = self.val_input_data.df
                sample_size = min(sample_size, len(val_df))
                sample_df = val_df.sample(n=sample_size, random_state=42) if len(val_df) > sample_size else val_df
                sample_records = sample_df.to_dict('records')
            else:
                raise ValueError("No sample_records provided and no validation data available")
        
        # Limit sample size
        sample_records = sample_records[:sample_size]
        
        # Encode records with both spaces
        embeddings1_list = []
        embeddings2_list = []
        valid_indices = []
        
        for i, record in enumerate(sample_records):
            try:
                emb1 = self.encode_record(record, squeeze=True, short=False, output_device=torch.device("cpu"))
                emb2 = other_embedding_space.encode_record(record, squeeze=True, short=False, output_device=torch.device("cpu"))
                embeddings1_list.append(emb1)
                embeddings2_list.append(emb2)
                valid_indices.append(i)
            except Exception as e:
                logger.warning(f"Failed to encode record {i} for comparison: {e}")
                continue
        
        if not embeddings1_list:
            raise ValueError("No valid embeddings could be computed for comparison")
        
        # Stack into tensors
        embeddings1 = torch.stack(embeddings1_list)
        embeddings2 = torch.stack(embeddings2_list)
        
        # Filter labels to match valid indices
        valid_labels = None
        if labels:
            valid_labels = [labels[i] for i in valid_indices]
        
        # Compute comparison
        metadata1 = {'n_samples': len(embeddings1_list), 'd_model': embeddings1.shape[1]}
        metadata2 = {'n_samples': len(embeddings2_list), 'd_model': embeddings2.shape[1]}
        
        comparison = compare_embedding_spaces(
            embeddings1=embeddings1,
            embeddings2=embeddings2,
            labels=valid_labels,
            metadata1=metadata1,
            metadata2=metadata2
        )
        
        return comparison

    def register_callback(self, type, callback_fn):
        callback_id = uuid.uuid4()
        self.callbacks[type][callback_id] = callback_fn

    def remove_callback(self, type, callback_id):
        try:
            del self.callbacks[type][callback_id]
        except KeyError:
            # Ignore key errors - if the callback does not exist,
            # removing doesn't matter.
            pass

    def run_callbacks(self, type, *args, **kwargs):
        for callback_id, callback_fn in self.callbacks[type].items():
            callback_fn(callback_id, *args, **kwargs)

    @staticmethod
    def safe_dump(package: Dict):
        if package.get("print_callback"):
            del package["print_callback"]

    def compute_val_loss(self, val_dataloader):
        was_training_es = self.encoder.training

        # CRITICAL: AGGRESSIVE GPU cache clearing BEFORE validation to defragment memory
        # Training leaves memory fragmented ("reserved but unallocated") which can cause
        # OOM during validation even when total free memory would be sufficient.
        # The aggressive clear does multiple passes with gc.collect() between iterations
        # to consolidate fragmented memory into contiguous blocks.
        try:
            if is_gpu_available():
                # Log memory state before cleanup
                allocated_before = get_gpu_memory_allocated()
                reserved_before = get_gpu_memory_reserved()
                logger.debug(f"   💾 Pre-validation memory: {allocated_before:.2f} GB allocated, {reserved_before:.2f} GB reserved")
                
                # Aggressive multi-pass clearing to defragment memory
                clear_result = aggressive_clear_gpu_cache(iterations=3, do_gc=True)
                synchronize_gpu()
                
                if clear_result:
                    final = clear_result.get('final', {})
                    allocated_after = final.get('allocated_gb', 0)
                    reserved_after = final.get('reserved_gb', 0)
                    freed = reserved_before - reserved_after
                    if freed > 0.1:  # Only log if we freed significant memory
                        logger.info(f"   💾 Freed {freed:.2f} GB of fragmented GPU memory before validation")
        except Exception as e:
            logger.debug(f"Failed to clear GPU cache before validation: {e}")

        with torch.no_grad():
            self.encoder.eval()

            batch_sizes = []
            batch_losses = []
            batch_loss_dicts = []
            val_batch_count = 0
            total_val_batches = len(val_dataloader) if hasattr(val_dataloader, '__len__') else None
            
            # Heartbeat for long validation runs
            val_start_time = time.time()
            last_heartbeat_time = val_start_time
            
            for batch in val_dataloader:
                val_batch_count += 1
                current_time = time.time()
                
                # Log validation progress every 5 batches or if we know the total
                if total_val_batches and (val_batch_count % 5 == 0 or val_batch_count == 1):
                    logger.info(f"      Validation batch {val_batch_count}/{total_val_batches}...")
                elif not total_val_batches and val_batch_count % 5 == 0:
                    logger.info(f"      Validation batch {val_batch_count}...")
                
                # Heartbeat: log every 30 seconds if validation is taking a long time
                if current_time - last_heartbeat_time >= 30.0:
                    elapsed = current_time - val_start_time
                    if total_val_batches:
                        logger.info(f"      ⏱️  Validation in progress: {val_batch_count}/{total_val_batches} batches ({elapsed:.1f}s elapsed)...")
                    else:
                        logger.info(f"      ⏱️  Validation in progress: {val_batch_count} batches ({elapsed:.1f}s elapsed)...")
                    last_heartbeat_time = current_time
                # Different datasets have different columns, but we want to
                # find out the length of any of the columns, because the token batch
                # for every column have the same length.
                first_column_token_batch = next(iter(batch.items()))[1]
                batch_size = len(first_column_token_batch)

                encodings = self.encoder(batch)
                batch_loss, loss_dict = self.encoder.compute_total_loss(*encodings)

                batch_sizes.append(batch_size)
                batch_losses.append(batch_loss.item())
                batch_loss_dicts.append(loss_dict)
                
                # CRITICAL: Explicitly delete batch data to free memory immediately
                # Without this, DataLoader workers can accumulate memory over many epochs
                del batch
                del encodings
                del batch_loss
                # Don't delete loss_dict - we need it in batch_loss_dicts
                
                # Periodic GPU cache clearing during validation (every 10 batches)
                # This prevents memory buildup in DataLoader workers
                if val_batch_count % 10 == 0:
                    try:
                        if is_gpu_available():
                            empty_gpu_cache()
                    except Exception:
                        pass  # Don't fail validation on cleanup errors

            if was_training_es:
                self.encoder.train()
            
            # CRITICAL: Clean up after validation to prevent memory leaks
            # Force garbage collection and clear GPU cache
            gc.collect()
            try:
                if is_gpu_available():
                    empty_gpu_cache()
                    synchronize_gpu()
            except Exception as e:
                logger.debug(f"Failed to clear GPU cache after validation: {e}")

        n_batches = len(batch_losses)

        if n_batches > 1:
            first_batch_size = batch_sizes[0]
            last_batch_size = batch_sizes[-1]

            # If the last batch is smaller than the first batch size,
            # it means that it's shorter than all other batches, and we discard it
            # because we use a contrastive loss function, and the batch size affects
            # the loss value, and therefore averaging losses from batches of different size
            # would give results which could not be easily interpreted.
            # NOTE: dropping the last, shorter batch, means that the size of the dataset
            # ACTUALLY used for validaton will be shorter than might appear from the outside
            # if we just call len(val_dataset).
            if first_batch_size > last_batch_size:
                batch_losses = batch_losses[:-1]
                batch_loss_dicts = batch_loss_dicts[:-1]
                n_batches = len(batch_losses)

        combined_loss = sum(batch_losses)

        # Return the average loss per example. The values that combined to give us
        # `combined_loss` are the average losses per example in each batch, so we
        # divide by the number of batches to get the average loss per example across
        # the entire dataset. This is OK because all batches are the same size.
        if n_batches == 0:
            logger.warning("No validation batches computed - returning zero loss")
            return 0.0, None
        
        # Log validation loss components (average across batches)
        components = {}
        # Always include batch info for diagnostics
        components['_batch_losses'] = [float(l) for l in batch_losses]
        components['_batch_sizes'] = [int(s) for s in batch_sizes]
        
        if batch_loss_dicts:
            avg_loss_dict = batch_loss_dicts[0]  # Use first batch's structure
            avg_spread = sum(d['spread_loss']['total'] for d in batch_loss_dicts) / n_batches
            avg_joint = sum(d['joint_loss']['total'] for d in batch_loss_dicts) / n_batches
            avg_marginal = sum(d['marginal_loss']['total'] for d in batch_loss_dicts) / n_batches
            
            # Get the BASE marginal weight from the encoder config
            # Get current marginal loss weight from config (scaling coefficient is now applied to loss value, not weight)
            # So config_marginal_weight is the actual weight being used
            current_marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
            
            # CRITICAL: NO MARGINAL LOSS SCALING COEFFICIENT
            # The scaling coefficient was multiplying by ~0.017 (dividing by ~60)
            # This was ANOTHER gradient reduction on top of the /normalizer
            # Combined: gradients were reduced by 60× (coefficient) × 327× (normalizer) = 19,620×!
            # Now we use raw marginal loss and let curriculum weight (0.005-0.03) handle balance
            
            # Disable scaling coefficient - use raw marginal
            self._marginal_loss_scaling_coefficient = None
            self.encoder.config.loss_config.marginal_loss_scaling_coefficient = None
            logger.info(f"📊 Marginal loss scaling DISABLED - using raw marginal loss")
            logger.info(f"   (spread={avg_spread:.4f}, joint={avg_joint:.4f}, marginal={avg_marginal:.4f})")
            logger.info(f"   Curriculum weight (0.005-0.03) will handle relative importance")
            
            # No scaling - use raw marginal
            avg_marginal_scaled = avg_marginal
            
            # Apply current weight to get weighted contribution
            avg_marginal_weighted = avg_marginal_scaled * current_marginal_weight
            
            # Compute worst-case InfoNCE loss for normalization
            # Worst case (random): loss = log(batch_size)
            # Best case (perfect): loss = 0
            # Normalized: actual / log(batch_size) gives 0-1 scale (0=perfect, 1=random, >1=worse than random)
            if batch_loss_dicts and batch_sizes:
                avg_batch_size = sum(batch_sizes) / len(batch_sizes)
                worst_case_infonce = math.log(avg_batch_size)
                # Normalize marginal loss: 0=perfect, 1=random
                marginal_normalized = avg_marginal / worst_case_infonce if worst_case_infonce > 0 else 0.0
            else:
                worst_case_infonce = 0.0
                marginal_normalized = 0.0
            
            # Extract spread loss sub-components
            avg_spread_full = sum(d['spread_loss']['full']['total'] for d in batch_loss_dicts) / n_batches
            avg_spread_short = sum(d['spread_loss']['short']['total'] for d in batch_loss_dicts) / n_batches
            
            # Extract full spread breakdown (joint + mask1 + mask2)
            avg_spread_full_joint = sum(d['spread_loss']['full']['joint'] for d in batch_loss_dicts) / n_batches
            avg_spread_full_mask1 = sum(d['spread_loss']['full']['mask_1'] for d in batch_loss_dicts) / n_batches
            avg_spread_full_mask2 = sum(d['spread_loss']['full']['mask_2'] for d in batch_loss_dicts) / n_batches
            
            # Extract RAW marginal loss (before normalization) for diagnostics
            avg_marginal_raw = sum(d['marginal_loss'].get('raw', d['marginal_loss']['total']) for d in batch_loss_dicts) / n_batches
            avg_marginal_normalizer = sum(d['marginal_loss'].get('normalizer', 1.0) for d in batch_loss_dicts) / n_batches
            
            # Extract short spread breakdown (joint + mask1 + mask2)
            avg_spread_short_joint = sum(d['spread_loss']['short']['joint'] for d in batch_loss_dicts) / n_batches
            avg_spread_short_mask1 = sum(d['spread_loss']['short']['mask_1'] for d in batch_loss_dicts) / n_batches
            avg_spread_short_mask2 = sum(d['spread_loss']['short']['mask_2'] for d in batch_loss_dicts) / n_batches
            
            # Helper function to convert tensor values to Python floats for JSON serialization
            def to_float(val):
                if val is None:
                    return None
                if hasattr(val, 'item'):
                    return float(val.item())
                return float(val)
            
            components = {
                'spread': to_float(avg_spread),
                'joint': to_float(avg_joint),
                'marginal': to_float(avg_marginal_scaled),  # Show scaled original marginal (not raw)
                'marginal_weighted': to_float(avg_marginal_weighted),
                'marginal_normalized': to_float(marginal_normalized),  # 0=perfect, 1=random
                'marginal_raw': to_float(avg_marginal_raw),  # Raw marginal (before normalization)
                'marginal_normalizer': to_float(avg_marginal_normalizer),  # Divisor used for normalization
                'worst_case_infonce': to_float(worst_case_infonce),  # log(batch_size)
                # Spread sub-components
                'spread_full': to_float(avg_spread_full),
                'spread_short': to_float(avg_spread_short),
                'spread_full_joint': to_float(avg_spread_full_joint),
                'spread_full_mask1': to_float(avg_spread_full_mask1),
                'spread_full_mask2': to_float(avg_spread_full_mask2),
                'spread_short_joint': to_float(avg_spread_short_joint),
                'spread_short_mask1': to_float(avg_spread_short_mask1),
                'spread_short_mask2': to_float(avg_spread_short_mask2),
            }
            # Batch info already added above, no need to add again
        
        # Return both total loss and components
        return combined_loss / n_batches, components

    def get_columns_with_codec_count(self, exclude_target_column=None):
        """
        Get count of columns with codecs (feature columns, not target).
        
        Args:
            exclude_target_column: Optional column name to exclude from count
                                   (used when checking for predictor training)
        
        Returns:
            int: Number of columns with codecs (excluding target if specified)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Always use col_codecs directly - it's the source of truth for what columns
        # were actually trained in the embedding space. train_input_data might be
        # recreated from SQLite and not match the original training data.
        if not self.col_codecs:
            logger.error(f"❌ CRITICAL: EmbeddingSpace.col_codecs is EMPTY or None!")
            logger.error(f"   This means the embedding space has no codecs - it cannot be used for training.")
            logger.error(f"   This is likely a data corruption or loading issue.")
            return 0
        
        codec_count = len(self.col_codecs)
        codec_keys = list(self.col_codecs.keys())
        
        logger.debug(f"🔍 get_columns_with_codec_count: total={codec_count}, exclude_target={exclude_target_column}")
        logger.debug(f"   Codec columns: {codec_keys[:20]}{'...' if len(codec_keys) > 20 else ''}")
        
        if exclude_target_column and exclude_target_column in self.col_codecs:
            # Exclude target column from count (we need at least 1 feature column)
            feature_count = codec_count - 1
            logger.debug(f"   Excluding target '{exclude_target_column}': {codec_count} -> {feature_count} feature columns")
            return feature_count
        
        logger.debug(f"   No target exclusion: returning {codec_count}")
        return codec_count

    def get_training_state_path(self, epoch=0, batch=0):
        """Get path for full training checkpoint (includes optimizer state for resuming)."""
        if batch == 0:
            path = f"{self.training_state_path}_e-{epoch}.pth"
        else:
            path = f"{self.training_state_path}_e-{epoch}_b-{batch}.pth"
        return path

    def get_inference_checkpoint_path(self, epoch=0, batch=0):
        """Get path for lightweight inference checkpoint (model only, no optimizer state)."""
        base_path = self.get_training_state_path(epoch, batch)
        # Replace checkpoint_resume_training with checkpoint_inference
        inference_path = base_path.replace('checkpoint_resume_training', 'checkpoint_inference')
        # Ensure .pt extension for inference checkpoints
        if inference_path.endswith('.pth'):
            inference_path = inference_path[:-4] + '.pt'
        return inference_path

    def get_best_checkpoint_path(self):
        # If we're saving the model because it's the best model so far, we want
        # its name to NOT contain epoch and batch information because we want it
        # to be overridden every time a better model is achieved.
        return f"{self.training_state_path}_BEST.pth"

    def find_latest_checkpoint(self, max_epoch: int = 10000) -> Optional[int]:
        """
        Find the latest valid checkpoint epoch with COLUMN VALIDATION.
        
        Searches backwards from max_epoch to find the most recent checkpoint
        that exists, can be loaded without errors, AND has matching columns.
        
        CRITICAL: Will NOT resume from checkpoints with different columns.
        This prevents garbage training when old checkpoints exist from different datasets.
        
        Args:
            max_epoch: Maximum epoch to search from (default 10000)
            
        Returns:
            The epoch number of the latest valid checkpoint with matching columns,
            or None if no valid checkpoint found.
        """
        from pathlib import Path
        
        # Get current column set for comparison
        # Get current columns - col_order is ALWAYS set during __init__
        current_cols = set(self.col_order)
        if not current_cols:
            # This should NEVER happen - if it does, something is seriously broken
            raise RuntimeError(
                "CRITICAL BUG: find_latest_checkpoint called but col_order is empty! "
                "EmbeddingSpace initialization failed silently. Cannot resume training."
            )
        
        logger.info(f"🔍 Searching for checkpoint with matching columns ({len(current_cols)} columns)...")
        
        for epoch in range(max_epoch, -1, -1):
            checkpoint_path = self.get_training_state_path(epoch, 0)
            if Path(checkpoint_path).exists():
                try:
                    # Load checkpoint and extract column info
                    checkpoint = torch.load(checkpoint_path, weights_only=False, map_location='cpu')
                    
                    # Try multiple ways to get checkpoint columns
                    checkpoint_cols = set()
                    
                    # Method 1: codec_metadata keys (most reliable)
                    if 'codec_metadata' in checkpoint:
                        checkpoint_cols = set(checkpoint['codec_metadata'].keys())
                    # Method 2: availableColumns 
                    elif 'availableColumns' in checkpoint:
                        checkpoint_cols = set(checkpoint['availableColumns'])
                    # Method 3: es_state.availableColumns
                    elif 'es_state' in checkpoint and 'availableColumns' in checkpoint['es_state']:
                        checkpoint_cols = set(checkpoint['es_state']['availableColumns'])
                    # Method 4: encoder_state_dict keys (parse column names)
                    elif 'encoder_state_dict' in checkpoint:
                        # Keys look like "column_encoder.encoders.column_name...."
                        for key in checkpoint['encoder_state_dict'].keys():
                            if key.startswith('column_encoder.encoders.'):
                                parts = key.split('.')
                                if len(parts) >= 3:
                                    checkpoint_cols.add(parts[2])
                    
                    if not checkpoint_cols:
                        logger.warning(f"⚠️  Checkpoint at epoch {epoch} has no column info - skipping: {checkpoint_path}")
                        continue
                    
                    # CRITICAL: Validate columns match exactly
                    if checkpoint_cols == current_cols:
                        logger.info(f"✅ Found valid checkpoint at epoch {epoch} with matching columns: {checkpoint_path}")
                        logger.info(f"   Checkpoint columns: {len(checkpoint_cols)}, Current columns: {len(current_cols)}")
                        return epoch
                    else:
                        # Column mismatch - DO NOT RESUME
                        missing_in_checkpoint = current_cols - checkpoint_cols
                        extra_in_checkpoint = checkpoint_cols - current_cols
                        logger.warning(f"❌ Checkpoint at epoch {epoch} has DIFFERENT COLUMNS - skipping: {checkpoint_path}")
                        if missing_in_checkpoint:
                            logger.warning(f"   Missing in checkpoint: {list(missing_in_checkpoint)[:5]}{'...' if len(missing_in_checkpoint) > 5 else ''}")
                        if extra_in_checkpoint:
                            logger.warning(f"   Extra in checkpoint: {list(extra_in_checkpoint)[:5]}{'...' if len(extra_in_checkpoint) > 5 else ''}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"⚠️  Checkpoint at epoch {epoch} is corrupted: {checkpoint_path} - {e}")
                    continue
        
        logger.info("🆕 No valid checkpoint with matching columns found - will start fresh")
        return None

    def save_es(self, local_path):
        self.hydrate_to_cpu_if_needed()


    def _extract_codec_metadata(self):
        """Extract serializable codec metadata for checkpoint validation and reconstruction.
        
        Returns dict of {col_name: {type, vocabulary/normalization params}}.
        Used by both training resume checkpoints and best model checkpoints.
        """
        codec_metadata = {}
        for col_name, codec in self.col_codecs.items():
            codec_meta = {
                "type": codec.get_codec_name() if hasattr(codec, 'get_codec_name') else type(codec).__name__,
            }
            
            # For SET codecs, save vocabulary
            if hasattr(codec, 'vocab'):
                codec_meta["vocabulary"] = list(codec.vocab.keys())
            
            # For SCALAR codecs, save normalization params
            if hasattr(codec, 'mean'):
                codec_meta["mean"] = float(codec.mean) if hasattr(codec.mean, 'item') else float(codec.mean)
            if hasattr(codec, 'std'):
                codec_meta["std"] = float(codec.std) if hasattr(codec.std, 'item') else float(codec.std)
            if hasattr(codec, 'min_val'):
                codec_meta["min_val"] = float(codec.min_val) if hasattr(codec.min_val, 'item') else float(codec.min_val)
            if hasattr(codec, 'max_val'):
                codec_meta["max_val"] = float(codec.max_val) if hasattr(codec.max_val, 'item') else float(codec.max_val)
            
            codec_metadata[col_name] = codec_meta
        
        return codec_metadata

    def save_best_for_inference(self, epoch, val_loss):
        """Save best model checkpoint for inference/deployment.
        
        Includes full model + complete ES state (codecs, configs, metadata).
        Saved to *_BEST.pth - overwrites previous best when validation improves.
        """
        codec_metadata = self._extract_codec_metadata()
        
        save_state = {
            "epoch_idx": epoch,
            "model": self.encoder,  # FULL encoder (PyTorch handles serialization)
            "val_loss": val_loss,
            "time": time.ctime(),
            # Save COMPLETE ES state - mix of serializable metadata + codec objects (PyTorch can handle)
            "es_state": {
                # Core attributes
                "d_model": self.d_model,
                "column_spec": {k: str(v) for k, v in self.column_spec.items()},  # Serialize ColumnType enums
                "availableColumns": self.availableColumns,
                "codec_metadata": codec_metadata,  # Serializable metadata for reference
                "col_codecs": self.col_codecs,  # ACTUAL codec objects (PyTorch can serialize these)
                
                # Config attributes  
                "n_layers": getattr(self, 'n_layers', None),
                "d_ff": getattr(self, 'd_ff', None),
                "n_heads": getattr(self, 'n_heads', None),
                "dropout": getattr(self, 'dropout', None),
                "n_epochs": self.n_epochs,
                
                # Metadata
                "session_id": getattr(self, 'session_id', None),
                "job_id": getattr(self, 'job_id', None),
                "name": self.name,
                "string_cache": self.string_cache,
                "json_transformations": getattr(self, 'json_transformations', {}),
                "required_child_es_mapping": getattr(self, 'required_child_es_mapping', {}),
                "user_metadata": getattr(self, 'user_metadata', None),
                "version_info": getattr(self, 'version_info', None),
                "output_debug_label": self.output_debug_label,
                
                # Training info
                "training_info": getattr(self, 'training_info', {}),
                
                # Customer quality trackers (per epoch)
                "customer_quality_trackers": {epoch: qt.to_dict() for epoch, qt in self.customer_quality_trackers.items()} if hasattr(self, 'customer_quality_trackers') and self.customer_quality_trackers else {},
            },
        }

        best_checkpoint_path = self.get_best_checkpoint_path()
        try:
            torch.save(save_state, best_checkpoint_path)
            epoch_num = save_state.get('epoch_idx', -1)
            # Show cumulative epoch for K-fold CV
            cumulative_epoch = epoch_num
            if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                cumulative_epoch = epoch_num + self._kv_fold_epoch_offset
            logger.info(f"🏆 Best model checkpoint saved to {best_checkpoint_path} (val_loss: {val_loss:.6f})")
        except Exception as e:
            # Re-raise so caller can handle it (caller should wrap in try/except)
            logger.error(f"❌ Failed to save best checkpoint at epoch {epoch}: {e}")
            raise

    def save_training_resume_point(self, epoch, batch, optimizer, scheduler, dropout_scheduler=None):
        """Save checkpoint for resuming training.
        
        Includes model state_dict + optimizer/scheduler state for exact resume.
        Includes column metadata for validation during resume.
        Saved to *_e-{epoch}.pth files.
        """
        codec_metadata = self._extract_codec_metadata()
        
        # Handle different scheduler types
        if isinstance(scheduler, LRTimeline):
            scheduler_state = scheduler.get_state_dict()
        else:
            scheduler_state = scheduler.state_dict() if scheduler is not None else None
        
        save_state = {
            "model": self.encoder.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler_state,
            "dropout_scheduler": dropout_scheduler.get_state_dict() if dropout_scheduler is not None else None,
            # CRITICAL: Column metadata for checkpoint validation during resume
            "availableColumns": self.availableColumns,
            "codec_metadata": codec_metadata,
        }

        checkpoint_path = self.get_training_state_path(epoch, batch)
        
        # Save lightweight checkpoint for projection building FIRST (every epoch)
        # This is small and needed for movie frames - prioritize it
        # Contains only what's needed for encoding: encoder model, codecs, column info
        # Does NOT include huge dataframes (train_input_data, val_input_data)
        embedding_space_checkpoint_path = self.get_inference_checkpoint_path(epoch, batch)
        embedding_space_checkpoint_saved = False
        try:
            # Ensure directory exists
            checkpoint_dir = Path(embedding_space_checkpoint_path).parent
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Save using atomic write (temp file then rename)
            temp_es_path = embedding_space_checkpoint_path + ".tmp"
            torch.save({
                'epoch': epoch,
                'encoder': self.encoder,  # The encoder model itself (not state_dict, the full model)
                'col_codecs': self.col_codecs,  # Codecs needed for encoding
                'col_order': self.col_order,  # Column order
                'column_spec': self.column_spec,  # Column specifications
                'encoder_config': self.encoder_config,  # Encoder configuration
                'd_model': self.d_model,  # Model dimension
                'use_bf16': getattr(self, 'use_bf16', False),  # BF16 mixed precision flag
                'json_transformations': getattr(self, 'json_transformations', {}),  # JSON transforms
                'required_child_es_mapping': getattr(self, 'required_child_es_mapping', {}),  # Child ES deps
                'schema_history': self.schema_history.to_dict() if hasattr(self, 'schema_history') else None,  # Schema provenance
                'customer_quality_trackers': {epoch: qt.to_dict() for epoch, qt in self.customer_quality_trackers.items()} if hasattr(self, 'customer_quality_trackers') and self.customer_quality_trackers else {},  # Customer quality metrics per epoch
            }, temp_es_path)
            # Atomic rename
            Path(temp_es_path).rename(embedding_space_checkpoint_path)
            
            # Verify the file was actually saved
            if Path(embedding_space_checkpoint_path).exists():
                embedding_space_checkpoint_saved = True
                file_size = Path(embedding_space_checkpoint_path).stat().st_size / (1024**2)
                logger.info(f"   ✅ Saved lightweight ES checkpoint: {file_size:.1f} MB - {embedding_space_checkpoint_path}")
                
                # Save schema history as separate JSON file for easy viewing
                if hasattr(self, 'schema_history'):
                    try:
                        schema_history_path = checkpoint_dir / f"schema_history_epoch_{epoch}.json"
                        self.schema_history.to_json(str(schema_history_path))
                    except Exception as e:
                        logger.warning(f"⚠️  Could not save schema history JSON: {e}")
            else:
                logger.error(f"❌ CRITICAL: Embedding space checkpoint file not found after save!")
                logger.error(f"   Expected path: {embedding_space_checkpoint_path}")
                logger.error(f"   Temp path existed: {Path(temp_es_path).exists()}")
                logger.error(f"   Checkpoint dir exists: {checkpoint_dir.exists()}")
                logger.error(f"   Checkpoint dir: {checkpoint_dir}")
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to save embedding_space checkpoint: {e}")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Checkpoint path: {embedding_space_checkpoint_path}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            # Clean up temp file if it exists
            temp_es_path = embedding_space_checkpoint_path + ".tmp"
            if Path(temp_es_path).exists():
                try:
                    Path(temp_es_path).unlink()
                except Exception:
                    pass
        
        # Store flag so _queue_project_training_movie_frame can check if checkpoint was saved
        self._last_embedding_space_checkpoint_saved = embedding_space_checkpoint_saved

        # NOTE: The old "resume checkpoint" (checkpoint_resume_training_e-*.pth) has been removed.
        # It only saved state_dict() without es_state, which broke SP training trying to load it.
        # The inference checkpoint above has everything needed (full encoder + codecs + column info).
        # TODO: Clean up - remove the old checkpoint_path variable and save_state dict above.
        
        # Use atomic write: save to temp file first, then rename
        try:
            checkpoint_dir = Path(checkpoint_path).parent
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Create temp file in same directory for atomic write
            temp_path = checkpoint_path + ".tmp"
            
            # Try saving with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    torch.save(save_state, temp_path)
                    # Atomic rename
                    Path(temp_path).rename(checkpoint_path)
                    break
                except (RuntimeError, OSError, IOError) as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  Checkpoint save attempt {attempt + 1} failed: {e}, retrying...")
                        time.sleep(0.5)  # Brief delay before retry
                    else:
                        # Clean up temp file if it exists
                        if Path(temp_path).exists():
                            try:
                                Path(temp_path).unlink()
                            except Exception:
                                pass
                        raise
            
            # Only log checkpoints every 10 epochs or at end (reduce noise)
            if epoch % 10 == 0 or epoch == save_state.get('n_epochs', 0):
                logger.info(f"💾 [{epoch}] Checkpoint saved")
                
        except RuntimeError as e:
            error_msg = str(e)
            if "disk" in error_msg.lower() or "space" in error_msg.lower() or "enforce fail" in error_msg.lower():
                logger.error(f"❌ Failed to save checkpoint at epoch {epoch}: {e}")
                logger.error(f"   This may indicate disk space issues or file system problems")
                logger.error(f"   Training will continue but checkpoint is lost")
                logger.error(f"   Checkpoint path: {checkpoint_path}")
                
                # Send Slack alert
                try:
                    from slack import send_slack_message
                    job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                    session_id = getattr(self, 'session_id', None) or self.training_info.get('session_id', None)
                    job_info = f"job {job_id}" if job_id else f"session {session_id}" if session_id else "training"
                    slack_msg = f"🚨 Checkpoint save FAILED at epoch {epoch} for {job_info}: {error_msg[:200]}"
                    send_slack_message(slack_msg, throttle=False, skip_hostname_prefix=True)
                except Exception as slack_err:
                    logger.warning(f"⚠️  Failed to send Slack alert: {slack_err}")
                
                # Don't raise - allow training to continue
            else:
                logger.error(f"❌ Failed to save checkpoint at epoch {epoch}: {e}")
                logger.error(f"   Checkpoint path: {checkpoint_path}")
                
                # Send Slack alert for non-disk errors too
                try:
                    from slack import send_slack_message
                    job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                    session_id = getattr(self, 'session_id', None) or self.training_info.get('session_id', None)
                    job_info = f"job {job_id}" if job_id else f"session {session_id}" if session_id else "training"
                    slack_msg = f"🚨 Checkpoint save FAILED at epoch {epoch} for {job_info}: {error_msg[:200]}"
                    send_slack_message(slack_msg, throttle=False, skip_hostname_prefix=True)
                except Exception as slack_err:
                    logger.warning(f"⚠️  Failed to send Slack alert: {slack_err}")
                
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error saving checkpoint at epoch {epoch}: {e}")
            logger.error(f"   Checkpoint path: {checkpoint_path}")
            
            # Send Slack alert
            try:
                from slack import send_slack_message
                job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                session_id = getattr(self, 'session_id', None) or self.training_info.get('session_id', None)
                job_info = f"job {job_id}" if job_id else f"session {session_id}" if session_id else "training"
                slack_msg = f"🚨 Checkpoint save ERROR at epoch {epoch} for {job_info}: {str(e)[:200]}"
                send_slack_message(slack_msg, throttle=False, skip_hostname_prefix=True)
            except Exception as slack_err:
                logger.warning(f"⚠️  Failed to send Slack alert: {slack_err}")
            
            raise

    # Backward compatibility aliases
    def save_state(self, epoch, batch, model, optimizer, scheduler, dropout_scheduler=None, is_best=False):
        """Deprecated: Use save_training_resume_point() instead."""
        return self.save_training_resume_point(epoch, batch, optimizer, scheduler, dropout_scheduler)
    
    def save_best_checkoint(self, epoch, model, val_loss):
        """Deprecated: Use save_best_for_inference() instead. (Note: typo 'checkoint' preserved for compatibility)"""
        return self.save_best_for_inference(epoch, val_loss)

    def load_best_checkpoint(self):
        # NOTE: loading the best model should be possible without having to first
        # instantiate the entire embedding space, including the input dataset.
        # This should be a class method.

        # PyTorch 2.6+ changed default to weights_only=True for security
        # Our checkpoints include custom classes (FeatrixTableEncoder), so we need weights_only=False
        checkpoint_state = torch.load(self.get_best_checkpoint_path(), weights_only=False)

        self.encoder = checkpoint_state["model"]
        epoch_idx = checkpoint_state["epoch_idx"]

        # We return the best epoch_idx so that we know which epoch the best model
        # came from.
        return epoch_idx

    def load_state(self, epoch, batch, is_best=False):
        self.training_state = torch.load(
            self.get_training_state_path(epoch, batch),
            weights_only=False
        )

    def preserve_progress(self, **kwargs):
        for k, v in kwargs.items():
            self.training_progress_data[k] = v
    
    def _create_model_package(self, best_epoch_idx):
        """
        Create a self-contained model package with everything needed to load and use the model.
        
        Package includes:
        - best_model.pickle - Pickled embedding space
        - best_model.pth - PyTorch checkpoint
        - metadata.json - Training metrics, config, column info
        - lib/featrix/neural/ - Code snapshot (for reproducibility if code changes)
        """
        try:
            import shutil
            
            output_dir = Path(self.output_dir) if isinstance(self.output_dir, str) else self.output_dir
            package_dir = output_dir / "best_model_package"
            package_dir.mkdir(exist_ok=True)
            
            logger.info(f"📦 Creating self-contained model package in {package_dir}")
            
            # 1. Save pickled embedding space
            pickle_path = package_dir / "best_model.pickle"
            with open(pickle_path, 'wb') as f:
                pickle.dump(self, f)
            logger.info(f"   ✅ Saved pickle: {pickle_path}")
            
            # 2. Save PyTorch checkpoint
            pth_path = package_dir / "best_model.pth"
            checkpoint_source = self.get_best_checkpoint_path()
            if Path(checkpoint_source).exists():
                shutil.copy(checkpoint_source, pth_path)
                logger.info(f"   ✅ Saved checkpoint: {pth_path}")
            
            # 3. Create metadata.json
            metadata = {
                "model_info": {
                    "name": getattr(self, 'name', None),
                    "session_id": getattr(self, 'session_id', None),
                    "job_id": getattr(self, 'job_id', None),
                    "d_model": self.d_model,
                    "best_epoch": best_epoch_idx,
                    "total_epochs": self.training_info.get('total_epochs', 0),
                    "created_at": datetime.now().isoformat(),
                },
                "data_info": {
                    "num_columns": len(self.col_order),
                    "column_names": self.col_order,
                    "column_types": {col: self.col_types.get(col) for col in self.col_order},
                    "train_rows": len(self.train_input_data.df) if self.train_input_data else 0,
                    "val_rows": len(self.val_input_data.df) if self.val_input_data else 0,
                },
                "training_metrics": {},
                "config": {},
                "version_info": self.version_info or {},
                "warnings": self._get_training_warnings(),
                "kl_divergences": getattr(self.train_input_data, 'kl_divergences_vs_val', {})
            }
            
            # Extract best epoch metrics from loss history
            loss_history = self.training_info.get('progress_info', {}).get('loss_history', [])
            if loss_history and best_epoch_idx < len(loss_history):
                best_entry = loss_history[best_epoch_idx]
                metadata["training_metrics"] = {
                    "epoch": best_epoch_idx,
                    "train_loss": best_entry.get('train_loss'),
                    "val_loss": best_entry.get('val_loss'),
                    "spread": best_entry.get('spread'),
                    "joint": best_entry.get('joint'),
                    "marginal": best_entry.get('marginal'),
                }
                logger.info(f"   ✅ Extracted metrics from epoch {best_epoch_idx}")
            
            metadata_path = package_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            logger.info(f"   ✅ Saved metadata: {metadata_path}")
            
            # 3b. Create comprehensive model_card.json
            model_card = self._create_model_card_json(best_epoch_idx, metadata)
            model_card_path = package_dir / "model_card.json"
            with open(model_card_path, 'w') as f:
                json.dump(model_card, f, indent=2, default=str)
            logger.info(f"   ✅ Saved model card: {model_card_path}")
            
            # 4. Copy lib/featrix/neural directory (code snapshot)
            src_neural_dir = Path(__file__).parent  # This file is in lib/featrix/neural
            dst_neural_dir = package_dir / "lib" / "featrix" / "neural"
            dst_neural_dir.parent.parent.mkdir(parents=True, exist_ok=True)
            
            if src_neural_dir.exists():
                shutil.copytree(src_neural_dir, dst_neural_dir, dirs_exist_ok=True)
                logger.info(f"   ✅ Copied code snapshot: {dst_neural_dir}")
            
            logger.info(f"📦 Model package complete! Location: {package_dir}")
            logger.info(f"   To load: pickle.load(open('best_model_package/best_model.pickle', 'rb'))")
            
        except Exception as e:
            logger.warning(f"Failed to create model package: {e}")
            traceback.print_exc()
    
    def _get_version_string(self):
        """Get version string from version_info, handling both dict and VersionInfo object."""
        if not self.version_info:
            return 'unknown'
        
        # Handle VersionInfo object
        if hasattr(self.version_info, 'semantic_version'):
            return self.version_info.semantic_version
        
        # Handle dict (backward compatibility)
        if isinstance(self.version_info, dict):
            return self.version_info.get('version', self.version_info.get('semantic_version', 'unknown'))
        
        return 'unknown'
    
    def _create_model_card_json(self, best_epoch_idx, metadata):
        """
        Create comprehensive model card JSON with all training info.
        
        Based on LoadSure HTML model card format.
        """
        import socket
        
        # Get loss history for best epoch
        loss_history = self.training_info.get('progress_info', {}).get('loss_history', [])
        best_entry = loss_history[best_epoch_idx] if loss_history and best_epoch_idx < len(loss_history) else {}
        
        model_card = {
            "model_identification": {
                "session_id": getattr(self, 'session_id', None),
                "job_id": getattr(self, 'job_id', None),
                "name": getattr(self, 'name', None),
                "compute_cluster": socket.gethostname().split('.')[0].upper(),
                "training_date": datetime.now().strftime('%Y-%m-%d'),
                "status": "DONE",
                "model_type": "Embedding Space",
                "framework": f"FeatrixSphere {self._get_version_string()}"
            },
            
            "training_dataset": {
                "total_rows": len(self.train_input_data.df) + len(self.val_input_data.df) if self.train_input_data and self.val_input_data else 0,
                "train_rows": len(self.train_input_data.df) if self.train_input_data else 0,
                "val_rows": len(self.val_input_data.df) if self.val_input_data else 0,
                "total_features": len(self.col_order),
                "feature_names": self.col_order,
            },
            
            "feature_inventory": self._get_feature_inventory(),
            
            "training_configuration": {
                "epochs_total": self.training_info.get('total_epochs', 0),
                "best_epoch": best_epoch_idx,
                "d_model": self.d_model,
                "batch_size": self.training_info.get('batch_size', None),
                "learning_rate": self.training_info.get('learning_rate', None),
                "optimizer": self.training_info.get('optimizer', 'Adam'),
                "dropout_schedule": {
                    "enabled": True,
                    "initial": 0.5,
                    "final": 0.25
                }
            },
            
            "training_metrics": {
                "best_epoch": {
                    "epoch": best_epoch_idx,
                    "train_loss": best_entry.get('train_loss'),
                    "val_loss": best_entry.get('val_loss'),
                    "spread_loss": best_entry.get('spread'),
                    "joint_loss": best_entry.get('joint'),
                    "marginal_loss": best_entry.get('marginal'),
                },
                "final_epoch": {
                    "epoch": len(loss_history) - 1 if loss_history else 0,
                    "train_loss": loss_history[-1].get('train_loss') if loss_history else None,
                    "val_loss": loss_history[-1].get('val_loss') if loss_history else None,
                },
                "loss_progression": {
                    "initial_train": loss_history[0].get('train_loss') if loss_history else None,
                    "initial_val": loss_history[0].get('val_loss') if loss_history else None,
                    "improvement_pct": self._calculate_improvement(loss_history) if loss_history else None
                }
            },
            
            "column_statistics": self._get_column_statistics(),
            
            "model_architecture": {
                "attention_heads": self.encoder_config.joint_encoder_config.n_heads if hasattr(self, 'encoder_config') and hasattr(self.encoder_config, 'joint_encoder_config') else None,
                "transformer_layers": self.encoder_config.joint_encoder_config.n_layers if hasattr(self, 'encoder_config') and hasattr(self.encoder_config, 'joint_encoder_config') else None,
                "d_model": self.d_model,
                "dim_feedforward_factor": self.encoder_config.joint_encoder_config.dim_feedforward_factor if hasattr(self, 'encoder_config') and hasattr(self.encoder_config, 'joint_encoder_config') else None,
                "loss_function": "Composite: Marginal (per-column) + Joint (transformer) + Spread (distance)",
                "loss_weights": {
                    "marginal": self.encoder.config.loss_config.marginal_loss_weight if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config') else None,
                    "joint": self.encoder.config.loss_config.joint_loss_weight if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config') else None,
                    "spread": self.encoder.config.loss_config.spread_loss_weight if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config') else None,
                },
                "curriculum_learning": self.encoder.config.loss_config.curriculum_learning.enabled if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config') and hasattr(self.encoder.config.loss_config, 'curriculum_learning') and self.encoder.config.loss_config.curriculum_learning else False,
            },
            
            "model_quality": {
                "assessment": self._assess_model_quality(loss_history),
                "recommendations": self._get_recommendations(loss_history),
                "warnings": self._get_training_warnings(),
                "quality_checks": self._get_quality_checks_for_model_card(best_epoch_idx)
            },
            
            "technical_details": {
                "pytorch_version": torch.__version__ if torch else "unknown",
                "device": "GPU" if is_gpu_available() else "CPU",
                "precision": "float32",
                "normalization": "unit_sphere",
                "loss_function": "InfoNCE (contrastive)",
            },
            
            "provenance": {
                "created_at": datetime.now().isoformat(),
                "training_duration_minutes": self.training_info.get('duration_minutes', 0),
                "version_info": self.version_info or {},
            }
        }
        
        return model_card
    
    def _get_feature_inventory(self):
        """Extract feature inventory for model card."""
        features = []
        
        for col_name in self.col_order:
            codec = self.col_codecs.get(col_name)
            col_type = self.col_types.get(col_name, "unknown")
            
            feature_info = {
                "name": col_name,
                "type": str(col_type),
                "encoder_type": type(codec).__name__ if codec else "unknown"
            }
            
            # Add column importance information
            # Check if this is a random/zero-contribution column
            is_random = False
            is_pruned = False
            importance_reason = None
            pruning_info = {}
            
            # Check if column was pruned during training (AdaptiveScalarEncoder only)
            if hasattr(self, 'encoder') and hasattr(self.encoder, 'column_encoder'):
                encoder = self.encoder.column_encoder.encoders.get(col_name)
                if encoder and hasattr(encoder, '_disabled') and encoder._disabled:
                    is_pruned = True
                    importance_reason = "pruned_during_training"
                    # Get pruning statistics if available
                    if hasattr(self, '_column_loss_tracker') and col_name in self._column_loss_tracker:
                        pruning_info = {
                            "average_loss": float(self._column_loss_tracker[col_name]),
                            "pruning_method": "progressive_worst_performers"
                        }
            
            # Check if this is a random/zero-contribution column (detected at initialization)
            if hasattr(codec, 'is_random_column'):
                is_random = getattr(codec, 'is_random_column', False)
                if is_random:
                    importance_reason = "random_strings_detected"
            
            # Build column_importance based on status
            if is_pruned:
                feature_info["column_importance"] = {
                    "weight": 0.0,
                    "reason": importance_reason,
                    "description": f"Column was dynamically pruned during training due to poor performance (high reconstruction loss)",
                    **pruning_info
                }
            elif is_random:
                feature_info["column_importance"] = {
                    "weight": 0.0,
                    "reason": importance_reason,
                    "description": "Column contains random/meaningless strings (UUIDs, hashes, transaction IDs) and contributes zero information to the model"
                }
                
                # Extract additional importance metadata from adaptive analysis if available
                if hasattr(codec, '_adaptive_analysis'):
                    analysis = codec._adaptive_analysis
                    if 'is_random' in analysis and analysis['is_random']:
                        # Get randomness confidence from precomputed analysis
                        precomputed = analysis.get('precomputed', {})
                        column_stats = precomputed.get('column_stats', {})
                        if 'column_stats' in precomputed:
                            # Store detailed signals for transparency
                            feature_info["column_importance"]["confidence"] = column_stats.get('unique_ratio', 0.0)
                            feature_info["column_importance"]["unique_ratio"] = column_stats.get('unique_ratio', 0.0)
                            feature_info["column_importance"]["semantic_similarity"] = column_stats.get('avg_semantic_similarity')
            else:
                # Normal column included in training
                feature_info["column_importance"] = {
                    "weight": 1.0,
                    "reason": "included_in_training",
                    "description": "Column is included in model training with normal importance weighting"
                }
            
            # Add type-specific info
            if hasattr(codec, 'members'):
                feature_info["unique_values"] = len(codec.members)
                feature_info["sample_values"] = list(codec.members)[:5] if hasattr(codec.members, '__iter__') else []
            elif hasattr(codec, 'stats'):
                feature_info["statistics"] = codec.stats
            
            features.append(feature_info)
        
        return features
    
    def _get_column_statistics(self):
        """Get per-column loss and predictability statistics."""
        col_stats = {}
        
        # Get predictability estimates (now 0-100% scale, was "MI in bits" but that was broken)
        col_pred = getattr(self.encoder, 'col_mi_estimates', {})
        
        # Get latest marginal losses
        latest_marginal = self.training_info.get('progress_info', {}).get('latest_marginal_losses', {})
        
        for col_name in self.col_order:
            pred_pct = col_pred.get(col_name)
            col_stats[col_name] = {
                # New field: 0-100% scale, higher = more predictable from context
                "predictability_pct": pred_pct,
                # Deprecated: kept for backwards compat, now contains same value as predictability_pct
                "mutual_information_bits": pred_pct,
                "marginal_loss": latest_marginal.get(col_name),
            }
        
        return col_stats
    
    def _calculate_improvement(self, loss_history):
        """Calculate overall training improvement."""
        if not loss_history or len(loss_history) < 2:
            return None
        
        initial = loss_history[0].get('val_loss')
        final = loss_history[-1].get('val_loss')
        
        if initial and final and initial > 0:
            return ((initial - final) / initial) * 100
        return None
    
    def _assess_model_quality(self, loss_history):
        """Assess overall model quality."""
        if not loss_history:
            return "UNKNOWN"
        
        improvement = self._calculate_improvement(loss_history)
        
        if improvement is None:
            return "UNKNOWN"
        elif improvement > 80:
            return "EXCELLENT"
        elif improvement > 50:
            return "GOOD"
        elif improvement > 20:
            return "FAIR"
        else:
            return "POOR"
    
    def _get_recommendations(self, loss_history):
        """Generate training recommendations."""
        recommendations = []
        
        if not loss_history:
            return recommendations
        
        # Check for overfitting
        final_entry = loss_history[-1]
        train_loss = final_entry.get('train_loss', 0)
        val_loss = final_entry.get('val_loss', 0)
        
        if val_loss > 0 and train_loss > 0:
            gap = val_loss - train_loss
            gap_pct = (gap / train_loss) * 100
            
            if gap_pct > 30:
                recommendations.append({
                    "issue": "Large train/val gap indicates overfitting",
                    "suggestion": "Consider higher dropout or more regularization"
                })
        
        # Check for poor improvement
        improvement = self._calculate_improvement(loss_history)
        if improvement is not None and improvement < 20:
            recommendations.append({
                "issue": "Training did not improve sufficiently",
                "suggestion": "Review data quality or try longer training"
            })
        
        # Check for distribution shift (KL divergence)
        kl_divergences = getattr(self.train_input_data, 'kl_divergences_vs_val', {})
        if kl_divergences:
            high_kl_count = sum(1 for kl_div in kl_divergences.values() if kl_div > 1.0)
            if high_kl_count > 0:
                recommendations.append({
                    "issue": f"Distribution shift detected: {high_kl_count} column(s) have high KL divergence (>1.0) between train and validation sets",
                    "suggestion": "Review data splitting strategy - train/val distributions should be similar. Check for temporal drift or data leakage."
                })
        
        return recommendations
    
    def _get_quality_checks_for_model_card(self, epoch_idx=None):
        """
        Extract quality checks for model card display.
        
        Args:
            epoch_idx: Optional epoch to get checks for. If None, gets latest checks.
        
        Returns:
            Dict with quality checks organized by check name
        """
        if not hasattr(self, 'customer_quality_trackers') or not self.customer_quality_trackers:
            return {}
        
        quality_checks = {}
        
        # If epoch specified, get checks for that epoch
        if epoch_idx is not None and epoch_idx in self.customer_quality_trackers:
            tracker = self.customer_quality_trackers[epoch_idx]
            checks = tracker.get_all_checks()
            for check in checks:
                check_name = check['name']
                if check_name not in quality_checks:
                    quality_checks[check_name] = []
                quality_checks[check_name].append({
                    "epoch": check['epoch'],
                    "grade": check['graded_score'],
                    "timestamp": check['timestamp'],
                    "metadata": check['metadata']
                })
        else:
            # Get latest check for each type across all epochs
            from featrix.neural.customer_quality_tracker import QualityCheckName
            for check_type in QualityCheckName:
                latest_check = None
                latest_epoch = -1
                for epoch, tracker in self.customer_quality_trackers.items():
                    check = tracker.get_latest_check(check_type)
                    if check and check['epoch'] > latest_epoch:
                        latest_check = check
                        latest_epoch = check['epoch']
                
                if latest_check:
                    quality_checks[check_type.value] = {
                        "epoch": latest_check['epoch'],
                        "grade": latest_check['graded_score'],
                        "timestamp": latest_check['timestamp'],
                        "metadata": latest_check['metadata']
                    }
        
        return quality_checks
    
    def _get_training_warnings(self):
        """Get training warnings including KL divergence issues."""
        warnings = []
        
        # Check KL divergence between train and val distributions
        kl_divergences = getattr(self.train_input_data, 'kl_divergences_vs_val', {})
        if kl_divergences:
            high_kl_columns = []
            for col_name, kl_div in kl_divergences.items():
                if kl_div > 1.0:  # High distribution shift
                    high_kl_columns.append((col_name, kl_div))
            
            if high_kl_columns:
                # Sort by KL divergence (highest first)
                high_kl_columns.sort(key=lambda x: x[1], reverse=True)
                warnings.append({
                    "type": "DISTRIBUTION_SHIFT",
                    "severity": "HIGH",
                    "message": f"High KL divergence between train and validation distributions detected for {len(high_kl_columns)} column(s)",
                    "details": {
                        "threshold": 1.0,
                        "affected_columns": [
                            {
                                "column": col_name,
                                "kl_divergence": round(kl_div, 3),
                                "interpretation": "HIGH" if kl_div > 2.0 else "MODERATE"
                            }
                            for col_name, kl_div in high_kl_columns
                        ]
                    },
                    "recommendation": "Train and validation sets have different distributions. This may indicate data leakage, temporal drift, or sampling issues. Review data splitting strategy."
                })
        
        return warnings
    
    def _save_movie_data_snapshot(self, movie_frame_interval):
        """
        Save a one-time data snapshot for async movie frame generation.
        Uses same sampling logic as EpochProjectionCallback.
        """
        try:
            # Get combined train+val data (same as movie frames use)
            combined_df = pd.concat([self.train_input_data.df, self.val_input_data.df], ignore_index=True)
            
            # Sample consistently (max 500 points)
            max_samples = 500
            if len(combined_df) > max_samples:
                # Use same sampling as EpochProjectionCallback
                # TODO: Handle important_columns if needed
                sample_df = combined_df.sample(max_samples, random_state=42)
                sample_indices = sample_df.index.tolist()
            else:
                sample_df = combined_df
                sample_indices = None
            
            # Save as JSON (ensure output_dir is Path object)
            output_dir = Path(self.output_dir) if isinstance(self.output_dir, str) else self.output_dir
            self.movie_data_snapshot_path = output_dir / "movie_data_snapshot.json"
            snapshot_data = {
                'records': json.loads(sample_df.to_json(orient='records')),
                'sample_indices': sample_indices,
                'total_records': len(combined_df),
                'sampled_records': len(sample_df),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.movie_data_snapshot_path, 'w') as f:
                json.dump(snapshot_data, f)
            
            logger.info(f"🎬 Saved movie data snapshot: {len(sample_df)} records to {self.movie_data_snapshot_path}")
            logger.info(f"   Movie frames will be generated EVERY epoch (interval={movie_frame_interval} ignored for async)")
            
        except Exception as e:
            logger.warning(f"Failed to save movie data snapshot: {e}")
            self.movie_data_snapshot_path = None
    
    def _queue_project_training_movie_frame(self, epoch_idx):
        """
        Queue async training movie frame generation task immediately after checkpoint save.
        Uses the epoch-specific checkpoint that was just saved.
        Returns immediately - doesn't block training!
        
        This is the unified movie frame function (replaces both _queue_project_training_movie_frame
        and _queue_movie_frame which were duplicates).
        """
        # DISABLED: Movie generation disabled to prevent CPU overload
        return
        
        # Skip if no data snapshot
        if not hasattr(self, 'movie_data_snapshot_path') or not self.movie_data_snapshot_path:
            return
        
        try:
            output_dir = Path(self.output_dir) if isinstance(self.output_dir, str) else self.output_dir
            
            # Ensure movie_data_snapshot_path is a Path object for exists() check
            movie_snapshot_path = Path(self.movie_data_snapshot_path) if isinstance(self.movie_data_snapshot_path, str) else self.movie_data_snapshot_path
            if not movie_snapshot_path.exists():
                logger.warning(f"Movie data snapshot not found: {movie_snapshot_path}, skipping projection build")
                return
            
            # Use the epoch-specific checkpoint that was just saved by save_state()
            # This checkpoint contains encoder + codecs (no huge dataframes)
            training_state_path = self.get_training_state_path(epoch_idx, 0)
            checkpoint_path = Path(self.get_inference_checkpoint_path(epoch_idx, 0))
            
            # Check if checkpoint was saved successfully (from save_state flag)
            if not getattr(self, '_last_embedding_space_checkpoint_saved', False):
                logger.warning(f"⚠️  Embedding space checkpoint was not saved for epoch {epoch_idx}, skipping projection build")
                return
            
            # Verify checkpoint file exists (retry with longer wait for large checkpoints)
            # The checkpoint save uses atomic write (temp file + rename), so we need
            # to wait for the file system to sync, especially for large files (60MB+)
            max_retries = 10  # Increased from 3
            checkpoint_exists = False
            for attempt in range(max_retries):
                if checkpoint_path.exists():
                    checkpoint_exists = True
                    break
                if attempt < max_retries - 1:
                    time.sleep(0.2)  # Wait 200ms between retries (was 100ms)
            
            if not checkpoint_exists:
                # Use DEBUG instead of WARNING - this function is only called after checkpoint save succeeds
                # Any missing checkpoint after 2 seconds (10 × 200ms) is a real filesystem issue, not a race
                logger.debug(f"Checkpoint not found for epoch {epoch_idx} after {max_retries} retries: {checkpoint_path}")
                logger.debug(f"   Movie frame generation will be skipped for this epoch")
                logger.debug(f"   This is normal if checkpoint save is slow or filesystem is busy")
                return
            
            logger.debug(f"   Using epoch checkpoint: {checkpoint_path}")
            
            # Skip async processing on development machines (Mac, or non-production Linux)
            from featrix.neural.platform_utils import os_is_featrix_firmware
            if not os_is_featrix_firmware():
                logger.info(f"💻 Running on development machine - skipping movie frame generation (async processing not needed)")
                return
            
            # Check if Redis/Celery is available before trying to use it
            # On production servers, Redis MUST be available - crash if it's not
            redis_available = False
            redis_error = None
            try:
                import redis
                redis_client = redis.Redis(host='localhost', port=6379, db=1, socket_timeout=1, socket_connect_timeout=1)
                redis_client.ping()
                redis_available = True
            except Exception as e:
                redis_available = False
                redis_error = e
            
            if not redis_available:
                # On production servers (taco/churro), Redis is REQUIRED
                # Crash immediately - this is a critical system failure
                error_msg = f"❌ CRITICAL: Redis is not available on production server\n"
                error_msg += f"   Redis is REQUIRED for movie frame generation, progress tracking, and job coordination\n"
                error_msg += f"   Error: {redis_error}\n"
                error_msg += f"   Fix: systemctl start redis-server (or check Redis status)\n"
                error_msg += f"   This is a deployment/infrastructure problem that must be fixed immediately"
                logger.error(error_msg)
                raise RuntimeError(f"Redis not available on production server: {redis_error}")
            
            # Create job spec for Celery task
            job_spec = {
                'type': 'project_training_movie_frame',
                'session_id': getattr(self, 'session_id', 'unknown'),
                'epoch': epoch_idx,
                'checkpoint_path': str(checkpoint_path),
                'data_snapshot_path': str(self.movie_data_snapshot_path),
                'output_dir': str(output_dir),
            }
            
            # Queue via Celery (cpu_worker queue) - only if Redis is available
            try:
                # Import celery_app - this may try to connect to Redis
                # Wrap in try/except to handle connection failures gracefully
                try:
                    from celery_app import app
                except Exception as celery_import_err:
                    logger.error(f"❌ Failed to import celery_app: {celery_import_err}")
                    logger.error(f"   This usually means Redis is not running")
                    logger.error(f"   Start Redis with: redis-server (or systemctl start redis-server)")
                    return
                
                task = app.send_task(
                    'celery_app.project_training_movie_frame',
                    args=[job_spec],
                    queue='movie_generation'  # Dedicated movie generation queue (concurrency=1)
                )
                
                # Save job to Redis for tracking (consistent with other jobs)
                try:
                    from lib.job_manager import save_job, JobStatus
                    session_id_for_job = job_spec.get('session_id', getattr(self, 'session_id', 'unknown'))
                    save_job(
                        job_id=task.id,
                        job_data={
                            'status': JobStatus.READY,
                            'created_at': datetime.now(tz=ZoneInfo("America/New_York")),
                            'job_spec': job_spec,
                        },
                        session_id=session_id_for_job,
                        job_type='project_training_movie_frame'
                    )
                    logger.debug(f"✅ Saved project_training_movie_frame job {task.id} to Redis")
                except Exception as redis_err:
                    logger.warning(f"⚠️  Could not save job to Redis: {redis_err}")
                    # Continue anyway - job tracking is non-critical
                
                logger.info(f"🎬 Queued training movie frame for epoch {epoch_idx} → movie_generation queue (task_id: {task.id}, non-blocking)")
            except Exception as celery_err:
                logger.error(f"❌ Failed to queue movie frame via Celery: {celery_err}")
                logger.error(f"   Check that Redis is running: redis-server")
                logger.error(f"   Check that Celery workers are running")
                # Don't crash training - movie frames are optional
            
        except Exception as e:
            logger.warning(f"Failed to queue projection build for epoch {epoch_idx}: {e}")
    
    def _queue_movie_frame(self, epoch_idx):
        """
        DEPRECATED: Use _queue_project_training_movie_frame instead.
        This function is kept for backward compatibility but just calls the unified function.
        """
        return self._queue_project_training_movie_frame(epoch_idx)

    def restore_progress(self, *args):
        ret = []
        for key in args:
            ret.append(self.training_progress_data.get(key))
        return ret

    def __getstate__(self):
        """
        Custom pickle state - exclude sqlite connections, DataLoaders, and thread locks that can't be pickled.
        
        NOTE: train_input_data, val_input_data, train_data, and val_data are INTENTIONALLY excluded.
        These contain large pandas DataFrames that would make pickle files huge (100GB+). The data can be
        reloaded from SQLite database or original files when needed. This is EXPECTED behavior, not an error.
        """
        import copy
        import threading
        import sqlite3
        from torch.utils.data import DataLoader
        
        logger.debug("💾 Preparing pickle state - intentionally excluding large DataFrames (train_input_data, val_input_data, train_data, val_data)")
        logger.debug("   ✅ This is EXPECTED - data can be reloaded from SQLite/original files. Pickle file will be small and fast.")
        
        # Start with a shallow copy, then selectively deep copy safe objects
        state = {}
        
        # List of attributes to exclude (unpicklable objects)
        exclude_attrs = {
            'data_loader', 'val_dataloader',  # DataLoaders can't be pickled
            'timed_data_loader',  # Custom data loaders
            'train_input_data', 'val_input_data',  # FeatrixInputDataSet objects contain large pandas DataFrames (100GB+)
            # These are explicitly excluded to keep pickle files small - data can be reloaded from SQLite
            'train_data', 'val_data',  # Also exclude these if they exist (backup check)
        }
        
        # List of attributes that might contain thread locks or other unpicklable objects
        # These will be set to None
        exclude_if_has_lock = set()
        
        # First pass: identify problematic objects
        for key, value in self.__dict__.items():
            # CRITICAL: train_input_data and val_input_data contain 100GB+ DataFrames - NEVER pickle them
            # This is INTENTIONAL - we exclude them to keep pickle files small and fast
            if key in exclude_attrs:
                if key in ('train_input_data', 'val_input_data', 'train_data', 'val_data'):
                    logger.debug(f"✅ INTENTIONAL EXCLUSION: Skipping {key} in pickle (contains large DataFrames - data can be reloaded from SQLite/original files)")
                continue  # Skip excluded attributes entirely
            
            # Check if this is a DataLoader
            if isinstance(value, DataLoader):
                continue  # Skip DataLoaders
            
            # Check for DataLoader iterators explicitly (they can't be pickled)
            if hasattr(value, '__class__'):
                class_name = value.__class__.__name__
                if 'DataLoaderIter' in class_name or '_MultiProcessingDataLoaderIter' == class_name:
                    logger.debug(f"Skipping {key} in pickle state (DataLoader iterator: {class_name})")
                    continue
            
            # Check if this is a FeatrixInputDataSet - EXCLUDE IT ENTIRELY (backup check)
            # FeatrixInputDataSet contains large pandas DataFrames (self.df) that can be 100GB+
            # These should NOT be pickled - data can be reloaded from SQLite database or original files
            # This is INTENTIONAL to keep pickle files small and fast
            if hasattr(value, '__class__') and value.__class__.__name__ == 'FeatrixInputDataSet':
                logger.debug(f"✅ INTENTIONAL EXCLUSION: Skipping {key} in pickle (FeatrixInputDataSet contains large DataFrames - data can be reloaded from SQLite/original files)")
                continue
            
            # Check for thread locks
            try:
                if hasattr(value, '__dict__'):
                    # Check if object or any nested object has a lock
                    has_lock = False
                    try:
                        for attr_name, attr_value in value.__dict__.items():
                            if isinstance(attr_value, (threading.Lock, threading.RLock, threading.Condition, threading.Semaphore)):
                                has_lock = True
                                break
                            # Check nested objects
                            if hasattr(attr_value, '__dict__'):
                                for nested_attr in attr_value.__dict__.values():
                                    if isinstance(nested_attr, (threading.Lock, threading.RLock, threading.Condition, threading.Semaphore)):
                                        has_lock = True
                                        break
                                if has_lock:
                                    break
                    except (AttributeError, TypeError):
                        pass
                    
                    if has_lock:
                        exclude_if_has_lock.add(key)
                        continue
            except (AttributeError, TypeError):
                pass
            
            # Check for sqlite3.Connection objects directly
            if isinstance(value, sqlite3.Connection):
                logger.debug(f"Skipping {key} in pickle state (sqlite3.Connection)")
                continue
            
            # Check for TrainingHistoryDB objects (they contain sqlite connections)
            if hasattr(value, '__class__') and value.__class__.__name__ == 'TrainingHistoryDB':
                # Exclude history_db entirely - it's not needed for model package
                logger.debug(f"Skipping {key} in pickle state (TrainingHistoryDB with sqlite connection)")
                continue
            
            # Check for DataLoader iterators explicitly (they can't be pickled)
            if hasattr(value, '__class__'):
                class_name = value.__class__.__name__
                if 'DataLoader' in class_name or 'dataloader' in class_name.lower():
                    logger.debug(f"Skipping {key} in pickle state (DataLoader or iterator: {class_name})")
                    continue
                # Check for DataLoader iterator classes
                if class_name == '_MultiProcessingDataLoaderIter' or 'DataLoaderIter' in class_name:
                    logger.debug(f"Skipping {key} in pickle state (DataLoader iterator: {class_name})")
                    continue
            
            # PyTorch-approved way: Save encoder as state_dict instead of whole object
            # This avoids persistent_load errors and is the recommended approach
            if key == 'encoder' and hasattr(value, 'state_dict') and hasattr(value, 'load_state_dict'):
                # It's a PyTorch nn.Module - save state_dict instead
                try:
                    state['encoder_state_dict'] = value.state_dict()
                    logger.debug(f"Saved encoder as state_dict (PyTorch-approved method)")
                    continue  # Skip the deepcopy for encoder
                except Exception as e:
                    logger.warning(f"Failed to get encoder state_dict, falling back to deepcopy: {e}")
                    # Fall through to try deepcopy
            
            # Try to deep copy, but catch errors for unpicklable objects
            try:
                state[key] = copy.deepcopy(value)
            except (TypeError, AttributeError, NotImplementedError, RuntimeError) as e:
                # If deepcopy fails, try to identify why
                error_msg = str(e).lower()
                error_type = type(e).__name__
                error_str = str(e)
                
                # Check for tensor-related errors (PyTorch tensors that aren't graph leaves can't be deepcopied)
                is_tensor_error = False
                if 'tensor' in error_msg or 'graph leaves' in error_msg or 'deepcopy protocol' in error_msg:
                    is_tensor_error = True
                    logger.debug(f"Skipping {key} in pickle state (tensor deepcopy error: {error_type} - {error_str})")
                    continue
                
                # Check for DataLoader-related errors
                # The error message might be a tuple like ('{} cannot be pickled', '_MultiProcessingDataLoaderIter')
                # Check both the string representation and the exception args
                is_dataloader_error = False
                if hasattr(e, 'args') and e.args:
                    # Check if any arg contains DataLoader-related strings
                    for arg in e.args:
                        arg_str = str(arg)
                        if 'DataLoader' in arg_str or 'DataLoaderIter' in arg_str or '_MultiProcessingDataLoaderIter' in arg_str:
                            is_dataloader_error = True
                            break
                
                if is_dataloader_error or 'dataloader' in error_msg or 'DataLoader' in error_str or 'DataLoaderIter' in error_str or '_MultiProcessingDataLoaderIter' in error_str:
                    logger.debug(f"Skipping {key} in pickle state (DataLoader error: {error_type} - {error_str})")
                    continue
                elif 'lock' in error_msg or 'thread' in error_msg:
                    # Skip objects with locks
                    logger.debug(f"Skipping {key} in pickle state (contains thread lock)")
                    continue
                elif 'sqlite' in error_msg or 'connection' in error_msg:
                    # Skip sqlite connections
                    logger.debug(f"Skipping {key} in pickle state (sqlite connection)")
                    continue
                elif 'cannot be pickled' in error_msg:
                    # Generic unpicklable object
                    logger.debug(f"Skipping {key} in pickle state (cannot be pickled: {error_type})")
                    continue
                else:
                    # For other errors, try shallow copy as fallback
                    try:
                        state[key] = copy.copy(value)
                    except (TypeError, AttributeError, NotImplementedError, RuntimeError):
                        logger.warning(f"Could not pickle {key}, excluding from state")
                        continue
        
        # Remove sqlite connections from string_cache objects
        def remove_conn(obj):
            """Recursively remove conn and cursor from objects."""
            if hasattr(obj, '__dict__'):
                if hasattr(obj, 'conn'):
                    obj.conn = None
                if hasattr(obj, 'cursor'):
                    obj.cursor = None
                # Recursively process nested objects
                for attr_name, attr_value in obj.__dict__.items():
                    if attr_name not in ('conn', 'cursor'):
                        try:
                            remove_conn(attr_value)
                        except (AttributeError, TypeError, RecursionError):
                            pass
        
        # Remove connections from input data objects
        if 'train_input_data' in state and state['train_input_data']:
            try:
                remove_conn(state['train_input_data'])
            except (AttributeError, TypeError, RecursionError):
                pass
        
        if 'val_input_data' in state and state['val_input_data']:
            try:
                remove_conn(state['val_input_data'])
            except (AttributeError, TypeError, RecursionError):
                pass
        
        # Final pass: check for any remaining sqlite3.Connection objects in state
        keys_to_remove = []
        for key, value in state.items():
            if isinstance(value, sqlite3.Connection):
                keys_to_remove.append(key)
            elif hasattr(value, '__dict__'):
                # Check nested objects
                try:
                    for attr_name, attr_value in value.__dict__.items():
                        if isinstance(attr_value, sqlite3.Connection):
                            keys_to_remove.append(key)
                            break
                except (AttributeError, TypeError):
                    pass
        
        for key in keys_to_remove:
            logger.debug(f"Removing {key} from pickle state (contains sqlite3.Connection)")
            del state[key]
        
        return state
    
    def __setstate__(self, state):
        """Restore state after unpickling - connections will be None and need to be recreated when used."""
        # Get logger first before using it
        import logging
        logger = logging.getLogger(__name__)
        
        # WHO THE FUCK IS CALLING US? Log the call stack!
        logger.info(f"🔍 EmbeddingSpace.__setstate__: CALL STACK (who called us):")
        for line in traceback.format_stack()[:-1]:  # Skip the last frame (this line)
            for subline in line.strip().split('\n'):
                logger.info(f"   {subline}")
        
        # Log GPU memory before unpickling to see if __setstate__ triggers allocation
        allocated_before = 0.0
        reserved_before = 0.0
        try:
            if is_gpu_available():
                allocated_before = get_gpu_memory_allocated()
                reserved_before = get_gpu_memory_reserved()
                logger.info(f"📊 EmbeddingSpace.__setstate__: GPU memory BEFORE: Allocated={allocated_before:.3f} GB, Reserved={reserved_before:.3f} GB")
        except Exception as e:
            logger.info(f"📊 EmbeddingSpace.__setstate__: Could not check GPU memory before: {e}")
        
        # Check what's in the state dict before unpickling
        state_keys = list(state.keys())
        logger.info(f"📊 EmbeddingSpace.__setstate__: State dict has {len(state_keys)} keys")
        if 'col_codecs' in state:
            col_codec_count = len(state['col_codecs']) if state['col_codecs'] else 0
            logger.info(f"📊 EmbeddingSpace.__setstate__: About to unpickle {col_codec_count} col_codecs")
            # Log codec types
            if state['col_codecs']:
                codec_types = {}
                for col_name, codec in state['col_codecs'].items():
                    codec_type = type(codec).__name__
                    codec_types[codec_type] = codec_types.get(codec_type, 0) + 1
                logger.info(f"📊 EmbeddingSpace.__setstate__: Codec types: {codec_types}")
        if 'encoder' in state:
            logger.info(f"📊 EmbeddingSpace.__setstate__: State dict contains 'encoder' key (old format)")
        if 'encoder_state_dict' in state:
            logger.info(f"📊 EmbeddingSpace.__setstate__: State dict contains 'encoder_state_dict' key (new PyTorch-approved format)")
        if 'string_cache' in state:
            logger.info(f"📊 EmbeddingSpace.__setstate__: State dict contains 'string_cache' key")
        
        logger.info(f"📊 EmbeddingSpace.__setstate__: About to call self.__dict__.update(state) - this will unpickle col_codecs")
        logger.info(f"📊 EmbeddingSpace.__setstate__: State has {len(state.get('col_codecs', {}))} col_codecs to unpickle")
        
        # PyTorch-approved way: Recreate encoder from state_dict if present
        # Check if we have the new format (encoder_state_dict) or old format (encoder already pickled)
        encoder_state_dict = state.pop('encoder_state_dict', None)
        encoder_in_state = 'encoder' in state
        
        logger.info(f"📊 EmbeddingSpace.__setstate__: Starting self.__dict__.update(state)...")
        import time as time_module
        update_start = time_module.time()
        
        self.__dict__.update(state)
        
        update_time = time_module.time() - update_start
        logger.info(f"📊 EmbeddingSpace.__setstate__: Finished self.__dict__.update(state) in {update_time:.1f}s")
        logger.info(f"   This unpickled: {len(self.col_codecs)} col_codecs")
        
        # Recreate encoder from state_dict if we have it (new PyTorch-approved format)
        if encoder_state_dict is not None:
            try:
                logger.info(f"")
                logger.info(f"📊 EmbeddingSpace.__setstate__: Recreating encoder from state_dict...")
                logger.info(f"   ⏳ This creates FeatrixTableEncoder from {len(self.col_codecs)} codecs")
                # We need col_codecs and encoder_config to recreate the encoder
                if not hasattr(self, 'col_codecs') or not self.col_codecs:
                    raise ValueError("Cannot recreate encoder: col_codecs missing from state")
                if not hasattr(self, 'encoder_config') or not self.encoder_config:
                    raise ValueError("Cannot recreate encoder: encoder_config missing from state")
                
                # CRITICAL FIX: Check if encoder_config.cols_in_order is empty but we have codecs
                # This happens when the model was saved with a corrupted col_order
                # We need to rebuild the ENTIRE encoder_config from col_codecs
                config_cols = getattr(self.encoder_config, 'cols_in_order', [])
                if not config_cols or len(config_cols) == 0:
                    logger.warning(f"   ⚠️  encoder_config.cols_in_order is EMPTY - rebuilding entire config from col_codecs")
                    
                    # Use col_codecs keys directly - they are the source of truth
                    # The state_dict may have 'featrix_' prefixed names that don't match col_codecs
                    if self.col_codecs:
                        recovered_cols = sorted(list(self.col_codecs.keys()))
                        logger.warning(f"   ✅ Using {len(recovered_cols)} column names from col_codecs")
                        logger.warning(f"   Columns: {recovered_cols[:10]}{'...' if len(recovered_cols) > 10 else ''}")
                        
                        # Infer col_types from col_codecs using codec.get_codec_name()
                        # This MUST match what get_default_column_encoder_configs() uses
                        col_types = {}
                        for col_name in recovered_cols:
                            codec = self.col_codecs[col_name]
                            # Use the same method as get_default_column_encoder_configs
                            col_types[col_name] = codec.get_codec_name()
                        
                        # Get d_model from the original config or infer from state_dict
                        d_model = getattr(self.encoder_config, 'd_model', 128)
                        
                        # Rebuild the ENTIRE encoder_config using the same method as __init__
                        logger.warning(f"   🔧 Rebuilding encoder_config with {len(recovered_cols)} columns, d_model={d_model}")
                        self.encoder_config = self.get_default_table_encoder_config(
                            d_model=d_model,
                            col_codecs=self.col_codecs,
                            col_order=recovered_cols,
                            col_types=col_types,
                            relationship_features=None,
                        )
                        logger.warning(f"   ✅ Rebuilt encoder_config successfully")
                    else:
                        logger.error(f"   ❌ No col_codecs available - cannot rebuild encoder_config")
                
                # Recreate the encoder (same as in __init__)
                logger.info(f"   🔧 Creating FeatrixTableEncoder from {len(self.col_codecs)} codecs...")
                logger.info(f"   📊 encoder_config.cols_in_order has {len(getattr(self.encoder_config, 'cols_in_order', []))} columns")
                encoder_create_start = time_module.time()
                # Use stored masking parameters or defaults for older models
                min_mask = getattr(self, 'min_mask_ratio', 0.40)
                max_mask = getattr(self, 'max_mask_ratio', 0.60)
                self.encoder = FeatrixTableEncoder(
                    col_codecs=self.col_codecs,
                    config=self.encoder_config,
                    min_mask_ratio=min_mask,
                    max_mask_ratio=max_mask,
                )
                encoder_create_time = time_module.time() - encoder_create_start
                logger.info(f"   ✅ FeatrixTableEncoder created in {encoder_create_time:.1f}s")
                
                # Load the state_dict - CRITICAL: Load to CPU first to avoid GPU OOM
                logger.info(f"   🔧 Loading encoder weights from state_dict TO CPU...")
                state_dict_start = time_module.time()
                # Move state_dict tensors to CPU before loading
                cpu_state_dict = {k: v.cpu() if hasattr(v, 'cpu') else v for k, v in encoder_state_dict.items()}
                
                # Filter out keys with size mismatches before loading
                # PyTorch's load_state_dict with strict=False still raises RuntimeError for size mismatches
                model_state_dict = self.encoder.state_dict()
                filtered_state_dict = {}
                size_mismatches = []
                for key, value in cpu_state_dict.items():
                    if key in model_state_dict:
                        model_shape = model_state_dict[key].shape
                        checkpoint_shape = value.shape if hasattr(value, 'shape') else None
                        if checkpoint_shape is not None and model_shape != checkpoint_shape:
                            size_mismatches.append(f"{key}: checkpoint {checkpoint_shape} vs model {model_shape}")
                            continue
                    filtered_state_dict[key] = value
                
                if size_mismatches:
                    logger.warning(f"   ⚠️  Filtered out {len(size_mismatches)} keys with size mismatches (different data = different vocabs/column counts)")
                    if len(size_mismatches) <= 10:
                        for mismatch in size_mismatches:
                            logger.debug(f"      {mismatch}")
                    else:
                        for mismatch in size_mismatches[:5]:
                            logger.debug(f"      {mismatch}")
                        logger.debug(f"      ... and {len(size_mismatches) - 5} more")
                
                # Use strict=False to allow missing/unexpected keys (but we've already filtered size mismatches)
                missing_keys, unexpected_keys = self.encoder.load_state_dict(filtered_state_dict, strict=False)
                state_dict_time = time_module.time() - state_dict_start
                if missing_keys:
                    logger.warning(f"   ⚠️  {len(missing_keys)} missing keys (new columns or larger vocabs in current data):")
                    for key in missing_keys[:10]:
                        logger.warning(f"      MISSING: {key}")
                    if len(missing_keys) > 10:
                        logger.warning(f"      ... and {len(missing_keys) - 10} more")
                if unexpected_keys:
                    logger.warning(f"   ⚠️  {len(unexpected_keys)} unexpected keys (removed columns or smaller vocabs in current data):")
                    for key in unexpected_keys[:10]:
                        logger.warning(f"      UNEXPECTED: {key}")
                    if len(unexpected_keys) > 10:
                        logger.warning(f"      ... and {len(unexpected_keys) - 10} more")
                logger.info(f"   ✅ Encoder weights loaded to CPU in {state_dict_time:.1f}s (strict=False)")
                
                # Encoder is already on CPU from load_state_dict(cpu_state_dict)
                logger.info(f"✅ EmbeddingSpace.__setstate__: Successfully recreated encoder from state_dict on CPU")
            except Exception as e:
                logger.error(f"❌ EmbeddingSpace.__setstate__: Failed to recreate encoder from state_dict: {e}")
                logger.error(f"❌ EXCEPTION TRACEBACK:\n{traceback.format_exc()}")
                logger.error(f"❌ CALL STACK (who called __setstate__):\n{''.join(traceback.format_stack())}")
                logger.error(f"❌ CRITICAL: Cannot continue without encoder. Exiting immediately.")
                sys.exit(1)
        elif not encoder_in_state:
            # No encoder in state at all - might be None or missing
            logger.warning(f"⚠️  EmbeddingSpace.__setstate__: No encoder found in state (neither encoder nor encoder_state_dict)")
            if not hasattr(self, 'encoder'):
                self.encoder = None
        
        # Log GPU memory after unpickling to see if __setstate__ triggered allocation
        allocated_after = 0.0
        reserved_after = 0.0
        try:
            if is_gpu_available():
                allocated_after = get_gpu_memory_allocated()
                reserved_after = get_gpu_memory_reserved()
                logger.info(f"📊 EmbeddingSpace.__setstate__: GPU memory AFTER: Allocated={allocated_after:.3f} GB, Reserved={reserved_after:.3f} GB")
                if allocated_after > allocated_before + 0.001:  # >1MB increase
                    logger.error(f"🚨 EmbeddingSpace.__setstate__: GPU memory INCREASED by {allocated_after - allocated_before:.3f} GB during unpickling!")
                    logger.error(f"   This likely means col_codecs or StringCache objects triggered GPU allocation")
        except Exception as e:
            logger.info(f"📊 EmbeddingSpace.__setstate__: Could not check GPU memory after: {e}")
        
        # CRITICAL: Check encoder device immediately after unpickling
        # The encoder is a large model and might be unpickled onto GPU even with map_location='cpu'
        if hasattr(self, 'encoder') and self.encoder is not None:
            try:
                allocated_before_encoder_check = 0.0
                if is_gpu_available():
                    allocated_before_encoder_check = get_gpu_memory_allocated()
                    logger.info(f"📊 EmbeddingSpace.__setstate__: GPU memory BEFORE encoder check: Allocated={allocated_before_encoder_check:.3f} GB")
                
                if list(self.encoder.parameters()):
                    encoder_device = next(self.encoder.parameters()).device
                    encoder_param_count = sum(p.numel() for p in self.encoder.parameters())
                    logger.info(f"📊 EmbeddingSpace.__setstate__: Encoder device: {encoder_device.type}, Parameters: {encoder_param_count:,}")
                    
                    if encoder_device.type in ['cuda', 'mps']:
                        logger.error(f"🚨 EmbeddingSpace.__setstate__: Encoder is on GPU! Moving to CPU...")
                        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
                        if force_cpu:
                            logger.info(f"🔄 __setstate__: Moving encoder from GPU to CPU (CPU mode)")
                            self.encoder = self.encoder.cpu()
                            if is_gpu_available():
                                empty_gpu_cache()
                                allocated_after_encoder_move = get_gpu_memory_allocated()
                                logger.info(f"📊 EmbeddingSpace.__setstate__: GPU memory AFTER moving encoder to CPU: Allocated={allocated_after_encoder_move:.3f} GB")
                    else:
                        logger.info(f"✅ EmbeddingSpace.__setstate__: Encoder is already on CPU")
                else:
                    logger.info(f"📊 EmbeddingSpace.__setstate__: Encoder has no parameters")
            except Exception as e:
                logger.error(f"❌ EmbeddingSpace.__setstate__: Could not check encoder device: {e}")
                logger.error(traceback.format_exc())
        
        # train_input_data and val_input_data are excluded from pickle to avoid 100GB+ files
        # Try to recreate them from SQLite database if available
        if 'train_input_data' not in state or 'val_input_data' not in state:
            # Try to recreate from SQLite database
            sqlite_db_path = state.get('sqlite_db_path') or getattr(self, 'sqlite_db_path', None)
            
            if sqlite_db_path and Path(sqlite_db_path).exists():
                try:
                    from featrix.neural.input_data_file import FeatrixInputDataFile
                    from featrix.neural.input_data_set import FeatrixInputDataSet
                    from sklearn.model_selection import train_test_split
                    import logging
                    logger = logging.getLogger(__name__)
                    
                    logger.info(f"🔄 Recreating train_input_data and val_input_data from SQLite: {sqlite_db_path}")
                    
                    # Load data from SQLite
                    input_data_file = FeatrixInputDataFile(sqlite_db_path)
                    df = input_data_file.df
                    
                    # Split into train/val (use same split ratio as original training if available)
                    # Default to 80/20 split
                    train_size = 0.8
                    if len(df) > 0:
                        train_df, val_df = train_test_split(df, train_size=train_size, random_state=42)
                        
                        # Create FeatrixInputDataSet objects
                        # Use standup_only=True to skip expensive detection/enrichment (already done)
                        train_input_data = FeatrixInputDataSet(
                            df=train_df,
                            standup_only=True,
                            dataset_title="TRAIN (recreated from SQLite)"
                        )
                        val_input_data = FeatrixInputDataSet(
                            df=val_df,
                            standup_only=True,
                            dataset_title="VAL (recreated from SQLite)"
                        )
                        
                        if 'train_input_data' not in state:
                            self.train_input_data = train_input_data
                        if 'val_input_data' not in state:
                            self.val_input_data = val_input_data
                        
                        logger.info(f"✅ Recreated train_input_data ({len(train_df)} rows) and val_input_data ({len(val_df)} rows) from SQLite")
                    else:
                        logger.warning(f"⚠️  SQLite database is empty, cannot recreate input data")
                        if 'train_input_data' not in state:
                            self.train_input_data = None
                        if 'val_input_data' not in state:
                            self.val_input_data = None
                except Exception as e:
                    logger.warning(f"⚠️  Failed to recreate input data from SQLite: {e}")
                    logger.debug(f"   Traceback: {traceback.format_exc()}")
                    # Set to None if recreation failed
                    if 'train_input_data' not in state:
                        self.train_input_data = None
                    if 'val_input_data' not in state:
                        self.val_input_data = None
            else:
                # No SQLite database available - set to None
                # Caller should provide input data if needed (e.g., when resuming training)
                if 'train_input_data' not in state:
                    self.train_input_data = None
                if 'val_input_data' not in state:
                    self.val_input_data = None
        
        # Note: sqlite connections (conn/cursor) are set to None and will need to be
        # recreated when string_cache is actually used. This is handled by the
        # movie frame task which uses the data snapshot instead of the full input data.

    # def load_epoch(self, ...):
    # might be missing encoders

    def _get_lambda_lr(self, step_lr_segments):
        """Implement piecewise-constant learning rate schedule.

        Used as input to LambdaLR in `train`.

        lr_stops are expected to have the format
        [(n_steps, lr), (n_steps, lr), ...]
        """

        # Convert from segments expressed in epochs to cumulative milestones expressed in optimizer steps.
        # One step corresponds to a single batch.
        step_lr_milestones = []
        cum = 0
        for n_steps, lr in step_lr_segments:
            step_lr_milestones.append((cum, lr))
            # cum = cum + n_epochs * batches_per_epoch
            cum = cum + n_steps 

        def func(step):
            chosen_lr = None
            for cum_n_steps, lr in step_lr_milestones:
                # Iterate until we find a milestone we haven't reached yet.
                if step >= cum_n_steps:
                    chosen_lr = lr
                else:
                    break

            # This is here just to help with debugging.
            if chosen_lr is None:
                warnings.warn(
                    f"No LR milestone was selected. Current step: {step}. All milestones: {step_lr_milestones}"
                )
                chosen_lr = 1

            return chosen_lr

        return func

    def _prep_profiler(self):
        logger.info("Setting up the profiler.")
        return torch.profiler.profile(
            activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
            schedule=torch.profiler.schedule(
                skip_first=10,
                wait=10,
                warmup=10,
                active=1,
                repeat=1,
            ),
            with_stack=True,
            profile_memory=True,
            record_shapes=True,
            on_trace_ready=torch.profiler.tensorboard_trace_handler('./profiler_output')
        )

    # class TrainingStatusInfo:

    def log_trickiest_columns(self, loss_dict, epoch_idx, top_n=None):
        """
        Analyze and log which columns have the highest losses (are trickiest to predict).
        
        Args:
            loss_dict: The loss dictionary from compute_total_loss containing per-column losses
            epoch_idx: Current epoch index
            top_n: Number of top difficult columns to log. If None, shows all columns (default: None)
        """
        try:
            # Extract column losses from the different marginal loss components
            marginal_loss = loss_dict.get('marginal_loss', {})
            
            # Get column losses from all four marginal loss components
            full_1_cols = marginal_loss.get('marginal_loss_full_1', {}).get('cols', {})
            full_2_cols = marginal_loss.get('marginal_loss_full_2', {}).get('cols', {})
            short_1_cols = marginal_loss.get('marginal_loss_short_1', {}).get('cols', {})
            short_2_cols = marginal_loss.get('marginal_loss_short_2', {}).get('cols', {})
            
            # Aggregate column losses - average across all masks
            column_losses = {}
            all_cols = set(full_1_cols.keys()) | set(full_2_cols.keys()) | set(short_1_cols.keys()) | set(short_2_cols.keys())
            
            for col in all_cols:
                losses = []
                if col in full_1_cols:
                    losses.append(full_1_cols[col])
                if col in full_2_cols:
                    losses.append(full_2_cols[col])
                if col in short_1_cols:
                    losses.append(short_1_cols[col])
                if col in short_2_cols:
                    losses.append(short_2_cols[col])
                
                if losses:
                    column_losses[col] = sum(losses) / len(losses)
            
            if not column_losses:
                return  # No column losses to report
            
            # Sort columns by loss (highest first)
            sorted_cols = sorted(column_losses.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate mean and std dev of column losses
            loss_values = np.array(list(column_losses.values()))
            mean_loss = loss_values.mean()
            std_loss = loss_values.std()
            min_loss = loss_values.min()
            max_loss = loss_values.max()
            median_loss = np.median(loss_values)
            
            # Determine how many columns to show
            n_to_show = len(sorted_cols) if top_n is None else min(top_n, len(sorted_cols))
            
            # Log summary statistics FIRST
            logger.info(f"🎯 [Epoch {epoch_idx+1}] Column Loss Statistics (n={len(sorted_cols)}):")
            logger.info(f"   Mean: {mean_loss:.4f}, Std: {std_loss:.4f}, Median: {median_loss:.4f}")
            logger.info(f"   Min: {min_loss:.4f}, Max: {max_loss:.4f}, Range: {max_loss-min_loss:.4f}")
            
            # Get MI estimates for columns
            col_mi_estimates = self.encoder.col_mi_estimates if hasattr(self.encoder, 'col_mi_estimates') else {}
            
            # Log individual columns sorted from trickiest to easiest
            logger.info(f"🎯 [Epoch {epoch_idx+1}] Column Losses & MI (sorted HARDEST to EASIEST - showing top {n_to_show}):")
            for i, (col_name, avg_loss) in enumerate(sorted_cols[:n_to_show], 1):
                # Add emoji indicators for very high/low losses
                if avg_loss > 10.0:
                    indicator = "🔥"  # Very tricky
                elif avg_loss > 5.0:
                    indicator = "⚠️ "  # Moderately tricky
                elif avg_loss < 1.0:
                    indicator = "✅"  # Easy
                else:
                    indicator = "  "  # Normal
                
                # Get predictability for this column (if available) - now 0-100% scale
                pred_pct = col_mi_estimates.get(col_name, None)
                pred_str = f", pred={pred_pct:.1f}%" if pred_pct is not None else ""
                
                # Flag low predictability columns (likely independent/unpredictable)
                if pred_pct is not None and pred_pct < 20:
                    pred_indicator = " ⚠️ LOW_PRED"
                elif pred_pct is not None and pred_pct < 10:
                    pred_indicator = " 🚫 VERY_LOW_PRED"
                else:
                    pred_indicator = ""
                    
                logger.info(f"   {indicator} {i:3d}. '{col_name}': loss={avg_loss:.4f}{pred_str}{pred_indicator}")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to log column losses: {e}")

    def _encode_value_for_decoding(self, col_name, value, encoder, codec):
        """
        Encode a value using codec.tokenize() + encoder, properly using learned strategy weights.
        
        This is the correct way to encode values for decoding/search - it ensures:
        1. Values are normalized the same way as during training (via codec.tokenize())
        2. Encoders use their learned strategy weights (e.g., AdaptiveScalarEncoder uses ROB if that's best)
        
        Args:
            col_name: Column name
            value: Actual value (not normalized)
            encoder: The encoder for this column (ScalarEncoder, AdaptiveScalarEncoder, SetEncoder, etc.)
            codec: The codec for this column (ScalarCodec, SetCodec, etc.)
            
        Returns:
            full_emb: Full embedding [d_model] (squeezed, no batch dimension)
        """
        from featrix.neural.featrix_token import create_token_batch
        
        # CRITICAL: Use codec.tokenize() to properly normalize the value
        # This ensures the encoder gets values normalized the same way as during training
        token = codec.tokenize(value)
        
        # Create TokenBatch from the token (encoder expects TokenBatch)
        token_batch = create_token_batch([token])
        
        # Encode - encoder uses learned strategy weights
        encoder_output = encoder(token_batch)
        if not isinstance(encoder_output, tuple) or len(encoder_output) != 2:
            raise ValueError(f"Encoder returned unexpected type: {type(encoder_output)}, value: {encoder_output}")
        _, full_emb = encoder_output
        
        # Remove batch dimension
        if full_emb.dim() == 2:
            full_emb = full_emb.squeeze(0)
        
        return full_emb
    
    def _decode_scalar_embedding(self, col_name, col_prediction, encoder, codec, search_samples=None):
        """
        Invert the encoder to decode an embedding back to its scalar value.
        Used to measure encoding lossiness: encode(X) -> embedding -> decode(embedding) -> Y, then measure dist(X, Y).
        
        If encoder has a trained decoder (AdaptiveScalarEncoder with enable_reconstruction=True),
        use it directly for fast, accurate inversion. Otherwise, fall back to gradient descent search.
        
        Args:
            col_name: Column name (unused)
            col_prediction: Encoded embedding [d_model] 
            encoder: The encoder for this column
            codec: ScalarCodec for this column
            search_samples: Ignored
            
        Returns:
            predicted_value: Decoded actual value
            similarity: Always 1.0
        """
        import torch
        import torch.nn.functional as F
        from featrix.neural.featrix_token import Token, TokenStatus, create_token_batch
        
        # Handle batched input: normalize to [1, d_model]
        original_shape = col_prediction.shape
        
        # If it's 2D with batch dimension, extract single embedding
        if col_prediction.dim() == 2:
            if col_prediction.shape[0] > 1:
                # Multiple embeddings in batch - use first one (or could use mean)
                col_prediction = col_prediction[0]  # [d_model]
            elif col_prediction.shape[0] == 1:
                # Single element batch - squeeze it
                col_prediction = col_prediction.squeeze(0)  # [d_model]
            else:
                # Empty batch dimension - shouldn't happen
                raise ValueError(f"Unexpected col_prediction shape: {original_shape}")
        
        # Handle other dimension cases
        if col_prediction.dim() == 0:
            # Scalar - shouldn't happen but handle it
            col_prediction = col_prediction.unsqueeze(0)
        elif col_prediction.dim() > 2:
            # Multiple dimensions - flatten and take appropriate size
            # Assume last dimension is d_model
            col_prediction = col_prediction.view(-1, col_prediction.shape[-1])[0]  # [d_model]
        
        # At this point col_prediction should be 1D [d_model]
        # Now make it [1, d_model] for matrix operations
        if col_prediction.dim() == 1:
            col_prediction = col_prediction.unsqueeze(0)  # [1, d_model]
        elif col_prediction.dim() != 2 or col_prediction.shape[0] != 1:
            raise ValueError(f"After normalization, col_prediction should be [1, d_model], got shape: {col_prediction.shape}")
        
        # FAST PATH: Use trained decoder if available
        # If encoder has reconstruction enabled, use the decoder directly (much faster and more accurate!)
        if (hasattr(encoder, 'enable_reconstruction') and 
            encoder.enable_reconstruction and 
            hasattr(encoder, 'decoder') and 
            encoder.decoder is not None):
            
            with torch.no_grad():
                # Decoder takes embedding and returns normalized value
                normalized_val = encoder.decoder(col_prediction)  # [1, 1]
                normalized_val = normalized_val.squeeze()  # scalar
                
                # Decode normalized value back to actual value
                token = Token(value=normalized_val.item(), status=TokenStatus.OK)
                predicted_value = codec.detokenize(token)
                
                return predicted_value, 1.0
        
        # SLOW PATH: Fall back to gradient descent search (legacy behavior)
        # This is used when encoder doesn't have a decoder (e.g., ScalarEncoder, not AdaptiveScalarEncoder)
        target_emb = F.normalize(col_prediction, dim=-1)  # [1, d_model]
        
        normalized_val = torch.tensor(0.0, device=col_prediction.device, requires_grad=True)
        
        # Store original training mode of encoder
        encoder_was_training = encoder.training if hasattr(encoder, 'training') else False
        
        # Invert encoder with gradient descent
        # Need to enable gradients for the encoder computation
        try:
            with torch.enable_grad():
                # Temporarily set encoder to train mode if it's a module (to enable gradients)
                if hasattr(encoder, 'train'):
                    encoder.train()
                
                for iteration in range(15):
                    with torch.no_grad():
                        normalized_val.clamp_(-4.0, 4.0)
                    
                    # Create a new tensor that requires grad for this iteration
                    normalized_val_iter = normalized_val.clone().detach().requires_grad_(True)
                    
                    token = Token(
                        value=normalized_val_iter.unsqueeze(0),
                        status=torch.tensor([TokenStatus.OK], device=col_prediction.device)
                    )
                    _, encoded_emb = encoder(create_token_batch([token]))
                    
                    # Handle batched encoder output - ensure we have [1, d_model]
                    if encoded_emb.dim() == 2:
                        if encoded_emb.shape[0] > 1:
                            # Multiple embeddings - take first or mean
                            encoded_emb = encoded_emb[0:1]  # Take first: [1, d_model]
                        elif encoded_emb.shape[0] == 1:
                            # Already [1, d_model] - keep as is
                            pass
                        else:
                            raise ValueError(f"Unexpected encoded_emb shape: {encoded_emb.shape}")
                    elif encoded_emb.dim() == 1:
                        # [d_model] - add batch dimension
                        encoded_emb = encoded_emb.unsqueeze(0)  # [1, d_model]
                    elif encoded_emb.dim() > 2:
                        # Flatten extra dimensions
                        encoded_emb = encoded_emb.view(-1, encoded_emb.shape[-1])[0:1]  # [1, d_model]
                    
                    encoded_emb = F.normalize(encoded_emb, dim=-1)  # [1, d_model]
                    
                    # Use matrix multiplication: [1, d_model] @ [d_model, 1] = [1, 1] (scalar)
                    # Both target_emb and encoded_emb are now [1, d_model], so this works correctly
                    loss = -(target_emb @ encoded_emb.T).squeeze()
                    
                    # Check if loss requires grad before calling backward
                    # Also check that encoded_emb has gradients (encoder must be in train mode with requires_grad)
                    if loss.requires_grad and loss.grad_fn is not None and encoded_emb.requires_grad:
                        try:
                            loss.backward()
                            
                            with torch.no_grad():
                                if normalized_val_iter.grad is not None:
                                    normalized_val = normalized_val_iter - 0.5 * normalized_val_iter.grad
                                else:
                                    # No gradient available - break early
                                    normalized_val = normalized_val_iter.detach()
                                    break
                        except RuntimeError as e:
                            if "does not require grad" in str(e) or "grad_fn" in str(e):
                                # Gradient computation failed - fall back to grid search
                                normalized_val = normalized_val_iter.detach()
                                break
                            else:
                                raise
                    else:
                        # If loss doesn't require grad, we can't do gradient descent
                        # This happens when the encoder output doesn't have gradients
                        # Use the current value and break
                        normalized_val = normalized_val_iter.detach()
                        break
        except RuntimeError as e:
            # If backward pass fails (e.g., "does not require grad"), fall back to simple search
            if "does not require grad" in str(e) or "grad_fn" in str(e):
                # Use a simple grid search instead
                best_val = 0.0
                best_sim = -float('inf')
                for test_val in torch.linspace(-4.0, 4.0, steps=50, device=col_prediction.device):
                    token = Token(
                        value=test_val.unsqueeze(0),
                        status=torch.tensor([TokenStatus.OK], device=col_prediction.device)
                    )
                    with torch.no_grad():
                        _, encoded_emb = encoder(create_token_batch([token]))
                        if encoded_emb.dim() == 2:
                            encoded_emb = encoded_emb[0:1] if encoded_emb.shape[0] > 0 else encoded_emb
                        elif encoded_emb.dim() == 1:
                            encoded_emb = encoded_emb.unsqueeze(0)
                        encoded_emb = F.normalize(encoded_emb, dim=-1)
                        sim = (target_emb @ encoded_emb.T).squeeze().item()
                        if sim > best_sim:
                            best_sim = sim
                            best_val = test_val.item()
                normalized_val = torch.tensor(best_val, device=col_prediction.device)
            else:
                raise
        finally:
            # Restore encoder training mode
            if hasattr(encoder, 'train') and not encoder_was_training:
                encoder.eval()
        
        # Decode normalized value back to actual value
        token = Token(value=normalized_val.item(), status=TokenStatus.OK)
        predicted_value = codec.detokenize(token)
        
        return predicted_value, 1.0
    
    def _decode_set_embedding(self, col_name, col_prediction, encoder, codec):
        """
        Decode a set embedding back to an actual value by searching all possible set members.
        
        Uses proper encoding (codec.tokenize + encoder) for each candidate.
        For sets, tokenize() returns token IDs which are used by SetEncoder.
        
        Args:
            col_name: Column name
            col_prediction: Predicted embedding [d_model]
            encoder: The encoder for this column (SetEncoder)
            codec: SetCodec for this column
            
        Returns:
            predicted_value: Best matching set member value
            similarity: Cosine similarity of best match
        """
        from featrix.neural.featrix_token import TokenBatch, TokenStatus, create_token_batch
        import torch
        
        # Get all possible member values
        all_values = [m for m in codec.members if m != "<UNKNOWN>"]
        
        if not all_values:
            return "<EMPTY_SET>", 0.0
        
        # Encode all possible values using codec.tokenize() for consistency
        # For sets, tokenize() returns token IDs which SetEncoder uses
        token_embeddings_list = []
        valid_values = []
        
        for member_value in all_values:
            try:
                # Use codec.tokenize() to get token ID (consistent with training)
                token = codec.tokenize(member_value)
                if token.status != TokenStatus.OK:
                    continue  # Skip UNKNOWN tokens
                
                # Create TokenBatch from token
                token_batch = create_token_batch([token])
                
                # Encode using encoder (SetEncoder uses learned embeddings)
                encoder_output = encoder(token_batch)
                if not isinstance(encoder_output, tuple) or len(encoder_output) != 2:
                    continue
                _, member_emb = encoder_output
                
                # Remove batch dimension
                if member_emb.dim() == 2:
                    member_emb = member_emb.squeeze(0)
                
                token_embeddings_list.append(member_emb.unsqueeze(1))
                valid_values.append(member_value)
            except Exception:
                continue  # Skip values that fail to encode
        
        if not token_embeddings_list:
            return "<EMPTY_SET>", 0.0
        
        # Concatenate along dim=1 to get [d_model, num_candidates]
        token_embeddings = torch.cat(token_embeddings_list, dim=1)
        
        # Find closest embedding to prediction (cosine similarity)
        pred_norm = torch.nn.functional.normalize(col_prediction.unsqueeze(0), dim=-1)
        tok_norm = torch.nn.functional.normalize(token_embeddings, dim=0)  # Normalize along d_model dim
        similarities = (pred_norm @ tok_norm).squeeze()
        best_idx = similarities.argmax().item()
        best_similarity = similarities[best_idx].item()
        
        predicted_value = valid_values[best_idx]
        
        return predicted_value, best_similarity
    
    def _decode_string_embedding(self, col_name, col_prediction, encoder, codec, search_samples=200, debug=False):
        """
        Decode a string embedding back to an actual value using nearest neighbor search in string cache.
        
        COMMENTED OUT: String decoding not yet implemented - needs final embedding index (d_model dims)
        in LanceDB, not BERT embeddings (384 dims).
        
        Args:
            col_name: Column name
            col_prediction: Predicted embedding [d_model] from the model
            encoder: The encoder for this column (StringEncoder)
            codec: StringCodec for this column
            search_samples: Number of candidate values to search (unused, kept for compatibility)
            debug: If True, return top 3 neighbors for debugging
            
        Returns:
            (predicted_value, similarity) tuple with placeholder values
        """
        # TODO: Implement string decoding - requires indexing final embeddings (d_model dims) in LanceDB
        # The encoder outputs d_model dimensions, but the cache stores BERT embeddings (384 dims).
        # Need to build a separate index of final embeddings for proper decoding.
        return "[string_embedding]", 0.0
    
    def _debug_autoencoding_quality(self, epoch_idx):
        """
        Test autoencoding quality: Can we encode → decode values accurately?
        
        This tests representation lossiness (NOT marginal prediction).
        For each column, encode the actual value and decode it back.
        """
        try:
            logger.info(f"")
            logger.info(f"🔍 AUTOENCODING QUALITY TEST")
            logger.info(f"   Testing: Encode → Decode accuracy (representation lossiness)")
            logger.info(f"")
            
            # Sample validation data
            val_df = self.val_input_data.df
            sample_size = min(20, len(val_df))
            sample_df = val_df.sample(sample_size, random_state=42 + epoch_idx)
            
            # Test autoencoding for first 5 columns
            for col_idx, col_name in enumerate(self.col_order[:5]):
                try:
                    codec = self.col_codecs.get(col_name)
                    if not codec:
                        continue
                    
                    from featrix.neural.set_codec import SetCodec
                    from featrix.neural.scalar_codec import ScalarCodec, AdaptiveScalarEncoder
                    
                    codec_type = codec.get_codec_name() if hasattr(codec, 'get_codec_name') else "unknown"
                    
                    results = []
                    
                    # CRITICAL: Set to eval mode for inference, restore training mode after
                    was_training = self.encoder.training
                    self.encoder.eval()
                    try:
                        with torch.no_grad():
                            for idx, row in sample_df.iterrows():
                                try:
                                    original_value = row[col_name]
                                    
                                    # Skip NaN values
                                    if pd.isna(original_value):
                                        continue
                                    
                                    # Use encode_record() - just pass a dict with the single field
                                    # It handles ALL tokenization automatically
                                    # encode_record() returns a single tensor (full_encoding by default)
                                    record = {col_name: original_value}
                                    # Get the device where the encoder is located
                                    encoder_device = next(self.encoder.parameters()).device
                                    full_joint_encoding = self.encode_record(record, squeeze=True, short=False, output_device=encoder_device)
                                    
                                    # Use column predictor to get column-specific encoding from joint encoding
                                    full_col_predictions = self.encoder.column_predictor(full_joint_encoding.unsqueeze(0))
                                    if not isinstance(full_col_predictions, (list, tuple)):
                                        raise TypeError(f"column_predictor should return list, got {type(full_col_predictions)}")
                                    if col_idx >= len(full_col_predictions):
                                        raise IndexError(f"col_idx {col_idx} out of range for {len(full_col_predictions)} predictions")
                                    
                                    # Get the column-specific encoding (full_emb)
                                    full_emb = full_col_predictions[col_idx]
                                    if full_emb.dim() == 2:
                                        full_emb = full_emb.squeeze(0)  # Remove batch dimension
                                    
                                    # Get encoder for decoding - handle featrix_ prefix
                                    encoder = None
                                    if col_name in self.encoder.column_encoder.encoders:
                                        encoder = self.encoder.column_encoder.encoders[col_name]
                                    elif f"featrix_{col_name}" in self.encoder.column_encoder.encoders:
                                        encoder = self.encoder.column_encoder.encoders[f"featrix_{col_name}"]
                                    else:
                                        # Try reverse - if col_name has prefix, try without
                                        if col_name.startswith("featrix_") and col_name[8:] in self.encoder.column_encoder.encoders:
                                            encoder = self.encoder.column_encoder.encoders[col_name[8:]]
                                    
                                    if encoder is None:
                                        logger.info(f"      Autoencoding: No encoder found for '{col_name}' (available: {list(self.encoder.column_encoder.encoders.keys())[:5]}...)")
                                        continue
                                    
                                    # Decode back to value using modular helper functions
                                    try:
                                        if isinstance(codec, SetEncoder):
                                            decoded_value, cosine_sim = self._decode_set_embedding(col_name, full_emb, encoder, codec)
                                            match = str(decoded_value) == str(original_value)
                                            error = 0 if match else 1
                                            
                                        elif isinstance(codec, AdaptiveScalarEncoder):
                                            decoded_value_raw, cosine_sim = self._decode_scalar_embedding(col_name, full_emb, encoder, codec, search_samples=100)
                                            
                                            # Calculate error
                                            try:
                                                if hasattr(original_value, 'item'):
                                                    orig_float = original_value.item()
                                                elif isinstance(original_value, (int, float)):
                                                    orig_float = float(original_value)
                                                else:
                                                    orig_float = float(original_value)
                                                
                                                # Skip if original is NaN
                                                if pd.isna(orig_float) or not np.isfinite(orig_float):
                                                    continue
                                                
                                                error = abs(decoded_value_raw - orig_float)
                                                relative_error = error / (abs(orig_float) + 1e-6)
                                                match = relative_error < 0.1  # <10% error = match
                                            except (ValueError, TypeError):
                                                # Skip invalid values
                                                continue
                                            except Exception:
                                                error = None
                                                match = None
                                                relative_error = None
                                            
                                            decoded_value = decoded_value_raw
                                            
                                        else:
                                            decoded_value = None
                                            match = None
                                            error = None
                                            
                                    except Exception as decode_err:
                                        logger.info(f"      Autoencoding failed for row {idx}: {decode_err}")
                                        decoded_value = None
                                        match = None
                                        error = None
                                    
                                    results.append({
                                        'original': str(original_value)[:20],
                                        'decoded': str(decoded_value)[:20] if decoded_value is not None else "N/A",
                                        'match': match,
                                        'error': error
                                    })
                                    
                                except Exception as e:
                                    logger.info(f"      Autoencoding failed for row {idx}: {e}")
                                    continue
                    finally:
                        # Always restore training mode if it was in training mode before
                        if was_training:
                            self.encoder.train()
                    
                    if results:
                        if isinstance(codec, SetEncoder):
                            correct = sum(1 for r in results if r['match'])
                            accuracy = (correct / len(results)) * 100
                            logger.info(f"   Column '{col_name}' ({codec_type}): {correct}/{len(results)} exact match ({accuracy:.1f}%)")
                            
                            # Show mismatches
                            mismatches = [r for r in results if not r['match']]
                            if mismatches:
                                logger.info(f"      Mismatches:")
                                for i, r in enumerate(mismatches[:3], 1):
                                    logger.info(f"         {i}. Original: {r['original']:20s} → Decoded: {r['decoded']:20s}")
                        
                        elif isinstance(codec, (ScalarCodec, AdaptiveScalarEncoder)):
                            errors = [r['error'] for r in results if r['error'] is not None]
                            if errors:
                                avg_error = sum(errors) / len(errors)
                                max_error = max(errors)
                                good_reconstructions = sum(1 for r in results if r.get('match'))
                                
                                logger.info(f"   Column '{col_name}' ({codec_type}): avg_error={avg_error:.3f}, max_error={max_error:.3f}")
                                logger.info(f"      Good reconstructions (<10% error): {good_reconstructions}/{len(results)} ({100*good_reconstructions/len(results):.1f}%)")
                                
                                # Show worst cases
                                worst = sorted(results, key=lambda r: r.get('error', 0) if r.get('error') is not None else 0, reverse=True)[:3]
                                logger.info(f"      Worst cases:")
                                for i, r in enumerate(worst, 1):
                                    if r['error'] is not None:
                                        logger.info(f"         {i}. Original: {r['original']:20s} → Decoded: {r['decoded']:20s} (error: {r['error']:.3f})")
                            else:
                                logger.info(f"   Column '{col_name}': No valid error calculations (all attempts failed)")
                    else:
                        logger.info(f"   Column '{col_name}': No results collected (all attempts failed)")
                
                except Exception as e:
                    logger.info(f"   Skipped {col_name}: {e}")
            
            logger.info(f"")
            
        except Exception as e:
            logger.warning(f"Failed to debug autoencoding quality: {e}")
            traceback.print_exc()
    
    def _debug_marginal_reconstruction(self, epoch_idx):
        """
        Debug marginal loss by showing actual reconstruction quality on validation data.
        
        For each column, shows:
        - Original value
        - Reconstructed value (from masked prediction)
        - Reconstruction accuracy
        """
        try:
            logger.info(f"")
            logger.info(f"🔬 MARGINAL RECONSTRUCTION DEBUG")
            logger.info(f"   Testing: Can we reconstruct masked columns from other columns?")
            logger.info(f"")
            
            # Get validation data
            val_df = self.val_input_data.df
            
            # Test reconstruction for ALL columns
            for col_idx, col_name in enumerate(self.col_order):
                try:
                    codec = self.col_codecs.get(col_name)
                    if not codec:
                        continue
                    
                    # Get column type
                    from featrix.neural.model_config import ColumnType
                    from featrix.neural.set_codec import SetCodec
                    from featrix.neural.scalar_codec import ScalarCodec, AdaptiveScalarEncoder
                    
                    codec_type = codec.get_codec_name() if hasattr(codec, 'get_codec_name') else "unknown"
                    
                    # Pick 3-4 unique examples from this column
                    unique_values = val_df[col_name].dropna().unique()
                    if len(unique_values) == 0:
                        continue
                    
                    # Sample 3-4 unique values
                    import random
                    random.seed(42 + epoch_idx + col_idx)  # Deterministic but different per column/epoch
                    num_examples = random.choice([3, 4])
                    selected_values = random.sample(list(unique_values), min(num_examples, len(unique_values)))
                    
                    # Check if None is in vocabulary (for SetCodec, check members; for others, try tokenizing)
                    none_in_vocab = False
                    if isinstance(codec, (SetEncoder, SetCodec)):
                        none_in_vocab = None in codec.members or "None" in codec.members or "none" in codec.members
                    else:
                        # Try tokenizing None to see if it's handled
                        try:
                            token = codec.tokenize(None)
                            none_in_vocab = token.status != TokenStatus.UNKNOWN
                        except:
                            none_in_vocab = False
                    
                    # 1/len(selected_values) chance to swap one example with None (if None is not in vocabulary)
                    if not none_in_vocab and random.random() < (1.0 / len(selected_values)):
                        selected_values[random.randint(0, len(selected_values) - 1)] = None
                    
                    # Find rows with these values
                    sample_rows = []
                    for val in selected_values:
                        if val is None:
                            # Find rows where column is None/NaN
                            matching_rows = val_df[val_df[col_name].isna()]
                        else:
                            matching_rows = val_df[val_df[col_name] == val]
                        if len(matching_rows) > 0:
                            # Pick a random row with this value
                            # Ensure random_state is within valid range [0, 2**32 - 1]
                            val_hash = abs(hash(str(val))) % (2**32)
                            random_state = (42 + epoch_idx + col_idx + val_hash) % (2**32)
                            sample_rows.append(matching_rows.sample(1, random_state=random_state).iloc[0])
                    
                    if len(sample_rows) == 0:
                        continue
                    
                    # Collect original vs reconstructed
                    results = []
                    
                    # CRITICAL: Set to eval mode for inference, restore training mode after
                    was_training = self.encoder.training
                    self.encoder.eval()
                    try:
                        with torch.no_grad():
                            for row in sample_rows:
                                try:
                                    idx = row.name if hasattr(row, 'name') else None
                                    original_value = row[col_name]
                                    
                                    # Create record dict from row, but OMIT the target column
                                    # encode_record() will use NOT_PRESENT tokens for missing fields
                                    record = row.to_dict()
                                    del record[col_name]  # Remove target column to mask it
                                    
                                    # Use encode_record() - it handles ALL tokenization automatically
                                    # encode_record() returns a single tensor (full_encoding by default, or short_encoding if short=True)
                                    # Get the device where the encoder is located
                                    encoder_device = next(self.encoder.parameters()).device
                                    full_joint_encoding = self.encode_record(record, squeeze=True, short=False, output_device=encoder_device)
                                    if not isinstance(full_joint_encoding, torch.Tensor):
                                        logger.error(f"❌ Reconstruction failed for row {idx}: encode_record returned unexpected type: {type(full_joint_encoding)}, value: {full_joint_encoding}")
                                        logger.error(f"   Row data: {row.to_dict()}")
                                        logger.error(f"   Record (masked): {record}")
                                        break
                                    
                                    # Predict the masked column from joint encoding
                                    full_col_predictions = self.encoder.column_predictor(full_joint_encoding.unsqueeze(0))
                                    
                                    # column_predictor returns a list of tensors, one per column
                                    if not isinstance(full_col_predictions, (list, tuple)):
                                        raise TypeError(f"column_predictor should return list, got {type(full_col_predictions)}")
                                    
                                    if col_idx >= len(full_col_predictions):
                                        raise IndexError(f"col_idx {col_idx} out of range for {len(full_col_predictions)} predictions")
                                    
                                    col_prediction = full_col_predictions[col_idx]
                                    
                                    # Ensure col_prediction is a tensor with correct shape
                                    if not isinstance(col_prediction, torch.Tensor):
                                        device = full_joint_encoding.device
                                        if isinstance(col_prediction, (int, float)):
                                            col_prediction = torch.tensor(col_prediction, dtype=torch.float32, device=device)
                                        else:
                                            raise TypeError(f"col_prediction must be a tensor, got {type(col_prediction)}")
                                    
                                    # Ensure it has the right shape (should be [batch_size, d_model], squeeze batch dim)
                                    if col_prediction.dim() == 2:
                                        col_prediction = col_prediction.squeeze(0)  # Remove batch dimension
                                    elif col_prediction.dim() == 0:
                                        col_prediction = col_prediction.unsqueeze(0)  # Add dimension if scalar
                                    
                                    # Decode prediction back to value using modular helper functions
                                    # Handle featrix_ prefix
                                    encoder = None
                                    if col_name in self.encoder.column_encoder.encoders:
                                        encoder = self.encoder.column_encoder.encoders[col_name]
                                    elif f"featrix_{col_name}" in self.encoder.column_encoder.encoders:
                                        encoder = self.encoder.column_encoder.encoders[f"featrix_{col_name}"]
                                    else:
                                        # Try reverse - if col_name has prefix, try without
                                        if col_name.startswith("featrix_") and col_name[8:] in self.encoder.column_encoder.encoders:
                                            encoder = self.encoder.column_encoder.encoders[col_name[8:]]
                                    
                                    if encoder is None:
                                        logger.info(f"      Reconstruction: No encoder found for '{col_name}' (available: {list(self.encoder.column_encoder.encoders.keys())[:5]}...)")
                                        continue
                                    
                                    try:
                                        if isinstance(codec, (SetEncoder, SetCodec)):
                                            predicted_value, cosine_sim = self._decode_set_embedding(col_name, col_prediction, encoder, codec)
                                            match = str(predicted_value) == str(original_value)
                                            error = None
                                            
                                        elif isinstance(codec, (AdaptiveScalarEncoder, ScalarCodec)):
                                            predicted_value_raw, cosine_sim = self._decode_scalar_embedding(col_name, col_prediction, encoder, codec)
                                            
                                            # Calculate error
                                            original_value_float = None
                                            try:
                                                if hasattr(original_value, 'item'):
                                                    original_value_float = original_value.item()
                                                elif isinstance(original_value, (int, float)):
                                                    original_value_float = float(original_value)
                                                else:
                                                    original_value_float = float(original_value)
                                                error = abs(predicted_value_raw - original_value_float)
                                                relative_error = error / (abs(original_value_float) + 1e-6)
                                            except Exception:
                                                error = None
                                                relative_error = None
                                            
                                            predicted_value = f"{predicted_value_raw:.3f}"
                                            # For scalars, quality should be based on prediction accuracy, not embedding similarity
                                            # Consider it a "match" if relative error is less than 10% (not based on cosine sim)
                                            match = relative_error < 0.1 if relative_error is not None else False
                                            
                                        else:
                                            # For other types (strings, vectors, etc.)
                                            predicted_value = "[embedding]"
                                            match = None
                                            error = None
                                            cosine_sim = None
                                            
                                    except Exception as decode_err:
                                        logger.info(f"      Reconstruction failed for row {idx}: {decode_err}")
                                        predicted_value = f"[ERROR: {decode_err}]"
                                        match = None
                                        error = None
                                        cosine_sim = None
                                        relative_error = None
                                    
                                    results.append({
                                        'original': str(original_value)[:30],
                                        'predicted': str(predicted_value)[:30],
                                        'match': match,
                                        'error': error,
                                        'cosine_sim': cosine_sim,
                                        'relative_error': relative_error if 'relative_error' in locals() else None
                                    })
                                    
                                except Exception as e:
                                    logger.info(f"      Reconstruction failed for row {idx}: {e}")
                                    continue
                    finally:
                        # Always restore training mode if it was in training mode before
                        if was_training:
                            self.encoder.train()
                    
                    if results:
                        # Calculate accuracy for sets
                        if isinstance(codec, (SetEncoder, SetCodec)):
                            correct = sum(1 for r in results if r['match'])
                            accuracy = (correct / len(results)) * 100
                            logger.info(f"   Column '{col_name}' ({codec_type}): {correct}/{len(results)} correct ({accuracy:.1f}%)")
                            
                            # Show examples
                            logger.info(f"      Examples:")
                            for i, r in enumerate(results[:5], 1):
                                status = "✅" if r['match'] else "❌"
                                logger.info(f"         {i}. {status} Original: {r['original']:30s} → Predicted: {r['predicted']:30s}")
                        elif isinstance(codec, (AdaptiveScalarEncoder, ScalarCodec)):
                            # For scalars: show actual decoded values and errors
                            good_reconstructions = sum(1 for r in results if r.get('match'))
                            avg_cosine_sim = sum(r.get('cosine_sim', 0) for r in results) / len(results)
                            
                            # Calculate average absolute and relative errors
                            errors_with_values = [r for r in results if r.get('error') is not None]
                            if errors_with_values:
                                avg_abs_error = sum(r['error'] for r in errors_with_values) / len(errors_with_values)
                                avg_rel_error = sum(r.get('relative_error', 0) for r in errors_with_values) / len(errors_with_values)
                                
                                # Track error history for trend analysis (use a different key to distinguish from scalar quality test)
                                marginal_key = f"marginal_{col_name}"
                                self._reconstruction_error_history[marginal_key].append((epoch_idx, avg_rel_error))
                                
                                # Compute trend
                                trend = ""
                                history = self._reconstruction_error_history.get(marginal_key, [])
                                if len(history) >= 2:
                                    recent = history[-min(3, len(history)):]
                                    errors_only = [err for _, err in recent]
                                    first_err = errors_only[0]
                                    last_err = errors_only[-1]
                                    
                                    if first_err > 0:
                                        pct_change = ((last_err - first_err) / first_err) * 100
                                        if pct_change < -5:
                                            trend = " [↓ improving]"
                                        elif pct_change > 5:
                                            trend = " [↑ worsening]"
                                        else:
                                            trend = " [→ stable]"
                                
                                logger.info(f"   Column '{col_name}' ({codec_type}): avg_similarity={avg_cosine_sim:.3f}, avg_error={avg_abs_error:.4f} ({avg_rel_error*100:.1f}%){trend}")
                                logger.info(f"      High quality (<10% error): {good_reconstructions}/{len(results)} ({100*good_reconstructions/len(results):.1f}%)")
                            else:
                                logger.info(f"   Column '{col_name}' ({codec_type}): avg_similarity={avg_cosine_sim:.3f}")
                            
                            # Show examples with actual predicted vs original values
                            logger.info(f"      Examples:")
                            for i, r in enumerate(results[:5], 1):
                                sim = r.get('cosine_sim', 0)
                                err = r.get('error')
                                rel_err = r.get('relative_error')
                                
                                # For scalars, status should be based on prediction accuracy, not embedding similarity
                                if rel_err is not None:
                                    if rel_err < 0.1:  # Less than 10% error
                                        status = "✅"
                                    elif rel_err < 0.3:  # Less than 30% error
                                        status = "⚠️ "
                                    else:
                                        status = "❌"
                                else:
                                    # Fallback to similarity if error not available
                                    if sim > 0.9:
                                        status = "✅"
                                    elif sim > 0.7:
                                        status = "⚠️ "
                                    else:
                                        status = "❌"
                                
                                if err is not None and rel_err is not None:
                                    logger.info(f"         {i}. {status} Original: {r['original']:>12s} → Predicted: {r['predicted']:>12s} | Error: {err:>8.3f} ({rel_err*100:>5.1f}%)")
                                else:
                                    logger.info(f"         {i}. {status} Original: {r['original']:>12s} → Predicted: {r['predicted']:>12s} | Similarity: {sim:.3f}")
                        else:
                            logger.info(f"   Column '{col_name}' ({codec_type}): {len(results)} samples")
                            logger.info(f"      [Reconstruction quality metrics not yet implemented for this type]")

                except Exception as e:
                    logger.info(f"   Skipped {col_name}: {e}")

            logger.info(f"")

        except Exception as e:
            logger.warning(f"Failed to debug marginal reconstruction: {e}")
            traceback.print_exc()


    def _debug_scalar_reconstruction_quality(self, epoch_idx):
        """
        Test scalar reconstruction quality by sampling 100 values per column and computing total error.
        Runs every 10 epochs.
        """
        if epoch_idx % 10 != 0:
            return  # Only run every 10 epochs
        
        try:
            logger.info(f"")
            logger.info(f"📊 SCALAR RECONSTRUCTION QUALITY TEST (100 samples per column)")
            logger.info(f"   Testing: Encode → Decode accuracy across distribution")
            logger.info(f"")
            
            # Get all scalar columns
            scalar_columns = []
            
            # DEBUG: Log what columns we have
            logger.info(f"   DEBUG: col_order has {len(self.col_order)} columns: {self.col_order[:10]}...")
            logger.info(f"   DEBUG: col_codecs has {len(self.col_codecs)} codecs: {list(self.col_codecs.keys())[:10]}...")
            logger.info(f"   DEBUG: encoder.column_encoder.encoders has {len(self.encoder.column_encoder.encoders)} encoders: {list(self.encoder.column_encoder.encoders.keys())[:10]}...")
            logger.info(f"   Starting to iterate over {len(self.col_order)} columns...")
            for col_idx, col_name in enumerate(self.col_order):
                try:
                    logger.info(f"   Processing column {col_idx+1}/{len(self.col_order)}: {col_name}")
                    codec = self.col_codecs.get(col_name)
                    if isinstance(codec, AdaptiveScalarEncoder):
                        # Try both with and without featrix_ prefix
                        encoder = None
                        if col_name in self.encoder.column_encoder.encoders:
                            encoder = self.encoder.column_encoder.encoders[col_name]
                        elif f"featrix_{col_name}" in self.encoder.column_encoder.encoders:
                            encoder = self.encoder.column_encoder.encoders[f"featrix_{col_name}"]
                            logger.info(f"   DEBUG: Found encoder with featrix_ prefix: featrix_{col_name} (original: {col_name})")
                        elif col_name.startswith("featrix_") and col_name[8:] in self.encoder.column_encoder.encoders:
                            encoder = self.encoder.column_encoder.encoders[col_name[8:]]
                            logger.info(f"   DEBUG: Found encoder without featrix_ prefix: {col_name[8:]} (original: {col_name})")
                        
                        if encoder:
                            scalar_columns.append((col_name, codec, encoder))
                            logger.info(f"   Added scalar column '{col_name}' to test list")
                        else:
                            logger.info(f"   DEBUG: ScalarCodec found for '{col_name}' but no matching encoder in column_encoder.encoders")
                except Exception as col_err:
                    logger.info(f"   Error processing column '{col_name}': {col_err}")
                    logger.info(f"   Traceback: {traceback.format_exc()}")
                    continue
            
            logger.info(f"   Found {len(scalar_columns)} scalar columns to test")
            
            if not scalar_columns:
                logger.info(f"   No scalar columns found!")
                logger.info(f"   Available encoders: {list(self.encoder.column_encoder.encoders.keys())}")
                logger.info(f"   Available codecs: {[k for k, v in self.col_codecs.items() if isinstance(v, AdaptiveScalarEncoder)]}")
                return
            
            # Set to eval mode for inference
            was_training = self.encoder.training
            self.encoder.eval()
            
            try:
                with torch.no_grad():
                    column_errors = {}
                    
                    logger.info(f"   Starting to test {len(scalar_columns)} scalar columns...")
                    for col_idx, (col_name, codec, encoder) in enumerate(scalar_columns):
                        try:
                            logger.info(f"   Testing column {col_idx+1}/{len(scalar_columns)}: {col_name}")
                            # Sample 100 values across the distribution
                            # Use key distribution points: min, q10, q25, median, q75, q90, max
                            # Plus uniform samples between min and max
                            stats = codec.stats
                            min_val = stats.get('min', codec.mean - 4 * codec.stdev)
                            max_val = stats.get('max', codec.mean + 4 * codec.stdev)
                            mean_val = codec.mean
                            
                            # Key distribution points
                            key_points = []
                            if 'q10' in stats:
                                key_points.append(stats['q10'])
                            if 'q25' in stats:
                                key_points.append(stats['q25'])
                            if 'median' in stats:
                                key_points.append(stats['median'])
                            if 'q75' in stats:
                                key_points.append(stats['q75'])
                            if 'q90' in stats:
                                key_points.append(stats['q90'])
                            
                            # Fill remaining samples with uniform distribution
                            n_key_points = len(key_points) + 3  # +3 for min, max, mean
                            n_uniform = 16 - n_key_points
                            
                            # Create test values
                            test_values = [min_val, mean_val, max_val] + key_points
                            if n_uniform > 0:
                                uniform_samples = np.linspace(min_val, max_val, n_uniform)
                                test_values.extend(uniform_samples.tolist())
                            
                            # Trim to exactly 100
                            test_values = test_values[:16]
                            
                            # Test each value
                            total_abs_error = 0.0
                            total_rel_error = 0.0
                            n_valid = 0
                            n_failed = 0
                            errors = []
                            
                            for idx, test_val in enumerate(test_values):
                                try:
                                    # Get column prediction from joint encoding
                                    # Create a dummy record and encode it
                                    record = {col_name: test_val}
                                    # Get the device where the encoder is located
                                    encoder_device = next(self.encoder.parameters()).device
                                    full_joint_encoding = self.encode_record(record, squeeze=True, short=False, output_device=encoder_device)
                                    
                                    # Get column-specific prediction
                                    # column_predictor returns a list of tensors, one per column in col_order
                                    full_col_predictions = self.encoder.column_predictor(full_joint_encoding.unsqueeze(0))
                                    if not isinstance(full_col_predictions, (list, tuple)):
                                        raise TypeError(f"column_predictor should return list, got {type(full_col_predictions)}")
                                    
                                    # Find the index of this column in col_order
                                    # Check both with and without prefix
                                    col_idx = None
                                    if col_name in self.col_order:
                                        col_idx = self.col_order.index(col_name)
                                    elif f"featrix_{col_name}" in self.col_order:
                                        col_idx = self.col_order.index(f"featrix_{col_name}")
                                    elif col_name.startswith("featrix_") and col_name[8:] in self.col_order:
                                        col_idx = self.col_order.index(col_name[8:])
                                    
                                    if col_idx is None:
                                        raise ValueError(f"Column '{col_name}' not found in col_order. Available: {self.col_order[:10]}...")
                                    if col_idx >= len(full_col_predictions):
                                        raise IndexError(f"col_idx {col_idx} out of range for {len(full_col_predictions)} predictions (col_order has {len(self.col_order)} columns)")
                                    
                                    col_prediction = full_col_predictions[col_idx]  # [batch_size, d_model]
                                    
                                    # Remove batch dimension
                                    if col_prediction.dim() == 2:
                                        col_prediction = col_prediction.squeeze(0)  # [d_model]
                                    elif col_prediction.dim() == 0:
                                        col_prediction = col_prediction.unsqueeze(0)  # Add dimension if scalar
                                    
                                    # Decode back
                                    predicted_val, similarity = self._decode_scalar_embedding(
                                        col_name, col_prediction, encoder, codec, search_samples=200
                                    )
                                    
                                    # Compute errors
                                    abs_error = abs(predicted_val - test_val)
                                    if abs(test_val) > 1e-10:
                                        rel_error = abs_error / abs(test_val)
                                    else:
                                        rel_error = abs_error  # Avoid division by zero
                                    
                                    total_abs_error += abs_error
                                    total_rel_error += rel_error
                                    errors.append(abs_error)
                                    n_valid += 1
                                    
                                except Exception as e:
                                    n_failed += 1
                                    # Log first 3 errors at WARNING level to diagnose issues
                                    if n_failed <= 3:
                                        logger.warning(f"      Failed to test value {test_val} for {col_name} (attempt {idx+1}/{len(test_values)}): {e}")
                                        logger.info(f"      Traceback: {traceback.format_exc()}")
                                    else:
                                        logger.info(f"      Failed to test value {test_val} for {col_name}: {e}")
                                    continue
                            
                            if n_valid > 0:
                                avg_abs_error = total_abs_error / n_valid
                                avg_rel_error = total_rel_error / n_valid
                                max_error = max(errors) if errors else 0.0
                                median_error = np.median(errors) if errors else 0.0
                                
                                column_errors[col_name] = {
                                    'total_abs_error': total_abs_error,
                                    'avg_abs_error': avg_abs_error,
                                    'avg_rel_error': avg_rel_error,
                                    'max_error': max_error,
                                    'median_error': median_error,
                                    'n_valid': n_valid
                                }
                                
                                # Track error history for trend analysis
                                self._reconstruction_error_history[col_name].append((epoch_idx, avg_rel_error))
                            else:
                                logger.warning(f"   Column '{col_name}': No valid reconstructions ({n_failed}/{len(test_values)} failed)")
                                
                        except Exception as e:
                            logger.warning(f"   Error testing column '{col_name}': {e}")
                            logger.warning(f"   Traceback: {traceback.format_exc()}")
                            # Continue with next column
                    
                    # Log results sorted by total error
                    if column_errors:
                        sorted_cols = sorted(column_errors.items(), key=lambda x: x[1]['total_abs_error'], reverse=True)
                        
                        logger.info(f"   Results (sorted by total error, worst first):")
                        logger.info(f"   {'Column Name':<40s} | {'Total Error':<12s} | {'Avg Error':<12s} | {'Avg Rel %':<10s} | {'Max Error':<12s} | {'Median':<12s} | {'Trend':<6s}")
                        logger.info(f"   {'-' * 40} | {'-' * 12} | {'-' * 12} | {'-' * 10} | {'-' * 12} | {'-' * 12} | {'-' * 6}")
                        
                        for col_name, errors_dict in sorted_cols:
                            total_err = errors_dict['total_abs_error']
                            avg_err = errors_dict['avg_abs_error']
                            avg_rel = errors_dict['avg_rel_error'] * 100
                            max_err = errors_dict['max_error']
                            median_err = errors_dict['median_error']
                            
                            # Compute trend indicator
                            trend = "     "  # Default: no trend data yet
                            history = self._reconstruction_error_history.get(col_name, [])
                            if len(history) >= 2:
                                # Compare current error to previous measurements
                                # Use last 3 measurements if available, otherwise last 2
                                recent = history[-min(3, len(history)):]
                                errors_only = [err for _, err in recent]
                                
                                # Simple linear trend: is it going down, up, or flat?
                                first_err = errors_only[0]
                                last_err = errors_only[-1]
                                
                                if len(errors_only) >= 2:
                                    # Calculate percentage change
                                    if first_err > 0:
                                        pct_change = ((last_err - first_err) / first_err) * 100
                                    else:
                                        pct_change = 0
                                    
                                    # Threshold: >5% change is significant
                                    if pct_change < -5:
                                        trend = "↓ ✅"  # Improving (error going down)
                                    elif pct_change > 5:
                                        trend = "↑ ❌"  # Worsening (error going up)
                                    else:
                                        trend = "→"     # Stable
                            
                            logger.info(f"   {col_name:<40s} | {total_err:>12.4f} | {avg_err:>12.4f} | {avg_rel:>9.2f}% | {max_err:>12.4f} | {median_err:>12.4f} | {trend:<6s}")
                        
                        # Summary statistics
                        total_errors = [e['total_abs_error'] for e in column_errors.values()]
                        avg_errors = [e['avg_abs_error'] for e in column_errors.values()]
                        
                        logger.info(f"")
                        logger.info(f"   Summary: {len(column_errors)} scalar columns tested")
                        logger.info(f"      Total error: mean={np.mean(total_errors):.4f}, std={np.std(total_errors):.4f}")
                        logger.info(f"      Avg error: mean={np.mean(avg_errors):.4f}, std={np.std(avg_errors):.4f}")
                    else:
                        logger.info(f"   No scalar columns successfully tested")
                        
            finally:
                # Restore training mode
                if was_training:
                    self.encoder.train()
            
            logger.info(f"")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to test scalar reconstruction quality: {e}")
            logger.error(f"   This may indicate a serious issue - training may halt")
            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            # Don't re-raise - allow training to continue even if debug test fails
    
    def _update_column_loss_tracker(self, loss_dict):
        """
        Update running average of per-column losses for scalar columns.
        Used for progressive pruning of worst-performing columns.
        """
        try:
            marginal_loss = loss_dict.get('marginal_loss', {})
            
            # Get column losses from all four marginal loss components
            full_1_cols = marginal_loss.get('marginal_loss_full_1', {}).get('cols', {})
            full_2_cols = marginal_loss.get('marginal_loss_full_2', {}).get('cols', {})
            short_1_cols = marginal_loss.get('marginal_loss_short_1', {}).get('cols', {})
            short_2_cols = marginal_loss.get('marginal_loss_short_2', {}).get('cols', {})
            
            # Aggregate column losses - average across all masks
            all_cols = set(full_1_cols.keys()) | set(full_2_cols.keys()) | set(short_1_cols.keys()) | set(short_2_cols.keys())
            
            for col in all_cols:
                losses = []
                if col in full_1_cols:
                    losses.append(full_1_cols[col])
                if col in full_2_cols:
                    losses.append(full_2_cols[col])
                if col in short_1_cols:
                    losses.append(short_1_cols[col])
                if col in short_2_cols:
                    losses.append(short_2_cols[col])
                
                if losses:
                    avg_loss = sum(losses) / len(losses)
                    # Update running average (EMA)
                    if col not in self._column_loss_tracker:
                        self._column_loss_tracker[col] = avg_loss
                        self._column_loss_count[col] = 1
                    else:
                        # Exponential moving average
                        alpha = 0.1  # Weight for new observation
                        self._column_loss_tracker[col] = (1 - alpha) * self._column_loss_tracker[col] + alpha * avg_loss
                        self._column_loss_count[col] += 1
        except Exception as e:
            logger.warning(f"Failed to update column loss tracker: {e}")
    
    def _prune_worst_scalar_columns(self, loss_dict, epoch_idx, prune_percent=0.10, cumulative=False):
        """
        Prune (disable) worst-performing scalar column encoders.
        
        Args:
            loss_dict: Current loss dictionary
            epoch_idx: Current epoch index
            prune_percent: Percentage of scalar columns to prune (0.10 = 10%)
            cumulative: If True, prune additional columns (for 20% milestone). If False, prune from all (for 10% milestone).
        """
        try:
            from featrix.neural.scalar_codec import AdaptiveScalarEncoder
            from featrix.neural.model_config import ColumnType
            
            # Get all scalar columns (including disabled ones to track original count)
            all_scalar_columns = []
            active_scalar_columns = []
            for col_name, encoder in self.encoder.column_encoder.encoders.items():
                if isinstance(encoder, AdaptiveScalarEncoder):
                    all_scalar_columns.append(col_name)
                    if not encoder._disabled:
                        active_scalar_columns.append(col_name)
            
            if not all_scalar_columns:
                logger.info(f"   No scalar columns found")
                return
            
            # Track original count on first call
            if not hasattr(self, '_original_scalar_count'):
                self._original_scalar_count = len(all_scalar_columns)
            
            if not active_scalar_columns:
                logger.info(f"   No active scalar columns to prune (all already pruned)")
                return
            
            # Get average losses for all scalar columns (including disabled ones for ranking)
            column_losses = {}
            for col_name in all_scalar_columns:
                if col_name in self._column_loss_tracker:
                    column_losses[col_name] = self._column_loss_tracker[col_name]
            
            if not column_losses:
                logger.warning(f"   No column loss data available for pruning")
                return
            
            # Sort by loss (highest = worst), but only consider active columns
            active_column_losses = {col: column_losses[col] for col in active_scalar_columns if col in column_losses}
            sorted_cols = sorted(active_column_losses.items(), key=lambda x: x[1], reverse=True)
            
            # Calculate how many to prune based on original count
            n_to_prune = max(1, int(self._original_scalar_count * prune_percent))
            
            # Prune worst columns
            pruned_cols = []
            for col_name, avg_loss in sorted_cols[:n_to_prune]:
                encoder = None
                if col_name in self.encoder.column_encoder.encoders:
                    encoder = self.encoder.column_encoder.encoders[col_name]
                if encoder and isinstance(encoder, AdaptiveScalarEncoder) and not encoder._disabled:
                    encoder._disabled = True
                    pruned_cols.append((col_name, avg_loss))
            
            if pruned_cols:
                total_pruned = sum(1 for col in all_scalar_columns 
                                 if self.encoder.column_encoder.encoders[col]._disabled)
                logger.info(f"✂️  [Epoch {epoch_idx}] Progressive pruning: Disabled {len(pruned_cols)} worst scalar columns ({prune_percent*100:.0f}% of original {self._original_scalar_count}):")
                for col_name, avg_loss in pruned_cols:
                    logger.info(f"      - {col_name}: avg_loss={avg_loss:.4f}")
                logger.info(f"   Total pruned: {total_pruned}/{self._original_scalar_count} ({total_pruned/self._original_scalar_count*100:.0f}%), Remaining active: {len(active_scalar_columns) - len(pruned_cols)}")
            else:
                logger.info(f"   No columns pruned (all candidates already disabled)")
                
        except Exception as e:
            logger.warning(f"Failed to prune worst scalar columns: {e}")
            traceback.print_exc()
    
    def _log_embedding_quality_summary(self, epoch_idx: int = None):
        """
        Log a full embedding quality table during training.
        
        Tests per-column perturbation sensitivity and prints a formatted table
        showing how well each column is being learned.
        
        Args:
            epoch_idx: Optional epoch number for quality tracking
        """
        try:
            # Use validation data if available, otherwise train data
            if hasattr(self, 'val_input_data') and self.val_input_data is not None:
                val_df = self.val_input_data.df
            elif hasattr(self, 'train_input_data') and self.train_input_data is not None:
                val_df = self.train_input_data.df
            else:
                logger.warning("   Quality check skipped: no data available")
                return
            
            target_col = self.target_column if hasattr(self, 'target_column') else None
            
            # Sample a test row
            test_row = val_df.iloc[0:1].copy()
            original_dict = test_row.iloc[0].to_dict()
            if target_col:
                original_dict = {k: v for k, v in original_dict.items() if k != target_col}
            
            self.encoder.eval()
            with torch.no_grad():
                original_emb = self.encode_record(original_dict, squeeze=True, short=False)
            
            # Identify column types
            numeric_cols = val_df.select_dtypes(include=[np.number]).columns.tolist()
            if target_col and target_col in numeric_cols:
                numeric_cols.remove(target_col)
            categorical_cols = [c for c in val_df.columns if c not in numeric_cols and c != target_col]
            
            # ============================================================================
            # ENCODER GEOMETRY GROUPING: Compute behavioral signatures for numeric columns
            # ============================================================================
            def get_encoder_geometry_groups():
                """Define encoder groups by geometric behavior."""
                return {
                    'METRIC': ['linear', 'zscore', 'minmax', 'robust', 'yeojohnson', 'log', 'clipped_log', 'inverse'],
                    'QUANTIZED': ['bucket', 'quantile', 'rank', 'target_bin'],
                    'SATURATING': ['sigmoid', 'winsor'],
                    'RELATIONAL': ['polynomial', 'frequency', 'is_positive', 'is_negative', 'is_outlier', 'periodic']
                }
            
            def compute_column_behavior(column_name):
                """
                Compute column behavioral signature from encoder strategy weights.
                
                Returns:
                    dict with keys: 'behavior', 'group_scores', 'group_probs', 'dominant_group'
                """
                geometry_groups = get_encoder_geometry_groups()
                
                # Get encoder strategy weights if available
                strategy_weights = {}
                try:
                    if hasattr(self.encoder, 'column_encoder') and hasattr(self.encoder.column_encoder, 'encoders'):
                        if column_name in self.encoder.column_encoder.encoders:
                            encoder = self.encoder.column_encoder.encoders[column_name]
                            from featrix.neural.scalar_codec import AdaptiveScalarEncoder
                            if isinstance(encoder, AdaptiveScalarEncoder):
                                if hasattr(encoder, 'get_strategy_weights'):
                                    strategy_weights = encoder.get_strategy_weights()
                except Exception as e:
                    logger.debug(f"   Could not get strategy weights for {column_name}: {e}")
                
                if not strategy_weights or 'error' in strategy_weights:
                    return {
                        'behavior': 'UNKNOWN',
                        'group_scores': {},
                        'group_probs': {},
                        'dominant_group': None
                    }
                
                # Sum scores by group
                group_scores = {
                    'METRIC': 0.0,
                    'QUANTIZED': 0.0,
                    'SATURATING': 0.0,
                    'RELATIONAL': 0.0
                }
                
                # Map geometry group names to strategy weight keys
                encoder_to_weight_key = {
                    'linear': 'linear', 'zscore': 'zscore', 'minmax': 'minmax', 'robust': 'robust',
                    'yeojohnson': 'yeojohnson', 'log': 'log', 'clipped_log': 'clipped_log', 'inverse': 'inverse',
                    'bucket': 'bucket', 'quantile': 'quantile', 'rank': 'rank', 'target_bin': 'target_bin',
                    'sigmoid': 'sigmoid', 'winsor': 'winsor',
                    'polynomial': 'polynomial', 'frequency': 'frequency', 'is_positive': 'is_positive',
                    'is_negative': 'is_negative', 'is_outlier': 'is_outlier', 'periodic': 'periodic'
                }
                
                for group_name, encoder_names in geometry_groups.items():
                    for encoder_name in encoder_names:
                        weight_key = encoder_to_weight_key.get(encoder_name, encoder_name)
                        if weight_key in strategy_weights:
                            group_scores[group_name] += strategy_weights[weight_key]
                
                # Normalize to probabilities using softmax
                scores_array = np.array([group_scores['METRIC'], group_scores['QUANTIZED'], 
                                        group_scores['SATURATING'], group_scores['RELATIONAL']])
                scores_array = scores_array + 1e-10
                exp_scores = np.exp(scores_array - np.max(scores_array))
                group_probs = exp_scores / exp_scores.sum()
                
                group_probs_dict = {
                    'METRIC': float(group_probs[0]),
                    'QUANTIZED': float(group_probs[1]),
                    'SATURATING': float(group_probs[2]),
                    'RELATIONAL': float(group_probs[3])
                }
                
                # Find dominant group (must exceed 40% to be considered dominant)
                max_prob = max(group_probs_dict.values())
                if max_prob >= 0.40:
                    dominant_group = max(group_probs_dict.items(), key=lambda x: x[1])[0]
                    behavior = dominant_group
                else:
                    behavior = 'MIXED'
                    dominant_group = None
                
                return {
                    'behavior': behavior,
                    'group_scores': group_scores,
                    'group_probs': group_probs_dict,
                    'dominant_group': dominant_group
                }
            
            # Compute behavioral signatures for all numeric columns
            column_behaviors = {}
            for col in numeric_cols:
                column_behaviors[col] = compute_column_behavior(col)
            
            column_results = {}
            
            # Test numeric columns
            for col in numeric_cols[:10]:  # Limit for speed
                if col not in original_dict:
                    continue
                original_value = original_dict[col]
                if pd.isna(original_value) or original_value == 0:
                    continue
                
                distances = []
                perturbations = []
                absolute_deltas = []
                
                for pct in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]:
                    modified_dict = original_dict.copy()
                    delta = original_value * (pct / 100.0)
                    modified_dict[col] = original_value + delta
                    perturbations.append(pct)
                    absolute_deltas.append(abs(delta))
                    
                    with torch.no_grad():
                        modified_emb = self.encode_record(modified_dict, squeeze=True, short=False)
                    dist = torch.norm(original_emb - modified_emb).item()
                    distances.append(dist)
                
                perturbations_array = np.array(perturbations)
                absolute_deltas_array = np.array(absolute_deltas)
                distances_array = np.array(distances)
                
                # Sensitivity per unit
                non_zero_mask = absolute_deltas_array > 1e-10
                if np.any(non_zero_mask):
                    sensitivity_per_unit = distances_array[non_zero_mask] / absolute_deltas_array[non_zero_mask]
                    mean_sensitivity = np.mean(sensitivity_per_unit)
                    std_sensitivity = np.std(sensitivity_per_unit)
                else:
                    mean_sensitivity = 0.0
                    std_sensitivity = 0.0
                
                # Proportionality correlation
                if len(distances) > 2 and np.std(perturbations_array) > 1e-10 and np.std(distances_array) > 1e-10:
                    try:
                        corr = np.corrcoef(perturbations_array, distances_array)[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                    except (ValueError, IndexError):
                        corr = 0.0
                else:
                    corr = 0.0
                
                dist_range = np.max(distances) - np.min(distances)
                consistency = std_sensitivity / (mean_sensitivity + 1e-10)
                
                # Get behavioral signature for this column
                behavior_info = column_behaviors.get(col, {})
                behavior = behavior_info.get('behavior', 'UNKNOWN')
                
                # Set expectations based on behavioral signature
                # METRIC: Expect high proportionality (corr > 0.7) - smooth, proportional sensitivity
                # QUANTIZED: Expect low/negative proportionality (by design - discrete jumps)
                # SATURATING: Sensitivity depends on operating region - moderate proportionality OK
                # RELATIONAL: Marginal perturbation is wrong test - expect low marginal sensitivity
                # MIXED: Context-dependent behavior - more lenient criteria
                
                if behavior == 'METRIC':
                    # Metric columns should have smooth, proportional sensitivity
                    is_proportional = corr > 0.7
                    is_marginal_prop = corr > 0.5 and not is_proportional
                    proportionality_ok = corr > 0.5  # Low proportionality is a problem for metric
                elif behavior == 'QUANTIZED':
                    # Quantized columns have discrete jumps - low proportionality is expected
                    is_proportional = False
                    is_marginal_prop = False
                    proportionality_ok = True  # Don't penalize for low correlation (by design)
                elif behavior == 'SATURATING':
                    # Saturating columns depend on operating region
                    is_proportional = corr > 0.5  # Moderate is OK
                    is_marginal_prop = corr > 0.3 and not is_proportional
                    proportionality_ok = True  # Context-dependent
                elif behavior == 'RELATIONAL':
                    # Relational columns have weak marginal sensitivity by design
                    is_proportional = False
                    is_marginal_prop = False
                    proportionality_ok = True  # Don't penalize - effects emerge via relationships
                else:  # MIXED or UNKNOWN
                    # Mixed behavior - use standard criteria
                    is_proportional = corr > 0.7
                    is_marginal_prop = corr > 0.5 and not is_proportional
                    proportionality_ok = corr > 0.3  # More lenient for mixed
                
                # Sensitivity check (adjusted by behavior)
                has_sensitivity = mean_sensitivity > 0.0001
                if behavior == 'RELATIONAL':
                    # For relational, low marginal sensitivity is expected
                    has_sensitivity = True  # Don't penalize
                
                # Consistency check: std_sensitivity / mean_sensitivity (lower = more stable)
                # For QUANTIZED, higher consistency variation is expected (discrete jumps)
                if behavior == 'QUANTIZED':
                    has_consistent = consistency < 1.0  # More lenient for quantized
                else:
                    has_consistent = consistency < 0.5  # Standard threshold
                
                has_variation = dist_range > 0.001
                
                quality_score = 0
                if proportionality_ok:
                    quality_score += 2  # Behavior matches expectations
                if has_sensitivity:
                    quality_score += 1
                if has_consistent:
                    quality_score += 1
                if has_variation:
                    quality_score += 1
                
                if quality_score >= 4:
                    quality = "GOOD"
                elif quality_score >= 2:
                    quality = "MARGINAL"
                else:
                    quality = "POOR"
                
                column_results[col] = {
                    'type': 'numeric',
                    'correlation': corr,
                    'mean_sensitivity': mean_sensitivity,
                    'std_sensitivity': std_sensitivity,
                    'consistency': consistency,
                    'variation': dist_range,
                    'quality': quality,
                    'is_proportional': is_proportional,
                    'is_marginal_prop': is_marginal_prop,
                    'has_sensitivity': has_sensitivity,
                    'has_consistent': has_consistent,
                    'has_variation': has_variation,
                    'behavior': behavior,
                    'proportionality_ok': proportionality_ok,
                }
            
            # Test categorical columns
            for col in categorical_cols[:10]:
                if col not in original_dict:
                    continue
                original_value = original_dict[col]
                possible_values = val_df[col].dropna().unique()
                
                if len(possible_values) < 2:
                    continue
                
                distances = []
                for new_value in possible_values:
                    if new_value == original_value:
                        continue
                    modified_dict = original_dict.copy()
                    modified_dict[col] = new_value
                    with torch.no_grad():
                        modified_emb = self.encode_record(modified_dict, squeeze=True, short=False)
                    dist = torch.norm(original_emb - modified_emb).item()
                    distances.append(dist)
                
                if distances:
                    mean_dist = np.mean(distances)
                    dist_range = np.max(distances) - np.min(distances)
                    has_sensitivity = mean_dist > 0.001
                    has_variation = dist_range > 0.0005
                    
                    if has_sensitivity and has_variation:
                        quality = "GOOD"
                    elif has_sensitivity or has_variation:
                        quality = "MARGINAL"
                    else:
                        quality = "POOR"
                    
                    column_results[col] = {
                        'type': 'categorical',
                        'mean_dist': mean_dist,
                        'variation': dist_range,
                        'quality': quality,
                        'has_sensitivity': has_sensitivity,
                        'has_variation': has_variation,
                    }
            
            # Print the table
            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 EMBEDDING QUALITY TABLE")
            logger.info("=" * 80)
            logger.info("")
            
            # Count by type and quality for summary
            num_good = num_marg = num_poor = 0
            cat_good = cat_marg = cat_poor = 0
            
            # Emoji status indicators (each emoji = 2 display columns)
            def mark(ok):
                return "✅" if ok else "❌"
            
            # Quality labels with emojis - pad to account for emoji width (emoji=2 cols)
            # Target: 13 display columns total
            def qual_label(q):
                if q == "GOOD":
                    return "✅ GOOD     "   # emoji(2) + space(1) + GOOD(4) + pad(6) = 13
                elif q == "MARGINAL":
                    return "⚠️MARGINAL  "   # emoji(2) + MARGINAL(8) + pad(3) = 13
                else:
                    return "❌ POOR     "   # emoji(2) + space(1) + POOR(4) + pad(6) = 13
            
            # Numeric columns table
            numeric_results = {k: v for k, v in column_results.items() if v['type'] == 'numeric'}
            if numeric_results:
                logger.info("## Numeric Columns")
                logger.info("")
                logger.info("   METRICS:")
                logger.info("   • Linearity: Pearson correlation between input perturbation % and embedding distance")
                logger.info("     - Measures: Does 2x input change → 2x embedding change? (proportional response)")
                logger.info("     - Check: corr > 0.7 (GOOD), > 0.5 (MARGINAL), else (POOR)")
                logger.info("     - Adjusted by encoder type: METRIC expects high, QUANTIZED expects low (by design)")
                logger.info("")
                logger.info("   • Sensitivity: Mean embedding distance per unit input change (in original units)")
                logger.info("     - Measures: Does the model respond to input changes?")
                logger.info("     - Check: sensitivity > 0.0001 (responds to changes)")
                logger.info("     - Adjusted by encoder type: RELATIONAL may have low marginal sensitivity (expected)")
                logger.info("")
                logger.info("   • Consistency: Coefficient of variation (std_sensitivity / mean_sensitivity)")
                logger.info("     - Measures: Is sensitivity stable across different perturbation sizes?")
                logger.info("     - Check: consistency < 0.5 (stable), < 1.0 (QUANTIZED - more lenient)")
                logger.info("     - Lower = more stable (same sensitivity for 1% vs 10% perturbations)")
                logger.info("")
                logger.info("   ENCODER BEHAVIOR TYPES:")
                logger.info("   • METRIC: Smooth/proportional (linear, zscore, log, etc.) - expects high linearity")
                logger.info("   • QUANTIZED: Discrete/jump (bucket, quantile, rank) - expects low linearity (by design)")
                logger.info("   • SATURATING: Bounded (sigmoid, winsor) - context-dependent")
                logger.info("   • RELATIONAL: Context-dependent (polynomial, frequency) - low marginal sensitivity expected")
                logger.info("   • MIXED: No dominant type - more lenient criteria")
                logger.info("")
                
                max_col_len = max(len(col) for col in numeric_results.keys())
                col_width = max(22, max_col_len)
                
                # Column widths: Col(var) | Behavior(10) | Linearity(16) | Sensitivity(18) | Consistency(18) | Quality(15)
                logger.info(f"┌{'─' * (col_width + 2)}┬────────────┬──────────────────┬────────────────────┬────────────────────┬───────────────┐")
                logger.info(f"│ {'Column':<{col_width}} │ Behavior   │ Linearity        │ Sensitivity        │ Consistency        │ Quality       │")
                logger.info(f"├{'─' * (col_width + 2)}┼────────────┼──────────────────┼────────────────────┼────────────────────┼───────────────┤")
                
                for col, res in sorted(numeric_results.items()):
                    corr = res['correlation']
                    sens = res['mean_sensitivity']
                    cons = res['consistency']
                    behavior = res.get('behavior', 'UNKNOWN')
                    
                    prop_ok = res.get('proportionality_ok', res['is_proportional'])
                    sens_ok = res['has_sensitivity']
                    cons_ok = res['has_consistent']
                    qual = res['quality']
                    
                    # Count for summary
                    if qual == 'GOOD':
                        num_good += 1
                    elif qual == 'MARGINAL':
                        num_marg += 1
                    else:
                        num_poor += 1
                    
                    # Behavior cell: 10 display cols (truncate if needed)
                    behavior_display = behavior[:9] if len(behavior) > 9 else behavior
                    behavior_cell = f"{behavior_display:<10}"
                    
                    # Build each cell: value + emoji (emoji takes 2 display cols)
                    # Linearity cell: 16 display cols total (number + space + emoji + padding)
                    num_str = f"{corr:>8.3f}"
                    lin_cell = f"{num_str} {mark(prop_ok)}".ljust(16)
                    # Sensitivity cell: 18 display cols total
                    num_str = f"{sens:>10.4f}"
                    sens_cell = f"{num_str} {mark(sens_ok)}".ljust(18)
                    # Consistency cell: 18 display cols total
                    num_str = f"{cons:>10.3f}"
                    cons_cell = f"{num_str} {mark(cons_ok)}".ljust(18)
                    
                    logger.info(f"│ {col:<{col_width}} │ {behavior_cell}│ {lin_cell}│ {sens_cell}│ {cons_cell}│ {qual_label(qual)}│")
                
                logger.info(f"└{'─' * (col_width + 2)}┴────────────┴──────────────────┴────────────────────┴────────────────────┴───────────────┘")
                logger.info("")
            
            # Categorical columns table
            categorical_results = {k: v for k, v in column_results.items() if v['type'] == 'categorical'}
            if categorical_results:
                logger.info("## Categorical Columns")
                logger.info("")
                logger.info("   Value Δ = embedding distance when category changes (higher = model responds to changes)")
                logger.info("   Spread  = variation in Δ across different values (higher = distinguishes between values)")
                logger.info("")
                
                max_col_len = max(len(col) for col in categorical_results.keys())
                col_width = max(22, max_col_len)
                
                logger.info(f"┌{'─' * (col_width + 2)}┬────────────────────┬────────────────────┬───────────────┐")
                logger.info(f"│ {'Column':<{col_width}} │ Value Δ (mean)     │ Spread (range)     │ Quality       │")
                logger.info(f"├{'─' * (col_width + 2)}┼────────────────────┼────────────────────┼───────────────┤")
                
                for col, res in sorted(categorical_results.items()):
                    mean_dist = res['mean_dist']
                    var = res['variation']
                    sens_ok = res['has_sensitivity']
                    var_ok = res['has_variation']
                    qual = res['quality']
                    
                    # Count for summary
                    if qual == 'GOOD':
                        cat_good += 1
                    elif qual == 'MARGINAL':
                        cat_marg += 1
                    else:
                        cat_poor += 1
                    
                    # Build cells: 18 display cols each (number + space + emoji + padding)
                    num_str = f"{mean_dist:>10.4f}"
                    val_cell = f"{num_str} {mark(sens_ok)}".ljust(18)
                    num_str = f"{var:>10.4f}"
                    spr_cell = f"{num_str} {mark(var_ok)}".ljust(18)
                    
                    logger.info(f"│ {col:<{col_width}} │ {val_cell}│ {spr_cell}│ {qual_label(qual)}│")
                
                logger.info(f"└{'─' * (col_width + 2)}┴────────────────────┴────────────────────┴───────────────┘")
                logger.info("")
            
            # Summary Statistics table
            logger.info("## Summary Statistics")
            logger.info("")
            total_good = num_good + cat_good
            total_marg = num_marg + cat_marg
            total_poor = num_poor + cat_poor
            
            logger.info("┌─────────────────┬──────────┬─────────────┬─────────┐")
            logger.info("│ Quality Level   │ Numeric  │ Categorical │ Total   │")
            logger.info("├─────────────────┼──────────┼─────────────┼─────────┤")
            logger.info(f"│ ✅ GOOD         │ {num_good:>8} │ {cat_good:>11} │ {total_good:>7} │")
            logger.info(f"│ ⚠️MARGINAL      │ {num_marg:>8} │ {cat_marg:>11} │ {total_marg:>7} │")
            logger.info(f"│ ❌ POOR         │ {num_poor:>8} │ {cat_poor:>11} │ {total_poor:>7} │")
            logger.info("└─────────────────┴──────────┴─────────────┴─────────┘")
            logger.info("=" * 80)
            
            # Record column sensitivity quality check
            if epoch_idx is not None:
                try:
                    from featrix.neural.customer_quality_tracker import QualityCheckName, QualityGrade
                    qt = self.get_quality_tracker(epoch_idx)
                    
                    # Calculate overall column sensitivity grade
                    total_cols = len(column_results)
                    if total_cols > 0:
                        good_pct = (total_good / total_cols) * 100
                        poor_pct = (total_poor / total_cols) * 100
                        
                        if good_pct >= 70 and poor_pct < 10:
                            col_grade = QualityGrade.A
                        elif good_pct >= 50 and poor_pct < 20:
                            col_grade = QualityGrade.B
                        elif good_pct >= 30 and poor_pct < 40:
                            col_grade = QualityGrade.C
                        elif good_pct >= 20:
                            col_grade = QualityGrade.D
                        else:
                            col_grade = QualityGrade.F
                    else:
                        col_grade = QualityGrade.F
                    
                    qt.record_check(
                        name=QualityCheckName.COLUMN_SENSITIVITY,
                        graded_score=col_grade,
                        metadata={
                            "total_columns": total_cols,
                            "good_columns": total_good,
                            "marginal_columns": total_marg,
                            "poor_columns": total_poor,
                            "good_percentage": (total_good / total_cols * 100) if total_cols > 0 else 0,
                            "numeric_good": num_good,
                            "categorical_good": cat_good,
                        }
                    )
                except Exception as e:
                    logger.debug(f"   Failed to record column sensitivity check: {e}")
            
            self.encoder.train()
            
        except Exception as e:
            logger.warning(f"   Quality check failed: {e}")
            traceback.print_exc()
    
    def _log_marginal_loss_breakdown(self, loss_dict, epoch_idx, batch_idx):
        """
        Log detailed breakdown of marginal loss components and per-column contributions.
        
        The marginal loss has 4 components:
        - full_1/full_2: Predictions using d_model-dimensional encodings with 2 different random masks
        - short_1/short_2: Predictions using 3D encodings with the same 2 random masks
        
        Each mask randomly hides some columns and tries to predict them from the rest.
        Using 2 different masks per batch doubles the training signal.
        
        Args:
            loss_dict: The loss dictionary from compute_total_loss
            epoch_idx: Current epoch index
            batch_idx: Current batch index
        """
        try:
            marginal_loss = loss_dict.get('marginal_loss', {})
            
            # Get the four marginal loss components
            full_1 = marginal_loss.get('marginal_loss_full_1', {})
            full_2 = marginal_loss.get('marginal_loss_full_2', {})
            short_1 = marginal_loss.get('marginal_loss_short_1', {})
            short_2 = marginal_loss.get('marginal_loss_short_2', {})
            
            # Get totals
            full_1_total = full_1.get('total', 0.0)
            full_2_total = full_2.get('total', 0.0)
            short_1_total = short_1.get('total', 0.0)
            short_2_total = short_2.get('total', 0.0)
            marginal_total = marginal_loss.get('total', 0.0)
            
            # Get per-column losses
            full_1_cols = full_1.get('cols', {})
            full_2_cols = full_2.get('cols', {})
            short_1_cols = short_1.get('cols', {})
            short_2_cols = short_2.get('cols', {})
            
            # Log component breakdown
            # NOTE: mask_1 and mask_2 are two different random column masking patterns applied to the same batch
            # This gives us 2 different prediction tasks per batch, increasing training signal
            logger.debug(f"📊 [batch={batch_idx}] MARGINAL LOSS BREAKDOWN:")
            logger.info(f"   Total Marginal: {marginal_total:.4f}")
            logger.info(f"   └─ Full Mask 1:  {full_1_total:.4f} ({full_1_total/marginal_total*100:.1f}%) [d_model encodings, mask pattern 1]")
            logger.info(f"   └─ Full Mask 2:  {full_2_total:.4f} ({full_2_total/marginal_total*100:.1f}%) [d_model encodings, mask pattern 2]")
            logger.info(f"   └─ Short Mask 1: {short_1_total:.4f} ({short_1_total/marginal_total*100:.1f}%) [3D encodings, mask pattern 1]")
            logger.info(f"   └─ Short Mask 2: {short_2_total:.4f} ({short_2_total/marginal_total*100:.1f}%) [3D encodings, mask pattern 2]")
            
            # Aggregate column losses across all masks
            all_cols = set(full_1_cols.keys()) | set(full_2_cols.keys()) | set(short_1_cols.keys()) | set(short_2_cols.keys())
            column_losses = {}
            column_counts = {}  # Track how many masks each column appeared in
            
            for col in all_cols:
                losses = []
                if col in full_1_cols:
                    losses.append(full_1_cols[col])
                if col in full_2_cols:
                    losses.append(full_2_cols[col])
                if col in short_1_cols:
                    losses.append(short_1_cols[col])
                if col in short_2_cols:
                    losses.append(short_2_cols[col])
                
                if losses:
                    column_losses[col] = sum(losses) / len(losses)
                    column_counts[col] = len(losses)
            
            if column_losses:
                # Sort by average loss
                sorted_cols = sorted(column_losses.items(), key=lambda x: x[1], reverse=True)
                
                # Calculate statistics
                loss_values = np.array(list(column_losses.values()))
                mean_loss = loss_values.mean()
                std_loss = loss_values.std()
                median_loss = np.median(loss_values)
                
                logger.info(f"   Column Loss Stats: mean={mean_loss:.4f}, std={std_loss:.4f}, median={median_loss:.4f}")
                
                # COLLAPSE DIAGNOSTICS: Print alongside column loss std to confirm real collapse vs metric artifact
                collapse_diagnostics = loss_dict.get('collapse_diagnostics', {})
                if collapse_diagnostics and 'error' not in collapse_diagnostics:
                    logger.info(f"   🔍 Collapse Diagnostics (to confirm real collapse vs metric artifact):")
                    
                    # 1. Joint embedding norms and std
                    if 'joint_embedding' in collapse_diagnostics:
                        je = collapse_diagnostics['joint_embedding']
                        logger.info(f"      Joint embedding ||norm||: mean={je['norm_mean']:.4f}, std={je['norm_std']:.4f}")
                        logger.info(f"      Joint embedding std/dim: mean={je['std_per_dim_mean']:.4f}, std={je['std_per_dim_std']:.4f}")
                    
                    # 2. Mask entropy
                    if 'mask_entropy' in collapse_diagnostics:
                        me = collapse_diagnostics['mask_entropy']
                        logger.info(f"      Mask entropy: mask1={me['mask_1']:.4f}, mask2={me['mask_2']:.4f}, mean={me['mean']:.4f}")
                        # High entropy (>0.6) = uniform masking (good), low entropy (<0.3) = biased masking (bad)
                        if me['mean'] < 0.3:
                            logger.warning(f"      ⚠️  LOW mask entropy ({me['mean']:.4f}) - masking may be biased!")
                    
                    # 3. Logit distribution per column
                    if 'logit_distribution' in collapse_diagnostics:
                        ld = collapse_diagnostics['logit_distribution']
                        logger.info(f"      Logit distribution (sample of {len(ld)} columns):")
                        for col_name, stats in list(ld.items())[:3]:  # Show first 3
                            logger.info(f"         {col_name}: diag={stats['diag_mean']:.2f}±{stats['diag_std']:.2f}, "
                                      f"off_diag={stats['off_diag_mean']:.2f}±{stats['off_diag_std']:.2f}, "
                                      f"separation={stats['separation']:.2f}")
                        # Low separation (<1.0) = predictions collapsing, high separation (>3.0) = good differentiation
                        avg_separation = np.mean([s['separation'] for s in ld.values()]) if ld else 0.0
                        # Only warn after epoch 5 - early training naturally has low separation
                        if epoch_idx >= 5 and avg_separation < 1.0:
                            logger.warning(f"      ⚠️  LOW logit separation ({avg_separation:.2f}) - predictions may be collapsing!")
                    
                    # 4. Ranking metrics (Positive Rank, Margin, AUC)
                    if 'ranking_metrics' in collapse_diagnostics:
                        rm = collapse_diagnostics['ranking_metrics']
                        logger.info(f"      📊 Ranking Metrics (InfoNCE-aligned):")
                        logger.info(f"         Positive Rank: mean={rm['positive_rank_mean']:.2f}, median={rm['positive_rank_median']:.1f}")
                        logger.info(f"         Recall@1: {rm['recall_at_1']:.1%}, Recall@5: {rm['recall_at_5']:.1%}")
                        logger.info(f"         Margin: mean={rm['margin_mean']:.3f}, % positive={rm['margin_pct_positive']:.1%}")
                        logger.info(f"         AUC: {rm['auc']:.3f}")
                        
                        # Warning logic based on user's recommendations
                        # Get batch_size from loss_dict if available
                        batch_size_for_warning = loss_dict.get('batch_size', 128)  # Default to 128 if not available
                        random_recall_1 = 1.0 / batch_size_for_warning if batch_size_for_warning > 0 else 0.0
                        warmup_epochs = 10
                        curriculum_phase_epochs = 25
                        
                        if epoch_idx >= warmup_epochs:
                            if rm['recall_at_1'] < random_recall_1 * 2:
                                logger.warning(f"      ⚠️  Recall@1 ({rm['recall_at_1']:.1%}) < 2× random ({random_recall_1*2:.1%}) after warmup")
                        
                        if epoch_idx >= warmup_epochs:
                            if rm['margin_pct_positive'] < 0.05:
                                logger.warning(f"      ⚠️  Only {rm['margin_pct_positive']:.1%} of rows have positive margin after warmup")
                        
                        if epoch_idx >= curriculum_phase_epochs:
                            if rm['auc'] < 0.55:
                                logger.warning(f"      ⚠️  AUC ({rm['auc']:.3f}) < 0.55 after curriculum phase")
                    
                    # Summary: If all metrics are flat, it's real collapse
                    all_flat = (
                        std_loss < 0.005 and
                        'joint_embedding' in collapse_diagnostics and
                        collapse_diagnostics['joint_embedding']['norm_std'] < 0.01 and
                        collapse_diagnostics['joint_embedding']['std_per_dim_std'] < 0.01
                    )
                    if all_flat:
                        logger.warning(f"      🚨 ALL METRICS FLAT - REAL COLLAPSE CONFIRMED (not just metric artifact)")
                    elif std_loss < 0.005:
                        logger.info(f"      ⚠️  Column loss std is low, but other metrics show structure - may be metric artifact")
                
                # Show top 5 hardest columns
                logger.info(f"   Top 5 Hardest Columns:")
                for i, (col_name, avg_loss) in enumerate(sorted_cols[:5], 1):
                    count = column_counts[col_name]
                    logger.info(f"      {i}. {col_name}: {avg_loss:.4f} (in {count}/4 masks)")
                
                # Show bottom 3 easiest columns
                if len(sorted_cols) > 3:
                    logger.info(f"   Bottom 3 Easiest Columns:")
                    for i, (col_name, avg_loss) in enumerate(sorted_cols[-3:], 1):
                        count = column_counts[col_name]
                        logger.info(f"      {i}. {col_name}: {avg_loss:.4f} (in {count}/4 masks)")
                
                # Log adaptive scalar encoder strategy weights
                logger.info(f"   📊 Adaptive Scalar Transform Strategies:")
                from featrix.neural.scalar_codec import AdaptiveScalarEncoder
                adaptive_count = 0
                
                # Collect all weights first
                strategy_data = []
                for col_name, encoder in self.encoder.column_encoder.encoders.items():
                    try:
                        if isinstance(encoder, AdaptiveScalarEncoder):
                            weights = encoder.get_strategy_weights()
                            strategy_data.append((col_name, weights))
                            adaptive_count += 1
                    except Exception as e:
                        logger.warning(f"      Skipped {col_name}: {type(e).__name__}: {e}")
                        logger.info(f"      Full traceback:\n{traceback.format_exc()}")
                
                if adaptive_count == 0:
                    logger.info(f"      No AdaptiveScalarEncoder columns found (total encoders: {len(self.encoder.column_encoder.encoders)})")
                    encoder_types = {}
                    for col_name, encoder in self.encoder.column_encoder.encoders.items():
                        encoder_type = type(encoder).__name__
                        encoder_types[encoder_type] = encoder_types.get(encoder_type, 0) + 1
                    logger.info(f"      Encoder types: {encoder_types}")
                else:
                    # All 20 strategies with 3-letter codes
                    strategy_order = [
                        ('linear', 'LIN'), ('log', 'LOG'), ('robust', 'ROB'), ('rank', 'RAN'), 
                        ('periodic', 'PER'), ('bucket', 'BUC'), ('is_positive', 'POS'), 
                        ('is_negative', 'NEG'), ('is_outlier', 'OUT'), ('zscore', 'ZSC'),
                        ('minmax', 'MIN'), ('quantile', 'QUA'), ('yeojohnson', 'YEO'),
                        ('winsor', 'WIN'), ('sigmoid', 'SIG'), ('inverse', 'INV'),
                        ('polynomial', 'POL'), ('frequency', 'FRE'), ('target_bin', 'TAR'),
                        ('clipped_log', 'CLI')
                    ]
                    
                    # Log legend/key the first time (use class-level flag)
                    if not hasattr(EmbeddingSpace, '_scalar_strategy_legend_logged'):
                        logger.info("      📋 Scalar Strategy Codes:")
                        logger.info("         Original: LIN=Linear, LOG=Log, ROB=Robust, RAN=Rank, PER=Periodic, BUC=Bucket, POS=IsPositive, NEG=IsNegative, OUT=IsOutlier")
                        logger.info("         New: ZSC=ZScore, MIN=MinMax, QUA=Quantile, YEO=YeoJohnson, WIN=Winsor, SIG=Sigmoid, INV=Inverse, POL=Polynomial, FRE=Frequency, TAR=TargetBin, CLI=ClippedLog")
                        EmbeddingSpace._scalar_strategy_legend_logged = True
                    
                    # ANSI color codes (used throughout this section)
                    YELLOW = "\033[33m"
                    GRAY = "\033[90m"
                    RESET = "\033[0m"
                    
                    # Format table header with 3-letter codes
                    header_parts = [f"{'Column':<45s}"]
                    for strategy_name, code in strategy_order:
                        header_parts.append(f"{code:>5s}")
                    header_parts.append("Dominant")
                    logger.info("      " + "   ".join(header_parts))
                    logger.info(f"      " + "-" * (45 + len(strategy_order) * 8 + 20))
                    
                    for col_name, weights in strategy_data:
                        # Check if weights contains an error
                        if not isinstance(weights, dict) or 'error' in weights:
                            display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                            error_msg = weights.get('error', 'invalid weights') if isinstance(weights, dict) else 'invalid weights'
                            logger.info(f"      {display_name:<45s} ERROR: {error_msg}")
                            continue
                        
                        # Filter out non-numeric values
                        numeric_weights = {k: v for k, v in weights.items() if isinstance(v, (int, float))}
                        if not numeric_weights:
                            display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                            logger.info(f"      {display_name:<45s} ERROR: No numeric weights available")
                            continue
                        
                        # Get encoder to check which strategies are active
                        encoder = None
                        active_weights = {}
                        total_active_weight = 0.0
                        if col_name in self.encoder.column_encoder.encoders:
                            encoder = self.encoder.column_encoder.encoders[col_name]
                        
                        # Calculate sum of active (non-pruned) strategy weights
                        for strategy_name, code in strategy_order:
                            weight = numeric_weights.get(strategy_name, 0.0)
                            is_active = True
                            if encoder and isinstance(encoder, AdaptiveScalarEncoder):
                                strategy_idx = next((i for i, (name, _) in enumerate(strategy_order) if name == strategy_name), -1)
                                if strategy_idx >= 0 and encoder._strategy_mask[strategy_idx].item() < 0.5:
                                    is_active = False
                            
                            if is_active:
                                active_weights[strategy_name] = weight
                                total_active_weight += weight
                        
                        # Normalize active weights to sum to 100%
                        if total_active_weight > 0:
                            normalized_weights = {name: w / total_active_weight for name, w in active_weights.items()}
                        else:
                            normalized_weights = active_weights
                        
                        # Determine dominant strategy from normalized weights
                        dominant_strategy_name = None
                        if normalized_weights:
                            dominant = max(normalized_weights.items(), key=lambda x: x[1])
                            dominant_strategy_name = dominant[0]
                            # Map to 3-letter code
                            dominant_code = next((code for name, code in strategy_order if name == dominant[0]), dominant[0][:3].upper())
                            dominant_str = f"{dominant_code} ({dominant[1]:.0%})"
                        else:
                            dominant_str = "N/A"
                        
                        # Truncate column name if too long
                        display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                        
                        # Build row with all strategies
                        row_parts = [f"{display_name:<45s}"]
                        for strategy_name, code in strategy_order:
                            # Check if strategy is pruned (weight is 0 and not in active strategies)
                            weight = weights.get(strategy_name, 0.0)
                            is_active = True
                            if encoder and isinstance(encoder, AdaptiveScalarEncoder):
                                strategy_idx = next((i for i, (name, _) in enumerate(strategy_order) if name == strategy_name), -1)
                                if strategy_idx >= 0 and encoder._strategy_mask[strategy_idx].item() < 0.5:
                                    is_active = False
                            
                            if not is_active:
                                row_parts.append(f"{'-':>5s}")  # Show "-" for pruned strategies
                            else:
                                # Use normalized weight (percentage of active strategies only)
                                normalized_weight = normalized_weights.get(strategy_name, 0.0)
                                weight_str = f"{normalized_weight:>5.1%}"
                                # Color: yellow for dominant, gray for others
                                if strategy_name == dominant_strategy_name:
                                    row_parts.append(f"{YELLOW}{weight_str}{RESET}")
                                else:
                                    row_parts.append(f"{GRAY}{weight_str}{RESET}")
                        # Dominant column also gets yellow
                        row_parts.append(f"{YELLOW}{dominant_str}{RESET}")
                        logger.info("      " + "   ".join(row_parts))
                    
                    # Calculate mean and std for each strategy across all columns (only active strategies)
                    strategy_stats = {}
                    for strategy_name, code in strategy_order:
                        # Only include weights from columns where this strategy is active (not pruned)
                        values = []
                        for col_name, weights in strategy_data:
                            # Skip error dictionaries and non-numeric weights
                            if not isinstance(weights, dict) or 'error' in weights:
                                continue
                            numeric_weights = {k: v for k, v in weights.items() if isinstance(v, (int, float))}
                            if not numeric_weights:
                                continue
                            
                            encoder = None
                            if col_name in self.encoder.column_encoder.encoders:
                                encoder = self.encoder.column_encoder.encoders[col_name]
                            if encoder and isinstance(encoder, AdaptiveScalarEncoder):
                                strategy_idx = next((i for i, (name, _) in enumerate(strategy_order) if name == strategy_name), -1)
                                if strategy_idx >= 0 and encoder._strategy_mask[strategy_idx].item() >= 0.5:
                                    values.append(numeric_weights.get(strategy_name, 0.0))
                            else:
                                values.append(numeric_weights.get(strategy_name, 0.0))
                        
                        if values:
                            strategy_stats[strategy_name] = {
                                'mean': np.mean(values),
                                'std': np.std(values),
                                'code': code,
                                'active_count': len(values)
                            }
                        else:
                            strategy_stats[strategy_name] = {
                                'mean': 0.0,
                                'std': 0.0,
                                'code': code,
                                'active_count': 0
                            }
                    
                    # logger.info(f"      " + "-" * (45 + len(strategy_order) * 8 + 20))
                    # logger.info(f"      Strategy Summary (mean ± std across active columns):")
                    # summary_parts = []
                    # for strategy_name, code in strategy_order:
                    #     stats = strategy_stats[strategy_name]
                    #     if stats['active_count'] > 0:
                    #         summary_parts.append(f"{code}: {stats['mean']:4.1%}±{stats['std']:3.1%}({stats['active_count']})")
                    #     else:
                    #         summary_parts.append(f"{code}: PRUNED")
                    # logger.info("      " + "  ".join(summary_parts))
                    
                    # Show simplified summary: top 3 and bottom 3 strategies
                    logger.info(f"      " + "-" * (45 + len(strategy_order) * 8 + 20))
                    logger.info(f"      Strategy Performance Summary:")
                    
                    # Sort strategies by mean weight (best to worst)
                    sorted_strategies = sorted(
                        [(name, stats) for name, stats in strategy_stats.items() if stats['active_count'] > 0],
                        key=lambda x: x[1]['mean'],
                        reverse=True
                    )
                    
                    if sorted_strategies:
                        logger.info(f"      Top 3 strategies (highest weights):")
                        for i, (strategy_name, stats) in enumerate(sorted_strategies[:3], 1):
                            code = next((code for name, code in strategy_order if name == strategy_name), strategy_name[:3].upper())
                            stat_str = f"{code}: {stats['mean']:4.1%}±{stats['std']:3.1%} ({stats['active_count']} columns)"
                            # Color: yellow for #1, gray for others
                            if i == 1:
                                logger.info(f"         {i}. {YELLOW}{stat_str}{RESET}")
                            else:
                                logger.info(f"         {i}. {GRAY}{stat_str}{RESET}")
                        
                        if len(sorted_strategies) > 3:
                            logger.info(f"      Bottom 3 strategies (lowest weights, candidates for pruning):")
                            for i, (strategy_name, stats) in enumerate(sorted_strategies[-3:], 1):
                                code = next((code for name, code in strategy_order if name == strategy_name), strategy_name[:3].upper())
                                stat_str = f"{code}: {stats['mean']:4.1%}±{stats['std']:3.1%} ({stats['active_count']} columns)"
                                # All bottom strategies in gray
                                logger.info(f"         {i}. {GRAY}{stat_str}{RESET}")
                    
                    # Count pruned strategies
                    pruned_count = sum(1 for stats in strategy_stats.values() if stats['active_count'] == 0)
                    if pruned_count > 0:
                        logger.info(f"      Pruned strategies: {pruned_count}/{len(strategy_order)}")
                    
                    logger.info(f"      Total: {adaptive_count} AdaptiveScalarEncoder columns")
                    logger.info(f"      Note: Pruning based on learned weights (softmax attention), not direct performance metrics")
                    
                    # Log dual-path gate values if using dual-path mode
                    dual_path_info = []
                    for col_name, encoder in self.encoder.column_encoder.encoders.items():
                        if isinstance(encoder, AdaptiveScalarEncoder) and hasattr(encoder, '_use_dual_path') and encoder._use_dual_path:
                            gate_info = encoder.get_dual_path_info()
                            dual_path_info.append((col_name, gate_info))
                    
                    if dual_path_info:
                        logger.info(f"")
                        logger.info(f"   🔀 Dual-Path Scalar Mode (Continuous vs Binned):")
                        for col_name, info in dual_path_info:
                            gate_val = info['gate_value']
                            # Interpret gate: 1.0 = pure continuous, 0.0 = pure binned
                            if gate_val > 0.7:
                                mode_str = f"CONTINUOUS ({gate_val:.1%})"
                            elif gate_val < 0.3:
                                mode_str = f"BINNED ({1-gate_val:.1%})"
                            else:
                                mode_str = f"MIXED (cont:{gate_val:.0%}/bin:{1-gate_val:.0%})"
                            display_name = col_name[:40] + "..." if len(col_name) > 40 else col_name
                            logger.info(f"      {display_name:<45s} gate={gate_val:.3f} → {mode_str}")
                        
                        avg_gate = np.mean([info['gate_value'] for _, info in dual_path_info])
                        if avg_gate > 0.6:
                            summary = "📈 Model prefers CONTINUOUS path (smooth transforms)"
                        elif avg_gate < 0.4:
                            summary = "📊 Model prefers BINNED path (discrete buckets)"
                        else:
                            summary = "⚖️  Model uses BALANCED mix of both paths"
                        logger.info(f"      Average gate: {avg_gate:.3f} - {summary}")
                
                # Log adaptive string encoder compression strategy weights
                logger.info(f"   📊 Adaptive String Compression Strategies:")
                from featrix.neural.string_codec import StringEncoder
                string_adaptive_count = 0
                
                # Collect all string encoder weights first
                string_strategy_data = []
                for col_name, encoder in self.encoder.column_encoder.encoders.items():
                    try:
                        if isinstance(encoder, StringEncoder) and hasattr(encoder, 'strategy_logits'):
                            # Get strategy weights (softmax of logits)
                            # torch is already imported at module level
                            weights_tensor = torch.softmax(encoder.strategy_logits, dim=0)
                            weights_list = weights_tensor.detach().cpu().tolist()
                            
                            # Map to strategy names
                            strategy_names = [name for name, _ in encoder.compression_levels]
                            weights_dict = dict(zip(strategy_names, weights_list))
                            
                            string_strategy_data.append((col_name, weights_dict))
                            string_adaptive_count += 1
                    except Exception as e:
                        logger.warning(f"      Skipped {col_name}: {type(e).__name__}: {e}")
                        logger.info(f"      Full traceback:\n{traceback.format_exc()}")
                
                if string_adaptive_count == 0:
                    logger.info(f"      No AdaptiveStringEncoder columns found")
                else:
                    # String strategies with 3-letter codes
                    string_strategy_order = [
                        ('ZERO', 'ZER'), ('DELIMITER', 'DEL'), ('AGGRESSIVE', 'AGG'),
                        ('MODERATE', 'MOD'), ('STANDARD', 'STA')
                    ]
                    
                    # Log legend/key the first time
                    if not hasattr(EmbeddingSpace, '_string_strategy_legend_logged'):
                        logger.info("      📋 String Strategy Codes: ZER=Zero, DEL=Delimiter, AGG=Aggressive, MOD=Moderate, STA=Standard")
                        EmbeddingSpace._string_strategy_legend_logged = True
                    
                    # ANSI color codes (used throughout this section)
                    YELLOW = "\033[33m"
                    GRAY = "\033[90m"
                    RESET = "\033[0m"
                    
                    # Format table header with 3-letter codes
                    header_parts = [f"{'Column':<45s}"]
                    for strategy_name, code in string_strategy_order:
                        header_parts.append(f"{code:>5s}")
                    header_parts.append("Dominant")
                    logger.info("      " + "   ".join(header_parts))
                    logger.info(f"      " + "-" * (45 + len(string_strategy_order) * 8 + 20))
                    
                    # Print each column's strategy distribution
                    for col_name, weights in string_strategy_data:
                        # Filter out non-numeric values
                        numeric_weights = {k: v for k, v in weights.items() if isinstance(v, (int, float))}
                        if not numeric_weights:
                            display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                            logger.info(f"      {display_name:<45s} ERROR: No numeric weights available")
                            continue
                        
                        # Find dominant strategy
                        dominant = max(numeric_weights.items(), key=lambda x: x[1])
                        dominant_strategy_name = dominant[0]
                        # Map to 3-letter code
                        dominant_code = next((code for name, code in string_strategy_order if name == dominant[0]), dominant[0][:3].upper())
                        dominant_str = f"{dominant_code} ({dominant[1]:.0%})"
                        
                        # Truncate column name if too long
                        display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                        
                        # Build row with all strategies
                        row_parts = [f"{display_name:<45s}"]
                        for strategy_name, _ in string_strategy_order:
                            weight = numeric_weights.get(strategy_name, 0.0)
                            weight_str = f"{weight:>5.1%}"
                            # Color: yellow for dominant, gray for others
                            if strategy_name == dominant_strategy_name:
                                row_parts.append(f"{YELLOW}{weight_str}{RESET}")
                            else:
                                row_parts.append(f"{GRAY}{weight_str}{RESET}")
                        # Dominant column also gets yellow
                        row_parts.append(f"{YELLOW}{dominant_str}{RESET}")
                        logger.info("      " + "   ".join(row_parts))
                    
                    # Calculate mean and std for each strategy across all columns
                    string_strategy_stats = {}
                    for strategy_name, code in string_strategy_order:
                        values = []
                        for _, weights in string_strategy_data:
                            # Filter out non-numeric values
                            if isinstance(weights, dict):
                                numeric_weights = {k: v for k, v in weights.items() if isinstance(v, (int, float))}
                                if numeric_weights:
                                    values.append(numeric_weights.get(strategy_name, 0.0))
                        string_strategy_stats[strategy_name] = {
                            'mean': np.mean(values) if values else 0.0,
                            'std': np.std(values) if values else 0.0,
                            'code': code
                        }
                    
                    logger.info(f"      " + "-" * (45 + len(string_strategy_order) * 8 + 20))
                    logger.info(f"      Strategy Summary (mean ± std across {string_adaptive_count} columns):")
                    summary_parts = []
                    # Find dominant strategy by mean weight
                    dominant_summary = max(string_strategy_stats.items(), key=lambda x: x[1]['mean'])
                    for strategy_name, code in string_strategy_order:
                        stats = string_strategy_stats[strategy_name]
                        stat_str = f"{code}: {stats['mean']:4.1%}±{stats['std']:3.1%}"
                        # Color: yellow for dominant, gray for others
                        if strategy_name == dominant_summary[0]:
                            summary_parts.append(f"{YELLOW}{stat_str}{RESET}")
                        else:
                            summary_parts.append(f"{GRAY}{stat_str}{RESET}")
                    logger.info("      " + "  ".join(summary_parts))
                    
                    # Add mean and std as bottom rows in the table
                    logger.info(f"      " + "-" * (45 + len(string_strategy_order) * 8 + 20))
                    mean_parts = [f"{'MEAN (across all columns)':<45s}"]
                    for strategy_name, _ in string_strategy_order:
                        mean_val = string_strategy_stats[strategy_name]['mean']
                        mean_str = f"{mean_val:>5.1%}"
                        # Color: yellow for dominant, gray for others
                        if strategy_name == dominant_summary[0]:
                            mean_parts.append(f"{YELLOW}{mean_str}{RESET}")
                        else:
                            mean_parts.append(f"{GRAY}{mean_str}{RESET}")
                    logger.info("      " + "   ".join(mean_parts))
                    
                    std_parts = [f"{'STD (variation between columns)':<45s}"]
                    for strategy_name, _ in string_strategy_order:
                        std_val = string_strategy_stats[strategy_name]['std']
                        std_str = f"{std_val:>5.1%}"
                        # All std values in gray
                        std_parts.append(f"{GRAY}{std_str}{RESET}")
                    logger.info("      " + "   ".join(std_parts))
                    logger.info(f"      Total: {string_adaptive_count} AdaptiveStringEncoder columns")
                
                # Log adaptive set encoder mixture weights (learned vs semantic)
                logger.info(f"   📊 Adaptive Set Encoder Mixtures (Learned vs Semantic):")
                from featrix.neural.set_codec import SetEncoder
                set_adaptive_count = 0
                set_total_count = 0
                
                # Track initial mixture weights for delta reporting
                if not hasattr(self, '_initial_set_mixture_weights'):
                    self._initial_set_mixture_weights = {}
                
                # Collect all set encoder mixture weights (show ALL SetEncoder columns)
                set_mixture_data = []
                set_mixture_deltas = {}  # Track deltas for reporting
                set_encoder_features = {}  # Track features per encoder (ordinal, per-member, etc.)
                set_per_member_stats = {}  # Track per-member weight diversity
                for col_name, encoder in self.encoder.column_encoder.encoders.items():
                    try:
                        if isinstance(encoder, SetEncoder):
                            set_total_count += 1
                            if encoder.use_semantic_mixture:
                                # FIXED: Use get_actual_mixture_weight() to show REAL weights
                                # Old code used raw sigmoid(mixture_logit) which ignored temperature
                                # and curriculum, showing 37.8% when actual was 8.5%
                                if hasattr(encoder, 'get_actual_mixture_weight'):
                                    mixture_weight, semantic_weight, raw_logit, temperature, epoch_progress = encoder.get_actual_mixture_weight()
                                else:
                                    # Fallback for old encoder versions
                                    mixture_weight = torch.sigmoid(encoder.mixture_logit).item()
                                    semantic_weight = 1 - mixture_weight
                                
                                # Save initial weight on first pass
                                if col_name not in self._initial_set_mixture_weights:
                                    self._initial_set_mixture_weights[col_name] = mixture_weight
                                    set_mixture_deltas[col_name] = 0.0  # No delta yet
                                else:
                                    # Calculate delta from initial
                                    delta = mixture_weight - self._initial_set_mixture_weights[col_name]
                                    set_mixture_deltas[col_name] = delta
                                
                                set_mixture_data.append((col_name, mixture_weight, semantic_weight))
                                set_adaptive_count += 1
                                
                                # Collect feature flags for this encoder
                                features = []
                                if getattr(encoder, 'is_ordinal', False):
                                    features.append('ORD')
                                if getattr(encoder, 'use_gating_network', False):
                                    features.append('GATE')  # Gating network (preferred)
                                elif getattr(encoder, 'use_per_member_mixture', False):
                                    features.append('PM')  # Per-member (deprecated)
                                    # Collect per-member weight diversity stats (using actual temperature)
                                    if hasattr(encoder, 'mixture_logits') and encoder.mixture_logits is not None:
                                        # Get temperature for accurate weight calculation
                                        if hasattr(encoder, 'get_actual_mixture_weight'):
                                            _, _, _, temp, _ = encoder.get_actual_mixture_weight()
                                        else:
                                            temp = 1.0
                                        # Apply temperature scaling to per-member logits
                                        pm_weights = torch.sigmoid(encoder.mixture_logits / temp).detach()
                                        set_per_member_stats[col_name] = {
                                            'min': pm_weights.min().item(),
                                            'max': pm_weights.max().item(),
                                            'std': pm_weights.std().item(),
                                            'n_members': len(pm_weights),
                                            'temperature': temp
                                        }
                                if getattr(encoder, 'use_curriculum_learning', False):
                                    features.append('CU')  # Curriculum
                                if getattr(encoder, 'use_temperature_annealing', False):
                                    features.append('TA')  # Temp annealing
                                set_encoder_features[col_name] = features
                            else:
                                # SetEncoder without semantic mixture - show as learned-only
                                set_mixture_data.append((col_name, 1.0, 0.0))  # 100% learned, 0% semantic
                                set_adaptive_count += 1
                                set_encoder_features[col_name] = []
                    except Exception as e:
                        logger.warning(f"      Skipped {col_name}: {type(e).__name__}: {e}")
                        logger.info(f"      Full traceback:\n{traceback.format_exc()}")
                
                # Log total count for debugging
                has_deltas = len(set_mixture_deltas) > 0 and any(abs(d) > 0.001 for d in set_mixture_deltas.values())
                if has_deltas:
                    logger.info(f"      Found {set_total_count} total SetEncoder columns, {set_adaptive_count} included in table (showing deltas from initial)")
                else:
                    logger.info(f"      Found {set_total_count} total SetEncoder columns, {set_adaptive_count} included in table")
                
                if set_adaptive_count == 0:
                    if set_total_count > 0:
                        logger.info(f"      Found {set_total_count} SetEncoder columns, but none have semantic mixture enabled")
                        logger.info(f"      (Semantic mixture requires: use_semantic_set_initialization=True, string_cache available, and member_names)")
                    else:
                        logger.info(f"      No SetEncoder columns found")
                else:
                    # Set strategies with 3-letter codes
                    set_strategy_order = [('Learned', 'LRN'), ('Semantic', 'SEM')]
                    
                    # Log legend/key the first time
                    if not hasattr(EmbeddingSpace, '_set_strategy_legend_logged'):
                        logger.info("      📋 Set Strategy Codes:")
                        logger.info("         LRN = Learned embeddings (trained from data, captures column-specific patterns)")
                        logger.info("         SEM = Semantic embeddings (BERT-based, captures general language meaning)")
                        logger.info("         Feature flags: ORD=ordinal, PM=per-member-mix, CU=curriculum, TA=temp-anneal")
                        EmbeddingSpace._set_strategy_legend_logged = True
                    
                    # ANSI color codes (used throughout this section)
                    YELLOW = "\033[33m"
                    GRAY = "\033[90m"
                    GREEN = "\033[32m"
                    RED = "\033[31m"
                    CYAN = "\033[36m"
                    RESET = "\033[0m"
                    
                    # Format table header with 3-letter codes + delta column if we have movement
                    header_parts = [f"{'Column':<45s}"]
                    for strategy_name, code in set_strategy_order:
                        header_parts.append(f"{code:>6s}")
                    if has_deltas:
                        header_parts.append(f"{'Δ':>8s}")  # Delta from initial
                    logger.info("      " + " ".join(header_parts))
                    
                    # Calculate separator width dynamically
                    sep_width = 45 + len(set_strategy_order) * 8 + 20
                    if has_deltas:
                        sep_width += 10  # Add space for delta column
                    logger.info(f"      " + "-" * sep_width)
                    
                    # Print each column's mixture distribution (show ALL columns, no limit)
                    for col_name, learned_weight, semantic_weight in set_mixture_data:
                        # Validate weights are numeric
                        if not isinstance(learned_weight, (int, float)) or not isinstance(semantic_weight, (int, float)):
                            display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                            logger.info(f"      {display_name:<45s} ERROR: Invalid weight types")
                            continue
                        
                        # Determine dominant strategy
                        if learned_weight > semantic_weight:
                            dominant_strategy = 'Learned'
                            dominant_str = f"LRN ({learned_weight:.0%})"
                        else:
                            dominant_strategy = 'Semantic'
                            dominant_str = f"SEM ({semantic_weight:.0%})"
                        
                        # Truncate column name if too long
                        display_name = col_name[:42] + "..." if len(col_name) > 42 else col_name
                        
                        # Build row with all strategies - FIXED WIDTH FOR ALIGNMENT
                        # Format: Column(45) LRN(6) SEM(6) Delta(8)
                        
                        # Color: yellow for dominant, gray for others
                        learned_str = f"{learned_weight:>6.1%}"
                        semantic_str = f"{semantic_weight:>6.1%}"
                        if dominant_strategy == 'Learned':
                            lrn_colored = f"{YELLOW}{learned_str}{RESET}"
                            sem_colored = f"{GRAY}{semantic_str}{RESET}"
                        else:
                            lrn_colored = f"{GRAY}{learned_str}{RESET}"
                            sem_colored = f"{YELLOW}{semantic_str}{RESET}"
                        
                        # Add delta column if we're tracking movement
                        delta_str = ""
                        if has_deltas and col_name in set_mixture_deltas:
                            delta = set_mixture_deltas[col_name]
                            # Color: green if moving toward LRN, cyan if toward SEM, gray if stable
                            if abs(delta) < 0.001:
                                delta_str = f" {GRAY}    -- {RESET}"  # No movement
                            else:
                                delta_pct = delta * 100  # Convert to percentage points
                                if delta > 0:
                                    # Moving toward learned (positive)
                                    delta_str = f" {GREEN}{delta_pct:>+6.1f}%{RESET}"
                                else:
                                    # Moving toward semantic (negative)
                                    delta_str = f" {CYAN}{delta_pct:>+6.1f}%{RESET}"
                        
                        # Add feature flags if present (ORD=ordinal, PM=per-member, CU=curriculum, TA=temp-anneal)
                        features = set_encoder_features.get(col_name, [])
                        features_str = ""
                        if features:
                            features_str = f" {CYAN}[{','.join(features)}]{RESET}"
                        
                        # Add per-member diversity info if available
                        pm_stats = set_per_member_stats.get(col_name)
                        pm_str = ""
                        if pm_stats:
                            pm_range = pm_stats['max'] - pm_stats['min']
                            if pm_range > 0.01:  # Only show if there's meaningful diversity
                                pm_str = f" {GREEN}(range:{pm_range:.1%}){RESET}"
                            else:
                                pm_str = f" {GRAY}(range:{pm_range:.1%}){RESET}"
                        
                        # Build final row with consistent spacing
                        logger.info(f"      {display_name:<45s} {lrn_colored} {sem_colored}{delta_str}{features_str}{pm_str}")
                    
                    # Calculate mean and std for each strategy across all columns
                    set_strategy_stats = {}
                    for strategy_name, code in set_strategy_order:
                        if strategy_name == 'Learned':
                            values = [learned for _, learned, _ in set_mixture_data]
                        else:  # Semantic
                            values = [semantic for _, _, semantic in set_mixture_data]
                        set_strategy_stats[strategy_name] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'code': code
                        }
                    
                    # Calculate mean delta if we have movement
                    mean_delta = 0.0
                    if has_deltas:
                        delta_values = [d for d in set_mixture_deltas.values() if abs(d) > 0.001]
                        if delta_values:
                            mean_delta = np.mean(delta_values)
                    
                    logger.info(f"      " + "-" * sep_width)
                    
                    # Add delta info to summary if we have movement
                    if has_deltas and abs(mean_delta) > 0.001:
                        delta_direction = "→LRN" if mean_delta > 0 else "→SEM"
                        delta_color = GREEN if mean_delta > 0 else CYAN
                        logger.info(f"      Strategy Summary (mean ± std across {set_adaptive_count} columns) [Avg Δ: {delta_color}{mean_delta*100:+.1f}%{RESET} {delta_direction}]:")
                    else:
                        logger.info(f"      Strategy Summary (mean ± std across {set_adaptive_count} columns):")
                    
                    summary_parts = []
                    # Find dominant strategy by mean weight
                    dominant_summary = max(set_strategy_stats.items(), key=lambda x: x[1]['mean'])
                    for strategy_name, code in set_strategy_order:
                        stats = set_strategy_stats[strategy_name]
                        stat_str = f"{code}: {stats['mean']:4.1%}±{stats['std']:3.1%}"
                        # Color: yellow for dominant, gray for others
                        if strategy_name == dominant_summary[0]:
                            summary_parts.append(f"{YELLOW}{stat_str}{RESET}")
                        else:
                            summary_parts.append(f"{GRAY}{stat_str}{RESET}")
                    logger.info("      " + "  ".join(summary_parts))
                    
                    # Add mean and std as bottom rows in the table
                    logger.info(f"      " + "-" * sep_width)
                    mean_parts = [f"{'MEAN (across all columns)':<45s}"]
                    for strategy_name, _ in set_strategy_order:
                        mean_val = set_strategy_stats[strategy_name]['mean']
                        mean_str = f"{mean_val:>6.1%}"
                        # Color: yellow for dominant, gray for others
                        if strategy_name == dominant_summary[0]:
                            mean_parts.append(f"{YELLOW}{mean_str}{RESET}")
                        else:
                            mean_parts.append(f"{GRAY}{mean_str}{RESET}")
                    # Add mean delta if we're showing deltas
                    if has_deltas:
                        if abs(mean_delta) < 0.001:
                            mean_parts.append(f"{GRAY}    -- {RESET}")
                        else:
                            delta_pct = mean_delta * 100
                            delta_color = GREEN if mean_delta > 0 else CYAN
                            mean_parts.append(f"{delta_color}{delta_pct:>+6.1f}%{RESET}")
                    logger.info("      " + " ".join(mean_parts))
                    
                    std_parts = [f"{'STD (variation between columns)':<45s}"]
                    for strategy_name, _ in set_strategy_order:
                        std_val = set_strategy_stats[strategy_name]['std']
                        std_str = f"{std_val:>6.1%}"
                        # All std values in gray
                        std_parts.append(f"{GRAY}{std_str}{RESET}")
                    # Add std of deltas if we're showing deltas
                    if has_deltas:
                        delta_values = [d for d in set_mixture_deltas.values() if abs(d) > 0.001]
                        if delta_values and len(delta_values) > 1:
                            delta_std = np.std(delta_values) * 100
                            std_parts.append(f"{GRAY}{delta_std:>+6.1f}%{RESET}")
                        else:
                            std_parts.append(f"{GRAY}    -- {RESET}")
                    logger.info("      " + " ".join(std_parts))
                    logger.info(f"      Total: {set_adaptive_count} AdaptiveSetEncoder columns")
                    logger.info("      [DEBUG] Strategy Summary complete - returning from _log_marginal_loss_breakdown")
                        
        except Exception as e:
            logger.warning(f"Failed to log marginal loss breakdown: {e}")

    def log_mi_summary(self, epoch_idx):
        """
        Log a concise MI summary every epoch for tracking MI progression over time.
        This allows analysis of which columns are learning relationships vs staying independent.
        """
        if not hasattr(self.encoder, 'col_mi_estimates'):
            return
        
        # Get MI estimates
        col_mi = self.encoder.col_mi_estimates
        joint_mi = self.encoder.joint_mi_estimate
        
        # Filter out None values
        valid_mi = {k: v for k, v in col_mi.items() if v is not None}
        
        if not valid_mi:
            return
        
        # Sort by MI value
        sorted_mi = sorted(valid_mi.items(), key=lambda x: x[1], reverse=True)
        
        # Log top 5 and bottom 3 (now 0-100% scale - higher = more predictable from context)
        logger.info(f"📊 Predictability Summary:")
        logger.info(f"   Joint predictability: {joint_mi:.1f}%" if joint_mi is not None else "   Joint: not available")
        
        if len(sorted_mi) > 0:
            logger.info(f"   Top 5 Most Predictable Columns:")
            for col, pred in sorted_mi[:5]:
                logger.info(f"      {col}: {pred:.1f}%")
            
            if len(sorted_mi) > 3:
                logger.info(f"   Bottom 3 Least Predictable Columns:")
                for col, pred in sorted_mi[-3:]:
                    logger.info(f"      {col}: {pred:.1f}%")
    
    def log_epoch_summary_banner(self, epoch_idx, val_loss, val_components):
        """
        Log a big visible banner showing loss trends over 1, 5, 20, 50 epochs.
        Makes it immediately obvious if training is progressing or stuck.
        """
        if not hasattr(self, 'history_db') or not self.history_db:
            return
        
        # Get loss history from database
        try:
            history = self.history_db.get_all_loss_history()
            if not history or len(history) < 2:
                return
            
            # Current epoch (1-indexed in display)
            current_epoch = epoch_idx + 1
            
            # Get current values
            current_total = val_loss
            current_spread = val_components.get('spread', 0) if val_components else 0
            current_joint = val_components.get('joint', 0) if val_components else 0
            current_marginal = val_components.get('marginal', 0) if val_components else 0
            
            # Helper to calculate delta from N epochs ago
            def get_delta(epochs_back, component='validation_loss'):
                target_epoch = current_epoch - epochs_back
                if target_epoch < 1:
                    return None, None, None
                
                # Find entry for target epoch
                for entry in history:
                    if entry.get('epoch') == target_epoch:
                        old_val = entry.get(component)
                        if old_val is None:
                            return None, None, None
                        
                        if component == 'validation_loss':
                            new_val = current_total
                        elif component == 'spread':
                            new_val = current_spread
                        elif component == 'joint':
                            new_val = current_joint
                        elif component == 'marginal':
                            new_val = current_marginal
                        else:
                            return None, None, None
                        
                        delta = new_val - old_val
                        pct = (delta / old_val * 100) if old_val != 0 else 0
                        return old_val, delta, pct
                
                return None, None, None
            
            # Calculate deltas for 1, 5, 10, 25 epochs
            deltas_1 = get_delta(1)
            deltas_5 = get_delta(5)
            deltas_10 = get_delta(10)
            deltas_25 = get_delta(25)
            
            # Calculate component deltas for same windows
            spread_1 = get_delta(1, 'spread')
            spread_5 = get_delta(5, 'spread')
            spread_10 = get_delta(10, 'spread')
            spread_25 = get_delta(25, 'spread')
            
            joint_1 = get_delta(1, 'joint')
            joint_5 = get_delta(5, 'joint')
            joint_10 = get_delta(10, 'joint')
            joint_25 = get_delta(25, 'joint')
            
            marginal_1 = get_delta(1, 'marginal')
            marginal_5 = get_delta(5, 'marginal')
            marginal_10 = get_delta(10, 'marginal')
            marginal_25 = get_delta(25, 'marginal')
            
            # Print banner
            logger.info("")
            logger.info("=" * 100)
            logger.info(f"{'EPOCH ' + str(current_epoch) + ' LOSS SUMMARY':^100}")
            logger.info("=" * 100)
            
            # Current loss values with components
            logger.info(f"  CURRENT: Total={current_total:.2f}  Spread={current_spread:.2f}  Joint={current_joint:.2f}  Marginal={current_marginal:.2f}")
            logger.info("")
            
            # Helper function to format delta with arrow as single string
            def format_delta(delta, pct):
                if delta is None or pct is None:
                    return "      N/A"
                
                # Arrow based on change
                if pct < -1:
                    arrow = "↓"  # Improving (loss going down)
                elif pct > 1:
                    arrow = "↑"  # Getting worse (loss going up)
                else:
                    arrow = "→"  # Flat
                
                return f"{delta:+8.2f}  {pct:+6.1f}% {arrow}"
            
            # Table headers with proper column widths (each column is 20 chars: 8 for delta + 2 spaces + 10 for percentage)
            logger.info(f"  {'Component':<12} {'Δ1':>20} {'Δ5':>20} {'Δ10':>20} {'Δ25':>20}")
            logger.info(f"  {'-' * 12} {'-' * 20} {'-' * 20} {'-' * 20} {'-' * 20}")
            
            # Total loss row
            d1 = format_delta(deltas_1[1], deltas_1[2])
            d5 = format_delta(deltas_5[1], deltas_5[2])
            d10 = format_delta(deltas_10[1], deltas_10[2])
            d25 = format_delta(deltas_25[1], deltas_25[2])
            logger.info(f"  {'TOTAL':<12} {d1:>20} {d5:>20} {d10:>20} {d25:>20}")
            
            # Spread row
            d1 = format_delta(spread_1[1], spread_1[2])
            d5 = format_delta(spread_5[1], spread_5[2])
            d10 = format_delta(spread_10[1], spread_10[2])
            d25 = format_delta(spread_25[1], spread_25[2])
            logger.info(f"  {'Spread':<12} {d1:>20} {d5:>20} {d10:>20} {d25:>20}")
            
            # Joint row
            d1 = format_delta(joint_1[1], joint_1[2])
            d5 = format_delta(joint_5[1], joint_5[2])
            d10 = format_delta(joint_10[1], joint_10[2])
            d25 = format_delta(joint_25[1], joint_25[2])
            logger.info(f"  {'Joint':<12} {d1:>20} {d5:>20} {d10:>20} {d25:>20}")
            
            # Marginal row
            d1 = format_delta(marginal_1[1], marginal_1[2])
            d5 = format_delta(marginal_5[1], marginal_5[2])
            d10 = format_delta(marginal_10[1], marginal_10[2])
            d25 = format_delta(marginal_25[1], marginal_25[2])
            logger.info(f"  {'Marginal':<12} {d1:>20} {d5:>20} {d10:>20} {d25:>20}")
            
            logger.info("=" * 100)
            logger.info("")
            
        except Exception as e:
            logger.warning(f"Failed to generate epoch summary banner: {e}")
    
    def log_encoder_summary(self):
        """
        Log summary information about encoders including adaptive strategies.
        Useful for understanding what the model learned.
        """
        logger.info("=" * 100)
        logger.info("🔧 ENCODER SUMMARY")
        logger.info("=" * 100)
        
        # Log adaptive scalar encoder strategies
        from featrix.neural.scalar_codec import AdaptiveScalarEncoder
        scalar_encoders = {}
        
        for col_name in self.encoder.column_encoder.encoders.keys():
            encoder = self.encoder.column_encoder.encoders[col_name]
            if isinstance(encoder, AdaptiveScalarEncoder):
                weights = encoder.get_strategy_weights()
                scalar_encoders[col_name] = weights
        
        if scalar_encoders:
            logger.info("")
            logger.info("📊 Adaptive Scalar Encoder Strategies:")
            logger.info("   Column Name                                    Linear  Log    Robust  Dominant")
            logger.info("   " + "-" * 90)
            
            for col_name, weights in scalar_encoders.items():
                # Check if weights contains an error
                if 'error' in weights:
                    display_name = col_name[:45] + "..." if len(col_name) > 45 else col_name
                    logger.info(f"   {display_name:48s} ERROR: {weights['error']}")
                    continue
                
                # Filter out non-numeric values and find dominant strategy
                numeric_weights = {k: v for k, v in weights.items() if isinstance(v, (int, float))}
                if not numeric_weights:
                    display_name = col_name[:45] + "..." if len(col_name) > 45 else col_name
                    logger.info(f"   {display_name:48s} ERROR: No numeric weights available")
                    continue
                
                # Determine dominant strategy from numeric weights only
                dominant = max(numeric_weights.items(), key=lambda x: x[1])
                dominant_str = f"{dominant[0].upper()} ({dominant[1]:.0%})"
                
                # Truncate column name if too long
                display_name = col_name[:45] + "..." if len(col_name) > 45 else col_name
                
                # Safely format weights, using 0.0 if key is missing
                linear_val = weights.get('linear', 0.0) if isinstance(weights.get('linear'), (int, float)) else 0.0
                log_val = weights.get('log', 0.0) if isinstance(weights.get('log'), (int, float)) else 0.0
                robust_val = weights.get('robust', 0.0) if isinstance(weights.get('robust'), (int, float)) else 0.0
                
                logger.info(
                    f"   {display_name:48s} {linear_val:6.1%}  {log_val:6.1%}  {robust_val:6.1%}  {dominant_str}"
                )
        
        # Log semantic set initialization status
        from featrix.neural.set_codec import SetEncoder
        # Note: get_config is already imported at top of file, don't re-import here
        
        if get_config().use_semantic_set_initialization():
            logger.info("")
            logger.info("🎨 Semantic Set Initialization: ENABLED")
            set_count = 0
            initialized_count = 0
            
            for col_name in self.encoder.column_encoder.encoders.keys():
                encoder = self.encoder.column_encoder.encoders[col_name]
                if isinstance(encoder, SetEncoder):
                    set_count += 1
                    if encoder.bert_projection is not None:
                        initialized_count += 1
            
            logger.info(f"   Set columns with semantic init: {initialized_count}/{set_count}")
        
        logger.info("=" * 100)

    def log_relationship_effectiveness(self, epoch_idx: int, loss_dict: Optional[Dict] = None):
        """
        Log comprehensive relationship effectiveness metrics.
        
        Measures how much relationships are helping marginal reconstruction and
        whether we have sufficient model capacity to learn from them.
        
        Run every 25 epochs for deep analysis, lightweight metrics every 5 epochs.
        """
        # Skip if relationships aren't enabled
        if not hasattr(self.encoder, 'joint_encoder'):
            return
        
        rel_extractor = getattr(self.encoder.joint_encoder, 'relationship_extractor', None)
        if rel_extractor is None:
            return
        
        # Lightweight logging every 5 epochs
        if epoch_idx % 5 == 0:
            self._log_relationship_summary_lite(epoch_idx, rel_extractor, loss_dict)
        
        # Deep analysis every 25 epochs
        if epoch_idx % 25 == 0:
            self._log_relationship_deep_analysis(epoch_idx, rel_extractor, loss_dict)
    
    def _log_relationship_summary_lite(self, epoch_idx: int, rel_extractor, loss_dict: Optional[Dict]):
        """Lightweight relationship summary - runs every 5 epochs."""
        try:
            n_cols = len(self.col_order)
            total_pairs = len(rel_extractor.all_pairs) if hasattr(rel_extractor, 'all_pairs') else 0
            disabled_pairs = len(rel_extractor.disabled_pairs) if hasattr(rel_extractor, 'disabled_pairs') else 0
            active_pairs = total_pairs - disabled_pairs
            
            # Calculate relationship token counts (query extractor for fusion mode)
            ops_per_pair = getattr(rel_extractor, 'ops_per_pair', 1)
            active_rel_tokens = active_pairs * ops_per_pair
            
            # Sequence composition
            total_seq_len = 1 + n_cols + active_rel_tokens  # CLS + columns + relationships
            rel_ratio = active_rel_tokens / n_cols if n_cols > 0 else 0
            
            logger.info(f"🔗 Relationships: {active_pairs}/{total_pairs} active pairs "
                       f"({active_rel_tokens} tokens, {rel_ratio:.1f}x columns)")
            
        except Exception as e:
            logger.warning(f"Failed to log relationship summary: {e}")
    
    def _log_relationship_deep_analysis(self, epoch_idx: int, rel_extractor, loss_dict: Optional[Dict]):
        """Deep relationship analysis - runs every 25 epochs."""
        try:
            logger.info("")
            logger.info("=" * 100)
            logger.info(f"🔬 RELATIONSHIP EFFECTIVENESS ANALYSIS - EPOCH {epoch_idx}")
            logger.info("=" * 100)
            
            n_cols = len(self.col_order)
            
            # 1. SEQUENCE COMPOSITION
            total_pairs = len(rel_extractor.all_pairs) if hasattr(rel_extractor, 'all_pairs') else 0
            disabled_pairs = len(rel_extractor.disabled_pairs) if hasattr(rel_extractor, 'disabled_pairs') else 0
            active_pairs = total_pairs - disabled_pairs
            # Query extractor for ops_per_pair (1 if fused, 9 if unfused)
            ops_per_pair = getattr(rel_extractor, 'ops_per_pair', 1)
            active_rel_tokens = active_pairs * ops_per_pair
            
            logger.info(f"")
            logger.info(f"📐 Sequence Composition:")
            logger.info(f"   Columns:                    {n_cols}")
            logger.info(f"   Relationship pairs:         {active_pairs}/{total_pairs} active")
            logger.info(f"   Relationship tokens:        {active_rel_tokens} ({ops_per_pair} ops × {active_pairs} pairs)")
            logger.info(f"   Total sequence length:      {1 + n_cols + active_rel_tokens} (CLS + cols + rel)")
            logger.info(f"   Relationship/Column ratio:  {active_rel_tokens/n_cols:.2f}x" if n_cols > 0 else "   N/A")
            
            # 2. ATTENTION HEAD ANALYSIS
            logger.info(f"")
            logger.info(f"🧠 Attention Head Analysis:")
            try:
                analysis = self.encoder.joint_encoder._analyze_attention_weight_similarity()
                logger.info(f"   Diversity score:      {analysis['diversity_score']:.3f} (higher = better)")
                logger.info(f"   Average similarity:   {analysis['avg_similarity']:.3f}")
                logger.info(f"   Redundant pairs:      {analysis['n_redundant_pairs']}/{analysis['n_heads'] * (analysis['n_heads']-1) // 2}")
                logger.info(f"   Status:               {analysis['status']}")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not analyze attention: {e}")
            
            # 3. HARDEST COLUMNS VS RELATIONSHIP COVERAGE
            if hasattr(rel_extractor, 'col_marginal_losses') and rel_extractor.col_marginal_losses:
                logger.info(f"")
                logger.info(f"🎯 Hardest Columns vs Relationship Coverage:")
                logger.info(f"   {'Column':<40} {'Loss':>10} {'Active Rels':>12}")
                logger.info(f"   {'-'*40} {'-'*10} {'-'*12}")
                
                hardest_cols = sorted(rel_extractor.col_marginal_losses.items(), 
                                     key=lambda x: x[1], reverse=True)[:10]
                
                for col_name, loss in hardest_cols:
                    col_idx = self.col_order.index(col_name) if col_name in self.col_order else -1
                    if col_idx >= 0:
                        # Count active relationships involving this column
                        active_rels = sum(1 for (i, j) in rel_extractor.all_pairs 
                                         if (i == col_idx or j == col_idx) 
                                         and (i, j) not in rel_extractor.disabled_pairs)
                        logger.info(f"   {col_name:<40} {loss:>10.4f} {active_rels:>12}")
            
            # 4. RELATIONSHIP IMPORTANCE DISTRIBUTION
            if hasattr(rel_extractor, '_compute_relationship_importance'):
                try:
                    importance_scores = rel_extractor._compute_relationship_importance()
                    if importance_scores:
                        scores = list(importance_scores.values())
                        logger.info(f"")
                        logger.info(f"📊 Relationship Importance Distribution:")
                        logger.info(f"   Min:     {min(scores):.4f}")
                        logger.info(f"   Max:     {max(scores):.4f}")
                        logger.info(f"   Mean:    {np.mean(scores):.4f}")
                        logger.info(f"   Std:     {np.std(scores):.4f}")
                        logger.info(f"   Spread:  {max(scores) - min(scores):.4f} (higher = more differentiated)")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not compute importance distribution: {e}")
            
            logger.info("=" * 100)
            logger.info("")
            
        except Exception as e:
            logger.warning(f"Failed to log relationship deep analysis: {e}")
            traceback.print_exc()
    
    def detect_capacity_bottlenecks(self, epoch_idx: int, loss_dict: Optional[Dict] = None) -> Dict[str, any]:
        """
        Detect if the model has sufficient capacity to learn from relationships.
        
        Returns a dict with bottleneck indicators and recommendations.
        Runs every 50 epochs (or on demand).
        
        Checks:
        1. Attention head redundancy (>0.7 similarity = need more heads)
        2. Marginal vs Joint loss ratio (marginal stuck = predictor bottleneck)
        3. Loss improvement rate (slow = capacity issue)
        4. Relationship pruning impact (heavy pruning helps = too many relationships)
        
        Returns:
            Dict with 'bottlenecks' list, 'recommendations' list, and metrics
        """
        if epoch_idx % 50 != 0 and epoch_idx != 0:
            return {}
        
        bottlenecks = []
        recommendations = []
        metrics = {}
        
        try:
            # 1. ATTENTION HEAD REDUNDANCY
            if hasattr(self.encoder, 'joint_encoder'):
                try:
                    analysis = self.encoder.joint_encoder._analyze_attention_weight_similarity()
                    metrics['attention_similarity'] = analysis['avg_similarity']
                    metrics['attention_diversity'] = analysis['diversity_score']
                    metrics['attention_redundant_pairs'] = analysis['n_redundant_pairs']
                    metrics['n_attention_heads'] = analysis['n_heads']
                    
                    if analysis['avg_similarity'] > 0.8:
                        bottlenecks.append("HIGH_ATTENTION_REDUNDANCY")
                        recommendations.append(
                            f"Attention heads are highly redundant (similarity={analysis['avg_similarity']:.2f}). "
                            f"Consider increasing n_attention_heads from {analysis['n_heads']} to {analysis['n_heads'] * 2}."
                        )
                    elif analysis['avg_similarity'] > 0.7:
                        bottlenecks.append("MODERATE_ATTENTION_REDUNDANCY")
                        recommendations.append(
                            f"Attention heads show moderate redundancy (similarity={analysis['avg_similarity']:.2f}). "
                            f"Current heads may be near capacity."
                        )
                except Exception as e:
                    logger.debug(f"Could not analyze attention redundancy: {e}")
            
            # 2. MARGINAL VS JOINT LOSS RATIO
            if loss_dict:
                try:
                    marginal_loss = loss_dict.get('marginal_loss', {}).get('total', 0)
                    joint_loss = loss_dict.get('joint_loss', {}).get('total', 0)
                    spread_loss = loss_dict.get('spread_loss', {}).get('total', 0)
                    
                    metrics['marginal_loss'] = marginal_loss
                    metrics['joint_loss'] = joint_loss
                    metrics['spread_loss'] = spread_loss
                    
                    if joint_loss > 0:
                        marginal_joint_ratio = marginal_loss / joint_loss
                        metrics['marginal_joint_ratio'] = marginal_joint_ratio
                        
                        # If marginal is much larger than joint, predictors may be bottleneck
                        if marginal_joint_ratio > 5.0 and epoch_idx > 50:
                            bottlenecks.append("PREDICTOR_BOTTLENECK")
                            recommendations.append(
                                f"Marginal loss ({marginal_loss:.4f}) is {marginal_joint_ratio:.1f}x joint loss ({joint_loss:.4f}). "
                                f"Column predictors may need more capacity (increase d_hidden or n_layers)."
                            )
                except Exception as e:
                    logger.debug(f"Could not analyze loss ratios: {e}")
            
            # 3. LOSS IMPROVEMENT RATE
            if hasattr(self, 'history_db') and self.history_db:
                try:
                    history = self.history_db.get_all_loss_history()
                    if len(history) >= 20:
                        # Compare last 10 epochs to previous 10
                        recent_10 = [h['val_loss'] for h in history[-10:] if h['val_loss'] is not None]
                        prev_10 = [h['val_loss'] for h in history[-20:-10] if h['val_loss'] is not None]
                        
                        if recent_10 and prev_10:
                            recent_mean = np.mean(recent_10)
                            prev_mean = np.mean(prev_10)
                            improvement_rate = (prev_mean - recent_mean) / prev_mean if prev_mean > 0 else 0
                            
                            metrics['improvement_rate_10_epochs'] = improvement_rate
                            
                            if improvement_rate < 0.01 and epoch_idx > 100:
                                bottlenecks.append("STALLED_TRAINING")
                                recommendations.append(
                                    f"Loss improvement rate is very low ({improvement_rate*100:.2f}% over last 10 epochs). "
                                    f"Model may be at capacity or learning rate too low."
                                )
                except Exception as e:
                    logger.debug(f"Could not analyze loss history: {e}")
            
            # 4. RELATIONSHIP TOKEN VS COLUMN RATIO
            if hasattr(self.encoder, 'joint_encoder'):
                rel_extractor = getattr(self.encoder.joint_encoder, 'relationship_extractor', None)
                if rel_extractor and hasattr(rel_extractor, 'all_pairs'):
                    n_cols = len(self.col_order)
                    total_pairs = len(rel_extractor.all_pairs)
                    disabled_pairs = len(getattr(rel_extractor, 'disabled_pairs', set()))
                    active_pairs = total_pairs - disabled_pairs
                    active_rel_tokens = active_pairs * 6  # 6 ops per pair
                    
                    metrics['n_columns'] = n_cols
                    metrics['active_relationship_pairs'] = active_pairs
                    metrics['active_relationship_tokens'] = active_rel_tokens
                    metrics['rel_to_col_ratio'] = active_rel_tokens / n_cols if n_cols > 0 else 0
                    
                    # Very high ratio may overwhelm the model
                    if active_rel_tokens > n_cols * 10 and epoch_idx < 50:
                        bottlenecks.append("HIGH_RELATIONSHIP_RATIO")
                        recommendations.append(
                            f"Relationship tokens ({active_rel_tokens}) are {active_rel_tokens/n_cols:.1f}x columns ({n_cols}). "
                            f"Consider more aggressive pruning or increasing d_model to handle the sequence."
                        )
            
            # 5. TRANSFORMER LAYER CAPACITY
            if hasattr(self.encoder, 'joint_encoder') and hasattr(self.encoder.joint_encoder, 'config'):
                config = self.encoder.joint_encoder.config
                n_layers = getattr(config, 'n_layers', 3)
                d_model = getattr(config, 'd_model', 256)
                n_heads = getattr(config, 'n_heads', 8)
                
                metrics['n_transformer_layers'] = n_layers
                metrics['d_model'] = d_model
                metrics['n_heads'] = n_heads
                
                # Check if sequence length exceeds typical attention capacity
                # CRITICAL: Use ACTUAL sequence length from transformer, not theoretical max
                # Relationship tokens are POOLED (not concatenated), so sequence = CLS + n_cols only
                n_cols = len(self.col_order)
                rel_extractor = getattr(self.encoder.joint_encoder, 'relationship_extractor', None)
                
                # ACTUAL sequence length used in transformer: CLS (1) + columns (n_cols)
                # Relationship tokens are pooled into CLS, not added to sequence
                actual_seq_len = 1 + n_cols  # CLS + columns
                metrics['total_sequence_length'] = actual_seq_len
                
                # Also track relationship tokens available (for reference, not used in sequence)
                if rel_extractor:
                    total_pairs = len(rel_extractor.all_pairs)
                    disabled_pairs = len(getattr(rel_extractor, 'disabled_pairs', set()))
                    active_pairs = total_pairs - disabled_pairs
                    ops_per_pair = getattr(rel_extractor, 'ops_per_pair', 1)
                    rel_tokens_available = active_pairs * ops_per_pair
                    metrics['relationship_tokens_available'] = rel_tokens_available
                    metrics['relationship_tokens_used_in_sequence'] = 0  # Pooled, not in sequence
                    
                    # Log both actual and available for clarity
                    logger.info(f"   📐 Sequence Length Analysis:")
                    logger.info(f"      Actual transformer sequence: {actual_seq_len} (CLS + {n_cols} cols)")
                    logger.info(f"      Relationship tokens available: {rel_tokens_available} ({ops_per_pair} ops × {active_pairs} pairs)")
                    logger.info(f"      Relationship tokens used in sequence: 0 (pooled into CLS, not concatenated)")
                    logger.info(f"      Relationship/Column ratio (available): {rel_tokens_available/n_cols:.1f}x" if n_cols > 0 else "      N/A")
                else:
                    metrics['relationship_tokens_available'] = 0
                    metrics['relationship_tokens_used_in_sequence'] = 0
                
                # Rule of thumb: attention degrades when seq >> d_model
                if actual_seq_len > d_model * 4:
                    bottlenecks.append("SEQUENCE_TOO_LONG")
                    recommendations.append(
                        f"Sequence length ({actual_seq_len}) is {actual_seq_len/d_model:.1f}x d_model ({d_model}). "
                        f"Consider increasing d_model or reducing columns."
                    )
                
                # Few layers with long sequences
                if n_layers < 3 and actual_seq_len > 200:
                    bottlenecks.append("FEW_LAYERS")
                    recommendations.append(
                        f"Only {n_layers} transformer layers for sequence of {actual_seq_len}. "
                        f"Consider increasing n_transformer_layers to 4-6."
                    )
            
            # LOG RESULTS
            if bottlenecks or (epoch_idx % 50 == 0 and epoch_idx > 0):
                logger.info("")
                logger.info("=" * 100)
                logger.info(f"🔍 CAPACITY BOTTLENECK ANALYSIS - EPOCH {epoch_idx}")
                logger.info("=" * 100)
                
                if bottlenecks:
                    logger.info(f"")
                    logger.info(f"⚠️  BOTTLENECKS DETECTED ({len(bottlenecks)}):")
                    for i, bottleneck in enumerate(bottlenecks, 1):
                        logger.info(f"   {i}. {bottleneck}")
                    
                    logger.info(f"")
                    logger.info(f"💡 RECOMMENDATIONS:")
                    for i, rec in enumerate(recommendations, 1):
                        logger.info(f"   {i}. {rec}")
                else:
                    logger.info(f"")
                    logger.info(f"✅ No capacity bottlenecks detected")
                
                # Log key metrics
                logger.info(f"")
                logger.info(f"📊 Key Metrics:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        logger.info(f"   {key}: {value:.4f}")
                    else:
                        logger.info(f"   {key}: {value}")
                
                logger.info("=" * 100)
                logger.info("")
            
        except Exception as e:
            logger.warning(f"Failed to detect capacity bottlenecks: {e}")
            traceback.print_exc()
        
        return {
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'metrics': metrics,
        }
    
    def log_ablation_comparison(self, epoch_idx: int):
        """
        Run an ablation study comparing predictions with vs without relationship tokens.
        
        This is EXPENSIVE - only run every 100 epochs starting from epoch 5.
        Temporarily zeros out relationship tokens and compares reconstruction quality.
        Averages over multiple batches for more stable estimates.
        """
        # Defer until epoch >= 5 (model needs time to learn before ablation is meaningful)
        if epoch_idx < 5 or epoch_idx % 100 != 0:
            return
        
        if not hasattr(self.encoder, 'joint_encoder'):
            return
        
        rel_extractor = getattr(self.encoder.joint_encoder, 'relationship_extractor', None)
        if rel_extractor is None:
            return
        
        try:
            logger.info("")
            logger.info("=" * 100)
            logger.info(f"🔬 RELATIONSHIP ABLATION STUDY - EPOCH {epoch_idx}")
            logger.info("=" * 100)
            logger.info("   (Comparing model WITH relationships vs relationships DISABLED)")
            logger.info("   (Averaging over multiple batches for stable estimates)")
            
            # Get a validation loader
            val_loader = self._get_validation_loader_for_ablation()
            if val_loader is None:
                logger.warning("   ⚠️  Could not get validation data for ablation study")
                return
            
            # Average over multiple batches (5-10 batches for stability)
            n_batches_to_average = min(10, len(val_loader))
            if n_batches_to_average == 0:
                logger.warning("   ⚠️  No validation batches available for ablation study")
                return
            
            logger.info(f"   Averaging over {n_batches_to_average} batches...")
            
            self.encoder.eval()
            
            # Accumulate losses across batches
            marginal_with_sum = 0.0
            marginal_without_sum = 0.0
            n_batches_processed = 0
            
            with torch.no_grad():
                for batch_idx, batch in enumerate(val_loader):
                    if batch_idx >= n_batches_to_average:
                        break
                    
                    try:
                        # 1. Normal forward pass (with relationships)
                        encodings_with_rel = self.encoder(batch)
                        loss_with_rel, loss_dict_with = self.encoder.compute_total_loss(*encodings_with_rel)
                        
                        # 2. Disable relationship extractor temporarily
                        saved_extractor = self.encoder.joint_encoder.relationship_extractor
                        self.encoder.joint_encoder.relationship_extractor = None
                        
                        # Forward pass without relationships
                        encodings_without_rel = self.encoder(batch)
                        loss_without_rel, loss_dict_without = self.encoder.compute_total_loss(*encodings_without_rel)
                        
                        # 3. Restore relationship extractor
                        self.encoder.joint_encoder.relationship_extractor = saved_extractor
                        
                        # Accumulate marginal losses
                        marginal_with = loss_dict_with.get('marginal_loss', {}).get('total', 0)
                        marginal_without = loss_dict_without.get('marginal_loss', {}).get('total', 0)
                        
                        marginal_with_sum += marginal_with
                        marginal_without_sum += marginal_without
                        n_batches_processed += 1
                        
                    except Exception as e:
                        logger.debug(f"   Skipping batch {batch_idx} due to error: {e}")
                        continue
            
            self.encoder.train()
            
            # Compute averages
            if n_batches_processed > 0:
                marginal_with_avg = marginal_with_sum / n_batches_processed
                marginal_without_avg = marginal_without_sum / n_batches_processed
                
                improvement = (marginal_without_avg - marginal_with_avg) / marginal_without_avg * 100 if marginal_without_avg > 0 else 0
                
                logger.info(f"")
                logger.info(f"📊 Marginal Reconstruction Loss (averaged over {n_batches_processed} batches):")
                logger.info(f"   WITH relationships:    {marginal_with_avg:.6f}")
                logger.info(f"   WITHOUT relationships: {marginal_without_avg:.6f}")
                logger.info(f"   Improvement:           {improvement:+.2f}%")
                
                if improvement > 5:
                    logger.info(f"   ✅ Relationships are HELPING ({improvement:.1f}% better)")
                elif improvement > 0:
                    logger.info(f"   ⚠️  Relationships provide MARGINAL benefit ({improvement:.1f}%)")
                else:
                    logger.info(f"   ❌ Relationships may NOT be helping ({improvement:.1f}%)")
                    logger.info(f"      Consider: more capacity, different relationship ops, or disabling")
            else:
                logger.warning("   ⚠️  No batches successfully processed for ablation study")
            
            logger.info("=" * 100)
            logger.info("")
            
        except Exception as e:
            logger.warning(f"Failed to run ablation comparison: {e}")
            traceback.print_exc()
            # Ensure encoder is back in training mode
            if hasattr(self, 'encoder'):
                self.encoder.train()
    
    def _get_validation_loader_for_ablation(self):
        """Get a small validation dataloader for ablation studies."""
        try:
            if hasattr(self, 'val_dataloader') and self.val_dataloader is not None:  # pylint: disable=no-member
                return self.val_dataloader  # pylint: disable=no-member
            
            # Create a minimal dataloader from validation data
            if hasattr(self, 'val_input_data') and self.val_input_data is not None:
                from torch.utils.data import DataLoader
                dataset = SuperSimpleSelfSupervisedDataset(
                    df=self.val_input_data.df,
                    codecs=self.col_codecs,
                )
                return DataLoader(
                    dataset,
                    batch_size=min(32, len(dataset)),
                    shuffle=False,
                    collate_fn=collate_tokens,
                    num_workers=0,
                )
        except Exception as e:
            logger.debug(f"Could not create validation loader: {e}")
        
        return None

    def train_save_progress_stuff(self,
                                        epoch_idx,
                                        batch_idx,
                                        epoch_start_time_now,
                                        encodings,
                                        save_prediction_vector_lengths,
                                        training_event_dict,  # passed by reference
                                        d,                    # passed by reference
                                        current_lr,
                                        loss_tensor,
                                        loss_dict,
                                        val_loss,
                                        val_components,
                                        dataloader_batch_durations,
                                        progress_counter,
                                        print_callback,
                                        training_event_callback
    ):
        # print("!!! train_save_progress_stuff called")
        full_predictions = encodings[-6:-3]
        short_predictions = encodings[-3:]

        if save_prediction_vector_lengths:
            full_pred_1_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(full_predictions[0])
            }
            full_pred_2_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(full_predictions[1])
            }
            full_pred_unmasked_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(full_predictions[2])
            }

            short_pred_1_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(short_predictions[0])
            }
            short_pred_2_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(short_predictions[1])
            }
            short_pred_unmasked_len = {
                self.col_order[idx]: torch.linalg.norm(
                    t, dim=1
                ).tolist()
                for idx, t in enumerate(short_predictions[2])
            }
            # Apply K-fold CV offset if present
            cumulative_epoch = epoch_idx
            if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
            
            training_event_dict["prediction_vec_lengths"] = (
                dict(
                    epoch=1 + cumulative_epoch,
                    full_1=full_pred_1_len,
                    full_2=full_pred_2_len,
                    full_unmasked=full_pred_unmasked_len,
                    short_1=short_pred_1_len,
                    short_2=short_pred_2_len,
                    short_unmasked=short_pred_unmasked_len,
                )
            )

        # Apply K-fold CV offset if present (makes K-fold CV invisible - epochs are cumulative)
        cumulative_epoch = epoch_idx
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
        
        # MEMORY LEAK FIX: Push to SQLite, keep minimal data in memory
        # Push mutual information to SQLite (non-blocking)
        mi_entry = {
                "epoch": 1 + cumulative_epoch,
            "columns": copy.deepcopy(self.encoder.col_mi_estimates),
            "joint": copy.deepcopy(self.encoder.joint_mi_estimate),
            }
        if hasattr(self, 'history_db') and self.history_db:
            self.history_db.push_mutual_information(1 + cumulative_epoch, mi_entry)
        
        # Keep only the most recent MI in memory (replace, don't append)
        d["mutual_information"] = [mi_entry]
        
        # Push loss history to SQLite (non-blocking) - don't keep in memory
        loss_entry = {
                "epoch": 1 + cumulative_epoch,
                "current_learning_rate": current_lr,
                "loss": loss_tensor.item(),
                "validation_loss": val_loss,
                "time_now": time.time(),
                "duration": time.time() - epoch_start_time_now,
            }
        
        # Add loss components if available
        if val_components:
            loss_entry["spread"] = val_components.get('spread')
            loss_entry["joint"] = val_components.get('joint')
            loss_entry["marginal"] = val_components.get('marginal')
            loss_entry["marginal_weighted"] = val_components.get('marginal_weighted')
        
        if hasattr(self, 'history_db') and self.history_db:
            self.history_db.push_loss_history(loss_entry)
        
        # Keep only validation loss value in memory (not full history)
        d["current_validation_loss"] = val_loss
        training_event_dict["loss_details"] = (
            {
                "epoch": 1 + cumulative_epoch,
                "current_learning_rate": current_lr,
                "loss": loss_tensor.item(),
                "validation_loss": val_loss,
                "time_now": time.time(),
                "duration": time.time() - epoch_start_time_now,
                "details": loss_dict
            }
        )

        training_event_dict["encoder_timing"] = (
            dict(
                epoch=1 + cumulative_epoch,
                durations=[],
            )
        )
        training_event_dict["loss_timing"] = (
            dict(
                epoch=1 + cumulative_epoch,
                durations=[],
            )
        )
        # training_event_dict["loop_timing"] = (
        #     dict(
        #         epoch=1 + epoch_idx,
        #         model_durations=[],  # loop_stopwatch removed
        #         dataloader_individual_durations=self.train_dataset.stopwatch.get_interval_durations() if hasattr(self.train_dataset, 'stopwatch') and self.train_dataset.stopwatch is not None else [],
        #         dataloader_batch_durations=dataloader_batch_durations, #timed_data_loader.stopwatch.get_interval_durations(),
        #     )
        # )

        d["progress_counter"] = progress_counter
        d["batch_idx"] = batch_idx
        d["time_now"] = time.time()
        if print_callback is not None:
            print_callback(d)

        if training_event_callback is not None:
            for k, v in d.items():
                training_event_dict[k] = v
            training_event_callback(training_event_dict)

        return

    @staticmethod
    def _get_default_curriculum_config() -> CurriculumLearningConfig:
        """
        Get the default curriculum learning schedule (30-55-15).
        
        Simplified 3-phase schedule that keeps marginal+joint aligned during reconstruction,
        since relationship features tie joint and marginal learning together.
        
        Phase 1 (0-30%): Spread focus - establish good embedding geometry
        Phase 2 (30-85%): Reconstruction focus - marginal+joint aligned (relationships connect them)
        Phase 3 (85-100%): Refinement - balanced fine-tuning
        """
        # CRITICAL: Marginal loss is ~100× larger than spread/joint (raw values ~3600 vs ~37)
        # After removing normalizer, marginal_weight must be ~1/100 of others for balance
        # We use >1.0 weights for AMPLIFICATION during focus phases
        return CurriculumLearningConfig(
            enabled=True,
            phases=[
                CurriculumPhaseConfig(
                    name="spread_focus",
                    start_progress=0.0,
                    end_progress=0.20,
                    spread_weight=10.0,     # Amplify 10× (compensate for LOW LR during 0-10% warmup phase)
                    marginal_weight=0.35,    # Increased from 0.02 to allow some marginal learning (marginal is 100× larger than spread, so 0.1 is still low)
                    joint_weight=0.5,       # Reduced but still present
                    transition_width=0.15,
                ),
                CurriculumPhaseConfig(
                    name="reconstruction_focus",
                    start_progress=0.20,
                    end_progress=0.80,
                    spread_weight=5.0,      # Moderate spread to maintain geometry
                    marginal_weight=0.25,   # Increased - better reconstruction with relationships
                    joint_weight=2.0,       # Joint and marginal aligned (relationships tie them together)
                    transition_width=0.05,
                ),
                CurriculumPhaseConfig(
                    name="refinement",
                    start_progress=0.80,
                    end_progress=1.0,
                    spread_weight=2.0,      # Slight emphasis on spread+joint for final polish
                    marginal_weight=0.15,   # Reduced but still present for refinement
                    joint_weight=2.0,       # Maintain joint for final reconstruction quality
                    transition_width=0.05,
                ),
            ],
        )

    def _smooth_transition(
        self,
        progress: float,
        phase_start: float,
        phase_end: float,
        start_val: float,
        end_val: float,
        transition_width: float,
    ) -> float:
        """
        Smooth cosine transition between two values.
        
        Args:
            progress: Current progress (0.0 to 1.0)
            phase_start: Start of transition phase
            phase_end: End of transition phase
            start_val: Value at phase_start
            end_val: Value at phase_end
            transition_width: Width of transition window (as fraction of total epochs)
            
        Returns:
            Interpolated value
        """
        transition_start = phase_start - transition_width
        transition_end = phase_start + transition_width
        
        if progress < transition_start:
            return start_val
        elif progress > transition_end:
            return end_val
        else:
            # Cosine interpolation for smooth transition
            t = (progress - transition_start) / (transition_end - transition_start)
            return start_val + (end_val - start_val) * (1 - math.cos(math.pi * t)) / 2

    def _compute_loss_weights(self, epoch_idx: int, n_epochs: int):
        """
        Compute all three loss weights (spread, marginal, joint) for curriculum learning.
        
        Uses curriculum_learning config if available, otherwise falls back to default schedule.
        If curriculum learning is disabled, returns constant weights (1.0, 1.0, 1.0).
        
        Can be disabled globally via config.json: "disable_curriculum_learning": true
        
        Args:
            epoch_idx: Current epoch (0-indexed)
            n_epochs: Total number of epochs
            
        Returns:
            tuple: (spread_weight, marginal_weight, joint_weight)
        """
        # Check global disable flag from config.json
        sphere_config = get_config()
        if sphere_config.get_disable_curriculum_learning():
            return (1.0, 1.0, 1.0)
        
        # Get curriculum config
        curriculum_config = None
        if hasattr(self, 'encoder') and hasattr(self.encoder, 'config'):
            if hasattr(self.encoder.config, 'loss_config'):
                curriculum_config = self.encoder.config.loss_config.curriculum_learning
        
        # If no curriculum config, use default
        if curriculum_config is None:
            curriculum_config = self._get_default_curriculum_config()
        
        # If curriculum learning is disabled, return constant weights
        if not curriculum_config.enabled or not curriculum_config.phases:
            return (1.0, 1.0, 1.0)
        
        # Calculate progress through training (0.0 to 1.0)
        progress = epoch_idx / n_epochs
        
        # Find the current phase and previous phase (for transitions)
        current_phase = None
        prev_phase = None
        
        for i, phase in enumerate(curriculum_config.phases):
            if progress >= phase.start_progress and progress <= phase.end_progress:
                current_phase = phase
                if i > 0:
                    prev_phase = curriculum_config.phases[i - 1]
                break
        
        if current_phase is None:
            # Fallback: use last phase if progress > 1.0 (shouldn't happen)
            current_phase = curriculum_config.phases[-1]
        
        # Determine if we're in a transition period
        transition_start = current_phase.start_progress - current_phase.transition_width
        transition_end = current_phase.start_progress + current_phase.transition_width
        
        if prev_phase and transition_start <= progress <= transition_end:
            # We're in a transition - interpolate between previous and current phase
            # The transition happens around current_phase.start_progress
            spread_weight = self._smooth_transition(
                progress,
                current_phase.start_progress,
                current_phase.start_progress,  # Not used, but required by signature
                prev_phase.spread_weight,
                current_phase.spread_weight,
                current_phase.transition_width,
            )
            marginal_weight = self._smooth_transition(
                progress,
                current_phase.start_progress,
                current_phase.start_progress,  # Not used, but required by signature
                prev_phase.marginal_weight,
                current_phase.marginal_weight,
                current_phase.transition_width,
            )
            joint_weight = self._smooth_transition(
                progress,
                current_phase.start_progress,
                current_phase.start_progress,  # Not used, but required by signature
                prev_phase.joint_weight,
                current_phase.joint_weight,
                current_phase.transition_width,
            )
        else:
            # We're in the middle of a phase - use phase weights directly
            spread_weight = current_phase.spread_weight
            marginal_weight = current_phase.marginal_weight
            joint_weight = current_phase.joint_weight
        
        return (spread_weight, marginal_weight, joint_weight)

    def _compute_marginal_loss_weight(self, epoch_idx, n_epochs):
        """
        DEPRECATED: Use _compute_loss_weights() instead.
        
        Kept for backward compatibility. Returns only marginal weight from curriculum schedule.
        """
        _, marginal_weight, _ = self._compute_loss_weights(epoch_idx, n_epochs)
        return marginal_weight

    def _update_encoder_epoch_counters(self, epoch_idx: int, n_epochs: int):
        """
        Update epoch counters in adaptive encoders for strategy pruning.
        
        Called at the start of each epoch to inform encoders about training progress.
        This enables adaptive strategies like Top-K pruning after warmup.
        """
        from featrix.neural.string_codec import StringEncoder
        from featrix.neural.scalar_codec import AdaptiveScalarEncoder
        from featrix.neural.set_codec import SetEncoder
        
        for col_name, encoder in self.encoder.column_encoder.encoders.items():
            # Update StringEncoder epoch counters
            if isinstance(encoder, StringEncoder) and hasattr(encoder, '_epoch_counter'):
                encoder._epoch_counter.fill_(epoch_idx)
                encoder._total_epochs.fill_(n_epochs)
            
            # Update AdaptiveScalarEncoder epoch counters for strategy pruning
            if isinstance(encoder, AdaptiveScalarEncoder) and hasattr(encoder, '_current_epoch'):
                encoder._current_epoch.fill_(epoch_idx)
                encoder._total_epochs.fill_(n_epochs)
            
            # Update SetEncoder epoch counters (if we add pruning there too)
            if isinstance(encoder, SetEncoder) and hasattr(encoder, '_epoch_counter'):
                encoder._epoch_counter.fill_(epoch_idx)
                encoder._total_epochs.fill_(n_epochs)
    
    def _log_mixture_logit_changes(self, epoch_idx: int):
        """
        Log mixture logit changes for all SetEncoders after each epoch.
        This helps track whether the mixture weights are actually updating during training.
        
        FIXED: Now uses get_actual_mixture_weight() to show REAL weights with temperature
        and curriculum applied, not just raw sigmoid(logit).
        """
        from featrix.neural.set_codec import SetEncoder
        
        mixture_changes = []
        for col_name, encoder in self.encoder.column_encoder.encoders.items():
            if isinstance(encoder, SetEncoder) and hasattr(encoder, 'mixture_logit') and encoder.mixture_logit is not None:
                current_logit = encoder.mixture_logit.item()
                
                # FIXED: Use actual mixture weight with temperature/curriculum applied
                if hasattr(encoder, 'get_actual_mixture_weight'):
                    mixture_weight, _, _, temperature, _ = encoder.get_actual_mixture_weight()
                else:
                    mixture_weight = torch.sigmoid(encoder.mixture_logit).item()
                    temperature = 1.0
                
                # Track changes across epochs
                if not hasattr(encoder, '_logged_logit_history'):
                    encoder._logged_logit_history = []
                
                encoder._logged_logit_history.append({
                    'epoch': epoch_idx,
                    'logit': current_logit,
                    'mixture': mixture_weight,
                    'temperature': temperature
                })
                
                # Calculate change from previous epoch
                if len(encoder._logged_logit_history) > 1:
                    prev_logit = encoder._logged_logit_history[-2]['logit']
                    logit_change = current_logit - prev_logit
                    prev_mixture = encoder._logged_logit_history[-2]['mixture']
                    mixture_change = mixture_weight - prev_mixture
                    
                    mixture_changes.append({
                        'column': col_name,
                        'logit': current_logit,
                        'logit_change': logit_change,
                        'mixture': mixture_weight,
                        'mixture_change': mixture_change,
                        'temperature': temperature
                    })
        
        # Log summary if there are changes to report
        if mixture_changes:
            logger.info("")
            logger.info(f"🎯 Mixture Logit Changes (Epoch {epoch_idx + 1}):")
            for change in mixture_changes:
                learned_pct = change['mixture'] * 100
                semantic_pct = (1 - change['mixture']) * 100
                temp_str = f", T={change.get('temperature', 1.0):.2f}" if change.get('temperature', 1.0) != 1.0 else ""
                logger.info(f"   {change['column']:20s}: Logit={change['logit']:7.4f} (Δ={change['logit_change']:+.4f}), "
                          f"Mixture={learned_pct:5.1f}%LRN/{semantic_pct:5.1f}%SEM (Δ={change['mixture_change']*100:+.2f}%){temp_str}")
            logger.info("")

    def _handle_cuda_oom_error(
        self,
        error: Exception,
        epoch_idx: int,
        batch_idx: int,
        batch_size: int,
        pass_type: str = "backward"
    ):
        """
        Handle CUDA out of memory errors with detailed diagnostics and recovery suggestions.
        
        This method is called when torch.OutOfMemoryError or a RuntimeError with CUDA OOM
        message is caught during forward or backward pass. It provides detailed diagnostics and
        actionable suggestions for recovery.
        
        Args:
            pass_type: Either "forward" or "backward" to indicate where the OOM occurred
        """
        logger.error("=" * 80)
        logger.error(f"💥 CUDA OUT OF MEMORY ERROR DURING {pass_type.upper()} PASS")
        logger.error("=" * 80)
        logger.error(f"   Epoch: {epoch_idx + 1}, Batch: {batch_idx + 1}")
        logger.error(f"   Current batch_size: {batch_size}")
        logger.error("")
        
        # Try to get GPU memory stats with detailed breakdown
        log_gpu_memory_detailed("OOM ERROR", model=self.encoder if hasattr(self, 'encoder') else None, level="error")
        
        # Check for DataLoader workers
        try:
            from lib.system_health_monitor import SystemHealthMonitor
            monitor = SystemHealthMonitor()
            workers = monitor.find_dataloader_workers()
            if workers:
                total_worker_rss = sum(w.get('rss_gb', 0) for w in workers)
                logger.error(f"      DataLoader Workers: {len(workers)} processes using ~{total_worker_rss:.2f} GB RAM")
        except Exception:
            pass
        
        logger.error("")
        logger.error("📋 RECOVERY SUGGESTIONS:")
        logger.error(f"   1. Reduce batch_size (current: {batch_size}) - try halving it")
        logger.error("   2. Set environment variable: PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True")
        logger.error("   3. Free up GPU memory by closing other GPU processes")
        logger.error("   4. Check if other training jobs are competing for GPU memory")
        logger.error("")
        
        # Suggest a new batch size (minimum 8, was 32 which caused infinite loops)
        suggested_batch_size = max(8, batch_size // 2)
        # Round to power of 2 (math is imported at top of file)
        suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
        logger.error(f"   💡 Suggested batch_size for retry: {suggested_batch_size}")
        logger.error("")
        logger.error(f"   Original error: {error}")
        logger.error("=" * 80)
        
        # Try to clear GPU cache
        try:
            aggressive_clear_gpu_cache()
            logger.info("🧹 GPU cache cleared after OOM error")
        except Exception as clear_err:
            logger.debug(f"Could not clear GPU cache: {clear_err}")

    def _init_d(
        self,
        timeStart,
        n_epochs,
        batches_per_epoch
    ):
        _pid = os.getpid()
        _hostname = socket.gethostname()

        d = {
                "debug_label": self.output_debug_label,
                "status": "training",
                "start_time": timeStart,
                "time_now": timeStart,
                # "resource_usage": [],
                "loss_history": [],  # Not used in memory - stored in SQLite
                "current_validation_loss": None,
                "epoch_idx": 0,
                "epoch_total": n_epochs,
                "batch_idx": 0,
                "batch_total": batches_per_epoch * n_epochs,
                "progress_counter": 0,
                "max_progress": batches_per_epoch * n_epochs,
                "num_rows": self.len_df(),
                "num_cols": len(self.train_input_data.df.columns),
                "compute_device": get_device().type,
                "pid": _pid,
                "hostname": _hostname,
                "mutual_information": [],
                "model_param_count": self.model_param_count,
                "encoder_timing": [],
                "loss_timing": [],
                "loop_timing": [],
                "prediction_vec_lengths": [],
            }
        return d

    def _record_epoch_loss_history(
        self, d: dict, epoch_idx: int, loss, val_loss, val_components: dict,
        current_lr: float, epoch_start_time_now: float
    ) -> None:
        """
        Record loss history entry for this epoch if not already recorded.
        
        Args:
            d: Progress dictionary
            epoch_idx: Current epoch index
            loss: Training loss tensor
            val_loss: Validation loss value
            val_components: Validation loss components dict
            current_lr: Function to get current learning rate
            epoch_start_time_now: Epoch start timestamp
        """
        try:
            _loss_item = loss.item()
        except Exception:
            _loss_item = "not set"
        
        # Check if we already have this epoch recorded (avoid duplicates)
        for entry in d["loss_history"]:
            if entry.get("epoch", -1) == epoch_idx:
                return  # Already recorded
        
        loss_entry = {
            "epoch": epoch_idx,
            "current_learning_rate": current_lr,
            "loss": _loss_item,
            "validation_loss": val_loss,
            "time_now": time.time(),
            "duration": time.time() - epoch_start_time_now,
        }
        
        # Add loss components if available
        if val_components:
            loss_entry["spread"] = val_components.get('spread')
            loss_entry["joint"] = val_components.get('joint')
            loss_entry["marginal"] = val_components.get('marginal')
            loss_entry["marginal_weighted"] = val_components.get('marginal_weighted')
        
        # Push to SQLite (non-blocking) - don't keep in memory
        if hasattr(self, 'history_db') and self.history_db:
            self.history_db.push_loss_history(loss_entry)
        
        # Keep only validation loss value in memory
        d["current_validation_loss"] = val_loss

    def _perform_gradual_data_rotation(
        self, epoch_idx: int, n_epochs: int, batch_size: int,
        data_loader, val_dataloader, collate_tokens
    ):
        """
        Perform gradual data rotation - swap a fraction of train/val data.
        
        Returns:
            Tuple of (new_data_loader, new_val_dataloader, timed_data_loader)
        """
        from featrix.neural.dataloader_utils import create_dataloader_kwargs
        from featrix.neural.gpu_utils import (
            is_gpu_available, get_gpu_memory_allocated, get_gpu_memory_reserved,
            get_gpu_device_properties
        )
        
        logger.info(f"🔄 GRADUAL DATA ROTATION at epoch {epoch_idx}/{n_epochs} ({epoch_idx/n_epochs*100:.1f}% complete)")
        logger.info(f"   Rotating {self._rotation_fraction*100:.0f}% of data (instead of 100% resample)")
        
        # Save the original column types and encoders to reuse
        original_ignore_cols = self.train_input_data.ignore_cols
        
        # CRITICAL FIX: Extract the ACTUAL detected types from detectors
        original_encoder_overrides = {}
        for col_name, detector in self.train_input_data._detectors.items():
            original_encoder_overrides[col_name] = detector.type_name
        
        logger.info(f"📋 Extracted {len(original_encoder_overrides)} encoder types from original detection:")
        for col, typ in list(original_encoder_overrides.items())[:5]:
            logger.info(f"   {col}: {typ}")
        if len(original_encoder_overrides) > 5:
            logger.info(f"   ... and {len(original_encoder_overrides) - 5} more")
        
        # Get the original split fraction
        original_split_fraction = len(self.val_dataset) / (len(self.train_dataset) + len(self.val_dataset))
        logger.info(f"   Original split fraction: {original_split_fraction:.3f}")
        
        # GRADUAL ROTATION: Swap a small fraction instead of fully reshuffling
        train_df = self.train_input_data.df.copy()
        val_df = self.val_input_data.df.copy()
        
        # Calculate how many rows to rotate
        rotation_size = int(min(len(train_df), len(val_df)) * self._rotation_fraction)
        rotation_size = max(1, rotation_size)
        logger.info(f"   Rotating {rotation_size} rows ({self._rotation_fraction*100:.0f}% of smaller set)")
        
        # Randomly select rows to swap
        np.random.seed(42 + epoch_idx)
        train_swap_indices = np.random.choice(len(train_df), size=rotation_size, replace=False)
        val_swap_indices = np.random.choice(len(val_df), size=rotation_size, replace=False)
        
        # Extract and swap rows
        train_rows_to_val = train_df.iloc[train_swap_indices].copy()
        val_rows_to_train = val_df.iloc[val_swap_indices].copy()
        train_df_remaining = train_df.drop(train_df.index[train_swap_indices]).reset_index(drop=True)
        val_df_remaining = val_df.drop(val_df.index[val_swap_indices]).reset_index(drop=True)
        
        new_train_df = pd.concat([train_df_remaining, val_rows_to_train], ignore_index=True)
        new_val_df = pd.concat([val_df_remaining, train_rows_to_val], ignore_index=True)
        
        # Shuffle the new sets
        new_train_df = new_train_df.sample(frac=1.0, random_state=42 + epoch_idx).reset_index(drop=True)
        new_val_df = new_val_df.sample(frac=1.0, random_state=43 + epoch_idx).reset_index(drop=True)
        logger.info(f"   New split: train={len(new_train_df)}, val={len(new_val_df)}")
        
        # Add timeline entry
        if hasattr(self, '_training_timeline'):
            self._training_timeline.append({
                "epoch": epoch_idx,
                "timestamp": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
                "event_type": "train_val_gradual_rotation",
                "description": f"Gradual data rotation at epoch {epoch_idx} ({self._rotation_fraction*100:.0f}% of data)",
                "rotation_size": rotation_size,
                "train_size": len(new_train_df),
                "val_size": len(new_val_df),
                "original_split_fraction": original_split_fraction,
                "random_seed": 42 + epoch_idx
            })
        
        # Recreate input datasets with preserved encoder overrides
        self.train_input_data = FeatrixInputDataSet(
            df=new_train_df, ignore_cols=original_ignore_cols, limit_rows=None,
            encoder_overrides=original_encoder_overrides, hybrid_detection_use_llm=False
        )
        self.val_input_data = FeatrixInputDataSet(
            df=new_val_df, ignore_cols=original_ignore_cols, limit_rows=None,
            encoder_overrides=original_encoder_overrides, hybrid_detection_use_llm=False
        )
        logger.info(f"   ✅ Reused encoder overrides for consistency")
        
        # Recreate datasets
        self.train_dataset = SuperSimpleSelfSupervisedDataset(
            self.train_input_data.df, codecs=self.col_codecs,
            row_meta_data=self.train_input_data.project_row_meta_data_list,
        )
        self.val_dataset = SuperSimpleSelfSupervisedDataset(
            self.val_input_data.df, codecs=self.col_codecs,
            row_meta_data=self.val_input_data.project_row_meta_data_list,
        )
        
        # Recreate dataloaders
        if self.train_input_data.project_row_meta_data_list is None:
            _cleanup_dataloader_workers(data_loader, "training DataLoader")
            
            train_dl_kwargs = create_dataloader_kwargs(
                batch_size=batch_size, shuffle=True, drop_last=True,
                dataset_size=len(self.train_input_data.df),
                num_columns=len(self.train_input_data.df.columns),
            )
            data_loader = DataLoader(self.train_dataset, collate_fn=collate_tokens, **train_dl_kwargs)
            
            # Calculate validation workers based on VRAM
            val_num_workers = 0
            if is_gpu_available():
                try:
                    total_memory = (get_gpu_device_properties(0).total_memory / (1024**3)) if get_gpu_device_properties(0) else 0.0
                    reserved = get_gpu_memory_reserved()
                    free_vram = total_memory - reserved
                    available_for_workers = max(0, free_vram - 20.0)  # 20GB safety margin
                    max_workers_by_vram = int(available_for_workers / 0.6)  # 600MB per worker
                    from featrix.neural.dataloader_utils import get_optimal_num_workers
                    default_workers = get_optimal_num_workers(dataset_size=len(self.val_input_data.df))
                    val_num_workers = min(default_workers, max_workers_by_vram, 2 if total_memory <= 32 else 4)
                    val_num_workers = max(0, val_num_workers)
                except Exception as e:
                    logger.warning(f"Could not calculate optimal validation workers: {e}")
            
            _cleanup_dataloader_workers(val_dataloader, "validation DataLoader")
            val_dl_kwargs = create_dataloader_kwargs(
                batch_size=batch_size, shuffle=False, drop_last=False, num_workers=val_num_workers,
                dataset_size=len(self.val_input_data.df), num_columns=len(self.val_input_data.df.columns),
            )
            val_dataloader = DataLoader(self.val_dataset, collate_fn=collate_tokens, **val_dl_kwargs)
            logger.info(f"   Recreated DataLoaders with num_workers={train_dl_kwargs.get('num_workers', 0)}")
        else:
            mySampler = DataSpaceBatchSampler(batch_size, self.train_input_data)
            sampler_dl_kwargs = create_dataloader_kwargs(
                batch_size=batch_size, shuffle=False, drop_last=False,
                dataset_size=len(self.train_input_data.df), num_columns=len(self.train_input_data.df.columns),
            )
            sampler_dl_kwargs.pop('batch_size', None)
            sampler_dl_kwargs.pop('shuffle', None)
            sampler_dl_kwargs.pop('drop_last', None)
            data_loader = DataLoader(self.train_dataset, batch_sampler=mySampler, collate_fn=collate_tokens, **sampler_dl_kwargs)
        
        logger.info(f"✅ Train/val split resampled successfully")
        return data_loader, val_dataloader, data_loader

    def _check_loss_stuck_detection(self, epoch_idx: int, val_components: Optional[Dict]) -> None:
        """Detect if joint/marginal losses are stuck (not improving)."""
        if not val_components or epoch_idx < 5:
            return
        
        # Initialize history
        if not hasattr(self, '_joint_loss_history'):
            self._joint_loss_history = []
        if not hasattr(self, '_marginal_loss_history'):
            self._marginal_loss_history = []
        
        self._joint_loss_history.append(val_components['joint'])
        self._marginal_loss_history.append(val_components['marginal'])
        
        # Keep only last 10 epochs
        if len(self._joint_loss_history) > 10:
            self._joint_loss_history = self._joint_loss_history[-10:]
        if len(self._marginal_loss_history) > 10:
            self._marginal_loss_history = self._marginal_loss_history[-10:]
        
        if len(self._joint_loss_history) < 5:
            return
        
        STUCK_VARIANCE_THRESHOLD = 0.0001
        STUCK_RANGE_THRESHOLD = 0.01
        
        joint_variance = np.var(self._joint_loss_history[-5:])
        joint_range = max(self._joint_loss_history[-5:]) - min(self._joint_loss_history[-5:])
        if joint_variance < STUCK_VARIANCE_THRESHOLD and joint_range < STUCK_RANGE_THRESHOLD:
            logger.warning(f"⚠️ JOINT LOSS IS STUCK (Epoch {epoch_idx})")
            logger.warning(f"   Last 5 epochs: {self._joint_loss_history[-5:]}")
            logger.warning(f"   Variance: {joint_variance:.8f}, Range: {joint_range:.8f}")
            logger.warning("   Suggests: Joint encoder COLLAPSED/FROZEN or vanishing gradients")
        
        marginal_variance = np.var(self._marginal_loss_history[-5:])
        marginal_range = max(self._marginal_loss_history[-5:]) - min(self._marginal_loss_history[-5:])
        if marginal_variance < STUCK_VARIANCE_THRESHOLD and marginal_range < STUCK_RANGE_THRESHOLD:
            logger.warning(f"⚠️ MARGINAL LOSS IS STUCK (Epoch {epoch_idx})")
            logger.warning(f"   Last 5 epochs: {self._marginal_loss_history[-5:]}")
            logger.warning(f"   Variance: {marginal_variance:.8f}, Range: {marginal_range:.8f}")
            logger.warning("   Suggests: Column predictors COLLAPSED/FROZEN or vanishing gradients")

    def _check_publish_and_save(self, epoch_idx: int) -> None:
        """Check for PUBLISH flag and save embedding space for single predictor training."""
        output_dir_str = str(self.output_dir) if hasattr(self, 'output_dir') and self.output_dir else None
        job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
        
        if not check_publish_file(job_id, output_dir_str):
            return
        
        # Avoid multiple saves per epoch
        if epoch_idx == getattr(self, '_last_published_epoch', -1):
            return
        
        try:
            from featrix.neural.embedding_space_utils import write_embedding_space_pickle
            session_id = getattr(self, 'session_id', None) or self.training_info.get('session_id', None)
            filename = f"{session_id}-es-prelim.pickle" if session_id else (
                f"{job_id}-es-prelim.pickle" if job_id else "embedding_space-prelim.pickle"
            )
            pickle_path = write_embedding_space_pickle(self, output_dir_str, filename=filename)
            self._last_published_epoch = epoch_idx
            logger.info(f"📦 PUBLISH flag detected - embedding space saved at epoch {epoch_idx} to {pickle_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save embedding space for PUBLISH flag at epoch {epoch_idx}: {e}")
            logger.warning(f"   Training will continue - this save can be retried later")

    def _log_relationship_correlation_analysis(self, epoch_idx: int) -> None:
        """Run relationship correlation analysis every 25 epochs to verify inverse relationships."""
        if (epoch_idx + 1) % 25 != 0:
            return
        try:
            if not hasattr(self.encoder.joint_encoder, 'relationship_extractor'):
                return
            rel_extractor = self.encoder.joint_encoder.relationship_extractor
            if rel_extractor is None or not hasattr(rel_extractor, 'log_correlation_analysis'):
                return
            
            logger.info(f"\n🔍 Running relationship correlation analysis (epoch {epoch_idx + 1})...")
            corr_analysis = rel_extractor.log_correlation_analysis()
            
            # Store for later comparison
            if not hasattr(self, '_correlation_history'):
                self._correlation_history = []
            self._correlation_history.append({'epoch': epoch_idx + 1, 'analysis': corr_analysis})
            
            # Warn if no inverse relationships found
            if corr_analysis.get('n_strong_negative', 0) == 0:
                logger.warning("⚠️  No strong inverse correlations detected in encodings")
                logger.warning("   If your data has inverse relationships, they may not be captured")
        except Exception as e:
            logger.debug(f"Could not analyze relationship correlations: {e}")

    def _periodic_gc_and_flush(self, epoch_idx: int) -> None:
        """Periodic garbage collection and SQLite history flush."""
        # GC every 10 epochs for large datasets, 50 for small
        gc_interval = 10 if hasattr(self, 'train_input_data') and len(self.train_input_data.df) >= 20000 else 50
        if epoch_idx > 0 and epoch_idx % gc_interval == 0:
            import gc
            gc.collect()
            if is_gpu_available():
                empty_gpu_cache()
                synchronize_gpu()
            logger.debug(f"🧹 Garbage collection performed (interval: {gc_interval} epochs)")
            # Log VRAM after GC
            if is_gpu_available():
                alloc = get_gpu_memory_allocated()
                reserved = get_gpu_memory_reserved()
                logger.debug(f"📊 AFTER GC (epoch {epoch_idx}): VRAM {alloc:.2f}GB allocated, {reserved:.2f}GB reserved")
        
        # Flush history to SQLite every 100 epochs
        if epoch_idx > 0 and epoch_idx % 100 == 0:
            if hasattr(self, 'history_db') and self.history_db:
                self.history_db.flush()
                logger.debug(f"💾 Training history flushed to SQLite")

    def _log_training_start_banner(self, n_epochs: int, batch_size: int) -> None:
        """Log the training start banner with model configuration."""
        try:
            from featrix.neural.training_banner import log_training_start_banner
            n_hybrid_groups = len(getattr(self.train_input_data, 'hybrid_groups', {})) if hasattr(self, 'train_input_data') else 0
            d_model = self.d_model
            if (hasattr(self, 'encoder') and self.encoder is not None and
                hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'd_model')):
                d_model = self.encoder.config.d_model
            log_training_start_banner(
                total_epochs=n_epochs,
                batch_size=batch_size,
                training_type="ES",
                d_model=d_model,
                n_columns=len(self.col_codecs),
                n_hybrid_groups=n_hybrid_groups if n_hybrid_groups > 0 else None,
                n_transformer_layers=self.encoder.config.joint_encoder_config.n_layers if hasattr(self.encoder, 'config') else None,
                n_attention_heads=self.encoder.config.joint_encoder_config.n_heads if hasattr(self.encoder, 'config') else None
            )
        except Exception as e:
            logger.debug(f"Could not log training start banner: {e}")

    def _check_system_health(self, epoch_idx: int) -> None:
        """Check system health every 10 epochs."""
        if epoch_idx % 10 != 0 and epoch_idx != 0:
            return
        try:
            from lib.system_health_monitor import check_system_health
            job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
            check_system_health(context=f"EPOCH_{epoch_idx}_START", job_id=job_id)
        except Exception as e:
            logger.debug(f"System health check failed: {e}")
        
        # Check for runaway child processes (early warning for worker spawn loops)
        try:
            _check_for_runaway_processes(context=f"epoch {epoch_idx}", max_expected=_MAX_EXPECTED_WORKERS)
        except Exception as e:
            logger.debug(f"Runaway process check failed: {e}")

    def _track_oom_consecutive_epochs(self, oom_stats: dict) -> None:
        """Track consecutive OOM epochs and reset counters appropriately."""
        if oom_stats["oom_count_this_epoch"] > 0:
            oom_stats["consecutive_oom_epochs"] += 1
            if oom_stats["consecutive_oom_epochs"] >= 2:
                logger.warning(f"⚠️  OOM occurred in {oom_stats['consecutive_oom_epochs']} consecutive epochs!")
        else:
            if oom_stats["consecutive_oom_epochs"] > 0:
                logger.info(f"✅ Clean epoch (no OOM) - resetting consecutive OOM counter from {oom_stats['consecutive_oom_epochs']}")
            oom_stats["consecutive_oom_epochs"] = 0
        
        # Reset per-epoch counters
        oom_stats["oom_count_this_epoch"] = 0
        oom_stats["batches_skipped_this_epoch"] = 0

    def _reset_per_epoch_grad_stats(self, grad_clip_stats: dict) -> None:
        """Reset per-epoch gradient statistics."""
        grad_clip_stats["total_batches"] = 0
        grad_clip_stats["clipped_batches"] = 0
        grad_clip_stats["sum_unclipped_norms"] = 0.0
        grad_clip_stats["sum_clipped_norms"] = 0.0

    def _get_lr_string(self, current_lr) -> str:
        """Format learning rate as string."""
        try:
            lr_value = current_lr
            if lr_value < 0.0001:
                return f"lr={lr_value:.8f}"
            elif lr_value < 0.01:
                return f"lr={lr_value:.6f}"
            return f"lr={lr_value:.4f}"
        except Exception:
            return "lr=N/A"

    def _get_curriculum_phase_string(self, epoch_idx: int) -> str:
        """Get current curriculum phase as string."""
        try:
            progress = epoch_idx / self.n_epochs
            curriculum_config = None
            if hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config'):
                curriculum_config = self.encoder.config.loss_config.curriculum_learning
            if curriculum_config is None:
                curriculum_config = self._get_default_curriculum_config()
            
            for i, phase in enumerate(curriculum_config.phases):
                if progress >= phase.start_progress and progress <= phase.end_progress:
                    return f"phase={i + 1},{phase.name}"
            
            if curriculum_config.phases:
                return f"phase={len(curriculum_config.phases)},{curriculum_config.phases[-1].name}"
            return "phase=N/A"
        except Exception:
            return "phase=N/A"

    def _get_elapsed_time_string(self) -> str:
        """Get elapsed training time as string."""
        try:
            elapsed = time.time() - self.training_start_time
            if elapsed < 60:
                return f"[{int(elapsed)}s]"
            elif elapsed < 3600:
                return f"[{int(elapsed // 60)}m {int(elapsed % 60)}s]"
            return f"[{int(elapsed // 3600)}h {int((elapsed % 3600) // 60)}m]"
        except Exception:
            return ""

    def _log_validation_loss_summary(self, epoch_idx: int, val_loss: float, val_components: dict, current_lr) -> None:
        """Log validation loss summary with all components."""
        if not val_components:
            logger.info(f"📊 VAL LOSS: {val_loss:.4f}")
            return
        
        lr_str = self._get_lr_string(current_lr)
        phase_str = self._get_curriculum_phase_string(epoch_idx)
        elapsed_str = self._get_elapsed_time_string()
        
        try:
            marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
            marg_w_str = f"marg_w={marginal_weight:.4f}"
        except Exception:
            marg_w_str = "marg_w=N/A"
        
        marginal_pct = val_components.get('marginal_normalized', 0.0) * 100
        
        # Get gradient norm and parameter update norm for this epoch
        grad_norm_str = "N/A"
        param_update_norm_str = "N/A"
        if hasattr(self, '_epoch_grad_norms') and self._epoch_grad_norms:
            avg_grad_norm = sum(self._epoch_grad_norms) / len(self._epoch_grad_norms)
            grad_norm_str = f"{avg_grad_norm:.6f}"
        if hasattr(self, '_epoch_param_update_norms') and self._epoch_param_update_norms:
            avg_param_update_norm = sum(self._epoch_param_update_norms) / len(self._epoch_param_update_norms)
            param_update_norm_str = f"{avg_param_update_norm:.6f}"
        
        # Compact validation summary - main metrics on one line
        logger.info(f"📊 [{phase_str}] {elapsed_str} VAL: {val_loss:.2f}  "
                    f"spread={val_components['spread']:.2f}  joint={val_components['joint']:.2f}  "
                    f"marginal={val_components['marginal']:.2f}  lr={lr_str}  {marg_w_str}")
        
        # Only show detailed breakdown at diagnostic epochs (matches _log_detailed_val_diagnostics)
        diagnostic_epochs = [1, 5, 10, 25, 50]
        if epoch_idx in diagnostic_epochs:
            logger.info(f"   Details: marginal_weighted={val_components['marginal_weighted']:.2f}, "
                        f"norm={marginal_pct:.0f}% of random, grad={grad_norm_str}")

    def _load_checkpoint_with_recovery(
        self, existing_epochs: int, batch_size: int
    ) -> Tuple[int, int, bool, dict, int, int]:
        """
        Load checkpoint with corruption recovery.
        
        Returns:
            Tuple of (existing_epochs, base_epoch_index, checkpoint_loaded, d, progress_counter, batches_per_epoch)
        """
        # Check if this is K-fold CV by checking if _kv_fold_epoch_offset is set
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            # K-fold CV: Each fold starts from epoch 0 internally
            base_epoch_index = 0
        else:
            # Regular resume: existing_epochs is the last completed epoch index (0-indexed)
            base_epoch_index = existing_epochs + 1
            logger.info(f"Continuing training from epoch {base_epoch_index} (last completed: {existing_epochs})")
        
        checkpoint_loaded = False
        checkpoint_path = self.get_training_state_path(existing_epochs, 0)
        checkpoint_exists = Path(checkpoint_path).exists()
        
        # Initialize checkpoint search variables
        found_valid_checkpoint = False
        last_valid_epoch = None
        
        if checkpoint_exists:
            try:
                self.load_state(existing_epochs, 0)
                checkpoint_loaded = True
            except (EOFError, RuntimeError) as e:
                # Checkpoint file is corrupted - try to find last valid checkpoint
                logger.error(f"⚠️  Corrupted checkpoint detected (epoch {existing_epochs}): {e}")
                logger.warning(f"🔍 Searching for last valid checkpoint...")
                
                for check_epoch in range(existing_epochs, -1, -1):
                    if check_epoch < 0:
                        break
                    try:
                        cp_path = self.get_training_state_path(check_epoch, 0)
                        if Path(cp_path).exists():
                            try:
                                torch.load(cp_path, weights_only=False, map_location='cpu')
                                last_valid_epoch = check_epoch
                                found_valid_checkpoint = True
                                logger.info(f"✅ Found valid checkpoint at epoch {check_epoch}")
                                break
                            except Exception:
                                logger.debug(f"   Epoch {check_epoch} checkpoint also corrupted...")
                                continue
                    except Exception:
                        continue
                
                if found_valid_checkpoint and last_valid_epoch is not None:
                    try:
                        logger.info(f"🔄 Loading last valid checkpoint from epoch {last_valid_epoch}")
                        self.load_state(last_valid_epoch, 0)
                        existing_epochs = last_valid_epoch
                        base_epoch_index = last_valid_epoch + 1
                        checkpoint_loaded = True
                        logger.info(f"✅ Loaded checkpoint from epoch {last_valid_epoch}, continuing from {base_epoch_index}")
                    except Exception as load_err:
                        logger.error(f"❌ Failed to load checkpoint from epoch {last_valid_epoch}: {load_err}")
                        logger.warning(f"🔄 Falling back to starting from scratch (epoch 0)")
                        existing_epochs = None
                        base_epoch_index = 0
                        self.training_state = {}
                        checkpoint_loaded = False
                else:
                    logger.warning(f"🔄 No valid checkpoint found, starting from scratch (epoch 0)")
                    existing_epochs = None
                    base_epoch_index = 0
                    self.training_state = {}
                    checkpoint_loaded = False
        else:
            # Checkpoint file doesn't exist - OK when resuming from ES object (K-fold CV)
            logger.info(f"ℹ️  Checkpoint file not found at {checkpoint_path}")
            logger.info(f"   This is expected when resuming from ES object (K-fold CV)")
            checkpoint_loaded = False
        
        # Restore critical checkpoint data
        if checkpoint_loaded:
            d, progress_counter = self.restore_progress("debug", "progress_counter")
        else:
            d = None
            progress_counter = 0
        
        if d is None:
            logger.warning("Debug dict is None, will reinitialize after getting batches_per_epoch")
        
        # Get batches_per_epoch with comprehensive None handling
        batches_per_epoch = self.restore_progress("batches_per_epoch")
        batches_per_epoch = self._fix_batches_per_epoch(batches_per_epoch, batch_size)
        
        return existing_epochs, base_epoch_index, checkpoint_loaded, d, progress_counter, batches_per_epoch

    def _fix_batches_per_epoch(self, batches_per_epoch, batch_size: int) -> int:
        """Fix batches_per_epoch if it's None, a list, or wrong type."""
        if batches_per_epoch is None:
            logger.warning("batches_per_epoch is None, recalculating")
            return self._calculate_batches_per_epoch(batch_size)
        
        if isinstance(batches_per_epoch, list) and len(batches_per_epoch) == 1:
            batches_per_epoch = batches_per_epoch[0]
            if batches_per_epoch is None:
                logger.warning("batches_per_epoch extracted from list is None, recalculating")
                return self._calculate_batches_per_epoch(batch_size)
        
        if not isinstance(batches_per_epoch, int):
            logger.warning(f"batches_per_epoch is {type(batches_per_epoch)}: {batches_per_epoch}, converting to int")
            batches_per_epoch = int(batches_per_epoch)
        
        # Final safety check
        if batches_per_epoch is None or batches_per_epoch < 1:
            logger.error("FINAL SAFETY CHECK: batches_per_epoch invalid! Using emergency value.")
            batches_per_epoch = max(1, int(math.ceil(len(self.train_input_data.df) / batch_size)))
        
        return batches_per_epoch

    def _calculate_batches_per_epoch(self, batch_size: int) -> int:
        """Calculate batches_per_epoch from dataset."""
        try:
            if self.train_input_data.project_row_meta_data_list is None:
                temp_loader = DataLoader(
                    self.train_dataset, batch_size=batch_size, shuffle=True,
                    collate_fn=collate_tokens, num_workers=0
                )
                result = len(temp_loader)
                logger.info(f"Recalculated batches_per_epoch from DataLoader: {result}")
                return result
            else:
                result = int(math.ceil(len(self.train_dataset) / batch_size))
                logger.info(f"Recalculated batches_per_epoch from dataset length: {result}")
                return result
        except Exception as e:
            logger.error(f"Failed to recalculate batches_per_epoch: {e}")
            num_rows = len(self.train_input_data.df)
            result = max(1, int(math.ceil(num_rows / batch_size)))
            logger.warning(f"Using emergency fallback batches_per_epoch: {result}")
            return result

    def _create_optimizer_with_separate_lrs(self, optimizer_params: dict) -> torch.optim.Optimizer:
        """
        Create optimizer with separate learning rates for encoders vs predictors.
        Predictors get 10x higher LR to compensate for vanishing gradients.
        
        Tries in order: 8-bit AdamW (memory savings) > Fused AdamW (speed) > Regular AdamW
        """
        # Ensure optimizer_params has valid values
        if optimizer_params is None:
            optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
        elif not isinstance(optimizer_params, dict):
            logger.warning(f"optimizer_params is not a dict: {type(optimizer_params)}, using defaults")
            optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
        else:
            if optimizer_params.get("lr") is None:
                logger.warning(f"optimizer_params has None lr, using default 0.001")
                optimizer_params = {**optimizer_params, "lr": 0.001}
            if "weight_decay" not in optimizer_params:
                optimizer_params["weight_decay"] = 1e-4
        
        base_lr = optimizer_params.get('lr')
        predictor_lr_multiplier = 10.0  # Predictors need higher LR due to vanishing gradients
        
        # Separate parameters into encoders and predictors
        predictor_params = []
        encoder_params = []
        for name, param in self.encoder.named_parameters():
            if 'column_predictor' in name or 'joint_predictor' in name:
                predictor_params.append(param)
            else:
                encoder_params.append(param)
        
        logger.info(f"🔧 SEPARATE LEARNING RATES (to fix vanishing predictor gradients):")
        logger.info(f"   Encoder LR: {base_lr:.6e}")
        logger.info(f"   Predictor LR: {base_lr * predictor_lr_multiplier:.6e} ({predictor_lr_multiplier}× higher)")
        
        optimizer_kwargs = {'weight_decay': optimizer_params.get('weight_decay', 1e-4)}
        optimizer = None
        
        # Try 8-bit AdamW first (saves ~50% memory)
        use_8bit = os.environ.get('FEATRIX_USE_8BIT_ADAM', '1').lower() in ('1', 'true', 'yes')
        if use_8bit:
            try:
                import bitsandbytes as bnb
                logger.info("🔋 Using 8-bit AdamW (saves ~50% optimizer memory)")
                optimizer = bnb.optim.AdamW8bit([
                    {'params': encoder_params, 'lr': base_lr},
                    {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
                ], **optimizer_kwargs)
            except ImportError:
                logger.info("⚠️  bitsandbytes not available, falling back to fused/regular AdamW")
            except Exception as e:
                logger.warning(f"⚠️  8-bit AdamW failed: {e}")
        
        # Try fused AdamW (PyTorch 2.0+, ~10% faster)
        if optimizer is None:
            try:
                optimizer = torch.optim.AdamW([
                    {'params': encoder_params, 'lr': base_lr},
                    {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
                ], fused=True, **optimizer_kwargs)
                logger.info("⚡ Using fused AdamW (10-15% faster)")
            except (TypeError, RuntimeError):
                pass
        
        # Fallback to regular AdamW
        if optimizer is None:
            optimizer = torch.optim.AdamW([
                {'params': encoder_params, 'lr': base_lr},
                {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
            ], **optimizer_kwargs)
            logger.info("📊 Using regular AdamW")
        
        # Log diagnostic info
        self._log_optimizer_diagnostics(optimizer)
        self._log_parameter_trainability_check()
        
        return optimizer

    def _log_optimizer_diagnostics(self, optimizer) -> None:
        """Log optimizer initialization diagnostics."""
        logger.info("=" * 80)
        logger.info("🔍 OPTIMIZER INITIALIZATION DIAGNOSTIC")
        logger.info("=" * 80)
        logger.info(f"   Optimizer param groups: {len(optimizer.param_groups)}")
        for i, group in enumerate(optimizer.param_groups):
            num_params = len(group['params'])
            lr = group['lr']
            group_name = "Encoders" if i == 0 else "Predictors"
            logger.info(f"   Group {i} ({group_name}): {num_params} parameters, LR={lr:.6e}")
        
        opt_params_count = sum(len(g['params']) for g in optimizer.param_groups)
        model_trainable_count = sum(1 for p in self.encoder.parameters() if p.requires_grad)
        logger.info(f"   Optimizer manages: {opt_params_count} parameters")
        logger.info(f"   Model has trainable: {model_trainable_count} parameters")
        
        if opt_params_count != model_trainable_count:
            logger.error(f"   💥 CRITICAL: Optimizer param count mismatch!")
        else:
            logger.info(f"   ✅ Optimizer parameter count matches model trainable parameters")
        logger.info("=" * 80)

    def _log_parameter_trainability_check(self) -> None:
        """Check and log which parameters are trainable vs frozen."""
        logger.info("🔍 PARAMETER TRAINABILITY CHECK:")
        predictor_trainable = predictor_frozen = encoder_trainable = encoder_frozen = 0
        
        for name, param in self.encoder.named_parameters():
            if 'column_predictor' in name or 'joint_predictor' in name:
                if param.requires_grad:
                    predictor_trainable += 1
                else:
                    predictor_frozen += 1
                    logger.warning(f"   ❌ PREDICTOR FROZEN: {name}")
            elif 'joint_encoder' in name or 'column_encoder' in name:
                if param.requires_grad:
                    encoder_trainable += 1
                else:
                    encoder_frozen += 1
                    logger.warning(f"   ❌ ENCODER FROZEN: {name}")
        
        logger.info(f"   Predictors: {predictor_trainable} trainable, {predictor_frozen} frozen")
        logger.info(f"   Encoders: {encoder_trainable} trainable, {encoder_frozen} frozen")
        
        if predictor_frozen > 0:
            logger.error(f"💥 CRITICAL: {predictor_frozen} predictor parameters are FROZEN!")
        if encoder_frozen > 0:
            logger.error(f"💥 CRITICAL: {encoder_frozen} encoder parameters are FROZEN!")

    def _recreate_optimizer_and_schedulers_for_resume(
        self,
        optimizer_params: dict,
        n_epochs: int,
        batches_per_epoch: int,
        existing_epochs: int,
        base_epoch_index: int,
        use_lr_scheduler: bool,
        lr_schedule_segments,
        enable_dropout_scheduler: bool,
        dropout_schedule_type: str,
        initial_dropout: float,
        final_dropout: float,
        data_loader,
    ) -> Tuple:
        """
        Recreate optimizer and schedulers from checkpoint state dicts.
        
        Returns:
            Tuple of (optimizer, scheduler, dropout_scheduler)
        """
        logger.warning("🔄 Recreating optimizer and scheduler from checkpoint state dicts")
        
        # Create fresh optimizer
        optimizer_params = optimizer_params or {"lr": 0.001, "weight_decay": 1e-4}
        optimizer = torch.optim.AdamW(self.encoder.parameters(), **optimizer_params)
        
        # Load saved state dict if available
        if "optimizer" in self.training_state and self.training_state["optimizer"] is not None:
            try:
                optimizer.load_state_dict(self.training_state["optimizer"])
                logger.info("✅ Successfully loaded optimizer state from checkpoint")
            except Exception as e:
                logger.warning(f"⚠️  Failed to load optimizer state: {e}, using fresh optimizer")
        
        # Create scheduler
        scheduler = None
        if use_lr_scheduler:
            if lr_schedule_segments is not None:
                scheduler = LambdaLR(optimizer, lr_lambda=self._get_lambda_lr(lr_schedule_segments))
            else:
                # Use LRTimeline for intelligent adaptive scheduling (same as fresh training)
                # CRITICAL: For K-fold CV, use TOTAL expected epochs, not just this fold's epochs
                scheduler_n_epochs = n_epochs
                if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                    scheduler_n_epochs = self._kv_fold_epoch_offset + n_epochs
                    logger.info(f"📐 K-fold CV scheduler (recovery): total_epochs={scheduler_n_epochs}")
                
                # Create LRTimeline with custom 4-phase schedule (same as fresh training)
                max_lr = optimizer_params["lr"]
                base_lr = max_lr / 10.0  # Start from 10% of max LR
                min_lr = max_lr / 100.0  # End at 1% of max LR
                
                scheduler = LRTimeline(
                    n_epochs=scheduler_n_epochs,
                    base_lr=base_lr,
                    max_lr=max_lr,
                    min_lr=min_lr,
                    aggressive_warmup_pct=0.05,  # 5% aggressive ramp
                    gentle_warmup_pct=0.05,      # 5% gentle ramp
                    onecycle_pct=0.50,           # 50% OneCycle productive phase
                )
                
                logger.info(f"🔄 LRTimeline (recovery): {scheduler_n_epochs} epochs, base_lr={base_lr:.2e}, max_lr={max_lr:.2e}, min_lr={min_lr:.2e}")
            
            # Load and correct scheduler state
            if "scheduler" in self.training_state and self.training_state["scheduler"] is not None:
                try:
                    scheduler.load_state_dict(self.training_state["scheduler"])
                    
                    # Fix current_epoch to match resume position (LRTimeline uses current_epoch, not last_epoch)
                    if isinstance(scheduler, LRTimeline):
                        # LRTimeline tracks epochs, not batch steps
                        correct_current_epoch = existing_epochs
                        if scheduler.current_epoch != correct_current_epoch:
                            logger.warning(f"⚠️ Correcting LRTimeline current_epoch: {scheduler.current_epoch} → {correct_current_epoch}")
                            scheduler.current_epoch = correct_current_epoch
                        
                        # Also fix n_epochs if needed (for K-fold CV)
                        scheduler_n_epochs_for_correction = n_epochs
                        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                            scheduler_n_epochs_for_correction = self._kv_fold_epoch_offset + n_epochs
                        
                        if scheduler.n_epochs != scheduler_n_epochs_for_correction:
                            logger.warning(f"⚠️ Correcting LRTimeline n_epochs: {scheduler.n_epochs} → {scheduler_n_epochs_for_correction}")
                            scheduler.n_epochs = scheduler_n_epochs_for_correction
                    
                    logger.info("✅ Successfully loaded scheduler state from checkpoint")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load scheduler state: {e}, using fresh scheduler")
        
        # Create and restore dropout scheduler
        dropout_scheduler = None
        if enable_dropout_scheduler and "dropout_scheduler" in self.training_state and self.training_state["dropout_scheduler"] is not None:
            try:
                dropout_scheduler = create_dropout_scheduler(
                    schedule_type=dropout_schedule_type,
                    initial_dropout=initial_dropout,
                    final_dropout=final_dropout,
                    total_epochs=n_epochs
                )
                dropout_scheduler.load_state_dict(self.training_state["dropout_scheduler"])
                logger.info("✅ Successfully loaded dropout scheduler state from checkpoint")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load dropout scheduler state: {e}, will create fresh scheduler later")
                dropout_scheduler = None
        
        logger.info(f"🚀 Recovery complete: optimizer, scheduler, and dropout scheduler properly recreated")
        return optimizer, scheduler, dropout_scheduler

    def _recreate_dataloaders_for_resume(
        self, batch_size: int, data_loader, val_dataloader, batches_per_epoch: int
    ) -> Tuple[DataLoader, DataLoader, int]:
        """
        Recreate DataLoaders during checkpoint resume (they can't be serialized).
        
        Returns:
            Tuple of (data_loader, val_dataloader, batches_per_epoch)
        """
        # Recreate train data_loader if it's None
        if data_loader is None:
            logger.warning("=" * 80)
            logger.warning("🔄 DATA_LOADER IS NONE - RECREATING FROM SCRATCH (CHECKPOINT RESUME)")
            logger.warning("=" * 80)
            if self.train_input_data.project_row_meta_data_list is None:
                train_dl_kwargs = create_dataloader_kwargs(
                    batch_size=batch_size, shuffle=True, drop_last=True,
                    dataset_size=len(self.train_input_data.df),
                    num_columns=len(self.train_input_data.df.columns),
                )
                logger.info(f"📦 Checkpoint Resume DataLoader kwargs: {train_dl_kwargs}")
                data_loader = DataLoader(
                    self.train_dataset, collate_fn=collate_tokens, **train_dl_kwargs
                )
                logger.info(f"✅ Recreated regular DataLoader with num_workers={train_dl_kwargs.get('num_workers', 0)}")
                logger.warning("=" * 80)
            else:
                sampler = DataSpaceBatchSampler(batch_size, self.train_input_data)
                sampler_dl_kwargs = create_dataloader_kwargs(
                    batch_size=batch_size, shuffle=False, drop_last=False,
                    dataset_size=len(self.train_input_data.df),
                    num_columns=len(self.train_input_data.df.columns),
                )
                sampler_dl_kwargs.pop('batch_size', None)
                sampler_dl_kwargs.pop('shuffle', None)
                sampler_dl_kwargs.pop('drop_last', None)
                logger.info(f"📦 Checkpoint Resume BatchSampler kwargs: {sampler_dl_kwargs}")
                data_loader = DataLoader(
                    self.train_dataset, batch_sampler=sampler, collate_fn=collate_tokens, **sampler_dl_kwargs
                )
                logger.info(f"✅ Recreated DataSpaceBatchSampler DataLoader with num_workers={sampler_dl_kwargs.get('num_workers', 0)}")
        
        # Recreate val_dataloader if it's None
        if val_dataloader is None:
            logger.warning("val_dataloader is None, recreating from scratch")
            val_num_workers = None
            if is_gpu_available():
                try:
                    reserved = get_gpu_memory_reserved()
                    total_memory = (get_gpu_device_properties(0).total_memory / (1024**3)) if get_gpu_device_properties(0) else 0.0
                    free_vram = total_memory - reserved
                    
                    worker_vram_gb = 0.6
                    safety_margin_gb = 20.0
                    available_for_workers = max(0, free_vram - safety_margin_gb)
                    max_workers_by_vram = int(available_for_workers / worker_vram_gb)
                    
                    from featrix.neural.dataloader_utils import get_optimal_num_workers
                    default_workers = get_optimal_num_workers(dataset_size=len(self.val_input_data.df))
                    
                    max_val_workers = 2 if total_memory <= 16 else 4
                    val_num_workers = min(default_workers, max_workers_by_vram, max_val_workers)
                    val_num_workers = max(0, val_num_workers)
                    
                    logger.info(f"🔍 Validation worker calculation: free_vram={free_vram:.1f}GB, total_memory={total_memory:.1f}GB → {val_num_workers} workers (max {max_val_workers})")
                except Exception as e:
                    logger.warning(f"Could not calculate optimal validation workers: {e}, using 0")
                    val_num_workers = 0
            
            val_dl_kwargs = create_dataloader_kwargs(
                batch_size=batch_size, shuffle=True, drop_last=True,
                num_workers=val_num_workers,
                dataset_size=len(self.val_input_data.df),
                num_columns=len(self.val_input_data.df.columns),
            )
            logger.info(f"📦 Checkpoint Resume Validation DataLoader kwargs: {val_dl_kwargs}")
            val_dataloader = DataLoader(self.val_dataset, collate_fn=collate_tokens, **val_dl_kwargs)
            logger.info(f"✅ Recreated validation DataLoader with num_workers={val_dl_kwargs.get('num_workers', 0)}")
        
        # Recalculate batches_per_epoch from recreated data loader
        if data_loader is not None:
            if self.train_input_data.project_row_meta_data_list is None:
                recalculated_batches = len(data_loader)
            else:
                recalculated_batches = int(math.ceil(len(self.train_dataset) / batch_size))
            
            if recalculated_batches != batches_per_epoch:
                logger.warning(
                    f"batches_per_epoch mismatch: restored={batches_per_epoch}, "
                    f"recalculated={recalculated_batches}. Using recalculated value."
                )
                batches_per_epoch = recalculated_batches
            
            if batches_per_epoch <= 0:
                raise ValueError(
                    f"Cannot recover training with batches_per_epoch={batches_per_epoch}. "
                    f"Dataset has {len(self.train_dataset)} samples, batch_size={batch_size}."
                )
            
            logger.info(f"Validated batches_per_epoch: {batches_per_epoch} from recreated DataLoader")
        
        return data_loader, val_dataloader, batches_per_epoch

    def _prepare_datasets_for_training(
        self, batch_size: int, quick_search_mode: bool, max_pre_analysis_data_size: int
    ) -> None:
        """
        Prepare train and validation datasets for training.
        Handles subsampling for quick_search_mode and duplication for small datasets.
        """
        # Handle training dataset
        train_dataset_size = len(self.train_dataset)
        
        # Subsample if dataset is too large (only for quick_search_mode)
        if quick_search_mode and train_dataset_size > max_pre_analysis_data_size:
            logger.warning(
                f"⚠️  Dataset too large: {train_dataset_size} samples > {max_pre_analysis_data_size}. "
                f"Subsampling to {max_pre_analysis_data_size} records."
            )
            sampled_indices = self.train_input_data.df.sample(
                n=max_pre_analysis_data_size, random_state=42
            ).index.tolist()
            sampled_indices.sort()
            
            train_df_sampled = self.train_input_data.df.iloc[sampled_indices].reset_index(drop=True)
            sampled_row_meta = None
            if self.train_input_data.project_row_meta_data_list is not None and len(self.train_input_data.project_row_meta_data_list) > 0:
                sampled_row_meta = [
                    self.train_input_data.project_row_meta_data_list[i] 
                    for i in sampled_indices 
                    if i < len(self.train_input_data.project_row_meta_data_list)
                ]
            sampled_casted_df = None
            if self.train_input_data.casted_df is not None:
                sampled_casted_df = self.train_input_data.casted_df.iloc[sampled_indices].reset_index(drop=True)
            
            self.train_dataset = SuperSimpleSelfSupervisedDataset(
                train_df_sampled, codecs=self.col_codecs,
                row_meta_data=sampled_row_meta, casted_df=sampled_casted_df
            )
            train_dataset_size = len(self.train_dataset)
            logger.info(f"✅ Train dataset subsampled to {train_dataset_size} samples")
        
        # Duplicate if dataset is too small
        if train_dataset_size < batch_size:
            logger.warning(
                f"⚠️  Dataset too small: {train_dataset_size} samples < batch_size {batch_size}. "
                f"Duplicating rows to ensure at least one batch."
            )
            duplication_factor = math.ceil(batch_size / train_dataset_size)
            logger.info(f"📋 Duplicating dataset {duplication_factor}x to reach at least {batch_size} samples")
            
            current_train_df = self.train_dataset.df if hasattr(self.train_dataset, 'df') else self.train_input_data.df
            current_row_meta = self.train_dataset.row_meta_data if hasattr(self.train_dataset, 'row_meta_data') else self.train_input_data.project_row_meta_data_list
            current_casted_df = self.train_dataset.casted_df if hasattr(self.train_dataset, 'casted_df') else self.train_input_data.casted_df
            
            duplicated_train_df = pd.concat([current_train_df] * duplication_factor, ignore_index=True)
            duplicated_row_meta = current_row_meta * duplication_factor if current_row_meta else None
            duplicated_casted_df = pd.concat([current_casted_df] * duplication_factor, ignore_index=True) if current_casted_df is not None else None
            
            self.train_dataset = SuperSimpleSelfSupervisedDataset(
                duplicated_train_df, codecs=self.col_codecs,
                row_meta_data=duplicated_row_meta, casted_df=duplicated_casted_df
            )
            logger.info(f"✅ Train dataset duplicated: {train_dataset_size} → {len(self.train_dataset)} samples")
        
        # Handle validation dataset
        val_dataset_size = len(self.val_dataset)
        
        # Subsample if dataset is too large (only for quick_search_mode)
        if quick_search_mode and val_dataset_size > max_pre_analysis_data_size:
            logger.warning(
                f"⚠️  Validation dataset too large: {val_dataset_size} samples > {max_pre_analysis_data_size}. "
                f"Subsampling to {max_pre_analysis_data_size} records."
            )
            sampled_val_indices = self.val_input_data.df.sample(
                n=max_pre_analysis_data_size, random_state=42
            ).index.tolist()
            sampled_val_indices.sort()
            
            val_df_sampled = self.val_input_data.df.iloc[sampled_val_indices].reset_index(drop=True)
            sampled_val_row_meta = None
            if self.val_input_data.project_row_meta_data_list is not None and len(self.val_input_data.project_row_meta_data_list) > 0:
                sampled_val_row_meta = [
                    self.val_input_data.project_row_meta_data_list[i]
                    for i in sampled_val_indices
                    if i < len(self.val_input_data.project_row_meta_data_list)
                ]
            sampled_val_casted_df = None
            if self.val_input_data.casted_df is not None:
                sampled_val_casted_df = self.val_input_data.casted_df.iloc[sampled_val_indices].reset_index(drop=True)
            
            self.val_dataset = SuperSimpleSelfSupervisedDataset(
                val_df_sampled, codecs=self.col_codecs,
                row_meta_data=sampled_val_row_meta, casted_df=sampled_val_casted_df
            )
            val_dataset_size = len(self.val_dataset)
            logger.info(f"✅ Validation dataset subsampled to {val_dataset_size} samples")
        
        # Duplicate if dataset is too small
        if val_dataset_size < batch_size:
            logger.warning(
                f"⚠️  Validation dataset too small: {val_dataset_size} samples < batch_size {batch_size}. "
                f"Duplicating rows to ensure at least one batch."
            )
            duplication_factor = math.ceil(batch_size / val_dataset_size)
            logger.info(f"📋 Duplicating validation dataset {duplication_factor}x to reach at least {batch_size} samples")
            
            current_val_df = self.val_dataset.df if hasattr(self.val_dataset, 'df') else self.val_input_data.df
            current_val_row_meta = self.val_dataset.row_meta_data if hasattr(self.val_dataset, 'row_meta_data') else self.val_input_data.project_row_meta_data_list
            current_val_casted_df = self.val_dataset.casted_df if hasattr(self.val_dataset, 'casted_df') else self.val_input_data.casted_df
            
            duplicated_val_df = pd.concat([current_val_df] * duplication_factor, ignore_index=True)
            duplicated_val_row_meta = current_val_row_meta * duplication_factor if current_val_row_meta else None
            duplicated_val_casted_df = pd.concat([current_val_casted_df] * duplication_factor, ignore_index=True) if current_val_casted_df is not None else None
            
            self.val_dataset = SuperSimpleSelfSupervisedDataset(
                duplicated_val_df, codecs=self.col_codecs,
                row_meta_data=duplicated_val_row_meta, casted_df=duplicated_val_casted_df
            )
            logger.info(f"✅ Validation dataset duplicated: {val_dataset_size} → {len(self.val_dataset)} samples")

    def _build_epoch_timeline_entry(
        self, epoch_idx: int, val_loss: float, val_components: dict, 
        d: dict, current_lr, lr_boost_multiplier: float, temp_boost_multiplier: float,
        batch_size: int, val_set_rotated: bool, loss_dict: dict
    ) -> dict:
        """Build epoch timeline entry with all metrics."""
        # Get learning rate
        lr_value = float(current_lr[0] if isinstance(current_lr, list) else current_lr) if current_lr is not None else None
        
        current_dropout = d.get("current_dropout")
        current_dropout = float(current_dropout) if current_dropout is not None else None
        
        current_train_loss = d.get("current_loss")
        current_train_loss = float(current_train_loss) if isinstance(current_train_loss, (int, float)) else None
        
        current_val = float(val_loss) if isinstance(val_loss, (int, float)) else None
        
        # Get gradient info
        gradient_info = {}
        for attr, key in [('_latest_gradient_norm', 'unclipped_norm'), 
                          ('_latest_gradient_clipped', 'clipped_norm'),
                          ('_latest_gradient_ratio', 'clip_ratio')]:
            val = getattr(self, attr, None)
            if val is not None:
                gradient_info[key] = float(val.item()) if hasattr(val, 'item') else float(val)
        
        # Get spread temperature
        spread_temp = getattr(self.encoder, '_last_spread_temp', None)
        if spread_temp is not None:
            spread_temp = float(spread_temp.item()) if hasattr(spread_temp, 'item') else float(spread_temp)
        
        # Get spread loss
        spread_loss_total = None
        if hasattr(loss_dict, 'get') and loss_dict and 'spread_loss' in loss_dict:
            spread_loss_data = loss_dict['spread_loss']
            spread_loss_total = spread_loss_data.get('total')
            if spread_loss_total is not None:
                spread_loss_total = float(spread_loss_total.item()) if hasattr(spread_loss_total, 'item') else float(spread_loss_total)
        
        # Get collapse diagnostics (for embedding std tracking)
        collapse_diagnostics = None
        if hasattr(loss_dict, 'get') and loss_dict and 'collapse_diagnostics' in loss_dict:
            collapse_diagnostics = loss_dict.get('collapse_diagnostics')
            # Only store if it's a dict and doesn't have errors
            if not isinstance(collapse_diagnostics, dict) or 'error' in collapse_diagnostics:
                collapse_diagnostics = None
        
        # Get column loss std (from relationship extractor)
        column_loss_std = None
        try:
            rel_extractor = getattr(getattr(self.encoder, 'joint_encoder', None), 'relationship_extractor', None)
            if rel_extractor and hasattr(rel_extractor, 'col_marginal_losses') and rel_extractor.col_marginal_losses:
                loss_values = np.array(list(rel_extractor.col_marginal_losses.values()))
                if len(loss_values) > 1:
                    column_loss_std = float(np.std(loss_values))
        except Exception:
            pass  # Fail silently if we can't get column loss std
        
        # Apply K-fold CV offset
        cumulative_epoch = epoch_idx
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
        
        return {
            "epoch": cumulative_epoch,
            "learning_rate": lr_value,
            "lr_multiplier": lr_boost_multiplier,
            "batch_size": batch_size,
            "val_set_rotated": val_set_rotated,
            "train_loss": current_train_loss,
            "validation_loss": current_val,
            "val_loss_components": val_components,
            "dropout_rate": current_dropout,
            "gradient_norm": gradient_info.get('unclipped_norm'),
            "gradients": gradient_info,
            "spread_loss": spread_loss_total,
            "spread_temperature": spread_temp,
            "temp_multiplier": temp_boost_multiplier,
            "failures_detected": [],
            "early_stop_blocked": False,
            "corrective_actions": [],
            "weightwatcher": None,
            "collapse_diagnostics": collapse_diagnostics,
            "column_loss_std": column_loss_std
        }

    def _shutdown_training_workers(self, data_loader, epoch_idx, batch_size):
        """Shutdown training dataloader workers to free VRAM for validation."""
        if not hasattr(data_loader, 'num_workers') or data_loader.num_workers == 0:
            return False, None
        
        try:
            logger.info(f"💾 Large validation set ({len(self.val_input_data.df)} rows) - temporarily shutting down training workers to free VRAM")
            
            train_dl_kwargs_backup = {
                'batch_size': batch_size,
                'shuffle': True,
                'drop_last': True,
                'num_workers': data_loader.num_workers,
            }
            
            _cleanup_dataloader_workers(data_loader, "training DataLoader")
            
            import gc
            gc.collect()
            if is_gpu_available():
                empty_gpu_cache()
                synchronize_gpu()
            
            logger.info(f"✅ Training workers shut down, VRAM freed for validation")
            return True, train_dl_kwargs_backup
        except Exception as e:
            logger.warning(f"Failed to shut down training workers: {e}")
            return False, None

    def _recreate_training_dataloader(self, train_dl_kwargs_backup: dict, epoch_idx: int, collate_tokens):
        """Recreate training dataloader after validation."""
        from featrix.neural.dataloader_utils import create_dataloader_kwargs
        
        logger.info(f"🔄 Recreating training dataloader after validation")
        
        train_dl_kwargs = create_dataloader_kwargs(
            batch_size=train_dl_kwargs_backup['batch_size'],
            shuffle=train_dl_kwargs_backup['shuffle'],
            drop_last=train_dl_kwargs_backup['drop_last'],
            num_workers=train_dl_kwargs_backup.get('num_workers'),
            dataset_size=len(self.train_input_data.df),
            num_columns=len(self.train_input_data.df.columns),
        )
        data_loader = DataLoader(
            self.train_dataset,
            collate_fn=collate_tokens,
            **train_dl_kwargs
        )
        
        logger.info(f"✅ Training dataloader recreated with {train_dl_kwargs.get('num_workers', 0)} workers")
        return data_loader

    def _check_oom_after_validation(self) -> None:
        """Check for OOM events after validation."""
        try:
            from lib.system_health_monitor import SystemHealthMonitor
            job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
            monitor = SystemHealthMonitor(job_id=job_id)
            oom_events = monitor.check_dmesg_for_oom()
            if oom_events:
                logger.error(f"🚨 DETECTED {len(oom_events)} KERNEL OOM EVENT(S) AFTER VALIDATION:")
                for event in oom_events:
                    logger.error(f"   Killed: {event['victim_process']} (PID {event['victim_pid']}) at {event['timestamp']}")
        except Exception as e:
            logger.debug(f"OOM check failed: {e}")

    def _log_temp_change(self, epoch_idx: int, spread_temp: float, temp_boost_multiplier: float, batch_size: int) -> None:
        """Log significant temperature changes."""
        if not hasattr(self, '_last_spread_temp'):
            self._last_spread_temp = None
        
        if spread_temp is not None and self._last_spread_temp is not None:
            temp_change_pct = ((spread_temp - self._last_spread_temp) / self._last_spread_temp) * 100
            if abs(temp_change_pct) > 10:
                logger.info(f"🌡️  [{epoch_idx}] Temperature changed: {self._last_spread_temp:.4f} → {spread_temp:.4f} ({temp_change_pct:+.1f}%) [temp_mult={temp_boost_multiplier}, batch_size={batch_size}]")
        
        self._last_spread_temp = spread_temp

    def _log_gradient_stats(self, epoch_idx: int, grad_clip_stats: dict, use_adaptive_clipping: bool) -> None:
        """Log per-epoch gradient clipping statistics."""
        total_batches = grad_clip_stats.get("total_batches", 0)
        if total_batches == 0:
            return  # Nothing to log
        
        clipped_batches = grad_clip_stats.get("clipped_batches", 0)
        clip_rate = (clipped_batches / total_batches) * 100
        avg_grad_norm = grad_clip_stats.get("sum_unclipped_norms", 0) / total_batches
        
        # Only log if there's significant clipping activity or at key epochs
        if clipped_batches > 0 or epoch_idx in [0, 4, 9, 24, 49, 99]:
            if use_adaptive_clipping:
                max_ratio = grad_clip_stats.get("max_grad_loss_ratio", 0)
                logger.debug(f"📈 [{epoch_idx+1}] Gradient stats: {clipped_batches}/{total_batches} clipped ({clip_rate:.1f}%), avg_norm={avg_grad_norm:.2f}, max_grad/loss_ratio={max_ratio:.2f}")
            else:
                logger.debug(f"📈 [{epoch_idx+1}] Gradient stats: avg_norm={avg_grad_norm:.2f}, max_norm={grad_clip_stats.get('max_unclipped_norm', 0):.2f}")

    def _log_detailed_val_diagnostics(self, epoch_idx: int, val_loss: float, val_components: dict) -> None:
        """Log detailed validation diagnostics at specific epochs."""
        diagnostic_epochs = [1, 5, 10, 25, 50]
        if epoch_idx not in diagnostic_epochs or not val_components:
            return
        
        logger.info(f"🔬 DETAILED VAL LOSS DIAGNOSTICS (Epoch {epoch_idx}):")
        logger.info(f"   Marginal RAW: {val_components.get('marginal_raw', 'N/A'):.4f} (before normalization)")
        logger.info(f"   Marginal NORMALIZER: {val_components.get('marginal_normalizer', 'N/A'):.2f} (divisor)")
        logger.info(f"   Marginal NORMALIZED: {val_components.get('marginal', 'N/A'):.4f} (after /normalizer)")
        logger.info(f"   Marginal SCALED: {val_components.get('marginal', 'N/A'):.4f} (after *coefficient)")
        logger.info(f"   Marginal WEIGHTED: {val_components.get('marginal_weighted', 'N/A'):.4f} (after *weight)")
        
        normalizer = val_components.get('marginal_normalizer', 1.0)
        if normalizer > 100:
            logger.warning(f"   ⚠️  Large normalizer ({normalizer:.2f}) may be destroying marginal loss gradients!")
        
        # Track improvement from epoch 1
        if not hasattr(self, '_val_loss_epoch1'):
            self._val_loss_epoch1 = {
                'total': val_loss, 'spread': val_components['spread'], 'joint': val_components['joint'],
                'marginal': val_components['marginal'], 'full_j': val_components['spread_full_joint'],
                'full_m1': val_components['spread_full_mask1'], 'full_m2': val_components['spread_full_mask2'],
            }
        else:
            imp = {k: self._val_loss_epoch1[k] - val_components.get(k, val_components.get('spread_full_joint' if k == 'full_j' else 'spread_full_mask1' if k == 'full_m1' else 'spread_full_mask2' if k == 'full_m2' else k, 0))
                   for k in ['total', 'spread', 'joint', 'marginal']}
            imp['total'] = self._val_loss_epoch1['total'] - val_loss
            logger.info(f"   📈 IMPROVEMENT SINCE EPOCH 1:")
            logger.info(f"      Total: {imp['total']:+.4f} ({100*imp['total']/self._val_loss_epoch1['total']:+.2f}%)")
            for k in ['spread', 'joint', 'marginal']:
                pct = 100 * imp[k] / self._val_loss_epoch1[k] if self._val_loss_epoch1[k] != 0 else 0
                logger.info(f"      {k.capitalize()}: {imp[k]:+.4f} ({pct:+.2f}%)")
            
            if abs(imp['total']) / self._val_loss_epoch1['total'] < 0.01:
                logger.warning(f"   ⚠️  Total improvement is only {100*abs(imp['total'])/self._val_loss_epoch1['total']:.2f}% - training may be stalled!")

    def _log_epoch_summary(
        self, epoch_idx: int, n_epochs: int, has_failure: bool, failure_type,
        intervention_stage: int, current_train_loss, current_val_loss, lr_value, 
        current_dropout, latest_gradient_norm
    ) -> None:
        """Log a clean epoch summary line."""
        logger.info("─" * 100)
        
        status_symbol = "✅" if not has_failure else "⚠️ "
        failure_label = f" [{failure_type}]" if has_failure and failure_type else ""
        intervention_label = f" I{intervention_stage}" if intervention_stage > 0 else ""
        
        cumulative_epoch = epoch_idx
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
        
        lr_value_str = f"{lr_value:.6f}" if lr_value else "N/A"
        current_dropout_str = f"{current_dropout:0.3f} " if current_dropout else "N/A"
        train_loss_str = f"{current_train_loss:.4f}" if current_train_loss is not None else "N/A"
        val_loss_str = f"{current_val_loss:.4f}" if current_val_loss is not None else "N/A"
        grad_str = f"{latest_gradient_norm:.4f}" if latest_gradient_norm is not None else "N/A"
        
        epoch_str = f"{cumulative_epoch:3d}" if cumulative_epoch is not None else "?"
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            epoch_display = f"{epoch_str}"
        else:
            epochs_str = f"{n_epochs}" if n_epochs is not None else "?"
            epoch_display = f"{epoch_str}/{epochs_str}"
        
        logger.info(
            f"{status_symbol} [{epoch_display}] "
            f"train={train_loss_str} val={val_loss_str} "
            f"lr={lr_value_str} drop={current_dropout_str} "
            f"grad={grad_str}{intervention_label}{failure_label}"
        )

    def _log_validation_loss_components(self, epoch_idx: int, val_loss, val_components, current_lr) -> None:
        """Log validation loss with all components in a compact format."""
        if not val_components:
            logger.info(f"📊 VAL LOSS: {val_loss:.4f}")
            return
        
        # Get current learning rate
        try:
            lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
            if lr_value < 0.0001:
                lr_str = f"lr={lr_value:.8f}"
            elif lr_value < 0.01:
                lr_str = f"lr={lr_value:.6f}"
            else:
                lr_str = f"lr={lr_value:.4f}"
        except Exception:
            lr_str = "lr=N/A"
        
        # Get marginal weight
        try:
            marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
            marginal_weight_str = f"marg_w={marginal_weight:.4f}"
        except Exception:
            marginal_weight_str = "marg_w=N/A"
        
        # Get curriculum phase
        try:
            progress = epoch_idx / self.n_epochs
            curriculum_config = getattr(self.encoder.config.loss_config, 'curriculum_learning', None) if hasattr(self.encoder, 'config') else None
            if curriculum_config is None:
                curriculum_config = self._get_default_curriculum_config()
            
            current_phase, phase_num = None, 0
            for i, phase in enumerate(curriculum_config.phases):
                if phase.start_progress <= progress <= phase.end_progress:
                    current_phase, phase_num = phase, i + 1
                    break
            if current_phase is None and curriculum_config.phases:
                current_phase, phase_num = curriculum_config.phases[-1], len(curriculum_config.phases)
            phase_str = f"phase={phase_num},{current_phase.name}" if current_phase else "phase=N/A"
        except Exception:
            phase_str = "phase=N/A"
        
        # Elapsed time
        try:
            elapsed = time.time() - self.training_start_time
            if elapsed < 60:
                elapsed_str = f"[{int(elapsed)}s]"
            elif elapsed < 3600:
                elapsed_str = f"[{int(elapsed//60)}m {int(elapsed%60)}s]"
            else:
                elapsed_str = f"[{int(elapsed//3600)}h {int((elapsed%3600)//60)}m]"
        except Exception:
            elapsed_str = ""
        
        marginal_pct = val_components.get('marginal_normalized', 0.0) * 100
        logger.info(
            f"📊 [{phase_str}] {elapsed_str} VAL LOSS: {val_loss:.4f} {lr_str} {marginal_weight_str} "
            f"(spread={val_components['spread']:.4f}, joint={val_components['joint']:.4f}, "
            f"marginal={val_components['marginal']:.4f}, marginal_weighted={val_components['marginal_weighted']:.4f}, "
            f"marginal_norm={marginal_pct:.0f}% of random)"
        )

    def _log_detailed_val_diagnostics(self, epoch_idx: int, val_loss, val_components) -> None:
        """Log detailed validation diagnostics for specific epochs."""
        if epoch_idx not in [1, 5, 10, 25, 50]:
            return
        
        logger.info(f"🔬 DETAILED VAL LOSS DIAGNOSTICS (Epoch {epoch_idx}):")
        logger.info(f"   Marginal RAW: {val_components.get('marginal_raw', 0):.4f}")
        logger.info(f"   Marginal NORMALIZER: {val_components.get('marginal_normalizer', 1):.2f}")
        logger.info(f"   Marginal WEIGHTED: {val_components.get('marginal_weighted', 0):.4f}")
        
        normalizer = val_components.get('marginal_normalizer', 1.0)
        if normalizer > 100:
            logger.warning(f"   ⚠️  Large normalizer ({normalizer:.2f}) may destroy gradients!")
        
        # Track improvements from epoch 1
        if not hasattr(self, '_val_loss_epoch1'):
            self._val_loss_epoch1 = {
                'total': val_loss, 'spread': val_components['spread'],
                'joint': val_components['joint'], 'marginal': val_components['marginal'],
            }
        else:
            e1 = self._val_loss_epoch1
            impr = {k: e1[k] - val_components.get(k, val_loss if k == 'total' else 0) for k in ['total', 'spread', 'joint', 'marginal']}
            impr['total'] = e1['total'] - val_loss
            logger.info(f"   📈 IMPROVEMENT SINCE EPOCH 1: total={impr['total']:+.4f} spread={impr['spread']:+.4f} joint={impr['joint']:+.4f} marginal={impr['marginal']:+.4f}")

    def _init_val_loss_tracker(self, val_loss_early_stop_patience: int, val_loss_min_delta: float) -> None:
        """Initialize validation loss early stopping tracker."""
        if not hasattr(self, '_val_loss_tracker'):
            self._val_loss_tracker = {
                'best_val_loss': float('inf'),
                'epochs_without_improvement': 0,
                'patience': val_loss_early_stop_patience,
                'min_delta': val_loss_min_delta,
                'best_spread': float('inf'),
                'best_joint': float('inf'),
                'best_marginal': float('inf'),
                'spread_no_improvement': 0,
                'joint_no_improvement': 0,
                'marginal_no_improvement': 0,
                'lr_history': [],
                'marginal_weight_history': []
            }
            logger.info(f"📊 Validation loss early stopping initialized: patience={val_loss_early_stop_patience}, min_delta={val_loss_min_delta}")
            logger.info(f"📊 Component-level tracking enabled: spread, joint, marginal losses")
        
        if not hasattr(self, '_spread_only_tracker'):
            self._spread_only_tracker = {
                'spread_only_epochs_completed': 0,
                'in_spread_phase': False
            }
        
        # Initialize early stop block logged flag
        if not hasattr(self, '_early_stop_block_logged'):
            self._early_stop_block_logged = False

    def _track_component_improvements(self, epoch_idx: int, val_components: dict) -> None:
        """Track improvements in individual loss components (spread, joint, marginal)."""
        if not val_components:
            return
        
        for comp_name in ['spread', 'joint', 'marginal']:
            if comp_name not in val_components:
                continue
            
            comp_val = val_components[comp_name]
            best_key = f'best_{comp_name}'
            no_improve_key = f'{comp_name}_no_improvement'
            
            prev_loss = self._val_loss_tracker.get(f'{comp_name}_prev', comp_val)
            
            if f'{comp_name}_start' not in self._val_loss_tracker:
                self._val_loss_tracker[f'{comp_name}_start'] = comp_val
            
            history_key = f'{comp_name}_history'
            if history_key not in self._val_loss_tracker:
                self._val_loss_tracker[history_key] = []
            self._val_loss_tracker[history_key].append((epoch_idx, comp_val))
            
            min_delta = self._val_loss_tracker['min_delta']
            if comp_val < self._val_loss_tracker[best_key] - min_delta:
                self._val_loss_tracker[best_key] = comp_val
                self._val_loss_tracker[no_improve_key] = 0
            else:
                self._val_loss_tracker[no_improve_key] += 1
            
            # Log time-moving values
            history = self._val_loss_tracker[history_key]
            nums = get_time_moving_loss_values(history, epoch_idx, prev_loss)
            nums.append(f"{comp_val:8.6f}")
            logger.info(f"{comp_name.capitalize():8s}: {' '.join(nums)}")
            
            if comp_name == 'marginal' and self._val_loss_tracker.get(no_improve_key, 0) >= 5:
                try:
                    mw = self.encoder.config.loss_config.marginal_loss_weight
                    logger.warning(f"⚠️  Marginal loss hasn't improved for {self._val_loss_tracker[no_improve_key]} epochs, weight={mw:.4f}")
                except Exception:
                    pass
            
            self._val_loss_tracker[f'{comp_name}_prev'] = comp_val

    def _check_val_loss_early_stopping(
        self, epoch_idx: int, n_epochs: int, val_loss, val_components: dict,
        scheduler, optimizer, dropout_scheduler, d: dict, print_callback,
        training_event_callback, training_event_dict: dict, max_progress: int, current_lr
    ) -> bool:
        """
        Check validation loss early stopping conditions.
        
        Returns:
            True if training should stop, False otherwise.
        """
        if not isinstance(val_loss, (int, float)) or val_loss <= 0:
            return False
        
        # Track component improvements
        self._track_component_improvements(epoch_idx, val_components)
        
        # Track LR and marginal weight history
        lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
        try:
            current_mw = self.encoder.config.loss_config.marginal_loss_weight
        except Exception:
            current_mw = 0.0
        
        self._val_loss_tracker['lr_history'].append((epoch_idx, lr_value))
        self._val_loss_tracker['marginal_weight_history'].append((epoch_idx, current_mw))
        
        # Log LR and marginal weight time series
        self._log_lr_and_mw_timeseries(epoch_idx, lr_value, current_mw)
        
        # Determine minimum epoch for early stop
        min_epoch = 50
        
        if epoch_idx < min_epoch:
            if epoch_idx == 50 or epoch_idx % 20 == 0:
                logger.info(f"⏭️  Early stopping DISABLED until epoch {min_epoch}")
            return False
        
        # Check validation loss change
        prev_val = self._val_loss_tracker.get('val_prev', val_loss)
        min_delta = self._val_loss_tracker['min_delta']
        
        if 'val_start' not in self._val_loss_tracker:
            self._val_loss_tracker['val_start'] = val_loss
        
        if 'val_history' not in self._val_loss_tracker:
            self._val_loss_tracker['val_history'] = []
        self._val_loss_tracker['val_history'].append((epoch_idx, val_loss))
        
        if val_loss < self._val_loss_tracker['best_val_loss'] - min_delta:
            self._val_loss_tracker['best_val_loss'] = val_loss
            self._val_loss_tracker['epochs_without_improvement'] = 0
        else:
            self._val_loss_tracker['epochs_without_improvement'] += 1
        
        self._val_loss_tracker['val_prev'] = val_loss
        
        # Log val loss time series
        history = self._val_loss_tracker['val_history']
        nums = get_time_moving_loss_values(history, epoch_idx, prev_val)
        nums.append(f"{val_loss:8.4f}")
        logger.info(f"Val loss  : {' '.join(nums)}")
        
        # Check if early stopping is blocked
        if self._is_early_stop_blocked(epoch_idx):
            return False
        
        # Check if any component is still improving
        training_progress = epoch_idx / n_epochs if n_epochs > 0 else 0.0
        if training_progress >= 0.25 and val_components:
            marginal_stale = self._val_loss_tracker.get('marginal_no_improvement', 999)
            if marginal_stale < (self._val_loss_tracker['patience'] // 2):
                logger.info(f"🔄 Marginal loss still improving (stale: {marginal_stale}) - continuing")
                return False
        
        # Check patience threshold
        total_stale = self._val_loss_tracker['epochs_without_improvement']
        if total_stale < self._val_loss_tracker['patience']:
            return False
        
        # Early stopping triggered - handle finalization phase
        return self._handle_val_loss_early_stop(
            epoch_idx, val_loss, val_components, optimizer, scheduler, dropout_scheduler,
            d, print_callback, training_event_callback, training_event_dict, max_progress
        )

    def _is_early_stop_blocked(self, epoch_idx: int) -> bool:
        """Check if early stopping is blocked due to recent NO_LEARNING warning."""
        if not hasattr(self, '_no_learning_tracker') or 'last_no_learning_epoch' not in self._no_learning_tracker:
            return False
        
        epochs_since = epoch_idx - self._no_learning_tracker['last_no_learning_epoch']
        min_required = self._no_learning_tracker.get('min_epochs_before_early_stop', 10)
        
        if epochs_since < min_required:
            remaining = min_required - epochs_since
            logger.info(f"🚫 Early stopping BLOCKED: {remaining} more epochs required after NO_LEARNING")
            return True
        return False

    def _handle_val_loss_early_stop(
        self, epoch_idx: int, val_loss, val_components: dict,
        optimizer, scheduler, dropout_scheduler, d: dict, print_callback,
        training_event_callback, training_event_dict: dict, max_progress: int
    ) -> bool:
        """Handle validation loss early stopping logic including finalization phase."""
        spread_epochs = self._spread_only_tracker.get('spread_only_epochs_completed', 0)
        FINALIZATION_EPOCHS = 5
        
        if spread_epochs < FINALIZATION_EPOCHS:
            if not hasattr(self, '_forced_spread_finalization'):
                self._forced_spread_finalization = True
                self._finalization_start_epoch = epoch_idx
                self.encoder.config.loss_config.spread_loss_weight = 1.0
                self.encoder.config.loss_config.marginal_loss_weight = 0.1
                self.encoder.config.loss_config.joint_loss_weight = 1.0
                logger.warning(f"⚡ [{epoch_idx+1}] FORCED EARLY FINALIZATION: spread+joint focus for {FINALIZATION_EPOCHS} epochs")
            return False
        
        if not getattr(self, '_forced_spread_finalization', False):
            return False
        
        logger.info(f"🛑 EARLY STOPPING: Val loss hasn't improved for {self._val_loss_tracker['patience']} epochs")
        logger.info(f"   Best: {self._val_loss_tracker['best_val_loss']:.4f}, Current: {val_loss:.4f}")
        
        try:
            self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
            logger.info("💾 Final model saved")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save final checkpoint: {e}")
        
        d["progress_counter"] = max_progress
        d["status"] = "early_stopped"
        d["early_stopping"] = True
        d["early_stop_reason"] = "validation_loss_plateau"
        
        if print_callback:
            d["time_now"] = time.time()
            print_callback(d)
        
        if training_event_callback:
            training_event_dict["early_stopped"] = True
            training_event_dict["progress_counter"] = max_progress
            training_event_callback(training_event_dict)
        
        return True

    def _log_lr_and_mw_timeseries(self, epoch_idx: int, lr_value, mw_value) -> None:
        """Log LR and marginal weight time series."""
        # Log LR time series
        lr_nums = get_time_moving_loss_values(self._val_loss_tracker['lr_history'], epoch_idx, lr_value)
        lr_nums.append(f"{lr_value:8.6f}")
        logger.info(f"{'LR':8s}: {' '.join(lr_nums)}")
        
        # Log marginal weight time series
        mw_nums = get_time_moving_loss_values(self._val_loss_tracker['marginal_weight_history'], epoch_idx, mw_value)
        mw_nums.append(f"{mw_value:8.6f}")
        logger.info(f"{'Marg Wt':8s}: {' '.join(mw_nums)}")

    def _run_epoch_diagnostics(self, epoch_idx: int, val_loss, val_components: dict, loss_dict: dict) -> None:
        """Run all per-epoch diagnostics and logging."""
        # Detect stuck losses
        self._check_loss_stuck_detection(epoch_idx, val_components)
        
        # Log MI summary
        self.log_mi_summary(epoch_idx)
        
        # Log epoch summary banner
        self.log_epoch_summary_banner(epoch_idx, val_loss, val_components)
        
        # Log relationship effectiveness (every 5/25 epochs)
        self.log_relationship_effectiveness(epoch_idx, loss_dict)
        
        # Detect capacity bottlenecks (every 50 epochs)
        self.detect_capacity_bottlenecks(epoch_idx, loss_dict)
        
        # Run ablation comparison (every 100 epochs)
        self.log_ablation_comparison(epoch_idx)
        
        # Log mixture logit changes for SetEncoders
        self._log_mixture_logit_changes(epoch_idx)
        
        # Monitor attention head diversity
        self._log_attention_head_diversity(epoch_idx)
        
        # Relationship correlation analysis (every 25 epochs)
        self._log_relationship_correlation_analysis(epoch_idx)
        
        # Log trickiest columns and marginal loss breakdown
        if loss_dict is not None:
            if epoch_idx < 5 or (epoch_idx + 1) % 5 == 0:
                self.log_trickiest_columns(loss_dict, epoch_idx, top_n=None)
            self._log_marginal_loss_breakdown(loss_dict, epoch_idx, 0)
        
        # Debug reconstruction quality periodically
        if epoch_idx > 100 and epoch_idx % 50 == 0:
            self._debug_marginal_reconstruction(epoch_idx)
            self._debug_autoencoding_quality(epoch_idx)
            self._debug_scalar_reconstruction_quality(epoch_idx)

    def _run_failure_detection(
        self, epoch_idx: int, epoch_entry: dict, latest_gradient_norm, lr_value: float
    ):
        """
        Run training failure detection if we have enough history.
        
        Returns:
            Tuple of (has_failure, failure_type, recommendations, current_train_loss, current_val_loss)
        """
        has_failure = False
        failure_type = None
        recommendations = []
        current_train_loss = None
        current_val_loss = None
        
        if epoch_idx < 5 or not hasattr(self, '_training_timeline') or len(self._training_timeline) < 5:
            return has_failure, failure_type, recommendations, current_train_loss, current_val_loss
        
        train_loss_hist = [e.get('train_loss', 0) for e in self._training_timeline 
                          if isinstance(e, dict) and e.get('train_loss') is not None]
        val_loss_hist = [e.get('validation_loss', 0) for e in self._training_timeline 
                        if isinstance(e, dict) and e.get('validation_loss') is not None]
        
        if len(train_loss_hist) < 5 or len(val_loss_hist) < 5:
            return has_failure, failure_type, recommendations, current_train_loss, current_val_loss
        
        current_train_loss = train_loss_hist[-1]
        current_val_loss = val_loss_hist[-1]
        
        # Get gradient norm history for relative comparisons
        gradient_norm_hist = None
        if hasattr(self, '_epoch_grad_norms') and self._epoch_grad_norms:
            gradient_norm_hist = self._epoch_grad_norms
        
        has_failure, failure_type, recommendations = detect_es_training_failure(
            epoch_idx=epoch_idx, train_loss=current_train_loss, val_loss=current_val_loss,
            train_loss_history=train_loss_hist, val_loss_history=val_loss_hist,
            gradient_norm=latest_gradient_norm, lr=lr_value,
            gradient_norm_history=gradient_norm_hist
        )
        
        if has_failure and failure_type:
            epoch_entry["failures_detected"] = failure_type if isinstance(failure_type, list) else [failure_type]
        
        return has_failure, failure_type, recommendations, current_train_loss, current_val_loss

    def _track_failure_warnings(
        self, epoch_idx: int, failure_type, current_train_loss, current_val_loss,
        lr_value, latest_gradient_norm, recommendations
    ) -> None:
        """Track failure warnings in the timeline."""
        failure_list = failure_type if isinstance(failure_type, list) else ([failure_type] if failure_type else [])
        
        # Track NO_LEARNING
        self._track_warning_in_timeline(
            epoch_idx=epoch_idx, warning_type="NO_LEARNING",
            is_active=any("NO_LEARNING" in f for f in failure_list),
            details={"train_loss": current_train_loss, "val_loss": current_val_loss,
                     "lr": lr_value, "gradient_norm": latest_gradient_norm, "recommendations": recommendations}
        )
        
        # Track SEVERE_OVERFITTING
        self._track_warning_in_timeline(
            epoch_idx=epoch_idx, warning_type="SEVERE_OVERFITTING",
            is_active=any("SEVERE_OVERFITTING" in f for f in failure_list),
            details={"train_loss": current_train_loss, "val_loss": current_val_loss,
                     "train_val_gap": current_val_loss - current_train_loss if (current_val_loss and current_train_loss) else None}
        )
        
        # Track DEAD_GRADIENTS
        self._track_warning_in_timeline(
            epoch_idx=epoch_idx, warning_type="DEAD_GRADIENTS",
            is_active=any("DEAD_GRADIENTS" in f or "ZERO_GRADIENTS" in f for f in failure_list),
            details={"gradient_norm": latest_gradient_norm, "lr": lr_value}
        )

    def _check_resolved_warnings(self, epoch_idx: int, has_failure: bool, failure_type, 
                                  current_train_loss, current_val_loss, lr_value) -> None:
        """Check for and resolve warnings that are no longer active."""
        if not hasattr(self, '_active_warnings'):
            return
        
        active_warning_types = set(self._active_warnings.keys())
        current_failure_types = set()
        
        if has_failure and failure_type:
            failure_list = failure_type if isinstance(failure_type, list) else [failure_type]
            if "NO_LEARNING" in str(failure_list):
                current_failure_types.add("NO_LEARNING")
            if "SEVERE_OVERFITTING" in str(failure_list):
                current_failure_types.add("SEVERE_OVERFITTING")
            if "DEAD_GRADIENTS" in str(failure_list) or "ZERO_GRADIENTS" in str(failure_list):
                current_failure_types.add("DEAD_GRADIENTS")
        
        # Check TINY_GRADIENTS
        if getattr(self, '_tiny_grad_warned_this_epoch', False):
            current_failure_types.add("TINY_GRADIENTS")
        elif "TINY_GRADIENTS" in active_warning_types:
            grad = getattr(self, '_latest_gradient_norm', None)
            if grad is not None:
                grad_val = float(grad.item()) if hasattr(grad, 'item') else float(grad)
                if grad_val < 0.001:
                    current_failure_types.add("TINY_GRADIENTS")
        
        # Resolve warnings no longer active
        for warning_type in list(active_warning_types):
            if warning_type not in current_failure_types:
                self._track_warning_in_timeline(
                    epoch_idx=epoch_idx, warning_type=warning_type, is_active=False,
                    details={"train_loss": current_train_loss, "val_loss": current_val_loss, "lr": lr_value}
                )

    def _append_to_timeline(self, epoch_idx: int, epoch_entry: dict) -> None:
        """Append epoch entry to timeline and push to SQLite."""
        self._training_timeline.append(epoch_entry)
        
        if hasattr(self, 'history_db') and self.history_db:
            self.history_db.push_timeline_entry(epoch_idx, epoch_entry)
        
        # Limit timeline to prevent unbounded growth
        max_history = 50
        if len(self._training_timeline) > max_history:
            self._training_timeline = self._training_timeline[-max_history:]

    def _save_timeline_to_json(
        self, epoch_idx: int, n_epochs: int, batch_size: int, optimizer_params: dict,
        scheduler, dropout_scheduler, initial_dropout: float, final_dropout: float
    ) -> None:
        """Save training timeline to JSON file every 5 epochs and generate plot."""
        if n_epochs is None or (epoch_idx % 5 != 0 and epoch_idx != n_epochs - 1):
            return
        
        timeline_path = os.path.join(self.output_dir, "training_timeline.json")
        try:
            with open(timeline_path, 'w') as f:
                json.dump({
                    "timeline": self._training_timeline,
                    "corrective_actions": self._corrective_actions,
                    "metadata": {
                        "initial_lr": optimizer_params.get("lr", 0.001),
                        "total_epochs": n_epochs, "batch_size": batch_size,
                        "scheduler_type": "LRTimeline" if isinstance(scheduler, LRTimeline) else ("LambdaLR" if scheduler else "None"),
                        "dropout_scheduler_enabled": dropout_scheduler is not None,
                        "initial_dropout": initial_dropout if dropout_scheduler else None,
                        "final_dropout": final_dropout if dropout_scheduler else None
                    }
                }, f, indent=2)
            logger.info(f"💾 Training timeline saved to {timeline_path}")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to save training timeline: {e}")
    
    def _plot_training_timeline(self, n_epochs: int, optimizer_params: dict = None) -> None:
        """Plot comprehensive training timeline: loss, LR, and events as PNG.
        
        Delegates to charting module for actual plotting.
        
        Args:
            n_epochs: Total number of epochs
            optimizer_params: Optional optimizer parameters for metadata
        """
        from featrix.neural.charting import plot_training_timeline
        
        if not hasattr(self, '_training_timeline') or not self._training_timeline:
            logger.warning("⚠️  No timeline data available for plotting")
            return
        
        plot_training_timeline(
            training_timeline=self._training_timeline,
            output_dir=self.output_dir,
            n_epochs=n_epochs,
            optimizer_params=optimizer_params,
            training_info=getattr(self, 'training_info', None)
        )

    def _handle_no_learning_intervention(
        self, 
        epoch_idx: int,
        has_failure: bool,
        failure_type,
        failure_changed: bool,
        current_train_loss: float,
        current_val_loss: float,
        val_loss: float,
        lr_boost_multiplier: float,
        temp_boost_multiplier: float,
        intervention_stage: int,
        epochs_since_last_intervention: int,
        epoch_entry: dict,
        d: dict = None  # Progress dict with loss history
    ) -> Tuple[float, float, int, int, bool]:
        """Handle NO_LEARNING failures with intelligent LR controller.
        
        NEW CONTROLLER LOGIC (replaces simple "NO_LEARNING → boost LR"):
        1. If grad norm is tiny AND loss is flat for M epochs → small LR increase (1.05x, cap 1.5x)
        2. If loss is getting worse or loss variance increases → LR decrease (0.5x) and cooldown
        3. If embedding variance collapses → LR decrease + stop boosting, possibly reload best checkpoint
        
        Returns:
            Tuple of (lr_boost_multiplier, temp_boost_multiplier, intervention_stage, 
                     epochs_since_last_intervention, should_break)
        """
        should_break = False
        
        if not (has_failure and failure_type and "NO_LEARNING" in failure_type):
            # Learning is happening - reset interventions if any are active
            if lr_boost_multiplier > 1.0 or temp_boost_multiplier > 1.0:
                old_boost = lr_boost_multiplier
                logger.info(f"✅ [{epoch_idx}] Learning resumed! Resetting LR boost {lr_boost_multiplier:.2f}x → 1.0x")
                lr_boost_multiplier = 1.0
                temp_boost_multiplier = 1.0
                intervention_stage = 0
                self._failure_repeat_count = 0
                self._last_logged_failure = None
                epochs_since_last_intervention = 0
                
                # If using LRTimeline, decrease LR back to normal
                if hasattr(self, '_train_scheduler') and isinstance(self._train_scheduler, LRTimeline):
                    scale_factor = 1.0 / old_boost  # Reverse the boost
                    self._train_scheduler.decrease_lr(
                        current_epoch=epoch_idx,
                        scale_factor=scale_factor,
                        reason=f"Learning resumed, reset from {old_boost:.2f}x boost"
                    )
                    logger.info(f"   → LRTimeline: decreased future LRs by {scale_factor:.2f}x to undo boost")
                
                corrective_action = {
                    "epoch": epoch_idx,
                    "trigger": "LEARNING_RESUMED",
                    "action_type": "RESET_INTERVENTIONS",
                    "details": {
                        "lr_multiplier": 1.0,
                        "temp_multiplier": 1.0,
                        "train_loss": current_train_loss,
                        "val_loss": current_val_loss
                    }
                }
                epoch_entry["corrective_actions"].append(corrective_action)
                self._corrective_actions.append(corrective_action)
            
            return lr_boost_multiplier, temp_boost_multiplier, intervention_stage, epochs_since_last_intervention, should_break
        
        # NO_LEARNING detected
        epochs_since_last_intervention += 1
        
        # ============================================================================
        # INTELLIGENT LR CONTROLLER: Replace simple "NO_LEARNING → boost LR" heuristic
        # ============================================================================
        # Gather diagnostic information for controller decisions
        intervention_made = False
        if not hasattr(self, '_no_learning_tracker'):
            self._no_learning_tracker = {}
        
        # 1. Get gradient norm (from training_info or compute from recent batches)
        avg_grad_norm = None
        grad_norm_tiny = False
        try:
            if hasattr(self, 'training_info') and 'gradient_clip_stats' in self.training_info:
                grad_stats = self.training_info['gradient_clip_stats']
                avg_grad_norm = grad_stats.get('avg_unclipped_norm', None)
                # Consider "tiny" if < 0.01 (very small gradients)
                if avg_grad_norm is not None:
                    grad_norm_tiny = avg_grad_norm < 0.01
        except Exception:
            pass
        
        # 2. Get loss history to compute trends and variance
        loss_history = []
        loss_getting_worse = False
        loss_variance_increasing = False
        loss_flat = False
        try:
            # Try to get from d dict first
            if d is not None and 'loss_history' in d:
                loss_history = d['loss_history']
            # Fallback to history_db
            elif hasattr(self, 'history_db') and self.history_db:
                loss_history = self.history_db.get_recent_loss_history(num_epochs=10)
            
            if loss_history and len(loss_history) >= 5:
                # Get recent validation losses (last M epochs)
                M = 5  # Lookback window
                recent_val_losses = [entry.get('validation_loss', 0) for entry in loss_history[-M:] if entry.get('validation_loss') is not None]
                if len(recent_val_losses) >= 3:
                    # Check if loss is getting worse (increasing trend)
                    if len(recent_val_losses) >= 3:
                        first_half = recent_val_losses[:len(recent_val_losses)//2]
                        second_half = recent_val_losses[len(recent_val_losses)//2:]
                        first_mean = np.mean(first_half)
                        second_mean = np.mean(second_half)
                        # Loss getting worse if second half is significantly higher
                        loss_getting_worse = second_mean > first_mean * 1.05  # 5% increase
                    
                    # Check if loss variance is increasing (instability)
                    if len(recent_val_losses) >= 4:
                        first_half = recent_val_losses[:len(recent_val_losses)//2]
                        second_half = recent_val_losses[len(recent_val_losses)//2:]
                        first_var = np.var(first_half)
                        second_var = np.var(second_half)
                        loss_variance_increasing = second_var > first_var * 1.5  # 50% increase in variance
                    
                    # Check if loss is flat (plateau)
                    loss_range = max(recent_val_losses) - min(recent_val_losses)
                    loss_mean = np.mean(recent_val_losses)
                    # Flat if range is < 2% of mean
                    loss_flat = loss_range < loss_mean * 0.02 if loss_mean > 0 else False
        except Exception as e:
            logger.debug(f"Failed to analyze loss history: {e}")
        
        # 3. Check for embedding collapse (column loss + joint embedding variance)
        column_loss_collapse_detected = False
        embedding_variance_collapse = False
        column_loss_std = None
        collapse_threshold_early = 0.02
        collapse_threshold_late = 0.005
        
        rel_extractor = getattr(getattr(self.encoder, 'joint_encoder', None), 'relationship_extractor', None)
        if rel_extractor and hasattr(rel_extractor, 'col_marginal_losses') and rel_extractor.col_marginal_losses:
            loss_values = np.array(list(rel_extractor.col_marginal_losses.values()))
            if len(loss_values) > 1:
                column_loss_std = float(np.std(loss_values))
                collapse_threshold = collapse_threshold_early if epoch_idx < 30 else collapse_threshold_late
                column_loss_collapse_detected = column_loss_std < collapse_threshold
        
        # Check joint embedding variance (from collapse diagnostics if available)
        # This would be computed in compute_total_loss and stored in loss_dict
        # For now, we'll rely on column_loss_std as the primary collapse signal
        embedding_variance_collapse = column_loss_collapse_detected
        
        # Log diagnostic information
        if failure_changed:
            logger.warning(f"⚠️  [{epoch_idx}] NO_LEARNING detected → loss plateaued at train={current_train_loss:.4f} val={current_val_loss:.4f}")
            logger.info(f"   📊 Controller diagnostics:")
            if avg_grad_norm is not None:
                logger.info(f"      Grad norm: {avg_grad_norm:.6f} ({'TINY' if grad_norm_tiny else 'OK'})")
            logger.info(f"      Loss trend: {'WORSE' if loss_getting_worse else 'FLAT' if loss_flat else 'UNKNOWN'}")
            if loss_variance_increasing:
                logger.warning(f"      ⚠️  Loss variance INCREASING (instability)")
            if column_loss_std is not None:
                logger.info(f"      Column loss std: {column_loss_std:.6f} (collapse={'YES' if column_loss_collapse_detected else 'NO'})")
            self._last_logged_failure = failure_type
            self._failure_repeat_count = 1
        else:
            self._failure_repeat_count += 1
            if self._failure_repeat_count % 10 == 0:
                logger.info(f"📊 [{epoch_idx}] Still NO_LEARNING (×{self._failure_repeat_count}), train={current_train_loss:.4f} val={current_val_loss:.4f}, lr_boost={lr_boost_multiplier:.2f}x")
        
        # ============================================================================
        # CONTROLLER DECISION LOGIC
        # ============================================================================
        
        # RULE 3: Embedding variance collapse → LR decrease + stop boosting, possibly reload checkpoint
        if embedding_variance_collapse or column_loss_collapse_detected:
            logger.warning(f"🚨 [{epoch_idx}] EMBEDDING COLLAPSE DETECTED")
            logger.warning(f"   → Reducing LR, stopping boosts, allowing early stopping")
            
            # Reduce LR by 0.5×
            old_boost = lr_boost_multiplier
            lr_boost_multiplier = max(1.0, lr_boost_multiplier * 0.5)
            if lr_boost_multiplier != old_boost:
                intervention_made = True
                logger.warning(f"📉 [{epoch_idx}] Collapse: Reducing LR {old_boost:.2f}x → {lr_boost_multiplier:.2f}x")
                if hasattr(self, '_train_scheduler') and isinstance(self._train_scheduler, LRTimeline):
                    scale_factor = lr_boost_multiplier / old_boost
                    self._train_scheduler.decrease_lr(
                        current_epoch=epoch_idx,
                        scale_factor=scale_factor,
                        reason=f"Embedding collapse detected, reducing LR from {old_boost:.2f}x to {lr_boost_multiplier:.2f}x"
                    )
            
            # Stop all boosting
            if temp_boost_multiplier > 1.0:
                temp_boost_multiplier = 1.0
                intervention_made = True
                logger.warning(f"🌡️  [{epoch_idx}] Collapse: Resetting temperature boost to 1.0x")
            
            # Allow early stopping
            epoch_entry["early_stop_blocked"] = False
            if hasattr(self, '_no_learning_tracker'):
                self._no_learning_tracker['min_epochs_before_early_stop'] = 0
            
            # Consider reloading best checkpoint if collapse is severe
            if column_loss_std is not None and column_loss_std < 0.001:  # Very severe collapse
                logger.error(f"💥 [{epoch_idx}] SEVERE COLLAPSE (std={column_loss_std:.6f}) - Attempting to reload best checkpoint")
                self._no_learning_tracker['severe_collapse_detected'] = True
                self._no_learning_tracker['collapse_epoch'] = epoch_idx
                self._no_learning_tracker['collapse_column_loss_std'] = column_loss_std
                
                # Try to reload best checkpoint if it exists
                try:
                    best_checkpoint_path = self.get_best_checkpoint_path()
                    if os.path.exists(best_checkpoint_path):
                        logger.warning(f"🔄 [{epoch_idx}] Reloading best checkpoint to recover from collapse...")
                        best_epoch_idx = self.load_best_checkpoint()
                        logger.info(f"✅ Reloaded best checkpoint from epoch {best_epoch_idx}")
                        # Reset collapse tracking after reload
                        if hasattr(self, '_collapse_lr_reduction_epochs'):
                            self._collapse_lr_reduction_epochs = 0
                    else:
                        logger.warning(f"⚠️  Best checkpoint not found at {best_checkpoint_path} - cannot recover")
                except Exception as reload_error:
                    logger.error(f"❌ Failed to reload best checkpoint: {reload_error}")
                    logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # RULE 2: Loss getting worse OR variance increasing → LR decrease + cooldown
        elif loss_getting_worse or loss_variance_increasing:
            logger.warning(f"📉 [{epoch_idx}] Loss {'getting WORSE' if loss_getting_worse else 'variance INCREASING'}")
            logger.warning(f"   → Decreasing LR and entering cooldown")
            
            old_boost = lr_boost_multiplier
            lr_boost_multiplier = max(1.0, lr_boost_multiplier * 0.5)
            if lr_boost_multiplier != old_boost:
                intervention_made = True
                logger.warning(f"📉 [{epoch_idx}] LR decrease: {old_boost:.2f}x → {lr_boost_multiplier:.2f}x")
                if hasattr(self, '_train_scheduler') and isinstance(self._train_scheduler, LRTimeline):
                    scale_factor = lr_boost_multiplier / old_boost
                    self._train_scheduler.decrease_lr(
                        current_epoch=epoch_idx,
                        scale_factor=scale_factor,
                        reason=f"Loss {'getting worse' if loss_getting_worse else 'variance increasing'}, reducing LR"
                    )
            
            # Reset temperature boost
            if temp_boost_multiplier > 1.0:
                temp_boost_multiplier = 1.0
                intervention_made = True
                logger.warning(f"🌡️  [{epoch_idx}] Resetting temperature boost to 1.0x")
            
            # Cooldown: block further interventions for a few epochs
            if not hasattr(self, '_lr_cooldown_until'):
                self._lr_cooldown_until = epoch_idx + 5  # 5 epoch cooldown
            else:
                self._lr_cooldown_until = max(self._lr_cooldown_until, epoch_idx + 5)
            logger.info(f"   → Cooldown active until epoch {self._lr_cooldown_until}")
        
        # RULE 1: Grad norm tiny AND loss flat for M epochs → small LR increase (capped at 1.5x)
        elif grad_norm_tiny and loss_flat and epochs_since_last_intervention >= 3:
            # Check if we're in cooldown
            in_cooldown = hasattr(self, '_lr_cooldown_until') and epoch_idx < self._lr_cooldown_until
            if not in_cooldown:
                old_boost = lr_boost_multiplier
                # Small increase: 1.05x, capped at 1.5x total
                new_boost = min(lr_boost_multiplier * 1.05, 1.5)
                if new_boost > lr_boost_multiplier:
                    lr_boost_multiplier = new_boost
                    intervention_made = True
                    logger.info(f"📈 [{epoch_idx}] Tiny grad + flat loss: Small LR increase {old_boost:.2f}x → {lr_boost_multiplier:.2f}x (capped at 1.5x)")
                    if hasattr(self, '_train_scheduler') and isinstance(self._train_scheduler, LRTimeline):
                        scale_factor = lr_boost_multiplier / old_boost
                        self._train_scheduler.increase_lr(
                            current_epoch=epoch_idx,
                            scale_factor=scale_factor,
                            reason=f"Tiny grad norm ({avg_grad_norm:.6f}) + flat loss, small LR increase"
                        )
            else:
                logger.debug(f"   Skipping LR increase (in cooldown until epoch {self._lr_cooldown_until})")
        
        # Default: No intervention (let training continue naturally)
        else:
            if failure_changed:
                logger.info(f"   No intervention needed (grad={'tiny' if grad_norm_tiny else 'OK'}, loss={'flat' if loss_flat else 'changing'})")
        
        # Stop training if LR boost maxed and still no learning
        if lr_boost_multiplier >= 1.5 and self._failure_repeat_count >= 20:  # Increased patience since we're more conservative
            logger.warning(f"🛑 [{epoch_idx}] CONVERGED: LR controller maxed, stopping")
            corrective_action = {
                "epoch": epoch_idx, "trigger": "CONVERGED", "action_type": "STOP_TRAINING",
                "details": {"val_loss": val_loss, "lr_multiplier": lr_boost_multiplier}
            }
            epoch_entry["corrective_actions"].append(corrective_action)
            self._corrective_actions.append(corrective_action)
            should_break = True
            return lr_boost_multiplier, temp_boost_multiplier, intervention_stage, epochs_since_last_intervention, should_break
        
        # Log intervention if made
        if intervention_made:
            self._no_learning_tracker['last_no_learning_epoch'] = epoch_idx
            # Only block early stopping if we increased LR (not if we decreased)
            if lr_boost_multiplier > 1.0:
                self._no_learning_tracker['min_epochs_before_early_stop'] = 5  # Reduced from 10
                epoch_entry["early_stop_blocked"] = True
                logger.info(f"   → Early stopping blocked for 5 epochs")
            else:
                epoch_entry["early_stop_blocked"] = False
            epochs_since_last_intervention = 0
            
            corrective_action = {
                "epoch": epoch_idx, "trigger": "NO_LEARNING", "action_type": "LR_CONTROLLER",
                "details": {
                    "lr_multiplier": lr_boost_multiplier,
                    "temp_multiplier": temp_boost_multiplier,
                    "grad_norm": avg_grad_norm,
                    "loss_trend": "worse" if loss_getting_worse else "flat" if loss_flat else "unknown",
                    "loss_variance_increasing": loss_variance_increasing,
                    "embedding_collapse": embedding_variance_collapse,
                }
            }
            epoch_entry["corrective_actions"].append(corrective_action)
            self._corrective_actions.append(corrective_action)
        
        return lr_boost_multiplier, temp_boost_multiplier, intervention_stage, epochs_since_last_intervention, should_break

    def _handle_val_loss_tracking_and_early_stop(
        self,
        epoch_idx: int,
        n_epochs: int,
        val_loss: float,
        val_components: dict,
        val_loss_early_stop_patience: int,
        val_loss_min_delta: float,
        scheduler,
        optimizer,
        dropout_scheduler,
        d: dict,
        max_progress: int,
        print_callback,
        training_event_callback,
        training_event_dict: dict,
        current_lr
    ) -> bool:
        """Handle validation loss tracking, component improvements, and early stopping.
        
        Returns True if training should stop (early stop triggered), False otherwise.
        """
        # Initialize trackers if needed
        if not hasattr(self, '_val_loss_tracker'):
            self._val_loss_tracker = {
                'best_val_loss': float('inf'),
                'epochs_without_improvement': 0,
                'patience': val_loss_early_stop_patience,
                'min_delta': val_loss_min_delta,
                'best_spread': float('inf'),
                'best_joint': float('inf'),
                'best_marginal': float('inf'),
                'spread_no_improvement': 0,
                'joint_no_improvement': 0,
                'marginal_no_improvement': 0,
                'lr_history': [],
                'marginal_weight_history': []
            }
            logger.info(f"📉 Validation loss early stopping enabled: patience={val_loss_early_stop_patience}, min_delta={val_loss_min_delta}")
            logger.info(f"📊 Component-level tracking enabled: spread, joint, marginal losses")
        
        if not hasattr(self, '_spread_only_tracker'):
            self._spread_only_tracker = {
                'spread_only_epochs_completed': 0,
                'in_spread_phase': False
            }
        
        if not isinstance(val_loss, (int, float)) or val_loss <= 0:
            return False
        
        # Track component improvements
        min_delta = self._val_loss_tracker['min_delta']
        if val_components:
            for comp_name in ['spread', 'joint', 'marginal']:
                if comp_name not in val_components:
                    continue
                comp_val = val_components[comp_name]
                best_key = f'best_{comp_name}'
                no_improve_key = f'{comp_name}_no_improvement'
                
                prev_loss = self._val_loss_tracker.get(f'{comp_name}_prev', comp_val)
                if f'{comp_name}_start' not in self._val_loss_tracker:
                    self._val_loss_tracker[f'{comp_name}_start'] = comp_val
                
                history_key = f'{comp_name}_history'
                if history_key not in self._val_loss_tracker:
                    self._val_loss_tracker[history_key] = []
                self._val_loss_tracker[history_key].append((epoch_idx, comp_val))
                
                if comp_val < self._val_loss_tracker[best_key] - min_delta:
                    self._val_loss_tracker[best_key] = comp_val
                    self._val_loss_tracker[no_improve_key] = 0
                else:
                    self._val_loss_tracker[no_improve_key] += 1
                
                self._val_loss_tracker[f'{comp_name}_prev'] = comp_val
                
                # Log component values
                history = self._val_loss_tracker[history_key]
                nums = get_time_moving_loss_values(history, epoch_idx, prev_loss)
                nums.append(f"{comp_val:8.6f}")
                logger.info(f"{comp_name.capitalize():8s}: {' '.join(nums)}")
        
        # Track LR and marginal weight history
        lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
        current_marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
        
        if 'lr_history' not in self._val_loss_tracker:
            self._val_loss_tracker['lr_history'] = []
        if 'marginal_weight_history' not in self._val_loss_tracker:
            self._val_loss_tracker['marginal_weight_history'] = []
        
        self._val_loss_tracker['lr_history'].append((epoch_idx, lr_value))
        self._val_loss_tracker['marginal_weight_history'].append((epoch_idx, current_marginal_weight))
        
        # Log LR and marginal weight
        lr_history = self._val_loss_tracker['lr_history']
        lr_nums = get_time_moving_loss_values(lr_history, epoch_idx, lr_value)
        lr_nums.append(f"{lr_value:8.6f}")
        logger.info(f"{'LR':8s}: {' '.join(lr_nums)}")
        
        mw_history = self._val_loss_tracker['marginal_weight_history']
        mw_nums = get_time_moving_loss_values(mw_history, epoch_idx, current_marginal_weight)
        mw_nums.append(f"{current_marginal_weight:8.6f}")
        logger.info(f"{'Marg Wt':8s}: {' '.join(mw_nums)}")
        
        # Determine minimum epoch for early stopping
        min_epoch_for_early_stop = 50
        
        if epoch_idx < min_epoch_for_early_stop:
            if epoch_idx == 50 or epoch_idx % 20 == 0:
                logger.info(f"⏭️  Early stopping DISABLED until epoch {min_epoch_for_early_stop}")
            return False
        
        # Track validation loss changes
        prev_val_loss = self._val_loss_tracker.get('val_prev', val_loss)
        if 'val_start' not in self._val_loss_tracker:
            self._val_loss_tracker['val_start'] = val_loss
        if 'val_history' not in self._val_loss_tracker:
            self._val_loss_tracker['val_history'] = []
        self._val_loss_tracker['val_history'].append((epoch_idx, val_loss))
        
        if val_loss < self._val_loss_tracker['best_val_loss'] - min_delta:
            self._val_loss_tracker['best_val_loss'] = val_loss
            self._val_loss_tracker['epochs_without_improvement'] = 0
            
            history = self._val_loss_tracker['val_history']
            nums = get_time_moving_loss_values(history, epoch_idx, prev_val_loss)
            nums.append(f"{val_loss:8.4f}")
            logger.info(f"Val loss  : {' '.join(nums)}")
        else:
            self._val_loss_tracker['epochs_without_improvement'] += 1
            logger.info(f"⚠️  No improvement for {self._val_loss_tracker['epochs_without_improvement']} epochs "
                       f"(current: {val_loss:.4f}, best: {self._val_loss_tracker['best_val_loss']:.4f})")
        
        self._val_loss_tracker['val_prev'] = val_loss
        
        # Check if early stopping is blocked
        early_stop_blocked = False
        epochs_remaining = 0
        if hasattr(self, '_no_learning_tracker') and 'last_no_learning_epoch' in self._no_learning_tracker:
            epochs_since_no_learning = epoch_idx - self._no_learning_tracker['last_no_learning_epoch']
            min_epochs_required = self._no_learning_tracker.get('min_epochs_before_early_stop', 10)
            if epochs_since_no_learning < min_epochs_required:
                early_stop_blocked = True
                epochs_remaining = min_epochs_required - epochs_since_no_learning
        
        # Check if any component is still improving
        total_no_improvement = self._val_loss_tracker['epochs_without_improvement']
        any_component_improving = False
        if val_components and n_epochs > 0:
            training_progress = epoch_idx / n_epochs
            if training_progress >= 0.25:
                marginal_no_improve = self._val_loss_tracker.get('marginal_no_improvement', total_no_improvement)
                if marginal_no_improve < (self._val_loss_tracker['patience'] // 2):
                    any_component_improving = True
                    logger.info(f"🔄 Marginal loss still improving (stale: {marginal_no_improve} epochs) - continuing")
        
        # Check early stopping conditions
        if total_no_improvement < self._val_loss_tracker['patience'] or any_component_improving:
            return False
        
        if early_stop_blocked:
            if not hasattr(self, '_early_stop_block_logged') or not self._early_stop_block_logged:
                logger.warning(f"⏸️  [{epoch_idx}] Early stopping blocked → {epochs_remaining} more epochs needed")
                self._early_stop_block_logged = True
            return False
        
        # Handle spread finalization phase
        spread_only_epochs = self._spread_only_tracker.get('spread_only_epochs_completed', 0)
        FINALIZATION_EPOCHS = 5
        
        if spread_only_epochs < FINALIZATION_EPOCHS:
            if not hasattr(self, '_forced_spread_finalization'):
                self._forced_spread_finalization = True
                self._finalization_start_epoch = epoch_idx
                self.encoder.config.loss_config.spread_loss_weight = 1.0
                self.encoder.config.loss_config.marginal_loss_weight = 0.1
                self.encoder.config.loss_config.joint_loss_weight = 1.0
                logger.warning(f"⚡ [{epoch_idx+1}] FORCED EARLY FINALIZATION: Jumping to final phase weights")
                logger.info(f"   📊 Loss weights → spread: 1.0, marginal: 0.1, joint: 1.0")
                logger.info(f"   🎯 Running {FINALIZATION_EPOCHS} more epochs in spread+joint focus")
            return False
        
        if not (hasattr(self, '_forced_spread_finalization') and self._forced_spread_finalization):
            return False
        
        # Execute early stopping
        comp_details = ""
        if val_components:
            comp_details = f"\n   Component staleness: spread={self._val_loss_tracker.get('spread_no_improvement', 0)} joint={self._val_loss_tracker.get('joint_no_improvement', 0)} marginal={self._val_loss_tracker.get('marginal_no_improvement', 0)}"
        
        logger.info(f"🛑 EARLY STOPPING: Val loss hasn't improved for {self._val_loss_tracker['patience']} epochs")
        logger.info(f"   Best validation loss: {self._val_loss_tracker['best_val_loss']:.4f} (current: {val_loss:.4f}){comp_details}")
        logger.info(f"   ✅ Completed {spread_only_epochs} epoch(s) of spread focus phase training")
        logger.info(f"   Stopping training to prevent overfitting")
        
        # Save final checkpoint
        try:
            self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
            logger.info(f"💾 Final model saved")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save final checkpoint at epoch {epoch_idx}: {e}")
        
        # Update progress dict
        d["progress_counter"] = max_progress
        d["status"] = "early_stopped"
        d["early_stopping"] = True
        d["early_stop_reason"] = "validation_loss_plateau"
        d["stopped_epoch"] = epoch_idx + 1
        d["best_val_loss"] = self._val_loss_tracker['best_val_loss']
        d["spread_only_epochs_completed"] = spread_only_epochs
        
        if print_callback is not None:
            d["time_now"] = time.time()
            logger.info(f"📊 Sending final progress update: {d['progress_counter']}/{d['max_progress']} (100%)")
            print_callback(d)
        
        if training_event_callback is not None:
            training_event_dict["early_stopped"] = True
            training_event_dict["early_stop_reason"] = "validation_loss_plateau"
            training_event_dict["best_val_loss"] = self._val_loss_tracker['best_val_loss']
            training_event_dict["spread_only_epochs_completed"] = spread_only_epochs
            training_event_dict["progress_counter"] = max_progress
            training_event_dict["max_progress"] = max_progress
            training_event_callback(training_event_dict)
        
        return True  # Signal to break training loop

    def _handle_checkpoint_saves(
        self,
        epoch_idx: int,
        n_epochs: int,
        save_state_after_every_epoch: bool,
        save_state_epoch_interval: int,
        val_loss: float,
        lowest_val_loss: float,
        optimizer,
        scheduler,
        dropout_scheduler
    ) -> float:
        """Handle periodic and best checkpoint saves.
        
        Returns the updated lowest_val_loss (or lowest composite score if using alpha).
        """
        # Save after every epoch if enabled
        if save_state_after_every_epoch:
            logger.info("about to save_state_after_every_epoch")
            try:
                self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
            except Exception as e:
                logger.warning(f"⚠️  Failed to save checkpoint after epoch {epoch_idx}: {e}")
                logger.warning(f"   Training will continue - checkpoint can be saved at next epoch")
        
        # Save at specified interval
        if epoch_idx > 0 and save_state_epoch_interval > 0 and (epoch_idx % save_state_epoch_interval) == 0:
            logger.info(f"💾 Saving checkpoint (interval={save_state_epoch_interval}, total_epochs={n_epochs})")
            try:
                self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
            except Exception as e:
                logger.warning(f"⚠️  Failed to save periodic checkpoint at epoch {epoch_idx}: {e}")
                logger.warning(f"   Training will continue - checkpoint can be saved at next interval")

        # Save best model using composite score (val_loss weighted by alpha health)
        # If WeightWatcher data is available, use composite score; otherwise just val_loss
        if isinstance(val_loss, (int, float)) and isinstance(lowest_val_loss, (int, float)):
            # Get current alpha score from WeightWatcher callback (if available)
            current_alpha_score = self._get_current_validation_alpha_score()
            
            if current_alpha_score is not None:
                # Use composite score: val_loss weighted by alpha health
                try:
                    from lib.weightwatcher_tracking import compute_composite_validation_score
                    current_composite = compute_composite_validation_score(val_loss, current_alpha_score)
                    
                    # Initialize best composite score tracker if needed
                    if not hasattr(self, '_best_composite_score'):
                        self._best_composite_score = float('inf')
                        self._best_composite_epoch = -1
                        self._best_alpha_score_at_best = None
                    
                    if current_composite < self._best_composite_score:
                        old_best = self._best_composite_score
                        old_epoch = self._best_composite_epoch
                        self._best_composite_score = current_composite
                        self._best_composite_epoch = epoch_idx
                        self._best_alpha_score_at_best = current_alpha_score
                        lowest_val_loss = val_loss  # Track raw val_loss too
                        
                        logger.info(f"🎯 NEW BEST COMPOSITE SCORE at epoch {epoch_idx}:")
                        logger.info(f"   Val Loss: {val_loss:.6f}, Alpha Score: {current_alpha_score:.4f}")
                        logger.info(f"   Composite: {current_composite:.6f} (prev best: {old_best:.6f} @ epoch {old_epoch})")
                        
                        try:
                            self.save_best_for_inference(epoch_idx, val_loss)
                        except Exception as e:
                            logger.warning(f"⚠️  Failed to save best checkpoint at epoch {epoch_idx}: {e}")
                            logger.warning(f"   Training will continue - best model will be saved on next improvement")
                    else:
                        # Log why we didn't save (for debugging)
                        logger.debug(f"   Composite {current_composite:.6f} >= best {self._best_composite_score:.6f}, not saving")
                except ImportError:
                    # Fall back to pure val_loss if weightwatcher_tracking not available
                    if val_loss < lowest_val_loss:
                        lowest_val_loss = val_loss
                        try:
                            self.save_best_for_inference(epoch_idx, val_loss)
                        except Exception as e:
                            logger.warning(f"⚠️  Failed to save best checkpoint at epoch {epoch_idx}: {e}")
            else:
                # No alpha data - use pure val_loss comparison
                if val_loss < lowest_val_loss:
                    lowest_val_loss = val_loss
                    try:
                        self.save_best_for_inference(epoch_idx, val_loss)
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to save best checkpoint at epoch {epoch_idx}: {e}")
                        logger.warning(f"   Training will continue - best model will be saved on next improvement")
        
        return lowest_val_loss
    
    def _get_current_validation_alpha_score(self) -> Optional[float]:
        """Get the current validation alpha score from WeightWatcher callback.
        
        Returns the most recent alpha score, or None if not available.
        """
        # Check if we have a WeightWatcher callback with metrics
        if hasattr(self, '_ww_callback') and self._ww_callback is not None:
            try:
                metrics = self._ww_callback._load_latest_metrics()
                if metrics and 'validation_alpha_score' in metrics:
                    return metrics['validation_alpha_score']
                # Try to compute from raw metrics if score not present
                if metrics:
                    alpha_mean = metrics.get('alpha_mean')
                    alpha_pct = metrics.get('alpha_pct_below_6')
                    if alpha_mean is not None and alpha_pct is not None:
                        from lib.weightwatcher_tracking import compute_validation_alpha_score
                        return compute_validation_alpha_score(alpha_mean, alpha_pct)
            except Exception as e:
                logger.debug(f"Could not get alpha score from WW callback: {e}")
        
        # Check training timeline for recent WeightWatcher data
        if hasattr(self, '_training_timeline') and self._training_timeline:
            # Look for most recent entry with weightwatcher data
            for entry in reversed(self._training_timeline):
                ww_data = entry.get('weightwatcher')
                if ww_data:
                    alpha_mean = ww_data.get('avg_alpha')
                    # We don't have alpha_pct in timeline, compute from alpha_mean alone
                    if alpha_mean is not None:
                        # Rough estimate: assume 70% of layers are good if alpha is reasonable
                        estimated_pct = max(0.3, min(0.95, 1.0 - (alpha_mean - 3.0) * 0.1))
                        from lib.weightwatcher_tracking import compute_validation_alpha_score
                        return compute_validation_alpha_score(alpha_mean, estimated_pct)
                    break  # Only check most recent entry with WW data
        
        return None

    def _log_epoch_summary_line(
        self, epoch_idx: int, n_epochs: int, epoch_entry: dict,
        has_failure: bool, failure_type, intervention_stage: int
    ) -> None:
        """Log clean epoch summary line."""
        logger.info("─" * 100)
        
        status_symbol = "✅" if not has_failure else "⚠️ "
        failure_label = f" [{failure_type}]" if has_failure and failure_type else ""
        intervention_label = f" I{intervention_stage}" if intervention_stage > 0 else ""
        
        cumulative_epoch = epoch_idx
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
        
        current_train_loss = epoch_entry.get("train_loss")
        current_val_loss = epoch_entry.get("validation_loss")
        current_dropout = epoch_entry.get("dropout_rate")
        lr_value = epoch_entry.get("learning_rate")
        latest_gradient_norm = getattr(self, '_latest_gradient_norm', None)
        
        lr_str = f"{lr_value:.6f}" if lr_value else "N/A"
        drop_str = f"{current_dropout:0.3f}" if current_dropout else "N/A"
        train_str = f"{current_train_loss:.4f}" if current_train_loss is not None else "N/A"
        val_str = f"{current_val_loss:.4f}" if current_val_loss is not None else "N/A"
        grad_str = f"{latest_gradient_norm:.4f}" if latest_gradient_norm is not None else "N/A"
        
        epoch_display = f"{cumulative_epoch:3d}/{n_epochs}" if n_epochs else f"{cumulative_epoch:3d}"
        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
            epoch_display = f"{cumulative_epoch:3d}"
        
        logger.info(
            f"{status_symbol} [{epoch_display}] train={train_str} val={val_str} "
            f"lr={lr_str} drop={drop_str} grad={grad_str}{intervention_label}{failure_label}"
        )

    def _periodic_embedding_quality_check(self, epoch_idx: int, n_epochs: int) -> None:
        """Run embedding quality check at 25%, 50%, 75% of training."""
        if n_epochs >= 40:
            check_epochs = [int(n_epochs * 0.25), int(n_epochs * 0.50), int(n_epochs * 0.75)]
        elif n_epochs > 20:
            check_epochs = [int(n_epochs * 0.50)]
        else:
            check_epochs = []
        
        if epoch_idx not in check_epochs:
            return
        
        pct = int((epoch_idx / n_epochs) * 100)
        try:
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"📊 EMBEDDING QUALITY CHECK @ {pct}% (epoch {epoch_idx}/{n_epochs})")
            logger.info("=" * 80)
            self._log_embedding_quality_summary(epoch_idx=epoch_idx)
            logger.info("=" * 80)
            logger.info("")
        except Exception as e:
            logger.warning(f"⚠️ Embedding quality check failed: {e}")

    def _run_weightwatcher_analysis(
        self, 
        epoch_idx: int,
        n_epochs: int,
        enable_weightwatcher: bool,
        weightwatcher_save_every: int,
        weightwatcher_out_dir: str,
        weightwatcher_job_id: str,
        min_epoch_for_early_stop: int,
        optimizer,
        scheduler,
        dropout_scheduler,
        d: dict,
        max_progress: int,
        print_callback
    ) -> bool:
        """Run WeightWatcher analysis with convergence monitoring.
        
        Returns True if training should stop (early convergence), False otherwise.
        """
        if not enable_weightwatcher:
            return False
        if epoch_idx % weightwatcher_save_every != 0 and epoch_idx != 0:
            return False
        
        try:
            from lib.weightwatcher_tracking import WeightWatcherCallback
            
            # Create WeightWatcher callback if not exists
            if not hasattr(self, '_ww_callback'):
                sphere_config = get_config()
                enable_clipping = sphere_config.get_enable_spectral_norm_clipping()
                clip_threshold = sphere_config.get_spectral_norm_clip_threshold()
                spectral_norm_clip_value = clip_threshold if enable_clipping else None
                
                logger.info(f"🔧 Spectral norm clipping: {'ENABLED' if enable_clipping else 'DISABLED'}")
                if enable_clipping:
                    logger.info(f"   Clip threshold: {clip_threshold}")
                
                self._ww_callback = WeightWatcherCallback(
                    out_dir=weightwatcher_out_dir,
                    job_id=weightwatcher_job_id,
                    save_every=weightwatcher_save_every,
                    convergence_patience=5,
                    convergence_min_improve=1e-4,
                    spectral_norm_clip=spectral_norm_clip_value,
                    freeze_threshold=None,
                    min_epoch_before_freeze=20,
                    max_layers_to_freeze=5,
                    max_freeze_percentage=0.1,
                    enable_layer_freezing=False
                )
            
            # Run analysis and get convergence results
            ww_result = self._ww_callback(self.encoder, epoch_idx)
            
            # WOULD_FREEZE checkpoint
            if ww_result.get('save_would_freeze_checkpoint', False):
                try:
                    checkpoint_name = f"WOULD_FREEZE_epoch_{epoch_idx}"
                    logger.warning(f"💾 Saving WOULD_FREEZE checkpoint: {checkpoint_name}")
                    logger.warning(f"   📍 This checkpoint can be used to experiment with layer freezing enabled")
                    logger.warning(f"   🔬 {ww_result.get('would_freeze_layer_count', 0)} layers would have been frozen")
                    
                    self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
                    checkpoint_path = self.get_training_state_path(epoch_idx, 0)
                    logger.warning(f"   ✅ WOULD_FREEZE checkpoint saved: {checkpoint_path}")
                except Exception as e:
                    logger.error(f"   ❌ Failed to save WOULD_FREEZE checkpoint: {e}")
                    traceback.print_exc()
            
            # Store WeightWatcher data in timeline
            if hasattr(self, '_training_timeline') and self._training_timeline:
                cumulative_epoch_for_ww = epoch_idx
                if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                    cumulative_epoch_for_ww = epoch_idx + self._kv_fold_epoch_offset
                
                current_epoch_entry = self._training_timeline[-1]
                if current_epoch_entry['epoch'] == cumulative_epoch_for_ww:
                    # Get validation_alpha_score from most recent WW metrics
                    validation_alpha_score = None
                    if hasattr(self, '_ww_callback') and self._ww_callback is not None:
                        try:
                            metrics = self._ww_callback._load_latest_metrics()
                            if metrics:
                                validation_alpha_score = metrics.get('validation_alpha_score')
                        except Exception:
                            pass
                    
                    ww_data = {
                        'should_stop': ww_result.get('should_stop', False),
                        'converged': ww_result.get('converged', False),
                        'avg_alpha': ww_result.get('avg_alpha'),
                        'avg_spectral_norm': ww_result.get('avg_spectral_norm'),
                        'avg_log_norm': ww_result.get('avg_log_norm'),
                        'rank_loss': ww_result.get('rank_loss'),
                        'entropy': ww_result.get('entropy'),
                        'layers_frozen': ww_result.get('layers_frozen', []),
                        'layers_clipped': ww_result.get('layers_clipped', []),
                        'validation_alpha_score': validation_alpha_score,
                    }
                    ww_data = {k: v for k, v in ww_data.items() if v is not None}
                    current_epoch_entry['weightwatcher'] = ww_data
                    logger.info(f"📊 Added WeightWatcher data to timeline for epoch {epoch_idx}")
            
            # Check if early stopping is blocked
            convergence_early_stop_blocked = False
            epochs_remaining = 0
            if hasattr(self, '_no_learning_tracker') and 'last_no_learning_epoch' in self._no_learning_tracker:
                epochs_since_no_learning = epoch_idx - self._no_learning_tracker['last_no_learning_epoch']
                min_epochs_required = self._no_learning_tracker.get('min_epochs_before_early_stop', 10)
                if epochs_since_no_learning < min_epochs_required:
                    convergence_early_stop_blocked = True
                    epochs_remaining = min_epochs_required - epochs_since_no_learning
            
            # Check if training should stop due to convergence
            if ww_result.get('should_stop', False):
                output_dir_str = str(self.output_dir) if hasattr(self, 'output_dir') and self.output_dir else None
                job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                
                if check_no_stop_file(job_id, output_dir_str):
                    logger.warning(f"🚫 NO_STOP flag detected - early stopping DISABLED")
                    logger.warning(f"   → WeightWatcher convergence detected but ignoring due to NO_STOP file")
                    logger.warning(f"   → Training will continue for all {n_epochs} epochs")
                elif epoch_idx < min_epoch_for_early_stop:
                    logger.info(f"⏭️  WeightWatcher convergence detected but early stopping DISABLED until epoch {min_epoch_for_early_stop}")
                    logger.info(f"   → Early stopping cooldown period - continuing training")
                elif convergence_early_stop_blocked:
                    logger.warning(f"⏸️  WeightWatcher convergence early stopping triggered but BLOCKED")
                    logger.warning(f"   → Continuing training for {epochs_remaining} more epochs")
                else:
                    logger.info(f"🛑 Early stopping triggered by convergence monitor at epoch {epoch_idx}")
                    logger.info(f"   Model has converged - stopping training to save compute")
                    
                    # Save final checkpoint
                    try:
                        self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
                        logger.info(f"💾 Final converged model saved")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to save final converged checkpoint at epoch {epoch_idx}: {e}")
                    
                    # Log convergence details
                    convergence_status = self._ww_callback.get_convergence_status()
                    logger.info(f"📊 Convergence details:")
                    logger.info(f"   Converged at epoch: {convergence_status.get('convergence_epoch', epoch_idx)}")
                    logger.info(f"   Epochs without improvement: {convergence_status.get('epochs_without_improvement', 'unknown')}")
                    logger.info(f"   Best rank loss: {convergence_status.get('best_rank_loss', 'unknown')}")
                    
                    # Update progress dict
                    d["progress_counter"] = max_progress
                    d["status"] = "converged"
                    d["early_stopping"] = True
                    d["converged_epoch"] = epoch_idx + 1
                    
                    if print_callback is not None:
                        d["time_now"] = time.time()
                        logger.info(f"📊 Sending final progress update: {d['progress_counter']}/{d['max_progress']} (100%)")
                        print_callback(d)
                    
                    return True  # Signal to break training loop
            
            # Log any interventions applied
            if ww_result.get('clipped_layers'):
                logger.info(f"🔧 Applied spectral norm clipping to {len(ww_result['clipped_layers'])} layers")
            if ww_result.get('frozen_layers'):
                logger.info(f"❄️ Froze {len(ww_result['frozen_layers'])} dominant layers")
            if ww_result.get('refreshed_sampler'):
                logger.info(f"🔁 Refreshed hard negative sampler")
                
        except Exception as e:
            logger.warning(f"⚠️ WeightWatcher analysis failed for epoch {epoch_idx}: {e}")
            try:
                from error_tracker import log_training_error
                log_training_error(
                    message=f"WeightWatcher finalization failed: {e}",
                    job_id=getattr(self, 'job_id', None) or self.training_info.get('job_id', None),
                    exception=e,
                    context={"method": "weightwatcher_finalization", "enable_weightwatcher": enable_weightwatcher}
                )
            except Exception as tracker_error:
                logger.warning(f"Error tracker failed: {tracker_error}")
        
        return False  # Continue training

    def _log_attention_head_diversity(self, epoch_idx: int) -> None:
        """Monitor transformer attention head diversity for collapse detection."""
        try:
            analysis = self.encoder.joint_encoder._analyze_attention_weight_similarity()
            
            # Compact summary every epoch
            logger.info(f"🔍 Attention Heads: "
                       f"diversity={analysis['diversity_score']:.3f}, "
                       f"avg_sim={analysis['avg_similarity']:.3f}, "
                       f"redundant={analysis['n_redundant_pairs']}/{analysis['n_heads']*(analysis['n_heads']-1)//2} "
                       f"{analysis['status']}")
            
            # Detailed analysis every 10 epochs
            if (epoch_idx + 1) % 10 == 0:
                logger.info(f"{'='*80}")
                logger.info(f"{analysis['status']} Attention Head Diversity Analysis:")
                logger.info(f"   Avg similarity: {analysis['avg_similarity']:.3f}, Diversity: {analysis['diversity_score']:.3f}")
                logger.info(f"   Min/Max: {analysis['min_similarity']:.3f} / {analysis['max_similarity']:.3f}")
                if analysis['redundant_pairs']:
                    logger.info(f"   ⚠️  {len(analysis['redundant_pairs'])} redundant pairs (>0.7 sim)")
                logger.info(f"   💡 {analysis['recommendation']}")
                logger.info(f"{'='*80}")
            
            # Alert on collapse
            if analysis['avg_similarity'] > 0.8:
                logger.warning(f"🚨 ATTENTION HEAD COLLAPSE! avg_sim={analysis['avg_similarity']:.3f}")
                logger.warning(f"   Consider increasing n_heads from {analysis['n_heads']} to {analysis['n_heads'] * 2}")
        except Exception as e:
            logger.debug(f"Could not analyze attention head diversity: {e}")

    def _log_parameter_trainability(self) -> None:
        """Log parameter trainability check before training starts."""
        trainable_params = sum(p.numel() for p in self.encoder.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.encoder.parameters())
        frozen_params = total_params - trainable_params
        
        logger.info("=" * 80)
        logger.info("🔍 PARAMETER TRAINABILITY CHECK (BEFORE TRAINING)")
        logger.info("=" * 80)
        logger.info(f"   Total parameters: {total_params:,}")
        logger.info(f"   Trainable parameters: {trainable_params:,} ({100*trainable_params/total_params:.1f}%)")
        logger.info(f"   Frozen parameters: {frozen_params:,} ({100*frozen_params/total_params:.1f}%)")
        
        if frozen_params > 0:
            logger.error(f"   ⚠️  WARNING: {frozen_params:,} parameters are FROZEN!")
            logger.error("   Checking which components are frozen...")
            
            # Check each major component
            col_enc_trainable = sum(p.numel() for p in self.encoder.column_encoder.parameters() if p.requires_grad)
            col_enc_total = sum(p.numel() for p in self.encoder.column_encoder.parameters())
            logger.info(f"   Column Encoder: {col_enc_trainable:,}/{col_enc_total:,} trainable ({100*col_enc_trainable/col_enc_total:.1f}%)")
            
            joint_enc_trainable = sum(p.numel() for p in self.encoder.joint_encoder.parameters() if p.requires_grad)
            joint_enc_total = sum(p.numel() for p in self.encoder.joint_encoder.parameters())
            logger.info(f"   Joint Encoder: {joint_enc_trainable:,}/{joint_enc_total:,} trainable ({100*joint_enc_trainable/joint_enc_total:.1f}%)")
            
            if hasattr(self.encoder, 'column_predictor') and self.encoder.column_predictor:
                col_pred_trainable = sum(p.numel() for p in self.encoder.column_predictor.parameters() if p.requires_grad)
                col_pred_total = sum(p.numel() for p in self.encoder.column_predictor.parameters())
                logger.info(f"   Column Predictor: {col_pred_trainable:,}/{col_pred_total:,} trainable ({100*col_pred_trainable/col_pred_total:.1f}%)")
            
            if hasattr(self.encoder, 'joint_predictor') and self.encoder.joint_predictor:
                joint_pred_trainable = sum(p.numel() for p in self.encoder.joint_predictor.parameters() if p.requires_grad)
                joint_pred_total = sum(p.numel() for p in self.encoder.joint_predictor.parameters())
                logger.info(f"   Joint Predictor: {joint_pred_trainable:,}/{joint_pred_total:,} trainable ({100*joint_pred_trainable/joint_pred_total:.1f}%)")
        else:
            logger.info(f"   ✅ All parameters are trainable")
        logger.info("=" * 80)

    def _init_mask_tracker(self) -> None:
        """Initialize the mask distribution tracker if not already initialized."""
        from .mask_tracker import MaskDistributionTracker
        
        if self.mask_tracker is not None:
            return
        
        mask_tracker_dir = os.path.join(self.output_dir, "mask_tracking")
        self.mask_tracker = MaskDistributionTracker(
            output_dir=mask_tracker_dir,
            save_full_sequence=False,  # Set to True to save every single mask
            column_names=self.col_order,  # Pass column names for mapping
            mean_nulls_per_row=self.mean_nulls_per_row,  # Null distribution for constraint tracking
            max_nulls_per_row=self.max_nulls_per_row,
        )
        logger.info(f"📊 Mask tracking initialized: {mask_tracker_dir}")
        logger.info(f"📊 Tracking {len(self.col_order)} columns in order")
        if self.mean_nulls_per_row is not None:
            logger.info(f"📊 Null distribution: mean={self.mean_nulls_per_row:.2f}, max={self.max_nulls_per_row}")

    def _defragment_gpu_memory(self, epoch_idx: int, force_full_defrag: bool = False) -> None:
        """
        Aggressively defragment GPU memory to prevent OOM from fragmentation.
        
        The relationship extractor creates large temporary tensors (up to 6GB per chunk)
        that fragment GPU memory over time. By epoch 20+, "reserved but unallocated"
        memory can reach 90GB+ with no contiguous block available for new allocations.
        
        This method:
        1. Every epoch: Runs aggressive GPU cache clearing (3 passes with GC)
        2. Every 10 epochs (or if forced): Moves model to CPU and back to release ALL
           reserved memory and eliminate fragmentation completely
        
        Args:
            epoch_idx: Current epoch index (used for periodic full defrag)
            force_full_defrag: If True, always do full CPU roundtrip defrag
        """
        if not is_gpu_available():
            return
        
        try:
            # Standard aggressive clear every epoch
            gc.collect()
            aggressive_clear_gpu_cache(iterations=3, do_gc=True)
            synchronize_gpu()
            
            # Every 10 epochs OR if forced: FULL GPU RESET - move model to CPU and back
            # This forces PyTorch to release ALL reserved memory and start fresh
            do_full_defrag = force_full_defrag or (epoch_idx > 0 and epoch_idx % 10 == 0)
            
            if do_full_defrag:
                allocated_before = get_gpu_memory_allocated()
                reserved_before = get_gpu_memory_reserved()
                
                # When scheduled (every 10 epochs) or forced, ALWAYS do full defrag regardless of ratio
                # The previous ratio check was causing scheduled defrags to be skipped, leading to memory
                # accumulation across epochs. Since we're already in do_full_defrag block (scheduled or forced),
                # we must always execute the defragmentation to prevent OOM.
                # Also allow opportunistic defragmentation if fragmentation is high (even if not scheduled)
                is_scheduled = (epoch_idx > 0 and epoch_idx % 10 == 0)
                has_fragmentation = reserved_before > allocated_before * 1.5
                
                # Always defrag if scheduled, forced, or fragmentation is high
                if force_full_defrag or is_scheduled or has_fragmentation:
                    fragmented_gb = reserved_before - allocated_before
                    logger.info(f"🧹 GPU DEFRAG [e={epoch_idx}]: {allocated_before:.1f}GB allocated, "
                               f"{reserved_before:.1f}GB reserved ({fragmented_gb:.1f}GB fragmented)")
                    logger.info(f"   Moving encoder to CPU to release reserved memory...")
                    
                    # Move model to CPU
                    device = next(self.encoder.parameters()).device
                    self.encoder.cpu()
                    
                    # Force release ALL GPU memory
                    gc.collect()
                    empty_gpu_cache()
                    synchronize_gpu()
                    
                    # Move back to GPU
                    self.encoder.to(device)
                    self.encoder.train()  # Ensure still in training mode
                    
                    allocated_after = get_gpu_memory_allocated()
                    reserved_after = get_gpu_memory_reserved()
                    freed = reserved_before - reserved_after
                    logger.info(f"   ✅ After defrag: {allocated_after:.1f}GB allocated, "
                               f"{reserved_after:.1f}GB reserved (freed {freed:.1f}GB)")
        except Exception as e:
            logger.debug(f"GPU memory defragmentation failed: {e}")

    def train(
        self,
        batch_size=None,
        n_epochs=None,
        print_progress_step=10,
        print_callback=None,
        training_event_callback=None,
        optimizer_params=None,
        existing_epochs=None,
        use_lr_scheduler=True,
        lr_schedule_segments=None,
        save_state_after_every_epoch=True,  # Default True for crash recovery
        use_profiler=False,
        save_prediction_vector_lengths=False,
        enable_weightwatcher=False,
        weightwatcher_save_every=5,
        weightwatcher_out_dir="ww_metrics",
        enable_dropout_scheduler=True,
        dropout_schedule_type="piecewise_constant",  # Better default: hold high, ramp, hold moderate
        initial_dropout=0.5,
        final_dropout=0.25,  # Increased from 0.1 to maintain more regularization,
        movie_frame_interval=3,  # Changed from 5 to 3 - generate projections every 3 epochs by default
        val_loss_early_stop_patience=100,  # Stop if validation loss doesn't improve for N epochs
        val_loss_min_delta=0.0001,  # Minimum improvement to count as progress
        max_grad_norm=None,  # LEGACY: Fixed gradient clipping threshold. Use adaptive_grad_clip_ratio instead.
        adaptive_grad_clip_ratio=2.0,  # RECOMMENDED: Clip when gradient > loss * this ratio. Adapts to loss scale.
        grad_clip_warning_multiplier=5.0,  # Warn when unclipped gradients exceed threshold * this multiplier.
        track_per_row_losses=False,  # Track per-row loss to identify hardest examples
        per_row_loss_log_top_n=10,  # Number of top difficult rows to log per epoch
        control_check_callback=None,  # Callback to check for control signals (ABORT, PAUSE, FINISH)
        enable_hourly_pickles=False,  # DISABLED: Hourly pickles are expensive and unnecessary (we have checkpoints)
        use_bf16=None,  # BF16 mixed precision training (None=use config.json, True/False=override)
        quick_search_mode=False,  # If True, disable DataLoader workers to prevent OOM during quick architecture search
        max_pre_analysis_data_size=5000,  # Maximum dataset size for pre-analysis (subsampling limit)
        max_oom_retries=3,  # Maximum number of OOM retries with reduced batch size (0 to disable)
        disable_recovery=False,  # If True, never load checkpoints (useful for QA tests requiring fresh training)
        _oom_retry_count=0,  # Internal: current retry count (do not set manually)
        _forced_batch_size=None,  # Internal: forced batch size after OOM retry (do not set manually)
    ):
        """
        Training the model.  This is re-entrant, so we could be coming back into this to pick up
        a training session that was interrupted.

        Arguments
        ---------
            print_callback takes a dictionary of info that gets displayed in the GUI/demo notebooks.
            lr_schedule_segments: Stepwise-constant lr schedule. Expected to have the shape List[(n_steps, lr)]
                where n_steps is how many steps/iterations each lr period should last.
            disable_recovery: If True, never load or resume from existing checkpoints, even if they exist.
                This forces a completely fresh training run from scratch. Useful for QA tests and benchmarks
                that need clean, repeatable training sessions without any checkpoint state.
            
        Default Dropout Schedule
        -------------------------
            Uses 'piecewise_constant' (0.5 → 0.25) which maintains high regularization longer:
            - First 1/3: Hold at 0.5 (strong regularization during exploration)
            - Second 1/3: Ramp 0.5 → 0.25 (gradual reduction as model stabilizes)
            - Final 1/3: Hold at 0.25 (moderate regularization to prevent overfitting)
            
            This prevents the dropout from dropping too low (e.g., 0.14) when training plateaus,
            which helps avoid getting stuck and provides more exploration capability.
        """
        
        # ============================================================================
        # DATALOADER CONTEXT SETUP: Set job context for heartbeat system
        # ============================================================================
        # DataLoader workers need job context to post heartbeats identifying themselves
        from featrix.neural.dataloader_utils import set_dataloader_job_context, clear_dataloader_job_context
        job_id_for_context = getattr(self, 'job_id', None)
        session_id_for_context = self.training_info.get('session_id', None) if hasattr(self, 'training_info') else None
        set_dataloader_job_context(
            job_id=job_id_for_context,
            session_id=session_id_for_context,
            job_type="train_embedding_space"
        )
        
        # ============================================================================
        # OOM RETRY WRAPPER: Catch OOM errors and retry with smaller batch size
        # ============================================================================
        # This wrapper catches FeatrixOOMRetryException and recursively retries training
        # with a smaller batch size. This allows training to adapt to GPU memory limits
        # automatically instead of just crashing.
        try:
            return self._train_impl(
                batch_size=batch_size,
                n_epochs=n_epochs,
                print_progress_step=print_progress_step,
                print_callback=print_callback,
                training_event_callback=training_event_callback,
                optimizer_params=optimizer_params,
                existing_epochs=existing_epochs,
                use_lr_scheduler=use_lr_scheduler,
                lr_schedule_segments=lr_schedule_segments,
                save_state_after_every_epoch=save_state_after_every_epoch,
                use_profiler=use_profiler,
                save_prediction_vector_lengths=save_prediction_vector_lengths,
                enable_weightwatcher=enable_weightwatcher,
                weightwatcher_save_every=weightwatcher_save_every,
                weightwatcher_out_dir=weightwatcher_out_dir,
                enable_dropout_scheduler=enable_dropout_scheduler,
                dropout_schedule_type=dropout_schedule_type,
                initial_dropout=initial_dropout,
                final_dropout=final_dropout,
                movie_frame_interval=movie_frame_interval,
                disable_recovery=disable_recovery,
                val_loss_early_stop_patience=val_loss_early_stop_patience,
                val_loss_min_delta=val_loss_min_delta,
                max_grad_norm=max_grad_norm,
                adaptive_grad_clip_ratio=adaptive_grad_clip_ratio,
                grad_clip_warning_multiplier=grad_clip_warning_multiplier,
                track_per_row_losses=track_per_row_losses,
                per_row_loss_log_top_n=per_row_loss_log_top_n,
                control_check_callback=control_check_callback,
                enable_hourly_pickles=enable_hourly_pickles,
                use_bf16=use_bf16,
                quick_search_mode=quick_search_mode,
                max_pre_analysis_data_size=max_pre_analysis_data_size,
                max_oom_retries=max_oom_retries,
                _oom_retry_count=_oom_retry_count,
                _forced_batch_size=_forced_batch_size,
            )
        except FeatrixOOMRetryException as oom_ex:
            # Clear ALL training state before retry [[memory:7006011]]
            logger.warning("=" * 80)
            logger.warning(f"🔄 OOM RETRY #{_oom_retry_count + 1}/{max_oom_retries}: Reducing batch size {oom_ex.current_batch_size} → {oom_ex.suggested_batch_size}")
            logger.warning("=" * 80)
            
            # Log GPU memory state BEFORE cleanup
            log_gpu_memory("BEFORE OOM CLEANUP", level="warning")
            
            # Extract values BEFORE we delete the exception (it holds tensor references in traceback)
            new_batch_size = oom_ex.suggested_batch_size
            old_batch_size = oom_ex.current_batch_size
            new_retry_count = _oom_retry_count + 1
            
            # Delete exception to release traceback tensor references
            del oom_ex
            
            # CRITICAL: Actually free GPU memory by moving model to CPU temporarily
            # Just calling empty_cache() doesn't free tensors that are still referenced
            if is_cuda_available() and hasattr(self, 'encoder') and self.encoder is not None:
                logger.info("🧹 Moving encoder to CPU to free GPU memory...")
                # Zero gradients first (releases gradient tensors)
                self.encoder.zero_grad(set_to_none=True)
                # Move to CPU (this actually frees GPU memory)
                self.encoder.cpu()
                # Now garbage collect and clear cache
                gc.collect()
                empty_gpu_cache()
                synchronize_gpu()
                # Log memory after clearing
                log_gpu_memory("After moving model to CPU", level="info")
                # Move back to GPU
                device = get_device()
                self.encoder.to(device)
                logger.info(f"🧹 Encoder moved back to GPU, ready for retry with batch_size={new_batch_size}")
            else:
                gc.collect()
            
            # Clear training state (also cleans up DataLoader workers)
            self.reset_training_state()
            
            # Log GPU memory state AFTER cleanup
            stats = log_gpu_memory("AFTER CLEANUP (ready for retry)", level="info")
            if stats:
                logger.info(f"   Memory freed: {(old_batch_size - new_batch_size) / old_batch_size * 100:.1f}% expected reduction from batch_size change")
            
            logger.info("=" * 80)
            logger.info(f"🔄 STARTING RETRY #{new_retry_count} with batch_size={new_batch_size}")
            logger.info("=" * 80)
            
            # Retry with smaller batch size
            return self.train(
                batch_size=new_batch_size,
                n_epochs=n_epochs,
                print_progress_step=print_progress_step,
                print_callback=print_callback,
                training_event_callback=training_event_callback,
                optimizer_params=optimizer_params,
                existing_epochs=existing_epochs,
                use_lr_scheduler=use_lr_scheduler,
                lr_schedule_segments=lr_schedule_segments,
                save_state_after_every_epoch=save_state_after_every_epoch,
                use_profiler=use_profiler,
                save_prediction_vector_lengths=save_prediction_vector_lengths,
                enable_weightwatcher=enable_weightwatcher,
                weightwatcher_save_every=weightwatcher_save_every,
                weightwatcher_out_dir=weightwatcher_out_dir,
                enable_dropout_scheduler=enable_dropout_scheduler,
                dropout_schedule_type=dropout_schedule_type,
                initial_dropout=initial_dropout,
                final_dropout=final_dropout,
                movie_frame_interval=movie_frame_interval,
                val_loss_early_stop_patience=val_loss_early_stop_patience,
                val_loss_min_delta=val_loss_min_delta,
                max_grad_norm=max_grad_norm,
                adaptive_grad_clip_ratio=adaptive_grad_clip_ratio,
                grad_clip_warning_multiplier=grad_clip_warning_multiplier,
                track_per_row_losses=track_per_row_losses,
                per_row_loss_log_top_n=per_row_loss_log_top_n,
                control_check_callback=control_check_callback,
                enable_hourly_pickles=enable_hourly_pickles,
                use_bf16=use_bf16,
                quick_search_mode=quick_search_mode,
                max_pre_analysis_data_size=max_pre_analysis_data_size,
                max_oom_retries=max_oom_retries,
                disable_recovery=disable_recovery,
                _oom_retry_count=new_retry_count,
                _forced_batch_size=new_batch_size,
            )
        finally:
            # ============================================================================
            # CLEANUP DATALOADER CONTEXT
            # ============================================================================
            # Clear the DataLoader job context environment variables
            # This runs whether training succeeds or fails
            clear_dataloader_job_context()
    
    def _train_impl(
        self,
        batch_size=None,
        n_epochs=None,
        print_progress_step=10,
        print_callback=None,
        training_event_callback=None,
        optimizer_params=None,
        existing_epochs=None,
        use_lr_scheduler=True,
        lr_schedule_segments=None,
        save_state_after_every_epoch=True,  # Default True for crash recovery
        use_profiler=False,
        save_prediction_vector_lengths=False,
        enable_weightwatcher=False,
        weightwatcher_save_every=5,
        weightwatcher_out_dir="ww_metrics",
        enable_dropout_scheduler=True,
        dropout_schedule_type="piecewise_constant",
        initial_dropout=0.5,
        final_dropout=0.25,
        movie_frame_interval=3,
        val_loss_early_stop_patience=100,
        val_loss_min_delta=0.0001,
        max_grad_norm=None,
        adaptive_grad_clip_ratio=2.0,
        grad_clip_warning_multiplier=5.0,
        track_per_row_losses=False,
        per_row_loss_log_top_n=10,
        control_check_callback=None,
        enable_hourly_pickles=False,
        use_bf16=None,
        quick_search_mode=False,
        max_pre_analysis_data_size=5000,
        max_oom_retries=3,
        disable_recovery=False,
        _oom_retry_count=0,
        _forced_batch_size=None,
    ):
        """Internal implementation of train() - see train() docstring for parameters."""

        # ============================================================================
        # EARLY ABORT CHECK: Check for ABORT file before any expensive setup
        # ============================================================================
        job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
        output_dir = getattr(self, 'output_dir', None)
        if job_id:
            check_abort_and_raise(job_id, output_dir=output_dir, context="train start")
        
        # ============================================================================
        # AUTO-RESUME: If existing_epochs is None, check for existing checkpoints
        # ============================================================================
        # This allows training to automatically resume after crashes without
        # requiring the caller to manually find and pass the checkpoint epoch.
        # ============================================================================
        if disable_recovery:
            # Recovery is disabled - always start fresh, never load checkpoints
            if existing_epochs is not None and existing_epochs != -1:
                logger.info("=" * 80)
                logger.info("🚫 RECOVERY DISABLED: Ignoring existing_epochs and all checkpoints")
                logger.info("   Starting fresh training from scratch (disable_recovery=True)")
                logger.info("=" * 80)
            existing_epochs = None
        elif existing_epochs is None:
            latest_checkpoint = self.find_latest_checkpoint()
            if latest_checkpoint is not None:
                logger.info("=" * 80)
                logger.info(f"🔄 AUTO-RESUME: Found checkpoint at epoch {latest_checkpoint}")
                logger.info(f"   Training will resume from epoch {latest_checkpoint + 1}")
                logger.info("   To start fresh, delete checkpoint files or pass disable_recovery=True")
                logger.info("=" * 80)
                existing_epochs = latest_checkpoint
        elif existing_epochs == -1:
            # Special value to force fresh start (ignore any checkpoints)
            logger.info("🆕 Fresh start requested (existing_epochs=-1), ignoring any existing checkpoints")
            existing_epochs = None
        
        save_state_epoch_interval = 0
        try:
            save_state_epoch_interval = int(n_epochs // 25)
        except:
            traceback.print_exc()
            save_state_epoch_interval = 10

        # ============================================================================
        # OOM RETRY: If we're retrying after OOM, use forced batch size
        # ============================================================================
        if _forced_batch_size is not None:
            batch_size = _forced_batch_size
            logger.warning("=" * 80)
            logger.warning(f"🔄 OOM RETRY {_oom_retry_count}: Using reduced batch_size={batch_size}")
            logger.warning("=" * 80)
        else:
            # ALWAYS recalculate batch_size to benefit from algorithm improvements
            # This ensures resumed jobs get optimal batch size for their GPU
            old_batch_size = batch_size
            batch_size = ideal_batch_size(self.len_df())
            if old_batch_size and old_batch_size != batch_size:
                logger.info(f"🔄 Batch size recalculated: {old_batch_size} → {batch_size} (GPU-optimized)")
            else:
                logger.info(f"✅ Using calculated batch_size: {batch_size}")
        
        # ============================================================================
        # GPU BATCH SIZE LIMITS: Apply device-specific constraints
        # ============================================================================
        # get_max_batch_size() handles all GPU-specific limits (MPS INT_MAX, etc.)
        # See gpu_utils.py for details.
        # ============================================================================
        from featrix.neural.gpu_utils import get_max_batch_size
        
        # Check if relationship features are enabled
        has_relationship_features = (
            hasattr(self, 'relationship_features') and self.relationship_features is not None  # pylint: disable=no-member
        ) or (
            hasattr(self, 'encoder') and self.encoder is not None and
            hasattr(self.encoder, 'joint_encoder') and self.encoder.joint_encoder is not None and
            hasattr(self.encoder.joint_encoder, 'relationship_extractor') and 
            self.encoder.joint_encoder.relationship_extractor is not None
        )
        
        # Query actual ops_per_pair from extractor (1 if fused, 9 if unfused)
        rel_extractor = getattr(getattr(self.encoder, 'joint_encoder', None), 'relationship_extractor', None)
        actual_ops_per_pair = getattr(rel_extractor, 'ops_per_pair', 1) if rel_extractor else 1
        
        batch_size = get_max_batch_size(
            requested_batch_size=batch_size,
            n_cols=len(self.train_input_data.df.columns),
            n_attention_heads=getattr(self, 'n_attention_heads', 16),
            has_relationship_features=has_relationship_features,
            ops_per_pair=actual_ops_per_pair,
            min_batch_size=128,  # InfoNCE needs larger batches for embedding space
        )

        if n_epochs is None or n_epochs == 0:
            # Auto-calculate epochs based on dataset size and batch size
            from .utils import ideal_epochs_embedding_space
            n_epochs = ideal_epochs_embedding_space(self.len_df(), batch_size)
            logger.info(f"Auto-calculated n_epochs: {n_epochs}")
        
        # CRITICAL: Update self.n_epochs so validation logging and curriculum can use it
        # This was causing phase=N/A because self.n_epochs was None while local n_epochs was 50
        self.n_epochs = n_epochs

        numRows = self.len_df()
        numCols = len(self.train_input_data.df.columns)

        logger.info(f"Training data size: {numCols} columns x {numRows} rows")
        logger.info(f"Columns: {list(self.train_input_data.df.columns)}")
        
        # Log schema evolution history
        if hasattr(self, 'schema_history'):
            self.schema_history.log_summary()

        val_dataloader = None
        # val_dataloader = self.val_dataset

        if print_progress_step is not None:
            assert (
                isinstance(print_progress_step, int) and print_progress_step > 0
            ), f"`print_progress_step` must be an integer greater than 0. Provided value: {print_progress_step}"

        # Initialize dropout_scheduler early to avoid UnboundLocalError in recovery path
        dropout_scheduler = None
        
        # Initialize mask distribution tracker
        self._init_mask_tracker()

        # Multi-architecture predictor selection (only for fresh training and if enabled in config)
        enable_architecture_selection = (
            existing_epochs is None and 
            get_config().get_enable_predictor_architecture_selection()
        )
        if enable_architecture_selection:
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔬 PREDICTOR HEAD ARCHITECTURE SELECTION (BEFORE MAIN EMBEDDING SPACE TRAINING)")
            logger.info("=" * 80)
            logger.info(f"⚠️  IMPORTANT: This selects PREDICTOR HEAD architectures, NOT the embedding space architecture!")
            logger.info(f"   - Embedding space encoder (column_encoder + joint_encoder): FIXED at d_model={self.d_model} (NOT being selected)")
            logger.info(f"   - Predictor heads (column_predictor + joint_predictor): Testing different hidden dimensions (64d, 128d, 192d, 256d)")
            logger.info(f"   - Will test 4 candidate predictor head architectures")
            
            # Use more epochs for architecture selection when GPU is available (faster training)
            if is_gpu_available():
                selection_epochs = 15  # GPU-accelerated: 15 epochs per candidate (sufficient signal, faster)
                logger.info(f"   - GPU detected: Using {selection_epochs} epochs per candidate (GPU-accelerated, fast)")
            else:
                selection_epochs = 15  # CPU-only: 15 epochs per candidate (matched to GPU)
                logger.info(f"   - CPU-only: Using {selection_epochs} epochs per candidate (CPU is slower)")
            
            logger.info(f"   - Each candidate: {selection_epochs} epochs training ONLY predictor heads (embedding space encoder is FROZEN)")
            logger.info(f"   - Embedding space encoder runs forward pass but weights are NOT updated during selection")
            logger.info(f"   - This is FAST because only small predictor head MLPs train, not the full embedding space")
            logger.info(f"   - After selection, MAIN TRAINING will train the FULL EMBEDDING SPACE (encoder + selected predictor heads) for {n_epochs} epochs")
            logger.info(f"   - Total overhead: ~{4 * selection_epochs} epochs (4 candidates × {selection_epochs} epochs) before main training starts")
            logger.info("=" * 80)
            try:
                best_architecture = self._select_best_predictor_architecture(
                    batch_size=batch_size,
                    selection_epochs=selection_epochs,  # GPU: 50 epochs, CPU: 25 epochs
                    val_dataloader=None
                )
                # Replace predictors with the winner
                self._replace_predictors_with_architecture(best_architecture)
                logger.info("=" * 80)
                logger.info("✅ PREDICTOR HEAD ARCHITECTURE SELECTION COMPLETE")
                logger.info("=" * 80)
                logger.info(f"   Selected best predictor head architecture based on validation loss")
                logger.info(f"   Embedding space encoder (d_model={self.d_model}): Unchanged (was fixed during selection)")
                logger.info(f"   Predictor heads: Replaced with selected architecture")
                logger.info(f"   🚀 NOW STARTING MAIN TRAINING: Will train FULL EMBEDDING SPACE (encoder + selected predictor heads) for {n_epochs} epochs")
                logger.info("=" * 80)
            except Exception as e:
                logger.warning(f"⚠️  Architecture selection failed: {e}")
                logger.warning("   Continuing with default architecture...")
                logger.debug(traceback.format_exc())
        
        # ============================================================================
        # BF16 MIXED PRECISION TRAINING SETUP (RTX 4090 / Ampere+ GPUs)
        # ============================================================================
        # BF16 offers ~50% memory savings with better numerical stability than FP16
        # No GradScaler needed (unlike FP16) due to wider dynamic range
        # CRITICAL: Define these BEFORE the if/else block so they're available in both paths
        use_autocast = False
        autocast_dtype = torch.float32
        device_type = get_device_type()  # 'cuda', 'mps', or 'cpu'
        
        # Use config.json value if not explicitly overridden
        if use_bf16 is None:
            use_bf16 = self.use_bf16
        
        if use_bf16:
            if is_cuda_available():
                # Check GPU compute capability (BF16 requires >= 8.0, i.e., Ampere or newer)
                device_prop = get_gpu_device_properties(0)
                compute_capability = device_prop.major + device_prop.minor / 10.0
                
                if compute_capability >= 8.0:
                    # BF16 supported!
                    use_autocast = True
                    autocast_dtype = torch.bfloat16
                    logger.info("=" * 80)
                    logger.info("🔋 BF16 MIXED PRECISION TRAINING ENABLED")
                    logger.info("=" * 80)
                    logger.info(f"   GPU: {device_prop.name}")
                    logger.info(f"   Compute Capability: {compute_capability:.1f} (>= 8.0 required)")
                    logger.info(f"   Memory Savings: ~50% (activations stored in BF16)")
                    logger.info(f"   Numerical Stability: Excellent (wider dynamic range than FP16)")
                    logger.info(f"   Speed: Similar or slightly faster than FP32")
                    logger.info("=" * 80)
                else:
                    logger.warning("=" * 80)
                    logger.warning("⚠️  BF16 REQUESTED BUT GPU DOESN'T SUPPORT IT")
                    logger.warning("=" * 80)
                    logger.warning(f"   GPU: {device_prop.name}")
                    logger.warning(f"   Compute Capability: {compute_capability:.1f} (< 8.0)")
                    logger.warning(f"   BF16 requires Ampere or newer (RTX 30xx, RTX 40xx, A100, etc.)")
                    logger.warning(f"   Falling back to FP32 training")
                    logger.warning("=" * 80)
            else:
                logger.warning("⚠️  BF16 requested but CUDA not available. Using FP32.")
        
        if existing_epochs is not None:
            # Load checkpoint with corruption recovery
            (existing_epochs, base_epoch_index, checkpoint_loaded, 
             d, progress_counter, batches_per_epoch) = self._load_checkpoint_with_recovery(
                existing_epochs, batch_size
            )
            
            # Validate batches_per_epoch is positive after all processing
            if batches_per_epoch <= 0:
                raise ValueError(
                    f"Cannot recover training with batches_per_epoch={batches_per_epoch}. "
                    f"Dataset has {len(self.train_dataset)} samples, batch_size={batch_size}. "
                    f"This usually means the dataset is empty or batch_size is too large."
                )
            
            logger.warning(f"FINAL batches_per_epoch value: {batches_per_epoch} (type: {type(batches_per_epoch)})")
            
            # Fix progress_counter with proper fallback
            logger.warning(f"DEBUG: progress_counter type: {type(progress_counter)}, value: {progress_counter}")
            logger.warning(f"DEBUG: existing_epochs: {existing_epochs}, batches_per_epoch: {batches_per_epoch}")
            if progress_counter is None:
                if batches_per_epoch is None:
                    logger.error("CRITICAL: Cannot calculate progress_counter because batches_per_epoch is STILL None!")
                    progress_counter = 0
                else:
                    # Handle case where existing_epochs might be None (starting from scratch after failed checkpoint)
                    epoch_num = existing_epochs or 0
                    progress_counter = epoch_num * batches_per_epoch
                    logger.warning(f"progress_counter is None, calculated as {epoch_num} × {batches_per_epoch} = {progress_counter}")
            elif isinstance(progress_counter, list) and len(progress_counter) == 1:
                progress_counter = progress_counter[0]
            elif not isinstance(progress_counter, int):
                logger.warning(f"progress_counter restored as {type(progress_counter)}: {progress_counter}, converting to int")
                progress_counter = int(progress_counter)
            # Restore other variables with None protection
            loss, val_loss, last_log_time = self.restore_progress("loss", "val_loss", "last_log_time")
            _encodeTime, _backTime, _lossTime = self.restore_progress("encode_time", "back_time", "loss_time")
            val_dataloader = self.restore_progress("val_dataloader")
            optimizer_params = self.restore_progress("optimizer_params")
            data_loader = self.restore_progress("data_loader")
            lowest_val_loss = self.restore_progress("lowest_val_loss")
            
            # Provide defaults for None values and fix type issues
            if loss is None:
                loss = "not set"
            elif isinstance(loss, list) and len(loss) == 1:
                loss = loss[0] if loss[0] is not None else "not set"
                
            if val_loss is None:
                val_loss = "not set"
            elif isinstance(val_loss, list) and len(val_loss) == 1:
                val_loss = val_loss[0] if val_loss[0] is not None else "not set"
            elif isinstance(val_loss, list):
                logger.warning(f"val_loss restored as list with {len(val_loss)} items: {val_loss}, using 'not set'")
                val_loss = "not set"
                
            if last_log_time is None:
                last_log_time = 0
            elif isinstance(last_log_time, list) and len(last_log_time) == 1:
                last_log_time = last_log_time[0] if last_log_time[0] is not None else 0
                
            if lowest_val_loss is None:
                lowest_val_loss = float("inf")
            elif isinstance(lowest_val_loss, list) and len(lowest_val_loss) == 1:
                lowest_val_loss = lowest_val_loss[0] if lowest_val_loss[0] is not None else float("inf")
            elif isinstance(lowest_val_loss, list):
                logger.warning(f"lowest_val_loss restored as list with {len(lowest_val_loss)} items: {lowest_val_loss}, using inf")
                lowest_val_loss = float("inf")
            elif not isinstance(lowest_val_loss, (int, float)):
                logger.warning(f"lowest_val_loss restored as {type(lowest_val_loss)}: {lowest_val_loss}, using inf")
                lowest_val_loss = float("inf")
            
            # Fix optimizer_params with proper type checking and conversion
            logger.warning(f"DEBUG: optimizer_params type: {type(optimizer_params)}, value: {optimizer_params}")
            if optimizer_params is None:
                logger.warning("optimizer_params is None, using default")
                optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            elif isinstance(optimizer_params, list) and len(optimizer_params) == 1:
                optimizer_params = optimizer_params[0]
                logger.warning(f"optimizer_params extracted from list: {optimizer_params}")
                if optimizer_params is None:
                    logger.warning("optimizer_params extracted from list is None, using default")
                    optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            elif not isinstance(optimizer_params, dict):
                logger.warning(f"optimizer_params restored as {type(optimizer_params)}: {optimizer_params}, using default")
                optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            
            # Ensure optimizer_params is a valid dict
            if not isinstance(optimizer_params, dict):
                logger.error(f"FINAL SAFETY: optimizer_params is STILL not a dict! Type: {type(optimizer_params)}, using default")
                optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            
            logger.warning(f"FINAL optimizer_params: {optimizer_params} (type: {type(optimizer_params)})")
            
            # CRITICAL: ALWAYS recreate DataLoaders during recovery (they can't be properly serialized)
            logger.warning("🔄 FORCING DataLoader recreation during recovery (DataLoaders can't be serialized)")
            
            # CRITICAL: Cleanup old DataLoader workers BEFORE recreation to prevent leaks
            _cleanup_dataloader_workers(data_loader, "training DataLoader")
            _cleanup_dataloader_workers(val_dataloader, "validation DataLoader")
            
            data_loader = None  # Force recreation
            val_dataloader = None  # Force recreation
            
            # Prepare datasets (subsampling for quick_search, duplication for small datasets)
            self._prepare_datasets_for_training(batch_size, quick_search_mode, max_pre_analysis_data_size)
            
            # Recreate DataLoaders (they can't be serialized/restored from checkpoint)
            data_loader, val_dataloader, batches_per_epoch = self._recreate_dataloaders_for_resume(
                batch_size, data_loader, val_dataloader, batches_per_epoch
            )
            
            # Handle case where existing_epochs might be None (starting from scratch after failed checkpoint)
            epoch_num = (existing_epochs or 0) + 1
            self.training_info[f"restart_time_{epoch_num}"] = time.time()
            timeStart = self.training_info.get("start_time")
            
            # Recreate optimizer and schedulers from checkpoint state dicts
            optimizer, scheduler, dropout_scheduler = self._recreate_optimizer_and_schedulers_for_resume(
                optimizer_params=optimizer_params,
                n_epochs=n_epochs,
                batches_per_epoch=batches_per_epoch,
                existing_epochs=existing_epochs,
                base_epoch_index=base_epoch_index,
                use_lr_scheduler=use_lr_scheduler,
                lr_schedule_segments=lr_schedule_segments,
                enable_dropout_scheduler=enable_dropout_scheduler,
                dropout_schedule_type=dropout_schedule_type,
                initial_dropout=initial_dropout,
                final_dropout=final_dropout,
                data_loader=data_loader,
            )
            
            # Reinitialize debug dict if it was None
            if d is None:
                logger.warning("Reinitializing debug dict from scratch")
                d = self._init_d(timeStart=timeStart, n_epochs=n_epochs, batches_per_epoch=batches_per_epoch)
                # Update with current progress
                # Handle case where existing_epochs might be None (starting from scratch after failed checkpoint)
                epoch_num = (existing_epochs or 0) + 1
                d["epoch_idx"] = epoch_num
                d["progress_counter"] = progress_counter
        else:
            lowest_val_loss = float("inf")

            sum_of_a_log = 0
            for name, codec in self.col_codecs.items():
                if isinstance(codec, SetEncoder):
                    logger.info(f"{name} --> set has {len(codec.members_to_tokens)} members")
                    sum_of_a_log += math.log(len(codec.members_to_tokens))
            logger.info(f"Sum of log cardinalities: {sum_of_a_log}")

            # Ensure optimizer_params has valid lr - handle None values
            if optimizer_params is None:
                optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            elif not isinstance(optimizer_params, dict):
                logger.warning(f"optimizer_params is not a dict: {type(optimizer_params)}, using defaults")
                optimizer_params = {"lr": 0.001, "weight_decay": 1e-4}
            else:
                # Ensure lr is not None - use default if missing or None
                if optimizer_params.get("lr") is None:
                    logger.warning(f"optimizer_params has None lr, using default 0.001")
                    optimizer_params = {**optimizer_params, "lr": 0.001}
                # Ensure weight_decay has a default if missing
                if "weight_decay" not in optimizer_params:
                    optimizer_params["weight_decay"] = 1e-4
            
            logger.info(f"🔧 Using optimizer_params: lr={optimizer_params.get('lr')}, weight_decay={optimizer_params.get('weight_decay')}")
            
            # CRITICAL FIX FOR VANISHING PREDICTOR GRADIENTS:
            # Predictors get 80-100× smaller gradients than encoders due to longer gradient path
            # Give predictors 10× higher learning rate to compensate
            base_lr = optimizer_params.get('lr')
            predictor_lr_multiplier = 10.0  # Predictors need higher LR due to vanishing gradients
            
            predictor_params = []
            encoder_params = []
            
            for name, param in self.encoder.named_parameters():
                if 'column_predictor' in name or 'joint_predictor' in name:
                    predictor_params.append(param)
                else:
                    encoder_params.append(param)
            
            logger.info(f"🔧 SEPARATE LEARNING RATES (to fix vanishing predictor gradients):")
            logger.info(f"   Encoder LR: {base_lr:.6e}")
            logger.info(f"   Predictor LR: {base_lr * predictor_lr_multiplier:.6e} ({predictor_lr_multiplier}× higher)")
            logger.info(f"   Reasoning: Predictors get ~80× smaller gradients, need higher LR to compensate")
            
            # Memory optimization: Try to use memory-efficient optimizers
            # Priority: 8-bit AdamW (best memory) > Fused AdamW (best speed) > Regular AdamW
            use_8bit = os.environ.get('FEATRIX_USE_8BIT_ADAM', '1').lower() in ('1', 'true', 'yes')
            
            optimizer_kwargs = {
                'weight_decay': optimizer_params.get('weight_decay', 1e-4),
            }
            
            optimizer_created = False
            
            # Try 8-bit AdamW first (saves ~50% memory by quantizing optimizer states)
            if use_8bit:
                try:
                    import bitsandbytes as bnb
                    logger.info("🔋 Using 8-bit AdamW (saves ~50% optimizer memory via state quantization)")
                    optimizer = bnb.optim.AdamW8bit([
                        {'params': encoder_params, 'lr': base_lr},
                        {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
                    ], **optimizer_kwargs)
                    optimizer_created = True
                except ImportError:
                    logger.info("⚠️  bitsandbytes not available, falling back to fused/regular AdamW")
                except Exception as e:
                    logger.warning(f"⚠️  8-bit AdamW failed: {e}, falling back to fused/regular AdamW")
            
            # Try fused AdamW (PyTorch 2.0+, ~10% faster, no memory savings but better perf)
            if not optimizer_created:
                try:
                    optimizer = torch.optim.AdamW([
                        {'params': encoder_params, 'lr': base_lr},
                        {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
                    ], fused=True, **optimizer_kwargs)
                    logger.info("⚡ Using fused AdamW (10-15% faster than regular AdamW)")
                    optimizer_created = True
                except (TypeError, RuntimeError) as e:
                    logger.info(f"⚠️  Fused AdamW not available ({e}), using regular AdamW")
            
            # Fallback to regular AdamW
            if not optimizer_created:
                optimizer = torch.optim.AdamW([
                    {'params': encoder_params, 'lr': base_lr},
                    {'params': predictor_params, 'lr': base_lr * predictor_lr_multiplier},
                ], **optimizer_kwargs)
                logger.info("📊 Using regular AdamW")
            
            # DEBUG: Verify optimizer has correct parameters
            logger.info("=" * 80)
            logger.info("🔍 OPTIMIZER INITIALIZATION DIAGNOSTIC")
            logger.info("=" * 80)
            logger.info(f"   Optimizer param groups: {len(optimizer.param_groups)}")
            for i, group in enumerate(optimizer.param_groups):
                num_params = len(group['params'])
                lr = group['lr']
                group_name = "Encoders" if i == 0 else "Predictors"
                logger.info(f"   Group {i} ({group_name}): {num_params} parameters, LR={lr:.6e}")
            
            # Count parameters in optimizer vs model
            opt_params_count = sum(len(g['params']) for g in optimizer.param_groups)
            model_trainable_count = sum(1 for p in self.encoder.parameters() if p.requires_grad)
            logger.info(f"   Optimizer manages: {opt_params_count} parameters")
            logger.info(f"   Model has trainable: {model_trainable_count} parameters")
            
            if opt_params_count != model_trainable_count:
                logger.error(f"   💥 CRITICAL: Optimizer param count mismatch!")
                logger.error(f"   Optimizer has {opt_params_count} params but model has {model_trainable_count} trainable params!")
                logger.error(f"   Some trainable parameters are NOT in optimizer - they won't update!")
            else:
                logger.info(f"   ✅ Optimizer parameter count matches model trainable parameters")
            logger.info("=" * 80)
            
            # DEBUG: Check which parameters are trainable
            logger.info("🔍 PARAMETER TRAINABILITY CHECK:")
            predictor_trainable = 0
            predictor_frozen = 0
            encoder_trainable = 0
            encoder_frozen = 0
            
            for name, param in self.encoder.named_parameters():
                if 'column_predictor' in name or 'joint_predictor' in name:
                    if param.requires_grad:
                        predictor_trainable += 1
                    else:
                        predictor_frozen += 1
                        logger.warning(f"   ❌ PREDICTOR FROZEN: {name}")
                elif 'joint_encoder' in name or 'column_encoder' in name:
                    if param.requires_grad:
                        encoder_trainable += 1
                    else:
                        encoder_frozen += 1
                        logger.warning(f"   ❌ ENCODER FROZEN: {name}")
            
            logger.info(f"   Predictors: {predictor_trainable} trainable, {predictor_frozen} frozen")
            logger.info(f"   Encoders: {encoder_trainable} trainable, {encoder_frozen} frozen")
            
            if predictor_frozen > 0:
                logger.error(f"💥 CRITICAL: {predictor_frozen} predictor parameters are FROZEN!")
                logger.error(f"   Joint and marginal losses CANNOT improve if predictors are frozen!")
                logger.error(f"   This explains why joint/marginal losses are stuck!")
            
            if encoder_frozen > 0:
                logger.error(f"💥 CRITICAL: {encoder_frozen} encoder parameters are FROZEN!")
                logger.error(f"   Spread and marginal losses CANNOT improve if encoders are frozen!")
                logger.error(f"   This explains why spread/marginal losses are stuck!")
            
            progress_counter = 0

            timeStart = time.time()
            self.training_start_time = timeStart  # Track for elapsed time in logs
            self.training_info["start_time"] = timeStart

            # Check if dataset is too small and reduce batch_size if needed
            train_dataset_size = len(self.train_dataset)
            if train_dataset_size < batch_size:
                old_batch_size = batch_size
                batch_size = train_dataset_size  # Reduce to dataset size
                logger.warning(
                    f"⚠️  Dataset too small: {train_dataset_size} samples < batch_size {old_batch_size}. "
                    f"Reducing batch_size to {batch_size} to avoid artificial duplication."
                )
                # Don't duplicate training data - it artificially inflates training and gives misleading metrics
            
            # Check if validation dataset is too small and reduce batch_size if needed
            val_dataset_size = len(self.val_dataset)
            if val_dataset_size < batch_size:
                old_batch_size = batch_size
                batch_size = val_dataset_size  # Reduce to dataset size
                logger.warning(
                    f"⚠️  Validation dataset too small: {val_dataset_size} samples < batch_size {old_batch_size}. "
                    f"Reducing batch_size to {batch_size} to avoid artificial duplication."
                )
                # Don't duplicate validation data - it gives misleading validation metrics

            if self.train_input_data.project_row_meta_data_list is None:
                logger.info("=" * 80)
                logger.info("🚀 CREATING REAL TRAINING DATALOADER")
                logger.info("=" * 80)
                # Regular vector space - use multiprocess dataloader
                # CRITICAL: In quick_search_mode, disable workers to prevent OOM when running many configs in sequence
                train_num_workers = 0 if quick_search_mode else None
                if quick_search_mode:
                    logger.info("🔍 Quick search mode: Disabling DataLoader workers to prevent OOM")
                train_dl_kwargs = create_dataloader_kwargs(
                    batch_size=batch_size,
                    shuffle=True,
                    drop_last=True,
                    num_workers=train_num_workers,
                    dataset_size=len(self.train_input_data.df),
                    num_columns=len(self.train_input_data.df.columns),
                )
                logger.info(f"📦 Training DataLoader kwargs: {train_dl_kwargs}")
                
                # CRITICAL: Check for existing workers before creating new DataLoader
                # This helps detect worker accumulation issues
                existing_workers_before = _check_and_cleanup_existing_workers(context=" before creating training DataLoader")
                if existing_workers_before > 0:
                    logger.warning(
                        f"⚠️  Found {existing_workers_before} existing worker(s) before creating training DataLoader. "
                        f"This may indicate worker accumulation from previous DataLoader recreations."
                    )
                
                # CRITICAL: Pre-flight memory check to prevent OOM during training
                # Check if we have enough RAM/VRAM for training with these parameters
                try:
                    from lib.system_health_monitor import check_training_memory_requirements
                    num_workers = train_dl_kwargs.get('num_workers', 0)
                    mem_check = check_training_memory_requirements(
                        num_workers=num_workers,
                        batch_size=batch_size,
                        dataset_size=len(self.train_input_data.df),
                        gpu_available=is_gpu_available(),
                        print_warnings=True  # Print warnings if memory is tight
                    )
                    # Note: We don't block training even if memory is insufficient
                    # Just warn the user so they can make informed decisions
                    if not mem_check['sufficient_memory']:
                        logger.warning("⚠️  Training may fail with OOM. Consider the recommendations above.")
                except Exception as e:
                    logger.debug(f"Could not perform pre-flight memory check: {e}")
                
                data_loader = DataLoader(
                    self.train_dataset,
                    collate_fn=collate_tokens,
                    **train_dl_kwargs
                )
                # Store reference for cleanup during OOM retry (see reset_training_state)
                self._current_data_loader = data_loader
                logger.info(f"✅ Training DataLoader created with num_workers={train_dl_kwargs.get('num_workers', 0)}")
                logger.info("=" * 80)

                # CRITICAL: Check for existing training workers before creating validation workers
                # This prevents having both training and validation workers active simultaneously,
                # which doubles memory usage and can cause OOM
                existing_workers = _check_and_cleanup_existing_workers(context=" before creating validation DataLoader")
                if existing_workers > 0:
                    logger.warning(
                        f"⚠️  Found {existing_workers} existing DataLoader worker(s) still active. "
                        f"Consider shutting down training workers before validation to prevent OOM."
                    )
                
                # CRITICAL: Reduce validation workers based on available VRAM to prevent OOM
                # In quick_search_mode, always use 0 workers to prevent OOM when running many configs in sequence
                val_num_workers = None
                if quick_search_mode:
                    val_num_workers = 0
                    logger.info("🔍 Quick search mode: Disabling validation DataLoader workers to prevent OOM")
                elif is_gpu_available():
                    try:
                        allocated = get_gpu_memory_allocated()
                        reserved = get_gpu_memory_reserved()
                        total_memory = (get_gpu_device_properties(0).total_memory / (1024**3)) if get_gpu_device_properties(0) else 0.0
                        free_vram = total_memory - reserved
                        
                        worker_vram_gb = 0.6
                        safety_margin_gb = 20.0
                        available_for_workers = max(0, free_vram - safety_margin_gb)
                        max_workers_by_vram = int(available_for_workers / worker_vram_gb)
                        
                        from featrix.neural.dataloader_utils import get_optimal_num_workers
                        default_workers = get_optimal_num_workers(dataset_size=len(self.val_input_data.df))
                        
                        # Cap based on total GPU memory: ≤16GB GPUs get max 2 workers, >16GB (4090=24GB) get max 4
                        max_val_workers = 2 if total_memory <= 16 else 4
                        val_num_workers = min(default_workers, max_workers_by_vram, max_val_workers)
                        val_num_workers = max(0, val_num_workers)
                        
                        logger.info(f"🔍 Validation worker calculation: free_vram={free_vram:.1f}GB, total_memory={total_memory:.1f}GB → {val_num_workers} workers (max {max_val_workers})")
                    except Exception as e:
                        logger.warning(f"Could not calculate optimal validation workers: {e}, using 0")
                        val_num_workers = 0
                
                val_dl_kwargs = create_dataloader_kwargs(
                    batch_size=batch_size,
                    shuffle=True,
                    drop_last=True,
                    num_workers=val_num_workers,
                    dataset_size=len(self.val_input_data.df),
                    num_columns=len(self.val_input_data.df.columns),
                )
                logger.info(f"📦 Validation DataLoader kwargs: {val_dl_kwargs}")
                val_dataloader = DataLoader(
                    self.val_dataset,
                    collate_fn=collate_tokens,
                    **val_dl_kwargs
                )
                # Store reference for cleanup during OOM retry (see reset_training_state)
                self._current_val_dataloader = val_dataloader
                logger.info(f"✅ Validation DataLoader created with num_workers={val_dl_kwargs.get('num_workers', 0)}, persistent_workers={val_dl_kwargs.get('persistent_workers', False)}")

                batches_per_epoch = len(data_loader)
            else:
                logger.info("Using batch sampler data loader for multi-dataset training with multiprocess support")
                mySampler = DataSpaceBatchSampler(batch_size, self.train_input_data)
                # Note: batch_sampler is mutually exclusive with batch_size/shuffle/drop_last
                # CRITICAL: In quick_search_mode, disable workers to prevent OOM when running many configs in sequence
                sampler_num_workers = 0 if quick_search_mode else None
                if quick_search_mode:
                    logger.info("🔍 Quick search mode: Disabling batch sampler DataLoader workers to prevent OOM")
                sampler_dl_kwargs = create_dataloader_kwargs(
                    batch_size=batch_size,
                    shuffle=False,  # Not used with batch_sampler
                    drop_last=False,  # Not used with batch_sampler
                    num_workers=sampler_num_workers,
                    dataset_size=len(self.train_input_data.df),
                    num_columns=len(self.train_input_data.df.columns),
                )
                sampler_dl_kwargs.pop('batch_size', None)
                sampler_dl_kwargs.pop('shuffle', None)
                sampler_dl_kwargs.pop('drop_last', None)
                
                data_loader = DataLoader(
                    self.train_dataset,
                    batch_sampler=mySampler,
                    collate_fn=collate_tokens,
                    **sampler_dl_kwargs
                )
                # the sampler's len() is the number of rows, not the number of batches.
                batches_per_epoch = int(math.ceil(len(data_loader) / batch_size))
            
            # Validate batches_per_epoch before proceeding (should never be 0 after duplication)
            if batches_per_epoch == 0:
                raise ValueError(
                    f"Cannot train with 0 batches per epoch. "
                    f"Dataset has {len(self.train_dataset)} samples, batch_size={batch_size}. "
                    f"This should not happen after row duplication - there may be an issue with the DataLoader."
                )
            
            logger.info(f"Calculated batches_per_epoch: {batches_per_epoch} (dataset_size={len(self.train_dataset)}, batch_size={batch_size})")
            
            d = self._init_d(timeStart=timeStart,
                             n_epochs=n_epochs,
                             batches_per_epoch=batches_per_epoch)

            if use_lr_scheduler:
                if lr_schedule_segments is not None:
                    # LambdaLR scheduler can be used to create very flexible schedulers,
                    # but we use it just to create segments of fixed LR.
                    scheduler = LambdaLR(
                        optimizer,
                        lr_lambda=self._get_lambda_lr(lr_schedule_segments),
                    )
                else:
                    # Use LRTimeline for intelligent adaptive scheduling
                    # CRITICAL: For K-fold CV, use TOTAL expected epochs, not just this fold's epochs
                    # Otherwise scheduler restarts every fold (LR jumps back up)
                    scheduler_n_epochs = n_epochs
                    if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                        # Estimate total epochs across all folds for smooth LR schedule
                        scheduler_n_epochs = self._kv_fold_epoch_offset + n_epochs
                        logger.info(f"📐 K-fold CV scheduler: using total_epochs={scheduler_n_epochs} (offset={self._kv_fold_epoch_offset}, fold_epochs={n_epochs})")
                    
                    # DIAGNOSTIC: Log values before calculation
                    logger.warning(f"🔍 DIAGNOSTIC: n_epochs={n_epochs} (type: {type(n_epochs)}), batches_per_epoch={batches_per_epoch} (type: {type(batches_per_epoch)})")
                    logger.warning(f"🔍 DIAGNOSTIC: train_dataset length={len(self.train_dataset)}, batch_size={batch_size}")
                    logger.warning(f"🔍 DIAGNOSTIC: data_loader length={len(data_loader) if data_loader is not None else 'None'}")
                    
                    # Create LRTimeline with custom 4-phase schedule
                    max_lr = optimizer_params["lr"]
                    base_lr = max_lr / 10.0  # Start from 10% of max LR
                    min_lr = max_lr / 100.0  # End at 1% of max LR
                    
                    scheduler = LRTimeline(
                        n_epochs=scheduler_n_epochs,
                        base_lr=base_lr,
                        max_lr=max_lr,
                        min_lr=min_lr,
                        aggressive_warmup_pct=0.05,  # 5% aggressive ramp
                        gentle_warmup_pct=0.05,      # 5% gentle ramp
                        onecycle_pct=0.50,           # 50% OneCycle productive phase
                    )
                    
                    # Store scheduler for access in intervention methods
                    self._train_scheduler = scheduler
                    
                    logger.info(f"🎯 LRTimeline: {scheduler_n_epochs} epochs, base_lr={base_lr:.2e}, max_lr={max_lr:.2e}, min_lr={min_lr:.2e}")
                    logger.info(f"   Phase 1 (0-5%): Aggressive warmup {base_lr:.2e} → {max_lr:.2e}")
                    logger.info(f"   Phase 2 (5-10%): Gentle warmup to maintain {max_lr:.2e}")
                    logger.info(f"   Phase 3 (10-60%): OneCycle productive phase")
                    logger.info(f"   Phase 4 (60-100%): Linear cooldown → {min_lr:.2e}")
            else:
                # Always have a scheduler - use constant LR if scheduling is disabled
                constant_lr = optimizer_params["lr"]
                scheduler = LRTimeline(
                    n_epochs=n_epochs,
                    base_lr=constant_lr,
                    max_lr=constant_lr,
                    min_lr=constant_lr,
                    aggressive_warmup_pct=0.0,
                    gentle_warmup_pct=0.0,
                    onecycle_pct=0.0,
                )
                self._train_scheduler = scheduler
                logger.info(f"📊 Constant LR scheduler: {constant_lr:.2e} (use_lr_scheduler=False)")
            loss = "not set"
            val_loss = "not set"
            last_log_time = 0
            base_epoch_index = 0

        # Initialize TrainingHistoryDB for SQLite-based storage (prevents memory leaks)
        # Save to qa.save subdirectory to keep output organized
        qa_save_dir = os.path.join(self.output_dir, "qa.save")
        os.makedirs(qa_save_dir, exist_ok=True)
        history_db_path = os.path.join(qa_save_dir, "training_history.db")
        self.history_db = TrainingHistoryDB(history_db_path)
        logger.info(f"💾 Training history database initialized: {history_db_path}")

        if existing_epochs is not None and "arguments" not in self.training_info:
            self.training_info["arguments"] = self.safe_dump(locals())

        if print_callback is not None:
            print_callback(d)

        # LR multiplier for NO_LEARNING recovery
        lr_boost_multiplier = 1.0
        lr_boost_epochs_remaining = 0
        
        # Temperature multiplier for NO_LEARNING recovery
        temp_boost_multiplier = 1.0
        
        # Intervention stage tracking
        intervention_stage = 0  # 0=none, 1=3x LR, 2=2x temp, 3=2x LR again, 4=2x temp again, 5=converged
        epochs_since_last_intervention = 0
        intervention_patience = 10  # Wait 10 epochs before escalating
        
        # Gradient tracking statistics
        grad_clip_stats = {
            "total_batches": 0,
            "clipped_batches": 0,
            "max_unclipped_norm": 0.0,
            "max_clipped_norm": 0.0,
            "sum_unclipped_norms": 0.0,
            "sum_clipped_norms": 0.0,
            "large_gradient_warnings": 0,
            "gradient_norms_history": [],  # Store last 100 for analysis
            "loss_values_history": [],  # Store corresponding loss values
            "max_grad_loss_ratio": 0.0,  # Track max ratio observed
        }
        
        # OOM tracking for graceful recovery
        # SMART OOM DETECTION: With small datasets (1 batch/epoch), we need to track OOMs
        # across epochs since we can only get 1 OOM per epoch. We use:
        # - oom_count_this_epoch: resets each epoch
        # - consecutive_oom_epochs: increments when ANY batch OOMs, resets when an epoch completes cleanly
        # - oom_count_total: cumulative OOM count for logging
        oom_stats = {
            "oom_count_this_epoch": 0,
            "oom_count_total": 0,
            "consecutive_oom_epochs": 0,  # Track consecutive epochs with at least 1 OOM
            "max_oom_per_epoch": 3,  # If we get more than 3 OOM errors per epoch, reduce batch size
            "max_consecutive_oom_epochs": 2,  # If we OOM in 2+ consecutive epochs, reduce batch size
            "batches_skipped_this_epoch": 0,
            "batch_size_reductions": _oom_retry_count,  # Track how many times we've reduced batch size (starts from current retry count)
            "max_batch_size_reductions": max_oom_retries,  # From train() parameter
            "current_batch_size": batch_size,  # The batch size we're actually using this attempt
            "retry_attempt": _oom_retry_count,  # Which retry attempt this is (0 = first try)
        }
        
        # Log OOM retry status at start of training
        if _oom_retry_count > 0:
            logger.warning("=" * 80)
            logger.warning(f"🔄 OOM RECOVERY: This is retry attempt #{_oom_retry_count}")
            logger.warning(f"   Using reduced batch_size={batch_size}")
            logger.warning(f"   Max retries allowed: {max_oom_retries}")
            logger.warning("=" * 80)
        
        # Determine clipping mode
        use_adaptive_clipping = adaptive_grad_clip_ratio is not None
        
        if use_adaptive_clipping:
            logger.info(f"🔧 ADAPTIVE gradient clipping: will clip when gradient > loss × {adaptive_grad_clip_ratio:.1f}")
            logger.info(f"   This adapts to loss magnitude (which scales with number of columns)")
            if grad_clip_warning_multiplier is not None:
                logger.info(f"   Will warn when ratio > {adaptive_grad_clip_ratio * grad_clip_warning_multiplier:.1f}")
            grad_clip_warning_threshold = None  # Will be computed per-batch
        else:
            logger.warning("⚠️  GRADIENT CLIPPING DISABLED")
            logger.warning("   This is not recommended - gradients can explode")
            grad_clip_warning_threshold = None
        

        max_progress = n_epochs * batches_per_epoch
        # Print every 1% of progress if it is less than the original progress step but don't go to 0
        print_progress_step = max(
            int(min((max_progress / 100), print_progress_step)), 1
        )
        logger.info(f"Training configuration:")
        logger.info(f"  Epochs for this training run: {n_epochs} (this may be per-fold if using cross-validation)")
        logger.info(f"  Batches per epoch: {batches_per_epoch}")
        logger.info(f"  Max progress: {max_progress}")
        logger.info(f"  Print progress step: {print_progress_step}")
        
        # WeightWatcher setup if enabled  
        weightwatcher_job_id = None
        if enable_weightwatcher:
            # Use job ID from training_info if available for file organization
            weightwatcher_job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
            logger.info(f"🔍 WeightWatcher enabled: saving every {weightwatcher_save_every} epochs to {weightwatcher_out_dir}")

        # DropoutScheduler setup if enabled (only if not already restored from checkpoint)
        if enable_dropout_scheduler and dropout_scheduler is None:
            dropout_scheduler = create_dropout_scheduler(
                schedule_type=dropout_schedule_type,
                initial_dropout=initial_dropout,
                final_dropout=final_dropout,
                total_epochs=n_epochs
            )
            logger.info(f"📉 DropoutScheduler enabled: {dropout_schedule_type} ({initial_dropout:.3f} → {final_dropout:.3f})")

        # Pre-warm string cache with ALL strings to prevent cache misses during training
        self.pre_warm_string_cache()

        # Save data snapshot for async movie frame generation
        self._save_movie_data_snapshot(movie_frame_interval)

        # raise Exception("stop")

        logger.info("Setting encoder to training mode")
        self.encoder.train()

        # Profiling is resource-intensive, so we only enable it if needed.
        if use_profiler:
            profiler_ctx_mngr = self._prep_profiler()
        else:
            profiler_ctx_mngr = nullcontext()

        timed_data_loader = (data_loader)
        
        # Track when to resample train/val split
        # Use minimum of 25 epochs per split for robust learning
        # For very long training (>250 epochs), allow resampling every 10%
        resample_interval = max(25, n_epochs // 10)
        num_splits = (n_epochs // resample_interval) + 1  # +1 for initial split
        logger.info(f"🔄 Train/val resampling enabled: every {resample_interval} epochs (min 25 epochs/split, {num_splits} total splits)")
        
        val_loss = float('inf')
        
        # Track time for hourly pickle saves
        training_start_time = time.time()
        
        # MEMORY LEAK DETECTION: Track VRAM usage throughout epoch to identify leaks
        def _log_vram_usage(context: str, epoch_idx: int, batch_idx: int = None, quiet: bool = False):
            """Log VRAM usage with context for leak detection
            
            Args:
                context: Description of when VRAM is being logged
                epoch_idx: Current epoch index
                batch_idx: Current batch index (optional)
                quiet: If True, use debug level instead of info level
            """
            if not is_gpu_available():
                return
            
            allocated = get_gpu_memory_allocated()  # GB
            reserved = get_gpu_memory_reserved()  # GB
            max_allocated = get_max_gpu_memory_allocated()  # GB
            
            batch_str = f"batch={batch_idx}" if batch_idx is not None else ""
            batch_prefix = f"[{batch_str}] " if batch_str else ""
            
            # Use debug level for quieter logging (can be enabled when debugging memory issues)
            log_level = logger.debug if quiet else logger.info
            # Dynamic width: context column only as wide as needed (no fixed padding)
            log_level(f"🔍 VRAM {batch_prefix}[{context}] Alloc={allocated:5.2f}GB  Reserved={reserved:5.2f}GB  Peak={max_allocated:5.2f}GB")
            
            # Track VRAM growth between checkpoints (always use debug level - too noisy for info)
            if not hasattr(self, '_vram_tracker'):
                self._vram_tracker = {'last_allocated': allocated, 'last_reserved': reserved}
            else:
                alloc_delta = allocated - self._vram_tracker['last_allocated']
                reserved_delta = reserved - self._vram_tracker['last_reserved']
                if abs(alloc_delta) > 0.1 or abs(reserved_delta) > 0.1:  # Log if >100MB change
                    logger.debug(f"🔍 VRAM DELTA: Alloc {alloc_delta:+.2f}GB   Reserved {reserved_delta:+.2f}GB")
                self._vram_tracker['last_allocated'] = allocated
                self._vram_tracker['last_reserved'] = reserved
        
        # Log training start banner
        self._log_training_start_banner(n_epochs, batch_size)
        
        # CRITICAL: Verify all encoder parameters are trainable before training starts
        self._log_parameter_trainability()
        
        with profiler_ctx_mngr as profiler:
            for epoch_idx in range(base_epoch_index, n_epochs):
                # Initialize val_components at start of epoch (will be populated after validation)
                val_components = None
                
                # Reset mask bias tracker at start of epoch
                from featrix.neural.mask_bias_tracker import reset_mask_bias_tracker, get_mask_bias_tracker
                reset_mask_bias_tracker()
                
                # MEMORY LEAK DETECTION: Log VRAM at start of epoch
                # First 3 epochs are NOT quiet to help debug OOM issues
                # After that, use quiet mode unless there have been OOM errors
                vram_quiet = epoch_idx >= 3 and oom_stats["oom_count_total"] == 0
                _log_vram_usage("start of epoch", epoch_idx, quiet=vram_quiet)
                
                # System health monitoring
                self._check_system_health(epoch_idx)
                
                # PERIODIC EMBEDDING QUALITY CHECK: Run at 25%, 50%, 75% of training
                self._periodic_embedding_quality_check(epoch_idx, n_epochs)
                
                # Reset tiny gradient warning flag
                self._tiny_grad_warned_this_epoch = False
                
                # Track consecutive OOM epochs and reset per-epoch counters
                self._track_oom_consecutive_epochs(oom_stats)
                
                # Periodic garbage collection and SQLite flush
                self._periodic_gc_and_flush(epoch_idx)
                
                # Check for PUBLISH flag - save embedding space for single predictor training
                self._check_publish_and_save(epoch_idx)
                
                # UPDATE ADAPTIVE ENCODER EPOCH COUNTERS for strategy pruning
                self._update_encoder_epoch_counters(epoch_idx, n_epochs)
                
                # Reset per-epoch gradient statistics
                self._reset_per_epoch_grad_stats(grad_clip_stats)
                
                # Decay LR boost multiplier if active
                if lr_boost_epochs_remaining > 0:
                    lr_boost_epochs_remaining -= 1
                    if lr_boost_epochs_remaining == 0:
                        lr_boost_multiplier = 1.0
                        logger.info(f"⏰ LR boost expired, returning to 1.0x multiplier")
                
                # Gradual data rotation: swap out a small fraction of train/val data
                # Initialize rotation settings if not present (backward compatibility with old checkpoints)
                if not hasattr(self, '_rotation_interval'):
                    self._rotation_interval = max(5, n_epochs // 50)
                    self._rotation_fraction = 0.05
                    logger.info(f"🔄 Initialized gradual data rotation: every {self._rotation_interval} epochs, rotate {self._rotation_fraction*100:.0f}% of data")
                
                val_set_rotated = False  # Track if we rotated this epoch
                if epoch_idx > 0 and epoch_idx % self._rotation_interval == 0 and self._rotation_interval > 0:
                    val_set_rotated = True
                    data_loader, val_dataloader, timed_data_loader = self._perform_gradual_data_rotation(
                        epoch_idx, n_epochs, batch_size, data_loader, val_dataloader, collate_tokens
                    )
                
                epoch_start_time_now = time.time()
                training_event_dict = {
                    "encoder_timing": [],
                    "loss_timing": [],
                    "loop_timing": [],
                    "loss_details": [],
                    "resource_usage": [],
                    "prediction_vec_lengths": [],
                }
                
                # Initialize training loss accumulation for this epoch
                train_loss_sum = 0.0
                train_batch_count = 0
                train_batch_losses = []  # Store individual batch losses for diagnostics
                train_batch_sizes = []   # Store batch sizes for diagnostics

                # Apply K-fold CV offset if present (makes K-fold CV invisible - epochs are cumulative)
                cumulative_epoch_idx = epoch_idx
                if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                    cumulative_epoch_idx = epoch_idx + self._kv_fold_epoch_offset
                
                d["epoch_idx"] = 1 + cumulative_epoch_idx  # Use cumulative epoch for callbacks
                
                # Set current epoch in logging context for standardized logging format
                from featrix.neural.logging_config import current_epoch_ctx
                current_epoch_ctx.set(cumulative_epoch_idx + 1)  # Use 1-indexed epoch for display
                
                # Set learning rate for this epoch using LRTimeline (if not using LambdaLR)
                if isinstance(scheduler, LRTimeline):
                    scheduler.set_epoch(cumulative_epoch_idx)
                    epoch_lr = scheduler.get_current_lr()
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = epoch_lr
                    
                    # Record actual LR used (will be updated if boost is applied)
                    actual_lr = optimizer.param_groups[0]['lr'] * lr_boost_multiplier
                    scheduler.record_actual_lr(cumulative_epoch_idx, actual_lr)
                    
                    # Log LR periodically (every 10 epochs or first/last)
                    if cumulative_epoch_idx == 0 or (cumulative_epoch_idx + 1) % 10 == 0 or cumulative_epoch_idx == n_epochs - 1:
                        progress_pct = (cumulative_epoch_idx + 1) / n_epochs * 100
                        logger.info(f"📈 LRTimeline: epoch {cumulative_epoch_idx + 1}/{n_epochs} ({progress_pct:.1f}%), LR={epoch_lr:.6e}")
                        if lr_boost_multiplier != 1.0:
                            logger.info(f"   → With boost: {actual_lr:.6e} ({lr_boost_multiplier:.2f}x)")
                
                # Log cool epoch banner (every epoch)
                try:
                    from featrix.neural.training_banner import log_epoch_banner
                    log_epoch_banner(cumulative_epoch_idx + 1, n_epochs, training_type="ES")
                except Exception as e:
                    logger.debug(f"Could not log epoch banner: {e}")
                    # Fall back to simple log
                    if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                        logger.info(f"🚀 Starting epoch {cumulative_epoch_idx + 1} ({batches_per_epoch} batches)")
                    else:
                        logger.info(f"🚀 Starting epoch {cumulative_epoch_idx + 1}/{n_epochs} ({batches_per_epoch} batches)")
                
                # Track last batch log time for rate limiting (max 1 log per minute)
                if not hasattr(self, '_last_batch_log_time'):
                    self._last_batch_log_time = {}
                if epoch_idx not in self._last_batch_log_time:
                    self._last_batch_log_time[epoch_idx] = time.time()
                
                # ============================================================================
                # DYNAMIC RELATIONSHIP PRUNING: Prune after exploration phase
                # ============================================================================
                if hasattr(self.encoder, 'joint_encoder') and hasattr(self.encoder.joint_encoder, 'relationship_extractor'):
                    rel_extractor = self.encoder.joint_encoder.relationship_extractor
                    
                    # Set dataset_hash and session_id for meta-learning scoring (only once)
                    if not hasattr(rel_extractor, '_metadata_set'):
                        if hasattr(self, '_dataset_hash') and self._dataset_hash:  # pylint: disable=no-member
                            rel_extractor._dataset_hash = self._dataset_hash  # pylint: disable=no-member
                        if hasattr(self, 'session_id') and self.session_id:  # pylint: disable=no-member
                            rel_extractor._session_id = self.session_id  # pylint: disable=no-member
                        elif hasattr(self, 'job_id') and self.job_id:  # pylint: disable=no-member
                            rel_extractor._session_id = self.job_id  # pylint: disable=no-member
                        rel_extractor._metadata_set = True
                    
                    # Check if this is a DynamicRelationshipExtractor and if we should prune
                    if hasattr(rel_extractor, 'should_prune') and hasattr(rel_extractor, 'current_epoch'):
                        # Update current epoch in extractor
                        rel_extractor.current_epoch = cumulative_epoch_idx
                        
                        # During exploration: track contributions and log progress
                        if rel_extractor.pruned_pairs_per_column is None:  # Still exploring
                            # Track contribution snapshot for stability analysis
                            if hasattr(rel_extractor, 'track_contribution_snapshot'):
                                rel_extractor.track_contribution_snapshot()
                            
                            # Log exploration progress (only every few epochs to avoid spam)
                            if hasattr(rel_extractor, 'log_exploration_progress') and cumulative_epoch_idx % 2 == 0:
                                rel_extractor.log_exploration_progress()
                        
                        # Prune at the end of exploration phase (old hard pruning method)
                        if rel_extractor.should_prune():
                            logger.info("")
                            logger.info("🔪 Relationship pruning triggered at epoch {}".format(cumulative_epoch_idx))
                            rel_extractor.prune_to_top_relationships()
                        
                        # Progressive pruning: gradually disable relationships each epoch
                        if hasattr(rel_extractor, 'should_progressive_prune') and rel_extractor.should_progressive_prune():
                            rel_extractor.progressive_prune_relationships()
                
                # ============================================================================
                # CURRICULUM LEARNING: Dynamic loss weight adjustment
                # ============================================================================
                # CRITICAL FIX: Calculate curriculum epochs ONCE before branching
                # Use cumulative epoch for curriculum when doing K-fold CV
                curriculum_epoch = cumulative_epoch_idx  # Use cumulative epoch (includes fold offset)
                curriculum_n_epochs = n_epochs  # Default: use current fold's n_epochs
                
                # If K-fold CV, estimate total expected epochs across all folds
                # This ensures curriculum progresses smoothly instead of restarting each fold
                if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                    # Estimate total epochs = current_offset + current_fold_epochs
                    # This is a conservative estimate (actual total may be higher if more folds remain)
                    curriculum_n_epochs = self._kv_fold_epoch_offset + n_epochs
                    if epoch_idx == 0:  # Only log on first epoch of each fold
                        logger.info(f"📐 K-fold CV curriculum: using cumulative_epoch={curriculum_epoch}, total_epochs={curriculum_n_epochs} (offset={self._kv_fold_epoch_offset}, fold_epochs={n_epochs})")
                
                # Skip curriculum updates if we're in forced finalization mode
                if hasattr(self, '_forced_spread_finalization') and self._forced_spread_finalization:
                    # Keep the forced weights (1.0, 0.1, 1.0)
                    spread_weight = self.encoder.config.loss_config.spread_loss_weight
                    marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
                    joint_weight = self.encoder.config.loss_config.joint_loss_weight
                else:
                    # Compute new loss weights based on training progress
                    spread_weight, marginal_weight, joint_weight = self._compute_loss_weights(curriculum_epoch, curriculum_n_epochs)
                
                old_spread_weight = self.encoder.config.loss_config.spread_loss_weight
                old_marginal_weight = self.encoder.config.loss_config.marginal_loss_weight
                old_joint_weight = self.encoder.config.loss_config.joint_loss_weight
                
                # DEBUG: Log computed weights on first epoch
                if epoch_idx == 0:
                    logger.info(f"📐 Curriculum weights computed: spread={spread_weight:.4f}, marginal={marginal_weight:.4f}, joint={joint_weight:.4f}")
                    # NOTE: Parameter trainability already checked in _log_parameter_trainability() before epoch loop
                
                # Update all three weights in the encoder's loss config (unless in forced mode, then they stay the same)
                self.encoder.config.loss_config.spread_loss_weight = spread_weight
                self.encoder.config.loss_config.marginal_loss_weight = marginal_weight
                self.encoder.config.loss_config.joint_loss_weight = joint_weight
                
                # Get current phase name for logging
                # CRITICAL: Use same epoch calculation as curriculum weight calculation!
                # Otherwise phase name won't match actual weights during K-fold CV
                phase_name_epoch = cumulative_epoch_idx if (hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None) else epoch_idx
                phase_name_n_epochs = curriculum_n_epochs if (hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None) else n_epochs
                progress = phase_name_epoch / phase_name_n_epochs
                
                curriculum_config = None
                if hasattr(self.encoder.config, 'loss_config') and hasattr(self.encoder.config.loss_config, 'curriculum_learning'):
                    curriculum_config = self.encoder.config.loss_config.curriculum_learning
                
                if curriculum_config is None:
                    curriculum_config = self._get_default_curriculum_config()
                
                current_phase_name = "CONSTANT"
                phase_emoji = "⚖️"
                if curriculum_config.enabled and curriculum_config.phases:
                    for phase in curriculum_config.phases:
                        if progress >= phase.start_progress and progress <= phase.end_progress:
                            current_phase_name = phase.name
                            # Assign emoji based on phase focus
                            if phase.spread_weight >= 0.9 and phase.joint_weight < 0.5:
                                phase_emoji = "🌊"  # Spread focus
                            elif phase.marginal_weight >= 0.4:
                                phase_emoji = "🎯"  # Marginal focus
                            
                            # Track when we enter the final "Spread + Joint Focus" phase (last 10%)
                            # This is when marginal_weight is low (< 0.2) and we're focusing on spread/joint
                            # OR when we're in forced finalization mode
                            if hasattr(self, '_spread_only_tracker'):
                                in_spread_phase = (phase.marginal_weight < 0.2 and phase.spread_weight >= 0.9)
                                in_forced_finalization = hasattr(self, '_forced_spread_finalization') and self._forced_spread_finalization
                                
                                # Check if we just entered the spread phase this epoch
                                if (in_spread_phase or in_forced_finalization) and not self._spread_only_tracker.get('in_spread_phase', False):
                                    self._spread_only_tracker['in_spread_phase'] = True
                                
                                # Increment counter if we're in the phase (natural or forced)
                                if in_spread_phase or in_forced_finalization:
                                    self._spread_only_tracker['spread_only_epochs_completed'] = \
                                        self._spread_only_tracker.get('spread_only_epochs_completed', 0) + 1
                            elif phase.joint_weight >= 0.9 and phase.spread_weight < 0.5:
                                phase_emoji = "🔗"  # Joint focus
                            elif phase.spread_weight >= 0.9 and phase.joint_weight >= 0.9:
                                phase_emoji = "🌊🔗"  # Spread + Joint focus
                            break
                
                # Log weight changes (only when there's a meaningful change or at phase boundaries)
                weight_changed = (
                    abs(spread_weight - old_spread_weight) > 0.01 or
                    abs(marginal_weight - old_marginal_weight) > 0.01 or
                    abs(joint_weight - old_joint_weight) > 0.01
                )
                
                should_log = (
                    epoch_idx == 0 or  # First epoch
                    weight_changed or  # Significant change
                    (epoch_idx % max(1, n_epochs // 10) == 0)  # Every 10%
                )
                
                if should_log:
                    # Show cumulative epoch for K-fold CV
                    display_epoch = epoch_idx + 1
                    if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                        display_epoch = epoch_idx + 1 + self._kv_fold_epoch_offset
                        epoch_display = f"epoch={display_epoch}"
                    else:
                        epoch_display = f"epoch={display_epoch}/{n_epochs}"
                    
                    scaling_info = ""
                    if hasattr(self, '_marginal_loss_scaling_coefficient') and self._marginal_loss_scaling_coefficient is not None:
                        scaling_info = f" (marginal scaled by {self._marginal_loss_scaling_coefficient:.4f}×)"
                    
                    logger.info(
                        f"{phase_emoji} [{epoch_display}] {current_phase_name}: "
                        f"spread={spread_weight:.4f}, marginal={marginal_weight:.4f}, joint={joint_weight:.4f}{scaling_info}"
                    )
                # ============================================================================

                # Check for ABORT file at the start of each epoch
                job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                output_dir = getattr(self, 'output_dir', None)
                check_abort_and_raise(job_id, output_dir=output_dir, context="epoch start")

                # Check for PAUSE file at the start of each epoch
                if job_id and check_pause_files(job_id):
                    logger.warning(f"⏸️  PAUSE file detected for job {job_id} - pausing training and saving checkpoint")
                    d["interrupted"] = "PAUSE file detected"
                    
                    # Save checkpoint before pausing
                    if save_state_after_every_epoch:
                        try:
                            self.save_training_resume_point(epoch_idx, 0, optimizer, scheduler, dropout_scheduler)
                            logger.info(f"💾 Checkpoint saved before pause at epoch {epoch_idx}")
                        except Exception as e:
                            logger.warning(f"⚠️  Failed to save checkpoint before pause: {e}")
                    
                    # Mark job as PAUSED
                    try:
                        from lib.job_manager import update_job_status
                        update_job_status(job_id, JobStatus.PAUSED, {
                            "pause_reason": "PAUSE file detected by user",
                            "paused_at": datetime.now(tz=ZoneInfo("America/New_York"))
                        })
                        logger.info(f"⏸️  Job {job_id} marked as PAUSED")
                    except Exception as e:
                        logger.error(f"Failed to update job status to PAUSED: {e}")
                    
                    logger.info(f"⏸️  Breaking out of training loop - job is paused. Remove PAUSE file and set status to READY to resume.")
                    break  # Break out of epoch loop
                
                # Check for FINISH file at the start of each epoch
                if job_id and check_finish_files(job_id):
                    logger.warning(f"🏁 FINISH file detected for job {job_id} - completing training gracefully")
                    d["interrupted"] = "FINISH file detected"
                    logger.info(f"🏁 Breaking out of training loop to save model and complete job")
                    break

                if self._gotControlC:
                    logger.warning("Got CTRL+C signal - stopping training. You can continue training later.")
                    d["interrupted"] = "Got SIGINT"
                    break

                if print_callback is not None:
                    if epoch_idx == 0:
                        d["epoch_idx"] = 1 + epoch_idx
                        d["progress_counter"] = progress_counter
                        d["max_progress"] = max_progress
                        print_callback(d)

                # for batch_idx, (batch, targets) in enumerate(dataloader):
                # Initialize loss_dict to None in case batch loop doesn't execute
                loss_dict = None
                
                # MEMORY LEAK DETECTION: Track first and last batch of each epoch
                first_batch_logged = False
                last_batch_idx = batches_per_epoch - 1
                
                # Wrap batch loop in try-except to catch OOM errors from DataLoader workers
                try:
                    for batch_idx, batch in enumerate(timed_data_loader):
                        # CRITICAL: Clear gradients at the very start of each batch iteration
                        # This prevents "backward through graph twice" errors if previous batch had issues
                        # or if a 'continue' statement was executed before zero_grad() was called
                        optimizer.zero_grad()
                        
                        assert self.encoder.training == True, "(top of batch loop) -- but the net net is that you are not in training mode."
                    
                        # VRAM logging removed - leaks are fixed, batch-level logging is too noisy
                        # Only log at epoch boundaries if needed for debugging
                        first_batch_logged = True
                        
                        # Log batch progress with rate limiting (max 1 log per minute)
                        current_time = time.time()
                        time_since_last_log = current_time - self._last_batch_log_time.get(epoch_idx, current_time)
                        should_log_batch = False
                        
                        if epoch_idx == 0:
                            # First epoch: log first batch, then every 10 batches OR every minute
                            if batch_idx == 0 or batch_idx % 10 == 0 or time_since_last_log >= 60:
                                should_log_batch = True
                        else:
                            # Other epochs: log at normal progress intervals OR every minute
                            if batch_idx % print_progress_step == 0 or time_since_last_log >= 60:
                                should_log_batch = True
                        
                        if should_log_batch:
                            # Get current loss (will be computed later, but we'll log it after)
                            # We'll log loss separately after it's computed
                            logger.info(f"   📦 Epoch {epoch_idx + 1}/{n_epochs}, Batch {batch_idx + 1}/{batches_per_epoch} ({(batch_idx + 1)/batches_per_epoch*100:.1f}%)")
                            self._last_batch_log_time[epoch_idx] = current_time
                            self._should_log_loss_this_batch = True
                        else:
                            self._should_log_loss_this_batch = False
                        
                        # Flag to skip remainder of batch processing after exiting with blocks
                        skip_batch = False

                        # Check for PAUSE file periodically during batch processing
                        if batch_idx % 10 == 0:
                            save_fn = (lambda: self.save_training_resume_point(epoch_idx, batch_idx, optimizer, scheduler, dropout_scheduler)) if save_state_after_every_epoch else None
                            if check_pause_and_handle(job_id, epoch_idx, batch_idx, save_fn, context=f"batch {batch_idx}"):
                                d["interrupted"] = "PAUSE file detected"
                                self._gotControlC = True
                                break
                        
                        # Check for ABORT file periodically during batch processing (every 10 batches)
                        if batch_idx % 10 == 0:
                            job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
                            output_dir = getattr(self, 'output_dir', None)
                            check_abort_and_raise(job_id, output_dir=output_dir, context=f"batch {batch_idx}")

                            # Check for FINISH file periodically during batch processing
                            if check_finish_and_signal(job_id, context=f"batch {batch_idx}"):
                                d["interrupted"] = "FINISH file detected"
                                self._gotControlC = True
                                break

                        if self._gotControlC:
                            logger.warning("Got CTRL+C signal - stopping training early.")
                            break

                        progress_counter += 1

                        # logger.info("loop_stopwatch encoder entered")
                        for tokenbatch in batch.values():
                            tokenbatch.to(get_device())

                        assert self.encoder.training == True, "(before encoder) -- but the net net is that you are not in training mode."
                        
                        # GPU RAM logging BEFORE forward pass - critical for OOM debugging
                        # Log for first batch of each epoch, first 3 epochs, or if we've had OOM errors
                        should_log_gpu_before_forward = (
                            batch_idx == 0 or 
                            epoch_idx < 3 or 
                            oom_stats["oom_count_total"] > 0
                        )
                        
                        if should_log_gpu_before_forward:
                            log_gpu_memory(f"BEFORE FORWARD [e={epoch_idx+1}, b={batch_idx}] (batch_size={batch_size})")
                        
                        # BF16 mixed precision: wrap forward pass in autocast
                        # This automatically casts operations to BF16 where safe, keeping FP32 where needed
                        # Also wrap in OOM handling since forward pass can OOM on large batches
                        try:
                            # Store current learning rate on encoder for logging
                            self.encoder._current_lr = scheduler.get_current_lr()
                            with torch.amp.autocast(device_type=device_type, dtype=autocast_dtype, enabled=use_autocast):
                                encodings = self.encoder(batch)
                        except (torch.OutOfMemoryError, RuntimeError) as forward_oom_err:
                            error_str = str(forward_oom_err).lower()
                            # Detect OOM errors: explicit OutOfMemoryError or RuntimeError with OOM indicators
                            is_oom_error = (
                                isinstance(forward_oom_err, torch.OutOfMemoryError) or
                                "out of memory" in error_str or
                                "cuda out of memory" in error_str or
                                "oom" in error_str or
                                ("cuda" in error_str and ("memory" in error_str or "allocation" in error_str))
                            )
                            
                            if is_oom_error:
                                # OOM during forward pass
                                oom_stats["oom_count_this_epoch"] += 1
                                oom_stats["oom_count_total"] += 1
                                oom_stats["batches_skipped_this_epoch"] += 1
                                
                                # Log OOM error immediately with high visibility
                                logger.error("=" * 100)
                                logger.error(f"💥 CUDA OUT OF MEMORY ERROR - FORWARD PASS")
                                logger.error(f"   Epoch: {epoch_idx + 1}, Batch: {batch_idx + 1}")
                                logger.error(f"   Batch Size: {batch_size}")
                                logger.error(f"   Error Type: {type(forward_oom_err).__name__}")
                                logger.error(f"   Error Message: {str(forward_oom_err)[:500]}")
                                logger.error("=" * 100)
                                
                                self._handle_cuda_oom_error(
                                    error=forward_oom_err,
                                    epoch_idx=epoch_idx,
                                    batch_idx=batch_idx,
                                    batch_size=batch_size,
                                    pass_type="forward"
                                )
                                
                                # EARLY EPOCH RETRY: If OOM on epoch <= 2 and this is the first OOM, retry immediately
                                # This catches batch size issues early before wasting time on many skipped batches
                                is_early_epoch = epoch_idx <= 1  # Epochs 1 and 2 (0-based: 0, 1)
                                is_first_oom = oom_stats["oom_count_total"] == 1
                                hasnt_retried_yet = _oom_retry_count == 0
                                
                                if is_early_epoch and is_first_oom and hasnt_retried_yet:
                                    # Calculate half batch size
                                    suggested_batch_size = max(8, batch_size // 2)
                                    suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                    
                                    # Check if we can actually reduce (avoid infinite loop at minimum)
                                    if suggested_batch_size >= batch_size:
                                        logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                        raise forward_oom_err
                                    
                                    if _oom_retry_count < max_oom_retries:
                                        next_retry = _oom_retry_count + 1
                                        logger.warning("=" * 80)
                                        logger.warning(f"🔄 EARLY EPOCH OOM RETRY: Epoch {epoch_idx + 1} <= 2, first OOM detected")
                                        logger.warning(f"   Retrying immediately with half batch size: {batch_size} → {suggested_batch_size}")
                                        logger.warning(f"   Retry attempt #{next_retry}/{max_oom_retries}")
                                        logger.warning("=" * 80)
                                        raise FeatrixOOMRetryException(
                                            message=f"CUDA OOM in forward pass on early epoch {epoch_idx + 1} (first OOM, batch_size={batch_size}, retry #{next_retry})",
                                            current_batch_size=batch_size,
                                            suggested_batch_size=suggested_batch_size,
                                            epoch_idx=epoch_idx,
                                            oom_count=oom_stats["oom_count_this_epoch"]
                                        )
                                    else:
                                        logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                        raise forward_oom_err
                                
                                # Check if we've hit too many OOMs
                                # SMART DETECTION: Trigger retry if EITHER:
                                # 1. Too many OOMs in this epoch (for multi-batch epochs)
                                # 2. Too many consecutive epochs with OOMs (for single-batch epochs)
                                # The consecutive check uses oom_count_this_epoch + consecutive_oom_epochs to
                                # catch the case where we're in a new epoch but just OOM'd
                                effective_consecutive = oom_stats["consecutive_oom_epochs"] + (1 if oom_stats["oom_count_this_epoch"] > 0 else 0)
                                
                                should_reduce_batch = (
                                    oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"] or
                                    effective_consecutive >= oom_stats["max_consecutive_oom_epochs"]
                                )
                                
                                if should_reduce_batch:
                                    # Minimum batch size is 8 (was 32, which caused infinite loops at batch_size=32)
                                    suggested_batch_size = max(8, batch_size // 2)
                                    suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                    
                                    if oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"]:
                                        logger.error(f"💥 {oom_stats['oom_count_this_epoch']} OOM errors this epoch (forward pass) - batch size too large")
                                    else:
                                        logger.error(f"💥 OOM in {effective_consecutive} consecutive epochs (forward pass) - batch size too large")
                                    
                                    # Check if we can actually reduce (avoid infinite loop at minimum)
                                    if suggested_batch_size >= batch_size:
                                        logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                        raise forward_oom_err
                                    
                                    if _oom_retry_count < max_oom_retries:
                                        next_retry = _oom_retry_count + 1
                                        logger.warning(f"🔄 Will retry #{next_retry}/{max_oom_retries} with batch_size={suggested_batch_size}")
                                        raise FeatrixOOMRetryException(
                                            message=f"CUDA OOM in forward pass after {oom_stats['oom_count_this_epoch']} errors (batch_size={batch_size}, retry #{next_retry})",
                                            current_batch_size=batch_size,
                                            suggested_batch_size=suggested_batch_size,
                                            epoch_idx=epoch_idx,
                                            oom_count=oom_stats["oom_count_this_epoch"]
                                        )
                                    else:
                                        logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                        raise forward_oom_err
                                
                                # Skip this batch and continue
                                logger.warning(f"⚠️  Skipping batch {batch_idx} due to forward pass OOM (this epoch: {oom_stats['oom_count_this_epoch']}/{oom_stats['max_oom_per_epoch']}, consecutive epochs: {effective_consecutive}/{oom_stats['max_consecutive_oom_epochs']})")
                                optimizer.zero_grad()
                                continue  # Skip to next batch
                            else:
                                # Not an OOM error - re-raise
                                raise
                        
                        # CRITICAL NaN DEBUGGING: Check encoder outputs for NaN (first 3 batches of first epoch)
                        debug_check_encodings_for_nan(encodings, epoch_idx, batch_idx)
                        
                        # VRAM logging after forward pass
                        if should_log_gpu_before_forward:
                            log_gpu_memory(f"AFTER FORWARD [e={epoch_idx+1}, b={batch_idx}] (batch_size={batch_size})")
                        
                        # Track mask distribution (encodings[9] = mask_1, encodings[10] = mask_2, encodings[17] = rows_skipped)
                        # Also need token_status_mask which is in the encoder forward pass
                        # We'll extract it from the batch since it's regenerated in encoder
                        if self.mask_tracker is not None:
                            # Track mask distribution - masks only contain columns that are in the batch
                            # The encoder processes columns in self.col_order order, but only those in the batch
                            # Return tuple indices: 0=batch_size, 1-3=full_joint, 4-5=column_encodings, 6-8=short_joint, 9=mask_1, 10=mask_2, 17=rows_skipped
                            mask_1, mask_2 = encodings[9], encodings[10]
                            rows_skipped = encodings[17] if len(encodings) > 17 else 0
                            
                            # Reconstruct original_mask to match mask dimensions (only columns in batch)
                            # Get columns in batch in the order they appear in self.col_order (matches encoder order)
                            batch_cols_in_order = [col_name for col_name in self.col_order if col_name in batch]
                            
                            # CRITICAL: Both masks should have the same dimensions
                            # If they don't match, something is wrong with the encoder output
                            # NOTE: Don't use 'continue' here - it would skip optimizer.zero_grad() and cause
                            # "backward through graph twice" errors on the next batch!
                            if mask_1.shape[1] != mask_2.shape[1]:
                                logger.warning(
                                    f"⚠️  Mask dimension mismatch: mask_1.shape[1]={mask_1.shape[1]}, "
                                    f"mask_2.shape[1]={mask_2.shape[1]}. Skipping mask tracking for this batch."
                                )
                                # Don't 'continue' - just skip the mask tracking for this batch
                            else:
                                # Both masks have the same number of columns - use that
                                num_mask_cols = mask_1.shape[1]
                                token_status_list = []
                                
                                for i, col_name in enumerate(batch_cols_in_order):
                                    if i >= num_mask_cols:
                                        break  # Only collect statuses for columns the encoder processed
                                    if col_name in batch:
                                        token_status_list.append(batch[col_name].status)
                                
                                # Verify we collected the right number of statuses
                                if len(token_status_list) == num_mask_cols:
                                    original_mask = torch.stack(token_status_list, dim=1)
                                    # Final verification that all dimensions match
                                    if original_mask.shape[1] == mask_1.shape[1] == mask_2.shape[1]:
                                        self.mask_tracker.record_batch(
                                            epoch_idx, batch_idx, mask_1, mask_2, original_mask, rows_skipped
                                        )
                                    else:
                                        logger.debug(
                                            f"Final dimension check failed: original_mask={original_mask.shape[1]}, "
                                            f"mask_1={mask_1.shape[1]}, mask_2={mask_2.shape[1]}"
                                        )
                                else:
                                    # Log when we can't construct matching mask
                                    logger.debug(
                                        f"Cannot construct matching mask: token_status_list={len(token_status_list)}, "
                                        f"expected={num_mask_cols}, batch_cols_in_order={len(batch_cols_in_order)}"
                                    )

                        # logger.info("loop_stopwatch compute_total_loss entered")
                        # BF16 mixed precision: loss computation also in autocast
                        with torch.amp.autocast(device_type=device_type, dtype=autocast_dtype, enabled=use_autocast):
                            loss, loss_dict = self.encoder.compute_total_loss(*encodings, temp_multiplier=temp_boost_multiplier)
                        
                        # CRITICAL NaN DEBUGGING: Check loss and components for NaN (first 3 batches of first epoch)
                        if epoch_idx == 0 and batch_idx < 3:
                            logger.info(f"🔍 NaN DEBUG [e={epoch_idx},b={batch_idx}] AFTER LOSS COMPUTATION:")
                            logger.info(f"   Total loss: {loss.item():.6f} (NaN={torch.isnan(loss).item()}, Inf={torch.isinf(loss).item()})")
                            
                            # Check each loss component
                            for component_name in ['spread_loss', 'joint_loss', 'marginal_loss']:
                                component = loss_dict.get(component_name, {})
                                if isinstance(component, dict) and 'total' in component:
                                    total_val = component['total']
                                    if isinstance(total_val, torch.Tensor):
                                        logger.info(f"   {component_name}: {total_val.item():.6f} (NaN={torch.isnan(total_val).item()})")
                                    else:
                                        logger.info(f"   {component_name}: {total_val:.6f}")
                            
                            # Check per-column marginal losses for NaN
                            marginal_loss_dict = loss_dict.get('marginal_loss', {})
                            for view_name in ['marginal_loss_full_1', 'marginal_loss_full_2']:
                                view_dict = marginal_loss_dict.get(view_name, {})
                                col_losses = view_dict.get('cols', {})
                                nan_cols = [col for col, val in col_losses.items() if math.isnan(val) or math.isinf(val)]
                                if nan_cols:
                                    logger.error(f"   💥 {view_name} has NaN/Inf in columns: {nan_cols}")
                        
                        # DEBUG: Track loss values on first epoch and periodically to verify they're improving
                        diagnostic_epochs_for_loss = [0, 1, 5, 10, 25, 50]
                        if epoch_idx in diagnostic_epochs_for_loss and batch_idx < 5:
                            if not hasattr(self, '_batch_losses'):
                                self._batch_losses = []
                            self._batch_losses.append(loss.item())
                            
                            # Extract all loss components for detailed logging
                            spread_total = loss_dict.get('spread_loss', {}).get('total', 0)
                            joint_total = loss_dict.get('joint_loss', {}).get('total', 0)
                            marginal_total = loss_dict.get('marginal_loss', {}).get('total', 0)
                            
                            # Get sub-components of marginal loss
                            marginal_dict = loss_dict.get('marginal_loss', {})
                            marginal_raw = marginal_dict.get('raw', 0)  # Before normalization
                            marginal_normalizer = marginal_dict.get('normalizer', 1)
                            
                            logger.info(f"🔍 [e={epoch_idx},b={batch_idx}] DETAILED LOSS BREAKDOWN:")
                            logger.info(f"   Total loss: {loss.item():.4f}")
                            logger.info(f"   Spread loss: {spread_total:.4f}")
                            logger.info(f"   Joint loss: {joint_total:.4f}")
                            logger.info(f"   Marginal loss: {marginal_total:.4f} (raw={marginal_raw:.4f}, normalizer={marginal_normalizer:.2f})")
                            
                            # Check if marginal loss is abnormally low/high
                            if marginal_total < 1e-6:
                                logger.error(f"   ⚠️  Marginal loss is near zero! No learning signal for marginal reconstruction!")
                            if marginal_normalizer > 1000:
                                logger.warning(f"   ⚠️  Marginal normalizer is very large ({marginal_normalizer:.2f}) - may be destroying gradients!")
                            
                            # Check loss component ratios
                            if spread_total > 0 and marginal_total > 0:
                                ratio = spread_total / marginal_total
                                logger.info(f"   Loss ratio (spread/marginal): {ratio:.4f}")
                                if ratio > 100 or ratio < 0.01:
                                    logger.warning(f"   ⚠️  Loss components are imbalanced by {max(ratio, 1/ratio):.1f}×!")
                        
                        # CRITICAL: Ensure loss is a fresh tensor (not reused from previous batch)
                        # This prevents "backward through graph a second time" errors
                        # The issue occurs when the same computation graph is accessed twice, which can happen if:
                        # 1. The encoder caches intermediate tensors between batches
                        # 2. Relationship features create shared computation graphs
                        # 3. The DataLoader reuses batches or caches computation
                        # Check if loss tensor appears to be reused by verifying it's a fresh computation
                        if not loss.requires_grad:
                            logger.warning(f"⚠️  Loss tensor doesn't require grad! This shouldn't happen. Creating new tensor.")
                            loss = loss.detach().requires_grad_(True)
                        
                        # Additional check: if loss has a grad_fn but any of its inputs already have gradients,
                        # it means the computation graph was reused from a previous batch
                        if loss.grad_fn is not None:
                            # Check if any encoding tensors already have gradients (they shouldn't before backward)
                            # Only check .grad on leaf tensors to avoid PyTorch warnings
                            for idx, enc in enumerate(encodings):
                                if isinstance(enc, torch.Tensor) and enc.is_leaf and enc.grad is not None:
                                    logger.error(f"💥 FATAL: Encoding tensor at index {idx} already has gradients before backward!")
                                    logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                                    logger.error(f"   Tensor shape: {enc.shape}, requires_grad: {enc.requires_grad}")
                                    logger.error(f"   This means the computation graph was reused from a previous batch")
                                    logger.error(f"   Possible cause: Encoder is caching tensors or DataLoader is reusing batches")
                                    logger.error(f"   ⚠️  SKIPPING THIS BATCH")
                                    skip_batch = True
                                    break
                            if skip_batch:
                                break
                        
                        # CRITICAL: Ensure encodings tuple doesn't contain cached tensors from previous batch
                        # If relationship features or encoder is caching, this could cause graph reuse
                        # Force a fresh forward pass by ensuring encodings are from current batch
                        # (This is a safeguard - the real fix would be in the encoder if it's caching)
                        
                        # ============================================================================
                        # REPRESENTATION COLLAPSE DETECTION (First 3 batches + diagnostic epochs)
                        # ============================================================================
                        diagnostic_epochs_for_collapse = [0, 1, 5, 10, 25, 50, 100]
                        if epoch_idx in diagnostic_epochs_for_collapse and batch_idx < 3:
                            try:
                                # Check if joint embeddings have collapsed (all rows identical)
                                # encodings tuple: (batch_size, full_joint_unmasked, full_joint_1, full_joint_2, ...)
                                full_joint_unmasked = encodings[1]  # (batch_size, d_model)
                                
                                # Check embedding diversity
                                emb_std = full_joint_unmasked.std().item()
                                emb_mean = full_joint_unmasked.mean().item()
                                emb_min = full_joint_unmasked.min().item()
                                emb_max = full_joint_unmasked.max().item()
                                
                                # Check pairwise distances between rows
                                pairwise_dists = torch.cdist(full_joint_unmasked, full_joint_unmasked)
                                avg_dist = pairwise_dists.mean().item()
                                max_dist = pairwise_dists.max().item()
                                
                                logger.info("=" * 80)
                                logger.info(f"🔍 REPRESENTATION COLLAPSE CHECK (Epoch {epoch_idx}, Batch {batch_idx})")
                                logger.info("=" * 80)
                                logger.info(f"   Joint Embeddings Shape: {full_joint_unmasked.shape}")
                                logger.info(f"   Value Range: [{emb_min:.6f}, {emb_max:.6f}] (range={emb_max-emb_min:.6f})")
                                logger.info(f"   Mean: {emb_mean:.6f}, Std: {emb_std:.6f}")
                                logger.info(f"   Pairwise Distances: avg={avg_dist:.6f}, max={max_dist:.6f}")
                                
                                # Detection thresholds
                                COLLAPSE_STD_THRESHOLD = 0.01  # If std < 0.01, embeddings are too similar
                                COLLAPSE_DIST_THRESHOLD = 0.1  # If avg distance < 0.1, rows are too similar
                                
                                # During training, collapse is often transient and the model recovers
                                # These are diagnostic checkpoints, not final validation
                                # Only ERROR if training completes with a broken/non-recovering model
                                if emb_std < COLLAPSE_STD_THRESHOLD:
                                    logger.warning(f"   ⚠️ REPRESENTATION COLLAPSE DETECTED: Embedding std ({emb_std:.6f}) < {COLLAPSE_STD_THRESHOLD}")
                                    logger.warning("      All embeddings are nearly identical!")
                                    logger.warning("      This is often transient - model should recover as training progresses...")
                                elif avg_dist < COLLAPSE_DIST_THRESHOLD:
                                    logger.warning(f"   ⚠️ REPRESENTATION COLLAPSE DETECTED: Avg pairwise distance ({avg_dist:.6f}) < {COLLAPSE_DIST_THRESHOLD}")
                                    logger.warning("      All rows have nearly identical embeddings!")
                                    logger.warning("      This is often transient - model should recover as training progresses...")
                                else:
                                    logger.info(f"   ✅ Embeddings are diverse (std={emb_std:.6f}, avg_dist={avg_dist:.6f})")
                                
                                logger.info("=" * 80)
                                
                                # ============================================================================
                                # SEMANTIC COLLAPSE DETECTION - Check if encodings represent actual values
                                # ============================================================================
                                logger.info("=" * 80)
                                logger.info(f"🔍 SEMANTIC COLLAPSE CHECK (Epoch {epoch_idx}, Batch {batch_idx})")
                                logger.info("=" * 80)
                                
                                # Extract full_column_encodings from encodings tuple
                                # encodings: (batch_size, full_joint_unmasked, ..., full_column_encodings, ...)
                                full_column_encodings = encodings[4]  # (batch_size, n_cols, d_model)
                                
                                # Check scalar columns: do different values get different embeddings?
                                scalar_semantic_ok = True
                                for col_name, codec in self.col_codecs.items():
                                    if hasattr(codec, 'codec_type') and codec.codec_type == 'scalar':
                                        # Get the column data from batch
                                        if col_name in batch and hasattr(batch[col_name], 'data'):
                                            col_data = batch[col_name].data  # Raw values
                                            
                                            # Get column index to extract encodings
                                            if col_name in self.col_order:
                                                col_idx = self.col_order.index(col_name)
                                                col_encodings = full_column_encodings[:, col_idx, :]  # (batch_size, d_model)
                                                
                                                # Check if embedding variance matches value variance
                                                value_std = col_data.std().item() if len(col_data) > 1 else 0
                                                emb_std = col_encodings.std().item()
                                                
                                                # Compute correlation between value differences and embedding distances
                                                if len(col_data) >= 5:  # Need at least 5 samples
                                                    value_diffs = torch.cdist(col_data.unsqueeze(1), col_data.unsqueeze(1)).flatten()
                                                    emb_dists = torch.cdist(col_encodings, col_encodings).flatten()
                                                    
                                                    # Correlation: if values differ, embeddings should differ proportionally
                                                    correlation = torch.corrcoef(torch.stack([value_diffs, emb_dists]))[0, 1].item()
                                                    
                                                    logger.info(f"   Scalar '{col_name}': value_std={value_std:.4f}, emb_std={emb_std:.6f}, value/emb_correlation={correlation:.4f}")
                                                    
                                                    # Semantic collapse: embeddings don't correlate with values
                                                    if abs(correlation) < 0.1:
                                                        logger.error(f"      💥 SEMANTIC COLLAPSE: '{col_name}' embeddings don't correlate with values (r={correlation:.4f})")
                                                        logger.error("         Embeddings vary but don't represent actual value differences!")
                                                        scalar_semantic_ok = False
                                
                                # Check set columns: does each unique value get a different embedding?
                                set_semantic_ok = True
                                for col_name, codec in self.col_codecs.items():
                                    if hasattr(codec, 'codec_type') and codec.codec_type == 'set':
                                        # Get the column data from batch
                                        if col_name in batch and hasattr(batch[col_name], 'data'):
                                            col_data = batch[col_name].data  # Token indices
                                            
                                            # Get column index to extract encodings
                                            if col_name in self.col_order:
                                                col_idx = self.col_order.index(col_name)
                                                col_encodings = full_column_encodings[:, col_idx, :]  # (batch_size, d_model)
                                                
                                                # Group embeddings by unique values
                                                unique_values = col_data.unique()
                                                if len(unique_values) >= 2:
                                                    # Compute average embedding per unique value
                                                    value_to_emb = {}
                                                    for val in unique_values:
                                                        mask = (col_data == val)
                                                        if mask.sum() > 0:
                                                            avg_emb = col_encodings[mask].mean(dim=0)
                                                            value_to_emb[val.item()] = avg_emb
                                                    
                                                    # Check if different values have different embeddings
                                                    if len(value_to_emb) >= 2:
                                                        emb_list = list(value_to_emb.values())
                                                        emb_stack = torch.stack(emb_list)
                                                        inter_value_dists = torch.cdist(emb_stack, emb_stack)
                                                        avg_inter_dist = inter_value_dists.sum() / (len(emb_list) * (len(emb_list) - 1))
                                                        
                                                        logger.info(f"   Set '{col_name}': {len(unique_values)} unique values, avg_distance_between_values={avg_inter_dist:.6f}")
                                                        
                                                        # Semantic collapse: different values have identical embeddings
                                                        if avg_inter_dist < 0.01:
                                                            logger.error(f"      💥 SEMANTIC COLLAPSE: '{col_name}' different values have identical embeddings (dist={avg_inter_dist:.6f})")
                                                            logger.error("         Set encoder is not distinguishing between different values!")
                                                            set_semantic_ok = False
                                
                                if scalar_semantic_ok and set_semantic_ok:
                                    logger.info("   ✅ Semantic integrity OK - encodings represent actual values")
                                logger.info("=" * 80)
                                
                            except Exception as e:
                                logger.error(f"⚠️  Collapse detection failed: {e}")
                                logger.error(traceback.format_exc())
                        
                        # Log marginal loss breakdown every N batches for visibility
                        if batch_idx % 50 == 0:
                            self._log_marginal_loss_breakdown(loss_dict, epoch_idx, batch_idx)
                            logger.info(f"[DEBUG] After _log_marginal_loss_breakdown - epoch={epoch_idx}, batch={batch_idx}")
                        
                        # Progressive pruning: track column losses and prune worst columns at 10% and 20% progress
                        if not hasattr(self, '_column_loss_tracker'):
                            self._column_loss_tracker = {}  # Track average loss per column
                            self._column_loss_count = {}    # Track number of samples per column
                        self._update_column_loss_tracker(loss_dict)
                        
                        # Check training progress and prune if needed
                        training_progress = (epoch_idx + 1) / n_epochs if n_epochs > 0 else 0.0
                        if training_progress >= 0.10 and not hasattr(self, '_pruned_at_10pct'):
                            self._prune_worst_scalar_columns(loss_dict, epoch_idx, prune_percent=0.10)
                            self._pruned_at_10pct = True
                        elif training_progress >= 0.20 and not hasattr(self, '_pruned_at_20pct'):
                            # At 20%, prune next worst 10% (total will be 20% pruned)
                            self._prune_worst_scalar_columns(loss_dict, epoch_idx, prune_percent=0.10, cumulative=True)
                            self._pruned_at_20pct = True

                        # logger.info("loop_stopwatch zero entered")
                        assert self.encoder.training == True, "(before zero_grad) -- but the net net is that you are not in training mode."
                        # NOTE: optimizer.zero_grad() is now called at the START of each batch iteration (line ~10634)
                        # This ensures gradients are always cleared even if previous batch had errors or continue statements
                        
                        # ============================================================================
                        # PROPORTIONALITY LOSS FOR NUMERIC COLUMNS
                        # ============================================================================
                        # Add proportionality loss every 5 batches (for efficiency)
                        # This encourages embedding distance to be proportional to input distance
                        proportionality_weight = 0.1  # Weight relative to other losses
                        if batch_idx % 5 == 0 and epoch_idx >= 5:  # Start after warmup
                            try:
                                prop_loss, prop_loss_dict = self.encoder.compute_proportionality_loss(
                                    batch, n_samples=8, perturbation_scale=0.1
                                )
                                if prop_loss.requires_grad and prop_loss.item() > 0:
                                    loss = loss + proportionality_weight * prop_loss
                                    loss_dict['proportionality_loss'] = prop_loss_dict
                                    
                                    # Log occasionally
                                    if batch_idx == 0 and epoch_idx % 10 == 0:
                                        logger.info(f"📐 Proportionality loss: {prop_loss.item():.4f} (scaled: {proportionality_weight * prop_loss.item():.4f})")
                                        if prop_loss_dict.get('cols'):
                                            for col, col_info in list(prop_loss_dict['cols'].items())[:3]:
                                                logger.info(f"   {col}: ratio_mean={col_info['ratio_mean']:.4f}, ratio_var={col_info['ratio_var']:.4f}")
                            except Exception as prop_e:
                                # Don't crash training if proportionality loss fails
                                if batch_idx == 0 and epoch_idx == 5:
                                    logger.warning(f"Proportionality loss computation failed: {prop_e}")
                        
                        # CRITICAL FIX: Check loss value BEFORE backward pass
                        # Extract loss value as float to avoid any tensor operations that might trigger autograd
                        loss_value = float(loss.item())
                        if torch.isnan(loss) or torch.isinf(loss):
                            logger.error(f"💥 FATAL: NaN/Inf loss detected BEFORE backward! loss={loss_value}")
                            logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                            # CRITICAL: Don't log loss_dict directly - nested dicts may contain tensors
                            # Only log top-level scalar values to avoid triggering autograd
                            try:
                                logger.error(f"   Total loss: {loss_dict.get('total', 'N/A')}")
                                logger.error(f"   Spread loss: {loss_dict.get('spread_loss', {}).get('total', 'N/A')}")
                                logger.error(f"   Joint loss: {loss_dict.get('joint_loss', {}).get('total', 'N/A')}")
                                logger.error(f"   Marginal loss: {loss_dict.get('marginal_loss', {}).get('total', 'N/A')}")
                            except Exception:
                                logger.error(f"   (Could not extract loss dict values)")
                            # Skip this batch entirely - don't corrupt gradients
                            logger.error("   ⚠️  SKIPPING THIS BATCH to prevent gradient corruption")
                            skip_batch = True
                            break  # Exit the with block cleanly
                        
                        # CRITICAL: Ensure we're not trying to backward through a graph that's already been freed
                        # This can happen if the loss tensor is somehow reused or if there's shared computation
                        # Check if loss tensor is part of a computation graph that might have been used
                        # If loss.grad_fn is None but requires_grad is True, it's a leaf tensor (should be safe)
                        # If loss.grad_fn exists, check if it's been used by checking if any input has .grad
                        if loss.grad_fn is not None:
                            # Check if any input to the loss computation has gradients (indicating it was already used)
                            # This is a heuristic - if we find gradients on inputs, the graph was likely already used
                            try:
                                # Check if encodings contain tensors with gradients (they shouldn't before backward)
                                # Only check .grad on leaf tensors to avoid PyTorch warnings
                                for enc in encodings:
                                    if isinstance(enc, torch.Tensor) and enc.is_leaf and enc.grad is not None:
                                        logger.error(f"💥 FATAL: Encoding tensor already has gradients before backward!")
                                        logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                                        logger.error(f"   This means the computation graph was reused from a previous batch")
                                        logger.error(f"   ⚠️  SKIPPING THIS BATCH")
                                        skip_batch = True
                                        break
                            except Exception as check_err:
                                # If check fails, log but continue - might be false positive
                                logger.debug(f"Could not check encoding gradients: {check_err}")
                        
                        if skip_batch:
                            break
                        
                        try:
                            # DEBUG: MPS INT_MAX - Print info before backward pass
                            if epoch_idx == 0 and batch_idx < 3:
                                logger.info(f"[DEBUG] About to call loss.backward() - epoch={epoch_idx}, batch={batch_idx}")
                                logger.info(f"[DEBUG]   loss shape: {loss.shape if hasattr(loss, 'shape') else 'scalar'}, value: {loss.item():.6f}")
                                if isinstance(encodings, tuple):
                                    for enc_idx, enc in enumerate(encodings):
                                        if isinstance(enc, torch.Tensor):
                                            logger.info(f"[DEBUG]   encoding[{enc_idx}] shape: {enc.shape}, numel: {enc.numel()}")
                            
                            # CRITICAL: Explicitly set retain_graph=False to ensure graph is freed after backward
                            # This prevents "backward through graph twice" errors when reusing encoder across batches
                            loss.backward(retain_graph=False)
                            
                            # ============================================================================
                            # CAPTURE GRADIENT NORMS (before optimizer.step()/zero_grad() clears them)
                            # ============================================================================
                            # Capture gradient norms right after backward() so they're available for epoch summary
                            if hasattr(self.encoder, 'joint_encoder') and hasattr(self.encoder.joint_encoder, 'relationship_extractor'):
                                rel_extractor = self.encoder.joint_encoder.relationship_extractor
                                if rel_extractor is not None and hasattr(rel_extractor, 'capture_gradient_norms'):
                                    rel_extractor.capture_gradient_norms()
                            
                            # ============================================================================
                            # UPDATE RELATIONSHIP CONTRIBUTIONS FROM GRADIENTS
                            # ============================================================================
                            # DISABLED: Gradient-based contribution tracking replaced by loss-based importance
                            # retain_grad() on 1,140 tokens was causing numerical instability and NaN gradients
                            # Loss-based importance (using column marginal losses) is more stable and effective
                            # if hasattr(self.encoder, 'joint_encoder') and hasattr(self.encoder.joint_encoder, 'relationship_extractor'):
                            #     rel_extractor = self.encoder.joint_encoder.relationship_extractor
                            #     if rel_extractor is not None and hasattr(rel_extractor, 'update_contributions_from_gradients'):
                            #         rel_extractor.update_contributions_from_gradients()
                            
                            # ============================================================================
                            # GRADIENT SCALING FIX FOR PREDICTOR VANISHING GRADIENTS
                            # ============================================================================
                            # PROBLEM: Predictors get 80-100× smaller gradients than encoders due to
                            #          longer gradient path through InfoNCE loss
                            # EVIDENCE: encoder grad=11.72, predictor grad=0.14 (83× smaller!)
                            # SOLUTION: Scale predictor gradients by 10× to compensate
                            # ============================================================================
                            
                            predictor_grad_scale = 1.0  # (was 10.0) legacy workaround for earlier vanishing-grad measurement
                           
                            # CRITICAL: Capture predictor gradient norms BEFORE scaling
                            predictor_norm_pre_scale_squared = 0.0
                            predictor_params_with_grad = 0
                            for name, param in self.encoder.named_parameters():
                                if param.grad is not None:
                                    if 'column_predictor' in name or 'joint_predictor' in name:
                                        param_norm = param.grad.norm().item()
                                        predictor_norm_pre_scale_squared += param_norm ** 2
                                        predictor_params_with_grad += 1
                            predictor_norm_pre_scale = predictor_norm_pre_scale_squared ** 0.5 if predictor_params_with_grad > 0 else 0.0
                            
                            # Compute encoder global norm (all encoder params, excluding predictors)
                            encoder_norm_squared = 0.0
                            encoder_params_with_grad = 0
                            encoder_params_frozen = []
                            for name, param in self.encoder.named_parameters():
                                # Skip predictors - they're separate
                                if 'column_predictor' in name or 'joint_predictor' in name:
                                    continue
                                # Track frozen params for verification
                                if not param.requires_grad:
                                    encoder_params_frozen.append(name)
                                if param.grad is not None:
                                    encoder_params_with_grad += 1
                                    param_norm = param.grad.norm().item()
                                    encoder_norm_squared += param_norm ** 2
                            encoder_norm = encoder_norm_squared ** 0.5 if encoder_params_with_grad > 0 else 0.0
                            
                            # Compute logR = log(enc_global+eps) - log(pred_global+eps)
                            # This gives apples-to-apples comparison with single_predictor
                            eps = 1e-10
                            if encoder_norm > eps and predictor_norm_pre_scale > eps:
                                gradient_flow_log_ratio = math.log(encoder_norm + eps) - math.log(predictor_norm_pre_scale + eps)
                            elif encoder_norm > eps:
                                gradient_flow_log_ratio = float('inf')
                            else:
                                gradient_flow_log_ratio = float('-inf')
                            
                            # Scale predictor gradients
                            predictor_params_scaled = 0
                            for name, param in self.encoder.named_parameters():
                                if param.grad is not None:
                                    if 'column_predictor' in name or 'joint_predictor' in name:
                                        param.grad *= predictor_grad_scale
                                        predictor_params_scaled += 1
                            
                            # Capture predictor gradient norms AFTER scaling
                            predictor_norm_post_scale_squared = 0.0
                            for name, param in self.encoder.named_parameters():
                                if param.grad is not None:
                                    if 'column_predictor' in name or 'joint_predictor' in name:
                                        param_norm = param.grad.norm().item()
                                        predictor_norm_post_scale_squared += param_norm ** 2
                            predictor_norm_post_scale = predictor_norm_post_scale_squared ** 0.5 if predictor_params_scaled > 0 else 0.0
                            
                            # GRADIENT FLOW DIAGNOSTICS (First 3 batches + epochs 0, 1, 5, 10, 25, 50)
                            # Pass pre-scale norm so it can log both, plus encoder global norm and logR
                            debug_log_gradient_flow(self.encoder, epoch_idx, batch_idx, 
                                                   predictor_norm_pre_scale=predictor_norm_pre_scale,
                                                   predictor_norm_post_scale=predictor_norm_post_scale,
                                                   encoder_norm=encoder_norm,
                                                   gradient_flow_log_ratio=gradient_flow_log_ratio,
                                                   encoder_params_frozen=encoder_params_frozen)
                            
                            # Log scaling on first batch
                            if epoch_idx == 0 and batch_idx == 0:
                                logger.info(f"🔧 GRADIENT SCALING: Amplifying predictor gradients by {predictor_grad_scale}×")
                                # Make reason conditional on actual gradient flow (logR)
                                # Only print the "vanishing gradient" reason if encoder is actually dominating
                                if gradient_flow_log_ratio is not None and not (math.isinf(gradient_flow_log_ratio) or math.isnan(gradient_flow_log_ratio)):
                                    if gradient_flow_log_ratio > 2.3:
                                        # Encoder is >10× stronger than predictor
                                        actual_ratio = math.exp(gradient_flow_log_ratio)
                                        logger.info(f"   Reason: Encoder gradients are ~{actual_ratio:.1f}× stronger than predictor (logR={gradient_flow_log_ratio:+.2f})")
                                        logger.info(f"   Action: Scaling predictor gradients to balance learning")
                                    elif gradient_flow_log_ratio < -2.3:
                                        # Predictor is >10× stronger than encoder
                                        actual_ratio = math.exp(-gradient_flow_log_ratio)
                                        logger.info(f"   Reason: Predictor gradients are ~{actual_ratio:.1f}× stronger than encoder (logR={gradient_flow_log_ratio:+.2f})")
                                        logger.info(f"   Action: Scaling predictor gradients (encoder starved, may need separate LR)")
                                    else:
                                        # Balanced (within 10×)
                                        actual_ratio = math.exp(abs(gradient_flow_log_ratio))
                                        logger.info(f"   Reason: Gradients are balanced (ratio={actual_ratio:.2f}×, logR={gradient_flow_log_ratio:+.2f})")
                                        logger.info(f"   Action: No scaling needed; balanced learning")
                                else:
                                    # Fallback if logR not available yet
                                    logger.info(f"   Reason: Default scaling applied (gradient flow not yet measured)")
                                logger.info(f"   Scaled {predictor_params_scaled} predictor parameters")
                            
                            # DEBUG: Check gradient flow immediately after backward on first batches
                            if epoch_idx == 0 and batch_idx < 3:
                                # Check if predictors received gradients
                                predictor_has_grads = False
                                encoder_has_grads = False
                                
                                for name, param in self.encoder.named_parameters():
                                    if param.grad is not None:
                                        if 'column_predictor' in name or 'joint_predictor' in name:
                                            predictor_has_grads = True
                                        if 'joint_encoder' in name or 'column_encoder' in name:
                                            encoder_has_grads = True
                                
                                if not predictor_has_grads:
                                    logger.error(f"💥 [e=0,b={batch_idx}] AFTER BACKWARD: PREDICTORS HAVE NO GRADIENTS!")
                                    logger.error(f"   This means column_predictor and joint_predictor are NOT in computation graph!")
                                    logger.error(f"   Joint loss and marginal loss CANNOT update predictor weights!")
                                else:
                                    logger.info(f"✅ [e=0,b={batch_idx}] AFTER BACKWARD+SCALING: Predictors have gradients (scaled {predictor_grad_scale}×)")
                                
                                if encoder_has_grads:
                                    logger.info(f"✅ [e=0,b={batch_idx}] AFTER BACKWARD: Encoders have gradients (unscaled)")
                                else:
                                    logger.error(f"💥 [e=0,b={batch_idx}] AFTER BACKWARD: ENCODERS HAVE NO GRADIENTS!")
                            
                        except RuntimeError as e:
                            error_str = str(e)
                            if "backward through the graph a second time" in error_str or "backward through the graph twice" in error_str:
                                logger.error(f"💥 FATAL: Attempted to backward through graph twice!")
                                logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                                logger.error(f"   Loss tensor: requires_grad={loss.requires_grad}, is_leaf={loss.is_leaf}")
                                # Safely format loss_value - handle case where it might not be set or is None
                                try:
                                    # Try to use loss_value if it exists and is valid
                                    if 'loss_value' in locals() and loss_value is not None:
                                        loss_value_str = f"{loss_value:.6f}"
                                    else:
                                        # Extract loss value directly from tensor
                                        loss_value_str = f"{float(loss.detach().item()):.6f}"
                                except Exception as format_err:
                                    # Last resort: just show the error type
                                    loss_value_str = f"N/A (could not extract: {type(format_err).__name__})"
                                logger.error(f"   Loss value: {loss_value_str}")
                                logger.error(f"   This usually means the loss tensor was reused from a previous batch")
                                logger.error(f"   Possible causes:")
                                logger.error(f"   1. Encoder caching intermediate tensors between batches")
                                logger.error(f"   2. Relationship features creating shared computation graphs")
                                logger.error(f"   3. DataLoader reusing batches or caching computation")
                                logger.error(f"   ⚠️  RE-RAISING ERROR TO CRASH (don't hide the bug)")
                                raise  # Don't skip - crash so we can see the real problem
                            elif "DataLoader worker" in error_str and "killed by signal" in error_str:
                                # OOM error - worker was killed by OOM killer
                                logger.error(f"💥 FATAL: DataLoader worker killed by OOM!")
                                logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                                # Print helpful recovery instructions
                                from lib.system_health_monitor import print_oom_recovery_help
                                print_oom_recovery_help(
                                    error=e,
                                    num_workers=train_dl_kwargs.get('num_workers', 0) if 'train_dl_kwargs' in locals() else None,
                                    batch_size=batch_size
                                )
                                raise  # Re-raise to stop training
                            elif "out of memory" in error_str.lower() or "cuda" in error_str.lower():
                                # CUDA OOM during backward pass (RuntimeError variant)
                                # Try to recover by skipping this batch
                                oom_stats["oom_count_this_epoch"] += 1
                                oom_stats["oom_count_total"] += 1
                                oom_stats["batches_skipped_this_epoch"] += 1
                                
                                self._handle_cuda_oom_error(
                                    error=e,
                                    epoch_idx=epoch_idx,
                                    batch_idx=batch_idx,
                                    batch_size=batch_size
                                )
                                
                                # EARLY EPOCH RETRY: If OOM on epoch <= 2 and this is the first OOM, retry immediately
                                # This catches batch size issues early before wasting time on many skipped batches
                                is_early_epoch = epoch_idx <= 1  # Epochs 1 and 2 (0-based: 0, 1)
                                is_first_oom = oom_stats["oom_count_total"] == 1
                                hasnt_retried_yet = _oom_retry_count == 0
                                
                                if is_early_epoch and is_first_oom and hasnt_retried_yet:
                                    # Calculate half batch size
                                    suggested_batch_size = max(8, batch_size // 2)
                                    suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                    
                                    # Check if we can actually reduce (avoid infinite loop at minimum)
                                    if suggested_batch_size >= batch_size:
                                        logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                        raise  # Re-raise original error
                                    
                                    if _oom_retry_count < max_oom_retries:
                                        next_retry = _oom_retry_count + 1
                                        logger.warning("=" * 80)
                                        logger.warning(f"🔄 EARLY EPOCH OOM RETRY: Epoch {epoch_idx + 1} <= 2, first OOM detected (backward pass)")
                                        logger.warning(f"   Retrying immediately with half batch size: {batch_size} → {suggested_batch_size}")
                                        logger.warning(f"   Retry attempt #{next_retry}/{max_oom_retries}")
                                        logger.warning("=" * 80)
                                        raise FeatrixOOMRetryException(
                                            message=f"CUDA OOM in backward pass on early epoch {epoch_idx + 1} (first OOM, batch_size={batch_size}, retry #{next_retry})",
                                            current_batch_size=batch_size,
                                            suggested_batch_size=suggested_batch_size,
                                            epoch_idx=epoch_idx,
                                            oom_count=oom_stats["oom_count_this_epoch"]
                                        )
                                    else:
                                        logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                        raise  # Re-raise original error
                                
                                # Check if we've hit too many OOMs
                                # SMART DETECTION: Trigger retry if EITHER:
                                # 1. Too many OOMs in this epoch (for multi-batch epochs)
                                # 2. Too many consecutive epochs with OOMs (for single-batch epochs)
                                effective_consecutive = oom_stats["consecutive_oom_epochs"] + (1 if oom_stats["oom_count_this_epoch"] > 0 else 0)
                                
                                should_reduce_batch = (
                                    oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"] or
                                    effective_consecutive >= oom_stats["max_consecutive_oom_epochs"]
                                )
                                
                                if should_reduce_batch:
                                    # Minimum batch size is 8 (was 32, which caused infinite loops)
                                    suggested_batch_size = max(8, batch_size // 2)
                                    # Round to power of 2
                                    suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                    
                                    if oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"]:
                                        logger.error(f"💥 {oom_stats['oom_count_this_epoch']} OOM errors this epoch (backward pass) - batch size too large")
                                    else:
                                        logger.error(f"💥 OOM in {effective_consecutive} consecutive epochs (backward pass) - batch size too large")
                                    
                                    # Check if we can actually reduce (avoid infinite loop at minimum)
                                    if suggested_batch_size >= batch_size:
                                        logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                        raise  # Re-raise original error
                                    
                                    # Check if we can retry with smaller batch size
                                    if _oom_retry_count < max_oom_retries:
                                        next_retry = _oom_retry_count + 1
                                        logger.warning(f"🔄 Will retry #{next_retry}/{max_oom_retries} with batch_size={suggested_batch_size}")
                                        raise FeatrixOOMRetryException(
                                            message=f"CUDA OOM after {oom_stats['oom_count_this_epoch']} errors (batch_size={batch_size}, retry #{next_retry})",
                                            current_batch_size=batch_size,
                                            suggested_batch_size=suggested_batch_size,
                                            epoch_idx=epoch_idx,
                                            oom_count=oom_stats["oom_count_this_epoch"]
                                        )
                                    else:
                                        logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                        logger.error(f"   Minimum batch_size={batch_size} still too large for this GPU")
                                        raise  # Re-raise original error
                                
                                # Skip this batch and continue
                                logger.warning(f"⚠️  Skipping batch {batch_idx} due to OOM (this epoch: {oom_stats['oom_count_this_epoch']}/{oom_stats['max_oom_per_epoch']}, consecutive epochs: {effective_consecutive}/{oom_stats['max_consecutive_oom_epochs']})")
                                optimizer.zero_grad()  # Clear any partial gradients
                                continue  # Skip to next batch
                            else:
                                # Unknown RuntimeError - re-raise
                                raise
                        except torch.OutOfMemoryError as e:
                            # CUDA OOM during backward pass (torch.OutOfMemoryError in PyTorch 2.x+)
                            # Try to recover by skipping this batch
                            oom_stats["oom_count_this_epoch"] += 1
                            oom_stats["oom_count_total"] += 1
                            oom_stats["batches_skipped_this_epoch"] += 1
                            
                            self._handle_cuda_oom_error(
                                error=e,
                                epoch_idx=epoch_idx,
                                batch_idx=batch_idx,
                                batch_size=batch_size
                            )
                            
                            # EARLY EPOCH RETRY: If OOM on epoch <= 2 and this is the first OOM, retry immediately
                            # This catches batch size issues early before wasting time on many skipped batches
                            is_early_epoch = epoch_idx <= 1  # Epochs 1 and 2 (0-based: 0, 1)
                            is_first_oom = oom_stats["oom_count_total"] == 1
                            hasnt_retried_yet = _oom_retry_count == 0
                            
                            if is_early_epoch and is_first_oom and hasnt_retried_yet:
                                # Calculate half batch size
                                suggested_batch_size = max(8, batch_size // 2)
                                suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                
                                # Check if we can actually reduce (avoid infinite loop at minimum)
                                if suggested_batch_size >= batch_size:
                                    logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                    raise  # Re-raise original error
                                
                                if _oom_retry_count < max_oom_retries:
                                    next_retry = _oom_retry_count + 1
                                    logger.warning("=" * 80)
                                    logger.warning(f"🔄 EARLY EPOCH OOM RETRY: Epoch {epoch_idx + 1} <= 2, first OOM detected (backward pass)")
                                    logger.warning(f"   Retrying immediately with half batch size: {batch_size} → {suggested_batch_size}")
                                    logger.warning(f"   Retry attempt #{next_retry}/{max_oom_retries}")
                                    logger.warning("=" * 80)
                                    raise FeatrixOOMRetryException(
                                        message=f"CUDA OOM in backward pass on early epoch {epoch_idx + 1} (first OOM, batch_size={batch_size}, retry #{next_retry})",
                                        current_batch_size=batch_size,
                                        suggested_batch_size=suggested_batch_size,
                                        epoch_idx=epoch_idx,
                                        oom_count=oom_stats["oom_count_this_epoch"]
                                    )
                                else:
                                    logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                    raise  # Re-raise original error
                            
                            # Check if we've hit too many OOMs
                            # SMART DETECTION: Trigger retry if EITHER:
                            # 1. Too many OOMs in this epoch (for multi-batch epochs)
                            # 2. Too many consecutive epochs with OOMs (for single-batch epochs)
                            effective_consecutive = oom_stats["consecutive_oom_epochs"] + (1 if oom_stats["oom_count_this_epoch"] > 0 else 0)
                            
                            should_reduce_batch = (
                                oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"] or
                                effective_consecutive >= oom_stats["max_consecutive_oom_epochs"]
                            )
                            
                            if should_reduce_batch:
                                # Minimum batch size is 8 (was 32, which caused infinite loops)
                                suggested_batch_size = max(8, batch_size // 2)
                                # Round to power of 2
                                suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                                
                                if oom_stats["oom_count_this_epoch"] >= oom_stats["max_oom_per_epoch"]:
                                    logger.error(f"💥 {oom_stats['oom_count_this_epoch']} OOM errors this epoch (backward pass) - batch size too large")
                                else:
                                    logger.error(f"💥 OOM in {effective_consecutive} consecutive epochs (backward pass) - batch size too large")
                                
                                # Check if we can actually reduce (avoid infinite loop at minimum)
                                if suggested_batch_size >= batch_size:
                                    logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                                    raise  # Re-raise original error
                                
                                # Check if we can retry with smaller batch size
                                if _oom_retry_count < max_oom_retries:
                                    next_retry = _oom_retry_count + 1
                                    logger.warning(f"🔄 Will retry #{next_retry}/{max_oom_retries} with batch_size={suggested_batch_size}")
                                    raise FeatrixOOMRetryException(
                                        message=f"CUDA OOM after {oom_stats['oom_count_this_epoch']} errors (batch_size={batch_size}, retry #{next_retry})",
                                        current_batch_size=batch_size,
                                        suggested_batch_size=suggested_batch_size,
                                        epoch_idx=epoch_idx,
                                        oom_count=oom_stats["oom_count_this_epoch"]
                                    )
                                else:
                                    logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                                    logger.error(f"   Minimum batch_size={batch_size} still too large for this GPU")
                                    raise  # Re-raise original error
                            
                            # Skip this batch and continue
                            logger.warning(f"⚠️  Skipping batch {batch_idx} due to OOM (this epoch: {oom_stats['oom_count_this_epoch']}/{oom_stats['max_oom_per_epoch']}, consecutive epochs: {effective_consecutive}/{oom_stats['max_consecutive_oom_epochs']})")
                            optimizer.zero_grad()  # Clear any partial gradients
                            continue  # Skip to next batch
                    
                        # VRAM logging removed - batch-level logging is too noisy
                        
                        # Compute unclipped gradient norm for diagnostics
                        unclipped_norm = torch.nn.utils.clip_grad_norm_(self.encoder.parameters(), float('inf'))
                        
                        # CRITICAL SAFETY CHECK: Ensure loss is a tensor, not the initial "not set" string
                        # This can happen if compute_total_loss() failed silently or was never called
                        if not isinstance(loss, torch.Tensor):
                            logger.error(f"💥 CRITICAL BUG: loss is {type(loss).__name__} ('{loss}'), not a tensor!")
                            logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                            logger.error(f"   This means compute_total_loss() was never called or failed silently")
                            logger.error(f"   Skipping gradient clipping and optimizer step for this batch")
                            continue  # Skip to next batch
                        
                        # Determine clipping threshold for this batch
                        if use_adaptive_clipping:
                            # Adaptive clipping: threshold = loss × ratio
                            loss_value = loss.item()
                            adaptive_threshold = loss_value * adaptive_grad_clip_ratio
                            total_norm = torch.nn.utils.clip_grad_norm_(self.encoder.parameters(), adaptive_threshold)
                            was_clipped = unclipped_norm > adaptive_threshold
                            effective_threshold = adaptive_threshold
                            
                            # Track gradient/loss ratio
                            grad_loss_ratio = unclipped_norm / (loss_value + 1e-8)
                            grad_clip_stats["max_grad_loss_ratio"] = max(grad_clip_stats["max_grad_loss_ratio"], grad_loss_ratio)
                        else:
                            # No clipping
                            total_norm = unclipped_norm
                            was_clipped = False
                            effective_threshold = None
                        
                        # Track gradient statistics
                        update_gradient_stats(grad_clip_stats, unclipped_norm, total_norm, was_clipped, loss)
                        
                        # CRITICAL FIX: Detect NaN/Inf gradients BEFORE they corrupt parameters
                        # CRITICAL FIX: Detect NaN/Inf gradients BEFORE they corrupt parameters
                        if handle_nan_inf_gradients(self.encoder, optimizer, loss, epoch_idx, batch_idx, total_norm):
                            skip_batch = True
                            break  # Exit the with block cleanly
                        
                        # Store latest gradient info for failure detection and timeline (every batch)
                        # CRITICAL: Convert tensors to floats for JSON serialization in timeline
                        lr_value = scheduler.get_current_lr()
                        clipped_ratio = (unclipped_norm / effective_threshold) if (effective_threshold is not None and unclipped_norm > effective_threshold) else 1.0
                        
                        # Convert tensors to Python floats to avoid "Object of type Tensor is not JSON serializable" errors
                        self._latest_gradient_norm = float(unclipped_norm.item()) if hasattr(unclipped_norm, 'item') else float(unclipped_norm)
                        self._latest_gradient_clipped = float(total_norm.item()) if hasattr(total_norm, 'item') else float(total_norm)
                        self._latest_gradient_ratio = float(clipped_ratio.item()) if hasattr(clipped_ratio, 'item') else float(clipped_ratio)
                        
                        # Store gradient norm on encoder for loss logging
                        self.encoder._latest_gradient_norm = self._latest_gradient_norm
                        
                        # Gradient monitoring
                        if unclipped_norm < 0.001 and batch_idx % 500 == 0:
                            logger.warning(f"⚠️  TINY GRADIENTS: {unclipped_norm:.6e}, lr={lr_value:.6e} (model may not be learning)")
                            
                            # Track TINY_GRADIENTS warning in timeline (only log once per epoch)
                            if not hasattr(self, '_tiny_grad_warned_this_epoch') or not self._tiny_grad_warned_this_epoch:
                                unclipped_val = float(unclipped_norm.item()) if hasattr(unclipped_norm, 'item') else float(unclipped_norm)
                                self._track_warning_in_timeline(
                                    epoch_idx=epoch_idx,
                                    warning_type="TINY_GRADIENTS",
                                    is_active=True,
                                    details={
                                        "gradient_norm": unclipped_val,
                                        "lr": lr_value,
                                        "batch_idx": batch_idx,
                                        "threshold": 0.001
                                    }
                                )
                                self._tiny_grad_warned_this_epoch = True
                        elif batch_idx % 500 == 0:
                            loss_value = loss.item()
                            grad_loss_ratio = unclipped_norm / (loss_value + 1e-8)
                            
                            # For adaptive clipping, warn based on ratio threshold
                            if use_adaptive_clipping and grad_clip_warning_multiplier is not None:
                                warning_ratio = adaptive_grad_clip_ratio * grad_clip_warning_multiplier
                                if grad_loss_ratio > warning_ratio:
                                    grad_clip_stats["large_gradient_warnings"] += 1
                                    logger.warning(f"⚠️  High gradient/loss ratio: {grad_loss_ratio:.2f} (threshold: {warning_ratio:.2f})")
                                    logger.warning(f"   gradient={unclipped_norm:.2f}, loss={loss_value:.2f}, clipped={was_clipped}")


                        # logger.info("loop_stopwatch step entered")
                        
                        # CRITICAL FIX: Validate parameters BEFORE optimizer step
                        nan_params_before = []
                        for name, param in self.encoder.named_parameters():
                            if torch.isnan(param).any():
                                nan_params_before.append(name)
                        
                        if nan_params_before:
                            logger.error(f"💥 FATAL: NaN parameters detected BEFORE optimizer step!")
                            logger.error(f"   Corrupted parameters: {nan_params_before[:5]}...")
                            logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                            logger.error("   ⚠️  SKIPPING optimizer step to prevent further corruption")
                            # Don't step the optimizer if parameters are already corrupted
                            skip_batch = True
                            break  # Exit the with block cleanly
                        
                        # Store parameters before optimizer step to compute parameter update norm
                        params_before = {}
                        for name, param in self.encoder.named_parameters():
                            if param.requires_grad:
                                params_before[name] = param.data.clone()
                        
                        # DEBUG: On first epoch, verify DataLoader is providing different batches
                        if epoch_idx == 0 and batch_idx < 3:
                            # Check if batch data is changing between iterations
                            if not hasattr(self, '_batch_hashes'):
                                self._batch_hashes = []
                            
                            # Compute a simple hash of the first column's first few values
                            first_col_name = list(batch.keys())[0] if batch else None
                            if first_col_name and hasattr(batch[first_col_name], 'data'):
                                first_values = batch[first_col_name].data[:5] if len(batch[first_col_name].data) > 0 else []
                                batch_hash = hash(tuple(first_values.cpu().numpy().flatten().tolist() if hasattr(first_values, 'cpu') else first_values))
                                self._batch_hashes.append(batch_hash)
                                
                                if len(self._batch_hashes) > 1 and batch_hash == self._batch_hashes[-2]:
                                    logger.error(f"⚠️  CRITICAL: Batch {batch_idx} is IDENTICAL to previous batch! DataLoader may be broken!")
                                else:
                                    logger.info(f"🔍 [e=0,b={batch_idx}] Batch hash: {batch_hash} (unique: {'✓' if batch_hash not in self._batch_hashes[:-1] else '✗'})")
                        
                        # DEBUG: On first epoch, log gradient norms to verify gradients are flowing
                        if epoch_idx == 0 and batch_idx < 3:
                            grad_norms = []
                            predictor_grads = []
                            encoder_grads = []
                            
                            for name, param in self.encoder.named_parameters():
                                if param.grad is not None:
                                    norm = param.grad.norm().item()
                                    grad_norms.append((name, norm))
                                    
                                    # Categorize by component
                                    if 'column_predictor' in name or 'joint_predictor' in name:
                                        predictor_grads.append((name, norm))
                                    elif 'joint_encoder' in name or 'column_encoder' in name:
                                        encoder_grads.append((name, norm))
                            
                            # Log top 5 gradient norms overall
                            grad_norms.sort(key=lambda x: x[1], reverse=True)
                            logger.info(f"🔍 [e=0,b={batch_idx}] Top 5 gradient norms (all):")
                            for name, norm in grad_norms[:5]:
                                logger.info(f"   {name}: {norm:.6f}")
                            
                            # Log predictor gradients separately
                            if predictor_grads:
                                predictor_grads.sort(key=lambda x: x[1], reverse=True)
                                logger.info(f"🔍 [e=0,b={batch_idx}] Top 3 PREDICTOR gradients:")
                                for name, norm in predictor_grads[:3]:
                                    logger.info(f"   {name}: {norm:.6f}")
                            else:
                                logger.error(f"❌ [e=0,b={batch_idx}] NO PREDICTOR GRADIENTS! (column_predictor and joint_predictor have no gradients!)")
                            
                            # Log encoder gradients separately  
                            if encoder_grads:
                                encoder_grads.sort(key=lambda x: x[1], reverse=True)
                                logger.info(f"🔍 [e=0,b={batch_idx}] Top 3 ENCODER gradients:")
                                for name, norm in encoder_grads[:3]:
                                    logger.info(f"   {name}: {norm:.6f}")
                            
                            # Count total parameters with/without gradients
                            total_params = len(list(self.encoder.named_parameters()))
                            params_with_grad = len([p for _, p in self.encoder.named_parameters() if p.grad is not None])
                            params_without_grad = total_params - params_with_grad
                            logger.info(f"🔍 [e=0,b={batch_idx}] Gradient coverage: {params_with_grad}/{total_params} params have gradients ({params_without_grad} frozen)")
                        
                        # DEBUG: On first epoch, track weight change magnitude
                        if epoch_idx == 0 and batch_idx == 0:
                            # Store initial weights for comparison after first batch
                            self._initial_weights = {}
                            for name, param in self.encoder.named_parameters():
                                self._initial_weights[name] = param.data.clone()
                        
                        # CRITICAL: Catch optimizer state mismatch errors and recreate optimizer
                        try:
                            optimizer.step()
                        except RuntimeError as opt_err:
                            if "size of tensor" in str(opt_err) and "must match" in str(opt_err):
                                # Optimizer state mismatch - recreate with fresh state
                                logger.error(f"⚠️  Optimizer state mismatch detected: {opt_err}")
                                logger.error("   Recreating optimizer with fresh state")
                                old_lr = optimizer.param_groups[0]['lr']
                                optimizer = torch.optim.AdamW(
                                    self.encoder.parameters(),
                                    lr=old_lr,
                                    weight_decay=optimizer.param_groups[0].get('weight_decay', 1e-4)
                                )
                            else:
                                raise
                        
                        # Compute parameter update norm (||w_after - w_before||)
                        param_update_norm = 0.0
                        if params_before:
                            param_update_norm_squared = 0.0
                            for name, param in self.encoder.named_parameters():
                                if param.requires_grad and name in params_before:
                                    param_diff = param.data - params_before[name]
                                    param_update_norm_squared += param_diff.norm(2).item() ** 2
                            param_update_norm = param_update_norm_squared ** 0.5
                        
                        # Store for epoch-level logging with validation loss
                        if not hasattr(self, '_epoch_grad_norms'):
                            self._epoch_grad_norms = []
                            self._epoch_param_update_norms = []
                        self._epoch_grad_norms.append(float(unclipped_norm.item()) if hasattr(unclipped_norm, 'item') else float(unclipped_norm))
                        self._epoch_param_update_norms.append(param_update_norm)
                        
                        # ============================================================================
                        # WEIGHT UPDATE DIAGNOSTICS (First batch after optimizer.step())
                        # ============================================================================
                        if epoch_idx == 0 and batch_idx == 0 and hasattr(self, '_initial_weights'):
                            logger.info("=" * 80)
                            logger.info("🔍 WEIGHT UPDATE DIAGNOSTIC (Epoch 0, Batch 0 - After optimizer.step())")
                            logger.info("=" * 80)
                            
                            # Check if weights actually changed
                            col_enc_changes = []
                            joint_enc_changes = []
                            pred_changes = []
                            
                            for name, param in self.encoder.named_parameters():
                                if name in self._initial_weights:
                                    old_weight = self._initial_weights[name]
                                    new_weight = param.data
                                    weight_change = (new_weight - old_weight).abs().max().item()
                                    
                                    if 'column_encoder' in name:
                                        col_enc_changes.append(weight_change)
                                    elif 'joint_encoder' in name:
                                        joint_enc_changes.append(weight_change)
                                    elif 'predictor' in name:
                                        pred_changes.append(weight_change)
                            
                            # Calculate statistics
                            col_enc_max_change = np.max(col_enc_changes) if col_enc_changes else 0.0
                            col_enc_mean_change = np.mean(col_enc_changes) if col_enc_changes else 0.0
                            joint_enc_max_change = np.max(joint_enc_changes) if joint_enc_changes else 0.0
                            joint_enc_mean_change = np.mean(joint_enc_changes) if joint_enc_changes else 0.0
                            pred_max_change = np.max(pred_changes) if pred_changes else 0.0
                            pred_mean_change = np.mean(pred_changes) if pred_changes else 0.0
                            
                            logger.info(f"   Column Encoders: max_change={col_enc_max_change:.2e}, mean_change={col_enc_mean_change:.2e}")
                            logger.info(f"   Joint Encoder:   max_change={joint_enc_max_change:.2e}, mean_change={joint_enc_mean_change:.2e}")
                            logger.info(f"   Predictors:      max_change={pred_max_change:.2e}, mean_change={pred_mean_change:.2e}")
                            
                            # Check for problems
                            if col_enc_max_change < 1e-10:
                                logger.error("   💥 CRITICAL: Column encoder weights DID NOT CHANGE!")
                                logger.error("   Gradients exist but optimizer is not updating weights!")
                                logger.error("   Possible causes: learning rate too small, weights frozen, or optimizer bug")
                            elif col_enc_max_change < 1e-6:
                                logger.warning(f"   ⚠️  WARNING: Column encoder weight changes are tiny ({col_enc_max_change:.2e})")
                                logger.warning("   Learning may be extremely slow")
                            else:
                                logger.info(f"   ✅ Column encoders updated successfully")
                            
                            if joint_enc_max_change < 1e-10:
                                logger.error("   💥 CRITICAL: Joint encoder weights DID NOT CHANGE!")
                                logger.error("   Gradients exist but optimizer is not updating weights!")
                            elif joint_enc_max_change < 1e-6:
                                logger.warning(f"   ⚠️  WARNING: Joint encoder weight changes are tiny ({joint_enc_max_change:.2e})")
                            else:
                                logger.info(f"   ✅ Joint encoder updated successfully")
                            
                            logger.info("=" * 80)
                            
                            # Clean up to save memory
                            del self._initial_weights
                        
                        elif epoch_idx == 0 and batch_idx == 0:
                            logger.warning("⚠️  Could not check weight updates - _initial_weights not set")
                            
                            # Clean up to save memory
                            del self._initial_weights
                            
                        # CRITICAL FIX: Validate parameters AFTER optimizer step
                        nan_params_after = []
                        for name, param in self.encoder.named_parameters():
                            if torch.isnan(param).any():
                                nan_params_after.append(name)
                        
                        if nan_params_after:
                            logger.error(f"💥 FATAL: NaN parameters detected AFTER optimizer step!")
                            logger.error(f"   Corrupted parameters: {nan_params_after[:5]}...")
                            logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                            logger.error(f"   Loss value: {loss.item()}")
                            logger.error(f"   Learning rate: {scheduler.get_current_lr()}")
                            
                            # Show the actual corrupted parameter values for the first one
                            if nan_params_after:
                                first_param_name = nan_params_after[0]
                                for name, param in self.encoder.named_parameters():
                                    if name == first_param_name:
                                        logger.error(f"   Sample corrupted values from {name}: {param.flatten()[:10]}")
                                        break
                            
                            # CRITICAL: Training is now corrupted - we must stop
                            logger.error("   🚨 TRAINING CORRUPTED - STOPPING TO PREVENT FURTHER DAMAGE")
                            raise RuntimeError(f"FATAL PARAMETER CORRUPTION AFTER STEP: {len(nan_params_after)} corrupted parameters")
                            
                        # CRITICAL: If batch had NaN/errors, ABORT training
                        # Don't continue with corrupted embeddings - fail fast
                        if skip_batch:
                            logger.error(f"🚨 ABORTING: NaN/Inf detected in batch {batch_idx + 1} - training is corrupted")
                            logger.error(f"   Embeddings from this training run are INVALID and should not be used")
                            raise RuntimeError(
                                f"Training aborted due to NaN/Inf gradients at epoch {epoch_idx}, batch {batch_idx + 1}. "
                                f"This indicates numerical instability - check for extreme values, learning rate too high, "
                                f"or bugs in loss computation."
                            )
                        
                        # LRTimeline sets LR per-epoch (not per-batch), so skip step() for it
                        # LambdaLR needs to step after each batch
                        if not isinstance(scheduler, LRTimeline):
                            try:
                                scheduler.step()
                            except ValueError as err:
                                logger.error("Overstepped.", exc_info=1)
                                break  # break out of the loop.
                        
                        # Apply LR boost multiplier if active
                        if lr_boost_multiplier != 1.0:
                            for param_group in optimizer.param_groups:
                                param_group['lr'] = param_group['lr'] * lr_boost_multiplier

                        # After executing the optimization step, detach loss from the computational
                        # graph, so we don't accidentally accumulate references to it across the
                        # whole training run, and thus blow up memory.
                        loss = loss.detach()

                        d["current_learning_rate"] = scheduler.get_current_lr()
                        d["current_loss"] = loss.item()
                        
                        # Accumulate training loss for epoch average
                        batch_loss_value = loss.item()
                        train_loss_sum += batch_loss_value
                        train_batch_count += 1
                        train_batch_losses.append(batch_loss_value)
                        # Get batch size from first column token batch
                        first_column_token_batch = next(iter(batch.items()))[1]
                        batch_size_actual = len(first_column_token_batch)
                        train_batch_sizes.append(batch_size_actual)

                        # Log loss when we logged batch progress (same rate limiting)
                        if getattr(self, '_should_log_loss_this_batch', False):
                            logger.info(f"      Loss: {loss.item():.4f} (batch {batch_idx + 1}/{batches_per_epoch})")

                        self.run_callbacks(CallbackType.AFTER_BATCH, epoch_idx, batch_idx)

                        # NOTE: the procedure for computing and saving the training progress
                        # is getting too complicated, and difficult to replicate at the end
                        # of the training, so the info saved at the end is more limited.
                        # We should factor this out into a separate method.
                        if print_progress_step is not None:
                            last_log_delta = time.time() - last_log_time
                            # print("last_log_delta = ", last_log_delta)
                            if (
                                last_log_delta > 10
                                or (progress_counter % print_progress_step) == 0
                            ):
                                last_log_time = time.time()

                                self.train_save_progress_stuff(
                                    epoch_idx=epoch_idx,
                                    batch_idx=batch_idx,
                                    epoch_start_time_now=epoch_start_time_now,
                                    encodings=encodings,
                                    save_prediction_vector_lengths=save_prediction_vector_lengths,
                                    training_event_dict=training_event_dict,
                                    d=d,
                                    current_lr=scheduler.get_current_lr(),
                                    loss_tensor=loss,
                                    loss_dict=loss_dict,
                                    val_loss=val_loss,
                                    val_components=val_components,
                                    dataloader_batch_durations=[],
                                    print_callback=print_callback,
                                    progress_counter=progress_counter,
                                    training_event_callback=training_event_callback
                                )
                        
                        # CRITICAL MEMORY CLEANUP: Delete encodings and clear GPU cache after all uses
                        # PyTorch's allocator can hold onto reserved memory even after tensors are deleted.
                        # Aggressive cleanup prevents memory growth during training.
                        # NOTE: Don't delete 'loss' here - it's used after the batch loop for epoch-level logging
                        del encodings
                        # Clear GPU cache periodically to prevent reserved memory growth
                        # Do it every batch for small datasets (<10 batches/epoch), every 5 batches for larger ones
                        cache_clear_interval = max(1, min(5, batches_per_epoch // 10))
                        if batch_idx % cache_clear_interval == 0:
                            try:
                                if is_gpu_available():
                                    empty_gpu_cache()
                            except Exception:
                                pass  # Don't fail training on cleanup errors

                        if use_profiler:
                            logger.info(f"Profiler step. Progress counter = {progress_counter}")
                            profiler.step()
                    # endfor (batch loop)
                    
                    # CRITICAL: Check if ALL batches were skipped due to OOM
                    # This happens when batch_size is too large for available GPU memory
                    # In this case, we should trigger the OOM retry mechanism instead of
                    # continuing with invalid loss values
                    if oom_stats["batches_skipped_this_epoch"] >= batches_per_epoch:
                        effective_consecutive = oom_stats["consecutive_oom_epochs"] + 1
                        logger.error(f"💥 ALL {batches_per_epoch} batches skipped due to OOM in epoch {epoch_idx + 1}")
                        logger.error(f"   This means batch_size={batch_size} is too large for available GPU memory")
                        
                        # Minimum batch size is 8 (was 32, which caused infinite loops)
                        suggested_batch_size = max(8, batch_size // 2)
                        suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                        
                        # Check if we can actually reduce (avoid infinite loop at minimum)
                        if suggested_batch_size >= batch_size:
                            logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                            raise RuntimeError(f"Cannot train: batch_size={batch_size} is minimum and still OOMs")
                        
                        if _oom_retry_count < max_oom_retries:
                            next_retry = _oom_retry_count + 1
                            logger.warning(f"🔄 Will retry #{next_retry}/{max_oom_retries} with batch_size={suggested_batch_size}")
                            raise FeatrixOOMRetryException(
                                message=f"All batches skipped due to OOM (batch_size={batch_size}, retry #{next_retry})",
                                current_batch_size=batch_size,
                                suggested_batch_size=suggested_batch_size,
                                epoch_idx=epoch_idx,
                                oom_count=oom_stats["oom_count_this_epoch"]
                            )
                        else:
                            logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                            raise RuntimeError(f"All batches skipped due to OOM and max retries ({max_oom_retries}) reached")
                        
                except RuntimeError as e:
                    error_str = str(e)
                    # Check if this is an OOM error from DataLoader worker being killed
                    if "DataLoader worker" in error_str and ("killed" in error_str.lower() or "signal" in error_str.lower()):
                        num_workers_used = train_dl_kwargs.get('num_workers', 0) if 'train_dl_kwargs' in locals() else 0
                        logger.error(f"💥 FATAL: DataLoader worker killed (likely OOM) during epoch {epoch_idx + 1}, batch {batch_idx + 1}")
                        logger.error(f"   Current configuration: {num_workers_used} workers, batch_size={batch_size}")
                        logger.error(f"   The Linux OOM killer terminated a worker process because system RAM was exhausted.")
                        logger.error(f"   This can happen when multiple processes compete for memory or memory usage spikes during training.")
                        # Print helpful recovery instructions
                        from lib.system_health_monitor import print_oom_recovery_help
                        print_oom_recovery_help(
                            error=e,
                            num_workers=num_workers_used,
                            batch_size=batch_size
                        )
                        raise  # Re-raise to stop training
                    elif "received 0 items of ancdata" in error_str or "ancdata" in error_str.lower():
                        # DataLoader worker IPC corruption - typically happens after CUDA OOM when workers die
                        # This error means file descriptor passing between processes failed because workers are dead/corrupted
                        num_workers_used = train_dl_kwargs.get('num_workers', 0) if 'train_dl_kwargs' in locals() else 0
                        batch_idx_context = batch_idx if 'batch_idx' in dir() else 0
                        
                        logger.error(f"=" * 80)
                        logger.error(f"💥 DATALOADER WORKER IPC CORRUPTION")
                        logger.error(f"=" * 80)
                        logger.error(f"   Error: {error_str}")
                        logger.error(f"   Epoch: {epoch_idx + 1}, Batch: {batch_idx_context + 1}")
                        logger.error(f"   Workers: {num_workers_used}, batch_size: {batch_size}")
                        logger.error(f"")
                        logger.error(f"   📋 DIAGNOSIS:")
                        logger.error(f"   This error occurs when DataLoader workers die (usually from OOM)")
                        logger.error(f"   and the inter-process communication breaks down. The 'ancdata'")
                        logger.error(f"   mechanism is how PyTorch passes file descriptors between processes.")
                        logger.error(f"   When workers are killed, pending data transfers fail.")
                        logger.error(f"")
                        
                        # Check if we already had OOM errors this epoch
                        had_oom = oom_stats.get("oom_count_this_epoch", 0) > 0 or oom_stats.get("oom_count_total", 0) > 0
                        if had_oom:
                            logger.error(f"   🔍 LIKELY CAUSE: CUDA OOM killed worker processes")
                            logger.error(f"   OOMs this epoch: {oom_stats.get('oom_count_this_epoch', 0)}")
                            logger.error(f"   OOMs total: {oom_stats.get('oom_count_total', 0)}")
                        else:
                            logger.error(f"   🔍 LIKELY CAUSE: System RAM exhaustion or resource limits")
                        
                        logger.error(f"=" * 80)
                        
                        # Trigger OOM retry with reduced batch size - same logic as other OOM handlers
                        suggested_batch_size = max(8, batch_size // 2)
                        suggested_batch_size = 2 ** int(math.log2(suggested_batch_size))
                        
                        if suggested_batch_size >= batch_size:
                            logger.error(f"❌ Already at minimum batch size ({batch_size}) - cannot reduce further")
                            raise
                        
                        if _oom_retry_count < max_oom_retries:
                            next_retry = _oom_retry_count + 1
                            logger.warning(f"🔄 Will retry #{next_retry}/{max_oom_retries} with batch_size={suggested_batch_size}")
                            raise FeatrixOOMRetryException(
                                message=f"DataLoader IPC corruption after OOM (batch_size={batch_size}, retry #{next_retry})",
                                current_batch_size=batch_size,
                                suggested_batch_size=suggested_batch_size,
                                epoch_idx=epoch_idx,
                                oom_count=oom_stats.get("oom_count_this_epoch", 1)
                            )
                        else:
                            logger.error(f"❌ Already retried {_oom_retry_count} times (max: {max_oom_retries}) - cannot retry")
                            raise
                    else:
                        # Not an OOM error - re-raise as is
                        raise
                
                # Compute validation loss ONCE per epoch (not after every batch!)
                try:
                    # AGGRESSIVE VRAM LOGGING: Log AFTER batch loop, BEFORE validation
                    _log_vram_usage("AFTER_BATCH_LOOP", epoch_idx, quiet=False)
                    
                    if val_dataloader is not None:
                        logger.info(f"   🔍 Computing validation loss for epoch {epoch_idx + 1}/{n_epochs}...")
                        
                        # NOTE: We do NOT kill training workers before validation anymore.
                        # With persistent_workers=True, workers stay alive across epochs - that's the whole point.
                        # Killing and recreating workers every epoch caused hangs when workers died during recreation.
                        # The training and validation dataloaders can coexist - they use the same data in memory.
                        
                        val_loss, val_components = self.compute_val_loss(val_dataloader)
                        
                        # Extract batch info from val_components for diagnostics
                        val_batch_losses = val_components.get('_batch_losses', []) if val_components else []
                        val_batch_sizes = val_components.get('_batch_sizes', []) if val_components else []
                        
                        # Compute average training loss for this epoch (before creating loss entry)
                        avg_train_loss = train_loss_sum / train_batch_count if train_batch_count > 0 else 0.0
                        
                        # UPDATE LOSS HISTORY WITH VALIDATION COMPONENTS
                        # The loss_history entry was created during the batch loop (before validation)
                        # with val_components=None. Now that validation is complete, update it with
                        # the actual component values so the training summary shows them correctly.
                        cumulative_epoch = epoch_idx
                        if hasattr(self, '_kv_fold_epoch_offset') and self._kv_fold_epoch_offset is not None:
                            cumulative_epoch = epoch_idx + self._kv_fold_epoch_offset
                        
                        loss_entry_with_components = {
                            "epoch": 1 + cumulative_epoch,
                            "current_learning_rate": scheduler.get_current_lr(),
                            "loss": avg_train_loss,  # Use averaged training loss, not last batch
                            "validation_loss": val_loss,
                            "time_now": time.time(),
                            "duration": time.time() - epoch_start_time_now,
                        }
                        
                        # Add loss components if available
                        if val_components:
                            loss_entry_with_components["spread"] = val_components.get('spread')
                            loss_entry_with_components["joint"] = val_components.get('joint')
                            loss_entry_with_components["marginal"] = val_components.get('marginal')
                            loss_entry_with_components["marginal_weighted"] = val_components.get('marginal_weighted')
                        
                        # Update the loss_history entry (INSERT OR REPLACE) with components
                        if hasattr(self, 'history_db') and self.history_db:
                            self.history_db.push_loss_history(loss_entry_with_components)
                        
                        # Check for OOM events after validation
                        self._check_oom_after_validation()
                        
                        # Log validation loss summary
                        self._log_validation_loss_summary(epoch_idx, val_loss, val_components, scheduler.get_current_lr())
                        self._log_detailed_val_diagnostics(epoch_idx, val_loss, val_components)
                        
                        # Reset epoch-level gradient and parameter update norm tracking for next epoch
                        if hasattr(self, '_epoch_grad_norms'):
                            self._epoch_grad_norms = []
                        if hasattr(self, '_epoch_param_update_norms'):
                            self._epoch_param_update_norms = []
                    else:
                        val_loss = 0
                        val_components = None
                        val_batch_losses = []
                        val_batch_sizes = []
                    
                    # Compute average training loss for this epoch (if not already computed above)
                    if 'avg_train_loss' not in locals():
                        avg_train_loss = train_loss_sum / train_batch_count if train_batch_count > 0 else 0.0
                    total_train_examples = sum(train_batch_sizes) if train_batch_sizes else 0
                    
                    # DIAGNOSTIC LOGGING: Compare train vs val loss computation
                    logger.info("=" * 80)
                    logger.info(f"📊 LOSS DIAGNOSTICS - Epoch {epoch_idx + 1}")
                    logger.info("=" * 80)
                    logger.info("TRAINING LOSS:")
                    logger.info(f"   loss_raw_sum: {train_loss_sum:.6f}")
                    logger.info(f"   loss_raw_mean: {avg_train_loss:.6f}")
                    logger.info(f"   num_batches: {train_batch_count}")
                    logger.info(f"   num_examples: {total_train_examples}")
                    logger.info(f"   batch_sizes: min={min(train_batch_sizes) if train_batch_sizes else 0}, max={max(train_batch_sizes) if train_batch_sizes else 0}, mean={sum(train_batch_sizes)/len(train_batch_sizes) if train_batch_sizes else 0:.1f}")
                    logger.info(f"   loss_per_batch_range: [{min(train_batch_losses) if train_batch_losses else 0:.6f}, {max(train_batch_losses) if train_batch_losses else 0:.6f}]")
                    logger.info(f"   reduction: mean over batches (averaged)")
                    if val_dataloader is not None:
                        logger.info("VALIDATION LOSS:")
                        logger.info(f"   loss_raw_sum: {sum(val_batch_losses):.6f}" if val_batch_losses else "   loss_raw_sum: N/A")
                        logger.info(f"   loss_raw_mean: {val_loss:.6f}")
                        logger.info(f"   num_batches: {len(val_batch_losses)}" if val_batch_losses else "   num_batches: N/A")
                        logger.info(f"   num_examples: {sum(val_batch_sizes)}" if val_batch_sizes else "   num_examples: N/A")
                        if val_batch_sizes:
                            logger.info(f"   batch_sizes: min={min(val_batch_sizes)}, max={max(val_batch_sizes)}, mean={sum(val_batch_sizes)/len(val_batch_sizes):.1f}")
                            logger.info(f"   loss_per_batch_range: [{min(val_batch_losses):.6f}, {max(val_batch_losses):.6f}]" if val_batch_losses else "")
                        logger.info(f"   reduction: mean over batches (averaged)")
                        # Log loss configuration if available
                        if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') and hasattr(self.encoder.config, 'loss_config'):
                            loss_config = self.encoder.config.loss_config
                            logger.info("LOSS CONFIGURATION:")
                            logger.info(f"   marginal_loss_weight: {getattr(loss_config, 'marginal_loss_weight', 'N/A')}")
                            logger.info(f"   marginal_loss_scaling_coefficient: {getattr(loss_config, 'marginal_loss_scaling_coefficient', 'N/A')}")
                    logger.info("=" * 80)
                    
                    # MEMORY LEAK DETECTION: Log VRAM after validation (NOT quiet - need to see this!)
                    _log_vram_usage("AFTER_VALIDATION", epoch_idx, quiet=False)
                except Exception as e:
                    raise e
                
                # Run all epoch diagnostics
                self._run_epoch_diagnostics(epoch_idx, val_loss, val_components, loss_dict)
                
                # ========================================================================
                # TRAINING TIMELINE - Track all metrics for visualization
                # ========================================================================
                if not hasattr(self, '_training_timeline'):
                    self._training_timeline = []
                    self._corrective_actions = []
                    logger.info("📊 Training timeline tracking initialized")
                
                # Log temperature changes
                spread_temp = getattr(self.encoder, '_last_spread_temp', None)
                if spread_temp is not None:
                    spread_temp = float(spread_temp.item()) if hasattr(spread_temp, 'item') else float(spread_temp)
                self._log_temp_change(epoch_idx, spread_temp, temp_boost_multiplier, batch_size)
                
                # Build epoch entry
                epoch_entry = self._build_epoch_timeline_entry(
                    epoch_idx, val_loss, val_components, d, scheduler.get_current_lr(),
                    lr_boost_multiplier, temp_boost_multiplier, batch_size, val_set_rotated, loss_dict
                )
                
                # Run failure detection
                latest_gradient_norm = getattr(self, '_latest_gradient_norm', None)
                lr_value = epoch_entry["learning_rate"]
                has_failure, failure_type, recommendations, current_train_loss, current_val_loss = self._run_failure_detection(
                    epoch_idx, epoch_entry, latest_gradient_norm, lr_value
                )
                
                # Track failure warnings in timeline
                if current_train_loss is not None:
                    self._track_failure_warnings(
                        epoch_idx, failure_type, current_train_loss, current_val_loss,
                        lr_value, latest_gradient_norm, recommendations
                    )
                
                # Initialize failure logging state
                if not hasattr(self, '_last_logged_failure'):
                    self._last_logged_failure = None
                    self._failure_repeat_count = 0
                failure_changed = (failure_type != self._last_logged_failure)
                
                # Handle NO_LEARNING failures with gradual LR ramping
                (lr_boost_multiplier, temp_boost_multiplier, intervention_stage, 
                 epochs_since_last_intervention, should_break_no_learning) = self._handle_no_learning_intervention(
                    epoch_idx=epoch_idx,
                    has_failure=has_failure,
                    failure_type=failure_type,
                    failure_changed=failure_changed,
                    current_train_loss=current_train_loss,
                    current_val_loss=current_val_loss,
                    val_loss=val_loss,
                    lr_boost_multiplier=lr_boost_multiplier,
                    temp_boost_multiplier=temp_boost_multiplier,
                    intervention_stage=intervention_stage,
                    epochs_since_last_intervention=epochs_since_last_intervention,
                    epoch_entry=epoch_entry,
                    d=d  # Pass progress dict for loss history access
                )
                if should_break_no_learning:
                    break
                
                # Check for resolved warnings
                self._check_resolved_warnings(
                    epoch_idx, has_failure, failure_type, current_train_loss, current_val_loss, lr_value
                )
                
                # Add entry to timeline
                self._append_to_timeline(epoch_idx, epoch_entry)
                
                # Log epoch summary line
                self._log_epoch_summary_line(epoch_idx, n_epochs, epoch_entry, has_failure, failure_type, intervention_stage)
                
                # Log mask bias statistics at end of epoch
                try:
                    from featrix.neural.mask_bias_tracker import get_mask_bias_tracker
                    tracker = get_mask_bias_tracker()
                    col_names = self.encoder.config.cols_in_order if hasattr(self, 'encoder') and hasattr(self.encoder, 'config') else None
                    tracker.log_stats(epoch_idx, col_names=col_names)
                except Exception as e:
                    # Don't fail training if mask bias logging fails
                    logger.debug(f"Mask bias logging failed: {e}")
                
                # Save timeline to JSON periodically
                self._save_timeline_to_json(epoch_idx, n_epochs, batch_size, optimizer_params,
                                             scheduler, dropout_scheduler, initial_dropout, final_dropout)
                
                # Generate/update timeline plot every epoch for real-time monitoring
                # This allows users to keep the plot open and watch it update during training
                try:
                    self._plot_training_timeline(n_epochs, optimizer_params)
                except Exception as plot_error:
                    # Don't fail training if plot generation fails
                    logger.debug(f"Failed to update timeline plot: {plot_error}")

                thisProc = psutil.Process(os.getpid())
                with thisProc.oneshot():
                    cpu_times = thisProc.cpu_times()
                    cpu_times = {"user": cpu_times.user, "system": cpu_times.system}
                    mem_info = thisProc.memory_info()
                    mem_info = {"rss": mem_info.rss, "vms": mem_info.vms}
                    resource_usage = {
                        "epoch": 1 + epoch_idx,
                        "pid": os.getpid(),
                        "p_create_time": thisProc.create_time(),
                        "p_cpu_times": cpu_times,
                        "p_mem_info": mem_info,
                    }
                    training_event_dict["resource_usage"] = resource_usage

                # Log gradient stats
                self._log_gradient_stats(epoch_idx, grad_clip_stats, use_adaptive_clipping)

                # Handle checkpoint saves (periodic and best)
                lowest_val_loss = self._handle_checkpoint_saves(
                    epoch_idx=epoch_idx,
                    n_epochs=n_epochs,
                    save_state_after_every_epoch=save_state_after_every_epoch,
                    save_state_epoch_interval=save_state_epoch_interval,
                    val_loss=val_loss,
                    lowest_val_loss=lowest_val_loss,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    dropout_scheduler=dropout_scheduler
                )
                
                # Handle validation loss tracking and early stopping
                if self._handle_val_loss_tracking_and_early_stop(
                    epoch_idx=epoch_idx,
                    n_epochs=n_epochs,
                    val_loss=val_loss,
                    val_components=val_components,
                    val_loss_early_stop_patience=val_loss_early_stop_patience,
                    val_loss_min_delta=val_loss_min_delta,
                    scheduler=scheduler,
                    optimizer=optimizer,
                    dropout_scheduler=dropout_scheduler,
                    d=d,
                    max_progress=max_progress,
                    print_callback=print_callback,
                    training_event_callback=training_event_callback,
                    training_event_dict=training_event_dict,
                    current_lr=scheduler.get_current_lr()
                ):
                    break  # Early stop triggered
                
                # NOTE: Validation loss tracking logic moved to _handle_val_loss_tracking_and_early_stop
                
                # Calculate min_epoch_for_early_stop for WeightWatcher analysis
                min_epoch_for_early_stop = 50

                # Run WeightWatcher analysis with convergence monitoring if enabled
                if self._run_weightwatcher_analysis(
                    epoch_idx=epoch_idx,
                    n_epochs=n_epochs,
                    enable_weightwatcher=enable_weightwatcher,
                    weightwatcher_save_every=weightwatcher_save_every,
                    weightwatcher_out_dir=weightwatcher_out_dir,
                    weightwatcher_job_id=weightwatcher_job_id,
                    min_epoch_for_early_stop=min_epoch_for_early_stop,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    dropout_scheduler=dropout_scheduler,
                    d=d,
                    max_progress=max_progress,
                    print_callback=print_callback
                ):
                    break  # WeightWatcher convergence detected - exit training loop

                # Update dropout rate if scheduler is enabled
                if dropout_scheduler is not None:
                    try:
                        current_dropout = dropout_scheduler.step(
                            epoch=epoch_idx,
                            model=self.encoder,
                            val_loss=val_loss if isinstance(val_loss, (int, float)) else None
                        )
                        d["current_dropout"] = current_dropout
                    except Exception as e:
                        logger.warning(f"⚠️ DropoutScheduler failed: {e}")

                # End of epoch summary - add separator
                logger.info("─" * 100)
                
                # ============================================================================
                # DYNAMIC RELATIONSHIP EXTRACTOR: Log detailed epoch summary
                # ============================================================================
                if hasattr(self.encoder, 'joint_encoder') and hasattr(self.encoder.joint_encoder, 'relationship_extractor'):
                    rel_extractor = self.encoder.joint_encoder.relationship_extractor
                    if rel_extractor is not None and hasattr(rel_extractor, 'log_epoch_summary'):
                        rel_extractor.log_epoch_summary()
                
                # MEMORY LEAK DETECTION: Log VRAM at end of epoch (NOT quiet - need to track growth!)
                _log_vram_usage("END_OF_EPOCH", epoch_idx, quiet=False)
                
                # Defragment GPU memory to prevent OOM from fragmentation buildup
                self._defragment_gpu_memory(epoch_idx)
                
                # Record metrics in LRTimeline for tracking and visualization
                if scheduler is not None and isinstance(scheduler, LRTimeline):
                    # Record training loss (use .item() if it's a tensor)
                    train_loss_val = loss.item() if hasattr(loss, 'item') else float(loss) if loss != "not set" else None
                    # Record validation loss (use .item() if it's a tensor)
                    val_loss_val = val_loss.item() if hasattr(val_loss, 'item') else float(val_loss) if val_loss != "not set" else None
                    
                    if train_loss_val is not None and val_loss_val is not None:
                        scheduler.record_loss(cumulative_epoch_idx, train_loss=train_loss_val, val_loss=val_loss_val)

                self.preserve_progress(
                    debug=d,
                    progress_counter=progress_counter,
                    # encode_time=loop_stopwatch.interval("encoder").duration(),
                    # loss_time=loop_stopwatch.interval("loss").duration(),
                    # back_time=loop_stopwatch.interval("backward").duration(),
                    # step_time=loop_stopwatch.interval("optimizer_step").duration(),
                    loss=loss,
                    val_loss=val_loss,
                    last_log_time=last_log_time,
                    batches_per_epoch=batches_per_epoch,
                    val_dataloader=val_dataloader,
                    optimizer_params=optimizer_params,
                    data_loader=data_loader,
                    lowest_val_loss=lowest_val_loss,
                )
                embedding_space_debug_training(epoch=epoch_idx, embedding_space=self)
                
                # Final callback after epoch completes (using variables from epoch loop)
                if print_progress_step is not None:
                    if print_callback is not None:
                        d["time_now"] = time.time()
                        d["epoch_idx"] = epoch_idx
                        d["batch_idx"] = batch_idx
                        d["progress_counter"] = progress_counter
                        d["max_progress"] = max_progress

                        self._record_epoch_loss_history(
                            d, epoch_idx, loss, val_loss, val_components, scheduler.get_current_lr(), epoch_start_time_now
                        )
                        print_callback(d)
                
        logger.info("Setting encoder.eval()")
        self.encoder.eval()

        # Final validation loss computation after all epochs complete
        if print_progress_step is not None:
            try:
                if val_dataloader is not None:
                    final_val_loss = self.compute_val_loss(val_dataloader)
                    if isinstance(final_val_loss, tuple):
                        final_val_loss = final_val_loss[0]  # Extract loss value if tuple
                else:
                    final_val_loss = 0
                logger.info(f"📊 Final validation loss after all epochs: {final_val_loss:.4f}")
            except Exception:
                pass  # Final validation loss computation is optional

        # TODO: anything to do post-training?
        # TODO: this method is where we would put tracking for e.g. W&B
        self.training_info["end_time"] = time.time()
        self.training_info["progress_info"] = d
        self.training_info["epochs"] = n_epochs
        
        # MEMORY LEAK FIX: Load full loss history from SQLite for summary
        if hasattr(self, 'history_db') and self.history_db:
            # Final flush to ensure all data is written
            self.history_db.flush()
            # Load full history from DB for summary
            full_loss_history = self.history_db.get_all_loss_history()
            if full_loss_history:
                # Update d with full history for summary
                d["loss_history"] = full_loss_history
                logger.info(f"💾 Loaded {len(full_loss_history)} loss history entries from SQLite for summary")
        
        # Generate final timeline plot (loss + LR + events)
        try:
            self._plot_training_timeline(n_epochs, optimizer_params)
        except Exception as e:
            logger.warning(f"⚠️  Failed to generate timeline plot: {e}")
            logger.debug(traceback.format_exc())
        
        # Log final string cache stats at end of training
        try:
            from featrix.neural.string_codec import log_final_string_cache_stats_all
            log_final_string_cache_stats_all()
        except Exception as e:
            logger.debug(f"Could not log final string cache stats: {e}")
        
        # Final gradient statistics summary
        logger.info("=" * 100)
        logger.info("📊 GRADIENT CLIPPING SUMMARY (ENTIRE TRAINING)")
        logger.info("=" * 100)
        if grad_clip_stats["total_batches"] > 0:
            total_batches = grad_clip_stats["total_batches"]
            clipped_batches = grad_clip_stats["clipped_batches"]
            clip_rate = (clipped_batches / total_batches) * 100
            avg_unclipped = grad_clip_stats["sum_unclipped_norms"] / total_batches
            avg_clipped = grad_clip_stats["sum_clipped_norms"] / total_batches
            
            logger.info(f"Total batches processed: {total_batches}")
            
            if use_adaptive_clipping:
                logger.info(f"Gradient clipping: ADAPTIVE (clip when grad > loss × {adaptive_grad_clip_ratio:.1f})")
                logger.info(f"Batches clipped: {clipped_batches} / {total_batches} ({clip_rate:.1f}%)")
                logger.info(f"Max gradient/loss ratio: {grad_clip_stats['max_grad_loss_ratio']:.2f}")
                logger.info(f"Average gradient norm: {avg_unclipped:.2f}")
                
                if grad_clip_stats["large_gradient_warnings"] > 0:
                    logger.info(f"📊 Logged {grad_clip_stats['large_gradient_warnings']} gradient outliers")
                
                # Final gradient/loss correlation analysis
                if len(grad_clip_stats["gradient_norms_history"]) >= 10:
                    grads = np.array(grad_clip_stats["gradient_norms_history"])
                    losses = np.array(grad_clip_stats["loss_values_history"])
                    
                    logger.info("")
                    logger.info("🔬 GRADIENT/LOSS RELATIONSHIP:")
                    logger.info(f"   Sample: {len(grads)} recent batches")
                    
                    if np.std(grads) > 0 and np.std(losses) > 0:
                        correlation = np.corrcoef(grads, losses)[0, 1]
                        avg_ratio = np.mean(grads / (losses + 1e-8))
                        logger.info(f"   Correlation: {correlation:.3f}")
                        logger.info(f"   Avg gradient/loss ratio: {avg_ratio:.3f}")
                        
                        if correlation > 0.5:
                            logger.info(f"   → Gradients scale with loss (correlation={correlation:.3f})")
                        elif correlation < -0.3:
                            logger.warning(f"   → Negative correlation ({correlation:.3f}) - unusual, may indicate LR too high or instability")
                        else:
                            logger.info(f"   → Weak correlation ({correlation:.3f}) - high batch-to-batch variance")
            else:
                logger.info("ℹ️  GRADIENT CLIPPING WAS DISABLED")
                logger.info(f"   Max gradient norm: {grad_clip_stats['max_unclipped_norm']:.2f}")
                logger.info(f"   Avg gradient norm: {avg_unclipped:.2f}")
        else:
            logger.warning("No gradient statistics collected (no batches processed?)")
        
        logger.info("=" * 100)
        
        # Store gradient stats in training info for later analysis
        self.training_info["gradient_clip_stats"] = {
            "total_batches": grad_clip_stats["total_batches"],
            "clipped_batches": grad_clip_stats["clipped_batches"],
            "clip_rate_pct": (grad_clip_stats["clipped_batches"] / max(1, grad_clip_stats["total_batches"])) * 100,
            "max_unclipped_norm": grad_clip_stats["max_unclipped_norm"],
            "max_clipped_norm": grad_clip_stats["max_clipped_norm"],
            "avg_unclipped_norm": grad_clip_stats["sum_unclipped_norms"] / max(1, grad_clip_stats["total_batches"]),
            "avg_clipped_norm": grad_clip_stats["sum_clipped_norms"] / max(1, grad_clip_stats["total_batches"]),
            "large_gradient_warnings": grad_clip_stats["large_gradient_warnings"],
            "clipping_mode": "adaptive" if use_adaptive_clipping else "disabled",
            "adaptive_grad_clip_ratio": adaptive_grad_clip_ratio,
            "max_grad_loss_ratio": grad_clip_stats["max_grad_loss_ratio"],
            "warning_multiplier": grad_clip_warning_multiplier,
        }
        
        # CRITICAL: Load the best checkpoint before generating summary or using the model
        # The final epoch may be overfit - we want the BEST model for downstream tasks
        logger.info("=" * 100)
        logger.info("🏆 LOADING BEST CHECKPOINT")
        logger.info("=" * 100)
        try:
            best_checkpoint_path = self.get_best_checkpoint_path()
            if os.path.exists(best_checkpoint_path):
                logger.info(f"📂 Loading best model from: {best_checkpoint_path}")
                best_epoch_idx = self.load_best_checkpoint()
                logger.info(f"✅ Successfully loaded best checkpoint from epoch {best_epoch_idx}")
                
                # Create self-contained model package
                try:
                    self._create_model_package(best_epoch_idx)
                except Exception as package_error:
                    logger.warning(f"⚠️  Failed to create model package: {package_error}")
                    # Continue anyway - package creation is optional
                
                # Re-compute losses on the best model for accurate reporting
                # Try to get data loaders from training_progress_data (stored during training)
                logger.info("🔄 Re-evaluating best model to verify performance...")
                self.encoder.eval()
                with torch.no_grad():
                    # Compute training loss on best model (sample for efficiency)
                    best_train_loss = None
                    try:
                        # Try to get from training_progress_data (stored during preserve_progress)
                        eval_data_loader = self.training_progress_data.get('data_loader')
                        
                        if eval_data_loader is not None:
                            best_train_loss = 0.0
                            train_batches = 0
                            for batch in eval_data_loader:
                                encodings = self.encoder(batch)
                                batch_loss, loss_dict = self.encoder.compute_total_loss(*encodings)
                                best_train_loss += batch_loss.item()
                                train_batches += 1
                                if train_batches >= 50:  # Sample for efficiency
                                    break
                            best_train_loss = best_train_loss / train_batches if train_batches > 0 else 0
                        else:
                            logger.debug("   Training data loader not available - skipping train loss recomputation")
                    except Exception as train_eval_error:
                        logger.warning(f"⚠️  Failed to recompute training loss: {train_eval_error}")
                        best_train_loss = None
                    
                    # Compute validation loss on best model
                    best_val_loss = None
                    best_val_components = None
                    try:
                        eval_val_dataloader = self.training_progress_data.get('val_dataloader')
                        
                        if eval_val_dataloader is not None:
                            best_val_loss, best_val_components = self.compute_val_loss(eval_val_dataloader)
                        else:
                            logger.debug("   Validation data loader not available - skipping val loss recomputation")
                    except Exception as val_eval_error:
                        logger.warning(f"⚠️  Failed to recompute validation loss: {val_eval_error}")
                        best_val_loss = None
                        best_val_components = None
                
                if best_train_loss is not None or best_val_loss is not None:
                    logger.info(f"📊 Best model performance:")
                    if best_train_loss is not None:
                        logger.info(f"   Training Loss: {best_train_loss:.4f}")
                    if best_val_loss is not None:
                        if best_val_components:
                            logger.info(f"   Validation Loss: {best_val_loss:.4f} (spread={best_val_components['spread']:.4f}, joint={best_val_components['joint']:.4f}, marginal={best_val_components['marginal_weighted']:.4f})")
                        else:
                            logger.info(f"   Validation Loss: {best_val_loss:.4f}")
                else:
                    logger.info("   Skipping loss recomputation (data loaders not available in this context)")
                
                # Store best model info for summary
                self.training_info["best_checkpoint_loaded"] = True
                self.training_info["best_checkpoint_epoch"] = best_epoch_idx
                if best_train_loss is not None:
                    self.training_info["best_checkpoint_train_loss"] = best_train_loss
                if best_val_loss is not None:
                    self.training_info["best_checkpoint_val_loss"] = best_val_loss
                    
                logger.info("=" * 100)
                logger.info(f"🎯 BEST CHECKPOINT LOADED: Using best model from epoch {best_epoch_idx} (not final epoch)")
                logger.info("=" * 100)
            else:
                logger.warning(f"⚠️  BEST CHECKPOINT NOT FOUND at {best_checkpoint_path}")
                logger.warning(f"   Using final epoch model (may be suboptimal)")
                self.training_info["best_checkpoint_loaded"] = False
        except Exception as e:
            logger.error(f"❌ Failed to load best checkpoint: {e}")
            logger.error(f"   Error details: {traceback.format_exc()}")
            logger.warning(f"   Using final epoch model (may be suboptimal)")
            self.training_info["best_checkpoint_loaded"] = False

        # Generate and log training summary with quality assessment
        try:
            progress_info = self.training_info.get('progress_info', {})
            loss_history = progress_info.get('loss_history', [])
            training_summary = summarize_es_training_results(self.training_info, loss_history, embedding_space=self)
            self.training_info["training_summary"] = training_summary
        except Exception as e:
            logger.warning(f"⚠️ Could not generate training summary: {e}")
        
        # Export LRTimeline data and visualizations
        if hasattr(self, '_train_scheduler') and isinstance(self._train_scheduler, LRTimeline):
            try:
                logger.info("=" * 100)
                logger.info("📊 EXPORTING LRTIMELINE DATA & VISUALIZATIONS")
                logger.info("=" * 100)
                
                # Export enhanced CSV with all metrics
                csv_path = os.path.join(self.output_dir, "es_lr_timeline.csv")
                self._train_scheduler.export_enhanced_csv(csv_path)
                logger.info(f"📄 ES LR schedule + metrics exported to: {csv_path}")
                
                # Export simple LR curve (for quick reference)
                simple_csv_path = os.path.join(self.output_dir, "es_lr_schedule.csv")
                self._train_scheduler.export_to_csv(simple_csv_path)
                logger.info(f"📄 ES LR schedule exported to: {simple_csv_path}")
                
                # Generate basic LR schedule plot
                schedule_plot_path = os.path.join(self.output_dir, "es_lr_schedule.png")
                self._train_scheduler.plot_schedule(schedule_plot_path)
                logger.info(f"📈 ES LR schedule plot saved to: {schedule_plot_path}")
                
                # Generate LR comparison plot (baseline vs adjusted)
                comparison_plot_path = os.path.join(self.output_dir, "es_lr_comparison.png")
                self._train_scheduler.plot_lr_comparison(comparison_plot_path)
                logger.info(f"📊 ES LR comparison plot (baseline vs adjusted) saved to: {comparison_plot_path}")
                
                # Generate comprehensive training history plot (LR + Loss + Metrics)
                history_plot_path = os.path.join(self.output_dir, "es_training_history.png")
                self._train_scheduler.plot_training_history(history_plot_path)
                logger.info(f"🎨 ES comprehensive training history plot saved to: {history_plot_path}")
                
                # Log adjustment summary
                if self._train_scheduler.adjustments:
                    logger.info("")
                    logger.info("🔧 LEARNING RATE ADJUSTMENTS SUMMARY:")
                    for epoch, adj_type, scale, reason in self._train_scheduler.adjustments:
                        logger.info(f"   Epoch {epoch}: {adj_type} by {scale:.2f}x - {reason}")
                else:
                    logger.info("")
                    logger.info("✅ No learning rate adjustments were needed")
                
                logger.info("=" * 100)
            except Exception as e:
                logger.warning(f"⚠️ LRTimeline export failed: {e}", exc_info=True)
        
        # Finalize WeightWatcher analysis
        if enable_weightwatcher:
            try:
                logger.info("📊 Creating final WeightWatcher summary...")
                from lib.weightwatcher_tracking import create_weightwatcher_summary, plot_convergence_dashboard
                create_weightwatcher_summary(
                    out_dir=weightwatcher_out_dir,
                    job_id=weightwatcher_job_id
                )
                
                # Create convergence dashboard visualization
                plot_convergence_dashboard(
                    out_dir=weightwatcher_out_dir,
                    job_id=weightwatcher_job_id,
                    save_plot=True,
                    show_plot=False
                )
                
            except Exception as e:
                logger.warning(f"⚠️ WeightWatcher finalization failed: {e}")
                # Log to centralized error tracker  
                try:
                    from error_tracker import log_training_error
                    log_training_error(
                        message=f"WeightWatcher finalization failed: {e}",
                        job_id=getattr(self, 'job_id', None) or self.training_info.get('job_id', None),
                        exception=e,
                        context={
                            "method": "weightwatcher_finalization",
                            "weightwatcher_out_dir": weightwatcher_out_dir,
                            "enable_weightwatcher": enable_weightwatcher
                        }
                    )
                except Exception as tracker_error:
                    logger.warning(f"Error tracker failed: {tracker_error}")
        
        # MEMORY LEAK FIX: Close training history database
        if hasattr(self, 'history_db') and self.history_db:
            self.history_db.close()
            logger.info("💾 Training history database closed")
        
        # Create comprehensive training movie JSON with all data
        logger.info("🎬 Creating comprehensive training movie JSON...")
        try:
            movie_data = self.create_training_movie_json(
                enable_weightwatcher=enable_weightwatcher,
                weightwatcher_out_dir=weightwatcher_out_dir
            )
            if movie_data:
                logger.info("✅ Training movie JSON created successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to create training movie JSON: {e}")
            # Log to centralized error tracker
            try:
                from error_tracker import log_training_error
                log_training_error(
                    message=f"Failed to create training movie JSON: {e}",
                    job_id=getattr(self, 'job_id', None) or self.training_info.get('job_id', None),
                    exception=e,
                    context={
                        "method": "create_training_movie_json",
                        "enable_weightwatcher": enable_weightwatcher,
                        "weightwatcher_out_dir": weightwatcher_out_dir
                    }
                )
            except Exception as tracker_error:
                logger.warning(f"Error tracker failed: {tracker_error}")
            return None
        
        # Generate GraphViz visualization of network architecture
        logger.info("🔷 Generating GraphViz network architecture visualization...")
        try:
            from lib.featrix.neural.network_viz import generate_graphviz_for_embedding_space
            graphviz_path = generate_graphviz_for_embedding_space(self)
            if graphviz_path:
                logger.info(f"✅ Network architecture visualization saved to {graphviz_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate GraphViz visualization: {e}")
        
        # Log encoder summary including adaptive strategies
        logger.info("")
        self.log_encoder_summary()
        
        self.reset_training_state()

        return

    def to_json_dict(self):
        # serialize to a json dict
        d = {}
        d["column-list"] = list(self.col_codecs.keys())
        d["codecs"] = self._codecs_to_dict()
        d["column_spec"] = self.column_spec
        d["json_transformations"] = self.json_transformations  # Include JSON transformation metadata
        # d['column-env_files'] = self.
        return d

    def _codecs_to_dict(self):
        d = {}
        for k, v in self.col_codecs.items():
            codec_dict = v.save()  # gets a dict
            d[k] = codec_dict
        return d

    def get_codec_meta(self):
        r = {}
        for k, v in self.col_codecs.items():
            codec_name = None
            try:
                codec_name = v.get_codec_name()
            except Exception:
                traceback.print_exc()
                codec_name = "ERROR"
            try:
                codec_info = v.get_codec_info()
            except Exception:
                codec_info = None
            r[k] = {"name": codec_name, "info": codec_info}
        return r

    def get_dimensions(self):
        return self.d_model

    def pre_warm_string_cache(self):
        """Pre-warm string cache with ALL strings from train and validation datasets."""
        if not self.string_cache:
            logger.info("No string cache provided - skipping pre-warming")
            return
        
        # Check if cache is already populated (from warm_string_server_cache call)
        # The @lru_cache is module-level and shared, so we can check its stats
        cache_info = _cached_encode.cache_info()  # pylint: disable=no-value-for-parameter
        
        # If cache already has significant entries (>1000), it was likely pre-warmed already
        # Skip the second pre-warming to avoid duplicate work
        if cache_info.currsize > 1000:
            logger.info(f"✅ String cache already populated: {cache_info.currsize} entries cached")
            logger.info(f"   Skipping duplicate pre-warming (cache was already populated in warm_string_server_cache)")
            logger.info(f"   Cache stats: {cache_info.hits} hits, {cache_info.misses} misses")
            return
            
        logger.info("🔥 Pre-warming string cache with ALL train and validation strings...")
        
        # Collect ALL string values from both datasets
        all_string_values = []
        string_columns = []
        
        # Get string columns from train dataset
        for c, codec in self.train_input_data.column_codecs().items():
            if codec == ColumnType.FREE_STRING:
                string_columns.append(c)
        
        if not string_columns:
            logger.info("ℹ️  No string columns found - skipping cache pre-warming")
            return
        
        logger.info(f"📝 Found {len(string_columns)} string columns: {string_columns}")
        
        # Collect strings from training dataset
        for col in string_columns:
            if col in self.train_input_data.df.columns:
                vals = self.train_input_data.df[col].astype(str).tolist()
                all_string_values.extend(vals)
                logger.info(f"   Train[{col}]: {len(vals)} strings")
        
        # Collect strings from validation dataset  
        for col in string_columns:
            if col in self.val_input_data.df.columns:
                vals = self.val_input_data.df[col].astype(str).tolist()
                all_string_values.extend(vals)
                logger.info(f"   Val[{col}]: {len(vals)} strings")
        
        # Remove duplicates
        unique_strings = list(set(all_string_values))
        logger.info(f"📊 Total unique strings to pre-warm: {len(unique_strings)} (from {len(all_string_values)} total)")
        
        if unique_strings:
            try:
                # Create a temporary StringCache to pre-warm the global @lru_cache
                _log_gpu_memory_embedded_space("BEFORE creating StringCache for pre-warming")
                from featrix.neural.simple_string_cache import SimpleStringCache as StringCache
                temp_cache = StringCache(
                    initial_values=unique_strings,
                    debugName="pre_warm_cache",
                    string_columns=string_columns,  # Enable local cache lookup
                    string_cache_filename=self.string_cache
                )
                _log_gpu_memory_embedded_space("AFTER creating StringCache for pre-warming")
                logger.info(f"✅ String cache pre-warmed with {len(unique_strings)} unique strings")
                logger.info("🚀 Training should now have minimal cache misses!")
            except Exception as e:
                logger.warning(f"⚠️ Failed to pre-warm cache: {e}")
                logger.info("Proceeding anyway - cache will be updated during training")
        else:
            logger.info("ℹ️  No strings to cache")

    def create_training_movie_json(self, enable_weightwatcher=False, weightwatcher_out_dir="ww_metrics"):
        """
        Create a comprehensive training movie JSON containing all training trajectory data.
        
        This includes:
        - Complete loss history with row IDs for path visualization
        - WeightWatcher metrics across all epochs
        - Mutual information progression
        - Training timings and resource usage
        - Convergence diagnostics and layer interventions
        
        Args:
            enable_weightwatcher: Whether WeightWatcher was enabled during training
            weightwatcher_out_dir: Directory containing WeightWatcher metrics
            
        Returns:
            dict: Comprehensive training movie data
        """
        try:
            logger.info("🎬 Creating comprehensive training movie JSON...")
            
            # Get job ID for file organization
            job_id = getattr(self, 'job_id', None) or self.training_info.get('job_id', None)
            
            # Base movie data from training_info
            movie_data = {
                "metadata": {
                    "job_id": job_id,
                    "creation_time": time.time(),
                    "model_type": "embedding_space",
                    "model_param_count": getattr(self, 'model_param_count', 0),
                    "num_rows": self.len_df(),
                    "num_cols": len(self.train_input_data.df.columns),
                    "column_list": list(self.col_codecs.keys()),
                    "compute_device": get_device().type,
                    "hostname": socket.gethostname(),
                    "pid": os.getpid(),
                },
                "training_trajectory": [],
                "weightwatcher_metrics": [],
                "convergence_diagnostics": {},
                "final_summary": {}
            }
            
            # Extract progress info from training_info
            progress_info = self.training_info.get('progress_info', {})
            
            # 1. Build training trajectory with row IDs
            loss_history = progress_info.get('loss_history', [])
            mutual_info = progress_info.get('mutual_information', [])
            
            # Create comprehensive trajectory combining all data sources
            row_id = 0
            for epoch_data in loss_history:
                trajectory_point = {
                    "row_id": row_id,
                    "epoch": epoch_data.get('epoch', 0),
                    "timestamp": epoch_data.get('time_now', 0),
                    "loss_metrics": {
                        "training_loss": epoch_data.get('loss', 0),
                        "validation_loss": epoch_data.get('validation_loss', 0),
                        "learning_rate": epoch_data.get('current_learning_rate', 0),
                        "duration": epoch_data.get('duration', 0),
                    },
                    "mutual_information": None,  # Will be populated below
                    "weightwatcher_metrics": None,  # Will be populated below
                    "interventions": {
                        "layers_clipped": [],
                        "layers_frozen": [],
                        "dropout_rate": None
                    }
                }
                
                # Add mutual information for this epoch
                for mi_data in mutual_info:
                    if mi_data.get('epoch') == epoch_data.get('epoch'):
                        trajectory_point["mutual_information"] = {
                            "column_estimates": mi_data.get('columns', {}),
                            "joint_estimate": mi_data.get('joint', 0)
                        }
                        break
                
                movie_data["training_trajectory"].append(trajectory_point)
                row_id += 1
            
            # 2. Load WeightWatcher metrics if enabled
            if enable_weightwatcher:
                try:
                    # Determine WeightWatcher output directory
                    if job_id and job_id != "unknown":
                        ww_full_dir = os.path.join(weightwatcher_out_dir, job_id)
                    else:
                        ww_full_dir = weightwatcher_out_dir
                    
                    # Load summary JSON if available
                    ww_summary_file = os.path.join(ww_full_dir, "ww_summary.json")
                    if os.path.exists(ww_summary_file):
                        with open(ww_summary_file, 'r') as f:
                            ww_data = json.load(f)
                        
                        # Add WeightWatcher metrics to trajectory points
                        for ww_entry in ww_data:
                            epoch = ww_entry.get('epoch', 0)
                            
                            # Find corresponding trajectory point
                            for traj_point in movie_data["training_trajectory"]:
                                if traj_point["epoch"] == epoch:
                                    traj_point["weightwatcher_metrics"] = {
                                        "alpha": ww_entry.get('alpha', 0),
                                        "spectral_norm": ww_entry.get('spectral_norm', 0),
                                        "log_norm": ww_entry.get('log_norm', 0),
                                        "entropy": ww_entry.get('entropy', 0),
                                        "rank_loss": ww_entry.get('rank_loss', 0),
                                        "layer_name": ww_entry.get('layer_name', ''),
                                        "layer_id": ww_entry.get('layer_id', 0)
                                    }
                                    break
                        
                        # Store all WeightWatcher metrics separately too
                        movie_data["weightwatcher_metrics"] = ww_data
                        
                        logger.info(f"📊 Added {len(ww_data)} WeightWatcher metric entries")
                    
                    # Load convergence diagnostics
                    clipping_file = os.path.join(ww_full_dir, "clipping_diagnostics.json")
                    if os.path.exists(clipping_file):
                        with open(clipping_file, 'r') as f:
                            clipping_data = json.load(f)
                        movie_data["convergence_diagnostics"] = clipping_data
                        logger.info("🔧 Added clipping diagnostics")
                    
                    # Load WeightWatcher summary CSV for aggregated metrics
                    ww_summary_csv = os.path.join(ww_full_dir, "ww_summary.csv")
                    if os.path.exists(ww_summary_csv):
                        df_summary = pd.read_csv(ww_summary_csv)
                        
                        # Add epoch-level summary metrics to trajectory
                        for _, row in df_summary.iterrows():
                            epoch = row.get('epoch', 0)
                            
                            # Find trajectory point and add summary metrics
                            for traj_point in movie_data["training_trajectory"]:
                                if traj_point["epoch"] == epoch:
                                    traj_point["epoch_summary"] = {
                                        "alpha_mean": row.get('alpha_mean', 0),
                                        "alpha_std": row.get('alpha_std', 0),
                                        "spectral_norm_mean": row.get('spectral_norm_mean', 0),
                                        "alpha_pct_below_6": row.get('alpha_pct_below_6', 0),
                                        "entropy_mean": row.get('entropy_mean', 0),
                                        "rank_loss_mean": row.get('rank_loss_mean', 0),
                                        "log_norm_mean": row.get('log_norm_mean', 0)
                                    }
                                    break
                        
                        logger.info(f"📈 Added epoch-level summary metrics for {len(df_summary)} epochs")
                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load WeightWatcher metrics: {e}")
            
            # 3. Add final summary
            final_epoch = len(loss_history)
            if loss_history:
                final_loss = loss_history[-1]
                movie_data["final_summary"] = {
                    "total_epochs": final_epoch,
                    "final_training_loss": final_loss.get('loss', 0),
                    "final_validation_loss": final_loss.get('validation_loss', 0),
                    "final_learning_rate": final_loss.get('current_learning_rate', 0),
                    "total_training_time": self.training_info.get('end_time', 0) - self.training_info.get('start_time', 0),
                    "converged": False,  # Will be updated if convergence info available
                    "convergence_epoch": None
                }
            
            # Add convergence status if available
            if hasattr(self, '_ww_callback') and self._ww_callback:
                convergence_status = self._ww_callback.get_convergence_status()
                movie_data["final_summary"]["converged"] = convergence_status.get('has_converged', False)
                movie_data["final_summary"]["convergence_epoch"] = convergence_status.get('convergence_epoch', None)
                movie_data["convergence_diagnostics"]["convergence_status"] = convergence_status
            
            # 4. Save the comprehensive movie JSON
            movie_filename = f"training_movie_{job_id}.json" if job_id else "training_movie.json"
            movie_path = os.path.join(self.output_dir, movie_filename)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(movie_path), exist_ok=True)
            
            with open(movie_path, 'w') as f:
                json.dump(movie_data, f, indent=2)
            
            logger.info(f"🎬 Training movie saved to {movie_path}")
            logger.info(f"   📊 {len(movie_data['training_trajectory'])} trajectory points")
            logger.info(f"   📈 {len(movie_data['weightwatcher_metrics'])} WeightWatcher entries")
            logger.info(f"   🔧 Convergence diagnostics: {len(movie_data['convergence_diagnostics'])} entries")
            
            return movie_data
            
        except Exception as e:
            logger.error(f"❌ Failed to create training movie JSON: {e}")
            traceback.print_exc()
            return None


if __name__ == "__main__":
    from featrix.neural.input_data_set import FeatrixInputDataSet

    fileName = sys.argv[1]
    if not os.path.exists(fileName):
        logger.error(f"No file exists at {fileName}")
        os._exit(2)

    # Load data from CSV
    df = pd.read_csv(fileName)
    
    # Split into train/val (80/20 split)
    train_size = int(0.8 * len(df))
    train_df = df.iloc[:train_size]
    val_df = df.iloc[train_size:]
    
    # Create FeatrixInputDataSet objects (expects DataFrame, not filename)
    train_fids = FeatrixInputDataSet(df=train_df)
    val_fids = FeatrixInputDataSet(df=val_df)
    
    # Create EmbeddingSpace (requires both train and val data)
    es = EmbeddingSpace(train_input_data=train_fids, val_input_data=val_fids)
    es.train()
