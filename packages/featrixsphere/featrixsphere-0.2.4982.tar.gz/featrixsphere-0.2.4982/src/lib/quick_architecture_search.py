"""
Quick Architecture Search

BOOTSTRAPPING MODE (default):
- Queries monitor.featrix.com for existing configs trained on this dataset
- If >= 25 configs found: picks the best one from existing results
- If < 25 configs found: generates new experimental configs to try (no training during pre-analysis)

LEGACY MODE (query_mode=False):
- Trains configs during pre-analysis (original behavior)
"""
import logging
import random
import asyncio
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List
from itertools import product
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Import logging config functions for analysis step tracking
from featrix.neural.logging_config import set_anal_step, clear_anal_step

# Import query function for bootstrapping mode
from lib.meta_learning_client import query_existing_configs_for_dataset, get_dataset_characteristics, register_experimental_configs


def analyze_dataset(df) -> Dict[str, List[int]]:
    """
    Analyze dataset to determine intelligent search space.

    Args:
        df: Training DataFrame

    Returns:
        Dict with parameter choices based on dataset size/complexity
    """
    n_rows = len(df)
    n_cols = len(df.columns) - 1  # Exclude target

    # Adaptive d_model based on columns
    if n_cols <= 10:
        d_model_choices = [64, 96]
    elif n_cols <= 30:
        d_model_choices = [96, 128]
    elif n_cols <= 60:
        d_model_choices = [128, 192]
    else:
        # Large datasets (60+ columns) - need more capacity
        d_model_choices = [192, 256]

    # Adaptive layers based on rows (more data = can go deeper)
    if n_rows < 1000:
        layer_choices = [2, 3, 4]  # Shallow - avoid overfitting
    elif n_rows < 10000:
        layer_choices = [3, 4, 6]
    else:
        layer_choices = [4, 6, 8, 10]  # Deep - can handle complexity

    # Heads: Keep 8-32 dims per head (d_model / n_heads)
    # For large datasets (60+ columns), allow up to 32 heads for complex interactions
    max_heads = 32 if n_cols >= 60 else 16
    head_options = [h for h in [2, 4, 8, 16, 32] if h <= max_heads]

    head_choices = []
    for d in d_model_choices:
        # Add heads that give reasonable dims/head
        for h in head_options:
            dims_per_head = d / h
            if 8 <= dims_per_head <= 32:  # Sweet spot
                if h not in head_choices:
                    head_choices.append(h)
    head_choices.sort()

    logger.info(f"📊 Dataset analysis:")
    logger.info(f"   {n_rows} rows, {n_cols} columns")
    logger.info(f"   Search space: d_model={d_model_choices}, layers={layer_choices}, heads={head_choices}")

    return {
        'd_model': d_model_choices,
        'n_transformer_layers': layer_choices,
        'n_attention_heads': head_choices,
    }


def sample_configs(search_space: Dict[str, List], n_samples: int = 20) -> List[Dict[str, int]]:
    """
    Sample configurations intelligently from search space.

    Strategy:
    - Always test extremes (min/max of each dimension)
    - Random sample the middle

    Args:
        search_space: Dict of parameter choices
        n_samples: Number of configs to sample

    Returns:
        List of config dicts
    """
    all_configs = list(product(
        search_space['d_model'],
        search_space['n_transformer_layers'],
        search_space['n_attention_heads']
    ))

    if len(all_configs) <= n_samples:
        # Small space - test everything
        configs = all_configs
    else:
        # Sample strategically
        configs_to_test = set()

        # Add corner cases (min/max combinations)
        configs_to_test.add(all_configs[0])   # Min everything
        configs_to_test.add(all_configs[-1])  # Max everything

        # Add mid-range
        mid_idx = len(all_configs) // 2
        if mid_idx < len(all_configs):
            configs_to_test.add(all_configs[mid_idx])

        # Random sample the rest
        remaining = n_samples - len(configs_to_test)
        if remaining > 0:
            available = [c for c in all_configs if c not in configs_to_test]
            if available:
                sampled = random.sample(available, min(remaining, len(available)))
                configs_to_test.update(sampled)

        configs = list(configs_to_test)

    # Convert to list of dicts
    config_dicts = [
        {
            'd_model': d,
            'n_transformer_layers': layers,
            'n_attention_heads': heads
        }
        for d, layers, heads in configs
    ]

    logger.info(f"🎲 Sampled {len(config_dicts)} configurations to test")

    return config_dicts


def run_quick_architecture_search(data_file: str, strings_cache: str, session_id: str,
                                   n_samples: int = 20, quick_epochs: int = 25,
                                   suggested_configs: List[Dict[str, int]] = None,
                                   job_id: str = None,
                                   target_column_hint: str = None,
                                   query_mode: bool = True,
                                   min_existing_configs: int = 25,
                                   min_epochs_required: int = 25) -> Dict[str, Any]:
    """
    Run quick architecture search on a dataset.

    BOOTSTRAPPING MODE (query_mode=True, default):
    - Queries monitor.featrix.com for existing configs trained on this dataset
    - If >= min_existing_configs (25) found: picks the best one from existing results
    - If < min_existing_configs found: generates new experimental set (but does NOT train)
    - NO TRAINING is done during pre-analysis

    Args:
        data_file: Path to SQLite database
        strings_cache: Path to strings cache (not used in query mode)
        session_id: Session ID (for loading data)
        n_samples: Number of experimental configs to generate if no existing configs found
        quick_epochs: Not used (kept for backward compatibility)
        suggested_configs: Optional list of specific configs to use if generating experimental set
                          Format: [{"d_model": 128, "n_transformer_layers": 6, "n_attention_heads": 8}, ...]
        query_mode: If True, query existing configs (bootstrapping mode, default)
        min_existing_configs: Target number of existing configs (default: 25, but will use best available)
        min_epochs_required: Minimum epochs required for a config to be considered (default: 25)

    Returns:
        Dict with optimal config (either from existing results or experimental set)
    """
    from featrix.neural.input_data_file import FeatrixInputDataFile
    from featrix.neural.input_data_set import FeatrixInputDataSet
    from featrix.neural.embedded_space import EmbeddingSpace
    from featrix.neural.single_predictor import FeatrixSinglePredictor
    from featrix.neural.simple_mlp import SimpleMLP
    from featrix.neural.model_config import SimpleMLPConfig
    import pandas as pd

    logger.info(f"📂 Loading dataset from: {data_file}")

    # Load data from SQLite database created by create_structured_data
    # NOTE: We use the data_file parameter (SQLite DB), NOT session.get('input_data') (original upload)
    if not data_file:
        from lib.session_manager import load_session

        # DEFENSIVE: Retry loading session to wait for sqlite_db to appear
        # This handles race condition where create_structured_data hasn't fully persisted yet
        max_retries = 6  # 6 retries = up to 30 seconds
        retry_sleep = 5  # 5 seconds between retries

        for attempt in range(max_retries):
            session = load_session(session_id)
            data_file = session.get('sqlite_db')

            if data_file:
                if attempt > 0:
                    logger.info(f"✅ Found sqlite_db after {attempt} retries ({attempt * retry_sleep}s)")
                break

            if attempt < max_retries - 1:
                logger.warning(f"⏳ sqlite_db not found in session yet, waiting {retry_sleep}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_sleep)
            else:
                # Final attempt failed
                raise ValueError(f"No data_file provided and session {session_id} has no sqlite_db after {max_retries * retry_sleep}s")

    # Load from SQLite database
    input_file = FeatrixInputDataFile(str(data_file))
    df = input_file.df

    logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns from SQLite database")

    # BOOTSTRAPPING MODE: Query existing configs instead of training
    if query_mode:
        logger.info("=" * 80)
        logger.info("🔍 BOOTSTRAPPING MODE: Querying monitor.featrix.com for existing configs")
        logger.info("=" * 80)

        # Get dataset characteristics for target type
        dataset_chars = get_dataset_characteristics(df)
        target_type = dataset_chars.get('target_type')

        # Query for existing configs
        existing_configs = query_existing_configs_for_dataset(
            df=df,
            min_epochs=min_epochs_required,
            target_type=target_type
        )

        logger.info("=" * 80)
        logger.info(f"📊 QUERY RESULTS: Found {len(existing_configs)} existing configs (need {min_existing_configs})")
        logger.info(f"   Dataset: {dataset_chars['n_rows']} rows, {dataset_chars['n_cols']} cols, {target_type}")
        logger.info(f"   Dataset hash: {dataset_chars.get('column_names_hash', 'unknown')[:16]}")
        logger.info("=" * 80)

        # If we have enough configs, pick the best one
        if len(existing_configs) >= min_existing_configs:
            logger.info("")
            logger.info("✅ SUFFICIENT CONFIGS FOUND - Selecting best from existing results")
            logger.info(f"   Found: {len(existing_configs)} configs (need: {min_existing_configs})")
            logger.info(f"   Status: Ready to use existing results")

            # Sort by performance (AUC > accuracy > epochs)
            def config_score(config):
                auc = config.get('final_auc', 0) or 0
                accuracy = config.get('final_accuracy', 0) or 0
                epochs = config.get('epochs_trained', 0) or 0
                # Primary: AUC, Secondary: accuracy, Tertiary: epochs
                return (auc, accuracy, epochs)

            existing_configs.sort(key=config_score, reverse=True)
            best_config = existing_configs[0]

            optimal_config = {
                'd_model': best_config['d_model'],
                'n_transformer_layers': best_config['n_transformer_layers'],
                'n_attention_heads': best_config['n_attention_heads'],
                'estimated_auc': best_config.get('final_auc', 0),
                'configs_found': len(existing_configs),
                'configs_used': min_existing_configs,
                'source': 'monitor_query',
                'session_id': best_config.get('session_id')
            }

            logger.info("")
            logger.info("🏆 SELECTED OPTIMAL CONFIG FROM EXISTING RESULTS:")
            logger.info(f"   Architecture: d_model={optimal_config['d_model']}, layers={optimal_config['n_transformer_layers']}, heads={optimal_config['n_attention_heads']}")
            logger.info(f"   Performance: AUC={best_config.get('final_auc', 'N/A'):.4f}, Accuracy={best_config.get('final_accuracy', 'N/A'):.4f}")
            logger.info(f"   Training: {best_config.get('epochs_trained', 'N/A')} epochs")
            logger.info(f"   Source: {best_config.get('session_id', 'N/A')[:8]}...")
            logger.info(f"   Total configs evaluated: {len(existing_configs)}")

            # Save to session
            try:
                from lib.session_manager import load_session, save_session
                session = load_session(session_id)
                session['pre_analysis_results'] = {
                    'all_tested_configs': existing_configs[:min_existing_configs],  # Top N
                    'optimal_config': optimal_config,
                    'total_configs_found': len(existing_configs),
                    'query_mode': True,
                    'source': 'monitor_query'
                }
                save_session(session_id, session, exist_ok=True)
                logger.info(f"💾 Saved query results to session")
            except Exception as e:
                logger.warning(f"⚠️  Failed to save query results to session: {e}")

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ PRE-ANALYSIS COMPLETE: Using existing optimal config")
            logger.info("=" * 80)
            logger.info("")

            return optimal_config

        else:
            # Not enough configs exist yet (< min_existing_configs) - generate new experimental set
            logger.info("")
            logger.info("⚠️  INSUFFICIENT CONFIGS - Generating new experimental set")
            logger.info(f"   Found: {len(existing_configs)} configs (need: {min_existing_configs})")
            logger.info(f"   Action: Generating {n_samples} new experimental configs to try")
            logger.info(f"   Note: These configs will be trained later (not during pre-analysis)")
            logger.info("")

            # Generate experimental configs to train
            if suggested_configs:
                logger.info("🎯 USING META-LEARNING SUGGESTIONS:")
                logger.info(f"   Source: Meta-learning API recommendations")
                logger.info(f"   Count: {len(suggested_configs)} suggested configs")
                experimental_configs = suggested_configs
            else:
                # Analyze dataset to determine search space
                logger.info("🔍 ANALYZING DATASET TO DETERMINE SEARCH SPACE:")
                search_space = analyze_dataset(df)
                logger.info(f"   Search space size: {len(search_space['d_model'])} d_models × {len(search_space['n_transformer_layers'])} layers × {len(search_space['n_attention_heads'])} heads")
                
                # Sample configurations
                logger.info(f"")
                logger.info(f"🎲 SAMPLING {n_samples} CONFIGURATIONS:")
                experimental_configs = sample_configs(search_space, n_samples=n_samples)
                logger.info(f"   Generated: {len(experimental_configs)} experimental configs")
                logger.info(f"   Strategy: Corner cases (min/max/mid) + random sampling")

            # Pick first one as "optimal" for now (will be updated after training)
            first_config = experimental_configs[0]
            optimal_config = {
                'd_model': first_config['d_model'],
                'n_transformer_layers': first_config['n_transformer_layers'],
                'n_attention_heads': first_config['n_attention_heads'],
                'estimated_auc': 0,
                'configs_found': len(existing_configs),
                'experimental_configs': experimental_configs,
                'source': 'experimental_set',
                'needs_training': True
            }

            logger.info("")
            logger.info("📋 EXPERIMENTAL CONFIG SET GENERATED:")
            logger.info(f"   Total configs: {len(experimental_configs)}")
            logger.info(f"   Initial selection: d_model={optimal_config['d_model']}, layers={optimal_config['n_transformer_layers']}, heads={optimal_config['n_attention_heads']}")
            logger.info(f"   Status: ⚠️  These configs need to be trained (not done in pre-analysis)")
            logger.info("")
            
            # Show first few configs for visibility
            logger.info("📝 EXPERIMENTAL CONFIGS TO TRY:")
            for i, config in enumerate(experimental_configs[:5], 1):
                marker = "👉" if i == 1 else "  "
                logger.info(f"   {marker} Config {i}: d_model={config['d_model']}, layers={config['n_transformer_layers']}, heads={config['n_attention_heads']}")
            if len(experimental_configs) > 5:
                logger.info(f"   ... and {len(experimental_configs) - 5} more configs")
            logger.info("")

            # Register experimental configs with monitor so they can be tracked
            logger.info("📤 REGISTERING EXPERIMENTAL CONFIGS WITH MONITOR:")
            try:
                dataset_chars = get_dataset_characteristics(df)
                target_type = dataset_chars.get('target_type')
                success = register_experimental_configs(
                    df=df,
                    experimental_configs=experimental_configs,
                    session_id=session_id,
                    target_type=target_type
                )
                if success:
                    logger.info(f"   ✅ Successfully registered {len(experimental_configs)} configs with monitor.featrix.com")
                    logger.info(f"   Monitor will track these configs when they are trained")
                else:
                    logger.warning(f"   ⚠️  Registration returned False (may have partially succeeded)")
            except Exception as e:
                logger.warning(f"   ❌ Failed to register experimental configs with monitor: {e}")
                logger.warning(f"   Continuing anyway - configs saved to session")
                # Don't fail pre-analysis if monitor registration fails
            logger.info("")

            # Save to session (include existing configs if any)
            try:
                from lib.session_manager import load_session, save_session
                session = load_session(session_id)
                session['pre_analysis_results'] = {
                    'experimental_configs': experimental_configs,
                    'optimal_config': optimal_config,
                    'total_configs_found': len(existing_configs),
                    'existing_configs': existing_configs if existing_configs else [],
                    'query_mode': True,
                    'source': 'experimental_set',
                    'needs_training': True
                }
                save_session(session_id, session, exist_ok=True)
                logger.info(f"💾 Saved experimental configs to session")
            except Exception as e:
                logger.warning(f"⚠️  Failed to save experimental configs to session: {e}")

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ PRE-ANALYSIS COMPLETE: Generated experimental configs")
            logger.info("=" * 80)
            logger.info(f"   Summary:")
            logger.info(f"   • Existing configs found: {len(existing_configs)}")
            logger.info(f"   • Experimental configs generated: {len(experimental_configs)}")
            logger.info(f"   • Initial config selected: d_model={optimal_config['d_model']}, layers={optimal_config['n_transformer_layers']}, heads={optimal_config['n_attention_heads']}")
            logger.info(f"   • Next step: These configs will be trained to find the best one")
            logger.info("=" * 80)
            logger.info("")

            return optimal_config

    # If we get here, query_mode was False - this shouldn't happen in bootstrapping mode
    logger.warning("⚠️  Legacy training mode - this should not be used in bootstrapping phase")
    raise RuntimeError("Pre-analysis training mode is disabled. Use query_mode=True for bootstrapping.")
