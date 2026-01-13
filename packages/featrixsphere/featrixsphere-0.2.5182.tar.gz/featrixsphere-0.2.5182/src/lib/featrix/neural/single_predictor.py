#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import copy
import json
import logging
import warnings
import math
import gc
import os
import pickle
import sys
import time
import traceback
import warnings
from typing import Dict
from typing import Optional
from typing import List
from typing import Any
from typing import cast
from datetime import datetime
from zoneinfo import ZoneInfo
import copy
import socket
from pathlib import Path

import pandas as pd
import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer, LabelEncoder
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression, chi2

from torch import nn
from torch.optim.lr_scheduler import CosineAnnealingLR, SequentialLR, ConstantLR
from featrix.neural.lr_timeline import LRTimeline
from torch.utils.data import DataLoader

from featrix.neural.exceptions import FeatrixRestartTrainingException, RestartConfig
from featrix.neural.training_exceptions import TrainingFailureException, EarlyStoppingException
from featrix.neural.training_logger import MetricTracker, RowErrorTracker, StructuredLogger

# from featrix.models import JobIncrementalStatus
from featrix.neural.gpu_utils import (
    is_gpu_available,
    is_cuda_available,
    get_device,
    get_gpu_memory_allocated,
    get_gpu_memory_reserved,
    get_max_gpu_memory_allocated,
    get_max_gpu_memory_reserved,
    get_gpu_memory_summary,
    get_gpu_memory_snapshot,
    get_gpu_device_properties,
    empty_gpu_cache,
    synchronize_gpu,
    reset_gpu_peak_memory_stats,
)
from featrix.neural.data_frame_data_set import collate_tokens
from featrix.neural.data_frame_data_set import SuperSimpleSelfSupervisedDataset
from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.dataloader_utils import create_dataloader_kwargs
from featrix.neural.encoders import create_scalar_codec
from featrix.neural.encoders import create_set_codec
from featrix.neural.featrix_token import Token
from featrix.neural.featrix_token import TokenBatch
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.scalar_codec import AdaptiveScalarEncoder
from featrix.neural.scalar_codec import ScalarCodec
from featrix.neural.set_codec import SetCodec
from featrix.neural.set_codec import SetEncoder
from featrix.neural.set_codec import FocalLoss

from featrix.neural.training_context_manager import PredictorTrainingContextManager, TrainingState, PredictorEvalModeContextManager
from featrix.neural.utils import ideal_batch_size, ideal_epochs_predictor
from featrix.neural.string_codec import StringCodec, get_global_string_cache
from featrix.neural.model_config import ColumnType, SimpleMLPConfig

# Import standardized logging configuration
from featrix.neural.logging_config import configure_logging
configure_logging()

# Suppress noisy library logs
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Rate limiter for prediction failure logging
_prediction_failure_log_state = {
    'last_reset_time': time.time(),
    'log_count': 0,
    'total_failures': 0,  # Track total failures even when not logging
    'window_duration': 600,  # 10 minutes in seconds
    'max_logs_per_window': 2,  # Max 2 full queries logged per window
}


def _should_log_prediction_failure():
    """
    Rate limiter for prediction failure logging.
    Returns True if we should log a full failure message, False otherwise.
    Also logs a summary periodically if there are many failures.
    """
    global _prediction_failure_log_state
    state = _prediction_failure_log_state
    current_time = time.time()
    
    # Reset window if expired
    if current_time - state['last_reset_time'] >= state['window_duration']:
        # Log summary if there were failures in the previous window
        if state['total_failures'] > 0:
            logger.warning(
                f"PREDICTION FAILURES: {state['total_failures']} failures in last {state['window_duration']/60:.1f} minutes "
                f"(only {state['log_count']} full queries logged due to rate limiting)"
            )
        # Reset counters
        state['last_reset_time'] = current_time
        state['log_count'] = 0
        state['total_failures'] = 0
    
    # Increment total failure count
    state['total_failures'] += 1
    
    # Check if we should log this failure
    if state['log_count'] < state['max_logs_per_window']:
        state['log_count'] += 1
        return True
    else:
        return False


def _walk_model_for_gpu(model, name="model", depth=0, indent="  "):
    """Recursively walk through entire model and report ANYTHING on GPU."""
    gpu_items = []
    
    # Check if it's a module
    if isinstance(model, torch.nn.Module):
        # Check all parameters
        for param_name, param in model.named_parameters(recurse=False):
            if param.device.type in ['cuda', 'mps']:
                full_name = f"{name}.{param_name}" if name != "model" else param_name
                gpu_items.append((full_name, "parameter", param.shape, param.numel(), param.device))
        
        # Check all buffers
        for buffer_name, buffer in model.named_buffers(recurse=False):
            if buffer.device.type in ['cuda', 'mps']:
                full_name = f"{name}.{buffer_name}" if name != "model" else buffer_name
                gpu_items.append((full_name, "buffer", buffer.shape, buffer.numel(), buffer.device))
        
        # Recursively check all child modules
        for child_name, child_module in model.named_children():
            child_full_name = f"{name}.{child_name}" if name != "model" else child_name
            child_gpu = _walk_model_for_gpu(child_module, child_full_name, depth + 1, indent)
            gpu_items.extend(child_gpu)
        
        # Check all attributes that might be tensors or modules
        for attr_name in dir(model):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(model, attr_name)
                if isinstance(attr, torch.nn.Module):
                    attr_full_name = f"{name}.{attr_name}" if name != "model" else attr_name
                    attr_gpu = _walk_model_for_gpu(attr, attr_full_name, depth + 1, indent)
                    gpu_items.extend(attr_gpu)
                elif isinstance(attr, torch.Tensor):
                    if attr.device.type in ['cuda', 'mps']:
                        attr_full_name = f"{name}.{attr_name}" if name != "model" else attr_name
                        gpu_items.append((attr_full_name, "tensor", attr.shape, attr.numel(), attr.device))
            except Exception:
                pass
    
    # Check if it's a tensor
    elif isinstance(model, torch.Tensor):
        if model.device.type in ['cuda', 'mps']:
            gpu_items.append((name, "tensor", model.shape, model.numel(), model.device))
    
    return gpu_items


def _log_gpu_memory(context: str = "", log_level=logging.INFO):
    """Quick GPU memory logging for tracing memory usage."""
    if not is_gpu_available():
        return
    try:
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        logger.log(log_level, f"📊 GPU MEMORY [{context}]: Allocated={allocated:.3f} GB, Reserved={reserved:.3f} GB, Peak={max_allocated:.3f} GB")
    except Exception as e:
        logger.debug(f"Could not log GPU memory: {e}")

def _dump_cuda_memory_usage(context: str = ""):
    """
    Dump detailed GPU memory usage information when OOM occurs.
    This helps debug what's holding VRAM.
    
    Args:
        context: Optional context string describing where the OOM occurred
    """
    try:
        if not is_gpu_available():
            logger.warning(f"⚠️  GPU not available - cannot dump memory usage")
            return
        
        logger.info("="*80)
        logger.info(f"🔍 GPU MEMORY DUMP {f'({context})' if context else ''}")
        logger.info("="*80)
        
        # Get memory stats
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        max_reserved = get_max_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        
        logger.info(f"📊 Current Memory Usage:")
        logger.info(f"   Allocated: {allocated:.2f} GB")
        logger.info(f"   Reserved: {reserved:.2f} GB")
        logger.info(f"   Max Allocated (peak): {max_allocated:.2f} GB")
        logger.info(f"   Max Reserved (peak): {max_reserved:.2f} GB")
        
        # Get detailed memory summary (CUDA only, empty string for MPS/CPU)
        try:
            memory_summary = get_gpu_memory_summary(abbreviated=False)
            if memory_summary:
                logger.info(f"\n📋 Detailed Memory Summary:")
                logger.info(memory_summary)
            else:
                logger.warning(f"⚠️  Memory summary not available for this backend")
        except Exception as summary_err:
            logger.warning(f"⚠️  Could not get detailed memory summary: {summary_err}")
        
        # Get memory snapshot (shows what tensors are allocated, CUDA only)
        try:
            memory_snapshot = get_gpu_memory_snapshot()
            if memory_snapshot:
                logger.info(f"\n📸 Memory Snapshot Analysis:")
                logger.info(f"   Total active allocations: {len(memory_snapshot)}")
                
                # Group allocations by size to identify patterns
                size_buckets = {
                    '<1MB': 0,
                    '1-10MB': 0,
                    '10-100MB': 0,
                    '100MB-1GB': 0,
                    '>1GB': 0
                }
                total_size_by_bucket = {
                    '<1MB': 0,
                    '1-10MB': 0,
                    '10-100MB': 0,
                    '100MB-1GB': 0,
                    '>1GB': 0
                }
                
                # Find largest allocations
                allocations_with_size = []
                for alloc in memory_snapshot:
                    if isinstance(alloc, dict):
                        total_size = alloc.get('total_size', 0)
                        active_size = alloc.get('active_size', 0)
                        size_mb = total_size / (1024**2)
                        
                        # Bucket by size
                        if size_mb < 1:
                            size_buckets['<1MB'] += 1
                            total_size_by_bucket['<1MB'] += total_size
                        elif size_mb < 10:
                            size_buckets['1-10MB'] += 1
                            total_size_by_bucket['1-10MB'] += total_size
                        elif size_mb < 100:
                            size_buckets['10-100MB'] += 1
                            total_size_by_bucket['10-100MB'] += total_size
                        elif size_mb < 1024:
                            size_buckets['100MB-1GB'] += 1
                            total_size_by_bucket['100MB-1GB'] += total_size
                        else:
                            size_buckets['>1GB'] += 1
                            total_size_by_bucket['>1GB'] += total_size
                        
                        # Track for largest allocations
                        if active_size > 0:
                            allocations_with_size.append((active_size, alloc))
                
                # Show size distribution
                logger.info(f"\n📊 Allocation Size Distribution:")
                for bucket, count in size_buckets.items():
                    if count > 0:
                        size_mb = total_size_by_bucket[bucket] / (1024**2)
                        logger.info(f"   {bucket:12s}: {count:6d} allocations, {size_mb:8.2f} MB total")
                
                # Show top 10 largest allocations
                if allocations_with_size:
                    allocations_with_size.sort(reverse=True, key=lambda x: x[0])
                    logger.info(f"\n🔝 Top 10 Largest Active Allocations:")
                    for i, (active_size, alloc) in enumerate(allocations_with_size[:10], 1):
                        size_mb = active_size / (1024**2)
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        logger.info(f"   {i:2d}. {size_mb:8.2f} MB active / {total_size_mb:8.2f} MB total ({segment_type} pool)")
                        # Show frames if available
                        frames = alloc.get('frames', [])
                        if frames:
                            logger.info(f"       Stack trace:")
                            for frame in frames[:3]:  # First 3 frames
                                filename = frame.get('filename', 'unknown')
                                line = frame.get('line', 'unknown')
                                func = frame.get('function', 'unknown')
                                logger.info(f"         {filename}:{line} in {func}")
                
                # Show first 5 allocations with details (for debugging)
                logger.info(f"\n🔍 Sample Allocations (first 5):")
                for i, alloc in enumerate(memory_snapshot[:5], 1):
                    if isinstance(alloc, dict):
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        active_size_mb = alloc.get('active_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        blocks = alloc.get('blocks', [])
                        active_blocks = [b for b in blocks if b.get('state') == 'active_allocated']
                        logger.info(f"   {i}. {active_size_mb:.2f} MB / {total_size_mb:.2f} MB ({segment_type}, {len(active_blocks)} active blocks)")
                
                if len(memory_snapshot) > 5:
                    logger.info(f"   ... and {len(memory_snapshot) - 5} more allocations")
        except Exception as snapshot_err:
            logger.warning(f"⚠️  Could not get memory snapshot: {snapshot_err}")
        
        # Get nvidia-smi output for comparison
        try:
            import subprocess
            nvidia_smi = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if nvidia_smi.returncode == 0:
                logger.info(f"\n🖥️  nvidia-smi GPU Status:")
                for line in nvidia_smi.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 3:
                            mem_used = parts[0].strip()
                            mem_total = parts[1].strip()
                            gpu_util = parts[2].strip()
                            logger.info(f"   Memory: {mem_used} MB / {mem_total} MB, Utilization: {gpu_util}%")
        except Exception as smi_err:
            logger.warning(f"⚠️  Could not get nvidia-smi output: {smi_err}")
        
        logger.info("="*80)
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to dump CUDA memory usage: {e}")


def compute_binary_lift_bands(y_pred, y_true, threshold=0.5, n_bins=10):
    """
    Compute prediction performance across probability bands.
    
    This metric bins predictions by probability and shows ground truth distribution,
    predicted distribution, and accuracy in each band.
    
    Args:
        y_pred: array-like of predicted probabilities for positive class (float in [0,1])
        y_true: array-like of ground truth binary labels (1 = positive, 0 = negative)
        threshold: classification threshold (predictions >= threshold are positive)
        n_bins: number of probability bands (e.g. deciles)
    
    Returns:
        pandas.DataFrame with one row per band:
            - band: band label (interval)
            - band_width: width of probability band
            - avg_pred: mean predicted prob in band
            - n: number of samples in band
            - actual_pos: count of actual positives (ground truth = 1)
            - actual_neg: count of actual negatives (ground truth = 0)
            - pred_pos: count predicted positive (prob >= threshold)
            - pred_neg: count predicted negative (prob < threshold)
            - correct: count of correct predictions
            - correct_pct: percentage correct in this band
    """
    df = pd.DataFrame({
        "y_true": np.asarray(y_true),
        "y_pred": np.asarray(y_pred),
    })
    
    # Bin by predicted probability into quantiles (deciles by default)
    df["band"] = pd.qcut(df["y_pred"], q=n_bins, duplicates="drop")
    
    def compute_band_stats(g):
        # Determine prediction for each sample based on threshold
        y_pred_class = (g["y_pred"] >= threshold).astype(int)
        correct = (g["y_true"] == y_pred_class).sum()
        
        return pd.Series({
            "avg_pred": g["y_pred"].mean(),
            "n": len(g),
            "actual_pos": (g["y_true"] == 1).sum(),
            "actual_neg": (g["y_true"] == 0).sum(),
            "pred_pos": (g["y_pred"] >= threshold).sum(),
            "pred_neg": (g["y_pred"] < threshold).sum(),
            "correct": correct,
            "correct_pct": (correct / len(g) * 100) if len(g) > 0 else 0,
        })
    
    # include_groups parameter only exists in pandas >= 2.2.0
    try:
        grouped = df.groupby("band", observed=True).apply(compute_band_stats, include_groups=False)
    except TypeError:
        # Fallback for older pandas versions
        grouped = df.groupby("band", observed=True).apply(compute_band_stats)
    
    # Add band width
    grouped['band_width'] = grouped.index.map(lambda x: x.right - x.left)
    
    # Sort by average predicted probability so the plot is monotone in x
    grouped = grouped.sort_values("avg_pred").reset_index()
    
    return grouped

class SPIdentifierFilter(logging.Filter):
    """Logging filter that prepends SP identifier and epoch to all log messages."""
    def __init__(self, identifier, sp_instance):
        super().__init__()
        self.identifier = identifier
        self.sp_instance = sp_instance  # Reference to FeatrixSinglePredictor for epoch tracking
    
    def filter(self, record):
        # Get current epoch and total epochs from the SP instance
        # Epoch is now shown in standardized logging format via current_epoch_ctx
        # No need to prepend it to messages anymore
        return True


class LearningRateTooLowError(Exception):
    """
    Exception raised when the model shows signs of learning too slowly 
    (zero gradients + constant probability outputs) and needs a higher learning rate.
    """
    def __init__(self, message, current_lr, suggested_lr_multiplier=2.0):
        self.current_lr = current_lr
        self.suggested_lr_multiplier = suggested_lr_multiplier
        super().__init__(message)




class FeatrixSinglePredictor:
    def __init__(
        self, 
        embedding_space: EmbeddingSpace, 
        predictor, 
        name: str = None, 
        user_metadata: dict = None,
        enable_feature_suggestions: bool = False,  # Disabled by default - DynamicRelationshipExtractor handles this
    ):
        self.d_model = embedding_space.d_model
        self.embedding_space = embedding_space
        self.enable_feature_suggestions = enable_feature_suggestions
        
        # Initialize disabled feature metadata tracking (kept for backward compatibility)
        self._loaded_feature_metadata = None
        
        # CRITICAL: If we have a pending fine-tuned encoder state_dict, load it now
        if hasattr(self, '_pending_state_dicts') and '_finetuned_encoder_state_dict' in self._pending_state_dicts:
            try:
                encoder_state = self._pending_state_dicts['_finetuned_encoder_state_dict']
                self.embedding_space.encoder.load_state_dict(encoder_state)
                logger.info(f"✅ Loaded fine-tuned encoder state_dict ({len(encoder_state)} keys)")
                del self._pending_state_dicts['_finetuned_encoder_state_dict']
            except Exception as e:
                logger.error(f"❌ CRITICAL: Failed to load fine-tuned encoder: {e}")
                logger.error(traceback.format_exc())
        
        # predictor_base should not have the final linear layer because the target
        # variable is not yet known, and we need to create the codec in order to figure
        # out its dimensionality.
        self.predictor_base = predictor
        # predictor is the full downstream prediction model, including the final output.
        self.predictor = None

        # Store name for identification and tracking
        self.name = name
        
        # Store user metadata for identification and tracking
        self.user_metadata = user_metadata
        
        self.target_col_type = None
        self.target_codec = None
        self.train_df = None
        self.target_type = None
        self.target_col_name = None

        # A dictionary to hold codecs from the embeddings space AND  the codec
        # for the target column.
        self.all_codecs = {}

        self.train_dataset = None
        self.is_target_scalar = None

        self.sm = nn.Softmax(dim=-1)
        self.training_metrics = None

        self.metrics_had_error = {}

        self.metrics_time = 0

        self.run_binary_metrics = True
        self._is_binary_cached = None  # Cache for should_compute_binary_metrics()
        
        # Metadata about categories excluded from validation during training
        self.validation_excluded_categories = None
        
        # Distribution metadata for hyperparameter selection
        self.distribution_metadata = None
        
        # Distribution shift analysis results (set during training if analysis is performed)
        self.distribution_shift_results = None
        
        # Training warnings tracker
        # Structure: {"warning_type": {"epochs": [list of epochs], "details": [list of detail dicts]}}
        self.training_warnings = {}
        
        # Run identifier for logging (set by test scripts)
        self.run_identifier = None
        
        # Track current epoch for logging
        self._current_epoch = -1  # -1 means pre-training/setup phase
        
        self.best_epoch_warnings = []  # Warnings that occurred at the best epoch
        
        # Adaptive FocalLoss parameters
        self.adaptive_loss_enabled = True  # Enable adaptive loss adjustment
        self.focal_gamma_history = []  # Track gamma adjustments
        self.focal_min_weight_history = []  # Track min_weight adjustments
        self.loss_adjustment_count = 0  # How many times we've adjusted
        self.last_loss_adjustment_epoch = -1  # Prevent too-frequent adjustments
        
        # Training timeline tracking (like ES training)
        self._training_timeline = []
        self._corrective_actions = []
        self._output_dir = None  # Will be set during training
        
        # Validation error tracking - per-row correct/wrong flags per epoch
        self._validation_error_tracking = None  # Will be initialized during training
        
        # Feature suggestion tracker - dynamic feature engineering during training
        # DISABLED BY DEFAULT: DynamicRelationshipExtractor handles relationship learning now
        self._feature_tracker = None
        self._effectiveness_tracker = None
        self._features_applied_epochs = []
        self._loaded_features = []
        
        if self.enable_feature_suggestions:
            from featrix.neural.feature_suggestion_tracker import FeatureSuggestionTracker
            from featrix.neural.feature_effectiveness_tracker import FeatureEffectivenessTracker
            
            self._feature_tracker = FeatureSuggestionTracker(
                vote_threshold=3,              # Min votes (ignored in aggressive mode)
                check_interval=5,              # Check every 5 epochs
                max_features_per_round=1,      # Apply top 1 feature at a time
                min_epoch_before_apply=20,     # Wait until epoch 20 before applying
                apply_top_every_interval=True  # AGGRESSIVE: always apply top-voted feature
            )
            
            # Feature effectiveness tracker - track which features actually improve metrics
            self._effectiveness_tracker = FeatureEffectivenessTracker()
        
        # Warning state tracking - track active warnings to detect start/stop
        self._active_warnings = {}  # {warning_type: {'start_epoch': int, 'details': dict}}
        
        # Dead gradient detection and restart mechanism
        self.dead_gradient_threshold = 1e-6  # Gradients below this are considered "dead"
        self.dead_gradient_epochs = []  # Track epochs with dead gradients
        self.training_restart_count = 0  # How many times we've restarted
        self.max_training_restarts = 2  # Maximum restarts allowed
        self.last_restart_epoch = -1  # Prevent too-frequent restarts
        
        # Class distribution metadata (for classification tasks)
        self.class_distribution = None  # Will store {'train': {...}, 'val': {...}, 'total': {...}}
        
        # Optimal threshold for binary classification (computed during training, used during prediction)
        # When costs are specified: Uses cost-optimal threshold (Bayes-optimal decision rule)
        #   - Formula: threshold ≈ C_FP / (C_FP + C_FN)
        #   - Example: With C_FN=2.33 and C_FP=1.0, threshold ≈ 0.30 (not 0.50)
        #   - This minimizes expected cost for the given false positive and false negative costs
        # When costs not specified: Uses F1-optimal threshold (maximizes F1 score on validation set)
        # The threshold is saved from the best AUC epoch during training
        self.optimal_threshold = None
        self.optimal_threshold_history = []  # Track threshold over epochs: [(epoch, threshold, f1_score, auc), ...]
        self._pos_label = None  # Rare class label for binary classification (typically the minority class) - kept as _pos_label for pickle compatibility
        
        # Track best metrics for threshold selection (only save threshold when metrics improve)
        self._best_auc = -1.0  # Best AUC seen so far
        self._best_auc_epoch = -1  # Epoch with best AUC
        self._best_f1_at_best_auc = -1.0  # Best F1 score at the epoch with best AUC
        self._best_threshold_at_best_auc = None  # Threshold at the epoch with best AUC
        self._last_auc_improvement_epoch = -1  # Last epoch when AUC improved (for plateau detection)
        self.best_model_metrics: Optional[Dict[str, Any]] = None  # Metrics from the best model (used by feature effectiveness tracker)
        
        # Cost-based optimization parameters
        self.cost_false_positive = None  # Cost of false positive (set during prep_for_training)
        self.cost_false_negative = None  # Cost of false negative (set during prep_for_training)
        self._best_cost = float('inf')  # Best cost seen so far (for cost-based checkpoint selection)
        
        # Training optimizer and scheduler references (set during training)
        self._training_optimizer = None
        self._training_scheduler = None
        
        # Calibration parameters (automatically fitted after training)
        self.calibration_method = None  # 'temperature_scaling', 'platt', 'isotonic', or None
        self.calibration_temperature = None  # Temperature parameter (if method is 'temperature_scaling')
        self.calibration_platt_model = None  # Platt scaling model (if method is 'platt')
        self.calibration_isotonic_model = None  # Isotonic regression model (if method is 'isotonic')
        self.calibration_metrics = None  # Full calibration metrics including candidate_scores
        
        # Track if GPU restore failed due to OOM (initialized early to avoid access-before-definition)
        self._restore_failed_oom = False
        
        # Feature engineer for derived features (set during training, used during prediction)
        self.feature_engineer = None  # FeatureEngineer instance for training/inference consistency
        
        # Initialize customer quality trackers (one per epoch)
        # Format: {epoch: CustomerQualityTracker}
        from featrix.neural.customer_quality_tracker import CustomerQualityTracker
        self.customer_quality_trackers: Dict[int, CustomerQualityTracker] = {}
    
    def _validate_and_fix_before_save(self):
        """
        Validate and fix model integrity before saving.
        This prevents saving corrupted models with empty col_order or missing encoders.
        
        Returns:
            bool: True if model is valid (or was fixed), False if model is corrupted beyond repair
        """
        logger = logging.getLogger(__name__)
        
        try:
            if not hasattr(self, 'embedding_space') or self.embedding_space is None:
                logger.error("❌ CRITICAL: Missing embedding_space - cannot validate")
                return False
            
            es = self.embedding_space
            if not hasattr(es, 'encoder') or es.encoder is None:
                logger.error("❌ CRITICAL: Missing encoder - cannot validate")
                return False
            
            encoder = es.encoder
            if not hasattr(encoder, 'column_encoder') or encoder.column_encoder is None:
                logger.error("❌ CRITICAL: Missing column_encoder - cannot validate")
                return False
            
            column_encoder = encoder.column_encoder
            
            # Check and fix empty col_order before saving
            if not hasattr(column_encoder, 'col_order') or len(column_encoder.col_order) == 0:
                logger.warning(f"⚠️  CRITICAL: col_order is empty before saving - attempting recovery")
                
                # Try to recover from encoders (most reliable)
                if hasattr(column_encoder, 'encoders') and column_encoder.encoders and len(column_encoder.encoders) > 0:
                    encoder_keys = list(column_encoder.encoders.keys())
                    column_encoder.col_order = encoder_keys.copy()
                    logger.warning(f"   ✅ Recovered col_order from {len(encoder_keys)} encoders before saving")
                    return True
                
                # Try to recover from codecs
                if hasattr(column_encoder, 'col_codecs') and column_encoder.col_codecs:
                    codec_keys = list(column_encoder.col_codecs.keys())
                    column_encoder.col_order = codec_keys.copy()
                    logger.warning(f"   ✅ Recovered col_order from {len(codec_keys)} codecs before saving")
                    return True
                
                # Try to recover from embedding space codecs
                if hasattr(es, 'col_codecs') and es.col_codecs:
                    codec_keys = list(es.col_codecs.keys())
                    column_encoder.col_order = codec_keys.copy()
                    if not hasattr(column_encoder, 'col_codecs') or not column_encoder.col_codecs:
                        column_encoder.col_codecs = es.col_codecs
                    logger.warning(f"   ✅ Recovered col_order from embedding_space codecs before saving")
                    return True
                
                logger.error(f"   ❌ Cannot recover col_order - model is corrupted and will be saved in broken state")
                logger.error(f"   This model will fail when loaded. Check training process for issues.")
                return False
            
            # Check if encoders exist
            if not hasattr(column_encoder, 'encoders') or not column_encoder.encoders or len(column_encoder.encoders) == 0:
                logger.error(f"❌ CRITICAL: Missing or empty encoders - model is corrupted")
                logger.error(f"   Model will be saved but will not work when loaded")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"⚠️  Error validating model before save: {e}")
            logger.exception(e)
            # Continue anyway - better to save a potentially broken model than crash
            return True  # Return True to allow save to proceed
    
    def __getstate__(self):
        """
        Custom pickle state - save only essential data using state_dict for models.
        Excludes large data (dataframes, queries, targets, datasets) to keep checkpoints small.
        Similar to EmbeddingSpace encoder state_dict approach.
        
        CRITICAL: If the encoder was fine-tuned, we MUST save its state_dict!
        Otherwise all the fine-tuning work is lost when we reload.
        """
        # Large data attributes to exclude (should be loaded from original source, not checkpoint)
        EXCLUDE_LARGE_DATA = {
            'train_df', 'val_df', 'train_queries', 'val_queries', 
            'train_targets', 'val_targets', 'train_dataset', 'val_dataset',
        }
        
        # Attributes to assign directly (no deepcopy) - pickle handles them fine
        # deepcopy is wasteful: it creates a temp copy just to immediately pickle it
        ASSIGN_DIRECTLY = {'embedding_space'}
        
        # Model attributes that should be saved as state_dict
        MODEL_ATTRIBUTES = {'predictor_base', 'predictor'}
        
        state = {}
        saved_keys = []
        skipped_keys = []
        
        # CRITICAL: Save fine-tuned encoder if it was trained
        # Check if we have embedding_space and if encoder was fine-tuned
        if hasattr(self, 'embedding_space') and self.embedding_space is not None:
            if hasattr(self, '_encoder_was_finetuned') and self._encoder_was_finetuned:
                # Encoder was fine-tuned - MUST save its weights!
                try:
                    encoder_state = self.embedding_space.encoder.state_dict()
                    state['_finetuned_encoder_state_dict'] = encoder_state
                    logger.info(f"💾 Saving fine-tuned encoder state_dict ({len(encoder_state)} keys)")
                    saved_keys.append("_finetuned_encoder_state_dict")
                except Exception as e:
                    logger.error(f"❌ CRITICAL: Failed to save fine-tuned encoder: {e}")
                    logger.error(f"   Fine-tuned encoder weights will be LOST!")
        
        for key, value in self.__dict__.items():
            # Skip None values
            if value is None:
                state[key] = None
                continue
            
            # Skip large data - these should not be in checkpoints
            if key in EXCLUDE_LARGE_DATA:
                logger.debug(f"Skipping {key} in checkpoint (large data - should be loaded separately)")
                skipped_keys.append(key)
                continue
            
            # Assign directly without deepcopy - pickle handles serialization
            # deepcopy is wasteful: triggers __getstate__/__setstate__ on a temp copy
            if key in ASSIGN_DIRECTLY:
                state[key] = value
                saved_keys.append(f"{key} (direct, no deepcopy)")
                continue

            # Save models as state_dict (PyTorch-approved method)
            # BUT: For predictor_base in full pickle files (with embedding_space), save as object
            # to avoid reconstruction issues during unpickling
            if key in MODEL_ATTRIBUTES and value is not None:
                # For predictor_base, if we have embedding_space (full pickle, not checkpoint),
                # save as object to avoid reconstruction issues
                # NOTE: We used to try deepcopy of predictor_base after moving to CPU, but
                # value.cpu() modifies the model IN PLACE, which breaks training after
                # checkpoint save (predictor ends up with mixed CPU/GPU layers).
                # Now we save ALL models as state_dict which is the PyTorch-approved method.
                # This also avoids GPU OOM during pickle since state_dict uses less memory.
                
                # For other cases (checkpoints, or predictor), save as state_dict
                if hasattr(value, 'state_dict'):
                    try:
                        state[key] = {
                            '__model_state_dict__': value.state_dict(),
                            '__model_class__': value.__class__.__name__
                        }
                        logger.debug(f"Saving {key} as state_dict()")
                        saved_keys.append(f"{key} (state_dict)")
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to save {key} as state_dict(): {e}")
                        # Fall through to try other methods
                else:
                    logger.warning(f"{key} is not a PyTorch model, cannot save as state_dict")
                    # Fall through to try normal copy
            
            # For other attributes, try to copy (but skip if it's too large)
            try:
                # Check if it's a pandas DataFrame or similar large object
                if hasattr(value, '__class__'):
                    class_name = value.__class__.__name__
                    if 'DataFrame' in class_name or 'Series' in class_name:
                        logger.debug(f"Skipping {key} (DataFrame/Series - should not be in checkpoint)")
                        continue
                
                state[key] = copy.deepcopy(value)
            except (TypeError, AttributeError, NotImplementedError) as e:
                # For models that failed deepcopy, try state_dict
                if hasattr(value, 'state_dict'):
                    try:
                        state[key] = {
                            '__model_state_dict__': value.state_dict(),
                            '__model_class__': value.__class__.__name__
                        }
                        logger.debug(f"Saving {key} as state_dict() (deepcopy failed: {str(e)[:100]})")
                        continue
                    except Exception as save_err:
                        logger.warning(f"Failed to save {key} as state_dict(): {save_err}")
                
                # For other errors, try shallow copy as fallback
                try:
                    state[key] = copy.copy(value)
                except (TypeError, AttributeError, NotImplementedError):
                    logger.warning(f"Could not pickle {key}, excluding from state: {e}")
                    # Skip this attribute - it will be missing after unpickling
                    continue
        
        return state
    
    def __setstate__(self, state):
        """
        Custom unpickle state - restore models from state_dict.
        Models (predictor_base, predictor) are saved as state_dict to keep checkpoints small.
        Embedding_space and large data (dataframes, queries, targets) are excluded and should be loaded separately.
        """
        import torch.nn as nn
        
        # Store pending state_dicts for models that need to be restored
        pending_state_dicts = {}
        
        # First, restore all normal attributes (excluding models saved as state_dict)
        # Also store model class names for reconstruction if needed
        model_class_names = {}
        for key, value in state.items():
            # Check if this is a model saved as state_dict()
            if isinstance(value, dict) and '__model_state_dict__' in value:
                # Store the state_dict temporarily - we'll load it after all attributes are set
                pending_state_dicts[key] = value['__model_state_dict__']
                # Also store the model class name for potential reconstruction
                if '__model_class__' in value:
                    model_class_names[key] = value['__model_class__']
                logger.debug(f"Storing state_dict for {key} (will load after attributes restored)")
                continue
            elif key == 'embedding_space':
                # embedding_space might be excluded from checkpoints (loaded separately)
                # but for full pickle files, it should be restored
                # Check if it's actually None or missing - if it's a real object, restore it
                if value is not None:
                    # It's a real embedding_space object - restore it
                    self.__dict__[key] = value
                    logger.debug(f"Restored embedding_space from pickle state")
                else:
                    # It's None or excluded - will be set by caller (for checkpoint loading)
                    logger.debug(f"Skipping embedding_space in __setstate__ (None/excluded - will be loaded separately)")
                continue
            else:
                # Normal attribute - just set it
                self.__dict__[key] = value
        
        # Now restore models from state_dict() if they exist
        for key, state_dict in pending_state_dicts.items():
            if key in self.__dict__ and self.__dict__[key] is not None:
                if hasattr(self.__dict__[key], 'load_state_dict'):
                    try:
                        self.__dict__[key].load_state_dict(state_dict)
                        logger.info(f"✅ Restored {key} from state_dict()")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to restore {key} from state_dict(): {e}")
                        logger.debug(traceback.format_exc())
                        # Model object exists but couldn't load state - keep existing model
                else:
                    logger.warning(f"⚠️  {key} exists but doesn't have load_state_dict method")
            else:
                # Model doesn't exist yet - store state_dict for later loading
                # This can happen if embedding_space is None and predictor_base wasn't created
                # OR if __init__ wasn't called (during unpickling, __init__ is NOT called)
                if not hasattr(self, '_pending_state_dicts'):
                    self._pending_state_dicts = {}
                self._pending_state_dicts[key] = state_dict
                # Also store model class name if available
                if key in model_class_names:
                    if not hasattr(self, '_pending_model_classes'):
                        self._pending_model_classes = {}
                    self._pending_model_classes[key] = model_class_names[key]
                logger.info(f"📦 Stored state_dict for {key} (model not yet created, will load when available)")
                
                # CRITICAL: If predictor_base is missing and we have its state_dict, we can't reconstruct it
                # without knowing the architecture. But we can at least set it to None so _ensure_predictor_available
                # knows to try reconstruction from predictor state_dict instead.
                if key == 'predictor_base':
                    # Set predictor_base to None so we know it needs reconstruction
                    self.predictor_base = None
                    logger.warning("⚠️  predictor_base state_dict found but model object missing - will need to reconstruct from predictor state_dict")
        
        # CRITICAL: Restore fine-tuned encoder if it was saved
        # NOTE: __init__ is NOT called during unpickling, so we MUST load the encoder here!
        if '_finetuned_encoder_state_dict' in state:
            encoder_state = state['_finetuned_encoder_state_dict']
            # Check if embedding_space is already available (it should be if this is a full pickle)
            if hasattr(self, 'embedding_space') and self.embedding_space is not None:
                if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                    encoder = self.embedding_space.encoder
                    column_encoder = encoder.column_encoder
                    
                    # STEP 1: Recover col_order from state dict keys if needed
                    # This fixes the case where col_order is empty but the state dict has encoder keys
                    if hasattr(column_encoder, 'col_order') and (not column_encoder.col_order or len(column_encoder.col_order) == 0):
                        logger.warning(f"⚠️  col_order is empty before loading encoder state dict - recovering from state dict keys")
                        # Extract column names from state dict keys like "column_encoder.encoders.<column_name>.*"
                        column_names = set()
                        for key in encoder_state.keys():
                            if key.startswith('column_encoder.encoders.'):
                                parts = key.split('.')
                                if len(parts) >= 3:
                                    column_name = parts[2]
                                    column_names.add(column_name)
                        
                        if column_names:
                            recovered_col_order = sorted(list(column_names))
                            column_encoder.col_order = recovered_col_order
                            logger.warning(f"   ✅ Recovered col_order from {len(recovered_col_order)} columns in state dict")
                        else:
                            logger.error(f"   ❌ Could not recover col_order from state dict keys")
                    
                    # STEP 2: ALWAYS fix pos_embedding shape before loading state dict
                    # This is CRITICAL - even if col_order was already recovered by ColumnEncoders.__setstate__,
                    # the pos_embedding might still have the wrong shape (e.g., [0, 256] instead of [148, 256])
                    import torch
                    import torch.nn as nn
                    
                    effective_col_count = len(column_encoder.col_order) if hasattr(column_encoder, 'col_order') and column_encoder.col_order else 0
                    logger.info(f"🔧 Fixing pos_embedding shape if needed (col_order has {effective_col_count} columns)")
                    
                    if effective_col_count > 0:
                        if hasattr(encoder, 'joint_encoder') and encoder.joint_encoder is not None:
                            if hasattr(encoder.joint_encoder, 'col_encoder') and encoder.joint_encoder.col_encoder is not None:
                                if hasattr(encoder.joint_encoder.col_encoder, 'pos_embedding') and encoder.joint_encoder.col_encoder.pos_embedding is not None:
                                    current_shape = encoder.joint_encoder.col_encoder.pos_embedding.shape
                                    expected_shape = (effective_col_count, current_shape[1])
                                    logger.info(f"   📏 pos_embedding current shape: {current_shape}, expected: {expected_shape}")
                                    if current_shape[0] != expected_shape[0]:
                                        logger.warning(f"   ⚠️  FIXING pos_embedding shape from {current_shape} to {expected_shape}")
                                        device = encoder.joint_encoder.col_encoder.pos_embedding.device
                                        dtype = encoder.joint_encoder.col_encoder.pos_embedding.dtype
                                        encoder.joint_encoder.col_encoder.pos_embedding = nn.Parameter(
                                            torch.zeros(expected_shape[0], expected_shape[1], device=device, dtype=dtype)
                                        )
                                        logger.warning(f"   ✅ Reinitialized pos_embedding with shape {expected_shape}")
                                    else:
                                        logger.info(f"   ✅ pos_embedding shape is already correct")
                                else:
                                    logger.warning(f"   ⚠️  pos_embedding is None or missing")
                            else:
                                logger.warning(f"   ⚠️  col_encoder is None or missing")
                        else:
                            logger.warning(f"   ⚠️  joint_encoder is None or missing")
                    else:
                        logger.error(f"   ❌ Cannot fix pos_embedding - col_order is empty!")
                    
                    # STEP 3: Load the state dict
                    try:
                        self.embedding_space.encoder.load_state_dict(encoder_state, strict=False)
                        logger.info(f"✅ Loaded fine-tuned encoder state_dict ({len(encoder_state)} keys) in __setstate__")
                    except Exception as e:
                        logger.error(f"❌ CRITICAL: Failed to load fine-tuned encoder in __setstate__: {e}")
                        logger.error(traceback.format_exc())
                        # Store for later as fallback
                        if not hasattr(self, '_pending_state_dicts'):
                            self._pending_state_dicts = {}
                        self._pending_state_dicts['_finetuned_encoder_state_dict'] = encoder_state
                else:
                    logger.warning(f"⚠️  embedding_space exists but encoder is None - storing fine-tuned encoder for later")
                    if not hasattr(self, '_pending_state_dicts'):
                        self._pending_state_dicts = {}
                    self._pending_state_dicts['_finetuned_encoder_state_dict'] = encoder_state
            else:
                # embedding_space not available yet - store for loading later
                logger.info(f"💾 Found fine-tuned encoder state_dict - storing for when embedding_space is available")
                if not hasattr(self, '_pending_state_dicts'):
                    self._pending_state_dicts = {}
                self._pending_state_dicts['_finetuned_encoder_state_dict'] = encoder_state
        
        # BACKWARD COMPATIBILITY: Set defaults for new attributes if missing from old pickles
        if 'optimal_threshold' not in state:
            self.optimal_threshold = None
        if 'optimal_threshold_history' not in state:
            self.optimal_threshold_history = []
        if '_pos_label' not in state:
            self._pos_label = None
        if '_encoder_was_finetuned' not in state:
            self._encoder_was_finetuned = False
        if '_best_auc' not in state:
            self._best_auc = -1.0
        if '_best_auc_epoch' not in state:
            self._best_auc_epoch = -1
        if '_best_f1_at_best_auc' not in state:
            self._best_f1_at_best_auc = -1.0
        if '_best_threshold_at_best_auc' not in state:
            self._best_threshold_at_best_auc = None
        if '_last_auc_improvement_epoch' not in state:
            self._last_auc_improvement_epoch = -1
    
    def _log(self, level, msg, *args, **kwargs):
        """Log with optional run identifier prefix."""
        if self.run_identifier:
            msg = f"{self.run_identifier} {msg}"
        getattr(logger, level)(msg, *args, **kwargs)
    
    def _get_log_prefix(self, epoch_idx=None):
        """Generate consistent log prefix with epoch and target information."""
        parts = []
        # Don't include epoch in log_prefix since it's already in the logger [e=XXX] tag
        # if epoch_idx is not None:
        #     parts.append(f"epoch={epoch_idx}")
        if self.target_col_name:
            parts.append(f"[t={self.target_col_name}]")
        return "".join(parts) + (" " if parts else "")

    def record_training_warning(self, warning_type, epoch, details=None):
        """
        Record a training warning for later retrieval.
        
        Args:
            warning_type: Type of warning (e.g., "SINGLE_CLASS_BIAS", "LOW_AUC", etc.)
            epoch: Epoch number where warning occurred
            details: Optional dict with additional details about the warning
        """
        if warning_type not in self.training_warnings:
            self.training_warnings[warning_type] = {
                "epochs": [],
                "details": [],
                "first_seen": epoch,
                "last_seen": epoch,
                "count": 0
            }
        
        self.training_warnings[warning_type]["epochs"].append(epoch)
        self.training_warnings[warning_type]["details"].append(details or {})
        self.training_warnings[warning_type]["last_seen"] = epoch
        self.training_warnings[warning_type]["count"] += 1
    
    def adjust_focal_loss_for_bias(self, pred_counts, y_true_counts, epoch_idx):
        """
        Adaptively adjust FocalLoss parameters when detecting class prediction bias.
        
        This handles both over-correction (reverse bias) and under-learning scenarios:
        - REVERSE BIAS: Model predicts minority class too frequently → reduce gamma
        - UNDER-LEARNING: Model predicts minority class too rarely → increase gamma
        
        Args:
            pred_counts: dict of predicted class counts
            y_true_counts: dict of ground truth class counts  
            epoch_idx: current epoch number
            
        Returns:
            bool: True if adjustment was made, False otherwise
        """
        if not self.adaptive_loss_enabled:
            return False
        
        # Only adjust if we're using FocalLoss
        if not isinstance(self.target_codec.loss_fn, FocalLoss):
            return False
        
        # Prevent adjustments too frequently (need at least 5 epochs between adjustments)
        if epoch_idx - self.last_loss_adjustment_epoch < 5:
            return False
        
        # Max 5 adjustments per training run (increased from 3 to allow bidirectional adjustments)
        if self.loss_adjustment_count >= 5:
            return False
        
        # Calculate prediction distribution
        total_preds = sum(pred_counts.values())
        if total_preds == 0:
            return False
        pred_pcts = {k: (v / total_preds * 100) for k, v in pred_counts.items()}
        
        # Calculate ground truth distribution
        total_true = sum(y_true_counts.values())
        if total_true == 0:
            return False
        true_pcts = {k: (v / total_true * 100) for k, v in y_true_counts.items()}
        
        # Identify minority and majority classes in ground truth
        minority_class = min(true_pcts, key=true_pcts.get)
        majority_class = max(true_pcts, key=true_pcts.get)
        
        minority_true_pct = true_pcts[minority_class]
        minority_pred_pct = pred_pcts.get(minority_class, 0)
        majority_true_pct = true_pcts[majority_class]
        majority_pred_pct = pred_pcts.get(majority_class, 0)
        
        # Calculate bias ratios
        reverse_bias_ratio = minority_pred_pct / max(minority_true_pct, 0.1)  # Minority over-predicted
        under_learning_ratio = minority_true_pct / max(minority_pred_pct, 0.1)  # Minority under-predicted
        
        log_prefix = self._get_log_prefix(epoch_idx)
        logger.info(f"{log_prefix}📊 Bias Analysis:")
        logger.info(f"{log_prefix}   Minority class '{minority_class}': {minority_true_pct:.1f}% in truth, {minority_pred_pct:.1f}% in predictions")
        logger.info(f"{log_prefix}   Majority class '{majority_class}': {majority_true_pct:.1f}% in truth, {majority_pred_pct:.1f}% in predictions")
        logger.info(f"{log_prefix}   Reverse bias ratio: {reverse_bias_ratio:.2f}x (>2.0 suggests over-correction)")
        logger.info(f"{log_prefix}   Under-learning ratio: {under_learning_ratio:.2f}x (>2.0 suggests under-learning)")
        
        current_loss = self.target_codec.loss_fn
        old_gamma = current_loss.gamma
        old_min_weight = current_loss.min_weight
        adjustment_made = False
        adjustment_type = None
        adjustment_details = {}
        
        # CASE 1: REVERSE BIAS - Model over-predicts minority class
        # Trigger if: minority predicted 2x+ more than ground truth AND minority >80% of predictions
        if reverse_bias_ratio > 2.0 and minority_pred_pct > 80:
            adjustment_type = "REVERSE_BIAS"
            
            # REDUCE gamma: Less focus on hard examples (minority class)
            # gamma=2.0 → 1.5 → 1.0 → 0.5 (approaches standard cross-entropy)
            new_gamma = max(0.5, old_gamma * 0.75)
            
            # INCREASE min_weight: Give more credit to easy examples (majority class)
            # min_weight=0.1 → 0.2 → 0.3 → 0.4 (up to 0.4 max)
            new_min_weight = min(0.4, old_min_weight + 0.1)
            
            logger.warning(f"{log_prefix}" + "=" * 80)
            logger.warning(f"{log_prefix}🔧 ADAPTIVE LOSS ADJUSTMENT #{self.loss_adjustment_count + 1}")
            logger.warning(f"{log_prefix}" + "=" * 80)
            logger.warning(f"{log_prefix}⚠️  REVERSE BIAS DETECTED: Model over-predicts minority class")
            logger.warning(f"{log_prefix}   Minority class '{minority_class}' predicted {reverse_bias_ratio:.2f}x more than ground truth")
            logger.warning(f"{log_prefix}   Adjusting FocalLoss to reduce class weight effect:")
            logger.warning(f"{log_prefix}   • gamma: {old_gamma:.2f} → {new_gamma:.2f} (less focus on hard/minority examples)")
            logger.warning(f"{log_prefix}   • min_weight: {old_min_weight:.2f} → {new_min_weight:.2f} (more credit to easy/majority examples)")
            logger.warning(f"{log_prefix}" + "=" * 80)
            
            adjustment_details = {
                "reverse_bias_ratio": float(reverse_bias_ratio),
                "minority_class": str(minority_class),
                "minority_true_pct": float(minority_true_pct),
                "minority_pred_pct": float(minority_pred_pct),
            }
            adjustment_made = True
        
        # CASE 2: UNDER-LEARNING - Model under-predicts minority class
        # Trigger if: minority predicted <50% of ground truth AND minority <20% of predictions
        # AND we haven't already reduced gamma too much (gamma > 1.0)
        elif under_learning_ratio > 2.0 and minority_pred_pct < 20 and old_gamma < 3.5:
            adjustment_type = "UNDER_LEARNING"
            
            # INCREASE gamma: More focus on hard examples (minority class)
            # gamma=2.0 → 2.5 → 3.0 → 3.5 (increases focus on minority class)
            new_gamma = min(3.5, old_gamma * 1.25)
            
            # DECREASE min_weight: Give less credit to easy examples (majority class)
            # min_weight=0.1 → 0.05 (down to 0.05 min) - but only if it's above 0.1
            new_min_weight = max(0.05, old_min_weight - 0.05) if old_min_weight > 0.1 else old_min_weight
            
            logger.warning(f"{log_prefix}" + "=" * 80)
            logger.warning(f"{log_prefix}🔧 ADAPTIVE LOSS ADJUSTMENT #{self.loss_adjustment_count + 1}")
            logger.warning(f"{log_prefix}" + "=" * 80)
            logger.warning(f"{log_prefix}⚠️  UNDER-LEARNING DETECTED: Model under-predicts minority class")
            logger.warning(f"{log_prefix}   Minority class '{minority_class}' predicted {under_learning_ratio:.2f}x less than ground truth")
            logger.warning(f"{log_prefix}   Adjusting FocalLoss to increase focus on minority class:")
            logger.warning(f"{log_prefix}   • gamma: {old_gamma:.2f} → {new_gamma:.2f} (more focus on hard/minority examples)")
            logger.warning(f"{log_prefix}   • min_weight: {old_min_weight:.2f} → {new_min_weight:.2f} (less credit to easy/majority examples)")
            logger.warning(f"{log_prefix}" + "=" * 80)
            
            adjustment_details = {
                "under_learning_ratio": float(under_learning_ratio),
                "minority_class": str(minority_class),
                "minority_true_pct": float(minority_true_pct),
                "minority_pred_pct": float(minority_pred_pct),
            }
            adjustment_made = True
        
        if adjustment_made:
            # Create new FocalLoss with adjusted parameters
            # Keep the same alpha (class weights) but adjust gamma and min_weight
            new_loss = FocalLoss(
                alpha=current_loss.alpha,
                gamma=new_gamma,
                min_weight=new_min_weight
            )
            
            # Move to same device as current loss
            if current_loss.alpha is not None:
                new_loss.alpha = current_loss.alpha.to(current_loss.alpha.device)
            
            # Update the loss function
            self.target_codec.loss_fn = new_loss
            
            # Track the adjustment
            self.focal_gamma_history.append((epoch_idx, old_gamma, new_gamma))
            self.focal_min_weight_history.append((epoch_idx, old_min_weight, new_min_weight))
            self.loss_adjustment_count += 1
            self.last_loss_adjustment_epoch = epoch_idx
            
            # LOG CORRECTIVE ACTION (like ES training does)
            corrective_action = {
                "epoch": epoch_idx,
                "trigger": adjustment_type,
                "action_type": "FOCAL_LOSS_ADJUSTMENT",
                "details": {
                    **adjustment_details,
                    "gamma_old": float(old_gamma),
                    "gamma_new": float(new_gamma),
                    "min_weight_old": float(old_min_weight),
                    "min_weight_new": float(new_min_weight),
                    "adjustment_number": self.loss_adjustment_count,
                    "pred_distribution": {str(k): int(v) for k, v in pred_counts.items()},
                    "true_distribution": {str(k): int(v) for k, v in y_true_counts.items()}
                }
            }
            self._corrective_actions.append(corrective_action)
            
            # Add to training timeline
            timeline_entry = {
                "epoch": epoch_idx,
                "event_type": "hyperparameter_change",
                "hyperparameter": "focal_loss",
                "changes": {
                    "gamma": {"old": float(old_gamma), "new": float(new_gamma)},
                    "min_weight": {"old": float(old_min_weight), "new": float(new_min_weight)}
                },
                "trigger": adjustment_type,
                "details": adjustment_details
            }
            if hasattr(self, '_training_timeline'):
                self._training_timeline.append(timeline_entry)
            
            logger.info(f"{log_prefix}✅ FocalLoss adjusted successfully. Will monitor for {5} more epochs before next adjustment.")
            
            return True
        
        return False
        
    def check_for_dead_gradients_and_raise(self, unclipped_norm, epoch_idx, current_lr):
        """
        Check for dead gradients and raise FeatrixRestartTrainingException if detected.
        
        This allows the training loop to catch the exception and restart training
        with modified parameters (boosted LR, reset optimizer state, etc.)
        
        Args:
            unclipped_norm: Unclipped gradient norm
            epoch_idx: Current epoch number
            current_lr: Current learning rate
            
        Raises:
            FeatrixRestartTrainingException: When dead gradients detected and restart needed
        """
        log_prefix = self._get_log_prefix(epoch_idx)
        
        # Check if gradients are dead
        if unclipped_norm >= self.dead_gradient_threshold:
            # Gradients are alive, clear history if any
            if self.dead_gradient_epochs:
                logger.info(f"{log_prefix}✅ Gradients recovered! Clearing dead gradient history.")
                self.dead_gradient_epochs = []
                # Track warning resolution
                self._track_warning_in_timeline(
                    epoch_idx=epoch_idx,
                    warning_type="DEAD_GRADIENTS",
                    is_active=False,
                    details={
                        "gradient_norm": float(unclipped_norm),
                        "lr": current_lr,
                        "recovered": True
                    }
                )
            return
        
        # Track dead gradient epochs
        was_dead = len(self.dead_gradient_epochs) > 0
        self.dead_gradient_epochs.append(epoch_idx)
        logger.warning(f"{log_prefix}⚠️  Dead gradient detected (norm={unclipped_norm:.6e})")
        
        # Track warning start if this is the first detection
        if not was_dead:
            self._track_warning_in_timeline(
                epoch_idx=epoch_idx,
                warning_type="DEAD_GRADIENTS",
                is_active=True,
                details={
                    "gradient_norm": float(unclipped_norm),
                    "lr": current_lr,
                    "threshold": self.dead_gradient_threshold
                }
            )
        
        # Check if we have consecutive dead gradients (3+ in a row = trigger restart)
        if len(self.dead_gradient_epochs) < 3:
            logger.info(f"{log_prefix}   Dead gradient count: {len(self.dead_gradient_epochs)}/3 (need 3 consecutive to restart)")
            return
        
        recent_dead = self.dead_gradient_epochs[-3:]
        # Check if last 3 dead gradient epochs are consecutive (within 2 epochs)
        if recent_dead[-1] - recent_dead[0] > 2:
            logger.info(f"{log_prefix}   Last 3 dead gradients not consecutive: {recent_dead} (skipping restart)")
            return
        
        # Check restart limits
        if self.training_restart_count >= self.max_training_restarts:
            logger.error(f"{log_prefix}💀 Dead gradients detected but max restarts ({self.max_training_restarts}) reached - cannot restart")
            logger.error(f"{log_prefix}   Training will continue with dead gradients (likely to fail)")
            return
        
        # Need cooldown between restarts (skip cooldown if never restarted before)
        if self.last_restart_epoch >= 0 and epoch_idx - self.last_restart_epoch < 5:
            logger.info(f"{log_prefix}   Too soon since last restart (epoch {self.last_restart_epoch}) - need 5 epoch cooldown")
            return
        
        # All conditions met - prepare restart!
        logger.error(f"{log_prefix}💀 DEAD GRADIENTS: {len(self.dead_gradient_epochs)} total, last 3 consecutive {recent_dead}")
        logger.error(f"{log_prefix}   🔄 Attempting to get restart recommendation from featrix-monitor...")
        
        # Query monitor for restart recommendation
        restart_recommendation = None
        try:
            from lib.training_monitor import get_restart_recommendation
            
            context = {
                "current_lr": float(current_lr),
                "gradient_norm": float(unclipped_norm),
                "epoch": epoch_idx,
                "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                "consecutive_dead_epochs": len(recent_dead),
                "total_dead_epochs": len(self.dead_gradient_epochs),
                "dead_epoch_history": list(self.dead_gradient_epochs[-10:]),
                "previous_restarts": self.training_restart_count,
                "hostname": socket.gethostname(),
            }
            logger.info(f"{log_prefix}   Querying monitor with context: {context}")
            logger.info(f"{log_prefix}   Dataset hash: {getattr(self, '_dataset_hash', None)}")
            
            restart_recommendation = get_restart_recommendation(
                session_id=getattr(self, 'job_id', 'unknown'),
                anomaly_type="dead_gradients",
                context=context,
                dataset_hash=getattr(self, '_dataset_hash', None)  # TOP-LEVEL parameter
            )
        except Exception as e:
            logger.warning(f"{log_prefix}⚠️  Failed to get restart recommendation from monitor: {e}")
        
        # Create restart configuration (use monitor recommendation if available, otherwise fallback to defaults)
        if restart_recommendation:
            logger.info(f"{log_prefix}✅ Using monitor-recommended restart config")
            logger.info(f"{log_prefix}   Confidence: {restart_recommendation.get('confidence', 0):.2f}")
            logger.info(f"{log_prefix}   Full recommendation received: {restart_recommendation}")
            restart_config = RestartConfig(
                reason="DEAD_GRADIENTS",
                epoch_detected=epoch_idx,
                lr_multiplier=restart_recommendation.get('lr_multiplier', 0.5),
                max_lr=restart_recommendation.get('max_lr', 0.01),
                reset_optimizer_state=restart_recommendation.get('reset_optimizer_state', True),
                reset_scheduler=restart_recommendation.get('reset_scheduler', False),
                load_best_checkpoint=restart_recommendation.get('load_best_checkpoint', True),
                additional_epochs=restart_recommendation.get('additional_epochs', None),
                metadata={
                    "dead_gradient_epochs": list(self.dead_gradient_epochs[-5:]),
                    "gradient_norm": float(unclipped_norm),
                    "current_lr": float(current_lr),
                    "restart_number": self.training_restart_count + 1,
                    "monitor_recommendation": restart_recommendation,  # Include full recommendation
                }
            )
            logger.info(f"{log_prefix}   Applied config: lr_multiplier={restart_config.lr_multiplier}, max_lr={restart_config.max_lr}, reset_optimizer={restart_config.reset_optimizer_state}")
        else:
            logger.info(f"{log_prefix}ℹ️  No monitor recommendation, using default restart config")
            restart_config = RestartConfig(
                reason="DEAD_GRADIENTS",
                epoch_detected=epoch_idx,
                lr_multiplier=0.5,  # REDUCE LR on dead gradients - high LR likely caused the problem
                max_lr=0.01,
                reset_optimizer_state=True,
                reset_scheduler=False,
                load_best_checkpoint=True,  # CRITICAL: Reload best checkpoint - current weights may be corrupted with NaN!
                additional_epochs=None,  # Don't extend training
                metadata={
                    "dead_gradient_epochs": list(self.dead_gradient_epochs[-5:]),
                    "gradient_norm": float(unclipped_norm),
                    "current_lr": float(current_lr),
                    "restart_number": self.training_restart_count + 1
                }
            )
            logger.info(f"{log_prefix}   Default config: lr_multiplier=0.5, max_lr=0.01, reset_optimizer=True")
        
        # Report to featrix-monitor BEFORE raising exception
        try:
            from lib.training_monitor import post_training_anomaly
            post_training_anomaly(
                session_id=getattr(self, 'job_id', 'unknown'),
                anomaly_type="dead_gradients",
                epoch=epoch_idx,
                dataset_hash=getattr(self, '_dataset_hash', None),  # TOP-LEVEL parameter
                details={
                    "collapse_type": "dead_gradients",
                    "gradient_norm": float(unclipped_norm),
                    "current_lr": float(current_lr),
                    "consecutive_dead_epochs": len(recent_dead),
                    "total_dead_epochs": len(self.dead_gradient_epochs),
                    "dead_epoch_history": list(self.dead_gradient_epochs[-10:]),  # Last 10
                    "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                    # Restart config details (complete config that will be applied)
                    "restart_config": restart_config.to_dict(),
                }
            )
        except Exception as monitor_err:
            logger.warning(f"⚠️  Failed to report dead gradients to monitor: {monitor_err}")
        
        # Raise exception - training loop will catch and restart
        raise FeatrixRestartTrainingException(
            f"Dead gradients detected at epoch {epoch_idx} ({len(recent_dead)} consecutive)",
            restart_config=restart_config
        )
    
    def _track_warning_in_timeline(self, epoch_idx, warning_type, is_active, details=None):
        """
        Track warnings in timeline - add entries when warnings start/stop.
        
        Args:
            epoch_idx: Current epoch number
            warning_type: Type of warning (e.g., 'DEAD_GRADIENTS', 'NO_LEARNING')
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
    
    def save_training_timeline(self, output_dir=None, current_epoch=None, total_epochs=None):
        """
        Save training timeline and corrective actions to JSON file (like ES training).
        
        Args:
            output_dir: Directory to save timeline JSON (default: self._output_dir)
            current_epoch: Current epoch number for logging
            total_epochs: Total number of epochs
        """
        import json
        import pandas as pd
        
        if output_dir is None:
            output_dir = self._output_dir
        
        if output_dir is None:
            # No output directory set, skip saving
            return
        
        try:
            # Build metadata
            metadata = {
                "total_epochs": total_epochs,
                "adaptive_loss_enabled": self.adaptive_loss_enabled,
                "loss_adjustments": self.loss_adjustment_count,
                "training_restarts": self.training_restart_count,
                "dead_gradient_threshold": self.dead_gradient_threshold,
                "target_col_name": self.target_col_name,
                "target_col_type": str(self.target_col_type) if self.target_col_type else None
            }
            
            # Add detailed target column distribution information
            if self.train_df is not None and self.target_col_name and self.target_col_name in self.train_df.columns:
                target_col = self.train_df[self.target_col_name]
                
                # Common info for both set and scalar
                total_rows = len(self.train_df)
                notna_count = target_col.notna().sum()
                notna_pct = (notna_count / total_rows * 100) if total_rows > 0 else 0.0
                null_count = target_col.isnull().sum()
                null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0.0
                
                metadata["target_column_distribution"] = {
                    "total_rows": int(total_rows),
                    "notna_count": int(notna_count),
                    "notna_percentage": float(notna_pct),
                    "null_count": int(null_count),
                    "null_percentage": float(null_pct)
                }
                
                # For set targets: add value_counts() info
                if self.target_col_type == "set" or (hasattr(self, 'is_target_scalar') and not self.is_target_scalar):
                    value_counts = target_col.value_counts()
                    # Convert to dict with string keys for JSON serialization
                    value_counts_dict = {}
                    for label, count in value_counts.items():
                        # Convert label to string for JSON compatibility
                        label_str = str(label)
                        value_counts_dict[label_str] = {
                            "count": int(count),
                            "percentage": float((count / notna_count * 100) if notna_count > 0 else 0.0)
                        }
                    
                    metadata["target_column_distribution"]["value_counts"] = value_counts_dict
                    metadata["target_column_distribution"]["unique_values"] = int(target_col.nunique())
                
                # For scalar targets: add distribution statistics
                elif self.target_col_type == "scalar" or (hasattr(self, 'is_target_scalar') and self.is_target_scalar):
                    # Get non-null values for statistics
                    non_null_values = target_col.dropna()
                    if len(non_null_values) > 0:
                        metadata["target_column_distribution"]["statistics"] = {
                            "mean": float(non_null_values.mean()),
                            "std": float(non_null_values.std()) if len(non_null_values) > 1 else 0.0,
                            "min": float(non_null_values.min()),
                            "max": float(non_null_values.max()),
                            "median": float(non_null_values.median()),
                            "q25": float(non_null_values.quantile(0.25)),
                            "q75": float(non_null_values.quantile(0.75)),
                            "unique_values": int(non_null_values.nunique())
                        }
                    else:
                        metadata["target_column_distribution"]["statistics"] = {
                            "mean": None,
                            "std": None,
                            "min": None,
                            "max": None,
                            "median": None,
                            "q25": None,
                            "q75": None,
                            "unique_values": 0
                        }
            
            timeline_path = os.path.join(output_dir, "sp_training_timeline.json")
            with open(timeline_path, 'w') as f:
                json.dump({
                    "timeline": self._training_timeline,
                    "corrective_actions": self._corrective_actions,
                    "metadata": metadata
                }, f, indent=2)
            
            # Generate/update timeline plot for real-time monitoring
            try:
                from featrix.neural.charting import plot_sp_training_timeline
                # Get optimizer params from training info if available
                opt_params = None
                if hasattr(self, 'training_info') and self.training_info:
                    # Try to get from first entry
                    first_entry = self.training_info[0] if isinstance(self.training_info, list) and self.training_info else None
                    if first_entry and isinstance(first_entry, dict):
                        hyperparams = first_entry.get('hyperparameters', {})
                        if hyperparams:
                            opt_params = {'lr': hyperparams.get('learning_rate')}
                
                plot_sp_training_timeline(
                    training_timeline=self._training_timeline,
                    output_dir=output_dir,
                    n_epochs=total_epochs,
                    optimizer_params=opt_params,
                    training_info=getattr(self, 'training_info', None)
                )
            except Exception as plot_error:
                # Don't fail training if plot generation fails
                logger.debug(f"Failed to update SP timeline plot: {plot_error}")
            
            if current_epoch is not None:
                logger.debug(f"💾 SP training timeline saved to {timeline_path} (epoch {current_epoch})")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save SP training timeline: {e}")
            logger.debug(traceback.format_exc())
        
    def get_model_warnings(self, include_epoch_details=False):
        """
        Get all training warnings that were recorded during model training.
        
        Args:
            include_epoch_details: If True, includes the full list of epochs and details.
                                  If False, returns a summary.
        
        Returns:
            dict: Dictionary of warnings with their metadata
        """
        if not self.training_warnings:
            return {}
        
        if include_epoch_details:
            return {
                "warnings": self.training_warnings,
                "best_epoch_warnings": self.best_epoch_warnings
            }
        else:
            # Return summary without full epoch lists
            summary = {}
            for warning_type, data in self.training_warnings.items():
                summary[warning_type] = {
                    "first_seen": data["first_seen"],
                    "last_seen": data["last_seen"],
                    "count": data["count"],
                    "occurred_at_best_epoch": warning_type in [w["type"] for w in self.best_epoch_warnings]
                }
            return summary
    
    def has_warnings(self):
        """Check if any warnings were recorded during training."""
        return len(self.training_warnings) > 0 or self.has_training_quality_issues()
    
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
    
    def has_training_quality_issues(self):
        """Check if final training metrics indicate quality issues."""
        if not self.training_metrics:
            return False
        return self.training_metrics.get('failure_detected', False)
    
    def get_training_quality_warning(self):
        """Get training quality warning message if any."""
        if not self.has_training_quality_issues():
            return None
        
        failure_label = self.training_metrics.get('failure_label', 'UNKNOWN')
        recommendations = list(self.training_metrics.get('recommendations', []))  # Make a copy
        
        warning = {
            "type": "TRAINING_QUALITY_ISSUE",
            "severity": "HIGH",
            "failure_mode": failure_label,
            "message": f"Model training completed with quality issues: {failure_label}",
            "recommendations": recommendations,
            "details": {
                "auc": self.training_metrics.get('auc', 0),
                "accuracy": self.training_metrics.get('accuracy', 0),
                "f1": self.training_metrics.get('f1', 0),
            }
        }
        
        # Add class distribution if available (for classification tasks)
        if self.class_distribution:
            warning["class_distribution"] = self.class_distribution
            
            # Add a human-readable summary of the class imbalance
            if self.training_metrics.get('is_binary', False):
                # For binary classification, compute imbalance ratio
                total_counts = self.class_distribution['total']
                labels = sorted(total_counts.keys())
                if len(labels) == 2:
                    majority_count = max(total_counts.values())
                    minority_count = min(total_counts.values())
                    if minority_count > 0:
                        imbalance_ratio = majority_count / minority_count
                        warning["imbalance_ratio"] = round(imbalance_ratio, 2)
                        warning["minority_class_count"] = minority_count
                        warning["majority_class_count"] = majority_count
                        
                        # Add contextual message
                        if minority_count < 10:
                            warning["data_sufficiency"] = "INSUFFICIENT - Need at least 50-100 examples of minority class"
                            recommendations.append(f"→ Training data has only {minority_count} positive examples (out of {self.class_distribution['total_total']} total) - need at least 50-100 for reliable training")
                        elif minority_count < 50:
                            warning["data_sufficiency"] = "LOW - Model may struggle with so few minority examples"
                            recommendations.append(f"→ Training data has only {minority_count} positive examples (out of {self.class_distribution['total_total']} total) - consider collecting more data")
                        elif imbalance_ratio > 20:
                            warning["data_sufficiency"] = "IMBALANCED - Large class imbalance may affect performance"
                            recommendations.append(f"→ Class imbalance is {imbalance_ratio:.1f}:1 ({majority_count} vs {minority_count} examples) - model may be biased toward majority class")
                        else:
                            warning["data_sufficiency"] = "ADEQUATE"
                        
                        # Update recommendations in the warning
                        warning["recommendations"] = recommendations
        
        return warning
    
    def get_warning_summary(self):
        """Get a human-readable summary of warnings."""
        if not self.training_warnings:
            return "No warnings recorded during training."
        
        lines = [f"Training completed with {len(self.training_warnings)} warning type(s):"]
        for warning_type, data in self.training_warnings.items():
            count = data["count"]
            first = data["first_seen"]
            last = data["last_seen"]
            lines.append(f"  - {warning_type}: occurred {count} time(s) (epochs {first}-{last})")
            
            # Check if warning was at best epoch
            if warning_type in [w["type"] for w in self.best_epoch_warnings]:
                lines.append(f"    ⚠️  Warning persisted at best model epoch!")
        
        return "\n".join(lines)
    
    def _apply_dynamic_features(self, current_epoch: int):
        """
        Record high-confidence feature suggestions for the next training run.
        
        IMPORTANT: We do NOT modify DataFrames or models mid-training anymore.
        This just records the suggestions so they can be applied at the START 
        of the next training run.
        
        Args:
            current_epoch: Current training epoch
        """
        features_to_apply = self._feature_tracker.get_features_to_apply(current_epoch)
        
        if not features_to_apply:
            return
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"📝 RECORDING DYNAMIC FEATURES FOR NEXT TRAINING RUN (EPOCH {current_epoch})")
        logger.info("=" * 80)
        
        for fname, finfo in features_to_apply:
            epochs_list = finfo['suggested_at_epochs']
            if len(epochs_list) > 25:
                epochs_str = ', '.join(map(str, epochs_list[:25]))
                remaining = len(epochs_list) - 25
                epochs_str += f" + {remaining} others"
            else:
                epochs_str = ', '.join(map(str, epochs_list))
            logger.info(f"   • {fname}")
            logger.info(f"     - Votes: {finfo['count']}")
            logger.info(f"     - Suggested at epochs: [{epochs_str}]")
        
        logger.info("=" * 80)
        
        try:
            # Track these suggestions for the next training run
            for feature_name, info in features_to_apply:
                self._features_applied_epochs.append({
                    'epoch': current_epoch,
                    'feature_name': feature_name,
                    'votes': info['count'],
                    'suggested_at_epochs': info['suggested_at_epochs']
                })
                
                # CRITICAL: Mark as recorded in tracker to prevent duplicate recording
                if feature_name in self._feature_tracker.suggestion_history:
                    self._feature_tracker.suggestion_history[feature_name]['applied'] = True
                    self._feature_tracker.suggestion_history[feature_name]['applied_epoch'] = current_epoch
                self._feature_tracker.applied_features.add(feature_name)
                
                # Log to application log for next training run to pick up
                self._feature_tracker.application_log.append({
                    'epoch': current_epoch,
                    'feature_name': feature_name,
                    'votes': info['count'],
                    'first_seen_epoch': info['first_seen_epoch'],
                    'suggestion': info['suggestion']
                })
            
            logger.info("")
            logger.info(f"✅ Feature suggestions recorded for next training run")
            logger.info(f"   Features recorded: {len(features_to_apply)}")
            logger.info(f"   Current training continues with {len(self.train_df.columns)} columns")
            logger.info(f"   Note: These features will be automatically applied at the start of the next training run")
            logger.info("=" * 80)
            logger.info("")
            
        except Exception as e:
            logger.error(f"❌ Failed to record features: {e}")
            traceback.print_exc()

    # DISABLED: Feature suggestions replaced by DynamicRelationshipExtractor (2026-01-02)
    # The DynamicRelationshipExtractor learns relationships directly in embedding space,
    # which is more powerful than pre-computing feature columns. It computes N*(N-1)/2 pairs
    # with 6 operations each (*, +, -, /, both directions), then prunes to top 25% based on
    # gradient contributions. This captures 90%+ of what feature suggestions were doing,
    # without the ES extension issues and DataFrame modification complexity.
    #
    # Original method signature:
    # def _load_and_apply_previous_features(self, train_df: pd.DataFrame, val_df: Optional[pd.DataFrame] = None) -> tuple:
    #
    # To re-enable (NOT RECOMMENDED):
    # 1. Uncomment this entire method (lines 1726-1997)
    # 2. Uncomment the call in prep_for_training() (around line 2715)
    # 3. Uncomment auto_apply_monitor_features parameter in __init__ (line 425)
    # 4. Deal with ES extension issues that this causes
    
    def _load_and_apply_previous_features_DISABLED(self, train_df: pd.DataFrame, val_df: Optional[pd.DataFrame] = None) -> tuple:
        """
        DISABLED 2026-01-02: Replaced by DynamicRelationshipExtractor.
        
        This method is kept for reference but will not be called.
        Relationships are now learned dynamically in embedding space rather than
        pre-computed as DataFrame columns.
        """
        logger.warning("⚠️  _load_and_apply_previous_features_DISABLED called - this is disabled!")
        logger.warning("   Relationships are now learned by DynamicRelationshipExtractor")
        return train_df, val_df
    
    # Original implementation preserved below for reference (commented out):
    #
    # def _load_and_apply_previous_features(self, train_df: pd.DataFrame, val_df: Optional[pd.DataFrame] = None) -> tuple:
    #     """
    #     Load feature suggestion history from previous training runs and apply them.
    #     
    #     This allows features discovered in one training run to be used in the next run.
    #     First checks monitor.featrix.com for suggestions keyed by dataset hash,
    #     then falls back to local files.
    #     
    #     Features are filtered based on effectiveness history - only features that
    #     actually improved metrics in previous runs are loaded.
    #     
    #     Args:
    #         train_df: Training DataFrame
    #         val_df: Optional validation DataFrame
    #     
    #     Returns:
    #         (train_df, val_df) with features applied
    #     """
    #     ... (original 270 lines of implementation) ...
    
    def _filter_useless_columns(self, columns: set) -> tuple[set, set, set]:
        """
        Filter out columns with no information content.
        
        Args:
            columns: Set of column names to check
            
        Returns:
            Tuple of (useful_columns, all_null_columns, uniform_columns)
        """
        all_null_cols = set()
        uniform_cols = set()
        
        for col in columns:
            try:
                col_data = self.train_df[col]
                
                # Check for all nulls
                if col_data.isna().all():
                    all_null_cols.add(col)
                    continue
                
                # Check for uniform values (only 1 unique value, ignoring nulls)
                non_null_data = col_data.dropna()
                if len(non_null_data) > 0 and non_null_data.nunique() == 1:
                    uniform_cols.add(col)
                    
            except Exception as e:
                logger.warning(f"   ⚠️  Could not check column '{col}': {e}")
        
        useless_cols = all_null_cols | uniform_cols
        useful_cols = columns - useless_cols
        
        return useful_cols, all_null_cols, uniform_cols
    
    def _select_best_columns_by_mi(
        self, 
        columns: set, 
        target_col_name: str, 
        max_columns: int
    ) -> set:
        """
        Select best columns using Mutual Information.
        
        Args:
            columns: Set of column names to select from
            target_col_name: Name of target column
            max_columns: Maximum number of columns to select
            
        Returns:
            Set of selected column names
        """
        try:
            # Prepare target variable
            y = self.train_df[target_col_name].copy()
            
            # Determine if classification or regression
            is_classification = (self.target_col_type == 'set' or 
                                (hasattr(self, 'target_type') and self.target_type in ['classification', 'set']))
            
            # Encode target if needed for MI calculation
            if is_classification:
                le = LabelEncoder()
                y_encoded = le.fit_transform(y.astype(str))
            else:
                y_encoded = pd.to_numeric(y, errors='coerce').fillna(0).values
            
            # Calculate MI scores for each column
            mi_scores = {}
            for col in columns:
                try:
                    X_col = self.train_df[[col]].copy()
                    
                    # Handle different column types
                    if X_col[col].dtype == 'object' or X_col[col].dtype.name == 'category':
                        # Categorical: encode
                        le_col = LabelEncoder()
                        X_encoded = le_col.fit_transform(X_col[col].astype(str)).reshape(-1, 1)
                    else:
                        # Numeric: use as-is, fill NaN
                        X_encoded = pd.to_numeric(X_col[col], errors='coerce').fillna(0).values.reshape(-1, 1)
                    
                    # Calculate MI
                    if is_classification:
                        mi = mutual_info_classif(X_encoded, y_encoded, discrete_features=False, random_state=42)[0]
                    else:
                        mi = mutual_info_regression(X_encoded, y_encoded, random_state=42)[0]
                    
                    mi_scores[col] = mi
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not calculate MI for '{col}': {e}")
                    mi_scores[col] = 0.0
            
            # Sort by MI score and select top N
            sorted_cols = sorted(mi_scores.items(), key=lambda x: x[1], reverse=True)
            selected_columns = set([col for col, score in sorted_cols[:max_columns]])
            
            # Log results
            logger.info(f"📊 ES_EXTENSION_MI_RESULTS:")
            logger.info(f"   Top {len(selected_columns)} columns selected by Mutual Information:")
            for col, score in sorted_cols[:max_columns]:
                logger.info(f"   ✅ {col:<50} MI={score:.6f}")
            logger.info(f"")
            
            rejected_columns = columns - selected_columns
            if rejected_columns:
                logger.info(f"   Rejected {len(rejected_columns)} low-information columns:")
                for col, score in sorted_cols[max_columns:]:
                    logger.info(f"   ❌ {col:<50} MI={score:.6f}")
                logger.info(f"")
            
            return selected_columns
            
        except Exception as selection_error:
            logger.error(f"❌ ES_EXTENSION_SELECTION_ERROR: Feature selection failed: {selection_error}")
            logger.error(f"   Falling back to first {max_columns} columns alphabetically")
            return set(sorted(columns)[:max_columns])
    
    def _auto_extend_embedding_space_if_needed(self, target_col_name: str):
        """
        Automatically extend the embedding space if DataFrame has columns that ES doesn't have codecs for.
        
        This is called during prep_for_training() after features are loaded.
        If new columns are detected, the ES is extended and trained automatically.
        
        Args:
            target_col_name: Target column name (excluded from comparison)
        """
        if self.train_df is None:
            return
        
        # Get columns from DataFrame (exclude target)
        df_columns = set(self.train_df.columns) - {target_col_name}
        
        # Get columns from EmbeddingSpace
        es_columns = set(self.embedding_space.col_codecs.keys()) if self.embedding_space.col_codecs else set()
        
        # Find new columns in DataFrame that aren't in ES
        new_columns = df_columns - es_columns
        
        if not new_columns:
            # No new columns - no extension needed
            return
        
        logger.info("")
        logger.info("")
        logger.info("█" * 80)
        logger.info("█" * 80)
        logger.info("███")
        logger.info("███  🚀 ES_EXTENSION_START - AUTO-EXTENDING EMBEDDING SPACE")
        logger.info("███")
        logger.info("█" * 80)
        logger.info("█" * 80)
        logger.info("")
        logger.info(f"🔍 ES_EXTENSION_REASON: Detected {len(new_columns)} new columns in DataFrame that are not in EmbeddingSpace")
        logger.info(f"")
        logger.info(f"📊 ES_EXTENSION_COLUMN_ANALYSIS:")
        logger.info(f"   Original EmbeddingSpace columns:  {len(es_columns)}")
        logger.info(f"   DataFrame columns (no target):    {len(df_columns)}")
        logger.info(f"   NEW columns requiring extension:  {len(new_columns)}")
        logger.info(f"")
        
        # STEP 1: Filter out useless columns (all nulls or uniform values)
        logger.info(f"🧹 ES_EXTENSION_CLEANING: Filtering out useless columns...")
        new_columns, all_null_cols, uniform_cols = self._filter_useless_columns(new_columns)
        
        useless_cols = all_null_cols | uniform_cols
        if useless_cols:
            logger.info(f"   ❌ Dropped {len(useless_cols)} useless columns:")
            if all_null_cols:
                logger.info(f"      • {len(all_null_cols)} all-null columns: {sorted(list(all_null_cols))[:10]}")
                if len(all_null_cols) > 10:
                    logger.info(f"        ... and {len(all_null_cols) - 10} more")
            if uniform_cols:
                logger.info(f"      • {len(uniform_cols)} uniform columns: {sorted(list(uniform_cols))[:10]}")
                if len(uniform_cols) > 10:
                    logger.info(f"        ... and {len(uniform_cols) - 10} more")
            logger.info(f"")
            logger.info(f"   ✅ Remaining useful columns: {len(new_columns)}")
        else:
            logger.info(f"   ✅ All {len(new_columns)} columns have data and variance")
        logger.info(f"")
        
        # STEP 2: Check if we still need MI-based feature selection
        max_new_columns = max(20, int(len(es_columns) * 0.25))
        
        if len(new_columns) > max_new_columns:
            logger.info(f"⚠️  ES_EXTENSION_LIMIT: Too many new columns ({len(new_columns)})")
            logger.info(f"   Maximum allowed: {max_new_columns} (25% of {len(es_columns)} existing columns, min 20)")
            logger.info(f"")
            logger.info(f"🔬 ES_EXTENSION_FEATURE_SELECTION: Using Mutual Information to select best columns")
            logger.info(f"")
            
            # Use MI to select best columns
            new_columns = self._select_best_columns_by_mi(new_columns, target_col_name, max_new_columns)
        
        logger.info(f"🆕 ES_EXTENSION_FINAL_COLUMNS ({len(new_columns)} total):")
        for col in sorted(new_columns):
            logger.info(f"   • {col}")
        logger.info("")
        logger.info("ℹ️  ES_EXTENSION_CONTEXT: Feature engineering added derived features")
        logger.info("ℹ️  ES_EXTENSION_ACTION: Creating extended ES with new column codecs")
        logger.info("")
        logger.info("█" * 80)
        logger.info("")
        
        # Extend the embedding space
        try:
            from featrix.neural.embedded_space import EmbeddingSpace
            
            # Determine training parameters for extension
            original_epochs = getattr(self.embedding_space, 'n_epochs', 50)
            extension_epochs = original_epochs * 2 # ... and allow for early stopping?!  -- max(10, original_epochs // 4)  # At least 10 epochs, typically 1/4 of original
            batch_size = getattr(self.embedding_space, 'batch_size', 128)
            
            # Build feature metadata if available
            feature_metadata = {}
            if hasattr(self, '_loaded_feature_metadata') and self._loaded_feature_metadata is not None:
                feature_metadata = {
                    'source': 'auto_extension_from_prep_for_training',
                    'applied_features': self._loaded_feature_metadata.get('feature_names', []),
                    'load_date': self._loaded_feature_metadata.get('load_date'),
                    'auto_extended': True
                }
            else:
                feature_metadata = {
                    'source': 'auto_extension_from_prep_for_training',
                    'new_columns': list(new_columns),
                    'auto_extended': True
                }
            
            logger.info(f"🔧 ES_EXTENSION_CONFIG:")
            logger.info(f"   Original ES epochs:     {original_epochs}")
            logger.info(f"   Extension epochs:       {extension_epochs} (1/4 of original, min 10)")
            logger.info(f"   Batch size:             {batch_size}")
            logger.info(f"   Output dir:             {self._output_dir or 'default'}")
            logger.info("")
            
            # CRITICAL: Filter DataFrames to only include ES columns + selected new columns + target
            # This prevents extending with rejected low-information columns
            columns_to_keep = list(es_columns | new_columns | {target_col_name})
            filtered_train_df = self.train_df[columns_to_keep].copy()
            filtered_val_df = self.val_df[columns_to_keep].copy() if self.val_df is not None else None
            
            logger.info(f"📋 ES_EXTENSION_DATAFRAME_FILTERING:")
            logger.info(f"   Original train_df columns: {len(self.train_df.columns)}")
            logger.info(f"   Filtered train_df columns: {len(filtered_train_df.columns)}")
            logger.info(f"   (ES columns: {len(es_columns)}, new columns: {len(new_columns)}, target: 1)")
            logger.info("")
            
            # Extend the ES
            logger.info("█" * 80)
            logger.info("🚀 ES_EXTENSION_PHASE_1: Creating extended EmbeddingSpace structure...")
            logger.info("█" * 80)
            extended_es = EmbeddingSpace.extend_from_existing(
                existing_es=self.embedding_space,
                enriched_train_df=filtered_train_df,
                enriched_val_df=filtered_val_df,
                n_epochs=extension_epochs,
                batch_size=batch_size,
                output_dir=self._output_dir,
                name=f"{self.embedding_space.name}_extended" if self.embedding_space.name else "extended_es",
                feature_metadata=feature_metadata
            )
            
            logger.info("")
            logger.info("✅ ES_EXTENSION_PHASE_1_COMPLETE: Structure created")
            logger.info(f"   Extended ES now has {len(extended_es.col_codecs)} columns (was {len(es_columns)})")
            logger.info("")
            
            # Train the extended ES
            logger.info("█" * 80)
            logger.info(f"🏋️  ES_EXTENSION_PHASE_2: Training extended ES for {extension_epochs} epochs...")
            logger.info("█" * 80)
            logger.info("")
            extended_es.train(
                batch_size=batch_size,
                n_epochs=extension_epochs,
                print_progress_step=max(1, extension_epochs // 10)  # Print ~10 progress updates
            )
            
            logger.info("")
            logger.info("█" * 80)
            logger.info("█" * 80)
            logger.info("███")
            logger.info("███  ✅ ES_EXTENSION_COMPLETE - EMBEDDING SPACE EXTENDED SUCCESSFULLY")
            logger.info("███")
            logger.info("█" * 80)
            logger.info("█" * 80)
            logger.info("")
            logger.info(f"📊 ES_EXTENSION_SUMMARY:")
            logger.info(f"   Original columns:       {len(es_columns)}")
            logger.info(f"   Extended columns:       {len(extended_es.col_codecs)}")
            logger.info(f"   New columns added:      {len(new_columns)}")
            logger.info(f"   Training epochs used:   {extension_epochs}")
            logger.info("")
            logger.info("✅ ES_EXTENSION_NEXT_STEP: SinglePredictor will use the extended EmbeddingSpace")
            logger.info("")
            logger.info("█" * 80)
            logger.info("")
            
            # Replace the embedding space with the extended one
            self.embedding_space = extended_es
            
        except Exception as e:
            logger.error("")
            logger.error("█" * 80)
            logger.error("█" * 80)
            logger.error("███")
            logger.error("███  ❌ ES_EXTENSION_FAILED - EMBEDDING SPACE EXTENSION FAILED")
            logger.error("███")
            logger.error("█" * 80)
            logger.error("█" * 80)
            logger.error("")
            logger.error(f"❌ ES_EXTENSION_ERROR: {e}")
            logger.error("")
            logger.error("⚠️  ES_EXTENSION_CONSEQUENCE: New columns CANNOT be used for training")
            logger.error(f"⚠️  ES_EXTENSION_IGNORED_COLUMNS ({len(new_columns)} total):")
            for col in sorted(new_columns):
                logger.error(f"   • {col}")
            logger.error("")
            logger.error("🔧 ES_EXTENSION_FIX_OPTIONS:")
            logger.error("   1. Manually extend ES: EmbeddingSpace.extend_from_existing()")
            logger.error("   2. Remove extra columns from DataFrame before training")
            logger.error("   3. Check error details above for specific failure reason")
            logger.error("")
            logger.error("█" * 80)
            logger.error("")
            import traceback
            traceback.print_exc()
            
            # Don't raise - allow training to continue with existing columns
            # The user will see the warning above
    
    def create_extended_embedding_space(
        self,
        enriched_train_df: pd.DataFrame,
        enriched_val_df: Optional[pd.DataFrame] = None,
        n_epochs: int = None,
        batch_size: int = None,
        output_dir: str = None
    ) -> 'EmbeddingSpace':
        """
        Create an extended EmbeddingSpace that includes loaded feature columns.
        
        This is a convenience method that wraps EmbeddingSpace.extend_from_existing()
        and uses the feature metadata tracked from _load_and_apply_previous_features().
        
        NOTE: As of the auto-extension feature, this is typically called automatically
        by prep_for_training() when new columns are detected. You only need to call
        this manually if you want more control over the extension process.
        
        WHEN TO USE THIS:
        - After calling prep_for_training() which loaded features
        - You want a new ES that includes those features
        - For the next training run with extended embeddings
        
        Args:
            enriched_train_df: Training DataFrame with features already applied
            enriched_val_df: Validation DataFrame with features (optional)
            n_epochs: Training epochs for extension (default: original_epochs / 4)
            batch_size: Training batch size (default: use existing ES batch size)
            output_dir: Output directory for extended ES
            
        Returns:
            New extended EmbeddingSpace
            
        Example:
            # Prep for training (loads features automatically)
            sp.prep_for_training(train_df, 'target', 'set')
            # sp.train_df now has engineered features
            
            # Create extended ES that includes those features
            extended_es = sp.create_extended_embedding_space(
                enriched_train_df=sp.train_df,
                enriched_val_df=sp.val_df,
                output_dir="qa.out/featrix_output"
            )
            
            # Save for next run
            extended_es.save("embedding_space_v2.pkl")
        """
        from featrix.neural.embedded_space import EmbeddingSpace
        
        if not hasattr(self, '_loaded_feature_metadata') or self._loaded_feature_metadata is None:
            raise ValueError(
                "No loaded features found. "
                "This method should be called after prep_for_training() which loads features. "
                "If no features were loaded, there's nothing to extend."
            )
        
        logger.info("=" * 80)
        logger.info("🔧 CREATING EXTENDED EMBEDDING SPACE")
        logger.info("=" * 80)
        logger.info(f"📦 Loaded features to include: {len(self._loaded_features)}")
        for feat in self._loaded_features:
            logger.info(f"   • {feat}")
        logger.info("")
        
        # Use output_dir from current predictor if not specified
        if output_dir is None:
            output_dir = getattr(self, '_output_dir', None)
        
        # Call EmbeddingSpace.extend_from_existing
        extended_es = EmbeddingSpace.extend_from_existing(
            existing_es=self.embedding_space,
            enriched_train_df=enriched_train_df,
            enriched_val_df=enriched_val_df,
            n_epochs=n_epochs,
            batch_size=batch_size,
            output_dir=output_dir,
            name=f"{getattr(self.embedding_space, 'name', 'unnamed')}_with_features",
            feature_metadata=self._loaded_feature_metadata
        )
        
        logger.info("✅ Extended EmbeddingSpace created successfully!")
        logger.info("=" * 80)
        logger.info("")
        
        return extended_es

    def hydrate_to_cpu_if_needed(self):
        if hasattr(self, 'predictor') and self.predictor is not None:
            logger.info("predictor going to cpu")
            self.predictor.to(torch.device("cpu"))
        else:
            logger.info("no predictor for cpu")
        return

    def hydrate_to_gpu_if_needed(self):
        # CRITICAL: Check if we have a pending fine-tuned encoder that needs loading
        # This can happen if __setstate__ deferred loading
        if hasattr(self, '_pending_state_dicts') and '_finetuned_encoder_state_dict' in self._pending_state_dicts:
            if hasattr(self, 'embedding_space') and self.embedding_space is not None:
                if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                    try:
                        encoder_state = self._pending_state_dicts['_finetuned_encoder_state_dict']
                        self.embedding_space.encoder.load_state_dict(encoder_state)
                        logger.info(f"✅ Loaded pending fine-tuned encoder state_dict ({len(encoder_state)} keys) in hydrate")
                        del self._pending_state_dicts['_finetuned_encoder_state_dict']
                    except Exception as e:
                        logger.error(f"❌ Failed to load fine-tuned encoder in hydrate: {e}")
        
        # ENABLED: Move predictor to GPU if available
        if is_gpu_available():
            if hasattr(self, 'predictor') and self.predictor is not None:
                current_device = next(self.predictor.parameters()).device if list(self.predictor.parameters()) else None
                if current_device is None or current_device.type == 'cpu':
                    logger.info("🔄 Moving predictor to GPU...")
                    self.predictor = self.predictor.to(get_device())
                    logger.info(f"✅ Predictor moved to GPU: {next(self.predictor.parameters()).device}")
                else:
                    logger.debug(f"✅ Predictor already on GPU: {current_device}")
            
            # Also move predictor_base if it exists
            if hasattr(self, 'predictor_base') and self.predictor_base is not None:
                current_device = next(self.predictor_base.parameters()).device if list(self.predictor_base.parameters()) else None
                if current_device is None or current_device.type == 'cpu':
                    self.predictor_base = self.predictor_base.to(get_device())
        else:
            logger.debug("CPU mode - CUDA not available")

    def cleanup_gpu_memory(self):
        """
        Clean up GPU memory used by this single predictor.
        This should be called after training or prediction to free GPU resources.
        """
        try:
            # Move models to CPU first to free GPU memory
            if hasattr(self, 'predictor') and self.predictor is not None:
                logger.info("Moving predictor to CPU for cleanup")
                self.predictor.cpu()
            
            if hasattr(self, 'predictor_base') and self.predictor_base is not None:
                logger.info("Moving predictor_base to CPU for cleanup")
                self.predictor_base.cpu()
            
            # Move codecs to CPU if they have tensors
            if hasattr(self, 'target_codec') and self.target_codec is not None:
                if hasattr(self.target_codec, 'cpu'):
                    self.target_codec.cpu()
            
            if hasattr(self, 'all_codecs') and self.all_codecs:
                for codec_name, codec in self.all_codecs.items():
                    if hasattr(codec, 'cpu'):
                        codec.cpu()
            
            # Force PyTorch GPU memory cleanup
            try:
                # torch is already imported at module level
                if is_gpu_available():
                    empty_gpu_cache()
                    synchronize_gpu()
                    logger.info("GPU memory cache cleared")
            except ImportError:
                pass  # PyTorch not available
            
            # Force garbage collection
            gc.collect()
            logger.info("Python garbage collection completed")
            
        except Exception as cleanup_error:
            logger.warning(f"GPU cleanup failed: {cleanup_error}")
            traceback.print_exc()

    def _probs_dict(self, probs) -> Dict:
        return {
            self.target_codec.detokenize(Token(value=i, status=2)): prob.item()
            for i, prob in enumerate(probs)
        }

    def _evaluate_encoder_quality(self, train_df, val_df):
        """
        Evaluate embedding space encoder quality on training data.
        
        Checks for:
        - Embedding spread/variance (low variance = constant embeddings = bad)
        - Class separation (for classification tasks)
        - Embedding magnitude/norm
        - Pairwise distances between samples
        
        This helps catch issues where the ES encoder is producing poor embeddings
        that will cause SP training to fail (e.g., CONSTANT_PROBABILITY).
        """
        try:
            from featrix.neural.gpu_utils import get_device, is_gpu_available
            
            # Sample a subset of training data for evaluation (max 100 samples for speed)
            sample_size = min(100, len(train_df))
            sample_df = train_df.sample(n=sample_size, random_state=42).reset_index(drop=True)
            
            logger.info(f"📊 Sampling {sample_size} rows from training data for encoder quality evaluation")
            
            # Encode all samples
            embeddings = []
            target_values = []
            
            encoder = self.embedding_space.encoder
            encoder_device = next(encoder.parameters()).device if list(encoder.parameters()) else get_device()
            
            # Put encoder in eval mode for consistent outputs
            was_training = encoder.training
            encoder.eval()
            
            try:
                with torch.no_grad():
                    for idx, row in sample_df.iterrows():
                        try:
                            # Create query dict (exclude target column)
                            query = {k: v for k, v in row.items() if k != self.target_col_name}
                            
                            # Encode the record
                            embedding = self.embedding_space.encode_record(query, squeeze=True)
                            
                            # Move to CPU for analysis
                            if isinstance(embedding, torch.Tensor):
                                embedding = embedding.cpu()
                            
                            embeddings.append(embedding)
                            
                            # Store target value if available
                            if self.target_col_name in row:
                                target_values.append(row[self.target_col_name])
                            
                        except Exception as e:
                            logger.debug(f"   ⚠️  Failed to encode row {idx}: {e}")
                            continue
                
                if len(embeddings) == 0:
                    logger.warning("   ⚠️  No embeddings generated - cannot evaluate encoder quality")
                    return
                
                # Stack embeddings into tensor
                if isinstance(embeddings[0], torch.Tensor):
                    embedding_tensor = torch.stack(embeddings)
                else:
                    embedding_tensor = torch.tensor(np.array(embeddings))
                
                # Compute statistics
                n_samples, d_model = embedding_tensor.shape
                mean_embedding = embedding_tensor.mean(dim=0)
                std_embedding = embedding_tensor.std(dim=0)
                
                # Per-dimension statistics
                mean_std = std_embedding.mean().item()
                min_std = std_embedding.min().item()
                max_std = std_embedding.max().item()
                
                # Overall embedding statistics
                embedding_norms = torch.norm(embedding_tensor, dim=1)
                mean_norm = embedding_norms.mean().item()
                std_norm = embedding_norms.std().item()
                min_norm = embedding_norms.min().item()
                max_norm = embedding_norms.max().item()
                
                # Pairwise distances (sample a subset to avoid O(n²) computation)
                n_pairwise = min(50, n_samples)
                pairwise_indices = torch.randperm(n_samples)[:n_pairwise]
                pairwise_embeddings = embedding_tensor[pairwise_indices]
                
                # Compute pairwise L2 distances
                pairwise_distances = torch.cdist(pairwise_embeddings, pairwise_embeddings, p=2)
                # Exclude diagonal (self-distances)
                mask = ~torch.eye(n_pairwise, dtype=torch.bool)
                pairwise_distances_flat = pairwise_distances[mask]
                
                mean_distance = pairwise_distances_flat.mean().item()
                std_distance = pairwise_distances_flat.std().item()
                min_distance = pairwise_distances_flat.min().item()
                max_distance = pairwise_distances_flat.max().item()
                
                # Log statistics
                logger.info(f"📊 EMBEDDING STATISTICS ({n_samples} samples, d_model={d_model}):")
                logger.info(f"   Per-dimension std: mean={mean_std:.6f}, min={min_std:.6f}, max={max_std:.6f}")
                logger.info(f"   Embedding norms: mean={mean_norm:.6f}, std={std_norm:.6f}, range=[{min_norm:.6f}, {max_norm:.6f}]")
                logger.info(f"   Pairwise distances ({n_pairwise} samples): mean={mean_distance:.6f}, std={std_distance:.6f}, range=[{min_distance:.6f}, {max_distance:.6f}]")
                
                # Check for problems
                warnings = []
                
                # Check 1: Low variance (constant embeddings)
                if mean_std < 0.01:
                    warnings.append(f"🚨 CRITICAL: Very low embedding variance (std={mean_std:.6f}) - embeddings are nearly constant!")
                    warnings.append("   → This will cause CONSTANT_PROBABILITY in SP training")
                    warnings.append("   → Check if ES encoder is frozen or not trained properly")
                elif mean_std < 0.05:
                    warnings.append(f"⚠️  WARNING: Low embedding variance (std={mean_std:.6f}) - embeddings have limited spread")
                
                # Check 2: Very small pairwise distances (all embeddings similar)
                if mean_distance < 0.1:
                    warnings.append(f"🚨 CRITICAL: Very small pairwise distances (mean={mean_distance:.6f}) - all embeddings are nearly identical!")
                    warnings.append("   → This will cause CONSTANT_PROBABILITY in SP training")
                elif mean_distance < 0.5:
                    warnings.append(f"⚠️  WARNING: Small pairwise distances (mean={mean_distance:.6f}) - embeddings are too similar")
                
                # Check 3: Zero or near-zero norms
                if mean_norm < 0.01:
                    warnings.append(f"🚨 CRITICAL: Embedding norms are near-zero (mean={mean_norm:.6f}) - embeddings are collapsed!")
                
                # Check 4: Class separation (for classification tasks)
                if len(target_values) > 0 and hasattr(self, 'target_codec') and self.target_codec is not None:
                    try:
                        # Group embeddings by target class
                        unique_targets = list(set(target_values))
                        if len(unique_targets) >= 2:  # Binary or multi-class
                            class_embeddings = {}
                            for i, target_val in enumerate(target_values):
                                if target_val not in class_embeddings:
                                    class_embeddings[target_val] = []
                                class_embeddings[target_val].append(embedding_tensor[i])
                            
                            # Compute class centroids
                            class_centroids = {}
                            for target_val, emb_list in class_embeddings.items():
                                class_tensor = torch.stack(emb_list)
                                class_centroids[target_val] = class_tensor.mean(dim=0)
                            
                            # Compute inter-class distances
                            class_names = list(class_centroids.keys())
                            inter_class_distances = []
                            for i, class_a in enumerate(class_names):
                                for class_b in class_names[i+1:]:
                                    dist = torch.norm(class_centroids[class_a] - class_centroids[class_b]).item()
                                    inter_class_distances.append(dist)
                            
                            if inter_class_distances:
                                mean_inter_class_dist = np.mean(inter_class_distances)
                                min_inter_class_dist = np.min(inter_class_distances)
                                
                                logger.info(f"📊 CLASS SEPARATION ({len(unique_targets)} classes):")
                                logger.info(f"   Mean inter-class distance: {mean_inter_class_dist:.6f}")
                                logger.info(f"   Min inter-class distance: {min_inter_class_dist:.6f}")
                                
                                if mean_inter_class_dist < 0.1:
                                    warnings.append(f"🚨 CRITICAL: Poor class separation (mean inter-class dist={mean_inter_class_dist:.6f})!")
                                    warnings.append("   → Classes are not well-separated in embedding space")
                                    warnings.append("   → SP will struggle to learn class boundaries")
                                elif mean_inter_class_dist < 0.5:
                                    warnings.append(f"⚠️  WARNING: Weak class separation (mean inter-class dist={mean_inter_class_dist:.6f})")
                    except Exception as e:
                        logger.debug(f"   ⚠️  Failed to compute class separation: {e}")
                
                # Log warnings if any
                if warnings:
                    logger.warning("=" * 80)
                    logger.warning("🚨 ENCODER QUALITY ISSUES DETECTED:")
                    for warning in warnings:
                        logger.warning(f"   {warning}")
                    logger.warning("=" * 80)
                else:
                    logger.info("✅ Encoder quality looks good - embeddings have sufficient spread and diversity")
                
                # Record encoder quality check (if we have embedding stats)
                try:
                    from featrix.neural.customer_quality_tracker import QualityCheckName, QualityGrade
                    # Use epoch 0 for encoder quality (evaluated at start of training)
                    qt = self.get_quality_tracker(0)
                    
                    # Determine grade based on warnings and stats
                    if warnings:
                        # Has warnings - check severity
                        has_critical = any("CRITICAL" in w for w in warnings)
                        if has_critical:
                            enc_grade = QualityGrade.F
                        else:
                            enc_grade = QualityGrade.D
                    else:
                        # No warnings - check if we have good stats
                        if 'mean_std' in locals() and mean_std > 0.01:
                            if mean_std > 0.1:
                                enc_grade = QualityGrade.A
                            elif mean_std > 0.05:
                                enc_grade = QualityGrade.B
                            else:
                                enc_grade = QualityGrade.C
                        else:
                            enc_grade = QualityGrade.C  # Default if no stats
                    
                    metadata = {}
                    if 'mean_std' in locals():
                        metadata['embedding_spread'] = mean_std
                    if 'min_std' in locals():
                        metadata['min_std'] = min_std
                    if 'mean_distance' in locals():
                        metadata['pairwise_distance_mean'] = mean_distance
                    if warnings:
                        metadata['warnings'] = warnings
                    
                    qt.record_check(
                        name=QualityCheckName.ENCODER_QUALITY,
                        graded_score=enc_grade,
                        metadata=metadata
                    )
                except Exception as e:
                    logger.debug(f"   Failed to record encoder quality check: {e}")
                
            finally:
                # Restore encoder training mode
                if was_training:
                    encoder.train()
                else:
                    encoder.eval()
                    
        except Exception as e:
            logger.warning(f"⚠️  Error during encoder quality evaluation: {e}")
            logger.debug(traceback.format_exc())

    def _compute_class_weights(self, target_col, class_imbalance=None):
        """
        Compute class weights for imbalanced classification.
        
        Uses square root of inverse frequency weighting to prevent over-correction:
        weight = sqrt(1 / frequency)
        
        This is gentler than full inverse frequency and prevents models from 
        over-predicting the minority class.
        
        Args:
            target_col: pandas Series containing the target column values
            class_imbalance: Optional dict with expected class ratios/counts from real world.
                           If provided, uses these instead of the training data distribution.
                           Can be ratios (e.g., {"good": 0.97, "bad": 0.03}) or counts (e.g., {"good": 9700, "bad": 300})
            
        Returns:
            dict mapping class names to weights
        """
        try:
            # If class_imbalance is provided, use it instead of training data distribution
            if class_imbalance is not None:
                logger.info("📊 Using provided class_imbalance for class weighting")
                logger.info(f"   Provided class_imbalance: {class_imbalance}")
                
                # Convert to frequencies (normalize if needed)
                total = sum(class_imbalance.values())
                class_frequencies = {k: v / total for k, v in class_imbalance.items()}
                
                # Log the expected class distribution
                logger.info("📊 Expected Class Distribution (from class_imbalance):")
                for class_name, freq in class_frequencies.items():
                    logger.info(f"   '{class_name}': {freq*100:.1f}%")
                
                # Compute SQRT of inverse frequency weights (gentler than full inverse)
                class_weights_dict = {}
                for class_name, freq in class_frequencies.items():
                    weight = np.sqrt(1.0 / freq)
                    class_weights_dict[class_name] = weight
                
                # Normalize weights so they average to 1.0
                avg_weight = sum(class_weights_dict.values()) / len(class_weights_dict)
                class_weights_dict = {k: v / avg_weight for k, v in class_weights_dict.items()}
                
                # Log computed weights
                logger.info("⚖️  Computed Class Weights (sqrt method, from class_imbalance):")
                for class_name, weight in class_weights_dict.items():
                    logger.info(f"   '{class_name}': {weight:.4f}")
                
                return class_weights_dict
            
            # Otherwise use the training data distribution (original behavior)
            # Get value counts directly from the target column
            value_counts = target_col.astype(str).value_counts()
            
            # Filter out NaN-like values
            nan_variants = {'nan', 'NaN', 'Nan', 'NAN', 'None', '', ' '}
            value_counts = value_counts[~value_counts.index.isin(nan_variants)]
            
            if len(value_counts) == 0:
                logger.warning("⚠️  No valid class values found for class weighting")
                return {}
            
            # Compute total samples
            total_samples = value_counts.sum()
            
            # Compute class frequencies
            class_frequencies = value_counts / total_samples
            
            # Log class distribution
            logger.info("📊 Class Distribution for Target Column:")
            for class_name, freq in class_frequencies.items():
                count = value_counts[class_name]
                logger.info(f"   '{class_name}': {count} samples ({freq*100:.1f}%)")
            
            # Compute SQRT of inverse frequency weights (gentler than full inverse)
            # For 5:1 imbalance (84%/16%), this gives ~2.35x ratio instead of 5.5x
            class_weights_dict = {}
            for class_name in value_counts.index:
                freq = class_frequencies[class_name]
                weight = np.sqrt(1.0 / freq)
                class_weights_dict[class_name] = weight
            
            # Normalize weights so they average to 1.0
            avg_weight = sum(class_weights_dict.values()) / len(class_weights_dict)
            class_weights_dict = {k: v / avg_weight for k, v in class_weights_dict.items()}
            
            # Log computed weights with comparison to full inverse frequency
            logger.info("⚖️  Computed Class Weights (sqrt method, normalized):")
            for class_name, weight in class_weights_dict.items():
                freq = class_frequencies[class_name]
                full_inverse = (1.0 / freq) / ((1.0 / class_frequencies).sum() / len(class_frequencies))
                logger.info(f"   '{class_name}': {weight:.4f} (vs {full_inverse:.4f} with full inverse)")
            
            return class_weights_dict
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to compute class weights: {e}")
            logger.warning("   Continuing without class weighting")
            return {}

    def prep_for_training(self, train_df, target_col_name, target_col_type, use_class_weights=True, loss_type="adaptive", class_imbalance=None, cost_false_positive=None, cost_false_negative=None):
        # we need to get the target codec set up and the predictor mapped to the right dimensionality.
        logger.info("=" * 80)
        logger.info("🎯 PREP_FOR_TRAINING CALLED - START")
        logger.info(f"🎯 Module: {self.__class__.__module__}")
        logger.info(f"🎯 File: {__file__}")
        logger.info(f"🎯 target_col_name: {target_col_name}")
        logger.info(f"🎯 target_col_type: {target_col_type}")
        logger.info(f"🎯 use_class_weights: {use_class_weights}")
        logger.info(f"🎯 class_imbalance: {class_imbalance}")
        logger.info(f"🎯 cost_false_positive: {cost_false_positive}")
        logger.info(f"🎯 cost_false_negative: {cost_false_negative}")
        logger.info("=" * 80)
        
        # For set (classification) columns, compute default costs if not provided
        if target_col_type == "set":
            if cost_false_positive is None or cost_false_negative is None:
                # Compute default costs based on class imbalance
                target_col = train_df[target_col_name]
                
                # Count positives and negatives
                # Positive is typically the minority class (rare_label_value)
                # For now, we'll use the class with fewer samples as positive
                value_counts = target_col.value_counts()
                if len(value_counts) == 2:
                    # Binary classification
                    pos_count = value_counts.min()  # Minority class
                    neg_count = value_counts.max()  # Majority class
                    imbalance_ratio = neg_count / pos_count if pos_count > 0 else 1.0
                    
                    # Default cost calculation: cost_fp = 1.0, cost_fn = imbalance_ratio
                    cost_false_positive = 1.0
                    cost_false_negative = imbalance_ratio
                    
                    logger.info(f"💰 Default cost calculation (Bayes-optimal for imbalanced data):")
                    logger.info(f"   Positive class count: {pos_count}")
                    logger.info(f"   Negative class count: {neg_count}")
                    logger.info(f"   Imbalance ratio: {imbalance_ratio:.2f}")
                    logger.info(f"   cost_false_positive = {cost_false_positive:.2f}")
                    logger.info(f"   cost_false_negative = {cost_false_negative:.2f}")
                else:
                    # Multi-class: use symmetric costs
                    cost_false_positive = 1.0
                    cost_false_negative = 1.0
                    logger.info(f"💰 Multi-class classification: using symmetric costs (FP=1.0, FN=1.0)")
            else:
                # Validate provided costs
                if cost_false_positive <= 0 or cost_false_negative <= 0:
                    raise ValueError("cost_false_positive and cost_false_negative must be positive numbers")
                logger.info(f"💰 User-provided costs: FP cost={cost_false_positive}, FN cost={cost_false_negative}")
            
            self.cost_false_positive = cost_false_positive
            self.cost_false_negative = cost_false_negative
        else:
            # Scalar (regression): costs don't apply
            self.cost_false_positive = None
            self.cost_false_negative = None
        
        # Determine loss type based on class imbalance, cost asymmetry, and data characteristics
        # loss_type="auto" will auto-detect the best loss function
        if target_col_type == "set" and loss_type == "auto":
            logger.info("🔍 AUTO-DETECTING optimal loss function...")
            
            try:
                from featrix.neural.qa.model_advisor import ModelAdvisor, ImbalanceSeverity
                
                # Analyze class distribution
                target_col_for_analysis = train_df[target_col_name].astype(str)
                advisor = ModelAdvisor()
                distribution = advisor.analyze_class_distribution(target_col_for_analysis.values)
                
                # Determine task priority based on cost asymmetry
                # If cost_fp > cost_fn, user cares more about precision (reducing FP)
                # If cost_fn > cost_fp, user cares more about recall (catching positives)
                if cost_false_positive is not None and cost_false_negative is not None:
                    if cost_false_positive > cost_false_negative * 1.5:
                        task_priority = "precision"
                    elif cost_false_negative > cost_false_positive * 1.5:
                        task_priority = "recall"
                    else:
                        task_priority = "balanced"
                else:
                    task_priority = "balanced"
                
                # Get recommendation
                recommendation = advisor.recommend_loss_function(
                    distribution=distribution,
                    task_priority=task_priority,
                    cost_fp=cost_false_positive or 1.0,
                    cost_fn=cost_false_negative or 1.0
                )
                
                # Map to supported loss types
                recommended_loss = recommendation.loss_type
                if recommended_loss in ["focal", "cross_entropy", "prauc", "adaptive"]:
                    loss_type = recommended_loss
                elif recommended_loss == "class_balanced_focal":
                    loss_type = "focal"  # Fall back to focal with high gamma
                else:
                    loss_type = "focal"  # Default fallback
                
                logger.info(f"📊 Class Distribution: {distribution.severity.value} imbalance ({distribution.imbalance_ratio:.1f}:1)")
                logger.info(f"📊 Task Priority: {task_priority} (based on cost_fp={cost_false_positive}, cost_fn={cost_false_negative})")
                logger.info(f"🎯 AUTO-SELECTED loss_type='{loss_type}' (confidence={recommendation.confidence:.0%})")
                logger.info(f"   Reason: {recommendation.reason}")
                if recommendation.alternatives:
                    alts = ", ".join([f"{a[0]}" for a in recommendation.alternatives[:2]])
                    logger.info(f"   Alternatives: {alts}")
                
            except ImportError:
                logger.warning("⚠️  ModelAdvisor not available, defaulting to focal loss")
                loss_type = "focal"
            except Exception as e:
                logger.warning(f"⚠️  Auto-detection failed: {e}, defaulting to focal loss")
                loss_type = "focal"
        elif target_col_type == "set" and loss_type not in ["focal", "cross_entropy", "prauc", "adaptive"]:
            logger.warning(f"⚠️  Unknown loss_type '{loss_type}', defaulting to focal")
            loss_type = "focal"
        
        logger.debug(
            "prep_for_training: %s is a %s" % (target_col_name, target_col_type)
        )

        # CRITICAL: Normalize target column to consistent type BEFORE any processing
        # This prevents "1" vs "1.0" from being treated as different classes
        target_col = train_df[target_col_name].copy()
        
        # Convert to string first, then normalize numeric strings
        # This handles: 1, 1.0, "1", "1.0" all becoming "1"
        target_col_str = target_col.astype(str)
        
        # Normalize numeric strings: "1.0" -> "1", "0.0" -> "0"
        def normalize_numeric_string(val):
            if pd.isna(val) or val in ['nan', 'NaN', 'None', '', ' ']:
                return val
            try:
                # Try to convert to float, then back to int if it's a whole number
                float_val = float(val)
                if float_val.is_integer():
                    return str(int(float_val))
                return str(float_val)
            except (ValueError, TypeError):
                # Not numeric, return as-is
                return str(val)
        
        target_col_normalized = target_col_str.apply(normalize_numeric_string)
        
        # Update the dataframe with normalized target column
        train_df = train_df.copy()
        train_df[target_col_name] = target_col_normalized
        
        logger.info(f"🔧 Normalized target column '{target_col_name}' to consistent string type")
        logger.info(f"   Unique values after normalization: {sorted(target_col_normalized.unique())}")
        
        self.train_df = train_df
        self.val_df = None  # Initialize val_df (may be set later in train/val split)
        self.target_col_name = target_col_name
        
        # DISABLED 2026-01-02: Feature suggestions replaced by DynamicRelationshipExtractor
        # Load and apply features from previous training runs
        # This allows iterative feature engineering across multiple runs
        # self.train_df, self.val_df = self._load_and_apply_previous_features(self.train_df, self.val_df)
        
        # Update local reference after feature application
        train_df = self.train_df

        # DISABLED 2026-01-02: Auto-ES extension and new column detection removed
        # - ES extension is disabled (no more two-run training)
        # - New columns from feature suggestions won't happen (using DynamicRelationshipExtractor instead)
        # - DynamicRelationshipExtractor learns relationships in embedding space, not via DataFrame columns
        #
        # OLD CODE (commented out):
        # es_columns = set(self.embedding_space.column_names)
        # df_columns = set(train_df.columns) - {target_col_name}
        # new_columns = df_columns - es_columns
        # if new_columns:
        #     [warning messages about new columns]

        assert target_col_name in train_df.columns.values, (
            "__%s__ is not found in the list of columns __%s__"
            % (
                target_col_name,
                train_df.columns.values,
            )
        )

        if target_col_name in self.embedding_space.col_codecs:
            warnings.warn(
                f"""Overwriting an existing codec for column {target_col_name} from the training dataset. This may cause unexpected behavior. Also, presence of the target column in the training dataset may lead to data leakage and poor inference results."""
            )

        # The DF for downstream training must have at least one independent variable to base
        # the predictions on. We exclude the target column from the count since we need
        # feature columns to predict the target.
        cols_for_coding_count = self.embedding_space.get_columns_with_codec_count(exclude_target_column=target_col_name)
        
        # Log debug info
        total_codecs = len(self.embedding_space.col_codecs) if self.embedding_space.col_codecs else 0
        target_in_codecs = target_col_name in (self.embedding_space.col_codecs or {})
        logger.warning(f"🔍 Column codec check: total_codecs={total_codecs}, target_in_codecs={target_in_codecs}, feature_codecs={cols_for_coding_count}")
        if self.embedding_space.col_codecs:
            logger.warning(f"   Available codec columns: {list(self.embedding_space.col_codecs.keys())[:20]}{'...' if len(self.embedding_space.col_codecs) > 20 else ''}")
        
        if cols_for_coding_count < 1:
            raise Exception(
                f"Input data does not contain at least 1 feature column we can encode (found {cols_for_coding_count} feature columns, {total_codecs} total codecs). "
                f"Target column '{target_col_name}' {'is' if target_in_codecs else 'is not'} in codecs. "
                f"Please ensure the embedding space was trained on data with at least one feature column besides the target."
            )

        self.target_col_type = target_col_type

        # compute the target codec
        # TODO: I don't think we need a full-on codec here, just a tokenizer should be sufficient.
        #       But this means we need to create a separate tokenizer class.
        # Target column is already normalized above - use it directly
        target_col = self.train_df[target_col_name]
        if target_col_type == "set":
            # Compute class weights for imbalanced datasets (if enabled)
            class_weights_dict = {}
            if use_class_weights:
                class_weights_dict = self._compute_class_weights(target_col, class_imbalance=class_imbalance)
                logger.info(f"⚖️  Class weighting: ENABLED")
            else:
                logger.info(f"⚖️  Class weighting: DISABLED")
            
            # Create the codec with configurable loss type
            # FocalLoss: Better for imbalanced classification tasks (default)
            # CrossEntropyLoss: More stable for balanced data
            self.target_codec = create_set_codec(target_col, embed_dim=self.d_model, loss_type=loss_type)
            # Keep on GPU if available
            if is_gpu_available():
                self.target_codec = self.target_codec.to(get_device())
            logger.info(f"SET target members = {self.target_codec.members}")
            
            # Now convert class weights dict to tensor indexed by token ID
            if class_weights_dict and use_class_weights:
                # Determine if binary classification (excludes <UNKNOWN> from output)
                real_members = [m for m in self.target_codec.members if m != "<UNKNOWN>"]
                is_binary = len(real_members) == 2
                
                # CRITICAL FIX: For binary classification, only create weights for real classes (2 classes)
                # For multi-class, include all members (may include <UNKNOWN>)
                if is_binary:
                    # Binary: only use real members (exclude <UNKNOWN>)
                    n_classes = len(real_members)  # Should be 2
                    class_weights_tensor = torch.ones(n_classes, dtype=torch.float32)
                    
                    # Map class names to output indices (0 and 1, excluding <UNKNOWN>)
                    # The model output has classes in order: [real_class_0, real_class_1]
                    # We need to map from class names to these output indices
                    for idx, class_name in enumerate(real_members):
                        if class_name in class_weights_dict:
                            class_weights_tensor[idx] = class_weights_dict[class_name]
                    
                    logger.info(f"⚖️  Binary mode: Created class weights tensor with {n_classes} classes (excluded <UNKNOWN>)")
                else:
                    # Multi-class: include all members (may include <UNKNOWN>)
                    n_classes = len(self.target_codec.members)
                    class_weights_tensor = torch.ones(n_classes, dtype=torch.float32)
                    
                    for class_name, weight in class_weights_dict.items():
                        # Get the token ID for this class
                        if class_name in self.target_codec.members_to_tokens:
                            token_id = self.target_codec.members_to_tokens[class_name]
                            class_weights_tensor[token_id] = weight
                    
                    # Multi-class: zero <UNKNOWN> weight (backward compatibility)
                    unknown_token = self.target_codec.members_to_tokens.get('<UNKNOWN>', 0)
                    class_weights_tensor[unknown_token] = 0.0
                    logger.info(f"⚖️  Multi-class mode: Created class weights tensor with {n_classes} classes, set <UNKNOWN> weight to 0.0 (token {unknown_token})")
                
                # Keep class weights on same device as model
                if is_gpu_available():
                    class_weights_tensor = class_weights_tensor.to(get_device())
                
                # Apply class weights to the appropriate loss function
                if loss_type == "focal":
                    # Update FocalLoss with class weights via alpha parameter
                    self.target_codec.loss_fn = FocalLoss(alpha=class_weights_tensor, gamma=2.0, min_weight=0.1)
                    logger.info("🎯 Using FocalLoss with class weights")
                elif loss_type == "cross_entropy":
                    # Compute adaptive label smoothing based on dataset size and class distribution
                    # Label smoothing helps prevent overconfidence and improves generalization
                    label_smoothing = 0.0  # Default: no smoothing
                    
                    # Use distribution metadata if available for smart smoothing
                    if hasattr(self, 'distribution_metadata') and self.distribution_metadata is not None:
                        train_samples = self.distribution_metadata.get('train_samples', len(train_df))
                        n_classes = self.distribution_metadata.get('n_classes', 2)
                        imbalance_score = self.distribution_metadata.get('imbalance_score', 1.0)
                        
                        # Apply label smoothing for:
                        # 1. Small datasets (< 1000 samples) - helps prevent overfitting
                        # 2. Imbalanced datasets (score < 0.5) - prevents overconfidence on majority class
                        # 3. Many classes (>10) - smooths decision boundaries
                        
                        if train_samples < 500:
                            # Very small dataset - more aggressive smoothing
                            label_smoothing = 0.1
                            logger.info(f"📊 Small dataset ({train_samples} samples) → label_smoothing=0.1")
                        elif train_samples < 1000:
                            # Small dataset - moderate smoothing
                            label_smoothing = 0.05
                            logger.info(f"📊 Small dataset ({train_samples} samples) → label_smoothing=0.05")
                        elif imbalance_score < 0.33:
                            # Imbalanced dataset - light smoothing to prevent overconfidence
                            label_smoothing = 0.05
                            logger.info(f"📊 Imbalanced dataset (score={imbalance_score:.3f}) → label_smoothing=0.05")
                        elif n_classes > 10:
                            # Many classes - very light smoothing
                            label_smoothing = 0.02
                            logger.info(f"📊 Many classes ({n_classes}) → label_smoothing=0.02")
                        else:
                            logger.info(f"📊 Balanced dataset → no label smoothing")
                    
                    # Update CrossEntropyLoss with class weights and label smoothing
                    self.target_codec.loss_fn = nn.CrossEntropyLoss(
                        weight=class_weights_tensor,
                        label_smoothing=label_smoothing
                    )
                    logger.info(f"🎯 Using CrossEntropyLoss with class weights and label_smoothing={label_smoothing}")
                elif loss_type == "prauc":
                    # PRAUCLoss: Hard negative mining - best for reducing FP while maintaining recall
                    # Finds hardest negatives (high-scoring negs → FP) and hardest positives (low-scoring pos → FN)
                    # Penalizes when hard negatives outrank hard positives
                    from featrix.neural.set_codec import PRAUCLoss
                    self.target_codec.loss_fn = PRAUCLoss(alpha=class_weights_tensor)
                    logger.info("🎯 Using PRAUCLoss with class weights (hard negative mining for FP reduction)")
                elif loss_type == "adaptive":
                    # AdaptiveLoss: MLP learns optimal blend of focal, prauc, and cross-entropy
                    # Automatically adapts weights based on batch statistics and training progress
                    from featrix.neural.set_codec import AdaptiveLoss
                    self.target_codec.loss_fn = AdaptiveLoss(alpha=class_weights_tensor, learnable=True)
                    logger.info("🎯 Using AdaptiveLoss with class weights (MLP learns best loss blend)")
                
                # Log class weights for transparency
                logger.info("⚖️  Class Weights Applied:")
                for member, token in self.target_codec.members_to_tokens.items():
                    if token < len(class_weights_tensor):
                        logger.info(f"   '{member}' (token {token}): weight = {class_weights_tensor[token].item():.4f}")
            
            # For binary classification, exclude <UNKNOWN> from output space
            # <UNKNOWN> will be handled via margin-based abstention, not as a learned class
            real_members = [m for m in self.target_codec.members if m != "<UNKNOWN>"]
            is_binary = len(real_members) == 2
            
            if is_binary:
                # Binary mode: output only 2 classes (exclude <UNKNOWN>)
                target_dim = len(real_members)  # Should be 2
                logger.info(f"🎯 Binary classification detected: output_dim={target_dim} (excluded <UNKNOWN> from output space)")
                
                # CRITICAL: Create mapping from original token IDs to output indices for binary classification
                # Original tokens: <UNKNOWN>=0, real_class_0=1, real_class_1=2
                # Output indices: real_class_0=0, real_class_1=1
                # So we need to map: token_id -> output_idx (1->0, 2->1)
                self._binary_target_remap = {}
                for idx, class_name in enumerate(real_members):
                    if class_name in self.target_codec.members_to_tokens:
                        original_token_id = self.target_codec.members_to_tokens[class_name]
                        output_idx = idx
                        self._binary_target_remap[original_token_id] = output_idx
                logger.info(f"🎯 Binary target remapping: {self._binary_target_remap}")
            else:
                # Multi-class: keep all members (including <UNKNOWN> for backward compatibility)
                target_dim = len(self.target_codec.members)
                logger.info(f"🎯 Multi-class classification: output_dim={target_dim}")
                self._binary_target_remap = None
        elif target_col_type == "scalar":
            self.target_codec = create_scalar_codec(target_col, embed_dim=self.d_model)
            # Keep on GPU if available
            if is_gpu_available():
                self.target_codec = self.target_codec.to(get_device())
            target_dim = 1
            self._binary_target_remap = None  # Not applicable for scalar targets
        else:
            raise ValueError(
                f"Cannot create codec for column of type {target_col_type}."
            )

        self.target_type = self.target_codec.token_dtype
        logger.debug(f"self.target_type...{target_col_name} -> {self.target_type}")
        # figure out the dimensionality of the last layer of the predictor.
        # we know the input dimensionality
        # Create dummy input on device
        dummy_input = torch.randn(1, self.d_model)
        if is_gpu_available():
            dummy_input = dummy_input.to(get_device())
        # Use eval mode on the predictor to prevent contaminating the
        # batch norm stats with the dummy data.
        # This is also needed since we're passing in a batch of size 1,
        # which doesn't work with batch norm in training mode.

        # Keep predictor_base on device
        if is_gpu_available():
            self.predictor_base = self.predictor_base.to(get_device())
        logger.info("Setting predictor_base.eval()")
        self.predictor_base.eval()
        dummy_output = self.predictor_base(dummy_input)
        output_dim = dummy_output.shape[1]

        # Create a new set of codecs that contains the target, so entire DF records
        # can be tokenized. We don't want to add the target codec to the EmbeddingSpaces
        # codecs, so we create an entirely new dictionary.
        self.all_codecs = {
            col: codec for col, codec in self.embedding_space.col_codecs.items()
        }

        if self.all_codecs.get('target_col_name') is None:
            # Do not overwrite existing targets unless you want to spend a few days
            # looking for this line of code. :-P
            self.all_codecs[target_col_name] = self.target_codec

        self.is_target_scalar = isinstance(self.target_codec, AdaptiveScalarEncoder)

        self.predictor = nn.Sequential(
            self.predictor_base, nn.Linear(output_dim, target_dim)
        )
        # Keep predictor on device
        if is_gpu_available():
            self.predictor = self.predictor.to(get_device())
        return
    
    def _ensure_predictor_available(self):
        """
        Ensure predictor is available for prediction. If it's missing but we have
        predictor_base and target_codec, reconstruct it.
        
        This is needed when loading models from pickle where predictor might not
        be fully restored.
        """
        # CRITICAL: First check if we have a pending fine-tuned encoder that needs loading
        # This must happen BEFORE predictor reconstruction to ensure correct embeddings
        if hasattr(self, '_pending_state_dicts') and '_finetuned_encoder_state_dict' in self._pending_state_dicts:
            if hasattr(self, 'embedding_space') and self.embedding_space is not None:
                if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                    try:
                        encoder_state = self._pending_state_dicts['_finetuned_encoder_state_dict']
                        self.embedding_space.encoder.load_state_dict(encoder_state)
                        logger.info(f"✅ Loaded pending fine-tuned encoder ({len(encoder_state)} keys) in _ensure_predictor_available")
                        del self._pending_state_dicts['_finetuned_encoder_state_dict']
                    except Exception as e:
                        logger.error(f"❌ Failed to load fine-tuned encoder: {e}")
        
        if hasattr(self, 'predictor') and self.predictor is not None:
            return  # Already available
        
        # First, try to restore predictor_base from state_dict if needed
        predictor_base_missing = not hasattr(self, 'predictor_base') or self.predictor_base is None
        
        if predictor_base_missing:
            # Check if we have predictor state_dict - if so, we can reconstruct predictor directly
            has_predictor_state_dict = hasattr(self, '_pending_state_dicts') and 'predictor' in self._pending_state_dicts
            
            if hasattr(self, '_pending_state_dicts') and 'predictor_base' in self._pending_state_dicts:
                if has_predictor_state_dict:
                    # We have both - prefer reconstructing predictor directly
                    logger.debug("⚠️  predictor_base missing but predictor state_dict available - will reconstruct predictor directly")
                else:
                    raise AttributeError(
                        "Cannot reconstruct predictor: predictor_base state_dict found but model object is missing. "
                        "predictor_base must be provided when creating FeatrixSinglePredictor, or predictor state_dict must be available."
                    )
            elif not has_predictor_state_dict:
                raise AttributeError(
                    "Cannot reconstruct predictor: predictor_base is missing and no predictor state_dict available. "
                    "The model may not be properly loaded."
                )
        
        # Restore predictor_base from state_dict if available and predictor_base exists
        if not predictor_base_missing and hasattr(self, '_pending_state_dicts') and 'predictor_base' in self._pending_state_dicts:
            try:
                state_dict = self._pending_state_dicts['predictor_base']
                self.predictor_base.load_state_dict(state_dict)
                logger.info("✅ Restored predictor_base from state_dict")
                del self._pending_state_dicts['predictor_base']
            except Exception as e:
                logger.warning(f"⚠️  Could not load predictor_base state_dict: {e}")
                # Continue - predictor_base might already have correct weights
        
        if not hasattr(self, 'target_codec') or self.target_codec is None:
            raise AttributeError(
                "Cannot reconstruct predictor: target_codec is missing. "
                "The model may not have been trained."
            )
        
        if not hasattr(self, 'd_model') or self.d_model is None:
            raise AttributeError(
                "Cannot reconstruct predictor: d_model is missing. "
                "The model may not be properly initialized."
            )
        
        # Check if we can reconstruct predictor directly from state_dict
        if predictor_base_missing and hasattr(self, '_pending_state_dicts') and 'predictor' in self._pending_state_dicts:
            # Try to reconstruct predictor directly from state_dict
            logger.debug("🔧 Reconstructing predictor directly from state_dict (predictor_base missing)...")
            try:
                predictor_state_dict = self._pending_state_dicts['predictor']
                
                # Infer architecture from state_dict FIRST
                # Predictor is Sequential([predictor_base, Linear(output_dim, target_dim)])
                # State_dict keys will be like "0.weight", "0.bias", "1.weight", "1.bias"
                # where 0 is predictor_base and 1 is the final Linear layer
                
                # Find the final Linear layer dimensions
                final_layer_weight = None
                for key in sorted(predictor_state_dict.keys()):
                    if key.startswith('1.') and key.endswith('.weight'):
                        final_layer_weight = predictor_state_dict[key]
                        break
                
                if final_layer_weight is None:
                    # Try to find the final layer weight by looking for the last Linear layer
                    # Look for weights with shape [target_dim, output_dim] where target_dim is typically small
                    candidate_weights = []
                    for key, weight in predictor_state_dict.items():
                        if key.endswith('.weight') and len(weight.shape) == 2:
                            candidate_weights.append((key, weight))
                    
                    if candidate_weights:
                        # The final layer is typically the one with the smallest output dimension
                        # (assuming target_dim < output_dim for most cases)
                        final_layer_weight = min(candidate_weights, key=lambda x: x[1].shape[0])[1]
                
                if final_layer_weight is None:
                    raise ValueError("Cannot infer predictor architecture from state_dict - final layer weight not found")
                
                # CRITICAL: Infer target_dim from state_dict, not from target_codec
                # The state_dict has the correct number of classes the model was trained with
                target_dim = final_layer_weight.shape[0]  # First dimension is output size (target_dim)
                output_dim = final_layer_weight.shape[1]  # Second dimension is input size (output_dim)
                
                logger.debug(f"🔍 Inferred architecture from state_dict: d_model={self.d_model} -> output_dim={output_dim} -> target_dim={target_dim}")
                
                # Verify target_dim matches target_codec if available (warn if mismatch)
                if hasattr(self, 'target_codec') and self.target_codec is not None:
                    expected_target_dim = None
                    if isinstance(self.target_codec, AdaptiveScalarEncoder):
                        expected_target_dim = 1
                    else:
                        expected_target_dim = len(self.target_codec.members) if hasattr(self.target_codec, 'members') else len(self.target_codec.members_to_tokens)
                    
                    if expected_target_dim != target_dim:
                        logger.warning(
                            f"⚠️  target_dim mismatch: state_dict has {target_dim} classes, "
                            f"but target_codec has {expected_target_dim} classes. "
                            f"Using {target_dim} from state_dict (model was trained with this)."
                        )
                
                # Check if this is a SimpleMLP by looking for characteristic keys
                is_simple_mlp = '0.linear_in.weight' in predictor_state_dict or '0.linear_out.weight' in predictor_state_dict
                
                if is_simple_mlp:
                    # This is a SimpleMLP - reconstruct it properly
                    logger.debug("🔍 Detected SimpleMLP architecture - reconstructing...")
                    from featrix.neural.simple_mlp import SimpleMLP
                    
                    # Infer SimpleMLP config from state_dict
                    linear_in_weight = predictor_state_dict.get('0.linear_in.weight')
                    linear_out_weight = predictor_state_dict.get('0.linear_out.weight')
                    
                    if linear_in_weight is None or linear_out_weight is None:
                        raise ValueError("Cannot infer SimpleMLP config - missing linear_in or linear_out weights")
                    
                    d_in = linear_in_weight.shape[1]  # input dimension
                    d_hidden = linear_in_weight.shape[0]  # hidden dimension
                    d_out = linear_out_weight.shape[0]  # output dimension
                    
                    # Count hidden layers by looking for layers.0.0.weight, layers.1.0.weight, etc.
                    n_hidden_layers = 0
                    for key in predictor_state_dict.keys():
                        if key.startswith('0.layers.') and key.endswith('.0.weight'):
                            layer_idx = int(key.split('.')[2])
                            n_hidden_layers = max(n_hidden_layers, layer_idx + 1)
                    
                    # Check if batch norm is used (look for running_mean keys)
                    use_batch_norm = any('running_mean' in key for key in predictor_state_dict.keys() if '0.layers' in key)
                    
                    # Create SimpleMLP config
                    mlp_config = SimpleMLPConfig(
                        d_in=d_in,
                        d_out=d_out,
                        d_hidden=d_hidden,
                        n_hidden_layers=n_hidden_layers,
                        dropout=0.3,  # Default - can't infer from state_dict
                        use_batch_norm=use_batch_norm,
                        normalize=True,
                        residual=True
                    )
                    
                    # Create SimpleMLP
                    mlp_base = SimpleMLP(mlp_config)
                    logger.debug(f"   Created SimpleMLP: d_in={d_in}, d_hidden={d_hidden}, d_out={d_out}, n_hidden_layers={n_hidden_layers}, use_batch_norm={use_batch_norm}")
                    
                    # Create predictor
                    self.predictor = nn.Sequential(
                        mlp_base, nn.Linear(output_dim, target_dim)
                    )
                else:
                    # Simple Linear layer (old format)
                    logger.debug("🔍 Detected simple Linear architecture - reconstructing...")
                    minimal_base = nn.Linear(self.d_model, output_dim)
                    self.predictor = nn.Sequential(
                        minimal_base, nn.Linear(output_dim, target_dim)
                    )
                
                # Try to load state_dict - this might fail if architecture doesn't match exactly
                try:
                    self.predictor.load_state_dict(predictor_state_dict, strict=True)
                    logger.debug("✅ Loaded predictor state_dict (strict=True)")
                    
                    # Verify weights were loaded correctly (only log if there's a problem)
                    with torch.no_grad():
                        sample_weights = list(self.predictor.parameters())[0]
                        # Check for NaN/Inf
                        nan_count = torch.isnan(sample_weights).sum().item()
                        inf_count = torch.isinf(sample_weights).sum().item()
                        if nan_count > 0 or inf_count > 0:
                            logger.warning(f"⚠️  Found {nan_count} NaN and {inf_count} Inf values in weights!")
                except Exception as strict_err:
                    logger.warning(f"⚠️  Strict load failed: {strict_err}, trying strict=False")
                    missing_keys, unexpected_keys = self.predictor.load_state_dict(predictor_state_dict, strict=False)
                    logger.debug("✅ Loaded predictor state_dict (strict=False)")
                    if missing_keys:
                        logger.warning(f"   ⚠️  Missing keys ({len(missing_keys)}): {missing_keys[:5]}{'...' if len(missing_keys) > 5 else ''}")
                    if unexpected_keys:
                        logger.warning(f"   ⚠️  Unexpected keys ({len(unexpected_keys)}): {unexpected_keys[:5]}{'...' if len(unexpected_keys) > 5 else ''}")
                
                del self._pending_state_dicts['predictor']
                
                # Move to device
                if is_gpu_available():
                    self.predictor = self.predictor.to(get_device())
                
                # Extract predictor_base from the reconstructed predictor for context manager
                # Predictor is Sequential([predictor_base, Linear(...)])
                if isinstance(self.predictor, nn.Sequential) and len(self.predictor) >= 1:
                    self.predictor_base = self.predictor[0]
                
                logger.debug("✅ Predictor reconstructed successfully")
                return
            except Exception as e:
                logger.error(f"❌ Failed to reconstruct predictor from state_dict: {e}")
                logger.error(traceback.format_exc())
                raise AttributeError(
                    f"Cannot reconstruct predictor: failed to load from state_dict. "
                    f"predictor_base model object is required but missing. Error: {e}"
                )
        
        # Normal path: reconstruct predictor from predictor_base and target_codec
        logger.info("🔧 Reconstructing predictor from predictor_base and target_codec...")
        
        # Get output dimension from predictor_base
        dummy_input = torch.randn(1, self.d_model)
        if is_gpu_available():
            dummy_input = dummy_input.to(get_device())
            self.predictor_base = self.predictor_base.to(get_device())
        
        self.predictor_base.eval()
        with torch.no_grad():
            dummy_output = self.predictor_base(dummy_input)
        output_dim = dummy_output.shape[1]
        
        # Determine target dimension - prefer state_dict if available
        target_dim = None
        if hasattr(self, '_pending_state_dicts') and 'predictor' in self._pending_state_dicts:
            # Try to infer target_dim from state_dict first (most reliable)
            state_dict = self._pending_state_dicts['predictor']
            final_layer_weight = None
            for key in sorted(state_dict.keys()):
                if key.startswith('1.') and key.endswith('.weight'):
                    final_layer_weight = state_dict[key]
                    break
            
            if final_layer_weight is not None and len(final_layer_weight.shape) == 2:
                target_dim = final_layer_weight.shape[0]
                logger.debug(f"🔍 Inferred target_dim={target_dim} from state_dict final layer")
        
        # Fall back to target_codec if state_dict didn't provide target_dim
        if target_dim is None:
            if isinstance(self.target_codec, AdaptiveScalarEncoder):
                target_dim = 1
            else:
                # For set codecs, use the number of members
                target_dim = len(self.target_codec.members) if hasattr(self.target_codec, 'members') else len(self.target_codec.members_to_tokens)
            logger.debug(f"🔍 Using target_dim={target_dim} from target_codec")
        
        # Reconstruct predictor
        self.predictor = nn.Sequential(
            self.predictor_base, nn.Linear(output_dim, target_dim)
        )
        
        # Load state_dict if available
        if hasattr(self, '_pending_state_dicts') and 'predictor' in self._pending_state_dicts:
            try:
                state_dict = self._pending_state_dicts['predictor']
                # The state_dict might be for the full Sequential, or just the Linear layer
                # Try loading it
                self.predictor.load_state_dict(state_dict, strict=False)
                logger.info("✅ Loaded predictor state_dict")
                del self._pending_state_dicts['predictor']
            except Exception as e:
                logger.warning(f"⚠️  Could not load predictor state_dict: {e}")
                # Continue anyway - the predictor will have random weights for the final layer
                # but this might still work if only predictor_base was trained
        
        # Move to device
        if is_gpu_available():
            self.predictor = self.predictor.to(get_device())
        
        logger.info("✅ Predictor reconstructed successfully")
    
    @staticmethod
    def _create_marginal_token_batch_for_target(target_token_batch):
        """
        Replace the original token with marginal token. The values are set
        to 0 because that's a value all encoders can process, and the exact
        value doesn't matter for tokens with MARGINAL status.

        Args:
            target_token_batch:

        Returns:

        """
        batch_status = target_token_batch.status
        marginal_status = [TokenStatus.MARGINAL] * batch_status.shape[0]
        # Create tensors on same device as target_token_batch
        target_device = target_token_batch.status.device if hasattr(target_token_batch, 'status') and hasattr(target_token_batch.status, 'device') else torch.device('cpu')
        marginal_status_tensor = torch.tensor(marginal_status, device=target_device)

        marginal_values = [0] * batch_status.shape[0]
        marginal_values_tensor = torch.tensor(marginal_values, device=target_device)

        return TokenBatch.from_tensors(
            status=marginal_status_tensor,
            value=marginal_values_tensor,
        )
    

    def safe_split_train_val(self, df, target_col, test_size=0.2, random_state=None):
        logger.info(f"🔍 SPLIT DEBUG: Starting safe_split_train_val for target_col='{target_col}'")
        logger.info(f"🔍 SPLIT DEBUG: Input dataframe shape: {df.shape}")
        logger.info(f"🔍 SPLIT DEBUG: test_size={test_size}, random_state={random_state}")
        
        # DETAILED DISTRIBUTION ANALYSIS
        logger.info(f"📊 TARGET COLUMN ANALYSIS: '{target_col}'")
        
        # Check for NA/null values
        total_rows = len(df)
        null_count = df[target_col].isnull().sum()
        none_count = (df[target_col] == 'None').sum()
        empty_count = (df[target_col] == '').sum()
        
        # Count string 'nan' values (common issue when NA values get converted to strings)
        nan_string_count = (df[target_col].astype(str).str.lower() == 'nan').sum()
        
        logger.info(f"📊 Total rows: {total_rows}")
        logger.info(f"📊 Null values: {null_count} ({null_count/total_rows*100:.1f}%)")
        logger.info(f"📊 'None' string values: {none_count} ({none_count/total_rows*100:.1f}%)")
        logger.info(f"📊 Empty string values: {empty_count} ({empty_count/total_rows*100:.1f}%)")
        logger.info(f"📊 String 'nan' values: {nan_string_count} ({nan_string_count/total_rows*100:.1f}%)")
        
        # Filter out problematic values including string 'nan'
        # CRITICAL: Also filter out string 'nan' which commonly appears when NA values are converted to strings
        valid_mask = ~(
            df[target_col].isnull() | 
            (df[target_col] == 'None') | 
            (df[target_col] == '') |
            (df[target_col].astype(str).str.lower() == 'nan')  # Filter string 'nan', 'NaN', 'NAN', etc.
        )
        valid_rows = valid_mask.sum()
        filtered_df = df[valid_mask].copy()
        
        logger.info(f"📊 Valid (non-null/non-empty) rows: {valid_rows} ({valid_rows/total_rows*100:.1f}%)")
        logger.info(f"📊 Rows excluded due to missing/invalid targets: {total_rows - valid_rows}")
        
        if valid_rows == 0:
            raise ValueError(f"No valid target values found in column '{target_col}' after filtering nulls/empties")
        
        # Analyze the filtered data distribution
        unique_categories = filtered_df[target_col].unique()
        value_counts = filtered_df[target_col].value_counts()
        
        logger.info(f"🔍 SPLIT DEBUG: After filtering - Found {len(unique_categories)} unique categories: {unique_categories}")
        logger.info(f"🔍 SPLIT DEBUG: After filtering - Category counts: {value_counts.to_dict()}")
        
        # Work with filtered dataframe for all subsequent analysis
        df = filtered_df
        
        # Analyze category distribution and identify validation-suitable categories
        categories_with_sufficient_samples = []
        categories_excluded_from_validation = []
        single_sample_categories = []
        
        # Identify categories that can be safely split for validation
        for category, count in value_counts.items():
            min_samples_needed = max(2, int(1 / test_size))  # Need at least 2 samples, or enough for test_size split
            if count >= min_samples_needed:
                categories_with_sufficient_samples.append((category, count))
            elif count == 1:
                single_sample_categories.append((category, count))
            else:
                categories_excluded_from_validation.append((category, count))
        
        # Log the analysis
        logger.info(f"📊 SPLIT ANALYSIS: Categories with sufficient samples for validation (>={max(2, int(1/test_size))}): {len(categories_with_sufficient_samples)}")
        if categories_with_sufficient_samples:
            sorted_sufficient = sorted(categories_with_sufficient_samples, key=lambda x: x[1], reverse=True)
            top_categories = sorted_sufficient[:3]  # Show top 3 most frequent
            logger.info(f"📊 Top categories with sufficient samples: {[(cat, count) for cat, count in top_categories]}")
        
        if single_sample_categories:
            logger.warning(f"⚠️  Categories with only 1 sample (will use for training only): {len(single_sample_categories)} categories")
            logger.warning(f"⚠️  Single sample categories: {[(cat, count) for cat, count in single_sample_categories[:5]]}")  # Show first 5
        
        if categories_excluded_from_validation:
            logger.warning(f"⚠️  Categories with insufficient samples for validation: {len(categories_excluded_from_validation)} categories")
            logger.warning(f"⚠️  Excluded categories: {[(cat, count) for cat, count in categories_excluded_from_validation[:5]]}")  # Show first 5

        train_df = pd.DataFrame()
        val_df = pd.DataFrame()
        
        # Store metadata about excluded categories for later use
        self.validation_excluded_categories = {
            'single_sample': [cat for cat, _ in single_sample_categories],
            'insufficient_samples': [cat for cat, _ in categories_excluded_from_validation],
            'total_excluded_samples': sum(count for _, count in single_sample_categories + categories_excluded_from_validation)
        }

        # Iterate over each unique category in the target column
        for i, category in enumerate(unique_categories):
            logger.info(f"🔍 SPLIT DEBUG: Processing category {i+1}/{len(unique_categories)}: '{category}'")
            
            category_df = df[df[target_col] == category]
            category_count = len(category_df)
            
            # Determine minimum samples needed for splitting
            min_samples_for_split = max(2, int(1 / test_size))
            
            if category_count < min_samples_for_split:
                # Add all samples to training set - cannot validate on categories with insufficient samples
                logger.warning(f"🔍 SPLIT DEBUG: Category '{category}' has {category_count} samples (< {min_samples_for_split} needed) - adding all to training set")
                train_df = pd.concat([train_df, category_df])
                categories_excluded_from_validation.append((category, category_count))
                continue
            
            logger.info(f"🔍 SPLIT DEBUG: Category '{category}' has {category_count} samples - splitting for validation")

            try:
                logger.info(f"🔍 SPLIT DEBUG: About to call train_test_split for category '{category}'")
                # Use sklearn's split for categories with sufficient samples
                category_train, category_val = train_test_split(
                    category_df,
                    test_size=test_size,
                    random_state=random_state,
                    stratify=None
                )
                logger.info(f"🔍 SPLIT DEBUG: train_test_split succeeded for category '{category}': train={len(category_train)}, val={len(category_val)}")

                train_df = pd.concat([train_df, category_train])
                val_df = pd.concat([val_df, category_val])
                logger.info(f"🔍 SPLIT DEBUG: After concat for category '{category}': total_train={len(train_df)}, total_val={len(val_df)}")
                
            except ValueError as e:
                logger.warning(f"🔍 SPLIT DEBUG: ValueError for category '{category}': {e}")
                if "empty" in str(e).lower():
                    # If split fails, add all samples to training set
                    logger.info(f"🔍 SPLIT DEBUG: Split failed for category '{category}', adding all {category_count} samples to training set")
                    train_df = pd.concat([train_df, category_df])
                    categories_excluded_from_validation.append((category, category_count))
                else:
                    logger.error(f"🔍 SPLIT DEBUG: Unexpected ValueError for category '{category}': {e}")
                    raise e
            except Exception as e:
                logger.error(f"🔍 SPLIT DEBUG: Unexpected exception for category '{category}': {type(e).__name__}: {e}")
                raise e

        # Log final validation coverage
        total_samples = len(df)
        validation_samples = len(val_df)
        excluded_samples = self.validation_excluded_categories['total_excluded_samples']
        validation_coverage = (validation_samples / total_samples) * 100 if total_samples > 0 else 0
        
        logger.info(f"🔍 SPLIT DEBUG: Completed safe_split_train_val - final train={len(train_df)}, val={len(val_df)}")
        logger.info(f"📊 VALIDATION COVERAGE: {validation_samples}/{total_samples} samples ({validation_coverage:.1f}%) can be validated")
        logger.info(f"📊 EXCLUDED FROM VALIDATION: {excluded_samples} samples across {len(self.validation_excluded_categories['single_sample']) + len(self.validation_excluded_categories['insufficient_samples'])} categories")
        
        # Compute distribution metadata for hyperparameter selection
        self.distribution_metadata = {
            'n_classes': len(unique_categories),
            'total_samples': total_samples,
            'train_samples': len(train_df),
            'val_samples': len(val_df),
            'validation_coverage': validation_coverage,
            'test_size': test_size
        }
        
        # Add class distribution for classification tasks
        if len(train_df) > 0:
            train_value_counts = train_df[target_col].value_counts()
            self.distribution_metadata['train_class_counts'] = train_value_counts.to_dict()
            self.distribution_metadata['train_class_ratios'] = (train_value_counts / len(train_df)).to_dict()
            
            # Compute imbalance metrics
            if len(train_value_counts) >= 2:
                majority_count = train_value_counts.iloc[0]
                minority_count = train_value_counts.iloc[-1]
                
                # Traditional ratio format (e.g., 7.0 means "7:1 ratio")
                imbalance_ratio = majority_count / max(minority_count, 1)
                self.distribution_metadata['imbalance_ratio'] = imbalance_ratio
                
                # Normalized imbalance score [0,1] where:
                # 1.0 = perfectly balanced (50/50)
                # 0.5 = moderate imbalance (e.g., 67/33 or 2:1)
                # 0.1 = severe imbalance (e.g., 91/9 or 10:1)
                # 0.0 = extreme imbalance (one class completely dominates)
                minority_ratio = minority_count / max(majority_count, 1)
                self.distribution_metadata['imbalance_score'] = minority_ratio
                
                self.distribution_metadata['majority_class'] = train_value_counts.index[0]
                self.distribution_metadata['minority_class'] = train_value_counts.index[-1]
        
        if len(val_df) > 0:
            val_value_counts = val_df[target_col].value_counts()
            self.distribution_metadata['val_class_counts'] = val_value_counts.to_dict()
            self.distribution_metadata['val_class_ratios'] = (val_value_counts / len(val_df)).to_dict()
        
        # Log availability of distribution metadata for hyperparameter selection
        logger.info(f"📊 DISTRIBUTION METADATA: Available for hyperparameter selection")
        logger.info(f"📊   → n_classes={self.distribution_metadata['n_classes']}, train_samples={self.distribution_metadata['train_samples']}")
        if 'imbalance_ratio' in self.distribution_metadata:
            logger.info(f"📊   → imbalance_ratio={self.distribution_metadata['imbalance_ratio']:.2f}:1, imbalance_score={self.distribution_metadata['imbalance_score']:.3f}")
            logger.info(f"📊   → {self.distribution_metadata['majority_class']} / {self.distribution_metadata['minority_class']}")
        
        # DETAILED FINAL DISTRIBUTION ANALYSIS
        logger.info(f"")
        logger.info(f"📊 ============== FINAL DISTRIBUTION ANALYSIS ==============")
        
        # Training set distribution
        if len(train_df) > 0:
            train_value_counts = train_df[target_col].value_counts()
            logger.info(f"📈 TRAINING SET ({len(train_df)} samples):")
            for category, count in train_value_counts.items():
                percentage = (count / len(train_df)) * 100
                logger.info(f"📈   '{category}': {count} samples ({percentage:.1f}%)")
        else:
            logger.warning(f"📈 TRAINING SET: EMPTY!")
        
        # Validation set distribution  
        if len(val_df) > 0:
            val_value_counts = val_df[target_col].value_counts()
            logger.info(f"📉 VALIDATION SET ({len(val_df)} samples):")
            for category, count in val_value_counts.items():
                percentage = (count / len(val_df)) * 100
                logger.info(f"📉   '{category}': {count} samples ({percentage:.1f}%)")
                
            # Check if validation maintains class balance
            if len(train_df) > 0:
                logger.info(f"⚖️  CLASS BALANCE ANALYSIS:")
                train_ratios = train_df[target_col].value_counts(normalize=True)
                val_ratios = val_df[target_col].value_counts(normalize=True)
                
                for category in train_ratios.index:
                    train_pct = train_ratios[category] * 100
                    val_pct = val_ratios.get(category, 0) * 100
                    balance_diff = abs(train_pct - val_pct)
                    
                    balance_status = "✅" if balance_diff < 10 else "⚠️" if balance_diff < 20 else "❌"
                    logger.info(f"⚖️    '{category}': Train {train_pct:.1f}% vs Val {val_pct:.1f}% (diff: {balance_diff:.1f}%) {balance_status}")
        else:
            logger.warning(f"📉 VALIDATION SET: EMPTY!")
        
        logger.info(f"📊 ========================================================")
        logger.info(f"")
        
        # Provide context-appropriate warning about low validation coverage
        # Expected validation coverage is test_size * 100, but warn only if significantly lower (less than 50% of expected)
        expected_validation_coverage = test_size * 100
        coverage_threshold = expected_validation_coverage * 0.5  # Warn if we get less than half the expected validation data
        
        if validation_coverage < coverage_threshold:
            num_excluded_categories = len(self.validation_excluded_categories['single_sample']) + len(self.validation_excluded_categories['insufficient_samples'])
            num_total_categories = len(unique_categories)
            
            if num_excluded_categories > 0:
                if num_total_categories > 10:
                    # Many categories scenario
                    logger.warning(f"⚠️  LOW VALIDATION COVERAGE: Only {validation_coverage:.1f}% of data can be validated (expected {expected_validation_coverage:.1f}%) - {num_excluded_categories}/{num_total_categories} categories have insufficient samples")
                elif num_total_categories <= 2:
                    # Binary or very few classes - different message
                    logger.warning(f"⚠️  LOW VALIDATION COVERAGE: Only {validation_coverage:.1f}% of data can be validated (expected {expected_validation_coverage:.1f}%) - one or more classes have insufficient samples for splitting")
                else:
                    # Few categories but some excluded
                    logger.warning(f"⚠️  LOW VALIDATION COVERAGE: Only {validation_coverage:.1f}% of data can be validated (expected {expected_validation_coverage:.1f}%) - {num_excluded_categories} categories have insufficient samples")
            else:
                # Coverage is low but no categories were explicitly excluded - might be due to split ratio or data distribution
                logger.warning(f"⚠️  LOW VALIDATION COVERAGE: Only {validation_coverage:.1f}% of data in validation set (expected {expected_validation_coverage:.1f}%)")
        
        return train_df, val_df
    
    def get_validation_metadata(self):
        """
        Returns metadata about which categories were excluded from validation.
        
        Returns:
            dict: Contains information about categories that couldn't be validated:
                - 'single_sample': List of categories with only 1 sample
                - 'insufficient_samples': List of categories with too few samples for splitting  
                - 'total_excluded_samples': Total number of samples excluded from validation
                - 'excluded_categories_count': Total number of categories excluded
        """
        if self.validation_excluded_categories is None:
            return None
            
        metadata = self.validation_excluded_categories.copy()
        metadata['excluded_categories_count'] = (
            len(metadata['single_sample']) + len(metadata['insufficient_samples'])
        )
        return metadata
    
    def get_distribution_metadata(self):
        """
        Returns class distribution metadata for hyperparameter selection.
        
        This metadata can be used by models to automatically select optimal hyperparameters
        based on dataset characteristics such as class imbalance, sample size, etc.
        
        Returns:
            dict: Contains distribution information including:
                - 'n_classes': Number of unique classes
                - 'total_samples': Total number of samples
                - 'train_samples': Number of training samples
                - 'val_samples': Number of validation samples
                - 'validation_coverage': Percentage of data in validation set
                - 'test_size': Test size ratio used for splitting
                - 'train_class_counts': Dict of class counts in training set
                - 'train_class_ratios': Dict of class ratios in training set
                - 'val_class_counts': Dict of class counts in validation set (if available)
                - 'val_class_ratios': Dict of class ratios in validation set (if available)
                - 'imbalance_ratio': Ratio of majority to minority class (e.g., 7.0 = "7:1 ratio")
                - 'imbalance_score': Normalized imbalance [0,1] where 1.0=balanced, 0.0=extreme
                - 'majority_class': Name of the majority class (if binary/multiclass)
                - 'minority_class': Name of the minority class (if binary/multiclass)
                
            None: If distribution metadata hasn't been computed yet (before training split)
            
        Example usage for hyperparameter selection:
            ```python
            dist = predictor.get_distribution_metadata()
            
            # Use normalized score for clean threshold logic
            if dist['imbalance_score'] < 0.1:  # < 10% minority
                use_focal_loss = True
                focal_gamma = 3.0
            elif dist['imbalance_score'] < 0.33:  # < 33% minority  
                use_focal_loss = True
                focal_gamma = 2.0
            else:  # Relatively balanced
                use_focal_loss = False
            ```
        """
        return self.distribution_metadata

    def get_good_val_pos_label(self, val_targets):
        """
        Very chatty logging but I want to leave it so we can debug this stuff.
        """
        val_pos_label = None
        try:
            value_counts = val_targets.value_counts(ascending=True)
            logger.info(f">>> target column value_counts = {value_counts.to_dict()}")
            for vv, _ in value_counts.items():
                if val_pos_label is not None:
                    break
                logger.info(f"here we go... checking __{vv}__...")
                if (vv != vv) or (vv is None):
                    logger.info(f"got NaN/None")
                    continue
                if type(vv) == str:
                    logger.info(f"got a str")
                    if len(vv) == 0:
                        logger.info(f"got a str... but it's empty")
                        continue
                    try:
                        if len(vv.strip()) == 0:
                            logger.info(f"got a str... but it's whitespace")
                            continue
                        val_pos_label = vv
                        logger.info(f"set val_pos_label = {val_pos_label}")
                        break   # this breaks out of the try, !@&#*(# python)
                    except:
                        traceback.print_exc()
                else:
                    val_pos_label = vv
                    logger.info(f"set val_pos_label = {val_pos_label}... type() = {type(val_pos_label)}")
                    break

            # least_popular_value = val_targets.value_counts().idxmin()
            # print("The least popular value is:", least_popular_value)
        except:
            traceback.print_exc()
            logger.info(f"CHECK STDOUT FOR CRASH (stderr now redirected to stdout)")
            # Pick the first non-nan unique value as the positive label, arbitrarily.
            val_list = val_targets.unique().tolist()
            logger.info(f">>> target values found in target: {val_list}")
            for vv in val_list:
                if val_pos_label is not None:
                    break
                # vv != vv checks whether vv is NaN. In principle, math.isnan could be used,
                # but that fails on string input, so for the sake of clarity we use a simple comparison.
                if type(vv) == str:
                    if len(vv) == 0:
                        continue
                    try:
                        if len(vv.strip()) == 0:
                            continue
                    except:
                        traceback.print_exc()
                        print("Continuing...")
                if (vv != vv) or (vv is None):
                    val_pos_label = vv
                    break

        return val_pos_label
    
    def _normalize_pos_label_to_codec_format(self, pos_label) -> Any:
        """
        Normalize pos_label to match what the codec's detokenize() will return.
        
        The codec stores members as-is from the dataframe, but when detokenizing,
        it returns values from tokens_to_members. There can be type mismatches
        (e.g., boolean True vs string 'True') that cause metrics to fail.
        
        Args:
            pos_label: The positive label to normalize
            
        Returns:
            The normalized label that will match codec's detokenize output
        """
        if not hasattr(self, 'target_codec'):
            return pos_label
        
        # For SetCodec, check what values it can actually produce
        if isinstance(self.target_codec, SetCodec):
            # Get all possible values the codec can detokenize
            codec_values = list(self.target_codec.tokens_to_members.values())
            
            # Try exact match first
            if pos_label in codec_values:
                return pos_label
            
            # Try string conversion
            pos_label_str = str(pos_label)
            if pos_label_str in codec_values:
                logger.info(f"🔧 Normalized pos_label: {pos_label!r} (type: {type(pos_label).__name__}) → {pos_label_str!r} (string) to match codec format")
                return pos_label_str
            
            # Try converting codec values to pos_label's type
            for codec_val in codec_values:
                try:
                    # Try converting codec value to pos_label's type
                    converted = type(pos_label)(codec_val)
                    if converted == pos_label:
                        logger.info(f"🔧 Normalized pos_label: {pos_label!r} → {codec_val!r} (codec format) to match codec output")
                        return codec_val
                except (ValueError, TypeError):
                    continue
            
            # Try reverse: convert pos_label to codec value's type
            for codec_val in codec_values:
                try:
                    converted = type(codec_val)(pos_label)
                    if converted == codec_val:
                        logger.info(f"🔧 Normalized pos_label: {pos_label!r} → {codec_val!r} (codec format) to match codec output")
                        return codec_val
                except (ValueError, TypeError):
                    continue
            
            # If all else fails, log warning but return original
            logger.warning(f"⚠️  Could not normalize pos_label {pos_label!r} to match codec format")
            logger.warning(f"   Codec values: {codec_values}")
            logger.warning(f"   This may cause type mismatch in metrics computation")
        
        return pos_label
    
    def should_compute_binary_metrics(self):
        """Returns True if binary metrics should be computed, False otherwise.

        This essentially checks whether the target variable is a categorical 
        variable with 2 options. 
        
        Result is cached to avoid recomputing and spamming logs.
        """
        # Return cached result if already computed
        if self._is_binary_cached is not None:
            return self._is_binary_cached
        
        logger.info("=" * 80)
        logger.info("🔍🔍🔍 SHOULD_COMPUTE_BINARY_METRICS CALLED (first time) 🔍🔍🔍")
        logger.info("=" * 80)
        
        # Check if target_codec exists
        if not hasattr(self, 'target_codec'):
            logger.error("❌ self.target_codec DOES NOT EXIST!")
            logger.error(f"   Available attributes: {[a for a in dir(self) if 'target' in a.lower()]}")
            logger.info("=" * 80)
            self._is_binary_cached = False
            return False
        
        logger.info(f"✅ self.target_codec EXISTS")
        logger.info(f"   Type: {type(self.target_codec)}")
        logger.info(f"   Module: {type(self.target_codec).__module__}")
        logger.info(f"   Class name: {type(self.target_codec).__name__}")
        
        # Check if it's a SetEncoder OR SetCodec (target uses SetCodec which has loss function)
        is_set_encoder = isinstance(self.target_codec, SetEncoder)
        is_set_codec = isinstance(self.target_codec, SetCodec)
        is_set = is_set_encoder or is_set_codec
        
        logger.info(f"   isinstance(self.target_codec, SetEncoder) = {is_set_encoder}")
        logger.info(f"   isinstance(self.target_codec, SetCodec) = {is_set_codec}")
        logger.info(f"   is_set (either) = {is_set}")
        logger.info(f"   SetEncoder type: {SetEncoder}")
        logger.info(f"   SetCodec type: {SetCodec}")

        if is_set:
            # Check members attribute
            if not hasattr(self.target_codec, 'members'):
                logger.error(f"❌ target_codec is SetEncoder/SetCodec but has NO 'members' attribute!")
                logger.error(f"   Available attributes: {dir(self.target_codec)}")
                logger.info("=" * 80)
                self._is_binary_cached = False
                return False
            
            members = self.target_codec.members
            logger.info(f"✅ members attribute EXISTS")
            logger.info(f"   Type: {type(members)}")
            logger.info(f"   Length: {len(members)}")
            logger.info(f"   Contents (full): {list(members)}")
            
            # Check for <UNKNOWN> in members
            has_unknown = "<UNKNOWN>" in members
            logger.info(f"   '<UNKNOWN>' in members? {has_unknown}")
            
            # Filter out <UNKNOWN>
            real_members = [m for m in members if m != "<UNKNOWN>"]
            logger.info(f"   real_members (after filtering <UNKNOWN>): {real_members}")
            logger.info(f"   real_members length: {len(real_members)}")
            
            # Determine if binary
            is_binary = len(real_members) == 2
            logger.info(f"   len(real_members) == 2? {is_binary}")
            
            logger.info(f"🎯 FINAL RESULT: is_binary = {is_binary}")
            logger.info("=" * 80)
            
            # Cache the result
            self._is_binary_cached = is_binary
            return is_binary
        else:
            logger.info(f"❌ target_codec is NOT a SetEncoder or SetCodec")
            logger.info(f"   Type: {type(self.target_codec)}")
            logger.info(f"   Expected: SetEncoder or SetCodec")
            logger.info(f"🎯 FINAL RESULT: is_binary = False")
            logger.info("=" * 80)
            
            # Cache the result
            self._is_binary_cached = False
            return False


    def print_label_distribution(self, train_df, val_df, target_col):
        """Print the distribution of labels in train and validation datasets"""
        logger.info(f"📊 ============== LABEL DISTRIBUTION ANALYSIS ==============")
        
        # Train distribution
        train_counts = train_df[target_col].value_counts()
        train_total = len(train_df)
        logger.info(f"📈 TRAINING SET ({train_total} samples):")
        for label, count in train_counts.items():
            percentage = (count / train_total) * 100
            logger.info(f"📈   '{label}': {count} samples ({percentage:.1f}%)")
        
        # Validation distribution - handle empty val_df case
        val_total = len(val_df)
        if val_total > 0 and len(val_df.columns) > 0 and target_col in val_df.columns:
            val_counts = val_df[target_col].value_counts()
            logger.info(f"📉 VALIDATION SET ({val_total} samples):")
            for label, count in val_counts.items():
                percentage = (count / val_total) * 100
                logger.info(f"📉   '{label}': {count} samples ({percentage:.1f}%)")
        else:
            # Empty val_df - create empty Series for consistency
            val_counts = pd.Series(dtype='int64')
            logger.info(f"📉 VALIDATION SET ({val_total} samples):")
            if val_total == 0:
                logger.warning(f"📉 VALIDATION SET: EMPTY (0 samples)")
        
        # Class balance analysis
        logger.info(f"⚖️  CLASS BALANCE ANALYSIS:")
        for label in train_counts.index:
            train_pct = (train_counts[label] / train_total) * 100
            val_pct = (val_counts[label] / val_total) * 100 if label in val_counts and val_total > 0 else 0
            diff = abs(train_pct - val_pct)
            status = "✅" if diff < 5.0 else "⚠️"
            logger.info(f"⚖️    '{label}': Train {train_pct:.1f}% vs Val {val_pct:.1f}% (diff: {diff:.1f}%) {status}")
        
        logger.info(f"📊 ========================================================")
        
        # Store class distribution for later use (e.g., in warnings)
        # Convert to regular dicts with native Python types for JSON serialization
        # Convert all labels to strings before sorting to avoid TypeError when mixing str and int
        # Create a mapping from original labels to string labels for lookup
        train_label_set = {str(label) for label in train_counts.index}
        val_label_set = {str(label) for label in val_counts.index} if len(val_counts) > 0 else set()
        all_labels_str = sorted(train_label_set | val_label_set)
        
        # Build mapping from string labels back to original labels for lookup
        train_label_map = {str(label): label for label in train_counts.index}
        val_label_map = {str(label): label for label in val_counts.index} if len(val_counts) > 0 else {}
        
        total_counts = {}
        for label_str in all_labels_str:
            # Look up using original label type, fallback to 0 if not found
            train_orig = train_label_map.get(label_str)
            val_orig = val_label_map.get(label_str)
            train_count = train_counts.get(train_orig, 0) if train_orig is not None else 0
            val_count = val_counts.get(val_orig, 0) if val_orig is not None else 0
            total_counts[label_str] = train_count + val_count
        
        self.class_distribution = {
            'train': {label_str: int(train_counts.get(train_label_map.get(label_str), 0)) for label_str in all_labels_str},
            'val': {label_str: int(val_counts.get(val_label_map.get(label_str), 0)) for label_str in all_labels_str},
            'total': {label_str: int(count) for label_str, count in total_counts.items()},
            'train_total': int(train_total),
            'val_total': int(val_total),
            'total_total': int(train_total + val_total),
        }
        
        return

    def _compute_dataset_hash(self) -> Optional[str]:
        """
        Compute and cache the dataset hash for monitor reporting.
        
        Returns:
            Dataset hash string, or None if computation fails
        """
        try:
            from featrix_monitor import generate_dataset_hash
            dataset_hash = generate_dataset_hash(self.train_df)
            logger.info(f"📊 Dataset hash: {dataset_hash}")
            return dataset_hash
        except Exception as e:
            logger.debug(f"Could not generate dataset hash: {e}")
            return None

    def _setup_training_parameters(self, fine_tune: bool):
        """
        Configure trainable parameters based on fine-tuning setting.
        
        Args:
            fine_tune: If True, train both predictor and encoder. If False, freeze encoder.
            
        Returns:
            Tuple of (params_list, trainable_count, frozen_count)
        """
        # Count total parameters for logging
        predictor_params = list(self.predictor.parameters())
        encoder_params = list(self.embedding_space.encoder.parameters())
        
        predictor_count = sum(p.numel() for p in predictor_params)
        encoder_count = sum(p.numel() for p in encoder_params)
        total_count = predictor_count + encoder_count
        
        if fine_tune:
            logger.info(f"   ✅ FINE-TUNING ENABLED: training both predictor AND encoder parameters")
            logger.info(f"   🔓 Encoder is trainable - will adapt to your target column")
            params = predictor_params + encoder_params
            trainable_count = total_count
            frozen_count = 0
            # CRITICAL: Set flag so we know to save the fine-tuned encoder
            self._encoder_was_finetuned = True
            logger.info(f"   💾 Encoder will be saved when model is checkpointed")
        else:
            logger.info(f"   ⚠️  FINE-TUNING DISABLED: training ONLY predictor parameters (encoder frozen)")
            logger.info(f"   🔒 Encoder is frozen - only predictor will learn")
            # CRITICAL: Convert to list to ensure it's iterable and not consumed
            # Using generator directly can cause issues when iterating multiple times
            params = predictor_params
            trainable_count = predictor_count
            frozen_count = encoder_count
            # Clear the flag - encoder wasn't fine-tuned
            self._encoder_was_finetuned = False
            
            # Actually freeze encoder parameters
            for param in encoder_params:
                param.requires_grad = False
            logger.info(f"   🔒 Encoder parameters frozen: {encoder_count:,} params ({encoder_count/total_count:.1%} of model)")
        
        return params, trainable_count, frozen_count

    def _calculate_adaptive_learning_rate(self, optimizer_params=None, fine_tune=False):
        """
        Calculate adaptive learning rate based on dataset size.
        
        Dynamically set LR based on dataset size only (NOT batch size).
        Batch size scaling doesn't help with unstable/imbalanced datasets.
        
        CRITICAL: LRTimeline uses a simple warmup schedule.
        We use conservative base LR values to prevent instability.
        
        Args:
            optimizer_params: Optional dict with 'lr' key. If provided, used as a hint but
                             still adjusted based on dataset size to prevent collapse.
            fine_tune: If True, scales down the LR by 5x to protect pre-trained embeddings.
            
        Returns:
            Dict with 'lr' and 'weight_decay' keys
        """
        n_samples = len(self.train_df)
        
        # ALWAYS calculate dataset-size-appropriate base LR
        # This prevents using a fixed LR that's too low for the dataset size
        # SIGNIFICANTLY INCREASED base LRs - previous values were far too conservative
            # LRTimeline uses simple warmup + cosine decay schedule
        if n_samples < 500:
            # Tiny dataset: max_lr = 1.2e-3 (0.0012)
            adaptive_lr = 4e-04
        elif n_samples < 1000:
            # Very small dataset: max_lr = 1.8e-3 (0.0018)
            adaptive_lr = 6e-04
        elif n_samples < 2000:
            # Small dataset: max_lr = 2.4e-3 (0.0024)
            adaptive_lr = 8e-04
        elif n_samples < 5000:
            # Small-medium dataset: max_lr = 3.0e-3 (0.003)
            adaptive_lr = 1e-03
        elif n_samples < 10000:
            # Medium dataset: max_lr = 3.6e-3 (0.0036)
            adaptive_lr = 1.2e-03
        elif n_samples < 20000:
            # Medium-large dataset: max_lr = 4.5e-3 (0.0045)
            adaptive_lr = 1.5e-03
        else:
            # Large dataset: max_lr = 6.0e-3 (0.006)
            adaptive_lr = 2e-03
        
        # Apply fine_tune scaling: reduce LR by 2x (was 3x, too aggressive)
        # Still protects pre-trained embeddings but allows meaningful learning
        if fine_tune:
            adaptive_lr = adaptive_lr / 2.0
        
        # If user provided an LR, use it as a hint but ensure it's not too low
        # This prevents collapse when a fixed LR (like 1e-5) is too low for the dataset
        if optimizer_params is not None and "lr" in optimizer_params:
            provided_lr = optimizer_params.get("lr")
            # Use the higher of: provided LR or adaptive LR
            # This ensures we don't use a LR that's too low for the dataset size
            final_lr = max(provided_lr, adaptive_lr)
            if final_lr != provided_lr:
                logger.info(f"📊 LR ADJUSTMENT: Provided LR {provided_lr:.6e} too low for dataset size ({n_samples} samples)")
                logger.info(f"   Adjusted to {final_lr:.6e} to prevent collapse (minimum safe LR for this dataset)")
                if fine_tune:
                    logger.info(f"   Fine-tune mode: LR scaled down by 2x to protect pre-trained embeddings")
                
                # Add event to timeline: Adaptive LR adjustment
                if hasattr(self, '_training_timeline'):
                    lr_adjust_event = {
                        "epoch": -1,  # Before training starts
                        "event_type": "lr_adjustment",
                        "adjustment_type": "adaptive_initial",
                        "old_lr": float(provided_lr),
                        "new_lr": float(final_lr),
                        "reason": f"Provided LR too low for dataset size ({n_samples} samples) - adjusted to prevent collapse",
                        "dataset_size": n_samples,
                        "time_now": time.time(),
                    }
                    self._training_timeline.append(lr_adjust_event)
            else:
                logger.info(f"📊 Using provided LR: {final_lr:.6e} (appropriate for dataset size)")
                if fine_tune:
                    logger.info(f"   Fine-tune mode: LR scaled down by 2x to protect pre-trained embeddings")
        else:
            final_lr = adaptive_lr
        
        # Log LR schedule information
        logger.info(f"📊 ADAPTIVE LR + REGULARIZATION (ONECYCLE-AWARE):")
        logger.info(f"   Dataset size: {n_samples} samples → Base LR: {final_lr:.6e}")
        if fine_tune:
            logger.info(f"   Fine-tune mode: LR scaled down by 2x to protect pre-trained embeddings")
        logger.info(f"   LRTimeline peak: {final_lr:.6e} (reached during warmup)")
        logger.info(f"   Starting LR: {final_lr * 3.0 / 25.0:.6e} (warmup from 3x/25)")
        logger.info(f"   🎯 INCREASED: Base LRs 5-10x higher to ensure actual learning!")
        
        # Adaptive weight decay: smaller datasets need MORE regularization to prevent overfitting
        # This is critical - without weight decay, small datasets will overfit badly
        if n_samples < 500:
            weight_decay = 0.1  # Very aggressive regularization for tiny datasets
        elif n_samples < 1000:
            weight_decay = 0.05  # Strong regularization for small datasets
        elif n_samples < 5000:
            weight_decay = 0.01  # Moderate regularization
        elif n_samples < 20000:
            weight_decay = 0.001  # Light regularization
        else:
            weight_decay = 0.0001  # Minimal regularization for large datasets
        
        # Build result dict
        result = {"lr": final_lr, "weight_decay": weight_decay}
        
        # If optimizer_params was provided, merge in any other params (but LR and weight_decay are set above)
        if optimizer_params is not None:
            result.update({k: v for k, v in optimizer_params.items() if k not in ["lr", "weight_decay"]})
            # Override weight_decay only if it was explicitly provided
            if "weight_decay" in optimizer_params:
                result["weight_decay"] = optimizer_params["weight_decay"]
                logger.info(f"📊 Using provided weight_decay: {result['weight_decay']}")
            else:
                logger.info(f"📊 Adaptive weight_decay: {result['weight_decay']} (L2 regularization)")
        else:
            logger.info(f"📊 Adaptive weight_decay: {weight_decay} (L2 regularization)")
        
        return result

    def _create_optimizer(self, params, optimizer_params, encoder_params=None, predictor_params=None, 
                         encoder_lr=None, predictor_lr=None):
        """
        Create the most efficient available optimizer.
        
        Priority: 8-bit AdamW (best memory) > Fused AdamW (best speed) > Regular AdamW
        
        If encoder_params and predictor_params are provided with separate LRs, creates param groups.
        This allows different learning rates for encoder vs predictor to fix gradient flow imbalance.
        
        Args:
            params: List of parameters to optimize (used if encoder_params/predictor_params not provided)
            optimizer_params: Dict with 'lr', 'weight_decay', etc. (base params)
            encoder_params: Optional list of encoder parameters (for separate LR)
            predictor_params: Optional list of predictor parameters (for separate LR)
            encoder_lr: Optional learning rate for encoder (overrides optimizer_params['lr'])
            predictor_lr: Optional learning rate for predictor (overrides optimizer_params['lr'])
            
        Returns:
            Optimizer instance
        """
        # If separate param groups requested, use them
        use_separate_lrs = (encoder_params is not None and predictor_params is not None and 
                           encoder_lr is not None and predictor_lr is not None)
        
        if use_separate_lrs:
            # Create param groups with different learning rates
            # Use lower weight decay on encoder during fine-tune (WD acts like additional gradient term)
            # This helps prevent hurting a starved encoder
            base_weight_decay = optimizer_params.get('weight_decay', 0.0)
            encoder_weight_decay = base_weight_decay * 0.5  # 50% of base WD for encoder
            predictor_weight_decay = base_weight_decay  # Full WD for predictor
            
            param_groups = [
                {'params': encoder_params, 'lr': encoder_lr, 'weight_decay': encoder_weight_decay},
                {'params': predictor_params, 'lr': predictor_lr, 'weight_decay': predictor_weight_decay}
            ]
            logger.info(f"   Encoder weight_decay: {encoder_weight_decay:.6e} (50% of base to help starved encoder)")
            logger.info(f"   Predictor weight_decay: {predictor_weight_decay:.6e} (full)")
            logger.info(f"🔧 SEPARATE LEARNING RATES:")
            logger.info(f"   Encoder LR: {encoder_lr:.6e} ({len(encoder_params)} params)")
            logger.info(f"   Predictor LR: {predictor_lr:.6e} ({len(predictor_params)} params)")
            logger.info(f"   Ratio: encoder/predictor = {encoder_lr/predictor_lr:.2f}×")
        else:
            # Use single param group (original behavior)
            param_groups = [{'params': params, **optimizer_params}]
        
        # Memory optimization: Try to use memory-efficient optimizers
        use_8bit = os.environ.get('FEATRIX_USE_8BIT_ADAM', '1').lower() in ('1', 'true', 'yes')
        
        optimizer_created = False
        optimizer = None
        
        # Try 8-bit AdamW first (saves ~50% memory by quantizing optimizer states)
        if use_8bit:
            try:
                import bitsandbytes as bnb
                logger.info("🔋 Using 8-bit AdamW (saves ~50% optimizer memory via state quantization)")
                optimizer = bnb.optim.AdamW8bit(param_groups)
                optimizer_created = True
            except ImportError:
                logger.info("⚠️  bitsandbytes not available, falling back to fused/regular AdamW")
            except Exception as e:
                logger.warning(f"⚠️  8-bit AdamW failed: {e}, falling back to fused/regular AdamW")
        
        # Try fused AdamW (PyTorch 2.0+, ~10% faster, no memory savings but better perf)
        if not optimizer_created:
            try:
                optimizer = torch.optim.AdamW(param_groups, fused=True)
                logger.info("⚡ Using fused AdamW (10-15% faster than regular AdamW)")
                optimizer_created = True
            except (TypeError, RuntimeError) as e:
                logger.info(f"⚠️  Fused AdamW not available ({e}), using regular AdamW")
        
        # Fallback to regular AdamW
        if not optimizer_created:
            optimizer = torch.optim.AdamW(param_groups)
            logger.info("📊 Using regular AdamW")
        
        # CRITICAL: Store optimizer reference so we can clear its state later
        # This is needed because optimizer state (momentum, variance) can be on GPU even if params are on CPU
        self._current_optimizer = optimizer
        # Also store for LR adjustment during training
        self._training_optimizer = optimizer
        
        # CRITICAL VERIFICATION: If using separate LRs, verify all encoder params are in optimizer
        # This catches cases where parameters might be missing due to filtering or other issues
        if use_separate_lrs and encoder_params is not None:
            optimizer_param_ids = set()
            for param_group in optimizer.param_groups:
                optimizer_param_ids.update({id(p) for p in param_group['params']})
            
            encoder_param_ids = {id(p) for p in encoder_params}
            missing_encoder_params = encoder_param_ids - optimizer_param_ids
            
            if missing_encoder_params:
                logger.error(f"❌ CRITICAL: {len(missing_encoder_params)} encoder params missing from optimizer!")
                logger.error(f"   Adding missing params to encoder param group...")
                # Add missing params to the encoder param group (first group)
                missing_params_list = [p for p in encoder_params if id(p) in missing_encoder_params]
                optimizer.param_groups[0]['params'].extend(missing_params_list)
                logger.info(f"   ✅ Added {len(missing_params_list)} missing encoder params to optimizer")
            else:
                logger.debug(f"   ✅ All {len(encoder_params)} encoder params verified in optimizer")
        
        if use_separate_lrs:
            logger.info(f">>> fsp params: encoder_lr={encoder_lr:.6e}, predictor_lr={predictor_lr:.6e}, weight_decay={optimizer_params.get('weight_decay', 0.0)}")
        else:
            logger.info(f">>> fsp params = {optimizer_params}...")
        
        return optimizer

    def _prepare_validation_data(self, val_df):
        """
        Prepare training and validation datasets.
        
        If val_df is None, splits train_df into train/val sets (80/20).
        Otherwise uses provided val_df.
        
        Args:
            val_df: Optional validation DataFrame. If None, will split from train_df.
            
        Returns:
            Tuple of (train_df, val_df) with reset indices
        """
        if val_df is None:
            # NOTE: (24/03/01, pjz) We should draw a random seed and save it in the database, but
            # for now a fixed seed will do.
            split_seed = 0
            validation_set_fraction = 0.2

            # The function is called train_test_split, but we're using it to break out a validation set
            # from the train set.
            logger.info(f"@@@@ No passed val_df -- splitting the train data with split_seed = {split_seed} and validation_set_fraction = {validation_set_fraction} @@@@")
            logger.info(f"🔍 TRAIN DEBUG: About to check target_col_type")
            logger.info(f"🔍 TRAIN DEBUG: self.target_col_type = {repr(self.target_col_type)}")
            logger.info(f"🔍 TRAIN DEBUG: type(self.target_col_type) = {type(self.target_col_type)}")
            if self.target_col_type == 'set':
                logger.info(f"🔍 TRAIN DEBUG: Taking 'set' branch for target_col_type")
                train_df, val_df = self.safe_split_train_val(
                    self.train_df,
                    target_col=self.target_col_name,
                    test_size=validation_set_fraction,
                    random_state=split_seed,
                )
                logger.info(f"🔍 TRAIN DEBUG: Completed safe_split_train_val call")
            elif self.target_col_type == 'scalar':
                logger.info(f"🔍 TRAIN DEBUG: Taking 'scalar' branch for target_col_type")
                # use sklearn's function
                train_df, val_df = train_test_split(
                    self.train_df,
                    test_size=validation_set_fraction,
                    random_state=split_seed,
                )
                logger.info(f"🔍 TRAIN DEBUG: Completed train_test_split call")
            else:
                logger.error(f"🔍 TRAIN DEBUG: Unknown target column type: {self.target_col_type}")
                raise Exception(f"Unknown target column type: {self.target_col_type}")

            # Reset the indices after train_test_split to make sure we can index into them
            # independently from what the indices were in the original dataframes.
            logger.info(f"🔍 TRAIN DEBUG: About to reset indices - train_df shape: {train_df.shape}, val_df shape: {val_df.shape}")
            train_df.reset_index(drop=True, inplace=True)
            val_df.reset_index(drop=True, inplace=True)
            logger.info(f"🔍 TRAIN DEBUG: Completed index reset")
            
            # DATA DUPLICATION DISABLED - train with whatever data we have
            # (Previously duplicated small datasets to reach MIN_DATASET_SIZE=1024)
            original_train_size = len(train_df)
            original_val_size = len(val_df)
            total_size = original_train_size + original_val_size
            logger.info(f"📊 Dataset size: {total_size} samples (train: {original_train_size}, val: {original_val_size})")
            
            # Store actual split sizes for monitor reporting
            self._actual_train_size = original_train_size
            self._actual_val_size = original_val_size
            self._used_internal_split = True
        else:
            print("@@@@ We handed ourselves a val_df -- very good -- DEFINITELY NOT SPLITTING @@@@")
            train_df = self.train_df
            train_df.reset_index(drop=True, inplace=True)
            val_df.reset_index(drop=True, inplace=True)
            
            # Store actual sizes for monitor reporting
            self._actual_train_size = len(train_df)
            self._actual_val_size = len(val_df)
            self._used_internal_split = False
        
        return train_df, val_df

    def _cleanup_orphaned_dataloader_workers(self):
        """
        Clean up any orphaned DataLoader workers from previous training jobs.
        
        These workers inherit CUDA context (~600MB GPU memory each) and persist with persistent_workers=True.
        We MUST kill them before single predictor training to free GPU memory.
        
        PROBLEM: Workers can be children of:
        1. PID 1 (reparented orphans after parent died)
        2. Uvicorn workers (when training happens in API handlers - parent is still alive but training is dead)
        3. Celery workers (when training happens in Celery tasks)
        
        We need to kill ALL DataLoader workers that aren't part of an active training job.
        """
        try:
            import psutil
            logger.info("🔍 Scanning for orphaned DataLoader worker processes...")
            
            # Find ALL DataLoader workers and check if they're orphaned
            # A worker is orphaned if:
            # 1. Parent is PID 1 (reparented)
            # 2. Parent is dead
            # 3. Parent is uvicorn/celery but there's no active training job for this worker
            orphaned_workers = []
            current_pid = os.getpid()
            
            # Get list of active training PIDs (Celery workers, training scripts, etc.)
            active_training_pids = set()
            active_training_pids.add(current_pid)  # Current process is active
            
            # Find Celery workers
            try:
                for proc in psutil.process_iter(['pid', 'cmdline']):
                    try:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if 'celery' in cmdline.lower() and 'worker' in cmdline.lower():
                            active_training_pids.add(proc.info['pid'])
                            # Add all children of Celery workers
                            try:
                                celery_proc = psutil.Process(proc.info['pid'])
                                for child in celery_proc.children(recursive=True):
                                    active_training_pids.add(child.pid)
                            except:
                                pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except:
                pass
            
            for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline', 'memory_info']):
                try:
                    # Skip our own process
                    if proc.info['pid'] == current_pid:
                        continue
                    
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # Check if this is a DataLoader worker
                    is_worker = (
                        'multiprocessing.spawn' in cmdline and
                        'spawn_main' in cmdline
                    )
                    
                    if is_worker:
                        worker_pid = proc.info['pid']
                        ppid = proc.info['ppid']
                        mem_info = proc.info['memory_info']
                        rss_gb = mem_info.rss / (1024**3) if mem_info else 0
                        
                        # Skip if memory is too small or too large (not a worker)
                        if not (0.3 < rss_gb < 2.0):
                            continue
                        
                        # Check if orphaned
                        is_orphaned = False
                        orphan_reason = ""
                        
                        # Case 1: Parent is PID 1 (reparented orphan)
                        if ppid == 1:
                            is_orphaned = True
                            orphan_reason = "parent=PID1"
                        # Case 2: Parent is dead
                        elif ppid not in active_training_pids:
                            try:
                                parent = psutil.Process(ppid)
                                if not parent.is_running():
                                    is_orphaned = True
                                    orphan_reason = "parent_dead"
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                is_orphaned = True
                                orphan_reason = "parent_not_found"
                        # Case 3: Parent is uvicorn/celery but worker is not part of active training
                        else:
                            try:
                                parent = psutil.Process(ppid)
                                parent_cmdline = ' '.join(parent.cmdline()) if parent.cmdline() else ''
                                
                                # If parent is uvicorn/gunicorn, the worker is likely orphaned
                                # (training jobs should run in Celery, not uvicorn workers)
                                if any(x in parent_cmdline.lower() for x in ['uvicorn', 'gunicorn', 'main:app']):
                                    is_orphaned = True
                                    orphan_reason = f"parent_uvicorn_worker"
                                # If parent is Celery but worker PID is not in active training set, it's orphaned
                                elif 'celery' in parent_cmdline.lower() and worker_pid not in active_training_pids:
                                    is_orphaned = True
                                    orphan_reason = "parent_celery_but_not_active"
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                is_orphaned = True
                                orphan_reason = "parent_check_failed"
                        
                        if is_orphaned:
                            orphaned_workers.append({
                                'pid': worker_pid,
                                'ppid': ppid,
                                'rss_gb': rss_gb,
                                'cmdline': cmdline[:100],
                                'reason': orphan_reason
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.debug(f"Error checking process: {e}")
                    continue
            
            if orphaned_workers:
                total_gpu_mem_gb = len(orphaned_workers) * 0.6  # ~600MB per worker
                logger.error(
                    f"🔫 Found {len(orphaned_workers)} ORPHANED DataLoader worker(s) holding ~{total_gpu_mem_gb:.1f}GB GPU memory!"
                )
                logger.error(f"   These are from previous training runs and MUST be killed to free GPU memory")
                
                # Group by reason for logging
                by_reason = {}
                for w in orphaned_workers:
                    reason = w['reason']
                    if reason not in by_reason:
                        by_reason[reason] = []
                    by_reason[reason].append(w)
                
                for reason, workers in by_reason.items():
                    logger.error(f"   {len(workers)} workers: {reason}")
                
                killed = 0
                for worker in orphaned_workers:
                    try:
                        proc = psutil.Process(worker['pid'])
                        logger.info(f"   Killing orphaned worker PID {worker['pid']} (PPID={worker['ppid']}, RSS={worker['rss_gb']:.2f}GB, reason={worker['reason']})")
                        proc.terminate()
                        killed += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if killed > 0:
                    time.sleep(1.0)  # Wait for graceful termination
                    # Force kill any remaining
                    for worker in orphaned_workers:
                        try:
                            proc = psutil.Process(worker['pid'])
                            if proc.is_running():
                                logger.warning(f"   Force killing worker PID {worker['pid']} (didn't terminate gracefully)")
                                proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    logger.info(f"✅ Killed {killed} orphaned worker(s) - freed ~{killed * 0.6:.1f}GB GPU memory")
                    # Clear GPU cache after killing workers
                    if is_gpu_available():
                        empty_gpu_cache()
                        synchronize_gpu()
                        gc.collect()
                        empty_gpu_cache()
                        logger.info(f"   GPU cache cleared after worker cleanup")
            else:
                logger.info("✅ No orphaned DataLoader workers found")
                
        except ImportError:
            logger.warning("⚠️  psutil not available - cannot cleanup orphaned workers")
        except Exception as cleanup_err:
            logger.error(f"❌ Could not cleanup orphaned workers: {cleanup_err}")
            logger.exception("Full traceback:")

    def _cap_batch_size_for_dataset(self, batch_size, dataset_size):
        """
        Cap batch size to prevent overfitting on small datasets.
        
        Ensures a minimum number of batches per epoch based on dataset size:
        - Small datasets (<1000): At least 4 batches per epoch
        - Medium datasets (1000-10k): At least 6 batches per epoch
        - Large datasets (>10k): At least 8 batches per epoch
        
        The maximum batch size is rounded down to the nearest power of 2.
        
        Args:
            batch_size: Requested batch size
            dataset_size: Total number of training samples
            
        Returns:
            int: Capped batch size (may be same as input if no cap needed)
        """
        # Determine divisor based on dataset size
        if dataset_size < 1000:
            divisor = 4  # At least 4 batches per epoch
        elif dataset_size < 10000:
            divisor = 6  # At least 6 batches per epoch
        else:
            divisor = 8  # At least 8 batches per epoch
        
        max_batch_size_float = dataset_size / divisor
        
        # Round down to nearest power of 2
        if max_batch_size_float >= 1:
            max_batch_size = int(2 ** math.floor(math.log2(max_batch_size_float)))
        else:
            max_batch_size = 1  # Minimum batch size of 1
        
        # Cap batch_size if it exceeds the limit
        if batch_size > max_batch_size:
            logger.warning(
                f"⚠️  batch_size ({batch_size}) capped to {max_batch_size} "
                f"(max = len(data)/{divisor} = {dataset_size}/{divisor} = {max_batch_size_float:.1f}, "
                f"rounded down to power of 2 = {max_batch_size})"
            )
            return max_batch_size
        
        return batch_size

    def _setup_bf16_autocast(self, use_bf16):
        """
        Set up BF16 mixed precision training if requested and supported.
        
        BF16 offers ~50% memory savings with better numerical stability than FP16.
        No GradScaler needed (unlike FP16) due to wider dynamic range.
        Requires Ampere or newer GPUs (compute capability >= 8.0).
        
        Args:
            use_bf16: Bool or None. If None, inherits from embedding space.
            
        Returns:
            Tuple of (use_autocast, autocast_dtype)
        """
        use_autocast = False
        autocast_dtype = torch.float32
        
        # Inherit from embedding space if not explicitly specified
        if use_bf16 is None:
            use_bf16 = getattr(self.embedding_space, 'use_bf16', False)
            if use_bf16:
                logger.info("🔋 Inheriting BF16 setting from embedding space")
        
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
                    logger.info("🔋 BF16 MIXED PRECISION TRAINING ENABLED (Single Predictor)")
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
        
        return use_autocast, autocast_dtype

    def _suppress_noisy_logs(self):
        """
        Suppress harmless log messages from dependencies.
        
        - multiprocessing: Suppress "Bad file descriptor" errors from DataLoader worker cleanup
          (These occur when multiprocessing queues close during worker shutdown - harmless PyTorch internals)
        - urllib3: Suppress verbose connection pool DEBUG logs
        
        Note: Can't filter OSError with warnings.filterwarnings (OSError is not a Warning subclass)
        """
        #dump_logging_tree()
        
        logging.getLogger('multiprocessing').setLevel(logging.ERROR)  # Suppress QueueFeederThread errors
        logging.getLogger('urllib3').setLevel(logging.INFO)  # Suppress urllib3 connection pool DEBUG logs
        logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)  # Suppress connection logs

    def _setup_validation_metrics(self, val_df, val_queries, val_targets, val_pos_label):
        """
        Set up validation queries, targets, and positive label for metrics computation.
        
        Validates that val_df contains the target column, normalizes targets to match
        training normalization, and determines the positive label if not provided.
        
        Args:
            val_df: Validation DataFrame
            val_queries: Optional list of query dicts (will be extracted from val_df if None)
            val_targets: Optional Series of target values (will be extracted from val_df if None)
            val_pos_label: Optional positive label for binary classification metrics
            
        Returns:
            Tuple of (val_df, val_queries, val_targets, val_pos_label)
        """
        # CRITICAL: Check if val_df is empty or missing target column BEFORE accessing it
        if len(val_df) == 0 or len(val_df.columns) == 0:
            logger.warning(f"⚠️  VALIDATION SET IS EMPTY: {len(val_df)} rows, {len(val_df.columns)} columns")
            logger.warning(f"   This means all data was used for training (no validation split possible)")
            logger.warning(f"   Skipping validation metrics setup")
            val_queries = []
            val_targets = pd.Series(dtype='object')
        else:
            # Validate target column exists in val_df
            if self.target_col_name not in val_df.columns:
                available_cols = list(val_df.columns)[:20]
                error_msg = (
                    f"❌ CRITICAL ERROR: Target column '{self.target_col_name}' NOT FOUND in validation set!\n"
                    f"   Validation set has {len(val_df)} rows and {len(val_df.columns)} columns\n"
                    f"   Available columns (first 20): {available_cols}\n"
                    f"   This indicates the target column was lost during train/val split or CSV reading.\n"
                    f"   Check CSV reading logs to see what columns were actually loaded."
                )
                logger.error(error_msg)
                raise KeyError(f"Target column '{self.target_col_name}' not found in validation set. Available columns: {available_cols}")
            
        if val_queries is None:
            val_queries = val_df.to_dict("records")
            # Remove the target column from the queries.
            for q in val_queries:
                del q[self.target_col_name]
        if val_targets is None:
            val_targets = val_df[self.target_col_name]
            
            # CRITICAL: Normalize validation targets the same way as training targets
            # Training targets were normalized in prep_for_training with normalize_numeric_string
            # Validation targets must be normalized identically to match the codec's vocabulary
            if len(val_targets) > 0:
                # Apply the same normalization as in prep_for_training
                val_targets_str = val_targets.astype(str)
                
                def normalize_numeric_string(val):
                    if pd.isna(val) or val in ['nan', 'NaN', 'None', '', ' ']:
                        return val
                    try:
                        float_val = float(val)
                        if float_val.is_integer():
                            return str(int(float_val))
                        return str(float_val)
                    except (ValueError, TypeError):
                        return str(val)
                
                val_targets_normalized = val_targets_str.apply(normalize_numeric_string)
                val_targets = val_targets_normalized
                
                # Also update val_df so it's consistent for later use
                if val_df is not None:
                    val_df = val_df.copy()
                    val_df[self.target_col_name] = val_targets_normalized
                    self.val_df = val_df
                
                logger.info(f"🔧 Normalized validation target column '{self.target_col_name}' to match training normalization")
                logger.info(f"   Unique values after normalization: {sorted(val_targets_normalized.unique())}")
            
            # Only try to get val_pos_label if we have validation targets
            if val_pos_label is None and len(val_targets) > 0:
                val_pos_label = self.get_good_val_pos_label(val_targets=val_targets)
                
                logger.warning(
                    f"Choosing label '{val_pos_label}' as the positive label for validation metrics"
                )
                
                assert val_pos_label is not None, "couldn't auto pick a val_pos_label, apparently."
            elif val_pos_label is None and len(val_targets) == 0:
                logger.warning(f"⚠️  Cannot determine val_pos_label: validation set is empty")
                val_pos_label = None
            
            # CRITICAL: Normalize val_pos_label to match codec's output format
            # The codec's detokenize() returns values from tokens_to_members, which may have
            # different types than the dataframe values (e.g., boolean True vs string 'True')
            if val_pos_label is not None and hasattr(self, 'target_codec') and isinstance(self.target_codec, (SetEncoder, SetCodec)):
                val_pos_label = self._normalize_pos_label_to_codec_format(val_pos_label)
        
        return val_df, val_queries, val_targets, val_pos_label

    def _move_models_to_device(self):
        """
        Move predictor, encoder, and codecs to GPU/MPS if available.
        
        Checks for CPU_SP flag first - if present, all models remain on CPU.
        Otherwise moves predictor, embedding space encoder, and codecs to GPU/MPS.
        """
        # CRITICAL: Check for CPU_SP flag - if /sphere/CPU_SP exists, is_gpu_available() returns False
        if os.path.exists('/sphere/CPU_SP'):
            logger.warning("=" * 80)
            logger.warning("⚠️  /sphere/CPU_SP DETECTED - FORCING CPU TRAINING MODE")
            logger.warning("=" * 80)
            logger.warning("   All models will remain on CPU regardless of GPU availability")
            logger.warning("=" * 80)
        
        # CRITICAL: Move predictor to GPU/MPS BEFORE training starts
        if is_gpu_available():
            predictor_device = next(self.predictor.parameters()).device if list(self.predictor.parameters()) else None
            if predictor_device is None or predictor_device.type == 'cpu':
                logger.info(f"🚀 Moving predictor to GPU/MPS for training...")
                self.predictor = self.predictor.to(get_device())  # Use get_device() to support both CUDA and MPS
                predictor_device = next(self.predictor.parameters()).device
                logger.info(f"✅ Predictor device: {predictor_device}")
            else:
                logger.info(f"✅ Predictor already on GPU/MPS: {predictor_device}")
        
        # CRITICAL: Move embedding space encoder to GPU for training
        # This is the MAIN model that does all the heavy lifting!
        if is_gpu_available() and self.embedding_space is not None:
            if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                encoder_params = list(self.embedding_space.encoder.parameters())
                if encoder_params:
                    encoder_device = next(iter(encoder_params)).device
                    if encoder_device.type == 'cpu':
                        logger.info(f"🚀 Moving embedding space ENCODER to GPU (was on {encoder_device})...")
                        self.embedding_space.encoder = self.embedding_space.encoder.to(get_device())
                        encoder_device = next(self.embedding_space.encoder.parameters()).device
                        logger.info(f"✅ Encoder device: {encoder_device}")
                        encoder_param_count = sum(p.numel() for p in self.embedding_space.encoder.parameters())
                        logger.info(f"   Encoder params on GPU: {encoder_param_count:,}")
                    else:
                        logger.info(f"✅ Encoder already on GPU: {encoder_device}")
                else:
                    logger.warning(f"⚠️  Encoder has no parameters to move to GPU")
        
        # Move all codecs to GPU if available
        codecs_on_gpu = 0
        if is_gpu_available():
            for codec_name, codec in self.all_codecs.items():
                try:
                    if hasattr(codec, 'cuda'):
                        codec.to(get_device())
                        # Verify it's actually on GPU
                        if hasattr(codec, 'parameters') and list(codec.parameters()):
                            codec_device = next(codec.parameters()).device
                            if codec_device.type in ['cuda', 'mps']:
                                codecs_on_gpu += 1
                    elif hasattr(codec, 'to'):
                        codec.to(get_device())
                        codecs_on_gpu += 1
                except Exception as e:
                    logger.debug(f"Could not move {codec_name} codec to GPU: {e}")
            if codecs_on_gpu > 0:
                logger.info(f"✅ Moved {codecs_on_gpu}/{len(self.all_codecs)} codecs to GPU")

    def _save_final_best_checkpoints(self, use_auc_for_best_epoch, best_auc, sp_identifier, 
                                      training_start_timestamp, best_roc_auc_model_state, 
                                      best_roc_auc_embedding_space_state, best_auc_epoch, 
                                      best_pr_auc_model_state, best_pr_auc_embedding_space_state, 
                                      best_pr_auc_epoch, best_pr_auc, best_roc_auc_checkpoint_path, 
                                      best_pr_auc_checkpoint_path):
        """
        Save final best model checkpoints (ROC-AUC and PR-AUC) at end of training.
        
        This is idempotent - checks if files exist before saving. Ensures we always have
        both ROC-AUC and PR-AUC best checkpoints available.
        
        Args:
            use_auc_for_best_epoch: Whether to use AUC for best epoch selection
            best_auc: Best ROC-AUC score
            sp_identifier: Single predictor identifier suffix
            training_start_timestamp: Timestamp when training started
            best_roc_auc_model_state: State dict for best ROC-AUC model
            best_roc_auc_embedding_space_state: State dict for best ROC-AUC embedding space
            best_auc_epoch: Epoch with best ROC-AUC
            best_pr_auc_model_state: State dict for best PR-AUC model
            best_pr_auc_embedding_space_state: State dict for best PR-AUC embedding space
            best_pr_auc_epoch: Epoch with best PR-AUC
            best_pr_auc: Best PR-AUC score
            best_roc_auc_checkpoint_path: Existing ROC-AUC checkpoint path (or None)
            best_pr_auc_checkpoint_path: Existing PR-AUC checkpoint path (or None)
            
        Returns:
            Tuple of (best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path)
        """
        try:
            if use_auc_for_best_epoch and best_auc >= 0:
                id_suffix = f"_{sp_identifier}" if sp_identifier else ""
                checkpoint_dir = self._output_dir if self._output_dir else "."
                
                # Helper function to save a checkpoint (reuse the same logic from training loop)
                def save_checkpoint_variant_final(metric_type, epoch, metric_value, model_state, es_state):
                    """Save a checkpoint variant at end of training."""
                    try:
                        # Include training_start_timestamp to prevent stomping across re-runs
                        # Format: best_single_predictor_auc_roc_<value>_epoch_<value>.pickle
                        if metric_type.lower() == 'roc_auc':
                            checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_auc_roc_{metric_value:.4f}_epoch_{epoch}{id_suffix}.pickle")
                        elif metric_type.lower() == 'pr_auc':
                            checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_auc_pr_{metric_value:.4f}_epoch_{epoch}{id_suffix}.pickle")
                        else:
                            checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_{metric_type.lower()}_{metric_value:.4f}_epoch_{epoch}{id_suffix}.pickle")
                        
                        # Check if checkpoint already exists
                        if os.path.exists(checkpoint_path):
                            logger.debug(f"   ✅ {metric_type} checkpoint already exists: {checkpoint_path}")
                            return checkpoint_path
                        
                        _log_gpu_memory(f"BEFORE FINAL {metric_type} CHECKPOINT SAVE (epoch {epoch})", log_level=logging.INFO)
                        
                        # Temporarily restore the model state to save the checkpoint
                        original_predictor_state = self.predictor.state_dict()
                        original_es_state = self.embedding_space.encoder.state_dict()
                        
                        # Load the best state
                        self.predictor.load_state_dict(model_state)
                        self.embedding_space.encoder.load_state_dict(es_state)
                        
                        # CRITICAL: Validate and fix model integrity before saving best checkpoint
                        self._validate_and_fix_before_save()
                        
                        # Save checkpoint
                        with open(checkpoint_path, "wb") as f:
                            pickle.dump(self, f)
                        
                        # Restore original state
                        self.predictor.load_state_dict(original_predictor_state)
                        self.embedding_space.encoder.load_state_dict(original_es_state)
                        
                        _log_gpu_memory(f"AFTER FINAL {metric_type} CHECKPOINT SAVE (epoch {epoch})", log_level=logging.INFO)
                        logger.info(f"💾 FINAL {metric_type} BEST CHECKPOINT: Saved to {checkpoint_path}")
                        logger.info(f"   Epoch {epoch}: {metric_type}={metric_value:.4f}")
                        
                        return checkpoint_path
                    except Exception as e:
                        logger.error(f"❌ Failed to save final {metric_type} checkpoint: {e}")
                        logger.debug(traceback.format_exc())
                        return None
                
                # Save ROC-AUC best checkpoint if we have one and it hasn't been saved
                if best_roc_auc_model_state is not None and best_auc_epoch >= 0:
                    if not best_roc_auc_checkpoint_path or not os.path.exists(best_roc_auc_checkpoint_path):
                        saved_path = save_checkpoint_variant_final('roc_auc', best_auc_epoch, best_auc, best_roc_auc_model_state, best_roc_auc_embedding_space_state)
                        if saved_path:
                            best_roc_auc_checkpoint_path = saved_path
                
                # Save PR-AUC best checkpoint if we have one and it hasn't been saved
                if best_pr_auc_model_state is not None and best_pr_auc_epoch >= 0:
                    if not best_pr_auc_checkpoint_path or not os.path.exists(best_pr_auc_checkpoint_path):
                        saved_path = save_checkpoint_variant_final('pr_auc', best_pr_auc_epoch, best_pr_auc, best_pr_auc_model_state, best_pr_auc_embedding_space_state)
                        if saved_path:
                            best_pr_auc_checkpoint_path = saved_path
                        
        except Exception as e:
            logger.error(f"❌ Failed to save best model checkpoints: {e}")
            logger.debug(traceback.format_exc())
            # Continue anyway - training completed, just checkpoint save failed
        
        return best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path

    def _generate_network_visualization(self, network_viz_identifier):
        """
        Generate GraphViz visualization of network architecture.
        
        Args:
            network_viz_identifier: Custom identifier for output filename (optional)
        """
        logger.info("🔷 Generating GraphViz network architecture visualization...")
        try:
            from lib.featrix.neural.network_viz import generate_graphviz_for_single_predictor
            
            # Use custom identifier if provided, otherwise default
            output_path = None
            if network_viz_identifier:
                output_path = f"network_architecture_sp_{network_viz_identifier}"
            
            graphviz_path = generate_graphviz_for_single_predictor(self, output_path=output_path)
            if graphviz_path:
                logger.info(f"✅ Network architecture visualization saved to {graphviz_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate GraphViz visualization: {e}")

    def _determine_best_model_to_restore(self, use_auc_for_best_epoch, best_auc, 
                                          best_metric_preference, best_pr_auc_epoch, 
                                          best_pr_auc_model_state, best_pr_auc, 
                                          best_pr_auc_embedding_space_state, best_roc_auc_model_state, 
                                          best_auc_epoch, best_roc_auc_embedding_space_state, 
                                          best_model_state, best_epoch, best_val_loss):
        """
        Determine which best model to restore based on metric preference or auto-detection.
        
        Priority:
        1. Explicit preference (PR-AUC or ROC-AUC) if provided
        2. Auto-detect based on dataset imbalance (imbalanced → PR-AUC, balanced → ROC-AUC)
        3. Fall back to validation loss if AUC not available
        
        Args:
            use_auc_for_best_epoch: Whether AUC is used for best epoch selection
            best_auc: Best ROC-AUC score
            best_metric_preference: Explicit metric preference ('pr_auc', 'roc_auc', or None)
            best_pr_auc_epoch: Epoch with best PR-AUC
            best_pr_auc_model_state: State dict for best PR-AUC model
            best_pr_auc: Best PR-AUC score
            best_pr_auc_embedding_space_state: State dict for best PR-AUC embedding space
            best_roc_auc_model_state: State dict for best ROC-AUC model
            best_auc_epoch: Epoch with best ROC-AUC
            best_roc_auc_embedding_space_state: State dict for best ROC-AUC embedding space
            best_model_state: Fallback model state (if not using AUC)
            best_epoch: Fallback best epoch (if not using AUC)
            best_val_loss: Best validation loss
            
        Returns:
            Tuple of (primary_metric, primary_epoch, primary_value, best_model_state, 
                     best_embedding_space_state, best_epoch)
        """
        primary_metric = None
        primary_epoch = -1
        primary_value = -1.0
        best_embedding_space_state = None
        
        if use_auc_for_best_epoch and best_auc >= 0:
            # Determine which metric to use based on preference or auto-detect
            use_pr_auc_for_restore = False
            
            if best_metric_preference is not None:
                # Explicit preference from caller
                if best_metric_preference.lower() in ['pr_auc', 'pr-auc', 'precision_recall']:
                    use_pr_auc_for_restore = True
                elif best_metric_preference.lower() in ['roc_auc', 'roc-auc', 'auc']:
                    use_pr_auc_for_restore = False
                else:
                    logger.warning(f"⚠️  Unknown best_metric_preference='{best_metric_preference}', using auto-detect")
                    best_metric_preference = None  # Fall back to auto-detect
            
            if best_metric_preference is None:
                # Auto-detect: Check if dataset is imbalanced to determine primary metric
                is_imbalanced_restore = False
                if hasattr(self, 'distribution_metadata') and self.distribution_metadata:
                    imbalance_score = self.distribution_metadata.get('imbalance_score', 1.0)
                    is_imbalanced_restore = imbalance_score < 0.3
                use_pr_auc_for_restore = is_imbalanced_restore
            
            if use_pr_auc_for_restore and best_pr_auc_epoch >= 0 and best_pr_auc_model_state is not None:
                # Use PR-AUC best
                primary_metric = "PR-AUC"
                primary_epoch = best_pr_auc_epoch
                primary_value = best_pr_auc
                best_model_state = best_pr_auc_model_state
                best_embedding_space_state = best_pr_auc_embedding_space_state
                best_epoch = best_pr_auc_epoch
            elif best_roc_auc_model_state is not None:
                # Use ROC-AUC best
                primary_metric = "ROC-AUC"
                primary_epoch = best_auc_epoch
                primary_value = best_auc
                best_model_state = best_roc_auc_model_state
                best_embedding_space_state = best_roc_auc_embedding_space_state
                best_epoch = best_auc_epoch
        elif best_model_state is not None:
            # Validation loss based
            primary_metric = "val_loss"
            primary_epoch = best_epoch
            primary_value = best_val_loss
        
        return primary_metric, primary_epoch, primary_value, best_model_state, best_embedding_space_state, best_epoch

    def _cleanup_intermediate_checkpoints(self, training_start_timestamp, sp_identifier, 
                                           best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path, 
                                           best_checkpoint_path):
        """
        Clean up intermediate periodic checkpoints, keeping only best model checkpoints.
        
        Deletes all periodic checkpoints that are not marked as "best" models (ROC-AUC, PR-AUC, or val_loss).
        Only runs if we have at least one best model checkpoint saved.
        
        Args:
            training_start_timestamp: Timestamp prefix for checkpoint files
            sp_identifier: Single predictor identifier suffix
            best_roc_auc_checkpoint_path: Path to best ROC-AUC checkpoint (or None)
            best_pr_auc_checkpoint_path: Path to best PR-AUC checkpoint (or None)
            best_checkpoint_path: Path to best checkpoint (or None)
        """
        try:
            checkpoint_dir = self._output_dir if self._output_dir else "."
            id_suffix = f"_{sp_identifier}" if sp_identifier else ""
            
            # Check if we have any best model checkpoints
            has_best_models = (
                (best_roc_auc_checkpoint_path and os.path.exists(best_roc_auc_checkpoint_path)) or
                (best_pr_auc_checkpoint_path and os.path.exists(best_pr_auc_checkpoint_path)) or
                (best_checkpoint_path and os.path.exists(best_checkpoint_path))
            )
            
            if has_best_models:
                import glob
                # Find all periodic checkpoints for this training run
                periodic_pattern = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_epoch_*.pickle")
                periodic_checkpoints = glob.glob(periodic_pattern)
                
                # Exclude best model checkpoints from deletion
                best_checkpoint_files = set()
                if best_roc_auc_checkpoint_path:
                    best_checkpoint_files.add(os.path.abspath(best_roc_auc_checkpoint_path))
                if best_pr_auc_checkpoint_path:
                    best_checkpoint_files.add(os.path.abspath(best_pr_auc_checkpoint_path))
                if best_checkpoint_path:
                    best_checkpoint_files.add(os.path.abspath(best_checkpoint_path))
                
                # Delete periodic checkpoints that are not best models
                deleted_count = 0
                freed_bytes = 0
                for checkpoint_file in periodic_checkpoints:
                    abs_checkpoint = os.path.abspath(checkpoint_file)
                    # Skip if this is a best model checkpoint
                    if abs_checkpoint in best_checkpoint_files:
                        continue
                    # Skip if filename contains "best" (safety check)
                    if "best" in os.path.basename(checkpoint_file):
                        continue
                    
                    try:
                        file_size = os.path.getsize(checkpoint_file)
                        os.remove(checkpoint_file)
                        deleted_count += 1
                        freed_bytes += file_size
                        logger.debug(f"🗑️  Deleted periodic checkpoint: {os.path.basename(checkpoint_file)}")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to delete {os.path.basename(checkpoint_file)}: {e}")
                
                if deleted_count > 0:
                    freed_gb = freed_bytes / (1024**3)
                    logger.info(f"✅ Cleaned up {deleted_count} periodic checkpoints, freed {freed_gb:.2f} GB")
                    logger.info(f"   Kept {len(best_checkpoint_files)} best model checkpoint(s)")
                else:
                    logger.info(f"ℹ️  No periodic checkpoints to clean up")
            else:
                logger.warning(f"⚠️  No best models found - keeping all periodic checkpoints for debugging")
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup intermediate checkpoints: {e}")
            logger.debug(traceback.format_exc())

    def _check_sentence_transformer_device(self):
        """
        Check if sentence transformer is using GPU memory (legacy/disabled code).
        
        This is disabled code kept for reference - we no longer use local sentence transformers,
        instead using the string server for embeddings.
        """
        try:
            # Removed sentence_model import - no longer exists
            sentence_model = None
            if False:  # Disabled - no local model
                # Check device
                if hasattr(sentence_model, 'device'):
                    if sentence_model.device.type == 'cuda':
                        logger.error(f"🚨 Sentence transformer is on GPU! Moving to CPU...")
                        sentence_model = sentence_model.to('cpu')
                # Check parameters
                elif hasattr(sentence_model, 'parameters'):
                    if list(sentence_model.parameters()):
                        if next(sentence_model.parameters()).device.type == 'cuda':
                            logger.error(f"🚨 Sentence transformer parameters on GPU! Moving to CPU...")
                            sentence_model = sentence_model.to('cpu')
                # Check all submodules
                for module_name, module in sentence_model.named_modules():
                    if hasattr(module, 'parameters') and list(module.parameters()):
                        if next(module.parameters()).device.type == 'cuda':
                            logger.error(f"🚨 Sentence transformer submodule {module_name} on GPU! Moving to CPU...")
                            sentence_model = sentence_model.to('cpu')
                            break
        except Exception as e:
            logger.warning(f"Could not check sentence transformer: {e}")

    def _move_optimizer_state_to_cpu(self):
        """
        Move optimizer state tensors from GPU to CPU before checkpoint saving.
        
        AdamW optimizer state can be 2x the size of parameters (momentum + variance).
        Even if params are on CPU, optimizer state might still be on GPU.
        This method moves all optimizer state tensors to CPU to free GPU memory.
        """
        try:
            if hasattr(self, '_current_optimizer') and self._current_optimizer is not None:
                optimizer = self._current_optimizer
                optimizer_state_moved = 0
                for param_group in optimizer.param_groups:
                    for param in param_group['params']:
                        if param in optimizer.state:
                            state = optimizer.state[param]
                            for key, value in state.items():
                                if isinstance(value, torch.Tensor) and value.device.type == 'cuda':
                                    state[key] = value.to('cpu')
                                    optimizer_state_moved += 1
                if optimizer_state_moved > 0:
                    logger.debug(f"🚨 Moved {optimizer_state_moved} optimizer state tensors from GPU to CPU (checkpoint save)")
        except Exception as e:
            logger.warning(f"Could not move optimizer state to CPU: {e}")

    def _move_codecs_to_cpu(self):
        """
        Move all embedding space codecs from GPU to CPU before checkpoint saving.
        
        Checks each codec for GPU parameters, buffers, and embedded modules
        (e.g., StringCodec has bert_projection, feature_embedding_mlp, merge_mlp).
        If any GPU components are found, moves the entire codec to CPU.
        
        Returns:
            int: Number of codecs moved to CPU
        """
        moved_count = 0
        if hasattr(self.embedding_space, 'col_codecs'):
            for col_name, codec in self.embedding_space.col_codecs.items():
                codec_has_gpu = False
                
                # Check if codec has GPU parameters (StringCodec, JsonCodec have these!)
                if hasattr(codec, 'parameters') and list(codec.parameters()):
                    if next(codec.parameters()).device.type == 'cuda':
                        codec_has_gpu = True
                
                # Check buffers
                if not codec_has_gpu and hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                    for buffer in codec.buffers():
                        if buffer.device.type in ['cuda', 'mps']:
                            codec_has_gpu = True
                            break
                
                # Check embedded modules (StringCodec: bert_projection, feature_embedding_mlp, merge_mlp)
                for attr_name in ['bert_projection', 'feature_embedding_mlp', 'merge_mlp', 'projection', 'encoder']:
                    if hasattr(codec, attr_name):
                        embedded_module = getattr(codec, attr_name)
                        if embedded_module is not None and hasattr(embedded_module, 'parameters'):
                            if list(embedded_module.parameters()):
                                if next(embedded_module.parameters()).device.type == 'cuda':
                                    codec_has_gpu = True
                                    break
                
                # Move entire codec to CPU if it has any GPU components
                if codec_has_gpu:
                    codec.cpu()  # This moves parameters, buffers, and all submodules
                    moved_count += 1
                    logger.info(f"   Moved codec '{col_name}' to CPU")
            
            if moved_count > 0:
                logger.info(f"   ✅ Moved {moved_count} codecs to CPU")
        
        return moved_count

    def _update_best_model_tracking(self, epoch_idx, use_auc_for_best_epoch, current_auc, 
                                     current_pr_auc, current_val_loss, progress_dict,
                                     best_auc, best_auc_epoch, best_pr_auc, best_pr_auc_epoch,
                                     best_val_loss, best_epoch, best_roc_auc_model_state,
                                     best_roc_auc_embedding_space_state, best_pr_auc_model_state,
                                     best_pr_auc_embedding_space_state, log_prefix=""):
        """
        Update best model tracking based on current metrics.
        
        Handles composite score (when costs are available), AUC-based selection (ROC-AUC/PR-AUC),
        and validation loss-based selection. Tracks both ROC-AUC and PR-AUC best models separately.
        
        Args:
            epoch_idx: Current epoch index
            use_auc_for_best_epoch: Whether to use AUC for best model selection
            current_auc: Current ROC-AUC score
            current_pr_auc: Current PR-AUC score
            current_val_loss: Current validation loss
            progress_dict: Progress dictionary with metrics
            best_auc: Best ROC-AUC seen so far
            best_auc_epoch: Epoch with best ROC-AUC
            best_pr_auc: Best PR-AUC seen so far
            best_pr_auc_epoch: Epoch with best PR-AUC
            best_val_loss: Best validation loss
            best_epoch: Epoch with best validation loss
            best_roc_auc_model_state: State dict for best ROC-AUC model
            best_roc_auc_embedding_space_state: State dict for best ROC-AUC encoder
            best_pr_auc_model_state: State dict for best PR-AUC model
            best_pr_auc_embedding_space_state: State dict for best PR-AUC encoder
            log_prefix: Optional prefix for log messages
            
        Returns:
            Tuple of (is_new_best, best_auc, best_auc_epoch, best_pr_auc, best_pr_auc_epoch,
                     best_val_loss, best_epoch, best_roc_auc_model_state, 
                     best_roc_auc_embedding_space_state, best_pr_auc_model_state,
                     best_pr_auc_embedding_space_state)
        """
        is_new_best = False
        
        # Check if we have cost parameters - if so, use composite score
        use_composite_score = (
            self.cost_false_positive is not None and 
            self.cost_false_negative is not None and
            use_auc_for_best_epoch and 
            current_auc >= 0
        )
        
        if use_composite_score:
            # Use composite score (PR-AUC + cost savings + ROC-AUC)
            current_composite_score = progress_dict.get("metrics", {}).get("composite_score")
            if current_composite_score is not None:
                if not hasattr(self, '_best_composite_score') or self._best_composite_score < 0:
                    self._best_composite_score = -1.0
                    self._best_composite_score_epoch = -1
                
                if current_composite_score > self._best_composite_score + 1e-4:
                    previous_best_score = self._best_composite_score
                    previous_best_score_epoch = self._best_composite_score_epoch if self._best_composite_score_epoch >= 0 else -1
                    self._best_composite_score = current_composite_score
                    self._best_composite_score_epoch = epoch_idx
                    
                    # Also update individual metric tracking
                    best_auc = current_auc
                    best_auc_epoch = epoch_idx
                    if current_pr_auc >= 0:
                        best_pr_auc = current_pr_auc
                        best_pr_auc_epoch = epoch_idx
                    
                    is_new_best = True
                    score_components = progress_dict.get("metrics", {}).get("score_components", {})
                    if previous_best_score_epoch >= 0:
                        logger.info(f"   ⭐ New best composite score: {current_composite_score:.4f} (previous: {previous_best_score:.4f} @ epoch {previous_best_score_epoch})")
                        logger.info(f"      ROC-AUC: {current_auc:.4f}, PR-AUC: {current_pr_auc:.4f if current_pr_auc >= 0 else 'N/A'}, Cost savings: {score_components.get('cost_savings', 0):.3f}")
                        logger.info(f"      Weights: α={score_components.get('alpha', 0):.2f}, β={score_components.get('beta', 0):.2f}, γ={score_components.get('gamma', 0):.2f}")
                    else:
                        logger.info(f"   ⭐ New best composite score: {current_composite_score:.4f} (first valid score)")
                        logger.info(f"      ROC-AUC: {current_auc:.4f}, PR-AUC: {current_pr_auc:.4f if current_pr_auc >= 0 else 'N/A'}")
        elif use_auc_for_best_epoch and current_auc >= 0:
            # Use AUC for binary classification (fallback when no costs)
            # For imbalanced datasets, PR-AUC is often more informative than ROC-AUC
            # Check if dataset is imbalanced (positive rate < 0.3 or > 0.7)
            is_imbalanced = False
            if hasattr(self, 'distribution_metadata') and self.distribution_metadata:
                imbalance_score = self.distribution_metadata.get('imbalance_score', 1.0)
                # imbalance_score is minority_ratio, so < 0.3 means imbalanced
                is_imbalanced = imbalance_score < 0.3
            
            # For imbalanced datasets, prefer PR-AUC; otherwise use ROC-AUC
            use_pr_auc = is_imbalanced and current_pr_auc >= 0
            
            # Determine which metric to use for primary best model selection
            # CRITICAL: Check for new best BEFORE updating the best values, otherwise the
            # comparison will always be false since best_auc == current_auc after update
            is_new_roc_auc_best = current_auc > best_auc
            is_new_pr_auc_best = current_pr_auc >= 0 and current_pr_auc > best_pr_auc
            
            # Track ROC-AUC best separately (always, regardless of which metric we use for selection)
            if is_new_roc_auc_best:
                previous_best_auc = best_auc
                previous_best_auc_epoch = best_auc_epoch if best_auc_epoch >= 0 else -1
                best_auc = current_auc
                best_auc_epoch = epoch_idx
                # Save state dicts for ROC-AUC best model
                best_roc_auc_model_state = self.predictor.state_dict()
                best_roc_auc_embedding_space_state = self.embedding_space.encoder.state_dict()
                # Set is_new_best if we're using ROC-AUC for selection
                if not use_pr_auc:
                    is_new_best = True
                    if previous_best_auc_epoch >= 0:
                        logger.info(f"   ⭐ New best ROC-AUC: {best_auc:.4f} (PR-AUC: {current_pr_auc:.4f if current_pr_auc >= 0 else 'N/A'}, previous: {previous_best_auc:.4f} @ epoch {previous_best_auc_epoch})")
                    else:
                        logger.info(f"   ⭐ New best ROC-AUC: {best_auc:.4f} (PR-AUC: {current_pr_auc:.4f if current_pr_auc >= 0 else 'N/A'}, first valid AUC)")
            
            # Track PR-AUC best separately (always, if PR-AUC is available)
            if is_new_pr_auc_best:
                previous_best_pr_auc = best_pr_auc
                previous_best_pr_auc_epoch = best_pr_auc_epoch if best_pr_auc_epoch >= 0 else -1
                best_pr_auc = current_pr_auc
                best_pr_auc_epoch = epoch_idx
                # Save state dicts for PR-AUC best model
                best_pr_auc_model_state = self.predictor.state_dict()
                best_pr_auc_embedding_space_state = self.embedding_space.encoder.state_dict()
                # Set is_new_best if we're using PR-AUC for selection
                if use_pr_auc:
                    is_new_best = True
                    if previous_best_pr_auc_epoch >= 0:
                        logger.info(f"   ⭐ New best PR-AUC: {best_pr_auc:.4f} (ROC-AUC: {current_auc:.4f}, previous PR-AUC: {previous_best_pr_auc:.4f} @ epoch {previous_best_pr_auc_epoch})")
                    else:
                        logger.info(f"   ⭐ New best PR-AUC: {best_pr_auc:.4f} (ROC-AUC: {current_auc:.4f}, first valid PR-AUC)")
        else:
            # Use validation loss for scalar/regression or when AUC not available
            if current_val_loss < best_val_loss:
                previous_best = best_val_loss
                best_val_loss = current_val_loss
                best_epoch = epoch_idx
                is_new_best = True
                if epoch_idx >= 20:
                    logger.info(f"{log_prefix}   ⭐ New best validation loss: {best_val_loss:.4f} (previous best: {previous_best:.4f})")
                else:
                    logger.debug(f"{log_prefix}   ⭐ New best val loss: {best_val_loss:.4f} (< epoch 20, not saving checkpoint)")
        
        return (is_new_best, best_auc, best_auc_epoch, best_pr_auc, best_pr_auc_epoch,
                best_val_loss, best_epoch, best_roc_auc_model_state, 
                best_roc_auc_embedding_space_state, best_pr_auc_model_state,
                best_pr_auc_embedding_space_state)

    def _save_best_model_checkpoints(self, epoch_idx, nodump_exists, is_last_fold, 
                                       sp_identifier, training_start_timestamp, best_auc, 
                                       best_auc_epoch, best_pr_auc, best_pr_auc_epoch,
                                       best_roc_auc_model_state, best_roc_auc_embedding_space_state,
                                       best_pr_auc_model_state, best_pr_auc_embedding_space_state,
                                       best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path,
                                       best_checkpoint_path, use_auc_for_best_epoch, current_auc,
                                       current_val_loss, should_save_best_file, optimizer):
        """
        Save best model checkpoints for ROC-AUC and/or PR-AUC variants.
        
        Saves checkpoint files and state dicts for best models found so far.
        Handles both ROC-AUC and PR-AUC best models, plus validation loss-based best models.
        Includes OOM recovery logic to save on CPU if GPU save fails.
        
        Args:
            epoch_idx: Current epoch index
            nodump_exists: Whether /NODUMP file exists (skip saves if True)
            is_last_fold: Whether this is the last fold in cross-validation
            sp_identifier: Single predictor identifier for file naming
            training_start_timestamp: Timestamp prefix for checkpoint files
            best_auc: Best ROC-AUC score
            best_auc_epoch: Epoch with best ROC-AUC
            best_pr_auc: Best PR-AUC score
            best_pr_auc_epoch: Epoch with best PR-AUC
            best_roc_auc_model_state: State dict for best ROC-AUC model
            best_roc_auc_embedding_space_state: State dict for best ROC-AUC encoder
            best_pr_auc_model_state: State dict for best PR-AUC model
            best_pr_auc_embedding_space_state: State dict for best PR-AUC encoder
            best_roc_auc_checkpoint_path: Path to best ROC-AUC checkpoint (or None)
            best_pr_auc_checkpoint_path: Path to best PR-AUC checkpoint (or None)
            best_checkpoint_path: Primary best checkpoint path (or None)
            use_auc_for_best_epoch: Whether using AUC for selection
            current_auc: Current ROC-AUC score
            current_val_loss: Current validation loss
            should_save_best_file: Whether to save validation loss-based checkpoint
            optimizer: Optimizer instance for saving state
            
        Returns:
            Tuple of (best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path, best_checkpoint_path)
        """
        # Only save checkpoints from epoch 3+ (unless it's the last fold or NODUMP override)
        if epoch_idx < 3 or (nodump_exists and not is_last_fold):
            return best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path, best_checkpoint_path
        
        id_suffix = f"_{sp_identifier}" if sp_identifier else ""
        checkpoint_dir = self._output_dir if self._output_dir else "."
        
        # Helper function to update symlink to best_single_predictor.pickle
        def update_best_single_predictor_symlink(checkpoint_path):
            """Update best_single_predictor.pickle symlink to point to the latest best checkpoint.
            
            This symlink is the DEFAULT checkpoint for inference - always points to the best model
            (by PR-AUC or ROC-AUC), not the last epoch.
            """
            try:
                best_pickle_path = os.path.join(checkpoint_dir, "best_single_predictor.pickle")
                if os.path.exists(checkpoint_path):
                    # Remove existing symlink or file if it exists
                    if os.path.exists(best_pickle_path) or os.path.islink(best_pickle_path):
                        os.remove(best_pickle_path)
                    
                    # Create relative symlink (works better across filesystems)
                    rel_checkpoint_path = os.path.relpath(checkpoint_path, checkpoint_dir)
                    os.symlink(rel_checkpoint_path, best_pickle_path)
                    logger.info(f"🔗 Updated best model symlink (DEFAULT for inference): {best_pickle_path} -> {os.path.basename(checkpoint_path)}")
                    logger.info(f"   This is the best checkpoint, not the last epoch - use this for inference")
                    return True
            except Exception as e:
                logger.debug(f"Could not update best_single_predictor.pickle symlink: {e}")
                # Don't fail training if this fails
            return False
        
        # Helper function to save a checkpoint variant
        def save_checkpoint_variant(metric_type, epoch, metric_value, model_state, es_state, checkpoint_path_var):
            """Save a checkpoint variant (ROC-AUC or PR-AUC best)."""
            try:
                _log_gpu_memory(f"BEFORE {metric_type} CHECKPOINT FILE SAVE (epoch {epoch})", log_level=logging.INFO)
                
                # Temporarily restore the model state to save the checkpoint
                original_predictor_state = self.predictor.state_dict()
                original_es_state = self.embedding_space.encoder.state_dict()
                
                # Load the best state
                self.predictor.load_state_dict(model_state)
                self.embedding_space.encoder.load_state_dict(es_state)
                
                # Save checkpoint
                with open(checkpoint_path_var, "wb") as f:
                    pickle.dump(self, f)
                
                # Restore original state
                self.predictor.load_state_dict(original_predictor_state)
                self.embedding_space.encoder.load_state_dict(original_es_state)
                
                _log_gpu_memory(f"AFTER {metric_type} CHECKPOINT PICKLE.DUMP (epoch {epoch})", log_level=logging.INFO)
                logger.info(f"💾 BEST {metric_type} MODEL CHECKPOINT: Saved to {checkpoint_path_var}")
                logger.info(f"   Epoch {epoch}: {metric_type}={metric_value:.4f}")
                
                # Also save state dicts
                state_dict_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_model_state_{metric_type.lower()}{id_suffix}_epoch_{epoch}.pt")
                
                # Get display metadata for this best epoch
                display_metadata = None
                if hasattr(self, '_epoch_display_metadata') and epoch in self._epoch_display_metadata:
                    display_metadata = self._epoch_display_metadata[epoch]
                else:
                    # Try to extract it now if not already stored
                    try:
                        # Get metrics for this epoch
                        epoch_metrics = None
                        if hasattr(self, 'training_info') and self.training_info:
                            for entry in self.training_info:
                                if entry.get('epoch_idx') == epoch:
                                    epoch_metrics = entry.get('metrics', {})
                                    break
                        if epoch_metrics:
                            display_metadata = self._extract_classification_display_metadata(epoch, epoch_metrics)
                    except Exception as e:
                        logger.debug(f"Could not extract display metadata for best {metric_type} epoch {epoch}: {e}")
                
                checkpoint_metadata = {
                    'epoch': epoch,
                    'predictor_state_dict': model_state,
                    'embedding_space_state_dict': es_state,
                    'val_loss': current_val_loss,
                    'optimizer_state_dict': optimizer.state_dict(),
                    'metrics': self.training_metrics,
                    'sp_identifier': sp_identifier,
                    'best_metric': metric_type.lower(),
                    'classification_display_metadata': display_metadata,
                }
                if metric_type == 'ROC-AUC':
                    checkpoint_metadata['auc'] = metric_value
                elif metric_type == 'PR-AUC':
                    checkpoint_metadata['pr_auc'] = metric_value
                
                torch.save(checkpoint_metadata, state_dict_path)
                logger.info(f"💾 {metric_type} model state dicts saved to {state_dict_path}")
                
                # Update symlink to best_single_predictor.pickle (will be updated with primary best later)
                # Don't update here - wait for primary best_checkpoint_path to be determined
                
                return True
            except Exception as e:
                logger.error(f"❌ Failed to save {metric_type} checkpoint: {e}")
                return False
        
        # Save ROC-AUC best checkpoint if we have a new best at this epoch
        if best_roc_auc_model_state is not None and best_auc_epoch == epoch_idx:
            roc_auc_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_auc_roc_{best_auc:.4f}_epoch_{best_auc_epoch}{id_suffix}.pickle")
            # Only save if we don't already have this checkpoint (avoid overwriting)
            if not best_roc_auc_checkpoint_path or best_roc_auc_checkpoint_path != roc_auc_checkpoint_path:
                if save_checkpoint_variant('ROC-AUC', best_auc_epoch, best_auc, best_roc_auc_model_state, best_roc_auc_embedding_space_state, roc_auc_checkpoint_path):
                    best_roc_auc_checkpoint_path = roc_auc_checkpoint_path
        
        # Save PR-AUC best checkpoint if we have a new best at this epoch
        if best_pr_auc_model_state is not None and best_pr_auc_epoch == epoch_idx:
            pr_auc_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_auc_pr_{best_pr_auc:.4f}_epoch_{best_pr_auc_epoch}{id_suffix}.pickle")
            # Only save if we don't already have this checkpoint (avoid overwriting)
            if not best_pr_auc_checkpoint_path or best_pr_auc_checkpoint_path != pr_auc_checkpoint_path:
                if save_checkpoint_variant('PR-AUC', best_pr_auc_epoch, best_pr_auc, best_pr_auc_model_state, best_pr_auc_embedding_space_state, pr_auc_checkpoint_path):
                    best_pr_auc_checkpoint_path = pr_auc_checkpoint_path
        
        # Set primary checkpoint path based on which metric we're using for selection
        if use_auc_for_best_epoch and current_auc >= 0:
            # Determine if dataset is imbalanced
            is_imbalanced_checkpoint = False
            if hasattr(self, 'distribution_metadata') and self.distribution_metadata:
                imbalance_score = self.distribution_metadata.get('imbalance_score', 1.0)
                is_imbalanced_checkpoint = imbalance_score < 0.3
            
            if is_imbalanced_checkpoint and best_pr_auc_epoch >= 0 and best_pr_auc_checkpoint_path:
                best_checkpoint_path = best_pr_auc_checkpoint_path
            elif best_roc_auc_checkpoint_path:
                best_checkpoint_path = best_roc_auc_checkpoint_path
        
        # Update symlink to point to the primary best checkpoint
        if best_checkpoint_path and os.path.exists(best_checkpoint_path):
            update_best_single_predictor_symlink(best_checkpoint_path)
        
        if not use_auc_for_best_epoch:
            # For validation loss, use the primary best model state
            if should_save_best_file:
                checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_best_single_predictor_valloss_{current_val_loss:.4f}_epoch_{epoch_idx}{id_suffix}.pickle")
                try:
                    with open(checkpoint_path, "wb") as f:
                        pickle.dump(self, f)
                    best_checkpoint_path = checkpoint_path
                    logger.info(f"💾 BEST MODEL CHECKPOINT: Saved to {checkpoint_path}")
                except RuntimeError as save_error:
                    # Handle CUDA OOM during best checkpoint save
                    error_msg = str(save_error).lower()
                    if "cuda" in error_msg and ("out of memory" in error_msg or "oom" in error_msg):
                        logger.warning(f"⚠️  Failed to save best checkpoint due to CUDA OOM, trying CPU...")
                        try:
                            # Store original device locations
                            predictor_device = next(self.predictor.parameters()).device if list(self.predictor.parameters()) else None
                            encoder_device = next(self.embedding_space.encoder.parameters()).device if list(self.embedding_space.encoder.parameters()) else None
                            
                            # Move models to CPU for checkpoint saving (to avoid GPU memory issues)
                            if predictor_device and predictor_device.type in ['cuda', 'mps']:
                                self.predictor = self.predictor.cpu()
                            if encoder_device and encoder_device.type in ['cuda', 'mps']:
                                self.embedding_space.encoder = self.embedding_space.encoder.cpu()
                            
                            # Clear GPU cache
                            if is_gpu_available():
                                empty_gpu_cache()
                                synchronize_gpu()
                            
                            # Try saving again on CPU
                            with open(checkpoint_path, "wb") as f:
                                pickle.dump(self, f)
                            
                            logger.info(f"✅ Best checkpoint saved on CPU: {checkpoint_path}")
                            
                            # Move models back to original device
                            if predictor_device and predictor_device.type in ['cuda', 'mps']:
                                self.predictor = self.predictor.to(predictor_device)
                            if encoder_device and encoder_device.type in ['cuda', 'mps']:
                                self.embedding_space.encoder = self.embedding_space.encoder.to(encoder_device)
                        except Exception as cpu_save_error:
                            logger.error(f"❌ Failed to save best checkpoint on CPU: {cpu_save_error}")
                            # Try to move models back
                            try:
                                if predictor_device and predictor_device.type in ['cuda', 'mps']:
                                    self.predictor = self.predictor.to(predictor_device)
                                if encoder_device and encoder_device.type in ['cuda', 'mps']:
                                    self.embedding_space.encoder = self.embedding_space.encoder.to(encoder_device)
                            except Exception:
                                pass
                    else:
                        logger.error(f"❌ Failed to save checkpoint: {save_error}")
                except Exception as e:
                    logger.error(f"❌ Failed to save checkpoint: {e}")
        
        return best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path, best_checkpoint_path

    def _collect_all_gpu_items(self, _walk_model_for_gpu):
        """
        Collect all GPU tensors from models, encoders, and codecs for diagnostics.
        
        Walks through predictor, embedding space encoder, target codec, and all column codecs
        to find any tensors/buffers/parameters that are still on GPU. Used for debugging
        checkpoint save failures and GPU memory issues.
        
        Args:
            _walk_model_for_gpu: Function to walk a model and collect GPU items
            
        Returns:
            List of GPU items found across all models
        """
        all_gpu_items = []
        
        # Check predictor
        if hasattr(self, 'predictor') and self.predictor is not None:
            predictor_gpu = _walk_model_for_gpu(self.predictor, "predictor")
            all_gpu_items.extend(predictor_gpu)
        
        # Check encoder
        if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
            encoder_gpu = _walk_model_for_gpu(self.embedding_space.encoder, "embedding_space.encoder")
            all_gpu_items.extend(encoder_gpu)
        
        # Check target_codec
        if hasattr(self, 'target_codec') and self.target_codec is not None:
            target_codec_gpu = _walk_model_for_gpu(self.target_codec, "target_codec")
            all_gpu_items.extend(target_codec_gpu)
        
        # Check all col_codecs
        if hasattr(self.embedding_space, 'col_codecs'):
            for col_name, codec in self.embedding_space.col_codecs.items():
                codec_gpu = _walk_model_for_gpu(codec, f"embedding_space.col_codecs['{col_name}']")
                all_gpu_items.extend(codec_gpu)
        
        return all_gpu_items

    def _clear_gpu_memory_aggressively(self):
        """
        Aggressively clear GPU memory before checkpoint save.
        
        Performs multiple passes of GPU cache clearing and garbage collection to try to
        force release of reserved memory. Deletes optimizer state and performs 4 passes
        of clearing to handle PyTorch's allocator fragmentation.
        
        Returns:
            Tuple of (allocated_before, reserved_before, allocated_after, reserved_after) in GB
        """
        if not is_gpu_available():
            return 0.0, 0.0, 0.0, 0.0
        
        # Delete optimizer to free its state
        if hasattr(self, '_current_optimizer'):
            del self._current_optimizer
            self._current_optimizer = None
        
        # Note: sentence_model is not exported from string_codec
        # String encoding is now handled by string server, not a local model
        
        # AGGRESSIVE GPU clearing - PyTorch's allocator can hold onto memory even after tensors are deleted
        # Do multiple passes to try to force release of reserved memory
        allocated_before = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved_before = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        logger.error(f"📊 BEFORE CLEARING: Allocated={allocated_before:.3f} GB, Reserved={reserved_before:.3f} GB")
        
        # Pass 1: Standard clearing
        empty_gpu_cache()
        synchronize_gpu()
        gc.collect()
        
        # Pass 2: Clear again after GC
        empty_gpu_cache()
        synchronize_gpu()
        gc.collect()
        
        # Pass 3: Try to force release by resetting stats and clearing again
        reset_gpu_peak_memory_stats()
        empty_gpu_cache()
        synchronize_gpu()
        
        # Pass 4: Final aggressive clear
        gc.collect()
        empty_gpu_cache()
        
        # Check results (just log, don't block - model is on CPU so we can save)
        allocated_after = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved_after = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        logger.info(f"📊 AFTER CLEARING: Allocated={allocated_after:.3f} GB, Reserved={reserved_after:.3f} GB")
        logger.info(f"   Change: Allocated {allocated_before - allocated_after:.3f} GB, Reserved {reserved_before - reserved_after:.3f} GB")
        
        if allocated_after > 0.1:
            logger.warning(f"⚠️  {allocated_after:.2f} GB still allocated on GPU (fragmentation), but model is on CPU - proceeding with save")
        if reserved_after > 1.0:
            logger.warning(f"⚠️  {reserved_after:.2f} GB reserved on GPU (fragmentation), but model is on CPU - proceeding with save")
        
        # Don't block save - model walk confirmed no GPU state in model, so fragmentation is fine
        
        return allocated_before, reserved_before, allocated_after, reserved_after

    def _dump_gpu_memory_and_clear_before_checkpoint(self, _dump_cuda_memory_usage):
        """
        Dump GPU memory usage and clear before checkpoint save.
        
        Checks current GPU memory allocation, logs warnings if memory is still allocated,
        moves optimizer state to CPU, and performs aggressive GPU cache clearing.
        Used during OOM recovery in checkpoint saving.
        
        Args:
            _dump_cuda_memory_usage: Function to dump detailed CUDA memory usage
        """
        if not is_gpu_available():
            return
        
        # DUMP WHAT'S ACTUALLY USING GPU MEMORY
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        logger.error(f"📊 GPU MEMORY BEFORE PICKLE: Allocated={allocated:.2f} GB, Reserved={reserved:.2f} GB")
        if allocated > 0.1:  # More than 100MB
            logger.error(f"🚨 WARNING: {allocated:.2f} GB still allocated on GPU even though model params are on CPU!")
            logger.error(f"   This might be cached tensors, sentence transformer, or other GPU state")
            _dump_cuda_memory_usage(context="before pickle.dump")
        
        # CRITICAL: Force optimizer state to CPU if it exists
        # AdamW optimizer state can be 2x the size of parameters (momentum + variance)
        # Even if params are on CPU, optimizer state might be on GPU
        self._move_optimizer_state_to_cpu()
        
        # Clear GPU cache aggressively
        empty_gpu_cache()
        synchronize_gpu()
        # Force garbage collection to free up any lingering references
        gc.collect()
        empty_gpu_cache()
        # Clear again after GC
        empty_gpu_cache()
        # Try to release reserved memory by resetting peak stats
        reset_gpu_peak_memory_stats()

    def _save_checkpoint_on_cpu_with_oom_recovery(self, epoch_idx, checkpoint_start_time, sp_identifier,
                                                    training_start_timestamp, n_epochs, progress_dict,
                                                    optimizer, _dump_cuda_memory_usage, _walk_model_for_gpu,
                                                    _log_gpu_memory):
        """
        Save checkpoint on CPU to recover from CUDA OOM during checkpoint save.
        
        This is the fallback mechanism when checkpoint save fails due to GPU OOM.
        It moves all models to CPU, saves the checkpoint, then attempts to restore
        models back to GPU. If GPU restore fails due to OOM, training continues on CPU.
        
        Steps:
        1. Check and log current device placement
        2. Move all models/codecs/optimizer to CPU
        3. Clear GPU memory aggressively
        4. Validate no GPU state remains
        5. Save checkpoint file
        6. Attempt to restore models to GPU
        7. Handle restoration failures gracefully
        
        Args:
            epoch_idx: Current epoch index
            checkpoint_start_time: Time when checkpoint save started
            sp_identifier: Single predictor identifier
            training_start_timestamp: Timestamp for file naming
            n_epochs: Total number of epochs
            progress_dict: Training progress dictionary
            optimizer: Optimizer instance
            _dump_cuda_memory_usage: Function to dump CUDA memory usage
            _walk_model_for_gpu: Function to walk model for GPU tensors
            _log_gpu_memory: Function to log GPU memory
        """
        logger.info(f"🔄 Attempting to save checkpoint on CPU to avoid CUDA OOM...")
        try:
            force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
            
            # DETAILED DEVICE CHECK - log what's on GPU before moving
            logger.info("="*80)
            logger.info("🔍 DETAILED DEVICE CHECK BEFORE MOVING TO CPU:")
            logger.info("="*80)
            
            # Check predictor
            if list(self.predictor.parameters()):
                predictor_device = next(self.predictor.parameters()).device
                predictor_params = sum(p.numel() for p in self.predictor.parameters())
                logger.info(f"   Predictor: {predictor_device.type} (device: {predictor_device}), {predictor_params:,} params")
            else:
                predictor_device = None
                logger.info(f"   Predictor: No parameters")
            
            # Check encoder
            if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                if list(self.embedding_space.encoder.parameters()):
                    encoder_device = next(self.embedding_space.encoder.parameters()).device
                    encoder_params = sum(p.numel() for p in self.embedding_space.encoder.parameters())
                    logger.info(f"   Encoder: {encoder_device.type} (device: {encoder_device}), {encoder_params:,} params")
                else:
                    encoder_device = None
                    logger.info(f"   Encoder: No parameters")
            else:
                encoder_device = None
                logger.info(f"   Encoder: Not found")
            
            # Check codecs for GPU state - only log if found (StringCodec has parameters!)
            gpu_codecs_found = []
            if hasattr(self.embedding_space, 'col_codecs'):
                for col_name, codec in self.embedding_space.col_codecs.items():
                    codec_has_gpu = False
                    codec_params = 0
                    
                    # Check parameters (StringCodec, JsonCodec have these!)
                    if hasattr(codec, 'parameters') and list(codec.parameters()):
                        codec_device = next(codec.parameters()).device
                        codec_params = sum(p.numel() for p in codec.parameters())
                        if codec_device.type in ['cuda', 'mps']:
                            codec_has_gpu = True
                            gpu_codecs_found.append((col_name, codec_device, codec_params, 'params'))
                    
                    # Check buffers
                    if not codec_has_gpu and hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                        for buffer in codec.buffers():
                            if buffer.device.type in ['cuda', 'mps']:
                                codec_has_gpu = True
                                buffer_size = sum(b.numel() for b in codec.buffers() if b.device.type in ['cuda', 'mps'])
                                gpu_codecs_found.append((col_name, buffer.device, buffer_size, 'buffers'))
                                break
                    
                    # Check embedded modules (StringCodec: bert_projection, feature_embedding_mlp, merge_mlp)
                    for attr_name in ['bert_projection', 'feature_embedding_mlp', 'merge_mlp', 'projection', 'encoder']:
                        if hasattr(codec, attr_name):
                            embedded_module = getattr(codec, attr_name)
                            if embedded_module is not None and hasattr(embedded_module, 'parameters'):
                                if list(embedded_module.parameters()):
                                    embedded_device = next(embedded_module.parameters()).device
                                    if embedded_device.type == 'cuda':
                                        embedded_params = sum(p.numel() for p in embedded_module.parameters())
                                        if not any(c[0] == col_name for c in gpu_codecs_found):
                                            gpu_codecs_found.append((col_name, embedded_device, embedded_params, f'{attr_name}'))
            
            if gpu_codecs_found:
                logger.info(f"   🚨 Found {len(gpu_codecs_found)} codecs with GPU state:")
                total_gpu_params = sum(params for _, _, params, _ in gpu_codecs_found)
                logger.info(f"   Total GPU params in codecs: {total_gpu_params:,}")
                for col_name, device, params, source in gpu_codecs_found:
                    logger.info(f"      - {col_name}: {params:,} params on {device} ({source})")
            logger.info("="*80)
            
            # Move models to CPU (only if not already in CPU mode)
            if not force_cpu:
                if predictor_device and predictor_device.type in ['cuda', 'mps']:
                    logger.info(f"   Moving predictor to CPU...")
                    self.predictor = self.predictor.cpu()
                if encoder_device and encoder_device.type in ['cuda', 'mps']:
                    logger.info(f"   Moving encoder to CPU...")
                    self.embedding_space.encoder = self.embedding_space.encoder.cpu()
                    
                    # CRITICAL: Delete cached encoder tensors to free GPU memory
                    # column_encodings and token_status_mask are cached tensors - delete them, not move
                    if hasattr(self.embedding_space.encoder, 'column_encodings'):
                        if isinstance(self.embedding_space.encoder.column_encodings, torch.Tensor):
                            logger.info(f"   Deleting encoder.column_encodings to free GPU memory...")
                            del self.embedding_space.encoder.column_encodings
                            self.embedding_space.encoder.column_encodings = None
                    if hasattr(self.embedding_space.encoder, 'token_status_mask'):
                        if isinstance(self.embedding_space.encoder.token_status_mask, torch.Tensor):
                            logger.info(f"   Deleting encoder.token_status_mask to free GPU memory...")
                            del self.embedding_space.encoder.token_status_mask
                            self.embedding_space.encoder.token_status_mask = None
            
            # CRITICAL: Move target_codec loss_fn.alpha to CPU if it exists
            if hasattr(self, 'target_codec') and self.target_codec is not None:
                if hasattr(self.target_codec, 'loss_fn') and self.target_codec.loss_fn is not None:
                    if hasattr(self.target_codec.loss_fn, 'alpha'):
                        if isinstance(self.target_codec.loss_fn.alpha, torch.Tensor):
                            if self.target_codec.loss_fn.alpha.device.type == 'cuda':
                                logger.info(f"   Moving target_codec.loss_fn.alpha to CPU...")
                                self.target_codec.loss_fn.alpha = self.target_codec.loss_fn.alpha.cpu()
            
            # CRITICAL: Move ALL codecs to CPU - check parameters, buffers, and embedded modules
            self._move_codecs_to_cpu()
            
            # CRITICAL: Clear optimizer state from GPU - optimizer states can be HUGE (AdamW stores 2x params)
            # Optimizer state is on same device as parameters, but we need to explicitly clear it
            self._move_optimizer_state_to_cpu()
            
            # CRITICAL: No local sentence transformer to clear - using string server
            self._check_sentence_transformer_device()
            
            # DUMP WHAT'S ACTUALLY USING GPU MEMORY and clear
            self._dump_gpu_memory_and_clear_before_checkpoint(_dump_cuda_memory_usage)
            
            # WALK THE ENTIRE MODEL BEFORE PICKLE.DUMP - CHECK FOR ANY GPU STATE
            logger.info("="*80)
            logger.info("🔍 WALKING ENTIRE MODEL BEFORE PICKLE.DUMP - CHECKING FOR GPU STATE:")
            logger.info("="*80)
            
            all_gpu_items = self._collect_all_gpu_items(_walk_model_for_gpu)
            
            # Report findings
            if all_gpu_items:
                logger.error(f"🚨 FOUND {len(all_gpu_items)} GPU ITEMS:")
                total_elements = 0
                for item_name, item_type, shape, numel, device in all_gpu_items:
                    total_elements += numel
                    logger.error(f"   - {item_name}: {item_type}, shape={shape}, elements={numel:,}, device={device}")
                logger.error(f"   📊 TOTAL GPU ELEMENTS: {total_elements:,}")
                logger.error("="*80)
                raise RuntimeError(f"FOUND {len(all_gpu_items)} GPU ITEMS BEFORE PICKLE.DUMP! Cannot save checkpoint with GPU state.")
            else:
                logger.info("✅ NO GPU STATE FOUND - Safe to pickle.dump")
                logger.info("="*80)
            
            # CRITICAL: Clear ALL GPU memory before pickle.dump
            # pickle.dump might trigger GPU allocation if there are any references
            self._clear_gpu_memory_aggressively()
            
            # Save full pickle (not just state dicts) - everything is now on CPU
            checkpoint_dir = self._output_dir if self._output_dir else "."
            id_suffix = f"_{sp_identifier}" if sp_identifier else ""
            # Include training_start_timestamp to prevent stomping across re-runs
            epoch_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_epoch_{epoch_idx}.pickle")
            
            _log_gpu_memory(f"BEFORE PICKLE.DUMP (epoch {epoch_idx})", log_level=logging.ERROR)
            
            # CRITICAL: Validate and fix model integrity before saving
            self._validate_and_fix_before_save()
            
            # Use map_location='cpu' context to prevent any GPU allocation during pickle
            _log_gpu_memory(f"BEFORE PICKLE.DUMP FILE OPEN (epoch {epoch_idx})", log_level=logging.ERROR)
            with open(epoch_checkpoint_path, "wb") as f:
                _log_gpu_memory(f"BEFORE PICKLE.DUMP CALL (epoch {epoch_idx})", log_level=logging.ERROR)
                # Temporarily disable CUDA to prevent any GPU allocation during pickle
                # NOTE: This ONLY works for CUDA, not MPS - MPS doesn't have _initialized flag
                cuda_was_available = is_cuda_available()
                if cuda_was_available:
                    # Set environment to prevent CUDA allocation
                    old_cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES')
                    os.environ['CUDA_VISIBLE_DEVICES'] = ''
                    # Force PyTorch to think CUDA is unavailable (CUDA-specific hack)
                    torch.cuda._initialized = False
                
                try:
                    pickle.dump(self, f)
                    # Verify file was written
                    if not os.path.exists(epoch_checkpoint_path):
                        raise RuntimeError(f"Checkpoint file was not created: {epoch_checkpoint_path}")
                    file_size = os.path.getsize(epoch_checkpoint_path)
                    if file_size == 0:
                        raise RuntimeError(f"Checkpoint file is empty: {epoch_checkpoint_path}")
                    logger.info(f"✅ Checkpoint saved: {epoch_checkpoint_path} ({file_size / 1024 / 1024:.2f} MB)")
                except Exception as pickle_err:
                    logger.error(f"❌ pickle.dump failed: {pickle_err}")
                    # Clean up partial file
                    if os.path.exists(epoch_checkpoint_path):
                        try:
                            os.remove(epoch_checkpoint_path)
                            logger.info(f"   Removed partial checkpoint file")
                        except:
                            pass
                    raise
                finally:
                    # Restore CUDA state (CUDA-specific)
                    if cuda_was_available:
                        if old_cuda_visible is not None:
                            os.environ['CUDA_VISIBLE_DEVICES'] = old_cuda_visible
                        else:
                            del os.environ['CUDA_VISIBLE_DEVICES']
                        torch.cuda._initialized = True
            _log_gpu_memory(f"AFTER PICKLE.DUMP FILE CLOSE (epoch {epoch_idx})", log_level=logging.ERROR)
            
            # Also save latest checkpoint (only if we successfully restored to GPU, or if force_cpu)
            # Skip if restore failed due to OOM to avoid another pickle.dump with models on CPU
            # Include training_start_timestamp to prevent stomping across re-runs
            if not (hasattr(self, '_restore_failed_oom') and self._restore_failed_oom):
                latest_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_latest.pickle")
                try:
                    with open(latest_checkpoint_path, "wb") as f:
                        pickle.dump(self, f)
                    logger.info(f"✅ Latest checkpoint saved: {latest_checkpoint_path}")
                except Exception as latest_err:
                    logger.warning(f"⚠️  Failed to save latest checkpoint: {latest_err}")
                    # Don't fail the whole checkpoint save if latest fails
            else:
                logger.warning(f"⚠️  Skipping latest checkpoint save (restore to GPU failed due to OOM)")
            
            # Save metadata
            current_metrics = None
            if hasattr(self, 'training_metrics') and self.training_metrics:
                current_metrics = self.training_metrics.copy()
            
            status_metadata = {
                "epoch": epoch_idx,
                "total_epochs": n_epochs,
                "progress_percent": (epoch_idx + 1) / n_epochs * 100 if n_epochs > 0 else 0,
                "training_loss": progress_dict.get("current_loss"),
                "validation_loss": progress_dict.get("validation_loss"),
                "metrics": current_metrics,
                "checkpoint_path": epoch_checkpoint_path,
                "latest_checkpoint_path": latest_checkpoint_path,
                "checkpoint_save_time_secs": time.time() - checkpoint_start_time,
                "is_training": True,
                "timestamp": time.time(),
                "data_passes": epoch_idx + 1,
                "saved_on_cpu": True  # Mark that this was saved on CPU
            }
            # Include training_start_timestamp to prevent stomping across re-runs
            status_metadata_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_training_status.json")
            with open(status_metadata_path, "w") as f:
                json.dump(status_metadata, f, indent=2, default=str)
            
            logger.info(f"✅ Epoch checkpoint saved on CPU: {epoch_checkpoint_path} (took {time.time() - checkpoint_start_time:.3f}s total)")
            
            # CRITICAL: Clear GPU cache aggressively before trying to restore models
            # DataLoader workers may be holding GPU memory
            if is_gpu_available() and not force_cpu:
                logger.info(f"   Clearing GPU cache before restoring models...")
                empty_gpu_cache()
                synchronize_gpu()
                gc.collect()
                empty_gpu_cache()
                
                # Check available memory
                free_memory = get_gpu_memory_reserved() - get_gpu_memory_allocated()
                logger.info(f"   GPU memory: {get_gpu_memory_allocated():.2f} GB allocated, {get_gpu_memory_reserved():.2f} GB reserved, ~{free_memory:.2f} GB free")
            
            # Move models back to original device ONLY if not in CPU mode
            if not force_cpu:
                try:
                    if predictor_device and predictor_device.type in ['cuda', 'mps']:
                        logger.info(f"   Moving predictor back to {predictor_device}...")
                        self.predictor = self.predictor.to(predictor_device)
                    if encoder_device and encoder_device.type in ['cuda', 'mps']:
                        logger.info(f"   Moving encoder back to {encoder_device}...")
                        self.embedding_space.encoder = self.embedding_space.encoder.to(encoder_device)
                except RuntimeError as oom_err:
                    if "out of memory" in str(oom_err).lower() or "oom" in str(oom_err).lower():
                        logger.error(f"   ❌ CUDA OOM when restoring models to GPU - models will stay on CPU")
                        logger.error(f"   EXACT ERROR: {oom_err}")
                        logger.error(f"   Error type: {type(oom_err).__name__}")
                        logger.exception(f"   Full traceback:")
                        logger.error(f"   This is OK - training can continue on CPU, but will be slower")
                        logger.error(f"   Consider reducing batch_size or num_workers if this persists")
                        # Mark that restore failed so we skip further GPU operations
                        self._restore_failed_oom = True
                        # Don't raise - continue with models on CPU
                        force_cpu = True  # Prevent further GPU operations
                    else:
                        raise
                
                # Only continue with GPU restore if we didn't hit OOM
                if not (hasattr(self, '_restore_failed_oom') and self._restore_failed_oom):
                    # Note: column_encodings and token_status_mask were deleted (set to None) - will be recreated on next encode()
                    
                    # CRITICAL: Move target_codec loss_fn.alpha back to GPU if it exists
                    if hasattr(self, 'target_codec') and self.target_codec is not None:
                        if hasattr(self.target_codec, 'loss_fn') and self.target_codec.loss_fn is not None:
                            if hasattr(self.target_codec.loss_fn, 'alpha'):
                                if isinstance(self.target_codec.loss_fn.alpha, torch.Tensor):
                                    # Find the device from target_codec parameters
                                    target_codec_device = None
                                    if hasattr(self.target_codec, 'parameters') and list(self.target_codec.parameters()):
                                        target_codec_device = next(self.target_codec.parameters()).device
                                    elif encoder_device:
                                        target_codec_device = encoder_device
                                    
                                    if target_codec_device and target_codec_device.type in ['cuda', 'mps']:
                                        if self.target_codec.loss_fn.alpha.device.type == 'cpu':
                                            logger.info(f"   Moving target_codec.loss_fn.alpha back to {target_codec_device}...")
                                            self.target_codec.loss_fn.alpha = self.target_codec.loss_fn.alpha.to(target_codec_device)
                    
                    # CRITICAL: Restore ALL codecs back to GPU (they were moved to CPU for checkpoint save)
                    if hasattr(self.embedding_space, 'col_codecs') and encoder_device:
                        restored_count = 0
                        failed_count = 0
                        for col_name, codec in self.embedding_space.col_codecs.items():
                            try:
                                # Check if codec has any CPU parameters/buffers
                                needs_restore = False
                                if hasattr(codec, 'parameters') and list(codec.parameters()):
                                    if next(codec.parameters()).device.type == 'cpu':
                                        needs_restore = True
                                if not needs_restore and hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                                    for buffer in codec.buffers():
                                        if buffer.device.type == 'cpu':
                                            needs_restore = True
                                            break
                                
                                if needs_restore:
                                    codec.to(encoder_device)
                                    restored_count += 1
                                    logger.info(f"   Restored codec '{col_name}' to {encoder_device}")
                            except Exception as restore_err:
                                failed_count += 1
                                logger.error(f"   ❌ Failed to restore codec '{col_name}': {restore_err}")
                        
                        if restored_count > 0:
                            logger.info(f"   ✅ Restored {restored_count} codecs to {encoder_device}")
                        if failed_count > 0:
                            logger.error(f"   ⚠️  Failed to restore {failed_count} codecs - may cause device mismatch errors")
                    
                    # CRITICAL: Restore optimizer state to GPU (it was moved to CPU for checkpoint save)
                    if hasattr(self, '_current_optimizer') and self._current_optimizer is not None:
                        try:
                            optimizer = self._current_optimizer
                            optimizer_state_restored = 0
                            for param_group in optimizer.param_groups:
                                for param in param_group['params']:
                                    if param in optimizer.state:
                                        state = optimizer.state[param]
                                        for key, value in state.items():
                                            if isinstance(value, torch.Tensor) and value.device.type == 'cpu':
                                                # Move optimizer state to same device as parameter
                                                param_device = param.device
                                                state[key] = value.to(param_device)
                                                optimizer_state_restored += 1
                            if optimizer_state_restored > 0:
                                logger.info(f"   ✅ Restored {optimizer_state_restored} optimizer state tensors to GPU")
                        except Exception as opt_err:
                            logger.error(f"   ❌ Failed to restore optimizer state: {opt_err}")
                            # If optimizer state restore fails, we need to recreate optimizer
                            # Otherwise training will fail with device mismatch
                            logger.warning(f"   ⚠️  Optimizer state restore failed - optimizer may need to be recreated")
                else:
                    logger.warning(f"   ⚠️  Skipping GPU restore operations (OOM during initial restore)")
            else:
                logger.info(f"   Models staying on CPU (CPU mode enabled)")
            
        except Exception as cpu_save_error:
            logger.error(f"❌ Failed to save checkpoint on CPU: {cpu_save_error}")
            # Try to move models back to GPU even if save failed (only if not in CPU mode)
            force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
            if not force_cpu:
                try:
                    if predictor_device and predictor_device.type in ['cuda', 'mps']:
                        self.predictor = self.predictor.to(predictor_device)
                    if encoder_device and encoder_device.type in ['cuda', 'mps']:
                        self.embedding_space.encoder = self.embedding_space.encoder.to(encoder_device)
                        
                        # Note: column_encodings and token_status_mask were deleted (set to None) - will be recreated on next encode()
                    
                    # CRITICAL: Move target_codec loss_fn.alpha back to GPU if it exists
                    if hasattr(self, 'target_codec') and self.target_codec is not None:
                        if hasattr(self.target_codec, 'loss_fn') and self.target_codec.loss_fn is not None:
                            if hasattr(self.target_codec.loss_fn, 'alpha'):
                                if isinstance(self.target_codec.loss_fn.alpha, torch.Tensor):
                                    target_codec_device = encoder_device if encoder_device else None
                                    if target_codec_device and target_codec_device.type in ['cuda', 'mps']:
                                        if self.target_codec.loss_fn.alpha.device.type == 'cpu':
                                            self.target_codec.loss_fn.alpha = self.target_codec.loss_fn.alpha.to(target_codec_device)
                    
                    # CRITICAL: Restore ALL codecs back to GPU (they were moved to CPU for checkpoint save)
                    if hasattr(self.embedding_space, 'col_codecs') and encoder_device:
                        restored_count = 0
                        failed_count = 0
                        for col_name, codec in self.embedding_space.col_codecs.items():
                            try:
                                # Check if codec has any CPU parameters/buffers
                                needs_restore = False
                                if hasattr(codec, 'parameters') and list(codec.parameters()):
                                    if next(codec.parameters()).device.type == 'cpu':
                                        needs_restore = True
                                if not needs_restore and hasattr(codec, 'buffers') and isinstance(codec, torch.nn.Module):
                                    for buffer in codec.buffers():
                                        if buffer.device.type == 'cpu':
                                            needs_restore = True
                                            break
                                
                                if needs_restore:
                                    codec.to(encoder_device)
                                    restored_count += 1
                                    logger.info(f"   Restored codec '{col_name}' to {encoder_device}")
                            except Exception as restore_err:
                                failed_count += 1
                                logger.error(f"   ❌ Failed to restore codec '{col_name}': {restore_err}")
                        
                        if restored_count > 0:
                            logger.info(f"   ✅ Restored {restored_count} codecs to {encoder_device}")
                        if failed_count > 0:
                            logger.error(f"   ⚠️  Failed to restore {failed_count} codecs - may cause device mismatch errors")
                    
                    # CRITICAL: Restore optimizer state to GPU (it was moved to CPU for checkpoint save)
                    if hasattr(self, '_current_optimizer') and self._current_optimizer is not None:
                        try:
                            optimizer = self._current_optimizer
                            optimizer_state_restored = 0
                            for param_group in optimizer.param_groups:
                                for param in param_group['params']:
                                    if param in optimizer.state:
                                        state = optimizer.state[param]
                                        for key, value in state.items():
                                            if isinstance(value, torch.Tensor) and value.device.type == 'cpu':
                                                # Move optimizer state to same device as parameter
                                                param_device = param.device
                                                state[key] = value.to(param_device)
                                                optimizer_state_restored += 1
                            if optimizer_state_restored > 0:
                                logger.info(f"   ✅ Restored {optimizer_state_restored} optimizer state tensors to GPU")
                        except Exception as opt_err:
                            logger.error(f"   ❌ Failed to restore optimizer state: {opt_err}")
                            # If optimizer state restore fails, we need to recreate optimizer
                            # Otherwise training will fail with device mismatch
                            logger.warning(f"   ⚠️  Optimizer state restore failed - optimizer may need to be recreated")
                except Exception as restore_err:
                    logger.error(f"❌ Failed to restore models to GPU: {restore_err}")
                    logger.error(traceback.format_exc())
            # Clear cache and continue training
            if is_gpu_available():
                empty_gpu_cache()
                synchronize_gpu()
                logger.warning(f"   Skipping checkpoint save for this epoch")

    def _should_send_progress_callback(self, epoch_idx, n_epochs):
        """
        Determine if progress callback should be sent for this epoch.
        
        Uses smart frequency to reduce noise:
        - Short training (≤10 epochs): Every epoch
        - Medium training (≤50 epochs): Every 2 epochs
        - Long training (≤100 epochs): Every 5 epochs
        - Very long training (>100 epochs): Every 10 epochs or ~10% intervals
        
        Always sends callback on the last epoch.
        
        Args:
            epoch_idx: Current epoch index
            n_epochs: Total number of epochs
            
        Returns:
            bool: True if callback should be sent for this epoch
        """
        if n_epochs <= 10:
            # Short training: send every epoch
            return True
        elif n_epochs <= 50:
            # Medium training: send every 2 epochs or ~10% intervals
            return (epoch_idx % 2 == 0) or (epoch_idx == n_epochs - 1)
        elif n_epochs <= 100:
            # Long training: send every 5 epochs or ~10% intervals  
            return (epoch_idx % 5 == 0) or (epoch_idx == n_epochs - 1)
        else:
            # Very long training: send every 10 epochs or ~10% intervals
            interval = max(10, n_epochs // 10)  # At least every 10 epochs, or 10% of total
            return (epoch_idx % interval == 0) or (epoch_idx == n_epochs - 1)

    def _setup_sp_identifier_filter(self, sp_identifier):
        """
        Set up logging filter for single predictor training run identifier.
        
        Adds a filter to the logger that includes the SP identifier in log messages.
        This helps track logs from specific single predictor training runs.
        
        Args:
            sp_identifier: Identifier for this SP (e.g., target column name)
        """
        if sp_identifier:
            self.run_identifier = f"[SP:{sp_identifier}]"
            
            # Add filter to the logger for this module
            sp_filter = SPIdentifierFilter(self.run_identifier, self)
            logger.addFilter(sp_filter)
            
            # Store filter reference so we can remove it later if needed
            self._sp_log_filter = sp_filter

    def _log_parameter_breakdown(self, params, trainable_count, frozen_count):
        """
        Log parameter counts and store training params for gradient clipping.
        
        Computes and logs the breakdown of parameters across predictor and encoder,
        showing counts and percentages. Also stores params as instance variable
        for use in gradient clipping during training.
        
        Args:
            params: List of parameters to optimize (from _setup_training_parameters)
            trainable_count: Number of trainable parameters
            frozen_count: Number of frozen parameters
        """
        # Compute counts efficiently without storing full parameter lists
        predictor_count = sum(p.numel() for p in self.predictor.parameters())
        encoder_count = sum(p.numel() for p in self.embedding_space.encoder.parameters())
        total_count = predictor_count + encoder_count
        
        # CRITICAL: Store params as instance variable for gradient clipping
        # This is used throughout training for gradient clipping and optimizer recreation
        self._training_params = params
        
        # Log breakdown
        logger.info(f"   📊 Parameter breakdown:")
        logger.info(f"      Predictor: {predictor_count:,} params ({predictor_count/total_count:.1%})")
        logger.info(f"      Encoder: {encoder_count:,} params ({encoder_count/total_count:.1%})")
        logger.info(f"      Trainable: {trainable_count:,} params ({trainable_count/total_count:.1%})")
        logger.info(f"      Frozen: {frozen_count:,} params ({frozen_count/total_count:.1%})")

    def _check_abort_finish_files(self, job_id, batch_idx, log_prefix, progress_dict):
        """
        Check for ABORT and FINISH files to allow external control of training.
        
        ABORT file: Causes immediate training termination with exception
        FINISH file: Triggers graceful early stop (returns True to signal break)
        
        Args:
            job_id: Job ID to check files for
            batch_idx: Current batch index (for logging)
            log_prefix: Prefix for log messages
            progress_dict: Progress dictionary to update if files detected
            
        Returns:
            bool: True if FINISH file detected (caller should break), False otherwise
            
        Raises:
            FeatrixTrainingAbortedException: If ABORT file detected
        """
        if not job_id:
            return False
            
        # Check for ABORT file (highest priority - hard stop)
        from featrix.neural.embedded_space import check_abort_files
        abort_file_path = check_abort_files(job_id)
        if abort_file_path:
            logger.error(f"{log_prefix}🚫 ABORT file detected for job {job_id} during batch {batch_idx} - exiting single predictor training")
            logger.error(f"{log_prefix}🚫 ABORT file path: {abort_file_path}")
            progress_dict["interrupted"] = "ABORT file detected"
        
            # Mark job as FAILED before exiting
            try:
                from lib.job_manager import JobStatus
                from lib.job_manager import load_job, update_job_status
                job_data = load_job(job_id)
                if job_data:
                    update_job_status(job_id, JobStatus.FAILED, {
                        "error_message": f"Training aborted due to ABORT file at {abort_file_path}"
                    })
                logger.info(f"{log_prefix}🚫 Job {job_id} marked as FAILED due to ABORT file")
            except Exception as e:
                logger.error(f"{log_prefix}Failed to update job status before exit: {e}")
        
            # Raise exception with the actual path found
            from featrix.neural.exceptions import FeatrixTrainingAbortedException
            raise FeatrixTrainingAbortedException(
                f"Single predictor training aborted due to ABORT file at {abort_file_path}",
                job_id=job_id,
                abort_file_path=abort_file_path
            )
    
        # Check for FINISH file (graceful early stop)
        from featrix.neural.embedded_space import check_finish_files
        if check_finish_files(job_id):
            logger.warning(f"{log_prefix}⏹️  FINISH file detected for job {job_id} during batch {batch_idx} - graceful early stop")
            progress_dict["interrupted"] = "FINISH file detected"
            progress_dict["early_stop_reason"] = "User requested early stop via FINISH flag"
            return True  # Signal caller to break out of training loop
        
        return False  # No files detected, continue training

    def _diagnose_dead_gradients(self, unclipped_norm, loss, out, targets, fine_tune, epoch_idx, batch_idx):
        """
        Diagnose why gradients are dead (near-zero) to aid in debugging training issues.
        
        Performs comprehensive analysis of:
        - Loss value and gradient propagation
        - Model outputs and targets
        - Parameter gradient status (predictor and encoder)
        - Training mode verification
        - Batch embedding gradient flow
        
        Args:
            unclipped_norm: Unclipped gradient norm
            loss: Loss tensor
            out: Model output tensor
            targets: Target tensor
            fine_tune: Whether fine-tuning is enabled
            epoch_idx: Current epoch index
            batch_idx: Current batch index
        """
        logger.error(f"🔍 DEAD GRADIENT DIAGNOSTICS (epoch={epoch_idx}, batch={batch_idx}):")
        logger.error(f"   Loss value: {loss.item():.6f}")
        logger.error(f"   Loss requires_grad: {loss.requires_grad}")
        logger.error(f"   Output stats: min={out.min().item():.4f}, max={out.max().item():.4f}, mean={out.mean().item():.4f}")
        logger.error(f"   Target stats: min={targets.min().item()}, max={targets.max().item()}")
        
        # Check which parameters have gradients
        params_with_grads = []
        params_without_grads = []
        params_not_requiring_grad = []
        total_params = 0
        
        for name, param in self.predictor.named_parameters():
            total_params += 1
            if not param.requires_grad:
                params_not_requiring_grad.append(name)
            elif param.grad is None:
                params_without_grads.append(name)
            else:
                grad_norm = param.grad.data.norm(2).item()
                if grad_norm > 0:
                    params_with_grads.append((name, grad_norm))
        
        logger.error(f"   Total predictor parameters: {total_params}")
        logger.error(f"   Parameters requiring grad: {total_params - len(params_not_requiring_grad)}")
        logger.error(f"   Parameters with gradients: {len(params_with_grads)}")
        logger.error(f"   Parameters without gradients: {len(params_without_grads)}")
        
        if params_not_requiring_grad:
            logger.error(f"   ⚠️  Parameters NOT requiring grad (first 5): {params_not_requiring_grad[:5]}")
        if params_without_grads:
            logger.error(f"   ⚠️  Parameters with None gradients (first 5): {params_without_grads[:5]}")
        if params_with_grads:
            logger.error(f"   ✅ Parameters with non-zero gradients (first 5): {[(n, f'{v:.6e}') for n, v in params_with_grads[:5]]}")
        
        # Check embedding space encoder if fine-tuning
        if fine_tune:
            encoder_params_with_grads = []
            encoder_params_without_grads = []
            encoder_params_not_requiring_grad = []
            encoder_total = 0
            
            for name, param in self.embedding_space.encoder.named_parameters():
                encoder_total += 1
                if not param.requires_grad:
                    encoder_params_not_requiring_grad.append(name)
                elif param.grad is None:
                    encoder_params_without_grads.append(name)
                else:
                    grad_norm = param.grad.data.norm(2).item()
                    if grad_norm > 0:
                        encoder_params_with_grads.append((name, grad_norm))
            
            logger.error(f"   Encoder total parameters: {encoder_total}")
            logger.error(f"   Encoder parameters with gradients: {len(encoder_params_with_grads)}")
            logger.error(f"   Encoder parameters without gradients: {len(encoder_params_without_grads)}")
            
            if encoder_params_not_requiring_grad:
                logger.error(f"   ⚠️  Encoder parameters NOT requiring grad (first 5): {encoder_params_not_requiring_grad[:5]}")
        
        # Check if batch_full was detached (stored in a local var earlier in the batch loop)
        # We need access to batch_full here, but it's out of scope. Log what we can.
        # This is a limitation of the refactoring - we'd need to pass batch_full as a parameter
        # or store it as self._last_batch_full for diagnostics. For now, just note this.
        
        # Check model training mode
        logger.error(f"   Predictor training mode: {self.predictor.training}")
        logger.error(f"   Encoder training mode: {self.embedding_space.encoder.training}")

    def _set_training_modes(self, fine_tune):
        """
        Set predictor and encoder to correct training modes with verification.
        
        The predictor is always set to training mode. The encoder is set to
        training mode if fine_tune=True, otherwise eval mode to freeze weights.
        
        Includes assertions to catch silent failures where .train()/.eval() 
        is called but the mode doesn't actually change.
        
        Args:
            fine_tune: Whether to fine-tune the encoder (True) or freeze it (False)
        """
        # CRITICAL: Set models to training mode
        # The predictor was set to eval() mode during initialization (line 1894)
        # to get output dimensions. We MUST set it to train() mode before training!
        logger.info("🔄 Setting predictor to TRAIN mode")
        self.predictor.train()
        assert self.predictor.training == True, f"❌ CRITICAL BUG: predictor.train() was called but predictor.training={self.predictor.training}! Model will not learn!"
        
        if fine_tune:
            logger.info("🔄 Setting encoder to TRAIN mode (fine-tuning enabled)")
            self.embedding_space.encoder.train()
            assert self.embedding_space.encoder.training == True, f"❌ CRITICAL BUG: encoder.train() was called but encoder.training={self.embedding_space.encoder.training}! Encoder will not fine-tune!"
        else:
            logger.info("🔒 Setting encoder to EVAL mode (fine-tuning disabled)")
            self.embedding_space.encoder.eval()
            assert self.embedding_space.encoder.training == False, f"❌ CRITICAL BUG: encoder.eval() was called but encoder.training={self.embedding_space.encoder.training}! Encoder should be frozen!"
        
        logger.info(f"✅ Training mode verified: predictor.training={self.predictor.training}, encoder.training={self.embedding_space.encoder.training}")

    def _verify_predictor_device(self, epoch_idx, batch_idx, log_prefix):
        """
        Verify predictor is on correct device (GPU if available, else CPU).
        
        Only runs on first batch of first epoch. If GPU is available but predictor
        is on CPU, moves it to GPU and logs the correction. This catches cases where
        the predictor wasn't properly moved to GPU during initialization.
        
        Args:
            epoch_idx: Current epoch index
            batch_idx: Current batch index
            log_prefix: Prefix for log messages
        """
        # Only check on first batch of first epoch
        if epoch_idx != 0 or batch_idx != 0:
            return
            
        predictor_device = next(self.predictor.parameters()).device if list(self.predictor.parameters()) else None
        
        if is_gpu_available():
            if predictor_device is None or predictor_device.type == 'cpu':
                logger.error(f"{log_prefix}❌ PREDICTOR IS ON CPU! Moving to GPU...")
                self.predictor = self.predictor.to(get_device())
                predictor_device = next(self.predictor.parameters()).device
            logger.info(f"{log_prefix}✅ PREDICTOR DEVICE VERIFICATION: {predictor_device}")
        else:
            logger.info(f"{log_prefix}⚠️  Running on CPU (CUDA not available)")

    def _handle_nan_gradients(self, total_norm, consecutive_nan_batches, max_consecutive_nan_batches, 
                              loss, epoch_idx, batch_idx, job_id, lr_value, optimizer):
        """
        Handle NaN/Inf gradients by logging diagnostics and deciding whether to skip or abort.
        
        Strategy:
        - Count consecutive NaN batches
        - Log detailed diagnostics
        - Skip batch and zero gradients (allow training to continue)
        - Abort if NaN persists for too many consecutive batches
        
        Args:
            total_norm: Gradient norm (may be NaN/Inf)
            consecutive_nan_batches: Current count of consecutive NaN batches
            max_consecutive_nan_batches: Maximum allowed before abort
            loss: Loss tensor
            epoch_idx: Current epoch
            batch_idx: Current batch
            job_id: Job ID for logging
            lr_value: Current learning rate
            optimizer: Optimizer instance
            
        Returns:
            tuple: (should_continue, updated_consecutive_nan_batches)
                - should_continue: True if should skip and continue, False if should abort
                - updated_consecutive_nan_batches: Incremented count
                
        Raises:
            DeadNetworkError: If NaN persists for too many consecutive batches
        """
        consecutive_nan_batches += 1
        
        logger.error(f"💥 FATAL: NaN/Inf gradients in single predictor! total_norm={total_norm}")
        logger.error(f"   Job ID: {job_id}")
        logger.error(f"   Output Dir: {self.embedding_space.output_dir}")
        logger.error(f"   Target Column: {self.target_col_name}")
        logger.error(f"   Loss value: {loss.item()}")
        logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
        logger.error(f"   Consecutive NaN batches: {consecutive_nan_batches}/{max_consecutive_nan_batches}")
        
        # Check individual parameter gradients to identify the source
        nan_params = []
        for name, param in self.predictor.named_parameters():
            if param.grad is not None and (torch.isnan(param.grad).any() or torch.isinf(param.grad).any()):
                nan_params.append(name)
        
        if nan_params:
            logger.warning(f"   Parameters with NaN/Inf gradients: {nan_params[:5]}...")
        
        # ABORT if NaN persists for too many consecutive batches
        if consecutive_nan_batches >= max_consecutive_nan_batches:
            from featrix.neural.training_exceptions import DeadNetworkError
            logger.error("="*80)
            logger.error(f"💀 ABORTING: {consecutive_nan_batches} consecutive batches with NaN gradients!")
            logger.error(f"   Training is permanently broken - model cannot recover")
            logger.error(f"   Job ID: {job_id}")
            logger.error(f"   Output Dir: {self.embedding_space.output_dir}")
            logger.error(f"   Target Column: {self.target_col_name}")
            logger.error(f"   Current LR: {lr_value:.6e}")
            logger.error(f"   Loss value: {loss.item() if not torch.isnan(loss) else 'nan'}")
            logger.error(f"   Batch: {batch_idx}")
            logger.error("="*80)
            
            recommendations = [
                "Reduce learning rate by 10x and restart training",
                "Check for data quality issues (extreme values, corrupted data)",
                "Verify embedding space quality",
                f"Current LR ({lr_value:.6e}) may be too high - caused gradient explosion"
            ]
            raise DeadNetworkError(
                message=f"Persistent NaN gradients for {consecutive_nan_batches} consecutive batches",
                epoch=epoch_idx,
                recommendations=recommendations
            )
        
        # CRITICAL: ABORT training - NaN means embeddings are corrupted
        logger.error("   🚨 ABORTING: Single predictor training corrupted by NaN/Inf gradients")
        logger.error("   This indicates the embedding space is invalid or the predictor has numerical instability")
        
        # Raise exception to stop training and fail QA test
        raise RuntimeError(
            f"Single predictor training aborted due to NaN/Inf gradients at epoch {epoch_idx}, batch {batch_idx}. "
            f"Loss was {loss.item():.6f} (normal), but gradients exploded. "
            f"Check: (1) Embedding space quality, (2) Learning rate too high, (3) Extreme values in embeddings."
        )

    def _log_encoder_diagnostics(self, epoch_idx, batch_idx, log_prefix, encoder_device, 
                                 encoder_training, fine_tune, column_batch, batch_full=None):
        """
        Log comprehensive encoder diagnostics on first batch.
        
        Logs encoder state, input data stats, and output embedding stats to help
        diagnose encoding issues, frozen encoders, or constant outputs.
        
        Only runs on first batch of first epoch.
        
        Args:
            epoch_idx: Current epoch
            batch_idx: Current batch
            log_prefix: Prefix for log messages
            encoder_device: Device encoder is on
            encoder_training: Whether encoder is in training mode
            fine_tune: Whether fine-tuning is enabled
            column_batch: Input column batch dict
            batch_full: Output encoded batch tensor (None if called before encoding)
        """
        # Only log on first batch
        if epoch_idx != 0 or batch_idx != 0:
            return
        
        # Log input diagnostics (before encoding)
        if batch_full is None:
            logger.info(f"{log_prefix}🔍 ENCODER DIAGNOSTIC [batch={batch_idx}]:")
            logger.info(f"{log_prefix}   Encoder device: {encoder_device}")
            logger.info(f"{log_prefix}   Encoder training mode: {encoder_training}")
            logger.info(f"{log_prefix}   Fine-tune enabled: {fine_tune}")
            
            # Defensive check: ensure column_batch is a dict and has items
            if column_batch is None:
                logger.error(f"{log_prefix}   ❌ ERROR: column_batch is None!")
                return
            if not isinstance(column_batch, dict):
                logger.error(f"{log_prefix}   ❌ ERROR: column_batch is not a dict (type={type(column_batch)})!")
                return
            if len(column_batch) == 0:
                logger.error(f"{log_prefix}   ❌ ERROR: column_batch is empty!")
                return
            
            logger.info(f"{log_prefix}   Column batch keys: {list(column_batch.keys())[:10]}... ({len(column_batch)} total)")
            
            # Check if column_batch has valid data
            for col_name, token_batch in list(column_batch.items())[:3]:
                if hasattr(token_batch, 'value'):
                    val = token_batch.value
                    logger.info(f"{log_prefix}   Column '{col_name}': shape={val.shape}, device={val.device}, dtype={val.dtype}, min={val.min().item():.4f}, max={val.max().item():.4f}, mean={val.mean().item():.4f}")
        else:
            # Log output diagnostics (after encoding)
            batch_std = batch_full.std().item()
            batch_min = batch_full.min().item()
            batch_max = batch_full.max().item()
            batch_mean = batch_full.mean().item()
            logger.info(f"{log_prefix}🔍 ENCODING RESULT [batch={batch_idx}]:")
            logger.info(f"{log_prefix}   Encoded batch shape: {batch_full.shape}, device: {batch_full.device}, dtype: {batch_full.dtype}")
            logger.info(f"{log_prefix}   Encoded batch stats: min={batch_min:.4f}, max={batch_max:.4f}, mean={batch_mean:.4f}, std={batch_std:.6f}")
            
            if batch_std < 0.001:
                logger.error(f"{log_prefix}⚠️  WARNING: Encoded batch has nearly zero std ({batch_std:.6f})!")
                logger.error(f"{log_prefix}   This means the encoder is producing identical embeddings for all samples")
                logger.error(f"{log_prefix}   Check if encoder is frozen and producing constant outputs")
            else:
                logger.info(f"{log_prefix}   ✅ Encoded batch has variation (std={batch_std:.6f})")

    def _verify_training_state_assertions(self, epoch_idx, batch_idx, fine_tune, optimizer=None):
        """
        Assert that predictor and encoder are in correct training states.
        
        This is a critical safety check to catch silent failures where calling
        .train() or .eval() doesn't actually change the model's training state.
        
        Args:
            epoch_idx: Current epoch (for error messages)
            batch_idx: Current batch (for error messages)
            fine_tune: Whether fine-tuning is enabled (effective_fine_tune)
            optimizer: Optional optimizer to check encoder param membership
            
        Raises:
            AssertionError: If training state doesn't match expectations
        """
        # Predictor must always be in training mode
        assert self.predictor.training is True, \
            f"epoch = {epoch_idx}; batch = {batch_idx} - training = {self.predictor.training}"
        
        # Encoder training state depends on fine_tune flag (effective_fine_tune)
        if fine_tune:
            # When fine-tuning: encoder should be in train mode
            assert self.embedding_space.encoder.training is True, \
                f"epoch = {epoch_idx}; batch = {batch_idx} - encoder.training = {self.embedding_space.encoder.training} (expected True)"
            
            # When fine-tuning: encoder params should be in optimizer (Option B pattern)
            if optimizer is not None:
                encoder_param_ids = {id(p) for p in self.embedding_space.encoder.parameters()}
                optimizer_param_ids = {id(p) for group in optimizer.param_groups for p in group['params']}
                encoder_in_optimizer = bool(encoder_param_ids & optimizer_param_ids)
                assert encoder_in_optimizer, \
                    f"epoch = {epoch_idx}; batch = {batch_idx} - encoder params not in optimizer (fine_tune=True but encoder params missing)"
        else:
            # When frozen: encoder should be in eval mode
            assert self.embedding_space.encoder.training is False, \
                f"epoch = {epoch_idx}; batch = {batch_idx} - encoder.training = {self.embedding_space.encoder.training} (expected False)"
            
            # When frozen: do NOT assert optimizer membership (encoder params may or may not be in optimizer)
            # Option B pattern: encoder params are removed from optimizer during warmup

    def _prepare_batch_targets(self, column_batch):
        """
        Extract and prepare target values from batch, handling marginal tokens.
        
        Process:
        1. Extract target column from batch
        2. If target was in original embedding space, replace with marginal tokens
        3. Extract target values
        4. Format targets based on target type (scalar vs categorical)
        
        Args:
            column_batch: Dict of column name -> TokenBatch
            
        Returns:
            tuple: (targets tensor, modified column_batch)
                - targets: Prepared target tensor (float for scalar, long for categorical)
                - column_batch: Modified batch dict (target replaced with marginal if needed)
        """
        # Remove the target column from the batch to be encoded
        # We don't want to presume the presence of the target when making predictions
        target_token_batch = column_batch.pop(self.target_col_name)
        
        # If target column was in the original embedding space, replace with marginal tokens
        # This creates a representation where the target column's value is not known
        target_column_in_original_df = (
            self.target_col_name in self.embedding_space.col_codecs
        )
        if target_column_in_original_df:
            marginal_token_batch = self._create_marginal_token_batch_for_target(
                target_token_batch
            )
            column_batch[self.target_col_name] = marginal_token_batch
        
        # Extract target values
        targets = target_token_batch.value
        
        # Format targets based on type
        if self.is_target_scalar:
            # Scalar: add dimension to match predictor output shape (B, 1)
            targets = targets.float().unsqueeze(dim=1)
        else:
            # Categorical: CrossEntropyLoss expects integer class indices
            targets = targets.long()
            
            # CRITICAL FIX: For binary classification, remap targets from original token IDs to output indices
            # Original tokens include <UNKNOWN>=0, so real classes are 1 and 2
            # Model output only has 2 classes (indices 0 and 1), so we need to remap: 1->0, 2->1
            if hasattr(self, '_binary_target_remap') and self._binary_target_remap is not None:
                # Create remapped tensor
                remapped_targets = targets.clone()
                for original_token_id, output_idx in self._binary_target_remap.items():
                    remapped_targets[targets == original_token_id] = output_idx
                targets = remapped_targets
        
        return targets, column_batch

    def _compute_loss_with_pairwise_ranking(self, out, targets, loss_fn, use_pairwise_ranking_loss,
                                            pairwise_loss_weight, autocast_dtype, use_autocast, batch_idx):
        """
        Compute loss with optional pairwise ranking component for binary classification.
        
        Main loss is computed via the codec's loss function (e.g., CrossEntropyLoss).
        For binary classification, adds optional pairwise ranking loss that encourages
        positive examples to have higher scores than negative examples.
        
        Args:
            out: Model output logits [batch_size, num_classes]
            targets: Target labels
            loss_fn: Loss function from codec
            use_pairwise_ranking_loss: Whether to add pairwise ranking loss
            pairwise_loss_weight: Weight for pairwise loss component
            autocast_dtype: Data type for mixed precision (if enabled)
            use_autocast: Whether to use automatic mixed precision
            batch_idx: Current batch index (for logging)
            
        Returns:
            torch.Tensor: Combined loss value
        """
        # Clamp logits to prevent extreme loss values
        out_clamped = torch.clamp(out, min=-20.0, max=20.0)
        
        # Log if clamping occurred
        if (out.abs() > 20.0).any():
            n_clamped = (out.abs() > 20.0).sum().item()
            max_logit = out.abs().max().item()
            if batch_idx % 10 == 0:  # Don't spam logs
                logger.warning(f"⚠️  [batch={batch_idx}] Clamped {n_clamped} extreme logits (max={max_logit:.1f}) to prevent loss explosion")
        
        # Compute main loss with BF16 mixed precision if enabled
        with torch.amp.autocast(device_type='cuda', dtype=autocast_dtype, enabled=use_autocast):
            main_loss = loss_fn(out_clamped, targets)
        
        # Add pairwise ranking loss for binary classification (if enabled)
        total_loss = main_loss
        if use_pairwise_ranking_loss and not self.is_target_scalar:
            is_binary_batch = self.should_compute_binary_metrics()
            
            if is_binary_batch:
                with torch.amp.autocast(device_type='cuda', dtype=autocast_dtype, enabled=use_autocast):
                    # Extract logits for positive (1) and negative (0) classes
                    pos_class_idx = 1
                    neg_class_idx = 0
                    
                    pos_logits = out[:, pos_class_idx]  # [batch_size]
                    neg_logits = out[:, neg_class_idx]  # [batch_size]
                    
                    # Create binary labels
                    y_binary = (targets == pos_class_idx).float()  # [batch_size]
                    
                    # Separate positive and negative samples
                    pos_mask = y_binary == 1
                    neg_mask = y_binary == 0
                    
                    if pos_mask.sum() > 0 and neg_mask.sum() > 0:
                        s_pos = pos_logits[pos_mask]  # [P] positives
                        s_neg = neg_logits[neg_mask]  # [N] negatives
                        
                        # Compute pairwise differences
                        diff = s_pos.unsqueeze(1) - s_neg.unsqueeze(0)  # [P, N]
                        
                        # Pairwise ranking loss: encourages pos > neg
                        pairwise_loss = torch.log1p(torch.exp(-diff)).mean()
                        
                        # Combine losses
                        total_loss = main_loss + pairwise_loss_weight * pairwise_loss
                        
                        # Log occasionally
                        if batch_idx % 100 == 0:
                            logger.debug(f"📊 Pairwise loss: {pairwise_loss.item():.6f}, main loss: {main_loss.item():.6f}, total: {total_loss.item():.6f}")
        
        return total_loss

    def _step_optimizer_and_scheduler(self, optimizer, scheduler):
        """Execute optimizer step and scheduler step (if present)."""
        optimizer.step()
        if scheduler is not None:
            # LRTimeline sets LR per-epoch (not per-batch), so skip step() for it
            if not isinstance(scheduler, LRTimeline):
                scheduler.step()

    def _update_progress_after_batch(self, progress_dict, training_info_entry, loss, get_lr):
        """Update progress dict and training_info after a batch completes."""
        progress_dict["time_now"] = time.time()
        progress_dict["current_loss"] = loss.item()
        training_info_entry['loss'] = progress_dict["current_loss"]
        progress_dict["lr"] = get_lr()
        
        # Update hyperparameters
        current_lr = get_lr()
        lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
        training_info_entry['hyperparameters']['learning_rate'] = float(lr_value) if lr_value is not None else None
        
        # Update FocalLoss parameters if they changed
        if isinstance(self.target_codec.loss_fn, FocalLoss):
            training_info_entry['hyperparameters']['focal_gamma'] = float(self.target_codec.loss_fn.gamma)
            training_info_entry['hyperparameters']['focal_min_weight'] = float(self.target_codec.loss_fn.min_weight)

    def _restore_best_model_and_log_summary(self, use_auc_for_best_epoch, best_auc, 
                                             best_roc_auc_model_state, best_auc_epoch, 
                                             best_roc_auc_checkpoint_path, best_pr_auc_model_state, 
                                             best_pr_auc_epoch, best_pr_auc, best_pr_auc_checkpoint_path, 
                                             primary_metric, primary_epoch, primary_value, 
                                             best_model_state, best_epoch, best_embedding_space_state, 
                                             best_checkpoint_path, best_metric_preference):
        """
        Restore the best model and log a summary of both variants (ROC-AUC and PR-AUC).
        
        Loads the best model state into the predictor and encoder, logs checkpoint paths,
        and stores metadata about both variants for future reference.
        
        Args:
            use_auc_for_best_epoch: Whether AUC is used for best epoch selection
            best_auc: Best ROC-AUC score
            best_roc_auc_model_state: State dict for best ROC-AUC model
            best_auc_epoch: Epoch with best ROC-AUC
            best_roc_auc_checkpoint_path: Path to best ROC-AUC checkpoint
            best_pr_auc_model_state: State dict for best PR-AUC model
            best_pr_auc_epoch: Epoch with best PR-AUC
            best_pr_auc: Best PR-AUC score
            best_pr_auc_checkpoint_path: Path to best PR-AUC checkpoint
            primary_metric: Which metric was chosen (ROC-AUC, PR-AUC, or val_loss)
            primary_epoch: Epoch of the primary metric
            primary_value: Value of the primary metric
            best_model_state: State dict to restore
            best_epoch: Epoch to restore
            best_embedding_space_state: Embedding space state dict to restore
            best_checkpoint_path: Path to the checkpoint
            best_metric_preference: User's metric preference (or None for auto)
        """
        # Log summary of both variants if available
        if use_auc_for_best_epoch and best_auc >= 0:
            logger.info("=" * 80)
            logger.info("📊 MODEL VARIANTS SUMMARY:")
            if best_roc_auc_model_state is not None:
                logger.info(f"   🎯 ROC-AUC Best: Epoch {best_auc_epoch}, AUC={best_auc:.4f}")
                if best_roc_auc_checkpoint_path:
                    logger.info(f"      Checkpoint: {best_roc_auc_checkpoint_path}")
            if best_pr_auc_model_state is not None and best_pr_auc_epoch >= 0:
                logger.info(f"   🎯 PR-AUC Best:  Epoch {best_pr_auc_epoch}, PR-AUC={best_pr_auc:.4f}")
                if best_pr_auc_checkpoint_path:
                    logger.info(f"      Checkpoint: {best_pr_auc_checkpoint_path}")
            if best_roc_auc_model_state is not None and best_pr_auc_model_state is not None:
                if best_auc_epoch != best_pr_auc_epoch:
                    logger.info(f"   ℹ️  Different epochs selected - both variants saved as separate checkpoints")
                else:
                    logger.info(f"   ℹ️  Same epoch selected for both metrics - single checkpoint")
            logger.info(f"   ✅ Restoring: {primary_metric} variant (epoch {primary_epoch})")
            logger.info("=" * 80)
        
        if best_model_state is not None:
            logger.info(f"🔄 RESTORING BEST MODEL from epoch {best_epoch} ({primary_metric}={primary_value:.4f})")
            logger.info(f"   Checkpoint path: {best_checkpoint_path if best_checkpoint_path else '(state dict only)'}")
            self.predictor.load_state_dict(best_model_state)
            self.embedding_space.encoder.load_state_dict(best_embedding_space_state)
            logger.info(f"✅ Best model restored successfully from epoch {best_epoch}")
            # CRITICAL: Make it clear that the best checkpoint is the default for inference
            logger.info("=" * 80)
            logger.info(f"🎯 FINAL = best@{primary_metric}@e={best_epoch} (using best checkpoint, not last epoch)")
            logger.info("=" * 80)
            
            # Store metadata about both variants in training info
            if not hasattr(self, 'training_info'):
                self.training_info = []
            if hasattr(self, 'training_info') and isinstance(self.training_info, list):
                # Add variant info to the last entry or create a summary entry
                variant_info = {
                    'best_roc_auc_epoch': best_auc_epoch if best_roc_auc_model_state is not None else None,
                    'best_roc_auc': best_auc if best_roc_auc_model_state is not None else None,
                    'best_roc_auc_checkpoint': best_roc_auc_checkpoint_path if best_roc_auc_checkpoint_path else None,
                    'best_pr_auc_epoch': best_pr_auc_epoch if best_pr_auc_model_state is not None else None,
                    'best_pr_auc': best_pr_auc if best_pr_auc_model_state is not None else None,
                    'best_pr_auc_checkpoint': best_pr_auc_checkpoint_path if best_pr_auc_checkpoint_path else None,
                    'primary_metric': primary_metric,
                    'primary_epoch': primary_epoch,
                    'best_metric_preference': best_metric_preference,  # What preference was used (None = auto)
                }
                # Store in a way that's accessible
                if not hasattr(self, 'model_variants'):
                    self.model_variants = {}
                self.model_variants = variant_info
        else:
            logger.warning(f"⚠️  No best model found - using final epoch weights")

    def _log_best_vs_final_comparison(self, best_epoch, n_epochs, primary_metric):
        """
        Log a comparison table between the best model (by primary metric) and the final epoch model.
        
        Args:
            best_epoch: Epoch number of the best model
            n_epochs: Total number of epochs trained
            primary_metric: Primary metric used for best model selection (e.g., "AUC-ROC", "PR-AUC", "validation_loss")
        """
        if not hasattr(self, 'training_info') or not self.training_info:
            return
        
        # Find best epoch entry
        best_entry = None
        for entry in self.training_info:
            if entry.get('epoch_idx') == best_epoch:
                best_entry = entry
                break
        
        # Find final epoch entry (last entry in training_info)
        final_entry = None
        final_epoch_idx = None
        if self.training_info:
            final_entry = self.training_info[-1]
            final_epoch_idx = final_entry.get('epoch_idx')
        
        if not best_entry or not final_entry:
            return
        
        # Extract metrics
        best_metrics = best_entry.get('metrics', {}) or {}
        final_metrics = final_entry.get('metrics', {}) or {}
        
        # Only log if we have metrics for both
        if not best_metrics or not final_metrics:
            return
        
        # Determine which metric was used for selection (for display)
        metric_display = primary_metric if primary_metric else "AUC-ROC"
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🏆 BEST MODEL vs FINAL EPOCH COMPARISON")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📌 Best Model: Epoch {best_epoch} (by {metric_display}) | Final Model: Epoch {final_epoch_idx}")
        logger.info("")
        
        # Define metrics to compare (in order)
        metrics_to_compare = [
            ('accuracy', 'Accuracy'),
            ('precision', 'Precision'),
            ('recall', 'Recall'),
            ('f1', 'F1 Score'),
            ('auc', 'AUC-ROC'),
            ('pr_auc', 'PR-AUC'),
            ('specificity', 'Specificity'),
        ]
        
        # Build table
        logger.info("┌─────────────────┬──────────────┬──────────────┬───────────┐")
        logger.info(f"│ Metric          │ Best (E {best_epoch:2d})  │ Final (E {final_epoch_idx:2d}) │ Δ Change  │")
        logger.info("├─────────────────┼──────────────┼──────────────┼───────────┤")
        
        for metric_key, metric_name in metrics_to_compare:
            best_val = best_metrics.get(metric_key)
            final_val = final_metrics.get(metric_key)
            
            # Skip if either value is None
            if best_val is None or final_val is None:
                continue
            
            # Calculate change
            delta = final_val - best_val
            delta_str = f"{delta:+.4f}"
            
            # Add emoji indicator
            if delta > 0:
                indicator = "✅"
            elif delta < 0:
                indicator = "❌"
            else:
                indicator = "➖"
            
            # Format values to match exact format: "       0.7750" (12 chars total, right-aligned)
            best_str = f"{best_val:>12.4f}"
            final_str = f"{final_val:>12.4f}"
            
            # Format delta with emoji and sign: "❌ -0.0200"
            delta_with_indicator = f"{indicator} {delta_str}"
            
            logger.info(f"│ {metric_name:<15} │ {best_str} │ {final_str} │ {delta_with_indicator} │")
        
        logger.info("└─────────────────┴──────────────┴──────────────┴───────────┘")
        logger.info("")
        logger.info("=" * 80)
        logger.info("")

    def _fit_calibration_on_validation_set(self, val_queries, val_targets):
        """
        Auto-fit probability calibration on validation set for classification tasks.
        
        Collects validation logits, fits calibration (temperature scaling, Platt scaling, or isotonic),
        and stores the best calibration method and parameters.
        
        Args:
            val_queries: Validation queries (DataFrame or list of dicts)
            val_targets: Validation target values (Series or list)
        """
        if not isinstance(self.target_codec, SetCodec) or val_queries is None or val_targets is None:
            return
        
        logger.info("🔍 Auto-fitting calibration on validation set...")
        try:
            from featrix.neural.calibration_utils import auto_fit_calibration
            # torch is already imported at module level
            
            # Collect validation logits
            self.predictor.eval()
            self.embedding_space.encoder.eval()
            val_logits_list = []
            val_labels_list = []
            
            # Process validation data in batches
            # val_queries should be a DataFrame with the target column removed
            # Create a DataFrame from val_queries if it's not already one
            if not isinstance(val_queries, pd.DataFrame):
                val_queries = pd.DataFrame(val_queries)
            
            val_dataset = SuperSimpleSelfSupervisedDataset(
                val_queries,
                self.all_codecs
            )
            calibration_batch_size = min(256, len(val_dataset))
            val_dataloader = DataLoader(
                val_dataset,
                collate_fn=collate_tokens,
                **create_dataloader_kwargs(batch_size=calibration_batch_size, num_workers=0, dataset_size=len(val_dataset))  # Force single-process, shuffle set in kwargs
            )
            
            with torch.no_grad():
                batch_idx = 0
                for batch in val_dataloader:
                    queries_batch = batch
                    
                    # Encode queries using the encoder's encode method
                    _, encoding = self.embedding_space.encoder.encode(
                        queries_batch,
                        apply_noise=False  # No noise during calibration
                    )
                    
                    # Get logits
                    logits = self.predictor(encoding)
                    val_logits_list.append(logits.detach().cpu())
                    
                    # Get labels from val_targets (not from batch)
                    # Calculate which indices in val_targets correspond to this batch
                    batch_start = batch_idx * val_dataloader.batch_size
                    batch_end = min(batch_start + len(queries_batch), len(val_targets))
                    batch_targets = val_targets.iloc[batch_start:batch_end] if hasattr(val_targets, 'iloc') else val_targets[batch_start:batch_end]
                    
                    # Convert targets to class indices
                    labels = []
                    for target_val in batch_targets:
                        if isinstance(target_val, Token):
                            label_idx = target_val.value
                            # Ensure we have a Python int, not a tensor
                            if isinstance(label_idx, torch.Tensor):
                                label_idx = label_idx.item()
                            labels.append(int(label_idx))
                        else:
                            # Convert target value to token, then to index
                            target_token = self.target_codec.tokenize(target_val)
                            if isinstance(target_token, Token):
                                label_idx = target_token.value
                                # Ensure we have a Python int, not a tensor
                                if isinstance(label_idx, torch.Tensor):
                                    label_idx = label_idx.item()
                                labels.append(int(label_idx))
                            else:
                                # Fallback: try to get index directly
                                logger.warning(f"Could not convert target value {target_val} to token index")
                                labels.append(0)  # Default to first class
                    val_labels_list.extend(labels)
                    batch_idx += 1  # CRITICAL: Increment batch_idx to get correct label indices for next batch
            
            if val_logits_list:
                # Concatenate all logits
                val_logits = torch.cat(val_logits_list, dim=0)
                val_labels = torch.tensor(val_labels_list, dtype=torch.long)
                
                # Fit calibration
                best_method, temp, platt_model, isotonic_model, cal_metrics = auto_fit_calibration(
                    val_logits, val_labels, validation_split=0.0  # Use all validation data
                )
                
                # Store calibration info
                self.calibration_method = best_method
                self.calibration_temperature = temp
                self.calibration_platt_model = platt_model
                self.calibration_isotonic_model = isotonic_model
                self.calibration_metrics = cal_metrics
                
                logger.info(f"✅ Calibration fitted: method={best_method}")
                if best_method == 'temperature':
                    logger.info(f"   Temperature: {temp:.4f}")
            else:
                logger.warning("⚠️  No validation logits collected for calibration")
        except Exception as e:
            logger.warning(f"⚠️  Failed to fit calibration: {e}")
            logger.debug(traceback.format_exc())

    def _save_validation_error_tracking_and_analyze(self):
        """
        Save validation error tracking to JSON and analyze patterns.
        
        Computes summary statistics (always wrong, frequently wrong, etc.),
        analyzes hard rows vs easy rows, and finds distinguishing patterns
        in categorical and numeric features.
        """
        if self._validation_error_tracking is None:
            return
        
        try:
            output_dir = self._output_dir if self._output_dir else "."
            tracking_file = os.path.join(output_dir, "validation_error_tracking.json")
            
            # Add summary statistics before saving
            num_epochs = len(self._validation_error_tracking["validation_results"])
            num_rows = self._validation_error_tracking["metadata"]["num_validation_samples"]
            
            if num_epochs > 0 and num_rows > 0:
                # Compute per-row error statistics
                results_matrix = np.array([
                    self._validation_error_tracking["validation_results"][f"epoch_{i}"]
                    for i in sorted([int(k.split('_')[1]) for k in self._validation_error_tracking["validation_results"].keys()])
                ])
                
                # Error rate per row (fraction of epochs where row was wrong)
                error_rates = 1.0 - results_matrix.mean(axis=0)
                
                self._validation_error_tracking["summary"] = {
                    "num_epochs_tracked": num_epochs,
                    "always_wrong_count": int((error_rates > 0.95).sum()),
                    "frequently_wrong_count": int(((error_rates > 0.7) & (error_rates <= 0.95)).sum()),
                    "sometimes_wrong_count": int(((error_rates > 0.3) & (error_rates <= 0.7)).sum()),
                    "rarely_wrong_count": int(((error_rates > 0) & (error_rates <= 0.3)).sum()),
                    "never_wrong_count": int((error_rates == 0).sum()),
                    "mean_error_rate": float(error_rates.mean()),
                    "std_error_rate": float(error_rates.std())
                }
            
            with open(tracking_file, 'w') as f:
                json.dump(self._validation_error_tracking, f, indent=2)
            
            logger.info(f"💾 Saved validation error tracking to {tracking_file}")
            logger.info(f"   Tracked {num_epochs} epochs × {num_rows} validation samples")
            if num_epochs > 0 and num_rows > 0:
                summary = self._validation_error_tracking["summary"]
                logger.info(f"   Always wrong: {summary['always_wrong_count']} rows ({summary['always_wrong_count']/num_rows*100:.1f}%)")
                logger.info(f"   Never wrong: {summary['never_wrong_count']} rows ({summary['never_wrong_count']/num_rows*100:.1f}%)")
                logger.info(f"   Mean error rate: {summary['mean_error_rate']:.3f}")
                
                # Analyze hardest rows for feature patterns
                if summary['always_wrong_count'] > 0 or summary['frequently_wrong_count'] > 0:
                    logger.info("")
                    logger.info("🔍 HARD ROW FEATURE ANALYSIS:")
                    
                    # Get hardest rows
                    hardest_indices = np.argsort(error_rates)[::-1][:min(10, num_rows)]
                    hardest_error_rates = error_rates[hardest_indices]
                    
                    # Only analyze rows with >70% error rate
                    truly_hard = hardest_indices[hardest_error_rates > 0.7]
                    
                    if len(truly_hard) >= 3:
                        # Get features for hard rows
                        hard_features = [self._validation_error_tracking["validation_data"]["row_features"][i] 
                                       for i in truly_hard if i < len(self._validation_error_tracking["validation_data"]["row_features"])]
                        
                        # Get features for easy rows (error rate < 30%)
                        easy_indices = np.where(error_rates < 0.3)[0]
                        if len(easy_indices) >= len(truly_hard):
                            easy_features = [self._validation_error_tracking["validation_data"]["row_features"][i]
                                           for i in easy_indices[:len(truly_hard)]]
                            
                            # Find commonalities
                            if hard_features and easy_features and len(hard_features) > 0:
                                # Analyze categorical features
                                feature_names = set()
                                for f in hard_features + easy_features:
                                    if isinstance(f, dict):
                                        feature_names.update(f.keys())
                                
                                cat_patterns = []
                                num_patterns = []
                                
                                for feat_name in feature_names:
                                    hard_vals = [f.get(feat_name) for f in hard_features if isinstance(f, dict) and feat_name in f]
                                    easy_vals = [f.get(feat_name) for f in easy_features if isinstance(f, dict) and feat_name in f]
                                    
                                    if not hard_vals or not easy_vals:
                                        continue
                                    
                                    sample_val = hard_vals[0]
                                    is_numeric = isinstance(sample_val, (int, float)) and not isinstance(sample_val, bool)
                                    
                                    if is_numeric:
                                        # Numeric comparison
                                        hard_mean = np.mean([v for v in hard_vals if isinstance(v, (int, float))])
                                        easy_mean = np.mean([v for v in easy_vals if isinstance(v, (int, float))])
                                        diff_pct = abs(hard_mean - easy_mean) / (abs(easy_mean) + 1e-6) * 100
                                        if diff_pct > 20:  # 20% difference
                                            num_patterns.append((feat_name, hard_mean, easy_mean, diff_pct))
                                    else:
                                        # Categorical comparison
                                        from collections import Counter
                                        hard_counter = Counter([str(v) for v in hard_vals])
                                        easy_counter = Counter([str(v) for v in easy_vals])
                                        
                                        for val, hard_count in hard_counter.most_common(3):
                                            hard_freq = hard_count / len(hard_vals)
                                            easy_count = easy_counter.get(val, 0)
                                            easy_freq = easy_count / len(easy_vals)
                                            if hard_freq > easy_freq + 0.3:  # 30% more common
                                                cat_patterns.append((feat_name, val, hard_freq, easy_freq))
                                
                                # Show categorical patterns
                                if cat_patterns:
                                    logger.info("")
                                    logger.info("   Categorical Patterns (appear more in hard rows):")
                                    for feat, val, hard_freq, easy_freq in sorted(cat_patterns, key=lambda x: x[2]-x[3], reverse=True)[:5]:
                                        logger.info(f"      {feat}='{val}': {hard_freq*100:.0f}% of hard vs {easy_freq*100:.0f}% of easy  (Δ={hard_freq-easy_freq:+.0%})")
                                
                                # Show numeric patterns
                                if num_patterns:
                                    logger.info("")
                                    logger.info("   Numeric Differences (hard vs easy rows):")
                                    for feat, hard_mean, easy_mean, diff_pct in sorted(num_patterns, key=lambda x: x[3], reverse=True)[:5]:
                                        logger.info(f"      {feat}: hard={hard_mean:.1f} vs easy={easy_mean:.1f}  (Δ={diff_pct:.0f}%)")
                                
                                if cat_patterns or num_patterns:
                                    logger.info("")
                                    logger.info("   💡 Hard rows have these distinctive features")
                    else:
                        logger.info("   ℹ️  Too few hard rows for meaningful pattern analysis")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save validation error tracking: {e}")
            logger.debug(traceback.format_exc())

    async def train(
        self,
        n_epochs=0,
        batch_size=0,
        fine_tune=True,
        val_df=None,
        val_queries=None,
        val_targets=None,
        val_pos_label=None,
        print_progress_step=10,     # deprecated
        optimizer_params=None,
        use_lr_scheduler=True,
        print_callback=None,
        job_id=None,
        network_viz_identifier=None,
        sp_identifier=None,
        use_auc_for_best_epoch=None,  # None = auto-detect (True for binary, False for scalar)
        best_metric_preference=None,  # None = auto (PR-AUC for imbalanced, ROC-AUC for balanced), "roc_auc", or "pr_auc"
        use_pairwise_ranking_loss=True,  # Default True for testing
        pairwise_loss_weight=0.1,  # Weight for pairwise ranking loss component
        use_bf16=None,  # BF16 mixed precision training (None=inherit from ES, True/False=override)
        pre_best_restore_callback=None,  # Callback called BEFORE loading best checkpoint (receives self, last_epoch_idx)
    ):
        """
        # fine_tune: whether the encoder should be fine-tuned for this task.
        # val_df: if provided, it's used to report validation error during training
        # print_callback: callback function that receives progress dictionary like ES.train
        # job_id: job ID for ABORT/FINISH file detection (optional)
        # sp_identifier: identifier for this SP (e.g., target column name) used in logs and filenames
        """
        
        # Store validation dataframe for use during training (e.g., feature engineering)
        self.val_df = val_df
        
        # Reset epoch counter for clean state
        self._current_epoch = 0
        
        # Compute dataset hash for monitor reporting (cache it)
        self._dataset_hash = self._compute_dataset_hash()
        
        # Set up logging filter for this training run
        self._setup_sp_identifier_filter(sp_identifier)
        
        # Set output directory for timeline saving (from embedding space)
        if hasattr(self.embedding_space, 'output_dir') and self.embedding_space.output_dir:
            self._output_dir = self.embedding_space.output_dir
            logger.info(f"📊 SP training timeline will be saved to: {self._output_dir}")
        
        # Suppress noisy logs from dependencies
        self._suppress_noisy_logs()
            
        # Logging is already configured via logging_config.py at module import
        logger.info(f"@@@@@@@@@@ SINGLE PREDICTOR INPUT n_epochs = {n_epochs}, batch_size = {batch_size}, fine_tune = {fine_tune}")
        
        # Track training start time
        training_start_time = time.time()
        
        # Create timestamp prefix for checkpoint filenames to prevent stomping across re-runs
        # Format: YYYYMMDD_HHMMSS (e.g., 20250131_143022)
        training_start_timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(training_start_time))
        logger.info(f"📅 Training session timestamp: {training_start_timestamp}")
        
        # Auto-calculate batch_size if not specified
        if batch_size is None or batch_size == 0:
            batch_size = ideal_batch_size(len(self.train_df), mode="predictor")
            logger.info(f"Auto-calculated batch_size: {batch_size}")
        
        # Auto-calculate n_epochs if not specified
        if n_epochs is None or n_epochs == 0:
            n_epochs = ideal_epochs_predictor(len(self.train_df), batch_size)
            logger.info(f"Auto-calculated n_epochs: {n_epochs}")
        
        # Store total epochs for logging filter
        self._total_epochs = n_epochs

        if self.predictor is None:
            raise Exception("Need to call `prep_for_training` first.")

        # 
        # Choose which parameters to train and set the optimizer
        # 
        logger.info(f"🔧 Training configuration: fine_tune={fine_tune}")
        
        # Setup trainable parameters based on fine-tuning setting
        params, trainable_count, frozen_count = self._setup_training_parameters(fine_tune)
        
        # Log parameter breakdown and store params for gradient clipping
        self._log_parameter_breakdown(
            params=params,
            trainable_count=trainable_count,
            frozen_count=frozen_count
        )

        # Calculate adaptive learning rate
        optimizer_params = self._calculate_adaptive_learning_rate(optimizer_params, fine_tune=fine_tune)
        
        # Store original LR for CONSTANT_PROBABILITY recovery (before any increases)
        self._original_lr = optimizer_params.get("lr", 1e-3)
        
        # SEPARATE LEARNING RATES FOR ENCODER VS PREDICTOR (to fix gradient flow imbalance)
        # When fine_tune=True and encoder gradients are tiny (log R < -2.3), use higher encoder LR
        # Goal: bring log R closer to 0 (balanced learning)
        encoder_lr = None
        predictor_lr = None
        encoder_params_separate = None
        predictor_params_separate = None
        
        if fine_tune:
            # Split params into encoder and predictor
            encoder_params_separate = list(self.embedding_space.encoder.parameters())
            predictor_params_separate = list(self.predictor.parameters())
            
            # CRITICAL: Ensure ALL encoder parameters have requires_grad=True when fine_tune=True
            # This is essential - optimizer won't update params with requires_grad=False
            encoder_params_with_grad_disabled = 0
            for param in encoder_params_separate:
                if not param.requires_grad:
                    param.requires_grad = True
                    encoder_params_with_grad_disabled += 1
            if encoder_params_with_grad_disabled > 0:
                logger.warning(f"   ⚠️  Fixed {encoder_params_with_grad_disabled} encoder params that had requires_grad=False")
                logger.warning(f"      Set requires_grad=True for fine-tuning (all encoder params must be trainable)")
            
            # Default: encoder gets 5× higher LR to compensate for tiny gradients
            # This is the "right way" - param groups instead of gradient multipliers
            base_lr = optimizer_params.get("lr", 1e-3)
            encoder_lr = 5e-4  # Fixed higher LR for encoder
            predictor_lr = 1e-4  # Lower LR for predictor (or use base_lr / 2)
            
            # Allow override via environment variable for experimentation
            env_encoder_lr = os.environ.get('FEATRIX_ENCODER_LR')
            env_predictor_lr = os.environ.get('FEATRIX_PREDICTOR_LR')
            if env_encoder_lr:
                encoder_lr = float(env_encoder_lr)
            if env_predictor_lr:
                predictor_lr = float(env_predictor_lr)
            
            logger.info(f"🔧 SEPARATE LEARNING RATES (to fix encoder gradient starvation):")
            logger.info(f"   Encoder LR: {encoder_lr:.6e} (higher to compensate for tiny gradients)")
            logger.info(f"   Predictor LR: {predictor_lr:.6e} (lower to balance learning)")
            logger.info(f"   Ratio: encoder/predictor = {encoder_lr/predictor_lr:.2f}×")
            logger.info(f"   Goal: Bring log R closer to 0 (balanced encoder/predictor learning)")
            logger.info(f"   Encoder params to add: {len(encoder_params_separate)}")
            logger.info(f"   Predictor params to add: {len(predictor_params_separate)}")
        
        # Store encoder LR for phased freezing (if enabled and fine_tune=True)
        if fine_tune:
            self._encoder_lr_for_unfreeze = encoder_lr if encoder_lr is not None else optimizer_params.get("lr", 1e-3)
        else:
            self._encoder_lr_for_unfreeze = None
        
        # Create optimizer with memory-efficient variant if available
        if fine_tune and encoder_lr is not None and predictor_lr is not None:
            optimizer = self._create_optimizer(
                params=params,  # Still pass for backward compatibility
                optimizer_params=optimizer_params,
                encoder_params=encoder_params_separate,
                predictor_params=predictor_params_separate,
                encoder_lr=encoder_lr,
                predictor_lr=predictor_lr
            )
        else:
            optimizer = self._create_optimizer(params, optimizer_params)
        
        # CRITICAL DIAGNOSTIC: Verify encoder params are in optimizer when fine_tune=True
        if fine_tune:
            # Check all param groups (optimizer might have multiple groups with different LRs)
            optimizer_param_ids = set()
            for param_group in optimizer.param_groups:
                optimizer_param_ids.update({id(p) for p in param_group['params']})
            
            encoder_param_ids = {id(p) for p in self.embedding_space.encoder.parameters()}
            encoder_params_in_optimizer = encoder_param_ids.intersection(optimizer_param_ids)
            encoder_params_missing = encoder_param_ids - optimizer_param_ids
            
            logger.info("=" * 80)
            logger.info("🔍 OPTIMIZER PARAMETER VERIFICATION (Fine-tuning enabled)")
            logger.info("=" * 80)
            logger.info(f"   Total encoder params: {len(encoder_param_ids)}")
            logger.info(f"   Encoder params in optimizer: {len(encoder_params_in_optimizer)}/{len(encoder_param_ids)}")
            logger.info(f"   Optimizer param groups: {len(optimizer.param_groups)}")
            if encoder_params_missing:
                logger.error(f"   ❌ MISSING FROM OPTIMIZER: {len(encoder_params_missing)} encoder params NOT in optimizer!")
                logger.error(f"      This means optimizer won't update these params even if they have gradients!")
                logger.error(f"      First 5 missing param names:")
                missing_names = [name for name, p in self.embedding_space.encoder.named_parameters() if id(p) in encoder_params_missing][:5]
                for name in missing_names:
                    logger.error(f"         - {name}")
            else:
                logger.info(f"   ✅ All encoder params are in optimizer")
            logger.info("=" * 80)

        # ============================================================================
        # BF16 MIXED PRECISION TRAINING SETUP (RTX 4090 / Ampere+ GPUs)
        # ============================================================================
        use_autocast, autocast_dtype = self._setup_bf16_autocast(use_bf16)

        # NOTE: LRTimeline scheduler creation moved AFTER DataLoader creation
        # to use exact len(train_dataloader) 
        # Scheduler will be created after train_dataloader (see below)        
        def get_lr():
            # get_lr function defined here but scheduler created later
            if hasattr(self, '_training_scheduler') and self._training_scheduler is not None:
                # LRTimeline uses internal epoch counter, PyTorch schedulers use get_last_lr()
                if isinstance(self._training_scheduler, LRTimeline):
                    # LRTimeline tracks epoch internally, just get current LR
                    return self._training_scheduler.get_current_lr()
                else:
                    # PyTorch schedulers have get_last_lr() method
                    if hasattr(self._training_scheduler, 'get_last_lr'):
                        return self._training_scheduler.get_last_lr()  # pylint: disable=no-member
                    # Fallback for other scheduler types
                    return optimizer_params["lr"]
            else:
                return optimizer_params["lr"]

        loss_fn = self.target_codec.loss_fn

        # 
        # Set up validation batch for computing validation loss,
        # and validation queries for computing metrics.
        # 
        # Prepare train and validation datasets (split if needed)
        train_df, val_df = self._prepare_validation_data(val_df)

        self.print_label_distribution(train_df=train_df, val_df=val_df, target_col=self.target_col_name)

        # Setup validation metrics (queries, targets, positive label)
        val_df, val_queries, val_targets, val_pos_label = self._setup_validation_metrics(
            val_df=val_df,
            val_queries=val_queries,
            val_targets=val_targets,
            val_pos_label=val_pos_label
        )

        # Move models (predictor, encoder, codecs) to GPU/MPS if available
        self._move_models_to_device()
        
        # PRE-LOAD STRING CACHE: Populate the global string cache with values from SP training/validation data
        # This prevents cache misses when SP training data contains strings not seen during ES training
        logger.info("=" * 80)
        logger.info("📦 PRE-LOADING STRING CACHE FOR SINGLE PREDICTOR TRAINING")
        logger.info("=" * 80)
        
        # Identify all STRING columns in self.all_codecs
        string_columns = []
        for col_name, codec in self.all_codecs.items():
            if isinstance(codec, StringCodec):
                string_columns.append((col_name, codec))
        
        if string_columns:
            logger.info(f"🔍 Found {len(string_columns)} STRING columns in codecs:")
            for col_name, _ in string_columns:
                logger.info(f"   • {col_name}")
            
            # For each STRING column, collect unique values from train + val dataframes
            for col_name, codec in string_columns:
                try:
                    # Collect unique values from training data
                    if col_name in train_df.columns:
                        train_unique_values = train_df[col_name].dropna().astype(str).unique().tolist()
                    else:
                        train_unique_values = []
                    
                    # Collect unique values from validation data
                    if col_name in val_df.columns:
                        val_unique_values = val_df[col_name].dropna().astype(str).unique().tolist()
                    else:
                        val_unique_values = []
                    
                    # Combine and deduplicate
                    all_unique_values = list(set(train_unique_values + val_unique_values))
                    
                    if all_unique_values:
                        # Apply delimiter preprocessing if codec has delimiter configured
                        if hasattr(codec, 'delimiter') and codec.delimiter:
                            from featrix.neural.string_analysis import preprocess_delimited_string
                            preprocessed_values = [preprocess_delimited_string(v, codec.delimiter) for v in all_unique_values]
                            logger.info(f"   📊 {col_name}: Pre-loading {len(preprocessed_values)} unique values (delimiter-preprocessed)")
                        else:
                            preprocessed_values = all_unique_values
                            logger.info(f"   📊 {col_name}: Pre-loading {len(preprocessed_values)} unique values")
                        
                        # Pre-warm the global cache with these values
                        # Use the codec's string_cache_filename to get the right cache instance
                        cache_filename = getattr(codec, '_string_cache_filename', None)
                        cache = get_global_string_cache(
                            cache_filename=cache_filename,
                            initial_values=preprocessed_values,
                            debug_name=f"sp_{col_name}"
                        )
                        logger.info(f"   ✅ {col_name}: Cache pre-loaded successfully")
                    else:
                        logger.warning(f"   ⚠️  {col_name}: No values to pre-load (column might be missing from train/val data)")
                        
                except Exception as e:
                    logger.error(f"   ❌ {col_name}: Failed to pre-load cache: {e}")
                    # Don't fail training - cache misses will be handled by runtime fallback
            
            logger.info("✅ String cache pre-loading complete")
        else:
            logger.info("ℹ️  No STRING columns found in codecs - skipping cache pre-loading")
        
        logger.info("=" * 80)
        
        # ============================================================================
        # EMBEDDING SPACE QUALITY DIAGNOSTICS
        # ============================================================================
        # Evaluate ES encoder quality on training data before starting SP training
        # This helps catch issues like constant embeddings, low variance, poor class separation
        logger.info("=" * 80)
        logger.info("🔍 EVALUATING EMBEDDING SPACE ENCODER QUALITY")
        logger.info("=" * 80)
        try:
            self._evaluate_encoder_quality(train_df, val_df if val_df is not None else train_df)
        except Exception as e:
            logger.warning(f"⚠️  Failed to evaluate encoder quality: {e}")
            logger.debug(traceback.format_exc())
            # Don't fail training - this is just a diagnostic
        logger.info("=" * 80)
            
        train_dataset = SuperSimpleSelfSupervisedDataset(train_df, self.all_codecs)
        
        # Validate dataset is not empty
        if len(train_df) == 0:
            raise ValueError(f"❌ Training dataframe is EMPTY (0 rows)! Cannot train with no data.")
        
        # Store dataset size for use in multiple places
        dataset_size = len(train_df)
        
        # Cap batch_size to prevent overfitting on small datasets
        batch_size = self._cap_batch_size_for_dataset(
            batch_size=batch_size,
            dataset_size=dataset_size
        )
        
        # Clean up orphaned DataLoader workers from previous training jobs
        self._cleanup_orphaned_dataloader_workers()
        
        # CRITICAL: If batch_size > len(train_df) and drop_last=True, dataloader will be EMPTY (0 batches)!
        # This causes 0% GPU usage and 0.0000 losses. Auto-adjust drop_last to prevent this.
        use_drop_last = True  # Default: drop incomplete batches to prevent batch_size=1 (breaks BatchNorm)
        if batch_size > dataset_size:
            logger.warning(
                f"⚠️  batch_size ({batch_size}) > train_df size ({dataset_size})! "
                f"Setting drop_last=False to prevent empty dataloader. "
                f"Will use single batch of size {dataset_size}."
            )
            use_drop_last = False  # Must keep the incomplete batch or we'll have 0 batches
        
        train_dl_kwargs = create_dataloader_kwargs(
            batch_size=batch_size,
            shuffle=True,
            drop_last=use_drop_last,  # Auto-adjusted: False if batch_size > dataset_size
            num_workers=0,  # Force single-process to avoid worker cache miss issues
            dataset_size=len(train_df),
        )
        train_dataloader = DataLoader(
            train_dataset,
            collate_fn=collate_tokens,
            **train_dl_kwargs
        )
        
        # Validate dataloader is not empty
        dataloader_len = len(train_dataloader)
        if dataloader_len == 0:
            raise ValueError(
                f"❌ Training dataloader is EMPTY (0 batches)! "
                f"This means no training data is available.\n"
                f"   train_df size: {len(train_df)}\n"
                f"   batch_size: {batch_size}\n"
                f"   drop_last: {train_dl_kwargs.get('drop_last', False)}\n"
                f"   Dataset length: {len(train_dataset)}\n"
                f"   If drop_last=True and batch_size > len(train_df), all batches will be dropped.\n"
                f"   Consider reducing batch_size or setting drop_last=False."
            )
        
        logger.info(f"✅ Training dataloader created: {dataloader_len} batches (dataset_size={len(train_df)}, batch_size={batch_size})")
        
        # 
        # Set up LRTimeline scheduler NOW (after DataLoader creation)
        # Using exact len(train_dataloader) prevents off-by-one errors
        # 
        # Define n_batches_per_epoch for use in both scheduler and progress logging
        n_batches_per_epoch = dataloader_len
        
        if use_lr_scheduler:
            # Use LRTimeline with simple schedule: linear warmup + cosine decay
            # Simple, boring schedule that works:
            # - Epochs 0-4: Linear warmup from 5e-5 → 6e-4
            # - Epochs 5+: Cosine decay from 6e-4 → 1e-5
            
            warmup_epochs = 5
            warmup_start_lr = 5e-5
            warmup_end_lr = 6e-4
            decay_end_lr = 1e-5
            
            # Use 'sp_plus_es' mode if fine-tuning (ES will be unfrozen), otherwise 'sp_only'
            scheduler_mode = 'sp_plus_es' if fine_tune else 'sp_only'
            
            scheduler = LRTimeline(
                n_epochs=n_epochs,
                schedule_type='simple',
                warmup_epochs=warmup_epochs,
                warmup_start_lr=warmup_start_lr,
                warmup_end_lr=warmup_end_lr,
                decay_end_lr=decay_end_lr,
                mode=scheduler_mode,
            )
            
            # Store scheduler for use in get_lr() function defined above
            self._training_scheduler = scheduler
            
            logger.info(f"🎯 LRTimeline Scheduler (Simple Schedule):")
            logger.info(f"   Epochs 0-{warmup_epochs-1}: Linear warmup {warmup_start_lr:.6e} → {warmup_end_lr:.6e}")
            logger.info(f"   Epochs {warmup_epochs}-{n_epochs-1}: Cosine decay {warmup_end_lr:.6e} → {decay_end_lr:.6e}")
        else:
            scheduler = None
            self._training_scheduler = None

        # TODO: check that val_df has the same columns as train_df.
        # Construct the validation batch. Validation uses a single, so we can
        # draw it from the dataloader immediately. The validation dataloder
        # is just used to make sure that the validation batch is formatted properly.
        
        validation_dataset = SuperSimpleSelfSupervisedDataset(
            val_df,
            self.all_codecs,
        )
        # Use smart batch size for validation
        # Validation doesn't need the "minimum batches per epoch" constraint that training has
        # (that constraint is to prevent overfitting via more gradient updates, which doesn't apply to validation)
        # Just use training batch size, capped at 256 for efficiency, and ensure it doesn't exceed validation set size
        val_batch_size = min(batch_size, 256, len(val_df))
        validation_dataloader = DataLoader(
            validation_dataset,
            batch_size=val_batch_size,
            # Don't need to shuffle because we're computing loss over entire validation set
            shuffle=False,
            collate_fn=collate_tokens,
        )
        
        # Store validation dataloader for computing validation loss across entire validation set
        self._validation_dataloader = validation_dataloader
        
        # Extract all validation targets for metrics computation
        # We need targets on the correct device for loss computation
        validation_targets_list = []
        encoder_device = next(self.embedding_space.encoder.parameters()).device
        
        for val_batch in validation_dataloader:
            # Extract targets from this batch
            val_target_token_batch = val_batch[self.target_col_name]
            batch_targets = val_target_token_batch.value
            validation_targets_list.append(batch_targets)
        
        # Concatenate all validation targets
        validation_targets = torch.cat(validation_targets_list, dim=0)
        
        # Move validation targets to same device as encoder (GPU/MPS/CPU)
        validation_targets = validation_targets.to(encoder_device)
        
        if self.is_target_scalar:
            validation_targets = validation_targets.float().unsqueeze(dim=1)
        else:
            # For set/categorical targets, CrossEntropyLoss expects integer class indices
            validation_targets = validation_targets.long()

        is_binary = self.should_compute_binary_metrics()
        
        # Auto-detect use_auc_for_best_epoch if not specified
        if use_auc_for_best_epoch is None:
            # Use AUC for binary classification, validation loss for scalar/regression
            # Use same logic as should_compute_binary_metrics() - count only real classes
            use_auc_for_best_epoch = is_binary and not self.is_target_scalar
            logger.info(f"🎯 Auto-detected best epoch selection: {'AUC' if use_auc_for_best_epoch else 'validation_loss'} (is_binary={is_binary})")
        else:
            logger.info(f"🎯 Best epoch selection: {'AUC' if use_auc_for_best_epoch else 'validation_loss'} (explicitly set)")

        # Validation set size warning
        val_size = len(val_df) if val_df is not None else 0
        if val_size > 0:
            if val_size < 200:
                logger.warning(f"⚠️  Small validation set ({val_size} samples) - threshold estimates may be noisy")
            else:
                logger.info(f"✅ Validation set size: {val_size} samples (sufficient for stable threshold estimation)")
        
        # Log pairwise ranking loss configuration
        if use_pairwise_ranking_loss:
            # Use same logic as should_compute_binary_metrics() - count only real classes (exclude <UNKNOWN>)
            is_binary_for_pairwise = is_binary and not self.is_target_scalar
            
            if is_binary_for_pairwise:
                logger.info(f"📊 Pairwise ranking loss: ENABLED (weight={pairwise_loss_weight:.3f})")
            else:
                logger.warning(f"⚠️  Pairwise ranking loss requested but target is not binary - disabling")
                use_pairwise_ranking_loss = False
        else:
            logger.info(f"📊 Pairwise ranking loss: DISABLED")

        # Initialize validation error tracking
        # Track per-row correct/wrong flags at each epoch for analysis
        self._validation_error_tracking = {
            "validation_results": {},  # {f"epoch_{i}": [1,0,1,0,...]}
            "metadata": {
                "num_validation_samples": len(val_df) if val_df is not None else 0,
                "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                "pos_label": val_pos_label,
                "training_params": {
                    "n_epochs": n_epochs,
                    "batch_size": batch_size,
                    "fine_tune": fine_tune,
                    "n_hidden_layers": self.predictor_base.config.n_hidden_layers if hasattr(self, 'predictor_base') and hasattr(self.predictor_base, 'config') else None,
                }
            },
            "validation_data": {
                "ground_truth": val_targets.tolist() if val_targets is not None else [],
                "row_features": val_queries if val_queries is not None else []
            }
        }
        logger.info(f"📊 Validation error tracking initialized for {len(val_df) if val_df is not None else 0} validation samples")

        # Initialize structured logging components
        self._metric_tracker = MetricTracker()
        self._row_tracker = RowErrorTracker(
            num_rows=len(val_df) if val_df is not None else 0,
            features=val_queries if val_queries is not None else [],
            ground_truth=val_targets.tolist() if val_targets is not None else []
        )
        self._structured_logger = StructuredLogger(
            logger, 
            target_col_name=self.target_col_name, 
            output_dir=self._output_dir,
            enable_feature_suggestions=self.enable_feature_suggestions
        )
        logger.info(f"📊 Structured logging initialized (multi-epoch deltas, feature analysis)")
        if self.enable_feature_suggestions and self._output_dir:
            logger.info(f"   Feature suggestions will be saved to: {self._output_dir}")

        # 
        # Compute pre-training metrics, and initialize progress dictionary
        # 
        try:
            self.training_metrics = self.compute_classification_metrics(
                val_queries, val_targets, val_pos_label, epoch_idx=0, n_epochs=n_epochs
            )
        except:
            logger.exception("error with compute_classification_metrics")

        # Initialize progress tracking dictionary (ES.train style)
        # Reuse training_start_time from earlier for consistency
        max_progress = n_epochs * len(train_dataloader)
        
        progress_dict = {
            "status": "training",
            "start_time": training_start_time,
            "time_now": training_start_time,
            "epoch_total": n_epochs,
            "batch_total": len(train_dataloader),
            "batch_idx": 0,
            "epoch_idx": 0,
            "max_progress": max_progress,
            "progress_counter": 0,
            "validation_loss": 0,
            "metrics": self.training_metrics,
            "lr": get_lr(),
        }

        # Initial progress callback
        if print_callback is not None:
            print_callback(progress_dict)

        encode_time = 0
        loop_start = time.time()
        last_metrics_time = time.time()

        # 
        # Main training loop
        # 
        # Make sure the encoder is in eval mode, to avoid introducing randomness from e.g.
        # dropout or batch norm.
        # NOTE: (23/12/07, pjz) if we allow fine-tuning of the embedding_space model, we may want to
        # keep the encoder in training mode.
        encoder_mode = TrainingState.TRAIN if fine_tune else TrainingState.EVAL
        with PredictorTrainingContextManager(
            fsp=self, 
            predictor_mode=TrainingState.TRAIN, 
            encoder_mode=encoder_mode, 
            debugLabel="FeatrixSinglePredictor.train"):
            
            self.training_info = []
            
            # Track best model for checkpointing
            best_val_loss = float('inf')
            best_epoch = -1
            best_auc = -1.0  # Track best AUC separately
            best_auc_epoch = -1  # Track epoch with best AUC
            best_pr_auc = -1.0  # Track best PR-AUC (for imbalanced datasets)
            best_pr_auc_epoch = -1  # Track epoch with best PR-AUC
            self._best_composite_score = -1.0  # Track best composite score (when costs available)
            self._best_composite_score_epoch = -1  # Track epoch with best composite score
            best_model_state = None
            best_embedding_space_state = None
            # Track separate state dicts for ROC-AUC and PR-AUC best models
            best_roc_auc_model_state = None
            best_roc_auc_embedding_space_state = None
            best_pr_auc_model_state = None
            best_pr_auc_embedding_space_state = None
            best_checkpoint_path = None  # Track the path for logging (primary checkpoint)
            best_roc_auc_checkpoint_path = None  # Track ROC-AUC best checkpoint path
            best_pr_auc_checkpoint_path = None  # Track PR-AUC best checkpoint path
            
            # TRAINING RESTART LOOP
            # Wrap main training in try/except to catch FeatrixRestartTrainingException
            # This allows us to restart training with modified parameters when issues detected
            restart_loop_active = True
            restart_attempts = 0
            max_restart_attempts = self.max_training_restarts
            
            # ============================================================================
            # START: RESTART WHILE LOOP
            # ============================================================================
            while restart_loop_active and restart_attempts <= max_restart_attempts:
                try:
                    # ========================================================================
                    # START: EPOCH FOR LOOP (range(n_epochs))
                    # ========================================================================
                    _log_gpu_memory("START TRAINING LOOP")
                    
                    # ========================================================================
                    # PHASED FREEZING: Freeze ES for first 5% of epochs (if enabled and > 5 epochs)
                    # ========================================================================
                    from featrix.neural.sphere_config import get_config
                    config = get_config()
                    freeze_warmup_enabled = config.get("freeze_es_warmup_enabled", True)
                    
                    # Calculate warmup epochs: 5% of total, but only if > 5 epochs total
                    freeze_warmup_epochs = 0
                    if freeze_warmup_enabled and n_epochs > 5 and fine_tune:
                        freeze_warmup_epochs = max(1, int(n_epochs * 0.05))  # At least 1 epoch, 5% of total
                        logger.info(f"🔒 PHASED FREEZING: Freezing embedding space for first {freeze_warmup_epochs} epochs ({freeze_warmup_epochs/n_epochs*100:.1f}% of {n_epochs} total)")
                        logger.info(f"   Predictor will learn from stable embeddings, then encoder will unfreeze for fine-tuning")
                        
                        # Initialize tracking for warmup diagnostics
                        self._best_auc_during_warmup = -1.0
                        self._warmup_best_auc_epoch = -1
                        self._initial_auc = None  # Track first AUC value
                        self._auc_ever_improved = False  # Track if AUC ever improved from initial
                    else:
                        if not freeze_warmup_enabled:
                            logger.info(f"🔓 PHASED FREEZING: Disabled via config (freeze_es_warmup_enabled=False)")
                        elif n_epochs <= 5:
                            logger.info(f"🔓 PHASED FREEZING: Skipped (only {n_epochs} epochs, need > 5)")
                        elif not fine_tune:
                            logger.info(f"🔓 PHASED FREEZING: Skipped (fine_tune=False, encoder already frozen)")
                        
                        # Initialize tracking even if warmup disabled (for "nothing improves" detection)
                        self._initial_auc = None
                        self._auc_ever_improved = False
                    
                    # Set models to correct training modes (will be updated during warmup if needed)
                    # If warmup enabled and fine_tune=True, start with encoder frozen
                    train_encoder_now_initial = fine_tune and (freeze_warmup_epochs == 0)
                    self._set_training_modes(fine_tune=train_encoder_now_initial)
                    
                    # If warmup is enabled, we need to handle encoder params in optimizer
                    # Start with encoder frozen (not in optimizer if warmup enabled)
                    if freeze_warmup_epochs > 0 and fine_tune:
                        # Freeze encoder parameters
                        encoder_params = list(self.embedding_space.encoder.parameters())
                        for param in encoder_params:
                            param.requires_grad = False
                        
                        # Remove encoder params from optimizer (if they were added)
                        # Keep only predictor params in optimizer during warmup
                        predictor_param_ids = {id(p) for p in self.predictor.parameters()}
                        new_param_groups = []
                        for param_group in optimizer.param_groups:
                            filtered_params = [p for p in param_group['params'] if id(p) in predictor_param_ids]
                            if filtered_params:
                                new_param_groups.append({
                                    'params': filtered_params,
                                    'lr': param_group.get('lr', optimizer_params.get("lr", 1e-3)),
                                    **{k: v for k, v in param_group.items() if k not in ['params', 'lr']}
                                })
                        optimizer.param_groups = new_param_groups
                        logger.info(f"   🔒 Encoder params removed from optimizer during warmup")
                        
                        # Add event to training timeline: ES frozen
                        if hasattr(self, '_training_timeline'):
                            freeze_event = {
                                "epoch": 0,
                                "event_type": "es_frozen",
                                "freeze_warmup_epochs": freeze_warmup_epochs,
                                "total_epochs": n_epochs,
                                "unfreeze_epoch": freeze_warmup_epochs,
                                "reason": f"Phased freezing: ES frozen for first {freeze_warmup_epochs} epochs ({freeze_warmup_epochs/n_epochs*100:.1f}% of training) to allow predictor to learn from stable embeddings",
                                "time_now": training_start_time,
                            }
                            self._training_timeline.append(freeze_event)
                    
                    # Log cool training start banner
                    try:
                        from featrix.neural.training_banner import log_training_start_banner
                        # Get d_model from encoder config (source of truth) if available, fallback to embedding_space.d_model
                        d_model = None
                        if hasattr(self, 'embedding_space') and self.embedding_space is not None:
                            if (hasattr(self.embedding_space, 'encoder') and 
                                self.embedding_space.encoder is not None and
                                hasattr(self.embedding_space.encoder, 'config') and
                                hasattr(self.embedding_space.encoder.config, 'd_model')):
                                d_model = self.embedding_space.encoder.config.d_model
                            elif hasattr(self.embedding_space, 'd_model'):
                                d_model = self.embedding_space.d_model
                        log_training_start_banner(
                            total_epochs=n_epochs,
                            batch_size=batch_size,
                            training_type="SP",
                            d_model=d_model,
                            target_column=self.target_col_name,
                            fine_tune=fine_tune,
                            n_hidden_layers=self.predictor.config.n_hidden_layers if hasattr(self.predictor, 'config') else None
                        )
                    except Exception as e:
                        logger.debug(f"Could not log training start banner: {e}")
                    
                    # Add event to training timeline: ES frozen (when fine_tune=False, encoder is always frozen)
                    if not fine_tune and hasattr(self, '_training_timeline'):
                        freeze_event = {
                            "epoch": 0,
                            "event_type": "es_frozen",
                            "freeze_warmup_epochs": 0,
                            "total_epochs": n_epochs,
                            "unfreeze_epoch": None,
                            "reason": "Fine-tuning disabled: ES frozen throughout training (only predictor parameters are trainable)",
                            "time_now": training_start_time,
                        }
                        self._training_timeline.append(freeze_event)
                    
                    # Track consecutive NaN batches to abort if training is permanently broken
                    consecutive_nan_batches = 0
                    max_consecutive_nan_batches = 50  # Abort after 50 consecutive NaN batches
                    
                    for epoch_idx in range(n_epochs):
                        # Track current epoch for logging
                        self._current_epoch = epoch_idx
                        
                        # ====================================================================
                        # CRITICAL: Define train_encoder_now ONCE per epoch
                        # This determines whether encoder should be trainable this epoch
                        # True only when the ES is intended to be updated
                        # ====================================================================
                        train_encoder_now = fine_tune and (freeze_warmup_epochs == 0 or epoch_idx >= freeze_warmup_epochs)
                        
                        # ====================================================================
                        # MODE BANNER: Log current training mode for clarity
                        # ====================================================================
                        if epoch_idx == 0 or (freeze_warmup_epochs > 0 and epoch_idx == freeze_warmup_epochs):
                            if train_encoder_now:
                                logger.info("")
                                logger.info("=" * 80)
                                logger.info(f"🎯 MODE: JOINT_FINE_TUNE (encoder trainable)")
                                logger.info("=" * 80)
                            else:
                                warmup_remaining = max(0, freeze_warmup_epochs - epoch_idx) if freeze_warmup_epochs > 0 else 0
                                if warmup_remaining > 0:
                                    logger.info("")
                                    logger.info("=" * 80)
                                    logger.info(f"🎯 MODE: SP_TRAINING_ONLY (encoder frozen, warmup epochs remaining: {warmup_remaining})")
                                    logger.info("=" * 80)
                                else:
                                    logger.info("")
                                    logger.info("=" * 80)
                                    logger.info(f"🎯 MODE: SP_TRAINING_ONLY (encoder frozen)")
                                    logger.info("=" * 80)
                        
                        # ====================================================================
                        # PHASED FREEZING: Unfreeze encoder after warmup period
                        # ====================================================================
                        if freeze_warmup_epochs > 0 and fine_tune and epoch_idx == freeze_warmup_epochs:
                            logger.info("")
                            logger.info("=" * 80)
                            logger.info(f"🔓 UNFREEZING ENCODER: Epoch {epoch_idx + 1} (warmup complete)")
                            logger.info("=" * 80)
                            
                            encoder_params = list(self.embedding_space.encoder.parameters())
                            
                            # Apply train_encoder_now pattern: mode, requires_grad, optimizer
                            if train_encoder_now:
                                # Set encoder to training mode
                                self.embedding_space.encoder.train()
                                assert self.embedding_space.encoder.training == True, f"❌ CRITICAL: encoder.train() failed!"
                                
                                # Enable gradients
                                for param in encoder_params:
                                    param.requires_grad = True
                                
                                # Add encoder params to optimizer (Option B: add param group at switch time)
                                # LRTimeline will manage ES LR coordination
                                if scheduler is not None and isinstance(scheduler, LRTimeline):
                                    scheduler.set_es_unfreeze_epoch(epoch_idx)
                                    es_start_lr = scheduler.get_es_lr(epoch_idx)
                                else:
                                    # Fallback if no scheduler
                                    sp_current_lr = optimizer_params.get("lr", 1e-3)
                                    es_start_lr = sp_current_lr * 0.4
                                
                                optimizer.add_param_group({
                                    'params': encoder_params,
                                    'lr': es_start_lr,  # Start low, LRTimeline will manage updates
                                })
                                
                                # Add event to training timeline: ES unfrozen
                                if hasattr(self, '_training_timeline'):
                                    unfreeze_event = {
                                        "epoch": epoch_idx,
                                        "event_type": "es_unfrozen",
                                        "freeze_warmup_epochs": freeze_warmup_epochs,
                                        "total_epochs": n_epochs,
                                        "es_start_lr": float(es_start_lr),
                                        "sp_current_lr": float(optimizer.param_groups[0]['lr']) if optimizer.param_groups else None,
                                        "es_lr_ratio": float(es_start_lr / optimizer.param_groups[0]['lr']) if optimizer.param_groups and optimizer.param_groups[0]['lr'] > 0 else None,
                                        "reason": f"Phased freezing complete: ES unfrozen at epoch {epoch_idx + 1} after {freeze_warmup_epochs} epoch warmup period",
                                        "time_now": time.time(),
                                    }
                                    self._training_timeline.append(unfreeze_event)
                                
                                logger.info(f"   ✅ Encoder unfrozen: {len(encoder_params)} params now trainable")
                                if scheduler is not None and isinstance(scheduler, LRTimeline):
                                    logger.info(f"   ✅ LRTimeline managing ES LR coordination")
                                    logger.info(f"   ✅ ES LR: 40% of SP LR (constant ratio)")
                                logger.info(f"   ✅ Fine-tuning begins now (epoch {epoch_idx + 1}/{n_epochs})")
                            else:
                                # This should never happen at unfreeze time, but be defensive
                                logger.error(f"❌ BUG: train_encoder_now=False at unfreeze epoch!")
                                self.embedding_space.encoder.eval()
                                for param in encoder_params:
                                    param.requires_grad = False
                            
                            # Log warmup summary for diagnostics
                            if hasattr(self, '_best_auc_during_warmup') and self._best_auc_during_warmup >= 0:
                                logger.info(f"   📊 Warmup summary: Best AUC during warmup = {self._best_auc_during_warmup:.4f} @ epoch {self._warmup_best_auc_epoch + 1}")
                            
                            logger.info("=" * 80)
                            logger.info("")
                        
                        # ====================================================================
                        # Apply train_encoder_now pattern: ensure encoder state matches
                        # ====================================================================
                        if train_encoder_now:
                            # Encoder should be in train mode with gradients enabled
                            self.embedding_space.encoder.train()
                            for param in self.embedding_space.encoder.parameters():
                                param.requires_grad = True
                        else:
                            # Encoder should be in eval mode with gradients disabled
                            self.embedding_space.encoder.eval()
                            for param in self.embedding_space.encoder.parameters():
                                param.requires_grad = False
                        
                        # Set learning rate for this epoch using LRTimeline (if applicable)
                        if scheduler is not None and isinstance(scheduler, LRTimeline):
                            scheduler.set_epoch(epoch_idx)
                            
                            # Get SP and ES LR from LRTimeline
                            sp_lr = scheduler.get_sp_lr(epoch_idx)
                            es_lr = scheduler.get_es_lr(epoch_idx) if scheduler.mode == 'sp_plus_es' else None
                            
                            # Update param groups: SP group gets SP LR, ES group (if exists) gets ES LR
                            if len(optimizer.param_groups) == 1:
                                # Only SP group (ES not unfrozen yet)
                                optimizer.param_groups[0]['lr'] = sp_lr
                                actual_lr = sp_lr
                            elif len(optimizer.param_groups) >= 2:
                                # Both SP and ES groups
                                # Identify which group is which by checking param IDs
                                encoder_param_ids = {id(p) for p in self.embedding_space.encoder.parameters()}
                                predictor_param_ids = {id(p) for p in self.predictor.parameters()}
                                
                                for group in optimizer.param_groups:
                                    group_param_ids = {id(p) for p in group['params']}
                                    if group_param_ids.intersection(encoder_param_ids):
                                        # This is the ES group
                                        group['lr'] = es_lr if es_lr is not None else 0.0
                                    elif group_param_ids.intersection(predictor_param_ids):
                                        # This is the SP group
                                        group['lr'] = sp_lr
                                    else:
                                        # Unknown group, use SP LR as fallback
                                        group['lr'] = sp_lr
                                
                                actual_lr = sp_lr  # Record SP LR as primary
                            else:
                                # Fallback
                                for param_group in optimizer.param_groups:
                                    param_group['lr'] = sp_lr
                                actual_lr = sp_lr
                            
                            # Record actual LR used
                            scheduler.record_actual_lr(epoch_idx, actual_lr)
                            
                            # Log LR periodically (every 10 epochs or first/last)
                            if epoch_idx == 0 or (epoch_idx + 1) % 10 == 0 or epoch_idx == n_epochs - 1:
                                progress_pct = (epoch_idx + 1) / n_epochs * 100
                                if es_lr is not None and es_lr > 0:
                                    logger.info(f"📈 LRTimeline: epoch {epoch_idx + 1}/{n_epochs} ({progress_pct:.1f}%), SP LR={sp_lr:.6e}, ES LR={es_lr:.6e}")
                                else:
                                    logger.info(f"📈 LRTimeline: epoch {epoch_idx + 1}/{n_epochs} ({progress_pct:.1f}%), LR={sp_lr:.6e}")
                        
                        # Update epoch progress for AdaptiveLoss (if using learned loss blending)
                        if hasattr(self, 'target_codec') and hasattr(self.target_codec, 'loss_fn'):
                            from featrix.neural.set_codec import AdaptiveLoss
                            if isinstance(self.target_codec.loss_fn, AdaptiveLoss):
                                epoch_progress = (epoch_idx + 1) / n_epochs
                                self.target_codec.loss_fn.set_epoch_progress(epoch_progress)
                        
                        # Set current epoch in logging context for standardized logging format
                        from featrix.neural.logging_config import current_epoch_ctx
                        current_epoch_ctx.set(epoch_idx + 1)  # Use 1-indexed epoch for display
                        
                        # Log cool epoch banner (every 10 epochs, or first/last epoch)
                        if epoch_idx == 0 or (epoch_idx + 1) % 10 == 0 or epoch_idx == n_epochs - 1:
                            try:
                                from featrix.neural.training_banner import log_epoch_banner
                                log_epoch_banner(epoch_idx + 1, n_epochs, training_type="SP")
                            except Exception as e:
                                logger.debug(f"Could not log epoch banner: {e}")
                        
                        # CRITICAL: Get log prefix for this epoch - EVERY log line must use this
                        log_prefix = self._get_log_prefix(epoch_idx)
                        
                        training_info_entry = {}
                        training_info_entry['loss'] = None
                        training_info_entry['validation_loss'] = None

                        training_info_entry['start_time'] = time.time()
                        training_info_entry['epoch_idx'] = epoch_idx
                        
                        # Track hyperparameters at start of epoch
                        training_info_entry['hyperparameters'] = {}
                        # Get current learning rate
                        current_lr = get_lr()
                        lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
                        training_info_entry['hyperparameters']['learning_rate'] = float(lr_value) if lr_value is not None else None
                        
                        # Get current FocalLoss parameters if using FocalLoss
                        if isinstance(self.target_codec.loss_fn, FocalLoss):
                            training_info_entry['hyperparameters']['focal_gamma'] = float(self.target_codec.loss_fn.gamma)
                            training_info_entry['hyperparameters']['focal_min_weight'] = float(self.target_codec.loss_fn.min_weight)
                        else:
                            training_info_entry['hyperparameters']['focal_gamma'] = None
                            training_info_entry['hyperparameters']['focal_min_weight'] = None
                        # progress_dict.batch_idx = 0
                        # logger.debug("epoch_idx = ", epoch_idx)
                        
                        # ====================================================================
                        # START: BATCH FOR LOOP (enumerate(train_dataloader))
                        # ====================================================================
                        for batch_idx, column_batch in enumerate(train_dataloader):
                            # CRITICAL: Clear gradients at the very start of each batch iteration
                            # This prevents "backward through graph twice" errors if previous batch had issues
                            # or if a 'continue' statement was executed before zero_grad() was called
                            optimizer.zero_grad()
                            
                            # print("METADUDE: ", batch_idx, type(column_batch), column_batch))
                            progress_dict["batch_idx"] += 1
    
                            # Check for ABORT/FINISH files periodically (every 10 batches)
                            if batch_idx % 10 == 0:
                                should_finish = self._check_abort_finish_files(
                                    job_id=job_id,
                                    batch_idx=batch_idx,
                                    log_prefix=log_prefix,
                                    progress_dict=progress_dict
                                )
                                if should_finish:
                                    break  # FINISH file detected - graceful early stop
    
                            # Move data to same device as encoder
                            encoder_device = next(self.embedding_space.encoder.parameters()).device
                            for key, tokenbatch in column_batch.items():
                                column_batch[key] = tokenbatch.to(encoder_device)
    
                            # Verify predictor is on correct device (first batch only)
                            self._verify_predictor_device(
                                epoch_idx=epoch_idx,
                                batch_idx=batch_idx,
                                log_prefix=log_prefix
                            )
                            
                            # Assert that models are in correct training states
                            # Use train_encoder_now defined once per epoch (not recomputed)
                            self._verify_training_state_assertions(
                                epoch_idx=epoch_idx,
                                batch_idx=batch_idx,
                                fine_tune=train_encoder_now,
                                optimizer=optimizer
                            )
    
                            # Extract and prepare target values from batch
                            targets, column_batch = self._prepare_batch_targets(column_batch)
    
                            # 
                            # Encode the batch using the ES encoder
                            # 
                            enc_time = time.time()
                            # Encoder
                            # Apply noise so that some column embeddings are masked out with MARGINAL
                            # tokens. This helps regularize the downstream model, and make it robust
                            # to missing data at query time.
                            # Only use full-dimensional embeddings for the predictor.
                            try:
                                # CRITICAL: Verify encoder is in correct mode
                                # Use train_encoder_now defined once per epoch (not recomputed)
                                encoder_device = next(self.embedding_space.encoder.parameters()).device if list(self.embedding_space.encoder.parameters()) else None
                                encoder_training = self.embedding_space.encoder.training
                                
                                # Defensive check: encoder state should match train_encoder_now (set at epoch start)
                                # This should rarely trigger if epoch-level setup is correct, but catch any drift
                                if train_encoder_now and not encoder_training:
                                    logger.warning(f"{log_prefix}⚠️  Encoder is in eval mode but train_encoder_now=True! Correcting to train mode...")
                                    self.embedding_space.encoder.train()
                                    encoder_training = True
                                    for param in self.embedding_space.encoder.parameters():
                                        param.requires_grad = True
                                elif not train_encoder_now and encoder_training:
                                    logger.warning(f"{log_prefix}⚠️  Encoder is in train mode but train_encoder_now=False (frozen mode)! Correcting to eval mode...")
                                    self.embedding_space.encoder.eval()
                                    encoder_training = False
                                    for param in self.embedding_space.encoder.parameters():
                                        param.requires_grad = False
                                
                                # Log encoder diagnostics on first batch
                                self._log_encoder_diagnostics(
                                    epoch_idx=epoch_idx,
                                    batch_idx=batch_idx,
                                    log_prefix=log_prefix,
                                    encoder_device=encoder_device,
                                    encoder_training=encoder_training,
                                    fine_tune=fine_tune,
                                    column_batch=column_batch,
                                    batch_full=None  # Will be set after encode
                                )
                                
                                _, batch_full = self.embedding_space.encoder.encode(
                                    column_batch, apply_noise=True
                                )
                                
                                # CRITICAL DIAGNOSTIC: Verify encoder output invariants based on mode
                                # Use train_encoder_now defined once per epoch (not recomputed)
                                if epoch_idx == 0 and batch_idx < 3:
                                    if train_encoder_now:
                                        # FINE-TUNE MODE: h.requires_grad == True is required
                                        if not batch_full.requires_grad:
                                            logger.error(f"💥 CRITICAL: Encoder output is DETACHED when train_encoder_now=True!")
                                            logger.error(f"   batch_full.requires_grad = {batch_full.requires_grad}")
                                            logger.error(f"   This means gradients CANNOT flow back to encoder!")
                                            logger.error(f"   Check encoder.encode() for .detach() calls or torch.no_grad() contexts")
                                        else:
                                            logger.info(f"✅ Encoder output has requires_grad=True (gradients can flow)")
                                    else:
                                        # FROZEN MODE: h.requires_grad == False is expected
                                        if batch_full.requires_grad:
                                            logger.warning(f"⚠️  Encoder output has requires_grad=True in frozen mode (will be detached)")
                                        else:
                                            logger.info(f"✅ Encoder output detached (frozen mode, as expected)")
                                
                                # Log encoding output diagnostics on first batch
                                if epoch_idx == 0 and batch_idx == 0:
                                    self._log_encoder_diagnostics(
                                        epoch_idx=epoch_idx,
                                        batch_idx=batch_idx,
                                        log_prefix=log_prefix,
                                        encoder_device=encoder_device,
                                        encoder_training=encoder_training,
                                        fine_tune=fine_tune,
                                        column_batch=column_batch,
                                        batch_full=batch_full
                                    )
                                
                                # CRITICAL FIX: Ensure all tensor dtypes are float32 before hitting linear layers
                                # SetCodec produces int64, StringCodec produces float32, causing dtype mismatch
                                if hasattr(batch_full, 'dtype') and batch_full.dtype != torch.float32:
                                    batch_full = batch_full.to(dtype=torch.float32)
                            
                                # CRITICAL FIX: If not training encoder, detach embeddings so gradients don't vanish
                                # When train_encoder_now=False, encoder params aren't in the optimizer, so gradients
                                # trying to flow through them just disappear, causing zero gradient bug
                                if not train_encoder_now:
                                    batch_full = batch_full.detach()
                                    if epoch_idx == 0 and batch_idx == 0:
                                        logger.info(f"✅ Detached encoder output (train_encoder_now=False, encoder frozen)")
                                
                            except Exception as err:
                                print("self.embedding_space.encoder.encode failed:")
                                print(f"Error: {err}")
                                print(f"column_batch type: {type(column_batch)}")
                            
                                # Show device information for each column's tensors
                                if isinstance(column_batch, dict):
                                    print("Device information for column_batch:")
                                    for col_name, token_batch in column_batch.items():
                                        if hasattr(token_batch, 'values') and hasattr(token_batch.values, 'device'):
                                            values_device = token_batch.values.device
                                            print(f"  {col_name}: values on {values_device}")
                                        elif hasattr(token_batch, 'value') and hasattr(token_batch.value, 'device'):
                                            value_device = token_batch.value.device  
                                            print(f"  {col_name}: value on {value_device}")
                                        else:
                                            print(f"  {col_name}: no device info available ({type(token_batch)})")
                            
                                print(f"embedding_space.encoder device: {next(self.embedding_space.encoder.parameters()).device}")
                                print("------------------------------------------------------")
                                raise(err)
                        
                            batch = batch_full
                            enc_delta = time.time() - enc_time
                            encode_time += enc_delta
                            
                            # CRITICAL: Move batch to same device as predictor
                            # Encoder might be on CPU (force_cpu=True) but predictor is on GPU
                            predictor_device = next(self.predictor.parameters()).device
                            if batch.device != predictor_device:
                                batch = batch.to(predictor_device)
                            
                            # CRITICAL: Move targets to same device as predictor
                            if targets.device != predictor_device:
                                targets = targets.to(predictor_device)
                            
                            # DIAGNOSTIC: Check if batch embeddings are varying (should be different for each sample)
                            if epoch_idx == 0 and batch_idx == 0:
                                batch_std = batch.std().item()
                                batch_min = batch.min().item()
                                batch_max = batch.max().item()
                                batch_mean = batch.mean().item()
                                logger.info(f"🔍 BATCH EMBEDDING DIAGNOSTIC [batch={batch_idx}]:")
                                logger.info(f"   Batch shape: {batch.shape}, device: {batch.device}")
                                logger.info(f"   Batch stats: min={batch_min:.4f}, max={batch_max:.4f}, mean={batch_mean:.4f}, std={batch_std:.6f}")
                                if batch_std < 0.001:
                                    logger.error(f"⚠️  WARNING: Batch embeddings are nearly constant! std={batch_std:.6f}")
                                    logger.error(f"   This means encoder is producing identical embeddings for all samples")
                                    logger.error(f"   First 3 batch rows (first 5 dims): {batch[:3, :5].tolist()}")
                                else:
                                    logger.info(f"   ✅ Batch embeddings are varying (std={batch_std:.6f})")
    
                            # 
                            # MAIN STEP (with BF16 mixed precision if enabled)
                            # 
                            # SAFETY CHECK: Ensure batch is on predictor device right before forward pass
                            # This catches any case where the earlier move was skipped or failed
                            if batch.device != predictor_device:
                                logger.warning(f"⚠️  SAFETY: batch still on {batch.device}, moving to {predictor_device}")
                                batch = batch.to(predictor_device)
                            
                            # CRITICAL DEBUG: Verify encoder is in computation graph
                            # h = tensor that feeds predictor from encoder (batch_full -> batch)
                            h = batch  # This is the encoder output feeding into predictor
                            
                            # Initialize aggregated gradient tracking for hooks (if not exists)
                            if not hasattr(self, '_grad_hook_stats'):
                                self._grad_hook_stats = {
                                    'dL_dh_norms': [],
                                    'h_norms': [],
                                    'h_stds': [],
                                    'last_logged_batch': -1
                                }
                            
                            # Check computation graph connection (first 3 batches + every 100 batches)
                            # Use train_encoder_now defined once per epoch (not recomputed)
                            should_check_computation_graph = (epoch_idx == 0 and batch_idx < 3) or (batch_idx % 100 == 0 and epoch_idx < 3)
                            if should_check_computation_graph:
                                # Compute h statistics (representation collapse detection)
                                h_norm = h.norm().item()
                                h_std = h.std().item()
                                
                                logger.info("=" * 80)
                                logger.info(f"🔍 COMPUTATION GRAPH CHECK (Epoch {epoch_idx}, Batch {batch_idx})")
                                logger.info(f"   Mode: {'JOINT_FINE_TUNE' if train_encoder_now else 'SP_TRAINING_ONLY'}")
                                logger.info("=" * 80)
                                logger.info(f"   h (encoder output) requires_grad: {h.requires_grad}")
                                logger.info(f"   h.grad_fn: {h.grad_fn}")
                                logger.info(f"   h.grad_fn type: {type(h.grad_fn) if h.grad_fn is not None else 'None'}")
                                logger.info(f"   ||h||: {h_norm:.6e}")
                                logger.info(f"   std(h): {h_std:.6e}")
                                
                                if train_encoder_now:
                                    # FINE-TUNE MODE: h.requires_grad == True and grad_fn exists is required
                                    if not h.requires_grad:
                                        logger.error(f"   ❌ CRITICAL: h.requires_grad = False! Encoder is NOT in computation graph!")
                                        logger.error(f"      Encoder output was detached or computed with torch.no_grad()")
                                        logger.error(f"      Gradients CANNOT flow back to encoder!")
                                    elif h.grad_fn is None:
                                        logger.error(f"   ❌ CRITICAL: h.grad_fn = None! Encoder is NOT in computation graph!")
                                        logger.error(f"      Encoder output has no gradient function - was detached!")
                                        logger.error(f"      Gradients CANNOT flow back to encoder!")
                                    else:
                                        logger.info(f"   ✅ Encoder IS in computation graph (requires_grad=True, grad_fn exists)")
                                else:
                                    # FROZEN MODE: h.requires_grad == False is expected
                                    if h.requires_grad:
                                        logger.warning(f"   ⚠️  h.requires_grad = True in frozen mode (will be detached)")
                                    else:
                                        logger.info(f"   ✅ Encoder output detached (frozen mode, as expected)")
                                
                                # Check for representation collapse
                                if h_std < 0.001:
                                    logger.error(f"   ⚠️  REPRESENTATION COLLAPSE: std(h) = {h_std:.6e} (nearly zero variance!)")
                                    logger.error(f"      Encoder is producing nearly identical embeddings for all samples")
                                    logger.error(f"      Predictor can dominate and gradients back to encoder become meaningless")
                                
                                # Register aggregated hook to check gradient flow (rate-limited)
                                # CRITICAL: Only register hook when training encoder (fine-tune mode)
                                # In frozen mode, encoder output is detached and doesn't require gradients (expected)
                                if train_encoder_now:
                                    if h.requires_grad:
                                        def grad_hook(grad):
                                            if grad is not None:
                                                grad_norm = grad.norm().item()
                                                # Accumulate stats for this batch
                                                self._grad_hook_stats['dL_dh_norms'].append(grad_norm)
                                                self._grad_hook_stats['h_norms'].append(h_norm)
                                                self._grad_hook_stats['h_stds'].append(h_std)
                                            return grad
                                        
                                        # Register hook (will be called during backward)
                                        h.register_hook(grad_hook)
                                        logger.info("   ✅ Registered aggregated gradient hook on h (will accumulate ||dL/dh|| for batch)")
                                    else:
                                        logger.error("   ❌ Cannot register gradient hook - tensor does not require gradients in fine-tune mode!")
                                else:
                                    # Frozen mode: encoder output is detached, no gradient hook needed
                                    logger.info("   ℹ️  Skipping gradient hook registration (frozen encoder mode)")
                                logger.info("=" * 80)
                            
                            with torch.amp.autocast(device_type='cuda', dtype=autocast_dtype, enabled=use_autocast):
                                out = self.predictor(batch)
                            
                            # CRITICAL: Verify output is on correct device
                            if out.device != predictor_device:
                                logger.error(f"❌ MODEL OUTPUT ON WRONG DEVICE! out.device={out.device}, predictor_device={predictor_device}")
                                out = out.to(predictor_device)
                            
                            # SANITY CHECK: Print raw outputs per batch to diagnose probability spread issues
                            # If logits range is ~6 but probs std is 0.001, something is off in conversion/measurement
                            should_log_raw_outputs = (epoch_idx == 0 and batch_idx < 3) or (batch_idx % 50 == 0 and epoch_idx < 3)
                            if should_log_raw_outputs:
                                # Compute probabilities from logits (always use softmax for consistency)
                                probs = torch.softmax(out, dim=1)  # [batch_size, n_classes]
                                
                                # Check if binary classification
                                is_binary = out.shape[1] == 2
                                if is_binary:
                                    # For binary, p_good is typically the positive class (index 1)
                                    # But check target_codec to see which class is "good"
                                    p_good = probs[:, 1]  # Assume index 1 is positive class
                                
                                # Extract first 5 samples
                                logits_first5 = out[:5].detach().cpu()
                                probs_first5 = probs[:5].detach().cpu()
                                
                                # Compute max probabilities for first 20 samples
                                n_samples = min(20, out.shape[0])
                                max_probs = probs[:n_samples].max(dim=1).values.detach().cpu()
                                
                                logger.info("=" * 80)
                                logger.info(f"🔍 RAW OUTPUT SANITY CHECK (Epoch {epoch_idx}, Batch {batch_idx})")
                                logger.info("=" * 80)
                                logger.info(f"   Logits[:5]:")
                                for i in range(min(5, out.shape[0])):
                                    logger.info(f"      Sample {i}: {logits_first5[i].tolist()}")
                                
                                logger.info(f"   Probs[:5]:")
                                for i in range(min(5, out.shape[0])):
                                    logger.info(f"      Sample {i}: {probs_first5[i].tolist()}")
                                
                                logger.info(f"   Max probs (first {n_samples} samples):")
                                logger.info(f"      Mean: {max_probs.mean().item():.6f}, Std: {max_probs.std().item():.6f}")
                                logger.info(f"      Min: {max_probs.min().item():.6f}, Max: {max_probs.max().item():.6f}")
                                
                                if is_binary:
                                    # Binary classification: log p_good stats
                                    p_good_first20 = p_good[:n_samples].detach().cpu()
                                    logger.info(f"   Binary p_good (first {n_samples} samples, class index 1):")
                                    logger.info(f"      Mean: {p_good_first20.mean().item():.6f}, Std: {p_good_first20.std().item():.6f}")
                                    logger.info(f"      Min: {p_good_first20.min().item():.6f}, Max: {p_good_first20.max().item():.6f}")
                                
                                # Check for suspicious patterns
                                logit_range = out.max().item() - out.min().item()
                                prob_std = probs.std().item()
                                
                                # Store prob_std for LR controller (to block adjustments if output collapsed)
                                self._last_prob_std = prob_std
                                
                                logger.info(f"   Overall stats:")
                                logger.info(f"      Logit range: {logit_range:.4f}")
                                logger.info(f"      Prob std: {prob_std:.6f}")
                                
                                if logit_range > 5.0 and prob_std < 0.001:
                                    logger.error(f"   ⚠️  SUSPICIOUS: Logit range is {logit_range:.2f} but prob std is {prob_std:.6f}!")
                                    logger.error(f"      This suggests a problem with logit→prob conversion or measurement")
                                    logger.error(f"      Check: softmax computation, numerical stability, or batch statistics")
                                
                                logger.info("=" * 80)
                            
                            # DIAGNOSTIC: Log first batch and periodically to catch constant outputs
                            should_log_diagnostic = (epoch_idx == 0 and batch_idx == 0) or (batch_idx % 50 == 0 and epoch_idx < 3)
                            if should_log_diagnostic:
                                out_std = out.std().item()
                                out_mean = out.mean().item()
                                out_min = out.min().item()
                                out_max = out.max().item()
                                
                                # CRITICAL: Check if predictor output is constant (model collapse)
                                if out_std < 0.01:
                                    logger.error(f"{log_prefix}🚨 PREDICTOR OUTPUT COLLAPSE: std={out_std:.6f} (nearly constant!)")
                                    logger.error(f"{log_prefix}   Output stats: min={out_min:.4f}, max={out_max:.4f}, mean={out_mean:.4f}")
                                    logger.error(f"{log_prefix}   This means the predictor is outputting the same value for all inputs")
                                    logger.error(f"{log_prefix}   Check: predictor initialization, learning rate, or encoder outputs")
                                    
                                    # Check if embeddings are constant too
                                    batch_std = batch.std().item()
                                    if batch_std < 0.001:
                                        logger.error(f"{log_prefix}   ⚠️  ENCODER ALSO COLLAPSED: embedding std={batch_std:.6f}")
                                        logger.error(f"{log_prefix}   Encoder is producing identical embeddings - check encoder loading!")
                                    else:
                                        logger.error(f"{log_prefix}   ✅ Encoder OK: embedding std={batch_std:.6f} (encoder is working)")
                                        logger.error(f"{log_prefix}   ❌ Predictor is the problem - check initialization or LR")
                                out_min = out.min().item()
                                out_max = out.max().item()
                                out_mean = out.mean().item()
                                
                                logger.info(f"🔍 BATCH DIAGNOSTIC [batch={batch_idx}]:")
                                logger.info(f"   Output shape: {out.shape}, device: {out.device}")
                                logger.info(f"   Output stats: min={out_min:.4f}, max={out_max:.4f}, mean={out_mean:.4f}, std={out_std:.6f}")
                                logger.info(f"   Targets shape: {targets.shape}, device: {targets.device}, dtype: {targets.dtype}")
                                logger.info(f"   Batch device: {batch.device}, Predictor device: {predictor_device}")
                                
                                # Check if output is constant (bad sign)
                                if out_std < 0.001:
                                    logger.error(f"⚠️  WARNING: Model output is nearly constant! std={out_std:.6f}")
                                    logger.error(f"   This suggests the model isn't learning or inputs are constant")
                                    logger.error(f"   First 5 outputs: {out[:5].tolist()}")
                                    logger.error(f"   First 5 targets: {targets[:5].tolist()}")
                                
                                if epoch_idx == 0 and batch_idx == 0:
                                    if hasattr(self.target_codec, 'tokens_to_members'):
                                        logger.info(f"   Target codec mapping: {self.target_codec.tokens_to_members}")
                                    # Show raw logits before softmax
                                    logger.info(f"   First 3 raw logits (before softmax):")
                                    for i in range(min(3, out.shape[0])):
                                        logger.info(f"     Sample {i}: logits={out[i].tolist()}, target_token={targets[i].item()}")
    
                            # Compute loss (main + optional pairwise ranking)
                            loss = self._compute_loss_with_pairwise_ranking(
                                out=out,
                                targets=targets,
                                loss_fn=loss_fn,
                                use_pairwise_ranking_loss=use_pairwise_ranking_loss,
                                pairwise_loss_weight=pairwise_loss_weight,
                                autocast_dtype=autocast_dtype,
                                use_autocast=use_autocast,
                                batch_idx=batch_idx
                            )
    
                            optimizer.zero_grad()
                            # NOTE: optimizer.zero_grad() is now ALSO called at the START of each batch iteration (line ~7303)
                            # This is the second call which is technically redundant but kept for backwards compatibility
                            # The early call ensures gradients are always cleared even if previous batch had errors
                            
                            # CRITICAL FIX: Check loss value BEFORE backward pass
                            # This prevents gradient corruption from propagating
                            if torch.isnan(loss) or torch.isinf(loss):
                                logger.error(f"💥 FATAL: NaN/Inf loss detected BEFORE backward! loss={loss.item()}")
                                logger.error(f"   Epoch: {epoch_idx}, Batch: {batch_idx}")
                                logger.error(f"   Output stats: min={out.min().item():.4f}, max={out.max().item():.4f}, mean={out.mean().item():.4f}")
                                logger.error(f"   Target stats: min={targets.min().item()}, max={targets.max().item()}")
                                # Skip this batch entirely - don't corrupt gradients
                                logger.error("   ⚠️  SKIPPING THIS BATCH to prevent gradient corruption")
                                continue  # Skip to next batch
                            
                            loss.backward()
                            
                            # Log aggregated gradient stats after backward (hook has accumulated stats)
                            should_log_grad_stats = (batch_idx % 100 == 0) or (epoch_idx == 0 and batch_idx < 3)
                            if should_log_grad_stats and fine_tune and hasattr(self, '_grad_hook_stats') and len(self._grad_hook_stats.get('dL_dh_norms', [])) > 0:
                                dL_dh_norms = self._grad_hook_stats['dL_dh_norms']
                                h_norms = self._grad_hook_stats['h_norms']
                                h_stds = self._grad_hook_stats['h_stds']
                                
                                if dL_dh_norms:
                                    mean_dL_dh = sum(dL_dh_norms) / len(dL_dh_norms)
                                    max_dL_dh = max(dL_dh_norms)
                                    mean_h_norm = sum(h_norms) / len(h_norms) if h_norms else 0.0
                                    mean_h_std = sum(h_stds) / len(h_stds) if h_stds else 0.0
                                    
                                    logger.info("=" * 80)
                                    logger.info(f"📊 GRADIENT FLOW STATS (Epoch {epoch_idx}, Batch {batch_idx}) - Aggregated over batch")
                                    logger.info("=" * 80)
                                    logger.info(f"   ||dL/dh||: mean={mean_dL_dh:.6e}, max={max_dL_dh:.6e} (over {len(dL_dh_norms)} samples)")
                                    logger.info(f"   ||h||: mean={mean_h_norm:.6e}")
                                    logger.info(f"   std(h): mean={mean_h_std:.6e}")
                                    
                                    if mean_dL_dh < 1e-6:
                                        logger.warning(f"   ⚠️  dL/dh is near zero! Encoder won't learn even if connected!")
                                    
                                    # Representation collapse signature
                                    if mean_h_std < 0.001 and mean_dL_dh < 1e-6:
                                        logger.error(f"   🚨 REPRESENTATION COLLAPSED: std(h) ~ 0 and ||dL/dh|| ~ 0")
                                        logger.error(f"      This is an immediate 'representation collapsed' signature!")
                                        logger.error(f"      Encoder output has no variance and no gradient signal")
                                    
                                    logger.info("=" * 80)
                                    
                                    # Clear stats for next batch
                                    self._grad_hook_stats['dL_dh_norms'] = []
                                    self._grad_hook_stats['h_norms'] = []
                                    self._grad_hook_stats['h_stds'] = []
                        
                            # Compute unclipped gradient norm for diagnostics WITHOUT modifying gradients
                            # CRITICAL: Don't use clip_grad_norm_ with inf - it modifies gradients in-place!
                            # Use predictor parameters directly to ensure we're checking the right parameters
                            
                            # Compute predictor gradient norm: GLOBAL L2 norm over entire module
                            # Formula: ||∇||_global = sqrt(sum over all params p of ||g_p||^2^2)
                            # This is NOT mean-of-norms (which would be misleading if modules have different sizes)
                            # We sum squared norms then take sqrt to get the true global L2 norm
                            predictor_norm_squared = 0.0
                            for p in self.predictor.parameters():
                                if p.grad is not None:
                                    param_norm = p.grad.data.norm(2)  # L2 norm of this parameter's gradient tensor
                                    predictor_norm_squared += param_norm.item() ** 2  # Sum of squared norms
                            predictor_norm = predictor_norm_squared ** 0.5  # Global L2: sqrt(sum ||g_p||^2)
                            
                            # Compute encoder gradient norm separately: GLOBAL L2 norm
                            # Same formula: ||∇||_global = sqrt(sum over all params p of ||g_p||^2^2)
                            # Always compute encoder stats (for both frozen and fine-tune modes)
                            encoder_norm = 0.0
                            gradient_flow_ratio = None
                            gradient_flow_log_ratio = None
                            
                            encoder_norm_squared = 0.0
                            encoder_params_with_grad = 0
                            encoder_params_total = 0
                            encoder_params_frozen = 0
                            encoder_params_not_in_optimizer = 0
                            
                            # Check if encoder params are in optimizer (check all param groups)
                            optimizer_param_ids = set()
                            for param_group in optimizer.param_groups:
                                optimizer_param_ids.update({id(p) for p in param_group['params']})
                            
                            # Also check predictor params are in optimizer (required invariant)
                            predictor_param_ids = {id(p) for p in self.predictor.parameters()}
                            predictor_params_in_optimizer = sum(1 for pid in predictor_param_ids if pid in optimizer_param_ids)
                            predictor_params_total = len(predictor_param_ids)
                            
                            # Bucket encoder params by module prefix for gradient coverage analysis
                            module_buckets = {
                                'joint_encoder': {'total': 0, 'with_grad': 0, 'frozen': 0, 'not_in_opt': 0},
                                'column_encoder': {'total': 0, 'with_grad': 0, 'frozen': 0, 'not_in_opt': 0},
                                'relationship': {'total': 0, 'with_grad': 0, 'frozen': 0, 'not_in_opt': 0},
                                'out_converter': {'total': 0, 'with_grad': 0, 'frozen': 0, 'not_in_opt': 0},
                                'other': {'total': 0, 'with_grad': 0, 'frozen': 0, 'not_in_opt': 0},
                            }
                            
                            encoder_param_ids = set()
                            for name, p in self.embedding_space.encoder.named_parameters():
                                encoder_params_total += 1
                                encoder_param_ids.add(id(p))
                                
                                # Determine which bucket this param belongs to
                                bucket_key = 'other'
                                if 'joint_encoder' in name:
                                    bucket_key = 'joint_encoder'
                                elif 'column_encoder' in name or 'column_encoders' in name:
                                    bucket_key = 'column_encoder'
                                elif 'relationship' in name:
                                    bucket_key = 'relationship'
                                elif 'out_converter' in name:
                                    bucket_key = 'out_converter'
                                
                                module_buckets[bucket_key]['total'] += 1
                                
                                if not p.requires_grad:
                                    encoder_params_frozen += 1
                                    module_buckets[bucket_key]['frozen'] += 1
                                if id(p) not in optimizer_param_ids:
                                    encoder_params_not_in_optimizer += 1
                                    module_buckets[bucket_key]['not_in_opt'] += 1
                                if p.grad is not None:
                                    encoder_params_with_grad += 1
                                    module_buckets[bucket_key]['with_grad'] += 1
                                    param_norm = p.grad.data.norm(2)  # L2 norm of this parameter's gradient tensor
                                    encoder_norm_squared += param_norm.item() ** 2  # Sum of squared norms
                            encoder_norm = encoder_norm_squared ** 0.5  # Global L2: sqrt(sum ||g_p||^2)
                            
                            # ENHANCED DIAGNOSTICS: Log detailed encoder gradient status
                            # Use train_encoder_now defined once per epoch (not recomputed)
                            should_log_encoder_diagnostics = (
                                (epoch_idx == 0 and batch_idx < 3) or  # First 3 batches
                                (batch_idx % 100 == 0) or  # Every 100 batches
                                (train_encoder_now and encoder_norm < 1e-6 and predictor_norm > 1e-6)  # When encoder is clearly dead in fine-tune mode
                            )
                            
                            if should_log_encoder_diagnostics:
                                    # Compute total global norm (encoder + predictor)
                                    total_norm_squared = encoder_norm_squared + predictor_norm_squared
                                    total_norm = total_norm_squared ** 0.5
                                    
                                    logger.info("=" * 80)
                                    logger.info(f"🔍 ENCODER GRADIENT DIAGNOSTICS (Epoch {epoch_idx}, Batch {batch_idx})")
                                    logger.info(f"   Mode: {'JOINT_FINE_TUNE' if train_encoder_now else 'SP_TRAINING_ONLY'}")
                                    logger.info("=" * 80)
                                    logger.info(f"   Encoder params: {encoder_params_total} total")
                                    logger.info(f"   Encoder params with grad: {encoder_params_with_grad}/{encoder_params_total} ({100*encoder_params_with_grad/encoder_params_total:.1f}%)")
                                    logger.info(f"   ||∇encoder||_global: {encoder_norm:.6e}")
                                    logger.info(f"   ||∇predictor||_global: {predictor_norm:.6e}")
                                    logger.info(f"   ||∇all||_global: {total_norm:.6e}")
                                    
                                    if train_encoder_now:
                                        # ====================================================================
                                        # FINE-TUNE MODE: Verify fine-tune invariants
                                        # ====================================================================
                                        
                                        # GRADIENT COVERAGE BY MODULE: Identify which components are missing grads
                                        logger.info("")
                                        logger.info(f"   📊 Gradient Coverage by Module:")
                                        for bucket_name in ['joint_encoder', 'column_encoder', 'relationship', 'out_converter', 'other']:
                                            bucket = module_buckets[bucket_name]
                                            if bucket['total'] > 0:
                                                coverage_pct = 100 * bucket['with_grad'] / bucket['total'] if bucket['total'] > 0 else 0.0
                                                status = "✅" if coverage_pct > 50 else "⚠️ " if coverage_pct > 0 else "❌"
                                                # Build message parts
                                                msg_parts = [f"      {status} {bucket_name:20s}: {bucket['with_grad']:4d}/{bucket['total']:4d} ({coverage_pct:5.1f}%) have grads"]
                                                if bucket['frozen'] > 0:
                                                    msg_parts.append(f" | {bucket['frozen']} frozen")
                                                if bucket['not_in_opt'] > 0:
                                                    msg_parts.append(f" | {bucket['not_in_opt']} not in optimizer")
                                                # Log as single message (logger.info doesn't support end parameter)
                                                logger.info("".join(msg_parts))
                                        
                                        # FINE-TUNE INVARIANT 1: any(p.requires_grad for p in encoder.parameters())
                                        if encoder_params_frozen == encoder_params_total:
                                            logger.error(f"   ❌ CRITICAL: ALL encoder params frozen (requires_grad=False)!")
                                            logger.error(f"      Fine-tune mode requires encoder params to be trainable!")
                                        elif encoder_params_frozen > 0:
                                            logger.error(f"   ❌ CRITICAL: {encoder_params_frozen}/{encoder_params_total} encoder params frozen (requires_grad=False)!")
                                            logger.error(f"      Fine-tune mode requires ALL encoder params to be trainable!")
                                        else:
                                            logger.info(f"   ✅ All encoder params have requires_grad=True")
                                        
                                        # FINE-TUNE INVARIANT 2: encoder.training == True
                                        if not self.embedding_space.encoder.training:
                                            logger.error(f"   ❌ CRITICAL: encoder.training = False in fine-tune mode!")
                                        else:
                                            logger.info(f"   ✅ encoder.training = True")
                                        
                                        # FINE-TUNE INVARIANT 3: encoder_param_ids ⊆ optimizer_param_ids
                                        encoder_params_in_optimizer = encoder_params_total - encoder_params_not_in_optimizer
                                        if encoder_params_not_in_optimizer > 0:
                                            logger.error(f"   ❌ CRITICAL: {encoder_params_not_in_optimizer}/{encoder_params_total} encoder params NOT in optimizer!")
                                            logger.error(f"      Fine-tune mode requires ALL encoder params in optimizer!")
                                        else:
                                            logger.info(f"   ✅ All {encoder_params_total} encoder params in optimizer")
                                        
                                        # FINE-TUNE INVARIANT 4: h.requires_grad == True (checked earlier, just log summary)
                                        # This is verified in the computation graph check above
                                        
                                        # FINE-TUNE INVARIANT 5: nonzero encoder grads (at least some coverage)
                                        if encoder_params_with_grad == 0:
                                            logger.error(f"   ❌ CRITICAL: Zero encoder params have gradients!")
                                            logger.error(f"      Possible causes:")
                                            logger.error(f"        1. Encoder output was detached (check for .detach() after encoder.encode())")
                                            logger.error(f"        2. torch.no_grad() context around encoder forward")
                                            logger.error(f"        3. Encoder not in computation graph (check loss.backward() path)")
                                        elif encoder_norm < 1e-6:
                                            logger.warning(f"   ⚠️  TINY GRADIENTS: Encoder grad norm {encoder_norm:.6e} is near zero!")
                                            logger.warning(f"      Encoder is effectively dead - gradients are 480× smaller than predictor")
                                            logger.warning(f"      Check if encoder output was detached or encoder is weakly coupled to loss")
                                        else:
                                            logger.info(f"   ✅ Encoder has gradients (norm={encoder_norm:.6e})")
                                        
                                        # Interpretation: warn if core encoder blocks are missing grads
                                        joint_coverage = 100 * module_buckets['joint_encoder']['with_grad'] / module_buckets['joint_encoder']['total'] if module_buckets['joint_encoder']['total'] > 0 else 0.0
                                        if joint_coverage < 50 and module_buckets['joint_encoder']['total'] > 0:
                                            logger.warning(f"   ⚠️  WARNING: Joint encoder has low gradient coverage ({joint_coverage:.1f}%)!")
                                            logger.warning(f"      Core encoder blocks should have gradients - check for detachment/freezing")
                                        elif joint_coverage >= 50:
                                            logger.info(f"   ✅ Joint encoder has good gradient coverage ({joint_coverage:.1f}%)")
                                    
                                    else:
                                        # ====================================================================
                                        # FROZEN MODE: Verify frozen invariants
                                        # ====================================================================
                                        
                                        # FROZEN INVARIANT 1: all(not p.requires_grad for p in encoder.parameters())
                                        if encoder_params_frozen == encoder_params_total:
                                            logger.info(f"   ✅ All {encoder_params_total} encoder params frozen (requires_grad=False, as expected)")
                                        else:
                                            logger.error(f"   ❌ CRITICAL: {encoder_params_total - encoder_params_frozen}/{encoder_params_total} encoder params NOT frozen!")
                                            logger.error(f"      Frozen mode requires ALL encoder params to have requires_grad=False!")
                                        
                                        # FROZEN INVARIANT 2: encoder.training == False
                                        if not self.embedding_space.encoder.training:
                                            logger.info(f"   ✅ encoder.training = False (eval mode, as expected)")
                                        else:
                                            logger.error(f"   ❌ CRITICAL: encoder.training = True in frozen mode!")
                                        
                                        # FROZEN INVARIANT 3: encoder_param_ids ∩ optimizer_param_ids == ∅ (optional)
                                        if encoder_params_not_in_optimizer == encoder_params_total:
                                            logger.info(f"   ✅ All {encoder_params_total} encoder params NOT in optimizer (as expected)")
                                        elif encoder_params_not_in_optimizer > 0:
                                            logger.warning(f"   ⚠️  {encoder_params_total - encoder_params_not_in_optimizer}/{encoder_params_total} encoder params in optimizer (should be 0 in frozen mode)")
                                        else:
                                            logger.error(f"   ❌ CRITICAL: All encoder params in optimizer in frozen mode!")
                                        
                                        # FROZEN INVARIANT 4: predictor_param_ids ⊆ optimizer_param_ids (must)
                                        if predictor_params_in_optimizer == predictor_params_total:
                                            logger.info(f"   ✅ All {predictor_params_total} predictor params in optimizer")
                                        else:
                                            logger.error(f"   ❌ CRITICAL: {predictor_params_total - predictor_params_in_optimizer}/{predictor_params_total} predictor params NOT in optimizer!")
                                            logger.error(f"      Predictor params MUST be in optimizer!")
                                        
                                        # Summary: Encoder frozen OK
                                        logger.info(f"   ✅ Encoder frozen: OK (0% grad coverage expected)")
                                    
                                    logger.info("=" * 80)
                            
                            # Compute Gradient Flow Ratio: R(t) = ||∇_ES||_global / ||∇_Predictor||_global
                            # CRITICAL: Uses GLOBAL L2 norms, not mean-of-norms
                            # Mean-of-norms would be misleading if one module has many more parameters
                            # This diagnostic tells us if encoder and predictor are learning at balanced rates
                            # R → 0: encoder dead (not learning)
                            # R explodes: encoder dominating (instability/forgetting)
                            # R stabilizes: healthy balance
                            # Only compute in fine-tune mode (train_encoder_now=True)
                            if train_encoder_now:
                                if predictor_norm > 1e-10 and encoder_norm > 1e-10:  # Avoid division by zero
                                    gradient_flow_ratio = encoder_norm / predictor_norm
                                    # Log ratio: log R = log(||∇_ES||) - log(||∇_Predictor||)
                                    # This is symmetric and easier to threshold:
                                    #   log R = 0: balanced
                                    #   log R > 0: encoder dominating
                                    #   log R < 0: predictor dominating
                                    #   |log R| > 2.3: more than 10× difference
                                    gradient_flow_log_ratio = math.log(encoder_norm) - math.log(predictor_norm)
                                elif encoder_norm > 1e-10:
                                    gradient_flow_ratio = float('inf')
                                    gradient_flow_log_ratio = float('inf')
                                else:
                                    gradient_flow_ratio = 0.0
                                    gradient_flow_log_ratio = float('-inf')
                                
                                # AUTOMATIC LEARNING RATE CONTROLLER (based on gradient flow imbalance)
                                # Uses EMA(logR) with hysteresis and cooldown to avoid oscillation
                                # Goal: bring log R closer to 0 (balanced learning)
                                
                                # Initialize EMA and controller state
                                if not hasattr(self, '_ema_log_r'):
                                    self._ema_log_r = None
                                if not hasattr(self, '_lr_controller_state'):
                                    self._lr_controller_state = {
                                        'in_starved_mode': False,
                                        'last_adjustment_batch': -1,
                                        'cooldown_steps': 400  # 400 batches cooldown
                                    }
                                
                                # Update EMA(logR)
                                if gradient_flow_log_ratio is not None and not (math.isinf(gradient_flow_log_ratio) or math.isnan(gradient_flow_log_ratio)):
                                    if self._ema_log_r is None:
                                        self._ema_log_r = gradient_flow_log_ratio
                                    else:
                                        self._ema_log_r = 0.9 * self._ema_log_r + 0.1 * gradient_flow_log_ratio
                                
                                # Controller logic with hysteresis and cooldown
                                should_adjust_lr = (batch_idx % 100 == 0) and (epoch_idx > 0)  # Don't adjust on first epoch
                                if should_adjust_lr and self._ema_log_r is not None:
                                        state = self._lr_controller_state
                                        batches_since_adjustment = batch_idx - state['last_adjustment_batch']
                                        
                                        # Hysteresis: enter starved mode at logR < -2.3, exit at logR > -1.6 (≈ 5×)
                                        if self._ema_log_r < -2.3:  # Encoder is dead (predictor > 10× encoder)
                                            state['in_starved_mode'] = True
                                        elif self._ema_log_r > -1.6:  # Balanced (within 5×)
                                            state['in_starved_mode'] = False
                                        
                                        # Check if we should adjust (in starved mode + cooldown passed)
                                        should_adjust = (state['in_starved_mode'] and 
                                                       batches_since_adjustment >= state['cooldown_steps'])
                                        
                                        # Additional guard: don't adjust if probability spread is collapsed
                                        # Get prob_std from earlier in the batch (if available)
                                        prob_std = getattr(self, '_last_prob_std', None)
                                        if prob_std is not None and prob_std < 0.02:
                                            should_adjust = False
                                            if state['in_starved_mode']:
                                                logger.warning(f"🔧 LR ADJUST BLOCKED: prob_std={prob_std:.6f} < 0.02 (output collapsed)")
                                                logger.warning(f"   Focus on fixing collapse first (calibration/logits→probs/label leakage)")
                                        
                                        if should_adjust:  # Encoder is starved and cooldown passed
                                            # Increase encoder LR or decrease predictor LR to balance
                                            # Check if we have separate param groups (separate LRs enabled)
                                            if len(optimizer.param_groups) >= 2:
                                                # Identify which group is encoder vs predictor by checking param IDs
                                                encoder_param_ids = {id(p) for p in self.embedding_space.encoder.parameters()}
                                                predictor_param_ids = {id(p) for p in self.predictor.parameters()}
                                                
                                                encoder_group = None
                                                predictor_group = None
                                                for group in optimizer.param_groups:
                                                    group_param_ids = {id(p) for p in group['params']}
                                                    if group_param_ids.intersection(encoder_param_ids):
                                                        encoder_group = group
                                                    elif group_param_ids.intersection(predictor_param_ids):
                                                        predictor_group = group
                                                
                                                if encoder_group is not None and predictor_group is not None:
                                                    # Store initial LRs if not already stored
                                                    if not hasattr(self, '_initial_encoder_lr'):
                                                        self._initial_encoder_lr = encoder_group['lr']
                                                        self._initial_predictor_lr = predictor_group['lr']
                                                    
                                                    # Adjust: multiply encoder LR by 2 (cap at 10× initial AND absolute cap)
                                                    current_encoder_lr = encoder_group['lr']
                                                    current_predictor_lr = predictor_group['lr']
                                                    max_encoder_lr_multiplier = self._initial_encoder_lr * 10.0
                                                    max_encoder_lr_absolute = 2e-3  # Absolute cap to prevent destabilization
                                                    max_encoder_lr = min(max_encoder_lr_multiplier, max_encoder_lr_absolute)
                                                    min_predictor_lr = self._initial_predictor_lr * 0.1
                                                    
                                                    # Strategy: increase encoder LR (more aggressive)
                                                    new_encoder_lr = min(current_encoder_lr * 2.0, max_encoder_lr)
                                                    
                                                    # Only adjust if we haven't hit the cap
                                                    if new_encoder_lr > current_encoder_lr:
                                                        encoder_group['lr'] = new_encoder_lr
                                                        state['last_adjustment_batch'] = batch_idx
                                                        logger.warning(f"🔧 AUTO-LR ADJUST [e={epoch_idx},b={batch_idx}]: EMA(log R) = {self._ema_log_r:.2f} (encoder starved)")
                                                        logger.warning(f"   Increased encoder LR: {current_encoder_lr:.6e} → {new_encoder_lr:.6e} ({new_encoder_lr/current_encoder_lr:.2f}×)")
                                                        logger.warning(f"   Caps: multiplier={max_encoder_lr_multiplier:.6e}, absolute={max_encoder_lr_absolute:.6e}")
                                                        logger.warning(f"   Goal: bring log R closer to 0 (balanced learning)")
                                                        logger.warning(f"   Cooldown: {state['cooldown_steps']} batches before next adjustment")
                                                        
                                                        # Add event to timeline: Auto LR adjustment
                                                        if hasattr(self, '_training_timeline'):
                                                            lr_adjust_event = {
                                                                "epoch": epoch_idx,
                                                                "event_type": "lr_adjustment",
                                                                "adjustment_type": "auto_encoder_increase",
                                                                "component": "encoder",
                                                                "old_lr": float(current_encoder_lr),
                                                                "new_lr": float(new_encoder_lr),
                                                                "multiplier": float(new_encoder_lr / current_encoder_lr),
                                                                "ema_log_r": float(self._ema_log_r),
                                                                "reason": f"Encoder starved (log R = {self._ema_log_r:.2f}) - increased encoder LR to balance learning",
                                                                "batch_idx": batch_idx,
                                                                "time_now": time.time(),
                                                            }
                                                            self._training_timeline.append(lr_adjust_event)
                                                    elif current_predictor_lr > min_predictor_lr:
                                                        # If encoder LR is capped, decrease predictor LR instead
                                                        new_predictor_lr = max(current_predictor_lr * 0.5, min_predictor_lr)
                                                        predictor_group['lr'] = new_predictor_lr
                                                        state['last_adjustment_batch'] = batch_idx
                                                        logger.warning(f"🔧 AUTO-LR ADJUST [e={epoch_idx},b={batch_idx}]: EMA(log R) = {self._ema_log_r:.2f} (encoder starved, encoder LR capped)")
                                                        logger.warning(f"   Decreased predictor LR: {current_predictor_lr:.6e} → {new_predictor_lr:.6e} ({new_predictor_lr/current_predictor_lr:.2f}×)")
                                                        logger.warning(f"   Goal: bring log R closer to 0 (balanced learning)")
                                                        logger.warning(f"   Cooldown: {state['cooldown_steps']} batches before next adjustment")
                                                        
                                                        # Add event to timeline: Auto LR adjustment
                                                        if hasattr(self, '_training_timeline'):
                                                            lr_adjust_event = {
                                                                "epoch": epoch_idx,
                                                                "event_type": "lr_adjustment",
                                                                "adjustment_type": "auto_predictor_decrease",
                                                                "component": "predictor",
                                                                "old_lr": float(current_predictor_lr),
                                                                "new_lr": float(new_predictor_lr),
                                                                "multiplier": float(new_predictor_lr / current_predictor_lr),
                                                                "ema_log_r": float(self._ema_log_r),
                                                                "reason": f"Encoder starved but encoder LR capped - decreased predictor LR to balance learning",
                                                                "batch_idx": batch_idx,
                                                                "time_now": time.time(),
                                                            }
                                                            self._training_timeline.append(lr_adjust_event)
                                                    else:
                                                        logger.warning(f"🔧 AUTO-LR ADJUST BLOCKED [e={epoch_idx},b={batch_idx}]: Both LRs at limits")
                                                        logger.warning(f"   Encoder LR capped at {current_encoder_lr:.6e}, Predictor LR at {current_predictor_lr:.6e}")
                                                        logger.warning(f"   EMA(log R) = {self._ema_log_r:.2f} - may need manual intervention")
                            
                            # Total norm for global clipping
                            # Use train_encoder_now defined once per epoch (not recomputed)
                            total_norm_squared = predictor_norm_squared
                            if train_encoder_now:
                                total_norm_squared += encoder_norm ** 2
                            unclipped_norm = total_norm_squared ** 0.5
                        
                            # GRADIENT CLIPPING: Prevent extreme gradient explosions while allowing healthy training
                            # Set to 8.0 to allow natural gradient variability (previous 2.0 was too aggressive)
                            # Log when gradients exceed old threshold (2.0) to monitor if we're being too permissive
                            max_grad_norm = 8.0
                            old_threshold = 2.0  # Previous overly-aggressive value
                            
                            # Use stored training params (set during optimizer creation)
                            # This ensures we clip the same parameters that are being optimized
                            total_norm = torch.nn.utils.clip_grad_norm_(self._training_params, max_grad_norm)
                            
                            # Check if we would have clipped at the old aggressive threshold
                            would_have_clipped_at_2 = unclipped_norm > old_threshold
                            if would_have_clipped_at_2 and batch_idx % 10 == 0:  # Log every 10 batches to avoid spam
                                logger.warning(f"⚠️  [epoch={epoch_idx}, batch={batch_idx}] Gradient norm {unclipped_norm:.2f} exceeds old threshold {old_threshold:.1f} (would have been clipped), now using {max_grad_norm:.1f}")
                        
                            # Log gradient norms every 100 batches to diagnose learning issues
                            # Also check on first batch of each epoch if we've been seeing dead gradients
                            should_check_gradients = (batch_idx % 100 == 0) or (batch_idx == 0 and len(self.dead_gradient_epochs) > 0)
                            
                            if should_check_gradients:
                                current_lr = get_lr()
                                # get_lr() returns a list if scheduler is used, or a float otherwise
                                lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
                                clipped_ratio = (unclipped_norm / max_grad_norm) if unclipped_norm > max_grad_norm else 1.0
                                logger.info(f"📊 Gradients: unclipped={unclipped_norm:.6f}, clipped={total_norm:.6f}, ratio={clipped_ratio:.2f}x, lr={lr_value:.6e}")
                                
                                # Store for structured logging
                                # Use train_encoder_now defined once per epoch (not recomputed)
                                progress_dict["gradient_unclipped"] = unclipped_norm
                                progress_dict["gradient_clipped"] = total_norm
                                progress_dict["predictor_grad_norm"] = predictor_norm
                                if train_encoder_now:
                                    progress_dict["encoder_grad_norm"] = encoder_norm
                                    progress_dict["gradient_flow_ratio"] = gradient_flow_ratio
                                    progress_dict["gradient_flow_log_ratio"] = gradient_flow_log_ratio
                            
                            # Log LR at start of each epoch to track scheduler
                            if batch_idx == 0:
                                current_lr = get_lr()
                                lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
                                if scheduler is not None:
                                    logger.info(f"📈 LR Schedule : LR={lr_value:.6e}")
                                else:
                                    logger.info(f"📈 LR Schedule : No scheduler (LR fixed at {lr_value:.6e})")
                            
                                # DEAD GRADIENT DETECTION & RESTART MECHANISM
                                # This will raise FeatrixRestartTrainingException if conditions met
                                
                                # ENHANCED DEBUGGING: If gradients are dead, diagnose why
                                if unclipped_norm < self.dead_gradient_threshold:
                                    self._diagnose_dead_gradients(
                                        unclipped_norm=unclipped_norm,
                                        loss=loss,
                                        out=out,
                                        targets=targets,
                                        fine_tune=fine_tune,
                                        epoch_idx=epoch_idx,
                                        batch_idx=batch_idx
                                    )
                                
                                self.check_for_dead_gradients_and_raise(
                                    unclipped_norm=unclipped_norm,
                                    epoch_idx=epoch_idx,
                                    current_lr=lr_value
                                )
                        
                            # CRITICAL FIX: Detect NaN/Inf gradients BEFORE they corrupt parameters
                            # NOW ABORTS instead of continuing with corrupted state
                            if torch.isnan(total_norm) or torch.isinf(total_norm):
                                # This will raise RuntimeError and abort training
                                self._handle_nan_gradients(
                                    total_norm=total_norm,
                                    consecutive_nan_batches=consecutive_nan_batches,
                                    max_consecutive_nan_batches=max_consecutive_nan_batches,
                                    loss=loss,
                                    epoch_idx=epoch_idx,
                                    batch_idx=batch_idx,
                                    job_id=job_id,
                                    lr_value=lr_value,
                                    optimizer=optimizer
                                )
                                # Code never reaches here - exception raised above
                            else:
                                # Reset counter on successful batch
                                consecutive_nan_batches = 0
                        
                            # Store parameters before optimizer step to compute parameter update norm
                            params_before = {}
                            for p in self._training_params:
                                if p.requires_grad:
                                    params_before[id(p)] = p.data.clone()
                            
                            self._step_optimizer_and_scheduler(optimizer, scheduler)
                            
                            # Compute parameter update norm (||w_after - w_before||)
                            param_update_norm = 0.0
                            if params_before:
                                param_update_norm_squared = 0.0
                                for p in self._training_params:
                                    if p.requires_grad and id(p) in params_before:
                                        param_diff = p.data - params_before[id(p)]
                                        param_update_norm_squared += param_diff.norm(2).item() ** 2
                                param_update_norm = param_update_norm_squared ** 0.5
                            
                            # Store for epoch-level logging with validation loss
                            if not hasattr(self, '_epoch_grad_norms'):
                                self._epoch_grad_norms = []
                                self._epoch_param_update_norms = []
                            self._epoch_grad_norms.append(float(unclipped_norm))
                            self._epoch_param_update_norms.append(param_update_norm)
                            
                            # Add to progress dict for logging
                            progress_dict["gradient_norm"] = float(unclipped_norm)
                            progress_dict["param_update_norm"] = param_update_norm
                            # Store gradient flow ratio for epoch-level tracking
                            if fine_tune and gradient_flow_ratio is not None:
                                if not hasattr(self, '_epoch_gradient_flow_ratios'):
                                    self._epoch_gradient_flow_ratios = []
                                    self._epoch_gradient_flow_log_ratios = []
                                self._epoch_gradient_flow_ratios.append(gradient_flow_ratio)
                                if gradient_flow_log_ratio is not None and not (math.isinf(gradient_flow_log_ratio) or math.isnan(gradient_flow_log_ratio)):
                                    self._epoch_gradient_flow_log_ratios.append(gradient_flow_log_ratio)
    
                            self._update_progress_after_batch(progress_dict, training_info_entry, loss, get_lr)
    
                            # 
                            # After each batch, run validation.
                            # 
                            val_loss = self.compute_val_loss(loss_fn)
                            progress_dict["validation_loss"] = val_loss
                            training_info_entry['validation_loss'] = progress_dict["validation_loss"]
    
                                # Removed: in-batch metrics calculation (was every 5 minutes)
                                # Now only calculate metrics at end of each epoch for consistency
                                # print(progress_dict.model_dump())
    
                            # TODO: dump the validation loss to metadata in a way that preserves
                            # the history for all training epochs.
    
                            # Update progress without recalculating metrics (done once per epoch now)
                            # Call callback even if progress_counter is 0 (first batch) to show training has started
                            if print_callback is not None:
                                print_callback(progress_dict)
                            
                            progress_dict["progress_counter"] += 1
                        # ====================================================================
                        # END: BATCH FOR LOOP (enumerate(train_dataloader))
                        # ====================================================================
                    
                        # Check if FINISH flag or early stopping caused early break from batch loop or metrics
                        if progress_dict.get("interrupted"):
                            interrupted_reason = progress_dict.get("interrupted")
                            logger.info(f"⏹️  Breaking epoch loop due to: {interrupted_reason}")
                            break
                        
                        # Add epoch-level gradient and parameter update norms to progress dict for logging
                        if hasattr(self, '_epoch_grad_norms') and self._epoch_grad_norms:
                            avg_grad_norm = sum(self._epoch_grad_norms) / len(self._epoch_grad_norms)
                            progress_dict["avg_gradient_norm"] = avg_grad_norm
                        if hasattr(self, '_epoch_param_update_norms') and self._epoch_param_update_norms:
                            avg_param_update_norm = sum(self._epoch_param_update_norms) / len(self._epoch_param_update_norms)
                            progress_dict["avg_param_update_norm"] = avg_param_update_norm
                        
                        # Add epoch-level gradient flow ratio (R = ||∇_ES|| / ||∇_Predictor||)
                        if fine_tune and hasattr(self, '_epoch_gradient_flow_ratios') and self._epoch_gradient_flow_ratios:
                            avg_gradient_flow_ratio = sum(self._epoch_gradient_flow_ratios) / len(self._epoch_gradient_flow_ratios)
                            progress_dict["avg_gradient_flow_ratio"] = avg_gradient_flow_ratio
                            # Also store min/max for diagnostic purposes
                            progress_dict["min_gradient_flow_ratio"] = min(self._epoch_gradient_flow_ratios)
                            progress_dict["max_gradient_flow_ratio"] = max(self._epoch_gradient_flow_ratios)
                            
                            # Log ratio (log R = log(||∇_ES||) - log(||∇_Predictor||)) - symmetric and easier to threshold
                            if hasattr(self, '_epoch_gradient_flow_log_ratios') and self._epoch_gradient_flow_log_ratios:
                                avg_gradient_flow_log_ratio = sum(self._epoch_gradient_flow_log_ratios) / len(self._epoch_gradient_flow_log_ratios)
                                progress_dict["avg_gradient_flow_log_ratio"] = avg_gradient_flow_log_ratio
                                progress_dict["min_gradient_flow_log_ratio"] = min(self._epoch_gradient_flow_log_ratios)
                                progress_dict["max_gradient_flow_log_ratio"] = max(self._epoch_gradient_flow_log_ratios)
                        
                        # Reset epoch-level tracking for next epoch
                        if hasattr(self, '_epoch_grad_norms'):
                            self._epoch_grad_norms = []
                        if hasattr(self, '_epoch_param_update_norms'):
                            self._epoch_param_update_norms = []
                        if hasattr(self, '_epoch_gradient_flow_ratios'):
                            self._epoch_gradient_flow_ratios = []
                        if hasattr(self, '_epoch_gradient_flow_log_ratios'):
                            self._epoch_gradient_flow_log_ratios = []
        
                        # ALWAYS compute validation metrics at least once per epoch
                        # This is critical for detecting overfitting and monitoring training health
                        # We compute the full metrics every epoch, but may log them less frequently
                        # to reduce noise in progress callbacks
                    
                        # ASSERT: Before calling metrics, we should still be in training mode
                        # (The metrics function will temporarily switch to eval mode)
                        assert self.predictor.training == True, f"❌ TRAINING BUG: predictor should be in train mode before metrics but training={self.predictor.training}"
                    
                        try:
                            self.training_metrics = self.compute_classification_metrics(
                                val_queries, val_targets, val_pos_label, epoch_idx=epoch_idx, n_epochs=n_epochs
                            )
                        except (TrainingFailureException, EarlyStoppingException):
                            # Re-raise training failure/early stopping exceptions - these should stop training immediately
                            raise
                        except Exception:
                            logger.exception("error with compute_classification_metrics")
                        _log_gpu_memory(f"AFTER COMPUTE_CLASSIFICATION_METRICS (epoch {epoch_idx})", log_level=logging.DEBUG)
                    
                        # Check if early stopping was triggered in compute_classification_metrics
                        # (it sets instance variables instead of raising immediately to allow best model save)
                        if hasattr(self, '_training_interrupted') and self._training_interrupted:
                            progress_dict["interrupted"] = self._training_interrupted
                            progress_dict["early_stop_reason"] = getattr(self, '_early_stop_reason', 'Early stopping triggered')
                            logger.info(f"⏹️  Early stopping detected: {progress_dict['early_stop_reason']}")
                            
                            # Add event to timeline: Early stopping
                            if hasattr(self, '_training_timeline'):
                                early_stop_event = {
                                    "epoch": epoch_idx,
                                    "event_type": "early_stopping",
                                    "reason": progress_dict["early_stop_reason"],
                                    "total_epochs": n_epochs,
                                    "epochs_completed": epoch_idx + 1,
                                    "time_now": time.time(),
                                }
                                self._training_timeline.append(early_stop_event)
                        
                        # Check for resolved warnings at end of epoch
                        # DEAD_GRADIENTS is checked during batch loop, so if we got here without dead gradients
                        # and it was active before, it's resolved
                        if hasattr(self, '_active_warnings') and "DEAD_GRADIENTS" in self._active_warnings:
                            # If dead_gradient_epochs is empty, gradients recovered
                            if not self.dead_gradient_epochs:
                                # Already tracked in check_for_dead_gradients_and_raise, but double-check
                                pass  # Already handled in the check method
                        
                        # Save timeline every epoch (for real-time plot updates)
                        _log_gpu_memory(f"BEFORE SAVE_TRAINING_TIMELINE (epoch {epoch_idx})", log_level=logging.DEBUG)
                        self.save_training_timeline(
                            output_dir=self._output_dir,
                            current_epoch=epoch_idx,
                            total_epochs=n_epochs
                        )
                        _log_gpu_memory(f"AFTER SAVE_TRAINING_TIMELINE (epoch {epoch_idx})", log_level=logging.DEBUG)
                        
                        # ASSERT: After metrics, we should be back in training mode
                        assert self.predictor.training == True, f"❌ TRAINING BUG: predictor should be back in train mode after metrics but training={self.predictor.training}"
                        logger.debug(f"{log_prefix}✓ Training loop: Models correctly restored to TRAIN mode after metrics")
                        
                        progress_dict["metrics"] = self.training_metrics
        
                        _log_gpu_memory(f"BEFORE COPY.DEEPCOPY METRICS (epoch {epoch_idx})", log_level=logging.INFO)
                        training_info_entry['metrics'] = copy.deepcopy(progress_dict["metrics"])
                        _log_gpu_memory(f"AFTER COPY.DEEPCOPY METRICS (epoch {epoch_idx})", log_level=logging.INFO)
                        
                        # Record metrics in LRTimeline for tracking and visualization
                        if scheduler is not None and isinstance(scheduler, LRTimeline):
                            # Get train and val loss
                            train_loss_val = training_info_entry.get('loss')
                            val_loss_val = training_info_entry.get('validation_loss')
                            
                            if train_loss_val is not None and val_loss_val is not None:
                                scheduler.record_loss(epoch_idx, train_loss=train_loss_val, val_loss=val_loss_val)
                            
                            # Record AUC if available
                            if progress_dict.get("metrics") and progress_dict["metrics"].get("auc") is not None:
                                auc_val = progress_dict["metrics"]["auc"]
                                scheduler.record_auc(epoch_idx, auc_val)
                            
                            # Record PR-AUC if available as a custom metric
                            if progress_dict.get("metrics") and progress_dict["metrics"].get("pr_auc") is not None:
                                pr_auc_val = progress_dict["metrics"]["pr_auc"]
                                scheduler.record_metric(epoch_idx, "pr_auc", pr_auc_val)
                        
                        # Add comprehensive epoch snapshot to timeline for this epoch (include ALL metrics)
                        if hasattr(self, '_training_timeline'):
                            epoch_entry = {
                                "epoch": epoch_idx,
                                "event_type": "epoch_summary",
                                "hyperparameters": training_info_entry['hyperparameters'].copy(),
                                "train_loss": training_info_entry.get('loss'),
                                "validation_loss": training_info_entry.get('validation_loss'),
                                "metrics": copy.deepcopy(progress_dict.get("metrics", {})),  # Include ALL calculated metrics
                                "learning_rate": training_info_entry['hyperparameters'].get('learning_rate'),
                                "time_now": progress_dict.get("time_now"),
                            }
                            # Add any other progress_dict fields that might be useful
                            if "lr" in progress_dict:
                                epoch_entry["lr"] = progress_dict["lr"]
                            
                            # Add ES LR if available (from scheduler or optimizer)
                            if scheduler is not None and isinstance(scheduler, LRTimeline) and scheduler.mode == 'sp_plus_es':
                                es_lr = scheduler.get_es_lr(epoch_idx)
                                if es_lr is not None and es_lr > 0:
                                    epoch_entry["es_learning_rate"] = float(es_lr)
                            elif fine_tune and len(optimizer.param_groups) >= 2:
                                # Try to get ES LR from optimizer param groups
                                encoder_param_ids = {id(p) for p in self.embedding_space.encoder.parameters()}
                                for group in optimizer.param_groups:
                                    group_param_ids = {id(p) for p in group['params']}
                                    if group_param_ids.intersection(encoder_param_ids):
                                        # This is the ES group
                                        if group['lr'] > 0:
                                            epoch_entry["es_learning_rate"] = float(group['lr'])
                                        break
                            # Add gradient flow ratio if fine-tuning (R = ||∇_ES|| / ||∇_Predictor||)
                            if fine_tune and "avg_gradient_flow_ratio" in progress_dict:
                                epoch_entry["gradient_flow_ratio"] = progress_dict["avg_gradient_flow_ratio"]
                                epoch_entry["min_gradient_flow_ratio"] = progress_dict.get("min_gradient_flow_ratio")
                                epoch_entry["max_gradient_flow_ratio"] = progress_dict.get("max_gradient_flow_ratio")
                                # Also store log ratio (symmetric, easier to threshold)
                                if "avg_gradient_flow_log_ratio" in progress_dict:
                                    epoch_entry["gradient_flow_log_ratio"] = progress_dict["avg_gradient_flow_log_ratio"]
                                    epoch_entry["min_gradient_flow_log_ratio"] = progress_dict.get("min_gradient_flow_log_ratio")
                                    epoch_entry["max_gradient_flow_log_ratio"] = progress_dict.get("max_gradient_flow_log_ratio")
                            self._training_timeline.append(epoch_entry)
        
                        self.training_info.append(training_info_entry)

                        # ====================================================================
                        # DIAGNOSTIC: Track AUC patterns for phased freezing diagnostics
                        # ====================================================================
                        current_auc = -1.0
                        if progress_dict.get("metrics") and progress_dict["metrics"].get("auc") is not None:
                            current_auc = progress_dict["metrics"]["auc"]
                            
                            # Track initial AUC (first valid AUC value)
                            if self._initial_auc is None and current_auc >= 0:
                                self._initial_auc = current_auc
                                logger.info(f"{log_prefix}📊 Initial AUC: {current_auc:.4f} (will track improvements from this baseline)")
                            
                            # Track if AUC ever improved from initial
                            if self._initial_auc is not None and current_auc > self._initial_auc + 0.001:  # Small threshold to avoid noise
                                if not self._auc_ever_improved:
                                    self._auc_ever_improved = True
                                    logger.info(f"{log_prefix}✅ AUC improved from initial {self._initial_auc:.4f} to {current_auc:.4f}")
                            
                            # Track best AUC during warmup period
                            if freeze_warmup_epochs > 0 and epoch_idx < freeze_warmup_epochs:
                                if current_auc > self._best_auc_during_warmup:
                                    self._best_auc_during_warmup = current_auc
                                    self._warmup_best_auc_epoch = epoch_idx
                            
                            # DIAGNOSTIC 1: Check if AUC degrades after unfreezing
                            if freeze_warmup_epochs > 0 and epoch_idx >= freeze_warmup_epochs:
                                # Check degradation after unfreezing (allow 2 epochs for adjustment)
                                epochs_since_unfreeze = epoch_idx - freeze_warmup_epochs
                                if epochs_since_unfreeze >= 2:  # Give it 2 epochs to stabilize
                                    if self._best_auc_during_warmup >= 0 and current_auc < self._best_auc_during_warmup - 0.01:
                                        # Significant degradation detected (>0.01 drop)
                                        degradation = self._best_auc_during_warmup - current_auc
                                        logger.warning("")
                                        logger.warning("=" * 80)
                                        logger.warning("⚠️  DIAGNOSTIC: AUC DEGRADATION AFTER UNFREEZING DETECTED")
                                        logger.warning("=" * 80)
                                        logger.warning(f"   Pattern: AUC improved during warmup (best: {self._best_auc_during_warmup:.4f} @ epoch {self._warmup_best_auc_epoch + 1})")
                                        logger.warning(f"            but degraded after unfreezing (current: {current_auc:.4f}, drop: {degradation:.4f})")
                                        logger.warning(f"   Epochs since unfreeze: {epochs_since_unfreeze}")
                                        logger.warning("")
                                        logger.warning("   🔧 RECOMMENDED ACTIONS:")
                                        current_encoder_lr = getattr(self, '_unfreeze_encoder_lr', optimizer_params.get("lr", 1e-3))
                                        logger.warning("   1. Reduce encoder learning rate (current: {:.6e})".format(current_encoder_lr))
                                        logger.warning("      → Try 2-5× lower LR (e.g., {:.6e})".format(current_encoder_lr / 3))
                                        logger.warning("   2. Unfreeze later (increase warmup epochs)")
                                        logger.warning("      → Current warmup: {} epochs, try {} epochs".format(freeze_warmup_epochs, int(freeze_warmup_epochs * 1.5)))
                                        logger.warning("   3. Check gradient flow ratio - encoder gradients may be too large")
                                        logger.warning("=" * 80)
                                        logger.warning("")
                            
                            # DIAGNOSTIC 2: Check if nothing improves at all
                            # Check this after reasonable number of epochs (at least 10 or 20% of total)
                            min_epochs_for_diagnosis = max(10, int(n_epochs * 0.2))
                            if epoch_idx >= min_epochs_for_diagnosis and not self._auc_ever_improved:
                                if self._initial_auc is not None and current_auc <= self._initial_auc + 0.001:
                                    logger.warning("")
                                    logger.warning("=" * 80)
                                    logger.warning("⚠️  DIAGNOSTIC: NO IMPROVEMENT DETECTED")
                                    logger.warning("=" * 80)
                                    logger.warning(f"   Pattern: AUC has not improved from initial value ({self._initial_auc:.4f})")
                                    logger.warning(f"            Current AUC: {current_auc:.4f} (epoch {epoch_idx + 1}/{n_epochs})")
                                    logger.warning("")
                                    logger.warning("   🔧 RECOMMENDED ACTIONS:")
                                    if freeze_warmup_epochs > 0:
                                        logger.warning("   1. Unfreeze encoder earlier (reduce warmup period)")
                                        logger.warning("      → Current warmup: {} epochs, try {} epochs".format(freeze_warmup_epochs, max(1, freeze_warmup_epochs - 2)))
                                        logger.warning("   2. Predictor may be underpowered - try deeper/wider architecture")
                                    else:
                                        logger.warning("   1. Predictor may be underpowered - try deeper/wider architecture")
                                        logger.warning("   2. Check if embedding space quality is sufficient")
                                        logger.warning("   3. Consider enabling fine-tuning if disabled")
                                    logger.warning("   4. Check learning rate - may be too high (causing instability) or too low (no learning)")
                                    logger.warning("=" * 80)
                                    logger.warning("")
                        
                        # 🎯 CHECKPOINT: Save best model after epoch 3
                        current_val_loss = progress_dict.get("validation_loss", float('inf'))
                        current_pr_auc = -1.0
                        if progress_dict.get("metrics") and progress_dict["metrics"].get("pr_auc") is not None:
                            current_pr_auc = progress_dict["metrics"]["pr_auc"]
                        
                        # Get current loss and metrics for logging
                        current_train_loss = progress_dict.get("current_loss", 0)
                        current_metrics = progress_dict.get("metrics", {})
                        
                        # Determine if this is a new best epoch based on selection metric
                        is_new_best = False
                        # Track best model from epoch 3 onwards (but save checkpoint from epoch 20)
                        if epoch_idx >= 3:
                            # Update best model tracking based on current metrics
                            (is_new_best, best_auc, best_auc_epoch, best_pr_auc, best_pr_auc_epoch,
                             best_val_loss, best_epoch, best_roc_auc_model_state, 
                             best_roc_auc_embedding_space_state, best_pr_auc_model_state,
                             best_pr_auc_embedding_space_state) = self._update_best_model_tracking(
                                epoch_idx=epoch_idx,
                                use_auc_for_best_epoch=use_auc_for_best_epoch,
                                current_auc=current_auc,
                                current_pr_auc=current_pr_auc,
                                current_val_loss=current_val_loss,
                                progress_dict=progress_dict,
                                best_auc=best_auc,
                                best_auc_epoch=best_auc_epoch,
                                best_pr_auc=best_pr_auc,
                                best_pr_auc_epoch=best_pr_auc_epoch,
                                best_val_loss=best_val_loss,
                                best_epoch=best_epoch,
                                best_roc_auc_model_state=best_roc_auc_model_state,
                                best_roc_auc_embedding_space_state=best_roc_auc_embedding_space_state,
                                best_pr_auc_model_state=best_pr_auc_model_state,
                                best_pr_auc_embedding_space_state=best_pr_auc_embedding_space_state,
                                log_prefix=log_prefix
                            )
                        
                        # ═══════════════════════════════════════════════════════════════
                        # STRUCTURED EPOCH LOGGING
                        # ═══════════════════════════════════════════════════════════════
                        try:
                            # Add current epoch to tracker BEFORE computing deltas
                            metrics_with_loss = current_metrics.copy() if isinstance(current_metrics, dict) else {}
                            metrics_with_loss["train_loss"] = current_train_loss
                            metrics_with_loss["val_loss"] = current_val_loss if current_val_loss != float('inf') else None
                            self._metric_tracker.add_epoch(epoch_idx, metrics_with_loss)
                            
                            # Set epoch for structured logger (CRITICAL: every line must have epoch prefix)
                            self._structured_logger.set_epoch(epoch_idx)
                            
                            # Get loss deltas
                            train_deltas = self._metric_tracker.get_deltas("train_loss", epoch_idx, [1, 5, 10])
                            val_deltas = self._metric_tracker.get_deltas("val_loss", epoch_idx, [1, 5, 10])
                            
                            # Get current LR for logging
                            current_lr = get_lr()
                            lr_value = current_lr[0] if isinstance(current_lr, list) else current_lr
                            
                            # Log loss with LR prominently displayed
                            self._structured_logger.log_loss_section(
                                train_loss=current_train_loss,
                                val_loss=current_val_loss if current_val_loss != float('inf') else 0,
                                train_deltas=train_deltas,
                                val_deltas=val_deltas,
                                is_new_best=is_new_best,
                                learning_rate=lr_value
                            )
                            
                            # Log adaptive loss weights if using AdaptiveLoss
                            if hasattr(self, 'target_codec') and hasattr(self.target_codec, 'loss_fn'):
                                from featrix.neural.set_codec import AdaptiveLoss
                                if isinstance(self.target_codec.loss_fn, AdaptiveLoss):
                                    weight_summary = self.target_codec.loss_fn.get_weight_summary()
                                    logger.info(f"{log_prefix}🧠 ADAPTIVE LOSS WEIGHTS: {weight_summary}")
                            
                            # Update row tracker
                            if f"epoch_{epoch_idx}" in self._validation_error_tracking.get("validation_results", {}):
                                self._row_tracker.update(epoch_idx, self._validation_error_tracking["validation_results"][f"epoch_{epoch_idx}"])
                            
                            # Get predicted class distribution
                            class_dist = {}
                            pred_dist = current_metrics.get("prediction_distribution", {})
                            if pred_dist:
                                total = sum(pred_dist.values())
                                class_dist = {k: v/total for k, v in pred_dist.items()}
                            
                            # Log training health 
                            # Include gradient flow ratio if fine-tuning (R = ||∇_ES|| / ||∇_Predictor||)
                            gradient_flow_ratio = progress_dict.get("avg_gradient_flow_ratio") if fine_tune else None
                            gradient_flow_log_ratio = progress_dict.get("avg_gradient_flow_log_ratio") if fine_tune else None
                            self._structured_logger.log_health_section(
                                gradient_unclipped=progress_dict.get("gradient_unclipped", 0),
                                gradient_clipped=progress_dict.get("gradient_clipped", 0),
                                learning_rate=progress_dict.get("lr", 0),
                                lr_phase=f"epoch {epoch_idx+1}/{n_epochs}",
                                class_distribution=class_dist,
                                prob_std=current_metrics.get("prob_std", 0) if isinstance(current_metrics, dict) else 0,
                                logit_range=current_metrics.get("logit_range", 0) if isinstance(current_metrics, dict) else 0,
                                gradient_flow_ratio=gradient_flow_ratio,  # R = ||∇_ES|| / ||∇_Predictor||
                                gradient_flow_log_ratio=gradient_flow_log_ratio,  # log R = log(||∇_ES||) - log(||∇_Predictor||)
                                warnings=[]
                            )
                            
                            # Log metrics table
                            self._structured_logger.log_metrics_table(
                                current_metrics=current_metrics if isinstance(current_metrics, dict) else {},
                                metric_tracker=self._metric_tracker,
                                current_epoch=epoch_idx,
                                best_metrics={"auc": is_new_best}
                            )
                            
                            # Log model architecture parameters
                            self._structured_logger.log_model_parameters(
                                embedding_space=self.embedding_space,
                                predictor=self.predictor,
                                batch_size=batch_size,
                                n_epochs=n_epochs
                            )
                            
                            # Log confusion matrix
                            if isinstance(current_metrics, dict) and all(k in current_metrics for k in ['tp', 'fp', 'tn', 'fn']):
                                self._structured_logger.log_confusion_matrix(
                                    tp=int(current_metrics['tp']),
                                    fp=int(current_metrics['fp']),
                                    tn=int(current_metrics['tn']),
                                    fn=int(current_metrics['fn']),
                                    pos_label=str(val_pos_label) if val_pos_label else "positive",
                                    neg_label="negative",
                                    threshold=float(current_metrics.get('optimal_threshold', 0.5)),
                                    precision=float(current_metrics.get('precision', 0)),
                                    recall=float(current_metrics.get('recall', 0)),
                                    specificity=float(current_metrics.get('specificity', 0))
                                )
                            
                            # Log probability bands
                            if isinstance(current_metrics, dict):
                                bands_data = current_metrics.get('binary_lift_bands')
                                if bands_data:
                                    self._structured_logger.log_probability_bands(bands_data)
                            
                            # Log row tracking
                            self._structured_logger.log_row_tracking(self._row_tracker, epoch_idx)
                            
                            # DYNAMIC FEATURE ENGINEERING: Capture and apply suggestions
                            # (disabled by default - DynamicRelationshipExtractor handles this now)
                            if self.enable_feature_suggestions and self._feature_tracker is not None:
                                if hasattr(self._structured_logger, '_last_generated_suggestions'):
                                    suggestions = self._structured_logger._last_generated_suggestions
                                    if suggestions:
                                        # Record suggestions in tracker
                                        self._feature_tracker.record_suggestions(suggestions, epoch_idx)
                                        
                                        # Check if we should apply features this epoch
                                        if self._feature_tracker.should_apply_features(epoch_idx):
                                            try:
                                                self._apply_dynamic_features(epoch_idx)
                                            except Exception as feat_err:
                                                logger.warning(f"⚠️  Failed to apply dynamic features: {feat_err}")
                            
                            # Log threshold
                            if isinstance(current_metrics, dict) and current_metrics.get('optimal_threshold'):
                                self._structured_logger.log_threshold_section(
                                    optimal_threshold=float(current_metrics['optimal_threshold']),
                                    default_threshold=0.5,
                                    f1_optimal=float(current_metrics.get('f1', 0)),
                                    f1_default=float(current_metrics.get('argmax_f1', 0)),
                                    acc_optimal=float(current_metrics.get('accuracy', 0)),
                                    acc_default=float(current_metrics.get('argmax_accuracy', 0))
                                )
                            
                            # Separator
                            self._structured_logger.log_epoch_separator()
                            
                            # Store classification display metadata for this epoch
                            # This allows recreating the full display from checkpoint
                            try:
                                display_metadata = self._extract_classification_display_metadata(epoch_idx, current_metrics)
                                if not hasattr(self, '_epoch_display_metadata'):
                                    self._epoch_display_metadata = {}
                                self._epoch_display_metadata[epoch_idx] = display_metadata
                            except Exception as display_meta_error:
                                logger.debug(f"Could not extract display metadata for epoch {epoch_idx}: {display_meta_error}")
                            
                        except (TrainingFailureException, EarlyStoppingException):
                            # CRITICAL: Re-raise training failure/early stopping exceptions - they should stop training!
                            raise
                        except Exception as struct_log_error:
                            logger.warning(f"⚠️  Structured logging error: {struct_log_error}")
                        
                        # CRITICAL: Track best model state whenever we find a new best, regardless of epoch
                        # This ensures we always have the best model to restore, even if best epoch was before epoch 20
                        # The checkpoint FILE is only saved from epoch 20+, but we track the state from epoch 3+
                        if is_new_best:
                            _log_gpu_memory(f"BEFORE STATE_DICT CALLS (epoch {epoch_idx})", log_level=logging.INFO)
                            # Save model states for best model restoration
                            # Note: state_dict() returns a regular dict, so no need for deepcopy
                            best_model_state = self.predictor.state_dict()
                            best_embedding_space_state = self.embedding_space.encoder.state_dict()
                            _log_gpu_memory(f"AFTER STATE_DICT CALLS (epoch {epoch_idx})", log_level=logging.INFO)
                            
                            # Track warnings at best epoch
                            self.best_epoch_warnings = []
                            metrics = progress_dict.get("metrics", {})
                            if metrics and metrics.get("failure_detected"):
                                self.best_epoch_warnings.append({
                                    "type": metrics.get("failure_label", "UNKNOWN"),
                                    "epoch": epoch_idx,
                                    "details": {
                                        "recommendations": metrics.get("recommendations", []),
                                        "auc": metrics.get("auc"),
                                        "accuracy": metrics.get("accuracy")
                                    }
                                })
                            
                            # Update best_epoch to the appropriate one
                            # Recompute use_composite_score to determine which epoch to use
                            use_composite_score = (
                                self.cost_false_positive is not None and 
                                self.cost_false_negative is not None and
                                use_auc_for_best_epoch and 
                                current_auc >= 0
                            )
                            if use_composite_score and hasattr(self, '_best_composite_score_epoch') and self._best_composite_score_epoch >= 0:
                                # Use composite score epoch
                                best_epoch = self._best_composite_score_epoch
                            elif use_auc_for_best_epoch and current_auc >= 0:
                                # Use PR-AUC epoch if we're using PR-AUC for selection, otherwise ROC-AUC epoch
                                if hasattr(self, 'distribution_metadata') and self.distribution_metadata:
                                    imbalance_score = self.distribution_metadata.get('imbalance_score', 1.0)
                                    is_imbalanced = imbalance_score < 0.3
                                    if is_imbalanced and best_pr_auc_epoch >= 0:
                                        best_epoch = best_pr_auc_epoch
                                    else:
                                        best_epoch = best_auc_epoch
                                else:
                                    best_epoch = best_auc_epoch
                            else:
                                # best_epoch already set above for validation loss case
                                pass
                            
                            if epoch_idx < 20:
                                logger.debug(f"   📊 New best model at epoch {epoch_idx} (tracking state, will save checkpoint file from epoch 20+)")
                        
                        # Check /NODUMP file - skip best checkpoint FILE saves unless last fold
                        # But we still track best_model_state above for restoration
                        nodump_exists = os.path.exists('/NODUMP')
                        is_last_fold = getattr(self, 'is_last_fold', True)  # Assume True if not set
                        
                        # Save best checkpoints from epoch 3+ (lowered from 20 to catch early improvements)
                        should_save_best_file = is_new_best and epoch_idx >= 3 and (not nodump_exists or is_last_fold)
                        
                        if is_new_best and epoch_idx >= 3:
                            if nodump_exists and not is_last_fold:
                                logger.info(f"   ⏭️  /NODUMP exists and not last fold - skipping best checkpoint file save (but tracking best model state)")
                            elif nodump_exists and is_last_fold:
                                logger.info(f"   ✅ /NODUMP exists BUT this is last fold - saving best checkpoint file anyway")
                            
                            # Add event to timeline: New best epoch
                            if hasattr(self, '_training_timeline'):
                                best_epoch_event = {
                                    "epoch": epoch_idx,
                                    "event_type": "best_epoch",
                                    "metric_used": "auc" if use_auc_for_best_epoch else "validation_loss",
                                    "metric_value": float(current_auc) if use_auc_for_best_epoch and current_auc >= 0 else float(current_val_loss) if current_val_loss is not None else None,
                                    "previous_best_epoch": best_epoch if best_epoch >= 0 else None,
                                    "time_now": time.time(),
                                }
                                self._training_timeline.append(best_epoch_event)
                        
                        # Save checkpoints for both ROC-AUC and PR-AUC best models (if they exist and epoch >= 3)
                        (best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path, 
                         best_checkpoint_path) = self._save_best_model_checkpoints(
                            epoch_idx=epoch_idx,
                            nodump_exists=nodump_exists,
                            is_last_fold=is_last_fold,
                            sp_identifier=sp_identifier,
                            training_start_timestamp=training_start_timestamp,
                            best_auc=best_auc,
                            best_auc_epoch=best_auc_epoch,
                            best_pr_auc=best_pr_auc,
                            best_pr_auc_epoch=best_pr_auc_epoch,
                            best_roc_auc_model_state=best_roc_auc_model_state,
                            best_roc_auc_embedding_space_state=best_roc_auc_embedding_space_state,
                            best_pr_auc_model_state=best_pr_auc_model_state,
                            best_pr_auc_embedding_space_state=best_pr_auc_embedding_space_state,
                            best_roc_auc_checkpoint_path=best_roc_auc_checkpoint_path,
                            best_pr_auc_checkpoint_path=best_pr_auc_checkpoint_path,
                            best_checkpoint_path=best_checkpoint_path,
                            use_auc_for_best_epoch=use_auc_for_best_epoch,
                            current_auc=current_auc,
                            current_val_loss=current_val_loss,
                            should_save_best_file=should_save_best_file,
                            optimizer=optimizer
                        )
            
                        # Determine if we should send progress callback this epoch
                        should_send_callback = self._should_send_progress_callback(epoch_idx, n_epochs)
                        
                        # End of every epoch where we want to send update
                        if should_send_callback and print_callback is not None:
                            print_callback(progress_dict)
        
                        # Update last_metrics_time at end of epoch
                        time_now = time.time()
                        last_metrics_time = time_now
                        progress_dict["epoch_idx"] += 1
                        
                        # LRTimeline scheduler.step() is called per-epoch, not per-batch
                        # NOT here at end of epoch (that was for old CosineAnnealingLR)
                        # No scheduler.step() needed here anymore
                        
                        # Check for /NODUMP file - skip all checkpoints if it exists
                        nodump_exists = os.path.exists('/NODUMP')
                        
                        # PERIODIC CHECKPOINT: Save every N epochs for recovery
                        checkpoint_interval = 5  # Save every 5 epochs
                        should_save_checkpoint = (
                            not nodump_exists and
                            epoch_idx > 0 and  # Don't save at epoch 0
                            epoch_idx % checkpoint_interval == 0  # Every 5 epochs
                        )
                        
                        if nodump_exists:
                            logger.debug(f"⏭️  SKIPPING checkpoint: /NODUMP file exists")
                        elif should_save_checkpoint:
                            logger.info(f"✅ PERIODIC CHECKPOINT: epoch {epoch_idx} (every {checkpoint_interval} epochs)")
                        else:
                            logger.debug(f"⏭️  SKIPPING checkpoint: not at interval boundary (epoch {epoch_idx} % {checkpoint_interval} != 0)")
                        
                        # Save checkpoint if enabled
                        if should_save_checkpoint:
                            logger.info(f"")
                            logger.info(f"💾 PERIODIC CHECKPOINT (epoch {epoch_idx}, every {checkpoint_interval} epochs)")
                            checkpoint_start_time = time.time()
                            try:
                                _log_gpu_memory(f"BEFORE EPOCH CHECKPOINT SAVE (epoch {epoch_idx})", log_level=logging.INFO)
                                
                                # Clear GPU cache before saving checkpoint to free up memory
                                if is_gpu_available():
                                    empty_gpu_cache()
                                    synchronize_gpu()
                                
                                checkpoint_dir = self._output_dir if self._output_dir else "."
                                id_suffix = f"_{sp_identifier}" if sp_identifier else ""
                                # Periodic checkpoint naming
                                # Include training_start_timestamp to prevent stomping across re-runs
                                epoch_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_epoch_{epoch_idx}.pickle")
                                
                                _log_gpu_memory(f"BEFORE FIRST EPOCH CHECKPOINT PICKLE.DUMP (epoch {epoch_idx})", log_level=logging.INFO)
                                
                                # CRITICAL: Validate and fix model integrity before saving
                                self._validate_and_fix_before_save()
                                
                                # Save checkpoint with training status metadata
                                with open(epoch_checkpoint_path, "wb") as f:
                                    pickle.dump(self, f)
                                _log_gpu_memory(f"AFTER FIRST EPOCH CHECKPOINT PICKLE.DUMP (epoch {epoch_idx})", log_level=logging.INFO)
                                
                                checkpoint_time = time.time() - checkpoint_start_time
                                logger.info(f"💾 Epoch checkpoint saved: {epoch_checkpoint_path} ({checkpoint_time:.3f}s)")
                                
                                # Also save a "latest" checkpoint for easy access
                                # Include training_start_timestamp to prevent stomping across re-runs
                                latest_checkpoint_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_latest.pickle")
                                # Validate again before saving latest (col_order might have been fixed above)
                                self._validate_and_fix_before_save()
                                with open(latest_checkpoint_path, "wb") as f:
                                    pickle.dump(self, f)
                                
                                # Save training status metadata JSON for quick access without loading pickle
                                # Get current metrics if available
                                current_metrics = None
                                if hasattr(self, 'training_metrics') and self.training_metrics:
                                    current_metrics = self.training_metrics.copy()
                                
                                status_metadata = {
                                    "epoch": epoch_idx,
                                    "total_epochs": n_epochs,
                                    "progress_percent": (epoch_idx + 1) / n_epochs * 100 if n_epochs > 0 else 0,
                                    "training_loss": progress_dict.get("current_loss"),
                                    "validation_loss": progress_dict.get("validation_loss"),
                                    "metrics": current_metrics,
                                    "checkpoint_path": epoch_checkpoint_path,
                                    "latest_checkpoint_path": latest_checkpoint_path,
                                    "checkpoint_save_time_secs": checkpoint_time,
                                    "is_training": True,
                                    "timestamp": time.time(),
                                    "data_passes": epoch_idx + 1  # Number of data passes completed
                                }
                                # Include training_start_timestamp to prevent stomping across re-runs
                                status_metadata_path = os.path.join(checkpoint_dir, f"{training_start_timestamp}_single_predictor{id_suffix}_training_status.json")
                                with open(status_metadata_path, "w") as f:
                                    json.dump(status_metadata, f, indent=2, default=str)
                                
                                # CRITICAL: Move models back to GPU after checkpoint save
                                # __getstate__ moves predictor_base to CPU (line 650), and since
                                # self.predictor = nn.Sequential(predictor_base, Linear(...)),
                                # the predictor ends up with mixed devices (first layer CPU, rest GPU)
                                if is_gpu_available():
                                    device = get_device()
                                    if list(self.predictor.parameters()):
                                        current_device = next(self.predictor.parameters()).device
                                        if current_device.type == 'cpu':
                                            logger.info(f"   🔄 Moving predictor back to {device} after checkpoint save...")
                                            self.predictor = self.predictor.to(device)
                                    if hasattr(self, 'predictor_base') and self.predictor_base is not None:
                                        if list(self.predictor_base.parameters()):
                                            current_device = next(self.predictor_base.parameters()).device
                                            if current_device.type == 'cpu':
                                                logger.info(f"   🔄 Moving predictor_base back to {device} after checkpoint save...")
                                                self.predictor_base = self.predictor_base.to(device)
                                    if hasattr(self, 'embedding_space') and self.embedding_space is not None:
                                        if hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder is not None:
                                            if list(self.embedding_space.encoder.parameters()):
                                                current_device = next(self.embedding_space.encoder.parameters()).device
                                                if current_device.type == 'cpu':
                                                    logger.info(f"   🔄 Moving encoder back to {device} after checkpoint save...")
                                                    self.embedding_space.encoder = self.embedding_space.encoder.to(device)
                                
                            except RuntimeError as checkpoint_error:
                                # Handle CUDA OOM during checkpoint save
                                error_msg = str(checkpoint_error).lower()
                                checkpoint_time = time.time() - checkpoint_start_time
                                if "cuda" in error_msg and ("out of memory" in error_msg or "oom" in error_msg):
                                    # Dump memory usage to understand what's holding VRAM
                                    _dump_cuda_memory_usage(context=f"checkpoint save (epoch {epoch_idx})")
                                logger.warning(f"⚠️  Failed to save epoch checkpoint due to CUDA OOM (took {checkpoint_time:.3f}s)")
                                
                                # Try saving on CPU instead - save full pickle after moving everything to CPU
                                self._save_checkpoint_on_cpu_with_oom_recovery(
                                    epoch_idx=epoch_idx,
                                    checkpoint_start_time=checkpoint_start_time,
                                    sp_identifier=sp_identifier,
                                    training_start_timestamp=training_start_timestamp,
                                    n_epochs=n_epochs,
                                    progress_dict=progress_dict,
                                    optimizer=optimizer,
                                    _dump_cuda_memory_usage=_dump_cuda_memory_usage,
                                    _walk_model_for_gpu=_walk_model_for_gpu,
                                    _log_gpu_memory=_log_gpu_memory
                                )
                            except Exception as checkpoint_error:
                                # Catch any other exceptions during checkpoint save (not RuntimeError)
                                checkpoint_time = time.time() - checkpoint_start_time
                                logger.warning(f"⚠️  Failed to save epoch checkpoint (took {checkpoint_time:.3f}s): {checkpoint_error}")
                                # Don't re-raise - continue training even if checkpoint save fails
                        
                    # print("train loop: epoch = ", progress_dict.epoch_idx)
                    # ========================================================================
                    # END: EPOCH FOR LOOP (range(n_epochs))
                    # ========================================================================
                
                    # Normal completion - training finished without restart
                    restart_loop_active = False
                    logger.info("✅ Training completed successfully without restarts")
                    
                    # Export feature suggestion history
                    if hasattr(self, '_feature_tracker') and self._feature_tracker:
                        try:
                            final_epoch = n_epochs - 1
                            self._feature_tracker.log_status(final_epoch)
                            
                            # Export history to qa.save subdirectory to keep output organized
                            if self._output_dir:
                                qa_save_dir = os.path.join(self._output_dir, "qa.save")
                                os.makedirs(qa_save_dir, exist_ok=True)
                                history_path = os.path.join(qa_save_dir, "feature_suggestion_history.json")
                            else:
                                qa_save_dir = "qa.save"
                                os.makedirs(qa_save_dir, exist_ok=True)
                                history_path = os.path.join(qa_save_dir, "feature_suggestion_history.json")
                            
                            self._feature_tracker.export_history(history_path)
                            
                            # Log applied features summary
                            if self._features_applied_epochs:
                                logger.info("")
                                logger.info("📋 FEATURES APPLIED DURING TRAINING:")
                                for feat_info in self._features_applied_epochs:
                                    epoch = feat_info['epoch']
                                    fname = feat_info['feature_name']
                                    votes = feat_info['votes']
                                    epochs_list = feat_info['suggested_at_epochs']
                                    if len(epochs_list) > 25:
                                        epochs_str = ', '.join(map(str, epochs_list[:25]))
                                        remaining = len(epochs_list) - 25
                                        epochs_str += f" + {remaining} others"
                                    else:
                                        epochs_str = ', '.join(map(str, epochs_list))
                                    logger.info(f"   Epoch {epoch:3d}: {fname} ({votes} votes, suggested at epochs [{epochs_str}])")
                                logger.info("")
                        except Exception as export_err:
                            logger.warning(f"⚠️  Failed to export feature tracker history: {export_err}")
                    
                    # Record effectiveness of feature combination used in this run
                    if hasattr(self, '_effectiveness_tracker') and self._effectiveness_tracker:
                        try:
                            # Collect final metrics from best epoch
                            final_metrics = {}
                            
                            # Get metrics from stored best model metrics
                            if hasattr(self, 'best_model_metrics') and self.best_model_metrics:
                                best_metrics = cast(Dict[str, Any], self.best_model_metrics)  # pylint: disable=unsubscriptable-object
                                metrics_to_track = ['roc_auc', 'pr_auc', 'f1', 'accuracy', 'val_loss']
                                for metric_name in metrics_to_track:
                                    if best_metrics and metric_name in best_metrics:  # pylint: disable=unsupported-membership-test
                                        final_metrics[metric_name] = float(best_metrics[metric_name])  # pylint: disable=unsubscriptable-object
                            
                            # Record this run's results
                            if final_metrics:
                                # Get list of features used (loaded at start + applied during training)
                                features_used = list(self._loaded_features)  # Features loaded from previous run
                                
                                # Add features applied during this training
                                if self._features_applied_epochs:
                                    for feat_info in self._features_applied_epochs:
                                        feature_name = feat_info['feature_name']
                                        if feature_name not in features_used:
                                            features_used.append(feature_name)
                                
                                # Record the run
                                self._effectiveness_tracker.record_run(
                                    features=features_used,
                                    metrics=final_metrics,
                                    run_metadata={
                                        'n_epochs': n_epochs,
                                        'batch_size': batch_size,
                                        'job_id': job_id,
                                        'target': self.target_col_name
                                    }
                                )
                                
                                # Export effectiveness history
                                if self._output_dir:
                                    effectiveness_path = os.path.join(self._output_dir, "qa.save", "feature_effectiveness.json")
                                else:
                                    effectiveness_path = os.path.join("qa.save", "feature_effectiveness.json")
                                
                                self._effectiveness_tracker.export_history(effectiveness_path)
                                
                                # Log summary
                                self._effectiveness_tracker.log_summary()
                            else:
                                logger.debug("ℹ️  No metrics available for effectiveness tracking")
                                
                        except Exception as eff_err:
                            logger.warning(f"⚠️  Failed to record feature effectiveness: {eff_err}")
                            traceback.print_exc()
                
                except FeatrixRestartTrainingException as e:
                    # Caught restart exception - apply restart configuration
                    restart_config = e.restart_config
                    restart_attempts += 1
                    
                    logger.warning("=" * 80)
                    logger.warning(f"🔄 TRAINING RESTART #{restart_attempts} TRIGGERED")
                    logger.warning("=" * 80)
                    logger.warning(f"⚠️  Exception: {e}")
                    logger.warning(f"⚠️  Reason: {restart_config.reason}")
                    logger.warning(f"⚠️  Detected at epoch: {restart_config.epoch_detected}")
                    
                    # Get current learning rate
                    def get_current_lr_from_optimizer(opt):
                        if hasattr(opt, 'param_groups') and len(opt.param_groups) > 0:
                            return opt.param_groups[0]['lr']
                        return None
                    
                    current_lr = get_current_lr_from_optimizer(optimizer)
                    if current_lr is None:
                        logger.error("❌ Could not get current LR from optimizer - using default 0.01")
                        current_lr = 0.01
                    
                    # Calculate new learning rate
                    new_lr = current_lr * restart_config.lr_multiplier
                    if new_lr > restart_config.max_lr:
                        new_lr = restart_config.max_lr
                        logger.warning(f"   LR capped at maximum: {restart_config.max_lr:.6e}")
                    
                    logger.warning(f"   Old LR: {current_lr:.6e}")
                    logger.warning(f"   New LR: {new_lr:.6e} ({restart_config.lr_multiplier}x boost)")
                    
                    # Reset optimizer state if requested
                    if restart_config.reset_optimizer_state:
                        logger.warning(f"   Resetting optimizer state (clearing momentum/adaptive terms)...")
                        # CRITICAL: Can't just assign optimizer.state = {} - must use clear() or recreate
                        # PyTorch optimizer uses WeakKeyDictionary for state, need to properly clear it
                        optimizer.state.clear()
                        logger.warning(f"   ✅ Optimizer state cleared")
                    
                    # Update learning rate for all parameter groups
                    for group in optimizer.param_groups:
                        group['lr'] = new_lr
                    logger.warning(f"   ✅ Learning rate updated to {new_lr:.6e}")
                    
                    # CRITICAL: ALWAYS reset scheduler on restart to prevent LR explosion
                    # When training restarts, epochs start over at 0, but scheduler continues from old state
                    # This causes scheduler to step way past T_max, producing garbage LR values (can reach 10^21!)
                    if use_lr_scheduler:
                        logger.warning(f"   Recreating LRTimeline scheduler (required on restart)...")
                        remaining_epochs = n_epochs  # Full epoch count since we're starting from 0
                        
                        # Recreate LRTimeline with same config as initial training
                        # Use same simple schedule: linear warmup + cosine decay
                        warmup_epochs = 5
                        warmup_start_lr = 5e-5
                        warmup_end_lr = 6e-4
                        decay_end_lr = 1e-5
                        
                        # Use 'sp_plus_es' mode if fine-tuning (ES will be unfrozen), otherwise 'sp_only'
                        scheduler_mode = 'sp_plus_es' if fine_tune else 'sp_only'
                        
                        scheduler = LRTimeline(
                            n_epochs=remaining_epochs,
                            schedule_type='simple',
                            warmup_epochs=warmup_epochs,
                            warmup_start_lr=warmup_start_lr,
                            warmup_end_lr=warmup_end_lr,
                            decay_end_lr=decay_end_lr,
                            mode=scheduler_mode,
                        )
                        self._training_scheduler = scheduler  # Update stored reference
                        logger.warning(f"   ✅ LRTimeline scheduler reset ({remaining_epochs} epochs, warmup={warmup_start_lr:.2e}→{warmup_end_lr:.2e}, decay→{decay_end_lr:.2e})")
                    
                    # Load best checkpoint if requested
                    if restart_config.load_best_checkpoint and best_model_state is not None:
                        logger.warning(f"   Reloading best checkpoint from epoch {best_epoch}...")
                        self.predictor.load_state_dict(best_model_state)
                        self.embedding_space.encoder.load_state_dict(best_embedding_space_state)
                        
                        # CRITICAL: After loading checkpoint, model parameters are NEW objects
                        # We must recreate the optimizer to track the new parameters
                        logger.warning(f"   Recreating optimizer to track reloaded parameters...")
                        old_lr = optimizer.param_groups[0]['lr']
                        old_weight_decay = optimizer.param_groups[0].get('weight_decay', 0.0)
                        
                        # Check if we were fine-tuning by looking at optimizer param groups
                        # If encoder params are in optimizer, we were fine-tuning
                        was_fine_tuning = len(optimizer.param_groups) > 1 or any(
                            id(p) in {id(ep) for ep in self.embedding_space.encoder.parameters()}
                            for group in optimizer.param_groups
                            for p in group['params']
                        )
                        
                        if was_fine_tuning:
                            # Recreate with both predictor and encoder params
                            params = list(self.predictor.parameters()) + list(self.embedding_space.encoder.parameters())
                        else:
                            # Recreate with only predictor params
                            params = list(self.predictor.parameters())
                        
                        optimizer = torch.optim.AdamW(params, lr=old_lr, weight_decay=old_weight_decay)
                        logger.warning(f"   ✅ Optimizer recreated with new parameters (fine_tune={was_fine_tuning})")
                        
                        logger.warning(f"   ✅ Best model weights restored (epoch {best_epoch})")
                    else:
                        # CRITICAL: No checkpoint available - check if current weights are corrupted
                        logger.warning(f"   No best checkpoint available - checking current model weights for NaN/Inf...")
                        
                        # Check for NaN/Inf in model parameters
                        has_nan_weights = False
                        nan_param_names = []
                        for name, param in self.predictor.named_parameters():
                            if param is not None and (torch.isnan(param).any() or torch.isinf(param).any()):
                                has_nan_weights = True
                                nan_param_names.append(name)
                        
                        if has_nan_weights:
                            logger.error(f"   ❌ FATAL: Model weights are corrupted with NaN/Inf!")
                            logger.error(f"      Corrupted parameters: {nan_param_names[:10]}")
                            logger.error(f"      Cannot restart from corrupted weights - training must abort")
                            logger.error(f"   💡 Solution: Reduce learning rate or fix gradient clipping")
                            raise RuntimeError(
                                f"Training restart failed: model weights corrupted with NaN/Inf. "
                                f"Cannot continue from epoch {restart_config.epoch_detected}. "
                                f"Try reducing learning rate or improving gradient clipping."
                            )
                        
                        # Reset BatchNorm running statistics (may have accumulated NaN)
                        logger.warning(f"   Resetting BatchNorm running statistics...")
                        bn_modules_reset = 0
                        for module in self.predictor.modules():
                            if isinstance(module, (torch.nn.BatchNorm1d, torch.nn.BatchNorm2d, torch.nn.BatchNorm3d)):
                                module.reset_running_stats()
                                bn_modules_reset += 1
                        if bn_modules_reset > 0:
                            logger.warning(f"   ✅ Reset {bn_modules_reset} BatchNorm modules")
                        
                        logger.warning(f"   ✅ Weights verified clean, continuing from current weights")
                    
                    # Log corrective action
                    corrective_action = {
                        "epoch": restart_config.epoch_detected,
                        "trigger": restart_config.reason,
                        "action_type": "TRAINING_RESTART",
                        "details": {
                            "old_lr": float(current_lr),
                            "new_lr": float(new_lr),
                            "lr_boost_multiplier": float(restart_config.lr_multiplier),
                            "restart_number": restart_attempts,
                            "optimizer_state_reset": restart_config.reset_optimizer_state,
                            "scheduler_reset": restart_config.reset_scheduler,
                            "checkpoint_reloaded": restart_config.load_best_checkpoint and best_model_state is not None,
                            **restart_config.metadata
                        }
                    }
                    self._corrective_actions.append(corrective_action)
                    
                    # Add event to timeline: Training restart
                    if hasattr(self, '_training_timeline'):
                        restart_event = {
                            "epoch": restart_config.epoch_detected,
                            "event_type": "training_restart",
                            "reason": restart_config.reason,
                            "old_lr": float(current_lr),
                            "new_lr": float(new_lr),
                            "lr_multiplier": float(restart_config.lr_multiplier),
                            "restart_number": restart_attempts,
                            "optimizer_state_reset": restart_config.reset_optimizer_state,
                            "scheduler_reset": restart_config.reset_scheduler,
                            "checkpoint_reloaded": restart_config.load_best_checkpoint and best_model_state is not None,
                            "metadata": restart_config.metadata,
                            "time_now": time.time(),
                        }
                        self._training_timeline.append(restart_event)
                    
                    # Update tracking
                    self.training_restart_count = restart_attempts
                    self.last_restart_epoch = restart_config.epoch_detected
                    self.dead_gradient_epochs = []  # Clear dead gradient history
                    
                    logger.warning(f"   ✅ Corrective action logged")
                    logger.warning(f"   🔄 Training will restart from epoch {restart_config.epoch_detected}")
                    logger.warning("=" * 80)
                    
                    # Report to featrix-monitor that restart was successfully applied
                    try:
                        from lib.training_monitor import post_training_anomaly
                        post_training_anomaly(
                            session_id=job_id if job_id else "unknown",
                            anomaly_type="training_restart_applied",
                            epoch=restart_config.epoch_detected,
                            dataset_hash=getattr(self, '_dataset_hash', None),  # TOP-LEVEL parameter
                            details={
                                "restart_reason": restart_config.reason,
                                "restart_number": restart_attempts,
                                "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                                # LR changes
                                "old_lr": float(current_lr),
                                "new_lr": float(new_lr),
                                "lr_multiplier": float(restart_config.lr_multiplier),
                                "lr_capped": (new_lr == restart_config.max_lr),
                                # Optimizer changes
                                "optimizer_state_reset": restart_config.reset_optimizer_state,
                                "scheduler_reset": True,  # Always reset on restart
                                # Checkpoint info
                                "checkpoint_reloaded": restart_config.load_best_checkpoint and best_model_state is not None,
                                "best_epoch_loaded": best_epoch if (restart_config.load_best_checkpoint and best_model_state) else None,
                                # Training state
                                "batch_size": batch_size,
                                "remaining_epochs": n_epochs,
                            }
                        )
                    except Exception as monitor_err:
                        logger.warning(f"⚠️  Failed to report training restart to monitor: {monitor_err}")
                    
                    # Continue the while loop to restart training
                    continue
            # ============================================================================
            # END: RESTART WHILE LOOP
            # ============================================================================

            # 
            # Dump final training status.
            # 
            logger.info(f"@@@@@@@ >> encoding time took {encode_time} seconds")
            logger.info(
                f"@@@@@@@ >> encoding time vs a total of {time.time() - loop_start} seconds"
            )

            progress_dict["time_now"] = progress_dict["end_time"] = time.time()
            progress_dict["progress_counter"] = progress_dict["max_progress"]
            progress_dict["batch_idx"] = progress_dict["batch_total"]
            if print_callback is not None:
                print_callback(progress_dict)
            # self.training_info['progress_info'] = d

        # Call pre_best_restore_callback BEFORE restoring best model
        # This gives caller a chance to run predictions on the last-epoch model
        last_epoch_idx = n_epochs - 1
        if pre_best_restore_callback is not None:
            try:
                logger.info(f"📊 Running pre_best_restore_callback (model at epoch {last_epoch_idx})...")
                pre_best_restore_callback(self, last_epoch_idx)
                logger.info(f"✅ pre_best_restore_callback completed")
            except Exception as e:
                logger.warning(f"⚠️  pre_best_restore_callback failed: {e}")
                logger.debug(traceback.format_exc())
        
        # ============================================================================
        # ALWAYS SAVE BEST MODELS (idempotent - checks if files exist)
        # ============================================================================
        best_roc_auc_checkpoint_path, best_pr_auc_checkpoint_path = self._save_final_best_checkpoints(
            use_auc_for_best_epoch=use_auc_for_best_epoch,
            best_auc=best_auc,
            sp_identifier=sp_identifier,
            training_start_timestamp=training_start_timestamp,
            best_roc_auc_model_state=best_roc_auc_model_state,
            best_roc_auc_embedding_space_state=best_roc_auc_embedding_space_state,
            best_auc_epoch=best_auc_epoch,
            best_pr_auc_model_state=best_pr_auc_model_state,
            best_pr_auc_embedding_space_state=best_pr_auc_embedding_space_state,
            best_pr_auc_epoch=best_pr_auc_epoch,
            best_pr_auc=best_pr_auc,
            best_roc_auc_checkpoint_path=best_roc_auc_checkpoint_path,
            best_pr_auc_checkpoint_path=best_pr_auc_checkpoint_path
        )
        
        # Restore best model if we found one
        # Determine which variant to restore (primary selection)
        primary_metric = None
        primary_epoch = -1
        primary_value = -1.0
        
        # Determine which best model to restore (PR-AUC vs ROC-AUC vs val_loss)
        primary_metric, primary_epoch, primary_value, best_model_state, best_embedding_space_state, best_epoch = \
            self._determine_best_model_to_restore(
                use_auc_for_best_epoch=use_auc_for_best_epoch,
                best_auc=best_auc,
                best_metric_preference=best_metric_preference,
                best_pr_auc_epoch=best_pr_auc_epoch,
                best_pr_auc_model_state=best_pr_auc_model_state,
                best_pr_auc=best_pr_auc,
                best_pr_auc_embedding_space_state=best_pr_auc_embedding_space_state,
                best_roc_auc_model_state=best_roc_auc_model_state,
                best_auc_epoch=best_auc_epoch,
                best_roc_auc_embedding_space_state=best_roc_auc_embedding_space_state,
                best_model_state=best_model_state,
                best_epoch=best_epoch,
                best_val_loss=best_val_loss
            )
        
        # Restore best model and log summary of variants
        self._restore_best_model_and_log_summary(
            use_auc_for_best_epoch=use_auc_for_best_epoch,
            best_auc=best_auc,
            best_roc_auc_model_state=best_roc_auc_model_state,
            best_auc_epoch=best_auc_epoch,
            best_roc_auc_checkpoint_path=best_roc_auc_checkpoint_path,
            best_pr_auc_model_state=best_pr_auc_model_state,
            best_pr_auc_epoch=best_pr_auc_epoch,
            best_pr_auc=best_pr_auc,
            best_pr_auc_checkpoint_path=best_pr_auc_checkpoint_path,
            primary_metric=primary_metric,
            primary_epoch=primary_epoch,
            primary_value=primary_value,
            best_model_state=best_model_state,
            best_epoch=best_epoch,
            best_embedding_space_state=best_embedding_space_state,
            best_checkpoint_path=best_checkpoint_path,
            best_metric_preference=best_metric_preference
        )

        logger.info("Setting predictor.eval()")
        self.predictor.eval()
        
        # CRITICAL: Best checkpoint is now the default output for inference
        # The best model (by PR-AUC or ROC-AUC) has been restored and will be used for all predictions
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🎯 FINAL MODEL = best@{primary_metric}@e={best_epoch}")
        logger.info(f"   Using best checkpoint (epoch {best_epoch}), not last epoch ({n_epochs-1})")
        logger.info(f"   Best metric: {primary_metric}={primary_value:.4f}")
        if best_checkpoint_path:
            logger.info(f"   Checkpoint: {best_checkpoint_path}")
        logger.info("=" * 80)
        logger.info("")
        
        # Log best vs final epoch comparison
        self._log_best_vs_final_comparison(best_epoch, n_epochs, primary_metric)
        
        # Fit calibration automatically after training completes
        # Only for classification tasks (SetCodec), not regression (ScalarCodec)        
        # Auto-fit calibration on validation set for classification
        self._fit_calibration_on_validation_set(val_queries=val_queries, val_targets=val_targets)
        
        # Generate GraphViz visualization of network architecture
        self._generate_network_visualization(network_viz_identifier)
        
        # Clean up GPU memory after training
        logger.info("Cleaning up GPU memory after training")
        self.cleanup_gpu_memory()
        
        # Save validation error tracking
        self._save_validation_error_tracking_and_analyze()
        
        # If early stopping was triggered, raise the exception NOW after best model has been saved
        if hasattr(self, '_early_stop_exception') and self._early_stop_exception is not None:
            logger.warning("=" * 80)
            logger.warning("🛑 EARLY STOPPING: Raising EarlyStoppingException after best model save")
            logger.warning("=" * 80)
            raise self._early_stop_exception
        
        # Cleanup intermediate periodic checkpoints if we have best models
        self._cleanup_intermediate_checkpoints(
            training_start_timestamp=training_start_timestamp,
            sp_identifier=sp_identifier,
            best_roc_auc_checkpoint_path=best_roc_auc_checkpoint_path,
            best_pr_auc_checkpoint_path=best_pr_auc_checkpoint_path,
            best_checkpoint_path=best_checkpoint_path
        )
        
        # Export LRTimeline data and visualizations
        if scheduler is not None and isinstance(scheduler, LRTimeline):
            try:
                logger.info("=" * 100)
                logger.info("📊 EXPORTING LRTIMELINE DATA & VISUALIZATIONS")
                logger.info("=" * 100)
                
                # Export enhanced CSV with all metrics
                csv_path = os.path.join(self._output_dir, "sp_lr_timeline.csv")
                scheduler.export_enhanced_csv(csv_path)
                logger.info(f"📄 SP LR schedule + metrics exported to: {csv_path}")
                
                # Export simple LR curve (for quick reference)
                simple_csv_path = os.path.join(self._output_dir, "sp_lr_schedule.csv")
                scheduler.export_to_csv(simple_csv_path)
                logger.info(f"📄 SP LR schedule exported to: {simple_csv_path}")
                
                # Generate basic LR schedule plot
                schedule_plot_path = os.path.join(self._output_dir, "sp_lr_schedule.png")
                scheduler.plot_schedule(schedule_plot_path)
                logger.info(f"📈 SP LR schedule plot saved to: {schedule_plot_path}")
                
                # Generate LR comparison plot (baseline vs adjusted)
                comparison_plot_path = os.path.join(self._output_dir, "sp_lr_comparison.png")
                scheduler.plot_lr_comparison(comparison_plot_path)
                logger.info(f"📊 SP LR comparison plot (baseline vs adjusted) saved to: {comparison_plot_path}")
                
                # Generate comprehensive training history plot (LR + Loss + Metrics)
                history_plot_path = os.path.join(self._output_dir, "sp_training_history.png")
                scheduler.plot_training_history(history_plot_path)
                logger.info(f"🎨 SP comprehensive training history plot saved to: {history_plot_path}")
                
                # Log adjustment summary
                if scheduler.adjustments:
                    logger.info("")
                    logger.info("🔧 LEARNING RATE ADJUSTMENTS SUMMARY:")
                    for epoch, adj_type, scale, reason in scheduler.adjustments:
                        logger.info(f"   Epoch {epoch}: {adj_type} by {scale:.2f}x - {reason}")
                else:
                    logger.info("")
                    logger.info("✅ No learning rate adjustments were needed")
                
                logger.info("=" * 100)
            except Exception as e:
                logger.warning(f"⚠️ LRTimeline export failed: {e}", exc_info=True)
        
        return self.training_info

    def compute_val_loss(self, loss_fn):
        """
        Compute validation loss across entire validation set.
        
        Iterates through all batches in the validation dataloader and computes
        average loss across the entire validation set.
        
        Args:
            loss_fn: Loss function to use
            
        Returns:
            float: Average validation loss across all validation batches
        """
        # CRITICAL: Clear GPU cache BEFORE validation to free up memory
        try:
            if is_gpu_available():
                empty_gpu_cache()
                synchronize_gpu()
        except Exception as e:
            logger.debug(f"Failed to clear GPU cache before validation: {e}")
        
        with PredictorEvalModeContextManager(fsp=self, debugLabel="compute_val_loss"):
            assert self.predictor.training == False, "where's my eval man [p]"
            assert self.embedding_space.encoder.training == False, "where's my eval man [es]"

            total_loss = 0.0
            total_samples = 0
            device_mismatch_logged = False  # Only log device warning once per validation call
            batch_count = 0
            
            # Iterate through all validation batches
            for val_batch in self._validation_dataloader:
                batch_count += 1
                
                # Move val_batch to same device as encoder
                encoder_device = next(self.embedding_space.encoder.parameters()).device
                for key, tokenbatch in val_batch.items():
                    val_batch[key] = tokenbatch.to(encoder_device)

                # Extract targets
                val_target_token_batch = val_batch.pop(self.target_col_name)
                validation_targets = val_target_token_batch.value
                
                # CRITICAL: Move validation_targets to CPU if we're in CPU mode
                # Check: environment variable, failed GPU restore after checkpoint, or CPU_SP flag file
                force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
                restore_failed_oom = hasattr(self, '_restore_failed_oom') and self._restore_failed_oom
                cpu_sp_flag = os.path.exists('/sphere/CPU_SP')
                if force_cpu or restore_failed_oom or cpu_sp_flag:
                    validation_targets = validation_targets.to(torch.device('cpu'))

                # This mimicks the training loop, but with the validation data.
                target_column_in_original_df = (
                    self.target_col_name in self.embedding_space.col_codecs
                )
                if target_column_in_original_df:
                    marginal_token_batch = self._create_marginal_token_batch_for_target(
                        val_target_token_batch
                    )
                    val_batch[self.target_col_name] = marginal_token_batch

                # Don't apply noise to validation branch - no need for feature dropout
                # at validate time.
                # CRITICAL: Use no_grad() during validation to prevent building computation graphs
                # Validation should never compute gradients, regardless of fine_tune setting
                with torch.no_grad():
                    _, input_batch_full = self.embedding_space.encoder.encode(
                        val_batch, apply_noise=False
                    )
                    
                    # CRITICAL: Move batch to same device as predictor  
                    # Encoder might be on CPU (force_cpu=True) but predictor is on GPU
                    predictor_device = next(self.predictor.parameters()).device
                    if input_batch_full.device != predictor_device:
                        input_batch_full = input_batch_full.to(predictor_device)
                    
                    input_batch = input_batch_full
                    prediction = self.predictor(input_batch)

                # CRITICAL: Ensure validation_targets are on the same device as prediction
                if prediction.device != validation_targets.device:
                    if not device_mismatch_logged and prediction.device.type == 'cpu' and validation_targets.device.type == 'cuda':
                        logger.warning(f"⚠️  Prediction is on CPU but validation_targets is on GPU - moving targets to CPU")
                        device_mismatch_logged = True
                    validation_targets = validation_targets.to(prediction.device)

                # CRITICAL: Disable autocast for validation loss computation
                # BF16 mixed precision causes dtype mismatches in cross_entropy loss
                # Validation doesn't need mixed precision anyway (no backward pass)
                with torch.amp.autocast('cuda', enabled=False):
                    # Convert to float32 if in mixed precision mode
                    pred_for_loss = prediction.float() if prediction.dtype == torch.bfloat16 else prediction
                    targets_for_loss = validation_targets.long() if validation_targets.dtype != torch.long else validation_targets
                    val_loss = loss_fn(pred_for_loss, targets_for_loss).item()
                
                # Check for NaN/Inf in validation loss
                if torch.isnan(torch.tensor(val_loss)) or torch.isinf(torch.tensor(val_loss)):
                    logger.warning(f"⚠️  NaN/Inf validation loss detected in batch: {val_loss}")
                    logger.warning(f"   Prediction stats: min={prediction.min().item():.4f}, max={prediction.max().item():.4f}")
                    # Use a large but finite value for this batch
                    val_loss = 1e6
                
                # Accumulate loss (weighted by batch size)
                batch_size = len(validation_targets)
                total_loss += val_loss * batch_size
                total_samples += batch_size
                
                # CRITICAL: Explicitly delete batch data to free memory immediately
                del val_batch
                del val_target_token_batch
                del validation_targets
                del input_batch_full
                del input_batch
                del prediction
                del pred_for_loss
                del targets_for_loss
                
                # Periodic GPU cache clearing during validation (every 10 batches)
                if batch_count % 10 == 0:
                    try:
                        if is_gpu_available():
                            empty_gpu_cache()
                    except Exception:
                        pass  # Don't fail validation on cleanup errors
            
            # CRITICAL: Clean up after validation to prevent memory leaks
            gc.collect()
            try:
                if is_gpu_available():
                    empty_gpu_cache()
                    synchronize_gpu()
            except Exception as e:
                logger.debug(f"Failed to clear GPU cache after validation: {e}")

            # Return average loss across all validation samples
            avg_loss = total_loss / total_samples if total_samples > 0 else float('inf')
            return avg_loss

    def has_error_for_metric(self, metric_name):
        return self.metrics_had_error.get(metric_name) is not None

    def handle_metrics_error(self, metric_name, ex):
        existing = self.metrics_had_error.get(metric_name)
        if existing is None:
            # first time!
            edict = {
                "message": "Failed to compute %s: %s" % (metric_name, ex),
                "count": 1,
            }

            logger.warning(
                "Failed to compute %s. Error: %s ... further instances are not logged but counts will be stored in the database."
                % (metric_name, ex)
            )
        else:
            edict = existing
            edict["count"] = edict.get("count", 0) + 1
        self.metrics_had_error[metric_name] = edict
        return

    def clear_binary_metrics_errors(self):
        self.metrics_had_error = {}
        return

    def _find_best_threshold(self, y_ground, y_scores, pos_label):
        """
        Finds the threshold that maximizes the accuracy for binary classification.

        Args:
        y_true (array-like): True binary labels.
        y_scores (array-like): Scores or probabilities associated with the positive class.

        Returns:
        float: The threshold that gives the best accuracy.
        float: The best accuracy achieved with the best threshold.
        """

        y_true = [y_ground[i] == pos_label for i in range(len(y_ground))]

        # Compute FPR, TPR, and thresholds
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)

        # Calculate accuracy for each threshold
        accuracies = [(y_true == (y_scores >= t)).mean() for t in thresholds]

        # Find the threshold that gives the highest accuracy
        max_index = np.argmax(accuracies)
        best_threshold = thresholds[max_index]
        best_accuracy = accuracies[max_index]

        # If y_true contains all 0s, i.e. the predictions y_true are never positive,
        # then the ROC curve will have a single point at (0, 0) and the threshold will be np.inf.
        # We fix this by setting the threshold to 1.0 and the accuracy to 0.0.
        # threshold=1 means everything is negative, so a simple deterministic classifier
        # does a perfect job.
        if best_threshold == np.inf:
            best_threshold = 1.0
            best_accuracy = 1.0

        return best_threshold, best_accuracy

    def strip_queries(self, queries, ground_truth):
        assert len(queries) == len(ground_truth)

        new_q = []
        new_gt = []
        for idx in range(len(queries)):
            gt = ground_truth[idx]
            if gt != gt: #is_nan(gt):
                continue
            new_q.append(queries[idx])
            new_gt.append(ground_truth[idx])
        return new_q, new_gt

    def best_threshold_for_cost(self, y_true, y_prob, cost_fp, cost_fn, 
                                 min_pred_pos_frac=None, max_pred_pos_frac=None, n_thresholds=201):
        """
        Find the optimal threshold that minimizes cost: cost_fp * FP + cost_fn * FN.
        
        This implements the Bayes-optimal decision rule for cost-sensitive binary classification.
        The theoretical optimal threshold is: threshold = C_FP / (C_FP + C_FN)
        
        For example:
        - If C_FN = 2.33 and C_FP = 1.0 (false negatives cost 2.33x more than false positives)
        - Then optimal threshold ≈ 1.0 / (1.0 + 2.33) ≈ 0.30
        - This means: predict positive if P(positive|x) >= 0.30 (not the default 0.50)
        
        This threshold balances the asymmetric costs to minimize expected cost.
        
        Args:
            y_true: Binary ground truth labels (0 or 1)
            y_prob: Predicted probabilities for positive class
            cost_fp: Cost of false positive
            cost_fn: Cost of false negative
            min_pred_pos_frac: Optional minimum predicted positive rate (0.0-1.0)
            max_pred_pos_frac: Optional maximum predicted positive rate (0.0-1.0)
            n_thresholds: Number of thresholds to evaluate (default: 201)
        
        Returns:
            tuple: (optimal_threshold, min_cost, (tp, fp, tn, fn), f1_at_cost_optimal)
        """
        y_true = np.array(y_true)
        y_prob = np.array(y_prob)
        thresholds = np.linspace(0.0, 1.0, num=n_thresholds)
        N = len(y_true)
        
        best_tau = 0.5
        best_cost = float('inf')
        best_stats = None
        
        for tau in thresholds:
            y_pred = (y_prob >= tau).astype(int)
            
            tp = np.sum((y_true == 1) & (y_pred == 1))
            fn = np.sum((y_true == 1) & (y_pred == 0))
            fp = np.sum((y_true == 0) & (y_pred == 1))
            tn = np.sum((y_true == 0) & (y_pred == 0))
            
            pred_pos_rate = (tp + fp) / N if N > 0 else 0.0
            
            # Apply constraints if provided
            if min_pred_pos_frac is not None and pred_pos_rate < min_pred_pos_frac:
                continue
            if max_pred_pos_frac is not None and pred_pos_rate > max_pred_pos_frac:
                continue
            
            cost = cost_fp * fp + cost_fn * fn
            
            if cost < best_cost:
                best_cost = cost
                best_tau = tau
                best_stats = (tp, fp, tn, fn)
        
        # Fallback: if constraints killed all thresholds, ignore constraints
        if best_stats is None:
            for tau in thresholds:
                y_pred = (y_prob >= tau).astype(int)
                tp = np.sum((y_true == 1) & (y_pred == 1))
                fn = np.sum((y_true == 1) & (y_pred == 0))
                fp = np.sum((y_true == 0) & (y_pred == 1))
                tn = np.sum((y_true == 0) & (y_pred == 0))
                cost = cost_fp * fp + cost_fn * fn
                if cost < best_cost:
                    best_cost = cost
                    best_tau = tau
                    best_stats = (tp, fp, tn, fn)
        
        tp, fp, tn, fn = best_stats
        y_pred_best = (y_prob >= best_tau).astype(int)
        f1_best = f1_score(y_true, y_pred_best, zero_division=0)
        
        return float(best_tau), float(best_cost), (int(tp), int(fp), int(tn), int(fn)), float(f1_best)
    
    def best_threshold_for_f1(self, y_true, y_prob, predicted_positive_rate_bounds=None):
        """
        Find the optimal threshold for F1 score using precision-recall curve (optimized).
        
        Args:
            y_true: Binary ground truth labels (0 or 1)
            y_prob: Predicted probabilities for positive class
            predicted_positive_rate_bounds: Optional tuple (min_rate, max_rate) to constrain
                the predicted positive rate. If None, no constraints are applied.
                Example: (0.2, 0.5) means predicted positive rate must be between 20% and 50%.
        
        Returns:
            tuple: (optimal_threshold, optimal_f1_score)
        """
        try:
            # Ensure y_prob is a numpy array for proper comparison
            y_prob = np.array(y_prob)
            y_true = np.array(y_true)
            
            # OPTIMIZATION: Use precision_recall_curve which is already efficient
            p, r, t = precision_recall_curve(y_true, y_prob)
            # PR returns thresholds of len-1 vs p/r; align safely:
            thresholds = t if len(t) > 0 else [0.5]
            
            # OPTIMIZATION: Vectorized F1 calculation using precision and recall from curve
            # F1 = 2 * (precision * recall) / (precision + recall)
            # This avoids calling f1_score in a loop
            f1s = 2 * (p * r) / (p + r + 1e-10)  # Add small epsilon to avoid division by zero
            
            # Also check threshold 1.0 (all negative predictions)
            threshold_1_0_f1 = f1_score(y_true, (y_prob >= 1.0).astype(int), zero_division=0)
            
            # Combine with edge case
            all_f1s = np.concatenate([f1s, [threshold_1_0_f1]])
            all_thresholds = np.concatenate([thresholds, [1.0]])
            
            # Apply constraints on predicted positive rate if provided
            if predicted_positive_rate_bounds is not None:
                min_rate, max_rate = predicted_positive_rate_bounds
                valid_indices = []
                
                for idx, threshold in enumerate(all_thresholds):
                    # Compute predicted positive rate at this threshold
                    pred_pos_rate = (y_prob >= threshold).mean()
                    if min_rate <= pred_pos_rate <= max_rate:
                        valid_indices.append(idx)
                
                if valid_indices:
                    # Only consider thresholds that meet the constraint
                    constrained_f1s = all_f1s[valid_indices]
                    constrained_thresholds = all_thresholds[valid_indices]
                    best_idx = int(np.argmax(constrained_f1s))
                    best_threshold = float(constrained_thresholds[best_idx])
                    best_f1 = float(constrained_f1s[best_idx])
                    
                    # Log constraint info
                    pred_pos_rate = (y_prob >= best_threshold).mean()
                    logger.debug(f"📊 Threshold constraint applied: predicted positive rate {pred_pos_rate:.1%} (bounds: [{min_rate:.1%}, {max_rate:.1%}])")
                    
                    return best_threshold, best_f1
                else:
                    # No threshold meets constraints - fall back to multi-objective optimization
                    logger.warning(f"⚠️  No threshold meets predicted positive rate bounds [{min_rate:.1%}, {max_rate:.1%}]. Using multi-objective optimization.")
                    
                    # Multi-objective: maximize F1 subject to specificity >= 0.6 or accuracy >= argmax_accuracy - 0.05
                    argmax_preds = (y_prob >= 0.5).astype(int)
                    argmax_accuracy = (y_true == argmax_preds).mean()
                    min_accuracy = argmax_accuracy - 0.05
                    
                    best_f1_constrained = -1.0
                    best_threshold_constrained = 0.5
                    
                    for idx, threshold in enumerate(all_thresholds):
                        preds = (y_prob >= threshold).astype(int)
                        f1 = all_f1s[idx]
                        
                        # Compute specificity and accuracy
                        tn = ((y_true == 0) & (preds == 0)).sum()
                        fp = ((y_true == 0) & (preds == 1)).sum()
                        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
                        accuracy = (y_true == preds).mean()
                        
                        # Check constraints: specificity >= 0.6 OR accuracy >= min_accuracy
                        if (specificity >= 0.6 or accuracy >= min_accuracy) and f1 > best_f1_constrained:
                            best_f1_constrained = f1
                            best_threshold_constrained = threshold
                    
                    if best_f1_constrained > 0:
                        logger.info(f"   Multi-objective solution: threshold={best_threshold_constrained:.4f}, F1={best_f1_constrained:.3f}")
                        return float(best_threshold_constrained), float(best_f1_constrained)
                    else:
                        # Last resort: use unconstrained best
                        logger.warning(f"   Multi-objective optimization failed, using unconstrained best threshold")
            
            # No constraints or constraints failed - use unconstrained best
            best_idx = int(np.argmax(all_f1s))
            return float(all_thresholds[best_idx]), float(all_f1s[best_idx])
        except Exception as e:
            logger.warning(f"Error computing best threshold: {e}")
            return 0.5, 0.0
    
    def _compute_baseline_cost(self, y_true, cost_fp, cost_fn):
        """
        Compute baseline cost: always predict negative (no one is bad).
        Cost = FN for all positives, no FP.
        
        Args:
            y_true: Binary ground truth labels (0 or 1)
            cost_fp: Cost of false positive
            cost_fn: Cost of false negative
        
        Returns:
            float: Baseline cost
        """
        y_true = np.array(y_true)
        n_pos = np.sum(y_true == 1)
        cost_all_negative = cost_fn * n_pos  # all positives missed
        return float(cost_all_negative)
    
    def _choose_metric_weights(self, pos_rate):
        """
        Decide α, β, γ weights for composite score based on class prevalence.
        
        Args:
            pos_rate: Positive class rate (0.0-1.0)
        
        Returns:
            tuple: (alpha, beta, gamma) weights for (PR-AUC, cost_savings, ROC-AUC)
        """
        if pos_rate < 0.05:
            # Very rare – lean hard on PR-AUC + cost
            return 0.6, 0.3, 0.1
        elif pos_rate < 0.2:
            # Moderate imbalance
            return 0.5, 0.3, 0.2
        else:
            # Roughly balanced (like credit-g at 30%)
            return 0.4, 0.3, 0.3
    
    def _compute_composite_score(self, metrics, baseline_cost):
        """
        Compute composite score: α * PR-AUC + β * CostSavings + γ * ROC-AUC
        
        Args:
            metrics: dict with keys: roc_auc, pr_auc, cost_min, pos_rate
            baseline_cost: scalar baseline cost for normalization
        
        Returns:
            tuple: (composite_score, score_components_dict)
        """        
        roc_auc = metrics.get("roc_auc", 0.5)
        pr_auc = metrics.get("pr_auc", 0.0)
        cost_min = metrics.get("cost_min", float('inf'))
        pos_rate = metrics.get("pos_rate", 0.5)
        
        # Handle NaNs gracefully
        if np.isnan(roc_auc):
            roc_auc = 0.5
        if np.isnan(pr_auc):
            pr_auc = 0.0
        
        # Normalize cost -> savings in [0, 1]
        # CostSavings = 0 means no better than 'always negative'; 1 means zero cost.
        if baseline_cost > 0:
            cost_savings = (baseline_cost - cost_min) / baseline_cost
        else:
            cost_savings = 0.0
        cost_savings = float(np.clip(cost_savings, 0.0, 1.0))
        
        alpha, beta, gamma = self._choose_metric_weights(pos_rate)
        
        score = (alpha * pr_auc) + (beta * cost_savings) + (gamma * roc_auc)
        
        return float(score), {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "cost_savings": cost_savings,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
        }

    def normalize_types(self, ground_truth, preds, pos_label):
        """Normalize all inputs to the same type for sklearn compatibility"""
        logger.debug(f"🔍 NORMALIZING TYPES:")
        logger.debug(f"   Original pos_label: {pos_label} (type: {type(pos_label)})")
        logger.debug(f"   Original ground_truth sample: {ground_truth[:5]} (types: {[type(gt) for gt in ground_truth[:5]]})")
        logger.debug(f"   Original predictions sample: {preds[:5]} (types: {[type(p) for p in preds[:5]]})")
        
        # Determine the target type based on ground_truth
        if ground_truth:
            gt_sample = ground_truth[0]
            
            # Convert pos_label to match ground_truth type (use numpy types for consistency)
            try:
                if isinstance(gt_sample, (bool, np.bool_)):
                    # Boolean type: convert string to bool
                    if isinstance(pos_label, str):
                        pos_label_normalized = pos_label.lower() in ('true', '1', 'yes', 't', 'y')
                    else:
                        pos_label_normalized = bool(pos_label)
                elif isinstance(gt_sample, (int, float, np.integer, np.floating)):
                    pos_label_normalized = np.float64(pos_label)
                elif isinstance(gt_sample, str):
                    pos_label_normalized = str(pos_label)
                else:
                    pos_label_normalized = pos_label
            except (ValueError, TypeError):
                pos_label_normalized = str(pos_label)
            
            # Convert predictions to match ground_truth type (use numpy types for consistency)
            preds_normalized = []
            for pred in preds:
                try:
                    if isinstance(gt_sample, (bool, np.bool_)):
                        # Boolean type: convert string to bool
                        if isinstance(pred, str):
                            preds_normalized.append(pred.lower() in ('true', '1', 'yes', 't', 'y'))
                        else:
                            preds_normalized.append(bool(pred))
                    elif isinstance(gt_sample, (int, float, np.integer, np.floating)):
                        preds_normalized.append(np.float64(pred))
                    elif isinstance(gt_sample, str):
                        preds_normalized.append(str(pred))
                    else:
                        preds_normalized.append(pred)
                except (ValueError, TypeError):
                    preds_normalized.append(str(pred))
            
            logger.debug(f"   Normalized pos_label: {pos_label_normalized} (type: {type(pos_label_normalized)})")
            logger.debug(f"   Normalized predictions sample: {preds_normalized[:5]} (types: {[type(p) for p in preds_normalized[:5]]})")
            logger.debug(f"   Unique normalized ground_truth: {set(ground_truth)}")
            logger.debug(f"   Unique normalized predictions: {set(preds_normalized)}")
            
            return ground_truth, preds_normalized, pos_label_normalized
        else:
            return ground_truth, preds, pos_label

    def validate_metrics_inputs(self, ground_truth, preds, pos_label):
        """Validate inputs before calling sklearn metrics to catch issues early"""
        logger.debug(f":mag: VALIDATING METRICS INPUTS:")
        logger.debug(f"   pos_label: {pos_label} (type: {type(pos_label)})")
        logger.debug(f"   ground_truth sample: {ground_truth[:5]} (types: {[type(gt) for gt in ground_truth[:5]]})")
        logger.debug(f"   predictions sample: {preds[:5]} (types: {[type(p) for p in preds[:5]]})")
        logger.debug(f"   unique ground_truth values: {set(ground_truth)}")
        logger.debug(f"   unique prediction values: {set(preds)}")
        logger.debug(f"   pos_label in ground_truth: {pos_label in ground_truth}")
        logger.debug(f"   pos_label in predictions: {pos_label in preds}")

        # Check for type mismatches
        if ground_truth and preds:
            gt_sample = ground_truth[0]
            pred_sample = preds[0]

            if type(pos_label) != type(gt_sample):
                logger.debug(f":warning:  TYPE MISMATCH: pos_label is {type(pos_label)} but ground_truth contains {type(gt_sample)}")
                logger.debug(f"   pos_label: {pos_label}")
                logger.debug(f"   ground_truth sample: {gt_sample}")

            if type(gt_sample) != type(pred_sample):
                logger.debug(f":warning:  TYPE MISMATCH: ground_truth is {type(gt_sample)} but predictions contain {type(pred_sample)}")

        # Check if pos_label exists in data
        if pos_label not in ground_truth:
            logger.debug(f":warning:  pos_label '{pos_label}' {type(pos_label)} not found in ground_truth values: {set(ground_truth)}")

        if pos_label not in preds:
            logger.debug(f":warning:  pos_label '{pos_label}' not found in predictions: {set(preds)}")
            logger.debug(f"   This will cause 'Precision is ill-defined' warnings")

        return True

    def compute_metrics_at_threshold(self, y_true_binary, pos_probs_array, threshold, pos_label=None, neg_label=None):
        """
        Compute ALL threshold-dependent metrics in one place.
        
        This prevents "one metric left behind" bugs by ensuring all metrics
        that depend on the threshold are computed together from the same
        confusion matrix.
        
        Args:
            y_true_binary: np.array of 0/1 ground truth labels
            pos_probs_array: np.array of predicted probabilities for positive class
            threshold: float, decision threshold
            pos_label: optional, label for positive class (for prediction distribution)
            neg_label: optional, label for negative class (for prediction distribution)
            
        Returns:
            dict with all threshold-dependent metrics:
            - confusion_matrix: {tp, fp, tn, fn}
            - precision, recall, f1
            - accuracy
            - specificity (TNR)
            - balanced_accuracy
            - mcc
            - prediction_distribution: {pos_label: count, neg_label: count}
        """
        import warnings
        from sklearn.metrics import (
            precision_score, recall_score, f1_score, 
            confusion_matrix, matthews_corrcoef
        )
        
        # Apply threshold to get predictions
        preds = (pos_probs_array >= threshold).astype(int)
        
        # Compute confusion matrix
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tn, fp, fn, tp = confusion_matrix(y_true_binary, preds).ravel()
            
            # Core metrics
            precision = precision_score(y_true_binary, preds, zero_division=0)
            recall = recall_score(y_true_binary, preds, zero_division=0)
            f1 = f1_score(y_true_binary, preds, zero_division=0)
        
        # Derived metrics - all computed from the SAME confusion matrix
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate
        balanced_accuracy = (recall + specificity) / 2.0
        mcc = matthews_corrcoef(y_true_binary, preds)
        
        # Prediction distribution
        pred_pos_count = int(preds.sum())
        pred_neg_count = len(preds) - pred_pos_count
        
        result = {
            # Confusion matrix
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn),
            # Core metrics
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            # Derived metrics
            'accuracy': float(accuracy),
            'specificity': float(specificity),
            'balanced_accuracy': float(balanced_accuracy),
            'mcc': float(mcc),
            # Threshold info
            'threshold': float(threshold),
            # Prediction distribution
            'pred_pos_count': pred_pos_count,
            'pred_neg_count': pred_neg_count,
            'pred_pos_rate': pred_pos_count / len(preds) if len(preds) > 0 else 0,
        }
        
        # Add labeled distribution if labels provided
        if pos_label is not None and neg_label is not None:
            result['prediction_distribution'] = {
                str(pos_label): pred_pos_count,
                str(neg_label): pred_neg_count,
            }
        
        return result

    def detect_training_failure_mode(self, raw_logits_array, pos_probs_array, pred_counts, 
                                      y_true_binary, auc, accuracy, optimal_threshold, epoch_idx, n_epochs=None, log_prefix=""):
        """
        Detect and diagnose training failure modes.
        Returns: (failure_detected: bool, failure_label: str, recommendations: list)
        
        Args:
            epoch_idx: current epoch number
            n_epochs: total number of epochs (used to skip diagnostics if too early)
            log_prefix: prefix to include in all log messages (e.g., "epoch=N, target=col: ")
        """
        
        # Skip diagnostics until we're at least 5% through training or past epoch 5
        min_epoch_threshold = max(5, int(n_epochs * 0.05)) if n_epochs else 5
        log_prefix = self._get_log_prefix(epoch_idx)
        if epoch_idx < min_epoch_threshold:
            logger.debug(f"{log_prefix}Skipping failure diagnostics - waiting until epoch {min_epoch_threshold} ({min_epoch_threshold/n_epochs*100:.1f}% complete)")
            return False, "TOO_EARLY", []
        
        failures = []
        recommendations = []
        
        # Calculate key statistics
        prob_std = pos_probs_array.std()
        prob_range = pos_probs_array.max() - pos_probs_array.min()
        prob_mean = pos_probs_array.mean()
        
        # Count predictions near decision boundary (0.4-0.6)
        near_boundary = np.sum((pos_probs_array >= 0.4) & (pos_probs_array <= 0.6))
        pct_near_boundary = near_boundary / len(pos_probs_array) * 100
        
        # Get class imbalance in predictions
        total_preds = sum(pred_counts.values())
        max_pred_pct = max(pred_counts.values()) / total_preds * 100 if total_preds > 0 else 0
        
        # Get class imbalance in ground truth
        pos_count = sum(y_true_binary)
        true_pos_pct = pos_count / len(y_true_binary) * 100
        
        # Raw logits analysis
        logits_std = raw_logits_array.std() if raw_logits_array is not None else None
        logits_range = (raw_logits_array.max() - raw_logits_array.min()) if raw_logits_array is not None else None
        
        # FAILURE MODE 1: Dead Network (Raw logits have no variation)
        if logits_std is not None and logits_std < 0.01:
            failures.append("DEAD_NETWORK")
            recommendations.extend([
                "🔥 CRITICAL: Network outputs are frozen (std < 0.01)",
                "   → STOP TRAINING - Network is not learning",
                "   → Check if gradients are flowing (may need gradient logging)",
                "   → Increase learning rate by 10x and restart",
                "   → Verify embedding space is producing varied embeddings",
                "   → Check for NaN/Inf in loss or gradients"
            ])
        
        # FAILURE MODE 2: Constant Probability Output
        elif prob_std < 0.03 or prob_range < 0.05:
            failures.append("CONSTANT_PROBABILITY")
            
            # Determine what action will be taken based on epoch
            abort_threshold_epoch = max(1, int(n_epochs * 0.25)) if n_epochs else None
            
            if epoch_idx < 5:
                action_msg = "   → No action (too early - need epoch 5+)"
            elif abort_threshold_epoch and epoch_idx < abort_threshold_epoch:
                action_msg = f"   → WILL increase LR by 5x (up to 2 times if problem persists, capped at 0.01 max). Will abort at epoch {abort_threshold_epoch}+ (25% of {n_epochs} epochs) if prob_std not growing"
            elif abort_threshold_epoch:
                action_msg = f"   → MAY abort training (epoch {epoch_idx} >= {abort_threshold_epoch}, but only if prob_std not growing and wasn't stuck from beginning)"
            else:
                action_msg = "   → WILL increase LR by 5x (up to 2 times if problem persists, capped at 0.01 max). Will abort at 25% of total epochs if prob_std not growing"
            
            recommendations.extend([
                f"⚠️  WARNING: Model produces nearly identical probabilities (std={prob_std:.4f}, range={prob_range:.4f})",
                action_msg,
                f"   → Loss decreasing: Check if model is stuck in flat region",
                "   → Input embeddings: Verify they have sufficient variation"
            ])
        
        # FAILURE MODE 3: Always Predicts One Class
        elif max_pred_pct > 95:
            dominant_class = max(pred_counts, key=pred_counts.get)
            failures.append("SINGLE_CLASS_BIAS")
            recommendations.extend([
                f"⚠️  WARNING: Model predicts '{dominant_class}' {max_pred_pct:.1f}% of the time",
                f"   → Ground truth is {true_pos_pct:.1f}% positive class",
                "   → If classes are imbalanced in data, this may be expected initially",
                "   → Consider using class weights in loss function",
                "   → May need to train longer to learn minority class",
                f"   → Optimal threshold is {optimal_threshold:.3f} - very extreme suggests poor calibration"
            ])
        
        # FAILURE MODE 4: Random Predictions (AUC ~0.5)
        elif auc < 0.55:
            failures.append("RANDOM_PREDICTIONS")
            recommendations.extend([
                f"⚠️  WARNING: Model is guessing randomly (AUC={auc:.3f})",
                "   → Network has not learned to discriminate between classes",
                f"   → At epoch {epoch_idx}, may need significantly more training",
                "   → Verify embedding space is trained and meaningful",
                "   → Check if target column has predictive signal in the data",
                "   → Consider checking feature importance/correlations"
            ])
        
        # FAILURE MODE 5: Clustered Near Decision Boundary
        # Only check after epoch 10 - early epochs often show uncertainty as model is still learning
        elif pct_near_boundary > 70 and epoch_idx >= 10:
            failures.append("UNDERCONFIDENT")
            recommendations.extend([
                f"⚠️  WARNING: {pct_near_boundary:.1f}% of predictions are between 0.4-0.6",
                "   → Model is very uncertain/underconfident",
                f"   → May need more training (currently at epoch {epoch_idx})",
                "   → Consider if validation set is too different from training",
                "   → This can also indicate the problem is genuinely difficult"
            ])
        
        # FAILURE MODE 6: Poor Performance Despite Good Variation
        elif auc < 0.65 and accuracy < 0.6 and prob_std > 0.1:
            failures.append("POOR_DISCRIMINATION")
            recommendations.extend([
                f"⚠️  WARNING: Model has variation (std={prob_std:.3f}) but poor metrics (AUC={auc:.3f})",
                "   → Network is producing varied outputs but wrong predictions",
                "   → May be learning spurious patterns",
                "   → Check if training loss is decreasing properly",
                "   → Consider data quality or feature engineering issues"
            ])
        
        # SUCCESS: Model seems to be learning
        elif auc > 0.7 and prob_std > 0.1:
            return False, "HEALTHY", ["✅ Model appears to be learning normally"]
        
        # Log all detected failures
        if failures:
            failure_label = "_".join(failures)
            logger.warning(f"{log_prefix}" + "=" * 80)
            logger.warning(f"{log_prefix}🚨 TRAINING FAILURE DETECTED: {failure_label}")
            logger.warning(f"{log_prefix}" + "=" * 80)
            for rec in recommendations:
                logger.warning(f"{log_prefix}{rec}")
            logger.warning(f"{log_prefix}" + "=" * 80)
            
            # Record the warning
            self.record_training_warning(
                warning_type=failure_label,
                epoch=epoch_idx if epoch_idx is not None else -1,
                details={
                    "auc": auc,
                    "accuracy": accuracy,
                    "optimal_threshold": optimal_threshold,
                    "recommendations": recommendations,
                    "prediction_distribution": dict(pred_counts) if pred_counts else {}
                }
            )
            
            return True, failure_label, recommendations
        
        return False, "UNKNOWN", []

    def compute_classification_metrics(self, queries, ground_truth, pos_label, epoch_idx=0, n_epochs=None):
        """Compute classification metrics for both binary and multi-class problems.

        Args:
            queries: list of queries
            ground_truth: list of ground truth labels
            pos_label: label of the positive class (for binary) or main class (for multi-class)
            epoch_idx: current epoch number (for failure detection)
            n_epochs: total number of epochs (for failure detection)
        """
        if self.run_binary_metrics == False:
            return {}
        
        # Skip metrics computation for scalar/regression targets
        if not isinstance(self.target_codec, (SetEncoder, SetCodec)):
            return {}
        
        is_binary = self.should_compute_binary_metrics()
        
        log_prefix = self._get_log_prefix(epoch_idx)
        logger.info(f"{log_prefix}Computing {'binary' if is_binary else 'multi-class'} classification metrics")
        
        # Get actual training classes (excluding <UNKNOWN> which is removed from training)
        actual_classes = [m for m in self.target_codec.members if m != "<UNKNOWN>"]
        n_classes = len(actual_classes)
        
        # Build distribution string if we have class_distribution data
        dist_str = ""
        unknown_str = ""
        if self.class_distribution and 'total' in self.class_distribution:
            class_counts = []
            for cls in actual_classes:
                count = self.class_distribution['total'].get(str(cls), 0)
                class_counts.append(f"{cls}={count}")
            dist_str = " [" + ", ".join(class_counts) + "]"
            
            # Show unknown/null count
            unknown_count = self.class_distribution['total'].get("<UNKNOWN>", 0)
            unknown_str = f" + {unknown_count} unknowns [nulls]"
        
        logger.info(f"{log_prefix}Training classes: n={n_classes}{dist_str}{unknown_str}")

        # print(f"...compute_binary_metrics ... type(queries) = {type(queries)}... {type(queries[0])}")
        # print(f"...compute_binary_metrics ... type(ground_truth) = {type(ground_truth)}")
        # print(f"...compute_binary_metrics ... type(pos_label) = {type(pos_label)}.. pos_label = {pos_label}")

        queries, ground_truth = self.strip_queries(queries=queries, ground_truth=ground_truth)

        # print(f"pos_label = {pos_label}; type = {type(pos_label)}")
        if pos_label != pos_label:
            return {
                "accuracy": -1,
                "precision": -1,
                "recall": -1,
                "auc": -1,
                "_had_error": True,
                "metrics_secs": -1,
                "_reason": "pos_label is None",
            }

        # Put the model in eval model for evaluation, but save the entry training state
        # so it can be restored at exit.
        with PredictorEvalModeContextManager(fsp=self, debugLabel="compute_classification_metrics"):
            # ASSERT: We must be in eval mode for metrics computation
            assert self.predictor.training == False, f"❌ METRICS BUG: predictor should be in eval mode but training={self.predictor.training}"
            assert self.embedding_space.encoder.training == False, f"❌ METRICS BUG: encoder should be in eval mode but training={self.embedding_space.encoder.training}"
            logger.debug("✓ compute_classification_metrics: Models correctly in EVAL mode")
            
            # Log BatchNorm statistics at the start of metrics computation (only on first few epochs)
            if epoch_idx is not None and epoch_idx <= 3:
                # self.predictor is nn.Sequential(predictor_base, final_layer)
                # We need to access predictor_base (SimpleMLP) to get log_batchnorm_stats
                if hasattr(self.predictor_base, 'log_batchnorm_stats'):
                    logger.info(f"🔍 BatchNorm Stats at Epoch {epoch_idx} (EVAL MODE):")
                    self.predictor_base.log_batchnorm_stats()
                else:
                    logger.warning(f"⚠️  predictor_base ({type(self.predictor_base)}) doesn't have log_batchnorm_stats method")
            
            ts = time.time()
            if queries is None:
                queries = []

            f1 = 0
            accuracy = 0
            precision = 0
            recall = 0
            auc = 0
            
            # Multi-class specific metrics
            macro_f1 = 0
            weighted_f1 = 0

            # OPTIMIZATION: Use batched prediction instead of sequential predict() calls
            # This provides 10-100x speedup by processing all queries in GPU batches
            results = []
            raw_logits_list = []  # Track raw model outputs before softmax
            
            if not queries:
                return {}
            
            # Use internal batching logic for maximum performance
            try:
                import pandas as pd
                from torch.utils.data import DataLoader
                from featrix.neural.data_frame_data_set import SuperSimpleSelfSupervisedDataset, collate_tokens
                
                # Process queries in batches for GPU efficiency
                batch_size = 256  # Same as predict_batch default
                total_batches = (len(queries) + batch_size - 1) // batch_size
                
                for batch_start in range(0, len(queries), batch_size):
                    batch_end = min(batch_start + batch_size, len(queries))
                    batch_queries = queries[batch_start:batch_end]
                    
                    # Convert queries to DataFrame for batching
                    batch_df = pd.DataFrame(batch_queries)
                    
                    # Create dataset and dataloader for efficient batching
                    dataset = SuperSimpleSelfSupervisedDataset(batch_df, self.all_codecs)
                    dataloader = DataLoader(
                        dataset,
                        batch_size=len(batch_df),  # Process entire batch at once
                        shuffle=False,
                        collate_fn=collate_tokens,
                    )
                    
                    # Get the single batch
                    column_batch = next(iter(dataloader))
                    
                    # Move data to same device as encoder
                    encoder_device = next(self.embedding_space.encoder.parameters()).device
                    for key, tokenbatch in column_batch.items():
                        column_batch[key] = tokenbatch.to(encoder_device)
                    
                    # Remove target column if present (for marginal encoding)
                    if self.target_col_name in column_batch:
                        target_token_batch = column_batch.pop(self.target_col_name)
                        
                        # Add marginal tokens if target was in original embedding space
                        if self.target_col_name in self.embedding_space.col_codecs:
                            marginal_token_batch = self._create_marginal_token_batch_for_target(target_token_batch)
                            column_batch[self.target_col_name] = marginal_token_batch
                    
                    # Encode the entire batch at once - MASSIVE SPEEDUP!
                    # CRITICAL: Use no_grad() during metrics computation to prevent building computation graphs
                    # Metrics should never compute gradients, regardless of fine_tune setting
                    with torch.no_grad():
                        _, batch_encoding = self.embedding_space.encoder.encode(column_batch, apply_noise=False)
                        
                        # Move batch_encoding to same device as predictor
                        predictor_device = next(self.predictor.parameters()).device
                        batch_encoding = batch_encoding.to(predictor_device)
                        
                        # Run predictor on entire batch
                        batch_output = self.predictor(batch_encoding)  # Raw logits [batch_size, num_classes]
                    
                    # Extract raw logits before softmax (for diagnostics)
                    raw_logits_batch = batch_output.detach().cpu().numpy()
                    raw_logits_list.extend([raw_logits_batch[i] for i in range(len(batch_queries))])
                    
                    # Convert batch output to individual predictions
                    for i in range(len(batch_queries)):
                        single_output = batch_output[i:i+1]  # Keep batch dimension
                        prediction = self._convert_output_to_prediction(single_output)
                        
                        if type(prediction) != dict:
                            # not a classifier.
                            return {}
                        results.append(prediction)
                        
            except Exception as e:
                logger.warning(f"Batched prediction failed, falling back to sequential: {e}")
                logger.debug(f"  Full traceback:\n{traceback.format_exc()}")
                # Fallback to old method if batching fails
                for q in queries:
                    try:
                        prediction = self.predict(q, ignore_unknown=True, debug_print=False)
                        if type(prediction) != dict:
                            return {}
                        results.append(prediction)
                        # For fallback, we skip raw_logits extraction to save time
                    except Exception as e2:
                        def short_dict(d):
                            dd = {}
                            if d is None:
                                return "None"
                            for k, v in d.items():
                                v = str(v)
                                if len(v) > 32:
                                    v = v[:32] + "..."
                                dd[k] = v
                            return dd
                        
                        # Rate-limited logging: only log full details for first 1-2 failures per 10 minutes
                        if _should_log_prediction_failure():
                            logger.warning(f"PREDICTION FAILED: q = {short_dict(q)}")
                            logger.warning(f"  Exception: {type(e2).__name__}: {str(e2)}")
                            logger.debug(f"  Full traceback:\n{traceback.format_exc()}")
                        else:
                            # Just log a brief message without the full query
                            logger.debug(f"PREDICTION FAILED (rate limited): {type(e2).__name__}: {str(e2)[:100]}")
            
            # DIAGNOSTIC: Log raw logits distribution - ALWAYS log to detect issues
            if raw_logits_list and len(raw_logits_list) > 0:
                raw_logits_array = np.vstack(raw_logits_list)
                logit_std = raw_logits_array.std()
                logit_range = raw_logits_array.max() - raw_logits_array.min()
                
                logger.debug(f"{log_prefix}📊 RAW LOGITS (before softmax):")
                logger.debug(f"{log_prefix}   Shape: {raw_logits_array.shape}")
                logger.debug(f"{log_prefix}   Min: {raw_logits_array.min():.4f}, Max: {raw_logits_array.max():.4f}")
                logger.debug(f"{log_prefix}   Mean: {raw_logits_array.mean():.4f}, Std: {logit_std:.4f}, Range: {logit_range:.4f}")
                
                if raw_logits_array.shape[1] >= 2:
                    # For binary or multi-class, show per-class stats
                    for class_idx in range(min(3, raw_logits_array.shape[1])):  # Limit to 3 classes for brevity
                        class_logits = raw_logits_array[:, class_idx]
                        logger.info(f"{log_prefix}   Class {class_idx}: mean={class_logits.mean():.4f}, std={class_logits.std():.4f}")
                
                # Warn if logits are suspiciously large (>100 often leads to numerical issues)
                if abs(raw_logits_array).max() > 100:
                    logger.warning(f"{log_prefix}⚠️  Large logits detected (max abs value: {abs(raw_logits_array).max():.1f})")
                    logger.warning(f"{log_prefix}   Values >100 may cause numerical instability")
                    logger.warning(f"{log_prefix}   Consider reducing LR or adding regularization")
                
                # Check if logits are suspiciously constant (keep as ERROR for important issues)
                if raw_logits_array.std() < 0.01:
                    logger.error(f"🚨 RAW LOGITS ARE NEARLY CONSTANT (std={raw_logits_array.std():.6f})")
                    logger.error("   This suggests the model is not learning properly")
                    if hasattr(self.predictor_base, 'log_batchnorm_stats'):
                        logger.error("   Logging BatchNorm stats to diagnose:")
                        self.predictor_base.log_batchnorm_stats()
                    else:
                        logger.error(f"   predictor_base ({type(self.predictor_base)}) doesn't have log_batchnorm_stats")

            # DIAGNOSTIC: Dump validation probabilities to file for inspection
            # This helps diagnose issues where probabilities seem "too even"
            if results and len(results) > 0:
                try:
                    # CRITICAL: Validate format - MUST have 'probabilities' key
                    if 'probabilities' not in results[0]:
                        raise RuntimeError(
                            f"❌ CRITICAL: Prediction results MUST have 'probabilities' key (new format). "
                            f"Got keys: {list(results[0].keys())}. "
                            f"Expected format: {{'probabilities': {{class: prob, ...}}}}. "
                            f"Sample: {results[0]}"
                        )
                    
                    # Compute probability statistics - NEW FORMAT ONLY
                    all_probs = []
                    for r in results:
                        if 'probabilities' not in r:
                            raise RuntimeError(
                                f"❌ CRITICAL: All results must have 'probabilities' key. "
                                f"Found result without it: {r}"
                            )
                        probs = list(r['probabilities'].values())
                        all_probs.append(probs)
                    
                    all_probs_array = np.array(all_probs)
                    n_classes = all_probs_array.shape[1] if len(all_probs_array.shape) > 1 else 1
                    
                    # Compute entropy per sample (higher = more uncertain/even)
                    # Entropy = -sum(p * log(p)) for each sample
                    eps = 1e-10
                    entropies = -np.sum(all_probs_array * np.log(all_probs_array + eps), axis=1)
                    max_entropy = np.log(n_classes)  # Maximum entropy for uniform distribution
                    normalized_entropies = entropies / max_entropy if max_entropy > 0 else entropies
                    
                    # Log probability statistics
                    logger.info(f"{log_prefix}📊 VALIDATION PROBABILITY STATISTICS:")
                    logger.info(f"{log_prefix}   N samples: {len(results)}, N classes: {n_classes}")
                    logger.info(f"{log_prefix}   Prob min: {all_probs_array.min():.4f}, max: {all_probs_array.max():.4f}")
                    logger.info(f"{log_prefix}   Prob mean: {all_probs_array.mean():.4f}, std: {all_probs_array.std():.4f}")
                    logger.info(f"{log_prefix}   Entropy: mean={entropies.mean():.4f}, min={entropies.min():.4f}, max={entropies.max():.4f}")
                    logger.info(f"{log_prefix}   Normalized entropy: mean={normalized_entropies.mean():.4f} (1.0 = uniform)")
                    
                    # Per-class probability statistics - NEW FORMAT ONLY
                    class_labels = list(results[0]['probabilities'].keys())
                    for i, label in enumerate(class_labels[:5]):  # Limit to 5 classes for brevity
                        class_probs = all_probs_array[:, i]
                        logger.info(f"{log_prefix}   Class '{label}': mean={class_probs.mean():.4f}, std={class_probs.std():.4f}, "
                                    f"min={class_probs.min():.4f}, max={class_probs.max():.4f}")
                    
                    # Warn if probabilities are suspiciously even
                    if normalized_entropies.mean() > 0.9:
                        logger.warning(f"{log_prefix}⚠️  PROBABILITIES ARE VERY EVEN (normalized entropy={normalized_entropies.mean():.3f})")
                        logger.warning(f"{log_prefix}   Model may not be learning to discriminate between classes")
                    elif normalized_entropies.mean() > 0.8:
                        logger.warning(f"{log_prefix}⚠️  Probabilities are somewhat even (normalized entropy={normalized_entropies.mean():.3f})")
                    
                    # Dump to file if output_dir is available
                    if hasattr(self, '_output_dir') and self._output_dir:
                        dump_path = Path(self._output_dir) / f"validation_probs_epoch_{epoch_idx:03d}.json"
                        dump_data = {
                            "epoch": epoch_idx,
                            "n_samples": len(results),
                            "n_classes": n_classes,
                            "class_labels": class_labels,
                            "stats": {
                                "prob_min": float(all_probs_array.min()),
                                "prob_max": float(all_probs_array.max()),
                                "prob_mean": float(all_probs_array.mean()),
                                "prob_std": float(all_probs_array.std()),
                                "entropy_mean": float(entropies.mean()),
                                "entropy_min": float(entropies.min()),
                                "entropy_max": float(entropies.max()),
                                "normalized_entropy_mean": float(normalized_entropies.mean()),
                            },
                            "per_class_stats": {
                                str(label): {
                                    "mean": float(all_probs_array[:, i].mean()),
                                    "std": float(all_probs_array[:, i].std()),
                                    "min": float(all_probs_array[:, i].min()),
                                    "max": float(all_probs_array[:, i].max()),
                                }
                                for i, label in enumerate(class_labels)
                            },
                            # Include first 100 samples for detailed inspection - NEW FORMAT ONLY
                            "sample_probs": [
                                {str(k): float(v) for k, v in r['probabilities'].items()}
                                for r in results[:100]
                            ],
                            "sample_ground_truth": [str(gt) for gt in ground_truth[:100]] if ground_truth else [],
                            "sample_entropies": [float(e) for e in entropies[:100]],
                        }
                        with open(dump_path, 'w') as f:
                            json.dump(dump_data, f, indent=2)
                        logger.info(f"{log_prefix}📁 Validation probs dumped to: {dump_path}")
                        
                except Exception as e:
                    logger.error(f"{log_prefix}❌ Failed to compute probability statistics: {e}")
                    raise RuntimeError(f"Failed to compute probability statistics during validation: {e}") from e

            if isinstance(self.target_codec, (SetEncoder, SetCodec)):
                # CRITICAL: Normalize pos_label to match actual prediction dict keys
                # The prediction dict keys come from the codec's detokenize output, which may
                # have different types/values than the original pos_label from validation data
                if results and len(results) > 0:
                    # Get the actual keys from prediction dicts - NEW FORMAT ONLY
                    if 'probabilities' not in results[0]:
                        raise RuntimeError(
                            f"❌ CRITICAL: results[0] must have 'probabilities' key. "
                            f"Got keys: {list(results[0].keys())}. Sample: {results[0]}"
                        )
                    prediction_keys = set(results[0]['probabilities'].keys())
                    
                    # First, try exact match
                    if pos_label not in prediction_keys:
                        # Try string conversion
                        pos_label_str = str(pos_label)
                        if pos_label_str in prediction_keys:
                            logger.info(f"🔧 Normalized pos_label: {pos_label!r} -> {pos_label_str!r} to match prediction dict keys")
                            pos_label = pos_label_str
                        else:
                            # Use distribution metadata to find the minority class (positive class)
                            # The positive label is the minority class, and we can use the distribution
                            # percentages to determine which codec member corresponds to it
                            matched_via_distribution = False
                            if hasattr(self, 'distribution_metadata') and self.distribution_metadata:
                                minority_class = self.distribution_metadata.get('minority_class')
                                train_class_ratios = self.distribution_metadata.get('train_class_ratios', {})
                                
                                # Check if pos_label matches the minority class from training
                                if minority_class is not None:
                                    # Try to match pos_label to minority_class (with type/string conversion)
                                    if (pos_label == minority_class or 
                                        str(pos_label) == str(minority_class) or
                                        (hasattr(self.target_codec, 'encode') and 
                                         hasattr(self.target_codec, 'decode') and
                                         self.target_codec.encode(pos_label) == self.target_codec.encode(minority_class))):
                                        
                                        # pos_label is the minority class, now find which codec member has smallest percentage
                                        # The minority class should map to the codec member with smallest percentage
                                        if train_class_ratios and hasattr(self.target_codec, 'members'):
                                            codec_members = self.target_codec.members
                                            # Find which codec member has the smallest percentage in training
                                            min_percentage = float('inf')
                                            minority_codec_member = None
                                            
                                            for member in codec_members:
                                                if member == "<UNKNOWN>":
                                                    continue
                                                # Try to find this member's percentage in training data
                                                # Check both direct match and string conversion
                                                member_percentage = None
                                                for train_class, ratio in train_class_ratios.items():
                                                    if (member == train_class or 
                                                        str(member) == str(train_class) or
                                                        (hasattr(self.target_codec, 'encode') and 
                                                         hasattr(self.target_codec, 'decode') and
                                                         self.target_codec.encode(member) == self.target_codec.encode(train_class))):
                                                        member_percentage = ratio
                                                        break
                                                
                                                # If we found a percentage and it's the smallest, use it
                                                if member_percentage is not None and member_percentage < min_percentage:
                                                    min_percentage = member_percentage
                                                    minority_codec_member = member
                                            
                                            # Use the codec member with smallest percentage
                                            if minority_codec_member and minority_codec_member in prediction_keys:
                                                logger.info(f"🔧 Mapped pos_label {pos_label!r} (minority class) -> {minority_codec_member!r} (smallest % in training: {min_percentage*100:.1f}%)")
                                                pos_label = minority_codec_member
                                                matched_via_distribution = True
                            
                            # If distribution mapping didn't work, check if pos_label is in codec members
                            if not matched_via_distribution:
                                codec_members = None
                                if hasattr(self.target_codec, 'members'):
                                    codec_members = self.target_codec.members
                                    # Check if pos_label is directly in the codec's vocabulary
                                    if pos_label in codec_members:
                                        if pos_label in prediction_keys:
                                            logger.info(f"🔧 pos_label {pos_label!r} is in codec members and prediction keys - using directly")
                                            # Already matches, no change needed
                                        elif str(pos_label) in prediction_keys:
                                            logger.info(f"🔧 Normalized pos_label: {pos_label!r} -> {str(pos_label)!r} (string conversion)")
                                            pos_label = str(pos_label)
                                        else:
                                            logger.error(f"❌ pos_label {pos_label!r} is in codec members but not in prediction keys: {prediction_keys}")
                                            raise ValueError(f"pos_label {pos_label!r} not found in prediction keys: {prediction_keys}")
                            
                            # If pos_label is not in codec members, or still not matched, try tokens_to_members
                            if pos_label not in prediction_keys and str(pos_label) not in prediction_keys:
                                if hasattr(self.target_codec, 'tokens_to_members'):
                                    codec_values = list(self.target_codec.tokens_to_members.values())
                                    # Try to find a codec value that matches pos_label (with type conversion)
                                    matched_key = None
                                    for codec_val in codec_values:
                                        if codec_val == pos_label:
                                            matched_key = codec_val
                                            break
                                        # Try string comparison
                                        if str(codec_val) == str(pos_label):
                                            matched_key = codec_val
                                            break
                                        # Try type conversion
                                        try:
                                            if type(pos_label)(codec_val) == pos_label:
                                                matched_key = codec_val
                                                break
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if matched_key and matched_key in prediction_keys:
                                        logger.info(f"🔧 Normalized pos_label: {pos_label!r} -> {matched_key!r} to match prediction dict keys")
                                        pos_label = matched_key
                                    elif matched_key:
                                        logger.error(f"❌ Found matching codec value {matched_key!r} for pos_label {pos_label!r}, but it's not in prediction keys: {prediction_keys}")
                                        raise ValueError(f"Codec value {matched_key!r} for pos_label {pos_label!r} not found in prediction keys: {prediction_keys}")
                                    else:
                                        # Last resort: try encoding pos_label through the codec to see what it maps to
                                        # This handles cases where pos_label is a raw value that gets encoded/decoded
                                        try:
                                            if hasattr(self.target_codec, 'encode') and hasattr(self.target_codec, 'decode'):
                                                # Try encoding pos_label to see what token it gets
                                                encoded = self.target_codec.encode(pos_label)
                                                if encoded is not None:
                                                    # Decode it back to see what value it produces
                                                    decoded = self.target_codec.decode(encoded)
                                                    if decoded in prediction_keys:
                                                        logger.info(f"🔧 Normalized pos_label: {pos_label!r} -> {decoded!r} via codec encode/decode")
                                                        pos_label = decoded
                                                    elif str(decoded) in prediction_keys:
                                                        logger.info(f"🔧 Normalized pos_label: {pos_label!r} -> {str(decoded)!r} via codec encode/decode (string)")
                                                        pos_label = str(decoded)
                                        except Exception as e:
                                            logger.debug(f"Could not encode/decode pos_label through codec: {e}")
                                        
                                        if pos_label not in prediction_keys and str(pos_label) not in prediction_keys:
                                            logger.warning(f"⚠️  Could not find matching key for pos_label {pos_label!r} in prediction keys: {prediction_keys}")
                                            if codec_members:
                                                logger.warning(f"   Codec members: {codec_members}")
                                            logger.warning(f"   Codec values (tokens_to_members): {codec_values}")
                                else:
                                    logger.warning(f"⚠️  pos_label {pos_label!r} not in prediction keys: {prediction_keys}")
                                    if codec_members:
                                        logger.warning(f"   Codec members: {codec_members}")
                                    logger.warning(f"   target_codec doesn't have tokens_to_members attribute")
                
                # Ensure pos_label matches the data type in ground_truth (for sklearn compatibility)
                # But only if we haven't already normalized it above
                if ground_truth:
                    sample_gt = ground_truth[0]
                    if type(pos_label) != type(sample_gt):
                        # Convert pos_label to match the ground_truth type
                        if isinstance(sample_gt, str):
                            pos_label = str(pos_label)
                        elif isinstance(sample_gt, (int, float)):
                            try:
                                pos_label = type(sample_gt)(pos_label)
                            except (ValueError, TypeError):
                                pos_label = str(pos_label)


            # CRITICAL: Validate and extract predictions - CRASH IMMEDIATELY if format is wrong
            if not results:
                raise RuntimeError("❌ CRITICAL: results list is empty - cannot compute predictions")
            
            # Validate first result - MUST be new format
            sample_result = results[0]
            if not isinstance(sample_result, dict):
                raise RuntimeError(f"❌ CRITICAL: Prediction results must be dicts, got {type(sample_result).__name__}. "
                                 f"Sample: {sample_result!r}")
            
            # Validate NEW FORMAT ONLY - must have 'probabilities' key
            if 'probabilities' not in sample_result:
                raise RuntimeError(
                    f"❌ CRITICAL: Prediction results MUST have 'probabilities' key (new format). "
                    f"Got keys: {list(sample_result.keys())}. "
                    f"Expected format: {{'probabilities': {{class: prob, ...}}}}. "
                    f"Sample: {sample_result}"
                )
            
            logger.debug(f"{log_prefix}✅ Validated NEW prediction format: {{'probabilities': {{...}}}}")
            if not isinstance(sample_result['probabilities'], dict):
                raise RuntimeError(f"❌ CRITICAL: 'probabilities' value must be dict, got {type(sample_result['probabilities']).__name__}. "
                                 f"Sample: {sample_result!r}")
            
            # Extract predictions from new format
            # Use items() to avoid key comparison when values are tied (mixed-type keys break in Python 3)
            try:
                preds = [max(d['probabilities'].items(), key=lambda x: x[1])[0] for d in results]
            except KeyError as e:
                raise RuntimeError(f"❌ CRITICAL: Not all prediction dicts have 'probabilities' key. "
                                 f"Sample without key: {results[[i for i, d in enumerate(results) if 'probabilities' not in d][0]]!r}") from e
            except Exception as e:
                raise RuntimeError(f"❌ CRITICAL: Failed to extract predictions from new format. "
                                 f"Error: {e}. Sample: {sample_result!r}") from e
            
            logger.debug(f"PREDS = {preds[:10]}...")  # Show first 10
            
            # DIAGNOSTIC: Show unique predicted classes (moved to DEBUG for performance)
            from collections import Counter
            pred_counts = Counter(preds)
            logger.debug(f"{log_prefix}📊 PREDICTED CLASS DISTRIBUTION:")
            for pred_class, count in pred_counts.most_common():
                logger.debug(f"{log_prefix}   {pred_class}: {count} ({count/len(preds)*100:.1f}%)")
            
            # DIAGNOSTIC: Show ground truth class distribution for comparison (moved to DEBUG)
            gt_counts = Counter(ground_truth)
            logger.debug(f"{log_prefix}📊 GROUND TRUTH CLASS DISTRIBUTION:")
            for gt_class, count in gt_counts.most_common():
                logger.debug(f"{log_prefix}   {gt_class}: {count} ({count/len(ground_truth)*100:.1f}%)")

            num_tests_worked = 0
            ground_truth, preds, pos_label = self.normalize_types(ground_truth, preds, pos_label)
            self.validate_metrics_inputs(ground_truth, preds, pos_label)
            
            # CRITICAL: For binary classification, row tracking must use the SAME threshold-based predictions
            # as the confusion matrix. We'll compute row tracking AFTER threshold is determined.
            # For multi-class, we can use argmax predictions immediately.
            row_tracking_predictions = None
            row_tracking_threshold = None
            row_tracking_source = None
            
            # Track per-row correct/wrong flags for this epoch (for multi-class, use argmax immediately)
            # For binary, we'll update this after threshold is computed
            # NOTE: Multi-class row tracking uses argmax; if multi-class thresholds are introduced
            # (e.g., top-k, reject-option, or class-specific thresholds), move row tracking to
            # post-threshold analogous to binary to ensure consistency with confusion matrix.
            if self._validation_error_tracking is not None and epoch_idx is not None:
                if not is_binary:
                    # Multi-class: use argmax predictions immediately
                    correct_flags = [1 if p == gt else 0 for p, gt in zip(preds, ground_truth)]
                    self._validation_error_tracking["validation_results"][f"epoch_{epoch_idx}"] = correct_flags
                    logger.debug(f"{log_prefix}📊 Validation error tracking (multi-class, argmax): {sum(correct_flags)}/{len(correct_flags)} correct this epoch")
                # For binary, row tracking will be done after threshold computation

            # Overall accuracy (works for both binary and multi-class)
            # For binary, this will be updated after threshold computation
            try:
                # Suppress verbose sklearn warnings that dump full arrays
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    accuracy = accuracy_score(ground_truth, preds)
                num_tests_worked += 1
                logger.info(f"{log_prefix}Overall accuracy (argmax): {accuracy:.3f}")
            except Exception as e:
                accuracy = 0
                self.handle_metrics_error("accuracy", e)

            if is_binary:
                # Binary classification metrics
                try:
                    # Suppress verbose sklearn warnings that dump full arrays
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                    
                    # CRITICAL: Extract probability dicts - ONLY NEW FORMAT SUPPORTED
                    logger.info(f"{log_prefix}🔍 BINARY METRICS DEBUG: Starting binary classification metrics computation")
                    logger.info(f"{log_prefix}   pos_label = {pos_label!r} (type: {type(pos_label).__name__})")
                    logger.info(f"{log_prefix}   is_binary = {is_binary}")
                    logger.info(f"{log_prefix}   num results = {len(results)}")
                    logger.info(f"{log_prefix}   num ground_truth = {len(ground_truth)}")
                    
                    if not results:
                        raise RuntimeError("❌ CRITICAL: results is empty in binary classification metrics")
                    
                    # Validate format: MUST be new format with 'probabilities' key
                    sample_result = results[0]
                    logger.info(f"{log_prefix}   Sample result keys: {list(sample_result.keys())}")
                    
                    if 'probabilities' not in sample_result:
                        raise RuntimeError(
                            f"❌ CRITICAL: Prediction results MUST have 'probabilities' key (new format). "
                            f"Got keys: {list(sample_result.keys())}. "
                            f"Expected format: {{'probabilities': {{class: prob, ...}}}}. "
                            f"Sample: {sample_result}"
                        )
                    
                    # NEW FORMAT: {'probabilities': {class: prob, ...}}
                    logger.info(f"{log_prefix}   ✅ Validated NEW format: {{'probabilities': {{...}}}}")
                    prob_dicts = [d['probabilities'] for d in results]
                    sample_prob_dict = sample_result['probabilities']
                    logger.info(f"{log_prefix}   Sample prob dict keys: {list(sample_prob_dict.keys())}")
                    logger.info(f"{log_prefix}   Sample prob dict: {sample_prob_dict}")
                    
                    # OPTIMIZATION: Vectorized probability extraction with type mismatch handling
                    # Prediction dicts may have string keys, but pos_label might be float/int
                    
                    pos_probs = []
                    extraction_method = None
                    sample_dict_keys = list(sample_prob_dict.keys())
                    
                    logger.info(f"{log_prefix}🔍 Attempting to extract probabilities for pos_label={pos_label!r}")
                    logger.info(f"{log_prefix}   Available keys in prob dict: {sample_dict_keys}")
                    logger.info(f"{log_prefix}   Key types: {[type(k).__name__ for k in sample_dict_keys]}")
                    
                    # Pre-determine extraction strategy from first result to avoid per-item checks
                    if prob_dicts:
                        first_dict = sample_prob_dict
                        # Try strategies in order of preference
                        logger.info(f"{log_prefix}   Strategy 1: Exact match - checking if {pos_label!r} in {sample_dict_keys}")
                        if pos_label in first_dict:
                            extraction_method = f"exact_match (key type: {type(pos_label).__name__})"
                            pos_probs = [d.get(pos_label, 0.0) for d in prob_dicts]
                            logger.info(f"{log_prefix}   ✅ SUCCESS: Exact match found!")
                            logger.info(f"{log_prefix}   First 5 probabilities: {pos_probs[:5]}")
                        elif str(pos_label) in first_dict:
                            logger.info(f"{log_prefix}   Strategy 2: String conversion - {pos_label!r} -> {str(pos_label)!r}")
                            extraction_method = f"string_conversion ('{pos_label}' -> '{str(pos_label)}')"
                            pos_label_str = str(pos_label)
                            pos_probs = [d.get(pos_label_str, 0.0) for d in prob_dicts]
                            logger.warning(f"⚠️  TYPE MISMATCH: pos_label is {type(pos_label).__name__} but dict keys are strings")
                            logger.warning(f"   Using string conversion: {pos_label} -> '{pos_label_str}'")
                            logger.warning(f"   Dict keys: {sample_dict_keys}")
                            logger.info(f"{log_prefix}   First 5 probabilities: {pos_probs[:5]}")
                        else:
                            # Fuzzy match: try converting keys to pos_label type, or pos_label to key type
                            logger.info(f"{log_prefix}   Strategy 3: Fuzzy matching - type conversions and case-insensitive")
                            found_key = None
                            for key in first_dict.keys():
                                if key == "<UNKNOWN>":
                                    continue  # Skip <UNKNOWN> key
                                try:
                                    # Try converting key to pos_label type
                                    if type(pos_label)(key) == pos_label:
                                        found_key = key
                                        extraction_method = f"fuzzy_match (key '{key}' converted to {type(pos_label).__name__})"
                                        logger.info(f"{log_prefix}   ✅ FUZZY MATCH: Found by converting key '{key}' -> {type(pos_label)(key)}")
                                        break
                                except (ValueError, TypeError):
                                    pass
                                
                                try:
                                    # Try converting pos_label to key type
                                    if type(key)(pos_label) == key:
                                        found_key = key
                                        extraction_method = f"fuzzy_match (pos_label '{pos_label}' converted to {type(key).__name__})"
                                        logger.info(f"{log_prefix}   ✅ FUZZY MATCH: Found by converting pos_label '{pos_label}' -> {type(key)(pos_label)}")
                                        break
                                except (ValueError, TypeError):
                                    pass
                                
                                # Try string comparison (case-insensitive)
                                if str(key).lower() == str(pos_label).lower():
                                    found_key = key
                                    extraction_method = f"fuzzy_match (case-insensitive: '{pos_label}' -> '{key}')"
                                    logger.info(f"{log_prefix}   ✅ FUZZY MATCH: Found by case-insensitive match '{pos_label}' -> '{key}'")
                                    break
                            
                            if found_key:
                                pos_probs = [d.get(found_key, 0.0) for d in prob_dicts]
                                logger.info(f"{log_prefix}   First 5 probabilities: {pos_probs[:5]}")
                            else:
                                # CRASH IMMEDIATELY - no fallbacks
                                logger.error(f"{log_prefix}❌ CRITICAL: Cannot extract probabilities for pos_label={pos_label!r}")
                                logger.error(f"{log_prefix}   pos_label type: {type(pos_label).__name__}")
                                logger.error(f"{log_prefix}   Available keys: {sample_dict_keys}")
                                logger.error(f"{log_prefix}   Key types: {[type(k).__name__ for k in sample_dict_keys]}")
                                logger.error(f"{log_prefix}   Sample prob dict: {sample_prob_dict}")
                                logger.error(f"{log_prefix}   Tried:")
                                logger.error(f"{log_prefix}     1. Exact match: {pos_label!r} in keys")
                                logger.error(f"{log_prefix}     2. String conversion: {str(pos_label)!r} in keys")
                                logger.error(f"{log_prefix}     3. Type conversion for each key")
                                logger.error(f"{log_prefix}     4. Case-insensitive string match")
                                logger.error(f"{log_prefix}")
                                logger.error(f"{log_prefix}   This is a CRITICAL BUG - pos_label must match a key in probability dicts!")
                                raise RuntimeError(
                                    f"❌ CRITICAL: Cannot extract probabilities for pos_label={pos_label!r} (type={type(pos_label).__name__}). "
                                    f"Available keys: {sample_dict_keys} (types: {[type(k).__name__ for k in sample_dict_keys]}). "
                                    f"Tried exact match, string conversion, type conversion, and case-insensitive matching. "
                                    f"This indicates a type mismatch or missing key in prediction output."
                                )
                    
                    # Log which extraction method was used (only once)
                    if extraction_method:
                        logger.info(f"{log_prefix}📊 Probability extraction method: {extraction_method}")
                    else:
                        # If we got here without an extraction method, something is very wrong
                        raise RuntimeError(f"❌ CRITICAL: No extraction method set - this should never happen!")
                    
                    # CRITICAL: Check if we're getting valid probabilities - CRASH if all zero
                    if all(p == 0 for p in pos_probs):
                        logger.error(f"{log_prefix}❌ CRITICAL: All extracted probabilities are 0.0!")
                        logger.error(f"{log_prefix}   pos_label = {pos_label!r} (type={type(pos_label).__name__})")
                        logger.error(f"{log_prefix}   Extraction method: {extraction_method}")
                        logger.error(f"{log_prefix}   Sample dict keys: {sample_dict_keys}")
                        logger.error(f"{log_prefix}   Sample prob dict: {sample_prob_dict}")
                        logger.error(f"{log_prefix}   First 10 extracted probs: {pos_probs[:10]}")
                        raise RuntimeError(
                            f"❌ CRITICAL: All extracted probabilities are 0.0 for pos_label={pos_label!r}. "
                            f"Extraction method was '{extraction_method}' but resulted in all zeros. "
                            f"This indicates the extraction key doesn't exist in probability dicts, or all actual probabilities are zero. "
                            f"Sample dict: {sample_prob_dict}"
                        )
                    
                    # CRITICAL: Validate we have the right number of probabilities
                    if len(pos_probs) != len(ground_truth):
                        logger.error(f"{log_prefix}❌ CRITICAL: Probability count mismatch!")
                        logger.error(f"{log_prefix}   len(pos_probs) = {len(pos_probs)}")
                        logger.error(f"{log_prefix}   len(ground_truth) = {len(ground_truth)}")
                        logger.error(f"{log_prefix}   len(prob_dicts) = {len(prob_dicts)}")
                        raise RuntimeError(
                            f"❌ CRITICAL: Extracted {len(pos_probs)} probabilities but have {len(ground_truth)} ground truth values. "
                            f"These must match!"
                        )
                    
                    logger.info(f"{log_prefix}✅ Successfully extracted {len(pos_probs)} probabilities for pos_label={pos_label!r}")
                    logger.info(f"{log_prefix}   First 10 probs: {pos_probs[:10]}")
                    
                    # OPTIMIZATION: Vectorized binary conversion
                    pos_probs_array = np.array(pos_probs)
                    y_true_binary = np.array([1 if gt == pos_label else 0 for gt in ground_truth])
                    
                    # DIAGNOSTIC: Log probability distribution and track collapse
                    prob_std = pos_probs_array.std()
                    prob_mean = pos_probs_array.mean()
                    prob_range = pos_probs_array.max() - pos_probs_array.min()
                    
                    # Track std history to detect collapse
                    if not hasattr(self, '_prob_std_history'):
                        self._prob_std_history = []
                    self._prob_std_history.append((epoch_idx, prob_std))
                    
                    # CRITICAL: Always log probability stats - collapse is a serious issue
                    logger.info(f"{log_prefix}📊 PROBABILITY DISTRIBUTION:")
                    logger.info(f"{log_prefix}   Min: {pos_probs_array.min():.4f}, Max: {pos_probs_array.max():.4f}")
                    logger.info(f"{log_prefix}   Mean: {prob_mean:.4f}, Median: {np.median(pos_probs_array):.4f}")
                    logger.info(f"{log_prefix}   Std: {prob_std:.4f}, Range: {prob_range:.4f}")
                    
                    # CRITICAL: Check for probability collapse (all predictions same)
                    if prob_std < 0.0001:  # Very strict threshold - probabilities are completely collapsed
                        logger.error(f"{log_prefix}🚨 CRITICAL: PROBABILITY COLLAPSE DETECTED!")
                        logger.error(f"{log_prefix}   Probability std={prob_std:.6f} (all predictions are nearly identical)")
                        logger.error(f"{log_prefix}   This means the model is outputting the same probability for all samples")
                        logger.error(f"{log_prefix}   Check: learning rate too small, predictor not learning, or encoder producing constant embeddings")
                    
                    # Warn if std is collapsing (compared to first epoch)
                    if len(self._prob_std_history) > 1:
                        first_std = self._prob_std_history[0][1]
                        if first_std > 0.01 and prob_std < first_std * 0.1:  # Collapsed to <10% of original
                            logger.warning(f"{log_prefix}⚠️  PROBABILITY STD COLLAPSE: {prob_std:.4f} (started at {first_std:.4f})")
                            logger.warning(f"{log_prefix}   This suggests LR schedule or regularization is too aggressive")
                    
                    logger.debug(f"{log_prefix}   Percentiles [10%, 25%, 50%, 75%, 90%]: {np.percentile(pos_probs_array, [10, 25, 50, 75, 90])}")
                    
                    # DIAGNOSTIC: Class distribution (moved to DEBUG)
                    pos_count = int(y_true_binary.sum())
                    neg_count = len(y_true_binary) - pos_count
                    ground_truth_pos_rate = pos_count / len(y_true_binary) if len(y_true_binary) > 0 else 0.0
                    
                    # Determine negative class label from target_codec
                    neg_label = None
                    if self.target_codec and hasattr(self.target_codec, 'members'):
                        # Find the other class that's not pos_label
                        # Handle type mismatches (e.g., pos_label='1.0' vs member='1')
                        pos_label_normalized = str(pos_label).strip()
                        for member in self.target_codec.members:
                            member_str = str(member).strip()
                            # Compare normalized strings and also check if they represent the same value
                            if member_str != pos_label_normalized and member != "<UNKNOWN>":
                                # Double-check: if both convert to same float/int, they're the same class
                                try:
                                    pos_val = float(pos_label_normalized)
                                    member_val = float(member_str)
                                    if pos_val == member_val:
                                        continue  # Same value, skip
                                except (ValueError, TypeError):
                                    pass  # Can't convert, use string comparison
                                neg_label = member
                                break
                        # If not found (shouldn't happen for binary), use a default
                        if neg_label is None:
                            neg_label = "other"
                    
                    logger.debug(f"{log_prefix}📊 CLASS DISTRIBUTION:")
                    logger.debug(f"{log_prefix}   Positive class = '{pos_label}': {pos_count} ({pos_count/len(y_true_binary)*100:.1f}%)")
                    logger.debug(f"{log_prefix}   Negative class = '{neg_label}': {neg_count} ({neg_count/len(y_true_binary)*100:.1f}%)")
                    
                    # Compute constraint bounds on predicted positive rate (C: Constraints)
                    # Rule: [ground_truth_rate * 0.5, ground_truth_rate * 1.5] with min 0.1, max 0.9
                    if ground_truth_pos_rate > 0:
                        min_rate = max(0.1, ground_truth_pos_rate * 0.5)
                        max_rate = min(0.9, ground_truth_pos_rate * 1.5)
                        # Ensure min < max and reasonable bounds
                        if min_rate >= max_rate:
                            min_rate = max(0.1, ground_truth_pos_rate - 0.1)
                            max_rate = min(0.9, ground_truth_pos_rate + 0.1)
                        predicted_positive_rate_bounds = (min_rate, max_rate)
                    else:
                        predicted_positive_rate_bounds = None
                    
                    # Find optimal threshold for F1 score with constraints
                    optimal_threshold, optimal_f1 = self.best_threshold_for_f1(
                        y_true_binary, 
                        pos_probs,
                        predicted_positive_rate_bounds=predicted_positive_rate_bounds
                    )
                    
                    # Compute predicted positive rate at optimal threshold for logging
                    pred_pos_rate_at_optimal = (pos_probs_array >= optimal_threshold).mean()
                    
                    # Log constraint info if constraints were applied
                    if predicted_positive_rate_bounds:
                        logger.debug(f"{log_prefix}📊 Threshold Search Constraints:")
                        logger.debug(f"{log_prefix}   Ground truth positive rate: {ground_truth_pos_rate:.1%}")
                        logger.debug(f"{log_prefix}   Allowed predicted positive rate: [{predicted_positive_rate_bounds[0]:.1%}, {predicted_positive_rate_bounds[1]:.1%}]")
                        logger.debug(f"{log_prefix}   Selected threshold: {optimal_threshold:.4f} → predicted rate: {pred_pos_rate_at_optimal:.1%}")
                    
                    # TRACK: Record threshold history over epochs (always track for debugging)
                    self.optimal_threshold_history.append({
                        'epoch': epoch_idx,
                        'threshold': optimal_threshold,
                        'f1_score': optimal_f1,
                        'accuracy_at_optimal': None,  # Will be set below
                        'auc': None  # Will be set below
                    })
                    
                    # OPTIMIZATION: Vectorized threshold application
                    optimal_preds = (pos_probs_array >= optimal_threshold).astype(int).tolist()
                    
                    # Compute prediction counts for threshold-based predictions (for failure detection)
                    # Map 1/0 back to actual class labels
                    from collections import Counter
                    threshold_based_preds = [pos_label if p == 1 else neg_label for p in optimal_preds]
                    threshold_pred_counts = Counter(threshold_based_preds)
                    
                    # Log threshold-based prediction distribution (for failure detection verification)
                    logger.debug(f"{log_prefix}📊 THRESHOLD-BASED PREDICTION DISTRIBUTION (used for failure detection):")
                    for pred_class, count in threshold_pred_counts.most_common():
                        logger.debug(f"{log_prefix}   {pred_class}: {count} ({count/len(threshold_based_preds)*100:.1f}%)")
                    
                    # DIAGNOSTIC: Prediction distribution at optimal threshold (moved to DEBUG)
                    pred_pos_count = int(sum(optimal_preds))
                    pred_neg_count = len(optimal_preds) - pred_pos_count
                    logger.debug(f"{log_prefix}📊 PREDICTIONS AT OPTIMAL THRESHOLD {optimal_threshold:.4f}:")
                    logger.debug(f"{log_prefix}   Predicted positive = '{pos_label}': {pred_pos_count} ({pred_pos_count/len(optimal_preds)*100:.1f}%)")
                    logger.debug(f"{log_prefix}   Predicted negative = '{neg_label}': {pred_neg_count} ({pred_neg_count/len(optimal_preds)*100:.1f}%)")
                    
                    # Compute ALL threshold-dependent metrics using helper function
                    # This ensures all metrics are consistent with the same confusion matrix
                    f1_metrics = self.compute_metrics_at_threshold(
                        y_true_binary, pos_probs_array, optimal_threshold, 
                        pos_label=pos_label, neg_label=neg_label
                    )
                    
                    # Extract values for local use (backwards compatibility)
                    precision = f1_metrics['precision']
                    recall = f1_metrics['recall']
                    f1 = f1_metrics['f1']
                    tp = f1_metrics['tp']
                    fp = f1_metrics['fp']
                    tn = f1_metrics['tn']
                    fn = f1_metrics['fn']
                    accuracy_at_optimal = f1_metrics['accuracy']
                    specificity = f1_metrics['specificity']
                    balanced_accuracy = f1_metrics['balanced_accuracy']
                    mcc = f1_metrics['mcc']
                    tpr = recall  # TPR = Recall = Sensitivity
                    
                    # Track which threshold mode we're using
                    threshold_mode = "f1_optimal"
                    threshold_value = optimal_threshold
                    
                    # Update threshold history with accuracy
                    if self.optimal_threshold_history:
                        self.optimal_threshold_history[-1]['accuracy_at_optimal'] = accuracy_at_optimal
                    
                    # Brier Score (mean squared error of probabilities) - calibration metric
                    brier_score = brier_score_loss(y_true_binary, pos_probs_array)
                    
                    # Calibration metrics: ECE (Expected Calibration Error) and MCE (Maximum Calibration Error)
                    # Also compute reliability curve data
                    ece = None
                    mce = None
                    reliability_curve = None
                    sharpness = None
                    
                    try:
                        # Compute calibration metrics using probability bins
                        n_bins = 10
                        bin_boundaries = np.linspace(0, 1, n_bins + 1)
                        bin_lowers = bin_boundaries[:-1]
                        bin_uppers = bin_boundaries[1:]
                        
                        # Compute calibration errors per bin
                        ece_sum = 0.0
                        mce_max = 0.0
                        total_samples = len(y_true_binary)
                        reliability_data = []
                        
                        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
                            # Find samples in this bin
                            in_bin = (pos_probs_array > bin_lower) & (pos_probs_array <= bin_upper)
                            prop_in_bin = in_bin.mean()
                            
                            if prop_in_bin > 0:
                                # Mean predicted probability in this bin
                                mean_pred_prob = pos_probs_array[in_bin].mean()
                                
                                # Actual event frequency in this bin
                                actual_freq = y_true_binary[in_bin].mean()
                                
                                # Calibration error for this bin
                                bin_error = abs(mean_pred_prob - actual_freq)
                                
                                # Weight by proportion of samples in bin
                                ece_sum += bin_error * prop_in_bin
                                
                                # Track maximum error
                                if bin_error > mce_max:
                                    mce_max = bin_error
                                
                                # Store reliability curve data
                                reliability_data.append({
                                    'bin_center': (bin_lower + bin_upper) / 2.0,
                                    'mean_pred_prob': float(mean_pred_prob),
                                    'actual_freq': float(actual_freq),
                                    'prop_in_bin': float(prop_in_bin),
                                    'bin_error': float(bin_error)
                                })
                            else:
                                # Empty bin - still record for completeness
                                reliability_data.append({
                                    'bin_center': (bin_lower + bin_upper) / 2.0,
                                    'mean_pred_prob': None,
                                    'actual_freq': None,
                                    'prop_in_bin': 0.0,
                                    'bin_error': None
                                })
                        
                        ece = float(ece_sum)
                        mce = float(mce_max)
                        reliability_curve = reliability_data
                        
                        # Sharpness: variance of predicted probabilities
                        sharpness = float(pos_probs_array.var())
                        
                    except Exception as e:
                        logger.warning(f"{log_prefix}⚠️  Failed to compute calibration metrics: {e}")
                    
                    # Binary AUC (doesn't depend on threshold)
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        auc = roc_auc_score(y_true_binary, pos_probs)
                    
                    # PR-AUC (Average Precision) - often better for imbalanced datasets
                    pr_auc = average_precision_score(y_true_binary, pos_probs)
                    
                    # ABSTENTION REPORTING: Track <UNKNOWN> predictions and AUC on non-unknown subset
                    pct_unknown_predicted = 0.0
                    auc_non_unknown = None
                    n_unknown = 0
                    n_non_unknown = len(pos_probs)
                    
                    # Extract <UNKNOWN> probabilities if available (binary mode with margin-based abstention)
                    if prob_dicts and '<UNKNOWN>' in sample_prob_dict:
                        unknown_probs = [d.get('<UNKNOWN>', 0.0) for d in prob_dicts]
                        # Count predictions where p_unknown > 0.5 (or where prediction == "<UNKNOWN>")
                        # For metrics, we'll use the prediction labels from results
                        unknown_predictions = [r.get('prediction') == '<UNKNOWN>' for r in results]
                        n_unknown = sum(unknown_predictions)
                        n_non_unknown = len(unknown_predictions) - n_unknown
                        pct_unknown_predicted = (n_unknown / len(unknown_predictions) * 100.0) if unknown_predictions else 0.0
                        
                        # Compute AUC on non-unknown subset
                        if n_non_unknown > 0:
                            non_unknown_mask = [not pred for pred in unknown_predictions]
                            pos_probs_non_unknown = [p for p, mask in zip(pos_probs, non_unknown_mask) if mask]
                            y_true_non_unknown = [y for y, mask in zip(y_true_binary, non_unknown_mask) if mask]
                            
                            if len(set(y_true_non_unknown)) > 1:  # Need both classes for AUC
                                try:
                                    with warnings.catch_warnings():
                                        warnings.simplefilter("ignore")
                                        auc_non_unknown = roc_auc_score(y_true_non_unknown, pos_probs_non_unknown)
                                except Exception as e:
                                    logger.debug(f"{log_prefix}⚠️  Could not compute AUC on non-unknown subset: {e}")
                                    auc_non_unknown = None
                            else:
                                logger.debug(f"{log_prefix}⚠️  Cannot compute AUC on non-unknown subset: only one class present")
                                auc_non_unknown = None
                        
                        logger.info(f"{log_prefix}📊 ABSTENTION METRICS:")
                        logger.info(f"{log_prefix}   % Unknown predicted: {pct_unknown_predicted:.2f}% ({n_unknown}/{len(unknown_predictions)})")
                        if auc_non_unknown is not None:
                            logger.info(f"{log_prefix}   AUC (non-unknown subset): {auc_non_unknown:.4f} (n={n_non_unknown})")
                            logger.info(f"{log_prefix}   AUC (full dataset): {auc:.4f} (n={len(pos_probs)})")
                        else:
                            logger.info(f"{log_prefix}   AUC (full dataset): {auc:.4f} (n={len(pos_probs)})")
                    else:
                        logger.debug(f"{log_prefix}   No <UNKNOWN> probabilities found (multi-class or legacy binary mode)")
                    
                    # Update threshold history with AUC
                    if self.optimal_threshold_history:
                        self.optimal_threshold_history[-1]['auc'] = auc
                        self.optimal_threshold_history[-1]['pr_auc'] = pr_auc
                    
                    # Compute prediction performance across probability bands
                    bands_data = None
                    try:
                        bands_df = compute_binary_lift_bands(pos_probs, y_true_binary, threshold=optimal_threshold, n_bins=10)
                        # Convert DataFrame to dict format for JSON serialization
                        bands_list = []
                        for idx, row in bands_df.iterrows():
                            band_interval = row['band']
                            band_dict = {
                                'band_lower': float(band_interval.left) if pd.notna(band_interval.left) else None,
                                'band_upper': float(band_interval.right) if pd.notna(band_interval.right) else None,
                                'band_width': float(row['band_width']),
                                'avg_pred': float(row['avg_pred']),
                                'n': int(row['n']),
                                'actual_pos': int(row['actual_pos']),
                                'actual_neg': int(row['actual_neg']),
                                'pred_pos': int(row['pred_pos']),
                                'pred_neg': int(row['pred_neg']),
                                'correct': int(row['correct']),
                                'correct_pct': float(row['correct_pct']),
                            }
                            bands_list.append(band_dict)
                        bands_data = {'bands': bands_list}
                        logger.debug(f"{log_prefix}📊 Performance by Probability Band (threshold={optimal_threshold:.4f}):")
                        logger.info(f"{log_prefix}   {'Band Range':<22} {'Width':>6} {'Avg':>6} {'N':>5} {'Actual':<11} {'Predicted':<11} {'Correct':>7} {'Acc%':>6}")
                        logger.info(f"{log_prefix}   {'':22} {'':6} {'Pred':>6} {'':5} {'Pos':>5} {'Neg':>5} {'Pos':>5} {'Neg':>5} {'':7} {'':6}")
                        logger.info(f"{log_prefix}   {'-'*22} {'-'*6} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*5} {'-'*7} {'-'*6}")
                        for band in bands_list:
                            band_str = f"[{band['band_lower']:.3f},{band['band_upper']:.3f}]"
                            width = band['band_width']
                            avg_pred = band['avg_pred']
                            n = band['n']
                            actual_pos = band['actual_pos']
                            actual_neg = band['actual_neg']
                            pred_pos = band['pred_pos']
                            pred_neg = band['pred_neg']
                            correct = band['correct']
                            correct_pct = band['correct_pct']
                            logger.info(f"{log_prefix}   {band_str:<22} {width:6.3f} {avg_pred:6.3f} {n:5d} {actual_pos:5d} {actual_neg:5d} {pred_pos:5d} {pred_neg:5d} {correct:7d} {correct_pct:6.1f}")
                    except Exception as e:
                        logger.warning(f"{log_prefix}⚠️  Failed to compute performance bands: {e}")
                        logger.debug(f"{log_prefix}   Full traceback:\n{traceback.format_exc()}")
                    
                    # Cost-based metrics (if costs are available)
                    cost_min = None
                    tau_cost = None
                    f1_cost = None
                    cost_metrics = None
                    use_cost_optimal_threshold = False
                    if self.cost_false_positive is not None and self.cost_false_negative is not None:
                        try:
                            # Compute cost-optimal threshold (Bayes-optimal decision threshold)
                            # Formula: threshold = C_FP / (C_FP + C_FN)
                            # This minimizes expected cost for the given FP and FN costs
                            tau_cost, cost_min, (tp_cost, fp_cost, tn_cost, fn_cost), f1_cost = self.best_threshold_for_cost(
                                y_true_binary,
                                pos_probs,
                                self.cost_false_positive,
                                self.cost_false_negative,
                                min_pred_pos_frac=predicted_positive_rate_bounds[0] if predicted_positive_rate_bounds else None,
                                max_pred_pos_frac=predicted_positive_rate_bounds[1] if predicted_positive_rate_bounds else None,
                            )
                            
                            # Compute baseline cost for normalization
                            baseline_cost = self._compute_baseline_cost(y_true_binary, self.cost_false_positive, self.cost_false_negative)
                            
                            # Store cost metrics
                            cost_metrics = {
                                "cost_min": cost_min,
                                "tau_cost": tau_cost,
                                "f1_cost": f1_cost,
                                "tp_cost": tp_cost,
                                "fp_cost": fp_cost,
                                "tn_cost": tn_cost,
                                "fn_cost": fn_cost,
                                "baseline_cost": baseline_cost,
                            }
                            
                            # BAYES-OPTIMAL DECISION THRESHOLD:
                            # When costs are specified, use the cost-optimal threshold instead of F1-optimal.
                            # This is the theoretically correct Bayes-optimal decision rule that minimizes expected cost.
                            # The threshold approximates: C_FP / (C_FP + C_FN)
                            # For example, with C_FN=2.33 and C_FP=1.0, threshold ≈ 0.30 (not 0.50)
                            use_cost_optimal_threshold = True
                            
                            # Compute Bayes-optimal theoretical threshold for comparison
                            bayes_threshold_theory = self.cost_false_positive / (self.cost_false_positive + self.cost_false_negative)
                            
                            logger.info(f"{log_prefix}💰 Cost-optimal threshold: {tau_cost:.4f} (Bayes-optimal theory: {bayes_threshold_theory:.4f})")
                            logger.info(f"{log_prefix}💰 Cost at threshold: {cost_min:.2f} (baseline: {baseline_cost:.2f}), F1: {f1_cost:.3f}")
                            logger.debug(f"{log_prefix}💰 Cost confusion matrix: TP={tp_cost}, FP={fp_cost}, TN={tn_cost}, FN={fn_cost}")
                            logger.debug(f"{log_prefix}💰 Cost formula: C_FP={self.cost_false_positive}, C_FN={self.cost_false_negative}")
                        except Exception as e:
                            logger.warning(f"{log_prefix}⚠️  Failed to compute cost metrics: {e}")
                            use_cost_optimal_threshold = False
                    
                    num_tests_worked += 3
                    
                    # DECISION: Which threshold to use for predictions?
                    # - If costs specified: Use cost-optimal threshold (Bayes-optimal)
                    # - Otherwise: Use F1-optimal threshold
                    if use_cost_optimal_threshold and tau_cost is not None:
                        threshold_for_prediction = tau_cost
                        threshold_source = "cost-optimal (Bayes)"
                        threshold_mode = "cost_optimal"
                        threshold_value = tau_cost
                        
                        # Recompute ALL metrics at cost-optimal threshold using helper
                        # This ensures all metrics are consistent with the confusion matrix
                        cost_metrics_at_threshold = self.compute_metrics_at_threshold(
                            y_true_binary, pos_probs_array, tau_cost,
                            pos_label=pos_label, neg_label=neg_label
                        )
                        
                        # Update all local variables to use cost-optimal values
                        precision = cost_metrics_at_threshold['precision']
                        recall = cost_metrics_at_threshold['recall']
                        f1 = cost_metrics_at_threshold['f1']
                        tp = cost_metrics_at_threshold['tp']
                        fp = cost_metrics_at_threshold['fp']
                        tn = cost_metrics_at_threshold['tn']
                        fn = cost_metrics_at_threshold['fn']
                        accuracy_at_optimal = cost_metrics_at_threshold['accuracy']
                        specificity = cost_metrics_at_threshold['specificity']
                        balanced_accuracy = cost_metrics_at_threshold['balanced_accuracy']
                        mcc = cost_metrics_at_threshold['mcc']
                        tpr = recall
                        
                        # Update optimal_preds for downstream use
                        optimal_preds = (pos_probs_array >= tau_cost).astype(int)
                        optimal_threshold = tau_cost
                    else:
                        threshold_for_prediction = optimal_threshold
                        threshold_source = "F1-optimal"
                        # threshold_mode and threshold_value already set above
                    
                    # Update main metrics to use optimal threshold values
                    accuracy = accuracy_at_optimal
                    
                    # CRITICAL: Update row tracking to use the SAME threshold-based predictions as confusion matrix
                    # This ensures acc_from_cm == acc_rowtrack (within float rounding)
                    # 
                    # Label conversion verification:
                    # - pos_label corresponds to the same label used by compute_metrics_at_threshold
                    # - Both use the same y_true_binary conversion: 1 if gt == pos_label else 0
                    # - Both use the same threshold-based prediction: pos_label if prob >= threshold else neg_label
                    # - This ensures 1:1 label mapping between confusion matrix and row tracking
                    if self._validation_error_tracking is not None and epoch_idx is not None:
                        # Convert optimal_preds to list if it's a numpy array
                        if isinstance(optimal_preds, np.ndarray):
                            optimal_preds_list = optimal_preds.tolist()
                        else:
                            optimal_preds_list = optimal_preds
                        
                        # Convert threshold-based binary predictions (0/1) back to class labels
                        # CRITICAL: Use the SAME pos_label and neg_label as compute_metrics_at_threshold
                        # 
                        # Verification of 1:1 label mapping:
                        # 1. compute_metrics_at_threshold receives the same pos_label and neg_label variables
                        # 2. compute_metrics_at_threshold uses: y_true_binary = [1 if gt == pos_label else 0 for gt in ground_truth]
                        # 3. compute_metrics_at_threshold uses: preds = (pos_probs_array >= threshold).astype(int)  # 0/1
                        # 4. Row tracking uses: pred_labels = [pos_label if p == 1 else neg_label for p in preds]
                        # 
                        # This is the exact inverse operation, ensuring 1:1 correspondence:
                        # - CM: gt='bad' -> y_true_binary=1, prob=0.4, threshold=0.3 -> pred=1 -> label='bad'
                        # - RT: pred=1 -> label='bad' -> matches CM
                        # 
                        # Both use the SAME pos_label and neg_label variables (determined at lines 10694-10710),
                        # so label conversion is guaranteed to be 1:1 with the codec.
                        threshold_based_preds_labels = [pos_label if p == 1 else neg_label for p in optimal_preds_list]
                        row_tracking_predictions = threshold_based_preds_labels
                        row_tracking_threshold = threshold_for_prediction
                        row_tracking_source = threshold_source
                        
                        # Compute correct flags using threshold-based predictions
                        correct_flags = [1 if p == gt else 0 for p, gt in zip(threshold_based_preds_labels, ground_truth)]
                        self._validation_error_tracking["validation_results"][f"epoch_{epoch_idx}"] = correct_flags
                        
                        # Compute accuracy from row tracking
                        n_eval = len(ground_truth)
                        correct_count = sum(correct_flags)
                        acc_rowtrack = correct_count / n_eval if n_eval > 0 else 0.0
                        
                        # Compute accuracy from confusion matrix
                        acc_from_cm = accuracy_at_optimal
                        
                        # CRITICAL ASSERTION: These MUST match (within float rounding)
                        # If they don't, it means we're using different predictions/thresholds/datasets
                        tolerance = 1e-6
                        if abs(acc_from_cm - acc_rowtrack) > tolerance:
                            # Compute num_pred_pos for logging
                            if isinstance(optimal_preds, np.ndarray):
                                num_pred_pos_cm = int(optimal_preds.sum())
                            else:
                                num_pred_pos_cm = int(sum(optimal_preds))
                            num_pred_pos_rowtrack = int(sum(1 for p in threshold_based_preds_labels if p == pos_label))
                            
                            # Compute fast checksum of y_true for both paths to verify same dataset
                            # Use first/last 5 labels + fast hash for quick verification
                            # Note: Using built-in hash() is much faster than MD5 and sufficient for diagnostic purposes
                            # (We don't need cryptographic security, just to detect differences)
                            try:
                                # Fast hash: hash of tuple of first 10, middle 10, last 10 labels
                                # This is O(1) for small samples, O(n) only for very large datasets
                                sample_size = min(10, len(ground_truth))
                                if len(ground_truth) <= 20:
                                    # Small dataset: hash entire tuple
                                    y_true_hash = str(hash(tuple(ground_truth)))
                                else:
                                    # Large dataset: hash sample (first 10, middle 10, last 10)
                                    mid_start = len(ground_truth) // 2 - 5
                                    mid_end = mid_start + 10
                                    sample = tuple(ground_truth[:sample_size] + ground_truth[mid_start:mid_end] + ground_truth[-sample_size:])
                                    y_true_hash = str(hash(sample))
                            except (TypeError, AttributeError):
                                # Fallback if hash fails (e.g., unhashable types)
                                y_true_hash = "N/A (unhashable)"
                            
                            y_true_first5 = ground_truth[:5] if len(ground_truth) >= 5 else ground_truth
                            y_true_last5 = ground_truth[-5:] if len(ground_truth) >= 5 else ground_truth
                            
                            # Fast hash of predictions (same approach)
                            try:
                                if len(threshold_based_preds_labels) <= 20:
                                    preds_cm_hash = str(hash(tuple(threshold_based_preds_labels)))
                                else:
                                    sample_size = min(10, len(threshold_based_preds_labels))
                                    mid_start = len(threshold_based_preds_labels) // 2 - 5
                                    mid_end = mid_start + 10
                                    sample = tuple(threshold_based_preds_labels[:sample_size] + threshold_based_preds_labels[mid_start:mid_end] + threshold_based_preds_labels[-sample_size:])
                                    preds_cm_hash = str(hash(sample))
                            except (TypeError, AttributeError):
                                preds_cm_hash = "N/A (unhashable)"
                            
                            logger.error(f"{log_prefix}❌ CRITICAL: Accuracy mismatch detected!")
                            logger.error(f"{log_prefix}   acc_from_cm (confusion matrix): {acc_from_cm:.10f}")
                            logger.error(f"{log_prefix}   acc_rowtrack (row tracking): {acc_rowtrack:.10f}")
                            logger.error(f"{log_prefix}   difference: {abs(acc_from_cm - acc_rowtrack):.10f} (tolerance: {tolerance})")
                            logger.error(f"{log_prefix}   n_eval_cm: {n_eval}, n_eval_rowtrack: {n_eval}")
                            logger.error(f"{log_prefix}   threshold_used_cm: {threshold_for_prediction:.6f} ({threshold_source})")
                            logger.error(f"{log_prefix}   threshold_used_rowtrack: {row_tracking_threshold:.6f} ({row_tracking_source})")
                            logger.error(f"{log_prefix}   pos_label_cm: {pos_label!r}, pos_label_rowtrack: {pos_label!r}")
                            logger.error(f"{log_prefix}   num_pred_pos_cm: {num_pred_pos_cm}, num_pred_pos_rowtrack: {num_pred_pos_rowtrack}")
                            logger.error(f"{log_prefix}")
                            logger.error(f"{log_prefix}   y_true verification (to detect dataset/subset mismatch):")
                            logger.error(f"{log_prefix}     y_true_hash: {y_true_hash}")
                            logger.error(f"{log_prefix}     y_true_first5: {y_true_first5}")
                            logger.error(f"{log_prefix}     y_true_last5: {y_true_last5}")
                            logger.error(f"{log_prefix}     y_true_length: {len(ground_truth)}")
                            logger.error(f"{log_prefix}   predictions_hash: {preds_cm_hash}")
                            logger.error(f"{log_prefix}")
                            logger.error(f"{log_prefix}   This indicates a mismatch in:")
                            logger.error(f"{log_prefix}   1. Different thresholds (cm vs row tracking)")
                            logger.error(f"{log_prefix}   2. Different datasets/subset (check y_true_hash and first/last labels)")
                            logger.error(f"{log_prefix}   3. Different label mapping/pos_label")
                            logger.error(f"{log_prefix}   4. Different prediction source")
                            logger.error(f"{log_prefix}   5. Timing/caching bug")
                            raise AssertionError(
                                f"❌ CRITICAL: Accuracy mismatch! acc_from_cm={acc_from_cm:.10f} != acc_rowtrack={acc_rowtrack:.10f} "
                                f"(diff={abs(acc_from_cm - acc_rowtrack):.10f} > tolerance={tolerance}). "
                                f"This means confusion matrix and row tracking are using different predictions/thresholds/datasets. "
                                f"y_true_hash={y_true_hash} (check first/last labels in logs). "
                                f"Check logs above for details."
                            )
                        
                        # Log successful match
                        logger.debug(f"{log_prefix}✅ Accuracy consistency check passed:")
                        logger.debug(f"{log_prefix}   acc_from_cm: {acc_from_cm:.10f}, acc_rowtrack: {acc_rowtrack:.10f}")
                        logger.debug(f"{log_prefix}   threshold: {threshold_for_prediction:.6f} ({threshold_source})")
                        logger.debug(f"{log_prefix}   n_eval: {n_eval}, correct: {correct_count}, wrong: {n_eval - correct_count}")
                        logger.debug(f"{log_prefix}📊 Validation error tracking (binary, threshold-based): {correct_count}/{n_eval} correct this epoch")
                    
                    # Store argmax metrics for comparison (B: Log what you're optimizing)
                    argmax_preds = (pos_probs_array >= 0.5).astype(int)
                    argmax_accuracy = (y_true_binary == argmax_preds).mean()
                    argmax_precision = precision_score(y_true_binary, argmax_preds, zero_division=0)
                    argmax_recall = recall_score(y_true_binary, argmax_preds, zero_division=0)
                    argmax_f1 = f1_score(y_true_binary, argmax_preds, zero_division=0)
                    
                    # Compute deltas for logging
                    delta_f1 = f1 - argmax_f1
                    delta_accuracy = accuracy_at_optimal - argmax_accuracy
                    
                    # THRESHOLD TRACKING POLICY:
                    # - Each epoch computes its own optimal threshold and reports metrics using that threshold
                    # - When costs are specified, we use cost-optimal threshold (Bayes-optimal decision rule)
                    # - Otherwise, we use F1-optimal threshold
                    # - We track which epoch had the best AUC (for model checkpoint selection)
                    # - self.optimal_threshold is set to the best epoch's threshold (for final predictions)
                    # - This ensures metrics are always computed with the threshold optimal for the current model state
                    
                    auc_epsilon = 0.001  # Minimum improvement to count as "better"
                    is_best_epoch = False
                    best_epoch_msg = ""
                    
                    # First epoch: initialize best tracking
                    if self._best_auc < 0:
                        self._best_auc = auc
                        self._best_auc_epoch = epoch_idx
                        self._best_f1_at_best_auc = f1
                        self._best_threshold_at_best_auc = threshold_for_prediction
                        self.optimal_threshold = threshold_for_prediction
                        self._last_auc_improvement_epoch = epoch_idx  # Track when AUC improved
                        is_best_epoch = True
                        best_epoch_msg = f"⭐ New best epoch: AUC={auc:.3f}, F1={f1:.3f}, threshold={threshold_for_prediction:.4f} ({threshold_source})"
                    elif auc > self._best_auc + auc_epsilon:
                        # New best AUC - update best epoch tracking
                        previous_auc = self._best_auc
                        previous_epoch = self._best_auc_epoch
                        self._best_auc = auc
                        self._best_auc_epoch = epoch_idx
                        self._best_f1_at_best_auc = f1
                        self._best_threshold_at_best_auc = threshold_for_prediction
                        self.optimal_threshold = threshold_for_prediction
                        self._last_auc_improvement_epoch = epoch_idx  # Track when AUC improved
                        is_best_epoch = True
                        best_epoch_msg = f"⭐ New best epoch: AUC={auc:.3f} (previous best: {previous_auc:.3f} @ epoch {previous_epoch}), threshold={threshold_for_prediction:.4f} ({threshold_source})"
                    elif abs(auc - self._best_auc) <= auc_epsilon and f1 > self._best_f1_at_best_auc:
                        # AUC ties (within epsilon) but F1 improved - update best epoch
                        previous_f1 = self._best_f1_at_best_auc
                        previous_epoch = self._best_auc_epoch
                        self._best_auc_epoch = epoch_idx  # Update best epoch to current
                        self._best_f1_at_best_auc = f1
                        self._best_threshold_at_best_auc = threshold_for_prediction
                        self.optimal_threshold = threshold_for_prediction
                        self._last_auc_improvement_epoch = epoch_idx  # Track when AUC improved (F1 improvement counts)
                        is_best_epoch = True
                        best_epoch_msg = f"⭐ New best epoch: AUC tied ({auc:.3f}) but F1 improved to {f1:.3f} (previous: {previous_f1:.3f} @ epoch {previous_epoch}), threshold={threshold_for_prediction:.4f} ({threshold_source})"
                    else:
                        # Current epoch is not the best - track best for reference
                        best_epoch_msg = f"📊 Current: AUC={auc:.3f}, F1={f1:.3f}, threshold={threshold_for_prediction:.4f} ({threshold_source}) | Best: AUC={self._best_auc:.3f}, F1={self._best_f1_at_best_auc:.3f}, threshold={self._best_threshold_at_best_auc:.4f} @ epoch {self._best_auc_epoch}"
                    
                    # B: Enhanced logging showing what we're optimizing and tradeoffs
                    logger.debug(f"{log_prefix}📊 Threshold Optimization Summary:")
                    logger.info(f"{log_prefix}   Using {threshold_source} threshold: {threshold_for_prediction:.4f}")
                    logger.info(f"{log_prefix}   F1: argmax={argmax_f1:.3f}, optimal={f1:.3f}, ΔF1={delta_f1:+.3f}")
                    logger.info(f"{log_prefix}   Accuracy: argmax={argmax_accuracy:.3f}, optimal={accuracy_at_optimal:.3f}, ΔAcc={delta_accuracy:+.3f}")
                    if abs(delta_accuracy) > 0.01:  # Only show tradeoff if significant
                        tradeoff_direction = "cost" if delta_accuracy < 0 else "gain"
                        logger.info(f"{log_prefix}   Tradeoff: F1 improved by {delta_f1:.3f} at {tradeoff_direction} of {abs(delta_accuracy):.3f} accuracy")
                    
                    logger.debug(f"{log_prefix}Binary metrics (optimal threshold {threshold_for_prediction:.4f} - {threshold_source}) - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}, ROC-AUC: {auc:.3f}, PR-AUC: {pr_auc:.3f}")
                    logger.debug(f"{log_prefix}Imbalanced data metrics - Balanced Accuracy: {balanced_accuracy:.3f}, MCC: {mcc:.3f}, Specificity: {specificity:.3f}")
                    ece_str = f"{ece:.4f}" if ece is not None else "N/A"
                    mce_str = f"{mce:.4f}" if mce is not None else "N/A"
                    sharpness_str = f"{sharpness:.4f}" if sharpness is not None else "N/A"
                    logger.debug(f"{log_prefix}Calibration metrics - Brier Score: {brier_score:.4f}, ECE: {ece_str}, MCE: {mce_str}, Sharpness: {sharpness_str}")
                    if cost_metrics:
                        cost_savings_pct = ((baseline_cost - cost_min) / baseline_cost * 100) if baseline_cost > 0 else 0
                        logger.info(f"{log_prefix}💰 Cost metrics - Min cost: {cost_min:.2f} (baseline: {baseline_cost:.2f}, savings: {cost_savings_pct:.1f}%)")
                        logger.debug(f"{log_prefix}💰 Cost confusion at threshold {tau_cost:.3f}: TP={cost_metrics['tp_cost']}, FP={cost_metrics['fp_cost']}, TN={cost_metrics['tn_cost']}, FN={cost_metrics['fn_cost']}, F1={f1_cost:.3f}")
                    logger.debug(f"{log_prefix}Confusion Matrix - TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}, Specificity: {specificity:.3f}")
                    
                    # Log best epoch tracking
                    if is_best_epoch:
                        logger.info(f"{log_prefix}{best_epoch_msg}")
                    else:
                        logger.debug(f"{log_prefix}{best_epoch_msg}")
                    
                    # FAILURE DETECTION: Analyze training and detect common failure modes
                    # Use threshold-based predictions (not argmax) for accurate failure detection
                    failure_detected, failure_label, recommendations = self.detect_training_failure_mode(
                        raw_logits_array=raw_logits_array if 'raw_logits_array' in locals() else None,
                        pos_probs_array=pos_probs_array,
                        pred_counts=threshold_pred_counts,  # Use threshold-based counts, not argmax
                        y_true_binary=y_true_binary,
                        auc=auc,
                        accuracy=accuracy,
                        optimal_threshold=optimal_threshold,
                        epoch_idx=epoch_idx,
                        n_epochs=n_epochs,
                        log_prefix=log_prefix
                    )
                    
                    # SAVE: Store rare label for use during prediction
                    self._pos_label = pos_label
                    
                    # Note: optimal threshold info will be added to metrics_result below
                    
                    # CRITICAL FAILURE DETECTION: Raise specific exceptions for different failure modes
                    if failure_detected:
                        from featrix.neural.training_exceptions import (
                            RandomPredictionsError,
                            DeadNetworkError,
                            ConstantProbabilityError,
                            SingleClassBiasError,
                            PoorDiscriminationError,
                            UnderconfidentError,
                        )
                        
                        # Define which failures should immediately stop training
                        immediate_stop_failures = ["DEAD_NETWORK", "CONSTANT_PROBABILITY"]
                        
                        # Define failures that should stop if they persist beyond a threshold
                        # RANDOM_PREDICTIONS: Should stop only if we're past 80% of training and still random
                        late_stage_threshold = 0.80  # 80% through training
                        is_late_stage = n_epochs and epoch_idx > (n_epochs * late_stage_threshold)
                        
                        should_stop = False
                        exception_to_raise = None
                        
                        # Check immediate stop conditions and create appropriate exceptions
                        if "DEAD_NETWORK" in failure_label:
                            should_stop = True
                            exception_to_raise = DeadNetworkError(
                                message=f"Network outputs frozen at epoch {epoch_idx}",
                                epoch=epoch_idx,
                                recommendations=recommendations
                            )
                        
                        elif "CONSTANT_PROBABILITY" in failure_label:
                            # Check if we should abort based on:
                            # 1. We're past 25% of total epochs
                            # 2. prob_std is NOT growing (getting worse)
                            # 3. We haven't been stuck since the beginning (give it time to unwedge)
                            
                            # Calculate 25% threshold
                            abort_threshold_epoch = None
                            if n_epochs:
                                abort_threshold_epoch = max(1, int(n_epochs * 0.25))
                            
                            # Check if prob_std is growing (improving)
                            prob_std_growing = False
                            stuck_since_beginning = False
                            
                            if hasattr(self, '_prob_std_history') and len(self._prob_std_history) >= 3:
                                # Need at least 3 data points to detect growth
                                recent_stds = [std for _, std in self._prob_std_history[-3:]]
                                first_std = self._prob_std_history[0][1]
                                current_std = self._prob_std_history[-1][1]
                                
                                # Check if std is growing (trending upward)
                                if len(recent_stds) >= 2:
                                    # Simple trend: if last value > previous value, it's growing
                                    if recent_stds[-1] > recent_stds[-2]:
                                        prob_std_growing = True
                                    # Also check if we've improved from the start
                                    if current_std > first_std * 1.1:  # 10% improvement from start
                                        prob_std_growing = True
                                
                                # Check if we've been stuck since the beginning
                                # If first epoch already had low prob_std, we've been stuck from the start
                                if first_std < 0.03:  # First epoch was already constant
                                    stuck_since_beginning = True
                            
                            # Determine if we should abort
                            should_abort = False
                            abort_reason = ""
                            
                            if abort_threshold_epoch and epoch_idx >= abort_threshold_epoch:
                                # We're past 25% threshold
                                if prob_std_growing:
                                    # Don't abort if std is growing - model is improving
                                    should_abort = False
                                    abort_reason = f"prob_std is growing (improving), continuing despite constant probability"
                                elif stuck_since_beginning:
                                    # Don't abort if we've been stuck since the beginning - give it more time to unwedge
                                    should_abort = False
                                    abort_reason = f"stuck since beginning (first epoch prob_std was low), allowing more time to unwedge"
                                else:
                                    # We're past threshold, std not growing, and wasn't stuck from start - abort
                                    should_abort = True
                                    abort_reason = f"past 25% threshold (epoch {epoch_idx}/{n_epochs}), prob_std not growing, and wasn't stuck from beginning"
                            else:
                                # Not past threshold yet
                                should_abort = False
                                if abort_threshold_epoch:
                                    abort_reason = f"need epoch {abort_threshold_epoch}+ (25% of {n_epochs} epochs) to abort"
                                else:
                                    abort_reason = f"need 25% of total epochs to abort (n_epochs unknown)"
                            
                            if should_abort:
                                should_stop = True
                                exception_to_raise = ConstantProbabilityError(
                                    message=f"Model produces constant probabilities at epoch {epoch_idx} ({abort_reason})",
                                    epoch=epoch_idx,
                                    recommendations=recommendations
                                )
                            else:
                                logger.warning(f"⚠️  CONSTANT_PROBABILITY detected at epoch {epoch_idx} but continuing ({abort_reason})")
                                
                                # DISABLED: Auto LR increase on constant probability
                                # Increasing LR when model collapses to constant output is counterproductive.
                                # It tends to make the head bounce around priors or blow up, not recover ranking.
                                # 
                                # Recovery strategies (manual intervention recommended):
                                # 1. Lower LR (reduce learning rate)
                                # 2. Reset the head (reinitialize predictor head)
                                # 3. Freeze ES temporarily (freeze embedding space, train only head)
                                
                                # Get current LR for logging
                                optimizer = self._training_optimizer
                                if optimizer and len(optimizer.param_groups) > 0:
                                    lr_value = optimizer.param_groups[0]['lr']
                                else:
                                    lr_value = getattr(self, '_original_lr', 1e-3)
                                
                                logger.warning("="*80)
                                logger.warning("🚨 CONSTANT_PROBABILITY DETECTED - NO AUTO INTERVENTION")
                                logger.warning("="*80)
                                logger.warning(f"   Model collapsed to constant output at epoch {epoch_idx}")
                                logger.warning(f"   Current LR: {lr_value:.6e}")
                                logger.warning(f"   ⚠️  Auto LR increase DISABLED (increasing LR makes collapse worse)")
                                logger.warning(f"")
                                logger.warning(f"   Recommended recovery strategies:")
                                logger.warning(f"   1. Lower LR (reduce learning rate)")
                                logger.warning(f"   2. Reset the head (reinitialize predictor head)")
                                logger.warning(f"   3. Freeze ES temporarily (freeze embedding space, train only head)")
                                logger.warning("="*80)
                                
                                should_stop = False
                        
                        # Check late-stage failures (only stop if we're far into training)
                        elif "RANDOM_PREDICTIONS" in failure_label and is_late_stage:
                            should_stop = True
                            exception_to_raise = RandomPredictionsError(
                                message=f"Model still random at epoch {epoch_idx}/{n_epochs} (>{late_stage_threshold*100:.0f}% complete)",
                                epoch=epoch_idx,
                                recommendations=recommendations
                            )
                        
                        if should_stop and exception_to_raise:
                            error_message = f"💥 STOPPING TRAINING: {str(exception_to_raise)}\n"
                            error_message += "\n".join(recommendations)
                            logger.error(error_message)
                            raise exception_to_raise
                    
                    # CHECK FOR LOW LOGIT RANGE: Low logit range indicates compressed/saturated outputs
                    # DISABLED: Auto LR increase - same issue as constant probability (increasing LR makes it worse)
                    if 'raw_logits_array' in locals() and raw_logits_array is not None:
                        logit_range_val = float(raw_logits_array.max() - raw_logits_array.min())
                        
                        # Critical threshold: logit range < 0.5 indicates saturated/compressed outputs
                        if logit_range_val < 0.5 and epoch_idx >= 5:
                            # Get current LR for logging
                            optimizer = self._training_optimizer
                            if optimizer and len(optimizer.param_groups) > 0:
                                lr_value = optimizer.param_groups[0]['lr']
                            else:
                                lr_value = getattr(self, '_original_lr', 1e-3)
                            
                            logger.warning("="*80)
                            logger.warning("🚨 LOW LOGIT RANGE DETECTED - NO AUTO INTERVENTION")
                            logger.warning("="*80)
                            logger.warning(f"   Low logit range at epoch {epoch_idx}: {logit_range_val:.4f} (< 0.5 threshold)")
                            logger.warning(f"   Indicates model outputs are compressed/saturated (similar to constant probability)")
                            logger.warning(f"   Current LR: {lr_value:.6e}")
                            logger.warning(f"   ⚠️  Auto LR increase DISABLED (increasing LR makes collapse worse)")
                            logger.warning(f"")
                            logger.warning(f"   Recommended recovery strategies:")
                            logger.warning(f"   1. Lower LR (reduce learning rate)")
                            logger.warning(f"   2. Reset the head (reinitialize predictor head)")
                            logger.warning(f"   3. Freeze ES temporarily (freeze embedding space, train only head)")
                            logger.warning("="*80)
                    
                    # ADAPTIVE LOSS ADJUSTMENT: If reverse bias detected, adjust FocalLoss
                    if failure_detected and "SINGLE_CLASS_BIAS" in failure_label:
                        # Calculate ground truth counts from original labels
                        from collections import Counter
                        y_true_counts = Counter(ground_truth)
                        
                        # FIX TYPE MISMATCH: Normalize keys to strings for both dicts
                        # pred_counts has string keys (from dict keys), y_true_counts may have float keys
                        normalized_pred_counts = {str(k): v for k, v in pred_counts.items()}
                        normalized_true_counts = {str(k): v for k, v in y_true_counts.items()}
                        
                        # Try adaptive adjustment
                        adjustment_made = self.adjust_focal_loss_for_bias(
                            pred_counts=normalized_pred_counts,
                            y_true_counts=normalized_true_counts,
                            epoch_idx=epoch_idx
                        )
                        
                        if adjustment_made:
                            logger.info(f"🔧 Adaptive FocalLoss adjustment applied at epoch {epoch_idx}")
                    
                except (TrainingFailureException, EarlyStoppingException) as e:
                    # Re-raise training failure/early stopping exceptions - these should stop training, not be swallowed
                    logger.error(f"🚨 Training exception detected: {type(e).__name__}")
                    raise  # Re-raise to stop training
                except Exception as e:
                    # For other exceptions, log as warning and continue
                    logger.warning(f"Binary metrics failed: {e}")
                    precision = recall = f1 = auc = 0
                    tp = fp = tn = fn = 0
                    specificity = 0
                    self.handle_metrics_error("binary_metrics", e)
            else:
                # Multi-class classification metrics
                try:
                    
                    # Multi-class averages
                    precision = precision_score(ground_truth, preds, average='weighted', zero_division=0)
                    recall = recall_score(ground_truth, preds, average='weighted', zero_division=0)
                    f1 = f1_score(ground_truth, preds, average='weighted', zero_division=0)
                    macro_f1 = f1_score(ground_truth, preds, average='macro', zero_division=0)
                    weighted_f1 = f1  # Same as f1 above
                    
                    # Multi-class AUC (if possible)
                    try:

                        # Create probability matrix for multi-class AUC
                        unique_labels = sorted(set(ground_truth))
                        prob_matrix = []
                        for result in results:
                            prob_row = [result.get(label, 0) for label in unique_labels]
                            prob_matrix.append(prob_row)
                        
                        lb = LabelBinarizer()
                        y_true_binarized = lb.fit_transform(ground_truth)
                        
                        if len(unique_labels) > 2:
                            auc = roc_auc_score(y_true_binarized, prob_matrix, multi_class='ovr', average='weighted')
                        else:
                            auc = 0  # Fall back for edge cases
                            
                    except Exception:
                        auc = 0  # Multi-class AUC can be complex, skip if it fails
                    
                    num_tests_worked += 3
                    logger.info(f"{log_prefix}Multi-class metrics - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
                    logger.info(f"{log_prefix}Multi-class F1 scores - Macro: {macro_f1:.3f}, Weighted: {weighted_f1:.3f}")
                    
                except Exception as e:
                    logger.warning(f"Multi-class metrics failed: {e}")
                    precision = recall = f1 = macro_f1 = weighted_f1 = 0
                    self.handle_metrics_error("multiclass_metrics", e)

            dt = time.time() - ts
            self.metrics_time += dt

            if num_tests_worked == 0:
                logger.warning(f"No classification metrics could be computed... skipping computation going forward.")
                self.run_binary_metrics = False

            logger.info(f"{log_prefix}Finished computing {'binary' if is_binary else 'multi-class'} metrics. Time: {dt:.2f}s")
            
            # Collect failure detection info if available (from binary path)
            failure_info = {}
            if 'failure_detected' in locals():
                failure_info = {
                    "failure_detected": failure_detected,
                    "failure_label": failure_label if failure_detected else None,
                    "recommendations": recommendations if failure_detected else []
                }
            
            # Return comprehensive metrics for both binary and multi-class
            metrics_result = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "auc": auc,
                "pr_auc": pr_auc if is_binary and 'pr_auc' in locals() else None,  # PR-AUC (only for binary)
                "is_binary": is_binary,
                "num_classes": len(self.target_codec.members) - 1,  # Exclude <UNKNOWN>
                "_had_error": self.metrics_had_error,
                "metrics_secs": self.metrics_time,
            }
            
            # Add abstention metrics for binary classification (if available)
            if is_binary and 'pct_unknown_predicted' in locals():
                metrics_result["pct_unknown_predicted"] = pct_unknown_predicted
                metrics_result["n_unknown_predictions"] = n_unknown
                metrics_result["n_non_unknown_predictions"] = n_non_unknown
                if auc_non_unknown is not None:
                    metrics_result["auc_non_unknown"] = auc_non_unknown
            
            # Add optimal threshold info for binary classification (if computed)
            if is_binary and hasattr(self, 'optimal_threshold') and self.optimal_threshold is not None:
                metrics_result['optimal_threshold'] = self.optimal_threshold
                # Add threshold mode and value for clear reporting
                # This makes it explicit which threshold was used for all metrics
                if 'threshold_mode' in locals():
                    metrics_result['threshold_mode'] = threshold_mode
                    metrics_result['threshold_value'] = threshold_value
                # Get F1 and accuracy from history if available
                if self.optimal_threshold_history:
                    last_entry = self.optimal_threshold_history[-1]
                    metrics_result['optimal_threshold_f1'] = last_entry.get('f1_score', f1)
                    # Note: accuracy, precision, recall, f1 in metrics_result are already optimal threshold values
                    metrics_result['accuracy_at_optimal_threshold'] = last_entry.get('accuracy_at_optimal', accuracy)
                metrics_result['pos_label'] = getattr(self, '_pos_label', None)
                
                # Add prediction distribution (threshold-based, not argmax)
                has_threshold_counts = 'threshold_pred_counts' in locals() and threshold_pred_counts
                has_pred_counts = 'pred_counts' in locals() and pred_counts
                logger.info(f"{log_prefix}🔍 PREDICTION DISTRIBUTION DEBUG: has_threshold_counts={has_threshold_counts}, has_pred_counts={has_pred_counts}")
                
                if has_threshold_counts:
                    metrics_result['prediction_distribution'] = dict(threshold_pred_counts)
                    logger.info(f"{log_prefix}   Using threshold_pred_counts: {dict(threshold_pred_counts)}")
                # Fallback: use argmax-based counts if threshold counts not available
                elif has_pred_counts:
                    metrics_result['prediction_distribution'] = dict(pred_counts)
                    logger.info(f"{log_prefix}   Using pred_counts: {dict(pred_counts)}")
                else:
                    logger.error(f"{log_prefix}   ❌ NO PREDICTION COUNTS AVAILABLE!")
            else:
                # Multi-class or binary without threshold: use argmax-based prediction distribution
                if 'pred_counts' in locals() and pred_counts:
                    metrics_result['prediction_distribution'] = dict(pred_counts)
                
                # Store argmax metrics (0.5 threshold) for comparison if available
                # These show what metrics would be with default threshold
                if 'argmax_accuracy' in locals():
                    metrics_result['argmax_accuracy'] = argmax_accuracy
                    metrics_result['argmax_precision'] = argmax_precision
                    metrics_result['argmax_recall'] = argmax_recall
                    metrics_result['argmax_f1'] = argmax_f1
                
                # Add imbalanced data metrics
                if 'balanced_accuracy' in locals():
                    metrics_result['balanced_accuracy'] = balanced_accuracy
                if 'mcc' in locals():
                    metrics_result['mcc'] = mcc
                if 'specificity' in locals():
                    metrics_result['specificity'] = specificity
                if 'tpr' in locals():
                    metrics_result['tpr'] = tpr
                
                # Add calibration metrics
                if 'brier_score' in locals():
                    metrics_result['brier_score'] = brier_score
                if 'ece' in locals() and ece is not None:
                    metrics_result['ece'] = ece
                if 'mce' in locals() and mce is not None:
                    metrics_result['mce'] = mce
                if 'sharpness' in locals() and sharpness is not None:
                    metrics_result['sharpness'] = sharpness
                if 'reliability_curve' in locals() and reliability_curve is not None:
                    metrics_result['reliability_curve'] = reliability_curve
                
                # Add banding/lift-style metric (positive:negative ratio across probability bands)
                if 'bands_data' in locals() and bands_data is not None:
                    metrics_result['binary_lift_bands'] = bands_data
                
                # Add cost metrics if available
                if 'cost_metrics' in locals() and cost_metrics:
                    metrics_result['cost_min'] = cost_metrics['cost_min']
                    metrics_result['tau_cost'] = cost_metrics['tau_cost']
                    metrics_result['f1_cost'] = cost_metrics['f1_cost']
                    metrics_result['baseline_cost'] = cost_metrics['baseline_cost']
                    metrics_result['pos_rate'] = ground_truth_pos_rate if 'ground_truth_pos_rate' in locals() else 0.0
                    
                    # Compute composite score
                    cost_metrics_for_score = {
                        "roc_auc": auc,
                        "pr_auc": pr_auc,
                        "cost_min": cost_metrics['cost_min'],
                        "pos_rate": ground_truth_pos_rate if 'ground_truth_pos_rate' in locals() else 0.0,
                    }
                    composite_score, score_components = self._compute_composite_score(
                        cost_metrics_for_score,
                        cost_metrics['baseline_cost']
                    )
                    metrics_result['composite_score'] = composite_score
                    metrics_result['score_components'] = score_components
            
            # Add failure detection info if present
            if failure_info:
                metrics_result.update(failure_info)
            
            # Add multi-class specific metrics
            if not is_binary:
                metrics_result.update({
                    "macro_f1": macro_f1,
                    "weighted_f1": weighted_f1,
                })
            else:
                # Add binary-specific metrics (like threshold)
                metrics_result.update({
                    "accuracy_threshold": getattr(self, '_last_accuracy_threshold', None),
                })
                
                # Add confusion matrix if available (binary classification only)
                if 'tp' in locals() and 'fp' in locals() and 'tn' in locals() and 'fn' in locals():
                    metrics_result.update({
                        "tp": int(tp),
                        "fp": int(fp),
                        "tn": int(tn),
                        "fn": int(fn),
                        "specificity": float(specificity) if 'specificity' in locals() else None,
                    })
                
                # AUC PLATEAU EARLY STOPPING: Adaptive patience based on total epochs
                # For short runs (50 epochs), we can't wait 50 epochs to check!
                # Start checking after 20% of epochs (min 10), patience = 20% of epochs (min 10) + 25
                n_epochs_total = getattr(self, '_total_epochs', 100)  # Set during train()
                min_epochs_before_check = max(10, int(n_epochs_total * 0.2))
                patience_epochs = max(10, int(n_epochs_total * 0.2)) + 25
                
                if 'auc' in locals() and epoch_idx >= min_epochs_before_check and self._last_auc_improvement_epoch >= 0:
                    epochs_since_improvement = epoch_idx - self._last_auc_improvement_epoch
                    if epochs_since_improvement >= patience_epochs:
                        logger.warning(f"{log_prefix}⚠️  AUC PLATEAU DETECTED: AUC has not improved for {epochs_since_improvement} epochs")
                        logger.warning(f"{log_prefix}   Last improvement: epoch {self._last_auc_improvement_epoch} (AUC={self._best_auc:.4f})")
                        logger.warning(f"{log_prefix}   Current epoch: {epoch_idx} (AUC={auc:.4f})")
                        logger.warning(f"{log_prefix}   🛑 Stopping training early due to AUC plateau")
                        
                        # Store early stopping info to raise exception AFTER best model is saved
                        self._early_stop_exception = EarlyStoppingException(
                            message=f"AUC has not improved for {epochs_since_improvement} epochs (last improvement at epoch {self._last_auc_improvement_epoch})",
                            epoch=epoch_idx,
                            recommendations=[
                                f"AUC plateau detected: no improvement for {epochs_since_improvement} epochs",
                                f"Best AUC: {self._best_auc:.4f} at epoch {self._best_auc_epoch}",
                                f"Current AUC: {auc:.4f} at epoch {epoch_idx}",
                                "Training stopped early to prevent wasted computation"
                            ],
                            best_epoch=self._best_auc_epoch,
                            best_metric=self._best_auc
                        )
                        # Set flag for loop termination (will break out gracefully)
                        # These flags will be checked in the train() method to break the epoch loop
                        self._early_stop_reason = f"AUC plateau: no improvement for {epochs_since_improvement} epochs"
                        self._training_interrupted = "AUC plateau early stop"
                        
                        # Report to featrix-monitor about early stopping
                        try:
                            from lib.training_monitor import post_training_anomaly
                            post_training_anomaly(
                                session_id=getattr(self, 'job_id', 'unknown'),
                                anomaly_type="early_stopping",
                                epoch=epoch_idx,
                                dataset_hash=getattr(self, '_dataset_hash', None),  # TOP-LEVEL parameter
                                details={
                                    "collapse_type": "auc_plateau",
                                    "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                                    # Plateau details
                                    "epochs_without_improvement": epochs_since_improvement,
                                    "patience_threshold": patience_epochs,
                                    # Best model info
                                    "best_auc": float(self._best_auc),
                                    "best_epoch": self._best_auc_epoch,
                                    "best_pr_auc": float(getattr(self, '_best_pr_auc', -1)) if getattr(self, '_best_pr_auc', -1) >= 0 else None,
                                    "best_pr_auc_epoch": getattr(self, '_best_pr_auc_epoch', -1) if getattr(self, '_best_pr_auc_epoch', -1) >= 0 else None,
                                    # Current metrics
                                    "current_auc": float(auc),
                                    "current_epoch": epoch_idx,
                                    # Training config
                                    "batch_size": batch_size,
                                    "total_epochs_planned": n_epochs if 'n_epochs' in locals() else None,
                                    "completion_percentage": (epoch_idx / n_epochs * 100) if 'n_epochs' in locals() and n_epochs > 0 else 0,
                                }
                            )
                        except Exception as monitor_err:
                            logger.warning(f"⚠️  Failed to report early stopping to monitor: {monitor_err}")
                        
                        # Break out of metrics computation to allow loop to detect early stop
                        # The exception will be raised at the end of train() after best model is saved
                        return metrics_result
                    elif epochs_since_improvement >= 25 and epochs_since_improvement % 10 == 0:
                        # Log warning every 10 epochs after 25 epochs without improvement
                        logger.warning(f"{log_prefix}⚠️  AUC plateau warning: {epochs_since_improvement} epochs since last improvement (will stop at 50)")
                
                # Add positive prediction probabilities for distribution analysis
                if 'pos_probs_array' in locals() and pos_probs_array is not None:
                    metrics_result['pos_probs'] = pos_probs_array.tolist()
                
                # DIAGNOSTIC SUMMARY: Log key metrics for easy tracking
                # CRITICAL: Check if arrays exist (debug logging)
                has_pos_probs = 'pos_probs_array' in locals()
                has_raw_logits = 'raw_logits_array' in locals()
                logger.info(f"{log_prefix}🔍 BINARY METRICS DEBUG: has_pos_probs={has_pos_probs}, has_raw_logits={has_raw_logits}")
                
                if has_pos_probs and has_raw_logits:
                    logger.debug(f"{log_prefix}📈 EPOCH DIAGNOSTIC SUMMARY:")
                    logit_range_val = raw_logits_array.max() - raw_logits_array.min()
                    prob_std_val = pos_probs_array.std()
                    logger.info(f"{log_prefix}   Logits: range={logit_range_val:.2f}, std={raw_logits_array.std():.4f}")
                    logger.info(f"{log_prefix}   Probs:  range={pos_probs_array.max() - pos_probs_array.min():.4f}, std={prob_std_val:.4f}")
                    logger.info(f"{log_prefix}   AUC: {auc:.4f}, F1: {f1:.4f}, Accuracy: {accuracy:.4f}")
                    
                    # Store for structured logging
                    metrics_result['logit_range'] = float(logit_range_val)
                    metrics_result['prob_std'] = float(prob_std_val)
                elif has_pos_probs:
                    # We have probs but not logits - still compute prob_std
                    prob_std_val = pos_probs_array.std()
                    logger.info(f"{log_prefix}   ⚠️  raw_logits_array not in locals() - only storing prob_std")
                    logger.info(f"{log_prefix}   Probs:  range={pos_probs_array.max() - pos_probs_array.min():.4f}, std={prob_std_val:.4f}")
                    metrics_result['prob_std'] = float(prob_std_val)
                    metrics_result['logit_range'] = 0.0  # Default
                else:
                    logger.error(f"{log_prefix}   ❌ CRITICAL: pos_probs_array not in locals()! Cannot compute prob_std/logit_range")
                    metrics_result['prob_std'] = 0.0
                    metrics_result['logit_range'] = 0.0
            
            # Record quality checks
            if epoch_idx is not None:
                try:
                    from featrix.neural.customer_quality_tracker import QualityCheckName, QualityGrade
                    qt = self.get_quality_tracker(epoch_idx)
                    
                    # Record model performance
                    if 'auc' in metrics_result and metrics_result['auc'] > 0:
                        auc_score = metrics_result['auc']
                        if auc_score >= 0.80:
                            perf_grade = QualityGrade.A
                        elif auc_score >= 0.70:
                            perf_grade = QualityGrade.B
                        elif auc_score >= 0.60:
                            perf_grade = QualityGrade.C
                        elif auc_score >= 0.50:
                            perf_grade = QualityGrade.D
                        else:
                            perf_grade = QualityGrade.F
                        
                        qt.record_check(
                            name=QualityCheckName.MODEL_PERFORMANCE,
                            graded_score=perf_grade,
                            metadata={
                                "auc": auc_score,
                                "accuracy": metrics_result.get('accuracy', 0),
                                "f1": metrics_result.get('f1', 0),
                                "precision": metrics_result.get('precision', 0),
                                "recall": metrics_result.get('recall', 0),
                                "pr_auc": metrics_result.get('pr_auc'),
                            }
                        )
                    
                    # Record calibration quality (for binary classification)
                    if is_binary and 'brier_score' in metrics_result:
                        brier = metrics_result['brier_score']
                        if brier < 0.15:
                            cal_grade = QualityGrade.A
                        elif brier < 0.20:
                            cal_grade = QualityGrade.B
                        elif brier < 0.25:
                            cal_grade = QualityGrade.C
                        elif brier < 0.30:
                            cal_grade = QualityGrade.D
                        else:
                            cal_grade = QualityGrade.F
                        
                        qt.record_check(
                            name=QualityCheckName.CALIBRATION_QUALITY,
                            graded_score=cal_grade,
                            metadata={
                                "brier_score": brier,
                                "ece": metrics_result.get('ece'),
                                "mce": metrics_result.get('mce'),
                            }
                        )
                    
                    # Record training failure detection
                    if 'failure_detected' in metrics_result and metrics_result['failure_detected']:
                        qt.record_check(
                            name=QualityCheckName.TRAINING_FAILURE_DETECTION,
                            graded_score=QualityGrade.FAIL,
                            metadata={
                                "failure_label": metrics_result.get('failure_label'),
                                "recommendations": metrics_result.get('recommendations', []),
                            }
                        )
                    else:
                        qt.record_check(
                            name=QualityCheckName.TRAINING_FAILURE_DETECTION,
                            graded_score=QualityGrade.PASS,
                            metadata={}
                        )
                except Exception as e:
                    logger.debug(f"{log_prefix}   Failed to record quality checks: {e}")
            
            return metrics_result
    
    def compute_binary_metrics(self, queries, ground_truth, pos_label):
        """
        Legacy compatibility method - redirects to compute_classification_metrics.
        
        This method is deprecated. Use compute_classification_metrics instead.
        """
        logger.warning("compute_binary_metrics is deprecated. Use compute_classification_metrics instead.")
        return self.compute_classification_metrics(queries, ground_truth, pos_label)

    def predict(self, input_dict: Dict, print_top: bool = False, ignore_unknown=False, debug_print=True, extended_result=False):

        if input_dict.get(self.target_col_name) is not None:
            raise RuntimeError(
                "The query input contains the target column of the model"
            )

        if self.target_codec is None:
            raise Exception("Cannot predict before the predictor is trained.")

        # Ensure predictor is available (reconstruct if needed)
        self._ensure_predictor_available()
        
        # CRITICAL: Apply feature engineering if it exists
        # This ensures training/inference consistency for derived features
        if self.feature_engineer is not None:
            try:
                # Convert dict to DataFrame for feature engineering
                import pandas as pd
                df_single = pd.DataFrame([input_dict])
                
                # Apply feature transformations
                df_enhanced = self.feature_engineer.transform(df_single, verbose=False)
                
                # Convert back to dict (take first row)
                input_dict = df_enhanced.iloc[0].to_dict()
                
                if debug_print:
                    added_cols = set(df_enhanced.columns) - set(df_single.columns)
                    if added_cols:
                        logger.debug(f"🔧 Applied feature engineering: {len(added_cols)} derived features added")
            except Exception as fe_error:
                logger.warning(f"⚠️  Feature engineering failed during prediction: {fe_error}")
                logger.warning(f"   Continuing with original input (may affect prediction quality)")
                # Continue with original input_dict

        with PredictorEvalModeContextManager(fsp=self, debugLabel="predict"):
            # ASSERT: We must be in eval mode for prediction
            assert self.predictor.training == False, f"❌ PREDICT BUG: predictor should be in eval mode but training={self.predictor.training}"
            assert self.embedding_space.encoder.training == False, f"❌ PREDICT BUG: encoder should be in eval mode but training={self.embedding_space.encoder.training}"

            ####################################################### DO THE ACTUAL PREDICTION!!!
            # Only use full-dimensional embeddings for predictions.
            # CRITICAL: Use predictor's device, not global device variable
            # This ensures encoding is on same device as model (e.g., MPS on Mac)
            predictor_device = next(self.predictor.parameters()).device if list(self.predictor.parameters()) else get_device()
            encoding = self.embedding_space.encode_record(input_dict, 
                                                          squeeze=False,
                                                          short=False,
                                                          output_device=predictor_device)
            out = self.predictor(encoding)
            
            ###################################################################################

            # TODO: how to handle nans in the domain?
            #       they should probably not even enter in the domain of the codec.
            # logger.debug("self.target_type... --> ", self.target_type)

            if isinstance(self.target_codec, (SetEncoder, SetCodec)):
                # Apply calibration if available
                if self.calibration_method == 'temperature' and self.calibration_temperature is not None:
                    from featrix.neural.calibration_utils import apply_temperature_scaling
                    calibrated_out = apply_temperature_scaling(out, self.calibration_temperature)
                    probs = self.sm(calibrated_out).squeeze(dim=0)
                elif self.calibration_method == 'platt' and self.calibration_platt_model is not None:
                    from featrix.neural.calibration_utils import apply_platt_scaling
                    calibrated_probs_np = apply_platt_scaling(out, self.calibration_platt_model)
                    # Convert back to tensor for consistency (already probabilities, not logits)
                    probs = torch.from_numpy(calibrated_probs_np[0]).to(out.device)
                elif self.calibration_method == 'isotonic' and self.calibration_isotonic_model is not None:
                    from featrix.neural.calibration_utils import apply_isotonic_regression
                    calibrated_probs_np = apply_isotonic_regression(out, self.calibration_isotonic_model)
                    # Convert back to tensor for consistency (already probabilities, not logits)
                    probs = torch.from_numpy(calibrated_probs_np[0]).to(out.device)
                else:
                    # No calibration or calibration method not available
                    probs = self.sm(out).squeeze(dim=0)
                
                # DIAGNOSTIC: Log token mapping for debugging backwards predictions
                debug_count = getattr(self, '_predict_debug_count', 0)
                if debug_count < 3:  # Only log first 3 predictions
                    logger.info(f"🔍 PREDICTION DEBUG #{debug_count}:")
                    logger.info(f"   Raw logits: {out.squeeze(dim=0).tolist()}")
                    logger.info(f"   Softmax probs: {probs.tolist()}")
                    logger.info(f"   Token mapping: {self.target_codec.tokens_to_members}")
                    self._predict_debug_count = debug_count + 1
                
                # Check if this is binary classification
                is_binary = self.should_compute_binary_metrics()
                
                if is_binary:
                    # BINARY CLASSIFICATION: Output is 2-dim (excludes <UNKNOWN>)
                    # Get the two class labels (excluding <UNKNOWN>)
                    real_members = [m for m in self.target_codec.members if m != "<UNKNOWN>"]
                    assert len(real_members) == 2, f"Binary classification should have 2 classes, found {len(real_members)}: {real_members}"
                    
                    # Map logits to class labels (probs is already softmax over 2 classes)
                    # probs[0] corresponds to first real member, probs[1] to second
                    class0_label = real_members[0]
                    class1_label = real_members[1]
                    
                    # Get probabilities for the two classes
                    p_class0 = probs[0].item()
                    p_class1 = probs[1].item()
                    
                    # Determine which is "bad" and which is "good" (or pos/neg)
                    # Use stored pos_label if available, otherwise use first class as default
                    pos_label = getattr(self, '_pos_label', None)
                    if pos_label is None and self.training_metrics and 'pos_label' in self.training_metrics:
                        pos_label = self.training_metrics['pos_label']
                        self._pos_label = pos_label
                    
                    # Map to bad/good based on pos_label
                    if pos_label == class0_label:
                        p_bad = p_class1  # negative class
                        p_good = p_class0  # positive class
                        bad_label = class1_label
                        good_label = class0_label
                    elif pos_label == class1_label:
                        p_bad = p_class0  # negative class
                        p_good = p_class1  # positive class
                        bad_label = class0_label
                        good_label = class1_label
                    else:
                        # No pos_label stored, use first as "bad", second as "good"
                        p_bad = p_class0
                        p_good = p_class1
                        bad_label = class0_label
                        good_label = class1_label
                    
                    # MARGIN-BASED ABSTENTION
                    # Compute margin: distance from 0.5 (uncertainty)
                    margin = abs(p_bad - 0.5)
                    
                    # Threshold for abstention (tau) - default 0.05-0.10, configurable
                    tau = getattr(self, '_abstention_threshold', 0.05)
                    
                    # Compute p_unknown based on margin
                    if margin < tau:
                        # Low confidence: high p_unknown
                        p_unknown = max(0.0, min(1.0, 1.0 - (margin / tau)))
                    else:
                        # High confidence: low p_unknown
                        p_unknown = 0.0
                    
                    # Scale probabilities by (1 - p_unknown) so they sum to 1 with p_unknown
                    scale_factor = 1.0 - p_unknown
                    p_bad_scaled = p_bad * scale_factor
                    p_good_scaled = p_good * scale_factor
                    
                    # Build result dictionary
                    result_dict = {
                        bad_label: p_bad_scaled,
                        good_label: p_good_scaled,
                        "<UNKNOWN>": p_unknown
                    }
                    
                    # Apply optimal threshold if available (for prediction label, not probabilities)
                    use_optimal_threshold = self.optimal_threshold is not None
                    if use_optimal_threshold:
                        # Threshold applies to p_good (positive class probability)
                        # But we need to use the original p_good before scaling
                        if p_good >= self.optimal_threshold:
                            predicted_label = good_label
                        else:
                            predicted_label = bad_label
                    else:
                        # Use argmax on scaled probabilities (excluding <UNKNOWN>)
                        if p_good_scaled > p_bad_scaled:
                            predicted_label = good_label
                        else:
                            predicted_label = bad_label
                    
                    # If margin is too low, predict <UNKNOWN> as the label
                    if margin < tau:
                        predicted_label = "<UNKNOWN>"
                
                else:
                    # MULTI-CLASS: Original behavior (includes <UNKNOWN> in output)
                    probs_dict = {
                        self.target_codec.detokenize(
                            Token(value=i, status=TokenStatus.OK)
                        ): prob.item()
                        for i, prob in enumerate(probs)
                    }
                    result_dict = probs_dict
                    predicted_label = max(result_dict.items(), key=lambda x: x[1])[0]
                
                if ignore_unknown:
                    # Use None to avoid throwing an exception in case <UNKNOWN> is not in the result set.
                    result_dict.pop("<UNKNOWN>", None)
                    # Rebalance the probabilities of remaining keys to sum to 1.
                    # An alternative would be to leave the probabilities as-is, but
                    # the fact that they don't sum to 1 could be confusing to the user.
                    prob_total = sum(result_dict.values())
                    if prob_total > 0:
                        result_dict = {k: v / prob_total for k, v in result_dict.items()}
            elif isinstance(self.target_codec, AdaptiveScalarEncoder):
                theValue = self.target_codec.detokenize(
                    Token(value=out[0].item(), status=TokenStatus.OK)
                )
                result_dict = {self.target_col_name: theValue}
            else:
                assert False, "Unknown target codec: %s" % self.target_codec

        # Build calibration metadata
        calibration_meta = None
        if self.calibration_metrics is not None:
            # Map internal method names to user-facing names
            method_map = {
                'temperature': 'temperature_scaling',
                'platt': 'platt',
                'isotonic': 'isotonic',
                'none': None
            }
            method_name = method_map.get(self.calibration_method, None)
            
            # Always include calibration metadata if we have candidate scores
            candidate_scores = self.calibration_metrics.get('candidate_scores', {})
            if candidate_scores:
                calibration_meta = {
                    "method": method_name if method_name else None,
                    "params": {},
                    "candidate_scores": {}
                }
                
                # Add method-specific parameters
                if self.calibration_method == 'temperature' and self.calibration_temperature is not None:
                    calibration_meta["params"]["T"] = float(self.calibration_temperature)
                
                # Add candidate scores (NLL for each method)
                for method_key, scores in candidate_scores.items():
                    if 'nll' in scores:
                        calibration_meta["candidate_scores"][method_key] = {
                            "nll": float(scores['nll'])
                        }
        
        if extended_result:
            
            original_query = copy.copy(input_dict)
            actual_query = {}
            ignored_query_columns = []
            available_query_columns = list(self.all_codecs.keys())
            # codec_keys = list(self.all_codecs.keys())
            for k, v in original_query.items():
                if k in available_query_columns:
                    actual_query[k] = v
                else:
                    ignored_query_columns.append(k)
            
            # Extract prediction (label) and confidence (probability) from result_dict
            # For classification: prediction is the class with highest probability
            # For regression: prediction is the value itself
            predicted_label = None
            confidence = None
            if isinstance(result_dict, dict):
                # Filter to only probability values (exclude metadata keys)
                prob_items = [(k, v) for k, v in result_dict.items() 
                             if isinstance(v, (int, float)) and k not in ('calibration', '_meta')]
                if prob_items:
                    predicted_label, confidence = max(prob_items, key=lambda x: x[1])
            
            result = {
                "_meta": {
                    "compute_cluster": socket.gethostname(),
                    "compute_cluster_time": datetime.utcnow().isoformat() + "Z",
                    "model_warnings": self.get_model_warnings(include_epoch_details=False) if self.has_warnings() else None,
                    "training_quality_warning": self.get_training_quality_warning(),
                },
                "prediction": predicted_label,  # THE answer - the predicted label
                "confidence": confidence,       # probability of the predicted class
                "original_query": original_query,
                "actual_query": actual_query,
                "ignored_query_columns": ignored_query_columns,
                "available_query_columns": available_query_columns,
                "results": result_dict,
            }
            
            # Add threshold for binary classification
            if self.optimal_threshold is not None:
                result["threshold"] = float(self.optimal_threshold)
            
            # Add calibration metadata if available
            if calibration_meta:
                result["calibration"] = calibration_meta
            
            return result
        else:
            # Simple result - extract prediction and confidence
            predicted_label = None
            confidence = None
            if isinstance(result_dict, dict):
                prob_items = [(k, v) for k, v in result_dict.items() 
                             if isinstance(v, (int, float)) and k not in ('calibration', '_meta')]
                if prob_items:
                    predicted_label, confidence = max(prob_items, key=lambda x: x[1])
            
            simple_result = {
                "prediction": predicted_label,  # THE answer
                "confidence": confidence,       # probability of predicted class
                "probabilities": result_dict,   # full distribution
            }
            
            # Add threshold for binary classification
            if self.optimal_threshold is not None:
                simple_result["threshold"] = float(self.optimal_threshold)
            
            # Add calibration metadata if available
            if calibration_meta:
                simple_result["calibration"] = calibration_meta
            
            return simple_result

    def predict_batch(self, records_list: List[Dict], batch_size: int = 256, debug_print: bool = False, extended_result: bool = False, progress_callback = None):
        """
        Predict on a batch of records efficiently using GPU batching.
        
        Args:
            records_list: List of dictionaries to predict on
            batch_size: Number of records to process in each GPU batch
            debug_print: Whether to print debug info
            extended_result: Whether to return extended metadata including guardrails
            progress_callback: Optional callback function(current, total, message) for progress updates
            
        Returns:
            List of prediction results (same order as input)
        """
        if not records_list:
            return []
            
        if self.target_codec is None:
            raise Exception("Cannot predict before the predictor is trained.")
        
        # Ensure predictor is available (reconstruct if needed)
        self._ensure_predictor_available()
        
        # Check for target column in any record
        for record in records_list:
            if record.get(self.target_col_name) is not None:
                raise RuntimeError("Query input contains the target column of the model")
        
        all_predictions = []
        
        # Run guardrails analysis on all records if extended_result is requested
        guardrails_results = None
        if extended_result:
            from featrix.neural.guardrails import RunGuardrails
            guardrails_results = RunGuardrails(records_list, self, issues_only=False)
        
        with PredictorEvalModeContextManager(fsp=self, debugLabel="predict_batch"):
            # Process records in batches for GPU efficiency
            total_batches = (len(records_list) + batch_size - 1) // batch_size
            for batch_idx, batch_start in enumerate(range(0, len(records_list), batch_size)):
                batch_end = min(batch_start + batch_size, len(records_list))
                batch_records = records_list[batch_start:batch_end]
                
                if debug_print:
                    logger.info(f"Processing batch {batch_start}-{batch_end} ({len(batch_records)} records)")
                
                # Report progress if callback provided
                if progress_callback:
                    progress_callback(batch_idx, total_batches, f"Processing batch {batch_idx + 1}/{total_batches} ({batch_end}/{len(records_list)} records)")
                
                # Convert records to DataFrame for batching
                batch_df = pd.DataFrame(batch_records)
                
                # Create dataset and dataloader for efficient batching
                dataset = SuperSimpleSelfSupervisedDataset(batch_df, self.all_codecs)
                dataloader = DataLoader(
                    dataset,
                    batch_size=len(batch_df),  # Process entire batch at once
                    shuffle=False,
                    collate_fn=collate_tokens,
                )
                
                # Get the single batch
                column_batch = next(iter(dataloader))
                
                # Move to device
                for key, tokenbatch in column_batch.items():
                    column_batch[key] = tokenbatch.to(get_device())
                
                # Remove target column if present (for marginal encoding)
                if self.target_col_name in column_batch:
                    target_token_batch = column_batch.pop(self.target_col_name)
                    
                    # Add marginal tokens if target was in original embedding space
                    if self.target_col_name in self.embedding_space.col_codecs:
                        marginal_token_batch = self._create_marginal_token_batch_for_target(target_token_batch)
                        column_batch[self.target_col_name] = marginal_token_batch
                
                # Encode the entire batch at once - MASSIVE SPEEDUP!
                _, batch_encoding = self.embedding_space.encoder.encode(column_batch, apply_noise=False)
                
                # CRITICAL: Move batch_encoding to same device as predictor to avoid tensor device mismatch
                predictor_device = next(self.predictor.parameters()).device
                batch_encoding = batch_encoding.to(predictor_device)
                
                # Run predictor on entire batch
                batch_output = self.predictor(batch_encoding)
                
                # Convert batch output to individual predictions
                predictions = []
                for i, record in enumerate(batch_records):
                    single_output = batch_output[i:i+1]  # Keep batch dimension
                    prediction = self._convert_output_to_prediction(single_output)
                    
                    if extended_result:
                        # Add extended metadata for this record
                        import copy
                        original_query = copy.copy(record)
                        actual_query = {}
                        ignored_query_columns = []
                        available_query_columns = list(self.all_codecs.keys())
                        
                        for k, v in original_query.items():
                            if k in available_query_columns:
                                actual_query[k] = v
                            else:
                                ignored_query_columns.append(k)
                        
                        extended_prediction = {
                            "original_query": original_query,
                            "actual_query": actual_query,
                            "ignored_query_columns": ignored_query_columns,
                            "available_query_columns": available_query_columns,
                            "results": prediction,
                            "guardrails": guardrails_results,  # Guardrails for all records (could be optimized per record)
                            "model_warnings": self.get_model_warnings(include_epoch_details=False) if self.has_warnings() else None,
                        }
                        predictions.append(extended_prediction)
                    else:
                        predictions.append(prediction)
                
                all_predictions.extend(predictions)
        
        return all_predictions
    
    def _convert_output_to_prediction(self, model_output):
        """
        Convert raw model output to prediction dictionary.
        
        Returns dict with:
            - prediction: the predicted label (classification) or value (regression)
            - confidence: probability of predicted class (classification only)
            - probabilities: full probability distribution (classification only)
            - threshold: optimal threshold used (binary classification only)
        """
        if isinstance(self.target_codec, (SetEncoder, SetCodec)):
            # Classification: convert to probabilities
            probs = self.sm(model_output).squeeze(dim=0)
            
            # Check if binary classification
            is_binary = self.should_compute_binary_metrics()
            
            if is_binary:
                # BINARY CLASSIFICATION: Output is 2-dim (excludes <UNKNOWN>)
                # Get the two class labels (excluding <UNKNOWN>)
                real_members = [m for m in self.target_codec.members if m != "<UNKNOWN>"]
                assert len(real_members) == 2, f"Binary classification should have 2 classes, found {len(real_members)}: {real_members}"
                
                # Map probabilities to class labels
                class0_label = real_members[0]
                class1_label = real_members[1]
                
                # Get probabilities for the two classes
                p_class0 = probs[0].item()
                p_class1 = probs[1].item()
                
                # Determine which is positive class
                pos_label = getattr(self, '_pos_label', None)
                if pos_label is None and hasattr(self, 'training_metrics') and self.training_metrics and 'pos_label' in self.training_metrics:
                    pos_label = self.training_metrics['pos_label']
                    self._pos_label = pos_label
                
                # Map to bad/good based on pos_label
                if pos_label == class0_label:
                    p_bad = p_class1
                    p_good = p_class0
                    bad_label = class1_label
                    good_label = class0_label
                elif pos_label == class1_label:
                    p_bad = p_class0
                    p_good = p_class1
                    bad_label = class0_label
                    good_label = class1_label
                else:
                    # No pos_label stored, use first as "bad", second as "good"
                    p_bad = p_class0
                    p_good = p_class1
                    bad_label = class0_label
                    good_label = class1_label
                
                # MARGIN-BASED ABSTENTION
                margin = abs(p_bad - 0.5)
                tau = getattr(self, '_abstention_threshold', 0.05)
                
                # Compute p_unknown based on margin
                if margin < tau:
                    p_unknown = max(0.0, min(1.0, 1.0 - (margin / tau)))
                else:
                    p_unknown = 0.0
                
                # Scale probabilities by (1 - p_unknown)
                scale_factor = 1.0 - p_unknown
                p_bad_scaled = p_bad * scale_factor
                p_good_scaled = p_good * scale_factor
                
                # Build probabilities dict
                probs_dict = {
                    bad_label: p_bad_scaled,
                    good_label: p_good_scaled,
                    "<UNKNOWN>": p_unknown
                }
                
                # Determine predicted label
                if margin < tau:
                    predicted_label = "<UNKNOWN>"
                elif p_good_scaled > p_bad_scaled:
                    predicted_label = good_label
                else:
                    predicted_label = bad_label
                
                confidence = probs_dict[predicted_label] if predicted_label != "<UNKNOWN>" else p_unknown
            else:
                # MULTI-CLASS: Original behavior (includes <UNKNOWN> in output)
                probs_dict = {
                    self.target_codec.detokenize(Token(value=i, status=TokenStatus.OK)): prob.item()
                    for i, prob in enumerate(probs)
                }
                
                # Extract prediction (highest probability class, excluding <UNKNOWN>)
                prob_items = [(k, v) for k, v in probs_dict.items() 
                             if k not in ('calibration', '_meta', '<UNKNOWN>')]
                if prob_items:
                    predicted_label, confidence = max(prob_items, key=lambda x: x[1])
                else:
                    predicted_label, confidence = None, None
            
            result = {
                "prediction": predicted_label,
                "confidence": confidence,
                "probabilities": probs_dict,
            }
            
            # Add threshold for binary classification
            if self.optimal_threshold is not None:
                result["threshold"] = float(self.optimal_threshold)
            
            return result
            
        elif isinstance(self.target_codec, AdaptiveScalarEncoder):
            # Regression: extract scalar value
            value = self.target_codec.detokenize(
                Token(value=model_output[0].item(), status=TokenStatus.OK)
            )
            return {
                "prediction": value,
                "confidence": None,  # No confidence for regression
                self.target_col_name: value,  # Legacy field
            }
        else:
            raise ValueError(f"Unknown target codec: {self.target_codec}")

    def _extract_classification_display_metadata(self, epoch_idx: int, current_metrics: dict = None):
        """
        Extract all metadata needed to recreate the classification metrics display.
        
        This includes:
        - Classification metrics with deltas (Δ1, Δ5, Δ10) and trends
        - Confusion matrix data
        - Per-row error tracking
        - Hard row feature analysis
        
        Returns a dict with all display metadata.
        """
        display_metadata = {
            "epoch": epoch_idx,
            "timestamp": time.time(),
        }
        
        # Get metrics from current_metrics or training_info
        if current_metrics is None:
            if hasattr(self, 'training_info') and self.training_info:
                for entry in self.training_info:
                    if entry.get('epoch_idx') == epoch_idx:
                        current_metrics = entry.get('metrics', {})
                        break
        
        if not current_metrics:
            return display_metadata
        
        # Extract classification metrics with deltas
        if hasattr(self, '_metric_tracker') and self._metric_tracker:
            metrics_with_deltas = {}
            metric_keys = ['auc', 'pr_auc', 'accuracy', 'precision', 'recall', 'specificity', 'f1', 'mcc', 'brier_score']
            
            for metric_key in metric_keys:
                if metric_key in current_metrics:
                    value = current_metrics[metric_key]
                    deltas = self._metric_tracker.get_deltas(metric_key, epoch_idx, [1, 5, 10])
                    trend = self._metric_tracker.get_trend_indicator(metric_key, epoch_idx)
                    
                    # Determine quality rating
                    if metric_key == 'brier_score':
                        # Lower is better
                        quality = "EXCELLENT" if value < 0.15 else ("GOOD" if value < 0.20 else "FAIR")
                    else:
                        # Higher is better
                        thresholds = {
                            'auc': (0.70, 0.80),
                            'pr_auc': (0.50, 0.70),
                            'accuracy': (0.70, 0.80),
                            'precision': (0.60, 0.75),
                            'recall': (0.65, 0.80),
                            'specificity': (0.70, 0.80),
                            'f1': (0.60, 0.75),
                            'mcc': (0.40, 0.60),
                        }
                        good_thresh, exc_thresh = thresholds.get(metric_key, (0.5, 0.7))
                        quality = "EXCELLENT" if value > exc_thresh else ("GOOD" if value > good_thresh else "FAIR")
                    
                    metrics_with_deltas[metric_key] = {
                        "value": float(value) if value is not None else None,
                        "delta_1": float(deltas.get("delta_1")) if deltas.get("delta_1") is not None else None,
                        "delta_5": float(deltas.get("delta_5")) if deltas.get("delta_5") is not None else None,
                        "delta_10": float(deltas.get("delta_10")) if deltas.get("delta_10") is not None else None,
                        "trend": trend,
                        "quality": quality,
                    }
            
            display_metadata["classification_metrics"] = metrics_with_deltas
        
        # Extract confusion matrix data
        if all(k in current_metrics for k in ['tp', 'fp', 'tn', 'fn']):
            tp = int(current_metrics['tp'])
            fp = int(current_metrics['fp'])
            tn = int(current_metrics['tn'])
            fn = int(current_metrics['fn'])
            threshold = float(current_metrics.get('optimal_threshold', 0.5))
            
            precision = float(current_metrics.get('precision', 0))
            recall = float(current_metrics.get('recall', 0))
            specificity = float(current_metrics.get('specificity', 0))
            
            ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
            npv = tn / (tn + fn) if (tn + fn) > 0 else 0
            
            display_metadata["confusion_matrix"] = {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "threshold": threshold,
                "precision": precision,
                "recall": recall,
                "specificity": specificity,
                "positive_predictive_value": ppv,
                "negative_predictive_value": npv,
            }
        
        # Extract per-row error tracking
        if hasattr(self, '_row_tracker') and self._row_tracker and epoch_idx in self._row_tracker.epoch_results:
            correct_flags = self._row_tracker.epoch_results[epoch_idx]
            correct_count = sum(correct_flags)
            wrong_count = len(correct_flags) - correct_count
            accuracy_pct = correct_count / len(correct_flags) * 100 if correct_flags else 0
            
            # Get category counts
            category_counts = self._row_tracker.get_category_counts()
            
            # Get hardest rows (in last 10 epochs)
            window = min(10, epoch_idx + 1)
            hardest = self._row_tracker.get_hardest_rows(n=5, window=window)
            hardest_rows = []
            for row_idx, error_rate, gt in hardest:
                epochs_wrong = int(error_rate * window)
                hardest_rows.append({
                    "row_idx": int(row_idx),
                    "error_rate": float(error_rate),
                    "epochs_wrong": epochs_wrong,
                    "window": window,
                    "ground_truth": str(gt) if gt is not None else None,
                })
            
            # Get feature commonality analysis
            feature_analysis = {}
            if hardest and len(hardest) >= 3:
                hard_indices = [row_idx for row_idx, _, _ in hardest]
                commonalities = self._row_tracker.find_feature_commonality(hard_indices)
                
                feature_analysis = {
                    "categorical_patterns": commonalities.get("categorical_patterns", [])[:5],
                    "numeric_patterns": commonalities.get("numeric_patterns", [])[:5],
                }
            
            display_metadata["per_row_tracking"] = {
                "num_rows": self._row_tracker.num_rows,
                "this_epoch": {
                    "correct": correct_count,
                    "wrong": wrong_count,
                    "accuracy_pct": accuracy_pct,
                },
                "cumulative_categories": {
                    "never_wrong": category_counts.get("never_wrong", 0),
                    "rarely_wrong": category_counts.get("rarely_wrong", 0),
                    "sometimes_wrong": category_counts.get("sometimes_wrong", 0),
                    "frequently_wrong": category_counts.get("frequently_wrong", 0),
                    "always_wrong": category_counts.get("always_wrong", 0),
                },
                "hardest_rows": hardest_rows,
                "feature_analysis": feature_analysis,
            }
        
        return display_metadata
    
    def _get_class_imbalance_info(self):
        """Get class imbalance statistics for model card."""
        if not hasattr(self, 'target_col_type') or self.target_col_type != "set":
            return None
        
        info = {}
        
        # Get class distribution if available
        if hasattr(self, 'class_distribution') and self.class_distribution:
            info["class_distribution"] = self.class_distribution.get('total', {})
            info["train_distribution"] = self.class_distribution.get('train', {})
            info["val_distribution"] = self.class_distribution.get('val', {})
            info["total_samples"] = self.class_distribution.get('total_total', 0)
            
            # Compute imbalance ratio
            total_counts = self.class_distribution.get('total', {})
            if total_counts and len(total_counts) >= 2:
                counts = list(total_counts.values())
                majority_count = max(counts)
                minority_count = min(counts)
                if minority_count > 0:
                    info["imbalance_ratio"] = round(majority_count / minority_count, 2)
                    info["majority_class_count"] = majority_count
                    info["minority_class_count"] = minority_count
                    
                    # Find class names
                    for class_name, count in total_counts.items():
                        if count == majority_count:
                            info["majority_class"] = class_name
                        if count == minority_count:
                            info["minority_class"] = class_name
        
        # Add is_binary flag
        if hasattr(self, 'training_metrics') and self.training_metrics:
            info["is_binary"] = self.training_metrics.get('is_binary', False)
        
        return info if info else None
    
    def _get_embedding_space_info(self):
        """Get embedding space details for model card."""
        if not hasattr(self, 'embedding_space') or self.embedding_space is None:
            return None
        
        es = self.embedding_space
        
        # Count parameters and layers
        num_parameters = 0
        num_layers = 0
        if hasattr(es, 'encoder') and es.encoder is not None:
            try:
                num_parameters = sum(p.numel() for p in es.encoder.parameters())
                # Count layers (leaf modules only)
                for name, module in es.encoder.named_modules():
                    if len(list(module.children())) == 0:
                        num_layers += 1
            except:
                pass
        
        # Get row counts
        train_rows = 0
        val_rows = 0
        if hasattr(es, 'train_input_data') and es.train_input_data:
            if hasattr(es.train_input_data, 'df') and es.train_input_data.df is not None:
                train_rows = len(es.train_input_data.df)
        if hasattr(es, 'val_input_data') and es.val_input_data:
            if hasattr(es.val_input_data, 'df') and es.val_input_data.df is not None:
                val_rows = len(es.val_input_data.df)
        
        # Get column count
        num_columns = len(es.col_order) if hasattr(es, 'col_order') else 0
        
        es_info = {
            "num_rows": train_rows + val_rows,
            "num_columns": num_columns,
            "num_parameters": num_parameters,
            "num_layers": num_layers,
            "d_model": getattr(es, 'd_model', None),
        }
        
        # Include parent ES quality checks
        if hasattr(es, 'customer_quality_trackers') and es.customer_quality_trackers:
            es_info["quality_checks"] = es._get_quality_checks_for_model_card() if hasattr(es, '_get_quality_checks_for_model_card') else {}
        
        return es_info
    
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
    
    def _get_feature_inventory(self):
        """Extract feature inventory for model card (excludes target column)."""
        features = []
        
        # Get codecs from embedding space (which excludes the target column)
        if not hasattr(self, 'embedding_space') or self.embedding_space is None:
            return features
        
        es = self.embedding_space
        col_order = es.col_order if hasattr(es, 'col_order') else []
        col_codecs = es.col_codecs if hasattr(es, 'col_codecs') else {}
        col_types = es.col_types if hasattr(es, 'col_types') else {}
        
        for col_name in col_order:
            codec = col_codecs.get(col_name)
            col_type = col_types.get(col_name, "unknown")
            
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
            if hasattr(es, 'encoder') and hasattr(es.encoder, 'column_encoder'):
                encoder = es.encoder.column_encoder.encoders.get(col_name)
                if encoder and hasattr(encoder, '_disabled') and encoder._disabled:
                    is_pruned = True
                    importance_reason = "pruned_during_training"
                    # Get pruning statistics if available
                    if hasattr(es, '_column_loss_tracker') and col_name in es._column_loss_tracker:
                        pruning_info = {
                            "average_loss": float(es._column_loss_tracker[col_name]),
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
    
    def _create_model_card_json(self, best_epoch_idx=None, metadata=None):
        """
        Create comprehensive model card JSON for single predictor.
        
        Similar format to EmbeddingSpace model card but focused on classification/regression metrics.
        """
        
        # Determine best epoch if not provided
        if best_epoch_idx is None:
            # Find best epoch from training_info (lowest validation loss)
            best_epoch_idx = 0
            best_val_loss = float('inf')
            if hasattr(self, 'training_info') and self.training_info:
                for i, entry in enumerate(self.training_info):
                    val_loss = entry.get('validation_loss')
                    if val_loss and val_loss < best_val_loss:
                        best_val_loss = val_loss
                        best_epoch_idx = entry.get('epoch_idx', i)
        
        # Get best epoch metrics
        best_epoch_metrics = {}
        if hasattr(self, 'training_info') and self.training_info:
            for entry in self.training_info:
                if entry.get('epoch_idx') == best_epoch_idx:
                    best_epoch_metrics = entry.get('metrics', {})
                    break
        
        # Get training dataset info - try multiple sources since train_df may be None after unpickling
        train_rows = 0
        val_rows = 0
        
        # First try train_df directly
        if hasattr(self, 'train_df') and self.train_df is not None:
            train_rows = len(self.train_df)
        
        # Then try training_info
        if hasattr(self, 'training_info') and self.training_info:
            first_entry = self.training_info[0] if self.training_info else {}
            if train_rows == 0:
                train_rows = first_entry.get('train_rows', 0)
            val_rows = first_entry.get('val_rows', 0)
        
        # Finally try embedding_space
        if (train_rows == 0 or val_rows == 0) and hasattr(self, 'embedding_space') and self.embedding_space is not None:
            es = self.embedding_space
            if train_rows == 0 and hasattr(es, 'train_input_data') and es.train_input_data is not None:
                if hasattr(es.train_input_data, 'df') and es.train_input_data.df is not None:
                    train_rows = len(es.train_input_data.df)
            if val_rows == 0 and hasattr(es, 'val_input_data') and es.val_input_data is not None:
                if hasattr(es.val_input_data, 'df') and es.val_input_data.df is not None:
                    val_rows = len(es.val_input_data.df)
        
        # Get feature columns (all codecs except target)
        feature_columns = []
        if hasattr(self, 'all_codecs'):
            feature_columns = [col for col in self.all_codecs.keys() if col != self.target_col_name]
        
        # Get optimal threshold info
        optimal_threshold_info = {}
        if hasattr(self, 'optimal_threshold') and self.optimal_threshold is not None:
            optimal_threshold_info = {
                "optimal_threshold": self.optimal_threshold,
                "pos_label": getattr(self, '_pos_label', None),
            }
            if hasattr(self, 'optimal_threshold_history') and self.optimal_threshold_history:
                last_entry = self.optimal_threshold_history[-1]
                optimal_threshold_info.update({
                    "optimal_threshold_f1": last_entry.get('f1_score'),
                    "accuracy_at_optimal_threshold": last_entry.get('accuracy_at_optimal'),
                })
        
        # Get model architecture info
        predictor_param_count = 0
        predictor_layer_count = 0
        predictor_hidden_layers = 0
        predictor_d_hidden = None
        if hasattr(self, 'predictor') and self.predictor is not None:
            predictor_param_count = sum(p.numel() for p in self.predictor.parameters())
            for name, module in self.predictor.named_modules():
                if len(list(module.children())) == 0:
                    predictor_layer_count += 1
        
        # Get predictor config from predictor_base (SimpleMLP)
        if hasattr(self, 'predictor_base') and self.predictor_base is not None:
            if hasattr(self.predictor_base, 'n_hidden_layers'):
                predictor_hidden_layers = self.predictor_base.n_hidden_layers
            if hasattr(self.predictor_base, 'd_hidden'):
                predictor_d_hidden = self.predictor_base.d_hidden
        
        # Get embedding space transformer architecture
        attention_heads = None
        transformer_layers = None
        if hasattr(self, 'embedding_space') and self.embedding_space is not None:
            if hasattr(self.embedding_space, 'encoder_config'):
                enc_config = self.embedding_space.encoder_config
                if hasattr(enc_config, 'joint_encoder_config'):
                    joint_config = enc_config.joint_encoder_config
                    if hasattr(joint_config, 'n_heads'):
                        attention_heads = joint_config.n_heads
                    if hasattr(joint_config, 'n_layers'):
                        transformer_layers = joint_config.n_layers
        
        # Get version info
        version_string = "unknown"
        try:
            from config import config
            version_string = config.get('version', 'unknown')
        except:
            pass
        
        model_card = {
            "model_identification": {
                "session_id": getattr(self, 'session_id', None),
                "job_id": getattr(self, 'job_id', None),
                "name": getattr(self, 'name', None),
                "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
                "target_column_type": self.target_col_type if hasattr(self, 'target_col_type') else None,
                "compute_cluster": socket.gethostname().split('.')[0].upper(),
                "training_date": datetime.now().strftime('%Y-%m-%d'),
                "status": "DONE",
                "model_type": "Single Predictor",
                "framework": f"FeatrixSphere {version_string}"
            },
            
            "training_dataset": {
                "train_rows": train_rows,
                "val_rows": val_rows,
                "total_rows": train_rows + val_rows,
                "total_features": len(feature_columns),
                "feature_names": feature_columns,
                "target_column": self.target_col_name if hasattr(self, 'target_col_name') else None,
            },
            
            "class_imbalance": self._get_class_imbalance_info() if hasattr(self, 'target_col_type') and self.target_col_type == "set" else None,
            
            "training_configuration": {
                "epochs_total": len(self.training_info) if hasattr(self, 'training_info') and self.training_info else 0,
                "best_epoch": best_epoch_idx,
                "d_model": self.d_model if hasattr(self, 'd_model') else None,
                "batch_size": self.training_info[0].get('batch_size') if hasattr(self, 'training_info') and self.training_info else None,
                "learning_rate": self.training_info[0].get('lr') if hasattr(self, 'training_info') and self.training_info else None,
                "optimizer": "Adam",  # Default, could extract from training_info
            },
            
            "training_metrics": {
                "best_epoch": {
                    "epoch": best_epoch_idx,
                    "validation_loss": self.training_info[best_epoch_idx].get('validation_loss') if hasattr(self, 'training_info') and best_epoch_idx < len(self.training_info) else None,
                    "train_loss": self.training_info[best_epoch_idx].get('loss') if hasattr(self, 'training_info') and best_epoch_idx < len(self.training_info) else None,
                },
                "classification_metrics": {
                    "accuracy": best_epoch_metrics.get('accuracy'),
                    "precision": best_epoch_metrics.get('precision'),
                    "recall": best_epoch_metrics.get('recall'),
                    "f1": best_epoch_metrics.get('f1'),
                    "auc": best_epoch_metrics.get('auc'),
                    "is_binary": best_epoch_metrics.get('is_binary', False),
                },
                "optimal_threshold": optimal_threshold_info,
                "argmax_metrics": {
                    "accuracy": best_epoch_metrics.get('argmax_accuracy'),
                    "precision": best_epoch_metrics.get('argmax_precision'),
                    "recall": best_epoch_metrics.get('argmax_recall'),
                    "f1": best_epoch_metrics.get('argmax_f1'),
                } if best_epoch_metrics.get('argmax_accuracy') is not None else None,
            },
            
            "model_architecture": {
                "predictor_parameters": predictor_param_count,
                "predictor_layers": predictor_layer_count,
                "predictor_hidden_layers": predictor_hidden_layers,
                "predictor_d_hidden": predictor_d_hidden,
                "embedding_space_d_model": self.d_model if hasattr(self, 'd_model') else None,
                "transformer_layers": transformer_layers,
                "attention_heads": attention_heads,
                "total_parameters": predictor_param_count + (sum(p.numel() for p in self.embedding_space.encoder.parameters()) if hasattr(self, 'embedding_space') and self.embedding_space and hasattr(self.embedding_space, 'encoder') and self.embedding_space.encoder else 0),
            },
            
            "embedding_space": self._get_embedding_space_info() if hasattr(self, 'embedding_space') and self.embedding_space else None,
            
            "model_quality": {
                "warnings": self.best_epoch_warnings if hasattr(self, 'best_epoch_warnings') else [],
                "training_quality_warning": self.get_training_quality_warning() if hasattr(self, 'get_training_quality_warning') else None,
                "quality_checks": self._get_quality_checks_for_model_card(best_epoch_idx),
            },
            
            "technical_details": {
                "pytorch_version": torch.__version__ if torch else "unknown",
                "device": "GPU" if is_gpu_available() else "CPU",
                "precision": "float32",
                "loss_function": self.target_codec.loss_fn.__class__.__name__ if hasattr(self, 'target_codec') and hasattr(self.target_codec, 'loss_fn') else ("CrossEntropyLoss" if self.target_col_type == "set" else "MSELoss"),
            },
            
            "provenance": {
                "created_at": datetime.now().isoformat(),
                "training_duration_minutes": self.training_info[-1].get('duration_minutes') if hasattr(self, 'training_info') and self.training_info else None,
            }
        }
        
        # Add classification display metadata for best PR-AUC and ROC-AUC epochs
        # Find best PR-AUC and ROC-AUC epochs from training
        best_pr_auc_epoch = None
        best_roc_auc_epoch = None
        
        # Try to get from training_info
        if hasattr(self, 'training_info') and self.training_info:
            best_pr_auc = -1
            best_roc_auc = -1
            for entry in self.training_info:
                metrics = entry.get('metrics', {})
                epoch_idx = entry.get('epoch_idx', 0)
                
                pr_auc = metrics.get('pr_auc', -1)
                roc_auc = metrics.get('auc', -1)
                
                if pr_auc > best_pr_auc:
                    best_pr_auc = pr_auc
                    best_pr_auc_epoch = epoch_idx
                
                if roc_auc > best_roc_auc:
                    best_roc_auc = roc_auc
                    best_roc_auc_epoch = epoch_idx
        
        # Add display metadata for best PR-AUC epoch
        if best_pr_auc_epoch is not None:
            try:
                pr_auc_display_metadata = None
                if hasattr(self, '_epoch_display_metadata') and best_pr_auc_epoch in self._epoch_display_metadata:
                    pr_auc_display_metadata = self._epoch_display_metadata[best_pr_auc_epoch]
                else:
                    # Try to extract it now
                    epoch_metrics = None
                    if hasattr(self, 'training_info') and self.training_info:
                        for entry in self.training_info:
                            if entry.get('epoch_idx') == best_pr_auc_epoch:
                                epoch_metrics = entry.get('metrics', {})
                                break
                    if epoch_metrics:
                        pr_auc_display_metadata = self._extract_classification_display_metadata(best_pr_auc_epoch, epoch_metrics)
                
                if pr_auc_display_metadata:
                    if "best_epochs" not in model_card:
                        model_card["best_epochs"] = {}
                    model_card["best_epochs"]["best_pr_auc"] = {
                        "epoch": best_pr_auc_epoch,
                        "pr_auc": best_pr_auc,
                        "classification_display_metadata": pr_auc_display_metadata,
                    }
            except Exception as e:
                logger.debug(f"Could not add PR-AUC display metadata to model card: {e}")
        
        # Add display metadata for best ROC-AUC epoch
        if best_roc_auc_epoch is not None:
            try:
                roc_auc_display_metadata = None
                if hasattr(self, '_epoch_display_metadata') and best_roc_auc_epoch in self._epoch_display_metadata:
                    roc_auc_display_metadata = self._epoch_display_metadata[best_roc_auc_epoch]
                else:
                    # Try to extract it now
                    epoch_metrics = None
                    if hasattr(self, 'training_info') and self.training_info:
                        for entry in self.training_info:
                            if entry.get('epoch_idx') == best_roc_auc_epoch:
                                epoch_metrics = entry.get('metrics', {})
                                break
                    if epoch_metrics:
                        roc_auc_display_metadata = self._extract_classification_display_metadata(best_roc_auc_epoch, epoch_metrics)
                
                if roc_auc_display_metadata:
                    if "best_epochs" not in model_card:
                        model_card["best_epochs"] = {}
                    model_card["best_epochs"]["best_roc_auc"] = {
                        "epoch": best_roc_auc_epoch,
                        "roc_auc": best_roc_auc,
                        "classification_display_metadata": roc_auc_display_metadata,
                    }
            except Exception as e:
                logger.debug(f"Could not add ROC-AUC display metadata to model card: {e}")
        
        # Add feature inventory if embedding space is available
        if hasattr(self, 'embedding_space') and self.embedding_space is not None:
            try:
                feature_inventory = self._get_feature_inventory()
                if feature_inventory:
                    model_card["feature_inventory"] = feature_inventory
            except Exception as e:
                logger.debug(f"Could not add feature inventory to model card: {e}")
        
        # Add distribution shift analysis results if available
        if hasattr(self, 'distribution_shift_results') and self.distribution_shift_results is not None:
            try:
                shift_results = self.distribution_shift_results
                shift_summary = shift_results.get('summary', {})
                column_reports = shift_results.get('column_reports', {})
                metadata = shift_results.get('metadata', {})
                
                # Extract critical columns with their issues
                critical_columns = []
                for col_name, report in column_reports.items():
                    if report.get('has_critical_issues', False):
                        issues = report.get('issues', [])
                        critical_columns.append({
                            'column_name': col_name,
                            'issues': [issue.get('message', '') for issue in issues if issue.get('severity') == 'error']
                        })
                
                # Extract warning columns
                warning_columns = []
                for col_name, report in column_reports.items():
                    if report.get('has_warnings', False) and not report.get('has_critical_issues', False):
                        warnings = report.get('warnings', [])
                        warning_columns.append({
                            'column_name': col_name,
                            'warnings': warnings[:3]  # Limit to first 3 warnings per column
                        })
                
                # Extract missing columns (in ES but not in SP) - these are more important to track
                missing_columns = []
                for col_name, report in column_reports.items():
                    # Check if this is a missing column (in ES but not in SP)
                    # Missing columns have a warning saying "MISSING from SP data"
                    is_missing = any('MISSING from SP data' in w for w in report.get('warnings', []))
                    if is_missing:
                        missing_columns.append(col_name)
                
                model_card["distribution_shift"] = {
                    "summary": {
                        "total_columns_analyzed": shift_summary.get('total_columns', 0),
                        "ok_columns": shift_summary.get('ok_columns', 0),
                        "warning_columns": shift_summary.get('warning_columns', 0),
                        "critical_columns": shift_summary.get('critical_columns', 0),
                        "new_columns_in_sp": shift_summary.get('new_columns', 0),  # Count only - these are ignored during encoding
                        "missing_columns_from_sp": shift_summary.get('missing_from_sp', 0),
                        "has_critical_issues": shift_summary.get('has_critical_issues', False),
                    },
                    "critical_columns": critical_columns,
                    "warning_columns": warning_columns[:20],  # Limit to top 20 warning columns
                    # Note: new_columns_in_sp are not listed - they're ignored during encoding and are informational only
                    "missing_columns_from_sp": missing_columns[:50],  # Limit to first 50 missing columns
                    "metadata": {
                        "target_column": metadata.get('target_column'),
                        "sp_total_rows": metadata.get('sp_total_rows'),
                        "sp_total_columns": metadata.get('sp_total_columns'),
                        "es_total_columns": metadata.get('es_total_columns'),
                    }
                }
            except Exception as e:
                logger.debug(f"Could not add distribution shift analysis to model card: {e}")
        
        return model_card
