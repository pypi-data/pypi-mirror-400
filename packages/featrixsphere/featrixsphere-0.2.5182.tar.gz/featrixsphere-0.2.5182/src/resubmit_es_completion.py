#!/usr/bin/env python3
"""
Re-submit Embedding Space training completion to monitor API.

This tool loads a completed ES training session and re-submits the training data
to the monitor API with all required fields (including classification metrics
that don't apply to ES training but are now required by the API).
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple
import traceback

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from lib.session_manager import load_session, iterate_over_sessions
from lib.training_monitor import collect_es_training_data, post_training_data
from lib.featrix.neural.io_utils import load_embedded_space
from featrix.neural.input_data_file import FeatrixInputDataFile
from config import config
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_minimal_dataframes_from_codecs(es, training_info):
    """
    Create minimal dataframes from embedding space codecs for statistics collection.
    
    We don't need the actual data - just column names and row counts for get_column_statistics.
    The codecs contain all the statistical information we need.
    
    Returns:
        tuple: (train_df, val_df) - minimal dataframes with just column structure
    """
    # Get column names from codecs
    codecs = getattr(es, 'col_codecs', {})
    if not codecs:
        return None, None
    
    column_names = list(codecs.keys())
    
    # Try to get row counts from training_info
    train_size = None
    val_size = None
    
    if training_info:
        # Check for dataset sizes in training_info
        if 'train_size' in training_info:
            train_size = training_info['train_size']
        elif 'training_size' in training_info:
            train_size = training_info['training_size']
        
        if 'val_size' in training_info:
            val_size = training_info['val_size']
        elif 'validation_size' in training_info:
            val_size = training_info['validation_size']
    
    # If we can't determine sizes, estimate from combined size if available
    if train_size is None or val_size is None:
        combined_size = None
        if training_info:
            if 'input_rows' in training_info:
                combined_size = training_info['input_rows']
            elif 'total_rows' in training_info:
                combined_size = training_info['total_rows']
        
        if combined_size:
            # Default 80/20 split if we don't know the actual split
            if train_size is None:
                train_size = int(combined_size * 0.8)
            if val_size is None:
                val_size = combined_size - train_size
        else:
            # Last resort: use a reasonable default
            train_size = 1000
            val_size = 200
            logger.warning(f"⚠️  Could not determine dataset sizes, using defaults: train={train_size}, val={val_size}")
    
    # Create minimal dataframes with just the column structure
    # We'll use empty dataframes - get_column_statistics will use codecs for actual stats
    train_df = pd.DataFrame(columns=column_names, index=range(train_size))
    val_df = pd.DataFrame(columns=column_names, index=range(val_size))
    
    logger.info(f"📊 Created minimal dataframes from codecs: {len(column_names)} columns, train={train_size} rows, val={val_size} rows")
    
    return train_df, val_df


def load_es_and_dataframes(session_id: str):
    """
    Load embedding space and reconstruct train/val dataframes from session.
    
    Tries multiple strategies:
    1. Use dataframes from embedding space if available
    2. Load from input data file if available
    3. Create minimal dataframes from codecs (metadata-only approach)
    
    Returns:
        tuple: (embedding_space, train_df, val_df, training_info)
    """
    logger.info(f"🔍 Loading session {session_id}...")
    session = load_session(session_id)
    
    if not session:
        raise ValueError(f"Session {session_id} not found")
    
    # Get embedding space path
    es_path = session.get('embedding_space')
    if not es_path or not Path(es_path).exists():
        raise ValueError(f"Embedding space not found: {es_path}")
    
    logger.info(f"📦 Loading embedding space from {es_path}...")
    es = load_embedded_space(es_path)
    
    # Get training info from embedding space
    training_info = getattr(es, 'training_info', {})
    
    # Strategy 1: Try to get train/val split from embedding space first (most reliable)
    train_df = None
    val_df = None
    
    if hasattr(es, 'train_input_data') and es.train_input_data is not None:
        if hasattr(es.train_input_data, 'df'):
            train_df = es.train_input_data.df
            logger.info(f"✅ Found train_df from embedding space: {len(train_df)} rows")
    
    if hasattr(es, 'val_input_data') and es.val_input_data is not None:
        if hasattr(es.val_input_data, 'df'):
            val_df = es.val_input_data.df
            logger.info(f"✅ Found val_df from embedding space: {len(val_df)} rows")
    
    # If we have both train and val from embedding space, we're done
    if train_df is not None and val_df is not None:
        return es, train_df, val_df, training_info
    
    # Strategy 2: Try to load from input data file
    input_data_path = session.get('input_data') or session.get('input_filename')
    
    # If no input_data in this session, check if it's a single predictor session
    # and try to get input data from the foundation model session
    if not input_data_path:
        foundation_model_id = session.get('foundation_model_id')
        if foundation_model_id:
            logger.info(f"🔍 Single predictor session - checking foundation model {foundation_model_id}...")
            try:
                foundation_session = load_session(foundation_model_id)
                if foundation_session:
                    input_data_path = foundation_session.get('input_data') or foundation_session.get('input_filename')
                    if input_data_path:
                        logger.info(f"✅ Found input_data from foundation model session: {input_data_path}")
            except Exception as e:
                logger.warning(f"⚠️  Could not load foundation model session: {e}")
    
    # Try to find and load the input data file
    if input_data_path:
        input_data_path = Path(input_data_path)
        if not input_data_path.exists():
            # Try relative to session directory
            session_dir = config.session_dir / session_id
            candidate_path = session_dir / input_data_path.name
            if candidate_path.exists():
                input_data_path = candidate_path
            else:
                # Try foundation model session directory
                foundation_model_id = session.get('foundation_model_id')
                if foundation_model_id:
                    foundation_dir = config.session_dir / foundation_model_id
                    candidate_path = foundation_dir / input_data_path.name
                    if candidate_path.exists():
                        input_data_path = candidate_path
                        logger.info(f"✅ Found input_data in foundation model session directory: {input_data_path}")
        
        # Try to load the file
        if input_data_path.exists():
            logger.info(f"📊 Loading input data from {input_data_path}...")
            try:
                input_data_file = FeatrixInputDataFile(str(input_data_path))
                full_df = input_data_file.df
                
                # Use full_df if we don't have train/val from embedding space
                if train_df is None:
                    logger.info("📊 Using full dataframe for training data")
                    train_df = full_df
                
                if val_df is None:
                    logger.info("📊 Using full dataframe for validation data")
                    val_df = full_df
                
                return es, train_df, val_df, training_info
            except Exception as e:
                logger.warning(f"⚠️  Failed to load input data file: {e}")
                # Fall through to Strategy 3
    
    # Strategy 3: Use what we have from embedding space (partial dataframes)
    if train_df is not None:
        logger.info("📊 Using train_df from embedding space for both train and val")
        val_df = train_df if val_df is None else val_df
        return es, train_df, val_df, training_info
    
    if val_df is not None:
        logger.info("📊 Using val_df from embedding space for both train and val")
        train_df = val_df
        return es, train_df, val_df, training_info
    
    # Strategy 4: Create minimal dataframes from codecs (metadata-only approach)
    # This is the fallback - we use codec metadata which has all the stats we need
    logger.info("📊 Creating minimal dataframes from embedding space codecs (metadata-only approach)...")
    train_df, val_df = create_minimal_dataframes_from_codecs(es, training_info)
    
    if train_df is not None and val_df is not None:
        logger.info("✅ Using codec metadata for column statistics (no actual data needed)")
        return es, train_df, val_df, training_info
    
    # If all strategies fail
    raise ValueError(
        f"Session {session_id}: Could not find dataframes, input data file, or codecs. "
        f"Embedding space has col_codecs: {hasattr(es, 'col_codecs') and bool(getattr(es, 'col_codecs', {}))}"
    )


def estimate_training_times(training_info, epochs: int):
    """
    Estimate training start and end times from training info or use defaults.
    
    Returns:
        tuple: (training_start_time, training_end_time)
    """
    # Try to get actual times from training_info
    if training_info:
        progress_info = training_info.get('progress_info', {})
        if 'training_start_time' in progress_info:
            try:
                start_time = datetime.fromisoformat(progress_info['training_start_time'])
            except:
                start_time = None
        else:
            start_time = None
        
        if start_time:
            # Estimate end time based on epochs and a reasonable time per epoch
            # Default to 30 seconds per epoch if we can't determine it
            time_per_epoch = 30.0
            if 'time_taken' in training_info:
                time_taken = training_info['time_taken']
                if isinstance(time_taken, (int, float)) and epochs > 0:
                    time_per_epoch = time_taken / epochs
            
            end_time = start_time + timedelta(seconds=time_per_epoch * epochs)
            return start_time, end_time
    
    # Fallback: use current time minus estimated duration
    # Assume 30 seconds per epoch as default
    estimated_duration = epochs * 30
    end_time = datetime.now()
    start_time = end_time - timedelta(seconds=estimated_duration)
    
    logger.warning(f"⚠️  Could not determine actual training times, using estimates")
    logger.warning(f"   Start: {start_time.isoformat()}")
    logger.warning(f"   End: {end_time.isoformat()}")
    
    return start_time, end_time


def get_training_parameters(es, training_info, session):
    """
    Extract training parameters from embedding space, training info, and session.
    
    Returns:
        tuple: (epochs, batch_size, learning_rate)
    """
    # Get epochs
    epochs = None
    if training_info:
        epochs = training_info.get('epochs_trained')
        if epochs is None:
            epochs = training_info.get('n_epochs')
    
    if epochs is None:
        epochs = session.get('n_epochs', 0)
    
    if epochs is None or epochs == 0:
        # Try to infer from training timeline
        if hasattr(es, '_training_timeline') and es._training_timeline:
            epochs = len(es._training_timeline)
        else:
            epochs = 100  # Default fallback
            logger.warning(f"⚠️  Could not determine epochs, using default: {epochs}")
    
    # Get batch size
    batch_size = None
    if training_info:
        batch_size = training_info.get('batch_size')
    
    if batch_size is None:
        batch_size = session.get('batch_size', 64)  # Default
    
    # Get learning rate
    learning_rate = None
    if training_info:
        learning_rate = training_info.get('learning_rate')
    
    if learning_rate is None:
        learning_rate = 0.001  # Default
    
    logger.info(f"📋 Training parameters:")
    logger.info(f"   Epochs: {epochs}")
    logger.info(f"   Batch size: {batch_size}")
    logger.info(f"   Learning rate: {learning_rate}")
    
    return epochs, batch_size, learning_rate


def resubmit_es_completion(
    session_id: str,
    monitor_url: str = "https://monitor.featrix.com/training",
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Re-submit ES training completion data to monitor API.
    
    Args:
        session_id: Session ID of the completed ES training
        monitor_url: Monitor API URL (default: https://monitor.featrix.com/training)
        dry_run: If True, don't actually submit, just validate
        
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        if not dry_run:
            logger.info("=" * 80)
            logger.info(f"🔄 RE-SUBMITTING ES TRAINING COMPLETION")
            logger.info(f"   Session ID: {session_id}")
            logger.info("=" * 80)
        else:
            logger.info(f"🔍 [DRY RUN] Validating session {session_id}...")
        
        # Load embedding space - we don't need dataframes, codecs have all the stats
        logger.info(f"🔍 Loading session {session_id}...")
        session = load_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Get embedding space path
        es_path = session.get('embedding_space')
        if not es_path or not Path(es_path).exists():
            raise ValueError(f"Embedding space not found: {es_path}")
        
        logger.info(f"📦 Loading embedding space from {es_path}...")
        es = load_embedded_space(es_path)
        
        # Get training info from embedding space
        training_info = getattr(es, 'training_info', {})
        
        # We don't need to load dataframes - codecs and detectors have all the statistics
        # Just pass None and collect_es_training_data will extract everything from codecs
        train_df = None
        val_df = None
        
        # Load session for additional metadata
        session = load_session(session_id)
        
        # Get training parameters
        epochs, batch_size, learning_rate = get_training_parameters(es, training_info, session)
        
        # Estimate training times
        training_start_time, training_end_time = estimate_training_times(training_info, epochs)
        
        # Get metadata from session
        customer_id = session.get('customer_id')
        remote_hostname = session.get('remote_hostname')
        s3_path = session.get('s3_path')
        deployment_id = session.get('deployment_id')
        
        # Build optimal_params from embedding space
        optimal_params = {
            "d_model": getattr(es, 'd_model', None),
            "n_transformer_layers": getattr(es, 'n_transformer_layers', None),
            "n_attention_heads": getattr(es, 'n_attention_heads', None),
        }
        
        # Collect training data
        # NOTE: We pass None for train_df/val_df - collect_es_training_data will
        # extract everything from codecs and detectors (which already have all the stats
        # computed during ES creation - no need to re-inspect dataframes!)
        if not dry_run:
            logger.info("📊 Collecting training data from embedding space codecs/detectors (no dataframe loading needed)...")
        training_data = collect_es_training_data(
            embedding_space=es,
            train_df=None,  # None - codecs/detectors have all stats already computed
            val_df=None,  # None - codecs/detectors have all stats already computed
            training_start_time=training_start_time,
            training_end_time=training_end_time,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            customer_id=customer_id,
            remote_hostname=remote_hostname,
            s3_path=s3_path,
            session_id=session_id,
            deployment_id=deployment_id,
            optimal_params=optimal_params,
        )
        
        # Add required classification metrics (API now requires these even for ES training)
        # For embedding space training, these don't apply, so we set them to None
        if not dry_run:
            logger.info("➕ Adding required classification metrics (None for ES training)...")
        training_data["precision"] = None
        training_data["recall"] = None
        training_data["f1"] = None
        training_data["auc"] = None
        training_data["accuracy"] = None
        
        if dry_run:
            logger.info(f"✅ [DRY RUN] Session {session_id} is valid and ready to submit")
            return True, ""
        
        # Post to monitor API
        logger.info("=" * 80)
        logger.info("📤 POSTING TO MONITOR API")
        logger.info("=" * 80)
        
        success = post_training_data(training_data, monitor_url=monitor_url)
        
        if success:
            logger.info("=" * 80)
            logger.info("✅ SUCCESSFULLY RE-SUBMITTED ES TRAINING COMPLETION")
            logger.info("=" * 80)
            return True, ""
        else:
            logger.error("=" * 80)
            logger.error("❌ FAILED TO RE-SUBMIT ES TRAINING COMPLETION")
            logger.error("=" * 80)
            return False, "Failed to post to monitor API"
            
    except Exception as e:
        error_msg = f"{e}"
        if not dry_run:
            logger.error("=" * 80)
            logger.error(f"❌ ERROR RE-SUBMITTING ES TRAINING COMPLETION")
            logger.error(f"   Error: {e}")
            logger.error(f"   Traceback:\n{traceback.format_exc()}")
            logger.error("=" * 80)
        else:
            logger.warning(f"⚠️  [DRY RUN] Error validating {session_id}: {e}")
        return False, error_msg


def find_sessions_with_es(limit: int = None, recent: int = None):
    """
    Find all sessions that have completed ES training (have embedding_space).
    
    Args:
        limit: Maximum number of sessions to return
        recent: Only return N most recent sessions (by file mtime)
        
    Returns:
        List of session IDs with embedding spaces
    """
    sessions_with_es = []
    
    # Get all session files
    if not config.session_dir.exists():
        logger.warning(f"⚠️  Session directory does not exist: {config.session_dir}")
        return sessions_with_es
    
    session_files = list(config.session_dir.glob("*.session"))
    
    # Filter out temp and lock files
    session_files = [f for f in session_files if not f.name.endswith(('.tmp', '.lock'))]
    
    # Sort by modification time if --recent is specified
    if recent:
        session_files = sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True)
        session_files = session_files[:recent]
    
    logger.info(f"🔍 Scanning {len(session_files)} session files for ES training completions...")
    
    for session_file in session_files:
        session_id = session_file.stem
        try:
            session = load_session(session_id)
            if not session:
                continue
            
            # Check if session has embedding_space
            es_path = session.get('embedding_space')
            if es_path and Path(es_path).exists():
                sessions_with_es.append(session_id)
                if limit and len(sessions_with_es) >= limit:
                    break
        except Exception as e:
            # Skip corrupted or problematic sessions
            logger.debug(f"Skipping session {session_id}: {e}")
            continue
    
    return sessions_with_es


def resubmit_all_sessions(
    monitor_url: str = "https://monitor.featrix.com/training",
    dry_run: bool = False,
    limit: int = None,
    recent: int = None
):
    """
    Re-submit ES training completion for all sessions that have completed ES training.
    
    Args:
        monitor_url: Monitor API URL
        dry_run: If True, don't actually submit, just validate
        limit: Maximum number of sessions to process
        recent: Only process N most recent sessions
    """
    logger.info("=" * 80)
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No data will be submitted")
    logger.info("🔄 BULK RE-SUBMISSION OF ES TRAINING COMPLETIONS")
    logger.info("=" * 80)
    
    # Find all sessions with ES training
    session_ids = find_sessions_with_es(limit=limit, recent=recent)
    
    if not session_ids:
        logger.warning("⚠️  No sessions with completed ES training found")
        return 1
    
    logger.info(f"📊 Found {len(session_ids)} sessions with completed ES training")
    if limit:
        logger.info(f"   Limited to {limit} sessions")
    if recent:
        logger.info(f"   Processing {recent} most recent sessions")
    logger.info("")
    
    # Process each session
    success_count = 0
    error_count = 0
    errors = []
    
    for idx, session_id in enumerate(session_ids, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing session {idx}/{len(session_ids)}: {session_id}")
        logger.info(f"{'='*80}")
        
        success, error_msg = resubmit_es_completion(
            session_id=session_id,
            monitor_url=monitor_url,
            dry_run=dry_run
        )
        
        if success:
            success_count += 1
        else:
            error_count += 1
            errors.append((session_id, error_msg))
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 BULK RE-SUBMISSION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total sessions processed: {len(session_ids)}")
    logger.info(f"✅ Successful: {success_count}")
    logger.info(f"❌ Failed: {error_count}")
    
    if errors:
        logger.info("\nFailed sessions:")
        for session_id, error_msg in errors:
            logger.info(f"  - {session_id}: {error_msg[:100]}")
    
    if dry_run:
        logger.info("\n[DRY RUN MODE - No data was actually submitted]")
    
    logger.info("=" * 80)
    
    return 0 if error_count == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Re-submit Embedding Space training completion to monitor API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-submit ES completion for a specific session
  python3 resubmit_es_completion.py <session_id>
  
  # Re-submit all sessions with ES training
  python3 resubmit_es_completion.py --all
  
  # Dry run to validate all sessions without submitting
  python3 resubmit_es_completion.py --all --dry-run
  
  # Process only the 10 most recent sessions
  python3 resubmit_es_completion.py --all --recent 10
  
  # Limit to first 50 sessions found
  python3 resubmit_es_completion.py --all --limit 50
        """
    )
    
    parser.add_argument(
        'session_id',
        nargs='?',
        help='Session ID of the completed ES training (optional if --all is used)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all sessions with completed ES training'
    )
    
    parser.add_argument(
        '--monitor-url',
        default='https://monitor.featrix.com/training',
        help='Monitor API URL (default: https://monitor.featrix.com/training)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate sessions without actually submitting to monitor API'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of sessions to process (only with --all)'
    )
    
    parser.add_argument(
        '--recent',
        type=int,
        default=None,
        help='Only process N most recent sessions (only with --all)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.all:
        if args.session_id:
            logger.error("❌ Cannot specify both session_id and --all")
            sys.exit(1)
        exit_code = resubmit_all_sessions(
            monitor_url=args.monitor_url,
            dry_run=args.dry_run,
            limit=args.limit,
            recent=args.recent
        )
    else:
        if not args.session_id:
            logger.error("❌ Must specify either session_id or --all")
            parser.print_help()
            sys.exit(1)
        success, error_msg = resubmit_es_completion(
            session_id=args.session_id,
            monitor_url=args.monitor_url,
            dry_run=args.dry_run
        )
        exit_code = 0 if success else 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

