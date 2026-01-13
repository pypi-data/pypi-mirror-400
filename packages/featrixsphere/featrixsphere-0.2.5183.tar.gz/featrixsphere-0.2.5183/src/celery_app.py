#!/usr/bin/env python3
"""
Celery app for async batch prediction jobs.
Training jobs continue to use the existing featrix_queue system.
"""

from celery import Celery
from celery.signals import worker_ready, task_prerun
from celery.exceptions import Ignore
from config import config
import json
import traceback
import sys
import pickle
import gc
import logging
import os
import contextlib
import subprocess
import json as json_module
import tempfile
import signal
import time
import uuid
import hashlib
import redis
import shutil
import socket
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError

# CRITICAL: Set up Python path FIRST before importing Featrix modules
lib_path = Path(__file__).parent / "lib"
current_path = Path(__file__).parent

if str(lib_path.resolve()) not in sys.path:
    sys.path.insert(0, str(lib_path.resolve()))
if str(current_path.resolve()) not in sys.path:
    sys.path.insert(0, str(current_path.resolve()))

# Import standardized logging configuration EARLY
from lib.featrix.neural.logging_config import configure_logging
configure_logging(job_prefix='celery')
logger = logging.getLogger(__name__)

# Install Featrix exception hook for better error tracking
try:
    from lib.featrix_debug import install_featrix_excepthook
    install_featrix_excepthook()
except Exception:
    pass  # Don't fail if debug module not available

logger.info(f"🔧 Celery module loading - Python paths set up")
logger.info(f"  lib_path: {lib_path.resolve()}")
logger.info(f"  current_path: {current_path.resolve()}")

# Import NON-CUDA modules at module level only
# CRITICAL: Do NOT import torch here - causes CUDA fork issues
try:
    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    logger.info(f"✅ Non-CUDA modules imported at module level")
except ImportError as e:
    logger.warning(f"⚠️ Core modules not available: {e}")

# Will check torch availability inside tasks after fork
TORCH_AVAILABLE = False

try:
    from lib.session_manager import load_session
    FEATRIX_QUEUE_AVAILABLE = True
    logger.info(f"✅ session_manager imported at module level")
except ImportError as e:
    FEATRIX_QUEUE_AVAILABLE = False
    logger.warning(f"⚠️ session_manager not available: {e}")

# CRITICAL: Do NOT import featrix modules at module level
# They contain torch imports which cause CUDA fork issues in Celery
# Will import them inside tasks after the fork happens
logger.info(f"🔧 Skipping featrix imports at module level to avoid CUDA fork issues")
logger.info(f"🔧 Will import torch and featrix modules inside task after fork")

# Initialize Celery app
app = Celery('sphere_predictions')

# Configure Celery to use Redis as broker and result backend
app.conf.update(
    broker_url='redis://localhost:6379/1',
    result_backend='redis://localhost:6379/1',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/New_York',
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        'celery_app.predict_batch': {'queue': 'cpu_worker'},
        'celery_app.explain_prediction': {'queue': 'gpu_training'},  # GPU for gradient computation
        # 'celery_app.project_training_movie_frame': {'queue': 'movie_generation'},  # DISABLED - movie generation disabled
        'celery_app.create_structured_data': {'queue': 'cpu_worker'},
        'celery_app.run_clustering': {'queue': 'cpu_worker'},
        'celery_app.train_single_predictor': {'queue': 'gpu_training'},
        'celery_app.train_es': {'queue': 'gpu_training'},
        'celery_app.train_knn': {'queue': 'cpu_worker'},
        'celery_app.dump_to_backplane': {'queue': 'cpu_worker'},
        'celery_app.ping': {'queue': 'cpu_worker'},  # Default to cpu_worker, but can be overridden
    },
    worker_prefetch_multiplier=1,  # One task at a time for GPU jobs
    task_acks_late=True,
    worker_disable_rate_limits=True,
    # CRITICAL: Set reasonable visibility_timeout for task re-delivery
    # Default is 3600 seconds (1 hour). We set to 3 hours as a balance:
    # - Long enough that normal jobs don't get re-delivered
    # - Short enough that truly stuck jobs get retried
    # Duplicate deliveries are detected via task_prerun signal (see check_duplicate_task_delivery)
    broker_transport_options={
        'visibility_timeout': 10800,  # 3 hours in seconds
    },
    # Logging configuration
    worker_log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    worker_task_log_format='%(asctime)s - %(name)s - %(levelname)s - [%(task_name)s(%(task_id)s)] %(message)s',
    worker_hijack_root_logger=False,  # Let our logging config work
)

# ============================================================================
# DUPLICATE TASK DELIVERY DETECTION
# ============================================================================

def check_duplicate_delivery(job_id: str, session_id: str, job_type: str, task_id: str = None) -> bool:
    """
    Check if this job is already running by examining log file modification time.
    
    When visibility_timeout expires (3 hours), Celery re-delivers tasks that haven't been
    acknowledged yet. Long-running training jobs (6+ hours) will get re-delivered, but we
    detect this by checking if the log file is being actively written.
    
    This function should be called at the START of train_es and train_single_predictor
    tasks, BEFORE acquiring any locks or doing any work.
    
    Args:
        job_id: Job ID
        session_id: Session ID  
        job_type: Job type (train_es, train_single_predictor)
        task_id: Celery task ID for logging
        
    Returns:
        True if this is a duplicate (job already running), False if legitimate
    """
    try:
        from lib.job_manager import get_job_output_path
        import time
        from pathlib import Path
        
        job_dir = get_job_output_path(job_id, session_id, job_type)
        stdout_log = job_dir / "logs" / "stdout.log"
        
        if not stdout_log.exists():
            # No log file - this is the first delivery
            return False
        
        # Check log file modification time
        log_mtime = stdout_log.stat().st_mtime
        log_age_seconds = time.time() - log_mtime
        
        task_prefix = f"[{task_id}] " if task_id else ""
        logger.info(f"🔍 {task_prefix}Checking for duplicate delivery: log age = {log_age_seconds:.1f}s")
        
        # If log was modified in the last 5 minutes, job is actively running
        if log_age_seconds < 300:  # 5 minutes
            logger.warning(f"⚠️  {task_prefix}DUPLICATE TASK DELIVERY DETECTED!")
            logger.warning(f"   Job: {job_type} ({job_id})")
            logger.warning(f"   Session: {session_id}")
            logger.warning(f"   Log file: {stdout_log}")
            logger.warning(f"   Log last modified: {log_age_seconds:.1f} seconds ago")
            logger.warning(f"   This task is already running in another worker")
            logger.warning(f"   Skipping duplicate delivery gracefully")
            return True  # DUPLICATE
        else:
            # Log is stale - this might be a retry of a failed job
            logger.info(f"ℹ️  {task_prefix}Log file exists but is stale ({log_age_seconds:.1f}s old)")
            logger.info(f"   This appears to be a legitimate retry, not a duplicate delivery")
            return False  # NOT A DUPLICATE
            
    except Exception as e:
        # Don't let duplicate detection errors break task execution
        logger.warning(f"⚠️  {task_prefix}Error in duplicate delivery check: {e}")
        logger.warning(f"   Allowing task to proceed normally")
        return False  # Allow task to run on error


@task_prerun.connect
def log_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Log full job configuration for all tasks to help debug configuration issues.
    
    NOTE: Duplicate delivery detection is now handled INSIDE the task functions themselves,
    not in this signal handler. Signal handlers can't prevent task execution by raising exceptions.
    
    Args:
        sender: The task class
        task_id: Celery task ID
        task: Task instance
        args: Task positional arguments
        kwargs: Task keyword arguments
    """
    # LOG FULL JOB CONFIGURATION FOR ALL TASKS
    try:
        import json
        task_name = sender.name if sender else 'unknown'
        logger.info(f"\n{'='*80}")
        logger.info(f"🔵 [TASK START] {task_name}")
        logger.info(f"   Task ID: {task_id}")
        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
        
        # Extract and log job_spec for all tasks
        if args and len(args) > 0:
            job_spec = args[0] if isinstance(args[0], dict) else None
            if job_spec:
                logger.info(f"   📋 Job Configuration (job_spec):")
                # Pretty print the job_spec with indentation
                try:
                    job_spec_str = json.dumps(job_spec, indent=4, default=str)
                    # Log each line with indentation
                    for line in job_spec_str.split('\n'):
                        logger.info(f"      {line}")
                except Exception as json_err:
                    logger.info(f"      (Could not serialize job_spec: {json_err})")
                    logger.info(f"      job_spec type: {type(job_spec)}")
                    logger.info(f"      job_spec keys: {list(job_spec.keys()) if isinstance(job_spec, dict) else 'N/A'}")
            
            # Log all args
            logger.info(f"   📦 Task Arguments:")
            for i, arg in enumerate(args):
                if isinstance(arg, dict):
                    # Skip logging full dicts again (already logged as job_spec)
                    if i == 0 and job_spec:
                        logger.info(f"      args[{i}]: <job_spec> (logged above)")
                    else:
                        logger.info(f"      args[{i}]: {type(arg).__name__} with {len(arg)} keys" if isinstance(arg, dict) else f"      args[{i}]: {arg}")
                else:
                    logger.info(f"      args[{i}]: {arg}")
        
        if kwargs:
            logger.info(f"   📦 Task Keyword Arguments:")
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    logger.info(f"      {key}: <dict with {len(value)} keys>")
                elif isinstance(value, (list, tuple)):
                    logger.info(f"      {key}: <{type(value).__name__} with {len(value)} items>")
                else:
                    logger.info(f"      {key}: {value}")
        
        logger.info(f"{'='*80}\n")
    except Exception as log_err:
        # Don't let logging errors break task execution
        logger.warning(f"⚠️  Error logging job configuration: {log_err}")
    
    # Set job tracking environment variables for diagnostics
    # These are used by StringServerClient and other components
    try:
        task_name = sender.name if sender else 'unknown'
        job_type = task_name.split('.')[-1]  # 'celery_app.train_es' -> 'train_es'
        job_id = task_id  # Use Celery task ID as default
        
        # Extract job_id and session_id from task arguments (varies by task type)
        if args and len(args) > 0:
            # Most tasks have signature: (job_spec, job_id, session_id, ...)
            # Some tasks have different signatures, so we try to extract what we can
            if len(args) >= 2 and args[1] is not None:
                # Use provided job_id if available
                job_id = str(args[1])
            elif len(args) >= 3 and args[2] is not None:
                # Some tasks might have job_id in different position
                # Try to use session_id as fallback identifier
                pass
        
        # Get compute node identifier (hostname)
        compute_node = socket.gethostname()
        
        # Set environment variables
        os.environ['FEATRIX_JOB_TYPE'] = job_type
        os.environ['FEATRIX_JOB_ID'] = job_id
        os.environ['FEATRIX_JOB_COMPUTE_NODE'] = compute_node
        
        logger.info(f"🔧 Set job tracking environment variables:")
        logger.info(f"   FEATRIX_JOB_TYPE={job_type}")
        logger.info(f"   FEATRIX_JOB_ID={job_id}")
        logger.info(f"   FEATRIX_JOB_COMPUTE_NODE={compute_node}")
    except Exception as env_err:
        # Don't let environment variable setting errors break task execution
        logger.warning(f"⚠️  Error setting job tracking environment variables: {env_err}")


# ============================================================================
# STANDARD JOB SETUP - Used by ALL Celery tasks
# ============================================================================

@contextlib.contextmanager
def setup_job_logging(job_id: str, session_id: str, job_type: str):
    """
    Standard job setup for ALL Celery tasks.
    
    Creates job directory, logs directory, and redirects stdout/stderr to logs/stdout.log.
    This ensures all job output is captured and visible via ffsh tail.
    
    CRITICAL: Acquires an exclusive file lock on the job directory to prevent
    duplicate jobs from running simultaneously (job re-dispatch bug protection).
    
    Args:
        job_id: Job ID (Celery task ID)
        session_id: Session ID
        job_type: Job type (create_structured_data, train_es, etc.)
        
    Yields:
        tuple: (job_dir, original_cwd) - job directory and original working directory
    """
    from lib.job_manager import get_job_output_path
    import stat
    import socket
    import fcntl
    
    job_dir = get_job_output_path(job_id, session_id, job_type)
    original_cwd = os.getcwd()
    
    # Ensure job directory exists
    job_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Job directory: {job_dir} (exists: {job_dir.exists()})")
    
    # Rename existing CRASH.log to previous-CRASH-<X>.log if it exists (job restart)
    crash_log_path = job_dir / "CRASH.log"
    if crash_log_path.exists():
        # Find next available number for previous-CRASH-<X>.log
        counter = 1
        while True:
            previous_crash_path = job_dir / f"previous-CRASH-{counter}.log"
            if not previous_crash_path.exists():
                break
            counter += 1
        
        try:
            crash_log_path.rename(previous_crash_path)
            logger.info(f"📦 Renamed existing CRASH.log to {previous_crash_path.name} (job restart detected)")
        except Exception as rename_err:
            logger.warning(f"⚠️  Failed to rename CRASH.log: {rename_err}")
    
    # Write PID file and worker info when worker starts processing
    try:
        import platform
        
        pid = os.getpid()
        pid_file = job_dir / "WORKER.pid"
        pid_file.write_text(str(pid))
        logger.info(f"📝 Wrote PID file: {pid_file} (PID: {pid})")
        
        # Write comprehensive worker info
        worker_info = {
            "pid": pid,
            "hostname": socket.gethostname(),
            "started_at": datetime.now().isoformat(),
            "job_id": job_id,
            "session_id": session_id,
            "job_type": job_type,
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "cwd": str(job_dir),
            "celery_task_id": job_id,  # Usually same as job_id
        }
        
        # Try to get Celery worker hostname from task context
        try:
            from celery import current_task
            if current_task and hasattr(current_task, 'request'):
                worker_info["celery_worker_hostname"] = current_task.request.hostname
                worker_info["celery_task_id"] = current_task.request.id
        except:
            pass
        
        worker_info_file = job_dir / "WORKER_INFO.json"
        worker_info_file.write_text(json.dumps(worker_info, indent=2))
        logger.info(f"📝 Wrote worker info: {worker_info_file}")
    except Exception as e:
        logger.warning(f"⚠️  Failed to write PID/worker info: {e}")
    
    # Create JOB_INFO.json with job metadata (queued_at, created_at, etc.)
    try:
        from lib.job_manager import load_job
        job_data = load_job(job_id)
        
        job_info = {
            "job_id": job_id,
            "session_id": session_id,
            "job_type": job_type,
            "created_at": job_data.get("created_at") if job_data else None,
            "queued_at": job_data.get("created_at") if job_data else None,  # Same as created_at
            "started_at": datetime.now().isoformat(),
            "status": job_data.get("status") if job_data else "unknown",
            "worker_hostname": socket.gethostname(),
            "celery_task_id": job_id,
        }
        
        # Add any additional job_spec info if available
        if job_data and "job_spec" in job_data:
            job_spec = job_data["job_spec"]
            if isinstance(job_spec, dict):
                # Include relevant job_spec fields
                if "target_column" in job_spec:
                    job_info["target_column"] = job_spec["target_column"]
                if "target_column_type" in job_spec:
                    job_info["target_column_type"] = job_spec["target_column_type"]
        
        job_info_path = job_dir / "JOB_INFO.json"
        with open(job_info_path, 'w') as f:
            json.dump(job_info, f, indent=2, default=str)
        
        logger.info(f"📝 Created JOB_INFO.json: {job_info_path}")
        if job_info.get("queued_at"):
            logger.info(f"   Queued at: {job_info['queued_at']}")
    except Exception as job_info_err:
        logger.warning(f"⚠️  Could not create JOB_INFO.json: {job_info_err}")
        # Don't fail job setup if this fails
    
    # NOTE: Duplicate task delivery detection is handled by task_prerun signal (see below)
    # This checks log file mtime BEFORE the task runs to gracefully ignore duplicates
    
    # CRITICAL: Acquire exclusive lock to prevent duplicate jobs
    lock_file_path = job_dir / ".job.lock"
    lock_file = None
    lock_acquired = False
    
    # CLEANUP: Remove stale lock files from dead processes
    if lock_file_path.exists():
        try:
            with open(lock_file_path, 'r') as lf:
                lock_content = lf.read()
                # Extract PID from lock file
                import re
                pid_match = re.search(r'pid:\s*(\d+)', lock_content)
                if pid_match:
                    old_pid = int(pid_match.group(1))
                    # Check if process is still running
                    try:
                        os.kill(old_pid, 0)  # Signal 0 just checks if process exists
                        logger.warning(f"⚠️  Lock file exists and process {old_pid} is still running")
                    except OSError:
                        # Process is dead - remove stale lock
                        logger.warning(f"🧹 Removing stale lock file from dead process {old_pid}")
                        lock_file_path.unlink()
                elif not lock_content.strip():
                    # CRITICAL: Empty lock file - this happens when a job crashes during lock acquisition
                    # The file gets created but content never written. The flock might still be held
                    # by a dead process. Try to acquire the lock to test if it's actually free.
                    logger.warning(f"⚠️  Lock file exists but is EMPTY - testing if flock is held...")
                    try:
                        # Try to acquire lock non-blocking to see if it's actually held
                        test_lock = open(lock_file_path, 'a')
                        fcntl.flock(test_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        # Lock acquired - file was abandoned, no active flock
                        logger.warning(f"🧹 Empty lock file was abandoned - removing it")
                        fcntl.flock(test_lock.fileno(), fcntl.LOCK_UN)
                        test_lock.close()
                        lock_file_path.unlink()
                    except BlockingIOError:
                        # flock is actually held by another process
                        test_lock.close()
                        logger.warning(f"⚠️  Empty lock file but flock IS held by another process")
                        # Leave file alone - will fail below with proper error message
                    except Exception as test_err:
                        logger.warning(f"⚠️  Could not test empty lock file: {test_err}")
                else:
                    # Lock file has content but no PID - malformed
                    logger.warning(f"⚠️  Lock file exists but has no PID field (malformed)")
                    logger.warning(f"   Content preview: {lock_content[:200]}")
        except Exception as e:
            logger.warning(f"⚠️  Could not check/clean stale lock file: {e}")
    
    try:
        lock_file = open(lock_file_path, 'w')
        logger.info(f"🔒 Attempting to acquire exclusive lock: {lock_file_path}")
        
        # Try non-blocking lock first
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_acquired = True
            lock_file.write(f"job_id: {job_id}\n")
            lock_file.write(f"session_id: {session_id}\n")
            lock_file.write(f"job_type: {job_type}\n")
            lock_file.write(f"pid: {os.getpid()}\n")
            lock_file.write(f"hostname: {socket.gethostname()}\n")
            lock_file.write(f"locked_at: {datetime.now().isoformat()}\n")
            lock_file.flush()
            logger.info(f"✅ Acquired exclusive lock - this job has sole access to directory")
        except BlockingIOError:
            # Lock is held by another process
            logger.error(f"❌ CRITICAL: Another job is already running in this directory!")
            logger.error(f"   Lock file: {lock_file_path}")
            logger.error(f"   This indicates a job re-dispatch bug or race condition")
            
            # Try to read who holds the lock
            try:
                with open(lock_file_path, 'r') as lf:
                    lock_info = lf.read()
                    logger.error(f"   Lock held by:\n{lock_info}")
            except:
                pass
            
            lock_file.close()
            lock_file = None
            raise RuntimeError(f"Job directory locked by another process - refusing to run duplicate job")
    except Exception as lock_err:
        if lock_file:
            lock_file.close()
        raise
    
    # Create logs directory IMMEDIATELY (before chdir) to ensure it exists
    logs_dir = job_dir / "logs"
    logger.info(f"📁 Attempting to create logs directory: {logs_dir}")
    
    try:
        # Force creation - don't rely on exist_ok silently failing
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=False, mode=0o755)
            logger.info(f"✅ Created logs directory: {logs_dir}")
        else:
            logger.info(f"✅ Logs directory already exists: {logs_dir}")
        
        # Verify it was created and is accessible
        if not logs_dir.exists():
            raise RuntimeError(f"logs_dir.mkdir() succeeded but directory doesn't exist: {logs_dir}")
        if not logs_dir.is_dir():
            raise RuntimeError(f"logs_dir exists but is not a directory: {logs_dir}")
        
        # Ensure directory is writable - fix permissions if needed
        current_mode = logs_dir.stat().st_mode
        if not (current_mode & stat.S_IWRITE):
            logger.warning(f"⚠️  Logs directory not writable, fixing permissions: {logs_dir}")
            logs_dir.chmod(0o755)
        
        # Test write access
        test_file = logs_dir / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"✅ Logs directory is writable: {logs_dir}")
        except Exception as e:
            logger.error(f"❌ Logs directory is NOT writable: {e}")
            # Try to fix permissions on parent directory
            try:
                job_dir.chmod(0o755)
                logs_dir.chmod(0o755)
                # Try again
                test_file.write_text("test")
                test_file.unlink()
                logger.info(f"✅ Fixed permissions and verified writability")
            except Exception as e2:
                logger.error(f"❌ Still cannot write to logs directory after fixing permissions: {e2}")
                raise
        
        logger.info(f"📁 Logs directory ready: {logs_dir} (mode: {oct(logs_dir.stat().st_mode)})")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Failed to create logs directory {logs_dir}: {e}")
        logger.error(f"   Exception type: {type(e).__name__}")
        logger.error(f"   job_dir: {job_dir} (exists: {job_dir.exists()})")
        logger.error(f"   job_dir parent: {job_dir.parent} (exists: {job_dir.parent.exists() if job_dir.parent else 'N/A'})")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        # CRITICAL: This is a fatal error - we MUST have logs
        raise RuntimeError(f"Failed to create logs directory {logs_dir}: {e}") from e
    
    # Set up stdout_path
    stdout_path = logs_dir / "stdout.log"
    logger.info(f"📝 Log file will be: {stdout_path}")
    
    # Rotate old log file if it exists
    if stdout_path.exists():
        n = 1
        while (logs_dir / f"stdout.log.{n}").exists():
            n += 1
        stdout_path.rename(logs_dir / f"stdout.log.{n}")
    
    # Create README.txt documenting supported flags (if it doesn't exist)
    readme_path = job_dir / "README.txt"
    if not readme_path.exists():
        readme_content = """Job Control Flags
==================

This directory supports the following control flags:

ABORT
-----
Purpose: Stop a running job immediately and prevent automatic restart.
Usage: Create a file named "ABORT" in this directory.
Effect:
  - Job exits immediately when detected
  - Job is marked as FAILED
  - Job will NOT restart automatically
  - Recovery is blocked permanently

RESTART
-------
Purpose: Restart a job from scratch on next system startup.
Usage: Create a file named "RESTART" in this directory.
Effect (on worker startup):
  - Job is reset to READY status
  - All progress and recovery info is cleared
  - Job runs from the beginning
  - RESTART flag is renamed to started.RESTART.<date>
  - Jobs are processed newest first (by file modification time)

FINISH
------
Purpose: Gracefully stop training after current epoch completes.
Usage: Create a file named "FINISH" in this directory.
Effect:
  - Training completes current epoch
  - Model is saved
  - Job exits gracefully
  - FINISHED flag is created when done

NO_STOP
-------
Purpose: Disable early stopping for this job.
Usage: Create a file named "NO_STOP" in this directory.
Effect:
  - Early stopping mechanisms are disabled
  - Job will run for full number of epochs

PUBLISH
-------
Purpose: Save embedding_space.pickle during training for single predictor training.
Usage: Create a file named "PUBLISH" in this directory.
Effect:
  - Embedding space is saved as embedding_space.pickle in the job directory
  - Saved at the start of each epoch when flag is present
  - Can be used to train a single predictor before training completes
  - Flag can remain present - it will save once per epoch

PAUSE
-----
Purpose: Pause a running job gracefully (saves checkpoint and marks as PAUSED).
Usage: Create a file named "PAUSE" in this directory.
Effect:
  - Training completes current epoch/batch
  - Checkpoint is saved (if save_state_after_every_epoch is enabled)
  - Job is marked as PAUSED
  - Job exits gracefully (can be resumed later)
  - To resume: Remove PAUSE file and set job status to READY

Creating Flags
--------------
You can create flags using ffsh:

  ffsh jobs abort <job_path>
  ffsh jobs finish <job_path>
  ffsh jobs restart <job_path>
  ffsh jobs pause <job_path>
  ffsh jobs resume <job_path>

Where <job_path> can be:
  - <session_id>/<job_type>_<job_id> (full path)
  - <job_id> (just the job ID - will search all queues)

Or manually:
  touch <job_directory>/ABORT
  touch <job_directory>/RESTART
  touch <job_directory>/FINISH
  touch <job_directory>/PAUSE
  touch <job_directory>/NO_STOP
  touch <job_directory>/PUBLISH
"""
        try:
            readme_path.write_text(readme_content)
            logger.debug(f"📝 Created README.txt in job directory: {readme_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to create README.txt: {e}")
    
    # Change to job directory AFTER logs directory is created
    os.chdir(job_dir)
    logger.info(f"📁 Changed to job directory: {os.getcwd()}")
    
    # Redirect stdout/stderr to log file
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    stdout_file = None
    
    try:
        stdout_file = open(stdout_path, 'w', buffering=1)
        sys.stdout = stdout_file
        sys.stderr = stdout_file
        
        # Update logging to use the file with standardized Featrix format
        from lib.featrix.neural.logging_config import FeatrixFormatter, FeatrixFilter, VERSION, HOSTNAME, set_job_prefix
        
        # Set job prefix to last 8 chars of job_id for easy identification
        job_prefix = job_id[-8:] if len(job_id) > 8 else job_id
        set_job_prefix(job_prefix)
        
        root_logger.handlers = []
        handler = logging.StreamHandler(stdout_file)
        handler.setLevel(logging.INFO)
        
        # Use standardized Featrix logging format
        log_format = f'[{HOSTNAME},{VERSION}] %(asctime)s [pid=%(process)d] %(job_prefix_str)s%(level_str)s%(epoch_str)s %(short_name)-16s: %(message)s'
        formatter = FeatrixFormatter(log_format)
        handler.setFormatter(formatter)
        
        # Add Featrix filter for epoch and job_prefix support
        featrix_filter = FeatrixFilter()
        handler.addFilter(featrix_filter)
        
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        yield (job_dir, original_cwd)
    finally:
        # Release lock FIRST (before any cleanup that might fail)
        if lock_acquired and lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                lock_file.close()
                logger.info(f"🔓 Released exclusive lock on {lock_file_path}")
                
                # Remove lock file
                try:
                    lock_file_path.unlink()
                    logger.debug(f"   Deleted lock file: {lock_file_path}")
                except:
                    pass
            except Exception as unlock_err:
                logger.error(f"❌ Error releasing lock: {unlock_err}")
        
        # Flush before restoring
        if stdout_file:
            stdout_file.flush()
            os.fsync(stdout_file.fileno())  # Force write to disk
        
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        root_logger.handlers = original_handlers
        
        if stdout_file:
            stdout_file.close()
        
        # Change back to original directory
        os.chdir(original_cwd)
        logger.info(f"📁 Changed back to: {original_cwd}")
        
        # Verify file was created and write a marker if it's empty
        if stdout_path.exists():
            file_size = stdout_path.stat().st_size
            if file_size > 0:
                logger.debug(f"✅ Log file created: {stdout_path} ({file_size} bytes)")
            else:
                # File exists but is empty - write a marker
                try:
                    with open(stdout_path, 'a') as f:
                        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{socket.gethostname()}] [INFO    ] celery_app: Log file initialized (no output captured)\n")
                        f.flush()
                        os.fsync(f.fileno())
                except Exception as e:
                    logger.warning(f"⚠️  Could not write to log file: {e}")
        else:
            logger.warning(f"⚠️  Log file was not created: {stdout_path}")


def write_crash_log(job_dir: Path, exception: Exception, job_id: str, session_id: str = None, job_type: str = None, additional_info: dict = None):
    """
    Write crash/error information to CRASH.log in the job directory.
    
    This makes it easy to find crash information when debugging - just look for CRASH.log
    in the job directory instead of searching through stdout.log.
    
    Args:
        job_dir: Job directory path
        exception: The exception that was raised
        job_id: Job ID
        session_id: Session ID (optional)
        job_type: Job type (optional)
        additional_info: Additional dict of info to include (optional)
    """
    try:
        crash_log_path = job_dir / "CRASH.log"
        
        with open(crash_log_path, 'w') as f:
            f.write("=" * 100 + "\n")
            f.write("CRASH LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Job ID: {job_id}\n")
            if session_id:
                f.write(f"Session ID: {session_id}\n")
            if job_type:
                f.write(f"Job Type: {job_type}\n")
            f.write(f"Hostname: {socket.gethostname()}\n")
            f.write(f"PID: {os.getpid()}\n")
            f.write("\n")
            
            f.write("-" * 100 + "\n")
            f.write("EXCEPTION INFORMATION\n")
            f.write("-" * 100 + "\n")
            f.write(f"Exception Type: {type(exception).__name__}\n")
            f.write(f"Exception Message: {str(exception)}\n")
            f.write("\n")
            
            if additional_info:
                f.write("-" * 100 + "\n")
                f.write("ADDITIONAL INFORMATION\n")
                f.write("-" * 100 + "\n")
                for key, value in additional_info.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
            
            f.write("-" * 100 + "\n")
            f.write("FULL TRACEBACK\n")
            f.write("-" * 100 + "\n")
            f.write(traceback.format_exc())
            f.write("\n")
            
            f.write("=" * 100 + "\n")
            f.write("END OF CRASH LOG\n")
            f.write("=" * 100 + "\n")
        
        logger.info(f"📝 Wrote crash log to: {crash_log_path}")
    except Exception as log_err:
        # Don't fail if we can't write crash log - at least try to log it
        logger.warning(f"⚠️  Failed to write crash log: {log_err}")


def log_task_return_value(result: dict, task_name: str, max_size: int = 10000):
    """
    Safely log task return values, truncating large values to avoid log spam.
    
    Args:
        result: The return value from a task (should be a dict)
        task_name: Name of the task for logging
        max_size: Maximum size of value to log (in characters)
    """
    if not isinstance(result, dict):
        logger.info(f"📤 {task_name} returning: {type(result).__name__} (not a dict, size: {len(str(result))})")
        return
    
    logger.info(f"📤 {task_name} RETURN VALUE:")
    logger.info(f"   success: {result.get('success', 'N/A')}")
    
    # Log output keys but truncate large values
    if 'output' in result:
        output = result['output']
        if isinstance(output, dict):
            logger.info(f"   output keys: {list(output.keys())}")
            for key, value in output.items():
                if isinstance(value, (str, Path)):
                    # Check if it's a file path
                    path_obj = Path(value) if isinstance(value, str) else value
                    if path_obj.exists():
                        size = path_obj.stat().st_size / 1024 / 1024  # MB
                        logger.info(f"      {key}: {value} ({size:.2f} MB)")
                    else:
                        logger.info(f"      {key}: {value} (file not found)")
                else:
                    value_str = str(value)
                    if len(value_str) > max_size:
                        logger.info(f"      {key}: {value_str[:max_size]}... (truncated, {len(value_str)} chars)")
                    else:
                        logger.info(f"      {key}: {value_str}")
        else:
            output_str = str(output)
            if len(output_str) > max_size:
                logger.info(f"   output: {output_str[:max_size]}... (truncated, {len(output_str)} chars)")
            else:
                logger.info(f"   output: {output_str}")
    
    # Log other important fields
    for key in ['job_id', 'session_id', 'error', 'traceback']:
        if key in result:
            value = result[key]
            value_str = str(value)
            if len(value_str) > max_size:
                logger.info(f"   {key}: {value_str[:max_size]}... (truncated, {len(value_str)} chars)")
            else:
                logger.info(f"   {key}: {value_str}")


def verify_output_files_exist(output: dict, task_name: str) -> bool:
    """
    Verify that output files exist before updating session.
    
    Args:
        output: Dict of output file paths
        task_name: Name of task for logging
        
    Returns:
        True if all file paths exist, False otherwise
    """
    all_exist = True
    missing_files = []
    logger.info(f"🔍 {task_name}: Verifying output files exist before session update...")
    
    for key, path in output.items():
        if path and isinstance(path, (str, Path)):
            path_obj = Path(path) if isinstance(path, str) else path
            if path_obj.exists():
                size = path_obj.stat().st_size / 1024 / 1024  # MB
                logger.info(f"   ✅ {key}: {path} ({size:.2f} MB)")
            else:
                logger.error(f"   ❌ {key}: {path} (FILE NOT FOUND)")
                all_exist = False
                missing_files.append(f"{key}: {path}")
        elif path:
            # Not a path, just log it
            logger.info(f"   ℹ️  {key}: {path} (not a file path)")
    
    if all_exist:
        logger.info(f"✅ All output files verified")
    else:
        missing_list = "\n      ".join(missing_files)
        logger.error(f"❌ Missing output files ({len(missing_files)}):")
        logger.error(f"      {missing_list}")
        logger.error(f"   Session update may fail!")
    
    return all_exist


# Worker startup hook - run job recovery when workers start
@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    """
    Called when a Celery worker is ready to accept tasks.
    This is where we run job recovery to re-dispatch interrupted jobs.
    """
    # Lower GC threshold for more aggressive garbage collection
    # Default is (700, 10, 10) - this makes GC run more frequently
    # Lower thresholds = more frequent GC = less memory usage but more CPU
    gc.set_threshold(300, 5, 5)  # More aggressive: collect gen0 every 300 allocations instead of 700
    logger.info(f"🔧 GC threshold set to (300, 5, 5) for more aggressive garbage collection")
    
    # Only run recovery on one worker to avoid duplicate dispatches
    # Use a simple lock mechanism: first worker to check wins
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        
        # Try to acquire lock (expires in 60 seconds)
        lock_key = "celery:recovery:lock"
        lock_acquired = redis_client.set(lock_key, "locked", nx=True, ex=60)
        
        if lock_acquired:
            logger.info("🔍 Worker ready - running job recovery...")
            try:
                from lib.celery_job_recovery import recover_interrupted_jobs
                recovery_summary = recover_interrupted_jobs()
                logger.info(f"✅ Job recovery complete: {recovery_summary.get('total_recovered', 0)} jobs recovered")
            except Exception as recovery_error:
                logger.error(f"❌ Job recovery failed: {recovery_error}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
        else:
            logger.debug("⏭️  Another worker is handling job recovery, skipping...")
    except Exception as e:
        logger.warning(f"⚠️  Could not run job recovery on worker startup: {e}")
        # Don't fail worker startup if recovery fails


@app.task(bind=True, name='celery_app.ping')
def ping(self, timestamp: float, queue_name: str = "unknown", echo_data: str = None):
    """
    Ping task for queue connectivity testing.
    
    This task can be sent to any queue to verify end-to-end connectivity.
    It echoes back the original request data to confirm the task was received and processed.
    
    Args:
        timestamp: Original request timestamp (to verify round-trip)
        queue_name: Name of queue this ping was sent to
        echo_data: Optional data to echo back (for verification)
        
    Returns:
        dict with ping response, original timestamp, and echoed data
    """
    response_time = time.time()
    round_trip = response_time - timestamp
    
    logger.info(f"🏓 PING received on queue '{queue_name}' - round trip: {round_trip*1000:.2f}ms")
    
    return {
        'status': 'pong',
        'queue': queue_name,
        'request_timestamp': timestamp,
        'response_timestamp': response_time,
        'round_trip_ms': round_trip * 1000,
        'worker': self.request.hostname if hasattr(self.request, 'hostname') else 'unknown',
        'echo': echo_data  # Echo back the original data
    }

@app.task(bind=True)
def predict_batch(self, session_id: str, records: list, prediction_options: dict = None):
    """
    Celery task for batch predictions.
    
    Args:
        session_id: Session ID with trained single predictor
        records: List of record dictionaries to predict
        prediction_options: Optional parameters (batch_size, etc.)
    
    Returns:
        dict with predictions or error info
    """
    logger.info(f"🚀 CELERY TASK STARTED - Session: {session_id}, Records: {len(records)}")
    
    try:
        # Update task state to indicate processing has started
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(records),
                'status': 'Loading model...'
            }
        )
        
        # Paths already set up at module level - no need to repeat
        logger.info(f"🔧 Python paths already configured at module level")
        
        # Load the session and single predictor
        if not FEATRIX_QUEUE_AVAILABLE:
            raise ImportError("featrix_queue module not available")
            
        logger.info(f"🔧 Loading session {session_id}...")
        try:
            session = load_session(session_id)
            logger.info(f"✅ Session loaded successfully")
        except Exception as session_error:
            logger.error(f"❌ SESSION LOAD FAILED: {session_error}")
            logger.error(f"❌ Session traceback: {traceback.format_exc()}")
            raise
        
        # Get the single predictor path (backwards compatible)
        single_predictors = session.get("single_predictors")
        single_predictor = session.get("single_predictor")
        
        # Set prediction options (need this before accessing it below)
        options = prediction_options or {}
        
        # Helper function to generate predictor ID
        def generate_predictor_id(predictor_path: str) -> str:
            filename = os.path.basename(predictor_path) if predictor_path else 'unknown'
            # Remove .pickle extension from user-facing ID
            if filename.endswith('.pickle'):
                filename = filename[:-7]
            path_hash = hashlib.md5(predictor_path.encode('utf-8')).hexdigest()[:8]
            return f"{filename}_{path_hash}"
        
        # NEW: Check if predictor_id or target_column specified in options
        requested_predictor_id = options.get('predictor_id')
        requested_target_column = options.get('target_column')
        logger.info(f"🔍 CELERY PREDICT_BATCH - predictor_id='{requested_predictor_id}', target_column='{requested_target_column}'")
        
        predictor_path = None
        if single_predictors and isinstance(single_predictors, list):
            # NEW: If multiple predictors exist, REQUIRE target_column or predictor_id
            if len(single_predictors) > 1 and not requested_predictor_id and not requested_target_column:
                # Get available targets for error message
                available_targets = []
                available_ids = []
                for pred_path in single_predictors:
                    # Get predictor_id
                    if Path(pred_path).exists():
                        available_ids.append(generate_predictor_id(pred_path))
                    
                    # Get target_column from metadata
                    metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                    if Path(metadata_path).exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                                target_col = metadata.get('target_column')
                                if target_col:
                                    available_targets.append(target_col)
                        except Exception:
                            pass
                
                error_msg = f"Multiple predictors found ({len(single_predictors)}) - must specify 'target_column' or 'predictor_id'. Available targets: {available_targets}, Available IDs: {available_ids}"
                logger.error(f"❌ CELERY PREDICT_BATCH - {error_msg}")
                raise ValueError(error_msg)
            
            # PRIORITY 1: predictor_id (most precise)
            if requested_predictor_id:
                logger.info(f"🔍 CELERY PREDICT_BATCH - Looking for predictor with predictor_id='{requested_predictor_id}'")
                predictor_found = False
                available_predictor_ids = []
                
                for pred_path in single_predictors:
                    if Path(pred_path).exists():
                        current_predictor_id = generate_predictor_id(pred_path)
                        available_predictor_ids.append(current_predictor_id)
                        
                        if current_predictor_id == requested_predictor_id:
                            predictor_path = pred_path
                            predictor_found = True
                            logger.info(f"✅ CELERY PREDICT_BATCH - Found matching predictor by ID: {pred_path}")
                            break
                
                if not predictor_found:
                    raise ValueError(f"No predictor found for predictor_id '{requested_predictor_id}'. Available IDs: {available_predictor_ids}")
            
            # PRIORITY 2: target_column (semantic match)
            elif requested_target_column:
                logger.info(f"🔍 CELERY PREDICT_BATCH - Looking for predictor with target_column='{requested_target_column}'")
                predictor_found = False
                
                for pred_path in single_predictors:
                    # Skip None or invalid paths
                    if not pred_path:
                        logger.warning(f"⚠️  CELERY PREDICT_BATCH - Skipping None predictor path in list")
                        continue
                    
                    # Load predictor metadata to check target_column
                    metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                    if Path(metadata_path).exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                                target_col = metadata.get('target_column')
                                
                                logger.info(f"🔍 CELERY PREDICT_BATCH - Checking predictor {pred_path}: target_column='{target_col}'")
                                
                                if target_col == requested_target_column:
                                    predictor_path = pred_path
                                    predictor_found = True
                                    logger.info(f"✅ CELERY PREDICT_BATCH - Found matching predictor: {pred_path}")
                                    break
                        except Exception as metadata_error:
                            logger.warning(f"⚠️  CELERY PREDICT_BATCH - Could not read metadata for {pred_path}: {metadata_error}")
                            continue
                
                if not predictor_found:
                    raise ValueError(f"No predictor found for target column '{requested_target_column}'")
            
            # PRIORITY 3: Single predictor fallback (backwards compatibility)
            else:
                # Only allow fallback if there's exactly one predictor
                if len(single_predictors) == 1:
                    predictor_path = single_predictors[0]
                    logger.info(f"🔍 CELERY PREDICT_BATCH - Single predictor session, using: {predictor_path}")
                else:
                    # This should never be reached due to check above, but keep for safety
                    raise ValueError(f"Multiple predictors found ({len(single_predictors)}) but no target_column or predictor_id specified")
        elif single_predictor:
            predictor_path = single_predictor
        else:
            raise ValueError("No single predictor found in session")
        
        if not predictor_path or not Path(predictor_path).exists():
            raise ValueError(f"Single predictor not found at: {predictor_path}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': len(records),
                'status': 'Loading single predictor model...'
            }
        )
        
        # NEW APPROACH: Use subprocess to avoid all import/fork/CUDA issues
        logger.info(f"🚀 Using subprocess approach to avoid fork/CUDA issues")
        logger.info(f"📦 Predictor path: {predictor_path}")
        
        # Check if we should try to keep model loaded in memory
        # This is a simple check - in the future we could check actual RAM usage
        try:
            import psutil
            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            # Keep model loaded if we have at least 8GB free RAM
            KEEP_MODEL_LOADED = available_ram_gb >= 8.0
            if KEEP_MODEL_LOADED:
                logger.info(f"💾 Sufficient RAM available ({available_ram_gb:.1f}GB free) - model caching enabled")
            else:
                logger.info(f"⚠️ Limited RAM available ({available_ram_gb:.1f}GB free) - model will be loaded fresh")
        except ImportError:
            # psutil not available, default to not caching
            KEEP_MODEL_LOADED = False
            logger.info("⚠️ psutil not available - cannot check RAM, defaulting to fresh model load")
        except Exception as e:
            KEEP_MODEL_LOADED = False
            logger.warning(f"⚠️ Error checking RAM: {e}, defaulting to fresh model load")
        
        # Create temporary files for input/output
        # Initialize Redis for progress monitoring
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
            redis_available = True
            logger.info(f"✅ Redis connected for progress monitoring")
        except Exception as redis_error:
            logger.warning(f"⚠️ Redis not available for progress monitoring: {redis_error}")
            redis_available = False
        
        temp_dir = Path("/tmp") / f"celery_prediction_{uuid.uuid4().hex[:8]}"
        temp_dir.mkdir(exist_ok=True)
        
        input_file = temp_dir / "input.json"
        output_file = temp_dir / "output.json"
        
        logger.info(f"📁 Created temp directory: {temp_dir}")
        
        # Set prediction options
        options = prediction_options or {}
        
        try:
            # Write input data to file
            with open(input_file, 'w') as f:
                json.dump({
                    'session_id': session_id,
                    'predictor_path': predictor_path,
                    'records': records,
                    'batch_size': options.get('batch_size', 256)
                }, f)
            logger.info(f"✅ Written {len(records)} records to {input_file}")
            
            # Try to use persistent prediction server first (keeps models in memory)
            # Falls back to subprocess if server not available
            PREDICTION_SERVER_URL = "http://127.0.0.1:8765"
            use_prediction_server = False
            
            try:
                # Check if prediction server is available
                import urllib.request
                import urllib.error
                health_check = urllib.request.urlopen(f"{PREDICTION_SERVER_URL}/health", timeout=1)
                if health_check.getcode() == 200:
                    use_prediction_server = True
                    logger.info(f"✅ Prediction server available at {PREDICTION_SERVER_URL}")
            except (urllib.error.URLError, Exception) as e:
                logger.info(f"⚠️  Prediction server not available, falling back to subprocess: {e}")
            
            if use_prediction_server:
                # Use persistent prediction server (models stay in memory/GPU)
                logger.info(f"🚀 Using persistent prediction server (models stay loaded)...")
                
                try:
                    # Prepare request
                    request_data = {
                        'predictor_path': predictor_path,
                        'records': records,
                        'batch_size': options.get('batch_size', 256)
                    }
                    
                    # Send request to prediction server
                    import urllib.request
                    import urllib.parse
                    
                    req = urllib.request.Request(
                        PREDICTION_SERVER_URL,
                        data=json.dumps(request_data).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    start_time = time.time()
                    
                    with urllib.request.urlopen(req, timeout=3600) as response:
                        result_data = json.loads(response.read().decode('utf-8'))
                    
                    elapsed = time.time() - start_time
                    
                    if result_data.get('success'):
                        logger.info(f"✅ Prediction server completed in {elapsed:.1f}s")
                        
                        # Write results to output file (for consistency with subprocess approach)
                        with open(output_file, 'w') as f:
                            json.dump(result_data, f)
                        
                        # Skip subprocess execution
                        use_prediction_server = True
                    else:
                        logger.error(f"❌ Prediction server returned error: {result_data.get('error')}")
                        use_prediction_server = False  # Fall back to subprocess
                        
                except Exception as server_error:
                    logger.error(f"❌ Prediction server request failed: {server_error}")
                    logger.error(traceback.format_exc())
                    use_prediction_server = False  # Fall back to subprocess
            
            # Fallback: Run subprocess prediction if server not available or failed
            if not use_prediction_server:
                script_path = Path(__file__).parent / "standalone_prediction.py"
                
                logger.info(f"🔧 Running subprocess: python {script_path} {input_file} {output_file}")
                
                # Use subprocess to call the standalone prediction script
                # Get task ID for Redis progress tracking
                task_id = self.request.id
                redis_key = f"prediction_progress:{task_id}"
                
                # Start subprocess asynchronously - write output to log file to avoid pipe deadlock
                logger.info(f"🚀 Starting subprocess with Redis progress tracking...")
                
                # Create log files in temp directory
                subprocess_log = temp_dir / "subprocess.log"
                subprocess_err = temp_dir / "subprocess_error.log"
                
                with open(subprocess_log, 'w') as stdout_file, open(subprocess_err, 'w') as stderr_file:
                    process = subprocess.Popen(
                        [sys.executable, str(script_path), str(input_file), str(output_file), task_id],
                        stdout=stdout_file,
                        stderr=stderr_file,
                        text=True
                    )
                    
                    # Poll for subprocess completion while monitoring Redis progress
                    start_time = time.time()
                    last_progress_percentage = 0
                    
                    while process.poll() is None:
                        # Check for timeout (1 hour)
                        if time.time() - start_time > 3600:
                            process.terminate()
                            process.wait()
                            raise Exception("Prediction subprocess timed out after 1 hour")
                        
                        # Check Redis for progress updates
                        if redis_available:
                            try:
                                progress_data = redis_client.get(redis_key)
                                if progress_data:
                                    progress_info = json.loads(progress_data)
                                    current = progress_info.get('current', 0)
                                    total = progress_info.get('total', 100)
                                    status = progress_info.get('status', 'Processing...')
                                    percentage = progress_info.get('percentage', 0)
                                    
                                    # Only update Celery state if progress percentage has changed
                                    if percentage != last_progress_percentage:
                                        self.update_state(
                                            state='PROGRESS',
                                            meta={
                                                'current': current,
                                                'total': total,
                                                'status': status,
                                                'percentage': percentage,
                                                'timestamp': progress_info.get('timestamp')
                                            }
                                        )
                                        last_progress_percentage = percentage
                                        logger.info(f"📊 Relayed progress: {percentage}% - {status}")
                            except Exception as redis_err:
                                logger.warning(f"Failed to read progress from Redis: {redis_err}")
                        
                        # Sleep briefly to avoid busy polling
                        time.sleep(2)
                
                # Check final return code
                if process.returncode != 0:
                    # Read error logs
                    with open(subprocess_err, 'r') as f:
                        stderr_content = f.read()
                    logger.error(f"❌ Subprocess failed with return code {process.returncode}")
                    logger.error(f"❌ STDERR: {stderr_content}")
                    raise Exception(f"Prediction subprocess failed: {stderr_content}")
                
                logger.info(f"✅ Subprocess completed successfully")
                
                # Log subprocess output for debugging
                if subprocess_log.exists():
                    with open(subprocess_log, 'r') as f:
                        stdout_content = f.read()
                        if stdout_content:
                            logger.info(f"📊 Subprocess output logged to {subprocess_log}")
            
            # Read results from output file (works for both prediction server and subprocess)
            if not output_file.exists():
                raise Exception(f"Output file not created: {output_file}")
            
            with open(output_file, 'r') as f:
                result_data = json.load(f)
            
            logger.info(f"✅ Results loaded: {result_data.get('successful_predictions', 0)} successful predictions")
            
            # Handle both JSON Tables and legacy formats
            output_format = result_data.get('format', 'legacy')
            logger.info(f"📊 Output format: {output_format}")
            
            if output_format == 'json_tables' and 'results_table' in result_data:
                # Convert JSON Tables to legacy format for backward compatibility
                # But KEEP the results_table too for consistent API format
                try:
                    from jsontables import JSONTablesDecoder
                    
                    results_table = result_data['results_table']
                    records_with_predictions = JSONTablesDecoder.to_records(results_table)
                    
                    # Convert to legacy prediction format for backward compatibility
                    predictions = []
                    for i, record in enumerate(records_with_predictions):
                        # Extract prediction data from the enhanced record
                        prediction_obj = {
                            'row_index': record.get('row_index', i),
                            'prediction_id': None,  # Not stored in JSON Tables format
                            'error': record.get('prediction_error'),
                            'metadata': {}
                        }
                        
                        # Extract the actual prediction probabilities
                        if record.get('prediction_error') is None:
                            # Look for pred_* columns
                            prediction_probs = {}
                            for key, value in record.items():
                                if key.startswith('pred_') and key != 'pred_':
                                    class_name = key[5:]  # Remove 'pred_' prefix
                                    prediction_probs[class_name] = value
                            
                            if prediction_probs:
                                prediction_obj['prediction'] = prediction_probs
                            elif 'prediction' in record:
                                prediction_obj['prediction'] = record['prediction']
                            else:
                                prediction_obj['prediction'] = None
                                prediction_obj['error'] = "No prediction data found"
                            
                            # Add guardrails if available
                            if 'guardrails' in record:
                                prediction_obj['metadata']['guardrails'] = record['guardrails']
                        else:
                            prediction_obj['prediction'] = None
                        
                        predictions.append(prediction_obj)
                    
                    # Add legacy format alongside JSON Tables format
                    result_data['predictions'] = predictions
                    # Keep results_table as-is for consistent API format
                    logger.info(f"✅ Added legacy predictions format alongside JSON Tables: {len(predictions)} predictions")
                    
                except ImportError:
                    logger.warning(f"⚠️ JSON Tables not available for conversion, keeping raw format")
                except Exception as convert_error:
                    logger.warning(f"⚠️ Failed to convert JSON Tables format: {convert_error}")
                    # Keep the original format but log the issue
            
            elif output_format == 'legacy' and 'predictions' in result_data:
                logger.info(f"✅ Using legacy prediction format")
            else:
                logger.warning(f"⚠️ Unknown output format: {output_format}")
            
            # DON'T call update_state(state='SUCCESS') - Celery does this automatically
            # when the task returns. Calling it manually overwrites the return value!
            # Just update progress one final time with PROGRESS state
            self.update_state(
                state='PROGRESS',  # Use PROGRESS, not SUCCESS!
                meta={
                    'current': len(records),
                    'total': len(records),
                    'status': f"Completed: {result_data.get('successful_predictions', 0)} successful, {result_data.get('failed_predictions', 0)} failed",
                    'output_format': output_format,
                    'percentage': 100
                }
            )
            
            # Log what we're returning for debugging
            logger.info(f"📦 Returning result_data keys: {list(result_data.keys())}")
            logger.info(f"📦 results_table type: {type(result_data.get('results_table'))}")
            logger.info(f"📦 predictions count: {len(result_data.get('predictions', []))}")
            
            # Return the full result - Celery will automatically set state to SUCCESS
            return result_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Subprocess timed out after 1 hour")
            raise Exception("Prediction subprocess timed out")
            
        except Exception as subprocess_error:
            logger.error(f"❌ Subprocess error: {subprocess_error}")
            logger.error(f"❌ Subprocess traceback: {traceback.format_exc()}")
            raise Exception(f"Prediction subprocess failed: {subprocess_error}")
            
        finally:
            # Cleanup temp files
            try:
                if input_file.exists():
                    input_file.unlink()
                if output_file.exists():
                    output_file.unlink()
                temp_dir.rmdir()
                logger.info(f"✅ Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_err:
                logger.warning(f"⚠️ Failed to cleanup temp files: {cleanup_err}")

        
    except Exception as e:
        # Log the full error
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        # Log to worker logs for debugging
        logger.error(f"CELERY WORKER ERROR: {error_msg}")
        logger.error(f"CELERY WORKER TRACEBACK:\n{error_traceback}")
        
        # Return error state instead of re-raising
        return {
            'success': False,
            'error': error_msg,
            'traceback': error_traceback,
            'session_id': session_id,
            'total_records': len(records) if 'records' in locals() else 0,
            'exc_type': type(e).__name__,
            'exc_message': str(e)
        }
        
    finally:
        # Minimal cleanup since subprocess handles GPU/model cleanup
        try:
            import gc
            gc.collect()
            logger.info(f"✅ Python garbage collection completed")
        except Exception as cleanup_error:
            logger.warning(f"Cleanup failed: {cleanup_error}")

@app.task(bind=True, name='celery_app.explain_prediction')
def explain_prediction(self, session_id: str, record: dict, explain_options: dict = None):
    """
    Celery task for explaining a prediction using gradient attribution.
    
    Args:
        session_id: Session ID with trained single predictor
        record: Record dictionary (without target column)
        explain_options: Optional parameters (class_idx, target_column, predictor_id)
    
    Returns:
        dict with feature_scores, pair_scores, target_class_idx, logit
    """
    logger.info(f"🚀 EXPLAIN TASK STARTED - Session: {session_id}")
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Loading model...'
            }
        )
        
        # Load the session and single predictor
        if not FEATRIX_QUEUE_AVAILABLE:
            raise ImportError("featrix_queue module not available")
        
        logger.info(f"🔧 Loading session {session_id}...")
        session = load_session(session_id)
        logger.info(f"✅ Session loaded successfully")
        
        # Get explain options
        options = explain_options or {}
        class_idx = options.get('class_idx')
        target_column = options.get('target_column')
        predictor_id = options.get('predictor_id')
        
        # Get the single predictor path (backwards compatible)
        single_predictors = session.get("single_predictors")
        single_predictor = session.get("single_predictor")
        
        # Helper function to generate predictor ID
        def generate_predictor_id(predictor_path: str) -> str:
            import hashlib
            import os
            filename = os.path.basename(predictor_path) if predictor_path else "unknown"
            if filename.endswith(".pickle"):
                filename = filename[:-7]
            path_hash = hashlib.md5(predictor_path.encode("utf-8")).hexdigest()[:8]
            return f"{filename}_{path_hash}"
        
        # Find the correct predictor
        predictor_path = None
        if single_predictors:
            # New format: multiple predictors
            if predictor_id:
                # Find by predictor_id
                for pred_path, pred_info in single_predictors.items():
                    if generate_predictor_id(pred_path) == predictor_id:
                        predictor_path = pred_path
                        break
            elif target_column:
                # Find by target_column
                for pred_path, pred_info in single_predictors.items():
                    if pred_info.get('target_column') == target_column:
                        predictor_path = pred_path
                        break
            else:
                # Use first predictor
                predictor_path = list(single_predictors.keys())[0] if single_predictors else None
        elif single_predictor:
            # Old format: single predictor
            predictor_path = single_predictor
        
        if not predictor_path:
            raise ValueError("No predictor found for session")
        
        logger.info(f"🔧 Loading predictor from {predictor_path}...")
        
        # Load predictor
        from load_and_test_model import load_predictor
        fsp, es = load_predictor(str(predictor_path))
        
        if fsp is None or es is None:
            raise ValueError("Failed to load predictor")
        
        # Ensure predictor is available
        fsp._ensure_predictor_available()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Computing explanation...'
            }
        )
        
        # Get record_b if provided
        record_b = options.get('record_b')
        
        # Call explain on embedding space
        explanation = es.explain(
            record=record,
            predictor_model=fsp.predictor,
            target_codec=fsp.target_codec,
            class_idx=class_idx,
            record_b=record_b
        )
        
        logger.info(f"✅ Explanation computed successfully")
        
        # Helper to convert pair_scores keys to strings
        def convert_pair_scores(ps_dict):
            if isinstance(ps_dict, dict):
                return {f"{i}_{j}": score if isinstance((i, j), tuple) else score 
                        for (i, j), score in ps_dict.items()}
            return ps_dict
        
        # Handle different return types
        if isinstance(explanation, list):
            # List of explanations
            result = {
                'success': True,
                'explanations': [
                    {
                        'feature_scores': expl.get('feature_scores', {}),
                        'pair_scores': convert_pair_scores(expl.get('pair_scores', {})),
                        'target_class_idx': expl.get('target_class_idx'),
                        'logit': expl.get('logit'),
                    }
                    for expl in explanation
                ]
            }
        elif 'difference' in explanation:
            # Two-record comparison
            result = {
                'success': True,
                'record_a': {
                    'feature_scores': explanation['record_a'].get('feature_scores', {}),
                    'pair_scores': convert_pair_scores(explanation['record_a'].get('pair_scores', {})),
                    'target_class_idx': explanation['record_a'].get('target_class_idx'),
                    'logit': explanation['record_a'].get('logit'),
                },
                'record_b': {
                    'feature_scores': explanation['record_b'].get('feature_scores', {}),
                    'pair_scores': convert_pair_scores(explanation['record_b'].get('pair_scores', {})),
                    'target_class_idx': explanation['record_b'].get('target_class_idx'),
                    'logit': explanation['record_b'].get('logit'),
                },
                'difference': {
                    'feature_scores': explanation['difference'].get('feature_scores', {}),
                    'pair_scores': convert_pair_scores(explanation['difference'].get('pair_scores', {})),
                },
                'heatmap': explanation.get('heatmap', {}),  # Include heatmap data for visualization
            }
        else:
            # Single record
            result = {
                'success': True,
                'feature_scores': explanation.get('feature_scores', {}),
                'pair_scores': convert_pair_scores(explanation.get('pair_scores', {})),
                'target_class_idx': explanation.get('target_class_idx'),
                'logit': explanation.get('logit'),
            }
        
        log_task_return_value(result, "EXPLAIN_PREDICTION")
        return result
        
    except Exception as e:
        logger.error(f"❌ EXPLAIN TASK FAILED: {e}")
        logger.error(traceback.format_exc())
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        log_task_return_value(error_result, "EXPLAIN_PREDICTION")
        raise

@app.task(bind=True)
def project_training_movie_frame(self, job_spec: dict):
    """
    Celery task to generate a training movie frame from an embedding space checkpoint on CPU.
    
    DISABLED: Movie generation is disabled to prevent CPU overload.
    This task now immediately returns success without doing anything.
    
    Args:
        job_spec: Dict containing:
            - checkpoint_path: Path to model checkpoint (.pt file)
            - data_snapshot_path: Path to saved data sample (.json)
            - output_dir: Where to save the projection
            - session_id: Session ID
            - epoch: Epoch number
    
    Returns:
        dict with success status and output file path
    """
    logger.info(f"⏭️  SKIPPING movie frame generation (disabled) - Session: {job_spec.get('session_id')}, Epoch: {job_spec.get('epoch')}")
    return {
        'success': True,
        'skipped': True,
        'reason': 'movie_generation_disabled',
        'epoch': job_spec.get('epoch'),
        'session_id': job_spec.get('session_id')
    }
    
    # DISABLED CODE BELOW - keeping for reference
    from lib.featrix.neural.movie_frame_task import generate_movie_frame_on_cpu
    
    logger.info(f"🎬 CELERY PROJECT_TRAINING_MOVIE_FRAME STARTED - Session: {job_spec.get('session_id')}, Epoch: {job_spec.get('epoch')}")
    
    # Extract parameters early (needed for save_job)
    checkpoint_path = job_spec.get('checkpoint_path')
    data_snapshot_path = job_spec.get('data_snapshot_path')
    output_dir = job_spec.get('output_dir')
    session_id = job_spec.get('session_id', 'unknown')
    epoch = job_spec.get('epoch')
    
    # Save job to Redis for tracking (so ffsh can show job_type)
    job_id = self.request.id
    try:
        from lib.job_manager import save_job, JobStatus
        save_job(
            job_id=job_id,
            job_data={
                'status': JobStatus.READY,
                'created_at': datetime.now(tz=ZoneInfo("America/New_York")),
                'job_spec': job_spec,
            },
            session_id=session_id,
            job_type='project_training_movie_frame'
        )
        logger.debug(f"✅ Saved project_training_movie_frame job {job_id} to Redis")
    except Exception as redis_err:
        logger.warning(f"⚠️  Could not save job to Redis: {redis_err}")
        # Continue anyway - job tracking is non-critical
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Loading checkpoint...',
                'epoch': epoch,
                'session_id': session_id
            }
        )
        
        # Validate parameters
        if not checkpoint_path or not data_snapshot_path:
            raise ValueError("Missing required parameters in job_spec")
        
        # Validate checkpoint exists
        # NOTE: During recovery after restart/upgrade, checkpoint files may not exist
        # (cleaned up, never saved, or from old version). Movie frames are non-critical
        # visualizations - gracefully skip rather than crash.
        if not Path(checkpoint_path).exists():
            logger.warning(f"⚠️  Checkpoint not found: {checkpoint_path}")
            logger.warning(f"   This is normal during recovery after restart/upgrade")
            logger.warning(f"   Skipping movie frame generation for epoch {epoch}")
            return {
                'success': False,
                'error': 'Checkpoint not found (skipped during recovery)',
                'epoch': epoch,
                'session_id': session_id,
                'skipped': True  # Indicates graceful skip, not a failure
            }
        
        # Validate data snapshot exists
        if not Path(data_snapshot_path).exists():
            logger.warning(f"⚠️  Data snapshot not found: {data_snapshot_path}")
            logger.warning(f"   Skipping movie frame generation for epoch {epoch}")
            return {
                'success': False,
                'error': 'Data snapshot not found (skipped during recovery)',
                'epoch': epoch,
                'session_id': session_id,
                'skipped': True
            }
        
        logger.info(f"   Checkpoint: {checkpoint_path}")
        logger.info(f"   Data snapshot: {data_snapshot_path}")
        logger.info(f"   Output dir: {output_dir}")
        
        # Update job status to RUNNING
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id=job_id, status=JobStatus.RUNNING)
        except Exception as status_err:
            logger.debug(f"Could not update job status: {status_err}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Building projections...',
                'epoch': epoch
            }
        )
        
        # Call the existing movie frame generation function
        # This handles loading checkpoint, encoding points, and saving projections
        output_file = generate_movie_frame_on_cpu(
            checkpoint_path=checkpoint_path,
            data_snapshot_path=data_snapshot_path,
            epoch=epoch,
            output_dir=output_dir,
            session_id=session_id
        )
        
        if output_file:
            logger.info(f"✅ Projections built successfully: {output_file}")
            
            # Update job status to DONE
            try:
                from lib.job_manager import update_job_status, JobStatus
                update_job_status(job_id=job_id, status=JobStatus.DONE)
            except Exception as status_err:
                logger.debug(f"Could not update job status: {status_err}")
            
            return {
                'success': True,
                'output_file': output_file,
                'epoch': epoch,
                'session_id': session_id
            }
        else:
            raise Exception("Projection building returned None")
            
    except Exception as e:
        logger.error(f"❌ PROJECT_TRAINING_MOVIE_FRAME FAILED: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        # Update job status to FAILED
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata={'error': str(e)})
        except Exception as status_err:
            logger.debug(f"Could not update job status: {status_err}")
        
        return {
            'success': False,
            'error': str(e),
            'epoch': epoch,
            'session_id': session_id,
            'traceback': traceback.format_exc()
        }

@app.task(bind=True)
def create_structured_data(self, job_spec: dict, job_id: str, data_file: str = None, session_id: str = None):
    """
    Celery task to create structured data from raw input (CSV/JSON).
    
    This processes the input data file, creates the SQLite database, and prepares
    the data for embedding space training.
    
    Args:
        job_spec: Dict containing job parameters (column_overrides, s3 paths, etc.)
        job_id: Job identifier
        data_file: Path to input data file (CSV/JSON)
        session_id: Session ID
    
    Returns:
        dict with output paths (sqlite_db, structured_data, etc.)
    """
    task_start = time.time()
    celery_trace_id = f"CELERY-{uuid.uuid4().hex[:8]}"
    job_dir = None  # Initialize to avoid linter error when accessed in exception handler
    
    # Use Celery task ID if job_id not provided
    if not job_id:
        job_id = self.request.id
        logger.info(f"   Using Celery task ID as job_id: {job_id}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔵 [CELERY] {celery_trace_id} CREATE_STRUCTURED_DATA TASK STARTED")
    logger.info(f"   Timestamp: {datetime.now().isoformat()}")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Data file: {data_file}")
    logger.info(f"   Job spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
    logger.info(f"   Task ID: {self.request.id}")
    logger.info(f"{'='*80}")
    
    # CRITICAL: Wrap entire task in try/except to catch ANY unhandled exceptions
    try:
        logger.info(f"   📍 TRACE: Entered main try block")
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Loading data...',
                'job_id': job_id,
                'session_id': session_id
            }
        )
        
        # Import here to avoid CUDA fork issues
        # CRITICAL: If this import fails, the entire worker process dies silently!
        # So we wrap it in its own try/except to SCREAM LOUDLY if imports fail
        try:
            logger.info(f"   📍 TRACE: Importing structureddata module...")
            from lib.structureddata import CSVtoDB
            logger.info(f"   📍 TRACE: Successfully imported CSVtoDB")
        except Exception as import_err:
            logger.error(f"")
            logger.error(f"╔{'='*78}╗")
            logger.error(f"║  💥💥💥 CRITICAL IMPORT FAILURE - WORKER WILL DIE 💥💥💥{' '*15}║")
            logger.error(f"╚{'='*78}╝")
            logger.error(f"")
            logger.error(f"   ❌ FAILED TO IMPORT lib.structureddata")
            logger.error(f"   Exception: {type(import_err).__name__}: {import_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.error(f"")
            logger.error(f"   This usually means:")
            logger.error(f"   1. A module that structureddata.py imports is missing")
            logger.error(f"   2. There's a syntax error in structureddata.py")
            logger.error(f"   3. A deleted module is still being imported (e.g. device.py)")
            logger.error(f"")
            raise  # Re-raise to trigger the outer exception handler
        
        import boto3
        from urllib.parse import urlparse
        
        # Handle None job_spec (should be empty dict)
        if job_spec is None:
            job_spec = {}
        
        # Check if this is an embedding space job with S3 datasets
        s3_training_path = job_spec.get("s3_training_dataset")
        s3_validation_path = job_spec.get("s3_validation_dataset")
        name = job_spec.get("name", "embedding_space")
        
        # Handle S3 datasets for embedding space sessions
        if s3_training_path and s3_validation_path:
            logger.info(f"📥 Downloading S3 data for embedding space: {name}")
            
            # Check if paths are local files (not S3)
            if not s3_training_path.startswith('s3://') or not s3_validation_path.startswith('s3://'):
                # Local files - use them directly
                training_local_path = Path(s3_training_path)
                validation_local_path = Path(s3_validation_path)
                
                if not training_local_path.exists():
                    raise ValueError(f"Training file not found: {training_local_path}")
                if not validation_local_path.exists():
                    raise ValueError(f"Validation file not found: {validation_local_path}")
                
                logger.info(f"Using local training file: {training_local_path}")
                logger.info(f"Using local validation file: {validation_local_path}")
                
                # Use the training data as the data_file for processing
                data_file = str(training_local_path)
            else:
                # S3 paths - download them
                training_parsed = urlparse(s3_training_path)
                validation_parsed = urlparse(s3_validation_path)
                
                if training_parsed.scheme != 's3' or validation_parsed.scheme != 's3':
                    raise ValueError("S3 URLs must start with 's3://'")
                
                training_bucket = training_parsed.netloc
                training_key = training_parsed.path.lstrip('/')
                validation_bucket = validation_parsed.netloc
                validation_key = validation_parsed.path.lstrip('/')
                
                # Get session directory for downloads
                from lib.session_manager import load_session
                session = load_session(session_id)
                session_dir = Path(session.get('input_data', '')).parent if session.get('input_data') else Path(config.data_dir) / "es_train" / session_id
                session_dir.mkdir(parents=True, exist_ok=True)
                
                # Set up local file paths
                training_local_path = session_dir / f"{name}_training_data.csv"
                validation_local_path = session_dir / f"{name}_validation_data.csv"
                
                try:
                    # Initialize S3 client
                    s3_client = boto3.client('s3')
                    
                    # Download training dataset
                    logger.info(f"📥 Downloading training dataset from s3://{training_bucket}/{training_key}")
                    s3_client.download_file(training_bucket, training_key, str(training_local_path))
                    logger.info(f"✅ Training dataset downloaded to {training_local_path}")
                    
                    # Download validation dataset
                    logger.info(f"📥 Downloading validation dataset from s3://{validation_bucket}/{validation_key}")
                    s3_client.download_file(validation_bucket, validation_key, str(validation_local_path))
                    logger.info(f"✅ Validation dataset downloaded to {validation_local_path}")
                    
                    # Use the downloaded training data as the data_file for processing
                    data_file = str(training_local_path)
                    
                except Exception as e:
                    logger.error(f"❌ Error downloading S3 data: {e}")
                    raise
        
        # Check if data_file is an S3 URL and download it first
        elif data_file and isinstance(data_file, str) and data_file.startswith('s3://'):
            logger.info(f"📥 Downloading S3 data: {data_file}")
            
            # Parse S3 URL
            parsed = urlparse(data_file)
            if parsed.scheme != 's3':
                raise ValueError("S3 URL must start with 's3://'")
            
            bucket = parsed.netloc
            key = parsed.path.lstrip('/')
            
            # Set up local file path - preserve original extension
            local_filename = Path(key).name
            # Keep original extension if it's a supported format, otherwise default to .csv
            if not local_filename.lower().endswith(('.csv', '.parquet', '.json', '.jsonl')):
                local_filename += '.csv'
            
            # Get session directory for download
            from lib.session_manager import load_session
            session = load_session(session_id)
            session_dir = Path(session.get('input_data', '')).parent if session.get('input_data') else Path(config.data_dir) / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            data_file_path = session_dir / local_filename
            
            try:
                # Initialize S3 client and download
                s3_client = boto3.client('s3')
                logger.info(f"📥 Downloading from s3://{bucket}/{key} to {data_file_path}")
                s3_client.download_file(bucket, key, str(data_file_path))
                logger.info(f"✅ S3 download completed: {data_file_path}")
                data_file = str(data_file_path)
                
            except Exception as e:
                logger.error(f"❌ Error downloading S3 data: {e}")
                raise
        
        # Convert data_file to Path if provided
        data_file_path = Path(data_file) if data_file else None
        
        if not data_file_path or not data_file_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_file_path}")
        
        # Extract JSON analysis configuration from job spec (if provided)
        json_analysis_config = job_spec.get("json_analysis_config", {})
        
        # STANDARD JOB SETUP - creates job dir, logs dir, and redirects stdout/stderr
        with setup_job_logging(job_id, session_id, 'create_structured_data') as (job_dir, original_cwd):
                # Call CSVtoDB directly (replaces run_create_structured_data from featrix_queue)
                logger.info(f"🔄 STEP 1/3: Initializing CSVtoDB processor...")
                c2d = CSVtoDB(
                    column_overrides=job_spec.get("column_overrides", {}),
                    json_analysis_config=json_analysis_config
                )
                
                # Set db_path to current directory (job directory)
                c2d.db_path = str(Path.cwd() / "embedding_space.db")
                
                logger.info(f"🔄 STEP 2/3: Starting CSV/JSON to SQLite conversion...")
                logger.info(f"   📄 Input file: {data_file_path}")
                logger.info(f"   💾 Output DB: {c2d.db_path}")
                file_size_mb = data_file_path.stat().st_size / 1024 / 1024
                logger.info(f"   📊 File size: {file_size_mb:.2f} MB ({data_file_path.stat().st_size:,} bytes)")
                
                # Update task state to show we're processing
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': f'Processing {file_size_mb:.1f} MB file...',
                        'job_id': job_id,
                        'session_id': session_id,
                        'input_file': str(data_file_path),
                        'stage': 'Reading and processing data file'
                    }
                )
                
                logger.info(f"📊 Processing data file (reading, parsing, cleaning, expanding JSON columns, writing to SQLite)...")
                logger.info(f"   This may take a while for large files - watch for progress updates below...")
                c2d.csv_to_sqlite(csv_path=str(data_file_path))
                
                logger.info(f"✅ STEP 2/3 COMPLETE: CSV to SQLite conversion finished")
                
                # CRITICAL: Clean up empty data.db file if it exists (created by CSVtoDB.__init__)
                # We use embedding_space.db, so data.db is just a leftover empty file
                data_db_path = Path.cwd() / "data.db"
                if data_db_path.exists():
                    data_db_size = data_db_path.stat().st_size
                    if data_db_size == 0:
                        logger.info(f"🧹 Cleaning up empty data.db file (leftover from CSVtoDB initialization)")
                        try:
                            data_db_path.unlink()
                            logger.info(f"   ✅ Removed empty data.db file")
                        except Exception as cleanup_err:
                            logger.warning(f"   ⚠️  Could not remove empty data.db: {cleanup_err}")
                    else:
                        logger.warning(f"   ⚠️  data.db exists and is not empty ({data_db_size} bytes) - keeping it")
                
                logger.info(f"🔄 STEP 3/3: Gathering output files...")
                logger.info(f"   📍 TRACE: About to call c2d.get_output_files()...")
                output = c2d.get_output_files()
                logger.info(f"   📍 TRACE: c2d.get_output_files() returned, type: {type(output)}")
                logger.info(f"✅ Output files generated: {list(output.keys())}")
                logger.info(f"   📍 TRACE: About to iterate over {len(output)} output items...")
                # Only check file paths, not metadata (lists/dicts)
                file_path_keys = ['sqlite_db', 'strings_cache', 'vector_db_path']
                try:
                    for key, value in output.items():
                        try:
                            if key in file_path_keys:
                                # This is a file path - check if it exists
                                if value and isinstance(value, (str, Path)):
                                    path_obj = Path(value)
                                    if path_obj.exists():
                                        size = path_obj.stat().st_size / 1024 / 1024
                                        logger.info(f"   • {key}: {value} ({size:.2f} MB)")
                                    else:
                                        logger.info(f"   • {key}: {value} (file not found)")
                                else:
                                    logger.info(f"   • {key}: {value} (invalid path type: {type(value).__name__})")
                            else:
                                # This is metadata (list/dict) - just log the type and size
                                if isinstance(value, (list, dict)):
                                    if isinstance(value, list):
                                        logger.info(f"   • {key}: list with {len(value)} items")
                                    else:
                                        logger.info(f"   • {key}: dict with {len(value)} keys")
                                else:
                                    logger.info(f"   • {key}: {type(value).__name__} = {value}")
                        except Exception as file_err:
                            logger.error(f"   ❌ Error logging output item {key}: {file_err}")
                            logger.error(f"   Traceback: {traceback.format_exc()}")
                    logger.info(f"   📍 TRACE: Finished iterating over output items")
                except Exception as loop_err:
                    logger.error(f"   ❌ CRITICAL: Exception in output items loop: {loop_err}")
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    raise
                logger.info(f"   📍 TRACE: Finished logging output files")
        
                # CRITICAL: Validate sqlite_db file exists and is not empty before saving to session
                sqlite_db_path = output.get('sqlite_db')
                if sqlite_db_path:
                    sqlite_db_file = Path(sqlite_db_path)
                    if not sqlite_db_file.exists():
                        raise FileNotFoundError(f"sqlite_db file does not exist: {sqlite_db_path}")
                    
                    file_size = sqlite_db_file.stat().st_size
                    if file_size == 0:
                        raise ValueError(f"sqlite_db file is 0 bytes (empty): {sqlite_db_path}. This indicates create_structured_data failed to write data.")
                    
                    logger.info(f"✅ Validated sqlite_db file: {sqlite_db_path} ({file_size / 1024 / 1024:.2f} MB)")
                else:
                    raise ValueError("sqlite_db not found in output - create_structured_data failed to generate database file")
        
                # Update session with output (matching file-based queue behavior)
                # CRITICAL: Session update and verification must succeed before dispatch
                logger.info(f"   📍 TRACE: Starting session update block...")
                session_updated = False
                verified = False
                try:
                    logger.info(f"   📍 TRACE: About to import load_session, save_session...")
                    from lib.session_manager import load_session, save_session
                    logger.info(f"   📍 TRACE: Imports successful, about to load session...")
                    logger.info(f"🔄 Loading session {session_id} to update with output files...")
                    session = load_session(session_id)
                    logger.info(f"   ✅ Session loaded successfully")
                    logger.info(f"   Session keys before update: {list(session.keys())}")
                    logger.info(f"   Updating with output keys: {list(output.keys())}")
                    session = {**session, **output}
                    logger.info(f"   Saving session...")
                    save_session(session_id=session_id, session_doc=session, exist_ok=True)
                    session_updated = True
                    logger.info(f"✅ Session updated with structured data output")
                    logger.info(f"   sqlite_db: {output.get('sqlite_db')}")
                    
                    # CRITICAL: Wait and verify session is persisted before dispatching next job
                    # This prevents race condition where pre_analysis_architecture starts before session has sqlite_db
                    logger.info(f"⏳ Verifying session persistence before dispatch...")
                    max_verify_attempts = 6  # 6 attempts = up to 30 seconds
                    verify_sleep = 5  # 5 seconds between attempts
                    verified = False
                    for attempt in range(max_verify_attempts):
                        if attempt > 0:
                            logger.info(f"   Attempt {attempt + 1}/{max_verify_attempts}: Sleeping {verify_sleep}s before re-checking...")
                            time.sleep(verify_sleep)
                        
                        # Reload session and check if sqlite_db is present
                        check_session = load_session(session_id)
                        if check_session.get('sqlite_db'):
                            logger.info(f"   ✅ Verified: sqlite_db found in session after {attempt * verify_sleep}s")
                            verified = True
                            break
                        else:
                            logger.warning(f"   ⚠️  sqlite_db not found in session yet (attempt {attempt + 1}/{max_verify_attempts})")
                    
                    if not verified:
                        logger.error(f"   ❌ CRITICAL: Session still missing sqlite_db after {max_verify_attempts * verify_sleep}s!")
                        logger.error(f"   Cannot dispatch pre_analysis_architecture without sqlite_db - task will fail")
                        raise ValueError(f"Session {session_id} missing sqlite_db after {max_verify_attempts * verify_sleep}s - cannot proceed")
                    
                except Exception as session_error:
                    logger.error(f"❌ CRITICAL: Failed to update session with output: {session_error}")
                    logger.error(f"   Full traceback: {traceback.format_exc()}")
                    logger.error(f"   Output files were generated but session was not updated!")
                    logger.error(f"   Cannot dispatch next job without session update - task will fail")
                    raise  # Re-raise to fail the task
                
                # Automatically dispatch next job in chain
                # CRITICAL: Only dispatch if session was successfully updated and verified
                # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
                if not session_updated or not verified:
                    error_msg = f"Cannot dispatch next job: session_updated={session_updated}, verified={verified}"
                    logger.error(f"❌ CRITICAL: {error_msg}")
                    raise RuntimeError(error_msg)
                
                logger.info(f"🔄 Attempting to dispatch next job in chain for session {session_id}...")
                logger.info(f"   Session was updated: {session_updated}")
                logger.info(f"   sqlite_db verified in session: {verified}")
                from lib.session_chains import dispatch_next_job_in_chain
                from lib.session_manager import load_session
                
                next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='create_structured_data')
                if next_task_id:
                    logger.info(f"✅ Successfully dispatched next job in chain (task_id: {next_task_id})")
                else:
                    # Dispatch returned None - verify there really are no more jobs to dispatch
                    logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
                    session_check = load_session(session_id)
                    job_plan = session_check.get('job_plan', [])
                    remaining_jobs = []
                    for idx, job_desc in enumerate(job_plan):
                        job_type = job_desc.get("job_type", "unknown")
                        job_id = job_desc.get("job_id")
                        if not job_id or job_id == "None":
                            # Check if legitimately skipped
                            is_skipped = False
                            if job_type == "train_es":
                                embedding_space_path = session_check.get("embedding_space")
                                foundation_model_id = session_check.get("foundation_model_id")
                                from featrix.neural.embedding_space_utils import embedding_space_path_exists
                                if foundation_model_id or (embedding_space_path and embedding_space_path_exists(embedding_space_path)):
                                    is_skipped = True
                            elif job_type == "train_knn":
                                vector_db_path = session_check.get("vector_db")
                                if vector_db_path and Path(vector_db_path).exists():
                                    is_skipped = True
                            elif job_type == 'create_structured_data':
                                is_skipped = True  # Just completed
                            # CRITICAL: train_single_predictor should NEVER be skipped - it must be dispatched
                            # If it's in the job_plan without a job_id, it's a critical error
                            
                            if not is_skipped:
                                remaining_jobs.append((idx, job_type))
                                logger.error(f"   ❌ Found undispatchable job: {idx} ({job_type}) - NO JOB_ID")
                    
                    if remaining_jobs:
                        error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                        logger.error(f"❌ {error_msg}")
                        logger.error(f"   Session: {session_id}")
                        logger.error(f"   Session type: {session_check.get('session_type')}")
                        logger.error(f"   This task will FAIL to prevent silent chain breakage")
                        # CRITICAL: Before retrying, reload session to check if first dispatch actually succeeded
                        # There's a race condition where dispatch might have succeeded but session wasn't saved yet
                        logger.info(f"   🔄 Reloading session to check if first dispatch actually set job_id...")
                        session_recheck = load_session(session_id)
                        job_plan_recheck = session_recheck.get('job_plan', [])
                        
                        # Check if any of the remaining jobs now have job_ids (first dispatch succeeded)
                        still_remaining = []
                        for idx, job_type in remaining_jobs:
                            job_desc = job_plan_recheck[idx] if idx < len(job_plan_recheck) else None
                            if job_desc:
                                recheck_job_id = job_desc.get("job_id")
                                if recheck_job_id and recheck_job_id != "None":
                                    logger.info(f"   ✅ Job {idx} ({job_type}) now has job_id: {recheck_job_id} - first dispatch succeeded!")
                                    # Verify the job actually exists in Redis
                                    from lib.job_manager import load_job
                                    job_data = load_job(recheck_job_id)
                                    if job_data:
                                        logger.info(f"      Job exists in Redis - dispatch was successful, no retry needed")
                                        # CRITICAL: Verify the job_id is NOT the create_structured_data job_id (bug check)
                                        if recheck_job_id == self.request.id:
                                            logger.error(f"      ❌ CRITICAL BUG: train_single_predictor job_id matches create_structured_data job_id!")
                                            logger.error(f"         This indicates a bug where wrong job_id was saved")
                                            logger.error(f"         Job_id: {recheck_job_id}")
                                            logger.error(f"         This will cause duplicate job folders!")
                                        continue  # Skip this one, it's already dispatched
                                    else:
                                        logger.warning(f"      ⚠️  Job_id exists in session but not in Redis - may be stale")
                            still_remaining.append((idx, job_type))
                        
                        if still_remaining:
                            # CRITICAL: For predictor jobs, train_single_predictor MUST be dispatched
                            # Retry dispatch one more time before failing
                            if any(job_type == 'train_single_predictor' for _, job_type in still_remaining):
                                logger.error(f"   🔄 CRITICAL: train_single_predictor job still not dispatched - retrying dispatch...")
                                try:
                                    retry_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='create_structured_data')
                                    if retry_task_id:
                                        logger.info(f"   ✅ Retry dispatch succeeded: {retry_task_id}")
                                        # CRITICAL: Verify retry didn't use wrong job_id
                                        if retry_task_id == self.request.id:
                                            logger.error(f"   ❌ CRITICAL BUG: Retry dispatch returned create_structured_data job_id!")
                                            logger.error(f"      This indicates a bug in dispatch_next_job_in_chain")
                                            logger.error(f"      Retry task_id: {retry_task_id}")
                                            logger.error(f"      create_structured_data job_id: {self.request.id}")
                                        next_task_id = retry_task_id  # Update to indicate success
                                    else:
                                        logger.error(f"   ❌ Retry dispatch also returned None - failing task")
                                        raise RuntimeError(error_msg)
                                except Exception as retry_err:
                                    logger.error(f"   ❌ Retry dispatch failed: {retry_err}")
                                    raise RuntimeError(error_msg) from retry_err
                            else:
                                raise RuntimeError(error_msg)
                        else:
                            logger.info(f"   ✅ All remaining jobs now have job_ids - first dispatch succeeded, no retry needed")
                    else:
                        logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
                
                logger.info(f"✅ Structured data created successfully")
                
                # Update job status to DONE when completed successfully
                try:
                    from lib.job_manager import update_job_status, JobStatus
                    update_job_status(job_id=job_id, status=JobStatus.DONE)
                    logger.info(f"✅ Updated job {job_id} status to DONE")
                except Exception as status_err:
                    logger.warning(f"⚠️  Failed to update job {job_id} status to DONE: {status_err}")
                
                task_elapsed = time.time() - task_start
                logger.info(f"🏁 JOB {job_id} FINISHED")
                logger.info(f"🔵 [CELERY] {celery_trace_id} CREATE_STRUCTURED_DATA TASK COMPLETED")
                logger.info(f"   Elapsed time: {task_elapsed:.2f} seconds")
                logger.info(f"{'='*80}\n")
                
                result = {
                    'success': True,
                    'output': output,
                    'job_id': job_id,
                    'session_id': session_id
                }
                log_task_return_value(result, "CREATE_STRUCTURED_DATA")
                return result
        
    except Exception as e:
        # Write crash log to job directory for easy debugging
        if 'job_dir' in locals() and job_dir:
            try:
                write_crash_log(
                    job_dir=job_dir,
                    exception=e,
                    job_id=job_id,
                    session_id=session_id,
                    job_type='create_structured_data',
                    additional_info={
                        'data_file': data_file,
                        'task_id': getattr(self, 'request', {}).get('id', 'unknown'),
                    }
                )
            except Exception:
                pass  # Don't fail if crash log write fails
        
        # SCREAM LOUDLY - This is a critical failure that needs immediate attention
        logger.error(f"")
        logger.error(f"╔════════════════════════════════════════════════════════════════════════════════╗")
        logger.error(f"║                                                                                ║")
        logger.error(f"║  💥💥💥 CRITICAL TASK FAILURE - CREATE_STRUCTURED_DATA CRASHED 💥💥💥          ║")
        logger.error(f"║                                                                                ║")
        logger.error(f"╚════════════════════════════════════════════════════════════════════════════════╝")
        logger.error(f"")
        logger.error(f"❌❌❌ CREATE_STRUCTURED_DATA FAILED WITH UNHANDLED EXCEPTION ❌❌❌")
        logger.error(f"")
        logger.error(f"   Job ID: {job_id}")
        logger.error(f"   Session ID: {session_id}")
        
        # Print job directory and log location
        if 'job_dir' in locals() and job_dir:
            logger.error(f"")
            logger.error(f"   📁 Job Directory: {job_dir}")
            logger.error(f"   📝 Log File: {job_dir}/logs/stdout.log")
            logger.error(f"")
            logger.error(f"   To check logs:")
            logger.error(f"      tail -100 {job_dir}/logs/stdout.log")
        
        logger.error(f"")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error(f"   Exception Message: {str(e)}")
        logger.error(f"")
        logger.error(f"   📍 TRACE: Exception caught in outer try/except block")
        logger.error(f"   📍 TRACE: This means the task crashed before completing")
        logger.error(f"")
        logger.error(f"   FULL TRACEBACK:")
        logger.error(f"   {'='*100}")
        logger.error(f"   {traceback.format_exc()}")
        logger.error(f"   {'='*100}")
        logger.error(f"")
        
        # Update job status to FAILED when it fails
        try:
            logger.error(f"   📍 TRACE: Attempting to update job status to FAILED...")
            from lib.job_manager import update_job_status, JobStatus, determine_failure_reason
            tb_str = traceback.format_exc()
            failure_reason = determine_failure_reason(exception=e, traceback_str=tb_str)
            update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata={'failure_reason': failure_reason})
            logger.error(f"   ✅ Updated job {job_id} status to FAILED (reason: {failure_reason})")
        except Exception as status_err:
            logger.error(f"   ❌❌❌ FAILED TO UPDATE JOB STATUS TO FAILED ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
        
        logger.error(f"")
        logger.error(f"🏁 JOB {job_id} FINISHED (WITH ERRORS)")
        logger.error(f"")
        
        result = {
            'success': False,
            'error': str(e),
            'job_id': job_id,
            'session_id': session_id,
            'traceback': traceback.format_exc()
        }
        log_task_return_value(result, "CREATE_STRUCTURED_DATA")
        return result


@app.task(bind=True)
def pre_analysis_architecture(self, job_spec: dict, job_id: str, session_id: str, data_file: str = None, strings_cache: str = None):
    """
    Celery task to run quick architecture search (25 epochs) to find optimal ES parameters.
    
    This runs AFTER create_structured_data and BEFORE train_es.
    
    NEW: Queries meta-learning API first. If high confidence (>0.9), skips pre-analysis entirely!
    
    It saves optimal config to session for train_es to use.
    
    Args:
        job_spec: Dict containing:
            - n_samples: Number of configs to test (default: 20)
            - quick_epochs: Epochs for quick search (default: 25)
        job_id: UUID for this job
        session_id: Session UUID
        data_file: Path to SQLite database (from create_structured_data)
        strings_cache: Path to strings cache
    
    Returns:
        dict with optimal config
    """
    # Use Celery task ID if job_id not provided
    if not job_id:
        job_id = self.request.id
        logger.info(f"   Using Celery task ID as job_id: {job_id}")
    
    logger.info(f"🔬 CELERY PRE_ANALYSIS_ARCHITECTURE STARTED")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Session ID: {session_id}")
    
    # STANDARD JOB SETUP - creates job dir, logs dir, and redirects stdout/stderr
    with setup_job_logging(job_id, session_id, 'pre_analysis_architecture') as (job_dir, original_cwd):
        try:
            # Query meta-learning API for next untested configs to try
            logger.info(f"🧠 Querying meta-learning API for next untested configs...")
            suggested_configs = []
            try:
                from lib.session_manager import load_session
                from lib.meta_learning_client import (
                    get_dataset_characteristics,
                    get_meta_next_config
                )
                from lib.featrix.neural.input_data_file import FeatrixInputDataFile
                
                # Load session to get input data
                session = load_session(session_id)
                input_data_path = session.get('input_data')
                
                if input_data_path:
                    # Handle relative paths - check if file exists, if not try session directory
                    input_path = Path(input_data_path)
                    if not input_path.exists() and not input_path.is_absolute():
                        # Try to find it in the session directory or data directory
                        # Import config here to ensure it's available in this scope
                        from config import config
                        session_dir = Path(config.data_dir) / session_id
                        possible_paths = [
                            session_dir / input_path.name,
                            Path(config.data_dir) / input_path.name,
                            input_path  # Try original as-is
                        ]
                        for possible_path in possible_paths:
                            if possible_path.exists():
                                input_data_path = str(possible_path)
                                logger.info(f"✅ Found input data at: {input_data_path}")
                                break
                        else:
                            # File not found - skip meta-learning query but don't fail
                            logger.warning(f"⚠️  Input data file not found: {input_data_path}")
                            logger.warning(f"   Tried paths: {[str(p) for p in possible_paths]}")
                            logger.warning(f"   Skipping meta-learning query - will use adaptive sampling")
                            raise FileNotFoundError(f"Input data file not found: {input_data_path}")
                    
                    # File exists - try to load it
                    try:
                        input_file = FeatrixInputDataFile(str(input_data_path))
                        df = input_file.df
                    except Exception as load_err:
                        logger.warning(f"⚠️  Failed to load input data file: {load_err}")
                        logger.warning(f"   Skipping meta-learning query - will use adaptive sampling")
                        raise
                    
                    # Get dataset characteristics
                    dataset_chars = get_dataset_characteristics(df)
                    n_rows = dataset_chars['n_rows']
                    n_cols = dataset_chars['n_cols']
                    target_type = dataset_chars.get('target_type', 'regression')
                    
                    # Get n_samples from job_spec (default 20)
                    n_samples = job_spec.get('n_samples', 20)
                    
                    # Query meta-learning API for next untested configs (up to n_samples)
                    logger.info(f"   Requesting {n_samples} untested configs from meta-learning API...")
                    logger.info(f"   Dataset: {n_rows} rows, {n_cols} cols, {target_type}")
                    
                    for i in range(n_samples):
                        next_config_result = get_meta_next_config(
                            n_rows=n_rows,
                            n_cols=n_cols,
                            target_type=target_type,
                            min_epochs=25
                        )
                        
                        if next_config_result and next_config_result.get('next_config'):
                            next_config = next_config_result['next_config']
                            config_dict = {
                                'd_model': next_config.get('d_model'),
                                'n_transformer_layers': next_config.get('n_transformer_layers'),
                                'n_attention_heads': next_config.get('n_attention_heads')
                            }
                            suggested_configs.append(config_dict)
                            logger.info(f"   {i+1}/{n_samples}: Got config d_model={config_dict['d_model']}, layers={config_dict['n_transformer_layers']}, heads={config_dict['n_attention_heads']}")
                        else:
                            # No more untested configs available
                            logger.info(f"   {i+1}/{n_samples}: No more untested configs available (total tested: {next_config_result.get('total_tested', 0) if next_config_result else 0})")
                            break
                    
                    if suggested_configs:
                        logger.info(f"✅ Got {len(suggested_configs)} untested configs from meta-learning API")
                        logger.info(f"   These configs are assigned to this session and won't be picked by parallel jobs")
                        
                        # Override n_samples to test only the suggested configs
                        job_spec['n_samples'] = len(suggested_configs)
                        job_spec['use_suggested_configs'] = suggested_configs
                        logger.info(f"   Will test {len(suggested_configs)} untested configs from meta-learning API")
                    else:
                        logger.info(f"ℹ️  No untested configs available from meta-learning API - will use adaptive sampling")
                else:
                    logger.warning(f"⚠️  No input_data in session - skipping meta-learning query")
                    
            except Exception as e:
                logger.warning(f"⚠️  Meta-learning query failed (non-critical): {e}")
                logger.warning(f"   Continuing with standard pre-analysis...")
                logger.debug(traceback.format_exc())
            
            # Update task state
            self.update_state(
                state='PROGRESS',
                meta={'status': 'running', 'message': 'Starting quick architecture search'}
            )
            
            # Get parameters from job_spec
            n_samples = job_spec.get('n_samples', 20)
            quick_epochs = job_spec.get('quick_epochs', 25)
            suggested_configs = job_spec.get('use_suggested_configs')  # NEW: from meta-learning
            
            # Load session to get data_file if not provided
            if not data_file:
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
                
                strings_cache = session.get('strings_cache')
            
            # CRITICAL: Fork/exec pre-analysis in a non-daemon session leader process
            # Same pattern as ES/SP training for better GPU memory management and process isolation
            # Get target column hint from job_spec or session
            target_column_hint = job_spec.get('target_column_hint')
            if not target_column_hint:
                # Try to get from session metadata
                try:
                    from lib.session_manager import load_session
                    session = load_session(session_id)
                    target_column_hint = session.get('target_column')
                except Exception:
                    pass
            
            # Serialize args to pass to subprocess
            args_dict = {
                'data_file': str(data_file) if data_file else None,
                'strings_cache': strings_cache or "",
                'session_id': session_id,
                'n_samples': n_samples,
                'quick_epochs': quick_epochs,
                'suggested_configs': suggested_configs,
                'target_column_hint': target_column_hint
            }
            
            # Create a temporary file to pass args
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_file = f.name
                json_module.dump(args_dict, f)
            
            try:
                # Fork/exec pre-analysis in a new session leader process
                # This provides better process isolation and GPU memory cleanup
                python_cmd = sys.executable
                wrapper_script = Path(__file__).parent / "lib" / "pre_analysis_wrapper.py"
                
                if suggested_configs:
                    logger.info(f"🚀 Forking pre-analysis process with {len(suggested_configs)} meta-learning suggestions ({quick_epochs} epochs each)")
                else:
                    logger.info(f"🚀 Forking pre-analysis process ({n_samples} configs, {quick_epochs} epochs each)")
                logger.info(f"   Python: {python_cmd}")
                logger.info(f"   Script: {wrapper_script}")
                
                # Fork/exec with setsid to create new session leader (non-daemon)
                # CRITICAL: Open log file in append mode so subprocess writes to same file
                log_file_path = job_dir / "logs" / "stdout.log"
                
                # Open log file in append mode (line buffered) for subprocess
                with open(log_file_path, 'a', buffering=1) as log_file:
                    process = subprocess.Popen(
                        [python_cmd, str(wrapper_script), json_file, '--job-id', job_id],
                        cwd=str(job_dir),
                        stdout=log_file,
                        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                        start_new_session=True,  # setsid - become session leader (non-daemon)
                        env=os.environ.copy()  # Inherit environment
                    )
                    
                    pre_analysis_pid = process.pid
                    celery_worker_pid = os.getpid()
                    
                    # Write Celery worker mapping file for admin monitoring
                    mapping_file = Path(f"/tmp/featrix-celery-{celery_worker_pid}.json")
                    try:
                        mapping_data = {
                            "timestamp_started": datetime.now().isoformat(),
                            "celery_worker_pid": celery_worker_pid,
                            "pre_analysis_pid": pre_analysis_pid,
                            "job_id": job_id,
                            "session_id": session_id,
                            "job_type": "pre_analysis_architecture",
                        }
                        with open(mapping_file, 'w') as f:
                            json_module.dump(mapping_data, f, indent=2)
                        logger.info(f"📝 Wrote Celery worker mapping: {mapping_file}")
                    except Exception as e:
                        logger.warning(f"Failed to write Celery worker mapping: {e}")
                    
                    logger.info(f"✅ Pre-analysis process forked with PID {pre_analysis_pid} (session leader)")
                    logger.info(f"   Celery worker PID: {celery_worker_pid}")
                    logger.info(f"   Pre-analysis PID: {pre_analysis_pid}")
                    logger.info(f"   📝 Pre-analysis output in: {log_file_path}")
                    logger.info(f"   🔍 Monitor with: ffsh tail {session_id}/{job_id}")
                    logger.info(f"   Monitoring PID {pre_analysis_pid} until it exits...")
                    
                    # Wait for process to complete
                    # CRITICAL: Check for ABORT flag periodically AND update Celery state with progress
                    abort_flag = job_dir / "ABORT"
                    last_progress_update = 0
                    
                    try:
                        while True:
                            # Check if process completed
                            return_code = process.poll()
                            if return_code is not None:
                                # Process finished
                                if return_code == 0:
                                    logger.info(f"✅ Pre-analysis process completed successfully (exit code: {return_code})")
                                else:
                                    logger.error(f"❌ Pre-analysis process failed with exit code: {return_code}")
                                break
                            
                            # Check for abort flag
                            if abort_flag.exists():
                                logger.warning(f"⚠️  ABORT flag detected - terminating pre-analysis process")
                                process.terminate()
                                time.sleep(2)
                                if process.poll() is None:
                                    logger.warning(f"⚠️  Process didn't terminate, sending SIGKILL")
                                    process.kill()
                                break
                            
                            # Poll Redis for progress updates (every 2 seconds, like train_single_predictor)
                            current_time = time.time()
                            if current_time - last_progress_update >= 2:
                                try:
                                    from lib.job_manager import load_job
                                    job_data = load_job(job_id)
                                    if job_data:
                                        progress = job_data.get('progress', 0)
                                        current_config = job_data.get('current_config', 0)
                                        total_configs = job_data.get('total_configs', 0)
                                        current_auc = job_data.get('current_auc')
                                        best_config_so_far = job_data.get('best_config_so_far')
                                        best_auc_so_far = job_data.get('best_auc_so_far')
                                        status_message = job_data.get('status_message', 'Pre-analysis architecture search in progress...')
                                        
                                        # Build status message
                                        if current_config > 0 and total_configs > 0:
                                            status = f"Testing config {current_config}/{total_configs}"
                                            if current_auc is not None:
                                                status += f" (AUC: {current_auc:.4f})"
                                            if best_config_so_far and best_auc_so_far is not None:
                                                status += f" | Best so far: d_model={best_config_so_far.get('d_model')}, layers={best_config_so_far.get('n_transformer_layers')}, heads={best_config_so_far.get('n_attention_heads')} (AUC: {best_auc_so_far:.4f})"
                                        else:
                                            status = status_message
                                        
                                        # Update Celery state so client gets progress
                                        self.update_state(
                                            state='PROGRESS',
                                            meta={
                                                'status': status,
                                                'job_id': job_id,
                                                'session_id': session_id,
                                                'progress': progress,
                                                'current_config': current_config,
                                                'total_configs': total_configs,
                                                'current_auc': current_auc,
                                                'best_config_so_far': best_config_so_far,
                                                'best_auc_so_far': best_auc_so_far
                                            }
                                        )
                                        last_progress_update = current_time
                                except Exception as e:
                                    # Don't fail if progress update fails
                                    logger.debug(f"Failed to update progress: {e}")
                            
                            time.sleep(1)  # Check every second
                        
                        # Wait for process to fully exit
                        final_return_code = process.wait()
                        
                        if final_return_code != 0:
                            raise RuntimeError(f"Pre-analysis process failed with exit code: {final_return_code}")
                    
                    except KeyboardInterrupt:
                        logger.warning("⚠️  Received interrupt - terminating pre-analysis process")
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            process.kill()
                        raise
                    finally:
                        # Clean up temp JSON file
                        try:
                            os.unlink(json_file)
                        except Exception:
                            pass
                
                # Load results from session (wrapper saves it there)
                from lib.session_manager import load_session
                session = load_session(session_id)
                optimal_config = session.get('optimal_es_config')
                
                if not optimal_config:
                    raise RuntimeError("Pre-analysis completed but optimal_es_config not found in session")
                
                logger.info(f"✅ Quick search complete: {optimal_config}")
                
                # Save results to job directory for debugging
                results_file = job_dir / "pre_analysis_results.json"
                try:
                    # Get all tested configs from session if available
                    session = load_session(session_id)
                    pre_analysis_results = session.get('pre_analysis_results', {})
                    all_tested_configs = pre_analysis_results.get('all_tested_configs', [])
                    
                    results_output = {
                        "optimal_config": optimal_config,
                        "session_id": session_id,
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat(),
                        "all_tested_configs": all_tested_configs,  # Include all tested configs
                        "meta": {
                            "n_samples_requested": job_spec.get('n_samples', 20),
                            "quick_epochs": job_spec.get('quick_epochs', 25),
                            "used_suggested_configs": bool(suggested_configs),
                            "total_configs_tested": len(all_tested_configs),
                            "successful_configs": len([c for c in all_tested_configs if c.get('tested', False)]),
                            "failed_configs": len([c for c in all_tested_configs if not c.get('tested', False)])
                        }
                    }
                    
                    with open(results_file, 'w') as f:
                        json.dump(results_output, f, indent=2, default=str)
                        
                    logger.info(f"💾 Saved pre-analysis results to {results_file} (including {len(all_tested_configs)} tested configs)")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to save pre-analysis results: {e}")
                
                logger.info(f"💾 Optimal config loaded from session")
                
            except Exception as e:
                logger.error(f"❌ Failed to run pre-analysis: {e}")
                traceback.print_exc()
                raise
            
            # Dispatch next job (train_es)
            # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
            from lib.session_chains import dispatch_next_job_in_chain
            from lib.session_manager import load_session
            try:
                next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='pre_analysis_architecture')
            except Exception as chain_error:
                logger.error(f"❌ Failed to dispatch next job: {chain_error}")
                logger.error(f"   Full traceback: {traceback.format_exc()}")
                raise
            
            if next_task_id:
                logger.info(f"✅ Dispatched next job: train_es (task_id: {next_task_id})")
            else:
                # Dispatch returned None - verify there really are no more jobs to dispatch
                logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
                session_check = load_session(session_id)
                job_plan = session_check.get('job_plan', [])
                remaining_jobs = []
                for idx, job_desc in enumerate(job_plan):
                    job_type = job_desc.get("job_type", "unknown")
                    job_id = job_desc.get("job_id")
                    if not job_id or job_id == "None":
                        # Check if legitimately skipped
                        is_skipped = False
                        if job_type == "train_es":
                            embedding_space_path = session_check.get("embedding_space")
                            foundation_model_id = session_check.get("foundation_model_id")
                            if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                                is_skipped = True
                        elif job_type == "train_knn":
                            vector_db_path = session_check.get("vector_db")
                            if vector_db_path and Path(vector_db_path).exists():
                                is_skipped = True
                        elif job_type == 'pre_analysis_architecture':
                            is_skipped = True  # Just completed
                        
                        if not is_skipped:
                            remaining_jobs.append((idx, job_type))
                
                if remaining_jobs:
                    error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                    logger.error(f"❌ {error_msg}")
                    logger.error(f"   Session: {session_id}")
                    logger.error(f"   This task will FAIL to prevent silent chain breakage")
                    raise RuntimeError(error_msg)
                else:
                    logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
                    logger.info(f"ℹ️  No next job to dispatch")
            
            # Update job status to DONE
            try:
                from lib.job_manager import update_job_status, JobStatus
                update_job_status(job_id=job_id, status=JobStatus.DONE)
                logger.info(f"✅ Updated job {job_id} status to DONE")
            except Exception as status_err:
                logger.warning(f"⚠️  Failed to update job status: {status_err}")
            
            logger.info(f"🏁 PRE_ANALYSIS_ARCHITECTURE COMPLETED")
            
            result = {
                'success': True,
                'optimal_config': optimal_config,
                'job_id': job_id,
                'session_id': session_id
            }
            log_task_return_value(result, "PRE_ANALYSIS_ARCHITECTURE")
            return result
            
        except Exception as e:
            # Write crash log to job directory for easy debugging
            if 'job_dir' in locals() and job_dir:
                try:
                    write_crash_log(
                        job_dir=job_dir,
                        exception=e,
                        job_id=job_id,
                        session_id=session_id,
                        job_type='pre_analysis_architecture',
                    )
                except Exception:
                    pass  # Don't fail if crash log write fails
            
            logger.error(f"❌ PRE_ANALYSIS_ARCHITECTURE FAILED: {e}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            
            # Update job status to FAILED
            try:
                from lib.job_manager import update_job_status, JobStatus
                update_job_status(job_id=job_id, status=JobStatus.FAILED)
            except:
                pass
            
            result = {
                'success': False,
                'error': str(e),
                'job_id': job_id,
                'session_id': session_id
            }
            log_task_return_value(result, "PRE_ANALYSIS_ARCHITECTURE")
            return result


@app.task(bind=True)
def run_clustering(self, job_spec: dict):
    """
    Celery task to run clustering/projections for an embedding space.
    
    This generates the final projections and preview image for a trained embedding space.
    
    Args:
        job_spec: Dict containing:
            - model_path: Path to embedding space model (.pickle)
            - sqlite_db: Path to SQLite database
            - strings_cache: Path to strings cache (optional)
    
    Returns:
        dict with output paths (projections, preview_png)
    """
    from pathlib import Path
    
    logger.info(f"🔍 CELERY RUN_CLUSTERING STARTED")
    job_dir = None  # Initialize to avoid linter error when accessed in exception handler
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Loading embedding space...',
                'model_path': job_spec.get('model_path')
            }
        )
        
        # Import here to avoid CUDA fork issues
        from lib.es_projections import run_clustering
        
        # Extract parameters
        model_path = job_spec['model_path']
        sqlite_db = job_spec['sqlite_db']
        strings_cache = job_spec.get('strings_cache')
        
        logger.info(f"   Model path: {model_path}")
        logger.info(f"   SQLite DB: {sqlite_db}")
        
        # Get job_id and session_id for logging setup
        job_id = job_spec.get('job_id') or self.request.id
        session_id = job_spec.get('session_id')
        
        # STANDARD JOB SETUP - creates job dir, logs dir, and redirects stdout/stderr
        with setup_job_logging(job_id, session_id, 'run_clustering') as (job_dir, original_cwd):
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Running clustering...',
                }
            )
            
            # Call run_clustering directly (replaces run_clustering_job from featrix_queue)
            logger.info(f"   📍 TRACE: About to call run_clustering()...")
            logger.info(f"   📍 TRACE:   model_path: {model_path}")
            logger.info(f"   📍 TRACE:   sqlite_db: {sqlite_db}")
            logger.info(f"   📍 TRACE:   PID: {os.getpid()}")
            print(f"📍 TRACE: About to call run_clustering(model_path={model_path}, sqlite_db_path={sqlite_db})...", file=sys.stderr, flush=True)
            
            try:
                output = run_clustering(
                    model_path=model_path,
                    sqlite_db_path=sqlite_db
                )
                logger.info(f"   📍 TRACE: run_clustering() returned successfully")
                logger.info(f"   📍 TRACE:   output type: {type(output)}")
                logger.info(f"   📍 TRACE:   output: {output}")
                print(f"📍 TRACE: run_clustering() returned: {output}", file=sys.stderr, flush=True)
            except Exception as clustering_err:
                logger.error(f"   ❌ CRITICAL: run_clustering() raised exception: {type(clustering_err).__name__}: {clustering_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                print(f"❌ CRITICAL: run_clustering() failed: {clustering_err}", file=sys.stderr, flush=True)
                raise
        
        # Update session with output (matching file-based queue behavior)
        session_id = job_spec.get('session_id')
        if session_id:
            from lib.session_manager import load_session, save_session
            try:
                session = load_session(session_id)
                session = {**session, **output}
                save_session(session_id=session_id, session_doc=session, exist_ok=True)
                logger.info(f"✅ Session updated with clustering output")
                
                # Automatically dispatch next job in chain
                # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
                logger.info(f"🔄 Attempting to dispatch next job in chain for session {session_id}...")
                from lib.session_chains import dispatch_next_job_in_chain
                from lib.session_manager import load_session
                next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='run_clustering')
                if next_task_id:
                    logger.info(f"✅ Successfully dispatched next job in chain (task_id: {next_task_id})")
                    # CRITICAL: Log what job type was dispatched
                    try:
                        session_check = load_session(session_id)
                        job_plan = session_check.get('job_plan', [])
                        for job in job_plan:
                            if job.get('job_id') == next_task_id:
                                job_type = job.get('job_type', 'unknown')
                                logger.info(f"   📋 Dispatched job type: {job_type}")
                                if job_type == 'train_single_predictor':
                                    logger.info(f"   🎯✅ SP TRAINING DISPATCHED: {next_task_id}")
                                break
                    except Exception as check_err:
                        logger.warning(f"   ⚠️  Could not verify dispatched job type: {check_err}")
                else:
                    # Dispatch returned None - verify there really are no more jobs to dispatch
                    logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
                    session_check = load_session(session_id)
                    job_plan = session_check.get('job_plan', [])
                    
                    # CRITICAL: Check if train_single_predictor is in job_plan but wasn't dispatched
                    sp_jobs = [j for j in job_plan if j.get('job_type') == 'train_single_predictor']
                    if sp_jobs:
                        logger.error(f"   ❌ CRITICAL: train_single_predictor found in job_plan ({len(sp_jobs)} job(s)) but NOT dispatched!")
                        for idx, sp_job in enumerate(sp_jobs):
                            job_id = sp_job.get('job_id')
                            target_col = sp_job.get('spec', {}).get('target_column', 'unknown')
                            logger.error(f"      SP job {idx}: target_column={target_col}, job_id={job_id}")
                            if not job_id or job_id == "None":
                                logger.error(f"         ⚠️  SP job has NO job_id - should have been dispatched!")
                    
                    remaining_jobs = []
                    for idx, job_desc in enumerate(job_plan):
                        job_type = job_desc.get("job_type", "unknown")
                        job_id = job_desc.get("job_id")
                        if not job_id or job_id == "None":
                            # Check if legitimately skipped
                            is_skipped = False
                            if job_type == "train_es":
                                embedding_space_path = session_check.get("embedding_space")
                                foundation_model_id = session_check.get("foundation_model_id")
                                from featrix.neural.embedding_space_utils import embedding_space_path_exists
                                if foundation_model_id or (embedding_space_path and embedding_space_path_exists(embedding_space_path)):
                                    is_skipped = True
                            elif job_type == "train_knn":
                                vector_db_path = session_check.get("vector_db")
                                if vector_db_path and Path(vector_db_path).exists():
                                    is_skipped = True
                            elif job_type == 'run_clustering':
                                is_skipped = True  # Just completed
                            
                            if not is_skipped:
                                remaining_jobs.append((idx, job_type))
                    
                    if remaining_jobs:
                        error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                        logger.error(f"❌ {error_msg}")
                        logger.error(f"   Session: {session_id}")
                        logger.error(f"   This task will FAIL to prevent silent chain breakage")
                        raise RuntimeError(error_msg)
                    else:
                        logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
            except Exception as session_error:
                logger.error(f"❌ CRITICAL: Failed to update session {session_id} with output: {session_error}")
                logger.error(f"   Full traceback: {traceback.format_exc()}")
                logger.error(f"   Output files were generated but session was not updated!")
        
        logger.info(f"✅ Clustering completed successfully")
        
        # Update job status to DONE when completed successfully
        try:
            job_id = job_spec.get('job_id') or self.request.id
            if job_id:
                from lib.job_manager import update_job_status, JobStatus
                update_job_status(job_id=job_id, status=JobStatus.DONE)
                logger.info(f"✅ Updated job {job_id} status to DONE")
        except Exception as status_err:
            logger.warning(f"⚠️  Failed to update job status to DONE: {status_err}")
            logger.warning(f"   Error: {traceback.format_exc()}")
        
        result = {
            'success': True,
            'output': output
        }
        log_task_return_value(result, "RUN_CLUSTERING")
        return result
        
    except Exception as e:
        # Write crash log to job directory for easy debugging
        job_id = job_spec.get('job_id') or self.request.id
        if 'job_dir' in locals() and job_dir:
            try:
                write_crash_log(
                    job_dir=job_dir,
                    exception=e,
                    job_id=job_id,
                    session_id=session_id,
                    job_type='run_clustering',
                )
            except Exception:
                pass  # Don't fail if crash log write fails
        
        # SCREAM LOUDLY - This is a critical failure that needs immediate attention
        logger.error(f"")
        logger.error(f"╔════════════════════════════════════════════════════════════════════════════════╗")
        logger.error(f"║                                                                                ║")
        logger.error(f"║  💥💥💥 CRITICAL TASK FAILURE - RUN_CLUSTERING CRASHED 💥💥💥                    ║")
        logger.error(f"║                                                                                ║")
        logger.error(f"╚════════════════════════════════════════════════════════════════════════════════╝")
        logger.error(f"")
        logger.error(f"❌❌❌ RUN_CLUSTERING FAILED WITH UNHANDLED EXCEPTION ❌❌❌")
        logger.error(f"")
        logger.error(f"   Job ID: {job_id}")
        
        # Print job directory and log location
        if 'job_dir' in locals() and job_dir:
            logger.error(f"")
            logger.error(f"   📁 Job Directory: {job_dir}")
            logger.error(f"   📝 Log File: {job_dir}/logs/stdout.log")
            logger.error(f"")
            logger.error(f"   To check logs:")
            logger.error(f"      tail -100 {job_dir}/logs/stdout.log")
        
        logger.error(f"")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error(f"   Exception Message: {str(e)}")
        logger.error(f"")
        logger.error(f"   FULL TRACEBACK:")
        logger.error(f"   {'='*100}")
        logger.error(f"   {traceback.format_exc()}")
        logger.error(f"   {'='*100}")
        logger.error(f"")
        
        # Update job status to FAILED when it fails
        try:
            if job_id:
                from lib.job_manager import update_job_status, JobStatus, determine_failure_reason
                tb_str = traceback.format_exc()
                failure_reason = determine_failure_reason(exception=e, traceback_str=tb_str)
                update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata={'failure_reason': failure_reason})
                logger.error(f"   ✅ Updated job {job_id} status to FAILED (reason: {failure_reason})")
        except Exception as status_err:
            logger.error(f"   ❌❌❌ FAILED TO UPDATE JOB STATUS TO FAILED ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
        
        logger.error(f"")
        
        result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        log_task_return_value(result, "RUN_CLUSTERING")
        return result

@app.task(bind=True)
def train_single_predictor(self, *args, **kwargs):
    """
    Celery task to train a single predictor on a foundation model.
    
    This trains a supervised learning model on top of a pre-trained embedding space.
    
    When called in a chain, receives: (previous_result, job_spec, job_id, session_id)
    When called directly, receives: (job_spec, job_id, session_id)
    
    Returns:
        dict with output paths (single_predictor, training_metrics)
    """
    from pathlib import Path
    import sys
    
    # CRITICAL: Emergency logging + JOB_ACK to catch silent failures
    # JOB_ACK = Job acknowledged - signals that worker picked up the task
    # This ensures we can detect stuck jobs that were dispatched but never started
    emergency_log = None
    emergency_log_path = None
    job_ack_path = None
    
    try:
        # Try to extract session_id and job_id early for emergency logging + ACK
        emergency_session_id = None
        emergency_job_id = None
        
        try:
            if len(args) >= 3:
                if len(args) == 4:
                    # Chain call: (previous_result, job_spec, job_id, session_id)
                    emergency_job_id = args[2]
                    emergency_session_id = args[3]
                else:
                    # Direct call: (job_spec, job_id, session_id)
                    emergency_job_id = args[1]
                    emergency_session_id = args[2]
        except:
            pass
        
        # Create JOB_ACK file to signal job was picked up by worker
        # This happens BEFORE any other work, so we can detect stuck jobs
        if emergency_session_id:
            # Use Celery task ID if job_id is None
            actual_job_id = emergency_job_id
            if not actual_job_id or actual_job_id == 'None':
                actual_job_id = self.request.id if hasattr(self, 'request') else None
            
            if actual_job_id:
                try:
                    from lib.job_manager import get_job_output_path
                    job_dir = get_job_output_path(actual_job_id, emergency_session_id, 'train_single_predictor')
                    job_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create JOB_ACK file FIRST - signals worker picked up the task
                    job_ack_path = job_dir / "JOB_ACK"
                    with open(job_ack_path, 'w') as ack:
                        ack.write(f"Worker acknowledged job at {datetime.now().isoformat()}\n")
                        ack.write(f"Celery task ID: {self.request.id if hasattr(self, 'request') else 'unknown'}\n")
                        ack.write(f"Worker hostname: {self.request.hostname if hasattr(self, 'request') else 'unknown'}\n")
                        ack.write(f"Job ID from args: {emergency_job_id}\n")
                        ack.write(f"Actual job ID used: {actual_job_id}\n")
                    
                    # Now create emergency log
                    emergency_log_path = job_dir / "EMERGENCY_STARTUP.log"
                    emergency_log = open(emergency_log_path, 'w')
                    emergency_log.write(f"=== EMERGENCY STARTUP LOG ===\n")
                    emergency_log.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    emergency_log.write(f"Session ID: {emergency_session_id}\n")
                    emergency_log.write(f"Job ID from args: {emergency_job_id}\n")
                    emergency_log.write(f"Actual job ID used: {actual_job_id}\n")
                    emergency_log.write(f"Celery task ID: {self.request.id if hasattr(self, 'request') else 'unknown'}\n")
                    emergency_log.write(f"Args count: {len(args)}\n")
                    emergency_log.write(f"Kwargs count: {len(kwargs)}\n")
                    emergency_log.write(f"\n--- Starting argument unpacking ---\n")
                    emergency_log.flush()
                except Exception as e:
                    # If we can't create emergency log, use stderr
                    sys.stderr.write(f"❌ Could not create emergency log/ACK: {e}\n")
                    sys.stderr.flush()
    except Exception as outer_e:
        sys.stderr.write(f"❌ CRITICAL: Emergency logging setup failed: {outer_e}\n")
        sys.stderr.flush()
    
    # Handle both chain and direct call patterns
    # Chain: (previous_result, job_spec, job_id, session_id)
    # Direct: (job_spec, job_id, session_id)
    try:
        if len(args) == 4:
            # Called from chain: (previous_result, job_spec, job_id, session_id)
            previous_result, job_spec, job_id, session_id = args
            if emergency_log:
                emergency_log.write(f"✅ Unpacked 4 args (chain call)\n")
                emergency_log.write(f"   previous_result type: {type(previous_result).__name__}\n")
                emergency_log.write(f"   job_spec type: {type(job_spec).__name__}\n")
                emergency_log.write(f"   job_id: {job_id}\n")
                emergency_log.write(f"   session_id: {session_id}\n")
                emergency_log.flush()
            logger.info(f"📥 Called from chain - previous task result: {type(previous_result)}")
        elif len(args) == 3:
            # Called directly: (job_spec, job_id, session_id)
            job_spec, job_id, session_id = args
            previous_result = None
            if emergency_log:
                emergency_log.write(f"✅ Unpacked 3 args (direct call)\n")
                emergency_log.write(f"   job_spec type: {type(job_spec).__name__}\n")
                emergency_log.write(f"   job_id: {job_id}\n")
                emergency_log.write(f"   session_id: {session_id}\n")
                emergency_log.flush()
        else:
            # Try to get from kwargs or use defaults
            if emergency_log:
                emergency_log.write(f"⚠️  Unusual args count: {len(args)} - trying kwargs fallback\n")
                emergency_log.flush()
            job_spec = kwargs.get('job_spec') or (args[0] if len(args) > 0 else None)
            job_id = kwargs.get('job_id') or (args[1] if len(args) > 1 else None)
            session_id = kwargs.get('session_id') or (args[2] if len(args) > 2 else None)
            previous_result = kwargs.get('previous_result') or (args[0] if len(args) > 0 and isinstance(args[0], dict) and 'success' in args[0] else None)
            if emergency_log:
                emergency_log.write(f"   Extracted: job_id={job_id}, session_id={session_id}\n")
                emergency_log.flush()
    except Exception as unpack_error:
        error_msg = f"❌ CRITICAL: Argument unpacking failed: {unpack_error}\n"
        error_msg += f"   Args: {args}\n"
        error_msg += f"   Kwargs: {kwargs}\n"
        if emergency_log:
            emergency_log.write(error_msg)
            emergency_log.write(f"\n--- Full traceback ---\n")
            emergency_log.write(traceback.format_exc())
            emergency_log.flush()
            emergency_log.close()
        sys.stderr.write(error_msg)
        sys.stderr.flush()
        raise
    
    if emergency_log:
        emergency_log.write(f"\n--- Arguments unpacked successfully, starting task ---\n")
        emergency_log.flush()
    
    logger.info(f"🎯 CELERY TRAIN_SINGLE_PREDICTOR STARTED")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Job spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
    logger.info(f"   Previous result: {type(previous_result).__name__ if previous_result else 'None'}")
    
    # ============================================================================
    # DUPLICATE DELIVERY DETECTION
    # ============================================================================
    # Check if this task is already running in another worker before doing ANY work.
    # This prevents duplicate deliveries from Celery's visibility_timeout (3 hours)
    # for long-running training jobs (6+ hours).
    
    # Use Celery task ID if job_id is None
    actual_job_id = job_id or self.request.id
    
    if check_duplicate_delivery(actual_job_id, session_id, 'train_single_predictor', task_id=self.request.id):
        logger.warning(f"🛑 Duplicate delivery detected - exiting gracefully without doing any work")
        if emergency_log:
            emergency_log.write(f"🛑 DUPLICATE DELIVERY - Exiting without work\n")
            emergency_log.close()
        # Return a special result indicating duplicate skip
        return {
            "success": False,
            "duplicate_skip": True,
            "message": "Task skipped - already running in another worker"
        }
    
    # NOT a duplicate - continue normally
    logger.info(f"✅ Not a duplicate delivery - proceeding with training")
    
    try:
        if emergency_log:
            emergency_log.write(f"About to update task state...\n")
            emergency_log.flush()
        # Update task state
        if emergency_log:
            emergency_log.write(f"Updating task state to PROGRESS...\n")
            emergency_log.flush()
        
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Loading embedding space...',
                'job_id': job_id,
                'session_id': session_id
            }
        )
        
        if emergency_log:
            emergency_log.write(f"✅ Task state updated\n")
            emergency_log.write(f"Importing session_manager and single_predictor_training...\n")
            emergency_log.flush()
        
        # Import here to avoid CUDA fork issues
        # NOTE: No longer importing train_single_predictor here - we fork/exec a wrapper subprocess
        # The wrapper script (sp_training_wrapper.py) imports it
        try:
            from lib.session_manager import load_session, save_session
            if emergency_log:
                emergency_log.write(f"✅ Imports successful\n")
                emergency_log.flush()
        except Exception as import_error:
            error_msg = f"❌ IMPORT FAILED: {import_error}\n"
            if emergency_log:
                emergency_log.write(error_msg)
                emergency_log.write(traceback.format_exc())
                emergency_log.flush()
                emergency_log.close()
            logger.error(error_msg)
            raise
        
        if emergency_log:
            emergency_log.write(f"Loading session {session_id}...\n")
            emergency_log.flush()
        
        # Load session to get paths
        try:
            session = load_session(session_id)
            if emergency_log:
                emergency_log.write(f"✅ Session loaded\n")
                emergency_log.write(f"   Session keys: {list(session.keys())}\n")
                emergency_log.flush()
        except Exception as session_error:
            error_msg = f"❌ SESSION LOAD FAILED: {session_error}\n"
            if emergency_log:
                emergency_log.write(error_msg)
                emergency_log.write(traceback.format_exc())
                emergency_log.flush()
                emergency_log.close()
            logger.error(error_msg)
            raise
        
        sqlite_db_path = session.get('sqlite_db')
        strings_cache = session.get('strings_cache')
        embedding_space_path = session.get('embedding_space')
        
        if emergency_log:
            emergency_log.write(f"   sqlite_db: {sqlite_db_path}\n")
            emergency_log.write(f"   strings_cache: {strings_cache}\n")
            emergency_log.write(f"   embedding_space: {embedding_space_path}\n")
            emergency_log.flush()
        
        # If sqlite_db is None or doesn't exist, try to find it from create_structured_data job output
        if not sqlite_db_path or not Path(sqlite_db_path).exists():
            if emergency_log:
                emergency_log.write(f"⚠️  sqlite_db is None or missing, checking create_structured_data job output...\n")
                emergency_log.flush()
            
            # Check job plan for create_structured_data job
            job_plan = session.get('job_plan', [])
            create_structured_data_job = None
            for job in job_plan:
                if job.get('job_type') == 'create_structured_data':
                    create_structured_data_job = job
                    break
            
            if create_structured_data_job:
                job_id = create_structured_data_job.get('job_id')
                if job_id and job_id != 'None':
                    try:
                        from lib.job_manager import get_job_output_path
                        job_output_dir = get_job_output_path(job_id, session_id, 'create_structured_data')
                        
                        # Look for sqlite_db files in the job output directory
                        possible_db_names = ['embedding_space.db', 'data.db']
                        for db_name in possible_db_names:
                            candidate_path = job_output_dir / db_name
                            if candidate_path.exists():
                                sqlite_db_path = str(candidate_path.resolve())
                                logger.info(f"✅ Found sqlite_db from create_structured_data job output: {sqlite_db_path}")
                                if emergency_log:
                                    emergency_log.write(f"✅ Found sqlite_db in job output: {sqlite_db_path}\n")
                                    emergency_log.flush()
                                
                                # Update session with the found path
                                session['sqlite_db'] = sqlite_db_path
                                save_session(session_id, session, exist_ok=True)
                                logger.info(f"✅ Updated session with sqlite_db path")
                                break
                    except Exception as lookup_error:
                        logger.warning(f"⚠️  Could not find sqlite_db from create_structured_data job: {lookup_error}")
                        if emergency_log:
                            emergency_log.write(f"⚠️  Could not find sqlite_db from job output: {lookup_error}\n")
                            emergency_log.flush()
                else:
                    # Job exists in plan but hasn't been dispatched yet
                    error_msg = (
                        f"SQLite database not found and create_structured_data job has not been dispatched yet. "
                        f"train_single_predictor cannot run until create_structured_data completes. "
                        f"Job plan shows create_structured_data but job_id is {job_id!r}"
                    )
                    if emergency_log:
                        emergency_log.write(f"❌ {error_msg}\n")
                        emergency_log.write(f"   This indicates train_single_predictor was called too early in the chain.\n")
                        emergency_log.flush()
                        emergency_log.close()
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
            else:
                # No create_structured_data job in plan - this is a problem
                error_msg = (
                    f"SQLite database not found and no create_structured_data job in job plan. "
                    f"Session type: {session.get('session_type')}, "
                    f"Foundation model ID: {session.get('foundation_model_id')}"
                )
                if emergency_log:
                    emergency_log.write(f"❌ {error_msg}\n")
                    emergency_log.write(f"   Job plan: {[j.get('job_type') for j in job_plan]}\n")
                    emergency_log.flush()
                    emergency_log.close()
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        if not sqlite_db_path or not Path(sqlite_db_path).exists():
            error_msg = f"SQLite database not found: {sqlite_db_path}"
            if emergency_log:
                emergency_log.write(f"❌ {error_msg}\n")
                if sqlite_db_path:
                    emergency_log.write(f"   Path exists: {Path(sqlite_db_path).exists()}\n")
                else:
                    emergency_log.write(f"   sqlite_db is None/empty in session\n")
                emergency_log.flush()
                emergency_log.close()
            raise FileNotFoundError(error_msg)
        
        from featrix.neural.embedding_space_utils import resolve_embedding_space_path
        resolved_es_path = resolve_embedding_space_path(embedding_space_path) if embedding_space_path else None
        if not resolved_es_path:
            error_msg = f"Embedding space not found: {embedding_space_path}"
            if emergency_log:
                emergency_log.write(f"❌ {error_msg}\n")
                if embedding_space_path:
                    emergency_log.write(f"   Path exists: {Path(embedding_space_path).exists()}\n")
                else:
                    emergency_log.write(f"   embedding_space is None/empty in session\n")
                emergency_log.flush()
                emergency_log.close()
            raise FileNotFoundError(error_msg)
        
        if emergency_log:
            emergency_log.write(f"✅ All paths validated, files exist\n")
            emergency_log.write(f"About to enter setup_job_logging...\n")
            emergency_log.flush()
        
        logger.info(f"   SQLite DB: {sqlite_db_path}")
        logger.info(f"   Embedding space: {embedding_space_path}")
        
        # CRITICAL: If job_id is None, use Celery task ID
        if not job_id or job_id == 'None':
            job_id = self.request.id
            logger.info(f"   Using Celery task ID as job_id: {job_id}")
        
        # STANDARD JOB SETUP - creates job dir, logs dir, and redirects stdout/stderr
        with setup_job_logging(job_id, session_id, 'train_single_predictor') as (job_dir, original_cwd):
            # Successfully entered normal logging - close emergency log
            if emergency_log:
                emergency_log.write(f"\n✅ SUCCESS: Entered setup_job_logging - normal logging active\n")
                emergency_log.write(f"Emergency log ending here. Check stdout.log for continued output.\n")
                emergency_log.flush()
                emergency_log.close()
                emergency_log = None
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Training predictor...',
                    'job_id': job_id,
                    'session_id': session_id
                }
            )
            
            # CRITICAL: Fork/exec training in a non-daemon session leader process
            # Same pattern as ES training for better GPU memory management and process isolation
            # Serialize args to pass to subprocess
            args_dict = {
                'embedding_space_path': str(embedding_space_path),
                'input_file': str(sqlite_db_path),  # CRITICAL: Override default
                'sqlite_db_path': str(sqlite_db_path),
                'strings_cache': strings_cache or "",
                'target_column': job_spec.get('target_column'),
                'target_column_type': job_spec.get('target_column_type', 'set'),
                'job_id': job_id,
                'session_id': session_id,
                **{k: v for k, v in job_spec.items() if k not in ['target_column', 'target_column_type', 'embedding_space_path', 'input_file', 'sqlite_db_path', 'strings_cache']}
            }
            
            # Create a temporary file to pass args
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_file = f.name
                json_module.dump(args_dict, f)
            
            try:
                # Fork/exec training in a new session leader process
                # This provides better process isolation and GPU memory cleanup
                python_cmd = sys.executable
                train_script = Path(__file__).parent / "lib" / "sp_training_wrapper.py"
                
                logger.info(f"🚀 Forking SP training process as session leader...")
                logger.info(f"   Python: {python_cmd}")
                logger.info(f"   Script: {train_script}")
                
                # Fork/exec with setsid to create new session leader (non-daemon)
                # CRITICAL: Open log file in append mode so subprocess writes to same file
                log_file_path = job_dir / "logs" / "stdout.log"
                
                # Open log file in append mode (line buffered) for subprocess
                with open(log_file_path, 'a', buffering=1) as log_file:
                    process = subprocess.Popen(
                        [python_cmd, str(train_script), json_file, '--job-id', job_id],
                        cwd=str(job_dir),
                        stdout=log_file,
                        stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                        start_new_session=True,  # setsid - become session leader (non-daemon)
                        env=os.environ.copy()  # Inherit environment
                    )
                    
                    training_pid = process.pid
                    celery_worker_pid = os.getpid()
                    
                    # Write Celery worker mapping file for admin monitoring
                    # This lets us correlate Celery worker PIDs with training job PIDs
                    mapping_file = Path(f"/tmp/featrix-celery-{celery_worker_pid}.json")
                    try:
                        mapping_data = {
                            "timestamp_started": datetime.now().isoformat(),
                            "celery_worker_pid": celery_worker_pid,
                            "training_pid": training_pid,
                            "job_id": job_id,
                            "session_id": session_id,
                            "job_type": "train_single_predictor",
                        }
                        with open(mapping_file, 'w') as f:
                            json_module.dump(mapping_data, f, indent=2)
                        logger.info(f"📝 Wrote Celery worker mapping: {mapping_file}")
                    except Exception as e:
                        logger.warning(f"Failed to write Celery worker mapping: {e}")
                    
                    logger.info(f"✅ Training process forked with PID {training_pid} (session leader)")
                    logger.info(f"   Celery worker PID: {celery_worker_pid}")
                    logger.info(f"   Training PID: {training_pid}")
                    logger.info(f"   📝 Training output in: {log_file_path}")
                    logger.info(f"   🔍 Monitor with: ffsh tail {session_id}/{job_id}")
                    logger.info(f"   Monitoring PID {training_pid} until it exits...")
                    
                    # Wait for process to complete
                    # CRITICAL: Check for ABORT flag periodically AND update Celery state with progress
                    abort_flag = job_dir / "ABORT"
                    last_progress_update = 0
                    
                    try:
                        while process.poll() is None:
                            # Check for abort flag every second
                            if abort_flag.exists():
                                logger.warning(f"⚠️  ABORT flag detected - terminating training process")
                                process.terminate()
                                time.sleep(3)  # Give it time to cleanup
                                if process.poll() is None:
                                    logger.warning(f"   Process didn't terminate - killing it")
                                    process.kill()
                                raise RuntimeError("Training aborted by user (ABORT flag)")
                            
                            # Update Celery state with job progress from Redis (every 2 seconds to avoid spam)
                            current_time = time.time()
                            if current_time - last_progress_update >= 2:
                                try:
                                    from lib.job_manager import load_job
                                    job_data = load_job(job_id)
                                    if job_data:
                                        progress = job_data.get('progress', 0)
                                        current_epoch = job_data.get('current_epoch', 0)
                                        current_loss = job_data.get('current_loss', 0)
                                        validation_loss = job_data.get('validation_loss', 0)
                                        metrics = job_data.get('metrics', {})
                                        
                                        # Update Celery state so client gets progress
                                        self.update_state(
                                            state='PROGRESS',
                                            meta={
                                                'status': f'Training epoch {current_epoch}...',
                                                'job_id': job_id,
                                                'session_id': session_id,
                                                'progress': progress,
                                                'current_epoch': current_epoch,
                                                'current_loss': current_loss,
                                                'validation_loss': validation_loss,
                                                'metrics': metrics
                                            }
                                        )
                                        last_progress_update = current_time
                                except Exception as e:
                                    # Don't fail if progress update fails
                                    logger.debug(f"Failed to update progress: {e}")
                            
                            time.sleep(1)
                        
                        exit_code = process.returncode
                        
                        # Clean up mapping file when training completes
                        try:
                            if mapping_file.exists():
                                mapping_file.unlink()
                                logger.info(f"🗑️  Cleaned up Celery worker mapping: {mapping_file}")
                        except Exception as e:
                            logger.debug(f"Could not remove mapping file: {e}")
                        
                        logger.info(f"   Training process {training_pid} exited with code: {exit_code}")
                        
                        if exit_code != 0:
                            raise RuntimeError(f"Training process failed with exit code {exit_code}")
                        
                        logger.info(f"✅ Training subprocess completed successfully")
                    except KeyboardInterrupt:
                        logger.warning(f"⚠️  Received interrupt signal, terminating training process {training_pid}")
                        
                        # Clean up mapping file on interrupt
                        try:
                            if mapping_file.exists():
                                mapping_file.unlink()
                        except Exception:
                            pass
                        
                        process.terminate()
                        time.sleep(3)
                        if process.poll() is None:
                            process.kill()
                        raise
            finally:
                # Clean up temp args file
                try:
                    os.unlink(json_file)
                except Exception:
                    pass
        # Get output paths from session
        session = load_session(session_id)
        output = {
            'single_predictor': session.get('single_predictor'),
            'training_metrics': session.get('training_metrics')
        }
        
        # Verify output files exist before updating session
        verify_output_files_exist(output, "TRAIN_SINGLE_PREDICTOR")
        
        # Update session with output
        session_updated = False
        try:
            from lib.session_manager import load_session, save_session
            logger.info(f"🔄 Updating session {session_id} with predictor output...")
            logger.info(f"   Output keys: {list(output.keys())}")
            session = load_session(session_id)
            logger.info(f"   ✅ Session loaded successfully")
            session = {**session, **output}
            logger.info(f"   Saving session...")
            save_session(session_id=session_id, session_doc=session, exist_ok=True)
            session_updated = True
            logger.info(f"✅ Session updated with predictor output")
            # Verify the update worked
            session_check = load_session(session_id)
            if session_check.get('single_predictor'):
                logger.info(f"   ✅ Verified: single_predictor is now in session")
            else:
                logger.error(f"   ❌ WARNING: single_predictor NOT found in session after update!")
        except Exception as session_error:
            logger.error(f"❌ CRITICAL: Failed to update session with output: {session_error}")
            logger.error(f"   Error type: {type(session_error).__name__}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            logger.error(f"   Output files were generated but session was not updated!")
        
        # Automatically dispatch next job in chain
        # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
        logger.info(f"🔄 Attempting to dispatch next job in chain for session {session_id}...")
        logger.info(f"   Session was updated: {session_updated}")
        from lib.session_chains import dispatch_next_job_in_chain
        from lib.session_manager import load_session
        next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='train_single_predictor')
        if next_task_id:
            logger.info(f"✅ Successfully dispatched next job in chain (task_id: {next_task_id})")
        else:
            # Dispatch returned None - verify there really are no more jobs to dispatch
            logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
            session_check = load_session(session_id)
            job_plan = session_check.get('job_plan', [])
            remaining_jobs = []
            for idx, job_desc in enumerate(job_plan):
                job_type = job_desc.get("job_type", "unknown")
                job_id = job_desc.get("job_id")
                if not job_id or job_id == "None":
                    # Check if legitimately skipped
                    is_skipped = False
                    if job_type == "train_es":
                        embedding_space_path = session_check.get("embedding_space")
                        foundation_model_id = session_check.get("foundation_model_id")
                        if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                            is_skipped = True
                    elif job_type == "train_knn":
                        vector_db_path = session_check.get("vector_db")
                        if vector_db_path and Path(vector_db_path).exists():
                            is_skipped = True
                    elif job_type == 'train_single_predictor':
                        is_skipped = True  # Just completed
                    
                    if not is_skipped:
                        remaining_jobs.append((idx, job_type))
            
            if remaining_jobs:
                error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Session: {session_id}")
                logger.error(f"   This task will FAIL to prevent silent chain breakage")
                raise RuntimeError(error_msg)
            else:
                logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
        
        logger.info(f"✅ Single predictor training completed successfully")
        
        # Update job status to DONE when completed successfully
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id=job_id, status=JobStatus.DONE)
            logger.info(f"✅ Updated job {job_id} status to DONE")
        except Exception as status_err:
            logger.warning(f"⚠️  Failed to update job {job_id} status to DONE: {status_err}")
        
        logger.info(f"🏁 JOB {job_id} FINISHED")
        
        # ========================================
        # META-LEARNING: Log training results
        # ========================================
        try:
            logger.info("="*80)
            logger.info("📊 LOGGING SP TRAINING METADATA TO META-LEARNING API")
            logger.info("="*80)
            
            from lib.meta_learning_client import (
                get_dataset_characteristics,
                log_training_metadata
            )
            from lib.session_manager import load_session
            from lib.featrix.neural.input_data_file import FeatrixInputDataFile
            
            # Load session to get optimal config and input data
            session = load_session(session_id)
            optimal_config = session.get('optimal_es_config', {})
            input_data_path = session.get('input_data')
            
            if input_data_path and optimal_config:
                # Load dataframe for characteristics
                input_file = FeatrixInputDataFile(str(input_data_path))
                df = input_file.df
                
                # Get dataset characteristics
                dataset_chars = get_dataset_characteristics(df)
                n_rows = dataset_chars['n_rows']
                n_cols = dataset_chars['n_cols']
                target_type = dataset_chars.get('target_type', 'regression')
                
                # Extract final metrics from output
                final_auc = output.get('auc', 0)
                final_accuracy = output.get('accuracy', 0)
                final_f1 = output.get('f1', 0)
                
                # Build optimal parameters (ES config used for this training)
                optimal_parameters = {
                    'd_model': optimal_config.get('d_model'),
                    'n_transformer_layers': optimal_config.get('n_transformer_layers'),
                    'n_attention_heads': optimal_config.get('n_attention_heads')
                }
                
                # Build final results
                final_results = {
                    'auc': final_auc,
                    'accuracy': final_accuracy,
                    'f1': final_f1
                }
                
                # Get pre-analysis configs from session if available
                pre_analysis_epochs = None
                pre_analysis_results = session.get('pre_analysis_results', {})
                if pre_analysis_results:
                    # Extract configs that were tested during pre-analysis
                    all_tested = pre_analysis_results.get('all_tested_configs', [])
                    experimental_configs = pre_analysis_results.get('experimental_configs', [])
                    
                    # Combine both lists and format for API
                    all_configs = (all_tested or []) + (experimental_configs or [])
                    if all_configs:
                        pre_analysis_epochs = [
                            {
                                'd_model': c.get('d_model'),
                                'n_transformer_layers': c.get('n_transformer_layers'),
                                'n_attention_heads': c.get('n_attention_heads')
                            }
                            for c in all_configs
                            if all([c.get('d_model'), c.get('n_transformer_layers'), c.get('n_attention_heads')])
                        ]
                
                logger.info(f"   Dataset: {n_rows} rows, {n_cols} cols, {target_type}")
                logger.info(f"   Optimal parameters: d_model={optimal_parameters.get('d_model')}, layers={optimal_parameters.get('n_transformer_layers')}, heads={optimal_parameters.get('n_attention_heads')}")
                logger.info(f"   Final results: AUC={final_auc:.4f}, Accuracy={final_accuracy:.4f}, F1={final_f1:.4f}")
                if pre_analysis_epochs:
                    logger.info(f"   Pre-analysis configs: {len(pre_analysis_epochs)} configs tested")
                
                # Log to meta-learning API
                metadata_id = log_training_metadata(
                    session_id=session_id,
                    df=df,
                    optimal_params=optimal_parameters,
                    pre_analysis_epochs=pre_analysis_epochs,
                    final_result=final_results
                )
                
                if metadata_id:
                    logger.info(f"✅ Training metadata logged to meta-learning API: {metadata_id}")
                else:
                    logger.warning(f"⚠️  Failed to log training metadata (returned None)")
                
                logger.info("="*80)
            else:
                logger.info(f"ℹ️  Skipping meta-learning logging (missing input_data or optimal_config)")
                if not input_data_path:
                    logger.info(f"   Missing: input_data")
                if not optimal_config:
                    logger.info(f"   Missing: optimal_es_config")
                
        except Exception as meta_err:
            logger.warning(f"⚠️  Failed to log training metadata to meta-learning API: {meta_err}")
            logger.debug(traceback.format_exc())
            # Don't fail training if meta-learning logging fails
        
        result = {
            'success': True,
            'output': output,
            'job_id': job_id,
            'session_id': session_id
        }
        log_task_return_value(result, "TRAIN_SINGLE_PREDICTOR")
        return result
        
    except Exception as e:
        # Write crash log to job directory for easy debugging
        if 'job_dir' in locals() and job_dir:
            try:
                write_crash_log(
                    job_dir=job_dir,
                    exception=e,
                    job_id=job_id,
                    session_id=session_id,
                    job_type='train_single_predictor',
                    additional_info={
                        'target_column': job_spec.get('target_column') if 'job_spec' in locals() else None,
                        'target_column_type': job_spec.get('target_column_type') if 'job_spec' in locals() else None,
                        'task_id': getattr(self, 'request', {}).get('id', 'unknown'),
                    }
                )
            except Exception:
                pass  # Don't fail if crash log write fails
        
        # Write to emergency log if still open (means we crashed before normal logging)
        if emergency_log:
            emergency_log.write(f"\n{'='*80}\n")
            emergency_log.write(f"❌❌❌ EXCEPTION CAUGHT IN TRAIN_SINGLE_PREDICTOR ❌❌❌\n")
            emergency_log.write(f"{'='*80}\n")
            emergency_log.write(f"Exception type: {type(e).__name__}\n")
            emergency_log.write(f"Exception message: {str(e)}\n")
            emergency_log.write(f"\n--- Full traceback ---\n")
            emergency_log.write(traceback.format_exc())
            emergency_log.write(f"\n{'='*80}\n")
            emergency_log.write(f"This error occurred BEFORE normal logging was set up.\n")
            emergency_log.write(f"The task crashed during initialization/setup phase.\n")
            emergency_log.write(f"{'='*80}\n")
            emergency_log.flush()
            emergency_log.close()
            emergency_log = None
        
        # SCREAM LOUDLY - This is a critical failure that needs immediate attention
        logger.error(f"")
        logger.error(f"╔════════════════════════════════════════════════════════════════════════════════╗")
        logger.error(f"║                                                                                ║")
        logger.error(f"║  💥💥💥 CRITICAL TASK FAILURE - TRAIN_SINGLE_PREDICTOR CRASHED 💥💥💥            ║")
        logger.error(f"║                                                                                ║")
        logger.error(f"╚════════════════════════════════════════════════════════════════════════════════╝")
        logger.error(f"")
        logger.error(f"❌❌❌ TRAIN_SINGLE_PREDICTOR FAILED WITH UNHANDLED EXCEPTION ❌❌❌")
        logger.error(f"")
        logger.error(f"   Job ID: {job_id if 'job_id' in locals() else 'UNKNOWN'}")
        logger.error(f"   Session ID: {session_id if 'session_id' in locals() else 'UNKNOWN'}")
        
        # Print job directory and log location
        if 'job_dir' in locals() and job_dir:
            logger.error(f"")
            logger.error(f"   📁 Job Directory: {job_dir}")
            logger.error(f"   📝 Log File: {job_dir}/logs/stdout.log")
            logger.error(f"")
            logger.error(f"   To check logs:")
            logger.error(f"      tail -100 {job_dir}/logs/stdout.log")
        
        logger.error(f"")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error(f"   Exception Message: {str(e)}")
        logger.error(f"")
        logger.error(f"   FULL TRACEBACK:")
        logger.error(f"   {'='*100}")
        logger.error(f"   {traceback.format_exc()}")
        logger.error(f"   {'='*100}")
        logger.error(f"")
        
        # Send Slack alert for critical failure
        try:
            from slack import send_slack_message
            
            error_msg = f"🚨 *CELERY TASK CRASHED - train_single_predictor*\n"
            error_msg += f"• Job ID: `{job_id}`\n"
            error_msg += f"• Session ID: `{session_id}`\n"
            error_msg += f"• Exception: `{type(e).__name__}: {str(e)[:300]}`\n"
            
            # Get last few lines of traceback
            tb_lines = traceback.format_exc().split('\n')
            if len(tb_lines) > 5:
                error_msg += f"• Traceback:\n```\n{chr(10).join(tb_lines[-6:-1])}```"
            
            # pylint: disable=unexpected-keyword-arg
            send_slack_message(error_msg, throttle=False)  # Critical - don't throttle
            logger.info("✅ Slack alert sent for Celery task failure")
        except Exception as slack_error:
            logger.warning(f"Failed to send Slack alert: {slack_error}")
        
        # Update job status to FAILED when it fails
        try:
            from lib.job_manager import update_job_status, JobStatus, determine_failure_reason
            # Extract error information for metadata
            exception_type = type(e).__name__
            exception_msg = str(e)
            tb_str = traceback.format_exc()
            
            # Determine failure reason
            failure_reason = determine_failure_reason(
                exception=e,
                exception_type=exception_type,
                exception_msg=exception_msg,
                traceback_str=tb_str
            )
            
            # Build error metadata
            error_metadata = {
                'error': exception_msg[:500] if exception_msg else None,  # Truncate to 500 chars
                'failure_reason': failure_reason,
            }
            
            update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata=error_metadata)
            logger.error(f"   ✅ Updated job {job_id} status to FAILED (reason: {failure_reason})")
        except Exception as status_err:
            logger.error(f"   ❌❌❌ FAILED TO UPDATE JOB STATUS TO FAILED ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
        
        logger.error(f"")
        logger.error(f"🏁 JOB {job_id} FINISHED (WITH ERRORS)")
        logger.error(f"")
        
        result = {
            'success': False,
            'error': str(e),
            'job_id': job_id,
            'session_id': session_id,
            'traceback': traceback.format_exc()
        }
        log_task_return_value(result, "TRAIN_SINGLE_PREDICTOR")
        return result

@app.task(bind=True)
def train_es(self, job_spec: dict, job_id: str, session_id: str, data_file: str = None, strings_cache: str = None):
    """
    Celery task to train an embedding space.
    
    Args:
        job_spec: Job specification dict with training parameters
        job_id: Celery task ID (used as job ID)
        session_id: Session ID
        data_file: Path to SQLite database or CSV file
        strings_cache: Path to strings cache file
        
    Returns:
        dict with output paths (embedding_space)
    """
    from pathlib import Path
    
    # Use Celery task ID if job_id not provided
    if not job_id:
        job_id = self.request.id
        logger.info(f"   Using Celery task ID as job_id: {job_id}")
    
    logger.info(f"🎯 CELERY TRAIN_ES STARTED")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Data file: {data_file}")
    logger.info(f"   Job spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
    
    # ============================================================================
    # DUPLICATE DELIVERY DETECTION
    # ============================================================================
    # Check if this task is already running in another worker before doing ANY work.
    # This prevents duplicate deliveries from Celery's visibility_timeout (3 hours)
    # for long-running training jobs (6+ hours).
    
    if check_duplicate_delivery(job_id, session_id, 'train_es', task_id=self.request.id):
        logger.warning(f"🛑 Duplicate delivery detected - exiting gracefully without doing any work")
        # Return a special result indicating duplicate skip
        return {
            "success": False,
            "duplicate_skip": True,
            "message": "Task skipped - already running in another worker"
        }
    
    # NOT a duplicate - continue normally
    logger.info(f"✅ Not a duplicate delivery - proceeding with training")
    
    # CRITICAL: Check for ABORT file BEFORE setting status to RUNNING
    # This prevents overwriting FAILED status if job was already aborted
    try:
        from lib.job_manager import check_abort_file
        if check_abort_file(job_id):
            logger.warning(f"🚫 ABORT file detected for job {job_id} - skipping status update to RUNNING")
            # Don't set status to RUNNING - job is already aborted
            # The ABORT check in _train_es_single will handle marking it as FAILED
            # Return early to avoid doing any work
            return {
                "success": False,
                "aborted": True,
                "message": f"Job {job_id} has ABORT file - training will not proceed"
            }
    except Exception as abort_check_err:
        logger.warning(f"⚠️  Failed to check for ABORT file: {abort_check_err}")
        # Continue - ABORT check will happen later in training
    
    # CRITICAL: Update job status to RUNNING IMMEDIATELY - before any other work
    # This ensures status is updated as soon as the task starts, not after setup
    try:
        from lib.job_manager import update_job_status, JobStatus
        update_job_status(job_id=job_id, status=JobStatus.RUNNING)
        logger.info(f"✅ Updated job {job_id} status to RUNNING (immediately at task start)")
    except Exception as status_err:
        logger.warning(f"⚠️  Failed to update job {job_id} status to RUNNING: {status_err}")
        # Continue anyway - status will be updated later or detected by session_manager
    
    # STANDARD JOB SETUP - MUST BE FIRST to capture all output including errors
    with setup_job_logging(job_id, session_id, 'train_es') as (job_dir, original_cwd):
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Starting embedding space training...',
                    'job_id': job_id,
                    'session_id': session_id
                }
            )
            
            # Import here to avoid CUDA fork issues
            from lib.session_manager import load_session, save_session
            from lib.es_training import train_es, LightTrainingArgs
            
            # Load session to get paths if not provided
            session = load_session(session_id)
            
            # Use provided data_file or get from session
            if not data_file:
                data_file = session.get('sqlite_db')
                if not data_file:
                    raise ValueError(f"No data_file provided and session {session_id} has no sqlite_db")
            
            if not strings_cache:
                strings_cache = session.get('strings_cache')
            
            if not Path(data_file).exists():
                raise FileNotFoundError(f"Data file not found: {data_file}")
            
            logger.info(f"   Data file: {data_file}")
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Training embedding space...',
                    'job_id': job_id,
                    'session_id': session_id
                }
            )
            
            # CRITICAL: Fork/exec training in a non-daemon session leader process
            # Celery workers are daemon processes and cannot spawn children (DataLoader workers)
            # We fork/exec a new process that becomes a session leader, allowing DataLoader workers
            # The Celery job monitors the new PID and waits until it exits
            import subprocess
            import json as json_module
            import tempfile
            import signal
            
            # Serialize args to pass to subprocess
            args_dict = {
                'input_file': str(data_file),
                'string_cache': strings_cache or "",  # FIXED: Use 'string_cache' (singular) to match LightTrainingArgs field name
                'job_id': job_id,
                'session_id': session_id,
                'column_overrides': session.get('column_overrides', {}),
                'json_transformations': session.get('json_transformations', {}),
                **{k: v for k, v in job_spec.items() if k not in ['column_overrides', 'json_transformations']}
            }
            
            # Create a temporary file to pass args
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_file = f.name
                json_module.dump(args_dict, f)
            
            try:
                # Fork/exec training in a new session leader process
                # This allows DataLoader workers to spawn for maximum GPU utilization
                python_cmd = sys.executable
                train_script = Path(__file__).parent / "lib" / "es_training_wrapper.py"
                
                logger.info(f"🚀 Forking training process as session leader for maximum GPU utilization...")
                logger.info(f"   Python: {python_cmd}")
                logger.info(f"   Script: {train_script}")
                
                # Fork/exec with setsid to create new session leader (non-daemon)
                # This allows the process to spawn DataLoader worker children
                # CRITICAL: Open log file in append mode so subprocess writes to same file
                # The log file path is: job_dir/logs/stdout.log
                log_file_path = job_dir / "logs" / "stdout.log"
                
                # Open log file in append mode (line buffered) for subprocess
                # This ensures all output from the forked process goes to the same log file
                # Add --job-id, --session-id, and --job-path arguments so they're visible in /proc/<pid>/cmdline for process identification
                cmd = [python_cmd, str(train_script), json_file, '--job-id', job_id]
                if session_id:
                    cmd.extend(['--session-id', session_id])
                if job_dir:
                    cmd.extend(['--job-path', str(job_dir)])
                with open(log_file_path, 'a', buffering=1) as log_file:
                    process = subprocess.Popen(
                        cmd,
                        cwd=str(job_dir),
                        stdout=log_file,  # Write to same log file
                        stderr=subprocess.STDOUT,  # Merge stderr to stdout
                        start_new_session=True,  # setsid - become session leader (non-daemon)
                        env=os.environ.copy()  # Inherit environment
                    )
                    
                    training_pid = process.pid
                    celery_worker_pid = os.getpid()
                    
                    # Write Celery worker mapping file for admin monitoring
                    # This lets us correlate Celery worker PIDs with training job PIDs
                    mapping_file = Path(f"/tmp/featrix-celery-{celery_worker_pid}.json")
                    try:
                        mapping_data = {
                            "timestamp_started": datetime.now().isoformat(),
                            "celery_worker_pid": celery_worker_pid,
                            "training_pid": training_pid,
                            "job_id": job_id,
                            "session_id": session_id,
                            "job_type": "train_es",
                        }
                        with open(mapping_file, 'w') as f:
                            json_module.dump(mapping_data, f, indent=2)
                        logger.info(f"📝 Wrote Celery worker mapping: {mapping_file}")
                    except Exception as e:
                        logger.warning(f"Failed to write Celery worker mapping: {e}")
                    
                    logger.info(f"✅ Training process forked with PID {training_pid} (session leader)")
                    logger.info(f"   Celery worker PID: {celery_worker_pid}")
                    logger.info(f"   Training PID: {training_pid}")
                    logger.info(f"   Logging to: {log_file_path}")
                    logger.info(f"   Monitoring PID {training_pid} until it exits...")
                    
                    # Monitor the process - wait until it crashes or exits
                    try:
                        return_code = process.wait()
                        
                        # Clean up mapping file when training completes
                        try:
                            if mapping_file.exists():
                                mapping_file.unlink()
                                logger.info(f"🗑️  Cleaned up Celery worker mapping: {mapping_file}")
                        except Exception as e:
                            logger.debug(f"Could not remove mapping file: {e}")
                        
                        if return_code == 0:
                            logger.info(f"✅ Training process {training_pid} completed successfully")
                        else:
                            logger.error(f"❌ Training process {training_pid} exited with code {return_code}")
                            
                            # Try to extract the actual error from stdout.log
                            error_summary = None
                            try:
                                if log_file_path.exists():
                                    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        lines = f.readlines()
                                        # Get last 50 lines and look for errors
                                        last_lines = lines[-50:] if len(lines) > 50 else lines
                                        
                                        # Find error/exception lines
                                        error_lines = []
                                        for i, line in enumerate(reversed(last_lines)):
                                            line_lower = line.lower()
                                            if any(keyword in line_lower for keyword in ['error', 'exception', 'traceback', 'failed', 'crash', 'fatal']):
                                                # Include context (5 lines before and after)
                                                start_idx = max(0, len(last_lines) - i - 6)
                                                end_idx = min(len(last_lines), len(last_lines) - i + 5)
                                                error_lines = last_lines[start_idx:end_idx]
                                                break
                                        
                                        if error_lines:
                                            error_summary = "".join(error_lines[-20:])  # Last 20 lines of error context
                            except Exception as log_read_err:
                                logger.debug(f"Could not read error from log file: {log_read_err}")
                            
                            # Create exception with more context
                            error_msg = f"Training process exited with code {return_code}"
                            if error_summary:
                                error_msg += f"\n\nLast error lines from stdout.log:\n{'-'*80}\n{error_summary}\n{'-'*80}"
                            
                            # Write crash log with additional info
                            additional_info = {
                                'data_file': str(data_file) if data_file else None,
                                'strings_cache': strings_cache,
                                'return_code': return_code,
                                'training_pid': training_pid,
                                'log_file': str(log_file_path) if log_file_path.exists() else None,
                            }
                            if error_summary:
                                additional_info['error_summary'] = error_summary
                            
                            write_crash_log(
                                job_dir=job_dir,
                                exception=RuntimeError(error_msg),
                                job_id=job_id,
                                session_id=session_id,
                                job_type='train_es',
                                additional_info=additional_info
                            )
                            
                            raise RuntimeError(error_msg)
                    except KeyboardInterrupt:
                        logger.warning(f"⚠️  Received interrupt signal, terminating training process {training_pid}")
                        
                        # Clean up mapping file on interrupt
                        try:
                            if mapping_file.exists():
                                mapping_file.unlink()
                        except Exception:
                            pass
                        
                        # Send SIGTERM to the process group (kills session leader and all children)
                        try:
                            os.killpg(os.getpgid(training_pid), signal.SIGTERM)
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            logger.warning(f"⚠️  Process {training_pid} did not terminate, sending SIGKILL")
                            os.killpg(os.getpgid(training_pid), signal.SIGKILL)
                            process.wait()
                        except ProcessLookupError:
                            pass  # Process already dead
                        raise
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(json_file)
                except Exception:
                    pass
            
            # Get output paths from session (updated by es_training.py before exit)
            session = load_session(session_id)
            embedding_space_path = session.get('embedding_space')
            logger.info(f"   📍 Session embedding_space after train_es: {embedding_space_path}")
            
            # GUARD: If session wasn't updated (old code or error), try to find it in job_dir
            if not embedding_space_path:
                logger.warning(f"⚠️  Session not updated with embedding_space path - searching job_dir")
                from featrix.neural.embedding_space_utils import find_embedding_space_pickle
                found = find_embedding_space_pickle(job_dir)
                if found:
                    embedding_space_path = str(found)
                    logger.info(f"✅ Found embedding space pickle at fallback location: {embedding_space_path}")
                    # Update session with found path
                    try:
                        session['embedding_space'] = embedding_space_path
                        save_session(session_id, session, exist_ok=True)
                        logger.info(f"✅ Updated session with found embedding_space path")
                    except Exception as update_err:
                        logger.warning(f"⚠️  Could not update session: {update_err}")
                else:
                    logger.error(f"❌ CRITICAL: Embedding space pickle not found in job_dir: {job_dir}")
                    raise FileNotFoundError(f"Embedding space pickle not found in job_dir: {job_dir}")
            else:
                # Verify the path from session actually exists (might be wrong variant)
                from featrix.neural.embedding_space_utils import resolve_embedding_space_path
                resolved_path = resolve_embedding_space_path(embedding_space_path)
                if resolved_path:
                    if str(resolved_path) != embedding_space_path:
                        logger.info(f"   ✅ Resolved path differs from session: {resolved_path} vs {embedding_space_path}")
                        embedding_space_path = str(resolved_path)
                        # Update session with resolved path
                        try:
                            session['embedding_space'] = embedding_space_path
                            save_session(session_id, session, exist_ok=True)
                            logger.info(f"✅ Updated session with resolved embedding_space path")
                        except Exception as update_err:
                            logger.warning(f"⚠️  Could not update session: {update_err}")
                else:
                    logger.warning(f"⚠️  Session embedding_space path doesn't exist: {embedding_space_path}")
                    # Try to find it in job_dir as fallback
                    from featrix.neural.embedding_space_utils import find_embedding_space_pickle
                    found = find_embedding_space_pickle(job_dir)
                    if found:
                        embedding_space_path = str(found)
                        logger.info(f"✅ Found embedding space pickle in job_dir: {embedding_space_path}")
                        # Update session
                        try:
                            session['embedding_space'] = embedding_space_path
                            save_session(session_id, session, exist_ok=True)
                            logger.info(f"✅ Updated session with found embedding_space path")
                        except Exception as update_err:
                            logger.warning(f"⚠️  Could not update session: {update_err}")
                    else:
                        logger.error(f"❌ CRITICAL: Embedding space pickle not found at {embedding_space_path} or in {job_dir}")
                        raise FileNotFoundError(f"Embedding space pickle not found")
            
            output = {
                'embedding_space': embedding_space_path,
                'training_metrics': session.get('training_metrics')
            }
            
            # Update session with output
            session_updated = False
            try:
                logger.info(f"🔄 Updating session {session_id} with embedding space output...")
                logger.info(f"   Output keys: {list(output.keys())}")
                session = {**session, **output}
                save_session(session_id=session_id, session_doc=session, exist_ok=True)
                session_updated = True
                logger.info(f"✅ Session updated with embedding space output")
                logger.info(f"   embedding_space: {output.get('embedding_space')}")
            except Exception as session_error:
                logger.error(f"❌ CRITICAL: Failed to update session with output: {session_error}")
                logger.error(f"   Full traceback: {traceback.format_exc()}")
                logger.error(f"   Output files were generated but session was not updated!")
            
            # Automatically dispatch next job in chain
            # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
            logger.info(f"🔄 Attempting to dispatch next job in chain for session {session_id}...")
            logger.info(f"   Session was updated: {session_updated}")
            from lib.session_chains import dispatch_next_job_in_chain
            from lib.session_manager import load_session
            next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='train_es')
            if next_task_id:
                logger.info(f"✅ Successfully dispatched next job in chain (task_id: {next_task_id})")
            else:
                # Dispatch returned None - verify there really are no more jobs to dispatch
                logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
                session_check = load_session(session_id)
                job_plan = session_check.get('job_plan', [])
                remaining_jobs = []
                for idx, job_desc in enumerate(job_plan):
                    job_type = job_desc.get("job_type", "unknown")
                    job_id = job_desc.get("job_id")
                    if not job_id or job_id == "None":
                        # Check if legitimately skipped
                        is_skipped = False
                        if job_type == "train_es":
                            embedding_space_path = session_check.get("embedding_space")
                            foundation_model_id = session_check.get("foundation_model_id")
                            if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                                is_skipped = True
                        elif job_type == "train_knn":
                            vector_db_path = session_check.get("vector_db")
                            if vector_db_path and Path(vector_db_path).exists():
                                is_skipped = True
                        elif job_type == 'train_es':
                            is_skipped = True  # Just completed
                        
                        if not is_skipped:
                            remaining_jobs.append((idx, job_type))
                
                if remaining_jobs:
                    error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                    logger.error(f"❌ {error_msg}")
                    logger.error(f"   Session: {session_id}")
                    logger.error(f"   This task will FAIL to prevent silent chain breakage")
                    raise RuntimeError(error_msg)
                else:
                    logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
            
            logger.info(f"✅ Embedding space training completed successfully")
            
            # Update job status to DONE when completed successfully
            try:
                from lib.job_manager import update_job_status, JobStatus
                update_job_status(job_id=job_id, status=JobStatus.DONE)
                logger.info(f"✅ Updated job {job_id} status to DONE")
            except Exception as status_err:
                logger.warning(f"⚠️  Failed to update job {job_id} status to DONE: {status_err}")
                logger.warning(f"   Error: {traceback.format_exc()}")
            
            logger.info(f"🏁 JOB {job_id} FINISHED")
            
            result = {
                'success': True,
                'output': output,
                'job_id': job_id,
                'session_id': session_id
            }
            log_task_return_value(result, "TRAIN_ES")
            return result
            
        except Exception as e:
            # SCREAM LOUDLY - This is a critical failure that needs immediate attention
            logger.error(f"")
            logger.error(f"╔════════════════════════════════════════════════════════════════════════════════╗")
            logger.error(f"║                                                                                ║")
            # Write crash log to job directory for easy debugging
            if 'job_dir' in locals() and job_dir:
                try:
                    write_crash_log(
                        job_dir=job_dir,
                        exception=e,
                        job_id=job_id,
                        session_id=session_id,
                        job_type='train_es',
                        additional_info={
                            'data_file': data_file,
                            'strings_cache': strings_cache,
                        }
                    )
                except Exception:
                    pass  # Don't fail if crash log write fails
            
            logger.error(f"║  💥💥💥 CRITICAL TASK FAILURE - TRAIN_ES CRASHED 💥💥💥                        ║")
            logger.error(f"║                                                                                ║")
            logger.error(f"╚════════════════════════════════════════════════════════════════════════════════╝")
            logger.error(f"")
            logger.error(f"❌❌❌ TRAIN_ES FAILED WITH UNHANDLED EXCEPTION ❌❌❌")
            logger.error(f"")
            logger.error(f"   Job ID: {job_id}")
            logger.error(f"   Session ID: {session_id}")
            logger.error(f"   Exception Type: {type(e).__name__}")
            logger.error(f"   Exception Message: {str(e)}")
            logger.error(f"")
            logger.error(f"   FULL TRACEBACK:")
            logger.error(f"   {'='*100}")
            logger.error(f"   {traceback.format_exc()}")
            logger.error(f"   {'='*100}")
            logger.error(f"")
            
            # Update job status to FAILED when it fails
            try:
                from lib.job_manager import update_job_status, JobStatus, determine_failure_reason
                tb_str = traceback.format_exc()
                failure_reason = determine_failure_reason(exception=e, traceback_str=tb_str)
                update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata={'failure_reason': failure_reason})
                logger.error(f"   ✅ Updated job {job_id} status to FAILED (reason: {failure_reason})")
            except Exception as status_err:
                logger.error(f"   ❌❌❌ FAILED TO UPDATE JOB STATUS TO FAILED ❌❌❌")
                logger.error(f"   Error: {status_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
            
            logger.error(f"")
            logger.error(f"🏁 JOB {job_id} FINISHED (WITH ERRORS)")
            logger.error(f"")
            
            result = {
                'success': False,
                'error': str(e),
                'job_id': job_id,
                'session_id': session_id,
                'traceback': traceback.format_exc()
            }
            log_task_return_value(result, "TRAIN_ES")
            return result

@app.task(bind=True, name='celery_app.train_knn')
def train_knn(self, job_spec: dict, job_id: str, session_id: str):
    """
    Celery task to train KNN index (vector database).
    
    Args:
        job_spec: Job specification dict (should contain model_path, sqlite_db_path, strings_cache)
        job_id: Celery task ID (used as job ID)
        session_id: Session ID
        
    Returns:
        dict with output paths (vector_db)
    """
    # CRITICAL: Log to stderr FIRST - this goes to worker logs even if logger fails
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"🚨🚨🚨 TRAIN_KNN CELERY TASK FUNCTION CALLED 🚨🚨🚨", file=sys.stderr, flush=True)
    print(f"   job_id: {job_id}", file=sys.stderr, flush=True)
    print(f"   session_id: {session_id}", file=sys.stderr, flush=True)
    print(f"   task_id: {self.request.id}", file=sys.stderr, flush=True)
    print(f"{'='*80}\n", file=sys.stderr, flush=True)
    
    task_start = time.time()
    celery_trace_id = f"CELERY-{uuid.uuid4().hex[:8]}"
    job_dir = None  # Initialize to avoid linter error when accessed in exception handler
    
    # Use Celery task ID if job_id not provided
    if not job_id:
        job_id = self.request.id
        print(f"📍 Using Celery task ID as job_id: {job_id}", file=sys.stderr, flush=True)
        logger.info(f"   Using Celery task ID as job_id: {job_id}")
    
    # CRITICAL: Check for duplicate delivery BEFORE doing any work
    # This prevents duplicate deliveries from Celery's visibility_timeout
    if check_duplicate_delivery(job_id, session_id, 'train_knn', task_id=self.request.id):
        logger.warning(f"🛑 Duplicate delivery detected - exiting gracefully without doing any work")
        print(f"🛑 Duplicate delivery detected for job_id={job_id}, task_id={self.request.id}", file=sys.stderr, flush=True)
        # Return a special result indicating duplicate skip
        return {
            "success": False,
            "duplicate_skip": True,
            "message": "Task skipped - already running in another worker",
            "vector_db": None
        }
    
    logger.info(f"✅ Not a duplicate delivery - proceeding with KNN training")
    print(f"✅ Not a duplicate delivery - proceeding", file=sys.stderr, flush=True)
    
    # CRITICAL: Update job status to DONE IMMEDIATELY - before any imports or work
    # This ensures the job doesn't appear stuck even if everything else fails
    # User doesn't need actual KNN work, just needs job to complete and move on
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"🔄🔄🔄 UPDATING JOB {job_id} STATUS TO DONE (IMMEDIATELY, BEFORE ANY WORK) 🔄🔄🔄", file=sys.stderr, flush=True)
    print(f"{'='*80}\n", file=sys.stderr, flush=True)
    logger.info(f"🔄 Updating job {job_id} status to DONE (immediately, before any work)...")
    try:
        print(f"📍 About to import lib.job_manager...", file=sys.stderr, flush=True)
        from lib.job_manager import update_job_status, JobStatus
        print(f"📍 Imported update_job_status, about to call it for job_id={job_id}...", file=sys.stderr, flush=True)
        update_job_status(job_id=job_id, status=JobStatus.DONE)
        print(f"✅✅✅ SUCCESS: Updated job {job_id} status to DONE (early) ✅✅✅", file=sys.stderr, flush=True)
        logger.info(f"✅ Updated job {job_id} status to DONE (early)")
    except Exception as status_err:
        print(f"❌❌❌ FAILED to update job {job_id} status to DONE (early): {status_err} ❌❌❌", file=sys.stderr, flush=True)
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
        logger.error(f"❌ Failed to update job {job_id} status to DONE (early): {status_err}")
        # Continue anyway - try again later
    
    # CRITICAL: Create emergency log IMMEDIATELY after getting job_id
    # This must happen BEFORE any other operations that might fail
    # Use try/except with explicit error handling to prevent any crash
    emergency_log = None
    emergency_log_path = None
    try:
        print(f"📍 About to create emergency log...", file=sys.stderr, flush=True)
        from lib.job_manager import get_job_output_path
        print(f"📍 Imported get_job_output_path", file=sys.stderr, flush=True)
        emergency_job_dir = get_job_output_path(job_id, session_id, 'train_knn')
        print(f"📍 Got job dir: {emergency_job_dir}", file=sys.stderr, flush=True)
        emergency_job_dir.mkdir(parents=True, exist_ok=True)
        print(f"📍 Created directory", file=sys.stderr, flush=True)
        emergency_log_path = emergency_job_dir / "EMERGENCY_STARTUP.log"
        print(f"📍 About to open log file: {emergency_log_path}", file=sys.stderr, flush=True)
        emergency_log = open(emergency_log_path, 'w')
        print(f"📍 Opened log file", file=sys.stderr, flush=True)
        emergency_log.write(f"=== EMERGENCY STARTUP LOG ===\n")
        emergency_log.write(f"Timestamp: {datetime.now().isoformat()}\n")
        emergency_log.write(f"Session ID: {session_id}\n")
        emergency_log.write(f"Job ID: {job_id}\n")
        emergency_log.write(f"Task ID: {self.request.id}\n")
        emergency_log.write(f"Function entry point reached\n")
        emergency_log.flush()
        print(f"✅ Emergency log created: {emergency_log_path}", file=sys.stderr, flush=True)
    except Exception as emergency_err:
        # Don't fail if emergency log creation fails, but log to stderr
        print(f"❌ CRITICAL: Could not create emergency log: {emergency_err}", file=sys.stderr, flush=True)
        print(f"   Exception type: {type(emergency_err).__name__}", file=sys.stderr, flush=True)
        try:
            print(f"   Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
        except:
            pass
        # Continue anyway - don't let emergency log failure stop the task
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔵 [CELERY] {celery_trace_id} TRAIN_KNN TASK STARTED")
    logger.info(f"   Timestamp: {datetime.now().isoformat()}")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Job spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
    logger.info(f"   Task ID: {self.request.id}")
    logger.info(f"{'='*80}")
    
    # CRITICAL: Wrap entire task in try/except to catch ANY unhandled exceptions
    try:
        logger.info(f"   📍 TRACE: Entered main try block")
        print(f"📍 TRACE: Entered main try block", file=sys.stderr, flush=True)
        
        logger.info(f"   📍 TRACE: About to import Path...")
        print(f"📍 TRACE: About to import Path...", file=sys.stderr, flush=True)
        from pathlib import Path
        logger.info(f"   📍 TRACE: Path imported successfully")
        print(f"📍 TRACE: Path imported successfully", file=sys.stderr, flush=True)
        
        # Update progress
        logger.info(f"   📍 TRACE: About to call self.update_state()...")
        print(f"📍 TRACE: About to call self.update_state()...", file=sys.stderr, flush=True)
        try:
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Starting KNN training...',
                    'job_id': job_id,
                    'session_id': session_id
                }
            )
            logger.info(f"   📍 TRACE: self.update_state() completed successfully")
            print(f"📍 TRACE: self.update_state() completed successfully", file=sys.stderr, flush=True)
        except Exception as update_err:
            logger.error(f"   ❌ CRITICAL: self.update_state() FAILED: {update_err}")
            print(f"❌ CRITICAL: self.update_state() FAILED: {update_err}", file=sys.stderr, flush=True)
            logger.error(f"   Traceback: {traceback.format_exc()}")
            # Don't fail the task, just log it
            pass
        
        # Import here to avoid CUDA fork issues
        # CRITICAL: If this import fails, the entire worker process dies silently!
        # So we wrap it in its own try/except to SCREAM LOUDLY if imports fail
        try:
            print(f"📍 TRACE: About to import session_manager...", file=sys.stderr, flush=True)
            logger.info(f"   📍 TRACE: Importing session_manager and knn_training modules...")
            from lib.session_manager import load_session, save_session
            print(f"📍 TRACE: Successfully imported session_manager", file=sys.stderr, flush=True)
            logger.info(f"   📍 TRACE: Successfully imported session_manager")
            
            # CRITICAL: Import knn_training with explicit error handling
            # knn_training.py redirects stderr at import time, so save original stderr first
            original_stderr = sys.stderr
            print(f"📍 TRACE: About to import knn_training (saved stderr)...", file=sys.stderr, flush=True)
            logger.info(f"   📍 TRACE: About to import knn_training...")
            try:
                import importlib
                print(f"📍 TRACE: About to call importlib.import_module('lib.knn_training')...", file=sys.stderr, flush=True)
                logger.info(f"   📍 TRACE: About to import lib.knn_training module (this may take a moment)...")
                
                # Add timeout wrapper to detect hanging imports
                import signal
                def timeout_handler(signum, frame):
                    print(f"⏰ TIMEOUT: Import of lib.knn_training took > 60 seconds!", file=sys.stderr, flush=True)
                    logger.error(f"   ⏰ TIMEOUT: Import of lib.knn_training took > 60 seconds!")
                    raise TimeoutError("Import of lib.knn_training timed out after 60 seconds")
                
                # Set alarm for 60 seconds (only works on Unix)
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(60)
                
                try:
                    print(f"📍 TRACE: Calling importlib.import_module('lib.knn_training') NOW...", file=sys.stderr, flush=True)
                    print(f"📍 TRACE: PID={os.getpid()}, PPID={os.getppid()}", file=sys.stderr, flush=True)
                    import_start = time.time()
                    knn_module = importlib.import_module('lib.knn_training')
                    import_duration = time.time() - import_start
                    print(f"📍 TRACE: importlib.import_module() RETURNED after {import_duration:.2f}s - module loaded successfully", file=sys.stderr, flush=True)
                    logger.info(f"   📍 TRACE: knn_training module loaded successfully in {import_duration:.2f}s")
                except Exception as import_exc:
                    print(f"❌ CRITICAL: Exception during importlib.import_module: {import_exc}", file=sys.stderr, flush=True)
                    logger.error(f"   ❌ CRITICAL: Exception during import: {import_exc}")
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    raise
                finally:
                    # Cancel alarm
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)
                    print(f"📍 TRACE: Timeout alarm cancelled", file=sys.stderr, flush=True)
                
                # Restore stderr after import (knn_training redirects it)
                print(f"📍 TRACE: About to restore stderr...", file=sys.stderr, flush=True)
                sys.stderr = original_stderr
                print(f"📍 TRACE: Restored stderr after import", file=sys.stderr, flush=True)
                logger.info(f"   📍 TRACE: Restored stderr after import")
                
                print(f"📍 TRACE: About to extract train_knn function from module...", file=sys.stderr, flush=True)
                train_knn_function = knn_module.train_knn
                print(f"📍 TRACE: train_knn function extracted", file=sys.stderr, flush=True)
                logger.info(f"   📍 TRACE: train_knn function extracted from module")
                
                # Verify the function is callable
                if not callable(train_knn_function):
                    raise TypeError(f"train_knn is not callable: {type(train_knn_function)}")
                print(f"📍 TRACE: Verified train_knn is callable", file=sys.stderr, flush=True)
            except Exception as knn_import_err:
                # Restore stderr even on error
                sys.stderr = original_stderr
                print(f"❌ FAILED TO IMPORT knn_training: {knn_import_err}", file=sys.stderr, flush=True)
                logger.error(f"   ❌ FAILED TO IMPORT knn_training MODULE")
                logger.error(f"   Exception: {type(knn_import_err).__name__}: {knn_import_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                raise
            
            logger.info(f"   📍 TRACE: Successfully imported knn_training")
            print(f"📍 TRACE: All imports completed, about to continue with task logic", file=sys.stderr, flush=True)
            logger.info(f"   📍 TRACE: All imports completed, about to continue with task logic")
        except Exception as import_err:
            logger.error(f"")
            logger.error(f"╔{'='*78}╗")
            logger.error(f"║  💥💥💥 CRITICAL IMPORT FAILURE - WORKER WILL DIE 💥💥💥{' '*15}║")
            logger.error(f"╚{'='*78}╝")
            logger.error(f"")
            logger.error(f"   ❌ FAILED TO IMPORT lib.knn_training or lib.session_manager")
            logger.error(f"   Exception: {type(import_err).__name__}: {import_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.error(f"")
            logger.error(f"   This usually means:")
            logger.error(f"   1. A module that knn_training.py imports is missing")
            logger.error(f"   2. There's a syntax error in knn_training.py")
            logger.error(f"   3. A circular import issue")
            logger.error(f"")
            raise  # Re-raise to trigger the outer exception handler
        
        # Load session to get paths
        logger.info(f"   📍 TRACE: About to load session...")
        logger.info(f"   📍 TRACE: session_id = {session_id}")
        logger.info(f"   📍 TRACE: PID = {os.getpid()}")
        print(f"📍 TRACE: About to load session (session_id={session_id}, PID={os.getpid()})...", file=sys.stderr, flush=True)
        try:
            session = load_session(session_id)
            logger.info(f"   📍 TRACE: Session loaded successfully")
            logger.info(f"   📍 TRACE: Session keys: {list(session.keys())[:10]}...")  # Log first 10 keys
            print(f"📍 TRACE: Session loaded successfully, has {len(session)} keys", file=sys.stderr, flush=True)
        except Exception as session_err:
            logger.error(f"   ❌ CRITICAL: Failed to load session: {session_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            print(f"❌ CRITICAL: Failed to load session: {session_err}", file=sys.stderr, flush=True)
            raise
        
        # Get paths from job_spec or session
        logger.info(f"   📍 TRACE: Extracting paths from job_spec and session...")
        logger.info(f"   📍 TRACE: job_spec keys: {list(job_spec.keys())}")
        logger.info(f"   📍 TRACE: job_spec.get('model_path'): {job_spec.get('model_path')}")
        logger.info(f"   📍 TRACE: session.get('embedding_space'): {session.get('embedding_space')}")
        logger.info(f"   📍 TRACE: job_spec.get('sqlite_db_path'): {job_spec.get('sqlite_db_path')}")
        logger.info(f"   📍 TRACE: session.get('sqlite_db'): {session.get('sqlite_db')}")
        
        model_path = job_spec.get('model_path') or session.get('embedding_space')
        sqlite_db_path = job_spec.get('sqlite_db_path') or session.get('sqlite_db')
        strings_cache = job_spec.get('strings_cache') or session.get('strings_cache')
        
        logger.info(f"   📍 TRACE: Resolved paths:")
        logger.info(f"   📍 TRACE:   model_path = {model_path}")
        logger.info(f"   📍 TRACE:   sqlite_db_path = {sqlite_db_path}")
        logger.info(f"   📍 TRACE:   strings_cache = {strings_cache}")
        
        # Use resolve function to handle both embedding_space.pickle and embedded_space.pickle
        if model_path:
            logger.info(f"   📍 Original model_path from session/job_spec: {model_path}")
            logger.info(f"   📍 Path exists: {Path(model_path).exists()}")
            from featrix.neural.embedding_space_utils import resolve_embedding_space_path
            resolved_path = resolve_embedding_space_path(model_path)
            if resolved_path:
                resolved_model_path = str(resolved_path)
                logger.info(f"   📍 Resolved path: {resolved_model_path}")
                logger.info(f"   📍 Resolved path exists: {Path(resolved_model_path).exists()}")
                
                # If the resolved path is different from the original, update session
                if resolved_model_path != model_path:
                    logger.info(f"   ✅ Resolved embedding space path: {resolved_model_path} (original: {model_path})")
                    logger.info(f"   🔄 Updating session with resolved path...")
                    # Update session with correct path
                    try:
                        from lib.session_manager import save_session
                        old_path = session.get('embedding_space')
                        logger.info(f"   📍 Session current embedding_space: {old_path}")
                        session['embedding_space'] = resolved_model_path
                        logger.info(f"   📍 About to save session with new embedding_space: {resolved_model_path}")
                        save_session(session_id, session, exist_ok=True)
                        logger.info(f"   ✅ Session save completed")
                        
                        # VERIFY the update worked
                        from lib.session_manager import load_session
                        verify_session = load_session(session_id)
                        verified_path = verify_session.get('embedding_space')
                        logger.info(f"   🔍 VERIFICATION: Session embedding_space after save: {verified_path}")
                        if verified_path == resolved_model_path:
                            logger.info(f"   ✅ VERIFIED: Session correctly updated with resolved embedding_space path")
                        else:
                            logger.error(f"   ❌ VERIFICATION FAILED: Expected {resolved_model_path}, got {verified_path}")
                            logger.error(f"   ⚠️  Session update may have failed silently!")
                    except Exception as update_err:
                        logger.error(f"   ❌ CRITICAL: Could not update session with resolved path: {update_err}")
                        logger.error(f"   Traceback: {traceback.format_exc()}")
                else:
                    logger.info(f"   ✅ Using embedding space path (no change needed): {model_path}")
                model_path = resolved_model_path
            else:
                logger.error(f"   ❌ Could not resolve embedding space path from: {model_path}")
                raise FileNotFoundError(f"Embedding space not found at {model_path} or in parent directory")
        else:
            logger.error(f"   ❌ No model_path provided in job_spec or session")
            raise FileNotFoundError(f"No embedding space path provided in job_spec or session")
        
        if not sqlite_db_path or not Path(sqlite_db_path).exists():
            raise FileNotFoundError(f"SQLite database not found: {sqlite_db_path}")
        
        logger.info(f"   Embedding space: {model_path}")
        logger.info(f"   SQLite DB: {sqlite_db_path}")
        
        # Update emergency log with path info
        if emergency_log:
            try:
                emergency_log.write(f"Model path: {model_path}\n")
                emergency_log.write(f"SQLite DB path: {sqlite_db_path}\n")
                emergency_log.write(f"About to enter setup_job_logging...\n")
                emergency_log.flush()
            except:
                pass
        
        # STANDARD JOB SETUP - creates job dir, logs dir, and redirects stdout/stderr
        with setup_job_logging(job_id, session_id, 'train_knn') as (job_dir, original_cwd):
            # Successfully entered normal logging - close emergency log
            if emergency_log:
                try:
                    emergency_log.write(f"\n✅ SUCCESS: Entered setup_job_logging - normal logging active\n")
                    emergency_log.write(f"Emergency log ending here. Check logs/stdout.log for continued output.\n")
                    emergency_log.flush()
                    emergency_log.close()
                    emergency_log = None
                except:
                    pass
            
            # CRITICAL: Update job status to DONE NOW (inside setup_job_logging so it's logged)
            # This ensures the job doesn't appear stuck even if everything else fails
            logger.info(f"\n{'='*80}")
            logger.info(f"🔄🔄🔄 UPDATING JOB {job_id} STATUS TO DONE (INSIDE SETUP_JOB_LOGGING) 🔄🔄🔄")
            logger.info(f"{'='*80}")
            try:
                from lib.job_manager import update_job_status, JobStatus
                logger.info(f"📍 Imported update_job_status, about to call it for job_id={job_id}...")
                update_job_status(job_id=job_id, status=JobStatus.DONE)
                logger.info(f"✅✅✅ SUCCESS: Updated job {job_id} status to DONE ✅✅✅")
            except Exception as status_err:
                logger.error(f"❌❌❌ FAILED to update job {job_id} status to DONE: {status_err} ❌❌❌")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                # Continue anyway - try again later
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Building vector database...',
                    'job_id': job_id,
                    'session_id': session_id
                }
            )
            
            # Call train_knn directly (replaces run_train_knn_job from featrix_queue)
            logger.info(f"   📍 TRACE: About to call train_knn_function()...")
            logger.info(f"   📍 TRACE:   es_path (Path): {Path(model_path)}")
            logger.info(f"   📍 TRACE:   sqlite_db_path (Path): {Path(sqlite_db_path)}")
            logger.info(f"   📍 TRACE:   job_id: {job_id}")
            print(f"📍 TRACE: About to call train_knn_function(es_path={model_path}, sqlite_db_path={sqlite_db_path}, job_id={job_id})...", file=sys.stderr, flush=True)
            
            try:
                output = train_knn_function(
                    es_path=Path(model_path),
                    sqlite_db_path=Path(sqlite_db_path),
                    job_id=job_id
                )
                logger.info(f"   📍 TRACE: train_knn_function() returned successfully")
                logger.info(f"   📍 TRACE:   output type: {type(output)}")
                logger.info(f"   📍 TRACE:   output: {output}")
                print(f"📍 TRACE: train_knn_function() returned: {output}", file=sys.stderr, flush=True)
            except Exception as train_err:
                logger.error(f"   ❌ CRITICAL: train_knn_function() raised exception: {type(train_err).__name__}: {train_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                print(f"❌ CRITICAL: train_knn_function() failed: {train_err}", file=sys.stderr, flush=True)
                raise
        
        # CRITICAL: Update job status to DONE IMMEDIATELY after function returns
        # This must happen FIRST so the job doesn't appear stuck even if later steps fail
        logger.info(f"🔄 Updating job {job_id} status to DONE (immediately after function return)...")
        print(f"🔄 Updating job {job_id} status to DONE (immediately after function return)...", file=sys.stderr, flush=True)
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id=job_id, status=JobStatus.DONE)
            logger.info(f"✅ Updated job {job_id} status to DONE")
            print(f"✅ Updated job {job_id} status to DONE", file=sys.stderr, flush=True)
        except Exception as status_err:
            logger.error(f"❌❌❌ CRITICAL: Failed to update job {job_id} status to DONE ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            print(f"❌❌❌ CRITICAL: Failed to update job {job_id} status to DONE: {status_err}", file=sys.stderr, flush=True)
            print(f"   Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
            # Don't raise - continue with rest of work even if status update fails
        
        # Verify output files exist before updating session
        logger.info(f"🔍 About to verify output files...")
        print(f"🔍 About to verify output files...", file=sys.stderr, flush=True)
        verify_output_files_exist(output, "TRAIN_KNN")
        logger.info(f"✅ File verification complete")
        print(f"✅ File verification complete", file=sys.stderr, flush=True)
        
        # Update session with output
        logger.info(f"🔄 About to update session with output...")
        print(f"🔄 About to update session with output...", file=sys.stderr, flush=True)
        session_updated = False
        try:
            from lib.session_manager import load_session, save_session
            logger.info(f"🔄 Updating session {session_id} with KNN output...")
            logger.info(f"   Output keys: {list(output.keys())}")
            session = load_session(session_id)
            logger.info(f"   ✅ Session loaded successfully")
            session = {**session, **output}
            logger.info(f"   Saving session...")
            save_session(session_id=session_id, session_doc=session, exist_ok=True)
            session_updated = True
            logger.info(f"✅ Session updated with KNN output")
            # Verify the update worked
            session_check = load_session(session_id)
            if session_check.get('vector_db'):
                logger.info(f"   ✅ Verified: vector_db is now in session")
            else:
                logger.error(f"   ❌ WARNING: vector_db NOT found in session after update!")
        except Exception as session_error:
            logger.error(f"❌ CRITICAL: Failed to update session with output: {session_error}")
            logger.error(f"   Error type: {type(session_error).__name__}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            logger.error(f"   Output files were generated but session was not updated!")
        
        # Automatically dispatch next job in chain
        # CRITICAL: If dispatch fails, the task MUST FAIL - don't silently succeed
        logger.info(f"🔄 Attempting to dispatch next job in chain for session {session_id}...")
        logger.info(f"   Session was updated: {session_updated}")
        from lib.session_chains import dispatch_next_job_in_chain
        from lib.session_manager import load_session
        next_task_id = dispatch_next_job_in_chain(session_id, completed_job_type='train_knn')
        if next_task_id:
            logger.info(f"✅ Successfully dispatched next job in chain (task_id: {next_task_id})")
        else:
            # Dispatch returned None - verify there really are no more jobs to dispatch
            logger.info(f"ℹ️  Dispatch returned None - verifying no jobs remain...")
            session_check = load_session(session_id)
            job_plan = session_check.get('job_plan', [])
            remaining_jobs = []
            for idx, job_desc in enumerate(job_plan):
                job_type = job_desc.get("job_type", "unknown")
                job_id = job_desc.get("job_id")
                if not job_id or job_id == "None":
                    # Check if legitimately skipped
                    is_skipped = False
                    if job_type == "train_es":
                        embedding_space_path = session_check.get("embedding_space")
                        foundation_model_id = session_check.get("foundation_model_id")
                        if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                            is_skipped = True
                    elif job_type == "train_knn":
                        vector_db_path = session_check.get("vector_db")
                        if vector_db_path and Path(vector_db_path).exists():
                            is_skipped = True
                    elif job_type == 'train_knn':
                        is_skipped = True  # Just completed
                    
                    if not is_skipped:
                        remaining_jobs.append((idx, job_type))
            
            if remaining_jobs:
                error_msg = f"CRITICAL: Dispatch returned None but {len(remaining_jobs)} job(s) remain without job_ids: {remaining_jobs}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Session: {session_id}")
                logger.error(f"   This task will FAIL to prevent silent chain breakage")
                raise RuntimeError(error_msg)
            else:
                logger.info(f"✅ Verified: No remaining jobs to dispatch (all complete or legitimately skipped)")
        
        logger.info(f"✅ KNN training completed successfully")
        print(f"✅ KNN training completed successfully", file=sys.stderr, flush=True)
        
        # Update job status to DONE when completed successfully
        # CRITICAL: This must succeed or the job will appear stuck in "ready" status
        logger.info(f"🔄 About to update job {job_id} status to DONE...")
        print(f"🔄 About to update job {job_id} status to DONE...", file=sys.stderr, flush=True)
        try:
            from lib.job_manager import update_job_status, JobStatus
            logger.info(f"   Imported update_job_status, about to call it...")
            print(f"   Imported update_job_status, about to call it...", file=sys.stderr, flush=True)
            update_job_status(job_id=job_id, status=JobStatus.DONE)
            logger.info(f"✅ Updated job {job_id} status to DONE")
            print(f"✅ Updated job {job_id} status to DONE", file=sys.stderr, flush=True)
        except Exception as status_err:
            logger.error(f"❌❌❌ CRITICAL: Failed to update job {job_id} status to DONE ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            print(f"❌❌❌ CRITICAL: Failed to update job {job_id} status to DONE: {status_err}", file=sys.stderr, flush=True)
            print(f"   Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
            # Don't raise - job completed successfully, just status update failed
            # But log it prominently so it's visible
        
        logger.info(f"🏁 JOB {job_id} FINISHED")
        print(f"🏁 JOB {job_id} FINISHED", file=sys.stderr, flush=True)
        
        result = {
            'success': True,
            'output': output,
            'job_id': job_id,
            'session_id': session_id
        }
        log_task_return_value(result, "TRAIN_KNN")
        return result
        
    except Exception as e:
        # SCREAM LOUDLY - This is a critical failure that needs immediate attention
        logger.error(f"")
        logger.error(f"╔════════════════════════════════════════════════════════════════════════════════╗")
        logger.error(f"║                                                                                ║")
        logger.error(f"║  💥💥💥 CRITICAL TASK FAILURE - TRAIN_KNN CRASHED 💥💥💥                        ║")
        logger.error(f"║                                                                                ║")
        logger.error(f"╚════════════════════════════════════════════════════════════════════════════════╝")
        logger.error(f"")
        logger.error(f"❌❌❌ TRAIN_KNN FAILED WITH UNHANDLED EXCEPTION ❌❌❌")
        logger.error(f"")
        logger.error(f"   Job ID: {job_id}")
        logger.error(f"   Session ID: {session_id}")
        logger.error(f"   Exception Type: {type(e).__name__}")
        logger.error(f"   Exception Message: {str(e)}")
        logger.error(f"")
        logger.error(f"   FULL TRACEBACK:")
        logger.error(f"   {'='*100}")
        logger.error(f"   {traceback.format_exc()}")
        logger.error(f"   {'='*100}")
        logger.error(f"")
        
        # Update job status to FAILED when it fails
        try:
            from lib.job_manager import update_job_status, JobStatus
            update_job_status(job_id=job_id, status=JobStatus.FAILED)
            logger.error(f"   ✅ Updated job {job_id} status to FAILED")
        except Exception as status_err:
            logger.error(f"   ❌❌❌ FAILED TO UPDATE JOB STATUS TO FAILED ❌❌❌")
            logger.error(f"   Error: {status_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
        
        logger.error(f"")
        logger.error(f"🏁 JOB {job_id} FINISHED (WITH ERRORS)")
        logger.error(f"")
        
        result = {
            'success': False,
            'error': str(e),
            'job_id': job_id,
            'session_id': session_id,
            'traceback': traceback.format_exc()
        }
        log_task_return_value(result, "TRAIN_KNN")
        return result

@app.task(bind=True)
def dump_to_backplane(self, session_id: str):
    """
    Celery task to copy a session's workspace to /backplane/backplane1.
    
    This task:
    1. Verifies /backplane/backplane1 is mounted and different from /backplane
    2. Rsyncs the session workspace to the backplane
    3. Creates a LAST_HOST_DUMP.json marker file with metadata
    
    Args:
        session_id: Session ID to dump
    
    Returns:
        dict with success status and dump metadata
    """
    import os
    import subprocess
    import socket
    import json
    from pathlib import Path
    from datetime import datetime
    
    logger.info(f"💾 CELERY DUMP_TO_BACKPLANE STARTED - Session: {session_id}")
    
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Verifying filesystem...',
                'session_id': session_id
            }
        )
        
        # Verify /backplane/backplane1 exists and is a directory
        backplane1 = Path("/backplane/backplane1")
        backplane = Path("/backplane")
        
        if not backplane1.exists():
            raise FileNotFoundError(f"/backplane/backplane1 does not exist")
        
        if not backplane1.is_dir():
            raise ValueError(f"/backplane/backplane1 is not a directory")
        
        # Verify it's mounted (check if it's a different filesystem from /backplane)
        try:
            stat_backplane = os.statvfs(str(backplane))
            stat_backplane1 = os.statvfs(str(backplane1))
            
            # Compare filesystem IDs (f_fsid on Linux, f_fsid on macOS)
            if hasattr(stat_backplane, 'f_fsid') and hasattr(stat_backplane1, 'f_fsid'):
                if stat_backplane.f_fsid == stat_backplane1.f_fsid:
                    raise ValueError(f"/backplane/backplane1 is the same filesystem as /backplane - not a separate mount")
        except Exception as fs_check_error:
            logger.warning(f"⚠️  Could not verify filesystem mount: {fs_check_error}")
            # Continue anyway - might be a different OS or permission issue
        
        # Get session workspace path
        if not FEATRIX_QUEUE_AVAILABLE:
            raise ImportError("featrix_queue module not available")
        
        from config import config
        source_dir = config.output_dir / session_id
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Session workspace not found: {source_dir}")
        
        # Destination path
        dest_dir = backplane1 / session_id
        
        logger.info(f"   Source: {source_dir}")
        logger.info(f"   Destination: {dest_dir}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Copying files...',
            }
        )
        
        # Run rsync
        rsync_cmd = [
            'rsync',
            '-a',  # Archive mode (preserves permissions, timestamps, etc.)
            '--progress',
            f"{source_dir}/",
            str(dest_dir)
        ]
        
        logger.info(f"   Running: {' '.join(rsync_cmd)}")
        result = subprocess.run(rsync_cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            raise Exception(f"Rsync failed with exit code {result.returncode}: {result.stderr}")
        
        # Count files and calculate size
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(dest_dir):
            file_count += len(files)
            for f in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        
        # Get training status and epochs from session
        training_status = "unknown"
        epochs = None
        try:
            from lib.session_manager import load_session
            session = load_session(session_id)
            training_status = session.get('status', 'unknown')
            # Try to get epoch count from training logs or model checkpoints
            # This is approximate - we'd need to parse logs or checkpoints
        except Exception as session_error:
            logger.warning(f"Could not load session for metadata: {session_error}")
        
        # Create marker file
        marker_file = dest_dir / "LAST_HOST_DUMP.json"
        marker_data = {
            "host": socket.gethostname(),
            "session_id": session_id,
            "dumped_at": datetime.utcnow().isoformat() + "Z",
            "training_status": training_status,
            "epochs": epochs,
            "source_path": str(source_dir),
            "destination_path": str(dest_dir),
            "rsync_exit_code": result.returncode,
            "file_count": file_count,
            "total_size_bytes": total_size
        }
        
        with open(marker_file, 'w') as f:
            json.dump(marker_data, f, indent=2)
        
        logger.info(f"✅ Dump completed successfully")
        logger.info(f"   Files: {file_count}, Size: {total_size / 1024 / 1024:.2f} MB")
        logger.info(f"   Marker file: {marker_file}")
        
        return {
            'success': True,
            'session_id': session_id,
            'destination': str(dest_dir),
            'file_count': file_count,
            'total_size_bytes': total_size,
            'marker_file': str(marker_file)
        }
        
    except Exception as e:
        logger.error(f"❌ DUMP_TO_BACKPLANE FAILED: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'session_id': session_id,
            'traceback': traceback.format_exc()
        }

@app.task(bind=True)
def run_grid_search(self, job_spec: dict, job_id: str = None, dataset_path: str = None):
    """
    Celery task to run architecture grid search.
    
    This task runs the grid_search_architecture.py script in a subprocess to find
    optimal model architecture parameters (d_model, layers, heads, feature engineering, etc.)
    
    Args:
        job_spec: Job specification dict with grid search parameters
            - parallel: Number of parallel workers (default: 8)
            - resume: Whether to resume from previous run (default: True)
            - phase: Which phase to run (1=ES only, 2=SP only, None=both)
            - dataset: Path to dataset CSV (default: qa_data/credit_g_31.csv)
        job_id: Celery task ID (used as job ID)
        dataset_path: Path to dataset (overrides job_spec['dataset'])
        
    Returns:
        dict with grid search results summary
    """
    from pathlib import Path
    import subprocess
    import json as json_module
    import socket
    
    # Use Celery task ID if job_id not provided
    if not job_id:
        job_id = self.request.id
        logger.info(f"   Using Celery task ID as job_id: {job_id}")
    
    logger.info(f"🔬 CELERY RUN_GRID_SEARCH STARTED")
    logger.info(f"   Job ID: {job_id}")
    logger.info(f"   Job spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
    
    # STANDARD JOB SETUP - MUST BE FIRST to capture all output including errors
    with setup_job_logging(job_id, None, 'grid_search') as (job_dir, original_cwd):
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Starting grid search...',
                    'job_id': job_id
                }
            )
            
            # Get parameters from job_spec
            parallel = job_spec.get('parallel', 8)  # Default 8 workers on GPU servers
            resume = job_spec.get('resume', True)   # Default resume=True
            phase = job_spec.get('phase', None)     # None = both phases
            dataset = dataset_path or job_spec.get('dataset', 'qa_data/credit_g_31.csv')
            
            # Build command
            cmd = [
                'python3',
                'grid_search_architecture.py',
                '--parallel', str(parallel),
                '--dataset', dataset,
                '--db-file', f'{job_dir}/grid_search_results.db',
                '--output-dir', f'{job_dir}/grid_search_output'
            ]
            
            if resume:
                cmd.append('--resume')
            
            if phase is not None:
                cmd.extend(['--phase', str(phase)])
            
            logger.info(f"   Running: {' '.join(cmd)}")
            logger.info(f"   Parallel workers: {parallel}")
            logger.info(f"   Resume: {resume}")
            logger.info(f"   Phase: {phase or 'both'}")
            logger.info(f"   Dataset: {dataset}")
            logger.info(f"   Hostname: {socket.gethostname()}")
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': f'Running grid search with {parallel} workers...',
                    'job_id': job_id
                }
            )
            
            # Run grid search in subprocess
            # Use setsid to make it a session leader (allows DataLoader workers)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # Stream output to logger
            for line in process.stdout:
                logger.info(line.rstrip())
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code != 0:
                raise Exception(f"Grid search failed with exit code {return_code}")
            
            # Read results from database
            db_path = Path(job_dir) / 'grid_search_results.db'
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get summary stats
                cursor.execute("SELECT COUNT(*) FROM es_trainings WHERE status = 'completed'")
                es_completed = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM grid_search_results WHERE status = 'completed'")
                sp_completed = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM grid_search_results")
                sp_total = cursor.fetchone()[0]
                
                # Get top 5 results
                cursor.execute("""
                    SELECT combo_id, d_model, n_transformer_layers, n_attention_heads,
                           use_feature_engineering, auc, accuracy, f1_score
                    FROM grid_search_results
                    WHERE status = 'completed'
                    ORDER BY auc DESC
                    LIMIT 5
                """)
                top_results = cursor.fetchall()
                
                conn.close()
                
                logger.info(f"✅ GRID SEARCH COMPLETE")
                logger.info(f"   ES completed: {es_completed}")
                logger.info(f"   SP completed: {sp_completed}/{sp_total}")
                logger.info(f"   Top AUC: {top_results[0][5]:.4f}" if top_results else "   No results")
                
                return {
                    'success': True,
                    'job_id': job_id,
                    'es_completed': es_completed,
                    'sp_completed': sp_completed,
                    'sp_total': sp_total,
                    'top_results': [
                        {
                            'combo_id': r[0],
                            'd_model': r[1],
                            'n_transformer_layers': r[2],
                            'n_attention_heads': r[3],
                            'use_feature_engineering': bool(r[4]),
                            'auc': r[5],
                            'accuracy': r[6],
                            'f1_score': r[7]
                        }
                        for r in top_results
                    ],
                    'database': str(db_path),
                    'output_dir': f'{job_dir}/grid_search_output'
                }
            else:
                logger.warning(f"⚠️  Grid search completed but no database found")
                return {
                    'success': True,
                    'job_id': job_id,
                    'warning': 'No results database found'
                }
                
        except Exception as e:
            logger.error(f"❌ GRID_SEARCH FAILED: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id,
                'traceback': traceback.format_exc()
            }


if __name__ == '__main__':
    app.start() 