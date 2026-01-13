#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import asyncio
import copy
import glob
import inspect
import json
import logging
import os
import pandas as pd
import pickle
import socket
import sys
import time
import traceback

# CRITICAL: Redirect stderr to stdout IMMEDIATELY so all errors/crashes go to one log
sys.stderr = sys.stdout
print("🔧 STDERR REDIRECTED TO STDOUT - all output in one place!", flush=True)

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from featrix.neural.embedded_space import EmbeddingSpace

from pydantic import BaseModel, ConfigDict

try:
    from featrix.neural import device  # noqa: F401
except ModuleNotFoundError:
    p = Path(__file__).parent
    sys.path.insert(0, str(p))

    from featrix.neural import device  # noqa: F401

from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.input_data_file import FeatrixInputDataFile
from featrix.neural.io_utils import load_embedded_space
from featrix.neural.single_predictor import FeatrixSinglePredictor
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.gpu_utils import (
    get_device,
    is_gpu_available,
    get_gpu_memory_allocated,
    get_gpu_memory_reserved,
    get_max_gpu_memory_allocated,
    get_gpu_device_properties,
)

# Get device once at module level  
device = get_device()

from featrix.neural.utils import ideal_batch_size, ideal_epochs_predictor 
from lib.job_manager import load_job, save_job, update_job_status, JobStatus
from featrix.neural.training_exceptions import TrainingFailureException, EarlyStoppingException
from featrix.neural.exceptions import FeatrixRestartTrainingException

import torch

# Import standardized logging configuration
from featrix.neural.logging_config import configure_logging, current_fold_ctx
configure_logging()

logger = logging.getLogger(__name__)

def _log_gpu_memory(context: str = "", log_level=logging.INFO):
    """Quick GPU memory logging for tracing memory usage."""
    try:
        if not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        reserved = get_gpu_memory_reserved()  # GB (returns 0.0 for MPS/CPU)
        max_allocated = get_max_gpu_memory_allocated()  # GB (returns 0.0 for MPS/CPU)
        logger.log(log_level, f"📊 GPU MEMORY [{context}]: Allocated={allocated:.3f} GB, Reserved={reserved:.3f} GB, Peak={max_allocated:.3f} GB")
    except Exception as e:
        logger.debug(f"Could not log GPU memory: {e}")

# Import proper CV function (feature-flagged)
try:
    from lib.single_predictor_cv import train_with_proper_cv
    PROPER_CV_AVAILABLE = True
except ImportError:
    PROPER_CV_AVAILABLE = False
    logger.warning("⚠️  Proper CV module not available - using sequential CV")


def dump_cuda_memory_usage(context: str = ""):
    """
    Dump detailed CUDA memory usage information when OOM occurs.
    This helps debug what's holding VRAM.
    
    Args:
        context: Optional context string describing where the OOM occurred
    """
    try:
        if not torch.cuda.is_available():
            logger.warning(f"⚠️  CUDA not available - cannot dump memory usage")
            return
        
        logger.error("="*80)
        logger.error(f"🔍 CUDA MEMORY DUMP {f'({context})' if context else ''}")
        logger.error("="*80)
        
        # Get memory stats
        allocated = torch.cuda.memory_allocated() / (1024**3)  # GB
        reserved = torch.cuda.memory_reserved() / (1024**3)  # GB
        max_allocated = torch.cuda.max_memory_allocated() / (1024**3)  # GB
        max_reserved = torch.cuda.max_memory_reserved() / (1024**3)  # GB
        
        logger.error(f"📊 Current Memory Usage:")
        logger.error(f"   Allocated: {allocated:.2f} GB")
        logger.error(f"   Reserved: {reserved:.2f} GB")
        logger.error(f"   Max Allocated (peak): {max_allocated:.2f} GB")
        logger.error(f"   Max Reserved (peak): {max_reserved:.2f} GB")
        
        # Get detailed memory summary
        try:
            memory_summary = torch.cuda.memory_summary(abbreviated=False)
            logger.error(f"\n📋 Detailed Memory Summary:")
            logger.error(memory_summary)
        except Exception as summary_err:
            logger.warning(f"⚠️  Could not get detailed memory summary: {summary_err}")
        
        # Get memory snapshot (shows what tensors are allocated)
        try:
            memory_snapshot = torch.cuda.memory_snapshot()
            if memory_snapshot:
                logger.error(f"\n📸 Memory Snapshot Analysis:")
                logger.error(f"   Total active allocations: {len(memory_snapshot)}")
                
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
                logger.error(f"\n📊 Allocation Size Distribution:")
                for bucket, count in size_buckets.items():
                    if count > 0:
                        size_mb = total_size_by_bucket[bucket] / (1024**2)
                        logger.error(f"   {bucket:12s}: {count:6d} allocations, {size_mb:8.2f} MB total")
                
                # Show top 10 largest allocations
                if allocations_with_size:
                    allocations_with_size.sort(reverse=True, key=lambda x: x[0])
                    logger.error(f"\n🔝 Top 10 Largest Active Allocations:")
                    for i, (active_size, alloc) in enumerate(allocations_with_size[:10], 1):
                        size_mb = active_size / (1024**2)
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        logger.error(f"   {i:2d}. {size_mb:8.2f} MB active / {total_size_mb:8.2f} MB total ({segment_type} pool)")
                        # Show frames if available
                        frames = alloc.get('frames', [])
                        if frames:
                            logger.error(f"       Stack trace:")
                            for frame in frames[:3]:  # First 3 frames
                                filename = frame.get('filename', 'unknown')
                                line = frame.get('line', 'unknown')
                                func = frame.get('function', 'unknown')
                                logger.error(f"         {filename}:{line} in {func}")
                
                # Show first 5 allocations with details (for debugging)
                logger.error(f"\n🔍 Sample Allocations (first 5):")
                for i, alloc in enumerate(memory_snapshot[:5], 1):
                    if isinstance(alloc, dict):
                        total_size_mb = alloc.get('total_size', 0) / (1024**2)
                        active_size_mb = alloc.get('active_size', 0) / (1024**2)
                        segment_type = alloc.get('segment_type', 'unknown')
                        blocks = alloc.get('blocks', [])
                        active_blocks = [b for b in blocks if b.get('state') == 'active_allocated']
                        logger.error(f"   {i}. {active_size_mb:.2f} MB / {total_size_mb:.2f} MB ({segment_type}, {len(active_blocks)} active blocks)")
                
                if len(memory_snapshot) > 5:
                    logger.error(f"   ... and {len(memory_snapshot) - 5} more allocations")
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
                logger.error(f"\n🖥️  nvidia-smi GPU Status:")
                for line in nvidia_smi.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 3:
                            mem_used = parts[0].strip()
                            mem_total = parts[1].strip()
                            gpu_util = parts[2].strip()
                            logger.error(f"   Memory: {mem_used} MB / {mem_total} MB, Utilization: {gpu_util}%")
        except Exception as smi_err:
            logger.warning(f"⚠️  Could not get nvidia-smi output: {smi_err}")
        
        logger.error("="*80)
        
    except ImportError:
        logger.warning(f"⚠️  PyTorch not available - cannot dump CUDA memory usage")
    except Exception as e:
        logger.warning(f"⚠️  Failed to dump CUDA memory usage: {e}")

# Suppress noisy loggers
for noisy in [
    "aiobotocore",
    "asyncio", 
    "botocore",
    "com",
    "fastapi",
    "dotenv",
    "concurrent",
    "aiohttp",
    "filelock",
    "fsspec",
    "httpcore",
    "httpx",
    "requests",
    "s3fs",
    "tornado",
    "twilio",
    "urllib3",
    "com.supertokens",
    "kombu.pidbox"
]:
    logging.getLogger(noisy).setLevel(logging.WARNING)




class SimpleStatus:
    """Simple status object for progress tracking."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class LightSinglePredictorArgs(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    n_epochs: int = 0
    batch_size: int = 0 
    target_column: str  # Required
    target_column_type: str  # Required: "set" or "scalar"
    fine_tune: bool = True  # GRID SEARCH RESULT: +3.18pp AUC improvement vs False
    n_hidden_layers: int = 7  # GRID SEARCH RESULT: Peak AUC 0.7409 with 7 layers (deep network)
    learning_rate: Optional[Union[float, str]] = None  # None or 'auto' = auto-select based on fine_tune (1e-3 standard, 1e-5 fine-tune)
    resume_from_predictor: Optional[str] = None  # Path to existing predictor pickle to resume training from
    input_file: str = "./featrix_data/test.csv"
    job_id: Optional[str] = None
    job_queue: Optional[str] = None
    string_cache: Optional[str] = None
    embedding_space_path: str = "embedded_space.pickle"  # Path to embedding space
    positive_label: Optional[str] = None  # Positive label for binary classification - optional for backward compatibility
    class_imbalance: Optional[dict] = None  # Expected class ratios/counts from real world for sampled data (set codec only)
    use_class_weights: bool = True  # Enable class weighting by default for imbalanced data
    cost_false_positive: Optional[float] = None  # Cost of false positive (only for set columns). If not provided, defaults to 1.0.
    cost_false_negative: Optional[float] = None  # Cost of false negative (only for set columns). If not provided, defaults to negatives/positives ratio.
    loss_type: str = "adaptive"  # Loss function: "adaptive" (MLP learns best blend), "auto", "focal", "cross_entropy", or "prauc" (hard neg mining)
    best_metric_preference: Optional[str] = None  # Which metric to prefer for best model selection: "roc_auc", "pr_auc", or None (auto-detect based on imbalance)
    session_id: Optional[str] = None  # Session ID for metadata tracking
    name: Optional[str] = None  # Name for the single predictor
    webhooks: Optional[Dict[str, str]] = None  # Webhook configuration (webhook_callback_secret, s3_backup_url, model_id_update_url)
    user_metadata: Optional[dict] = None  # User metadata - arbitrary dict for user identification (max 32KB when serialized)




def load_single_predictor(predictor_path: str):
    """
    Load a single predictor from disk.
    
    Supports:
    - .pickle files: Full pickled FeatrixSinglePredictor object
    - .pth files: PyTorch state_dict checkpoint (requires load_state() to restore)
    """
    # Initialize logger at the beginning of the function
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(predictor_path):
        raise FileNotFoundError(f"Single predictor not found at: {predictor_path}")
    
    # Check file extension to determine loading method
    file_ext = os.path.splitext(predictor_path)[1].lower()
    
    if file_ext == '.pth':
        # This is a PyTorch state_dict checkpoint, not a full pickle
        # We need to load it with torch.load and then use load_state() if available
        logger.info(f"📦 Loading PyTorch checkpoint (.pth file): {predictor_path}")
        logger.warning("⚠️  .pth files are state_dict checkpoints, not full predictor objects.")
        logger.warning("   You need to create a new predictor and call load_state() to restore weights.")
        logger.warning("   Or use a .pickle file for a full predictor object.")
        
        try:
            # torch is already imported at top of file - don't import here (causes UnboundLocalError)
            checkpoint = torch.load(predictor_path, weights_only=False, map_location='cpu')
            logger.info(f"✅ Checkpoint loaded. Keys: {list(checkpoint.keys()) if isinstance(checkpoint, dict) else 'Not a dict'}")
            return checkpoint  # Return the state_dict, caller can use load_state() if needed
        except Exception as e:
            logger.error(f"❌ Failed to load .pth checkpoint: {e}")
            raise
    
    # For .pickle files, use pickle loading
    with open(predictor_path, "rb") as f:
        try:
            # Try standard pickle.load first
            fsp = pickle.load(f)
        except (AttributeError, pickle.UnpicklingError) as e:
            error_msg = str(e).lower()
            if "persistent_load" in error_msg or "persistent id" in error_msg:
                # If we get a persistent_load error, try with Unpickler
                f.seek(0)  # Reset file pointer
                unpickler = pickle.Unpickler(f)
                # Provide a handler for unknown persistent IDs
                # Protocol 0 requires ASCII strings, so return empty string instead of None
                def persistent_load(saved_id):
                    persistent_logger = logging.getLogger(__name__)
                    # Convert saved_id to string if it's not already
                    saved_id_str = str(saved_id) if saved_id is not None else "unknown"
                    persistent_logger.warning(f"⚠️  Encountered persistent_id {saved_id_str} in pickle file - returning empty string. This may cause issues if the ID is required.")
                    # Protocol 0 requires ASCII strings, not None
                    return ""
                unpickler.persistent_load = persistent_load
                fsp = unpickler.load()
            else:
                raise
    
    # Ensure predictor is ready for use (reconstruct if needed)
    if hasattr(fsp, '_ensure_predictor_available'):
        try:
            fsp._ensure_predictor_available()
            logger.info("✅ Predictor verified/restored after loading")
        except Exception as e:
            logger.warning(f"⚠️  Could not ensure predictor availability: {e}")
            # Continue anyway - might still work
    
    return fsp


def write_single_predictor(fsp, local_path: str, model_id: str = None):
    """Save the trained single predictor to disk with metadata and model card."""
    assert os.path.exists(local_path)
    pickle_path = local_path + f"/single_predictor.pickle"
    
    # CRITICAL: Validate and fix model integrity before saving
    # This prevents saving corrupted models with empty col_order
    try:
        if hasattr(fsp, 'embedding_space') and fsp.embedding_space:
            es = fsp.embedding_space
            if hasattr(es, 'encoder') and es.encoder:
                encoder = es.encoder
                if hasattr(encoder, 'column_encoder') and encoder.column_encoder:
                    column_encoder = encoder.column_encoder
                    
                    # Check and fix empty col_order before saving
                    if not hasattr(column_encoder, 'col_order') or len(column_encoder.col_order) == 0:
                        logger.warning(f"⚠️  CRITICAL: col_order is empty before saving - attempting recovery")
                        
                        # Try to recover from encoders
                        if hasattr(column_encoder, 'encoders') and column_encoder.encoders and len(column_encoder.encoders) > 0:
                            encoder_keys = list(column_encoder.encoders.keys())
                            column_encoder.col_order = encoder_keys.copy()
                            logger.warning(f"   ✅ Recovered col_order from {len(encoder_keys)} encoders before saving")
                        # Try to recover from codecs
                        elif hasattr(column_encoder, 'col_codecs') and column_encoder.col_codecs:
                            codec_keys = list(column_encoder.col_codecs.keys())
                            column_encoder.col_order = codec_keys.copy()
                            logger.warning(f"   ✅ Recovered col_order from {len(codec_keys)} codecs before saving")
                        # Try to recover from embedding space codecs
                        elif hasattr(es, 'col_codecs') and es.col_codecs:
                            codec_keys = list(es.col_codecs.keys())
                            column_encoder.col_order = codec_keys.copy()
                            if not hasattr(column_encoder, 'col_codecs') or not column_encoder.col_codecs:
                                column_encoder.col_codecs = es.col_codecs
                            logger.warning(f"   ✅ Recovered col_order from embedding_space codecs before saving")
                        else:
                            logger.error(f"   ❌ Cannot recover col_order - model is corrupted and will be saved in broken state")
                            logger.error(f"   This model will fail when loaded. Check training process for issues.")
    except Exception as e:
        logger.error(f"⚠️  Error validating model before save: {e}")
        # Continue anyway - better to save a potentially broken model than crash
    
    with open(pickle_path, "wb") as f:
        pickle.dump(fsp, f)
    
    # Save model architecture metadata separately (backward compatibility)
    metadata_path = local_path + f"/model_metadata.json"
    try:
        # Count layers in the predictor
        layer_count = 0
        param_count = 0
        
        if hasattr(fsp, 'predictor'):
            for name, module in fsp.predictor.named_modules():
                if len(list(module.children())) == 0:  # Leaf modules only
                    layer_count += 1
            
            # Count parameters
            param_count = sum(p.numel() for p in fsp.predictor.parameters())
        
        metadata = {
            "name": fsp.name if hasattr(fsp, 'name') else None,
            "model_id": model_id,  # Store model_id in metadata
            "model_architecture": {
                "layer_count": layer_count,
                "parameter_count": param_count
            },
            "d_model": fsp.d_model if hasattr(fsp, 'd_model') else None,
            "target_column": fsp.target_col_name if hasattr(fsp, 'target_col_name') else None,
            "target_column_type": fsp.target_col_type if hasattr(fsp, 'target_col_type') else None,
        }
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Safe formatting - check type before using format specifier
        param_str = f"{param_count}" if isinstance(param_count, (int, float)) else str(param_count)
        logger.info(f"💾 Model metadata saved: {layer_count} layers, {param_str} parameters")
        if model_id:
            logger.info(f"   Model ID: {model_id}")
    except Exception as e:
        logger.warning(f"Failed to save model metadata: {e}")
    
    # Save comprehensive model card (similar to embedding space)
    model_card_path = local_path + f"/model_card.json"
    try:
        # Find best epoch (lowest validation loss)
        best_epoch_idx = 0
        best_val_loss = float('inf')
        if hasattr(fsp, 'training_info') and fsp.training_info:
            for i, entry in enumerate(fsp.training_info):
                val_loss = entry.get('validation_loss')
                if val_loss and val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_epoch_idx = entry.get('epoch_idx', i)
        
        # Create model card
        model_card = fsp._create_model_card_json(best_epoch_idx=best_epoch_idx)
        
        with open(model_card_path, "w") as f:
            json.dump(model_card, f, indent=2, default=str)
        
        logger.info(f"💾 Model card saved: {model_card_path}")
    except Exception as e:
        logger.warning(f"Failed to save model card: {e}")
        logger.debug(traceback.format_exc())
    
    return pickle_path


def create_predictor_mlp(d_in: int, d_hidden: int = 256, n_hidden_layers: int = 2, dropout: float = 0.3, use_batch_norm: bool = True, residual: bool = True):
    """
    Create a simple MLP predictor architecture.
    
    Args:
        d_in: Input dimension (embedding space dimension)
        d_hidden: Hidden layer dimension (default 256)
        n_hidden_layers: Number of hidden layers (0 = simple Linear layer)
        dropout: Dropout rate (default 0.3)
        use_batch_norm: Whether to use batch normalization (default True)
        residual: Whether to use residual connections (default True)
    """
    from featrix.neural.model_config import SimpleMLPConfig
    
    config = SimpleMLPConfig(
        d_in=d_in,
        d_out=d_hidden,  # This will be overridden by prep_for_training
        d_hidden=d_hidden,
        n_hidden_layers=n_hidden_layers,
        dropout=dropout,
        normalize=False,
        residual=residual,
        use_batch_norm=use_batch_norm,
    )
    
    return SimpleMLP(config)


def apply_predictor_filter(train_df):
    """
    Filter training data to rows where __featrix_train_predictor == True, then drop the column.
    
    Args:
        train_df: The training dataframe
        
    Returns:
        Filtered dataframe with the filter column removed
    """
    PREDICTOR_FILTER_COLUMN = "__featrix_train_predictor"
    
    logger.info("=" * 80)
    logger.info("🔍 SINGLE PREDICTOR: Checking for __featrix_train_predictor column")
    logger.info(f"📊 Initial data shape: {train_df.shape}")
    logger.info(f"📋 Columns present: {list(train_df.columns)}")
    
    if PREDICTOR_FILTER_COLUMN not in train_df.columns:
        logger.info(f"ℹ️  No {PREDICTOR_FILTER_COLUMN} column found - proceeding with all data as-is")
        logger.info("=" * 80)
        return train_df
    
    logger.info(f"✅ Found {PREDICTOR_FILTER_COLUMN} column in data")
    logger.info(f"📊 Column dtype: {train_df[PREDICTOR_FILTER_COLUMN].dtype}")
    logger.info(f"📊 Column value counts:\n{train_df[PREDICTOR_FILTER_COLUMN].value_counts()}")
    logger.info(f"📊 Column null count: {train_df[PREDICTOR_FILTER_COLUMN].isna().sum()}")
    
    # Show target column distribution BEFORE filtering
    if 'label' in train_df.columns or 'target' in train_df.columns:
        target_col = 'label' if 'label' in train_df.columns else 'target'
        logger.info(f"📊 Target '{target_col}' distribution BEFORE filtering:")
        logger.info(f"{train_df[target_col].value_counts()}")
        
        # Show which targets have True vs False predictor flags
        cross_tab = pd.crosstab(
            train_df[target_col].fillna('NULL'), 
            train_df[PREDICTOR_FILTER_COLUMN].fillna('NULL'),
            margins=True
        )
        logger.info(f"📊 Cross-tabulation of target vs {PREDICTOR_FILTER_COLUMN}:")
        logger.info(f"\n{cross_tab}")
    
    # Filter to only TRUE rows
    rows_before = len(train_df)
    logger.info(f"🔍 Filtering to rows where {PREDICTOR_FILTER_COLUMN} == True")
    
    # Convert to boolean mask - handle both int (1/0) and bool (True/False) values
    filter_mask = train_df[PREDICTOR_FILTER_COLUMN].astype(bool)
    train_df = train_df[filter_mask]
    rows_after = len(train_df)
    rows_dropped = rows_before - rows_after
    
    logger.info(f"📊 Rows before filter: {rows_before}")
    logger.info(f"📊 Rows after filter: {rows_after}")
    logger.info(f"📊 Rows dropped: {rows_dropped}")
    logger.info(f"📊 Percentage kept: {(rows_after/rows_before*100):.1f}%")
    
    if rows_after == 0:
        raise ValueError(f"❌ After filtering on {PREDICTOR_FILTER_COLUMN}==True, no rows remain! Cannot train single predictor with zero training examples.")
    
    # Warn if filtering drops > 50% of data
    pct_kept = (rows_after/rows_before*100)
    if pct_kept < 50:
        logger.warning(f"⚠️  WARNING: {PREDICTOR_FILTER_COLUMN} filter dropped {100-pct_kept:.1f}% of data!")
        logger.warning(f"   Training on only {rows_after}/{rows_before} rows")
        logger.warning(f"   This may lead to poor performance - consider:")
        logger.warning(f"   1. Remove {PREDICTOR_FILTER_COLUMN} column to use all data")
        logger.warning(f"   2. Or verify this filtering is intentional")
    elif pct_kept < 80:
        logger.info(f"ℹ️  Note: Filtering kept {pct_kept:.1f}% of data ({rows_after} rows)")
    
    logger.info(f"🗑️  Single Predictor: Now dropping {PREDICTOR_FILTER_COLUMN} column")
    train_df = train_df.drop(columns=[PREDICTOR_FILTER_COLUMN])
    
    logger.info(f"✅ Column dropped successfully")
    logger.info(f"📊 Final data shape: {train_df.shape}")
    logger.info(f"📋 Remaining columns: {list(train_df.columns)}")
    logger.info("=" * 80)
    
    return train_df


def resolve_positive_label(user_label, target_column, train_df):
    """
    Validate and fuzzy-match a user-specified positive label to actual values in the dataframe.
    
    Handles type conversions and common boolean representations (True/False, 1/0, Yes/No, etc.)
    
    Args:
        user_label: The positive label specified by the user (any type)
        target_column: Name of the target column in the dataframe
        train_df: The training dataframe
        
    Returns:
        The matched value from the dataframe (with correct type), or the original user_label if no match found
    """
    if user_label is None:
        return None
    
    logger.info("=" * 80)
    logger.info("🔍 POSITIVE LABEL VALIDATION AND FUZZY MATCHING")
    logger.info(f"🏷️  User-specified positive_label: {user_label!r} (type: {type(user_label).__name__})")
    
    # Get unique values from target column
    unique_values = train_df[target_column].dropna().unique()
    logger.info(f"📊 Unique values in target column '{target_column}': {unique_values}")
    logger.info(f"📊 Value types: {[type(v).__name__ for v in unique_values]}")
    
    # Try direct match first
    for val in unique_values:
        if val == user_label:
            logger.info(f"✅ Direct match found: {val!r}")
            logger.info("=" * 80)
            return val
    
    # No direct match - try fuzzy matching
    logger.info("🔍 No direct match - attempting fuzzy matching...")
    
    def fuzzy_match(user_val, df_val):
        """Try to match user_val to df_val with type conversions."""
        user_str = str(user_val).lower().strip()
        df_str = str(df_val).lower().strip()
        
        if user_str == df_str:
            return True
        
        # Common boolean representations
        true_values = {'true', 't', 'yes', 'y', '1', '1.0'}
        false_values = {'false', 'f', 'no', 'n', '0', '0.0'}
        
        # If user specified a "truthy" value, match it to True/1/1.0/Yes
        if user_str in true_values:
            if df_str in true_values:
                return True
            if df_val is True or df_val == 1 or df_val == 1.0:
                return True
        
        # If user specified a "falsy" value, match it to False/0/0.0/No
        if user_str in false_values:
            if df_str in false_values:
                return True
            if df_val is False or df_val == 0 or df_val == 0.0:
                return True
        
        return False
    
    # Try fuzzy matching against each unique value
    for val in unique_values:
        if fuzzy_match(user_label, val):
            logger.info(f"✅ Fuzzy match found: user '{user_label!r}' → dataframe '{val!r}'")
            logger.info(f"✅ Positive label resolved: '{user_label!r}' → '{val!r}' (type: {type(val).__name__})")
            logger.info("=" * 80)
            return val
    
    # No match found - this is a critical error, abort training
    error_msg = (
        f"❌ CRITICAL ERROR: Could not match positive_label '{user_label!r}' to any value in target column '{target_column}'!\n"
        f"   Available values in target column: {list(unique_values)}\n"
        f"   Value types: {[type(v).__name__ for v in unique_values]}\n"
        f"   \n"
        f"   The positive_label must match one of the actual values in the target column.\n"
        f"   This prevents metrics from being calculated correctly.\n"
        f"   \n"
        f"   Please specify a positive_label that exists in your data, or omit it to auto-detect."
    )
    logger.error(error_msg)
    logger.info("=" * 80)
    raise ValueError(error_msg)


def get_predictor_detailed_info(client, session_id, target_column):
    """
    Get detailed information about a trained predictor from the FeatrixSphere API.
    
    Args:
        client: FeatrixSphere client
        session_id: Session ID
        target_column: Target column of the predictor
        
    Returns:
        dict: Detailed predictor information including model stats
    """
    try:
        # Get session info to find predictor details
        session_info = client._get_json(f"/compute/session/{session_id}")
        
        predictor_info = {}
        
        # Extract embedding space ID
        predictor_info['es_id'] = session_info.get('embedding_space_id') or session_info.get('es_id')
        
        # Find the specific predictor for this target column
        predictors = session_info.get('predictors', {})
        predictor_data = None
        predictor_id = None
        
        for pred_id, pred in predictors.items():
            if isinstance(pred, dict) and pred.get('target_column') == target_column:
                predictor_data = pred
                predictor_id = pred_id
                break
        
        if predictor_data:
            predictor_info['predictor_id'] = predictor_id
            predictor_info['status'] = predictor_data.get('status')
            predictor_info['trained_at'] = predictor_data.get('trained_at')
            
            # Extract model architecture info
            model_info = predictor_data.get('model_info', {})
            predictor_info['parameter_count'] = model_info.get('parameter_count') or model_info.get('num_parameters')
            predictor_info['layer_count'] = model_info.get('layer_count') or model_info.get('num_layers')
            
            # Extract training statistics
            training_stats = predictor_data.get('training_stats', {}) or predictor_data.get('stats', {})
            predictor_info['best_epoch'] = training_stats.get('best_epoch')
            predictor_info['best_accuracy'] = training_stats.get('best_accuracy')
            predictor_info['best_loss'] = training_stats.get('best_loss')
            predictor_info['val_loss'] = training_stats.get('val_loss') or training_stats.get('validation_loss')
            predictor_info['val_accuracy'] = training_stats.get('val_accuracy') or training_stats.get('validation_accuracy')
            predictor_info['final_epoch'] = training_stats.get('final_epoch') or training_stats.get('epochs_trained')
            predictor_info['training_time_seconds'] = training_stats.get('training_time') or training_stats.get('elapsed_seconds')
        
        # Get column types from the session
        column_info = session_info.get('columns', {}) or session_info.get('column_types', {})
        if column_info:
            predictor_info['column_types'] = column_info
        
        # Get encoding information
        encoding_info = session_info.get('encoding', {}) or session_info.get('encodings', {})
        if encoding_info:
            predictor_info['column_encodings'] = encoding_info
            
        # Get training host/cluster info
        predictor_info['training_cluster'] = session_info.get('cluster') or session_info.get('compute_cluster')
        predictor_info['training_host'] = session_info.get('host') or session_info.get('compute_host')
        
        return predictor_info
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to get detailed predictor info: {e}")
        return {}


def save_predictor_metadata(
    session_id,
    target_column,
    target_column_type="set",
    epochs=None,  # None = use from args, 0 = auto-calculate
    training_response=None,
    csv_file=None,
    client=None,
    training_start_time=None,
    fsp=None
):
    """
    Save comprehensive predictor training metadata to a JSON file for future reference.
    
    This captures all critical information about the trained model including:
    - Model architecture (parameter count, layer count)
    - Training statistics (best stats, val loss, etc.)
    - Column types and encodings
    - Training environment details
    
    Args:
        session_id: FeatrixSphere session ID
        target_column: Target column being predicted
        target_column_type: Type of target ("set" or "numeric")
        epochs: Number of training epochs requested
        training_response: Initial training API response
        csv_file: Source CSV file path
        client: FeatrixSphere client (for fetching detailed stats)
        training_start_time: When training started (timestamp)
        fsp: FeatrixSinglePredictor instance (for local model info)
        
    Returns:
        str: Path to saved metadata file
    """
    try:
        # Basic metadata
        metadata = {
            "target_column": target_column,
            "session_id": session_id,
            "target_column_type": target_column_type,
            "epochs_requested": epochs,
            "started_at": training_start_time or datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "training_response": training_response,
            "source_csv": csv_file,
            "status": "completed",
            "metadata_version": "2.0"
        }
        
        # Add training host information
        try:
            metadata['training_client_host'] = socket.gethostname()
            metadata['training_client_fqdn'] = socket.getfqdn()
        except Exception:
            pass
        
        # Calculate training time if we have start time
        if training_start_time:
            try:
                start_dt = datetime.fromisoformat(training_start_time) if isinstance(training_start_time, str) else training_start_time
                end_dt = datetime.now()
                metadata['training_duration_seconds'] = (end_dt - start_dt).total_seconds()
            except Exception:
                pass
        
        # Get local model info from FeatrixSinglePredictor if available
        if fsp:
            try:
                # Add name if available
                if hasattr(fsp, 'name') and fsp.name:
                    metadata['name'] = fsp.name
                
                # Count layers and parameters
                layer_count = 0
                param_count = 0
                
                if hasattr(fsp, 'predictor'):
                    for name, module in fsp.predictor.named_modules():
                        if len(list(module.children())) == 0:  # Leaf modules only
                            layer_count += 1
                    
                    # Count parameters
                    param_count = sum(p.numel() for p in fsp.predictor.parameters())
                
                metadata['parameter_count'] = param_count
                metadata['layer_count'] = layer_count
                metadata['d_model'] = fsp.d_model if hasattr(fsp, 'd_model') else None
                
                # Get training metrics if available
                if hasattr(fsp, 'training_info') and fsp.training_info:
                    metadata['training_info'] = fsp.training_info
                if hasattr(fsp, 'training_metrics') and fsp.training_metrics:
                    metadata['final_metrics'] = fsp.training_metrics
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not extract local model info: {e}")
        
        # Get detailed predictor information from API if client provided
        if client:
            try:
                detailed_info = get_predictor_detailed_info(client, session_id, target_column)
                # Merge API info (don't override local info if it exists)
                for key, value in detailed_info.items():
                    if key not in metadata or metadata[key] is None:
                        metadata[key] = value
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch detailed predictor info from API: {e}")
        
        # Save to local metadata directory
        metadata_dir = Path("predictor_metadata")
        metadata_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_file = metadata_dir / f"{session_id}_{target_column}_{timestamp}.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"📝 Metadata saved to: {metadata_file}")
        logger.info(f"   - Target column: {target_column}")
        logger.info(f"   - Session ID: {session_id}")
        if 'es_id' in metadata:
            logger.info(f"   - Embedding space ID: {metadata['es_id']}")
        if 'parameter_count' in metadata:
            param_count = metadata['parameter_count']
            param_str = f"{param_count}" if isinstance(param_count, (int, float)) else str(param_count)
            logger.info(f"   - Parameter count: {param_str}")
        if 'layer_count' in metadata:
            logger.info(f"   - Layer count: {metadata['layer_count']}")
        if 'val_loss' in metadata:
            val_loss = metadata['val_loss']
            val_loss_str = f"{val_loss}" if isinstance(val_loss, (int, float)) else str(val_loss)
            logger.info(f"   - Validation loss: {val_loss_str}")
        if 'training_duration_seconds' in metadata:
            duration = metadata['training_duration_seconds']
            duration_str = f"{duration}" if isinstance(duration, (int, float)) else str(duration)
            logger.info(f"   - Training time: {duration_str}s")
        
        return str(metadata_file)
    except Exception as e:
        logger.error(f"⚠️ Failed to save metadata: {e}")
        traceback.print_exc()
        return None


def get_sp_config_from_monitor(train_df, es, session_id: str, mark_in_progress: bool = True) -> Optional[Dict[str, Any]]:
    """
    Query monitor.featrix.com for the next hyperparameter config to try.
    
    Args:
        train_df: Training dataframe (used to generate dataset hash)
        es: Embedding space (provides d_model)
        session_id: Training session ID
        mark_in_progress: Whether to mark the config as in-progress
    
    Returns:
        Config dict with hyperparameters, or None if no configs available or monitor unavailable
    """
    try:
        from featrix_monitor import create_client, generate_dataset_hash
        
        # Generate dataset hash
        dataset_hash = generate_dataset_hash(train_df)
        logger.info(f"📊 Dataset hash: {dataset_hash}")
        
        # Create monitor client
        client = create_client(
            base_url="https://monitor.featrix.com",
            cache_dir="/sphere/app/monitor"
        )
        
        # Get next config to try
        result = client.get_next_config_to_try(
            dataset_hash=dataset_hash,
            min_epochs=25,  # Consider configs trained for 25+ epochs as "completed"
            mark_in_progress=mark_in_progress,
            session_id=session_id if mark_in_progress else None
        )
        
        if result and result.get('next_config'):
            config = result['next_config']
            logger.info(f"✅ Got config from monitor for dataset {dataset_hash}")
            logger.info(f"   Config: {config}")
            return config
        else:
            logger.info(f"ℹ️  No pending configs available from monitor for dataset {dataset_hash}")
            logger.info(f"   All configs have been trained or are in progress.")
            return None
            
    except ImportError:
        logger.warning("⚠️  featrix-monitor not installed, skipping monitor query")
        return None
    except Exception as e:
        logger.warning(f"⚠️  Failed to query monitor for config: {e}")
        logger.debug(f"   Full error:", exc_info=True)
        return None


def propose_sp_configs_to_monitor(train_df, es, search_space: str = "default") -> bool:
    """
    Propose all hyperparameter configs from grid generation to monitor.featrix.com.
    
    This should be called once per dataset to populate the search space.
    
    Args:
        train_df: Training dataframe
        es: Embedding space
        search_space: "narrow", "default", or "wide"
    
    Returns:
        True if configs were proposed successfully, False otherwise
    """
    try:
        from featrix_monitor import create_client, generate_dataset_hash
        from featrix.neural.utils import generate_sp_hyperparameter_grid, format_sp_config_summary
        
        # Generate dataset hash
        dataset_hash = generate_dataset_hash(train_df)
        
        # Generate all configs to try
        configs = generate_sp_hyperparameter_grid(
            d_model=es.d_model,
            n_rows=len(train_df),
            search_space=search_space
        )
        
        logger.info(f"📊 Proposing {len(configs)} configs to monitor for dataset {dataset_hash}")
        logger.info(f"   Search space: {search_space}")
        logger.info(f"   First 3 configs:")
        for i, cfg in enumerate(configs[:3]):
            logger.info(f"     {i+1}. {format_sp_config_summary(cfg)}")
        
        # Create monitor client
        client = create_client(
            base_url="https://monitor.featrix.com",
            cache_dir="/sphere/app/monitor"
        )
        
        # Propose configs
        result = client.propose_dataset_configs(
            dataset_hash=dataset_hash,
            configs=configs
        )
        
        if result:
            logger.info(f"✅ Proposed {result.get('total_proposed', len(configs))} configs to monitor")
            return True
        else:
            logger.warning(f"⚠️  Failed to propose configs to monitor")
            return False
            
    except ImportError:
        logger.warning("⚠️  featrix-monitor not installed, skipping config proposal")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Failed to propose configs to monitor: {e}")
        logger.debug(f"   Full error:", exc_info=True)
        return False


def train_single_predictor(args: LightSinglePredictorArgs):
    # Print version info at start of training
    try:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add src to path
        from version import print_version_banner, get_version
        print_version_banner("Featrix Sphere Single Predictor Training")
        
        # Explicitly log version to syslog
        version_info = get_version()
        logger.info(f"📦 Single Predictor Training Version: {version_info.semantic_version} (git: {version_info.git_hash[:8] if version_info.git_hash else 'unknown'})")
        logger.info(f"📅 Version Date: {version_info.git_date or 'unknown'}")
    except Exception as e:
        logger.warning(f"⚠️ Could not load version info: {e}")
        print(f"⚠️ Could not load version info: {e}")
    
    # Capture training start time for metadata
    training_start_time = datetime.now()
    
    print(f"🎯 Training single predictor: {args.target_column} ({args.target_column_type})")
    print(f"📊 Args: {args.model_dump_json(indent=2)}")
    
    # Log training start event
    session_id = args.session_id
    if session_id:
        try:
            from event_log import log_training_event
            log_training_event(
                session_id=session_id,
                event_name="training_started",
                predictor_id=args.job_id,
                additional_info={
                    "target_column": args.target_column,
                    "target_column_type": args.target_column_type,
                    "epochs": args.n_epochs,
                    "batch_size": args.batch_size
                }
            )
        except Exception as e:
            logger.debug(f"Failed to log training start event: {e}")

    # DON'T CLEAR HANDLERS - it breaks all logging!
    # logging.getLogger().handlers.clear()
    
    print("@@@@ Starting Single Predictor Training! @@@@")
    
    # Validate required arguments
    if not args.target_column:
        raise ValueError("target_column is required")
    if args.target_column_type not in ["set", "scalar"]:
        raise ValueError("target_column_type must be 'set' or 'scalar'")
    
    logger.info("="*100)
    logger.info("🚀🚀🚀 train_single_predictor() FUNCTION ENTRY POINT")
    logger.info(f"🚀 Args: target_column={args.target_column}, target_column_type={args.target_column_type}")
    logger.info(f"🚀 This file: {__file__}")
    logger.info("="*100)
    
    # Post to Slack that Single Predictor training is starting
    try:
        from pathlib import Path as PathLib
        sys.path.insert(0, str(PathLib(__file__).parent.parent))
        from slack import send_slack_message
        
        slack_msg = f"🎯 **Single Predictor Training Started**\n"
        slack_msg += f"Target Column: {args.target_column}\n"
        slack_msg += f"Target Type: {args.target_column_type}\n"
        slack_msg += f"Session ID: {args.session_id}\n"
        slack_msg += f"Job ID: {args.job_id}\n"
        slack_msg += f"Epochs: {getattr(args, 'n_epochs', getattr(args, 'epochs', 0))}\n"
        slack_msg += f"Batch Size: {getattr(args, 'batch_size', 0)}\n"
        slack_msg += f"Learning Rate: {getattr(args, 'learning_rate', 'N/A')}\n"
        slack_msg += f"Started: {training_start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        send_slack_message(slack_msg, throttle=False)  # Critical - don't throttle
        logger.info("✅ Slack notification sent for Single Predictor training start")
    except Exception as slack_error:
        logger.warning(f"Failed to send Slack notification: {slack_error}", exc_info=True)
    
    logger.info(f"Training single predictor for target column: {args.target_column} (type: {args.target_column_type})")
    sys.stdout.flush()  # Force flush before GPU check
    sys.stderr.flush()
    
    # Enable GPU training for single predictors
    logger.info("🔍 Checking GPU availability...")
    sys.stdout.flush()
    try:
        use_gpu = is_gpu_available()
        logger.info(f"✅ GPU check complete: use_gpu={use_gpu}")
        sys.stdout.flush()
    except Exception as gpu_check_error:
        logger.error(f"❌ GPU availability check FAILED: {gpu_check_error}", exc_info=True)
        sys.stdout.flush()
        sys.stderr.flush()
        raise
    
    if use_gpu:
        logger.info("🔍 Getting GPU device properties...")
        sys.stdout.flush()
        try:
            props = get_gpu_device_properties(0)
            gpu_memory_gb = (props.total_memory / (1024**3)) if props else 0.0
            logger.info(f"🎮 GPU available: {gpu_memory_gb:.1f} GB - will use GPU for training")
            sys.stdout.flush()
        except Exception as gpu_props_error:
            logger.error(f"❌ GPU properties check FAILED: {gpu_props_error}", exc_info=True)
            sys.stdout.flush()
            sys.stderr.flush()
            raise
    else:
        logger.info(f"🖥️  No GPU available - will use CPU for training")
        sys.stdout.flush()
    
    # Load the pre-trained embedding space
    logger.info(f"🔍 Step 1: Checking if embedding space exists at {args.embedding_space_path}")
    if not os.path.exists(args.embedding_space_path):
        raise FileNotFoundError(f"{args.embedding_space_path} not found. Train an embedding space first.")
    
    # CRITICAL: Check for newer ES checkpoints on backplane if ES training is in-progress
    # This ensures we use the latest embeddings even if ES is still training
    original_es_path = args.embedding_space_path
    es_mtime = os.path.getmtime(args.embedding_space_path)
    
    # Load session early so it's available for foundation_info.json
    session = None
    try:
        from lib.session_manager import load_session
        session = load_session(args.session_id)
    except Exception as session_load_err:
        logger.warning(f"⚠️  Could not load session: {session_load_err}")
    
    try:
        # Check if there's a train_es job running or completed more recently
        from lib.job_manager import get_session_jobs
        
        if not session:
            from lib.session_manager import load_session
            session = load_session(args.session_id)
        session_jobs = get_session_jobs(args.session_id)
        
        # Find train_es job (session_jobs is a list of job dicts)
        train_es_job = None
        for job in session_jobs:
            if job.get('job_type') == 'train_es':
                job_id = job.get('job_id')
                train_es_job = (job_id, job)
                break
        
        if train_es_job:
            job_id, job = train_es_job
            job_status = job.get('status', 'unknown')
            
            logger.info(f"🔍 Found train_es job: {job_id} (status: {job_status})")
            
            # If ES is running or recently completed, check for newer checkpoints on backplane
            if job_status in ['running', 'done']:
                from lib.job_manager import get_job_output_path
                from pathlib import Path
                import subprocess
                
                # Get ES job output directory
                train_es_dir = get_job_output_path(job_id, args.session_id, 'train_es')
                
                logger.info(f"🔍 Checking for newer ES checkpoints in: {train_es_dir}")
                
                # Look for BEST checkpoint first
                best_checkpoint = train_es_dir / "checkpoint_BEST_MODEL.pth"
                if best_checkpoint.exists():
                    best_mtime = best_checkpoint.stat().st_mtime
                    if best_mtime > es_mtime:
                        logger.info(f"✅ Found newer BEST checkpoint: {best_checkpoint}")
                        logger.info(f"   Current ES: {es_mtime}, Newer checkpoint: {best_mtime} (Δ={(best_mtime-es_mtime)/60:.1f} min newer)")
                        args.embedding_space_path = str(best_checkpoint)
                    else:
                        logger.info(f"   BEST checkpoint exists but not newer than current ES")
                else:
                    # No BEST yet - look for latest inference checkpoint (in-progress)
                    inference_checkpoints = sorted(train_es_dir.glob("checkpoint_inference_e-*.pt"))
                    if inference_checkpoints:
                        latest_checkpoint = inference_checkpoints[-1]
                        latest_mtime = latest_checkpoint.stat().st_mtime
                        if latest_mtime > es_mtime:
                            logger.info(f"✅ Found newer in-progress checkpoint: {latest_checkpoint}")
                            logger.info(f"   Current ES: {es_mtime}, Newer checkpoint: {latest_mtime} (Δ={(latest_mtime-es_mtime)/60:.1f} min newer)")
                            logger.info(f"   Using latest of {len(inference_checkpoints)} inference checkpoints")
                            args.embedding_space_path = str(latest_checkpoint)
                        else:
                            logger.info(f"   In-progress checkpoints exist but not newer than current ES")
                    else:
                        logger.info(f"   No newer checkpoints found")
                
                # If path changed, log the update
                if args.embedding_space_path != original_es_path:
                    logger.info(f"🔄 UPDATED ES PATH: Using newer checkpoint from backplane")
                    logger.info(f"   Old: {original_es_path}")
                    logger.info(f"   New: {args.embedding_space_path}")
    
    except Exception as check_err:
        logger.warning(f"⚠️  Could not check for newer ES checkpoints: {check_err}")
        logger.warning(f"   Continuing with original path: {original_es_path}")
        # Continue with original path on error
    
    logger.info(f"🔍 Step 2: Loading pre-trained embedding space from {args.embedding_space_path}...")
    _log_gpu_memory("BEFORE LOAD_EMBEDDED_SPACE")
    # Load embedding space - will use GPU if available
    # skip_datasets=True because SP training creates its own datasets from args.input_file
    logger.info(f"🔧 Loading embedding space (skip_datasets=True for SP training)")
    es = load_embedded_space(args.embedding_space_path, skip_datasets=True)
    
    # Create foundation_info.json if this is a foundation model session
    try:
        if session and session.get("foundation_model_id"):
            foundation_model_id = session.get("foundation_model_id")
            foundation_checkpoint = session.get("foundation_checkpoint")
            foundation_checkpoint_type = session.get("foundation_checkpoint_type")
            embedding_space_path = session.get("embedding_space")
            embedding_space_source = session.get("embedding_space_source")
            
            # Determine output directory for foundation_info.json
            output_dir = Path(args.output_dir) if args.output_dir else Path(os.getcwd())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract es_id from embedding_space path or use foundation_model_id
            es_id = foundation_model_id  # Default to foundation_model_id
            if embedding_space_path:
                es_path_stem = Path(embedding_space_path).stem
                # Try to extract session ID from path (common patterns)
                if es_path_stem:
                    es_id = es_path_stem
            
            # Get queued_at from job if available
            queued_at = None
            if args.job_id:
                try:
                    from lib.job_manager import load_job
                    job_data = load_job(args.job_id)
                    if job_data and job_data.get("created_at"):
                        queued_at = job_data.get("created_at")
                except Exception:
                    pass
            
            # Create foundation_info.json
            foundation_info = {
                "session_id": args.session_id,
                "foundation_model_id": foundation_model_id,
                "es_id": es_id,
                "embedding_space_path": embedding_space_path,
                "embedding_space_source": embedding_space_source,
                "foundation_checkpoint": foundation_checkpoint,
                "foundation_checkpoint_type": foundation_checkpoint_type,
                "target_column": args.target_column,
                "target_column_type": args.target_column_type,
                "created_at": datetime.now().isoformat(),
                "queued_at": queued_at,
                "job_id": args.job_id,
                "name": session.get("name"),
                "session_type": session.get("session_type"),
            }
            
            foundation_info_path = output_dir / "foundation_info.json"
            with open(foundation_info_path, 'w') as f:
                json.dump(foundation_info, f, indent=2, default=str)
            
            logger.info(f"📝 Created foundation_info.json: {foundation_info_path}")
            logger.info(f"   Foundation Model ID: {foundation_model_id}")
            logger.info(f"   ES ID: {es_id}")
            logger.info(f"   Session ID: {args.session_id}")
            if queued_at:
                logger.info(f"   Queued at: {queued_at}")
    except Exception as e:
        logger.warning(f"⚠️  Could not create foundation_info.json: {e}")
        # Don't fail training if this fails
    
    # CRITICAL: Clear force_cpu env var after loading - io_utils sets it during unpickling to prevent OOM
    # but we want to use GPU for training! Must clear it before codecs are used.
    if 'FEATRIX_FORCE_CPU_SINGLE_PREDICTOR' in os.environ:
        logger.info(f"🔧 Clearing FEATRIX_FORCE_CPU_SINGLE_PREDICTOR env var (was set during unpickling)")
        os.environ.pop('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR', None)
        os.environ.pop('FEATRIX_FORCE_CPU_SENTENCE_MODEL', None)
    
    _log_gpu_memory("AFTER LOAD_EMBEDDED_SPACE")
    logger.info(f"🔍 Step 2 DONE: Embedding space loaded, type={type(es)}")
    
    # Validate that es is an EmbeddingSpace object
    from featrix.neural.embedded_space import EmbeddingSpace
    if not isinstance(es, EmbeddingSpace):
        raise TypeError(f"Expected EmbeddingSpace object, got {type(es)}. The file may be a checkpoint dict, not a full embedding space.")
    
    # CRITICAL: Validate encoder exists and is not None
    if not hasattr(es, 'encoder') or es.encoder is None:
        raise RuntimeError(
            f"EmbeddingSpace loaded but encoder is None! This usually means __setstate__ failed to load the encoder.\n"
            f"Check logs for 'Failed to recreate encoder from state_dict' errors.\n"
            f"Common causes:\n"
            f"  - Size mismatches (vocabulary/column count differences between checkpoint and current data)\n"
            f"  - Missing encoder_config or col_codecs in pickle\n"
            f"  - Corrupted checkpoint file\n"
            f"Embedding space path: {args.embedding_space_path}"
        )
    
    # Move encoder to GPU if available
    _log_gpu_memory("BEFORE CHECKING ENCODER DEVICE")
    if hasattr(es, 'encoder') and es.encoder is not None:
        if list(es.encoder.parameters()):
            encoder_device = next(es.encoder.parameters()).device
            if use_gpu and encoder_device.type != 'cuda':
                logger.info(f"🔄 Moving encoder to GPU for faster training...")
                es.encoder = es.encoder.to(get_device())
                torch.cuda.empty_cache()
                _log_gpu_memory("AFTER MOVING ENCODER TO GPU")
            logger.info(f"✅ Encoder device: {next(es.encoder.parameters()).device}")
        
        # Move codecs to GPU if available
        if use_gpu and hasattr(es, 'col_codecs') and es.col_codecs:
            codecs_moved = 0
            codecs_failed = 0
            for col_name, codec in es.col_codecs.items():
                try:
                    if hasattr(codec, 'cuda'):
                        codec.to(get_device())
                        codecs_moved += 1
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not move {col_name} codec to GPU: {e}")
                    codecs_failed += 1
            logger.info(f"   ✅ Moved {codecs_moved}/{len(es.col_codecs)} codecs to GPU")
            if codecs_failed > 0:
                logger.warning(f"   ⚠️  Failed to move {codecs_failed} codecs to GPU")
            if codecs_moved > 0:
                torch.cuda.empty_cache()
        
        # Clear training history/metadata from GPU memory (not needed for inference/training)
        # These are just metadata dicts, but clearing them ensures no accidental GPU tensors
        if hasattr(es, 'training_info') and es.training_info:
            # training_info is just metadata, but check for any GPU tensors
            try:
                # Remove any large lists that might have been accidentally stored
                for key in ['val_losses', 'train_losses', 'gradient_norms', 'learning_rates']:
                    if key in es.training_info:
                        # These are just lists of floats, not GPU tensors, but clear if large
                        if isinstance(es.training_info[key], list) and len(es.training_info[key]) > 1000:
                            logger.debug(f"   Trimming large {key} list ({len(es.training_info[key])} entries)")
                            es.training_info[key] = es.training_info[key][-100:]  # Keep last 100
            except Exception as e:
                logger.debug(f"   Could not trim training_info: {e}")
        
        # Clear training timeline if it's large (just metadata, not needed for training)
        if hasattr(es, '_training_timeline') and isinstance(es._training_timeline, list):
            if len(es._training_timeline) > 1000:
                logger.debug(f"   Trimming large training timeline ({len(es._training_timeline)} entries)")
                es._training_timeline = es._training_timeline[-100:]  # Keep last 100 entries
    
    # CRITICAL: Clear train_input_data and val_input_data - we don't need the ES's original training data
    # We only need the encoder and codecs to encode the NEW training data for the predictor
    if hasattr(es, 'train_input_data') and es.train_input_data is not None:
        logger.info(f"🗑️  Clearing ES train_input_data (not needed for predictor training - only need encoder/codecs)")
        # Check size before clearing
        try:
            if hasattr(es.train_input_data, 'df'):
                df_size = len(es.train_input_data.df) if hasattr(es.train_input_data.df, '__len__') else 'unknown'
                logger.info(f"   train_input_data had {df_size} rows")
        except Exception:
            pass
        es.train_input_data = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    if hasattr(es, 'val_input_data') and es.val_input_data is not None:
        logger.info(f"🗑️  Clearing ES val_input_data (not needed for predictor training - only need encoder/codecs)")
        # Check size before clearing
        try:
            if hasattr(es.val_input_data, 'df'):
                df_size = len(es.val_input_data.df) if hasattr(es.val_input_data.df, '__len__') else 'unknown'
                logger.info(f"   val_input_data had {df_size} rows")
        except Exception:
            pass
        es.val_input_data = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    # Also clear train_dataset and val_dataset if they exist
    if hasattr(es, 'train_dataset') and es.train_dataset is not None:
        logger.info(f"🗑️  Clearing ES train_dataset (not needed for predictor training)")
        es.train_dataset = None
    
    if hasattr(es, 'val_dataset') and es.val_dataset is not None:
        logger.info(f"🗑️  Clearing ES val_dataset (not needed for predictor training)")
        es.val_dataset = None
    
    _log_gpu_memory("AFTER CLEARING ES TRAINING DATA")
    logger.info(f"✅ Cleared ES training data - only encoder and codecs remain (needed for encoding)")
    
    # FIX: Update embedding space's output_dir to current working directory
    # The ES was trained in a different job directory, so its output_dir points to the wrong place
    current_dir = os.getcwd()
    if hasattr(es, 'output_dir'):
        old_output_dir = es.output_dir
        es.output_dir = current_dir
        logger.info(f"📂 Updated ES output_dir: {old_output_dir} → {current_dir}")
    else:
        es.output_dir = current_dir
        logger.info(f"📂 Set ES output_dir to: {current_dir}")
    
    # Load the training data
    logger.info(f"🔍 Step 3: Loading data from {args.input_file}...")
    input_data_file = FeatrixInputDataFile(args.input_file)
    train_df = input_data_file.df
    logger.info(f"🔍 Step 3 DONE: Data file loaded: {len(train_df)} rows × {len(train_df.columns)} columns")
    
    # Log columns found immediately after loading for debugging
    logger.info(f"📋 Columns found after CSV reading ({len(train_df.columns)} total): {list(train_df.columns)[:50]}{'...' if len(train_df.columns) > 50 else ''}")
    if len(train_df.columns) > 50:
        logger.info(f"   ... and {len(train_df.columns) - 50} more columns")
    
    # Check column compatibility between embedding space and training data
    # NOTE: For fine-tuning, columns don't need to match exactly - missing columns will use NULL/NOT_PRESENT tokens
    logger.info(f"🔍 Checking column compatibility between embedding space and training data...")
    
    # Extract columns from embedding space - try multiple sources in order of reliability
    es_columns = set()
    if hasattr(es, 'col_order') and es.col_order:
        es_columns = set(es.col_order)
        logger.debug(f"   Extracted {len(es_columns)} columns from es.col_order")
    elif hasattr(es, 'col_codecs') and es.col_codecs:
        es_columns = set(es.col_codecs.keys())
        logger.debug(f"   Extracted {len(es_columns)} columns from es.col_codecs.keys()")
    elif hasattr(es, 'encoder') and hasattr(es.encoder, 'column_encoder') and hasattr(es.encoder.column_encoder, 'col_order'):
        es_columns = set(es.encoder.column_encoder.col_order)
        logger.debug(f"   Extracted {len(es_columns)} columns from es.encoder.column_encoder.col_order")
    elif hasattr(es, 'encoder') and hasattr(es.encoder, 'column_encoder') and hasattr(es.encoder.column_encoder, 'col_codecs'):
        es_columns = set(es.encoder.column_encoder.col_codecs.keys())
        logger.debug(f"   Extracted {len(es_columns)} columns from es.encoder.column_encoder.col_codecs.keys()")
    elif hasattr(es, 'get_column_names'):
        try:
            es_columns = set(es.get_column_names())
            logger.debug(f"   Extracted {len(es_columns)} columns from es.get_column_names()")
        except Exception:
            pass
    
    if not es_columns:
        logger.error(f"❌ CRITICAL: Could not extract columns from embedding space!")
        logger.error(f"   es has col_order: {hasattr(es, 'col_order')}")
        logger.error(f"   es has col_codecs: {hasattr(es, 'col_codecs')}")
        if hasattr(es, 'col_codecs'):
            logger.error(f"   col_codecs length: {len(es.col_codecs) if es.col_codecs else 0}")
        logger.error(f"   es has encoder: {hasattr(es, 'encoder')}")
        if hasattr(es, 'encoder') and es.encoder:
            logger.error(f"   encoder has column_encoder: {hasattr(es.encoder, 'column_encoder')}")
        raise ValueError("Cannot extract columns from embedding space - embedding space may be corrupted or incomplete")
    df_columns = set(train_df.columns)
    
    missing_in_df = es_columns - df_columns
    extra_in_df = df_columns - es_columns
    
    if missing_in_df:
        logger.warning(f"⚠️  Fine-tuning mode: {len(missing_in_df)} ES columns not in training data (will use NULL values)")
        logger.warning(f"   ES columns not in data: {sorted(missing_in_df)[:20]}{'...' if len(missing_in_df) > 20 else ''}")
        logger.info(f"   ℹ️  The encoder will create NOT_PRESENT tokens for these columns")
    
    if extra_in_df:
        logger.info(f"ℹ️  Training data has {len(extra_in_df)} columns not used by embedding space (will be ignored):")
        logger.info(f"   Extra columns: {sorted(extra_in_df)[:20]}{'...' if len(extra_in_df) > 20 else ''}")
    
    overlap = es_columns & df_columns
    
    # Calculate overlap from BOTH directions
    es_overlap_pct = (len(overlap) / len(es_columns) * 100) if es_columns else 0  # How many ES columns are in data
    sp_overlap_pct = (len(overlap) / len(df_columns) * 100) if df_columns else 0  # How many SP columns are in ES
    
    logger.info(f"📊 Column overlap analysis:")
    logger.info(f"   ES → SP: {len(overlap)}/{len(es_columns)} ES columns in data ({es_overlap_pct:.1f}%)")
    logger.info(f"   SP → ES: {len(overlap)}/{len(df_columns)} data columns in ES ({sp_overlap_pct:.1f}%)")
    logger.info(f"   Overlapping columns: {len(overlap)}")
    
    # Check for NO overlap (immediate failure)
    if len(overlap) == 0:
        logger.error(f"💥 CRITICAL: ZERO overlapping columns - completely different datasets!")
        logger.error(f"   ES columns ({len(es_columns)}): {sorted(es_columns)[:30]}")
        logger.error(f"   Data columns ({len(df_columns)}): {sorted(df_columns)[:30]}")
        raise ValueError("No overlapping columns - completely different datasets. Cannot encode.")
    
    # Check SP → ES: How many NEW columns (in SP but not in ES)?
    # Having SOME new columns (<10%) is fine and expected for fine-tuning
    new_columns_pct = (len(extra_in_df) / len(df_columns) * 100) if df_columns else 0
    
    if new_columns_pct > 75:
        logger.error(f"💥 CRITICAL: {new_columns_pct:.1f}% of SP columns are NEW (not in ES)!")
        logger.error(f"   {len(extra_in_df)}/{len(df_columns)} columns will be IGNORED (not in ES)")
        logger.error(f"   Ignored columns: {sorted(extra_in_df)[:20]}")
        logger.error(f"   Only {len(overlap)} columns will be used for training!")
        logger.error(f"   This means most of your data won't be used - wrong embedding space?")
        raise ValueError(
            f"Too many new columns ({new_columns_pct:.1f}%). "
            f"More than 75% of your data columns are not in the embedding space. "
            f"Only {len(overlap)}/{len(df_columns)} columns will be encoded."
        )
    
    if new_columns_pct > 50:
        import time
        logger.warning(f"")
        logger.warning(f"⚠️  ⚠️  ⚠️  WARNING: {new_columns_pct:.1f}% NEW COLUMNS (not in ES)! ⚠️  ⚠️  ⚠️")
        logger.warning(f"")
        logger.warning(f"   {len(extra_in_df)}/{len(df_columns)} columns will be IGNORED (not in ES)")
        logger.warning(f"   Ignored columns: {sorted(extra_in_df)[:30]}")
        logger.warning(f"")
        logger.warning(f"   This means MORE THAN HALF your data won't contribute to training!")
        logger.warning(f"   Consider using an embedding space trained on this dataset instead.")
        logger.warning(f"")
        logger.warning(f"⏸️  PAUSING FOR 10 SECONDS - Press Ctrl+C to abort if this is wrong...")
        logger.warning(f"")
        time.sleep(10)
        logger.info(f"✅ Continuing with {new_columns_pct:.1f}% new columns...")
    
    elif new_columns_pct > 10:
        logger.warning(f"⚠️  {new_columns_pct:.1f}% of SP columns are new (not in ES)")
        logger.warning(f"   {len(extra_in_df)} columns will be ignored: {sorted(extra_in_df)[:20]}{'...' if len(extra_in_df) > 20 else ''}")
    
    elif len(extra_in_df) > 0:
        logger.info(f"ℹ️  {len(extra_in_df)} new columns in SP data ({new_columns_pct:.1f}%) - will be ignored")
        logger.info(f"   New columns: {sorted(extra_in_df)[:10]}{'...' if len(extra_in_df) > 10 else ''}")
    
    # Generate comprehensive column overlap report
    logger.info(f"")
    logger.info(f"=" * 100)
    logger.info(f"📋 COLUMN OVERLAP REPORT")
    logger.info(f"=" * 100)
    logger.info(f"")
    logger.info(f"✅ COLUMNS IN BOTH ES AND SP ({len(overlap)} columns):")
    for col in sorted(overlap)[:50]:
        logger.info(f"   ✓ {col}")
    if len(overlap) > 50:
        logger.info(f"   ... and {len(overlap) - 50} more overlapping columns")
    
    logger.info(f"")
    logger.info(f"➖ ES COLUMNS MISSING FROM SP ({len(missing_in_df)} columns - will use NOT_PRESENT):")
    if len(missing_in_df) == 0:
        logger.info(f"   (none)")
    else:
        for col in sorted(missing_in_df)[:50]:
            logger.info(f"   ✗ {col}")
        if len(missing_in_df) > 50:
            logger.info(f"   ... and {len(missing_in_df) - 50} more missing columns")
    
    logger.info(f"")
    logger.info(f"➕ SP COLUMNS NOT IN ES ({len(extra_in_df)} columns - will be ignored):")
    if len(extra_in_df) == 0:
        logger.info(f"   (none)")
    else:
        for col in sorted(extra_in_df)[:50]:
            logger.info(f"   + {col}")
        if len(extra_in_df) > 50:
            logger.info(f"   ... and {len(extra_in_df) - 50} more extra columns")
    
    logger.info(f"")
    logger.info(f"=" * 100)
    logger.info(f"")
    
    # Calculate distribution shift (KL divergence) for overlapping columns
    # DISABLED: Only works for categorical columns, not useful for most datasets
    if False and len(overlap) > 0:
        logger.info(f"📊 DISTRIBUTION SHIFT ANALYSIS (KL Divergence for overlapping columns)")
        logger.info(f"=" * 100)
        
        try:
            from lib.distribution_shift_detector import DistributionShiftDetector
            
            # Use the already-loaded ES object (has codecs with statistics)
            if es and hasattr(es, 'col_codecs') and es.col_codecs:
                logger.info(f"   Analyzing distribution shifts using ES codecs...")
                detector = DistributionShiftDetector(es)
                shift_reports = detector.analyze_dataframe(train_df, target_column=args.target_column)
                
                # Summarize ALL columns (overlapping, missing, and extra)
                critical_shifts = []
                warning_shifts = []
                ok_shifts = []
                missing_cols = []
                new_cols = []
                
                for col_name, report in shift_reports.items():
                    # Check if column is in overlap, missing, or extra
                    if col_name in missing_in_df:
                        missing_cols.append(col_name)
                        continue  # ES column missing from SP
                    elif col_name in extra_in_df:
                        new_cols.append(col_name)
                        continue  # SP column not in ES
                    
                    # Overlapping column - check metrics
                    kl_div = report.metrics.get('kl_divergence')
                    if kl_div is None:
                        continue
                    
                    # Categorize by KL divergence
                    if kl_div > 1.0:
                        critical_shifts.append((col_name, kl_div))
                    elif kl_div >= 0.5:
                        warning_shifts.append((col_name, kl_div))
                    else:
                        ok_shifts.append((col_name, kl_div))
                
                # Sort by KL divergence (highest first)
                critical_shifts.sort(key=lambda x: x[1], reverse=True)
                warning_shifts.sort(key=lambda x: x[1], reverse=True)
                ok_shifts.sort(key=lambda x: x[1], reverse=True)
                
                logger.info(f"")
                logger.info(f"   Summary (overlapping columns only):")
                logger.info(f"   - 🔴 CRITICAL shifts (KL > 1.0): {len(critical_shifts)} columns")
                logger.info(f"   - 🟡 WARNING shifts (KL 0.5-1.0): {len(warning_shifts)} columns")
                logger.info(f"   - 🟢 OK (KL < 0.5): {len(ok_shifts)} columns")
                logger.info(f"   - ➖ ES columns missing from SP: {len(missing_cols)} columns")
                logger.info(f"   - ➕ SP columns not in ES: {len(new_cols)} columns")
                logger.info(f"")
                
                if critical_shifts:
                    logger.warning(f"🔴 CRITICAL Distribution Shifts (top 20):")
                    for col, kl in critical_shifts[:20]:
                        logger.warning(f"   {col:40s} KL divergence: {kl:.4f}")
                    if len(critical_shifts) > 20:
                        logger.warning(f"   ... and {len(critical_shifts) - 20} more critical shifts")
                
                if warning_shifts:
                    logger.info(f"")
                    logger.info(f"🟡 WARNING Distribution Shifts (top 20):")
                    for col, kl in warning_shifts[:20]:
                        logger.info(f"   {col:40s} KL divergence: {kl:.4f}")
                    if len(warning_shifts) > 20:
                        logger.info(f"   ... and {len(warning_shifts) - 20} more warning shifts")
                
                # Show a few OK columns for reference
                if ok_shifts:
                    logger.info(f"")
                    logger.info(f"🟢 Stable Columns (lowest KL, top 10):")
                    for col, kl in sorted(ok_shifts, key=lambda x: x[1])[:10]:
                        logger.info(f"   {col:40s} KL divergence: {kl:.4f}")
                
                logger.info(f"")
                logger.info(f"   COVERAGE SUMMARY:")
                logger.info(f"   - Total columns analyzed: {len(shift_reports)} (excluding target '{args.target_column}' and __featrix* internal)")
                logger.info(f"   - Overlapping columns: {len(overlap)}")
                logger.info(f"   - KL divergence computed: {len(critical_shifts) + len(warning_shifts) + len(ok_shifts)}")
                logger.info(f"   - Missing ES columns: {len(missing_cols)}")
                logger.info(f"   - New SP columns: {len(new_cols)}")
                
                # List columns where KL could not be computed
                no_kl_columns = [r.column_name for r in shift_reports.values() if r.kl_divergence is None and r.column_name in overlap]
                if no_kl_columns:
                    logger.warning(f"   ⚠️  Could not compute KL divergence for {len(no_kl_columns)} columns:")
                    for col in sorted(no_kl_columns)[:20]:
                        logger.warning(f"      - {col}")
                    if len(no_kl_columns) > 20:
                        logger.warning(f"      ... and {len(no_kl_columns) - 20} more columns")
                
                # Note about KL divergence approximation
                logger.info(f"")
                logger.info(f"   NOTE: KL divergence is approximate (ES distribution assumed uniform)")
                logger.info(f"         Exact KL would require ES training data histograms")
                logger.info(f"         Use these values as relative indicators, not absolute measures")
            else:
                logger.warning(f"   ⚠️  ES codecs not available - cannot calculate distribution shift")
                logger.info(f"   (Distribution shift analysis requires ES codec statistics)")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not calculate distribution shift: {e}")
            logger.debug(traceback.format_exc())
        
        logger.info(f"=" * 100)
        logger.info(f"")
    
    # Check ES → SP overlap (how many ES columns are missing - will use NOT_PRESENT)
    if es_overlap_pct < 25:
        logger.error(f"💥 CRITICAL: Only {es_overlap_pct:.1f}% of ES columns are in data!")
        logger.error(f"   {len(overlap)}/{len(es_columns)} ES columns available")
        logger.error(f"   {len(missing_in_df)} ES columns MISSING: {sorted(missing_in_df)[:20]}")
        raise ValueError(
            f"Insufficient ES→SP overlap ({es_overlap_pct:.1f}%). "
            f"Need at least 25% of ES columns in training data. "
            f"Only {len(overlap)}/{len(es_columns)} columns available."
        )
    
    if es_overlap_pct < 50:
        logger.warning(f"⚠️  WARNING: Low ES→SP overlap ({es_overlap_pct:.1f}%) - embeddings may be poor quality!")
        logger.warning(f"   Only {len(overlap)}/{len(es_columns)} ES columns found in training data")
        logger.warning(f"   Missing {len(missing_in_df)} ES columns (will use NOT_PRESENT): {sorted(missing_in_df)[:10]}{'...' if len(missing_in_df) > 10 else ''}")
        logger.warning(f"   Training may produce poor results with this much missing data")
    
    # Handle __featrix_train_predictor column for single predictor training
    train_df = apply_predictor_filter(train_df)
    
    # CRITICAL: Validate target column has more than one unique value after filtering
    # This must happen AFTER filtering because filtering might reduce data to single value
    logger.info(f"🔍 Validating target column '{args.target_column}' has multiple values...")
    target_col_data = train_df[args.target_column].dropna()
    unique_values = target_col_data.unique()
    unique_count = len(unique_values)
    
    if unique_count == 0:
        error_msg = (
            f"❌ CRITICAL ERROR: Target column '{args.target_column}' has NO non-null values after filtering!\n"
            f"   Total rows: {len(train_df)}\n"
            f"   Non-null values: {len(target_col_data)}\n"
            f"   Cannot train a predictor with no target values."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if unique_count == 1:
        single_value = unique_values[0]
        value_count = len(target_col_data)
        error_msg = (
            f"❌ CRITICAL ERROR: Target column '{args.target_column}' has only ONE unique value after filtering!\n"
            f"   Unique value: {single_value!r} (type: {type(single_value).__name__})\n"
            f"   Count: {value_count} rows\n"
            f"   Cannot train a predictor when all examples have the same target value.\n"
            f"   A predictor needs at least 2 different target values to learn patterns."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"✅ Target column has {unique_count} unique values: {list(unique_values)}")
    logger.info(f"   Value distribution:")
    value_counts = target_col_data.value_counts()
    for val, count in value_counts.items():
        pct = (count / len(target_col_data) * 100) if len(target_col_data) > 0 else 0
        logger.info(f"      {val!r}: {count} ({pct:.1f}%)")
    
    # Create a proper FeatrixInputDataSet to get detector results
    logger.info("=" * 80)
    logger.info("📊 CREATING INPUT DATA SET FOR DETECTION ANALYSIS")
    logger.info("=" * 80)
    from featrix.neural.input_data_set import FeatrixInputDataSet
    
    # Create dataset with full detection (not standup_only) to get detector results
    training_input_dataset = FeatrixInputDataSet(
        df=train_df,
        ignore_cols=[],
        limit_rows=None,
        encoder_overrides=None,
        project_row_meta_data=None,
        standup_only=False,  # Full detection so we can print detector results
    )
    
    # Print detector results for the training data
    logger.info("=" * 80)
    logger.info("📊 PRINTING DETECTOR RESULTS FOR SINGLE PREDICTOR TRAINING DATA")
    logger.info("=" * 80)
    training_input_dataset._printDetectorResults("SINGLE PREDICTOR TRAINING DATA")
    logger.info("=" * 80)
    
    # AUTOMATIC TYPE CONVERSION: Convert SP data types to match ES codec types
    # MUST happen BEFORE distribution shift detection so the detector analyzes converted data
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 AUTOMATIC TYPE CONVERSION TO MATCH ES CODECS")
    logger.info("=" * 80)
    logger.info("Converting SP data types to match embedding space codec types...")
    
    from lib.distribution_shift_detector import DistributionShiftDetector
    detector = DistributionShiftDetector(es)
    conversions_made = 0
    
    for col_name in train_df.columns:
        if col_name == args.target_column:
            continue  # Skip target column - it will be handled separately
        
        if col_name not in es.col_codecs:
            continue  # Column not in ES, skip
        
        codec = es.col_codecs[col_name]
        col_data = train_df[col_name]
        
        # Get codec type
        from featrix.neural.set_codec import SetCodec
        from featrix.neural.scalar_codec import ScalarCodec
        from featrix.neural.string_codec import StringCodec
        
        is_set_codec = isinstance(codec, SetCodec)
        is_scalar_codec = isinstance(codec, ScalarCodec)
        is_string_codec = isinstance(codec, StringCodec)
        
        sp_is_numeric = pd.api.types.is_numeric_dtype(col_data)
        sp_is_categorical = pd.api.types.is_object_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data)
        
        # Convert numeric to categorical string if ES has SetCodec or StringCodec
        if sp_is_numeric and (is_set_codec or is_string_codec):
            # Normalize numeric values to strings to match codec vocabulary
            def normalize_to_string(val):
                if pd.isna(val):
                    return val
                try:
                    float_val = float(val)
                    if float_val.is_integer():
                        return str(int(float_val))
                    return str(float_val)
                except (ValueError, TypeError):
                    return str(val)
            
            train_df[col_name] = col_data.apply(normalize_to_string)
            conversions_made += 1
            logger.info(f"   ✅ {col_name}: float64 → object (normalized to match {type(codec).__name__} vocab)")
        
        # Convert categorical to numeric if ES has ScalarCodec
        elif sp_is_categorical and is_scalar_codec:
            # Try converting to numeric
            try:
                numeric_col = pd.to_numeric(col_data, errors='coerce')
                if numeric_col.notna().sum() > 0:  # At least some values converted
                    train_df[col_name] = numeric_col
                    conversions_made += 1
                    logger.info(f"   ✅ {col_name}: object → float64 (converted to match ScalarCodec)")
            except (ValueError, TypeError):
                pass  # Can't convert - leave as is
    
    if conversions_made > 0:
        logger.info(f"✅ Converted {conversions_made} column(s) to match ES codec types")
    else:
        logger.info("✅ No type conversions needed - all columns already match ES codec types")
    logger.info("=" * 80)
    logger.info("")
    
    # DISTRIBUTION SHIFT DETECTION: Compare SP training data to ES training data
    # NOTE: This happens AFTER type conversion so the detector analyzes already-converted data
    logger.info("=" * 80)
    logger.info("🔍 DISTRIBUTION SHIFT DETECTION")
    logger.info("=" * 80)
    logger.info("Comparing single predictor training data to base embedding space...")
    logger.info("(Note: Data types have been converted to match ES codecs)")
    logger.info("")
    shift_results = None
    try:
        from lib.distribution_shift_detector import detect_distribution_shift
        shift_results = detect_distribution_shift(
            embedding_space=es,
            sp_train_df=train_df,
            target_column=args.target_column
        )
        
        # Extract summary for logging
        shift_summary = shift_results.get('summary', {})
        
        # Log summary stats
        if shift_summary.get('has_critical_issues'):
            logger.error("🚨 CRITICAL DISTRIBUTION ISSUES DETECTED - training may fail or produce poor results!")
        elif shift_summary.get('warning_columns', 0) > 0:
            logger.warning(f"⚠️  {shift_summary['warning_columns']} columns have distribution warnings")
        else:
            logger.info("✅ No significant distribution shifts detected")
        
        # Save detailed report to JSON file
        report_filename = "sp_vs_es_distribution_report.json"
        try:
            with open(report_filename, 'w') as f:
                json.dump(shift_results, f, indent=2, default=str)
            logger.info(f"📄 Distribution shift report saved to: {report_filename}")
        except Exception as save_error:
            logger.warning(f"⚠️  Failed to save distribution report to JSON: {save_error}")
            
    except Exception as e:
        logger.warning(f"⚠️  Distribution shift detection failed: {e}")
        traceback.print_exc()
    logger.info("=" * 80)
    logger.info("")
    
    # Print label distribution early (before training starts)
    logger.info("=" * 80)
    logger.info("📊 LABEL DISTRIBUTION FOR SINGLE PREDICTOR TRAINING")
    logger.info("=" * 80)
    if args.target_column in train_df.columns:
        label_counts = train_df[args.target_column].value_counts()
        total_rows = len(train_df)
        logger.info(f"📈 TARGET COLUMN: '{args.target_column}'")
        logger.info(f"📈 Total rows: {total_rows:,}")
        logger.info(f"📈 Label distribution:")
        for label, count in label_counts.items():
            percentage = (count / total_rows) * 100 if total_rows > 0 else 0.0
            logger.info(f"   '{label}': {count:,} samples ({percentage:.2f}%)")
        
        # Show null/missing values
        null_count = train_df[args.target_column].isnull().sum()
        if null_count > 0:
            null_pct = (null_count / total_rows) * 100 if total_rows > 0 else 0.0
            logger.warning(f"   ⚠️  NULL/MISSING: {null_count:,} samples ({null_pct:.2f}%)")
        
        # Show unique values count
        unique_count = train_df[args.target_column].nunique()
        logger.info(f"   Unique values: {unique_count}")
    else:
        logger.error(f"❌ Target column '{args.target_column}' not found in data!")
        logger.error(f"   Available columns: {list(train_df.columns)}")
    logger.info("=" * 80)
    
    # Log fill rates for all columns when single predictor is using its own dataset
    # (This is always the case for single predictor training - it loads from args.input_file)
    logger.info("=" * 80)
    logger.info("📊 COLUMN FILL RATES (Single Predictor Training Dataset)")
    logger.info("=" * 80)
    total_rows = len(train_df)
    for col_name in train_df.columns:
        col_data = train_df[col_name]
        non_null_count = col_data.notna().sum()
        null_count = col_data.isnull().sum()
        fill_rate = (non_null_count / total_rows * 100) if total_rows > 0 else 0.0
        logger.info(f"   {col_name:40s}: {fill_rate:6.2f}% ({non_null_count:,}/{total_rows:,} non-null)")
    logger.info("=" * 80)
    
    # Validate that target column exists (with fuzzy matching for special characters)
    logger.info(f"🔍 Step 4: Validating target column '{args.target_column}' exists")
    if args.target_column not in train_df.columns:
        # Try fuzzy matching by removing special characters
        # This handles cases like "Love's" vs "Loves"
        import re
        def normalize_column_name(name):
            """Remove special characters except underscores for matching"""
            return re.sub(r"[^\w]", "", name)
        
        normalized_target = normalize_column_name(args.target_column)
        matches = []
        for col in train_df.columns:
            if normalize_column_name(col) == normalized_target:
                matches.append(col)
        
        if len(matches) == 1:
            actual_column = matches[0]
            logger.info(f"✅ Fuzzy match found: '{args.target_column}' → '{actual_column}'")
            logger.info(f"   (Normalized matching: special characters ignored)")
            args.target_column = actual_column
        elif len(matches) > 1:
            raise ValueError(f"Target column '{args.target_column}' not found. Multiple fuzzy matches found: {matches}. Please specify exact column name.")
        else:
            error_msg = (
                f"❌ CRITICAL ERROR: Target column '{args.target_column}' NOT FOUND in data!\n"
                f"   Data has {len(train_df)} rows and {len(train_df.columns)} columns\n"
                f"   Available columns: {list(train_df.columns)}\n"
                f"   This indicates the target column was lost during CSV reading.\n"
                f"   Check CSV reading logs (TRACE CSV messages) to see what columns were actually loaded.\n"
                f"   The CSV file may have been parsed incorrectly (wrong quotechar, delimiter issues, etc.)"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    logger.info(f"🔍 Step 4 DONE: Data loaded: {len(train_df)} rows, {len(train_df.columns)} columns")
    
    # CRITICAL: Fail immediately if there are 0 rows - cannot train on empty data
    if len(train_df) == 0:
        error_msg = (
            f"❌ CRITICAL ERROR: Training data has ZERO rows!\n"
            f"   Cannot train a single predictor with no training examples.\n"
            f"   This usually means:\n"
            f"   1. The SQLite database from create_structured_data is empty\n"
            f"   2. The CSV file was empty or failed to load\n"
            f"   3. All rows were filtered out by __featrix_train_predictor column\n"
            f"   Check create_structured_data logs to see if data was written to SQLite."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # CRITICAL: Prime string cache with strings from the new training file
    # Pre-warm the string server cache with strings from this training file
    logger.info("🔍 Step 5: Pre-warming string server cache with training data strings...")
    try:
        from featrix.neural.input_data_set import FeatrixInputDataSet
        # Create dataset to detect string columns and pre-warm cache
        training_dataset = FeatrixInputDataSet(
            df=train_df,
            ignore_cols=[],
            limit_rows=None,  # Use all rows to warm cache completely
            encoder_overrides=None,
            project_row_meta_data=None,
            standup_only=True,  # Skip detection/enrichment, just need column types
        )
        # Pre-warm the cache with all strings from training data
        logger.info(f"🔥 Pre-warming string server cache with {len(train_df)} rows of training data...")
        training_dataset.warm_string_server_cache()
        logger.info(f"✅ String server cache pre-warmed successfully")
    except Exception as cache_err:
        logger.warning(f"⚠️  Failed to pre-warm string server cache: {cache_err}")
        logger.warning(f"   Training will continue but may encounter cache misses")
    
    # Handle positive_label fuzzy matching and type conversion
    args.positive_label = resolve_positive_label(args.positive_label, args.target_column, train_df)
    
    # Progress callback for job system integration
    # Track last epoch posted to avoid duplicate posts
    last_posted_epoch = [-1]  # Use list to allow modification in closure
    
    def progress_callback(progress_dict):
        try:
            # Import here to avoid circular imports
            from training_monitor import post_training_progress
            
            # LOG TRAINING PROGRESS (like ES training does)
            epoch_idx = progress_dict.get('epoch_idx', 0)
            current_loss = progress_dict.get('current_loss', 0)
            validation_loss = progress_dict.get('validation_loss', 0)
            lr_raw = progress_dict.get('lr', 0)
            progress = progress_dict.get('progress_counter', 0)
            progress_max = progress_dict.get('max_progress', 1)
            
            # Handle learning rate - might be a list from scheduler
            if isinstance(lr_raw, list) and lr_raw:
                lr = lr_raw[0]  # Take first element if it's a list
            else:
                lr = lr_raw if lr_raw else 0
            
            # Log training progress every epoch like ES training
            # Note: progress_max is total BATCHES (epochs × batches_per_epoch), not epochs
            # So progress/progress_max gives batch-level progress, not epoch-level progress
            epoch_total = progress_dict.get('epoch_total', 0)
            # Safe formatting - check types before using format specifiers
            loss_str = f"{current_loss}" if isinstance(current_loss, (int, float)) else str(current_loss)
            val_loss_str = f"{validation_loss}" if isinstance(validation_loss, (int, float)) else str(validation_loss)
            lr_str = f"{lr}" if isinstance(lr, (int, float)) else str(lr)
            
            # Get gradient norm and parameter update norm if available
            grad_norm = progress_dict.get('avg_gradient_norm', progress_dict.get('gradient_norm', None))
            param_update_norm = progress_dict.get('avg_param_update_norm', progress_dict.get('param_update_norm', None))
            grad_norm_str = f", grad_norm={grad_norm:.6f}" if grad_norm is not None else ""
            param_update_norm_str = f", param_update_norm={param_update_norm:.6f}" if param_update_norm is not None else ""
            
            logger.info(f"🎯 SP Epoch {epoch_idx}/{epoch_total}: training_loss={loss_str}, validation_loss={val_loss_str}, lr={lr_str}{grad_norm_str}{param_update_norm_str}")
            if progress_max > 0:
                logger.info(f"   Batch Progress: {progress}/{progress_max} ({(progress/progress_max*100):.1f}%)")
            else:
                logger.info(f"   Batch Progress: {progress}/{progress_max}")
            
            # Log metrics if available
            metrics = progress_dict.get('metrics', {})
            if metrics and metrics != {}:
                accuracy = metrics.get('accuracy', 0)
                f1 = metrics.get('f1', 0) 
                auc = metrics.get('auc', 0)
                # Safe formatting - check types before using format specifiers
                acc_str = f"{accuracy}" if isinstance(accuracy, (int, float)) else str(accuracy)
                f1_str = f"{f1}" if isinstance(f1, (int, float)) else str(f1)
                auc_str = f"{auc}" if isinstance(auc, (int, float)) else str(auc)
                logger.info(f"   Metrics: accuracy={acc_str}, f1={f1_str}, auc={auc_str}")
            
            # Store detailed metrics to Redis for monitoring UI (only on epoch completion)
            if args.job_queue and args.job_id and epoch_idx != last_posted_epoch[0]:
                try:
                    from redis_job_progress import get_redis_job_progress
                    redis_progress = get_redis_job_progress()
                    if redis_progress.redis_available:
                        # Collect all available metrics for predictor training
                        detailed_metrics = {
                            'learning_rate': float(lr) if isinstance(lr, (int, float)) else None,
                            'train_loss': float(current_loss) if isinstance(current_loss, (int, float)) else None,
                            'validation_loss': float(validation_loss) if isinstance(validation_loss, (int, float)) else None,
                        }
                        
                        # Add classification/regression metrics
                        if metrics:
                            for key in ['auc', 'pr_auc', 'accuracy', 'f1', 'precision', 'recall', 'specificity', 'mcc', 'brier_score']:
                                if key in metrics and metrics[key] is not None:
                                    try:
                                        detailed_metrics[key] = float(metrics[key])
                                    except (ValueError, TypeError):
                                        pass
                        
                        redis_progress.append_training_metrics(
                            job_type=args.job_queue,
                            job_id=args.job_id,
                            epoch=int(epoch_idx),
                            metrics=detailed_metrics
                        )
                except Exception as redis_err:
                    logger.debug(f"Failed to store predictor training metrics to Redis: {redis_err}")
            
            # Post progress to monitor (only on epoch completion, not every batch)
            # Only post when epoch_idx changes (new epoch completed)
            if epoch_idx > 0 and epoch_total > 0 and epoch_idx != last_posted_epoch[0]:
                try:
                    # Check if GPU is being used
                    ran_on_gpu = torch.cuda.is_available() and torch.cuda.current_device() is not None
                    
                    # Determine training type from target column type
                    training_type = "classification"
                    if args.target_column_type == "numeric":
                        training_type = "regression"
                    
                    # Calculate estimated time remaining if we have timing info
                    estimated_time_remaining = None
                    time_now = progress_dict.get('time_now')
                    if time_now and epoch_idx > 0:
                        # Estimate based on batch progress rate
                        if progress_max > 0 and progress > 0:
                            elapsed = time_now - progress_dict.get('start_time', time_now)
                            if elapsed > 0:
                                rate = progress / elapsed  # batches per second
                                remaining_batches = progress_max - progress
                                if rate > 0:
                                    total_seconds = remaining_batches / rate
                                    minutes = int(total_seconds / 60)
                                    if minutes > 0:
                                        estimated_time_remaining = f"{minutes}m"
                                    else:
                                        estimated_time_remaining = f"{int(total_seconds)}s"
                    
                    # Get session_id from args (prefer session_id, fallback to job_id, or generate one)
                    session_id = (
                        getattr(args, 'session_id', None) or 
                        args.job_id if hasattr(args, 'job_id') and args.job_id else 
                        f"sp-{id(progress_dict)}"
                    )
                    
                    # Build metadata with dataset_hash and config parameters
                    progress_metadata = {}
                    progress_network_arch = {}
                    
                    # Add dataset_hash if available
                    try:
                        from featrix_monitor import generate_dataset_hash
                        dataset_hash = generate_dataset_hash(train_df)
                        progress_metadata['dataset_hash'] = dataset_hash
                    except:
                        pass
                    
                    # Add monitor config parameters if available
                    if hasattr(args, 'monitor_config') and args.monitor_config:
                        for key, value in args.monitor_config.items():
                            if key not in ['status', 'dataset_hash']:
                                progress_metadata[key] = value
                                progress_network_arch[key] = value
                    
                    # Add SP hyperparameters from predictor if available
                    if hasattr(args, 'predictor') or 'fsp' in locals():
                        predictor_obj = getattr(args, 'predictor', None) or (fsp if 'fsp' in locals() else None)
                        if predictor_obj and hasattr(predictor_obj, 'predictor'):
                            pred = predictor_obj.predictor
                            if hasattr(pred, 'n_hidden_layers'):
                                progress_network_arch['n_hidden_layers'] = pred.n_hidden_layers
                            if hasattr(pred, 'd_hidden'):
                                progress_network_arch['d_hidden'] = pred.d_hidden
                            if hasattr(pred, 'dropout'):
                                progress_network_arch['dropout'] = pred.dropout
                    
                    # Add embedding space params
                    if 'es' in locals() or hasattr(args, 'embedding_space'):
                        es_obj = locals().get('es') or getattr(args, 'embedding_space', None)
                        if es_obj:
                            if hasattr(es_obj, 'd_model'):
                                progress_network_arch['d_model'] = es_obj.d_model
                            if hasattr(es_obj, 'n_transformer_layers'):
                                progress_network_arch['n_transformer_layers'] = es_obj.n_transformer_layers
                            if hasattr(es_obj, 'n_attention_heads'):
                                progress_network_arch['n_attention_heads'] = es_obj.n_attention_heads
                    
                    post_training_progress(
                        session_id=session_id,
                        training_type=training_type,
                        current_epoch=int(epoch_idx),
                        total_epochs=int(epoch_total),
                        current_training_loss=float(current_loss) if current_loss else None,
                        current_validation_loss=float(validation_loss) if validation_loss else None,
                        estimated_time_remaining=estimated_time_remaining,
                        ran_on_gpu=ran_on_gpu,
                        metadata=progress_metadata if progress_metadata else None,
                        network_architecture=progress_network_arch if progress_network_arch else None,
                    )
                    # Mark this epoch as posted
                    last_posted_epoch[0] = epoch_idx
                except Exception as monitor_err:
                    # Don't let monitor errors break training
                    logger.debug(f"Monitor progress post failed: {monitor_err}")
            
            if args.job_queue and args.job_id:
                # Try Redis first for fast progress updates (partial updates)
                try:
                    from redis_job_progress import get_redis_job_progress
                    redis_progress = get_redis_job_progress()
                    if redis_progress.redis_available:
                        # Update progress in Redis (fast partial update)
                        redis_progress.update_progress(
                            job_type=args.job_queue,
                            job_id=args.job_id,
                            progress=progress / progress_max if progress_max > 0 else 0,
                            current_epoch=epoch_idx,
                            current_loss=current_loss,
                            validation_loss=validation_loss,
                            metrics=metrics,
                            time_now=progress_dict.get('time_now', None),
                        )
                        # Still update Redis job data periodically (every 10 batches or on epoch boundaries)
                        if epoch_idx > 0 and (progress % 10 == 0 or epoch_idx != last_posted_epoch[0]):
                            from lib.job_manager import load_job, save_job
                            job_data = load_job(args.job_id)
                            if job_data:
                                job_data['progress'] = progress / progress_max if progress_max > 0 else 0
                                job_data['current_epoch'] = epoch_idx
                                job_data['current_loss'] = current_loss
                                job_data['validation_loss'] = validation_loss
                                job_data['metrics'] = metrics
                                job_data['time_now'] = progress_dict.get('time_now', None)
                                session_id = job_data.get('session_id') or args.session_id
                                job_type = job_data.get('job_type') or args.job_queue
                                save_job(args.job_id, job_data, session_id, job_type)
                    else:
                        # Redis not available - update job data directly
                        from lib.job_manager import load_job, save_job
                        job_data = load_job(args.job_id)
                        if job_data:
                            job_data['progress'] = progress / progress_max if progress_max > 0 else 0
                            job_data['current_epoch'] = epoch_idx
                            job_data['current_loss'] = current_loss
                            job_data['validation_loss'] = validation_loss
                            job_data['metrics'] = metrics
                            job_data['time_now'] = progress_dict.get('time_now', None)
                            session_id = job_data.get('session_id') or args.session_id
                            job_type = job_data.get('job_type') or args.job_queue
                            save_job(args.job_id, job_data, session_id, job_type)
                except Exception as redis_err:
                    # Redis failed - try to update job data directly
                    logger.debug(f"Redis progress update failed: {redis_err}")
                    try:
                        from lib.job_manager import load_job, save_job
                        job_data = load_job(args.job_id)
                        if job_data:
                            job_data['progress'] = progress / progress_max if progress_max > 0 else 0
                            job_data['current_epoch'] = epoch_idx
                            job_data['current_loss'] = current_loss
                            job_data['validation_loss'] = validation_loss
                            job_data['metrics'] = metrics
                            job_data['time_now'] = progress_dict.get('time_now', None)
                            session_id = job_data.get('session_id') or args.session_id
                            job_type = job_data.get('job_type') or args.job_queue
                            save_job(args.job_id, job_data, session_id, job_type)
                    except Exception as job_err:
                        logger.debug(f"Failed to update job data: {job_err}")
                
                epoch_idx = progress_dict.get('epoch_idx', 0)
                current_loss = progress_dict.get('current_loss', 'N/A')
                # Safe formatting - check types before using format specifiers
                if isinstance(progress, (int, float)) and isinstance(progress_max, (int, float)) and progress_max > 0:
                    pct = progress / progress_max * 100
                    pct_str = f"{pct}"
                else:
                    pct_str = "N/A"
                loss_str = f"{current_loss}" if isinstance(current_loss, (int, float)) else str(current_loss)
                logger.info(f"Progress: {progress}/{progress_max} ({pct_str}%) - Epoch {epoch_idx}, Loss: {loss_str}")
                
        except Exception as err:
            logger.error(f"Error during saving job progress: {err}")
            traceback.print_exc()
    
    training_worked = False
    batch_size = args.batch_size or 0 
    epochs = args.n_epochs or 0
    logger.info(f"... input batch_size = {batch_size}, epochs = {epochs}")
    
    if batch_size == 0:
        batch_size = ideal_batch_size(len(train_df), mode="predictor")
    
    if epochs == 0:
        # Calculate class imbalance ratio for classification tasks
        imbalance_ratio = 1.0
        if args.target_column_type == "set" and args.target_column in train_df.columns:
            value_counts = train_df[args.target_column].value_counts()
            if len(value_counts) >= 2:
                majority_count = value_counts.iloc[0]
                minority_count = value_counts.iloc[-1]
                imbalance_ratio = majority_count / max(minority_count, 1)
                logger.info(f"📊 Class imbalance detected: {majority_count}:{minority_count} (ratio: {imbalance_ratio:.1f}:1)")
        
        if epochs == 0:
            epochs = ideal_epochs_predictor(len(train_df), batch_size, imbalance_ratio=imbalance_ratio)
            logger.info(f"📊 Auto-calculated epochs: {epochs} (based on {len(train_df)} rows, imbalance ratio {imbalance_ratio:.1f})")
        else:
            logger.info(f"📊 Using specified epochs: {epochs} (user provided, not auto-calculated)")

    logger.info(f"... will use batch_size = {batch_size}, epochs = {epochs}")
    
    # Check if we're resuming from an existing predictor (continuation training)
    resume_from_predictor = getattr(args, 'resume_from_predictor', None)
    if resume_from_predictor:
        logger.info(f"🔄 RESUME MODE: Loading existing predictor from {resume_from_predictor}")
        logger.info(f"   Will continue training for {epochs} additional epochs")


    worked = False
    # FORCE CPU - don't reset to GPU
    # Note: Device will be determined automatically based on CUDA availability
    
    while not worked and batch_size >= 8:
        try:
            # Don't use CUDA - we're forcing CPU
            # if torch.cuda.is_available():
            #     torch.cuda.empty_cache()
            #     torch.cuda.synchronize()
            
            logger.info(f"Attempting training with batch_size = {batch_size}")
            
            # Analyze dataset complexity FIRST
            from featrix.neural.utils import analyze_dataset_complexity
            
            logger.info("\n" + "="*100)
            logger.info("STEP 1: DATASET COMPLEXITY ANALYSIS")
            logger.info("="*100)
            
            complexity_analysis = analyze_dataset_complexity(
                train_df=train_df,
                target_column=args.target_column,
                target_column_type=args.target_column_type
            )
            
            logger.info("\n" + "="*100)
            logger.info("STEP 2: ARCHITECTURE SELECTION")
            logger.info("="*100)
            
            # Initialize predictor_base (will be set if creating new predictor)
            predictor_base = None
            predictor_name = args.name or f"{args.target_column}_predictor"
            
            # Check if we're resuming from an existing predictor
            resume_from_predictor = getattr(args, 'resume_from_predictor', None)
            if resume_from_predictor:
                logger.info(f"🔄 RESUME MODE: Loading existing predictor from {resume_from_predictor}")
                _log_gpu_memory("BEFORE LOAD_SINGLE_PREDICTOR")
                fsp = load_single_predictor(resume_from_predictor)
                _log_gpu_memory("AFTER LOAD_SINGLE_PREDICTOR")
                logger.info(f"✅ Loaded existing predictor: {fsp.name if hasattr(fsp, 'name') else 'unnamed'}")
                logger.info(f"   Will continue training for {epochs} additional epochs")
                
                # Update embedding space reference (may have changed)
                fsp.embedding_space = es
                fsp.embedding_space.output_dir = current_dir
                
                # Use existing batch_size and learning_rate if not specified
                if batch_size == 0 and hasattr(fsp, 'train_df') and len(fsp.train_df) > 0:
                    batch_size = ideal_batch_size(len(fsp.train_df), mode="predictor")
                    logger.info(f"   Using existing predictor's batch_size: {batch_size}")
                if args.learning_rate is None and hasattr(fsp, 'training_metrics') and fsp.training_metrics:
                    # Try to get last learning rate from training history
                    logger.info(f"   Using existing predictor's learning rate (will be set during training)")
            else:
                # NEW TRAINING: Create new predictor
                n_rows = len(train_df)
                
                # Try to get config from monitor.featrix.com first (if available)
                monitor_config = None
                if session_id:
                    logger.info("🔍 Querying monitor.featrix.com for next hyperparameter config...")
                    monitor_config = get_sp_config_from_monitor(
                        train_df=train_df,
                        es=es,
                        session_id=session_id,
                        mark_in_progress=True
                    )
                
                if monitor_config:
                    # Use config from monitor
                    logger.info("✅ Using hyperparameter config from monitor.featrix.com")
                    d_hidden = monitor_config.get("d_hidden")
                    n_hidden_layers = monitor_config.get("n_hidden_layers", 2)
                    dropout = monitor_config.get("dropout", 0.3)
                    use_batch_norm = monitor_config.get("use_batch_norm", True)
                    use_residual = monitor_config.get("residual", True)
                    
                    # Store monitor config in args for later use in posting results
                    if not hasattr(args, 'monitor_config'):
                        args.monitor_config = monitor_config
                else:
                    # Fallback: Auto-calculate optimal configuration
                    logger.info("ℹ️  No config from monitor, using auto-calculated configuration")
                    from featrix.neural.utils import ideal_single_predictor_config
                    
                    config = ideal_single_predictor_config(
                        n_rows=n_rows,
                        d_model=es.d_model,
                        n_cols=len(train_df.columns),
                        fine_tune=args.fine_tune,
                        complexity_analysis=complexity_analysis
                    )
                    
                    d_hidden = config.get("d_hidden", 256)
                    n_hidden_layers = config.get("n_hidden_layers", 2)
                    dropout = config.get("dropout", 0.3)
                    use_batch_norm = config.get("use_batch_norm", True)
                    use_residual = config.get("residual", True)
                
                # Override n_hidden_layers if explicitly provided (for manual grid search)
                if args.n_hidden_layers is not None and not monitor_config:
                    logger.info(f"🔧 Overriding auto-calculated n_hidden_layers ({n_hidden_layers}) with user-provided value: {args.n_hidden_layers}")
                    n_hidden_layers = args.n_hidden_layers
                    
                    # CRITICAL: When n_hidden_layers is set to a deep network (>=5), adjust other parameters
                    # to match deep network requirements. Deep networks need:
                    # - Larger d_hidden for capacity
                    # - batch_norm=True for training stability
                    # - residual=True for gradient flow
                    # - Smaller batch_size to fit in memory and improve training stability
                    if n_hidden_layers >= 5:
                        # Ensure d_hidden is at least 128 for deep networks
                        if d_hidden is None or d_hidden < 128:
                            old_d_hidden = d_hidden
                            d_hidden = 128
                            logger.info(f"🔧 Adjusting d_hidden from {old_d_hidden} to {d_hidden} for deep network ({n_hidden_layers} layers)")
                        
                        # Enable batch norm and residual for deep networks
                        if not use_batch_norm:
                            logger.info(f"🔧 Enabling batch_norm for deep network ({n_hidden_layers} layers)")
                            use_batch_norm = True
                        if not use_residual:
                            logger.info(f"🔧 Enabling residual connections for deep network ({n_hidden_layers} layers)")
                            use_residual = True
                        
                        # Reduce batch_size for deep networks to prevent OOM and improve training stability
                        # Deep networks use more memory per sample, so we need smaller batches
                        # For 7 layers, reduce batch_size by ~4x (512 -> 128) or use ideal_batch_size if smaller
                        if batch_size > 128:
                            # Use ideal_batch_size as baseline, but cap at 128 for deep networks
                            ideal_bs = ideal_batch_size(len(train_df), mode="predictor")
                            new_batch_size = min(128, ideal_bs, batch_size)
                            if new_batch_size < batch_size:
                                logger.info(f"🔧 Reducing batch_size from {batch_size} to {new_batch_size} for deep network ({n_hidden_layers} layers)")
                                logger.info(f"   Reason: Deep networks require more memory per sample - smaller batches prevent OOM")
                                batch_size = new_batch_size
                
                logger.info(f"📊 Dataset size: {n_rows} rows - configuration:")
                if d_hidden is None:
                    logger.info(f"   • Architecture: Simple Linear layer (no hidden layers)")
                else:
                    logger.info(f"   • Hidden dimension: {d_hidden}")
                    logger.info(f"   • Hidden layers: {n_hidden_layers}")
                logger.info(f"   • Dropout: {dropout}")
                logger.info(f"   • Batch normalization: {use_batch_norm}")
                logger.info(f"   • Residual connections: {use_residual}")
                
                # Create the predictor architecture
                predictor_base = create_predictor_mlp(
                    d_in=es.d_model, 
                    d_hidden=d_hidden if d_hidden is not None else 256,  # Fallback for linear head
                    n_hidden_layers=n_hidden_layers,
                    dropout=dropout,
                    use_batch_norm=use_batch_norm,
                    residual=use_residual
                )
                logger.info("🔧 Creating FeatrixSinglePredictor instance...")
                fsp = FeatrixSinglePredictor(es, predictor_base, name=predictor_name, user_metadata=args.user_metadata)
                logger.info(f"🔧 FeatrixSinglePredictor created with name: {predictor_name}")
                
                # Store distribution shift results for model card
                if shift_results is not None:
                    fsp.distribution_shift_results = shift_results
                    logger.info("📊 Distribution shift results stored in predictor for model card")
            logger.info(f"🔧 FeatrixSinglePredictor created from module: {fsp.__class__.__module__}")
            
            # Get file location safely
            try:
                module_name = fsp.__class__.__module__
                if module_name in sys.modules:
                    mod = sys.modules[module_name]
                    file_loc = getattr(mod, '__file__', 'unknown')
                    logger.info(f"🔧 FeatrixSinglePredictor file location: {file_loc}")
            except Exception as e:
                logger.warning(f"Could not determine file location: {e}")
            
            # Check prep_for_training signature
            sig = inspect.signature(fsp.prep_for_training)
            logger.info(f"🔧 prep_for_training signature: {sig}")
            logger.info(f"🔧 prep_for_training parameters: {list(sig.parameters.keys())}")
            
            # Only call prep_for_training if not resuming (resumed predictor is already prepared)
            if not resume_from_predictor:
                # AUTO-ENABLE class weights if complexity analysis recommends it
                # FORCE ENABLED: Always use class weights regardless of args
                use_class_weights = True  # FORCED TO TRUE - was: args.use_class_weights
                if complexity_analysis and not args.use_class_weights:
                    # Check if complexity analysis recommends class weights
                    recommendations = complexity_analysis.get('recommendations', [])
                    imbalance_ratio = complexity_analysis.get('class_imbalance_ratio', 1.0)
                    
                    # Auto-enable if recommendation mentions class weights or if imbalance is significant
                    should_enable = False
                    for rec in recommendations:
                        if 'class weight' in rec.lower() or 'imbalance' in rec.lower():
                            should_enable = True
                            logger.info(f"✅ AUTO-ENABLING class weights based on complexity analysis recommendation: {rec}")
                            break
                    
                    # Also auto-enable for significant imbalance even if not explicitly recommended
                    if not should_enable and imbalance_ratio > 3.0:
                        should_enable = True
                        logger.info(f"✅ AUTO-ENABLING class weights due to class imbalance ratio: {imbalance_ratio:.1f}:1")
                    
                    if should_enable:
                        use_class_weights = True
                
                logger.info("="*100)
                logger.info(f"🔧 ABOUT TO CALL prep_for_training with target_col_name='{args.target_column}', target_col_type='{args.target_column_type}'")
                logger.info(f"🔧 prep_for_training method object: {fsp.prep_for_training}")
                logger.info(f"🔧 use_class_weights: {use_class_weights} {'(AUTO-ENABLED from complexity analysis)' if use_class_weights and not args.use_class_weights else ''}")
                logger.info(f"🔧 loss_type: {args.loss_type}")
                if args.class_imbalance:
                    logger.info(f"🔧 class_imbalance provided: {args.class_imbalance}")
                logger.info("="*100)
                
                fsp.prep_for_training(
                    train_df=train_df,
                    target_col_name=args.target_column,
                    target_col_type=args.target_column_type,
                    use_class_weights=use_class_weights,
                    loss_type=args.loss_type,
                    class_imbalance=args.class_imbalance,
                    cost_false_positive=args.cost_false_positive,
                    cost_false_negative=args.cost_false_negative
                )
                
                logger.info("="*100)
                logger.info(f"🔧 COMPLETED prep_for_training call")
                logger.info(f"🔧 Target codec after prep: {type(fsp.target_codec).__name__}")
                logger.info("="*100)
            else:
                logger.info("🔄 RESUME MODE: Skipping prep_for_training (predictor already prepared)")
                # Update train_df if needed (in case data changed)
                if hasattr(fsp, 'train_df'):
                    logger.info(f"   Updating train_df reference (keeping existing data)")
            
            logger.info(f"Predictor prepared. Target codec: {type(fsp.target_codec).__name__}")
            
            # Check if we should use cross-validation (5-fold)
            # DISABLED: K-fold has bugs with fine_tune (ES not copied per fold) and causes 5x training time
            # Set USE_PREDICTOR_CV=true to re-enable
            use_cross_validation = os.getenv("USE_PREDICTOR_CV", "false").lower() == "true"
            n_folds = 5
            
            # Check feature flag for proper CV (only for new training, not resuming)
            use_proper_cv = (
                PROPER_CV_AVAILABLE and
                not resume_from_predictor and
                predictor_base is not None and
                os.getenv("USE_PROPER_CV", "true").lower() == "true"
            )
            
            if use_cross_validation and len(train_df) >= n_folds:
                if use_proper_cv:
                    # PROPER CROSS-VALIDATION: Train 5 independent predictors and select best
                    logger.info("="*100)
                    logger.info("✅ PROPER CV ENABLED: Training 5 independent predictors")
                    logger.info("   Set USE_PROPER_CV=false to use sequential CV (old behavior)")
                    logger.info("="*100)
                    
                    # Use proper CV function (creates predictors internally)
                    # Note: predictor_base and predictor_name are already set above
                    fsp = train_with_proper_cv(
                        embedding_space=es,
                        train_df=train_df,
                        args=args,
                        epochs=epochs,
                        batch_size=batch_size,
                        predictor_base=predictor_base,
                        predictor_name=predictor_name,
                        progress_callback=progress_callback,
                    )
                    
                    logger.info("="*80)
                    logger.info(f"✅ PROPER K-FOLD CROSS-VALIDATION COMPLETE")
                    logger.info("="*80)
                else:
                    # SEQUENTIAL CROSS-VALIDATION (old behavior): train one predictor across folds
                    from sklearn.model_selection import KFold
                    
                    logger.info("="*100)
                    logger.info("🔀 K-FOLD CROSS-VALIDATION (SEQUENTIAL): Training across 5 data folds")
                    logger.info(f"   Epochs specified: {epochs}")
                    logger.info("   Each fold continues from previous, ensuring predictor sees all data patterns")
                    if PROPER_CV_AVAILABLE:
                        logger.info("   💡 Set USE_PROPER_CV=true to train 5 independent predictors and select best")
                    logger.info("="*100)
                    
                    # Each fold gets the FULL epoch count (not divided)
                    epochs_per_fold = epochs
                    logger.info(f"📊 Training plan: {epochs_per_fold} epochs per fold × {n_folds} folds = {epochs_per_fold * n_folds} total epochs")
                    
                    # K-Fold splitter (shuffle for randomness, fixed seed for reproducibility)
                    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
                    
                    # Track total epochs trained across all folds
                    total_epochs_trained = 0
                    
                    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(train_df)):
                        logger.info("="*80)
                        logger.info(f"🔀 FOLD {fold_idx + 1}/{n_folds}: Training on {len(train_idx)} rows, validating on {len(val_idx)} rows")
                        if fold_idx == 0:
                            logger.info(f"   Starting fresh training")
                        else:
                            logger.info(f"   Continuing from fold {fold_idx}")
                        logger.info("="*80)
                        
                        # Create fold-specific train/val data
                        fold_train_df = train_df.iloc[train_idx].copy().reset_index(drop=True)
                        fold_val_df = train_df.iloc[val_idx].copy().reset_index(drop=True)
                        
                        # Update train_df for this fold (codecs already set up from full dataset prep)
                        # This allows the predictor to use fold-specific training data while keeping
                        # the same codec structure (all classes from full dataset)
                        logger.info(f"   Updating train_df for fold {fold_idx + 1}...")
                        fsp.train_df = fold_train_df
                        logger.info(f"   ✅ Train_df updated: {len(fold_train_df)} rows for fold {fold_idx + 1}")
                        
                        # Train this fold (continues from previous fold's state)
                        logger.info(f"🏋️  Training fold {fold_idx + 1} for {epochs_per_fold} epochs...")
                        logger.info(f"🏋️  FINE_TUNE SETTING: {args.fine_tune} ({'ENABLED - training encoder + predictor' if args.fine_tune else 'DISABLED - encoder frozen, only predictor trains'})")
                        
                        # Include fold number in sp_identifier for dump filenames
                        fold_sp_identifier = f"{predictor_name}_fold{fold_idx + 1}"
                        
                        # Set fold context for log prefix [e=fN-NNN]
                        current_fold_ctx.set(fold_idx + 1)
                        
                        try:
                            # Create validation DataFrame for this fold
                            # CRITICAL: Disable BF16 for single predictor training to match local QA results
                            # Local test (test_credit_full_dataset.py) explicitly sets use_bf16=False and gets better results
                            # BF16 can cause numerical instability issues in predictor training
                            asyncio.run(fsp.train(
                                n_epochs=epochs_per_fold,
                                batch_size=batch_size,
                                fine_tune=args.fine_tune,
                                val_df=fold_val_df,  # Use fold-specific validation set
                                optimizer_params={"lr": args.learning_rate},
                                val_pos_label=args.positive_label,
                                print_callback=progress_callback,
                                print_progress_step=10,
                                job_id=args.job_id,
                                sp_identifier=fold_sp_identifier,  # Include fold # in dump filenames
                                use_bf16=False,  # CRITICAL: Disable BF16 to match local QA results (prevents numerical instability)
                            ))
                        finally:
                            # Clear fold context after training
                            current_fold_ctx.set(None)
                        
                        # Update total epochs trained
                        total_epochs_trained += epochs_per_fold
                        
                        logger.info(f"✅ Fold {fold_idx + 1} completed (total epochs so far: {total_epochs_trained})")
                    
                    logger.info("="*80)
                    logger.info(f"✅ K-FOLD CROSS-VALIDATION COMPLETE: Predictor trained on all {len(train_df)} rows across {n_folds} different splits")
                    logger.info(f"   Total epochs trained: {total_epochs_trained}")
                    logger.info("="*80)
            else:
                # Standard training (no cross-validation)
                if not use_cross_validation:
                    logger.info("📊 K-fold CV disabled (set USE_PREDICTOR_CV=true to enable)")
                elif len(train_df) < n_folds:
                    logger.info(f"⚠️  Dataset too small ({len(train_df)} rows) for {n_folds}-fold CV. Using standard training.")
                
                # ========================================
                # PRE-TRAINING EMBEDDING QUALITY CHECK
                # ========================================
                logger.info("")
                logger.info("=" * 100)
                logger.info("🔍 PRE-TRAINING EMBEDDING QUALITY CHECK")
                logger.info("=" * 100)
                logger.info("Analyzing embedding space quality before starting predictor training...")
                logger.info("This helps diagnose potential training issues early.")
                logger.info("")
                
                try:
                    # Sample records for quality check (limit to 200 for speed)
                    sample_size = min(200, len(train_df))
                    sample_df = train_df.sample(n=sample_size, random_state=42) if len(train_df) > sample_size else train_df
                    sample_records = sample_df.to_dict('records')
                    
                    # Get embeddings for sample
                    # torch is already imported at top of file - don't import here (causes UnboundLocalError)
                    embeddings_list = []
                    labels_list = []
                    
                    logger.info(f"Computing embeddings for {len(sample_records)} sample records...")
                    
                    for record in sample_records:
                        try:
                            # Get embedding
                            embedding = es.encoder(record)
                            embeddings_list.append(embedding)
                            
                            # Get label if target column present
                            if args.target_column in record:
                                labels_list.append(record[args.target_column])
                        except Exception as e:
                            logger.debug(f"Failed to encode record: {e}")
                            continue
                    
                    if len(embeddings_list) < 10:
                        logger.warning("⚠️  Too few valid embeddings, skipping quality check")
                    else:
                        # Stack embeddings
                        embeddings_tensor = torch.stack(embeddings_list)
                        
                        # Compute quality metrics
                        from featrix.neural.embedding_quality import compute_embedding_quality_metrics
                        quality_metrics = compute_embedding_quality_metrics(
                            embeddings=embeddings_tensor,
                            labels=labels_list if labels_list else None,
                            metadata={"n_samples": len(embeddings_list)}
                        )
                        
                        # Log results
                        overall_score = quality_metrics.get('overall_score', 0.0)
                        separation_score = quality_metrics.get('separation_score', 0.0)
                        clustering_score = quality_metrics.get('clustering_score', 0.0)
                        
                        logger.info(f"📊 Embedding Quality Metrics:")
                        logger.info(f"   Overall Score:    {overall_score:.3f} / 1.0")
                        logger.info(f"   Separation Score: {separation_score:.3f} / 1.0")
                        logger.info(f"   Clustering Score: {clustering_score:.3f} / 1.0")
                        
                        # Get detailed metrics
                        detailed = quality_metrics.get('detailed_metrics', {})
                        
                        # Check for collapse/clumping
                        clustering_details = detailed.get('clustering', {})
                        spread_std = clustering_details.get('spread_std', 0.0)
                        pairwise_dist_mean = clustering_details.get('pairwise_distance_mean', 0.0)
                        
                        logger.info(f"   Spread (std):     {spread_std:.3f}")
                        logger.info(f"   Avg Distance:     {pairwise_dist_mean:.3f}")
                        
                        # CLASS SEPARATION ANALYSIS (YAY vs NAY)
                        # Only if we have labels and it's a classification task
                        if labels_list and args.target_column_type == "set" and len(set(labels_list)) >= 2:
                            logger.info("")
                            logger.info("=" * 80)
                            logger.info("🎯 CLASS SEPARATION ANALYSIS")
                            logger.info("=" * 80)
                            
                            try:
                                import numpy as np
                                from scipy.spatial.distance import euclidean, cdist
                                
                                embeddings_np = embeddings_tensor.detach().cpu().numpy()
                                labels_array = np.array(labels_list)
                                unique_labels = list(set(labels_list))
                                
                                logger.info(f"Target column: {args.target_column}")
                                logger.info(f"Classes found: {unique_labels}")
                                logger.info(f"Sample distribution:")
                                for label in unique_labels:
                                    count = (labels_array == label).sum()
                                    pct = count / len(labels_array) * 100
                                    logger.info(f"   {label}: {count} samples ({pct:.1f}%)")
                                logger.info("")
                                
                                # Compute per-class centroids and spreads
                                class_info = {}
                                for label in unique_labels:
                                    class_mask = labels_array == label
                                    class_embeddings = embeddings_np[class_mask]
                                    
                                    if len(class_embeddings) > 0:
                                        centroid = class_embeddings.mean(axis=0)
                                        
                                        # Intra-class spread (avg pairwise distance within class)
                                        if len(class_embeddings) > 1:
                                            pairwise_dists = cdist(class_embeddings, class_embeddings, metric='euclidean')
                                            # Get upper triangle (exclude diagonal and duplicates)
                                            upper_tri = np.triu_indices_from(pairwise_dists, k=1)
                                            intra_spread = pairwise_dists[upper_tri].mean()
                                        else:
                                            intra_spread = 0.0
                                        
                                        class_info[label] = {
                                            'centroid': centroid,
                                            'spread': intra_spread,
                                            'count': len(class_embeddings)
                                        }
                                
                                # Compute inter-class distances (all pairs)
                                logger.info("📏 Inter-Class Distances (centroid to centroid):")
                                inter_class_distances = []
                                for i, label1 in enumerate(unique_labels):
                                    for label2 in unique_labels[i+1:]:
                                        if label1 in class_info and label2 in class_info:
                                            dist = euclidean(class_info[label1]['centroid'], class_info[label2]['centroid'])
                                            inter_class_distances.append(dist)
                                            logger.info(f"   {label1} ↔ {label2}: {dist:.3f}")
                                
                                avg_inter_class = np.mean(inter_class_distances) if inter_class_distances else 0.0
                                
                                # Compute average intra-class spread
                                logger.info("")
                                logger.info("📊 Intra-Class Spread (avg within-class distance):")
                                intra_spreads = []
                                for label, info in class_info.items():
                                    logger.info(f"   {label}: {info['spread']:.3f}")
                                    if info['spread'] > 0:
                                        intra_spreads.append(info['spread'])
                                
                                avg_intra_class = np.mean(intra_spreads) if intra_spreads else 0.0
                                
                                # SEPARATION RATIO - The key metric!
                                if avg_intra_class > 0:
                                    separation_ratio = avg_inter_class / avg_intra_class
                                else:
                                    separation_ratio = float('inf') if avg_inter_class > 0 else 0.0
                                
                                logger.info("")
                                logger.info("🎯 SEPARATION METRICS:")
                                logger.info(f"   Avg Inter-Class Distance: {avg_inter_class:.3f}")
                                logger.info(f"   Avg Intra-Class Spread:   {avg_intra_class:.3f}")
                                logger.info(f"   Separation Ratio:         {separation_ratio:.2f}")
                                logger.info("")
                                
                                # DIAGNOSIS AND RECOMMENDATIONS
                                if separation_ratio < 0.5:
                                    logger.error("🚨 CRITICAL: Classes are COMPLETELY OVERLAPPING")
                                    logger.error("   The embedding space cannot distinguish between classes")
                                    logger.error("   Inter-class distance is SMALLER than within-class spread!")
                                    logger.error("")
                                    logger.error("   PREDICTOR TRAINING WILL FAIL regardless of hyperparameters")
                                    logger.error("")
                                    logger.error("   REQUIRED ACTIONS:")
                                    logger.error("   1. Re-train embedding space with MORE EPOCHS")
                                    logger.error("   2. Check ES training converged properly (review ES logs)")
                                    logger.error("   3. Verify training data has discriminative features")
                                    logger.error("   4. Consider different/additional features")
                                    logger.error("")
                                    logger.error("   Proceeding anyway, but expect poor results...")
                                    
                                elif separation_ratio < 1.0:
                                    logger.warning("⚠️  WARNING: Classes are POORLY SEPARATED")
                                    logger.warning(f"   Separation ratio {separation_ratio:.2f} is below minimum threshold (1.0)")
                                    logger.warning("   Classes overlap significantly - predictor will struggle")
                                    logger.warning("")
                                    logger.warning("   RECOMMENDATIONS:")
                                    logger.warning("   1. DISABLE FINE-TUNING to preserve existing separation")
                                    logger.warning("      (fine-tuning may destroy what little separation exists)")
                                    logger.warning("   2. Use class weights to handle imbalance")
                                    logger.warning("   3. Consider re-training ES with more epochs")
                                    logger.warning("   4. Review ES training - may have stopped too early")
                                    logger.warning("")
                                    
                                    # Auto-recommendation: disable fine-tuning
                                    if args.fine_tune:
                                        logger.warning("   💡 CONSIDER: Set fine_tune=False for this training")
                                        logger.warning("      (Current setting: fine_tune=True)")
                                    
                                elif separation_ratio < 2.0:
                                    logger.info("✅ Classes have MODERATE separation")
                                    logger.info(f"   Separation ratio {separation_ratio:.2f} is acceptable")
                                    logger.info("   Training should work but may require careful tuning")
                                    logger.info("")
                                    logger.info("   Tips for best results:")
                                    logger.info("   - Start with fine-tuning disabled if embeddings are marginal")
                                    logger.info("   - Use class weights for imbalanced data")
                                    logger.info("   - Monitor training health metrics closely")
                                    
                                elif separation_ratio < 5.0:
                                    logger.info("✅ Classes are WELL SEPARATED")
                                    logger.info(f"   Separation ratio {separation_ratio:.2f} is good")
                                    logger.info("   Embeddings have clear class structure")
                                    logger.info("   Training should proceed smoothly")
                                    
                                else:
                                    logger.info("✅ Classes are EXCELLENTLY SEPARATED")
                                    logger.info(f"   Separation ratio {separation_ratio:.2f} is excellent")
                                    logger.info("   Embedding space has very clear class boundaries")
                                    logger.info("   Predictor should learn quickly and effectively")
                                
                                logger.info("=" * 80)
                                
                            except Exception as e:
                                logger.warning(f"⚠️  Class separation analysis failed: {e}")
                                logger.debug(traceback.format_exc())
                        
                        # Assess quality and provide recommendations
                        logger.info("")
                        if overall_score < 0.3:
                            logger.error("🚨 CRITICAL: Embedding space quality is VERY POOR")
                            logger.error("   Embeddings appear collapsed/clumped - predictor training will likely fail")
                            logger.error("   RECOMMENDATIONS:")
                            logger.error("   1. Re-train embedding space with more epochs")
                            logger.error("   2. Check if ES training converged properly")
                            logger.error("   3. Verify ES training data quality")
                            logger.error("   4. Consider disabling fine-tuning to preserve what quality exists")
                        elif overall_score < 0.5:
                            logger.warning("⚠️  WARNING: Embedding space quality is LOW")
                            logger.warning("   Predictor may struggle to learn effectively")
                            logger.warning("   RECOMMENDATIONS:")
                            logger.warning("   1. Review ES training logs for issues")
                            logger.warning("   2. Consider fine-tuning disabled to avoid destroying embeddings further")
                        elif overall_score < 0.7:
                            logger.info("✅ Embedding quality is ACCEPTABLE")
                            logger.info("   Training should proceed normally")
                        else:
                            logger.info("✅ Embedding quality is GOOD")
                            logger.info("   Embeddings are well-separated and diverse")
                        
                        logger.info("")
                        
                except Exception as e:
                    logger.warning(f"⚠️  Embedding quality check failed: {e}")
                    logger.debug(traceback.format_exc())
                
                logger.info("=" * 100)
                logger.info("")
                
                logger.info("="*100)
                logger.info("🏋️ ABOUT TO START TRAINING by calling fsp.train()")
                
                # AUTOMATIC LEARNING RATE SELECTION
                # Client doesn't need to specify LR - we auto-select based on fine_tune mode
                if args.learning_rate is None or args.learning_rate == 'auto':
                    if args.fine_tune:
                        # Fine-tuning: Use very low LR to protect pre-trained embeddings
                        training_lr = 1e-5  # 0.00001
                        logger.info(f"🤖 AUTO LR SELECTION (fine_tune=True): {training_lr:.6e}")
                        logger.info(f"   Reason: Fine-tuning needs gentle updates to preserve embeddings")
                    else:
                        # Standard training: Use moderate LR for predictor head only
                        training_lr = 1e-3  # 0.001
                        logger.info(f"🤖 AUTO LR SELECTION (fine_tune=False): {training_lr:.6e}")
                        logger.info(f"   Reason: Training predictor only (encoder frozen)")
                elif isinstance(args.learning_rate, (int, float)):
                    # Manual LR specified - respect it but adjust if fine-tuning
                    if args.fine_tune:
                        # Reduce LR by 100x for fine-tuning
                        training_lr = float(args.learning_rate) / 100.0
                        logger.info(f"🔧 FINE-TUNING ENABLED: Reducing manual LR by 100x")
                        logger.info(f"   Original LR: {args.learning_rate:.6e}")
                        logger.info(f"   Fine-tune LR: {training_lr:.6e} (100x lower)")
                        logger.info(f"   Reason: Pre-trained embeddings need gentle updates to avoid collapse")
                    else:
                        training_lr = float(args.learning_rate)
                        logger.info(f"📌 Using manual LR: {training_lr:.6e}")
                else:
                    # Fallback (shouldn't happen with proper validation)
                    training_lr = 1e-3 if not args.fine_tune else 1e-5
                    logger.warning(f"⚠️  Invalid learning_rate value: {args.learning_rate}, using fallback: {training_lr:.6e}")
                
                # ============================================================================
                # COMPREHENSIVE CONFIGURATION SUMMARY (FOR COMPARISON: LOCAL vs API)
                # ============================================================================
                logger.info("")
                logger.info("=" * 100)
                logger.info("📋 SINGLE PREDICTOR TRAINING CONFIGURATION SUMMARY")
                logger.info("=" * 100)
                logger.info("")
                logger.info("🔧 ARCHITECTURE:")
                logger.info(f"   • n_hidden_layers: {n_hidden_layers}")
                logger.info(f"   • d_hidden: {d_hidden if d_hidden is not None else 'N/A (linear)'}")
                logger.info(f"   • d_model (ES): {es.d_model}")
                logger.info(f"   • dropout: {dropout}")
                logger.info(f"   • batch_norm: {use_batch_norm}")
                logger.info(f"   • residual: {use_residual}")
                logger.info("")
                logger.info("⚙️  TRAINING PARAMETERS:")
                logger.info(f"   • n_epochs: {epochs}")
                logger.info(f"   • batch_size: {batch_size}")
                logger.info(f"   • learning_rate: {training_lr:.6e}")
                logger.info(f"   • fine_tune: {args.fine_tune} ({'ENABLED - encoder + predictor' if args.fine_tune else 'DISABLED - predictor only'})")
                logger.info(f"   • use_bf16: False (EXPLICITLY DISABLED - matches local QA)")
                logger.info("")
                logger.info("🎯 TARGET CONFIGURATION:")
                logger.info(f"   • target_column: {args.target_column}")
                logger.info(f"   • target_column_type: {args.target_column_type}")
                if args.positive_label:
                    logger.info(f"   • positive_label: {args.positive_label}")
                logger.info(f"   • use_class_weights: {args.use_class_weights}")
                logger.info(f"   • loss_type: {args.loss_type}")
                logger.info(f"   • best_metric_preference: {args.best_metric_preference or 'auto'}")
                logger.info("")
                logger.info("📊 DATASET:")
                logger.info(f"   • training_rows: {len(train_df)}")
                logger.info(f"   • columns: {len(train_df.columns)}")
                logger.info("")
                logger.info("=" * 100)
                logger.info("")
                
                # Send initial progress update (0% but status = "starting")
                if args.job_queue and args.job_id:
                    try:
                        from redis_job_progress import get_redis_job_progress
                        redis_progress = get_redis_job_progress()
                        if redis_progress.redis_available:
                            redis_progress.update_progress(
                                job_type=args.job_queue,
                                job_id=args.job_id,
                                progress=0.0,
                                current_epoch=0,
                                current_loss=None,
                                validation_loss=None,
                                metrics={},
                                time_now=None,
                            )
                        # Also update job data
                        from lib.job_manager import load_job, save_job
                        job_data = load_job(args.job_id)
                        if job_data:
                            job_data['progress'] = 0.0
                            job_data['current_epoch'] = 0
                            session_id = job_data.get('session_id') or args.session_id
                            job_type = job_data.get('job_type') or args.job_queue
                            save_job(args.job_id, job_data, session_id, job_type)
                    except Exception as init_progress_err:
                        logger.debug(f"Failed to send initial progress update: {init_progress_err}")
                
                # CRITICAL: Disable BF16 for single predictor training to match local QA results
                # Local test (test_credit_full_dataset.py) explicitly sets use_bf16=False and gets better results
                # BF16 can cause numerical instability issues in predictor training
                asyncio.run(fsp.train(
                    n_epochs=epochs,
                    batch_size=batch_size,
                    fine_tune=args.fine_tune,
                    optimizer_params={"lr": training_lr},
                    val_pos_label=args.positive_label,  # Pass positive label for binary classification
                    best_metric_preference=args.best_metric_preference,  # Pass metric preference for best model selection
                    print_callback=progress_callback,
                    print_progress_step=10,
                    job_id=args.job_id,  # Pass job_id for ABORT/FINISH detection
                    use_bf16=False,  # CRITICAL: Disable BF16 to match local QA results (prevents numerical instability)
                ))
            
            logger.info("@@@ Single predictor training completed successfully! @@@")
            worked = True
            
            # Load session to get model_id before saving predictor
            model_id = None
            session_id = args.session_id or args.job_id
            session = None
            if session_id:
                try:
                    from lib.session_manager import load_session
                    session = load_session(session_id)
                    if session:
                        # Check session metadata first
                        metadata = session.get("metadata", {})
                        if isinstance(metadata, dict):
                            model_id = metadata.get("model_id")
                        
                        # Fallback to session name if it looks like a model_id
                        if not model_id:
                            session_name = session.get("name", "")
                            if session_name and session_name.startswith("dot_model_"):
                                model_id = session_name
                except Exception as e:
                    logger.warning(f"⚠️  Could not load session to get model_id: {e}")
            
            # Check if simple linear layer performed poorly and log recommendation
            if n_hidden_layers == 0 and hasattr(fsp, 'training_metrics') and fsp.training_metrics:
                metrics = fsp.training_metrics
                accuracy = metrics.get('accuracy', 0)
                f1 = metrics.get('f1', 0)
                val_loss = metrics.get('validation_loss', float('inf'))
                
                # Detect poor performance indicators
                poor_performance = False
                reasons = []
                
                if accuracy < 0.5:  # Less than 50% accuracy
                    poor_performance = True
                    reasons.append(f"Low accuracy ({accuracy:.2%})")
                
                if f1 < 0.3:  # F1 score below 0.3
                    poor_performance = True
                    reasons.append(f"Low F1 score ({f1:.3f})")
                
                if val_loss > 1.0:  # High validation loss
                    poor_performance = True
                    reasons.append(f"High validation loss ({val_loss:.3f})")
                
                if poor_performance:
                    logger.warning("=" * 80)
                    logger.warning("⚠️  SIMPLE LINEAR LAYER PERFORMANCE WARNING")
                    logger.warning("=" * 80)
                    logger.warning(f"   The simple Linear(d_model, d_out) architecture may be insufficient.")
                    logger.warning(f"   Performance indicators:")
                    for reason in reasons:
                        logger.warning(f"     • {reason}")
                    logger.warning(f"")
                    logger.warning(f"   💡 RECOMMENDATION:")
                    logger.warning(f"     Consider retraining with a hidden layer:")
                    logger.warning(f"     • Architecture: Linear(d_model→64) → GELU → Dropout(0.2) → Linear(64→d_out)")
                    logger.warning(f"     • This adds nonlinearity and may improve performance")
                    logger.warning(f"     • Small datasets (<1000 rows) can still benefit from 1 hidden layer")
                    logger.warning("=" * 80)
                    
                    # Store recommendation in training metrics for later reference
                    if not hasattr(metrics, '__dict__'):
                        metrics = dict(metrics) if isinstance(metrics, dict) else {}
                    metrics['architecture_recommendation'] = {
                        "current_architecture": "Linear(d_model, d_out)",
                        "recommended_architecture": "Linear(d_model→64) → GELU → Dropout(0.2) → Linear(64→d_out)",
                        "reason": "Poor performance detected with simple linear layer",
                        "indicators": reasons,
                        "accuracy": accuracy,
                        "f1": f1,
                        "validation_loss": val_loss
                    }
            
            # Save the trained predictor with model_id
            write_single_predictor(fsp, ".", model_id=model_id)
            
            # Ensure best_single_predictor.pickle symlink exists (should already be created during training)
            # This is a fallback in case the symlink wasn't created during training
            try:
                import glob
                
                best_pickle_path = "best_single_predictor.pickle"
                
                # Check if symlink already exists
                if os.path.exists(best_pickle_path) or os.path.islink(best_pickle_path):
                    logger.info(f"✅ Best model symlink already exists: {best_pickle_path}")
                else:
                    # Find the best checkpoint files to create symlink
                    best_checkpoints = []
                    
                    # Look for best ROC-AUC checkpoint (new format)
                    roc_auc_patterns = glob.glob("*_best_single_predictor_auc_roc_*.pickle")
                    if roc_auc_patterns:
                        # Sort by modification time, newest first
                        roc_auc_patterns.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                        best_checkpoints.append(roc_auc_patterns[0])
                    
                    # Look for best PR-AUC checkpoint (new format)
                    pr_auc_patterns = glob.glob("*_best_single_predictor_auc_pr_*.pickle")
                    if pr_auc_patterns:
                        pr_auc_patterns.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                        best_checkpoints.append(pr_auc_patterns[0])
                    
                    # Look for best validation loss checkpoint (new format)
                    val_loss_patterns = glob.glob("*_best_single_predictor_valloss_*.pickle")
                    if val_loss_patterns:
                        val_loss_patterns.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                        best_checkpoints.append(val_loss_patterns[0])
                    
                    # Use the most recent best checkpoint (or single_predictor.pickle if no best checkpoint found)
                    best_checkpoint_source = None
                    if best_checkpoints:
                        # Use the most recently modified best checkpoint
                        best_checkpoints.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                        best_checkpoint_source = best_checkpoints[0]
                        logger.info(f"📋 Found best checkpoint: {best_checkpoint_source}")
                    elif os.path.exists("single_predictor.pickle"):
                        # Fallback to single_predictor.pickle (which should contain the best model)
                        best_checkpoint_source = "single_predictor.pickle"
                        logger.info(f"📋 Using single_predictor.pickle as best model")
                    
                    if best_checkpoint_source and os.path.exists(best_checkpoint_source):
                        # Create relative symlink
                        rel_checkpoint_path = os.path.relpath(best_checkpoint_source, ".")
                        os.symlink(rel_checkpoint_path, best_pickle_path)
                        logger.info(f"✅ Created best model symlink: {best_pickle_path} -> {os.path.basename(best_checkpoint_source)}")
                    else:
                        logger.warning(f"⚠️  Could not find best checkpoint to symlink - best model may not be available")
            except Exception as e:
                logger.warning(f"⚠️  Failed to create best_single_predictor.pickle symlink: {e}")
                logger.debug(traceback.format_exc())
                # Don't fail training if this fails
            
            # Mark training as complete in status metadata
            try:
                import glob
                # Find and update any training status files
                status_files = glob.glob("*_training_status.json")
                for status_file in status_files:
                    try:
                        with open(status_file, 'r') as f:
                            status = json.load(f)
                        status['is_training'] = False
                        status['completed_at'] = time.time()
                        status['final_epoch'] = status.get('epoch', epochs)
                        with open(status_file, 'w') as f:
                            json.dump(status, f, indent=2, default=str)
                        logger.info(f"✅ Marked training as complete in {status_file}")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to update training status file {status_file}: {e}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to mark training as complete: {e}")
            
            # Handle webhook callbacks if configured
            if args.webhooks:
                try:
                    logger.info("="*80)
                    logger.info("🔔 PROCESSING WEBHOOK CALLBACKS")
                    logger.info("="*80)
                    
                    from lib.webhook_helpers import (
                        call_s3_backup_webhook,
                        upload_file_to_s3_url,
                        call_model_id_update_webhook
                    )
                    from lib.session_manager import load_session
                    
                    # Get session to extract model_id and org_id (reuse if already loaded)
                    if not model_id and session_id:
                        try:
                            if not session:
                                session = load_session(session_id)
                            # Try to extract model_id from session metadata or name
                            if session:
                                # Check session metadata first
                                metadata = session.get("metadata", {})
                                if isinstance(metadata, dict):
                                    model_id = metadata.get("model_id")
                                
                                # Fallback to session name if it looks like a model_id
                                if not model_id:
                                    session_name = session.get("name", "")
                                    if session_name and session_name.startswith("dot_model_"):
                                        model_id = session_name
                                
                                # If still no model_id, use session_id as fallback
                                if not model_id:
                                    model_id = session_id
                        except Exception as e:
                            logger.warning(f"⚠️  Could not load session for webhooks: {e}")
                            model_id = session_id
                    
                    if not model_id:
                        model_id = args.job_id or "unknown"
                    
                    org_id = args.webhooks.get("webhook_callback_secret")
                    if not org_id:
                        logger.warning("⚠️  No webhook_callback_secret provided, skipping webhooks")
                    else:
                        # Upload model assets to S3 if s3_backup_url is configured
                        s3_backup_url = args.webhooks.get("s3_backup_url")
                        if s3_backup_url:
                            logger.info("📤 Uploading model assets to S3...")
                            
                            # Upload single_predictor.pickle
                            predictor_path = Path(".") / "single_predictor.pickle"
                            if predictor_path.exists():
                                upload_result = call_s3_backup_webhook(
                                    webhook_url=s3_backup_url,
                                    model_id=model_id,
                                    org_id=org_id,
                                    file_name="single_predictor.pickle",
                                    content_type="application/octet-stream",
                                    webhook_secret=org_id
                                )
                                
                                if upload_result and upload_result.get("upload_url"):
                                    if upload_file_to_s3_url(predictor_path, upload_result["upload_url"]):
                                        logger.info(f"✅ Uploaded single_predictor.pickle to {upload_result.get('storage_path', 'S3')}")
                            
                            # Upload training_metrics.json
                            metrics_path = Path(".") / "training_metrics.json"
                            if metrics_path.exists():
                                upload_result = call_s3_backup_webhook(
                                    webhook_url=s3_backup_url,
                                    model_id=model_id,
                                    org_id=org_id,
                                    file_name="training_metrics.json",
                                    content_type="application/json",
                                    webhook_secret=org_id
                                )
                                
                                if upload_result and upload_result.get("upload_url"):
                                    if upload_file_to_s3_url(metrics_path, upload_result["upload_url"]):
                                        logger.info(f"✅ Uploaded training_metrics.json to {upload_result.get('storage_path', 'S3')}")
                        else:
                            logger.info("ℹ️  No s3_backup_url configured, skipping S3 upload")
                        
                        # Call model_id_update webhook when training completes successfully
                        model_id_update_url = args.webhooks.get("model_id_update_url")
                        if model_id_update_url:
                            # Extract metrics from the trained predictor
                            metrics = {}
                            if hasattr(fsp, 'training_metrics') and fsp.training_metrics:
                                metrics = fsp.training_metrics
                            
                            # Get featrix IDs
                            featrix_model_id = args.job_id or "unknown"
                            
                            # CRITICAL: Use the session_id (which should be the NEW predictor session ID)
                            # NOT the foundation_model_id. The session_id comes from args.session_id
                            # which is set when the job is created with the correct new session ID.
                            featrix_session_id = session_id or "unknown"
                            
                            # Defensive check: ensure we're not accidentally using foundation_model_id
                            foundation_model_id = None
                            if session:
                                foundation_model_id = session.get("foundation_model_id")
                                if foundation_model_id and featrix_session_id == foundation_model_id:
                                    logger.error(f"❌ CRITICAL BUG: featrix_session_id matches foundation_model_id!")
                                    logger.error(f"   This means the webhook would send the foundation's ID instead of the new session ID")
                                    logger.error(f"   session_id from args: {args.session_id}")
                                    logger.error(f"   job_id: {args.job_id}")
                                    logger.error(f"   featrix_session_id: {featrix_session_id}")
                                    logger.error(f"   foundation_model_id: {foundation_model_id}")
                                    # This should never happen, but if it does, log it and use session_id anyway
                            
                            logger.info(f"📤 Webhook sending: featrix_session_id={featrix_session_id} (foundation={foundation_model_id})")
                            
                            featrix_es_id = None
                            if session:
                                es_path = session.get("embedding_space")
                                if es_path:
                                    # Try to extract ES ID from path or session
                                    featrix_es_id = Path(es_path).stem if es_path else None
                            
                            call_model_id_update_webhook(
                                webhook_url=model_id_update_url,
                                model_id=model_id,
                                org_id=org_id,
                                featrix_model_id=featrix_model_id,
                                featrix_session_id=featrix_session_id,
                                featrix_es_id=featrix_es_id,
                                status="succeeded",
                                metrics=metrics,
                                webhook_secret=org_id
                            )
                        else:
                            logger.info("ℹ️  No model_id_update_url configured, skipping completion webhook")
                    
                    logger.info("="*80)
                    
                    # Log training completion event
                    if session_id:
                        try:
                            from event_log import log_training_event
                            metrics_dict = {}
                            if hasattr(fsp, 'training_metrics') and fsp.training_metrics:
                                metrics_dict = fsp.training_metrics
                            
                            log_training_event(
                                session_id=session_id,
                                event_name="training_completed",
                                predictor_id=args.job_id,
                                additional_info={
                                    "target_column": args.target_column,
                                    "target_column_type": args.target_column_type,
                                    "metrics": metrics_dict,
                                    "status": "succeeded"
                                }
                            )
                        except Exception as e:
                            logger.debug(f"Failed to log training completion event: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing webhooks: {e}")
                    logger.debug(f"   Full traceback: {traceback.format_exc()}")
                    # Don't fail training if webhooks fail
            
            # Post training data to monitor.featrix.com
            training_end_time = datetime.now()
            try:
                logger.info("="*80)
                logger.info("📊 POSTING SP TRAINING DATA TO MONITOR")
                logger.info("="*80)
                
                from training_monitor import collect_sp_training_data, post_training_data
                
                # SP training creates an internal validation split (20% by default)
                # We don't have direct access to the split after training, so we'll use train_df
                # and note in metadata that SP uses internal validation
                # The actual validation size is approximately 20% of train_df
                val_df = train_df  # SP uses internal validation split, approximate size is 20% of train_df
                
                # Get session_id from args (prefer session_id, fallback to job_id)
                session_id = getattr(args, 'session_id', None) or getattr(args, 'job_id', None)
                
                # Build optimal_params from embedding_space AND single predictor config
                optimal_params = {
                    "d_model": getattr(es, 'd_model', None),
                    "n_transformer_layers": getattr(es, 'n_transformer_layers', None),
                    "n_attention_heads": getattr(es, 'n_attention_heads', None),
                    # Add SP hyperparameters (from predictor or args)
                    "n_hidden_layers": getattr(fsp.predictor, 'n_hidden_layers', None) if hasattr(fsp, 'predictor') else None,
                    "d_hidden": getattr(fsp.predictor, 'd_hidden', None) if hasattr(fsp, 'predictor') else None,
                    "dropout": getattr(fsp.predictor, 'dropout', None) if hasattr(fsp, 'predictor') else None,
                    "fine_tune": args.fine_tune,
                }
                
                # Include dataset_hash and monitor config in metadata if available
                try:
                    from featrix_monitor import generate_dataset_hash
                    dataset_hash = generate_dataset_hash(train_df)
                    # Will be added to metadata inside collect_sp_training_data
                except:
                    dataset_hash = None
                
                training_data = collect_sp_training_data(
                    single_predictor=fsp,
                    embedding_space=es,
                    train_df=train_df,
                    val_df=val_df,
                    target_column=args.target_column,
                    target_column_type=args.target_column_type,
                    training_start_time=training_start_time,
                    training_end_time=training_end_time,
                    epochs=epochs,
                    batch_size=batch_size,
                    learning_rate=args.learning_rate,
                    customer_id=getattr(args, 'customer_id', None),
                    remote_hostname=getattr(args, 'remote_hostname', None),
                    s3_path=getattr(args, 's3_path', None),
                    session_id=session_id,
                    deployment_id=getattr(args, 'deployment_id', None),
                    optimal_params=optimal_params,
                )
                
                # Add dataset_hash to training_data if we got it
                if dataset_hash:
                    training_data['metadata']['dataset_hash'] = dataset_hash
                    logger.info(f"📊 Including dataset_hash in training metadata: {dataset_hash}")
                
                # Add monitor config parameters to metadata and network_architecture if available
                if hasattr(args, 'monitor_config') and args.monitor_config:
                    logger.info(f"📊 Including monitor config in training metadata")
                    for key, value in args.monitor_config.items():
                        if key not in ['status', 'dataset_hash']:
                            training_data['metadata'][key] = value
                            if 'network_architecture' not in training_data:
                                training_data['network_architecture'] = {}
                            training_data['network_architecture'][key] = value
                
                post_training_data(training_data)
                
                logger.info("="*80)
            except Exception as e:
                logger.warning(f"⚠️  Failed to post SP training data to monitor: {e}")
                logger.debug(f"   Full traceback: {traceback.format_exc()}")
                # Don't fail training if monitor posting fails
            
            # Save comprehensive training metadata JSON
            try:
                logger.info("="*80)
                logger.info("📝 SAVING COMPREHENSIVE TRAINING METADATA")
                logger.info("="*80)
                
                metadata_file = save_predictor_metadata(
                    session_id=args.session_id or args.job_id or "no_session",
                    target_column=args.target_column,
                    target_column_type=args.target_column_type,
                    epochs=epochs,
                    training_response=None,  # Could add initial API response if available
                    csv_file=args.input_file,
                    client=None,  # No API client available in local training
                    training_start_time=training_start_time,
                    fsp=fsp  # Pass the trained predictor for local model info
                )
                
                if metadata_file:
                    logger.info(f"✅ Training metadata successfully saved to: {metadata_file}")
                else:
                    logger.warning("⚠️ Failed to save training metadata")
                    
                logger.info("="*80)
            except Exception as e:
                logger.error(f"❌ Error saving training metadata: {e}")
                traceback.print_exc()
                # Don't fail the training if metadata save fails
            
            # Save training metrics
            metrics_path = "./training_metrics.json"
            with open(metrics_path, "w") as f:
                json.dump({
                    "training_info": getattr(fsp, 'training_info', []),
                    "target_column": args.target_column,
                    "target_column_type": args.target_column_type,
                    "final_metrics": getattr(fsp, 'training_metrics', {}),
                    "class_distribution": getattr(fsp, 'class_distribution', {}),  # Include validation set distribution
                    "args": args.model_dump()
                }, f, indent=2, default=str)
            
            logger.info(f"Training metrics saved to {metrics_path}")
            
            training_worked = True
            break
            
        except EarlyStoppingException as e:
            # EarlyStoppingException is NOT a failure - it's a successful early termination
            # The model has converged and the best model has been saved
            logger.info(f"✅ Training completed early due to convergence: {e}")
            logger.info(f"   Job ID: {args.job_id}")
            logger.info(f"   Output Dir: {os.getcwd()}")
            logger.info(f"   Target Column: {args.target_column}")
            if e.best_epoch is not None and e.best_metric is not None:
                logger.info(f"   Best model saved at epoch {e.best_epoch} with metric {e.best_metric:.4f}")
            logger.info(f"   Early stopping is normal and indicates successful convergence")
            
            # This is a success - continue with normal completion
            training_worked = True
            break
            
        except TrainingFailureException as e:
            # TrainingFailureExceptions are actual training failures (not early stopping)
            # These are NOT batch size issues and should ABORT, not retry
            traceback.print_exc(file=sys.stdout)
            logger.error(f"❌ Training failed with {type(e).__name__}: {e}")
            logger.error(f"   Job ID: {args.job_id}")
            logger.error(f"   Output Dir: {os.getcwd()}")
            logger.error(f"   Target Column: {args.target_column}")
            logger.error(f"   Batch Size: {batch_size}")
            logger.error(f"   This is a convergence/training issue, NOT a batch size problem")
            logger.error(f"   ABORTING - not retrying with different batch sizes")
            
            # Post to Slack
            try:
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from slack import send_slack_message
                
                slack_msg = f"💥 **Single Predictor Training Failed (Convergence Issue)**\n"
                slack_msg += f"Target Column: {args.target_column}\n"
                slack_msg += f"Session ID: {args.session_id}\n"
                slack_msg += f"Job ID: {args.job_id}\n"
                slack_msg += f"Output Dir: {os.getcwd()}\n"
                slack_msg += f"Batch Size: {batch_size}\n"
                slack_msg += f"Exception: {type(e).__name__}: {str(e)}\n"
                slack_msg += f"Action: ABORTING - convergence issues can't be fixed by reducing batch size"
                
                send_slack_message(slack_msg)
                logger.info("✅ Slack notification sent")
            except Exception as slack_error:
                logger.warning(f"Failed to send Slack notification: {slack_error}")
            
            # Re-raise to abort training
            raise
        
        # NOTE: FeatrixRestartTrainingException is NOT caught here
        # It will propagate up to the train() method in single_predictor.py which handles restarts internally
        # This is correct because restart issues (dead gradients, etc.) need different LR, not different batch size
            
        except (AssertionError, TypeError, AttributeError, ValueError, RuntimeError, OSError) as e:
            # Non-Featrix exceptions - check if it's OOM (retryable) or other error (abort)
            error_msg = str(e).lower()
            error_type = type(e).__name__
            oom_indicators = [
                'out of memory',
                'cuda out of memory',
                'oom',
                'torch.outofmemoryerror',
                'cuda oom',
                'gpu memory',
                'memory allocation',
                'allocation failed'
            ]
            is_oom = any(indicator in error_msg for indicator in oom_indicators) or 'OutOfMemoryError' in error_type
            
            if is_oom:
                # OOM errors CAN be fixed by reducing batch size - RETRY
                dump_cuda_memory_usage(context=f"training loop (batch_size={batch_size})")
                logger.error("")
                logger.error("=" * 100)
                logger.error("🚫 OUT OF MEMORY (OOM) ERROR DETECTED")
                logger.error("=" * 100)
                logger.error(f"   Error Type: {error_type}")
                logger.error(f"   Error Message: {str(e)[:500]}")
                logger.error(f"   Batch Size: {batch_size}")
                logger.error("")
                
                if batch_size >= 16:  # Only retry if we can meaningfully reduce batch size
                    new_batch_size = int(batch_size / 2)
                    logger.error(f"   ⚠️  RETRYING with smaller batch size: {batch_size} → {new_batch_size}")
                    logger.error(f"   Smaller batch size = less GPU memory usage")
                    logger.error("=" * 100)
                    logger.error("")
                    
                    # Post to Slack
                    try:
                        from pathlib import Path
                        sys.path.insert(0, str(Path(__file__).parent.parent))
                        from slack import send_slack_message
                        
                        slack_msg = f"⚠️ **Single Predictor OOM Error (Retrying)**\n"
                        slack_msg += f"Target Column: {args.target_column}\n"
                        slack_msg += f"Session ID: {args.session_id}\n"
                        slack_msg += f"Job ID: {args.job_id}\n"
                        slack_msg += f"Output Dir: {os.getcwd()}\n"
                        slack_msg += f"Batch Size: {batch_size} → {new_batch_size}\n"
                        slack_msg += f"Exception: {type(e).__name__}: {str(e)[:200]}\n"
                        slack_msg += f"Action: Reducing batch size and retrying"
                        
                        send_slack_message(slack_msg)
                        logger.info("✅ Slack notification sent for OOM retry")
                    except Exception as slack_error:
                        logger.warning(f"Failed to send Slack notification: {slack_error}")
                    
                    # Reduce batch size and retry
                    batch_size = new_batch_size
                    logger.info(f"Reducing batch size to {batch_size} due to OOM error...")
                    continue  # Retry with smaller batch size
                else:
                    # Batch size already too small - can't reduce further
                    logger.error(f"   ⚠️  Batch size ({batch_size}) already at minimum - cannot reduce further")
                    logger.error(f"   Possible solutions:")
                    logger.error(f"   - Free up GPU memory (kill other processes)")
                    logger.error(f"   - Use a GPU with more memory")
                    logger.error(f"   - Reduce model size (d_model, n_layers, etc.)")
                    logger.error("=" * 100)
                    logger.error("")
                    
                    # Store OOM flag for job status update
                    e._is_oom = True
                    args._last_oom_error = True
                    args._last_error = str(e)
                    args._last_error_type = error_type
                    
                    # Post abort notification to Slack
                    try:
                        from pathlib import Path
                        sys.path.insert(0, str(Path(__file__).parent.parent))
                        from slack import send_slack_message
                        
                        slack_msg = f"💥 **Single Predictor OOM Error (ABORTING)**\n"
                        slack_msg += f"Target Column: {args.target_column}\n"
                        slack_msg += f"Session ID: {args.session_id}\n"
                        slack_msg += f"Job ID: {args.job_id}\n"
                        slack_msg += f"Output Dir: {os.getcwd()}\n"
                        slack_msg += f"Batch Size: {batch_size} (minimum reached)\n"
                        slack_msg += f"Exception: {type(e).__name__}: {str(e)[:200]}\n"
                        slack_msg += f"Action: ABORTING - batch size cannot be reduced further"
                        
                        send_slack_message(slack_msg)
                        logger.info("✅ Slack notification sent for OOM abort")
                    except Exception as slack_error:
                        logger.warning(f"Failed to send Slack notification: {slack_error}")
                    
                    traceback.print_exc(file=sys.stdout)
                    raise  # Abort - can't reduce batch size any further
            else:
                # Non-OOM error - abort immediately (not retryable with different batch sizes)
                traceback.print_exc(file=sys.stdout)
                logger.error(f"❌ Non-Featrix exception during training with batch_size {batch_size}: {type(e).__name__}: {e}")
                logger.error(f"   Job ID: {args.job_id}")
                logger.error(f"   Output Dir: {os.getcwd()}")
                logger.error(f"   Target Column: {args.target_column}")
                logger.error(f"   Aborting immediately - these errors are not retryable with different batch sizes")
                
                # Post exception to Slack
                try:
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent.parent))
                    from slack import send_slack_message
                    
                    slack_msg = f"💥 **Single Predictor Training Failed (Non-Featrix Exception)**\n"
                    slack_msg += f"Target Column: {args.target_column}\n"
                    slack_msg += f"Session ID: {args.session_id}\n"
                    slack_msg += f"Job ID: {args.job_id}\n"
                    slack_msg += f"Output Dir: {os.getcwd()}\n"
                    slack_msg += f"Batch Size: {batch_size}\n"
                    slack_msg += f"Exception: {type(e).__name__}: {str(e)}\n"
                    slack_msg += f"Action: Aborting - not retrying with different batch sizes"
                    
                    send_slack_message(slack_msg)
                    logger.info("✅ Slack notification sent for Single Predictor training failure")
                except Exception as slack_error:
                    logger.warning(f"Failed to send Slack notification: {slack_error}")
                
                # Re-raise to abort training
                raise
            
        except Exception as e:
            # Any other exception - also abort (not a Featrix exception)
            # Check if it's an OOM error
            error_msg = str(e).lower()
            error_type = type(e).__name__
            oom_indicators = [
                'out of memory',
                'cuda out of memory',
                'oom',
                'torch.outofmemoryerror',
                'cuda oom',
                'gpu memory',
                'memory allocation',
                'allocation failed'
            ]
            is_oom = any(indicator in error_msg for indicator in oom_indicators) or 'OutOfMemoryError' in error_type
            
            if is_oom:
                logger.error("")
                logger.error("=" * 100)
                logger.error("🚫 OUT OF MEMORY (OOM) ERROR DETECTED")
                logger.error("=" * 100)
                logger.error(f"   Error Type: {error_type}")
                logger.error(f"   Error Message: {str(e)[:500]}")
                logger.error(f"   Batch Size: {batch_size}")
                logger.error("")
                logger.error("   ⚠️  This job will NOT be automatically retried.")
                logger.error("   ⚠️  OOM errors indicate insufficient GPU/system memory.")
                logger.error("   ⚠️  Retrying would likely fail again with the same error.")
                logger.error("")
                logger.error("   Possible solutions:")
                logger.error("   - Reduce batch_size in training configuration")
                logger.error("   - Free up GPU memory (kill other processes)")
                logger.error("   - Use a GPU with more memory")
                logger.error("   - Reduce model size (d_model, n_layers, etc.)")
                logger.error("=" * 100)
                logger.error("")
                e._is_oom = True  # Store flag on exception object
                # Also store in args so it's accessible when setting job status
                args._last_oom_error = True
                args._last_error = str(e)
                args._last_error_type = error_type
            
            traceback.print_exc(file=sys.stdout)
            logger.error(f"❌ Unexpected exception during training with batch_size {batch_size}: {type(e).__name__}: {e}")
            logger.error(f"   Job ID: {args.job_id}")
            logger.error(f"   Output Dir: {os.getcwd()}")
            logger.error(f"   Target Column: {args.target_column}")
            logger.error(f"   Aborting immediately - not a Featrix exception, not retryable")
            
            # Post exception to Slack
            try:
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from slack import send_slack_message
                
                slack_msg = f"💥 **Single Predictor Training Failed (Unexpected Exception)**\n"
                slack_msg += f"Target Column: {args.target_column}\n"
                slack_msg += f"Session ID: {args.session_id}\n"
                slack_msg += f"Job ID: {args.job_id}\n"
                slack_msg += f"Output Dir: {os.getcwd()}\n"
                slack_msg += f"Batch Size: {batch_size}\n"
                slack_msg += f"Exception: {type(e).__name__}: {str(e)}\n"
                slack_msg += f"Action: Aborting - not retrying with different batch sizes"
                
                send_slack_message(slack_msg)
                logger.info("✅ Slack notification sent for Single Predictor training failure")
            except Exception as slack_error:
                logger.warning(f"Failed to send Slack notification: {slack_error}")
            
            # Re-raise to abort training
            raise
    
    if not worked:
        # Post training failure to Slack
        try:
            from pathlib import Path  # Import here to ensure it's available (defensive)
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from slack import send_slack_message
            
            slack_msg = f"💥 **Single Predictor Training Failed**\n"
            slack_msg += f"Target Column: {args.target_column}\n"
            slack_msg += f"Target Type: {args.target_column_type}\n"
            slack_msg += f"Session ID: {args.session_id}\n"
            slack_msg += f"Job ID: {args.job_id}\n"
            slack_msg += f"Output Dir: {os.getcwd()}\n"
            slack_msg += f"Reason: Training failed with all attempted batch sizes"
            
            send_slack_message(slack_msg)
            logger.info("✅ Slack notification sent for Single Predictor training failure")
        except Exception as slack_error:
            logger.warning(f"Failed to send Slack notification for failure: {slack_error}")
        
        # Set job status to FAILED before raising
        try:
            job_id = getattr(args, 'job_id', None)
            if job_id:
                from lib.job_manager import determine_failure_reason
                # Check if the last exception was an OOM error
                error_metadata = {}
                is_oom = getattr(args, '_last_oom_error', False)
                # Check if exception has OOM flag (stored in args by exception handler)
                if is_oom:
                    error_metadata['is_oom'] = True
                    error_metadata['oom_detected'] = True
                    if hasattr(args, '_last_error'):
                        error_metadata['error'] = args._last_error
                    if hasattr(args, '_last_error_type'):
                        error_metadata['error_type'] = args._last_error_type
                
                # Determine failure reason
                exception_type = getattr(args, '_last_error_type', None)
                exception_msg = getattr(args, '_last_error', None)
                failure_reason = determine_failure_reason(exception_type=exception_type, exception_msg=exception_msg, is_oom=is_oom)
                error_metadata['failure_reason'] = failure_reason
                
                logger.error(f"❌ Setting job {job_id} status to FAILED due to training failure")
                update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata=error_metadata if error_metadata else None)
            else:
                logger.warning(f"⚠️  Cannot set job status to FAILED: job_id not available")
        except Exception as status_err:
            logger.error(f"⚠️  Failed to set job status to FAILED: {status_err}")
        
        # Call failure webhook if configured
        if args.webhooks:
            try:
                from lib.webhook_helpers import call_model_id_update_webhook
                from lib.session_manager import load_session
                
                model_id_update_url = args.webhooks.get("model_id_update_url")
                if model_id_update_url:
                    org_id = args.webhooks.get("webhook_callback_secret")
                    if org_id:
                        session_id = args.session_id or args.job_id
                        session = None
                        model_id = None
                        
                        if session_id:
                            try:
                                session = load_session(session_id)
                                if session:
                                    metadata = session.get("metadata", {})
                                    if isinstance(metadata, dict):
                                        model_id = metadata.get("model_id")
                                    if not model_id:
                                        session_name = session.get("name", "")
                                        if session_name and session_name.startswith("dot_model_"):
                                            model_id = session_name
                                    if not model_id:
                                        model_id = session_id
                            except Exception:
                                model_id = session_id
                        
                        if not model_id:
                            model_id = args.job_id or "unknown"
                        
                        # CRITICAL: Use the session_id (which should be the NEW predictor session ID)
                        # NOT the foundation_model_id
                        featrix_session_id = session_id or "unknown"
                        
                        # Defensive check: ensure we're not accidentally using foundation_model_id
                        foundation_model_id = None
                        if session:
                            foundation_model_id = session.get("foundation_model_id")
                            if foundation_model_id and featrix_session_id == foundation_model_id:
                                logger.error(f"❌ CRITICAL BUG: featrix_session_id matches foundation_model_id in failure webhook!")
                                logger.error(f"   session_id from args: {args.session_id}")
                                logger.error(f"   featrix_session_id: {featrix_session_id}")
                                logger.error(f"   foundation_model_id: {foundation_model_id}")
                        
                        logger.info(f"📤 Failure webhook sending: featrix_session_id={featrix_session_id} (foundation={foundation_model_id})")
                        
                        call_model_id_update_webhook(
                            webhook_url=model_id_update_url,
                            model_id=model_id,
                            org_id=org_id,
                            featrix_model_id=args.job_id or "unknown",
                            featrix_session_id=featrix_session_id,
                            featrix_es_id=None,
                            status="failed",
                            metrics={},
                            webhook_secret=org_id
                        )
            except Exception as webhook_err:
                logger.warning(f"⚠️  Failed to call failure webhook: {webhook_err}")
        
        raise Exception("Single predictor training failed with all attempted batch sizes")
    
    logger.info(f"training_worked = {training_worked}")
    
    if not training_worked:
        # Set job status to FAILED before raising
        try:
            job_id = getattr(args, 'job_id', None)
            if job_id:
                logger.error(f"❌ Setting job {job_id} status to FAILED due to training failure")
                update_job_status(job_id=job_id, status=JobStatus.FAILED)
            else:
                logger.warning(f"⚠️  Cannot set job status to FAILED: job_id not available")
        except Exception as status_err:
            logger.error(f"⚠️  Failed to set job status to FAILED: {status_err}")
        
        # Call failure webhook if configured
        if args.webhooks:
            try:
                from lib.webhook_helpers import call_model_id_update_webhook
                from lib.session_manager import load_session
                
                model_id_update_url = args.webhooks.get("model_id_update_url")
                if model_id_update_url:
                    org_id = args.webhooks.get("webhook_callback_secret")
                    if org_id:
                        session_id = args.session_id or args.job_id
                        session = None
                        model_id = None
                        
                        if session_id:
                            try:
                                session = load_session(session_id)
                                if session:
                                    metadata = session.get("metadata", {})
                                    if isinstance(metadata, dict):
                                        model_id = metadata.get("model_id")
                                    if not model_id:
                                        session_name = session.get("name", "")
                                        if session_name and session_name.startswith("dot_model_"):
                                            model_id = session_name
                                    if not model_id:
                                        model_id = session_id
                            except Exception:
                                model_id = session_id
                        
                        if not model_id:
                            model_id = args.job_id or "unknown"
                        
                        call_model_id_update_webhook(
                            webhook_url=model_id_update_url,
                            model_id=model_id,
                            org_id=org_id,
                            featrix_model_id=args.job_id or "unknown",
                            featrix_session_id=session_id or "unknown",
                            featrix_es_id=None,
                            status="failed",
                            metrics={},
                            webhook_secret=org_id
                        )
            except Exception as webhook_err:
                logger.warning(f"⚠️  Failed to call failure webhook: {webhook_err}")
        
        # Send Slack alert for training failure
        try:
            from pathlib import Path as PathLib
            sys.path.insert(0, str(PathLib(__file__).parent.parent))
            from slack import send_slack_message
            
            error_msg = f"🚨 *Single Predictor Training FAILED*\n"
            error_msg += f"• Session: `{args.session_id or 'unknown'}`\n"
            error_msg += f"• Job: `{args.job_id or 'unknown'}`\n"
            error_msg += f"• Target: `{args.target_column}` ({args.target_column_type})\n"
            error_msg += f"• Error: Training failed after all batch size retries"
            
            send_slack_message(error_msg, throttle=False)  # Critical - don't throttle
            logger.info("✅ Slack alert sent for training failure")
        except Exception as slack_error:
            logger.warning(f"Failed to send Slack alert: {slack_error}")
        
        raise Exception("Single predictor training failed")
    
    return 0


if __name__ == "__main__":
    print("Starting Single Predictor Training!")
    
    # Example usage
    args = LightSinglePredictorArgs(
        target_column="target_column_name",  # Replace with actual target column
        target_column_type="set",  # or "scalar"
        n_epochs=0,
        batch_size=0,
    )
    
    train_single_predictor(args=args) 
