"""
Unified Job Management Module

Handles Redis-based job operations and control file checking.
All jobs are stored in Redis.
"""
import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from zoneinfo import ZoneInfo

import redis

from config import config
from utils import convert_from_iso, convert_to_iso, clean_numpy_values

logger = logging.getLogger(__name__)


def determine_failure_reason(exception=None, exception_type=None, exception_msg=None, traceback_str=None, is_oom=False, is_disk_error=False, is_user_abort=False):
    """
    Determine failure reason string for a failed job.
    
    This function is designed to be backward-compatible:
    - Returns None if no information is available (field remains optional)
    - Handles None/empty values gracefully
    - Never raises exceptions
    
    Args:
        exception: Exception object (optional)
        exception_type: Exception type name (optional)
        exception_msg: Exception message (optional)
        traceback_str: Full traceback string (optional)
        is_oom: Whether this is an out-of-memory error
        is_disk_error: Whether this is a disk space error
        is_user_abort: Whether this is a user-initiated abort
        
    Returns:
        Failure reason string in format: "failed - <category> - <details>"
        Returns None if no information available (field remains optional)
    """
    # Handle explicit flags first
    if is_user_abort:
        return "failed - user aborted the training"
    
    if is_oom:
        return "failed - crash - out of memory"
    
    if is_disk_error:
        return "failed - crash - out of disk"
    
    # For crashes with traceback, include truncated traceback info
    if traceback_str and traceback_str.strip():
        try:
            # Get first few lines of traceback (last 500 chars to get the most relevant part)
            tb_snippet = traceback_str[-500:].strip()
            # Replace newlines with spaces for compactness
            tb_snippet = ' '.join(tb_snippet.split('\n')[-3:])  # Last 3 lines
            if len(tb_snippet) > 200:
                tb_snippet = tb_snippet[:200] + "..."
            if tb_snippet:
                return f"failed - crash - {tb_snippet}"
        except Exception:
            # If traceback processing fails, fall through to other methods
            pass
    
    # If we have exception info but no traceback
    if exception:
        try:
            exc_type = type(exception).__name__
            exc_msg = str(exception)[:200] if str(exception) else ""
            if exc_msg:
                return f"failed - crash - {exc_type}: {exc_msg}"
            return f"failed - crash - {exc_type}"
        except Exception:
            # If exception processing fails, fall through
            pass
    
    # Check exception_type and exception_msg
    if exception_type or exception_msg:
        try:
            exc_type = (exception_type or "Unknown").strip()
            exc_msg = (exception_msg or "").strip()[:200]
            if exc_type and exc_msg:
                return f"failed - crash - {exc_type}: {exc_msg}"
            elif exc_type:
                return f"failed - crash - {exc_type}"
            elif exc_msg:
                return f"failed - crash - {exc_msg}"
        except Exception:
            # If processing fails, fall through to default
            pass
    
    # Default fallback - but return None if truly no info available
    # This makes the field optional - only set it when we have meaningful info
    return "failed - other - needs investigation..."


class JobStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ControlSignal:
    """Control signals for training control."""
    CONTINUE = "continue"
    ABORT = "abort"
    PAUSE = "pause"
    FINISH = "finish"


# Redis connection pool (singleton)
_redis_pool = None


def get_redis_client():
    """Get Redis client with connection pooling and timeouts to prevent hanging."""
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            db=2,  # Use db 2 for job tracking (db 0 is default, db 1 is Celery)
            decode_responses=True,
            socket_timeout=2.0,  # 2 second timeout for socket operations (prevents hanging)
            socket_connect_timeout=2.0,  # 2 second timeout for connection attempts
            retry_on_timeout=True,  # Retry once on timeout
            health_check_interval=30  # Check connection health every 30 seconds
        )

    return redis.Redis(connection_pool=_redis_pool)


def save_job(job_id: str, job_data: dict, session_id: str, job_type: str, ttl: int = 86400 * 7, max_retries: int = 3):
    """
    Save job data to Redis using Celery task ID as key.
    
    Uses Redis transactions (MULTI/EXEC) for atomic updates and includes retry logic.
    
    Args:
        job_id: Celery task ID (used as Redis key)
        job_data: Job metadata dict
        session_id: Session ID this job belongs to
        job_type: Type of job (train_es, train_knn, etc.)
        ttl: Time to live in seconds (default: 7 days)
        max_retries: Maximum number of retry attempts (default: 3)
    """
    for attempt in range(max_retries):
        try:
            client = get_redis_client()

            # Serialize job data
            job_data['job_id'] = job_id
            job_data['session_id'] = session_id
            job_data['job_type'] = job_type
            job_data['updated_at'] = convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))

            # Convert datetime objects and JobStatus to JSON-serializable types (recursively)
            def serialize_value(val):
                """Recursively serialize values for JSON compatibility."""
                if isinstance(val, datetime):
                    return convert_to_iso(val)
                elif isinstance(val, JobStatus):
                    return val.value
                elif isinstance(val, dict):
                    return {k: serialize_value(v) for k, v in val.items()}
                elif isinstance(val, (list, tuple)):
                    return [serialize_value(item) for item in val]
                else:
                    return val
            
            serialized = {key: serialize_value(value) for key, value in job_data.items()}
            serialized_json = json.dumps(serialized)
            key = f"job:{job_id}"
            session_key = f"session:{session_id}:jobs"
            
            # Use Redis transaction (MULTI/EXEC) for atomic update
            pipe = client.pipeline()
            pipe.setex(key, ttl, serialized_json)
            pipe.sadd(session_key, job_id)
            pipe.expire(session_key, ttl)
            results = pipe.execute()
            
            # Verify the update was written (check first result - setex)
            if not results or not results[0]:
                raise Exception(f"Redis setex returned False - update may have failed")
            
            # Verify by reading back the value
            verification = client.get(key)
            if verification is None:
                raise Exception(f"Verification failed: job not found after write")
            # Handle bytes vs string comparison
            if isinstance(verification, bytes):
                verification = verification.decode('utf-8')
            if verification != serialized_json:
                raise Exception(f"Verification failed: written value doesn't match read value")
            
            logger.debug(f"✅ Saved job {job_id} to Redis (session: {session_id}, type: {job_type}) [attempt {attempt + 1}]")
            return  # Success - exit retry loop

        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                wait_time = 0.1 * (2 ** attempt)
                logger.warning(f"⚠️  Failed to save job {job_id} to Redis (attempt {attempt + 1}/{max_retries}): {e}")
                logger.warning(f"   Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Failed to save job {job_id} to Redis after {max_retries} attempts: {e}")
                # Don't raise - job tracking is non-critical, but log the failure


def load_job(job_id: str) -> Optional[dict]:
    """
    Load job data from Redis by Celery task ID.
    
    Args:
        job_id: Celery task ID
        
    Returns:
        Job data dict or None if not found
    """
    try:
        client = get_redis_client()
        key = f"job:{job_id}"
        data = client.get(key)

        if data is None:
            return None

        job_data = json.loads(data)

        # Deserialize datetime objects
        if 'created_at' in job_data:
            job_data['created_at'] = convert_from_iso(job_data['created_at'])
        if 'started_at' in job_data:
            job_data['started_at'] = convert_from_iso(job_data['started_at'])
        if 'finished_at' in job_data:
            job_data['finished_at'] = convert_from_iso(job_data['finished_at'])
        if 'updated_at' in job_data:
            job_data['updated_at'] = convert_from_iso(job_data['updated_at'])

        # Convert status string to enum
        if 'status' in job_data:
            try:
                job_data['status'] = JobStatus(job_data['status'])
            except ValueError:
                # Invalid status - default to READY
                job_data['status'] = JobStatus.READY

        return job_data

    except Exception as e:
        logger.error(f"❌ Failed to load job {job_id} from Redis: {e}")
        return None


def update_job_status(job_id: str, status: JobStatus, metadata: dict = None, max_retries: int = 3):
    """
    Update job status in Redis with atomic updates, retry logic, and verification.
    
    Args:
        job_id: Celery task ID
        status: New job status
        metadata: Optional additional metadata to update
        max_retries: Maximum number of retry attempts (default: 3)
    """
    for attempt in range(max_retries):
        try:
            client = get_redis_client()
            key = f"job:{job_id}"
            
            # Load current job data using existing function (with retry)
            job_data = None
            for load_attempt in range(3):
                try:
                    job_data = load_job(job_id)
                    break
                except Exception as load_err:
                    if load_attempt < 2:
                        time.sleep(0.05 * (2 ** load_attempt))
                        continue
                    raise
            
            if job_data is None:
                logger.warning(f"⚠️  Job {job_id} not found in Redis, creating new entry")
                job_data = {
                    'job_id': job_id,
                    'created_at': datetime.now(tz=ZoneInfo("America/New_York")),
                }

            # Store original status for idempotency check
            original_status = job_data.get('status')
            if isinstance(original_status, JobStatus):
                original_status_value = original_status.value
            else:
                original_status_value = str(original_status) if original_status else None

            # Update status (idempotent - safe to call multiple times)
            job_data['status'] = status.value

            # Update timestamps (only if transitioning to new state)
            now = datetime.now(tz=ZoneInfo("America/New_York"))
            if status == JobStatus.RUNNING and original_status_value != JobStatus.RUNNING.value:
                job_data['started_at'] = now
            elif status in [JobStatus.DONE, JobStatus.FAILED] and original_status_value not in [JobStatus.DONE.value, JobStatus.FAILED.value]:
                job_data['finished_at'] = now

            # Update metadata if provided
            # Note: failure_reason is optional - only set if provided and not empty
            if metadata:
                # Filter out None/empty failure_reason to keep field truly optional
                filtered_metadata = {}
                for key, value in metadata.items():
                    if key == 'failure_reason' and (value is None or (isinstance(value, str) and not value.strip())):
                        # Skip empty failure_reason to keep field optional
                        continue
                    filtered_metadata[key] = value
                if filtered_metadata:
                    job_data.update(filtered_metadata)

            # Get session_id and job_type (required for save_job)
            session_id = job_data.get('session_id', 'unknown')
            job_type = job_data.get('job_type', 'unknown')
            
            # Serialize for Redis
            job_data['updated_at'] = convert_to_iso(now)
            serialized = {}
            for k, v in job_data.items():
                if isinstance(v, datetime):
                    serialized[k] = convert_to_iso(v)
                elif isinstance(v, JobStatus):
                    serialized[k] = v.value
                else:
                    serialized[k] = v
            
            serialized_json = json.dumps(serialized)
            session_key = f"session:{session_id}:jobs"
            ttl = 86400 * 7  # 7 days
            
            # Use Redis transaction (MULTI/EXEC) for atomic update
            pipe = client.pipeline()
            pipe.setex(key, ttl, serialized_json)
            pipe.sadd(session_key, job_id)
            pipe.expire(session_key, ttl)
            
            # Maintain running jobs index for fast queries
            running_jobs_key = f"jobs:running:{job_type}"
            if status == JobStatus.RUNNING:
                # Add to running jobs set
                pipe.sadd(running_jobs_key, job_id)
                pipe.expire(running_jobs_key, ttl)
            elif status in [JobStatus.DONE, JobStatus.FAILED, JobStatus.CANCELLED]:
                # Remove from running jobs set
                pipe.srem(running_jobs_key, job_id)
            
            results = pipe.execute()
            
            # Verify the update was written
            if not results or not results[0]:
                raise Exception(f"Redis setex returned False - update may have failed")
            
            # Verify by reading back the status
            verification_raw = client.get(key)
            if verification_raw:
                try:
                    verification = json.loads(verification_raw)
                    if verification.get('status') != status.value:
                        raise Exception(f"Verification failed: status mismatch (expected {status.value}, got {verification.get('status')})")
                except (json.JSONDecodeError, Exception) as verify_err:
                    raise Exception(f"Verification failed: could not parse or verify written data: {verify_err}")
            else:
                raise Exception(f"Verification failed: job not found after update")
            
            logger.info(f"✅ Updated job {job_id} status to {status.value} [attempt {attempt + 1}]")
            
            # CRITICAL: Invalidate session_info cache when job status changes
            # This ensures monitoring code sees updated status immediately instead of stale cache
            try:
                cache_key = f"session_info_cache:{session_id}"
                client.delete(cache_key)
                logger.debug(f"🗑️  Invalidated session_info cache for session {session_id[:12]}... (job {job_id[:12]}... status changed)")
            except Exception as cache_err:
                logger.debug(f"Failed to invalidate session_info cache (non-critical): {cache_err}")
            
            return  # Success - exit retry loop

        except Exception as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                wait_time = 0.1 * (2 ** attempt)
                logger.warning(f"⚠️  Failed to update job {job_id} status (attempt {attempt + 1}/{max_retries}): {e}")
                logger.warning(f"   Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Failed to update job {job_id} status after {max_retries} attempts: {e}")
                # Don't raise - job tracking is non-critical, but log the failure


def get_session_jobs(session_id: str) -> List[dict]:
    """
    Get all jobs for a session from Redis.
    
    Args:
        session_id: Session ID
        
    Returns:
        List of job data dicts
    """
    try:
        client = get_redis_client()
        session_key = f"session:{session_id}:jobs"
        job_ids = client.smembers(session_key)

        jobs = []
        for job_id in job_ids:
            job_data = load_job(job_id)
            if job_data:
                jobs.append(job_data)

        return jobs

    except Exception as e:
        logger.error(f"❌ Failed to get jobs for session {session_id}: {e}")
        return []


def delete_job(job_id: str):
    """Delete job from Redis."""
    try:
        client = get_redis_client()
        key = f"job:{job_id}"

        # Get session_id before deleting
        job_data = load_job(job_id)
        session_id = job_data.get('session_id') if job_data else None

        # Delete job
        client.delete(key)

        # Remove from session index
        if session_id:
            session_key = f"session:{session_id}:jobs"
            client.srem(session_key, job_id)

        logger.debug(f"✅ Deleted job {job_id} from Redis")

    except Exception as e:
        logger.error(f"❌ Failed to delete job {job_id}: {e}")


def serialize_job(job: dict) -> dict:
    """
    Serialize a job dict for JSON response.
    Converts datetime objects to ISO strings and JobStatus enums to strings.
    
    NOTE: failure_reason is optional - if it's None or empty, it's removed to prevent
    Pydantic validation issues. This field is only set when a job fails with meaningful info.
    """
    from copy import deepcopy
    
    job = deepcopy(job)
    
    # Convert timestamp to string (handle missing fields for placeholder/deleted jobs)
    if "created_at" in job:
        job["created_at"] = convert_to_iso(job["created_at"])
    if "started_at" in job:
        job["started_at"] = convert_to_iso(job["started_at"])
    if "finished_at" in job:
        job["finished_at"] = convert_to_iso(job["finished_at"])
    if "updated_at" in job:
        job["updated_at"] = convert_to_iso(job["updated_at"])
    
    # Convert status enum to string (handle string status for placeholder jobs)
    if "status" in job:
        if hasattr(job["status"], "value"):
            job["status"] = job["status"].value
        # else: already a string (e.g., "deleted")
    
    # CRITICAL: Remove empty/None failure_reason to prevent Pydantic issues
    # This field is optional and should only exist when it has meaningful content
    if "failure_reason" in job:
        failure_reason = job.get("failure_reason")
        if failure_reason is None or (isinstance(failure_reason, str) and not failure_reason.strip()):
            # Remove empty/None failure_reason - field is optional
            del job["failure_reason"]
    
    # Convert any numpy types to native Python types for JSON serialization
    serialized_job = clean_numpy_values(job)
    return serialized_job


def get_job_output_path(job_id: str, session_id: str = None, job_type: str = None) -> Path:
    """
    Get output directory path for a job.
    
    Args:
        job_id: Job ID (Celery task ID)
        session_id: Session ID (required for creating new directories)
        job_type: Job type (required for creating new directories)
        
    Returns:
        Path to job output directory
        
    Raises:
        AssertionError: If session_id and job_type are not provided when directory doesn't exist
    """
    # CRITICAL: job_id must not be None - this causes {job_type}_None directories
    assert job_id and job_id != "None" and job_id != "null", (
        f"CRITICAL BUG: get_job_output_path called with job_id={job_id!r}. "
        f"This would create {job_type}_None directory. "
        f"Celery tasks MUST use self.request.id as job_id before calling this function. "
        f"Check that job_id parameter is set correctly in the task function."
    )
    
    # If session_id and job_type provided, use structured path and create it
    if session_id and job_type:
        session_output_dir = config.output_dir / session_id
        job_dir = session_output_dir / f"{job_type}_{job_id}"
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink to session file in the session output directory
        # This makes it easy to find the session file from the output directory
        session_file_path = config.session_dir / f"{session_id}.session"
        symlink_path = session_output_dir / f"{session_id}.session"
        
        # Only create symlink if session file exists and symlink doesn't already exist
        if session_file_path.exists() and not symlink_path.exists():
            try:
                # Use absolute path for symlink target to avoid issues
                symlink_path.symlink_to(session_file_path.resolve())
                logger.debug(f"✅ Created symlink: {symlink_path} -> {session_file_path.resolve()}")
            except Exception as e:
                # Don't fail if symlink creation fails - it's just a convenience feature
                logger.warning(f"⚠️  Failed to create symlink {symlink_path} -> {session_file_path}: {e}")
        elif symlink_path.exists() and not symlink_path.is_symlink():
            # If a regular file exists, log a warning but don't overwrite it
            logger.debug(f"⚠️  Symlink target {symlink_path} exists but is not a symlink (skipping)")
        elif symlink_path.is_symlink():
            # Verify the symlink points to the correct location
            try:
                actual_target = symlink_path.resolve()
                expected_target = session_file_path.resolve()
                if actual_target != expected_target:
                    # Symlink points to wrong location - update it
                    symlink_path.unlink()
                    symlink_path.symlink_to(session_file_path.resolve())
                    logger.debug(f"✅ Updated symlink: {symlink_path} -> {session_file_path.resolve()}")
            except Exception as e:
                logger.debug(f"⚠️  Could not verify/update symlink {symlink_path}: {e}")
        
        return job_dir
    
    # If only job_id provided, search for existing directory and assert it exists
    # This is used by control file checks (ABORT, PAUSE, etc.)
    if not session_id or not job_type:
        # Search in structured paths first
        if session_id:
            session_dir = config.output_dir / session_id
            if session_dir.exists():
                for potential_dir in session_dir.iterdir():
                    if potential_dir.is_dir() and potential_dir.name.endswith(f"_{job_id}"):
                        return potential_dir
        
        # Search common locations
        common_dirs = [
            config.output_dir / job_id,
            Path("/sphere/app/featrix_output") / job_id,
            Path("/featrix-output") / job_id,
            Path("/sphere/featrix_data") / job_id,
        ]
        
        for job_dir in common_dirs:
            if job_dir.exists():
                return job_dir
        
        # Not found - assert failure
        assert False, (
            f"Job directory not found for job_id={job_id}. "
            f"Must provide session_id and job_type to create new directory, "
            f"or ensure directory exists at one of: {[str(d) for d in common_dirs]}"
        )
    
    # Should never reach here
    assert False, f"Invalid arguments: job_id={job_id}, session_id={session_id}, job_type={job_type}"


# ============================================================================
# Job Control File Checking
# ============================================================================

def _find_control_file(job_id: str, filename: str, output_dir: str = None) -> Optional[Path]:
    """
    Find a control file (ABORT, PAUSE, FINISH, NO_STOP) for a job.
    
    For /sphere paths: Checks both job directory and parent directories (session-level control files)
    For other paths: ONLY checks the specific job's directory to avoid false positives
    """
    if job_id is None:
        return None
    
    paths_to_check = []
    
    # Helper to check if a path is under /sphere
    def is_sphere_path(path: Path) -> bool:
        try:
            return str(path.resolve()).startswith("/sphere")
        except Exception:
            return False
    
    # 1. Check the exact output_dir being used (most important)
    if output_dir:
        output_path = Path(output_dir)
        if output_path.exists():
            paths_to_check.append(output_path / filename)
            # For /sphere paths, also check parent directory (session-level control files)
            if is_sphere_path(output_path) and output_path.parent.exists():
                paths_to_check.append(output_path.parent / filename)
    
    # 2. Get job output directory - will assert if not found
    try:
        job_output_dir = get_job_output_path(job_id)
        paths_to_check.append(job_output_dir / filename)
        # For /sphere paths, also check parent directory (session-level control files)
        if is_sphere_path(job_output_dir) and job_output_dir.parent.exists():
            paths_to_check.append(job_output_dir.parent / filename)
    except Exception:
        pass
    
    # 3. Check common directories
    common_dirs = [
        Path("/sphere/app/featrix_output") / job_id,
        Path("/sphere/featrix_data") / job_id,
    ]
    if output_dir:
        common_dirs.append(Path(output_dir) / job_id)
    
    for common_dir in common_dirs:
        if common_dir.exists():
            paths_to_check.append(common_dir / filename)
            # For /sphere paths, also check parent directory (session-level control files)
            if is_sphere_path(common_dir) and common_dir.parent.exists():
                paths_to_check.append(common_dir.parent / filename)
    
    # Remove duplicates
    seen = set()
    unique_paths = []
    for p in paths_to_check:
        try:
            p_str = str(p.resolve())
            if p_str not in seen:
                seen.add(p_str)
                unique_paths.append(p)
        except Exception:
            pass
    
    for control_file in unique_paths:
        if control_file.exists():
            return control_file
    
    return None


def check_abort_file(job_id: str, output_dir: str = None) -> bool:
    """Check if ABORT file exists."""
    abort_file = _find_control_file(job_id, "ABORT", output_dir)
    if abort_file:
        logger.warning(f"🚫 ABORT file detected: {abort_file}")
        return True
    return False


def check_pause_file(job_id: str, output_dir: str = None) -> bool:
    """Check if PAUSE file exists."""
    return _find_control_file(job_id, "PAUSE", output_dir) is not None


def check_finish_file(job_id: str, output_dir: str = None) -> bool:
    """Check if FINISH file exists."""
    return _find_control_file(job_id, "FINISH", output_dir) is not None


def check_no_stop_file(job_id: str, output_dir: str = None) -> bool:
    """Check if NO_STOP file exists."""
    return _find_control_file(job_id, "NO_STOP", output_dir) is not None


def recover_stalled_job_from_directory(job_id: str, session_id: str = None, job_type: str = None) -> bool:
    """
    Check if a job has completed by examining its output directory, and update status if needed.
    
    This function detects jobs that completed successfully but their status wasn't updated in Redis.
    It checks for completion indicators (output files) based on job type and updates the status to DONE.
    
    Args:
        job_id: Job ID to check
        session_id: Session ID (optional, will be inferred from job data if not provided)
        job_type: Job type (optional, will be inferred from job data if not provided)
        
    Returns:
        True if job was detected as completed and status was updated, False otherwise
    """
    try:
        # Load job data to get session_id and job_type if not provided
        job_data = load_job(job_id)
        if not job_data:
            logger.debug(f"Could not load job {job_id} from Redis - skipping directory check")
            return False
        
        # Use provided values or fall back to job data
        if not session_id:
            session_id = job_data.get('session_id') or job_data.get('job_spec', {}).get('session_id')
        if not job_type:
            job_type = job_data.get('job_type') or job_data.get('job_spec', {}).get('job_type')
        
        # Check current status - only recover if status is READY or RUNNING
        current_status = job_data.get('status')
        if isinstance(current_status, JobStatus):
            current_status_value = current_status.value
        else:
            current_status_value = str(current_status) if current_status else 'unknown'
        
        if current_status_value in [JobStatus.DONE.value, JobStatus.FAILED.value]:
            # Job is already marked as done or failed - no recovery needed
            return False
        
        # Get job output directory
        if not session_id or not job_type:
            logger.debug(f"Cannot check job directory for {job_id} - missing session_id or job_type")
            return False
        
        try:
            job_output_dir = get_job_output_path(job_id, session_id=session_id, job_type=job_type)
        except Exception as dir_err:
            logger.debug(f"Could not get job output path for {job_id}: {dir_err}")
            return False
        
        if not job_output_dir.exists():
            # Job directory doesn't exist - job hasn't started yet
            return False
        
        # Check for completion indicators based on job type
        job_completed = False
        completion_evidence = []
        
        if job_type == "create_structured_data":
            if (job_output_dir / "embedding_space.db").exists():
                job_completed = True
                completion_evidence.append("embedding_space.db")
            if (job_output_dir / "data.db").exists():
                job_completed = True
                completion_evidence.append("data.db")
        elif job_type == "train_es":
            from featrix.neural.embedding_space_utils import find_embedding_space_pickle
            es_pickle = find_embedding_space_pickle(job_output_dir)
            if es_pickle:
                job_completed = True
                completion_evidence.append(str(es_pickle.name))
        elif job_type == "train_knn":
            if (job_output_dir / "vector_db").exists():
                job_completed = True
                completion_evidence.append("vector_db")
            if list(job_output_dir.glob("*.index")):
                job_completed = True
                completion_evidence.append("*.index files")
        elif job_type == "run_clustering":
            if (job_output_dir / "embedded_space_projections.json").exists():
                job_completed = True
                completion_evidence.append("embedded_space_projections.json")
            if (job_output_dir / "sphere_preview.png").exists():
                job_completed = True
                completion_evidence.append("sphere_preview.png")
            if list(job_output_dir.glob("*.json")):
                job_completed = True
                completion_evidence.append("*.json files")
            if list(job_output_dir.glob("*preview*.png")):
                job_completed = True
                completion_evidence.append("*preview*.png files")
        elif job_type == "pre_analysis_architecture":
            if (job_output_dir / "analysis.json").exists():
                job_completed = True
                completion_evidence.append("analysis.json")
            if list(job_output_dir.glob("analysis*.json")):
                job_completed = True
                completion_evidence.append("analysis*.json files")
        
        if job_completed:
            # Job has output files indicating completion - update status
            logger.info(f"🔧 Detected completed job {job_id} ({job_type}) via directory check")
            logger.info(f"   Evidence: {', '.join(completion_evidence)}")
            logger.info(f"   Updating status from {current_status_value} → DONE")
            
            try:
                update_job_status(job_id=job_id, status=JobStatus.DONE)
                logger.info(f"✅ Successfully updated job {job_id} status to DONE")
                return True
            except Exception as update_err:
                logger.warning(f"⚠️  Failed to update job {job_id} status to DONE: {update_err}")
                return False
        
        return False
        
    except Exception as e:
        logger.warning(f"⚠️  Error checking job directory for {job_id}: {e}")
        return False


class JobStatusTracker:
    """
    Utility class to track and write job_status.json to job root directory.
    
    Usage:
        tracker = JobStatusTracker(job_dir)
        tracker.start()  # Call at job start
        tracker.add_error("Error message")
        tracker.add_warning("Warning message")
        tracker.add_output_file("path/to/file")
        tracker.finish(successful=True)  # Call at job end
    """
    
    def __init__(self, job_dir: Path):
        """
        Initialize job status tracker.
        
        Args:
            job_dir: Path to job root directory
        """
        self.job_dir = Path(job_dir)
        self.status_file = self.job_dir / "job_status.json"
        self._errors = []
        self._warnings = []
        self._output_files = []
        self._start_time = None
        self._finished_time = None
        self._finished = False
        self._successful = False
    
    def start(self):
        """Mark job as started and write initial status."""
        self._start_time = datetime.now(tz=ZoneInfo("America/New_York"))
        self._write_status()
    
    def add_error(self, error: str):
        """Add an error message."""
        if error and error not in self._errors:
            self._errors.append(error)
            self._write_status()
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        if warning and warning not in self._warnings:
            self._warnings.append(warning)
            self._write_status()
    
    def add_output_file(self, file_path: str):
        """Add an output file path."""
        if file_path:
            # Convert to string and normalize path
            file_str = str(Path(file_path).resolve()) if Path(file_path).exists() else str(file_path)
            if file_str not in self._output_files:
                self._output_files.append(file_str)
                self._write_status()
    
    def finish(self, successful: bool = True, errors: list = None, warnings: list = None, output_files: list = None):
        """
        Mark job as finished and write final status.
        
        Args:
            successful: Whether job completed successfully
            errors: Optional list of error messages to add
            warnings: Optional list of warning messages to add
            output_files: Optional list of output file paths to add
        """
        self._finished_time = datetime.now(tz=ZoneInfo("America/New_York"))
        self._finished = True
        self._successful = successful
        
        if errors:
            for error in errors:
                self.add_error(error)
        if warnings:
            for warning in warnings:
                self.add_warning(warning)
        if output_files:
            for file_path in output_files:
                self.add_output_file(file_path)
        
        self._write_status()
    
    def _write_status(self):
        """Write current status to job_status.json file."""
        try:
            status = {
                "start_time": convert_to_iso(self._start_time) if self._start_time else None,
                "finished_time": convert_to_iso(self._finished_time) if self._finished_time else None,
                "errors": self._errors.copy(),
                "warnings": self._warnings.copy(),
                "finished": self._finished,
                "successful": self._successful,
                "output_files": self._output_files.copy()
            }
            
            # Write atomically (write to temp file, then rename)
            temp_file = self.status_file.with_suffix('.json.tmp')
            with open(temp_file, 'w') as f:
                json.dump(status, f, indent=2, default=str)
            temp_file.replace(self.status_file)
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to write job_status.json for {self.job_dir}: {e}")


def create_job_status_tracker(job_dir: Path) -> JobStatusTracker:
    """
    Create a JobStatusTracker instance for a job directory.
    
    Convenience function for easy usage.
    
    Args:
        job_dir: Path to job root directory
        
    Returns:
        JobStatusTracker instance
    """
    return JobStatusTracker(job_dir)


def create_control_check_callback(job_id: str, output_dir: str = None):
    """
    Create a control check callback function for use in training loops.
    
    Returns a function that checks control files and returns a ControlSignal.
    The callback also handles job status updates when control signals are detected.
    
    Args:
        job_id: Job ID
        output_dir: Optional output directory
        
    Returns:
        Callable that returns ControlSignal
    """
    def check_control() -> str:
        """Check for control files and return signal."""
        # Check ABORT first (highest priority)
        if check_abort_file(job_id, output_dir):
            logger.error(f"🚫 ABORT file detected for job {job_id}")
            try:
                job_data = load_job(job_id)
                if job_data:
                    failure_reason = determine_failure_reason(is_user_abort=True)
                    job_data["status"] = JobStatus.FAILED.value
                    job_data["finished_at"] = convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))
                    job_data["error_message"] = "Training aborted due to ABORT file"
                    job_data["failure_reason"] = failure_reason
                    save_job(
                        job_id,
                        job_data,
                        job_data.get("session_id", "unknown"),
                        job_data.get("job_type", "unknown")
                    )
                    logger.info(f"🚫 Job {job_id} marked as FAILED due to ABORT file (reason: {failure_reason})")
            except Exception as e:
                logger.error(f"Failed to update job status when ABORT detected: {e}")
            return ControlSignal.ABORT
        
        # Check PAUSE
        if check_pause_file(job_id, output_dir):
            logger.warning(f"⏸️  PAUSE file detected for job {job_id}")
            try:
                job_data = load_job(job_id)
                if job_data:
                    job_data["status"] = JobStatus.PAUSED.value
                    job_data["pause_reason"] = "PAUSE file detected by user"
                    job_data["paused_at"] = convert_to_iso(datetime.now(tz=ZoneInfo("America/New_York")))
                    save_job(
                        job_id,
                        job_data,
                        job_data.get("session_id", "unknown"),
                        job_data.get("job_type", "unknown")
                    )
                    logger.info(f"⏸️  Job {job_id} marked as PAUSED")
            except Exception as e:
                logger.error(f"Failed to update job status to PAUSED: {e}")
            return ControlSignal.PAUSE
        
        # Check FINISH
        if check_finish_file(job_id, output_dir):
            logger.warning(f"🏁 FINISH file detected for job {job_id}")
            return ControlSignal.FINISH
        
        return ControlSignal.CONTINUE
    
    return check_control
