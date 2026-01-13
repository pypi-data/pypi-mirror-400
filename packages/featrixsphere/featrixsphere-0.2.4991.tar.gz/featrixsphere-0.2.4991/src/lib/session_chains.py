"""
Session Chain Management

Replaces step_session with Celery chains for automatic job sequencing.
Celery tasks automatically chain to the next job when they complete.
"""
import fcntl
import logging
import time
import traceback
from pathlib import Path
from typing import Optional, List, Tuple
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo

from celery import chain

from lib.session_manager import load_session, save_session, SessionStatus

# Import app at module level - will be available throughout
try:
    from celery_app import app
except ImportError:
    # Fallback for when celery_app is not available (shouldn't happen in production)
    app = None
from lib.job_manager import save_job, load_job, JobStatus, get_redis_client
from config import config

logger = logging.getLogger(__name__)


def dispatch_next_job_in_chain(session_id: str, completed_job_type: str = None) -> Optional[str]:
    """
    Dispatch the next job in a session's job_plan that doesn't have a job_id yet.
    This is called automatically by Celery tasks when they complete.
    
    Uses file locking (flock) on the session file to prevent race conditions.
    
    Args:
        session_id: Session ID
        completed_job_type: Type of job that just completed (for logging)
        
    Returns:
        Task ID of dispatched job, or None if no more jobs
    """
    # CRITICAL: Ensure app is available (imported at module level)
    # This prevents UnboundLocalError if app is somehow not available
    if app is None:
        raise RuntimeError("Celery app is not available - cannot dispatch jobs. This usually means celery_app module failed to import.")
    
    dispatch_start = time.time()
    logger.info(f"\n{'='*80}")
    logger.info(f"🔵 [DISPATCH] DISPATCH_NEXT_JOB_IN_CHAIN called for session {session_id}")
    logger.info(f"   Timestamp: {datetime.now().isoformat()}")
    if completed_job_type:
        logger.info(f"   Triggered by completed job: {completed_job_type}")
    else:
        logger.info(f"   Initial dispatch (no previous job completed)")
    logger.info(f"{'='*80}")
    
    # Use Redis for atomic dispatch coordination (simpler than file locks, no permission issues)
    # Only ONE process should dispatch jobs for a session at a time
    redis_client = get_redis_client()
    dispatch_lock_key = f"dispatch_lock:{session_id}"
    lock_ttl = 120  # 120 second lock timeout (dispatch can take time with Celery checks)
    lock_acquired = False
    lock_acquire_start = time.time()
    max_lock_wait = 10.0  # 10 seconds max wait
    poll_interval = 0.1  # Poll every 100ms
    last_lock_refresh = time.time()
    lock_refresh_interval = 30  # Refresh lock every 30 seconds if still working
    
    def refresh_lock():
        """Refresh the dispatch lock if we're still working."""
        nonlocal last_lock_refresh
        now = time.time()
        if lock_acquired and (now - last_lock_refresh) >= lock_refresh_interval:
            try:
                redis_client.setex(dispatch_lock_key, lock_ttl, str(time.time()))
                last_lock_refresh = now
                logger.debug(f"🔄 Refreshed dispatch lock (TTL={lock_ttl}s)")
            except Exception as refresh_err:
                logger.warning(f"⚠️  Failed to refresh lock: {refresh_err}")
    
    try:
        logger.debug(f"🔒 Acquiring Redis dispatch lock for session {session_id}")
        
        # Try to acquire lock with SETNX (set if not exists) - atomic operation
        # Value is timestamp so we can detect stale locks
        lock_value = str(time.time())
        lock_acquired = redis_client.set(dispatch_lock_key, lock_value, nx=True, ex=lock_ttl)
        
        if not lock_acquired:
            # Lock is held - poll with timeout
            logger.debug(f"   Lock is held by another process, waiting up to {max_lock_wait:.1f} seconds...")
            elapsed = 0.0
            while elapsed < max_lock_wait:
                time.sleep(poll_interval)
                elapsed = time.time() - lock_acquire_start
                lock_acquired = redis_client.set(dispatch_lock_key, str(time.time()), nx=True, ex=lock_ttl)
                if lock_acquired:
                    break
            
            if not lock_acquired:
                lock_elapsed = time.time() - lock_acquire_start
                error_msg = f"Failed to acquire dispatch lock after {lock_elapsed:.2f} seconds - another process may be holding the lock (deadlock?)"
                logger.error(f"❌ CRITICAL: {error_msg}")
                logger.error(f"   Lock key: {dispatch_lock_key}")
                raise RuntimeError(error_msg)
        
        lock_elapsed = time.time() - lock_acquire_start
        if lock_elapsed > 1.0:
            logger.warning(f"⚠️  Lock acquisition took {lock_elapsed:.2f} seconds (slow)")
        else:
            logger.debug(f"✅ Acquired Redis dispatch lock in {lock_elapsed:.3f} seconds")

        # CRITICAL: Only hold lock for the minimal critical section
        # Load session, check status, find next job - then release lock
        try:
            logger.debug(f"   Loading session {session_id}...")
            session = load_session(session_id)
            logger.info(f"✅ Session loaded successfully")
            logger.debug(f"   Session type: {type(session)}, keys: {list(session.keys())[:10]}...")
        except Exception as load_error:
            logger.error(f"❌ CRITICAL: Failed to load session {session_id}: {load_error}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to load session {session_id}: {load_error}") from load_error
        
        try:
            job_plan = session.get("job_plan", [])
            logger.debug(f"   job_plan type: {type(job_plan)}, length: {len(job_plan) if job_plan else 0}")
            if not job_plan:
                logger.info(f"ℹ️  Session {session_id} has no job_plan - no jobs to dispatch (likely a cloned/foundation session)")
                logger.info(f"   Session keys: {list(session.keys())}")
                return None  # Legitimate "no jobs" case
            
            logger.info(f"📋 Session {session_id} has {len(job_plan)} jobs in job_plan")
            session_type = session.get('session_type', 'unknown')
            logger.info(f"   Session type: {session_type}")
            
            # CRITICAL: Check if there are any jobs without job_ids BEFORE checking session status
            # This allows new jobs (like predictor jobs added via API) to be dispatched even if
            # the session status is DONE (because initial jobs completed)
            jobs_without_ids = []
            for idx, job_desc in enumerate(job_plan):
                job_id = job_desc.get("job_id")
                if not job_id or job_id == "None" or job_id == "skipped-foundation-model":
                    # Check if this job was legitimately skipped
                    job_type = job_desc.get("job_type")
                    is_skipped = False
                    if job_type == "train_es":
                        embedding_space_path = session.get("embedding_space")
                        foundation_model_id = session.get("foundation_model_id")
                        if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                            is_skipped = True
                    elif job_type == "train_knn":
                        vector_db_path = session.get("vector_db")
                        if vector_db_path and Path(vector_db_path).exists():
                            is_skipped = True
                    
                    if not is_skipped:
                        jobs_without_ids.append((idx, job_type))
            
            # If there are jobs without IDs, we should dispatch them
            # Session status is computed dynamically from job statuses, not stored
            # We can always add new jobs to a session regardless of computed status
            if jobs_without_ids:
                logger.info(f"   ✅ Found {len(jobs_without_ids)} job(s) without job_ids - will dispatch")
                for idx, job_type in jobs_without_ids:
                    logger.info(f"      Job {idx}: {job_type} (needs dispatch)")
            else:
                # No jobs to dispatch - all jobs have IDs
                logger.info(f"⏭️  All jobs in job_plan have job_ids - no jobs to dispatch")
                return None
            
            # CRITICAL: For predictor sessions, explicitly check for train_single_predictor after create_structured_data
            if completed_job_type == 'create_structured_data' and session_type == 'predictor':
                logger.info(f"   🎯 PREDICTOR SESSION: Checking for train_single_predictor job after create_structured_data...")
                has_train_sp = False
                train_sp_job_id = None
                for idx, job_desc in enumerate(job_plan):
                    if job_desc.get("job_type") == 'train_single_predictor':
                        has_train_sp = True
                        train_sp_job_id = job_desc.get("job_id")
                        logger.info(f"      Found train_single_predictor at index {idx}, job_id: {train_sp_job_id}")
                        break
                if not has_train_sp:
                    logger.error(f"   ❌ CRITICAL: Predictor session has NO train_single_predictor job in job_plan!")
                elif not train_sp_job_id or train_sp_job_id == "None":
                    logger.warning(f"   ⚠️  CRITICAL: train_single_predictor job exists but has NO job_id - MUST be dispatched!")
            
            # Log current state of all jobs
            for idx, job_desc in enumerate(job_plan):
                try:
                    job_type = job_desc.get("job_type", "unknown")
                    job_id = job_desc.get("job_id", "None")
                    logger.info(f"   Job {idx}: {job_type} - job_id: {job_id}")
                except Exception as job_log_err:
                    logger.warning(f"   ⚠️  Error logging job {idx}: {job_log_err}")
                    logger.debug(f"      Job desc: {job_desc}")
            
            # Find first job without a job_id
            logger.info(f"🔍 Searching for next job to dispatch (completed: {completed_job_type})...")
        except Exception as job_plan_err:
            logger.error(f"❌ CRITICAL: Error processing job_plan: {job_plan_err}")
            logger.error(f"   Traceback: {traceback.format_exc()}")
            logger.error(f"   Session keys: {list(session.keys()) if session else 'N/A'}")
            raise
        
        # CRITICAL: Find the job to dispatch while holding the lock, then release lock
        # We'll re-acquire it only when we need to update the session
        job_to_dispatch = None
        job_idx = None
        for idx, job_desc in enumerate(job_plan):
            job_type = job_desc.get("job_type")
            job_spec = job_desc.get("spec", {})
            existing_job_id = job_desc.get("job_id")
            
            logger.info(f"   Checking job {idx}: {job_type}")
            logger.info(f"      existing_job_id: {existing_job_id}")
            
            if existing_job_id:
                # CRITICAL: Check if this job_id actually exists in Redis/Celery
                # If it's a UUID (not a Celery task ID) and doesn't exist in Redis, it's an orphaned job_id
                # from a failed dispatch. Remove it and retry.
                # load_job is imported at top of file
                job_data = load_job(existing_job_id)
                
                # Also check if it's a UUID format (8-4-4-4-12) vs Celery task ID format
                is_uuid_format = len(existing_job_id) == 36 and existing_job_id.count('-') == 4
                
                if not job_data and is_uuid_format:
                    logger.warning(f"   ⚠️  Job {idx} ({job_type}) has orphaned UUID job_id: {existing_job_id}")
                    logger.warning(f"      Job doesn't exist in Redis - this is from a failed dispatch")
                    logger.warning(f"      Removing orphaned job_id and retrying dispatch...")
                    refresh_lock()  # Refresh before save
                    job_plan[idx].pop("job_id", None)
                    save_session(session_id, session, exist_ok=True)
                    logger.info(f"   ✅ Removed orphaned job_id, will retry dispatch")
                    # CRITICAL: Clear existing_job_id so dispatch logic below works
                    existing_job_id = None
                    # Fall through to dispatch logic below (don't continue)
                elif job_data:
                    # Job exists in Redis - check its status
                    job_status = job_data.get('status')
                    if isinstance(job_status, JobStatus):
                        status_value = job_status.value
                    else:
                        status_value = str(job_status) if job_status else 'unknown'
                    
                    logger.info(f"   ⏭️  Job {idx} ({job_type}) already has job_id: {existing_job_id}, status: {status_value}")
                    if status_value == JobStatus.DONE.value:
                        logger.info(f"      Job is DONE - skipping (completed successfully)")
                        continue  # CRITICAL: Skip this job, don't re-dispatch!
                    elif status_value in [JobStatus.RUNNING.value, JobStatus.READY.value]:
                        # CRITICAL: First check if job has actually completed by examining directory
                        # This catches jobs that completed but status wasn't updated in Redis
                        from lib.job_manager import recover_stalled_job_from_directory
                        job_recovered = recover_stalled_job_from_directory(
                            job_id=existing_job_id,
                            session_id=session_id,
                            job_type=job_type
                        )
                        if job_recovered:
                            # Job was detected as completed and status was updated to DONE
                            logger.info(f"      ✅ Job {existing_job_id} was detected as completed via directory check")
                            logger.info(f"      Status updated to DONE - skipping (completed successfully)")
                            continue  # Skip this job, it's now marked as DONE
                        
                        # Check for JOB_ACK to detect stuck jobs
                        # BUT FIRST: Check if job actually completed (has output files)
                        job_has_output = False
                        if job_type == 'create_structured_data' and session.get('sqlite_db'):
                            job_has_output = True
                            logger.info(f"      Job has output (sqlite_db exists) - treating as complete despite {status_value} status")
                            continue
                        elif job_type == 'train_es' and session.get('embedding_space'):
                            job_has_output = True
                            logger.info(f"      Job has output (embedding_space exists) - treating as complete despite {status_value} status")
                            continue
                        elif job_type == 'train_single_predictor' and session.get('single_predictor'):
                            job_has_output = True
                            logger.info(f"      Job has output (single_predictor exists) - treating as complete despite {status_value} status")
                            continue
                        
                        # CRITICAL: For create_structured_data without sqlite_db, try to recover it from job output
                        # This handles cases where the job completed but session update failed
                        if job_type == 'create_structured_data' and not session.get('sqlite_db'):
                            from lib.job_manager import get_job_output_path
                            try:
                                job_dir = get_job_output_path(existing_job_id, session_id, job_type)
                                # Look for sqlite_db files in the job output directory
                                # CRITICAL: Check embedding_space.db FIRST (that's what we actually create)
                                # Then fall back to data.db, but validate file size (not empty)
                                possible_db_names = ['embedding_space.db', 'data.db']
                                sqlite_db_path = None
                                for db_name in possible_db_names:
                                    candidate_path = job_dir / db_name
                                    if candidate_path.exists():
                                        # CRITICAL: Validate file is not empty
                                        file_size = candidate_path.stat().st_size
                                        if file_size == 0:
                                            logger.warning(f"      ⚠️  Found {db_name} but it's 0 bytes - skipping (empty file)")
                                            continue
                                        
                                        sqlite_db_path = str(candidate_path.resolve())
                                        logger.info(f"      ✅ Found sqlite_db in job output directory: {sqlite_db_path} ({file_size / 1024 / 1024:.2f} MB)")
                                        # Update session with the found path
                                        refresh_lock()  # Refresh before save
                                        session['sqlite_db'] = sqlite_db_path
                                        save_session(session_id, session, exist_ok=True)
                                        logger.info(f"      ✅ Updated session with recovered sqlite_db path")
                                        job_has_output = True
                                        continue  # Treat as complete now
                                
                                if not sqlite_db_path:
                                    # sqlite_db not found in job output - check if task is still active
                                    logger.warning(f"      ⚠️  create_structured_data has status {status_value} but no sqlite_db in session or job output")
                                    try:
                                        celery_task = app.AsyncResult(existing_job_id)
                                        task_state = celery_task.state
                                        
                                        # Check if task is actually active (running, reserved, or scheduled)
                                        is_active = False
                                        if task_state in ['STARTED', 'PROGRESS']:
                                            is_active = True
                                        elif task_state == 'PENDING':
                                            # Check if it's in active/reserved/scheduled queues
                                            try:
                                                inspect = app.control.inspect(timeout=1.0)
                                                active_tasks = inspect.active() or {}
                                                reserved_tasks = inspect.reserved() or {}
                                                scheduled_tasks = inspect.scheduled() or {}
                                                
                                                for worker_tasks in [active_tasks, reserved_tasks, scheduled_tasks]:
                                                    for worker_name, tasks in worker_tasks.items():
                                                        for task in tasks:
                                                            if task.get('id') == existing_job_id:
                                                                is_active = True
                                                                break
                                                        if is_active:
                                                            break
                                                    if is_active:
                                                        break
                                            except Exception as inspect_err:
                                                logger.warning(f"      ⚠️  Could not inspect Celery queues: {inspect_err}")
                                                # If we can't check, assume active to avoid false positives
                                                is_active = True
                                        
                                        if not is_active:
                                            # Task is not active and no sqlite_db - job is stuck/failed
                                            logger.warning(f"      ⚠️  Task {existing_job_id} is not active (state: {task_state}) and no sqlite_db found")
                                            logger.warning(f"         Job appears stuck/failed - clearing job_id to re-dispatch")
                                            refresh_lock()  # Refresh before save
                                            job_plan[idx]['job_id'] = None
                                            session['job_plan'] = job_plan
                                            save_session(session_id, session, exist_ok=True)
                                            logger.info(f"      ✅ Cleared stuck job_id, will re-dispatch below")
                                            existing_job_id = None
                                            # Fall through to dispatch logic (don't continue)
                                        else:
                                            # Task is still active - wait for it to complete
                                            logger.info(f"      Task is active (state: {task_state}) - waiting for completion")
                                            continue
                                    except Exception as celery_check_err:
                                        logger.warning(f"      ⚠️  Could not check Celery task status: {celery_check_err}")
                                        # If we can't check, assume it's running to avoid false positives
                                        logger.info(f"      Job is {status_value} - skipping (cannot verify task status)")
                                        continue
                            except Exception as recovery_err:
                                logger.warning(f"      ⚠️  Could not recover sqlite_db from job output: {recovery_err}")
                                # Fall through to JOB_ACK check below
                        
                        # Check for JOB_ACK to detect truly stuck jobs
                        # Skip if we already cleared existing_job_id (job is stuck/failed)
                        if existing_job_id is None:
                            # Job was already determined to be stuck - fall through to dispatch
                            pass
                        else:
                            from lib.job_manager import get_job_output_path
                            try:
                                job_dir = get_job_output_path(existing_job_id, session_id, job_type)
                                job_ack = job_dir / "JOB_ACK"
                                
                                if not job_ack.exists() and not job_dir.exists():
                                    logger.warning(f"      ⚠️  Job has status {status_value} but NO JOB_ACK and NO job directory!")
                                    logger.warning(f"         Task was dispatched but worker never started")
                                    logger.warning(f"         Job is STUCK - clearing job_id to re-dispatch")
                                    refresh_lock()  # Refresh before save
                                    job_plan[idx]['job_id'] = None
                                    session['job_plan'] = job_plan
                                    save_session(session_id, session, exist_ok=True)
                                    logger.info(f"      ✅ Cleared stuck job_id, will re-dispatch below")
                                    # Update existing_job_id so dispatch logic below works
                                    existing_job_id = None
                                    # Fall through to dispatch logic (don't continue)
                                else:
                                    logger.info(f"      Job is {status_value} with JOB_ACK or job_dir - skipping (started/running)")
                                    continue
                            except Exception as ack_check_err:
                                logger.warning(f"      ⚠️  Could not check JOB_ACK: {ack_check_err}")
                                logger.info(f"      Job is {status_value} - skipping (already dispatched/running)")
                                continue
                    else:
                        logger.info(f"      Job status is {status_value} - skipping (has job_id)")
                        continue  # Already has a job_id and it exists
                else:
                    # Job ID exists but job not in Redis - might be a Celery task ID that hasn't been saved yet
                    # Or it might be a completed job that was cleaned up from Redis
                    # Or it might be a stuck PENDING task that was dispatched but never started
                    # Check if this is the completed_job_type - if so, it's safe to skip
                    if completed_job_type and job_type == completed_job_type:
                        logger.info(f"   ⏭️  Job {idx} ({job_type}) matches completed job type - skipping (just completed)")
                        continue
                    
                    # CRITICAL: Check if this is a stuck PENDING Celery task
                    # If task is PENDING and has no JOB_ACK, it's stuck and should be retried
                    try:
                        # Use module-level app (already imported at top of file)
                        celery_task = app.AsyncResult(existing_job_id)
                        task_state = celery_task.state
                        
                        if task_state == 'PENDING':
                            # Task is PENDING - check if it's actually stuck (no JOB_ACK, no job directory)
                            from lib.job_manager import get_job_output_path
                            try:
                                job_dir = get_job_output_path(existing_job_id, session_id, job_type)
                                job_ack = job_dir / "JOB_ACK"
                                
                                if not job_ack.exists() and not job_dir.exists():
                                    logger.warning(f"   ⚠️  Job {idx} ({job_type}) has PENDING Celery task but NO JOB_ACK and NO job directory!")
                                    logger.warning(f"      Task ID: {existing_job_id}")
                                    logger.warning(f"      Task was dispatched but worker never started - job is STUCK")
                                    logger.warning(f"      Clearing job_id to re-dispatch...")
                                    refresh_lock()  # Refresh before save
                                    job_plan[idx]['job_id'] = None
                                    session['job_plan'] = job_plan
                                    save_session(session_id, session, exist_ok=True)
                                    logger.info(f"   ✅ Cleared stuck PENDING job_id, will re-dispatch below")
                                    # Revoke the stuck Celery task
                                    try:
                                        app.control.revoke(existing_job_id, terminate=False)
                                        logger.info(f"   ✅ Revoked stuck Celery task {existing_job_id}")
                                    except Exception as revoke_err:
                                        logger.warning(f"   ⚠️  Could not revoke Celery task: {revoke_err}")
                                    # Update existing_job_id so dispatch logic below works
                                    existing_job_id = None
                                    # Fall through to dispatch logic (don't continue)
                                else:
                                    logger.info(f"   ⏭️  Job {idx} ({job_type}) has PENDING task but JOB_ACK or job_dir exists - task may be starting")
                                    logger.info(f"      Task ID: {existing_job_id}, State: {task_state}")
                                    continue
                            except Exception as stuck_check_err:
                                logger.warning(f"   ⚠️  Could not check if PENDING task is stuck: {stuck_check_err}")
                                logger.info(f"   ⏭️  Job {idx} ({job_type}) has job_id but not in Redis - assuming valid and skipping")
                                continue
                        else:
                            logger.info(f"   ⏭️  Job {idx} ({job_type}) has job_id but not in Redis, Celery state: {task_state}")
                            logger.info(f"      Task ID: {existing_job_id}")
                            continue
                    except Exception as celery_check_err:
                        logger.warning(f"   ⚠️  Could not check Celery task state: {celery_check_err}")
                        logger.info(f"   ⏭️  Job {idx} ({job_type}) already has job_id: {existing_job_id}, skipping (not in Redis but has job_id)")
                        continue  # Already has a job_id
            
            logger.info(f"   ✅ Found job {idx} ({job_type}) without job_id - will attempt to dispatch")
            
            # CRITICAL: Skip if this is the job that just completed (even if job_id was cleared)
            if completed_job_type and job_type == completed_job_type:
                logger.info(f"   ⏭️  Job {idx} ({job_type}) matches completed job type - skipping (just completed)")
                continue
            
            # CRITICAL: Check if there's already a job of this type running/dispatched for this session
            # This prevents duplicate dispatches when multiple jobs complete simultaneously
            # (e.g., train_es and run_clustering both trying to dispatch train_knn)
            duplicate_job_found = False
            
            # First, check job_plan for other jobs of the same type
            for other_idx, other_job_desc in enumerate(job_plan):
                if other_idx == idx:
                    continue  # Skip self
                other_job_type = other_job_desc.get("job_type")
                other_job_id = other_job_desc.get("job_id")
                
                if other_job_type == job_type and other_job_id and other_job_id != "None" and other_job_id != "skipped-foundation-model":
                    # Found another job of the same type with a job_id - check if it's still active
                    other_job_data = load_job(other_job_id)
                    if other_job_data:
                        other_job_status = other_job_data.get('status')
                        if isinstance(other_job_status, JobStatus):
                            other_status_value = other_job_status.value
                        else:
                            other_status_value = str(other_job_status) if other_job_status else 'unknown'
                        
                        if other_status_value in [JobStatus.RUNNING.value, JobStatus.READY.value]:
                            logger.info(f"   ⏭️  Job {idx} ({job_type}) already has a duplicate job {other_idx} running/dispatched (job_id: {other_job_id}, status: {other_status_value})")
                            logger.info(f"      Skipping dispatch to avoid duplicate - will wait for existing job to complete")
                            duplicate_job_found = True
                            break
                        elif other_status_value == JobStatus.DONE.value:
                            # Other job is done - check if it has output
                            if job_type == 'train_knn' and session.get('vector_db'):
                                logger.info(f"   ⏭️  Another {job_type} job already completed and has output - skipping")
                                duplicate_job_found = True
                                break
                    else:
                        # Job ID exists but not in Redis - might be a Celery task ID
                        try:
                            celery_task = app.AsyncResult(other_job_id)
                            task_state = celery_task.state
                            if task_state in ['PENDING', 'STARTED', 'PROGRESS']:
                                logger.info(f"   ⏭️  Job {idx} ({job_type}) already has a duplicate job {other_idx} in Celery (job_id: {other_job_id}, state: {task_state})")
                                logger.info(f"      Skipping dispatch to avoid duplicate - will wait for existing job to complete")
                                duplicate_job_found = True
                                break
                        except Exception:
                            pass  # Can't check Celery state - assume it's not active
            
            # Also check Redis for any active jobs of this type for this session
            # This catches jobs that were dispatched but session hasn't been updated yet
            if not duplicate_job_found:
                try:
                    from lib.job_manager import get_session_jobs
                    session_jobs = get_session_jobs(session_id)
                    for session_job in session_jobs:
                        session_job_type = session_job.get('job_type')
                        session_job_id = session_job.get('celery_task_id') or session_job.get('job_id')
                        session_job_status = session_job.get('status')
                        
                        if session_job_type == job_type:
                            if isinstance(session_job_status, JobStatus):
                                session_status_value = session_job_status.value
                            else:
                                session_status_value = str(session_job_status) if session_job_status else 'unknown'
                            
                            if session_status_value in [JobStatus.RUNNING.value, JobStatus.READY.value]:
                                logger.info(f"   ⏭️  Found active {job_type} job in Redis (job_id: {session_job_id}, status: {session_status_value})")
                                logger.info(f"      Skipping dispatch to avoid duplicate - will wait for existing job to complete")
                                duplicate_job_found = True
                                break
                            # Also check Celery state for jobs that might not be in Redis yet
                            elif session_job_id:
                                try:
                                    celery_task = app.AsyncResult(session_job_id)
                                    task_state = celery_task.state
                                    if task_state in ['PENDING', 'STARTED', 'PROGRESS']:
                                        logger.info(f"   ⏭️  Found active {job_type} job in Celery (job_id: {session_job_id}, state: {task_state})")
                                        logger.info(f"      Skipping dispatch to avoid duplicate - will wait for existing job to complete")
                                        duplicate_job_found = True
                                        break
                                except Exception:
                                    pass  # Can't check Celery state
                except Exception as redis_check_err:
                    logger.warning(f"   ⚠️  Could not check Redis for duplicate jobs: {redis_check_err}")
                    # Continue anyway - the job_plan check above should catch most cases
            
            if duplicate_job_found:
                continue  # Skip this job - there's already one running
            
            # CRITICAL: For predictor sessions, train_single_predictor MUST be dispatched after create_structured_data
            if completed_job_type == 'create_structured_data' and job_type == 'train_single_predictor':
                session_type = session.get('session_type', 'unknown')
                logger.info(f"   🎯 CRITICAL: Found train_single_predictor job after create_structured_data completion")
                logger.info(f"      Session type: {session_type}")
                logger.info(f"      This job MUST be dispatched - proceeding with dispatch...")
            
            # Skip train_es if embedding space already exists
            if job_type == "train_es":
                embedding_space_path = session.get("embedding_space")
                foundation_model_id = session.get("foundation_model_id")
                if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                    logger.info(f"⏭️  Skipping train_es - embedding space already exists")
                    refresh_lock()  # Refresh before save
                    job_plan[idx]["job_id"] = "skipped-foundation-model"
                    save_session(session_id, session, exist_ok=True)
                    continue
            
            # Skip train_knn if vector_db already exists
            if job_type == "train_knn":
                vector_db_path = session.get("vector_db")
                if vector_db_path and Path(vector_db_path).exists():
                    logger.info(f"⏭️  Skipping train_knn - vector_db already exists")
                    refresh_lock()  # Refresh before save
                    job_plan[idx]["job_id"] = "skipped-foundation-model"
                    save_session(session_id, session, exist_ok=True)
                    continue
            
            # CRITICAL: pre_analysis_architecture requires sqlite_db from create_structured_data
            # Don't dispatch it until create_structured_data has completed and sqlite_db exists
            if job_type == "pre_analysis_architecture":
                # First check if create_structured_data exists in job_plan and its status
                create_structured_data_completed = False
                for check_idx, check_job_desc in enumerate(job_plan):
                    if check_job_desc.get("job_type") == "create_structured_data":
                        create_structured_data_job_id = check_job_desc.get("job_id")
                        if create_structured_data_job_id and create_structured_data_job_id != "None":
                            # Check if this job is done
                            create_job_data = load_job(create_structured_data_job_id)
                            if create_job_data:
                                create_job_status = create_job_data.get('status')
                                if isinstance(create_job_status, JobStatus):
                                    create_status_value = create_job_status.value
                                else:
                                    create_status_value = str(create_job_status) if create_job_status else 'unknown'
                                
                                if create_status_value == JobStatus.DONE.value:
                                    create_structured_data_completed = True
                                    logger.info(f"   ✅ create_structured_data is DONE (status: {create_status_value})")
                                elif create_status_value in [JobStatus.RUNNING.value, JobStatus.READY.value]:
                                    logger.info(f"⏭️  Skipping pre_analysis_architecture - create_structured_data is still running (status: {create_status_value})")
                                    logger.info(f"   Will wait for create_structured_data to complete before dispatching pre_analysis_architecture")
                                    continue  # Skip this job - dependency still running
                        else:
                            # create_structured_data hasn't been dispatched yet - must wait
                            logger.info(f"⏭️  Skipping pre_analysis_architecture - create_structured_data hasn't been dispatched yet")
                            logger.info(f"   create_structured_data job_id: {create_structured_data_job_id}")
                            logger.info(f"   Will wait for create_structured_data to be dispatched and complete first")
                            continue  # Skip this job - dependency not even started yet
                
                # Also check if sqlite_db exists (definitive check - only exists after create_structured_data completes)
                sqlite_db_path = session.get("sqlite_db")
                if not sqlite_db_path or not Path(sqlite_db_path).exists():
                    logger.info(f"⏭️  Skipping pre_analysis_architecture - sqlite_db not available yet (create_structured_data must complete first)")
                    logger.info(f"   sqlite_db in session: {sqlite_db_path}")
                    logger.info(f"   Will wait for create_structured_data to complete before dispatching pre_analysis_architecture")
                    continue  # Skip this job - dependencies not met yet
            
            # CRITICAL: run_clustering requires embedding_space from train_es
            # Don't dispatch it until train_es has completed and embedding_space exists
            if job_type == "run_clustering":
                # First check if run_clustering already completed (has projections output)
                projections_path = session.get("projections")
                preview_png_path = session.get("preview_png")
                if (projections_path and Path(projections_path).exists()) or \
                   (preview_png_path and Path(preview_png_path).exists()):
                    logger.info(f"⏭️  Skipping run_clustering - already completed (projections/preview_png exist)")
                    refresh_lock()  # Refresh before save
                    job_plan[idx]["job_id"] = "skipped-already-completed"
                    save_session(session_id, session, exist_ok=True)
                    continue
                
                # Check if embedding_space exists (dependency check)
                embedding_space_path = session.get("embedding_space")
                if not embedding_space_path or not Path(embedding_space_path).exists():
                    logger.info(f"⏭️  Skipping run_clustering - embedding_space not available yet (train_es must complete first)")
                    logger.info(f"   embedding_space in session: {embedding_space_path}")
                    logger.info(f"   Will wait for train_es to complete before dispatching run_clustering")
                    continue  # Skip this job - dependencies not met yet
            
            # CRITICAL: Store job info and RELEASE LOCK before expensive operations
            job_to_dispatch = {
                'idx': idx,
                'job_type': job_type,
                'job_spec': job_spec,
                'session': session,  # Copy session data we need
            }
            job_idx = idx
            break  # Found the job to dispatch - exit loop
        
        # RELEASE LOCK - we've found the job to dispatch, now do expensive operations without lock
        if lock_acquired:
            try:
                redis_client.delete(dispatch_lock_key)
                logger.debug(f"🔓 Released dispatch lock (doing expensive operations without lock)")
                lock_acquired = False
            except Exception as unlock_err:
                logger.warning(f"⚠️  Failed to release lock: {unlock_err}")
        
        # If no job found, we're done
        if not job_to_dispatch:
            logger.info(f"✅ No jobs to dispatch - all jobs have job_ids or were skipped")
            return None
        
        # Now do all expensive operations WITHOUT the lock
        job_type = job_to_dispatch['job_type']
        job_spec = job_to_dispatch['job_spec']
        idx = job_to_dispatch['idx']
        
        # Dispatch will use Celery's auto-generated task ID as the job_id
        # The Celery task will use self.request.id to get its own task ID
        logger.info(f"   🚀 Dispatching job {idx} ({job_type}) - Celery will auto-generate task ID")
        
        # Get data_file for create_structured_data
        data_file = None
        if job_type == 'create_structured_data':
            input_data = job_to_dispatch['session'].get('input_data')
            logger.info(f"   Getting data_file for create_structured_data:")
            logger.info(f"      input_data: {input_data}")
            if input_data and not input_data.startswith('s3://'):
                input_path = Path(input_data)
                if input_path.is_absolute():
                    data_file = input_path
                else:
                    data_file = config.data_dir / input_data
                logger.info(f"      data_file: {data_file}")
            else:
                logger.info(f"      No local input_data found (may be S3)")
        
        # Get data_file for train_es (before dispatch)
        if job_type == 'train_es' and not data_file:
            sqlite_db = job_to_dispatch['session'].get('sqlite_db')
            logger.info(f"   Getting data_file for train_es:")
            logger.info(f"      sqlite_db from session: {sqlite_db}")
            data_file = sqlite_db
            if data_file:
                logger.info(f"      data_file: {data_file}")
                path_exists = Path(data_file).exists() if data_file else False
                logger.info(f"      data_file exists: {path_exists}")
            else:
                logger.warning(f"      ⚠️  No sqlite_db in session - train_es may fail!")
        
        # Dispatch job
        logger.info(f"   🚀 Dispatching job {job_type} to Celery...")

        # GUARD: Check Celery worker availability before dispatching (non-blocking check)
        target_queue = None
        if job_type in ('create_structured_data', 'train_knn', 'run_clustering'):
            target_queue = 'cpu_worker'
        elif job_type in ('train_es', 'train_single_predictor'):
            target_queue = 'gpu_training'

        if target_queue:
                try:
                    # Quick check if any workers are listening to this queue (with timeout)
                    inspect = app.control.inspect(timeout=0.5)  # Very short timeout
                    active_workers = inspect.active_queues() or {}
                    workers_for_queue = []
                    for worker_name, queues in active_workers.items():
                        for queue_info in queues:
                            if queue_info.get('name') == target_queue:
                                workers_for_queue.append(worker_name)
                                break

                    if workers_for_queue:
                        logger.info(f"   ✅ Found {len(workers_for_queue)} worker(s) listening to queue '{target_queue}': {workers_for_queue}")
                    else:
                        logger.error(f"   ❌ NO WORKERS listening to queue '{target_queue}'")
                        logger.error(f"   Available workers: {list(active_workers.keys())}")
                        
                        # AUTO-RESTART: Try to start the workers via supervisorctl
                        logger.info(f"   🔧 Attempting to auto-restart workers...")
                        
                        # Map queue to supervisor service names
                        supervisor_services = []
                        if target_queue == 'cpu_worker':
                            supervisor_services = ['cpu']
                        elif target_queue == 'gpu_training':
                            supervisor_services = ['gpu']
                        
                        workers_restarted = False
                        if supervisor_services:
                            try:
                                import subprocess
                                # Try to start the workers
                                cmd = ['supervisorctl', 'start'] + supervisor_services
                                logger.info(f"   Running: {' '.join(cmd)}")
                                result = subprocess.run(
                                    cmd,
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                
                                if result.returncode == 0:
                                    logger.info(f"   ✅ Successfully started workers: {', '.join(supervisor_services)}")
                                    logger.info(f"   Output: {result.stdout.strip()}")
                                    
                                    # Wait a moment for workers to register with broker
                                    logger.info(f"   ⏳ Waiting 3 seconds for workers to register...")
                                    # Lock already released - no need to refresh
                                    time.sleep(3)
                                    
                                    # Re-check if workers are now available
                                    inspect2 = app.control.inspect(timeout=0.5)
                                    active_workers2 = inspect2.active_queues() or {}
                                    workers_for_queue2 = []
                                    for worker_name, queues in active_workers2.items():
                                        for queue_info in queues:
                                            if queue_info.get('name') == target_queue:
                                                workers_for_queue2.append(worker_name)
                                                break
                                    
                                    if workers_for_queue2:
                                        logger.info(f"   ✅ Workers now available: {workers_for_queue2}")
                                        workers_restarted = True
                                    else:
                                        logger.warning(f"   ⚠️  Workers started but not yet registered with queue '{target_queue}'")
                                        logger.warning(f"   Job will be queued and picked up when workers are ready")
                                        workers_restarted = True  # Continue anyway - workers should pick up job
                                else:
                                    logger.error(f"   ❌ Failed to start workers (exit code {result.returncode})")
                                    logger.error(f"   stdout: {result.stdout.strip()}")
                                    logger.error(f"   stderr: {result.stderr.strip()}")
                            except subprocess.TimeoutExpired:
                                logger.error(f"   ❌ supervisorctl start timed out after 10s")
                            except FileNotFoundError:
                                logger.error(f"   ❌ supervisorctl command not found")
                            except Exception as restart_err:
                                logger.error(f"   ❌ Error restarting workers: {restart_err}")
                        
                        if not workers_restarted:
                            logger.error(f"   ❌ CRITICAL: Workers could not be auto-restarted")
                            logger.error(f"   Manual intervention required:")
                            logger.error(f"      supervisorctl start {' '.join(supervisor_services)}")
                            logger.error(f"   Job will be queued in Redis but will NOT execute until workers are available")
                            # DON'T raise - let the job queue in Redis, it won't be lost
                            logger.warning(f"   ⚠️  Queueing job anyway - it will execute when workers start")
                        
                except Exception as inspect_err:
                    # Non-critical - continue with dispatch even if inspection fails
                    logger.warning(f"   ⚠️  Could not check worker availability (non-critical): {inspect_err}")
                    logger.warning(f"   Error type: {type(inspect_err).__name__}")
                    logger.debug(f"   Traceback: {traceback.format_exc()}")
                    logger.debug(f"   Continuing with dispatch - send_task will verify connection")

        try:
            # Skip broker connection verification - send_task will fail fast if Redis is down
            # This avoids the slow ensure_connection retry logic
            logger.debug(f"   🔌 Sending task to Celery (connection will be verified on send)...")
            
            # Send task to Celery (pass None as job_id, tasks will use self.request.id)
            if job_type == 'create_structured_data':
                task = app.send_task(
                    'celery_app.create_structured_data',
                    args=[job_spec, None, str(data_file) if data_file else None, session_id],
                    queue='cpu_worker'
                )
            elif job_type == 'pre_analysis_architecture':
                # CRITICAL: pre_analysis_architecture requires sqlite_db from create_structured_data
                # Wait for it if missing (handles race condition where dispatch happens before session update)
                data_file = data_file or job_to_dispatch['session'].get('sqlite_db')
                temp_session = None
                if not data_file:
                    logger.warning(f"   ⚠️  sqlite_db not found in session - waiting for create_structured_data to complete...")
                    max_wait_attempts = 6  # 6 attempts = up to 30 seconds
                    wait_sleep = 5  # 5 seconds between attempts
                    for wait_attempt in range(max_wait_attempts):
                        if wait_attempt > 0:
                            logger.info(f"   ⏳ Waiting for sqlite_db... (attempt {wait_attempt + 1}/{max_wait_attempts})")
                            # Lock already released - no need to refresh
                            time.sleep(wait_sleep)
                        
                        # Reload session to get latest sqlite_db (lock already released)
                        temp_session = load_session(session_id)
                        data_file = temp_session.get('sqlite_db')
                        if data_file:
                            logger.info(f"   ✅ Found sqlite_db after {wait_attempt * wait_sleep}s: {data_file}")
                            break
                    
                    if not data_file:
                        error_msg = f"Cannot dispatch pre_analysis_architecture: session {session_id} has no sqlite_db after {max_wait_attempts * wait_sleep}s. create_structured_data may have failed or not completed yet."
                        logger.error(f"   ❌ CRITICAL: {error_msg}")
                        raise ValueError(error_msg)
                
                # Use temp_session if we loaded it, otherwise use the original session from job_to_dispatch
                if temp_session:
                    strings_cache = temp_session.get('strings_cache', '')
                else:
                    strings_cache = job_to_dispatch['session'].get('strings_cache', '')
                logger.info(f"   📋 pre_analysis_architecture parameters:")
                logger.info(f"      data_file: {data_file}")
                logger.info(f"   📤 Sending pre_analysis_architecture task to cpu_worker queue...")
                task = app.send_task(
                    'celery_app.pre_analysis_architecture',
                    args=[job_spec, None, session_id, str(data_file) if data_file else None, strings_cache],
                    queue='cpu_worker'  # CPU queue - quick search doesn't need GPU
                )
                logger.info(f"   ✅ pre_analysis_architecture task sent (task.id: {task.id})")
            elif job_type == 'train_es':
                data_file = data_file or job_to_dispatch['session'].get('sqlite_db')
                strings_cache = job_to_dispatch['session'].get('strings_cache', '')
                logger.info(f"   📋 train_es parameters:")
                logger.info(f"      data_file: {data_file}")
                if not data_file:
                    logger.error(f"   ❌ CRITICAL: No data_file or sqlite_db for train_es!")
                    logger.error(f"      Session sqlite_db: {job_to_dispatch['session'].get('sqlite_db')}")
                    logger.error(f"      This will cause train_es to fail!")
                logger.info(f"   📤 Sending train_es task to gpu_training queue...")
                # Pass None as job_id - the Celery task will use self.request.id
                task = app.send_task(
                    'celery_app.train_es',
                    args=[job_spec, None, session_id, str(data_file) if data_file else None, strings_cache],
                    queue='gpu_training'
                )
                logger.info(f"   ✅ train_es task sent (task.id: {task.id})")
            elif job_type == 'train_knn':
                if 'model_path' not in job_spec:
                    job_spec['model_path'] = job_to_dispatch['session'].get('embedding_space')
                if 'sqlite_db_path' not in job_spec:
                    job_spec['sqlite_db_path'] = job_to_dispatch['session'].get('sqlite_db')
                if 'strings_cache' not in job_spec:
                    job_spec['strings_cache'] = job_to_dispatch['session'].get('strings_cache')
                logger.info(f"   📤 Sending train_knn task to cpu_worker queue...")
                task = app.send_task(
                    'celery_app.train_knn',
                    args=[job_spec, None, session_id],
                    queue='cpu_worker'
                )
                logger.info(f"   ✅ train_knn task sent (task.id: {task.id})")
            elif job_type == 'train_single_predictor':
                logger.info(f"   🎯 CRITICAL: Dispatching train_single_predictor job")
                logger.info(f"      Session ID: {session_id}")
                logger.info(f"      Job spec keys: {list(job_spec.keys())}")
                logger.info(f"      Target column: {job_spec.get('target_column', 'unknown')}")
                logger.info(f"      Sending to gpu_training queue...")
                
                # CRITICAL: Verify embedding space exists before dispatching
                embedding_space_path = job_to_dispatch['session'].get('embedding_space')
                if not embedding_space_path:
                    # Try to get it from the session we just loaded
                    current_session = load_session(session_id)
                    embedding_space_path = current_session.get('embedding_space')
                
                if embedding_space_path and Path(embedding_space_path).exists():
                    logger.info(f"      ✅ Embedding space verified: {embedding_space_path}")
                else:
                    logger.warning(f"      ⚠️  Embedding space not found: {embedding_space_path}")
                    logger.warning(f"         Job will fail if ES is not ready, but dispatching anyway...")
                
                try:
                    task = app.send_task(
                        'celery_app.train_single_predictor',
                        args=[job_spec, None, session_id],
                        queue='gpu_training'
                    )
                    logger.info(f"   ✅ train_single_predictor task sent (task.id: {task.id})")
                    
                except Exception as dispatch_err:
                    logger.error(f"   ❌ CRITICAL: Failed to dispatch train_single_predictor task: {dispatch_err}")
                    logger.error(f"      Traceback: {traceback.format_exc()}")
                    raise RuntimeError(f"Failed to dispatch train_single_predictor task: {dispatch_err}") from dispatch_err
            elif job_type == 'run_clustering':
                clustering_job_spec = {
                    'model_path': job_to_dispatch['session'].get('embedding_space'),
                    'sqlite_db': job_to_dispatch['session'].get('sqlite_db'),
                    'strings_cache': job_to_dispatch['session'].get('strings_cache'),
                    'session_id': session_id
                }
                logger.info(f"   📤 Sending run_clustering task to cpu_worker queue...")
                task = app.send_task(
                    'celery_app.run_clustering',
                    args=[clustering_job_spec],
                    queue='cpu_worker'
                )
                logger.info(f"   ✅ run_clustering task sent (task.id: {task.id})")
                
                # CRITICAL: Update job_spec with job_id so run_clustering can update status
                # Note: This updates the local dict, but the task already received the original
                # The task will use self.request.id as fallback, which equals task.id
                clustering_job_spec['job_id'] = task.id
                # Also update the job_spec that will be saved to Redis
                job_spec = clustering_job_spec
            else:
                logger.warning(f"⚠️  Unknown job_type {job_type}, skipping")
                return None
            
            # Skip task state verification - accessing task.state can be slow
            # send_task() will raise an exception if Redis is down, so we'll catch that
            # The task will be queued or fail fast - no need to verify state synchronously
            logger.info(f"✅ Task {task.id} sent to Celery queue '{target_queue if 'target_queue' in locals() else 'unknown'}'")
            
            # Check if there are other jobs in this queue
            if target_queue:
                try:
                    # Check how many jobs are in the queue
                    inspect = app.control.inspect(timeout=0.5)
                    reserved_tasks = inspect.reserved() or {}
                    active_tasks = inspect.active() or {}
                    
                    # Count tasks in this specific queue
                    queue_reserved_count = 0
                    queue_active_count = 0
                    
                    for worker_name, tasks in reserved_tasks.items():
                        if target_queue in worker_name or any(t.get('delivery_info', {}).get('routing_key') == target_queue for t in tasks):
                            queue_reserved_count += len(tasks)
                    
                    for worker_name, tasks in active_tasks.items():
                        if target_queue in worker_name or any(t.get('delivery_info', {}).get('routing_key') == target_queue for t in tasks):
                            queue_active_count += len(tasks)
                    
                    total_queued = queue_reserved_count + queue_active_count
                    
                    if queue_active_count > 0:
                        logger.info(f"   ⏳ QUEUE STATUS: {queue_active_count} job(s) currently RUNNING in '{target_queue}' queue")
                        logger.info(f"      → This job will WAIT until the running job(s) complete")
                        if queue_reserved_count > 0:
                            logger.info(f"      → Plus {queue_reserved_count} job(s) already waiting in queue")
                            logger.info(f"      → Your job position: #{total_queued + 1} in queue")
                    elif queue_reserved_count > 0:
                        logger.info(f"   ⏳ QUEUE STATUS: {queue_reserved_count} job(s) waiting in '{target_queue}' queue")
                        logger.info(f"      → Your job position: #{queue_reserved_count + 1} in queue")
                    else:
                        logger.info(f"   ✅ QUEUE STATUS: No other jobs in '{target_queue}' queue - will start immediately")
                except Exception as queue_check_err:
                    logger.debug(f"   (Could not check queue status: {queue_check_err})")
            
            # CRITICAL: Save job to Redis FIRST before updating session
            # This ensures we don't leave orphaned job_ids in session if Redis save fails
            logger.info(f"   🔄 Saving job {task.id} to Redis...")
            redis_save_success = False
            try:
                save_job(
                    job_id=task.id,  # Use Celery task ID, NOT placeholder UUID
                    job_data={
                        'status': JobStatus.READY,
                        'created_at': datetime.now(tz=ZoneInfo("America/New_York")),
                        'job_spec': job_spec,
                        'celery_task_id': task.id,  # Store Celery task ID explicitly
                    },
                    session_id=session_id,
                    job_type=job_type
                )
                # Verify job was actually saved to Redis
                saved_job = load_job(task.id)
                if saved_job:
                    redis_save_success = True
                    logger.info(f"   ✅ Job {task.id} saved to Redis and verified")
                else:
                    logger.error(f"   ❌ CRITICAL: Job {task.id} NOT found in Redis after save")
                    logger.error(f"      save_job() succeeded but load_job() returned None")
            except Exception as redis_err:
                logger.error(f"   ❌ CRITICAL: Failed to save job {task.id} to Redis: {redis_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # CRITICAL: If Redis save failed, cleanup and raise BEFORE updating session
            if not redis_save_success:
                logger.error(f"   🔄 Attempting to clean up failed dispatch...")
                try:
                    # Revoke the Celery task
                    app.control.revoke(task.id, terminate=True)
                    logger.info(f"   ✅ Revoked Celery task {task.id}")
                except Exception as cleanup_err:
                    logger.error(f"   ❌ Cleanup failed: {cleanup_err}")
                
                raise RuntimeError(f"Job {task.id} ({job_type}) dispatched but failed to save to Redis")
            
            # ONLY update session AFTER Redis save succeeds
            # RE-ACQUIRE LOCK for the critical section (updating session)
            logger.info(f"   🔄 Re-acquiring lock to update session with job_id...")
            lock_acquire_start = time.time()
            lock_acquired = redis_client.set(dispatch_lock_key, str(time.time()), nx=True, ex=lock_ttl)
            
            if not lock_acquired:
                # Try to wait for lock (but don't wait too long)
                elapsed = 0.0
                while elapsed < 5.0:  # 5 second max wait
                    time.sleep(0.1)
                    elapsed = time.time() - lock_acquire_start
                    lock_acquired = redis_client.set(dispatch_lock_key, str(time.time()), nx=True, ex=lock_ttl)
                    if lock_acquired:
                        break
            
            if not lock_acquired:
                logger.error(f"   ❌ Failed to re-acquire lock to save session - job dispatched but session not updated!")
                logger.error(f"   Job {task.id} is running but session won't have job_id")
                raise RuntimeError(f"Failed to re-acquire lock to update session")
            
            # Reload session to get latest state (another process may have updated it)
            session = load_session(session_id)
            job_plan = session.get("job_plan", [])
            
            logger.info(f"   🔄 Setting job_id to Celery task ID {task.id} in session")
            logger.info(f"      Job index: {idx}, Job type: {job_type}")
            logger.info(f"      Current job_plan[{idx}] job_id before update: {job_plan[idx].get('job_id') if idx < len(job_plan) else 'N/A'}")
            logger.info(f"      Setting job_plan[{idx}]['job_id'] = {task.id}")
            
            # CRITICAL: Verify we're updating the correct job entry
            if idx >= len(job_plan) or job_plan[idx].get('job_type') != job_type:
                error_msg = f"CRITICAL BUG: Job type mismatch or index out of range! job_plan length: {len(job_plan)}, idx: {idx}, expected job_type: {job_type}"
                logger.error(f"   ❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            job_plan[idx]["job_id"] = task.id
            save_session(session_id, session, exist_ok=True)
            logger.info(f"   ✅ Updated job_id to Celery task ID {task.id} in session")
            logger.info(f"      Verified: job_plan[{idx}]['job_id'] = {job_plan[idx].get('job_id')}")
            logger.info(f"      Verified: job_plan[{idx}]['job_type'] = {job_plan[idx].get('job_type')}")
            
            dispatch_elapsed = time.time() - dispatch_start
            logger.info(f"🔵 [DISPATCH] ✅ Dispatched next job: {job_type} (task_id: {task.id}, after: {completed_job_type})")
            logger.info(f"🔵 [DISPATCH] Dispatch completed in {dispatch_elapsed:.3f} seconds")
            logger.info(f"{'='*80}\n")
            return task.id
            
        except Exception as e:
            logger.error(f"   ❌ FAILED to dispatch {job_type} job: {e}")
            logger.error(f"      Error type: {type(e).__name__}")
            logger.error(f"      Full traceback: {traceback.format_exc()}")
            # CRITICAL: Do NOT save job_id to session if dispatch failed
            # Remove the job_id we set earlier (re-acquire lock if needed)
            try:
                # Re-acquire lock if we don't have it
                if not lock_acquired:
                    lock_acquired = redis_client.set(dispatch_lock_key, str(time.time()), nx=True, ex=lock_ttl)
                    if lock_acquired:
                        session = load_session(session_id)
                        job_plan = session.get("job_plan", [])
                
                if lock_acquired and idx < len(job_plan) and job_plan[idx].get("job_id") == job_id:
                    job_plan[idx].pop("job_id", None)
                    save_session(session_id, session, exist_ok=True)
                    logger.info(f"   ✅ Removed job_id from session (dispatch failed)")
            except Exception as cleanup_err:
                logger.error(f"   ❌ Failed to cleanup job_id from session: {cleanup_err}")
                logger.error(f"      Error type: {type(cleanup_err).__name__}")
                logger.error(f"      Traceback: {traceback.format_exc()}")
            # This allows retry on next call
            return None
        
        # No more jobs to dispatch
        logger.info(f"🔵 [DISPATCH] ℹ️  No more jobs to dispatch for session {session_id}")
        logger.info(f"   Completed job type: {completed_job_type}")
        logger.info(f"   Job plan has {len(job_plan)} jobs")
        all_have_job_ids = True
        undispatchable_jobs = []
        for idx, job_desc in enumerate(job_plan):
            job_type = job_desc.get("job_type", "unknown")
            job_id = job_desc.get("job_id", "None")
            has_job_id = job_id and job_id != "None"
            if not has_job_id:
                all_have_job_ids = False
                # Check if this job was legitimately skipped
                is_skipped = False
                if job_type == "train_es":
                    embedding_space_path = session.get("embedding_space")
                    foundation_model_id = session.get("foundation_model_id")
                    if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                        is_skipped = True
                elif job_type == "train_knn":
                    vector_db_path = session.get("vector_db")
                    if vector_db_path and Path(vector_db_path).exists():
                        is_skipped = True
                elif job_type == completed_job_type:
                    is_skipped = True  # Just completed, skip it
                
                if not is_skipped:
                    undispatchable_jobs.append((idx, job_type))
                logger.info(f"     {idx}: {job_type} - NO JOB_ID (skipped: {is_skipped})")
            else:
                logger.info(f"     {idx}: {job_type} - job_id: {job_id}")
        
        if all_have_job_ids:
            logger.info(f"✅ All {len(job_plan)} jobs have been dispatched")
            logger.info(f"ℹ️  Session status will be computed dynamically from job statuses")
            # NOTE: Session status is NO LONGER STORED in session files
            # It's computed on-the-fly by compute_session_status() in session_manager.py
            # This eliminates sync bugs where job status != session status
            return None
        elif undispatchable_jobs:
            # CRITICAL: There are jobs that should have been dispatched but weren't
            error_msg = f"CRITICAL: Dispatch returned None but {len(undispatchable_jobs)} job(s) remain without job_ids and were not skipped: {undispatchable_jobs}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   This means dispatch failed to dispatch jobs that should have been dispatched!")
            logger.error(f"   Session: {session_id}")
            logger.error(f"   Completed job type: {completed_job_type}")
            raise RuntimeError(error_msg)
        else:
            # All remaining jobs were legitimately skipped
            logger.info(f"✅ All remaining jobs were legitimately skipped (foundation model exists, etc.)")
            return None
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Error in dispatch_next_job_in_chain: {e}")
        logger.error(f"   Full traceback: {traceback.format_exc()}")
        raise  # Re-raise to propagate error to caller
    finally:
        # Always release the Redis lock
        if lock_acquired:
            try:
                redis_client.delete(dispatch_lock_key)
                logger.debug(f"🔓 Released Redis dispatch lock")
            except Exception as unlock_err:
                logger.error(f"❌ CRITICAL: Error releasing Redis lock: {unlock_err}")
                logger.error(f"   Error type: {type(unlock_err).__name__}")
                logger.error(f"   Lock key: {dispatch_lock_key}")
                logger.error(f"   Traceback: {traceback.format_exc()}")


def create_job_chain_for_session(session_id: str) -> Optional[str]:
    """
    Create a Celery chain for all jobs in a session's job_plan.
    
    This replaces step_session by creating a chain that executes all jobs
    in sequence automatically.
    
    Args:
        session_id: Session ID to create chain for
        
    Returns:
        First task ID in the chain, or None if no jobs to run
    """
    session = load_session(session_id)
    
    # Check if session is already complete
    # Session status is computed dynamically, not stored
    # We can always create job chains regardless of computed status
    # Check if there are any jobs without job_ids that need to be dispatched
    job_plan = session.get("job_plan", [])
    jobs_without_ids = [j for j in job_plan if not j.get("job_id") or j.get("job_id") == "None"]
    if not jobs_without_ids:
        logger.info(f"Session {session_id} has no jobs without job_ids - skipping chain creation")
        return None
    
    job_plan = session.get("job_plan", [])
    if not job_plan:
        logger.info(f"Session {session_id} has no job_plan, skipping chain creation")
        return None
    
    # Build chain of tasks
    tasks = []
    job_ids = []
    
    for idx, job_desc in enumerate(job_plan):
        job_type = job_desc.get("job_type")
        job_spec = job_desc.get("spec", {})
        existing_job_id = job_desc.get("job_id")
        
        # Skip jobs that already have a job_id (already queued/completed)
        if existing_job_id:
            logger.info(f"⏭️  Skipping job {idx} ({job_type}) - already has job_id: {existing_job_id}")
            continue
        
        # Skip train_es if embedding space already exists
        if job_type == "train_es":
            embedding_space_path = session.get("embedding_space")
            foundation_model_id = session.get("foundation_model_id")
            if foundation_model_id or (embedding_space_path and Path(embedding_space_path).exists()):
                logger.info(f"⏭️  Skipping train_es - embedding space already exists")
                job_plan[idx]["job_id"] = "skipped-foundation-model"
                save_session(session_id, session, exist_ok=True)
                continue
        
        # Skip train_knn if vector_db already exists
        if job_type == "train_knn":
            vector_db_path = session.get("vector_db")
            if vector_db_path and Path(vector_db_path).exists():
                logger.info(f"⏭️  Skipping train_knn - vector_db already exists")
                job_plan[idx]["job_id"] = "skipped-foundation-model"
                save_session(session_id, session, exist_ok=True)
                continue
        
        # Generate job_id
        job_id = str(uuid4())
        job_ids.append((idx, job_id))
        
        # Get data_file for create_structured_data
        data_file = None
        if job_type == 'create_structured_data':
            input_data = session.get('input_data')
            if input_data and not input_data.startswith('s3://'):
                input_path = Path(input_data)
                if input_path.is_absolute():
                    data_file = input_path
                else:
                    data_file = config.data_dir / input_data
        
        # Create Celery task signature
        if job_type == 'create_structured_data':
            task = app.signature(
                'celery_app.create_structured_data',
                args=[job_spec, job_id, str(data_file) if data_file else None, session_id],
                queue='cpu_worker'
            )
        elif job_type == 'pre_analysis_architecture':
            # Get data_file and strings_cache from session
            data_file = data_file or session.get('sqlite_db')
            strings_cache = session.get('strings_cache', '')
            task = app.signature(
                'celery_app.pre_analysis_architecture',
                args=[job_spec, job_id, session_id, str(data_file) if data_file else None, strings_cache],
                queue='cpu_worker'
            )
        elif job_type == 'train_es':
            # Get data_file and strings_cache from session
            data_file = data_file or session.get('sqlite_db')
            strings_cache = session.get('strings_cache', '')
            task = app.signature(
                'celery_app.train_es',
                args=[job_spec, job_id, session_id, str(data_file) if data_file else None, strings_cache],
                queue='gpu_training'
            )
        elif job_type == 'train_knn':
            # Update job_spec with paths from session
            if 'model_path' not in job_spec:
                job_spec['model_path'] = session.get('embedding_space')
            if 'sqlite_db_path' not in job_spec:
                job_spec['sqlite_db_path'] = session.get('sqlite_db')
            if 'strings_cache' not in job_spec:
                job_spec['strings_cache'] = session.get('strings_cache')
            task = app.signature(
                'celery_app.train_knn',
                args=[job_spec, job_id, session_id],
                queue='cpu_worker'
            )
        elif job_type == 'train_single_predictor':
            task = app.signature(
                'celery_app.train_single_predictor',
                args=[job_spec, job_id, session_id],
                queue='gpu_training'
            )
        elif job_type == 'run_clustering':
            clustering_job_spec = {
                'model_path': session.get('embedding_space'),
                'sqlite_db': session.get('sqlite_db'),
                'strings_cache': session.get('strings_cache'),
                'session_id': session_id
            }
            task = app.signature(
                'celery_app.run_clustering',
                args=[clustering_job_spec],
                queue='cpu_worker'
            )
        else:
            logger.warning(f"⚠️  Unknown job_type {job_type}, skipping")
            continue
        
        tasks.append(task)
        logger.info(f"✅ Added {job_type} to chain (job_id: {job_id})")
    
    if not tasks:
        logger.info(f"No jobs to run for session {session_id}")
        return None
    
    # Create and execute chain
    chain_result = chain(*tasks).apply_async()
    first_task_id = chain_result.parent.id if hasattr(chain_result, 'parent') else chain_result.id
    
    # Update session with job_ids
    for idx, job_id in job_ids:
        job_plan[idx]["job_id"] = job_id
    save_session(session_id, session, exist_ok=True)
    
    logger.info(f"✅ Created Celery chain for session {session_id} with {len(tasks)} jobs (first task_id: {first_task_id})")
    return first_task_id
