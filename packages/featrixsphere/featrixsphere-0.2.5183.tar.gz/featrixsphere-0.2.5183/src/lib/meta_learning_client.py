"""
Meta-Learning Client

Client for logging training metadata and querying optimal parameters
from the central sphere-api meta-learning database.
"""
import hashlib
import json
import logging
import os
import requests
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Import PlatformUtils to get root directory
from featrix.neural.platform_utils import featrix_get_root


def _create_monitor_client():
    """
    Create featrix-monitor client with proper root directory configuration.
    
    Sets FEATRIX_ROOT environment variable before creating client to ensure
    the client uses the correct root directory (not hardcoded /sphere).
    """
    # Set root directory environment variable for featrix-monitor client
    # This ensures the client uses PlatformUtils logic instead of hardcoding /sphere
    root_dir = featrix_get_root()
    os.environ['FEATRIX_ROOT'] = root_dir
    # Also set SPHERE_ROOT for backward compatibility if client uses it
    os.environ['SPHERE_ROOT'] = root_dir
    
    from featrix_monitor import create_client
    return create_client()

# Central meta-learning API endpoint
META_API_URL = "https://sphere-api.featrix.com/meta"


def get_dataset_characteristics(df) -> Dict[str, Any]:
    """
    Extract dataset characteristics for meta-learning.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dict with dataset characteristics
    """
    import pandas as pd
    import numpy as np
    
    # Column type analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Text columns (strings with avg length > 20)
    text_cols = []
    for col in categorical_cols:
        if df[col].dtype == 'object':
            avg_len = df[col].astype(str).str.len().mean()
            if avg_len > 20:
                text_cols.append(col)
    
    # Remove text cols from categorical
    categorical_cols = [c for c in categorical_cols if c not in text_cols]
    
    # Cardinality analysis (for categorical columns)
    if categorical_cols:
        cardinalities = [df[col].nunique() for col in categorical_cols]
        avg_cardinality = np.mean(cardinalities)
        max_cardinality = max(cardinalities)
    else:
        avg_cardinality = 0
        max_cardinality = 0
    
    # Target analysis (assume last column or 'target')
    target_col = 'target' if 'target' in df.columns else df.columns[-1]
    target_cardinality = df[target_col].nunique()
    
    if target_cardinality == 2:
        target_type = 'binary_classification'
        # Class imbalance
        value_counts = df[target_col].value_counts()
        class_imbalance = value_counts.min() / value_counts.max()
    elif target_cardinality > 2 and target_cardinality < 50:
        target_type = 'multiclass_classification'
        class_imbalance = None
    else:
        target_type = 'regression'
        class_imbalance = None
    
    # Privacy-preserving column names hash
    col_names_str = '|'.join(sorted(df.columns))
    column_names_hash = hashlib.sha256(col_names_str.encode()).hexdigest()[:16]
    
    return {
        "n_rows": len(df),
        "n_cols": len(df.columns) - 1,  # Exclude target
        "column_types": {
            "numeric": len(numeric_cols),
            "categorical": len(categorical_cols),
            "text": len(text_cols)
        },
        "column_names_hash": column_names_hash,
        "avg_cardinality": float(avg_cardinality),
        "max_cardinality": int(max_cardinality),
        "target_type": target_type,
        "class_imbalance": float(class_imbalance) if class_imbalance is not None else None
    }


def log_training_metadata(
    session_id: str,
    df,
    optimal_params: Dict[str, int],
    pre_analysis_epochs: Optional[list] = None,
    final_result: Optional[Dict[str, float]] = None,
    deployment_id: Optional[str] = None
) -> Optional[str]:
    """
    Log training metadata to central meta-learning API.
    
    Args:
        session_id: Session ID
        df: Training DataFrame (for extracting characteristics)
        optimal_params: Optimal parameters found
        pre_analysis_epochs: Epoch-by-epoch pre-analysis results
        final_result: Final training results
        deployment_id: Deployment identifier (e.g., 'churro', 'burrito')
        
    Returns:
        metadata_id if successful, None otherwise
    """
    try:
        # Get software version
        from version import get_version
        software_version = get_version()
        
        # Extract dataset characteristics
        dataset_chars = get_dataset_characteristics(df)
        
        # Build metadata payload
        payload = {
            "software_version": str(software_version),  # Convert VersionInfo to string
            "deployment_id": deployment_id or "unknown",
            "session_id": session_id,
            "dataset_characteristics": dataset_chars,
            "optimal_params": optimal_params,
        }
        
        if pre_analysis_epochs:
            payload["pre_analysis_epochs"] = pre_analysis_epochs
        
        if final_result:
            payload["final_result"] = final_result
        
        # POST to meta-learning API
        logger.info(f"📤 Logging training metadata to {META_API_URL}/log-training-metadata")
        response = requests.post(
            f"{META_API_URL}/log-training-metadata",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            metadata_id = result.get('metadata_id')
            logger.info(f"✅ Training metadata logged successfully: {metadata_id}")
            return metadata_id
        else:
            logger.warning(f"⚠️  Failed to log training metadata: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error logging training metadata: {e}")
        return None


def query_optimal_parameters(df, target_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Query meta-learning API for recommended parameters based on dataset characteristics.
    
    Args:
        df: pandas DataFrame
        target_type: Override target type detection
        
    Returns:
        Dict with recommendation, or None if no data available
    """
    try:
        # Extract dataset characteristics
        dataset_chars = get_dataset_characteristics(df)
        
        # Query API
        params = {
            "n_rows": dataset_chars["n_rows"],
            "n_cols": dataset_chars["n_cols"],
            "target_type": target_type or dataset_chars["target_type"],
            "limit": 10
        }
        
        logger.info(f"🔍 Querying meta-learning API for similar datasets...")
        logger.info(f"   n_rows={params['n_rows']}, n_cols={params['n_cols']}, target_type={params['target_type']}")
        
        response = requests.get(
            f"{META_API_URL}/query-training-metadata",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            recommendation = result.get('recommendation')
            similar_count = len(result.get('similar_datasets', []))
            
            if recommendation:
                logger.info(f"✅ Found recommendation based on {similar_count} similar datasets:")
                logger.info(f"   d_model: {recommendation['d_model']}")
                logger.info(f"   n_transformer_layers: {recommendation['n_transformer_layers']}")
                logger.info(f"   n_attention_heads: {recommendation['n_attention_heads']}")
                logger.info(f"   Confidence: {recommendation['confidence']:.2f}")
                logger.info(f"   Pre-analysis epochs: {recommendation['pre_analysis_epochs']}")
                return result
            else:
                logger.info(f"ℹ️  No recommendations available yet (found {similar_count} datasets)")
                return None
        else:
            logger.warning(f"⚠️  Failed to query meta-learning API: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error querying meta-learning API: {e}")
        return None


def get_recommended_pre_analysis_config(df) -> Dict[str, Any]:
    """
    Get recommended pre-analysis configuration based on meta-learning.
    
    Falls back to defaults if no meta-learning data available.
    
    Args:
        df: Training DataFrame
        
    Returns:
        Dict with recommended config:
        {
            "n_configs": 20,
            "epochs": 10,
            "d_model_choices": [64, 128],
            "layer_choices": [4, 6, 8],
            "head_choices": [2, 4, 8],
            "skip_pre_analysis": False,
            "predicted_params": {...} or None
        }
    """
    # Query meta-learning API
    query_result = query_optimal_parameters(df)
    
    if query_result and query_result.get('recommendation'):
        rec = query_result['recommendation']
        confidence = rec['confidence']
        
        if confidence > 0.9:
            # High confidence - use prediction directly, skip pre-analysis
            logger.info(f"🎯 High confidence ({confidence:.2f}) - using meta-learning prediction directly")
            return {
                "skip_pre_analysis": True,
                "predicted_params": {
                    "d_model": rec['d_model'],
                    "n_transformer_layers": rec['n_transformer_layers'],
                    "n_attention_heads": rec['n_attention_heads']
                },
                "confidence": confidence,
                "based_on_n_datasets": rec['based_on_n_datasets']
            }
        elif confidence > 0.7:
            # Medium confidence - quick validation with neighbors
            logger.info(f"🎯 Medium confidence ({confidence:.2f}) - quick validation around prediction")
            pred_d_model = rec['d_model']
            pred_layers = rec['n_transformer_layers']
            pred_heads = rec['n_attention_heads']
            
            # Test prediction + neighbors
            d_model_choices = [pred_d_model]
            if pred_d_model == 64:
                d_model_choices.append(96)
            elif pred_d_model == 128:
                d_model_choices.extend([96, 192])
            elif pred_d_model == 192:
                d_model_choices.append(128)
            
            layer_choices = [pred_layers, max(2, pred_layers - 2), min(10, pred_layers + 2)]
            head_choices = [pred_heads]
            
            return {
                "skip_pre_analysis": False,
                "n_configs": 5,  # Test just 5 configs
                "epochs": max(3, rec['pre_analysis_epochs'] // 2),  # Quick validation
                "d_model_choices": sorted(set(d_model_choices)),
                "layer_choices": sorted(set(layer_choices)),
                "head_choices": head_choices,
                "predicted_params": {
                    "d_model": pred_d_model,
                    "n_transformer_layers": pred_layers,
                    "n_attention_heads": pred_heads
                },
                "confidence": confidence
            }
        else:
            # Low confidence - full search but guided by prediction
            logger.info(f"🎯 Low confidence ({confidence:.2f}) - guided search")
            return {
                "skip_pre_analysis": False,
                "n_configs": 15,
                "epochs": rec['pre_analysis_epochs'],
                "d_model_choices": [64, 96, 128, 192],
                "layer_choices": [2, 3, 4, 6, 8],
                "head_choices": [2, 4, 8, 16],
                "predicted_params": {
                    "d_model": rec['d_model'],
                    "n_transformer_layers": rec['n_transformer_layers'],
                    "n_attention_heads": rec['n_attention_heads']
                },
                "confidence": confidence
            }
    else:
        # No meta-learning data - use adaptive defaults
        logger.info(f"ℹ️  No meta-learning data available - using adaptive defaults")
        n_rows = len(df)
        n_cols = len(df.columns) - 1
        
        # Adaptive based on dataset size
        if n_cols <= 10:
            d_model_choices = [64, 96]
        elif n_cols <= 30:
            d_model_choices = [96, 128]
        else:
            d_model_choices = [128, 192]
        
        if n_rows < 1000:
            layer_choices = [2, 3, 4]
        elif n_rows < 10000:
            layer_choices = [3, 4, 6]
        else:
            layer_choices = [4, 6, 8, 10]
        
        return {
            "skip_pre_analysis": False,
            "n_configs": 20,
            "epochs": 10,
            "d_model_choices": d_model_choices,
            "layer_choices": layer_choices,
            "head_choices": [2, 4, 8, 16],
            "predicted_params": None,
            "confidence": 0.0
        }


def query_existing_configs_for_dataset(
    df,
    min_epochs: int = 25,
    target_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query monitor.featrix.com for existing configs that have been trained on this dataset.
    
    This is used during bootstrapping phase to find configs that have already been
    trained for at least min_epochs epochs on this dataset, so we can pick the best
    one without doing new training.
    
    Args:
        df: Training DataFrame (for generating dataset identifier)
        min_epochs: Minimum epochs required (default: 25)
        target_type: Optional target type override
        
    Returns:
        List of config dicts with results, each containing:
        {
            "d_model": int,
            "n_transformer_layers": int,
            "n_attention_heads": int,
            "epochs_trained": int,
            "final_auc": float,
            "final_accuracy": float,
            "session_id": str,
            ...
        }
    """
    try:
        # Import featrix-monitor client library
        try:
            from featrix_monitor import create_client
        except ImportError as e:
            logger.error(f"❌ featrix-monitor package not installed: {e}")
            logger.error("Install with: pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
            return []
        
        # Generate dataset identifier
        dataset_chars = get_dataset_characteristics(df)
        dataset_hash = dataset_chars.get('column_names_hash')
        target_type = target_type or dataset_chars.get('target_type')
        
        logger.info(f"   🔍 Querying monitor.featrix.com for existing configs")
        logger.info(f"      Dataset hash: {dataset_hash[:16]}")
        logger.info(f"      Dataset: {dataset_chars['n_rows']} rows, {dataset_chars['n_cols']} cols, {target_type}")
        logger.info(f"      Minimum epochs: {min_epochs}")
        
        # Create client and query
        client = _create_monitor_client()
        # Note: These methods exist in the new featrix-monitor client
        result = client.query_dataset_configs(  # type: ignore[attr-defined]  # pylint: disable=no-member
            dataset_hash=dataset_hash,
            min_epochs=min_epochs,
            n_rows=dataset_chars['n_rows'],
            n_cols=dataset_chars['n_cols'],
            target_type=target_type
        )
        
        if result and result.get('configs'):
            configs = result['configs']
            total_found = result.get('total_configs_found', len(configs))
            
            # Filter out configs that are currently being trained (in progress)
            # These are marked by other instances to prevent duplicate training
            completed_configs = [c for c in configs if not c.get('training_in_progress', False)]
            in_progress_count = len(configs) - len(completed_configs)
            
            if in_progress_count > 0:
                logger.info(f"      ⏳ {in_progress_count} config(s) currently being trained by other instances (excluded)")
            
            logger.info(f"      ✅ Found {len(completed_configs)} completed configs on monitor.featrix.com")
            
            # Show performance range if available
            if completed_configs:
                aucs = [c.get('final_auc', 0) or 0 for c in completed_configs if c.get('final_auc')]
                if aucs:
                    logger.info(f"      Performance range: AUC {min(aucs):.4f} - {max(aucs):.4f}")
                epochs = [c.get('epochs_trained', 0) for c in completed_configs if c.get('epochs_trained')]
                if epochs:
                    logger.info(f"      Training range: {min(epochs)} - {max(epochs)} epochs")
            return completed_configs
        else:
            logger.info(f"      ℹ️  No existing configs found for this dataset")
            return []
        
    except Exception as e:
        logger.error(f"❌ Error querying existing configs: {e}")
        logger.debug(traceback.format_exc())
        return []


def mark_config_training_started(
    df,
    config: Dict[str, int],
    session_id: str,
    target_type: Optional[str] = None
) -> bool:
    """
    Mark a config as "training started" in monitor.featrix.com to prevent duplicate training.
    
    This should be called when training actually starts (not during pre-analysis).
    Monitor will mark this config as in-progress so other instances don't start training it.
    
    Args:
        df: Training DataFrame (for generating dataset identifier)
        config: Config dict with d_model, n_transformer_layers, n_attention_heads
        session_id: Session ID for this training run
        target_type: Optional target type override
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import featrix-monitor client library
        try:
            from featrix_monitor import create_client
        except ImportError as e:
            logger.error(f"❌ featrix-monitor package not installed: {e}")
            return False
        
        # Generate dataset identifier
        dataset_chars = get_dataset_characteristics(df)
        dataset_hash = dataset_chars.get('column_names_hash')
        target_type = target_type or dataset_chars.get('target_type')
        
        logger.info(f"🔒 Marking config as training started on monitor.featrix.com")
        logger.info(f"   Config: d_model={config.get('d_model')}, layers={config.get('n_transformer_layers')}, heads={config.get('n_attention_heads')}")
        logger.info(f"   Dataset hash: {dataset_hash[:16]}")
        
        # Create client and mark config as started
        client = _create_monitor_client()
        # Note: Method exists in new client but version wasn't bumped yet
        client.mark_config_training_started(  # type: ignore[attr-defined]  # pylint: disable=no-member
            dataset_hash=dataset_hash,
            d_model=config.get('d_model'),
            n_transformer_layers=config.get('n_transformer_layers'),
            n_attention_heads=config.get('n_attention_heads'),
            session_id=session_id,
            n_rows=dataset_chars['n_rows'],
            n_cols=dataset_chars['n_cols'],
            target_type=target_type
        )
        
        logger.info(f"✅ Config marked as training started (prevents duplicate training)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error marking config as training started: {e}")
        logger.debug(traceback.format_exc())
        return False


def register_experimental_configs(
    df,
    experimental_configs: List[Dict[str, int]],
    session_id: str,
    target_type: Optional[str] = None
) -> bool:
    """
    Register experimental configs with monitor.featrix.com so they can be tracked.
    
    This is called during pre-analysis when we generate new configs to try. Monitor
    will hold onto these configs and track them when they get trained later.
    
    Args:
        df: Training DataFrame (for generating dataset identifier)
        experimental_configs: List of config dicts, each with:
            {
                "d_model": int,
                "n_transformer_layers": int,
                "n_attention_heads": int
            }
        session_id: Session ID where these configs will be trained
        target_type: Optional target type override
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import featrix-monitor client library
        try:
            from featrix_monitor import create_client
        except ImportError as e:
            logger.error(f"❌ featrix-monitor package not installed: {e}")
            logger.error("Install with: pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
            return False
        
        # Generate dataset identifier
        dataset_chars = get_dataset_characteristics(df)
        dataset_hash = dataset_chars.get('column_names_hash')
        target_type = target_type or dataset_chars.get('target_type')
        
        logger.info(f"   📤 Registering {len(experimental_configs)} experimental configs with monitor.featrix.com")
        logger.info(f"      Dataset hash: {dataset_hash[:16]}")
        logger.info(f"      Dataset: {dataset_chars['n_rows']} rows, {dataset_chars['n_cols']} cols, {target_type}")
        logger.info(f"      Session ID: {session_id[:8]}...")
        
        # Create client and register configs
        client = _create_monitor_client()
        
        # Check if method exists (may not be available in all client versions)
        if not hasattr(client, 'register_experimental_configs'):
            logger.warning(f"      ⚠️  register_experimental_configs() not available in this client version")
            logger.warning(f"      Configs will not be pre-registered with monitor (this is non-fatal)")
            return False
        
        # Note: Method exists in new client but version wasn't bumped yet
        result = client.register_experimental_configs(  # type: ignore[attr-defined]  # pylint: disable=no-member
            dataset_hash=dataset_hash,
            configs=experimental_configs,
            session_id=session_id,
            n_rows=dataset_chars['n_rows'],
            n_cols=dataset_chars['n_cols'],
            target_type=target_type
        )
        
        if result and result.get('registered'):
            count = result.get('count', len(experimental_configs))
            logger.info(f"      ✅ Successfully registered {count}/{len(experimental_configs)} configs")
            logger.info(f"      Monitor will track these configs when training begins")
            return True
        else:
            logger.warning(f"      ⚠️  Registration returned: {result}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error registering experimental configs: {e}")
        logger.debug(traceback.format_exc())
        return False


def push_feature_engineering_suggestions(
    df,
    suggestions: List[Dict[str, Any]],
    session_id: str,
    job_id: Optional[str] = None,
    epoch: Optional[int] = None
) -> bool:
    """
    Push feature engineering suggestions to monitor.featrix.com for a dataset.
    
    Suggestions are keyed by dataset hash (column_names_hash) so they can be
    retrieved later when training on the same dataset.
    
    Args:
        df: pandas DataFrame (used to compute dataset hash)
        suggestions: List of feature engineering suggestion dicts
        session_id: Session ID where suggestions were generated
        job_id: Optional job ID
        epoch: Optional epoch number when suggestions were generated
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import featrix-monitor client library
        try:
            from featrix_monitor import create_client
        except ImportError as e:
            logger.error(f"❌ featrix-monitor package not installed: {e}")
            logger.error("Install with: pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
            return False
        
        # Generate dataset identifier
        dataset_chars = get_dataset_characteristics(df)
        dataset_hash = dataset_chars.get('column_names_hash')
        
        if not suggestions:
            logger.debug(f"   No feature suggestions to push for dataset {dataset_hash[:16]}")
            return True
        
        logger.info(f"   📤 Pushing {len(suggestions)} feature engineering suggestions to monitor")
        logger.info(f"      Dataset hash: {dataset_hash[:16]}")
        
        # Create client and push
        client = _create_monitor_client()
        # Note: This method needs to be added to the featrix-monitor client
        result = client.push_feature_suggestions(  # type: ignore[attr-defined]  # pylint: disable=no-member
            dataset_hash=dataset_hash,
            suggestions=suggestions,
            session_id=session_id,
            job_id=job_id,
            epoch=epoch,
            n_rows=dataset_chars['n_rows'],
            n_cols=dataset_chars['n_cols'],
            target_type=dataset_chars.get('target_type')
        )
        
        if result and result.get('success'):
            logger.info(f"      ✅ Successfully pushed {len(suggestions)} suggestions to monitor")
            return True
        else:
            logger.warning(f"      ⚠️  Failed to push suggestions: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error pushing feature suggestions: {e}")
        logger.debug(traceback.format_exc())
        return False


def retrieve_feature_engineering_suggestions(
    df,
    min_votes: int = 1,
    only_applied: bool = False
) -> List[Dict[str, Any]]:
    """
    Retrieve feature engineering suggestions from monitor.featrix.com for a dataset.
    
    Suggestions are retrieved by dataset hash (column_names_hash) and can be filtered
    by vote count and whether they were applied in previous training runs.
    
    Args:
        df: pandas DataFrame (used to compute dataset hash)
        min_votes: Minimum vote count for suggestions to include (default: 1)
        only_applied: If True, only return suggestions that were applied in previous runs
        
    Returns:
        List of feature engineering suggestion dicts, empty list if none found
    """
    try:
        # Import featrix-monitor client library
        try:
            from featrix_monitor import create_client
        except ImportError as e:
            logger.error(f"❌ featrix-monitor package not installed: {e}")
            logger.error("Install with: pip install --upgrade --extra-index-url https://bits.featrix.com/pypi/simple --trusted-host bits.featrix.com featrix-monitor")
            return []
        
        # Generate dataset identifier
        dataset_chars = get_dataset_characteristics(df)
        dataset_hash = dataset_chars.get('column_names_hash')
        
        logger.info(f"   🔍 Retrieving feature engineering suggestions from monitor")
        logger.info(f"      Dataset hash: {dataset_hash[:16]}")
        logger.info(f"      Min votes: {min_votes}, Only applied: {only_applied}")
        
        # Create client and query
        client = _create_monitor_client()
        # Note: This method needs to be added to the featrix-monitor client
        result = client.get_feature_suggestions(  # type: ignore[attr-defined]  # pylint: disable=no-member
            dataset_hash=dataset_hash,
            min_votes=min_votes,
            only_applied=only_applied
        )
        
        if result and result.get('suggestions'):
            suggestions = result['suggestions']
            logger.info(f"      ✅ Retrieved {len(suggestions)} feature suggestions from monitor")
            return suggestions
        else:
            logger.info(f"      ℹ️  No feature suggestions found for this dataset")
            return []
            
    except Exception as e:
        logger.error(f"❌ Error retrieving feature suggestions: {e}")
        logger.debug(traceback.format_exc())
        return []


# ============================================================================
# RELATIONSHIP HISTORY
# ============================================================================
# Use the existing feature suggestion infrastructure to store relationship
# pair usefulness. Each pair is stored as a feature suggestion with type
# "relationship_pair". This reuses push_feature_suggestions / get_feature_suggestions.
# ============================================================================

# Relationship pair data is stored as feature suggestions with:
# - suggestion_type: "relationship_pair"
# - columns: [col_a, col_b]
# - contribution: float score
# - was_pruned: bool
#
# Use push_feature_engineering_suggestions() to save
# Use retrieve_feature_engineering_suggestions() to load


# ============================================================================
# NEW META-LEARNING API (matching guide API)
# ============================================================================

def get_meta_next_config(
    n_rows: int,
    n_cols: int,
    target_type: str,
    min_epochs: int = 25
) -> Optional[Dict[str, Any]]:
    """
    Get the next untested config recommendation from the meta-learning API.
    
    This automatically tracks assignments to prevent parallel jobs from picking
    the same config. When you call this, the returned config is marked as
    "assigned" for 4 hours. If no training results are received within 4 hours,
    the assignment expires and the config becomes available again.
    
    Args:
        n_rows: Number of rows in the dataset
        n_cols: Number of columns (excluding target)
        target_type: Type of target ('binary_classification', 'multiclass_classification', 'regression')
        min_epochs: Minimum epochs required for configs to consider (default: 25)
        
    Returns:
        Dict with next_config and metadata, or None if no configs available:
        {
            'next_config': {
                'd_model': int,
                'n_transformer_layers': int,
                'n_attention_heads': int,
                'final_auc': float (if available),
                'source': str
            },
            'total_tested': int
        }
    """
    try:
        client = _create_monitor_client()
        
        # Call the featrix-monitor client method
        result = client.get_meta_next_config(  # type: ignore[attr-defined]  # pylint: disable=no-member
            n_rows=n_rows,
            n_cols=n_cols,
            target_type=target_type,
            min_epochs=min_epochs
        )
        
        if result and result.get('next_config'):
            config = result['next_config']
            logger.info(f"✅ Got next config recommendation:")
            logger.info(f"   d_model: {config.get('d_model')}")
            logger.info(f"   n_transformer_layers: {config.get('n_transformer_layers')}")
            logger.info(f"   n_attention_heads: {config.get('n_attention_heads')}")
            if config.get('final_auc'):
                logger.info(f"   Expected AUC: {config.get('final_auc'):.4f}")
            logger.info(f"   Source: {config.get('source', 'unknown')}")
            return result
        else:
            logger.info(f"ℹ️  No untested configs available")
            logger.info(f"   Total tested: {result.get('total_tested', 0) if result else 0}")
            return result
            
    except Exception as e:
        logger.error(f"❌ Error getting next config: {e}")
        logger.debug(traceback.format_exc())
        return None


def log_training_metadata_v2(
    n_rows: int,
    n_cols: int,
    target_type: str,
    optimal_parameters: Dict[str, int],
    pre_analysis_epochs: Optional[List[Dict[str, Any]]] = None,
    final_results: Optional[Dict[str, float]] = None
) -> Optional[str]:
    """
    Log training metadata to the meta-learning API (v2 - uses featrix-monitor client).
    
    This logs what configs were tried (pre_analysis_epochs) and what worked best
    (optimal_parameters + final_results) so the API can make better recommendations
    for future similar datasets.
    
    Args:
        n_rows: Number of rows in the dataset
        n_cols: Number of columns (excluding target)
        target_type: Type of target ('binary_classification', 'multiclass_classification', 'regression')
        optimal_parameters: The config that was chosen for final training:
            {
                'd_model': int,
                'n_transformer_layers': int,
                'n_attention_heads': int
            }
        pre_analysis_epochs: List of configs that were tested during pre-analysis
            (no training, no metrics - just to track what was tried):
            [
                {
                    'd_model': int,
                    'n_transformer_layers': int,
                    'n_attention_heads': int
                },
                ...
            ]
        final_results: Final training results from the optimal config:
            {
                'auc': float,
                'accuracy': float,
                'f1': float (optional)
            }
            
    Returns:
        metadata_id if successful, None otherwise
    """
    try:
        client = _create_monitor_client()
        
        # Call the featrix-monitor client method
        result = client.log_training_metadata(  # type: ignore[attr-defined]  # pylint: disable=no-member
            n_rows=n_rows,
            n_cols=n_cols,
            target_type=target_type,
            optimal_parameters=optimal_parameters,
            pre_analysis_epochs=pre_analysis_epochs or [],
            final_results=final_results or {}
        )
        
        if result and result.get('metadata_id'):
            metadata_id = result['metadata_id']
            logger.info(f"✅ Training metadata logged successfully: {metadata_id}")
            return metadata_id
        else:
            logger.warning(f"⚠️  Failed to log training metadata: {result}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error logging training metadata: {e}")
        logger.debug(traceback.format_exc())
        return None
