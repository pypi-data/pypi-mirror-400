#!/usr/bin/env python3
"""
Wrapper script to run pre-analysis architecture search in a non-daemon process.

This script is executed by Celery workers via fork/exec to create a new
session leader process for better GPU memory management and process isolation.
"""
import atexit
import json
import logging
import os
import signal
import sys
import traceback
from pathlib import Path

# CRITICAL: Redirect stderr to stdout IMMEDIATELY so all errors/crashes go to one log
sys.stderr = sys.stdout
print("🔧 STDERR REDIRECTED TO STDOUT - all output in one place!", flush=True)

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import standardized Featrix logging configuration
from lib.featrix.neural.logging_config import configure_logging
configure_logging(job_prefix='pre-analysis')

logger = logging.getLogger(__name__)

from lib.quick_architecture_search import run_quick_architecture_search


def cleanup_gpu_memory():
    """
    Clean up GPU memory on exit.
    
    This is called on exit to ensure we don't leave GPU memory allocated.
    """
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.info("✅ GPU memory cache cleared")
    except Exception as e:
        logger.debug(f"Could not clear GPU cache: {e}")


if __name__ == "__main__":
    import argparse
    
    # Register cleanup to run on exit (normal or crash)
    atexit.register(cleanup_gpu_memory)
    
    # Also handle signals to ensure cleanup on kill/interrupt
    def signal_handler(signum, frame):
        logger.warning(f"⚠️  Received signal {signum} - cleaning up before exit")
        cleanup_gpu_memory()
        sys.exit(128 + signum)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description='Pre-analysis architecture search wrapper')
    parser.add_argument('args_json_file', help='JSON file containing search arguments')
    parser.add_argument('--job-id', help='Job ID (visible in /proc for process identification)', default=None)
    parsed_args = parser.parse_args()
    
    args_file = parsed_args.args_json_file
    job_id = parsed_args.job_id
    
    # Store job_id in environment so child processes can inherit it
    # This makes it visible in /proc/<pid>/environ as well
    if job_id:
        os.environ['FEATRIX_JOB_ID'] = job_id
    
    # Load args from JSON file
    with open(args_file, 'r') as f:
        args_dict = json.load(f)
    
    # Extract arguments
    data_file = args_dict.get('data_file')
    strings_cache = args_dict.get('strings_cache')
    session_id = args_dict.get('session_id')
    n_samples = args_dict.get('n_samples', 20)
    quick_epochs = args_dict.get('quick_epochs', 25)
    suggested_configs = args_dict.get('suggested_configs')
    target_column_hint = args_dict.get('target_column_hint')
    
    # Run architecture search
    try:
        optimal_config = run_quick_architecture_search(
            data_file=data_file,
            strings_cache=strings_cache,
            session_id=session_id,
            n_samples=n_samples,
            quick_epochs=quick_epochs,
            suggested_configs=suggested_configs,
            job_id=job_id,  # Pass job_id for progress reporting
            target_column_hint=target_column_hint
        )
        
        # Save optimal config to session
        from lib.session_manager import load_session, save_session
        session = load_session(session_id)
        session['optimal_es_config'] = optimal_config
        save_session(session_id, session, exist_ok=True)
        
        logger.info(f"✅ Pre-analysis completed successfully: {optimal_config}")
        logger.info(f"💾 Saved optimal config to session")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Pre-analysis failed: {e}")
        traceback.print_exc()
        # cleanup_gpu_memory() will be called automatically by atexit
        sys.exit(1)

