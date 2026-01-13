#!/usr/bin/env python3
"""
Wrapper script to run ES training in a non-daemon process.

This script is executed by Celery workers via fork/exec to create a new
session leader process that can spawn DataLoader workers for maximum GPU utilization.
"""
import atexit
import json
import logging
import os
import signal
import socket
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
configure_logging(job_prefix='es-train')

logger = logging.getLogger(__name__)

from lib.es_training import train_es, LightTrainingArgs


def cleanup_gpu_memory():
    """
    Clean up GPU memory and SIGKILL any DataLoader worker processes.
    
    CRITICAL: Do NOT try to gracefully shutdown workers or communicate with them.
    If workers are dead (e.g., from OOM), pipes are blocked and any communication
    will hang forever, preventing the process from exiting.
    
    Just SIGKILL everything immediately - workers have no important state to save.
    """
    # Step 1: SIGKILL all child processes IMMEDIATELY - no graceful shutdown!
    # This must happen FIRST, before any logging that might block on pipes.
    try:
        import psutil
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        
        if children:
            # Use sys.stdout.write instead of logger - logging might block on dead worker pipes!
            sys.stdout.write(f"⚠️  Found {len(children)} child processes - SIGKILL immediately\n")
            sys.stdout.flush()
            
            for child in children:
                try:
                    child.kill()  # SIGKILL - no graceful termination, instant death
                except psutil.NoSuchProcess:
                    pass
            
            # Brief wait for kernel to clean up
            psutil.wait_procs(children, timeout=1)
            sys.stdout.write("✅ Child processes killed\n")
            sys.stdout.flush()
    except ImportError:
        pass  # psutil not available
    except Exception as e:
        sys.stdout.write(f"⚠️  Cleanup error (non-fatal): {e}\n")
        sys.stdout.flush()
    
    # Step 2: Clear GPU cache (only after children are dead)
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
    
    parser = argparse.ArgumentParser(description='ES training wrapper')
    parser.add_argument('args_json_file', help='JSON file containing training arguments')
    parser.add_argument('--job-id', help='Job ID (visible in /proc for process identification)', default=None)
    parser.add_argument('--session-id', help='Session ID (visible in process table)', default=None)
    parser.add_argument('--job-path', help='Job path (visible in process table)', default=None)
    parsed_args = parser.parse_args()
    
    args_file = parsed_args.args_json_file
    job_id = parsed_args.job_id
    session_id = parsed_args.session_id
    job_path = parsed_args.job_path
    
    # Store job_id in environment so child processes can inherit it
    # This makes it visible in /proc/<pid>/environ as well
    if job_id:
        os.environ['FEATRIX_JOB_ID'] = job_id
    
    # Load args from JSON file
    with open(args_file, 'r') as f:
        args_dict = json.load(f)
    
    # Create LightTrainingArgs object
    args = LightTrainingArgs(**args_dict)
    
    # Run training
    try:
        train_es(args)
        logger.info("✅ Training completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        traceback.print_exc()
        # cleanup_gpu_memory() will be called automatically by atexit
        sys.exit(1)
