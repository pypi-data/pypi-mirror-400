"""
Session Management Module

Extracted from featrix_queue.py to provide clean session management interface.
Handles all session file operations, creation, loading, saving, and iteration.

NOW USES REDIS AS PRIMARY STORAGE for atomic updates and coordination.
File-based storage is kept as backup/fallback.
"""
import json
import logging
import os
import shutil
import socket
import sys
import time
import traceback
from copy import deepcopy
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from config import config
from utils import convert_from_iso, convert_to_iso
from featrix.neural.embedding_space_utils import find_embedding_space_pickle

logger = logging.getLogger(__name__)

# Redis connection for session storage (db 3 for sessions)
_session_redis_pool = None

def get_session_redis_client():
    """Get Redis client for session storage (db 3)."""
    global _session_redis_pool
    try:
        import redis
    except ImportError:
        logger.warning("Redis not available - falling back to file-based storage")
        return None
    
    if _session_redis_pool is None:
        try:
            _session_redis_pool = redis.ConnectionPool(
                host='localhost',
                port=6379,
                db=3,  # Use db 3 for session storage (db 0=default, db 1=Celery, db 2=jobs)
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=True,
                health_check_interval=30
            )
        except Exception as e:
            logger.warning(f"Failed to create Redis connection pool: {e}")
            return None
    
    try:
        client = redis.Redis(connection_pool=_session_redis_pool)
        # CRITICAL: Verify Redis persistence is enabled - crash if not!
        persistence_info = client.info('persistence')
        rdb_enabled = persistence_info.get('rdb_last_save_time', -1) != -1 or persistence_info.get('rdb_changes_since_last_save', 0) >= 0
        aof_enabled = persistence_info.get('aof_enabled', 0) == 1
        
        if not (rdb_enabled or aof_enabled):
            error_msg = (
                "❌ CRITICAL: Redis persistence is NOT enabled! "
                "Sessions will be lost on restart. "
                f"RDB enabled: {rdb_enabled}, AOF enabled: {aof_enabled}. "
                "Redis must be configured with persistence (RDB or AOF) before sessions can be stored."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        return client
    except RuntimeError:
        # Re-raise persistence errors
        raise
    except Exception as e:
        logger.warning(f"Failed to get Redis client: {e}")
        return None


class SessionStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


def compute_session_status(session: dict, session_jobs: dict = None) -> str:
    """
    Compute session status dynamically from job statuses.
    
    This is the SINGLE SOURCE OF TRUTH for session status. Session status
    is NO LONGER STORED in the session file - it's always computed on-the-fly.
    
    Args:
        session: Session document
        session_jobs: Optional dict of jobs (if not provided, will load from Redis)
        
    Returns:
        Status string: "ready", "running", "done", "failed", or "cancelled"
    """
    # Load jobs if not provided
    if session_jobs is None:
        session_id = session.get('session_id')
        if not session_id:
            return SessionStatus.READY.value
        
        from lib.job_manager import get_session_jobs
        session_jobs = get_session_jobs(session_id)
    
    # No jobs in Redis - check job_plan to see if there are jobs waiting to be dispatched
    if not session_jobs:
        job_plan = session.get('job_plan', [])
        if not job_plan:
            # No job plan - session is ready
            return SessionStatus.READY.value
        
        # Check if all jobs in plan have job_ids
        jobs_without_ids = [j for j in job_plan if not j.get('job_id') or j.get('job_id') == "None" or j.get('job_id') == "skipped-foundation-model"]
        
        if jobs_without_ids:
            # There are jobs without IDs - session is ready (waiting for dispatch)
            return SessionStatus.READY.value
        
        # All jobs have IDs but no jobs in Redis - this could mean:
        # 1. Jobs completed and were cleaned up from Redis (session is DONE)
        # 2. Jobs haven't been dispatched yet (session is READY)
        # 3. Jobs are still running but not in Redis yet (session is RUNNING - unlikely)
        
        # Check if we have output files - this is a strong indicator that jobs completed
        has_outputs = session.get('embedding_space') or session.get('single_predictors')
        
        if has_outputs:
            # Has output files AND all jobs have IDs - jobs likely completed and were cleaned up
            # Return DONE to indicate session completed successfully
            return SessionStatus.DONE.value
        
        # No outputs and all jobs have IDs - jobs might not have been dispatched yet
        # But if jobs have IDs, they should be in Redis if they're running
        # This is an ambiguous state - default to READY but could be DONE if jobs were cleaned up
        # For now, check if there are any active Celery tasks for this session
        try:
            from celery_app import app
            inspect = app.control.inspect(timeout=0.5)
            active = inspect.active() or {}
            for worker, tasks in active.items():
                for task in tasks:
                    task_args = task.get('args', [])
                    if isinstance(task_args, (list, tuple)) and len(task_args) > 0:
                        # Check if task is for this session
                        task_session_id = task_args[0] if task_args else None
                        if task_session_id == session.get('session_id'):
                            # Found active task for this session
                            return SessionStatus.RUNNING.value
        except Exception:
            # Celery inspection failed - can't determine, default to READY
            pass
        
        # Default to READY if we can't determine otherwise
        return SessionStatus.READY.value
    
    # Analyze job statuses
    all_done = True
    any_failed = False
    any_running = False
    any_cancelled = False
    
    for job_id, job in session_jobs.items():
        job_status = job.get("status")
        if isinstance(job_status, SessionStatus):
            job_status_value = job_status.value
        else:
            job_status_value = str(job_status) if job_status else "unknown"
        
        # Treat "unknown" job status as "ready" (waiting to be dispatched)
        # This handles cases where jobs are created but status isn't set yet
        if job_status_value == "unknown":
            job_status_value = "ready"
        
        if job_status_value not in ["done", "failed", "deleted", "cancelled"]:
            all_done = False
            if job_status_value == "running":
                any_running = True
        elif job_status_value == "failed":
            any_failed = True
        elif job_status_value == "cancelled":
            any_cancelled = True
    
    # Determine final status
    if all_done:
        if any_cancelled:
            return SessionStatus.CANCELLED.value
        elif any_failed:
            return SessionStatus.FAILED.value
        else:
            return SessionStatus.DONE.value
    elif any_running:
        return SessionStatus.RUNNING.value
    else:
        return SessionStatus.READY.value


def serialize_session(session_doc: dict, include_status: bool = False):
    """
    Serialize session document for storage (convert dates, enums, etc.).
    
    Args:
        session_doc: Session document to serialize
        include_status: If True, include the status field (for API responses).
                       If False, remove status (for saving to disk/Redis).
                       Default False for backward compatibility.
    """
    session_doc = deepcopy(session_doc)

    # Convert datetime objects to ISO strings
    if "created_at" in session_doc:
        session_doc["created_at"] = convert_to_iso(session_doc["created_at"])
    if "started_at" in session_doc:
        session_doc["started_at"] = convert_to_iso(session_doc["started_at"])
    if "finished_at" in session_doc:
        session_doc["finished_at"] = convert_to_iso(session_doc["finished_at"])
    if "published_at" in session_doc:
        session_doc["published_at"] = convert_to_iso(session_doc["published_at"])
    if "deprecated_at" in session_doc:
        session_doc["deprecated_at"] = convert_to_iso(session_doc["deprecated_at"])

    # Note: status is NOT saved to disk/Redis - it's computed dynamically by get_session_info()
    # However, for API responses, we want to include the computed status
    # Remove status field only if not including it (for storage)
    if not include_status:
        session_doc.pop("status", None)

    return session_doc


def update_session_field(session_id: str, field: str, value: Any):
    """
    Atomically update a single field in a session using Redis HSET.
    This is atomic - no read-modify-write needed!
    
    Args:
        session_id: Session ID
        field: Field name to update (e.g., 'job_plan', 'embedding_space')
        value: New value (will be JSON-serialized)
    """
    redis_client = get_session_redis_client()
    if not redis_client:
        # Fall back to full save
        session = load_session(session_id)
        session[field] = value
        save_session(session_id, session, exist_ok=True)
        return
    
    try:
        session_key = f"session:{session_id}"
        
        # Load current session
        data = redis_client.hget(session_key, "data")
        if not data:
            # Session not in Redis - load from file and migrate
            session = load_session(session_id)
            json_str = json.dumps(serialize_session(session))
            redis_client.hset(session_key, mapping={"data": json_str})
            redis_client.expire(session_key, 86400 * 30)
        
        # Update the field atomically
        session = json.loads(data) if data else {}
        session[field] = value
        
        # Save back atomically
        json_str = json.dumps(serialize_session(session))
        redis_client.hset(session_key, mapping={"data": json_str})
        
        logger.debug(f"✅ Updated field '{field}' in session {session_id} (Redis)")
        
        # Delete any existing file and lock file since we're using Redis (which is persisted to disk)
        session_path = config.session_dir / f"{session_id}.session"
        lock_path = config.session_dir / f"{session_id}.lock"
        
        if session_path.exists():
            try:
                session_path.unlink()
                logger.debug(f"🗑️  Deleted session file (now in Redis)")
            except Exception as delete_err:
                logger.warning(f"⚠️  Failed to delete session file: {delete_err}")
                # Non-critical
        
        if lock_path.exists():
            try:
                lock_path.unlink()
                logger.debug(f"🗑️  Deleted lock file")
            except Exception as lock_delete_err:
                logger.debug(f"⚠️  Failed to delete lock file: {lock_delete_err}")
            
    except Exception as e:
        logger.warning(f"⚠️  Failed to update session field in Redis: {e}")
        # Fall back to full save
        session = load_session(session_id)
        session[field] = value
        save_session(session_id, session, exist_ok=True)


def save_session(session_id: str, session_doc: dict, exist_ok: bool = False):
    """
    Save session document to Redis ONLY. No file-based storage.
    Raises exception if Redis is unavailable.
    """
    serialized_session = serialize_session(session_doc)
    
    # Invalidate session_info cache when session is updated
    try:
        from lib.job_manager import get_redis_client
        cache_redis = get_redis_client()
        cache_key = f"session_info_cache:{session_id}"
        cache_redis.delete(cache_key)
        logger.debug(f"🗑️  Invalidated session_info cache for {session_id[:12]}...")
    except Exception as cache_err:
        logger.debug(f"Failed to invalidate cache (non-critical): {cache_err}")
    
    # Redis is REQUIRED - no file fallback
    redis_client = get_session_redis_client()
    if not redis_client:
        raise RuntimeError(f"Cannot save session {session_id}: Redis is not available. Sessions must be stored in Redis.")
    
    try:
        session_key = f"session:{session_id}"
        json_str = json.dumps(serialized_session)
        
        # Check if session exists if exist_ok=False
        if not exist_ok:
            existing = redis_client.hget(session_key, "data")
            if existing:
                raise FileExistsError(f"Session {session_id} already exists")
        
        # Use HSET to atomically update all fields at once
        # This is atomic - no read-modify-write needed!
        redis_client.hset(session_key, mapping={"data": json_str})
        redis_client.expire(session_key, 86400 * 30)  # 30 day TTL
        
        logger.debug(f"✅ Session {session_id} saved to Redis")
        
    except FileExistsError:
        raise
    except Exception as redis_err:
        error_msg = f"Failed to save session {session_id} to Redis: {redis_err}"
        logger.error(f"🔴 {error_msg}")
        raise RuntimeError(error_msg) from redis_err


def load_session(session_id: str):
    """
    Load a session by session_id from Redis. If not found in Redis, check backplane for session files.
    Raises FileNotFoundError if session does not exist in Redis or backplane.
    """
    # Redis is REQUIRED - no file fallback
    redis_client = get_session_redis_client()
    if not redis_client:
        raise RuntimeError(f"Cannot load session {session_id}: Redis is not available. Sessions must be stored in Redis.")
    
    try:
        session_key = f"session:{session_id}"
        data = redis_client.hget(session_key, "data")
        if not data:
            # Not in Redis - check backplane for session files
            logger.info(f"🔍 Session {session_id} not in Redis, checking backplane...")
            session_doc = _load_session_from_backplane(session_id)
            if session_doc:
                # Found in backplane - save to local Redis for future access
                logger.info(f"✅ Found session {session_id} in backplane, saving to local Redis")
                save_session(session_id, session_doc, exist_ok=True)
                return _process_loaded_session(session_id, session_doc)
            else:
                raise FileNotFoundError(f"Session {session_id} does not exist in Redis or backplane")
        
        session_doc = json.loads(data)
        logger.debug(f"✅ Session {session_id} loaded from Redis")
        # Process the session (fix paths, convert dates, etc.)
        return _process_loaded_session(session_id, session_doc)
        
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        error_msg = f"Session {session_id} data in Redis is corrupted. JSON parse error: {e}"
        logger.error(f"🔴 {error_msg}")
        raise ValueError(error_msg) from e
    except Exception as redis_err:
        error_msg = f"Failed to load session {session_id} from Redis: {redis_err}"
        logger.error(f"🔴 {error_msg}")
        raise RuntimeError(error_msg) from redis_err


def _load_session_from_backplane(session_id: str) -> dict | None:
    """
    Load a session from backplane output directories.
    Searches /backplane/backplane1/sphere/host-*/app/featrix_output/{session_id}/session.json
    
    Returns:
        Session dict if found, None otherwise
    """
    backplane_base = Path("/backplane/backplane1/sphere")
    if not backplane_base.exists():
        logger.debug(f"   Backplane directory does not exist: {backplane_base}")
        return None
    
    # Search all host directories in backplane
    host_dirs = list(backplane_base.glob("host-*"))
    logger.info(f"   Searching {len(host_dirs)} hosts in backplane: {[h.name for h in host_dirs]}")
    
    for host_dir in host_dirs:
        if not host_dir.is_dir():
            continue
        
        # Check for session directory: host-*/app/featrix_output/{session_id}/
        session_output_dir = host_dir / "app" / "featrix_output" / session_id
        if session_output_dir.exists() and session_output_dir.is_dir():
            # Look for session.json in the session directory
            session_file = session_output_dir / "session.json"
            if session_file.exists():
                try:
                    logger.info(f"✅ Found session in backplane: {session_file}")
                    with open(session_file, 'r') as f:
                        session_doc = json.load(f)
                    return session_doc
                except Exception as e:
                    logger.warning(f"⚠️  Failed to load session file {session_file}: {e}")
                    continue
    
    logger.debug(f"   Session {session_id} not found in backplane")
    return None


def _process_loaded_session(session_id: str, session_doc: dict) -> dict:
    """Process a loaded session (fix paths, convert dates, etc.)."""
    session_doc['created_at'] = convert_from_iso(session_doc['created_at'])
    
    # Note: status is NOT loaded/converted here - it's computed dynamically by get_session_info()
    # Legacy sessions may have it stored, new sessions don't, but it doesn't matter since
    # all code uses .get("status") and get_session_info() recomputes it from job statuses
    
    # Skip path validation for archived sessions (they have _old_ prefix)
    # These are old sessions that we keep for reference but don't need to fix/validate
    is_archived_session = session_id.startswith("_old_")
    
    # Check if session is old (> 3 days) - if so, skip validation/logging for missing files
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    now = datetime.now(tz=ZoneInfo("America/New_York"))
    session_age = now - session_doc['created_at']
    is_old_session = session_age > timedelta(days=3)
    
    # CRITICAL: If session output directory doesn't exist, delete session from Redis
    # This cleans up stale sessions whose files were deleted
    if not is_archived_session:
        output_dir = session_doc.get('output_dir')
        if output_dir:
            output_path = Path(output_dir)
            if not output_path.exists():
                logger.warning(f"Session {session_id[:16]}... output directory doesn't exist: {output_dir}")
                logger.warning(f"   Deleting stale session from Redis (age: {session_age.days} days)")
                try:
                    redis_client = get_session_redis_client()
                    if redis_client:
                        redis_client.delete(f"session:{session_id}")
                        logger.info(f"   ✅ Deleted stale session from Redis")
                except Exception as del_err:
                    logger.warning(f"   ⚠️  Could not delete session from Redis: {del_err}")
                # Still return the session for this load, it'll be gone next time
    
    # CRITICAL: Fix stale paths from sessions created on different machines
    # Sessions might have paths like /shared1/sphere-data/... that don't exist on this machine
    paths_fixed = False
    
    # Fix sqlite_db path if it exists but file doesn't
    # Skip this entirely for archived sessions - they have stale paths and we don't care
    # Skip logging for old sessions (> 3 days) - they're just noise
    sqlite_db = session_doc.get('sqlite_db')
    if sqlite_db and not is_archived_session:
        sqlite_path = Path(sqlite_db)
        if not sqlite_path.exists():
            # Only log for recent sessions (< 3 days old) - old ones are just stale noise
            if not is_old_session:
                logger.debug(f"Session {session_id}: sqlite_db path doesn't exist: {sqlite_db}")
                # Try to find it
                fixed_path = find_session_data_files(session_id, sqlite_db, "sqlite_db")
                if fixed_path:
                    logger.info(f"   ✅ Fixed sqlite_db path: {fixed_path}")
                    session_doc['sqlite_db'] = fixed_path
                    paths_fixed = True
                else:
                    logger.debug(f"   Could not find sqlite_db file anywhere (session may be old/deleted)")
            # For old sessions, silently skip - don't log anything
    
    # strings_cache is optional (we don't use it anymore) - just remove if it doesn't exist
    # Skip for archived sessions
    strings_cache = session_doc.get('strings_cache')
    if strings_cache and not is_archived_session:
        cache_path = Path(strings_cache)
        if not cache_path.exists():
            logger.debug(f"Session {session_id}: strings_cache doesn't exist (not needed), removing from session")
            session_doc.pop('strings_cache', None)
            paths_fixed = True
    
    # If we fixed paths, save the session with corrected paths
    # Never modify archived sessions - they're read-only historical records
    if paths_fixed and not is_archived_session:
        logger.info(f"📝 Saving session {session_id} with corrected paths...")
        try:
            save_session(session_id, session_doc, exist_ok=True)
            logger.info(f"   ✅ Session paths corrected and saved")
        except Exception as save_err:
            logger.warning(f"   ⚠️  Could not save corrected paths: {save_err}")
            logger.warning(f"   Session will work but paths won't be permanently fixed")
            logger.debug(f"   Save error traceback: {traceback.format_exc()}")

    return session_doc


def find_session_data_files(session_id: str, original_path: str, file_type: str = "sqlite_db") -> str | None:
    """
    Search for a session's data files (sqlite_db, strings_cache) across multiple locations.
    
    Handles cases where sessions were created on different machines with different mount points.
    
    Args:
        session_id: Session ID to search for
        original_path: Original path stored in session (may not exist)
        file_type: Type of file ("sqlite_db" or "strings_cache")
    
    Returns:
        Path to the file if found, None otherwise
    """
    # Extract the relative path from the original path
    # Example: /shared1/sphere-data/app/featrix_output/public-alphafreight-medium-xyz/create_structured_data/abc/data.db
    # -> We want to find data.db in any create_structured_data job directory
    
    original_p = Path(original_path)
    filename = original_p.name
    
    # Common search locations (in priority order)
    search_roots = [
        config.output_dir,  # /sphere/app/featrix_output or /featrix-output
        Path("/sphere/app/featrix_output"),
        Path("/featrix-output"),
        Path("/shared1/sphere-data/app/featrix_output"),
    ]
    
    # If original path contains a parent session ID, extract it
    # Look for UUIDs in the path (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    import re
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    parent_sessions = re.findall(uuid_pattern, str(original_path))
    
    logger.debug(f"🔍 Searching for {file_type} file: {filename}")
    logger.debug(f"   Original path: {original_path}")
    logger.debug(f"   Found potential parent sessions: {parent_sessions}")
    
    # Search strategy:
    # 1. Check original path first
    if original_p.exists():
        logger.debug(f"   ✅ Found at original path: {original_path}")
        return str(original_path)
    
    # 2. Search in each parent session's create_structured_data directories
    for parent_session_id in parent_sessions:
        for root in search_roots:
            if not root.exists():
                continue
            
            # Look for create_structured_data job directories
            parent_dir = root / parent_session_id
            if not parent_dir.exists():
                continue
            
            # Search for the file in create_structured_data subdirectories
            for job_dir in parent_dir.glob("create_structured_data_*"):
                candidate = job_dir / filename
                if candidate.exists():
                    logger.info(f"   ✅ Found {file_type} at: {candidate}")
                    return str(candidate)
    
    # 3. Last resort: search for ANY create_structured_data directory with this file
    # (only for sqlite_db, not strings_cache which is optional)
    if file_type == "sqlite_db":
        for root in search_roots:
            if not root.exists():
                continue
            
            # Use glob to find all create_structured_data directories
            for candidate in root.glob(f"*/create_structured_data_*/{filename}"):
                if candidate.exists():
                    logger.info(f"   ⚠️  Found {file_type} at unexpected location: {candidate}")
                    return str(candidate)
        
        logger.warning(f"   ❌ Could not find {file_type} file: {filename}")
    else:
        logger.debug(f"   {file_type} not found (optional)")
    
    return None


def resolve_session_path(session_id: str, path_from_session: str) -> Path:
    """
    Resolve a path stored in a session document to an absolute Path.
    
    Handles:
    - Relative paths (relative to session output directory)
    - Absolute paths
    - Published session paths
    - Symlinked sessions
    """
    if not path_from_session:
        raise ValueError("path_from_session cannot be empty")

    # Try to load session to check if it's published
    try:
        session = load_session(session_id)
        published = session.get("published", False)
        published_path = session.get("published_path")
    except FileNotFoundError:
        # Session doesn't exist yet, assume not published
        published = False
        published_path = None

    # If path is already absolute, check if it exists
    original_path = Path(path_from_session)
    if original_path.is_absolute():
        if original_path.exists():
            return original_path
        # Path doesn't exist, but it's absolute - return as-is
        return original_path

    # Path is relative - resolve based on session location
    if published and published_path:
        # Session is published - resolve relative to published output directory
        published_output_dir = Path(published_path) / "output"
        resolved = published_output_dir / path_from_session
    else:
        # Regular session - resolve relative to output directory
        resolved = config.output_dir / session_id / path_from_session

    # If resolved path doesn't exist, try the original path
    if not resolved.exists() and original_path.exists():
        logger.warning(f"⚠️  Resolved path {resolved} doesn't exist, using original {original_path}")
        return original_path

    return resolved


def get_session_info(session_id: str, use_cache: bool = True):
    """
    Get session information from Redis/Celery (no file-based queues).
    
    PERFORMANCE: Uses Redis cache with 10s TTL to avoid expensive disk I/O on every request.
    
    Args:
        session_id: Session ID to fetch
        use_cache: If True, use Redis cache (default). Set False to force fresh load.
    
    Returns dict with:
    - session: The session document
    - jobs: Dict of job_id -> job data from Redis
    - job_queue_positions: Dict of job_id -> None (not applicable for Celery)
    - detailed_queue_info: Enhanced queue information per job
    """
    from lib.queue_manager import load_session_jobs
    from lib.job_manager import JobStatus, update_job_status, get_session_jobs, get_redis_client
    import json
    import time
    
    # Try cache first (10 second TTL)
    cache_key = f"session_info_cache:{session_id}"
    if use_cache:
        try:
            redis_client = get_redis_client()
            cached = redis_client.get(cache_key)
            if cached:
                cached_data = json.loads(cached)
                # CRITICAL: Always recompute status from jobs to ensure accuracy
                # Cached status can be stale or missing, so we recompute it
                cached_session = cached_data.get("session")
                cached_jobs = cached_data.get("jobs", {})
                if cached_session and isinstance(cached_session, dict) and cached_jobs is not None:
                    try:
                        recomputed_status = compute_session_status(cached_session, cached_jobs)
                        if recomputed_status and isinstance(recomputed_status, str):
                            # CRITICAL: Ensure we're modifying the dict in cached_data, not a copy
                            cached_data["session"]['status'] = recomputed_status
                            logger.debug(f"✅ Cache HIT for session {session_id[:12]}... (status recomputed: {recomputed_status})")
                        else:
                            logger.debug(f"⚠️  Cache HIT but status recomputation failed, will reload")
                            cached_data = None  # Force reload
                    except Exception as status_err:
                        logger.debug(f"⚠️  Error recomputing status from cache: {status_err}, will reload")
                        cached_data = None  # Force reload
                else:
                    # Missing session or jobs in cache - force reload
                    logger.debug(f"⚠️  Cache HIT but missing session/jobs, will reload")
                    cached_data = None
                
                if cached_data:
                    return cached_data
        except Exception as e:
            logger.debug(f"Cache lookup failed (non-critical): {e}")
    
    # Cache miss - load from disk
    cache_load_start = time.time()
    session = load_session(session_id)
    session_jobs = load_session_jobs(session)
    session_jobs_queue_positions = dict()
    detailed_queue_info = {}
    
    # Check Celery active tasks to see which jobs are actually running
    # CRITICAL: Add timeout to prevent hanging if Celery workers don't respond
    active_task_ids = set()
    try:
        from celery_app import app
        # Use timeout parameter to prevent hanging (1 second max)
        # If workers don't respond, this will return None/empty dict instead of hanging
        inspect = app.control.inspect(timeout=1.0)
        active = inspect.active() or {}
        for worker, tasks in active.items():
            if tasks:  # Check if tasks list exists and is not empty
                for task in tasks:
                    task_id = task.get('id')
                    if task_id:
                        active_task_ids.add(task_id)
    except Exception as e:
        # Celery inspection failed or timed out - continue without it (non-critical)
        logger.debug(f"Celery inspection failed/timed out (non-critical): {type(e).__name__}: {e}")
        pass
    
    # Process each job - collect job IDs to remove (deleted placeholders)
    jobs_to_remove = []
    
    for job_id, job in session_jobs.items():
        job_type = job.get("job_type") or job.get("type")
        
        # CRITICAL: Add 'type' alias for client compatibility
        # Clients expect 'type' but we save as 'job_type' in Redis
        if job_type and 'type' not in job:
            job['type'] = job_type
        
        # CRITICAL: Ensure 'progress' field exists for client progress bars
        # Default to 0 if not present (newly created jobs)
        if 'progress' not in job:
            job['progress'] = 0
        
        job_status = job.get("status")
        
        # Handle JobStatus enum - convert to string value immediately
        if isinstance(job_status, JobStatus):
            job_status_value = job_status.value
            job['status'] = job_status_value  # CRITICAL: Update the dict to use string value
        elif hasattr(job_status, 'value'):
            job_status_value = job_status.value
            job['status'] = job_status_value  # CRITICAL: Update the dict to use string value
        else:
            job_status_value = str(job_status) if job_status else "ready"  # Default to "ready" instead of "unknown"
            job['status'] = job_status_value  # CRITICAL: Ensure it's always a string
        
        # Skip deleted/placeholder jobs immediately - these are job IDs in job_plan that don't exist in Redis
        # They clutter the response and confuse clients
        if job_status_value == "deleted" or job_status == "deleted":
            # Mark for removal - don't include these in the response at all
            jobs_to_remove.append(job_id)
            logger.debug(f"⏭️  Skipping deleted/placeholder job {job_id} (not in Redis)")
            continue
        
        # Aggregate movie frame jobs into summary (don't show individual jobs to client)
        # These are background visualization jobs - show aggregated progress instead
        if job_type == 'project_training_movie_frame':
            jobs_to_remove.append(job_id)  # Remove from main jobs list
            # We'll add aggregated summary later
            continue
        
        # Check if job is actually running in Celery (even if status says READY)
        is_running_in_celery = job_id in active_task_ids
        
        # CRITICAL: Check if job has actually completed by looking for output files
        # This detects jobs that completed but status wasn't updated in Redis
        job_completed_by_files = False
        if job_status_value in ["ready", "running"] and not is_running_in_celery:
            # Job says ready/running but not in Celery - check if output files exist
            try:
                from lib.job_manager import get_job_output_path
                session_id_for_check = session.get('session_id') or session_id
                job_output_dir = get_job_output_path(job_id, session_id=session_id_for_check, job_type=job_type)
                
                # Check for completion indicators based on job type
                if job_type == "create_structured_data":
                    # Check for embedding_space.db or data.db
                    if (job_output_dir / "embedding_space.db").exists() or (job_output_dir / "data.db").exists():
                        job_completed_by_files = True
                        logger.info(f"🔧 Detected completed job {job_id} (create_structured_data): output files exist")
                elif job_type == "train_es":
                    # Check for embedding_space.pickle (using canonical find function)
                    es_pickle = find_embedding_space_pickle(job_output_dir)
                    if es_pickle:
                        job_completed_by_files = True
                        logger.info(f"🔧 Detected completed job {job_id} (train_es): {es_pickle.name} exists")
                elif job_type == "train_knn":
                    # Check for vector_db in job directory OR in session (train_knn updates session with vector_db path)
                    vector_db_in_dir = (job_output_dir / "vector_db").exists() or list(job_output_dir.glob("*.index"))
                    vector_db_in_session = session.get('vector_db') is not None
                    
                    if vector_db_in_dir or vector_db_in_session:
                        job_completed_by_files = True
                        if vector_db_in_dir:
                            logger.info(f"🔧 Detected completed job {job_id} (train_knn): vector_db files exist in job directory")
                        if vector_db_in_session:
                            logger.info(f"🔧 Detected completed job {job_id} (train_knn): vector_db found in session: {session.get('vector_db')}")
                elif job_type == "run_clustering":
                    # Check for projections JSON or preview PNG
                    # These files are created in the job directory or can be detected via session
                    if (job_output_dir / "embedded_space_projections.json").exists() or \
                       (job_output_dir / "sphere_preview.png").exists() or \
                       list(job_output_dir.glob("*.json")) or \
                       list(job_output_dir.glob("*preview*.png")):
                        job_completed_by_files = True
                        logger.info(f"🔧 Detected completed job {job_id} (run_clustering): output files exist")
                elif job_type == "pre_analysis_architecture":
                    # Check for analysis output files
                    if (job_output_dir / "analysis.json").exists() or \
                       list(job_output_dir.glob("analysis*.json")):
                        job_completed_by_files = True
                        logger.info(f"🔧 Detected completed job {job_id} (pre_analysis_architecture): analysis files exist")
            except Exception as e:
                # If we can't find the output directory, that's okay - job might not have started yet
                logger.debug(f"Could not check output files for job {job_id}: {e}")
        
        # CRITICAL: If job is actually running in Celery but status says "ready", update the status
        # This fixes the issue where jobs are running but status isn't updated in Redis yet
        if is_running_in_celery:
            # Job is detected as running in Celery - always update status to running
            # Check current status for logging, but always update if running in Celery
            current_status_str = str(job_status_value).lower()
            if current_status_str != "running":
                # Job is actually running - update the status in Redis AND the returned dict
                try:
                    update_job_status(job_id, JobStatus.RUNNING)
                    logger.info(f"🔧 Updated job {job_id} status in Redis: {current_status_str} → running (detected in Celery active tasks)")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to update job {job_id} status in Redis: {e}")
                    # Still update the returned dict even if Redis update fails
                
                # Update the status in the returned dict
                job['status'] = JobStatus.RUNNING.value
                job_status = JobStatus.RUNNING
                job_status_value = JobStatus.RUNNING.value
        
        # CRITICAL: If job completed but status wasn't updated, fix it
        elif job_completed_by_files:
            # Job has output files indicating completion - update status to done
            try:
                update_job_status(job_id, JobStatus.DONE)
                logger.info(f"🔧 Updated job {job_id} status in Redis: {job_status_value} → done (detected completion via output files)")
            except Exception as e:
                logger.warning(f"⚠️  Failed to update job {job_id} status in Redis: {e}")
            
            # Update the status in the returned dict
            job['status'] = JobStatus.DONE.value
            job_status = JobStatus.DONE
            job_status_value = JobStatus.DONE.value
        
        # Skip deleted/placeholder jobs - these are job IDs in job_plan that don't exist in Redis
        # They clutter the response and confuse clients
        if job_status_value == "deleted" or job_status == "deleted":
            # Don't include these in the response at all - they're just stale job IDs
            logger.debug(f"⏭️  Skipping deleted/placeholder job {job_id} (not in Redis)")
            continue
        
        # Celery doesn't have queue positions - jobs are either waiting, running, or done
        session_jobs_queue_positions[job_id] = None
        
        # Collect detailed information
        # Use the updated job_status_value (which may have been corrected above)
        detailed_info = {
            "position": None,  # Not applicable for Celery
            "status": job_status_value,  # This should be "running" if job was detected as running
            "queue_name": job_type or "unknown",
        }
        
        # Add detailed status information based on job state
        if is_running_in_celery or (job_status == JobStatus.RUNNING) or (job_status_value == JobStatus.RUNNING.value) or (job_status_value == "running"):
            # Job is currently running
            started_at = job.get("started_at")
            progress = job.get("progress", 0)
            
            detailed_info.update({
                "queue_status": "running",
                "started_at": convert_to_iso(started_at) if started_at else None,
                "progress": progress,
                "progress_percent": round(progress * 100, 1) if progress else 0,
                "estimated_wait_message": "Currently running",
                "current_epoch": job.get("current_epoch"),
                "current_loss": job.get("current_loss"),
                "validation_loss": job.get("validation_loss"),
            })
            
            # Add pre-analysis specific fields if this is a pre-analysis job
            if job_type == "pre_analysis_architecture":
                status_message = job.get("status_message", "Pre-analysis architecture search in progress...")
                current_config = job.get("current_config", 0)
                total_configs = job.get("total_configs", 0)
                current_auc = job.get("current_auc")
                best_config_so_far = job.get("best_config_so_far")
                best_auc_so_far = job.get("best_auc_so_far")
                
                detailed_info.update({
                    "status_message": status_message,
                    "current_config": current_config,
                    "total_configs": total_configs,
                    "current_auc": current_auc,
                    "best_config_so_far": best_config_so_far,
                    "best_auc_so_far": best_auc_so_far,
                })
                
                # Build a more informative wait message for pre-analysis
                if current_config > 0 and total_configs > 0:
                    wait_msg = f"Testing config {current_config}/{total_configs}"
                    if current_auc is not None:
                        wait_msg += f" (AUC: {current_auc:.4f})"
                    if best_config_so_far and best_auc_so_far is not None:
                        wait_msg += f" | Best: d_model={best_config_so_far.get('d_model')}, layers={best_config_so_far.get('n_transformer_layers')}, heads={best_config_so_far.get('n_attention_heads')} (AUC: {best_auc_so_far:.4f})"
                    detailed_info["estimated_wait_message"] = wait_msg
                elif status_message:
                    detailed_info["estimated_wait_message"] = status_message
            
        elif (job_status == JobStatus.READY) or (job_status_value == JobStatus.READY.value) or (job_status_value == "ready"):
            # Job is ready/waiting to be picked up
            detailed_info.update({
                "queue_status": "waiting",
                "estimated_wait_message": "Waiting for worker to pick up",
                "worker_available": True,  # Simplified
            })
            
        elif (job_status == JobStatus.DONE) or (job_status_value == JobStatus.DONE.value) or (job_status_value == "done"):
            finished_at = job.get("finished_at")
            detailed_info.update({
                "queue_status": "completed",
                "finished_at": convert_to_iso(finished_at) if finished_at else None,
                "estimated_wait_message": "Completed successfully",
                "progress_percent": 100,
            })
            
        elif (job_status == JobStatus.FAILED) or (job_status_value == JobStatus.FAILED.value) or (job_status_value == "failed"):
            finished_at = job.get("finished_at")
            # Preserve error information from job metadata
            error_info = job.get("error") or job.get("failure_reason") or "Job failed - check logs"
            detailed_info.update({
                "queue_status": "failed",
                "finished_at": convert_to_iso(finished_at) if finished_at else None,
                "estimated_wait_message": error_info[:200] if isinstance(error_info, str) else "Job failed - check logs",
                "progress_percent": 0,
            })
            # CRITICAL: Preserve error and failure_reason fields in the job dict for client access
            # These fields are needed by clients to display meaningful error messages
            if "error" not in job and job.get("failure_reason"):
                job["error"] = job["failure_reason"]
            if "failure_reason" not in job and job.get("error"):
                job["failure_reason"] = job["error"]
        
        elif (job_status == JobStatus.PAUSED) or (job_status_value == JobStatus.PAUSED.value) or (job_status_value == "paused"):
            paused_at = job.get("paused_at")
            pause_reason = job.get("pause_reason", "Paused by user")
            detailed_info.update({
                "queue_status": "paused",
                "paused_at": paused_at,
                "pause_reason": pause_reason,
                "estimated_wait_message": f"Job paused: {pause_reason}",
                "progress_percent": job.get("progress", 0) * 100 if job.get("progress") else 0,
            })
        
        detailed_queue_info[job_id] = detailed_info
    
    # Remove deleted/placeholder jobs from the response
    for job_id in jobs_to_remove:
        session_jobs.pop(job_id, None)
        detailed_queue_info.pop(job_id, None)
        session_jobs_queue_positions.pop(job_id, None)
    
    # Normalize job status values to strings (for backward compatibility)
    for job_id, job in session_jobs.items():
        job_status = job.get("status")
        if isinstance(job_status, JobStatus):
            job['status'] = job_status.value
        elif job_status:
            job['status'] = str(job_status)
    
    # DYNAMIC STATUS COMPUTATION - Session status is NO LONGER STORED
    # Instead, it's computed on-the-fly from job statuses (single source of truth)
    # This eliminates synchronization bugs where job status != session status
    try:
        computed_status = compute_session_status(session, session_jobs)
        # Defensive: ensure computed_status is always a valid string
        if not computed_status or not isinstance(computed_status, str):
            logger.warning(f"⚠️  compute_session_status returned invalid value: {computed_status}, defaulting to 'ready'")
            computed_status = SessionStatus.READY.value
    except Exception as e:
        logger.error(f"❌ Error computing session status: {e}")
        logger.debug(traceback.format_exc())
        computed_status = SessionStatus.READY.value
    
    # Store the computed status in the session dict for API responses
    # but DON'T save it to the session file
    session['status'] = computed_status
    
    # Log status transitions for debugging (but don't write to file)
    stored_status = session.get("_last_computed_status", "unknown")
    if computed_status != stored_status:
        logger.debug(f"🔧 Session {session_id} computed status: {stored_status} → {computed_status}")
        session['_last_computed_status'] = computed_status

    # Create aggregated movie frame progress from individual movie frame jobs
    movie_frame_summary = None
    if session_id:
        try:
            # Get all movie frame jobs for this session from Redis
            redis_jobs = get_session_jobs(session_id)
            movie_frame_jobs = [j for j in redis_jobs if j.get('job_type') == 'project_training_movie_frame']
            
            if movie_frame_jobs:
                total_frames = len(movie_frame_jobs)
                done_frames = len([j for j in movie_frame_jobs if j.get('status') == JobStatus.DONE.value or j.get('status') == 'done'])
                failed_frames = len([j for j in movie_frame_jobs if j.get('status') == JobStatus.FAILED.value or j.get('status') == 'failed'])
                running_frames = len([j for j in movie_frame_jobs if j.get('status') == JobStatus.RUNNING.value or j.get('status') == 'running'])
                
                # Calculate progress percentage
                progress_pct = (done_frames / total_frames * 100) if total_frames > 0 else 0
                
                # Determine overall status
                if done_frames == total_frames:
                    overall_status = 'done'
                elif running_frames > 0:
                    overall_status = 'running'
                elif failed_frames > 0 and done_frames == 0:
                    overall_status = 'failed'
                else:
                    overall_status = 'ready'
                
                movie_frame_summary = {
                    'job_id': 'movie_frames_summary',  # Virtual job ID
                    'type': 'training_movie_generation',
                    'status': overall_status,
                    'progress': progress_pct,
                    'frames_total': total_frames,
                    'frames_done': done_frames,
                    'frames_failed': failed_frames,
                    'frames_running': running_frames,
                    'description': f'Rendering training movie: {done_frames}/{total_frames} frames',
                }
                
                # Add to jobs dict as a virtual job
                session_jobs['movie_frames_summary'] = movie_frame_summary
                logger.debug(f"✅ Aggregated {total_frames} movie frame jobs into summary: {done_frames} done, {failed_frames} failed")
        except Exception as agg_err:
            logger.warning(f"⚠️  Failed to aggregate movie frame jobs: {agg_err}")
    
    # Automatically extract and add __featrix metadata fields to session
    # These are used by clients for tracking and webhook callbacks
    if "metadata" not in session:
        session["metadata"] = {}
    
    metadata = session["metadata"]
    
    # Extract __featrix_es_id from embedding_space path if available
    if "__featrix_es_id" not in metadata or not metadata.get("__featrix_es_id"):
        embedding_space_path = session.get("embedding_space")
        
        # If embedding_space is not set, try to find it from foundation_model_id or predictor path
        if not embedding_space_path:
            # Try to get from foundation_model_id (for single predictor sessions)
            foundation_model_id = session.get("foundation_model_id")
            if foundation_model_id:
                try:
                    # Use load_session from this module (already imported at top)
                    foundation_session = load_session(foundation_model_id)
                    embedding_space_path = foundation_session.get("embedding_space")
                    if embedding_space_path:
                        logger.debug(f"✅ Found embedding_space from foundation_model_id: {embedding_space_path}")
                except Exception as e:
                    logger.debug(f"Could not load foundation session {foundation_model_id}: {e}")
            
            # If still not found, try to extract from single predictor path
            if not embedding_space_path:
                single_predictor = session.get("single_predictor")
                if single_predictor:
                    try:
                        from pathlib import Path
                        predictor_path = resolve_session_path(session_id, single_predictor)
                        # Look for embedding_space in the predictor's directory or parent
                        predictor_dir = Path(predictor_path).parent
                        # Check common locations for embedding space
                        es_pickle = find_embedding_space_pickle(predictor_dir)
                        if es_pickle:
                            embedding_space_path = str(es_pickle)
                            logger.debug(f"✅ Found embedding_space near predictor: {embedding_space_path}")
                        else:
                            # Check parent directory
                            es_pickle = find_embedding_space_pickle(predictor_dir.parent)
                            if es_pickle:
                                embedding_space_path = str(es_pickle)
                                logger.debug(f"✅ Found embedding_space near predictor: {embedding_space_path}")
                            # Also check for .pth checkpoint
                            elif (predictor_dir / "foundation_training_state_BEST.pth").exists():
                                embedding_space_path = str(predictor_dir / "foundation_training_state_BEST.pth")
                                logger.debug(f"✅ Found embedding_space checkpoint near predictor: {embedding_space_path}")
                    except Exception as e:
                        logger.debug(f"Could not find embedding_space from predictor path: {e}")
        
        if embedding_space_path:
            try:
                from pathlib import Path
                # Extract ES ID from path (filename without extension)
                es_path_obj = Path(embedding_space_path)
                es_id = es_path_obj.stem  # Gets filename without extension
                if es_id:
                    metadata["__featrix_es_id"] = es_id
                    logger.debug(f"✅ Auto-extracted __featrix_es_id from embedding_space path: {es_id}")
            except Exception as e:
                logger.debug(f"Could not extract __featrix_es_id from path {embedding_space_path}: {e}")
        else:
            # Set to null explicitly if no embedding_space path found
            metadata["__featrix_es_id"] = None
    
    # Ensure __featrix_session_id is set
    if "__featrix_session_id" not in metadata:
        metadata["__featrix_session_id"] = session.get("session_id", session_id)
    
    # Ensure __featrix_model_id is set (for single predictor sessions, this is the session_id)
    if "__featrix_model_id" not in metadata:
        metadata["__featrix_model_id"] = session.get("session_id", session_id)
    
    # CRITICAL: Ensure session status is always set before creating result
    # Double-check that status is set (defensive programming)
    # Also log what we're computing for debugging
    current_status = session.get('status')
    if 'status' not in session or not current_status or current_status == 'unknown':
        try:
            # Recompute if missing or invalid
            recomputed = compute_session_status(session, session_jobs)
            if recomputed and isinstance(recomputed, str) and recomputed != 'unknown':
                session['status'] = recomputed
                logger.debug(f"🔧 Recomputed session {session_id[:12]} status: {current_status} → {recomputed} (jobs: {len(session_jobs)})")
            else:
                # Fallback: if all jobs are done and we have outputs, status should be "done"
                if not session_jobs and (session.get('embedding_space') or session.get('single_predictors')):
                    session['status'] = SessionStatus.DONE.value
                    logger.debug(f"🔧 Set session {session_id[:12]} status to 'done' (no jobs in Redis but has outputs)")
                else:
                    session['status'] = SessionStatus.READY.value
                    logger.debug(f"🔧 Set session {session_id[:12]} status to 'ready' (fallback)")
        except Exception as e:
            logger.error(f"❌ Error recomputing status for session {session_id[:12]}: {e}")
            # Fallback: if all jobs are done and we have outputs, status should be "done"
            if not session_jobs and (session.get('embedding_space') or session.get('single_predictors')):
                session['status'] = SessionStatus.DONE.value
            else:
                session['status'] = SessionStatus.READY.value
    
    result = {
        "session": session,
        "jobs": session_jobs,
        "job_queue_positions": session_jobs_queue_positions,
        "detailed_queue_info": detailed_queue_info,
    }
    
    # Store in cache with adaptive TTL based on session activity
    if use_cache:
        try:
            redis_client = get_redis_client()
            
            # Determine cache TTL based on session state
            # - Active sessions (RUNNING jobs): 5 seconds (fast updates)
            # - Recent sessions (modified < 1 hour ago): 60 seconds
            # - Stable sessions (completed, old): 3600 seconds (1 hour)
            has_running_jobs = any(
                job.get('status') in ['running', JobStatus.RUNNING.value, 'ready', JobStatus.READY.value]
                for job in session_jobs.values()
            )
            
            # Check session file modification time
            session_path = config.session_dir / f"{session_id}.session"
            is_recent = False
            if session_path.exists():
                mtime = session_path.stat().st_mtime
                age_seconds = time.time() - mtime
                is_recent = age_seconds < 3600  # Modified in last hour
            
            if has_running_jobs:
                cache_ttl = 5  # Active sessions - short TTL
            elif is_recent:
                cache_ttl = 60  # Recently modified - medium TTL
            else:
                cache_ttl = 3600  # Stable/completed - long TTL (1 hour)
            
            redis_client.setex(cache_key, cache_ttl, json.dumps(result, default=str))
            cache_load_time = time.time() - cache_load_start
            logger.debug(f"💾 Cached session_info for {session_id[:12]}... (TTL={cache_ttl}s, running={has_running_jobs}, recent={is_recent}, load_time={cache_load_time:.2f}s)")
        except Exception as cache_err:
            logger.debug(f"Failed to cache session_info (non-critical): {cache_err}")
    
    return result


def iterate_over_sessions():
    """Iterate over all sessions from Redis (primary source of truth)."""
    redis_client = get_session_redis_client()
    if not redis_client:
        logger.warning("⚠️  Redis not available - cannot iterate over sessions")
        return
    
    try:
        # Get all session keys from Redis
        session_keys = redis_client.keys("session:*")
        
        for session_key in session_keys:
            # Extract session_id from key (format: "session:{session_id}")
            session_id = session_key.replace("session:", "", 1)
            
            try:
                yield load_session(session_id)
            except (ValueError, json.JSONDecodeError) as e:
                # Skip corrupted sessions
                logger.warning(f"⚠️  Skipping corrupted session {session_id}: {e}")
                continue
            except Exception as e:
                logger.warning(f"⚠️  Error loading session {session_id}: {e}")
                continue
    except Exception as e:
        logger.error(f"❌ Error iterating over sessions from Redis: {e}")
        raise


# ============================================================================
# Exception Classes
# ============================================================================

class NodeUpgradingException(Exception):
    """Exception raised when a node is currently upgrading and cannot accept training requests."""
    pass


# ============================================================================
# Helper Functions
# ============================================================================

def ensure_directories_exist():
    """Ensure all necessary featrix directories exist."""
    directories_to_create = [
        config.output_dir, 
        config.data_dir,
        config.session_dir,
    ]
    
    for directory in directories_to_create:
        if directory and not directory.exists():
            logger.info(f"Creating directory: {directory}")
            directory.mkdir(parents=True, exist_ok=True)


def get_version_info() -> dict:
    """Get version information for tracking in jobs and recovery info."""
    try:
        from version import get_version
        version_info = get_version()
        version_dict = version_info.dict()
        return {
            "version": version_dict.get("semantic_version", "unknown"),
            "git_hash": version_dict.get("git_hash"),
            "git_date": version_dict.get("git_date"),
        }
    except Exception as e:
        logger.warning(f"Failed to get version info: {e}")
        return {
            "version": "unknown",
            "git_hash": None,
            "git_date": None,
        }


def _generate_wait_message(position: int, running_jobs: list, job_type: str) -> str:
    """Generate a human-readable wait message for a job in queue."""
    if position is None:
        return "Position unknown"
    
    if position == 0:
        if running_jobs:
            return f"Next in queue (1 job currently running)"
        else:
            return "Next in queue (will start soon)"
    
    ahead = position
    running = len(running_jobs)
    
    if running > 0:
        return f"Position {position + 1} in queue ({ahead} jobs ahead, {running} running)"
    else:
        return f"Position {position + 1} in queue ({ahead} jobs ahead)"


# ============================================================================
# Session Creation Functions
# ============================================================================

def create_sphere_session(session_id: str, created_at: datetime, input_filename: str | None = None, name: str = None, single_predictors: list = None, epochs: int = None, column_overrides: dict = None, string_list_delimiter: str = "|", movie_frame_interval: int = 3, weightwatcher_save_every: int = 5, important_columns_for_visualization: list = None, user_metadata: dict = None, target_column: str = None):
    """Create a sphere session (embedding space + optional predictors)."""
    # Allow sphere sessions without input_filename for testing/API usage
    if not input_filename:
        logger.info(f"Creating sphere session {session_id} without input file (API/testing mode)")
        input_filename = "api_created_session.csv"  # Placeholder filename
    single_predictors = single_predictors or []
    important_columns_for_visualization = important_columns_for_visualization or []

    # Import here to avoid circular dependencies
    from lib.sphere_config import get_row_limit
    
    # Get row limit from config
    default_row_limit = get_row_limit()

    # Build job plan with basic sphere jobs
    job_plan = [
        dict(
            job_type="create_structured_data",
            spec={
                "column_overrides": column_overrides or {},
                "string_list_delimiter": string_list_delimiter,
            },
            job_id=None,
        ),
        dict(
            job_type="pre_analysis_architecture",
            spec={
                "n_samples": 20,  # Test 20 random configs
                "quick_epochs": 25,  # 25 epochs for quick search
                "target_column_hint": target_column,  # Optional: hint for target column selection/evaluation
            },
            job_id=None,
        ),
        dict(
            job_type= "train_es",
            spec={
                # Use provided epochs or default to auto-calculate
                "epochs": epochs if epochs is not None else 0,
                # Row limit from config (customizable via /sphere/app/config.json)
                "row_limit": default_row_limit,
                "is_production": True,
                "ignore_cols": [],
                "batch_size": 0,  # Auto-calculate based on dataset size
                # DropoutScheduler parameters
                # "enable_dropout_scheduler": True,
                # "dropout_schedule_type": "linear_decay",
                # "initial_dropout": 0.5,
                # "final_dropout": 0.1,
                # # Movie frame and WeightWatcher intervals (configurable via API)
                # "movie_frame_interval": movie_frame_interval,
                # "weightwatcher_save_every": weightwatcher_save_every,
                # VISUALIZATION ONLY: Prefer rows with non-null values in these columns for epoch projections
                # ⚠️ IMPORTANT: Has NO EFFECT on model training, only affects visualization sampling
                "important_columns_for_visualization": important_columns_for_visualization,
                # User metadata for identification
                "user_metadata": user_metadata,
            },
            job_id=None,
        ),
        dict(
            job_type="train_knn",
            spec={},
            job_id=None,
        ),
        dict(
            job_type="run_clustering",
            spec={},
            job_id=None,
        ), 
    ]
    
    # Add single predictor training jobs to the plan
    single_predictors_artifacts = []
    training_metrics_artifacts = []
    
    for i, predictor_spec in enumerate(single_predictors):
        # Convert pydantic model to dict if needed
        if hasattr(predictor_spec, 'dict'):
            spec_dict = predictor_spec.dict()
        else:
            spec_dict = predictor_spec
        
        # Add user_metadata to predictor spec if not already present
        if user_metadata and 'user_metadata' not in spec_dict:
            spec_dict['user_metadata'] = user_metadata
            
        # Add job to plan
        job_plan.append(dict(
            job_type="train_single_predictor",
            spec=spec_dict,
            job_id=None,
            predictor_index=i,  # Track which predictor this is
        ))
        
        # Initialize artifact paths (will be filled when jobs complete)
        single_predictors_artifacts.append(None)
        training_metrics_artifacts.append(None)

    session_doc = dict(
        created_at=created_at,
        session_type="sphere",
        session_id=session_id,
        name=name,  # Optional name for identification and metadata
        # NOTE: status is NO LONGER STORED - it's computed dynamically from job statuses
        # See compute_session_status() in this file
        job_plan=job_plan,
        # Paths to artifacts that are shared across jobs.
        input_data=input_filename,
        embedding_space=None,
        sqlite_db=None,
        vector_db=None,
        projections=None,
        preview_png=None,
        strings_cache=None,
        # Support multiple single predictors
        single_predictors=single_predictors_artifacts,
        training_metrics=training_metrics_artifacts,
        # User metadata for identification
        user_metadata=user_metadata,
    )

    return session_doc


def create_cloned_session(session_id: str, created_at: datetime, embedding_space_path: str, strings_cache_path: str | None = None,
                         source_session_id: str = None, source_compute: str = None, validation_loss: float | None = None,
                         epoch: int | None = None, training_metadata: dict | None = None, name: str | None = None) -> dict:
    """Create a ready session from a cloned embedding space."""
    session_doc = dict(
        created_at=created_at,
        session_type="sphere",
        session_id=session_id,
        name=name,
        job_plan=[],  # Empty - session is ready to use
        input_data=None,  # No input data for cloned sessions
        embedding_space=embedding_space_path,
        sqlite_db=None,
        vector_db=None,
        projections=None,
        preview_png=None,
        strings_cache=strings_cache_path,
        single_predictors=[],
        training_metrics=[],
        clone_metadata={
            "source_session_id": source_session_id,
            "source_compute": source_compute,
            "validation_loss": validation_loss,
            "epoch": epoch,
            "training_metadata": training_metadata,
            "cloned_at": created_at.isoformat() if created_at else None,
        }
    )
    
    return session_doc


def create_embedding_space_session(name: str, s3_training_path: str, s3_validation_path: str, session_id: str = None, user_metadata: dict = None):
    """Create a session specifically for training an embedding space from S3 datasets."""
    # Check if node is upgrading
    upgrade_lock_file = Path("/tmp/auto-upgrade.lock")
    if upgrade_lock_file.exists():
        hostname = socket.gethostname()
        raise NodeUpgradingException(f"Node {hostname} is currently upgrading and cannot accept training requests. Please try again in a few minutes or use a different node.")

    # Ensure all necessary directories exist before creating sessions
    ensure_directories_exist()

    created_at = datetime.now(tz=ZoneInfo("America/New_York"))

    if session_id is None:
        unique_string = str(uuid4())[:6]
        session_timestamp = created_at.strftime('%Y%m%d-%H%M%S')
        # New format: {uuid}-{yyyy}{mm}{dd}-{hh}{mm}{ss}
        session_id = f"{unique_string}-{session_timestamp}"

    # Create job plan for embedding space training
    job_plan = [
        {
            "job_type": "create_structured_data",
            "spec": {
                "s3_training_dataset": s3_training_path,
                "s3_validation_dataset": s3_validation_path,
                "name": name
            },
            "job_id": None,
        },
        {
            "job_type": "train_es",
            "spec": {
                "user_metadata": user_metadata,
            },
            "job_id": None,
        },
        {
            "job_type": "train_knn",
            "spec": {},
            "job_id": None,
        },
        {
            "job_type": "run_clustering",
            "spec": {},
            "job_id": None,
        }
    ]

    # Create session directory and data path
    # New structure: es_train/{session_id}/
    es_train_dir = config.data_dir / "es_train"
    es_train_dir.mkdir(parents=True, exist_ok=True)
    session_dir = es_train_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # For embedding space sessions, the data will be downloaded by the first job
    input_data_path = session_dir / f"{name}_training_data.csv"

    session_doc = {
        "session_id": session_id,
        "session_type": "embedding_space",
        "name": name,
        "status": SessionStatus.READY,  # Removed by serialize_session() before saving
        "created_at": created_at,
        "input_data": str(input_data_path),
        "s3_training_dataset": s3_training_path,
        "s3_validation_dataset": s3_validation_path,
        "job_plan": job_plan,
        "projected_points": str(session_dir / "projection.json"),
        "preview_png": str(session_dir / "preview.png"),
        "embedding_space": str(session_dir / "embedding_space.json"),
        "sqlite_db": str(session_dir / "embedding_space.db"),
        "vector_db": str(session_dir / "vector_db.lance"),
        "projections": str(session_dir / "projections.json"),
        "strings_cache": str(session_dir / "strings_cache.pkl"),
        "user_metadata": user_metadata,  # User metadata for identification
    }

    return session_doc


def create_fine_tune_embedding_space_session(
    name: str,
    parent_session_id: str | None = None,
    parent_embedding_space_path: str | None = None,
    s3_training_path: str = None,
    s3_validation_path: str = None,
    session_id: str = None,
    user_metadata: dict = None
):
    """Create a session for fine-tuning an existing embedding space on new data."""
    logger.info(f"🔧 Creating fine-tuning session for embedding space: {name}")
    
    # Check if node is upgrading
    upgrade_lock_file = Path("/tmp/auto-upgrade.lock")
    if upgrade_lock_file.exists():
        hostname = socket.gethostname()
        raise NodeUpgradingException(f"Node {hostname} is currently upgrading and cannot accept training requests. Please try again in a few minutes or use a different node.")
    
    # Ensure all necessary directories exist
    ensure_directories_exist()
    
    created_at = datetime.now(tz=ZoneInfo("America/New_York"))
    
    if session_id is None:
        unique_string = str(uuid4())[:6]
        session_timestamp = created_at.strftime('%Y%m%d-%H%M%S')
        session_id = f"{unique_string}-{session_timestamp}"
    
    # Load parent embedding space to get original training info
    parent_es_path = None
    if parent_session_id:
        logger.info(f"📂 Loading parent embedding space from session: {parent_session_id}")
        parent_session = load_session(parent_session_id)
        if not parent_session:
            raise ValueError(f"Parent session {parent_session_id} not found")
        parent_es_path = parent_session.get("embedding_space")
        if not parent_es_path or not Path(parent_es_path).exists():
            raise FileNotFoundError(f"Parent embedding space not found at: {parent_es_path}")
    elif parent_embedding_space_path:
        parent_es_path = parent_embedding_space_path
        if not Path(parent_es_path).exists():
            raise FileNotFoundError(f"Parent embedding space not found at: {parent_embedding_space_path}")
    
    if not parent_es_path:
        raise ValueError("Either parent_session_id or parent_embedding_space_path must be provided")
    
    logger.info(f"📂 Loading parent embedding space from: {parent_es_path}")
    
    # Load the parent embedding space
    from featrix.neural.io_utils import load_embedded_space
    parent_es = load_embedded_space(parent_es_path, force_cpu=True)
    
    if not parent_es:
        raise ValueError(f"Failed to load parent embedding space from: {parent_es_path}")
    
    # Get original dataset size and epoch count
    original_train_size = len(parent_es.train_input_data) if hasattr(parent_es, 'train_input_data') else 0
    original_epochs = parent_es.n_epochs if hasattr(parent_es, 'n_epochs') and parent_es.n_epochs else 0
    
    # If n_epochs is not set, try to get from training_info
    if not original_epochs:
        training_info = getattr(parent_es, 'training_info', {})
        progress_info = training_info.get('progress_info', {})
        original_epochs = progress_info.get('epoch_total', 0)
        if not original_epochs:
            # Try to get from loss_history length
            loss_history = progress_info.get('loss_history', [])
            if loss_history:
                original_epochs = len(loss_history)
    
    logger.info(f"📊 Parent embedding space info:")
    logger.info(f"   Original training dataset size: {original_train_size} rows")
    logger.info(f"   Original epochs: {original_epochs}")
    
    if original_epochs == 0:
        logger.warning(f"⚠️  Could not determine original epoch count, defaulting to 100")
        original_epochs = 100
    
    # Download new datasets to get their sizes
    logger.info(f"📥 Downloading new datasets to calculate size...")
    
    import boto3
    import pandas as pd
    
    s3_client = boto3.client('s3')
    
    def download_and_count_rows(s3_url: str) -> int:
        """Download S3 file temporarily and count rows."""
        import tempfile
        import os
        
        # Parse S3 URL
        if not s3_url.startswith('s3://'):
            raise ValueError(f"Invalid S3 URL: {s3_url}")
        
        s3_path = s3_url[5:]  # Remove 's3://'
        bucket, key = s3_path.split('/', 1)
        
        # Download to temp file
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            try:
                s3_client.download_file(bucket, key, tmp_path)
                
                # Count rows (read CSV)
                df = pd.read_csv(tmp_path, nrows=0)  # Just get header
                # Count non-header rows by reading file
                with open(tmp_path, 'r') as f:
                    row_count = sum(1 for line in f) - 1  # Subtract header
                return row_count
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    try:
        new_train_size = download_and_count_rows(s3_training_path)
        new_val_size = download_and_count_rows(s3_validation_path)
        new_total_size = new_train_size + new_val_size
    except Exception as e:
        logger.warning(f"⚠️  Could not download datasets to count rows: {e}")
        logger.warning(f"   Will use default F=1.0 (same dataset size)")
        new_total_size = original_train_size
        new_train_size = int(original_train_size * 0.8)
        new_val_size = int(original_train_size * 0.2)
    
    logger.info(f"📊 New dataset info:")
    logger.info(f"   New training dataset size: {new_train_size} rows")
    logger.info(f"   New validation dataset size: {new_val_size} rows")
    logger.info(f"   New total size: {new_total_size} rows")
    
    # Calculate F = len(new_dataset) / len(old_dataset)
    F = new_total_size / original_train_size if original_train_size > 0 else 1.0
    logger.info(f"📐 Dataset size ratio F = {new_total_size} / {original_train_size} = {F:.4f}")
    
    # Calculate new epochs = original_epochs / F
    new_epochs = int(original_epochs / F) if F > 0 else original_epochs
    if new_epochs < 1:
        new_epochs = 1
    elif new_epochs > 1000:
        logger.warning(f"⚠️  Calculated epochs ({new_epochs}) is very high, capping at 1000")
        new_epochs = 1000
    
    logger.info(f"🎯 Fine-tuning will use {new_epochs} epochs (original: {original_epochs}, F: {F:.4f})")
    
    # Create job plan for fine-tuning
    job_plan = [
        {
            "job_type": "create_structured_data",
            "spec": {
                "s3_training_dataset": s3_training_path,
                "s3_validation_dataset": s3_validation_path,
                "name": name
            },
            "job_id": None,
        },
        {
            "job_type": "train_es",
            "spec": {
                "epochs": new_epochs,
                "parent_embedding_space_path": str(Path(parent_es_path).resolve()),
                "fine_tune": True,
                "user_metadata": user_metadata,
            },
            "job_id": None,
        },
        {
            "job_type": "train_knn",
            "spec": {},
            "job_id": None,
        },
        {
            "job_type": "run_clustering",
            "spec": {},
            "job_id": None,
        }
    ]
    
    # Create session directory
    es_train_dir = config.data_dir / "es_train"
    es_train_dir.mkdir(parents=True, exist_ok=True)
    session_dir = es_train_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    input_data_path = session_dir / f"{name}_training_data.csv"
    
    session_doc = {
        "session_id": session_id,
        "session_type": "embedding_space_finetune",
        "name": name,
        "status": SessionStatus.READY,  # Removed by serialize_session() before saving
        "created_at": created_at,
        "input_data": str(input_data_path),
        "s3_training_dataset": s3_training_path,
        "s3_validation_dataset": s3_validation_path,
        "parent_session_id": parent_session_id,
        "parent_embedding_space_path": str(Path(parent_es_path).resolve()),
        "fine_tune_info": {
            "original_train_size": original_train_size,
            "original_epochs": original_epochs,
            "new_train_size": new_train_size,
            "new_val_size": new_val_size,
            "new_total_size": new_total_size,
            "F": F,
            "calculated_epochs": new_epochs,
        },
        "job_plan": job_plan,
        "projected_points": str(session_dir / "projection.json"),
        "preview_png": str(session_dir / "preview.png"),
        "embedding_space": str(session_dir / "embedding_space.json"),
        "sqlite_db": str(session_dir / "embedding_space.db"),
        "vector_db": str(session_dir / "vector_db.lance"),
        "projections": str(session_dir / "projections.json"),
        "strings_cache": str(session_dir / "strings_cache.pkl"),
        "user_metadata": user_metadata,
    }
    
    logger.info(f"✅ Created fine-tuning session: {session_id}")
    
    return session_doc


def create_extend_embedding_space_session(
    name: str,
    parent_session_id: str | None = None,
    parent_embedding_space_path: str | None = None,
    s3_training_path: str = None,
    s3_validation_path: str = None,
    n_epochs: int | None = None,
    session_id: str = None,
    user_metadata: dict = None
):
    """Create a session for extending an existing embedding space with new feature columns."""
    logger.info(f"🔧 Creating extend ES session for: {name}")
    
    # Check if node is upgrading
    upgrade_lock_file = Path("/tmp/auto-upgrade.lock")
    if upgrade_lock_file.exists():
        hostname = socket.gethostname()
        raise NodeUpgradingException(f"Node {hostname} is currently upgrading and cannot accept training requests. Please try again in a few minutes or use a different node.")
    
    # Ensure all necessary directories exist
    ensure_directories_exist()
    
    created_at = datetime.now(tz=ZoneInfo("America/New_York"))
    
    if session_id is None:
        unique_string = str(uuid4())[:6]
        session_timestamp = created_at.strftime('%Y%m%d-%H%M%S')
        session_id = f"{unique_string}-{session_timestamp}"
    
    # Load parent embedding space
    parent_es_path = None
    if parent_session_id:
        logger.info(f"📂 Loading parent embedding space from session: {parent_session_id}")
        parent_session = load_session(parent_session_id)
        if not parent_session:
            raise ValueError(f"Parent session {parent_session_id} not found")
        parent_es_path = parent_session.get("embedding_space")
        if not parent_es_path or not Path(parent_es_path).exists():
            raise FileNotFoundError(f"Parent embedding space not found at: {parent_es_path}")
    elif parent_embedding_space_path:
        parent_es_path = parent_embedding_space_path
        if not Path(parent_es_path).exists():
            raise FileNotFoundError(f"Parent embedding space not found at: {parent_embedding_space_path}")
    
    if not parent_es_path:
        raise ValueError("Either parent_session_id or parent_embedding_space_path must be provided")
    
    logger.info(f"📂 Loading parent embedding space from: {parent_es_path}")
    
    # Load the parent embedding space
    from featrix.neural.io_utils import load_embedded_space
    parent_es = load_embedded_space(parent_es_path, force_cpu=True)
    
    if not parent_es:
        raise ValueError(f"Failed to load parent embedding space from: {parent_es_path}")
    
    # Get original epoch count
    original_epochs = parent_es.n_epochs if hasattr(parent_es, 'n_epochs') and parent_es.n_epochs else 100
    
    # If n_epochs not provided, use original_epochs / 4 (shorter training for extension)
    if n_epochs is None:
        n_epochs = max(1, original_epochs // 4)
    
    logger.info(f"📊 Extend ES info:")
    logger.info(f"   Original epochs: {original_epochs}")
    logger.info(f"   Extension epochs: {n_epochs}")
    
    # Create job plan for extending
    job_plan = [
        {
            "job_type": "create_structured_data",
            "spec": {
                "s3_training_dataset": s3_training_path,
                "s3_validation_dataset": s3_validation_path,
                "name": name
            },
            "job_id": None,
        },
        {
            "job_type": "extend_es",
            "spec": {
                "epochs": n_epochs,
                "parent_embedding_space_path": str(Path(parent_es_path).resolve()),
                "user_metadata": user_metadata,
            },
            "job_id": None,
        },
        {
            "job_type": "train_knn",
            "spec": {},
            "job_id": None,
        },
        {
            "job_type": "run_clustering",
            "spec": {},
            "job_id": None,
        }
    ]
    
    # Create session directory
    es_train_dir = config.data_dir / "es_train"
    es_train_dir.mkdir(parents=True, exist_ok=True)
    session_dir = es_train_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    input_data_path = session_dir / f"{name}_training_data.csv"
    
    session_doc = {
        "session_id": session_id,
        "session_type": "embedding_space_extend",
        "name": name,
        "status": SessionStatus.READY,
        "created_at": created_at,
        "input_data": str(input_data_path),
        "s3_training_dataset": s3_training_path,
        "s3_validation_dataset": s3_validation_path,
        "parent_session_id": parent_session_id,
        "parent_embedding_space_path": str(Path(parent_es_path).resolve()),
        "extend_es_info": {
            "original_epochs": original_epochs,
            "extension_epochs": n_epochs,
        },
        "job_plan": job_plan,
        "projected_points": str(session_dir / "projection.json"),
        "preview_png": str(session_dir / "preview.png"),
        "embedding_space": str(session_dir / "embedding_space.json"),
        "sqlite_db": str(session_dir / "embedding_space.db"),
        "vector_db": str(session_dir / "vector_db.lance"),
        "projections": str(session_dir / "projections.json"),
        "strings_cache": str(session_dir / "strings_cache.pkl"),
        "user_metadata": user_metadata,
    }
    
    logger.info(f"✅ Created extend ES session: {session_id}")
    
    return session_doc


def create_foundation_model_session(session_id: str, created_at: datetime, foundation_model_id: str, target_spec: dict, input_filename: str | None = None, name: str | None = None, user_metadata: dict | None = None):
    """Create a session that trains a predictor on a foundation model (existing embedding space)."""
    logger.info(f"🏗️  Creating foundation model session {session_id} based on foundation {foundation_model_id}")
    
    # Load the foundation model session to get its embedding space
    # Retry logic to handle race conditions where session might be saving/migrating
    foundation_session = None
    max_retries = 5
    retry_delay = 0.1  # Start with 100ms
    
    for attempt in range(max_retries):
        try:
            foundation_session = load_session(foundation_model_id)
            break  # Success - exit retry loop
        except FileNotFoundError as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️  Foundation model session {foundation_model_id} not found (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay:.2f}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff: 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
            else:
                # Last attempt failed - re-raise the exception
                logger.error(f"🔴 Failed to load foundation model session {foundation_model_id} after {max_retries} attempts")
                raise
    
    if foundation_session is None:
        raise FileNotFoundError(f"Foundation model session {foundation_model_id} does not exist")
    embedding_space_path = foundation_session.get("embedding_space")
    strings_cache_path = foundation_session.get("strings_cache")
    sqlite_db_path = foundation_session.get("sqlite_db")
    
    # Resolve to absolute path and validate
    if embedding_space_path:
        embedding_space_path = str(Path(embedding_space_path).resolve())
        if not Path(embedding_space_path).exists():
            logger.warning(f"⚠️  Embedding space not found at expected path: {embedding_space_path}")
            embedding_space_path = None  # Will trigger search below
    
    # If embedding_space_path is not set or doesn't exist, search for it
    if not embedding_space_path:
        logger.info(f"🔍 Searching for embedding space file for foundation model: {foundation_model_id}")
        
        # Strategy 1: Look for train_es job in foundation session's job_plan
        job_plan = foundation_session.get("job_plan", [])
        train_es_job = None
        for job in job_plan:
            if job.get("job_type") == "train_es":
                train_es_job = job
                break
        
        if train_es_job:
            job_id = train_es_job.get("job_id")
            foundation_session_id = foundation_session.get("session_id", foundation_model_id)
            if job_id and foundation_session_id:
                try:
                    from lib.job_manager import get_job_output_path
                    job_output_dir = get_job_output_path(job_id, foundation_session_id, "train_es")
                    
                    # Search for embedding space in common locations using canonical find function
                    es_pickle = find_embedding_space_pickle(job_output_dir)
                    if es_pickle:
                        embedding_space_path = str(es_pickle.resolve())
                        logger.info(f"✅ Found embedding space at: {embedding_space_path}")
                        foundation_session["embedding_space"] = embedding_space_path
                        save_session(foundation_model_id, foundation_session, exist_ok=True)
                    else:
                        # Also check best_model_package subdirectory
                        best_model_package_dir = job_output_dir / "best_model_package"
                        if best_model_package_dir.exists():
                            es_pickle = find_embedding_space_pickle(best_model_package_dir)
                            if es_pickle:
                                embedding_space_path = str(es_pickle.resolve())
                                logger.info(f"✅ Found embedding space at: {embedding_space_path}")
                                foundation_session["embedding_space"] = embedding_space_path
                                save_session(foundation_model_id, foundation_session, exist_ok=True)
                            # Also check for best_model.pickle as fallback
                            elif (best_model_package_dir / "best_model.pickle").exists():
                                embedding_space_path = str((best_model_package_dir / "best_model.pickle").resolve())
                                logger.info(f"✅ Found best_model.pickle at: {embedding_space_path}")
                                foundation_session["embedding_space"] = embedding_space_path
                                save_session(foundation_model_id, foundation_session, exist_ok=True)
                except Exception as e:
                    logger.warning(f"⚠️  Could not search job output directory: {e}")
        
        # Strategy 2: Search in featrix_output directory structure
        # Directory structure is: /featrix-output/{session_id}/train_es_{job_id}/
        if not embedding_space_path:
            featrix_output_dir = config.output_dir
            session_base_dir = featrix_output_dir / foundation_model_id
            
            logger.info(f"🔍 Searching for ES in session directory: {session_base_dir}")
            logger.info(f"   Directory exists: {session_base_dir.exists()}")
            
            # Search for train_es_* directories (job directories)
            if session_base_dir.exists():
                # Find all train_es_* directories (new structure)
                train_es_dirs = list(session_base_dir.glob("train_es_*"))
                logger.info(f"   Found {len(train_es_dirs)} train_es_* directories (new structure)")
                
                # Also check for old structure: train_es/{job_id}-{timestamp}/
                train_es_subdir = session_base_dir / "train_es"
                if train_es_subdir.exists() and train_es_subdir.is_dir():
                    old_structure_dirs = [d for d in train_es_subdir.iterdir() if d.is_dir()]
                    if old_structure_dirs:
                        logger.info(f"   Found {len(old_structure_dirs)} job directories in train_es/ subdirectory (old structure)")
                        train_es_dirs.extend(old_structure_dirs)
                for train_es_dir in train_es_dirs:
                    if train_es_dir.is_dir():
                        logger.info(f"   Searching in: {train_es_dir}")
                        # PREFER .pth checkpoints (small, fast) over pickles (huge, slow, fragile)
                        # Check .pth checkpoints FIRST (small and robust)
                        search_paths = [
                            train_es_dir / "training_state_BEST.pth",
                            train_es_dir / "embedding_space_checkpoint.pth",
                            train_es_dir / "best_model_package" / "best_model.pth",
                        ]
                        embedding_space_path = None
                        for search_path in search_paths:
                            logger.debug(f"      Checking: {search_path} (exists: {search_path.exists()})")
                            if search_path.exists():
                                embedding_space_path = str(search_path.resolve())
                                logger.info(f"✅ Found embedding space at: {embedding_space_path}")
                                break
                        
                        # If no .pth found, check for pickles using canonical find function
                        if not embedding_space_path:
                            es_pickle = find_embedding_space_pickle(train_es_dir)
                            if es_pickle:
                                embedding_space_path = str(es_pickle.resolve())
                                logger.info(f"✅ Found embedding space pickle at: {embedding_space_path}")
                            else:
                                # Check best_model_package subdirectory
                                best_model_package_dir = train_es_dir / "best_model_package"
                                if best_model_package_dir.exists():
                                    es_pickle = find_embedding_space_pickle(best_model_package_dir)
                                    if es_pickle:
                                        embedding_space_path = str(es_pickle.resolve())
                                        logger.info(f"✅ Found embedding space pickle at: {embedding_space_path}")
                                    # Also check for best_model.pickle as fallback
                                    elif (best_model_package_dir / "best_model.pickle").exists():
                                        embedding_space_path = str((best_model_package_dir / "best_model.pickle").resolve())
                                        logger.info(f"✅ Found best_model.pickle at: {embedding_space_path}")
                        
                        if embedding_space_path:
                                # If it's a .pth file, also check for metadata JSON (needed for reconstruction)
                                embedding_space_metadata = None
                                if search_path.suffix == '.pth':
                                    # Look for es_metadata JSON  
                                    metadata_paths = [
                                        search_path.parent / "metadata.json",  # Same directory as .pth
                                        search_path.parent / "embedding_space_metadata.json",
                                        search_path.parent / "es_metadata" / f"{search_path.stem}_metadata.json",
                                    ]
                                    for meta_path in metadata_paths:
                                        if meta_path.exists():
                                            logger.info(f"   ✅ Found ES metadata: {meta_path}")
                                            embedding_space_metadata = str(meta_path.resolve())
                                            break
                                # DON'T update foundation session - just use the path for new session
                                break
                        
                        # If BEST checkpoint not found, look for in-progress epoch checkpoints
                        if not embedding_space_path:
                            # Search for inference checkpoints (have full encoder + es_state)
                            epoch_checkpoints = sorted(train_es_dir.glob("checkpoint_inference_e-*.pt"))
                            if not epoch_checkpoints:
                                # Fallback to training_state checkpoints only
                                epoch_checkpoints = sorted(train_es_dir.glob("training_state_e-*.pth"))
                            if epoch_checkpoints:
                                # Use the latest epoch checkpoint
                                latest_checkpoint = epoch_checkpoints[-1]
                                embedding_space_path = str(latest_checkpoint.resolve())
                                logger.info(f"✅ Found in-progress epoch checkpoint: {embedding_space_path}")
                                logger.info(f"   Using latest of {len(epoch_checkpoints)} epoch checkpoints")
                                
                                # Look for metadata
                                embedding_space_metadata = None
                                metadata_paths = [
                                    latest_checkpoint.parent / "metadata.json",
                                    latest_checkpoint.parent / "embedding_space_metadata.json",
                                    latest_checkpoint.parent / "es_metadata" / f"{latest_checkpoint.stem}_metadata.json",
                                ]
                                for meta_path in metadata_paths:
                                    if meta_path.exists():
                                        logger.info(f"   ✅ Found ES metadata: {meta_path}")
                                        embedding_space_metadata = str(meta_path.resolve())
                                        break
                        
                        if embedding_space_path:
                            break
            else:
                logger.warning(f"   ⚠️  Session directory does not exist: {session_base_dir}")
        
        # Strategy 3: Search in backplane for foundation models trained on other hosts
        if not embedding_space_path:
            logger.info(f"🔍 Searching backplane for foundation model trained on another host")
            backplane_base = Path("/backplane/backplane1/sphere")
            
            if backplane_base.exists():
                # Get list of all hosts
                host_dirs = list(backplane_base.glob("host-*"))
                logger.info(f"   Found {len(host_dirs)} hosts in backplane: {[h.name for h in host_dirs]}")
                
                for host_dir in host_dirs:
                    # Skip if we already checked local
                    hostname = host_dir.name.replace("host-", "")
                    
                    # Check in host's featrix_output
                    host_output_dir = host_dir / "app" / "featrix_output" / foundation_model_id
                    
                    if host_output_dir.exists():
                        logger.info(f"   Found session directory on {hostname}: {host_output_dir}")
                        
                        # Search for train_es_* directories (new structure)
                        train_es_dirs = list(host_output_dir.glob("train_es_*"))
                        logger.info(f"   Found {len(train_es_dirs)} train_es_* directories on {hostname} (new structure)")
                        
                        # Also check for old structure: train_es/{job_id}-{timestamp}/
                        train_es_subdir = host_output_dir / "train_es"
                        if train_es_subdir.exists() and train_es_subdir.is_dir():
                            old_structure_dirs = [d for d in train_es_subdir.iterdir() if d.is_dir()]
                            if old_structure_dirs:
                                logger.info(f"   Found {len(old_structure_dirs)} job directories in train_es/ subdirectory on {hostname} (old structure)")
                                train_es_dirs.extend(old_structure_dirs)
                        
                        for train_es_dir in train_es_dirs:
                            if train_es_dir.is_dir():
                                logger.info(f"   Searching in: {train_es_dir}")
                                # PREFER .pth checkpoints over pickles
                                # Check .pth checkpoints FIRST (small and robust)
                                search_paths = [
                                    train_es_dir / "training_state_BEST.pth",
                                    train_es_dir / "embedding_space_checkpoint.pth",
                                    train_es_dir / "best_model_package" / "best_model.pth",
                                ]
                                embedding_space_path = None
                                for search_path in search_paths:
                                    logger.debug(f"      Checking: {search_path} (exists: {search_path.exists()})")
                                    if search_path.exists():
                                        embedding_space_path = str(search_path.resolve())
                                        logger.info(f"✅ Found embedding space on {hostname}: {embedding_space_path}")
                                        break
                                
                                # If no .pth found, check for pickles using canonical find function
                                if not embedding_space_path:
                                    es_pickle = find_embedding_space_pickle(train_es_dir)
                                    if es_pickle:
                                        embedding_space_path = str(es_pickle.resolve())
                                        logger.info(f"✅ Found embedding space pickle on {hostname}: {embedding_space_path}")
                                    else:
                                        # Check best_model_package subdirectory
                                        best_model_package_dir = train_es_dir / "best_model_package"
                                        if best_model_package_dir.exists():
                                            es_pickle = find_embedding_space_pickle(best_model_package_dir)
                                            if es_pickle:
                                                embedding_space_path = str(es_pickle.resolve())
                                                logger.info(f"✅ Found embedding space pickle on {hostname}: {embedding_space_path}")
                                            # Also check for best_model.pickle as fallback
                                            elif (best_model_package_dir / "best_model.pickle").exists():
                                                embedding_space_path = str((best_model_package_dir / "best_model.pickle").resolve())
                                                logger.info(f"✅ Found best_model.pickle on {hostname}: {embedding_space_path}")
                                
                                if embedding_space_path:
                                        # Check for metadata if .pth
                                        search_path = Path(embedding_space_path)
                                        if search_path.suffix == '.pth':
                                            metadata_paths = [
                                                search_path.parent / "metadata.json",
                                                search_path.parent / "embedding_space_metadata.json",
                                                search_path.parent / "es_metadata" / f"{search_path.stem}_metadata.json",
                                            ]
                                            for meta_path in metadata_paths:
                                                if meta_path.exists():
                                                    logger.info(f"   ✅ Found ES metadata: {meta_path}")
                                                    embedding_space_metadata = str(meta_path.resolve())
                                                    break
                                        break
                                
                                # If BEST checkpoint not found, look for in-progress epoch checkpoints
                                if not embedding_space_path:
                                    # Search for inference checkpoints (have full encoder + es_state)
                                    epoch_checkpoints = sorted(train_es_dir.glob("checkpoint_inference_e-*.pt"))
                                    if not epoch_checkpoints:
                                        # Fallback to training_state checkpoints only
                                        epoch_checkpoints = sorted(train_es_dir.glob("training_state_e-*.pth"))
                                    if epoch_checkpoints:
                                        # Use the latest epoch checkpoint
                                        latest_checkpoint = epoch_checkpoints[-1]
                                        embedding_space_path = str(latest_checkpoint.resolve())
                                        logger.info(f"✅ Found in-progress epoch checkpoint on {hostname}: {embedding_space_path}")
                                        logger.info(f"   Using latest of {len(epoch_checkpoints)} epoch checkpoints")
                                        
                                        # Look for metadata
                                        metadata_paths = [
                                            latest_checkpoint.parent / "metadata.json",
                                            latest_checkpoint.parent / "embedding_space_metadata.json",
                                            latest_checkpoint.parent / "es_metadata" / f"{latest_checkpoint.stem}_metadata.json",
                                        ]
                                        for meta_path in metadata_paths:
                                            if meta_path.exists():
                                                logger.info(f"   ✅ Found ES metadata: {meta_path}")
                                                embedding_space_metadata = str(meta_path.resolve())
                                                break
                                
                                if embedding_space_path:
                                    break
                        if embedding_space_path:
                            break
            else:
                logger.warning(f"   ⚠️  Backplane directory does not exist: {backplane_base}")
        
        # If still not found, raise error
        if not embedding_space_path:
            raise ValueError(
                f"Foundation model {foundation_model_id} does not have an embedding_space path set "
                f"and could not be found by searching local or backplane directories. "
                f"Please ensure the foundation model's train_es job completed successfully."
            )
    
    # Create output directory for new session
    new_session_output_dir = config.output_dir / session_id
    new_session_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the embedding space file (pickle or .pth) to new session
    copied_es_path = None
    copied_metadata_path = None
    
    if embedding_space_path:
        es_source = Path(embedding_space_path)
        es_filename = es_source.name
        dest_es = new_session_output_dir / f"foundation_{es_filename}"
        shutil.copy2(es_source, dest_es)
        copied_es_path = str(dest_es)
        logger.info(f"✅ Copied ES to new session: {dest_es}")
        
        # If there's metadata, copy it too
        if 'embedding_space_metadata' in locals() and embedding_space_metadata:
            meta_source = Path(embedding_space_metadata)
            dest_meta = new_session_output_dir / f"foundation_{meta_source.name}"
            shutil.copy2(meta_source, dest_meta)
            copied_metadata_path = str(dest_meta)
            logger.info(f"✅ Copied ES metadata to new session: {dest_meta}")
    
    # Also find and copy the best (or last) checkpoint from foundation model for resuming
    foundation_es_dir = Path(embedding_space_path).parent if embedding_space_path else None
    checkpoint_source = None
    checkpoint_type = None
    copied_checkpoint_path = None
    
    if foundation_es_dir and foundation_es_dir.exists():
        best_checkpoint = foundation_es_dir / "training_state_BEST.pth"
        
        if best_checkpoint.exists():
            checkpoint_source = best_checkpoint
            checkpoint_type = "best"
            logger.info(f"📂 Found BEST checkpoint from foundation model: {best_checkpoint}")
        else:
            # Look for last epoch checkpoint
            epoch_checkpoints = sorted(foundation_es_dir.glob("training_state_e-*.pth"))
            if epoch_checkpoints:
                checkpoint_source = epoch_checkpoints[-1]  # Last epoch
                checkpoint_type = "last"
                logger.info(f"📂 Found LAST checkpoint from foundation model: {checkpoint_source}")
            else:
                logger.warning(f"⚠️  No checkpoint found in foundation model directory: {foundation_es_dir}")
        
        # Copy checkpoint to new session
        if checkpoint_source:
            dest_checkpoint = new_session_output_dir / f"foundation_checkpoint_{checkpoint_type}.pth"
            shutil.copy2(checkpoint_source, dest_checkpoint)
            copied_checkpoint_path = str(dest_checkpoint)
            logger.info(f"✅ Copied {checkpoint_type} checkpoint to new session: {dest_checkpoint}")
    
    # Validate target_spec
    if "target_column" not in target_spec:
        raise ValueError("target_column is required in target_spec")
    if "target_column_type" not in target_spec:
        raise ValueError("target_column_type is required in target_spec")
    
    # Use foundation model's input data if not provided
    if input_filename is None:
        input_filename = foundation_session.get("input_data")
        logger.info(f"📁 Using foundation model's input data: {input_filename}")
    
    # Create job plan: ONLY create_structured_data and train_single_predictor
    job_plan = [
        dict(
            job_type="create_structured_data",
            spec={},
            job_id=None,
        ),
        dict(
            job_type="train_single_predictor",
            spec=target_spec,
            job_id=None,
            predictor_index=0,
        ),
    ]
    
    # CRITICAL: Set compute_cluster to current node's hostname
    # This prevents routing confusion where session created on taco but client queries burrito
    current_node = socket.gethostname()
    logger.info(f"📍 Setting compute_cluster={current_node} for foundation model session")
    
    session_doc = dict(
        created_at=created_at,
        session_type="predictor",
        session_id=session_id,
        name=name,
        status=SessionStatus.READY,  # Set initial status
        compute_cluster=current_node,  # CRITICAL: Track which node created this session
        job_plan=job_plan,
        embedding_space=copied_es_path,  # Use COPIED path, not original
        embedding_space_metadata=copied_metadata_path,  # Copied metadata JSON
        embedding_space_source=embedding_space_path,  # Original ES path for reference
        strings_cache=strings_cache_path,
        input_data=input_filename,
        sqlite_db=sqlite_db_path,  # Copy from foundation session
        vector_db=None,
        projections=None,
        preview_png=None,
        single_predictors=[None],
        training_metrics=[None],
        foundation_model_id=foundation_model_id,
        foundation_checkpoint=copied_checkpoint_path,  # Path to copied checkpoint
        foundation_checkpoint_type=checkpoint_type,  # "best" or "last"
        foundation_checkpoint_source=str(checkpoint_source) if checkpoint_source else None,  # Original checkpoint path
        user_metadata=user_metadata,
    )
    
    logger.info(f"✅ Foundation model session created: {session_id}")
    if copied_checkpoint_path:
        logger.info(f"   Checkpoint ({checkpoint_type}): {copied_checkpoint_path}")
    if strings_cache_path:
        logger.info(f"   Strings cache: {strings_cache_path}")
    if sqlite_db_path:
        logger.info(f"   SQLite database: {sqlite_db_path}")
    
    return session_doc


def create_session(session_type: str, session_id: str = None, start: bool = True, input_filename: str | None = None, name: str = None, session_name_prefix: str = None, target_spec: dict = None, single_predictors: list = None, epochs: int = None, column_overrides: dict = None, string_list_delimiter: str = "|", movie_frame_interval: int = 3, weightwatcher_save_every: int = 5, important_columns_for_visualization: list = None, user_metadata: dict = None):
    """Create a new session of the specified type."""
    # Check if node is upgrading
    upgrade_lock_file = Path("/tmp/auto-upgrade.lock")
    if upgrade_lock_file.exists():
        hostname = socket.gethostname()
        raise NodeUpgradingException(f"Node {hostname} is currently upgrading and cannot accept training requests. Please try again in a few minutes or use a different node.")

    # Ensure all necessary directories exist before creating sessions
    ensure_directories_exist()

    created_at = datetime.now(tz=ZoneInfo("America/New_York"))

    # Sanitize session_name_prefix: replace slashes and dots with underscores
    if session_name_prefix:
        session_name_prefix = session_name_prefix.replace('/', '_').replace('.', '_')
        logger.debug(f"📋 Sanitized session_name_prefix: {session_name_prefix}")

    if session_id is None:
        # Generate full UUID
        full_uuid = str(uuid4())
        
        # If prefix is provided, format as <prefix>-<full-uuid>
        # For embedding_space sessions, always use new format: <uuid6>-<timestamp>
        # Otherwise, use the original format: <timestamp>_<uuid6>
        if session_name_prefix:
            session_id = f"{session_name_prefix}-{full_uuid}"
        elif session_type == "embedding_space":
            # Embedding space sessions use new format: {uuid}-{timestamp}
            unique_string = full_uuid[:6]
            session_timestamp = created_at.strftime('%Y%m%d-%H%M%S')
            session_id = f"{unique_string}-{session_timestamp}"
        else:
            unique_string = full_uuid[:6]
            session_timestamp = created_at.strftime('%Y%m%d-%H%M%S')
            session_id = "_".join([session_timestamp, unique_string])
    else:
        # session_id was provided - if prefix is also provided, ensure session_id uses it with UUID
        if session_name_prefix:
            # Prefix is provided - session_id MUST be in format {prefix}-{uuid}
            # If it's not, create a new one with the prefix
            if not session_id.startswith(f"{session_name_prefix}-"):
                full_uuid = str(uuid4())
                session_id = f"{session_name_prefix}-{full_uuid}"
                logger.info(f"📋 Created session_id with prefix and UUID: {session_id}")
            # If it does start with prefix, verify it has UUID-like suffix (contains dashes after prefix)
            elif len(session_id) <= len(session_name_prefix) + 1:
                # Too short - probably just the prefix, add UUID
                full_uuid = str(uuid4())
                session_id = f"{session_name_prefix}-{full_uuid}"
                logger.info(f"📋 Added UUID suffix to session_id: {session_id}")

    if session_type == "sphere":
        # Extract target_column from target_spec if provided
        target_column = None
        if target_spec and isinstance(target_spec, dict):
            target_column = target_spec.get('target_column')
        
        session_doc = create_sphere_session(
            session_id=session_id,
            created_at=created_at,
            input_filename=input_filename,
            name=name,
            single_predictors=single_predictors,
            epochs=epochs,
            column_overrides=column_overrides,
            string_list_delimiter=string_list_delimiter,
            movie_frame_interval=movie_frame_interval,
            weightwatcher_save_every=weightwatcher_save_every,
            important_columns_for_visualization=important_columns_for_visualization,
            user_metadata=user_metadata,
            target_column=target_column,
        )
    elif session_type == "embedding_space":
        session_doc = create_embedding_space_session(
            name=name or input_filename or "embedding_space",
            s3_training_path=target_spec.get("training_dataset") if target_spec else None,
            s3_validation_path=target_spec.get("validation_dataset") if target_spec else None,
            session_id=session_id,
            user_metadata=user_metadata,
        )
    else:
        raise ValueError(f"Unsupported session type {session_type}")

    save_session(session_id=session_id, session_doc=session_doc, exist_ok=False)

    # Dispatch first job in chain if start=True
    if start:
        from lib.session_chains import dispatch_next_job_in_chain
        dispatch_next_job_in_chain(session_id=session_id)

    return session_doc


def find_closest_points(session_id: str, query_record: Dict[str, Any], k: int = 5) -> Dict[str, Any]:
    """Find the k closest points to a query record in the embedding space."""
    logger.debug(sys.path)
    pp = str(Path("./lib").resolve())
    if pp not in sys.path:
        sys.path.insert(0, pp)
    from featrix.neural.io_utils import load_embedded_space
    from lib.vector_db import CSVtoLanceDB

    session = load_session(session_id)

    # validate faiss index path
    vector_db_path = session.get("vector_db")
    if vector_db_path is None:
        raise ValueError(f"Session {session_id} does not have a vector_db")
    
    vector_db_path = Path(vector_db_path)
    if not vector_db_path.is_dir():
        raise FileNotFoundError(f"LanceDB data at {vector_db_path} does not exist")

    # validate embedding space path
    embedding_space_path = session.get("embedding_space")
    if embedding_space_path is None:
        raise ValueError(f"Session {session_id} does not have an embedding space")

    embedding_space_path = Path(embedding_space_path)
    if not embedding_space_path.is_file():
        raise FileNotFoundError(f"Embedding space {embedding_space_path} does not exist")

    # load the embedding space
    try: 
        embedded_space = load_embedded_space(embedding_space_path)
    except Exception as e:
        raise ValueError(f"Error loading embedding space: {e}")

    # validate sqlite_db_path
    sqlite_db_path = session.get("sqlite_db")
    if sqlite_db_path is None:
        raise ValueError(f"Session {session_id} does not have an sqlite db")
    
    sqlite_db_path = Path(sqlite_db_path)
    if not sqlite_db_path.is_file():
        raise FileNotFoundError(f"Sqlite db at {sqlite_db_path} does not exist")

    # load the faiss index
    try:
        vec_db = CSVtoLanceDB(
            featrix_es=embedded_space, 
            sqlite_db_path=sqlite_db_path, 
            lancedb_path=vector_db_path)
        vec_db.load_existing()
    except Exception as e:
        raise ValueError(f"Error loading faiss index: {e}")

    # get the nearest neighbors
    try:
        result = vec_db.search(query_record, k=k)
    except Exception as e:
        raise ValueError(f"Error querying nearest neighbors: {e}")

    # Add server metadata for debugging    
    result["_meta"] = {
        "compute_cluster": socket.gethostname(),
        "compute_cluster_time": datetime.utcnow().isoformat() + "Z",
    }
    
    return result


def get_queue_summary() -> dict:
    """Get a summary of all queue states for admin/debugging purposes."""
    from lib.queue_manager import iterate_over_jobs_in_queue
    from lib.job_manager import JobStatus
    
    queue_summary = {}
    
    # Check all known queue types
    known_queues = [
        "create_structured_data",
        "train_es", 
        "train_knn",
        "run_clustering",
        "train_single_predictor"
    ]
    
    for job_type in known_queues:
        ready_jobs = []
        running_jobs = []
        total_jobs = 0
        
        try:
            for job in iterate_over_jobs_in_queue(job_type):
                total_jobs += 1
                status = job.get("status")
                
                if status == JobStatus.READY:
                    ready_jobs.append(job)
                elif status == JobStatus.RUNNING:
                    running_jobs.append(job)
        except Exception as e:
            queue_summary[job_type] = {
                "exists": True,
                "error": str(e),
                "status": "error_reading_queue"
            }
            continue
        
        queue_summary[job_type] = {
            "exists": True,
            "ready_jobs": len(ready_jobs),
            "running_jobs": len(running_jobs),
            "total_jobs": total_jobs,
            "status": "active" if len(running_jobs) > 0 else "idle",
            "next_job_id": ready_jobs[0].get("job_id") if ready_jobs else None,
            "currently_running": [job.get("job_id") for job in running_jobs],
        }
    
    return queue_summary


def add_notification_email_to_session(session_id: str, email: str):
    """Add a notification email to a session."""
    session_doc = load_session(session_id)

    if "notification_email" not in session_doc:
        session_doc["notification_email"] = []

    session_doc["notification_email"].append(email)

    save_session(session_id, session_doc, exist_ok=True)

    logger.info(f"Notification email {email} added to session {session_id}")


# ============================================================================
# Session Publishing Functions
# ============================================================================

def publish_session(session_id: str, org_id: str, name: str) -> dict:
    """
    Publish a session by moving it to /backplane/backplane1/sphere/PUBLISHED/<org_id>/<name>/<sessionId>.
    Moves both the session file (if it exists) and output directory.
    
    Args:
        session_id: Session ID to publish
        org_id: Organization ID for subdirectory organization
        name: Name for the published session (creates subdirectory under org_id)
        
    Returns:
        Dictionary with published_path, output_path, and status
        
    Raises:
        FileNotFoundError: If session does not exist
        ValueError: If org_id or name is empty
        RuntimeError: If Redis is unavailable or move operation fails
    """
    # Validate parameters
    if not org_id or not org_id.strip():
        raise ValueError("org_id is required and cannot be empty")
    if not name or not name.strip():
        raise ValueError("name is required and cannot be empty")
    
    # Sanitize org_id and name for filesystem safety
    org_id = org_id.strip()
    name = name.strip()
    
    # Load session to verify it exists
    session = load_session(session_id)
    
    # Check if already published
    if session.get("published", False):
        published_path = session.get("published_path")
        if published_path and Path(published_path).exists():
            logger.info(f"Session {session_id} is already published at {published_path}")
            return {
                "status": "already_published",
                "published_path": published_path,
                "output_path": str(Path(published_path) / "output"),
            }
    
    # Define published directory structure: /backplane/backplane1/sphere/PUBLISHED/<org_id>/<name>/<sessionId>
    published_base = Path("/backplane/backplane1/sphere/PUBLISHED")
    published_session_dir = published_base / org_id / name / session_id
    published_session_file = published_session_dir / f"{session_id}.session"
    published_output_dir = published_session_dir / "output"
    
    # Create published directory
    published_session_dir.mkdir(parents=True, exist_ok=True)
    
    # Move session file if it exists
    session_file = config.session_dir / f"{session_id}.session"
    if session_file.exists():
        logger.info(f"Moving session file: {session_file} -> {published_session_file}")
        shutil.move(str(session_file), str(published_session_file))
    else:
        # Create a placeholder or note that file doesn't exist
        logger.info(f"Session file not found at {session_file} (may be Redis-only)")
    
    # Move output directory
    output_dir = config.output_dir / session_id
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")
    
    logger.info(f"Moving output directory: {output_dir} -> {published_output_dir}")
    shutil.move(str(output_dir), str(published_output_dir))
    
    # Update session document
    session["published"] = True
    session["published_path"] = str(published_session_dir)
    session["published_at"] = convert_to_iso(datetime.now(ZoneInfo("UTC")))
    session["published_org_id"] = org_id
    session["published_name"] = name
    
    # Save updated session
    save_session(session_id, session, exist_ok=True)
    
    logger.info(f"✅ Published session {session_id} to {published_session_dir}")
    
    return {
        "status": "published",
        "published_path": str(published_session_dir),
        "output_path": str(published_output_dir),
    }


def deprecate_session(session_id: str, warning_message: str, expiration_date: str) -> dict:
    """
    Deprecate a published session with a warning message and expiration date.
    The session remains available until the expiration date.
    
    Args:
        session_id: Session ID to deprecate
        warning_message: Warning message about deprecation
        expiration_date: ISO format date string when session will be removed (e.g., "2025-12-31T23:59:59Z")
        
    Returns:
        Dictionary with deprecation status
        
    Raises:
        FileNotFoundError: If session does not exist
        ValueError: If session is not published or expiration_date is invalid
    """
    # Load session
    session = load_session(session_id)
    
    # Verify session is published
    if not session.get("published", False):
        raise ValueError(f"Session {session_id} is not published. Cannot deprecate.")
    
    published_path = session.get("published_path")
    if not published_path or not Path(published_path).exists():
        raise ValueError(f"Published session path does not exist: {published_path}")
    
    # Validate expiration date format
    try:
        expiration_dt = convert_from_iso(expiration_date)
        if expiration_dt <= datetime.now(ZoneInfo("UTC")):
            raise ValueError(f"Expiration date must be in the future: {expiration_date}")
    except Exception as e:
        raise ValueError(f"Invalid expiration date format: {expiration_date}") from e
    
    # Update session document
    session["deprecated"] = True
    session["deprecation_warning"] = warning_message
    session["deprecation_expiration"] = expiration_date
    session["deprecated_at"] = convert_to_iso(datetime.now(ZoneInfo("UTC")))
    
    # Save updated session
    save_session(session_id, session, exist_ok=True)
    
    logger.info(f"✅ Deprecated session {session_id} (expires: {expiration_date})")
    
    return {
        "status": "deprecated",
        "session_id": session_id,
        "warning_message": warning_message,
        "expiration_date": expiration_date,
    }


def unpublish_session(session_id: str) -> dict:
    """
    Unpublish a session by moving it back from /backplane/backplane1/sphere/PUBLISHED/<sessionId>.
    Moves both the session file and output directory back to their original locations.
    
    Args:
        session_id: Session ID to unpublish
        
    Returns:
        Dictionary with unpublish status
        
    Raises:
        FileNotFoundError: If session does not exist or is not published
        RuntimeError: If move operation fails
    """
    # Load session
    session = load_session(session_id)
    
    # Verify session is published
    if not session.get("published", False):
        raise FileNotFoundError(f"Session {session_id} is not published. Cannot unpublish.")
    
    published_path = Path(session.get("published_path", ""))
    if not published_path.exists():
        raise FileNotFoundError(f"Published session path does not exist: {published_path}")
    
    # Define original locations
    original_session_file = config.session_dir / f"{session_id}.session"
    original_output_dir = config.output_dir / session_id
    
    # Move session file back if it exists in published location
    published_session_file = published_path / f"{session_id}.session"
    if published_session_file.exists():
        logger.info(f"Moving session file back: {published_session_file} -> {original_session_file}")
        config.session_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(published_session_file), str(original_session_file))
    
    # Move output directory back
    published_output_dir = published_path / "output"
    if not published_output_dir.exists():
        raise FileNotFoundError(f"Published output directory not found: {published_output_dir}")
    
    logger.info(f"Moving output directory back: {published_output_dir} -> {original_output_dir}")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(published_output_dir), str(original_output_dir))
    
    # Remove published directory if empty
    try:
        if published_path.exists() and not any(published_path.iterdir()):
            published_path.rmdir()
            logger.info(f"Removed empty published directory: {published_path}")
    except Exception as e:
        logger.warning(f"Could not remove published directory {published_path}: {e}")
    
    # Update session document
    session["published"] = False
    session.pop("published_path", None)
    session.pop("published_at", None)
    session.pop("deprecated", None)
    session.pop("deprecation_warning", None)
    session.pop("deprecation_expiration", None)
    session.pop("deprecated_at", None)
    
    # Save updated session
    save_session(session_id, session, exist_ok=True)
    
    logger.info(f"✅ Unpublished session {session_id}")
    
    return {
        "status": "unpublished",
        "session_id": session_id,
    }

# Re-export SessionStatus for backward compatibility
__all__ = [
    'SessionStatus',
    'NodeUpgradingException',
    'load_session',
    'save_session',
    'resolve_session_path',
    'get_session_info',
    'iterate_over_sessions',
    'serialize_session',
    'ensure_directories_exist',
    'get_version_info',
    'create_session',
    'create_sphere_session',
    'create_embedding_space_session',
    'create_fine_tune_embedding_space_session',
    'create_foundation_model_session',
    'create_cloned_session',
    'find_closest_points',
    'get_queue_summary',
    'add_notification_email_to_session',
    'publish_session',
    'deprecate_session',
    'unpublish_session',
]

