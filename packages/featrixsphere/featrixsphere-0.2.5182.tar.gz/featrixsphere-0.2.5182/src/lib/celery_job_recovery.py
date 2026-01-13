"""
Celery Job Recovery

Scans Redis for incomplete jobs (RUNNING or recently FAILED) and re-dispatches them.
This replaces the old file-based worker recovery mechanism.
"""
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo

import redis

from celery_app import app
from lib.job_manager import (
    get_redis_client, load_job, save_job, update_job_status,
    JobStatus, get_job_output_path
)
from lib.session_chains import dispatch_next_job_in_chain
from utils import convert_from_iso, convert_to_iso

logger = logging.getLogger(__name__)


# Store cancelled job markers in /tmp, NOT in featrix_output (which is user-visible)
CANCELLED_JOBS_DIR = Path("/tmp/featrix_cancelled_jobs")


def _mark_job_cancelled(job_id: str, replaced_by: str, reason: str) -> bool:
    """
    Mark a job as CANCELLED so it won't be picked up by recovery again.
    Writes a CANCELLED file to the filesystem that's easy to see.
    
    Returns True if successful, False otherwise.
    """
    try:
        CANCELLED_JOBS_DIR.mkdir(parents=True, exist_ok=True)
        marker_file = CANCELLED_JOBS_DIR / job_id
        content = {
            "job_id": job_id,
            "replaced_by": replaced_by,
            "reason": reason,
            "timestamp": convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))
        }
        marker_file.write_text(json.dumps(content, indent=2))
        logger.info(f"   ✅ Marked job {job_id[:12]}... as CANCELLED (replaced by {replaced_by[:12]}...)")
        return True
    except Exception as e:
        logger.warning(f"   ⚠️  Could not mark job {job_id[:12]}... as CANCELLED: {e}")
        return False


def _is_job_cancelled(job_id: str) -> bool:
    """
    Check if a job has been marked as CANCELLED.
    """
    try:
        marker_file = CANCELLED_JOBS_DIR / job_id
        return marker_file.exists()
    except Exception as e:
        logger.debug(f"Could not check cancelled status for {job_id}: {e}")
        return False


def _determine_restart_reason(upgrade_flag_path: Path) -> str:
    """
    Determine why the server restarted.
    
    Returns:
        'upgrade', 'crash', or 'dev'
    """
    if upgrade_flag_path.exists():
        return 'upgrade'
    
    # Check if we're in a dev environment (based on hostname or other indicators)
    import socket
    hostname = socket.gethostname().lower()
    if 'dev' in hostname or 'test' in hostname or 'local' in hostname:
        return 'dev'
    
    return 'crash'


def _should_retry_failed_job(job: dict) -> bool:
    """
    Check if a FAILED job should be retried.
    
    Only retry jobs that failed within the last hour.
    Does NOT retry jobs that failed due to OOM (Out of Memory) errors.
    """
    finished_at = job.get('finished_at')
    if not finished_at:
        return False
    
    # Convert to datetime if it's a string
    if isinstance(finished_at, str):
        finished_at = convert_from_iso(finished_at)
    
    # Only retry if failed within last hour
    now = datetime.now(tz=ZoneInfo("America/New_York"))
    time_since_failure = now - finished_at
    
    if time_since_failure > timedelta(hours=1):
        return False
    
    # Check if job was manually killed (don't retry those)
    recovery_info = job.get("recovery_info", [])
    for recovery in recovery_info:
        if recovery.get("manual_kill", False) or recovery.get("reason") == "manual_kill":
            logger.info(f"Job {job.get('job_id')} has manual_kill in recovery history - will not retry")
            return False
    
    # CRITICAL: Check for non-recoverable errors - don't retry these
    # These errors indicate the job cannot succeed and retrying will just waste resources
    job_id = job.get('job_id')
    error_text = ""
    
    # Check error field
    if job.get('error'):
        error_text = str(job.get('error')).lower()
    
    # Check metadata error field
    metadata = job.get('metadata', {})
    if isinstance(metadata, dict) and metadata.get('error'):
        error_text += " " + str(metadata.get('error')).lower()
    
    # Check failure_reason field
    if isinstance(metadata, dict) and metadata.get('failure_reason'):
        error_text += " " + str(metadata.get('failure_reason')).lower()
    
    # Check for OOM indicators
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
    
    if any(indicator in error_text for indicator in oom_indicators):
        logger.warning(f"🚫 Job {job_id} failed due to OOM - will NOT retry (error contains: {[ind for ind in oom_indicators if ind in error_text][:2]})")
        return False
    
    # Check for column mismatch errors - these are configuration errors, not recoverable
    # TODO: Allow retry of certain errors if a new version of the code is installed.
    #       Some errors (like column extraction failures) might be fixed in newer code versions.
    #       Implementation plan:
    #       1. Get job's version info from job_data.get('version_info') or JOB_INFO.json
    #       2. Get current version using session_manager.get_version_info()
    #       3. Compare versions (semantic_version or git_hash)
    #       4. If version changed, allow retry for these errors (they might be fixed)
    #       5. Log version comparison: "Job version: v0.2.3815 (abc123) vs Current: v0.2.3835 (def456) - allowing retry"
    non_recoverable_errors = [
        'no overlapping columns',
        'completely different datasets',
        'cannot extract columns from embedding space',
        'zero overlapping columns',
        'insufficient es→sp overlap',
        'too many new columns'
    ]
    
    if any(indicator in error_text for indicator in non_recoverable_errors):
        # TODO: Check if code version has changed since job was created
        #       If version changed, these errors might be fixed - allow retry
        #       Implementation:
        #       - Get job version: job.get('version_info', {}).get('version') or load from JOB_INFO.json
        #       - Get current version: from lib.session_manager import get_version_info; current = get_version_info()
        #       - Compare: if job_version != current.get('version') or job_git_hash != current.get('git_hash'):
        #       - If different: logger.info(f"🔄 Version changed ({job_version} -> {current['version']}), allowing retry")
        #       - Return True to allow retry
        logger.warning(f"🚫 Job {job_id} failed due to non-recoverable configuration error - will NOT retry")
        logger.warning(f"   Error: {[ind for ind in non_recoverable_errors if ind in error_text][0]}")
        return False
    
    # Also check stdout.log file if available (more reliable for OOM detection)
    try:
        output_path = get_job_output_path(job_id)
        if output_path:
            stdout_log = output_path / "logs" / "stdout.log"
            if stdout_log.exists():
                # Read last 2KB of log file to check for OOM errors
                with open(stdout_log, 'rb') as f:
                    try:
                        # Seek to end, then read last 2KB
                        f.seek(-2048, 2)  # 2KB from end
                    except OSError:
                        # File is smaller than 2KB, read from start
                        f.seek(0)
                    log_tail = f.read().decode('utf-8', errors='ignore').lower()
                    
                    if any(indicator in log_tail for indicator in oom_indicators):
                        logger.warning(f"🚫 Job {job_id} failed due to OOM (detected in stdout.log) - will NOT retry")
                        return False
    except Exception as log_check_err:
        # If we can't check the log, that's okay - we already checked error fields
        logger.debug(f"Could not check stdout.log for job {job_id}: {log_check_err}")
    
    return True


def _kill_orphaned_training_processes() -> int:
    """
    Find and kill orphaned training processes (PPID=1) that survived a worker restart.
    
    Training processes are spawned as session leaders (start_new_session=True) which
    means they survive when the Celery worker is killed. This causes multiple training
    jobs to run simultaneously when only one should be running.
    
    Returns:
        Number of orphaned processes killed
    """
    import subprocess
    import signal
    
    killed_count = 0
    
    try:
        # Find sp_training_wrapper processes with PPID=1 (orphaned)
        ps_output = subprocess.check_output(
            ["ps", "-o", "pid,ppid,cmd", "-C", "python"],
            text=True
        )
        
        for line in ps_output.split('\n'):
            if 'sp_training_wrapper.py' in line:
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    pid = int(parts[0])
                    ppid = int(parts[1])
                    
                    # PPID=1 means orphaned (adopted by init)
                    if ppid == 1:
                        logger.warning(f"🧹 Found orphaned training process: PID {pid}")
                        logger.warning(f"   Command: {parts[2]}")
                        logger.warning(f"   Killing orphaned process...")
                        
                        try:
                            # First try SIGTERM for graceful shutdown
                            subprocess.run(["kill", "-TERM", str(pid)], check=False, timeout=5)
                            time.sleep(2)
                            
                            # Check if still running
                            try:
                                subprocess.run(["kill", "-0", str(pid)], check=True, timeout=1)
                                # Still running, use SIGKILL
                                logger.warning(f"   Process {pid} didn't respond to SIGTERM, using SIGKILL")
                                subprocess.run(["kill", "-KILL", str(pid)], check=False, timeout=5)
                            except subprocess.CalledProcessError:
                                # Process is dead
                                pass
                            
                            logger.info(f"   ✅ Killed orphaned training process {pid}")
                            killed_count += 1
                            
                        except Exception as kill_err:
                            logger.error(f"   ❌ Failed to kill orphaned process {pid}: {kill_err}")
        
        if killed_count > 0:
            logger.info(f"🧹 Killed {killed_count} orphaned training process(es)")
        else:
            logger.debug("✅ No orphaned training processes found")
            
    except subprocess.CalledProcessError as e:
        logger.debug(f"ps command failed (no python processes?): {e}")
    except Exception as e:
        logger.warning(f"Failed to check for orphaned training processes: {e}")
    
    return killed_count


def _is_celery_task_active(task_id: str) -> bool:
    """
    Check if a Celery task is currently active, reserved, or queued.
    
    Args:
        task_id: Celery task ID to check
        
    Returns:
        True if task exists in Celery system, False otherwise
    """
    try:
        # Check active tasks
        inspect = app.control.inspect(timeout=1.0)
        
        # Check active (currently executing) tasks
        active_tasks = inspect.active() or {}
        for worker_name, tasks in active_tasks.items():
            for task in tasks:
                if task.get('id') == task_id:
                    logger.debug(f"Task {task_id} found in active tasks on {worker_name}")
                    return True
        
        # Check reserved (queued but not started) tasks
        reserved_tasks = inspect.reserved() or {}
        for worker_name, tasks in reserved_tasks.items():
            for task in tasks:
                if task.get('id') == task_id:
                    logger.debug(f"Task {task_id} found in reserved tasks on {worker_name}")
                    return True
        
        # Check scheduled tasks
        scheduled_tasks = inspect.scheduled() or {}
        for worker_name, tasks in scheduled_tasks.items():
            for task in tasks:
                if task.get('id') == task_id:
                    logger.debug(f"Task {task_id} found in scheduled tasks on {worker_name}")
                    return True
        
        logger.debug(f"Task {task_id} NOT found in Celery system - orphaned/lost")
        return False
        
    except Exception as e:
        logger.warning(f"Failed to check Celery task status for {task_id}: {e}")
        # If we can't check, assume it's active to avoid false positives
        return True


def _should_recover_job(job: dict, restart_reason: str) -> bool:
    """
    Check if a job should be recovered based on retry limits.
    
    Args:
        job: Job data dict
        restart_reason: 'upgrade', 'crash', or 'dev'
        
    Returns:
        True if job should be recovered
    """
    job_type = job.get('job_type')
    job_status = job.get('status')
    
    # CRITICAL: Never recover jobs that are already DONE (completed successfully)
    # Most job types should not be restarted when DONE
    # Exception: create_structured_data has special logic below to check if next job was dispatched
    if job_status == JobStatus.DONE:
        if job_type == 'create_structured_data':
            # Special case: create_structured_data can be recovered if next job wasn't dispatched
            # (fall through to check below)
            pass
        elif job_type in ['train_es', 'train_single_predictor', 'train_knn', 'run_clustering', 'project_training_movie_frame']:
            # These job types should never be recovered when DONE
            logger.info(f"⏭️  Skipping recovery for {job_type} job {job.get('job_id')} - job status is DONE (completed successfully)")
            return False
        else:
            # For any other job type that's DONE, skip recovery by default
            # This prevents restarting completed jobs of unknown types
            logger.info(f"⏭️  Skipping recovery for {job_type} job {job.get('job_id')} - job status is DONE (completed successfully)")
            return False
    
    # CRITICAL: Check if job is create_structured_data that completed but never dispatched next job
    # This happens when worker is killed after job completes but before dispatch_next_job_in_chain runs
    if job_type == 'create_structured_data' and job_status == JobStatus.DONE:
        # Check if next job in chain was dispatched
        session_id = job.get('session_id')
        if session_id and session_id != 'unknown':
            try:
                from lib.session_manager import load_session
                session = load_session(session_id)
                job_plan = session.get('job_plan', [])
                
                # Find the next job after create_structured_data
                found_csd = False
                next_job_dispatched = False
                for job_desc in job_plan:
                    if found_csd:
                        # This is the job after create_structured_data
                        if job_desc.get('job_id'):
                            next_job_dispatched = True
                        break
                    if job_desc.get('job_type') == 'create_structured_data':
                        found_csd = True
                
                if found_csd and not next_job_dispatched:
                    logger.info(f"🔍 Job {job.get('job_id')} is DONE but next job was never dispatched - needs recovery")
                    return True
            except Exception as e:
                logger.debug(f"Could not check if next job was dispatched: {e}")
    
    # Always recover for upgrades and dev restarts (unless job is already DONE)
    if restart_reason in ['upgrade', 'dev']:
        return True
    
    # For crashes, check retry limits
    recovery_info = job.get("recovery_info", [])
    if not recovery_info:
        return True  # No previous recovery attempts
    
    # Count recovery attempts in last 24 hours
    now = datetime.now(tz=ZoneInfo("America/New_York"))
    recent_recoveries = 0
    
    for recovery in recovery_info:
        recovered_at = recovery.get("recovered_at")
        if recovered_at:
            if isinstance(recovered_at, str):
                recovered_at = convert_from_iso(recovered_at)
            
            if (now - recovered_at) < timedelta(hours=24):
                recent_recoveries += 1
    
    # Limit to 3 retries per 24 hours for crash recovery
    max_retries = 3
    if recent_recoveries >= max_retries:
        logger.warning(f"Job {job.get('job_id')} has {recent_recoveries} recent recoveries - blocking retry")
        return False
    
    return True


def _add_recovery_info(job: dict, restart_reason: str, resume_epoch: int = None, checkpoint_file: str = None):
    """Add recovery info to job metadata."""
    if "recovery_info" not in job:
        job["recovery_info"] = []
    
    recovery_entry = {
        "recovered_at": convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York"))),
        "restart_reason": restart_reason,
        "previous_status": job.get("status"),
        "previous_job_id": job.get("job_id")
    }
    
    # Add checkpoint info if resuming
    if resume_epoch is not None:
        recovery_entry["resume_epoch"] = resume_epoch
        recovery_entry["reason"] = f"server_restart_{restart_reason}_resume_checkpoint"
    else:
        recovery_entry["reason"] = f"server_restart_{restart_reason}"
    
    if checkpoint_file is not None:
        # Extract just the filename for cleaner logs
        recovery_entry["checkpoint_file"] = Path(checkpoint_file).name
    
    job["recovery_info"].append(recovery_entry)


def _find_latest_checkpoint(job_id: str, job_type: str) -> tuple[Optional[int], Optional[str]]:
    """
    Find the latest checkpoint for a job.
    
    Args:
        job_id: Job ID
        job_type: Job type (train_es, train_single_predictor, etc.)
        
    Returns:
        (resume_epoch, checkpoint_path) tuple, or (None, None) if no checkpoint found
    """
    import re
    
    try:
        output_path = get_job_output_path(job_id)
        if not output_path or not output_path.exists():
            return None, None
        
        # Different checkpoint patterns for different job types
        if job_type == 'train_es':
            # Embedding space training uses .pt files: checkpoint_inference_e-N.pt
            checkpoint_files = list(output_path.glob("checkpoint_inference_e-*.pt"))
            pattern = r'checkpoint_inference_e-(\d+)\.pt'
        elif job_type == 'train_single_predictor':
            # Single predictor training uses .pickle files: single_predictor_epoch_N.pickle or single_predictor_epoch_N_hourly.pickle
            checkpoint_files = list(output_path.glob("single_predictor*_epoch_*.pickle"))
            pattern = r'single_predictor.*_epoch_(\d+)(?:_hourly)?\.pickle'
        else:
            logger.debug(f"No checkpoint pattern defined for job type {job_type}")
            return None, None
        
        if not checkpoint_files:
            logger.debug(f"No checkpoint files found for job {job_id} (type: {job_type})")
            return None, None
        
        # Find the latest checkpoint by epoch number
        latest_epoch = -1
        latest_checkpoint = None
        
        for checkpoint_file in checkpoint_files:
            # Extract epoch from filename
            match = re.search(pattern, checkpoint_file.name)
            if match:
                epoch = int(match.group(1))
                if epoch > latest_epoch:
                    latest_epoch = epoch
                    latest_checkpoint = checkpoint_file
        
        if latest_checkpoint and latest_epoch >= 0:
            logger.info(f"📁 Found latest checkpoint for job {job_id}: {latest_checkpoint.name} (epoch {latest_epoch})")
            return latest_epoch, str(latest_checkpoint)
        
        return None, None
        
    except Exception as e:
        logger.warning(f"Failed to find checkpoints for job {job_id}: {e}")
        return None, None


def _recover_job(job: dict, restart_reason: str) -> Optional[str]:
    """
    Recover a single job by re-dispatching it.
    
    Args:
        job: Job data dict
        restart_reason: 'upgrade', 'crash', or 'dev'
        
    Returns:
        New task ID if successful, None otherwise
    """
    job_id = job.get('job_id')
    job_type = job.get('job_type')
    session_id = job.get('session_id')
    job_spec = job.get('job_spec', {}).copy()  # IMPORTANT: Copy so we can modify without affecting original

    # Check if this job was already marked as CANCELLED (has a file in CANCELLED directory)
    if _is_job_cancelled(job_id):
        logger.debug(f"⏭️  Skipping job {job_id[:12]}... - already marked as CANCELLED")
        return None

    # CRITICAL: Check if there's already a RUNNING job of the same type for this session
    # This prevents creating duplicate jobs when recovery runs multiple times
    if session_id and session_id != 'unknown' and job_type and job_type != 'unknown':
        try:
            from lib.job_manager import get_session_jobs
            existing_jobs = get_session_jobs(session_id)
            for existing_job in existing_jobs:
                existing_job_id = existing_job.get('job_id')
                existing_job_type = existing_job.get('job_type') or existing_job.get('type')
                existing_status = existing_job.get('status')
                
                # Skip if it's the same job we're trying to recover
                if existing_job_id == job_id:
                    continue
                
                # If there's another RUNNING job of the same type, don't create a duplicate
                if (existing_job_type == job_type and 
                    existing_status in [JobStatus.RUNNING, JobStatus.RUNNING.value, 'running', 'RUNNING']):
                    logger.info(f"⏭️  Skipping recovery for {job_type} job {job_id[:12]}... - session {session_id[:12]}... already has RUNNING job {existing_job_id[:12]}...")
                    _mark_job_cancelled(job_id, existing_job_id, f"Session already has a RUNNING {job_type} job")
                    return None
        except Exception as check_err:
            logger.debug(f"Could not check for existing jobs: {check_err}")
            # Continue with recovery if check fails
    
    # Skip jobs with invalid/missing session_id if they're old
    # Files go missing, sessions get deleted - don't error out on old orphaned jobs
    if not session_id or session_id == 'unknown':
        created_at = job.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = convert_from_iso(created_at)
            now = datetime.now(tz=ZoneInfo("America/New_York"))
            age = now - created_at
            
            # Skip jobs older than 1 hour with invalid session_id
            if age > timedelta(hours=1):
                logger.info(f"⏭️  Skipping old job {job_id} with invalid session_id '{session_id}' - age: {age}")
                return None
            else:
                logger.warning(f"⚠️  Job {job_id} has invalid session_id '{session_id}' but is recent ({age}) - will attempt recovery")
        else:
            logger.warning(f"⚠️  Job {job_id} has invalid session_id '{session_id}' and no created_at - skipping recovery")
            return None
    
    # Try to infer job_type from job_spec or other fields if missing/unknown
    if not job_type or job_type == 'unknown':
        # Try to infer from job_spec keys or queue_name
        queue_name = job.get('queue_name') or job_spec.get('queue_name')
        if queue_name:
            # Map queue names to job types
            queue_to_type = {
                'cpu_data_tasks': 'create_structured_data',
                'train_es': 'train_es',
                'train_knn': 'train_knn',
                'gpu_training': 'train_single_predictor',  # Most common GPU job
                'cpu_worker': 'run_clustering',  # Most common CPU job
            }
            inferred_type = queue_to_type.get(queue_name)
            if inferred_type:
                logger.info(f"🔍 Inferred job_type '{inferred_type}' from queue_name '{queue_name}' for job {job_id}")
                job_type = inferred_type
            else:
                logger.warning(f"⚠️  Could not infer job_type from queue_name '{queue_name}' for job {job_id}")
        
        # Try to infer from job_spec structure
        if (not job_type or job_type == 'unknown') and job_spec:
            if 'data_file' in job_spec or 'sqlite_db' in job_spec:
                if 'target_column' in job_spec:
                    inferred_type = 'train_single_predictor'
                elif 'embedding_space' in job_spec:
                    inferred_type = 'train_knn'
                else:
                    inferred_type = 'create_structured_data'
                logger.info(f"🔍 Inferred job_type '{inferred_type}' from job_spec structure for job {job_id}")
                job_type = inferred_type
        
        # Try to infer from job_id pattern (last resort)
        if (not job_type or job_type == 'unknown') and job_id:
            inferred_type = None
            # Job IDs sometimes contain job type in the name
            job_id_lower = job_id.lower()
            if 'train_es' in job_id_lower or job_id_lower.startswith('es_'):
                inferred_type = 'train_es'
            elif 'train_single_predictor' in job_id_lower or job_id_lower.startswith('sp_'):
                inferred_type = 'train_single_predictor'
            elif 'create_structured_data' in job_id_lower or job_id_lower.startswith('csd_'):
                inferred_type = 'create_structured_data'
            elif 'train_knn' in job_id_lower or job_id_lower.startswith('knn_'):
                inferred_type = 'train_knn'
            
            if inferred_type:
                logger.info(f"🔍 Inferred job_type '{inferred_type}' from job_id pattern for job {job_id}")
                job_type = inferred_type
        
        # Try to infer from session's job_plan (if session_id is available)
        if (not job_type or job_type == 'unknown') and session_id and session_id != 'unknown':
            try:
                from lib.session_manager import load_session
                session = load_session(session_id)
                if session and hasattr(session, 'job_plan'):
                    # Look for this job_id in the job_plan
                    for planned_job in session.job_plan:
                        if planned_job.get('job_id') == job_id:
                            planned_type = planned_job.get('job_type') or planned_job.get('type')
                            if planned_type:
                                logger.info(f"🔍 Inferred job_type '{planned_type}' from session job_plan for job {job_id}")
                                job_type = planned_type
                                break
            except Exception as e:
                logger.debug(f"Could not load session {session_id} to infer job_type: {e}")
    
    if not job_type or job_type == 'unknown':
        logger.warning(f"⚠️  Job {job_id} missing or unknown job_type - cannot recover")
        logger.warning(f"   Job data: job_type={job.get('job_type')}, queue_name={job.get('queue_name')}, session_id={session_id}")
        logger.warning(f"   job_spec keys: {list(job_spec.keys()) if job_spec else 'None'}")
        logger.warning(f"   All job keys: {list(job.keys())}")
        return None
    
    if not session_id:
        logger.warning(f"⚠️  Job {job_id} missing session_id - cannot recover")
        return None
    
    # CRITICAL: For training jobs, check for checkpoints and add resume information
    # This allows jobs to pick up where they left off instead of starting from scratch
    if job_type in ['train_es', 'train_single_predictor']:
        resume_epoch, checkpoint_path = _find_latest_checkpoint(job_id, job_type)
        
        if resume_epoch is not None and checkpoint_path is not None:
            # Update job spec with resume information
            # Note: Different job types use different parameter names
            # The checkpoint_path is absolute, pointing to the old job directory
            # The training code will need to handle this (it constructs paths relative to new job directory)
            if job_type == 'train_es':
                job_spec['resume_from_epoch'] = resume_epoch
                job_spec['resume_from_checkpoint'] = checkpoint_path  # Absolute path to old job directory
            elif job_type == 'train_single_predictor':
                # Single predictor uses 'resume_from_predictor' parameter
                job_spec['resume_from_predictor'] = checkpoint_path
                # Note: resume_from_epoch is not used by single predictor training
            
            logger.info(f"✅ Job {job_id} will resume from epoch {resume_epoch}")
            logger.info(f"   Checkpoint: {checkpoint_path}")
            logger.info(f"   NOTE: Checkpoint is in old job directory - training code must handle absolute path")
        else:
            logger.info(f"ℹ️  No checkpoint found for job {job_id} - will start from scratch")
    
    # CRITICAL: Check if this job already has a job_id in the session's job_plan
    # If it does, and it's different from the current job_id, another process may have
    # already recovered or re-dispatched it. Don't create duplicates.
    #
    # ALSO CHECK REDIS: Even if job_plan shows job_id=None (job wasn't added to plan),
    # there might be a RUNNING job of this type already. This prevents duplicates when
    # the job_plan update failed but the job is actually running.
    #
    # SPECIAL CASE: project_training_movie_frame jobs are NOT in job_plan - they're created
    # dynamically during training. Skip recovery if:
    # 1. Job is not in job_plan (likely orphaned/stale)
    # 2. Job's checkpoint no longer exists
    # 3. The training session is already complete
    #
    # Skip this check if session_id is invalid - files go missing, don't error out
    session = None
    job_plan = []
    try:
        if not session_id or session_id == 'unknown':
            logger.debug(f"Skipping session validation for job {job_id} - invalid session_id '{session_id}'")
            # Still allow recovery for recent jobs with invalid sessions (already validated age above)
        else:
            from lib.session_manager import load_session
            session = load_session(session_id)
            job_plan = session.get("job_plan", [])
        
        # Special handling for project_training_movie_frame jobs
        if job_type == 'project_training_movie_frame':
            # These jobs are NOT in job_plan - they're created dynamically during training
            # Check if the checkpoint file still exists
            checkpoint_path = job_spec.get('checkpoint_path')
            if checkpoint_path:
                if not Path(checkpoint_path).exists():
                    logger.info(f"⏭️  Skipping project_training_movie_frame job {job_id} - checkpoint no longer exists: {checkpoint_path}")
                    return None
            
            # Check if the training session is already complete (only if we have a valid session)
            if session:
                foundation_model_id = session.get("foundation_model_id")
                if foundation_model_id:
                    # Training is complete - don't recover old movie frame jobs
                    logger.info(f"⏭️  Skipping project_training_movie_frame job {job_id} - training session already complete (foundation_model_id: {foundation_model_id})")
                    return None
            
            # Check job age - don't recover movie frame jobs older than 24 hours
            created_at = job.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = convert_from_iso(created_at)
                now = datetime.now(tz=ZoneInfo("America/New_York"))
                age = now - created_at
                if age > timedelta(hours=24):
                    logger.info(f"⏭️  Skipping project_training_movie_frame job {job_id} - too old ({age})")
                    return None
            
            logger.info(f"✅ project_training_movie_frame job {job_id} passed all checks - will recover")
        
        # Check if any job in the plan has this job_id or a different job_id for the same job_type
        # Only check if we have a valid job_plan
        if job_plan:
            for job_desc in job_plan:
                if job_desc and job_desc.get("job_type") == job_type:
                    existing_job_id = job_desc.get("job_id")
                    if existing_job_id and existing_job_id != job_id:
                        # This job type already has a different job_id - it may have been re-dispatched
                        logger.info(f"⏭️  Job {job_id} (type: {job_type}) already has job_id {existing_job_id} in session - skipping recovery to prevent duplicates")
                        _mark_job_cancelled(job_id, existing_job_id, "Session job_plan shows replacement exists")
                        return existing_job_id  # Return the existing job_id
        
        # CRITICAL: Check Redis for any RUNNING jobs of this type for this session
        # This catches the case where job_plan shows job_id=None but a job is actually running
        # (happens when job dispatch succeeded but job_plan update failed)
        if session_id and session_id != 'unknown':
            try:
                client = get_redis_client()
                all_job_keys = client.keys("job:*")
                
                for key in all_job_keys:
                    try:
                        other_job_json = client.hget(key, "data")
                        if other_job_json:
                            other_job = json.loads(other_job_json)
                            
                            # Check if this is a RUNNING job of the same type for the same session
                            if (other_job.get("session_id") == session_id and
                                other_job.get("job_type") == job_type and
                                other_job.get("status") == JobStatus.RUNNING and
                                other_job.get("job_id") != job_id):
                                
                                existing_running_job_id = other_job.get("job_id")
                                logger.warning(
                                    f"⏭️  Found existing RUNNING {job_type} job {existing_running_job_id[:12]}... "
                                    f"for session {session_id[:16]}... in Redis. "
                                    f"Skipping recovery of job {job_id[:12]}... to prevent duplicate."
                                )
                                _mark_job_cancelled(job_id, existing_running_job_id, "Redis shows replacement already RUNNING")
                                return existing_running_job_id
                    except redis.exceptions.ResponseError as wrongtype_err:
                        # Key exists but is wrong type (not a hash) - skip it
                        logger.debug(f"Skipping non-hash key {key}: {wrongtype_err}")
                        continue
                    except (json.JSONDecodeError, KeyError):
                        continue
            except Exception as redis_check_err:
                logger.debug(f"Could not check Redis for existing jobs: {redis_check_err}")
                # Continue - better to risk a duplicate than skip recovery entirely
                
    except FileNotFoundError as fnf_err:
        # Session file was deleted - this is normal, files go missing
        logger.warning(f"⚠️  Session {session_id} no longer exists for job {job_id}: {fnf_err}")
        logger.warning(f"   Skipping session validation - will attempt recovery anyway if job is recent")
    except Exception as check_err:
        logger.warning(f"⚠️  Could not check session job_plan for job {job_id}: {check_err}")
        # Continue with recovery anyway - better to recover than skip
    
    try:
        # Get resume info if we added it earlier (different field names for different job types)
        resume_epoch = job_spec.get('resume_from_epoch')  # Used by train_es
        checkpoint_path = job_spec.get('resume_from_checkpoint') or job_spec.get('resume_from_predictor')  # train_es uses resume_from_checkpoint, train_single_predictor uses resume_from_predictor
        
        # Add recovery info
        _add_recovery_info(job, restart_reason, resume_epoch=resume_epoch, checkpoint_file=checkpoint_path)
        
        # Determine which Celery task to call
        task_name_map = {
            'create_structured_data': 'celery_app.create_structured_data',
            'pre_analysis_architecture': 'celery_app.pre_analysis_architecture',
            'train_es': 'celery_app.train_es',
            'train_knn': 'celery_app.train_knn',
            'train_single_predictor': 'celery_app.train_single_predictor',
            'run_clustering': 'celery_app.run_clustering',
            'project_training_movie_frame': 'celery_app.project_training_movie_frame',
        }
        
        task_name = task_name_map.get(job_type)
        if not task_name:
            logger.warning(f"⚠️  Unknown job_type {job_type} for job {job_id}")
            return None
        
        # For create_structured_data, we need data_file
        data_file = None
        if job_type == 'create_structured_data':
            # Try to get data_file from job_spec or session
            data_file = job_spec.get('data_file')
            if not data_file and session_id and session_id != 'unknown':
                try:
                    from lib.session_manager import load_session
                    session = load_session(session_id)
                    input_data = session.get('input_data')
                    if input_data and not input_data.startswith('s3://'):
                        input_path = Path(input_data)
                        if input_path.is_absolute():
                            data_file = str(input_path)
                        else:
                            from config import config
                            data_file = str(config.data_dir / input_data)
                except Exception as e:
                    logger.warning(f"⚠️  Could not get data_file for job {job_id}: {e}")
                    # Continue anyway - task may handle missing data_file
        
        # Re-dispatch the task
        logger.info(f"🔄 Re-dispatching job {job_id} (type: {job_type}, session: {session_id})")
        
        # Determine queue
        if job_type in ['train_es', 'train_single_predictor']:
            queue = 'gpu_training'
        else:
            queue = 'cpu_worker'
        
        # Match actual task signatures from celery_app.py
        if job_type == 'create_structured_data':
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id if session_id else 'N/A'}, Reason: {restart_reason})")
            new_task = app.send_task(
                task_name,
                args=[job_spec, job_id, data_file, session_id],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'train_es':
            # Check if train_es job already completed successfully before re-dispatching
            try:
                # First check job status - if it's DONE, don't re-dispatch
                job_data = load_job(job_id)
                if job_data:
                    job_status = job_data.get('status')
                    if isinstance(job_status, JobStatus):
                        status_value = job_status.value
                    else:
                        status_value = str(job_status) if job_status else None
                    
                    if status_value == JobStatus.DONE.value:
                        logger.info(f"⏭️  Skipping train_es recovery for job {job_id} - job status is DONE")
                        return None  # Don't re-dispatch if job already completed
                
                # CRITICAL: Check job output directory directly for embedding_space.pickle
                # This catches cases where job completed but session wasn't updated yet
                if session_id and session_id != 'unknown':
                    try:
                        from lib.job_manager import get_job_output_path
                        job_output_dir = get_job_output_path(job_id, session_id=session_id, job_type='train_es')
                        
                        # Check for embedding space files in job output directory using canonical find function
                        from featrix.neural.embedding_space_utils import find_embedding_space_pickle
                        es_pickle = find_embedding_space_pickle(job_output_dir)
                        if es_pickle:
                            logger.info(f"⏭️  Skipping train_es recovery for job {job_id} - embedding space file found in output directory")
                            logger.info(f"   Found: {es_pickle}")
                            logger.info(f"   File size: {es_pickle.stat().st_size / (1024*1024):.1f} MB")
                            logger.info(f"   job status: {status_value if job_data else 'unknown'}")
                            
                            # If job status isn't DONE, update it now to prevent future restarts
                            if status_value != JobStatus.DONE.value:
                                try:
                                    from lib.job_manager import update_job_status
                                    update_job_status(job_id=job_id, status=JobStatus.DONE)
                                    logger.info(f"✅ Updated job {job_id} status to DONE (found completed output)")
                                except Exception as update_err:
                                    logger.warning(f"⚠️  Could not update job status to DONE: {update_err}")
                            
                            return None  # Don't re-dispatch if ES file exists
                    except Exception as dir_check_err:
                        logger.debug(f"Could not check job output directory: {dir_check_err}")
                
                # Also check if embedding space already exists in session (fallback check)
                # Skip this check if session_id is invalid
                if session_id and session_id != 'unknown':
                    from lib.session_manager import load_session
                    session = load_session(session_id)
                    if session:
                        embedding_space_path = session.get("embedding_space")
                        foundation_model_id = session.get("foundation_model_id")
                        if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                            logger.info(f"⏭️  Skipping train_es recovery for job {job_id} - embedding space already exists in session")
                            logger.info(f"   foundation_model_id: {foundation_model_id}")
                            logger.info(f"   embedding_space_path: {embedding_space_path}")
                            logger.info(f"   embedding_space exists: {Path(embedding_space_path).exists() if embedding_space_path else False}")
                            logger.info(f"   job status: {status_value if job_data else 'unknown'}")
                            return None  # Don't re-dispatch if ES already exists
            except Exception as check_err:
                logger.warning(f"⚠️  Could not check if train_es job completed for job {job_id}: {check_err}")
                logger.warning(f"   Error details: {traceback.format_exc()}")
                # Continue with recovery - better to recover than skip if we can't check
            
            # train_es signature: (job_spec, job_id, session_id, data_file=None, strings_cache='')
            data_file = job_spec.get('data_file') or job_spec.get('sqlite_db')
            strings_cache = job_spec.get('strings_cache', '')
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id}, Reason: {restart_reason})")
            new_task = app.send_task(
                task_name,
                args=[job_spec, job_id, session_id, data_file, strings_cache],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'train_knn':
            # train_knn signature: (job_spec, job_id, session_id)
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id}, Reason: {restart_reason})")
            new_task = app.send_task(
                task_name,
                args=[job_spec, job_id, session_id],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'train_single_predictor':
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id}, Reason: {restart_reason})")
            # train_single_predictor signature: (job_spec, job_id, session_id)
            new_task = app.send_task(
                task_name,
                args=[job_spec, job_id, session_id],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'run_clustering':
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id if session_id else 'N/A'}, Reason: {restart_reason})")
            # run_clustering signature: (job_spec)
            new_task = app.send_task(
                task_name,
                args=[job_spec],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'pre_analysis_architecture':
            # pre_analysis_architecture signature: (job_spec, job_id, session_id, data_file=None, strings_cache=None)
            data_file = job_spec.get('data_file') or job_spec.get('sqlite_db')
            strings_cache = job_spec.get('strings_cache', '')
            logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id}, Reason: {restart_reason})")
            new_task = app.send_task(
                task_name,
                args=[job_spec, job_id, session_id, data_file, strings_cache],
                queue=queue
            )
            logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        elif job_type == 'project_training_movie_frame':
            logger.info(f"⏭️  Skipping project_training_movie_frame recovery for job {job_id} - will be created dynamically")
            # logger.info(f"🔄 RESTARTING JOB: {job_type} (Job ID: {job_id}, Session: {session_id if session_id else 'N/A'}, Reason: {restart_reason})")
            # project_training_movie_frame signature: (job_spec)
            # new_task = app.send_task(
            #     task_name,
            #     args=[job_spec],
            #     queue=queue
            # )
            # logger.info(f"✅ Job {job_id} restarted with new task ID: {new_task.id}")
        else:
            logger.warning(f"⚠️  Unknown job_type {job_type} - cannot re-dispatch")
            return None
        
        new_job_id = new_task.id
        logger.info(f"✅ Re-dispatched job {job_id} as new task {new_job_id}")
        
        # CRITICAL: Update session's job_plan with new job_id to prevent duplicate dispatches
        # If we don't update the session, dispatch_next_job_in_chain will see the old job_id
        # and dispatch the job again, creating duplicates
        #
        # NOTE: Some job types (like project_training_movie_frame) are NOT in job_plan,
        # so it's expected that we won't find them. Don't log warnings for these.
        #
        # Skip session update if session_id is invalid - files go missing, don't error out
        if not session_id or session_id == 'unknown':
            logger.debug(f"Skipping session job_plan update for job {job_id} - invalid session_id '{session_id}'")
        else:
            try:
                from lib.session_manager import load_session, save_session
                session = load_session(session_id)
                job_plan = session.get("job_plan", [])
                
                # Find the job in job_plan that matches the old job_id
                updated = False
                for job_desc in job_plan:
                    if job_desc.get("job_id") == job_id:
                        # Update to new job_id
                        job_desc["job_id"] = new_job_id
                        updated = True
                        logger.info(f"✅ Updated session job_plan: {job_id} → {new_job_id}")
                        break
                
                if updated:
                    save_session(session_id, session, exist_ok=True)
                    logger.info(f"✅ Session {session_id} job_plan updated with recovered job_id")
                else:
                    # Some job types are not in job_plan (e.g., project_training_movie_frame)
                    # Only log warning for job types that SHOULD be in job_plan
                    jobs_not_in_plan = {'project_training_movie_frame'}
                    if job_type not in jobs_not_in_plan:
                        logger.warning(f"⚠️  Could not find job_id {job_id} in session {session_id} job_plan - may cause duplicate dispatch")
                    else:
                        logger.debug(f"ℹ️  Job {job_id} (type: {job_type}) not in job_plan (expected - these jobs are created dynamically)")
            except FileNotFoundError as fnf_err:
                # Session file was deleted - this is normal, files go missing
                logger.warning(f"⚠️  Session {session_id} no longer exists - cannot update job_plan for job {job_id}")
                logger.warning(f"   Job {new_job_id} dispatched but may not be tracked in session")
            except Exception as session_err:
                logger.error(f"❌ Failed to update session job_plan for session {session_id}: {session_err}")
                logger.error(f"   This may cause duplicate job dispatches!")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                # Continue anyway - job is already dispatched
        
        # Update job metadata with new task ID
        job['recovered_job_id'] = new_job_id
        job['status'] = JobStatus.READY.value
        job['recovered_at'] = convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))
        save_job(new_job_id, job, session_id, job_type)
        
        return new_job_id
        
    except Exception as e:
        logger.error(f"❌ Failed to recover job {job_id}: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return None


def _cleanup_stale_movie_frame_jobs(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Clean up stale project_training_movie_frame jobs from Redis.
    
    Movie frame jobs are created dynamically during training and saved to Redis,
    but they're NOT in the session's job_plan. When training completes or is cancelled,
    these jobs can become orphaned. This function removes them.
    
    Returns:
        dict with cleanup summary
    """
    cleanup_summary = {
        "checked_count": 0,
        "deleted_count": 0,
        "deleted_jobs": []
    }
    
    logger.info(f"🧹 Checking for stale movie frame jobs...")
    
    try:
        client = get_redis_client()
        cursor = 0
        
        while True:
            cursor, keys = client.scan(cursor, match="job:*", count=100)
            
            for key in keys:
                job_id = key.replace("job:", "")
                job = load_job(job_id)
                
                if not job:
                    continue
                
                job_type = job.get('job_type')
                if job_type != 'project_training_movie_frame':
                    continue
                
                cleanup_summary["checked_count"] += 1
                
                session_id = job.get('session_id')
                job_spec = job.get('job_spec', {})
                checkpoint_path = job_spec.get('checkpoint_path')
                created_at = job.get('created_at')
                
                # Delete if checkpoint no longer exists
                should_delete = False
                reason = None
                
                if checkpoint_path and not Path(checkpoint_path).exists():
                    should_delete = True
                    reason = "checkpoint no longer exists"
                
                # Delete if older than max_age_hours
                if not should_delete and created_at:
                    if isinstance(created_at, str):
                        created_at = convert_from_iso(created_at)
                    now = datetime.now(tz=ZoneInfo("America/New_York"))
                    age = now - created_at
                    if age > timedelta(hours=max_age_hours):
                        should_delete = True
                        reason = f"too old ({age.total_seconds() / 3600:.1f} hours)"
                
                # Delete if training session is complete
                if not should_delete and session_id:
                    try:
                        from lib.session_manager import load_session
                        session = load_session(session_id)
                        if session and session.get("foundation_model_id"):
                            should_delete = True
                            reason = "training session already complete"
                    except Exception:
                        pass
                
                if should_delete:
                    logger.info(f"🗑️  Deleting stale movie frame job {job_id[:12]}... (reason: {reason})")
                    logger.info(f"   Session: {session_id}")
                    logger.info(f"   Checkpoint: {checkpoint_path}")
                    
                    # Delete from Redis
                    client.delete(f"job:{job_id}")
                    
                    cleanup_summary["deleted_count"] += 1
                    cleanup_summary["deleted_jobs"].append({
                        'job_id': job_id,
                        'session_id': session_id,
                        'reason': reason
                    })
            
            if cursor == 0:
                break
        
        if cleanup_summary["deleted_count"] > 0:
            logger.info(f"🗑️  Movie frame cleanup complete: {cleanup_summary['deleted_count']} stale jobs deleted (checked {cleanup_summary['checked_count']} jobs)")
        else:
            logger.info(f"✅ No stale movie frame jobs found (checked {cleanup_summary['checked_count']} jobs)")
    
    except Exception as e:
        logger.error(f"❌ Error in movie frame job cleanup: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    return cleanup_summary


def _cleanup_stale_queued_jobs(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Auto-fail jobs that have been queued/ready for more than max_age_hours.
    
    Scans Redis directly for READY jobs instead of loading sessions.
    This is MUCH faster than the old approach which loaded 138 sessions + 709 old job files.
    
    Jobs older than 24 hours are likely stale from:
    - Cancelled user sessions
    - Failed prerequisite jobs
    - Old experiments that were abandoned
    
    This runs on Celery worker startup to clean up the queue.
    
    Returns:
        dict with cleanup summary
    """
    cleanup_summary = {
        "checked_count": 0,
        "failed_count": 0,
        "failed_jobs": []
    }
    
    logger.info(f"🧹 Checking for stale queued jobs (older than {max_age_hours} hours) - scanning Redis directly...")
    
    try:
        from lib.job_manager import update_job_status, JobStatus
        
        client = get_redis_client()
        cursor = 0
        
        # Scan all job keys in Redis (MUCH faster than loading 138 sessions + 709 old files)
        while True:
            cursor, keys = client.scan(cursor, match="job:*", count=100)
            
            for key in keys:
                job_id = key.replace("job:", "")
                job = load_job(job_id)
                
                if not job:
                    continue
                
                job_status = job.get('status')
                job_type = job.get('job_type')
                
                # Only check READY jobs (PENDING doesn't exist in JobStatus enum)
                if job_status not in [JobStatus.READY, 'READY', 'ready']:
                    continue
                
                cleanup_summary["checked_count"] += 1
                
                # Check age
                created_at = job.get('created_at')
                if not created_at:
                    continue
                
                # Convert to datetime if string
                if isinstance(created_at, str):
                    created_at = convert_from_iso(created_at)
                
                now = datetime.now(tz=ZoneInfo("America/New_York"))
                age = now - created_at
                
                if age.total_seconds() > (max_age_hours * 3600):
                    # Job is stale - auto-fail it
                    age_hours = age.total_seconds() / 3600
                    session_id = job.get('session_id', 'unknown')
                    
                    logger.warning(f"🗑️  STALE QUEUED JOB: {job_id[:12]}... ({job_type})")
                    logger.warning(f"   Age: {age_hours:.1f} hours (threshold: {max_age_hours}h)")
                    logger.warning(f"   Session: {session_id}")
                    logger.warning(f"   Created: {created_at}")
                    logger.warning(f"   Auto-failing stale job...")
                    
                    error_msg = f"Auto-failed by Celery recovery: Job was queued for {age_hours:.1f} hours without processing. Likely stale from cancelled session or failed prerequisite. Cleaned up on worker startup."
                    
                    update_job_status(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        metadata={'error': error_msg}
                    )
                    
                    cleanup_summary["failed_count"] += 1
                    cleanup_summary["failed_jobs"].append({
                        'job_id': job_id,
                        'job_type': job_type,
                        'age_hours': age_hours,
                        'session_id': session_id
                    })
                    
                    logger.info(f"   ✅ Auto-failed stale job {job_id[:12]}...")
            
            if cursor == 0:
                break
        
        if cleanup_summary["failed_count"] > 0:
            logger.info(f"🗑️  Stale job cleanup complete: {cleanup_summary['failed_count']} jobs auto-failed (checked {cleanup_summary['checked_count']} queued jobs)")
        else:
            logger.info(f"✅ No stale jobs found (checked {cleanup_summary['checked_count']} queued jobs)")
    
    except Exception as e:
        logger.error(f"❌ Error in stale job cleanup: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    return cleanup_summary


def cleanup_duplicate_running_jobs() -> Dict[str, Any]:
    """
    Find and kill duplicate RUNNING jobs for the same session+job_type.
    
    When recovery creates duplicates (old bug), we end up with multiple jobs
    running for the same session, writing to different output directories.
    This function detects duplicates and kills the older/stuck ones.
    
    Returns:
        dict with cleanup summary
    """
    cleanup_summary = {
        "checked_sessions": 0,
        "duplicates_found": 0,
        "duplicates_killed": [],
    }
    
    try:
        client = get_redis_client()
        job_keys = list(client.keys("job:*"))
        
        # Group RUNNING jobs by (session_id, job_type)
        from collections import defaultdict
        session_jobs = defaultdict(list)
        
        for key in job_keys:
            try:
                job_json = client.hget(key, "data")
                if not job_json:
                    continue
                
                job = json.loads(job_json)
                if job.get("status") != JobStatus.RUNNING:
                    continue
                
                session_id = job.get("session_id")
                job_type = job.get("job_type")
                
                if not session_id or session_id == "unknown" or not job_type:
                    continue
                
                # Group by (session_id, job_type)
                key = (session_id, job_type)
                session_jobs[key].append(job)
            except redis.exceptions.ResponseError as wrongtype_err:
                # Key exists but is wrong type (not a hash) - skip it
                logger.debug(f"Skipping non-hash key {key}: {wrongtype_err}")
                continue
            except (json.JSONDecodeError, KeyError):
                continue
        
        cleanup_summary["checked_sessions"] = len(session_jobs)
        
        # Find sessions with duplicate jobs of the same type
        for (session_id, job_type), jobs in session_jobs.items():
            if len(jobs) <= 1:
                continue  # No duplicates
            
            # Multiple jobs of same type for same session - DUPLICATES!
            logger.warning(f"🔥 Found {len(jobs)} RUNNING {job_type} jobs for session {session_id[:16]}...")
            cleanup_summary["duplicates_found"] += len(jobs) - 1
            
            # Sort by created_at - keep the newest, kill the rest
            jobs_sorted = sorted(jobs, key=lambda j: j.get("created_at", ""), reverse=True)
            newest_job = jobs_sorted[0]
            old_jobs = jobs_sorted[1:]
            
            logger.info(f"   ✅ Keeping newest job: {newest_job.get('job_id')[:12]}... (created: {newest_job.get('created_at')})")
            
            for old_job in old_jobs:
                old_job_id = old_job.get("job_id")
                created_at = old_job.get("created_at")
                # Try both field names - jobs may use either task_id or celery_task_id
                task_id = old_job.get("celery_task_id") or old_job.get("task_id")
                
                logger.warning(f"   🗑️  Killing duplicate: {old_job_id[:12]}... (created: {created_at})")
                
                # Try to revoke the Celery task if it has one
                if task_id:
                    try:
                        from celery_app import app
                        app.control.revoke(task_id, terminate=True, signal='SIGKILL')
                        logger.info(f"      ✅ Revoked Celery task {task_id[:16]}...")
                    except Exception as revoke_err:
                        logger.debug(f"      Could not revoke task: {revoke_err}")
                
                # Mark job as FAILED
                try:
                    update_job_status(
                        job_id=old_job_id,
                        status=JobStatus.FAILED,
                        metadata={
                            'error': f"Duplicate job killed by recovery. Newer job {newest_job.get('job_id')[:12]}... is handling this session.",
                            'killed_by_recovery': True,
                            'killed_at': convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))
                        }
                    )
                    logger.info(f"      ✅ Marked job as FAILED")
                except Exception as status_err:
                    logger.warning(f"      ⚠️  Could not update job status: {status_err}")
                
                cleanup_summary["duplicates_killed"].append({
                    'job_id': old_job_id,
                    'job_type': job_type,
                    'session_id': session_id[:16],
                    'created_at': created_at,
                    'kept_job': newest_job.get('job_id')[:12]
                })
        
        if cleanup_summary["duplicates_found"] > 0:
            logger.info(f"🧹 Duplicate job cleanup: Killed {cleanup_summary['duplicates_found']} duplicate job(s)")
        else:
            logger.info(f"✅ No duplicate jobs found")
    
    except Exception as e:
        logger.error(f"❌ Error in duplicate job cleanup: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    return cleanup_summary


def recover_interrupted_jobs() -> Dict[str, Any]:
    """
    Scan Redis for incomplete jobs and recover them.
    
    This function:
    1. Finds all RUNNING jobs (interrupted by restart)
    2. Finds recently FAILED jobs (within last hour)
    3. Re-dispatches them via Celery
    
    Returns:
        dict with recovery summary
    """
    recovery_summary = {
        "restart_reason": None,
        "jobs_checked": 0,
        "jobs_recovered": [],
        "jobs_blocked": [],
        "total_recovered": 0
    }
    
    # Determine restart reason
    upgrade_flag_path = Path("/tmp/UPGRADE_SPHERE")
    restart_reason = _determine_restart_reason(upgrade_flag_path)
    recovery_summary["restart_reason"] = restart_reason
    
    logger.info(f"🔍 Celery job recovery started - Reason: {restart_reason}")
    
    # Clean up upgrade flag if it exists
    if upgrade_flag_path.exists():
        try:
            with open(upgrade_flag_path, 'r') as f:
                flag_content = f.read().strip()
            logger.info(f"📋 Upgrade flag contents:\n{flag_content}")
            upgrade_flag_path.unlink()
            logger.info("🗑️  Upgrade flag cleaned up")
        except Exception as e:
            logger.warning(f"Failed to read/remove upgrade flag: {e}")
    
    # Kill orphaned training processes that survived the restart
    logger.info("🧹 Checking for orphaned training processes...")
    killed_orphans = _kill_orphaned_training_processes()
    if killed_orphans > 0:
        recovery_summary["orphaned_processes_killed"] = killed_orphans
    
    # Clean up duplicate RUNNING jobs (same session+job_type)
    logger.info("🔍 Checking for duplicate RUNNING jobs...")
    duplicate_cleanup = cleanup_duplicate_running_jobs()
    if duplicate_cleanup["duplicates_found"] > 0:
        recovery_summary["duplicates_killed"] = duplicate_cleanup["duplicates_killed"]
        logger.info(f"   ✅ Killed {duplicate_cleanup['duplicates_found']} duplicate job(s)")
    
    try:
        client = get_redis_client()
        
        # Scan for all job keys
        jobs_to_recover = []
        cursor = 0
        
        while True:
            cursor, keys = client.scan(cursor, match="job:*", count=100)
            
            for key in keys:
                job_id = key.replace("job:", "")
                job = load_job(job_id)
                
                if not job:
                    continue
                
                recovery_summary["jobs_checked"] += 1
                status = job.get("status")
                
                # Check if status is a JobStatus enum or string
                if hasattr(status, 'value'):
                    status = status.value
                
                # Skip movie frame jobs entirely - they're disabled
                if job.get('job_type') == 'project_training_movie_frame':
                    logger.debug(f"⏭️  Skipping movie frame job {job_id} - movie generation disabled")
                    continue
                
                # Include RUNNING jobs
                if status == JobStatus.RUNNING.value:
                    jobs_to_recover.append(job)
                    logger.info(f"🔄 Found RUNNING job {job_id} (type: {job.get('job_type')})")
                
                # Include recently FAILED jobs
                elif status == JobStatus.FAILED.value:
                    if _should_retry_failed_job(job):
                        jobs_to_recover.append(job)
                        logger.info(f"🔄 Found recently FAILED job {job_id} (type: {job.get('job_type')})")
                    else:
                        finished_at = job.get('finished_at')
                        if finished_at:
                            if isinstance(finished_at, str):
                                finished_at = convert_from_iso(finished_at)
                            now = datetime.now(tz=ZoneInfo("America/New_York"))
                            age = now - finished_at
                            logger.debug(f"⏭️  Skipping FAILED job {job_id} - failed {age} ago (too old)")
                
                # Check READY jobs - they might be orphaned/lost during restart
                elif status == JobStatus.READY.value:
                    # READY means the job was dispatched but might have been lost during a restart
                    # Check if the Celery task actually exists
                    if _is_celery_task_active(job_id):
                        logger.debug(f"⏭️  Skipping READY job {job_id} - Celery task is active/queued")
                    else:
                        # Check how old this READY job is
                        created_at = job.get('created_at')
                        job_age = None
                        if created_at:
                            if isinstance(created_at, str):
                                created_at = convert_from_iso(created_at)
                            now = datetime.now(tz=ZoneInfo("America/New_York"))
                            job_age = now - created_at
                        
                        # Recover READY jobs that are old enough (likely stuck/crashed before starting)
                        # This handles cases where tasks crash immediately after dispatch but before status update
                        # CRITICAL: Lower threshold to 2 minutes for train_knn jobs since they crash immediately
                        job_type = job.get('job_type', '')
                        threshold_minutes = 2 if job_type == 'train_knn' else 5
                        
                        if job_age and job_age > timedelta(minutes=threshold_minutes):
                            logger.info(f"🔄 Found STUCK READY job {job_id} (type: {job_type}) - age: {job_age}, will recover")
                            jobs_to_recover.append(job)
                        else:
                            # Very recent READY jobs might still be starting - don't recover yet
                            logger.debug(f"⏭️  Skipping recent READY job {job_id} (type: {job_type}) - age: {job_age if job_age else 'unknown'}, too recent to recover (threshold: {threshold_minutes} min)")
                
                # Skip DONE jobs
                elif status == JobStatus.DONE.value:
                    logger.debug(f"⏭️  Skipping DONE job {job_id} (type: {job.get('job_type')}) - already complete")
            
            if cursor == 0:
                break
        
        # Recover each job with rate limiting to prevent thundering herd
        # CRITICAL: Add delays between dispatches to avoid overwhelming workers
        # train_knn jobs are particularly problematic as they hang during import
        for idx, job in enumerate(jobs_to_recover):
            job_id = job.get('job_id')
            job_type = job.get('job_type', 'unknown')
            
            # Check if should recover based on retry limits
            if not _should_recover_job(job, restart_reason):
                recovery_summary["jobs_blocked"].append({
                    "job_id": job_id,
                    "reason": "retry_limit_exceeded"
                })
                logger.warning(f"🚫 Job {job_id} exceeded retry limit - not recovering")
                continue
            
            # Rate limiting: Add delay between dispatches, especially for train_knn
            # This prevents all jobs from hitting workers simultaneously and causing hangs
            if idx > 0:  # Don't delay the first job
                if job_type == 'train_knn':
                    # train_knn jobs hang during import - space them out more
                    delay_seconds = 2.0
                    logger.info(f"⏳ Rate limiting: Waiting {delay_seconds}s before dispatching train_knn job {job_id} ({idx+1}/{len(jobs_to_recover)})")
                    time.sleep(delay_seconds)
                else:
                    # Other jobs can be dispatched faster but still need spacing
                    delay_seconds = 0.5
                    time.sleep(delay_seconds)
            
            # Recover the job
            new_job_id = _recover_job(job, restart_reason)
            if new_job_id:
                recovery_summary["jobs_recovered"].append({
                    "old_job_id": job_id,
                    "new_job_id": new_job_id,
                    "job_type": job_type,
                    "session_id": job.get('session_id')
                })
                recovery_summary["total_recovered"] += 1
        
        # Log summary
        if recovery_summary["total_recovered"] > 0:
            logger.info(f"🎯 Job recovery complete: {recovery_summary['total_recovered']} jobs recovered")
            logger.info(f"   Restart reason: {restart_reason}")
            logger.info(f"   Jobs checked: {recovery_summary['jobs_checked']}")
            logger.info(f"   Jobs blocked: {len(recovery_summary['jobs_blocked'])}")
        else:
            logger.info(f"✅ No jobs needed recovery")
        
    except Exception as e:
        logger.error(f"❌ Error during job recovery: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    # Clean up stale movie frame jobs (orphaned from completed/cancelled training)
    try:
        movie_frame_cleanup_summary = _cleanup_stale_movie_frame_jobs()
        recovery_summary["movie_frame_jobs_deleted"] = movie_frame_cleanup_summary.get("deleted_count", 0)
        recovery_summary["movie_frame_jobs_checked"] = movie_frame_cleanup_summary.get("checked_count", 0)
    except Exception as e:
        logger.error(f"❌ Error during movie frame job cleanup: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    # Clean up stale queued jobs (>24 hours old)
    try:
        stale_cleanup_summary = _cleanup_stale_queued_jobs()
        recovery_summary["stale_jobs_failed"] = stale_cleanup_summary.get("failed_count", 0)
        recovery_summary["stale_jobs_checked"] = stale_cleanup_summary.get("checked_count", 0)
    except Exception as e:
        logger.error(f"❌ Error during stale job cleanup: {e}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
    
    return recovery_summary

