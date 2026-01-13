#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.

"""
Training Monitor Integration

Posts training data to monitor.featrix.com for analysis and hyperparameter prediction.
Collects comprehensive column statistics, training metrics, and hyperparameters.
"""

import logging
import os
import socket
import traceback
import threading
import queue
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
import pandas as pd

# Import clean_numpy_values from utils
from utils import clean_numpy_values

# Import GPU utilities
from featrix.neural.gpu_utils import is_cuda_available

# Import PlatformUtils to get root directory
from featrix.neural.platform_utils import featrix_get_root

logger = logging.getLogger(__name__)

# Import featrix-monitor client library - REQUIRED, crash if not available
try:
    from featrix_monitor import create_client
except ImportError as e:
    logger.error("=" * 80)
    logger.error("❌ CRITICAL ERROR: featrix-monitor package is not installed!")
    logger.error("=" * 80)
    logger.error("This package is REQUIRED for training monitoring.")
    logger.error("Install it with: pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
    logger.error("=" * 80)
    raise ImportError("featrix-monitor package is required but not installed. Install it and try again.") from e

# Global client instance
_monitor_client = None


def get_monitor_client():
    """Get or create the global monitor client instance.
    
    Sets FEATRIX_ROOT and SPHERE_ROOT environment variables before creating
    the client to ensure it uses the correct root directory (not hardcoded /sphere).
    """
    global _monitor_client
    if _monitor_client is None:
        try:
            # Set root directory environment variable for featrix-monitor client
            # This ensures the client uses PlatformUtils logic instead of hardcoding /sphere
            root_dir = featrix_get_root()
            os.environ['FEATRIX_ROOT'] = root_dir
            # Also set SPHERE_ROOT for backward compatibility if client uses it
            os.environ['SPHERE_ROOT'] = root_dir
            
            _monitor_client = create_client()
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ CRITICAL: Failed to create monitor client: {e}")
            logger.error("=" * 80)
            if "Read-only file system" in str(e) or "/sphere" in str(e):
                logger.error("The featrix-monitor package may need to be upgraded to support FEATRIX_ROOT env var.")
                logger.error(f"Current FEATRIX_ROOT is set to: {root_dir}")
            logger.error("To install/upgrade featrix-monitor:")
            logger.error("  pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
            logger.error("=" * 80)
            raise
    return _monitor_client


def get_column_statistics(
    df: pd.DataFrame,
    codecs: Dict[str, Any],
    input_data_set: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Collect comprehensive statistics for each column using detectors from FeatrixInputDataSet.
    
    Args:
        df: DataFrame with the data
        codecs: Dictionary mapping column names to codec objects
        input_data_set: Optional FeatrixInputDataSet object to get detectors from
        
    Returns:
        List of column statistics dictionaries
    """
    column_stats = []
    
    # Get detectors from input_data_set if provided
    detectors = {}
    if input_data_set is not None:
        if hasattr(input_data_set, '_detectors'):
            detectors = input_data_set._detectors
        elif hasattr(input_data_set, 'get_detector_for_col_name'):
            # Build detectors dict by calling get_detector_for_col_name for each column
            for col_name in df.columns:
                detector = input_data_set.get_detector_for_col_name(col_name)
                if detector:
                    detectors[col_name] = detector
    
    for col_name in df.columns:
        col_data = df[col_name]
        total_rows = len(col_data)
        non_null_count = col_data.notna().sum()
        null_count = col_data.isnull().sum()
        fill_rate = non_null_count / total_rows if total_rows > 0 else 0.0
        unique_count = col_data.nunique()
        
        col_info = {
            "column_name": col_name,
            "dtype": str(col_data.dtype),
            "total_rows": total_rows,
            "non_null_count": int(non_null_count),
            "null_count": int(null_count),
            "fill_rate": float(fill_rate),
            "unique_count": int(unique_count),
            "unique_ratio": float(unique_count / non_null_count) if non_null_count > 0 else 0.0,
        }
        
        # Get detector information first - detectors have the richest information
        detector = detectors.get(col_name)
        if detector:
            # Get detector type and confidence
            if hasattr(detector, 'get_codec_name'):
                col_info["detector_type"] = detector.get_codec_name()
            if hasattr(detector, 'confidence'):
                col_info["detector_confidence"] = float(detector.confidence())
            if hasattr(detector, 'get_meta_description'):
                meta_desc = detector.get_meta_description()
                if meta_desc:
                    col_info["detector_meta"] = meta_desc
            
            # Get comprehensive debug info from detector
            if hasattr(detector, 'get_debug_info'):
                debug_info = detector.get_debug_info()
                if debug_info:
                    # String complexity metrics from detector (most accurate)
                    if 'min_str_len' in debug_info:
                        col_info["string_length_min"] = int(debug_info.get('min_str_len', 0))
                    if 'max_str_len' in debug_info:
                        col_info["string_length_max"] = int(debug_info.get('max_str_len', 0))
                    if 'mean_str_len' in debug_info:
                        col_info["string_length_mean"] = float(debug_info.get('mean_str_len', 0))
                    if 'median_str_len' in debug_info:
                        col_info["string_length_median"] = float(debug_info.get('median_str_len', 0))
                    if 'quantile75_str_len' in debug_info:
                        col_info["string_length_q75"] = float(debug_info.get('quantile75_str_len', 0))
                    if 'std_str_len' in debug_info:
                        col_info["string_length_std"] = float(debug_info.get('std_str_len', 0))
                    if 'bertMaxLength' in debug_info:
                        col_info["bert_max_length"] = int(debug_info.get('bertMaxLength', 0))
                    
                    # String length distribution
                    if 'str_len_value_counts' in debug_info:
                        str_len_counts = debug_info['str_len_value_counts']
                        if str_len_counts:
                            # Convert to a more usable format
                            col_info["string_length_distribution"] = {str(k): int(v) for k, v in str_len_counts.items()}
                    
                    # Value counts from detector
                    if 'value_counts_10_largest' in debug_info:
                        col_info["top_10_values"] = {str(k): int(v) for k, v in debug_info['value_counts_10_largest'].items()}
                    if 'value_counts_10_weight' in debug_info:
                        col_info["top_10_values_total"] = int(debug_info['value_counts_10_weight'])
                    
                    # Detector-specific stats
                    if 'numUniques' in debug_info:
                        col_info["detector_num_uniques"] = int(debug_info['numUniques'])
                    if 'numNotNulls' in debug_info:
                        col_info["detector_num_not_nulls"] = int(debug_info['numNotNulls'])
                    if 'numNulls' in debug_info:
                        col_info["detector_num_nulls"] = int(debug_info['numNulls'])
            
            # Get detector-specific attributes
            # For string list detectors
            if hasattr(detector, 'delimiter'):
                col_info["delimiter"] = detector.delimiter
            if hasattr(detector, 'list_format'):
                col_info["list_format"] = detector.list_format
            if hasattr(detector, 'string_elements'):
                if detector.string_elements:
                    col_info["unique_string_elements"] = len(detector.string_elements)
                    if len(detector.string_elements) <= 100:
                        col_info["string_elements"] = list(detector.string_elements)
            
            # For set detectors
            if hasattr(detector, 'set_delimiter'):
                col_info["set_delimiter"] = detector.set_delimiter
        
        # Get codec information (supplement detector info)
        codec = codecs.get(col_name)
        if codec:
            codec_type = type(codec).__name__
            col_info["encoder_type"] = codec_type
            
            # Numeric columns (ScalarCodec)
            if hasattr(codec, 'mean') and hasattr(codec, 'stdev'):
                col_info["mean"] = float(codec.mean) if codec.mean is not None else None
                col_info["std"] = float(codec.stdev) if codec.stdev is not None else None
                
                # Try to get min/max from actual data (if not already from detector)
                if 'min' not in col_info:
                    numeric_data = pd.to_numeric(col_data, errors='coerce').dropna()
                    if len(numeric_data) > 0:
                        col_info["min"] = float(numeric_data.min())
                        col_info["max"] = float(numeric_data.max())
                        col_info["median"] = float(numeric_data.median())
                        col_info["q25"] = float(numeric_data.quantile(0.25))
                        col_info["q75"] = float(numeric_data.quantile(0.75))
            
            # Categorical/Set columns
            if hasattr(codec, 'vocabulary'):
                vocab = codec.vocabulary
                if vocab:
                    col_info["vocabulary_size"] = len(vocab)
                    col_info["cardinality"] = len(vocab)
                    # Store top values for distribution analysis
                    if len(vocab) <= 100:
                        col_info["vocabulary"] = list(vocab)
                    else:
                        col_info["top_values"] = list(vocab)[:50]
            
            # String columns - get string cache info
            if hasattr(codec, 'string_cache') and codec.string_cache:
                cache_dict = codec.string_cache.cache_dict if hasattr(codec.string_cache, 'cache_dict') else {}
                col_info["string_cache_size"] = len(cache_dict)
                if 'vocabulary_size' not in col_info:
                    col_info["vocabulary_size"] = len(cache_dict)
            
            # Set delimiter for set columns (if not from detector)
            if 'set_delimiter' not in col_info and hasattr(codec, 'set_delimiter'):
                col_info["set_delimiter"] = codec.set_delimiter
            
            # Vector columns
            if hasattr(codec, 'vector_dim'):
                col_info["vector_dimension"] = codec.vector_dim
        
        # Value distribution for categorical columns (if not already from detector)
        if 'top_10_values' not in col_info and col_info.get("unique_count", 0) < 100 and col_info.get("unique_count", 0) > 0:
            value_counts = col_data.value_counts().head(20).to_dict()
            # Convert keys to strings for JSON serialization
            col_info["value_distribution"] = {str(k): int(v) for k, v in value_counts.items()}
        
        column_stats.append(col_info)
    
    return column_stats


def collect_es_training_data(
    embedding_space,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    training_start_time: datetime,
    training_end_time: datetime,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    customer_id: Optional[str] = None,
    remote_hostname: Optional[str] = None,
    s3_path: Optional[str] = None,
    session_id: Optional[str] = None,
    deployment_id: Optional[str] = None,
    optimal_params: Optional[Dict[str, int]] = None,
    pre_analysis_epochs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Collect training data for Embedding Space training.
    
    Args:
        embedding_space: Trained EmbeddingSpace object
        train_df: Training dataframe
        val_df: Validation dataframe
        training_start_time: When training started
        training_end_time: When training finished
        epochs: Number of epochs trained
        batch_size: Batch size used
        learning_rate: Learning rate used
        customer_id: Optional customer ID
        remote_hostname: Optional hostname
        s3_path: Optional S3 path to saved model
        
    Returns:
        Dictionary ready to post to monitor API
    """
    # Get hostname if not provided
    if remote_hostname is None:
        try:
            remote_hostname = socket.gethostname()
        except:
            remote_hostname = "unknown"
    
    # Get customer ID from environment if not provided
    if customer_id is None:
        customer_id = os.getenv("FEATRIX_CUSTOMER_ID", "default")
    
    # Get deployment_id if not provided (use hostname as fallback)
    if deployment_id is None:
        deployment_id = remote_hostname or "unknown"
    
    # Get software version
    try:
        from version import get_version
        software_version = str(get_version())
    except:
        software_version = "unknown"
    
    # Collect column statistics
    codecs = embedding_space.col_codecs if hasattr(embedding_space, 'col_codecs') else {}
    
    # Get input_data_set from embedding_space (prefer train_input_data)
    input_data_set = None
    if hasattr(embedding_space, 'train_input_data'):
        input_data_set = embedding_space.train_input_data
    elif hasattr(embedding_space, 'val_input_data'):
        input_data_set = embedding_space.val_input_data
    
    # Use combined dataframe for column stats if provided, otherwise use codecs only
    if train_df is not None and val_df is not None:
        combined_df = pd.concat([train_df, val_df], ignore_index=True)
        column_stats = get_column_statistics(combined_df, codecs, input_data_set)
        
        # Calculate dataset characteristics (for meta-learning compatibility)
        import hashlib
        import numpy as np
        
        # Column names hash (privacy-preserving dataset identifier)
        col_names_str = '|'.join(sorted(combined_df.columns))
        column_names_hash = hashlib.sha256(col_names_str.encode()).hexdigest()[:16]
        
        # Cardinality analysis for categorical columns
        categorical_cols = combined_df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            cardinalities = [combined_df[col].nunique() for col in categorical_cols]
            avg_cardinality = float(np.mean(cardinalities))
            max_cardinality = int(max(cardinalities))
        else:
            avg_cardinality = 0.0
            max_cardinality = 0
    else:
        # No dataframes provided - extract everything from codecs and detectors
        import hashlib
        import numpy as np
        
        # Get column names from codecs
        column_names = list(codecs.keys())
        
        # Create minimal dataframe structure for get_column_statistics
        # It will use codecs/detectors for actual stats
        total_rows = len(train_df) if train_df is not None else (len(val_df) if val_df is not None else 0)
        if total_rows == 0:
            # Estimate from training_info if available
            training_info = getattr(embedding_space, 'training_info', {})
            total_rows = training_info.get('input_rows') or training_info.get('total_rows') or 1000
        
        combined_df = pd.DataFrame(columns=column_names, index=range(total_rows))
        column_stats = get_column_statistics(combined_df, codecs, input_data_set)
        
        # Column names hash (privacy-preserving dataset identifier)
        col_names_str = '|'.join(sorted(column_names))
        column_names_hash = hashlib.sha256(col_names_str.encode()).hexdigest()[:16]
        
        # Cardinality analysis from codecs (vocabulary sizes)
        cardinalities = []
        for col_name, codec in codecs.items():
            if hasattr(codec, 'vocabulary') and codec.vocabulary:
                cardinalities.append(len(codec.vocabulary))
            elif hasattr(codec, 'vocab') and codec.vocab:
                cardinalities.append(len(codec.vocab))
        
        if cardinalities:
            avg_cardinality = float(np.mean(cardinalities))
            max_cardinality = int(max(cardinalities))
        else:
            avg_cardinality = 0.0
            max_cardinality = 0
    
    # Extract training losses from timeline
    training_loss = []
    validation_loss = []
    
    if hasattr(embedding_space, '_training_timeline') and embedding_space._training_timeline:
        for entry in embedding_space._training_timeline:
            if entry.get('train_loss') is not None:
                training_loss.append(float(entry['train_loss']))
            if entry.get('validation_loss') is not None:
                validation_loss.append(float(entry['validation_loss']))
    
    # Fallback to training_info if timeline not available
    if not training_loss and hasattr(embedding_space, 'training_info'):
        progress_info = embedding_space.training_info.get('progress_info', {})
        loss_history = progress_info.get('loss_history', [])
        for entry in loss_history:
            if isinstance(entry, dict):
                if entry.get('loss') is not None:
                    training_loss.append(float(entry['loss']))
                if entry.get('validation_loss') is not None:
                    validation_loss.append(float(entry['validation_loss']))
    
    # Get hyperparameters from training_info
    training_info = getattr(embedding_space, 'training_info', {})
    
    # Extract metadata/hyperparameters
    metadata = {
        "learning_rate": learning_rate,
        "optimizer": "adam",  # Default for ES training
        "d_model": getattr(embedding_space, 'd_model', None),
        "n_columns": len(train_df.columns),
        "n_epochs": epochs,
        "batch_size": batch_size,
        "compute_hostname": remote_hostname,  # Include hostname in metadata for tracking
        "qa_test": True,  # Mark this as a QA test run
    }
    
    # Add dropout info if available
    if hasattr(embedding_space, '_training_timeline') and embedding_space._training_timeline:
        first_epoch = embedding_space._training_timeline[0] if embedding_space._training_timeline else {}
        last_epoch = embedding_space._training_timeline[-1] if embedding_space._training_timeline else {}
        if 'dropout_rate' in first_epoch:
            metadata["initial_dropout"] = first_epoch.get('dropout_rate')
        if 'dropout_rate' in last_epoch:
            metadata["final_dropout"] = last_epoch.get('dropout_rate')
    
    # Calculate time taken
    time_taken = (training_end_time - training_start_time).total_seconds()
    
    # Check if GPU was used
    ran_on_gpu = False
    try:
        import torch
        ran_on_gpu = is_cuda_available()
    except:
        pass
    
    # Build the training data payload
    training_data = {
        "customer_id": customer_id,
        "remote_hostname": remote_hostname,
        "training_type": "embedding_space",
        
        # Core hyperparameters
        "epochs": epochs,
        "batch_size": batch_size,
        
        # Additional hyperparameters in metadata
        "metadata": metadata,
        
        # Dataset info
        "input_rows": len(combined_df),
        "input_columns": len(train_df.columns),
        "training_size": len(train_df),
        "validation_size": len(val_df),
        
        # Column statistics
        "columns": column_stats,
        
        # Results - Loss curves
        "training_loss": training_loss,
        "validation_loss": validation_loss,
        
        # Execution details
        "time_taken": time_taken,
        "ran_on_gpu": ran_on_gpu,
        "datetime_started": training_start_time.isoformat() + "Z",
        "datetime_finished": training_end_time.isoformat() + "Z",
        
        # ES training doesn't have classification metrics - use empty metrics object
        "metrics": {},
        
        # API now requires these fields at top level (even for ES training where they don't apply)
        "precision": None,
        "recall": None,
        "f1": None,
        "auc": None,
        "accuracy": None,
        
        "s3_path": s3_path if s3_path else None,
        
        # Meta-learning fields (from log_training_metadata)
        "software_version": software_version,
        "deployment_id": deployment_id,
        "column_names_hash": column_names_hash,
        "avg_cardinality": avg_cardinality,
        "max_cardinality": max_cardinality,
    }
    
    # Add optimal_params if provided (for meta-learning)
    if optimal_params:
        training_data["optimal_params"] = optimal_params
    
    # Add pre_analysis_epochs if provided (for meta-learning)
    if pre_analysis_epochs:
        training_data["pre_analysis_epochs"] = pre_analysis_epochs
    
    # Add session_id if provided (optional field per API docs)
    if session_id:
        training_data["session_id"] = session_id
    
    return training_data


def collect_sp_training_data(
    single_predictor,
    embedding_space,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    target_column: str,
    target_column_type: str,
    training_start_time: datetime,
    training_end_time: datetime,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    customer_id: Optional[str] = None,
    remote_hostname: Optional[str] = None,
    s3_path: Optional[str] = None,
    session_id: Optional[str] = None,
    deployment_id: Optional[str] = None,
    optimal_params: Optional[Dict[str, int]] = None,
    pre_analysis_epochs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Collect training data for Single Predictor training.
    
    Args:
        single_predictor: Trained FeatrixSinglePredictor object
        embedding_space: The EmbeddingSpace used
        train_df: Training dataframe
        val_df: Validation dataframe
        target_column: Name of target column
        target_column_type: Type of target ("set" or "scalar")
        training_start_time: When training started
        training_end_time: When training finished
        epochs: Number of epochs trained
        batch_size: Batch size used
        learning_rate: Learning rate used
        customer_id: Optional customer ID
        remote_hostname: Optional hostname
        s3_path: Optional S3 path to saved model
        
    Returns:
        Dictionary ready to post to monitor API
    """
    # Get hostname if not provided
    if remote_hostname is None:
        try:
            remote_hostname = socket.gethostname()
        except:
            remote_hostname = "unknown"
    
    # Get customer ID from environment if not provided
    if customer_id is None:
        customer_id = os.getenv("FEATRIX_CUSTOMER_ID", "default")
    
    # Get deployment_id if not provided (use hostname as fallback)
    if deployment_id is None:
        deployment_id = remote_hostname or "unknown"
    
    # Get software version
    try:
        from version import get_version
        software_version = str(get_version())
    except:
        software_version = "unknown"
    
    # Collect column statistics (excluding target column for input columns)
    input_df = train_df.drop(columns=[target_column], errors='ignore')
    codecs = embedding_space.col_codecs if hasattr(embedding_space, 'col_codecs') else {}
    
    # Get input_data_set from embedding_space (prefer train_input_data)
    input_data_set = None
    if hasattr(embedding_space, 'train_input_data'):
        input_data_set = embedding_space.train_input_data
    elif hasattr(embedding_space, 'val_input_data'):
        input_data_set = embedding_space.val_input_data
    
    # Use combined dataframe for column stats
    combined_input_df = pd.concat([
        train_df.drop(columns=[target_column], errors='ignore'),
        val_df.drop(columns=[target_column], errors='ignore')
    ], ignore_index=True)
    
    column_stats = get_column_statistics(combined_input_df, codecs, input_data_set)
    
    # Calculate dataset characteristics (for meta-learning compatibility)
    import hashlib
    import numpy as np
    
    # Column names hash (privacy-preserving dataset identifier)
    # Include target column in hash for complete dataset identification
    all_cols = list(combined_input_df.columns) + [target_column]
    col_names_str = '|'.join(sorted(all_cols))
    column_names_hash = hashlib.sha256(col_names_str.encode()).hexdigest()[:16]
    
    # Cardinality analysis for categorical columns (input columns only)
    categorical_cols = combined_input_df.select_dtypes(include=['object', 'category']).columns.tolist()
    if categorical_cols:
        cardinalities = [combined_input_df[col].nunique() for col in categorical_cols]
        avg_cardinality = float(np.mean(cardinalities))
        max_cardinality = int(max(cardinalities))
    else:
        avg_cardinality = 0.0
        max_cardinality = 0
    
    # Calculate class imbalance for classification problems
    class_imbalance = None
    if target_column_type == "set" and target_column in train_df.columns:
        value_counts = train_df[target_column].value_counts()
        if len(value_counts) == 2:  # Binary classification
            class_imbalance = float(value_counts.min() / value_counts.max())
        elif len(value_counts) > 2:  # Multiclass - use min/max ratio
            class_imbalance = float(value_counts.min() / value_counts.max())
    
    # Extract training losses from timeline
    training_loss = []
    validation_loss = []
    
    if hasattr(single_predictor, '_training_timeline') and single_predictor._training_timeline:
        for entry in single_predictor._training_timeline:
            if entry.get('current_loss') is not None:
                training_loss.append(float(entry['current_loss']))
            if entry.get('validation_loss') is not None:
                validation_loss.append(float(entry['validation_loss']))
    
    # Fallback to training_info if timeline not available
    if not training_loss and hasattr(single_predictor, 'training_info') and single_predictor.training_info:
        for entry in single_predictor.training_info:
            if isinstance(entry, dict):
                if entry.get('loss') is not None:
                    training_loss.append(float(entry['loss']))
                if entry.get('validation_loss') is not None:
                    validation_loss.append(float(entry['validation_loss']))
    
    # Get final metrics
    metrics = {}
    if hasattr(single_predictor, 'training_metrics') and single_predictor.training_metrics:
        metrics = single_predictor.training_metrics
    
    # Get hyperparameters
    metadata = {
        "learning_rate": learning_rate,
        "optimizer": "adam",  # Default for SP training
        "target_column": target_column,
        "target_column_type": target_column_type,
        "d_model": getattr(embedding_space, 'd_model', None),
        "n_input_columns": len(input_df.columns),
        "n_epochs": epochs,
        "batch_size": batch_size,
        "compute_hostname": remote_hostname,  # Include hostname in metadata for tracking
        "qa_test": True,  # Mark this as a QA test run
    }
    
    # Add model architecture info
    if hasattr(single_predictor, 'predictor'):
        try:
            param_count = sum(p.numel() for p in single_predictor.predictor.parameters())
            metadata["parameter_count"] = param_count
        except:
            pass
    
    # Calculate time taken
    time_taken = (training_end_time - training_start_time).total_seconds()
    
    # Check if GPU was used
    ran_on_gpu = False
    try:
        import torch
        ran_on_gpu = is_cuda_available()
    except:
        pass
    
    # Build the training data payload
    training_data = {
        "customer_id": customer_id,
        "remote_hostname": remote_hostname,
        "training_type": "classification" if target_column_type == "set" else "regression",
        
        # Core hyperparameters
        "epochs": epochs,
        "batch_size": batch_size,
        
        # Additional hyperparameters in metadata
        "metadata": metadata,
        
        # Dataset info - use SP's actual split sizes if available (set during _prepare_validation_data)
        "input_rows": getattr(single_predictor, '_actual_train_size', len(train_df)) + getattr(single_predictor, '_actual_val_size', 0 if train_df is val_df else len(val_df)),
        "input_columns": len(input_df.columns),
        "training_size": getattr(single_predictor, '_actual_train_size', len(train_df)),
        "validation_size": getattr(single_predictor, '_actual_val_size', 0 if train_df is val_df else len(val_df)),
        "used_internal_split": getattr(single_predictor, '_used_internal_split', train_df is val_df),
        
        # Column statistics
        "columns": column_stats,
        
        # Results - Loss curves
        "training_loss": training_loss,
        "validation_loss": validation_loss,
        
        # Results - Metrics (nested object format)
        "metrics": {},
        
        # Execution details
        "time_taken": time_taken,
        "ran_on_gpu": ran_on_gpu,
        "datetime_started": training_start_time.isoformat() + "Z",
        "datetime_finished": training_end_time.isoformat() + "Z",
    }
    
    # Populate metrics object with available metrics
    if metrics:
        # Convert all metrics to float and add to metrics object
        for key, value in metrics.items():
            try:
                training_data["metrics"][key] = float(value)
            except (ValueError, TypeError):
                # Skip non-numeric metrics
                continue
    
        # Always include s3_path (API requires it, use null if not available)
    training_data["s3_path"] = s3_path
    
    # Meta-learning fields (from log_training_metadata)
    training_data["software_version"] = software_version
    training_data["deployment_id"] = deployment_id
    training_data["column_names_hash"] = column_names_hash
    training_data["avg_cardinality"] = avg_cardinality
    training_data["max_cardinality"] = max_cardinality
    if class_imbalance is not None:
        training_data["class_imbalance"] = class_imbalance
    
    # Add optimal_params if provided (for meta-learning)
    if optimal_params:
        training_data["optimal_params"] = optimal_params
    
    # Add pre_analysis_epochs if provided (for meta-learning)
    if pre_analysis_epochs:
        training_data["pre_analysis_epochs"] = pre_analysis_epochs
    
    # Add session_id if provided (optional field per API docs)
    if session_id:
        training_data["session_id"] = session_id
    
    return training_data


def post_training_progress(
    session_id: str,
    customer_id: Optional[str] = None,
    remote_hostname: Optional[str] = None,
    training_type: str = "embedding_space",
    current_epoch: int = 0,
    total_epochs: int = 0,
    current_training_loss: Optional[float] = None,
    current_validation_loss: Optional[float] = None,
    estimated_time_remaining: Optional[str] = None,
    ran_on_gpu: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
    network_architecture: Optional[Dict[str, Any]] = None,
    monitor_url: str = "https://monitor.featrix.com/training/progress"
) -> bool:
    """
    Post in-progress training updates to the monitor API (async, non-blocking).
    
    Uses the featrix-monitor client library which handles async posting with queue-based
    background processing. This function returns immediately without blocking.
    
    Args:
        session_id: Session/job ID for this training
        customer_id: Optional customer ID
        remote_hostname: Optional hostname (will auto-detect if not provided)
        training_type: Type of training ("embedding_space" or "classification"/"regression")
        current_epoch: Current epoch number
        total_epochs: Total epochs planned
        current_training_loss: Current training loss
        current_validation_loss: Current validation loss
        estimated_time_remaining: Estimated time remaining (e.g., "10m")
        ran_on_gpu: Whether running on GPU
        metadata: Optional metadata dict (should include dataset_hash and config params)
        network_architecture: Optional network architecture dict (should include config params)
        monitor_url: URL of the monitor progress endpoint (deprecated, kept for compatibility)
        
    Returns:
        True if queued successfully (always returns True for async client)
    """
    try:
        # Get hostname if not provided
        if remote_hostname is None:
            try:
                remote_hostname = socket.gethostname()
            except:
                remote_hostname = "unknown"
        
        # Get customer ID from environment if not provided
        if customer_id is None:
            customer_id = os.getenv("FEATRIX_CUSTOMER_ID", "default")
        
        # Use async client (non-blocking)
        client = get_monitor_client()
        client.update_training_progress(
            session_id=session_id,
            customer_id=customer_id,
            remote_hostname=remote_hostname,
            training_type=training_type,
            current_epoch=current_epoch,
            total_epochs=total_epochs,
            current_training_loss=current_training_loss,
            current_validation_loss=current_validation_loss,
            estimated_time_remaining=estimated_time_remaining,
            ran_on_gpu=ran_on_gpu,
            metadata=metadata,
            network_architecture=network_architecture,
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to post training progress update: {e}")
        logger.debug(traceback.format_exc())
        # Don't crash training if monitor fails, but log the error
        return False


def post_training_start(
    session_id: str,
    customer_id: Optional[str] = None,
    remote_hostname: Optional[str] = None,
    training_type: str = "embedding_space",
    total_epochs: int = 0,
    ran_on_gpu: bool = False,
) -> bool:
    """
    Post training start notification to the monitor API (async, non-blocking).
    
    Args:
        session_id: Session/job ID for this training
        customer_id: Optional customer ID
        remote_hostname: Optional hostname (will auto-detect if not provided)
        training_type: Type of training ("embedding_space" or "classification"/"regression")
        total_epochs: Total epochs planned
        ran_on_gpu: Whether running on GPU
        
    Returns:
        True if queued successfully (always returns True for async client)
    """
    try:
        # Get hostname if not provided
        if remote_hostname is None:
            try:
                remote_hostname = socket.gethostname()
            except:
                remote_hostname = "unknown"
        
        # Get customer ID from environment if not provided
        if customer_id is None:
            customer_id = os.getenv("FEATRIX_CUSTOMER_ID", "default")
        
        # Use async client (non-blocking)
        client = get_monitor_client()
        client.update_training_progress(
            session_id=session_id,
            customer_id=customer_id,
            remote_hostname=remote_hostname,
            training_type=training_type,
            current_epoch=0,
            total_epochs=total_epochs,
            ran_on_gpu=ran_on_gpu,
        )
        
        logger.info(f"📊 Training start posted to monitor (session_id={session_id}, hostname={remote_hostname})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to post training start notification: {e}")
        logger.debug(traceback.format_exc())
        # Don't crash training if monitor fails, but log the error
        return False


def post_training_data(training_data: Dict[str, Any], monitor_url: str = "https://monitor.featrix.com/training") -> bool:
    """
    Post training data to the monitor API.
    
    Args:
        training_data: Dictionary with training data
        monitor_url: URL of the monitor API endpoint
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"📊 Posting training data to {monitor_url}...")
        logger.info(f"   Training type: {training_data.get('training_type')}")
        logger.info(f"   Epochs: {training_data.get('epochs')}")
        logger.info(f"   Columns: {training_data.get('input_columns')}")
        logger.info(f"   Rows: {training_data.get('input_rows')}")
        
        # Sanitize the data to remove NaN/Inf values before JSON serialization
        # Use the existing clean_numpy_values function from featrix_queue
        sanitized_data = clean_numpy_values(training_data)
        
        response = requests.post(
            monitor_url,
            json=sanitized_data,
            timeout=30  # 30 second timeout
        )
        
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"✅ Successfully posted training data to monitor")
        logger.debug(f"   Response: {result}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        # Log the actual error response from the server
        error_detail = ""
        try:
            if hasattr(e.response, 'text'):
                error_detail = f" - {e.response.text[:500]}"
            elif hasattr(e.response, 'json'):
                error_json = e.response.json()
                error_detail = f" - {error_json}"
        except:
            pass
        
        error_msg = f"HTTP {e.response.status_code if hasattr(e, 'response') and e.response else 'unknown'}: {str(e)}{error_detail}"
        logger.warning(f"⚠️  Failed to post training data to monitor: {e}{error_detail}")
        logger.debug(f"   Full traceback: {traceback.format_exc()}")
        
        # Log for retry
        try:
            from lib.api_event_retry import get_retry_manager, EventType
            retry_manager = get_retry_manager()
            retry_manager.log_failed_event(
                event_type=EventType.TRAINING_DATA,
                url=monitor_url,
                method="POST",
                payload=sanitized_data,
                timeout=30,
                error=error_msg,
                metadata={"training_type": training_data.get('training_type')}
            )
        except Exception as retry_err:
            logger.debug(f"Failed to log training data for retry: {retry_err}")
        
        return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"⚠️  Failed to post training data to monitor: {e}")
        logger.debug(f"   Full traceback: {traceback.format_exc()}")
        
        # Log for retry
        try:
            from lib.api_event_retry import get_retry_manager, EventType
            retry_manager = get_retry_manager()
            retry_manager.log_failed_event(
                event_type=EventType.TRAINING_DATA,
                url=monitor_url,
                method="POST",
                payload=sanitized_data,
                timeout=30,
                error=str(e),
                metadata={"training_type": training_data.get('training_type')}
            )
        except Exception as retry_err:
            logger.debug(f"Failed to log training data for retry: {retry_err}")
        
        return False
    except Exception as e:
        logger.warning(f"⚠️  Unexpected error posting training data: {e}")
        logger.debug(f"   Full traceback: {traceback.format_exc()}")
        
        # Log for retry
        try:
            from lib.api_event_retry import get_retry_manager, EventType
            retry_manager = get_retry_manager()
            retry_manager.log_failed_event(
                event_type=EventType.TRAINING_DATA,
                url=monitor_url,
                method="POST",
                payload=sanitized_data,
                timeout=30,
                error=str(e),
                metadata={"training_type": training_data.get('training_type')}
            )
        except Exception as retry_err:
            logger.debug(f"Failed to log training data for retry: {retry_err}")
        
        return False


def post_training_anomaly(
    session_id: str,
    anomaly_type: str,
    epoch: int,
    details: Dict[str, Any],
    dataset_hash: Optional[str] = None,
    customer_id: Optional[str] = None,
    remote_hostname: Optional[str] = None,
) -> bool:
    """
    Report training anomalies/issues to featrix-monitor (async, non-blocking).
    
    This is used to notify the monitor about training issues like:
    - Dead gradients
    - Training restarts
    - Early stopping
    - Probability collapse
    - NaN weights
    - Other training failures
    
    Args:
        session_id: Session/job ID for this training
        anomaly_type: Type of anomaly (e.g., "dead_gradients", "training_restart_applied", "early_stopping")
        epoch: Epoch number when anomaly occurred
        details: Dict with anomaly-specific details (collapse_type, hostname, metrics, etc.)
        dataset_hash: Dataset hash for correlation (TOP-LEVEL parameter, not in details)
        customer_id: Optional customer ID
        remote_hostname: Optional hostname (will auto-detect if not provided)
        
    Returns:
        True if queued successfully (always returns True for async client)
        
    Example:
        post_training_anomaly(
            session_id="job-123",
            anomaly_type="dead_gradients",
            epoch=50,
            dataset_hash="abc123def456",
            details={
                "collapse_type": "dead_gradients",
                "gradient_norm": 0.0,
                "hostname": "churro",
                "current_lr": 0.001,
                "restart_config": {...}
            }
        )
    """
    try:
        client = get_monitor_client()
        
        # Extract dataset_hash from details if it was passed there (for backwards compatibility)
        if dataset_hash is None and "dataset_hash" in details:
            dataset_hash = details.pop("dataset_hash")
        
        # Ensure details has required fields
        if "hostname" not in details:
            details["hostname"] = remote_hostname or socket.gethostname()
        
        # Add timestamp if not present
        if "timestamp" not in details:
            details["timestamp"] = datetime.now().isoformat()
        
        # Use update_training_progress with metadata to signal anomaly
        client.update_training_progress(
            session_id=session_id,
            customer_id=customer_id or os.getenv("FEATRIX_CUSTOMER_ID", "default"),
            remote_hostname=details["hostname"],
            training_type="single_predictor",
            current_epoch=epoch,
            dataset_hash=dataset_hash,  # TOP-LEVEL parameter
            metadata={
                "anomaly_type": anomaly_type,
                "anomaly_details": details,
            }
        )
        
        logger.info(f"📊 Reported {anomaly_type} anomaly to monitor (epoch {epoch})")
        logger.info(f"   Session: {session_id}, Dataset: {dataset_hash}")
        logger.info(f"   Details sent: {details}")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to report training anomaly to monitor: {e}")
        logger.debug(traceback.format_exc())
        # Don't crash training if monitor fails
        return False


def get_training_state_dict(
    epoch: int,
    current_lr: float,
    batch_size: int,
    n_epochs: int,
    progress_dict: Dict[str, Any],
    target_col_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Helper to collect common training state info for anomaly reporting.
    
    Returns a dict with current training state that can be merged into anomaly details.
    """
    return {
        "hostname": socket.gethostname(),
        "target_column": target_col_name,
        "current_epoch": epoch,
        "current_lr": float(current_lr),
        "batch_size": batch_size,
        "total_epochs_planned": n_epochs,
        "completion_percentage": (epoch / n_epochs * 100) if n_epochs > 0 else 0,
        "current_training_loss": float(progress_dict.get("current_loss", 0)) if progress_dict.get("current_loss") else None,
        "current_validation_loss": float(progress_dict.get("validation_loss", 0)) if progress_dict.get("validation_loss") else None,
    }


def get_restart_recommendation(
    session_id: str,
    anomaly_type: str,
    context: Dict[str, Any],
    dataset_hash: Optional[str] = None,
    customer_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Query featrix-monitor for restart configuration recommendation.
    
    The monitor uses ML/heuristics to suggest optimal restart parameters based on:
    - Historical training data
    - Similar failures
    - Current training context
    
    Args:
        session_id: Session/job ID for this training
        anomaly_type: Type of anomaly (e.g., "dead_gradients", "nan_weights", "oom")
        context: Dict with training context:
            - current_lr: Current learning rate
            - gradient_norm: Current gradient norm (if applicable)
            - epoch: Current epoch
            - target_column: Target column name
            - batch_size: Current batch size
            - hostname: Training host
            - previous_restarts: Number of previous restart attempts
            - ... other relevant context
        dataset_hash: Dataset hash for correlation (TOP-LEVEL parameter, not in context)
        customer_id: Optional customer ID
        
    Returns:
        Dict with recommended restart config, or None if monitor unavailable/no recommendation
        
    Example return value:
        {
            "reason": "DEAD_GRADIENTS",
            "lr_multiplier": 0.3,  # Monitor-suggested (vs hardcoded 0.5)
            "max_lr": 0.008,
            "reset_optimizer_state": True,
            "reset_scheduler": False,
            "load_best_checkpoint": True,
            "additional_epochs": None,
            "confidence": 0.85,  # How confident the monitor is in this recommendation
            "based_on_n_similar_cases": 47  # How many similar cases were used
        }
    """
    try:
        client = get_monitor_client()
        
        # Extract dataset_hash from context if it was passed there (for backwards compatibility)
        if dataset_hash is None and "dataset_hash" in context:
            dataset_hash = context.pop("dataset_hash")
        
        # Query monitor for restart recommendation
        # Note: This method needs to be added to the featrix-monitor client package
        result = client.get_restart_recommendation(  # type: ignore[attr-defined]  # pylint: disable=no-member
            session_id=session_id,
            customer_id=customer_id or os.getenv("FEATRIX_CUSTOMER_ID", "default"),
            dataset_hash=dataset_hash,  # TOP-LEVEL parameter
            anomaly_type=anomaly_type,
            context=context
        )
        
        if result and result.get('recommendation'):
            rec = result['recommendation']
            logger.info(f"📊 Got restart recommendation from monitor for {anomaly_type}")
            logger.info(f"   LR multiplier: {rec.get('lr_multiplier')} (confidence: {rec.get('confidence', 0):.2f})")
            logger.info(f"   Based on {rec.get('based_on_n_similar_cases', 0)} similar cases")
            logger.info(f"   Full recommendation: {rec}")
            return rec
        else:
            logger.debug(f"ℹ️  No restart recommendation from monitor for {anomaly_type}")
            return None
            
    except AttributeError as e:
        # Method doesn't exist on client yet - expected
        logger.debug(f"⚠️  Monitor client doesn't have get_restart_recommendation method yet: {e}")
        return None
    except Exception as e:
        logger.warning(f"⚠️  Failed to get restart recommendation from monitor: {e}")
        logger.debug(traceback.format_exc())
        return None

