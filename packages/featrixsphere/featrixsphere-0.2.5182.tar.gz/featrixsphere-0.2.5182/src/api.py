#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import asyncio as aio
import datetime
import fcntl
import hashlib
import json
import logging
import math
import os
import pickle
import shutil
import socket
import sqlite3
import sys
import time
import traceback
from datetime import timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

# CRITICAL: Force CPU-only mode for API workers
# API workers should NEVER hold persistent GPU memory (would waste 20GB for 32 workers)
# GPU stats queries use a forked child process that has GPU visibility
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import torch  # CPU-only because CUDA_VISIBLE_DEVICES=''
from config import config
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
# JSONResponse is defined below with auto-sanitization - see sanitize_for_json()
from featrix.neural.io_utils import load_embedded_space
from featrix.neural.embedding_space_utils import find_embedding_space_pickle, get_embedding_space_pickle_filename, write_embedding_space_pickle, resolve_embedding_space_path, embedding_space_path_exists

# Import remaining functions from featrix_queue (not yet migrated)
from lib.session_manager import (
    NodeUpgradingException,
    add_notification_email_to_session,
    create_cloned_session,
    create_embedding_space_session,
    create_fine_tune_embedding_space_session,
    create_foundation_model_session,
    create_session,
    create_sphere_session,
    find_closest_points,
    get_queue_summary,
    get_version_info,
)
from lib.job_manager import serialize_job
from lib.queue_manager import iterate_over_jobs_in_queue
from jsontables import JSONTablesDecoder, JSONTablesEncoder, detect_table_in_json, is_json_table
from lib.job_manager import (
    JobStatus,
    get_job_output_path,
)
from lib.json_encoder_cache import JsonEncoderCache
from lib.es_training import sanitize_datetime_for_json
from lib.model_repair import get_best_model_path, check_and_repair_model
from prediction_client import predict_batch as prediction_server_predict, is_prediction_server_available

# Import from new modules
from lib.session_manager import (
    deprecate_session,
    get_session_info,
    iterate_over_sessions,
    load_session,
    publish_session,
    resolve_session_path,
    save_session,
    serialize_session,
    unpublish_session,
)
from pydantic import BaseModel, ConfigDict
from redis_prediction_store import RedisPredictionStore
from send_email import validate_and_normalize_email
from utils import convert_from_iso, convert_to_iso

__all__ = [
    "create_app",
]

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# Import standardized logging configuration
from lib.featrix.neural.logging_config import configure_logging
configure_logging(job_prefix='api')

logger = logging.getLogger(__name__)


# ==============================================================================
# GPU STATS HELPER - Spawn child process with GPU visibility
# ==============================================================================

def get_gpu_stats_via_subprocess():
    """
    Get GPU memory stats by spawning a child process that has GPU visibility.
    
    Parent API workers have CUDA_VISIBLE_DEVICES='' (CPU-only).
    Child process unsets this env var, imports torch, gets stats, prints JSON, exits.
    
    Returns dict with GPU info or empty dict on error.
    """
    import subprocess
    import json
    
    # Python script that child will execute
    gpu_stats_script = """
import json
import sys

try:
    import torch
    
    if not torch.cuda.is_available():
        print(json.dumps({"available": False}))
        sys.exit(0)
    
    stats = {
        "available": True,
        "gpu_allocated_mb": round(torch.cuda.memory_allocated() / 1024 / 1024, 1),
        "gpu_cached_mb": round(torch.cuda.memory_reserved() / 1024 / 1024, 1),
        "gpu_free_mb": round(
            (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated())
            / 1024 / 1024,
            1
        ),
    }
    print(json.dumps(stats))
except Exception as e:
    print(json.dumps({"available": False, "error": str(e)}))
"""
    
    try:
        # Spawn child with GPU visibility (unset CUDA_VISIBLE_DEVICES)
        env = os.environ.copy()
        if 'CUDA_VISIBLE_DEVICES' in env:
            del env['CUDA_VISIBLE_DEVICES']
        
        result = subprocess.run(
            [sys.executable, '-c', gpu_stats_script],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
        else:
            logger.warning(f"GPU stats subprocess failed: {result.stderr}")
            return {"available": False}
            
    except Exception as e:
        logger.warning(f"Failed to get GPU stats via subprocess: {e}")
        return {"available": False}


# LRU Cache for loaded predictors to avoid reloading models
class PredictorCache:
    """LRU cache for loaded FeatrixSinglePredictor instances."""

    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.cache = {}  # predictor_path -> (predictor, last_access_time)
        self.access_times = {}  # predictor_path -> access_time

    def get(self, predictor_path: str):
        """Get a predictor from cache if available."""
        if predictor_path in self.cache:
            # Update access time
            current_time = time.time()
            self.cache[predictor_path] = (self.cache[predictor_path][0], current_time)
            self.access_times[predictor_path] = current_time
            logger.info(f"🚀 CACHE HIT - Reusing loaded predictor: {predictor_path}")
            return self.cache[predictor_path][0]
        return None

    def put(self, predictor_path: str, predictor):
        """Add a predictor to cache, evicting LRU if needed."""
        current_time = time.time()

        # If cache is full, remove least recently used
        if len(self.cache) >= self.max_size and predictor_path not in self.cache:
            lru_path = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            logger.info(f"🗑️ CACHE EVICT - Removing LRU predictor: {lru_path}")

            # Clean up GPU memory for evicted predictor
            try:
                evicted_predictor = self.cache[lru_path][0]
                evicted_predictor.cleanup_gpu_memory()
            except Exception as e:
                logger.warning(f"Failed to cleanup evicted predictor: {e}")

            del self.cache[lru_path]
            del self.access_times[lru_path]

        # Add new predictor to cache
        self.cache[predictor_path] = (predictor, current_time)
        self.access_times[predictor_path] = current_time
        logger.info(f"🔄 CACHE ADD - Cached new predictor: {predictor_path}")

    def clear(self):
        """Clear all cached predictors and free GPU memory."""
        logger.info(f"🗑️ CACHE CLEAR - Clearing {len(self.cache)} cached predictors")
        for predictor_path, (predictor, _) in self.cache.items():
            try:
                predictor.cleanup_gpu_memory()
            except Exception as e:
                logger.warning(f"Failed to cleanup predictor {predictor_path}: {e}")

        self.cache.clear()
        self.access_times.clear()

    def stats(self):
        """Get cache statistics."""
        return {"size": len(self.cache), "max_size": self.max_size, "cached_predictors": list(self.cache.keys())}


# Global predictor cache instance
predictor_cache = PredictorCache(max_size=10)  # Cache up to 10 predictors


class EmbeddingSpaceCache:
    """LRU cache for loaded EmbeddingSpace instances."""

    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.cache = {}  # es_path -> (embedding_space, last_access_time)
        self.access_times = {}  # es_path -> access_time

    def get(self, es_path: str):
        """Get an embedding space from cache if available."""
        if es_path in self.cache:
            # Update access time
            current_time = time.time()
            self.cache[es_path] = (self.cache[es_path][0], current_time)
            self.access_times[es_path] = current_time
            logger.info(f"🚀 ES CACHE HIT - Reusing loaded embedding space: {es_path}")
            return self.cache[es_path][0]
        return None

    def put(self, es_path: str, embedding_space):
        """Add an embedding space to cache, evicting LRU if needed."""
        current_time = time.time()

        # If cache is full, remove least recently used
        if len(self.cache) >= self.max_size and es_path not in self.cache:
            lru_path = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            logger.info(f"🗑️ ES CACHE EVICT - Removing LRU embedding space: {lru_path}")

            # Clean up GPU memory for evicted embedding space
            try:
                evicted_es = self.cache[lru_path][0]
                if hasattr(evicted_es, "cleanup_gpu_memory"):
                    evicted_es.cleanup_gpu_memory()
            except Exception as e:
                logger.warning(f"Failed to cleanup evicted embedding space: {e}")

            del self.cache[lru_path]
            del self.access_times[lru_path]

        # Add new embedding space to cache
        self.cache[es_path] = (embedding_space, current_time)
        self.access_times[es_path] = current_time
        logger.info(f"🔄 ES CACHE ADD - Cached new embedding space: {es_path}")

    def clear(self):
        """Clear all cached embedding spaces and free GPU memory."""
        logger.info(f"🗑️ ES CACHE CLEAR - Clearing {len(self.cache)} cached embedding spaces")
        for es_path, (embedding_space, _) in self.cache.items():
            try:
                if hasattr(embedding_space, "cleanup_gpu_memory"):
                    embedding_space.cleanup_gpu_memory()
            except Exception as e:
                logger.warning(f"Failed to cleanup embedding space {es_path}: {e}")

        self.cache.clear()
        self.access_times.clear()

    def stats(self):
        """Get cache statistics."""
        return {"size": len(self.cache), "max_size": self.max_size, "cached_embedding_spaces": list(self.cache.keys())}


# Global cache instances
embedding_space_cache = EmbeddingSpaceCache(max_size=10)  # Cache up to 10 embedding spaces


def fix_paths():
    pp = "/sphere/app/lib"
    if pp not in sys.path:
        sys.path.insert(0, pp)


def post_slack_alert(msg):
    try:
        from slack import send_slack_message

        send_slack_message(msg)
    except Exception as e:
        logger.warning(f"Failed to send slack message: {msg} - Error: {e}")
    return


def replace_nans_with_nulls(data):
    # This looks like it doesn't do anything -- but it's for JSON encoding which gets angry about NaNs and not Nones.
    if isinstance(data, dict):
        return {k: replace_nans_with_nulls(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_nans_with_nulls(v) for v in data]
    elif isinstance(data, float) and math.isnan(data):
        return None
    else:
        return data


def get_compute_cluster_name() -> str:
    """Get short compute cluster name (taco, burrito, churro) from hostname."""
    hostname = socket.gethostname()
    short_name = hostname.split(".")[0].lower()

    # Map known cluster names
    if short_name in ["taco", "burrito", "churro"]:
        return short_name

    # Return full short hostname if not a known cluster
    return short_name


def get_server_metadata(version: str = "unknown") -> Dict[str, Any]:
    """Get server metadata to include in all API responses."""
    return {
        "compute_cluster_time": datetime.datetime.now(timezone.utc).isoformat() + "Z",
        "compute_cluster": socket.gethostname(),
        "compute_cluster_version": version,
    }


def sanitize_for_json(obj):
    """
    Recursively sanitize an object for JSON serialization.
    
    Converts:
    - datetime objects → ISO format strings
    - date objects → ISO format strings
    - numpy types → Python native types
    - NaN/Inf → None
    - Any other non-serializable → str(obj)
    
    NEVER let datetime objects crash JSON serialization again.
    """
    import datetime
    
    # Import numpy only if available
    try:
        import numpy as np
        has_numpy = True
    except ImportError:
        has_numpy = False
    
    if obj is None:
        return None
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    elif has_numpy and isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif has_numpy and isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, float):
        if has_numpy:
            if np.isnan(obj) or np.isinf(obj):
                return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (str, int, bool)):
        return obj
    else:
        # Last resort: convert to string
        try:
            # Try to serialize it first to see if it's actually JSON-safe
            import json
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Not serializable - convert to string
            return str(obj)


# Override JSONResponse to ALWAYS sanitize before serialization
from starlette.responses import JSONResponse as _OriginalJSONResponse

class JSONResponse(_OriginalJSONResponse):
    """
    JSONResponse that automatically sanitizes datetime objects.
    
    NEVER crashes on datetime - converts to ISO string automatically.
    """
    def __init__(self, content: Any, **kwargs):
        # Sanitize content before passing to parent
        sanitized_content = sanitize_for_json(content)
        super().__init__(content=sanitized_content, **kwargs)


class MetadataJSONResponse(JSONResponse):
    """JSONResponse that automatically adds server metadata to all responses."""

    def __init__(self, content: Any, version: str = "unknown", **kwargs):
        """
        Create a JSON response with server metadata.

        Args:
            content: The response data (will be wrapped with metadata)
            version: Server version string
            **kwargs: Additional arguments passed to JSONResponse
        """
        # Sanitize content to prevent datetime serialization crashes
        sanitized_content = sanitize_for_json(content)
        
        # Wrap the content with metadata
        wrapped_content = {"_meta": get_server_metadata(version), "data": sanitized_content}
        super().__init__(content=wrapped_content, **kwargs)


def create_app() -> FastAPI:
    """Create ASGI app with clean logging."""

    # Install Featrix exception hook for better error tracking
    try:
        from lib.featrix_debug import install_featrix_excepthook

        install_featrix_excepthook()
    except Exception:
        pass  # Don't fail if debug module not available

    # Disable default uvicorn access logs (we have custom middleware logging)
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.disabled = True

    # Apply bot traffic filter to uvicorn access logs
    # uvicorn_logger = logging.getLogger("uvicorn.access")
    # uvicorn_logger.addFilter(BotTrafficFilter())

    # Fetch compute node mapping from sphere-api
    def fetch_compute_nodes_from_sphere_api() -> dict:
        """Fetch compute node mapping from sphere-api with retries and fallback.
        
        CRITICAL: Keep timeout SHORT to avoid blocking FastAPI startup.
        If this hangs, the ENTIRE API becomes unresponsive and can't serve ANY requests.
        """
        import time

        import requests

        # Default fallback mapping (used if sphere-api is unavailable)
        default_mapping = {
            "taco": "http://sphere-compute.featrix.com:8003",
            "churro": "http://sphere-compute.featrix.com:8002",
            "burrito": "http://sphere-compute.featrix.com:8004",
        }

        # CRITICAL: Only 1 retry with SHORT timeout to avoid blocking startup
        # If sphere-api is down/slow, we need to fail fast and use defaults
        # Total blocking time: 3s + 0.5s + 3s = 6.5s max (acceptable)
        max_retries = 2
        for attempt in range(max_retries):
            try:
                timeout = 3  # SHORT timeout - fail fast
                response = requests.get("https://sphere-api.featrix.com/compute-nodes", timeout=timeout)
                if response.status_code == 200:
                    nodes = response.json()
                    if nodes:
                        logger.info(f"✅ Fetched compute node mapping from sphere-api: {list(nodes.keys())}")
                        return nodes
                    else:
                        logger.warning("Empty node mapping received from sphere-api, using defaults")
                        return default_mapping
                else:
                    logger.warning(
                        f"sphere-api returned status {response.status_code}, attempt {attempt + 1}/{max_retries}"
                    )
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(
                    f"Failed to fetch compute nodes from sphere-api (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    wait_time = 0.5  # SHORT wait - fail fast to avoid blocking startup
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            except Exception as e:
                logger.warning(f"Unexpected error fetching compute nodes (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 0.5  # SHORT wait - fail fast
                    time.sleep(wait_time)

        # All retries failed - use default mapping
        logger.warning("⚠️  Could not fetch compute node mapping from sphere-api after retries, using default mapping")
        logger.info(f"Using default compute node mapping: {list(default_mapping.keys())}")
        return default_mapping

    # Fetch on startup - use fallback if can't fetch
    try:
        COMPUTE_NODES = fetch_compute_nodes_from_sphere_api()
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching compute node mapping: {e}")
        # Use default mapping as last resort
        COMPUTE_NODES = {
            "taco": "http://sphere-compute.featrix.com:8003",
            "churro": "http://sphere-compute.featrix.com:8002",
            "burrito": "http://sphere-compute.featrix.com:8004",
        }
        logger.warning(f"Using fallback compute node mapping: {list(COMPUTE_NODES.keys())}")

    # Also filter the main uvicorn logger
    # main_uvicorn_logger = logging.getLogger("uvicorn")
    # main_uvicorn_logger.addFilter(BotTrafficFilter())
    """Create ASGI app."""
    # -------------------------------------------------------------------------------
    # Configure FastAPI
    # -------------------------------------------------------------------------------

    # Print version info immediately at startup
    from version import print_version_banner

    print_version_banner("Featrix Sphere API Server")

    # Track server startup time for uptime calculation
    import time

    SERVER_STARTUP_TIME = time.time()

    # Read version string at startup
    COMPUTE_CLUSTER_VERSION = "unknown"
    try:
        version_file = Path(__file__).parent.parent / "VERSION"
        if version_file.exists():
            COMPUTE_CLUSTER_VERSION = version_file.read_text().strip()
            logger.info(f"Compute cluster version: {COMPUTE_CLUSTER_VERSION}")
    except Exception as e:
        logger.warning(f"Could not read VERSION file: {e}")

    app = FastAPI(
        title="Featrix Sphere",
        description="Featrix Sphere ML Training Service",
        version="1.0.0",  # Keep this for OpenAPI docs
    )

    # Custom middleware for detailed access logging and server metadata injection
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests with timestamps, IPs, routes, and responses."""
        start_time = time.time()

        # Get client IP (handle proxy headers)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.headers.get("X-Real-IP", "")
        if not client_ip:
            client_ip = getattr(request.client, "host", "unknown")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log ALL HTTP requests - comprehensive access logging
            status_emoji = "✅" if response.status_code < 400 else "⚠️" if response.status_code < 500 else "❌"
            query_str = f" ?{dict(request.query_params)}" if request.query_params else ""
            
            # Include request body size if available
            content_length = request.headers.get("content-length", "unknown")
            user_agent = request.headers.get("user-agent", "unknown")[:100]  # Truncate long UAs
            
            log_message = (
                f"{status_emoji} {response.status_code} {request.method} {request.url.path}{query_str} "
                f"from {client_ip} ({process_time:.3f}s) "
                f"[size={content_length} bytes, ua={user_agent}]"
            )
            
            # Always log at INFO level - we need comprehensive access logs
            logger.info(log_message)

            return response

        except HTTPException as http_exc:
            # Log HTTPException requests (400, 404, etc.) before re-raising
            process_time = time.time() - start_time
            status_emoji = "⚠️" if http_exc.status_code < 500 else "❌"
            query_str = f" ?{dict(request.query_params)}" if request.query_params else ""
            content_length = request.headers.get("content-length", "unknown")
            user_agent = request.headers.get("user-agent", "unknown")[:100]
            
            log_message = (
                f"{status_emoji} {http_exc.status_code} {request.method} {request.url.path}{query_str} "
                f"from {client_ip} ({process_time:.3f}s) "
                f"[HTTPException: {http_exc.detail}, size={content_length} bytes, ua={user_agent}]"
            )
            logger.info(log_message)
            
            # Re-raise HTTPException to let the exception handler process it
            # (it will return the correct status code, not 500)
            raise
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"💥 500 {request.method} {request.url.path} from {client_ip} ({process_time:.3f}s) - {type(e).__name__}: {e}"
            )
            raise

    # Custom 404 handler - return JSON instead of HTML
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Return JSON for 404 errors instead of HTML."""
        # If the HTTPException has a detail message, use it (means endpoint exists but no data found)
        # Otherwise use generic "endpoint not found" message
        if hasattr(exc, "detail") and exc.detail:
            message = exc.detail
        else:
            message = "The requested endpoint does not exist"

        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": message,
                "path": str(request.url.path),
                "method": request.method,
                "compute_cluster": get_compute_cluster_name(),
            },
        )

    # Global exception handler for all HTTPExceptions
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Add compute_cluster to all HTTPException error responses."""
        # Build error response with compute_cluster
        error_content = {
            "error": exc.detail if exc.detail else "An error occurred",
            "compute_cluster": get_compute_cluster_name(),
        }

        # If there are headers on the exception, include them
        headers = getattr(exc, "headers", None)

        return JSONResponse(status_code=exc.status_code, content=error_content, headers=headers)

    # Global exception handler for all unhandled exceptions
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Add compute_cluster to all unhandled exception error responses."""
        logger.error(f"Unhandled exception: {exc}")
        logger.exception(exc)

        # Include error details for debugging (helpful for clients and developers)
        error_content = {
            "error": "Internal server error",
            "compute_cluster": get_compute_cluster_name(),
            "detail": str(exc),
            "error_type": type(exc).__name__
        }

        return JSONResponse(status_code=500, content=error_content)

    # -------------------------------------------------------------------------------
    # Health Check Endpoint
    # -------------------------------------------------------------------------------

    def convert_to_iso(dt):
        """Convert datetime to ISO format string."""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        return dt.isoformat()

    @app.get("/health")
    async def health_check() -> JSONResponse:
        """
        Comprehensive health check endpoint with system metrics.
        Reads cached health data from Redis (populated by system_monitor.py).
        Returns error if cache is stale (>90 seconds old).
        
        CRITICAL: Uses timeout on Redis operations to prevent hanging if Redis is slow/unresponsive.
        """
        from lib.job_manager import get_redis_client
        
        current_time = time.time()
        uptime_seconds = current_time - SERVER_STARTUP_TIME
        
        # Read cached health data from Redis with timeout handling and retry logic
        # CRITICAL: Run blocking Redis operation in thread pool to avoid blocking event loop
        redis_key = "health:cache"
        cached_data = None
        redis_error = None
        
        def _get_redis_cache_with_retry():
            """Blocking Redis operation with retry - runs in thread pool.
            Retries for up to 2 seconds if key is missing (handles transient cache refresh issues).
            """
            import redis
            import time
            
            start_time = time.time()
            max_retry_time = 2.0  # Retry for up to 2 seconds
            retry_delays = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4]  # Exponential backoff delays
            attempt = 0
            
            while time.time() - start_time < max_retry_time:
                try:
                    redis_client = get_redis_client()
                    # Verify connection is alive
                    redis_client.ping()
                    # Redis client now has socket_timeout=2.0, so this will timeout quickly if Redis is hung
                    result = redis_client.get(redis_key)
                    
                    if result is not None:
                        # Success - found the key
                        if attempt > 0:
                            logger.debug(f"✅ Health endpoint: Found health:cache after {attempt} retries ({time.time() - start_time:.3f}s)")
                        return result, None
                    
                    # Key doesn't exist - check if it really doesn't exist
                    exists = redis_client.exists(redis_key)
                    if exists:
                        # Key exists but GET returned None - possible decode issue
                        logger.warning(f"⚠️  Health endpoint: GET returned None but EXISTS=1 for {redis_key} (possible decode issue)")
                        return None, "Redis decode error: key exists but GET returned None"
                    
                    # Key truly doesn't exist - retry if we have time
                    elapsed = time.time() - start_time
                    if elapsed < max_retry_time:
                        # Wait before retry (use exponential backoff, but cap at remaining time)
                        delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                        remaining_time = max_retry_time - elapsed
                        delay = min(delay, remaining_time - 0.01)  # Leave 10ms buffer
                        if delay > 0:
                            time.sleep(delay)
                        attempt += 1
                    else:
                        break
                        
                except redis.TimeoutError as e:
                    return None, f"Redis timeout: {e}"
                except redis.ConnectionError as e:
                    return None, f"Redis connection error: {e}"
                except Exception as e:
                    return None, f"Redis error: {e}"
            
            # Exhausted retries - key still not found
            elapsed = time.time() - start_time
            logger.warning(f"⚠️  Health endpoint: health:cache key not found after {attempt} attempts ({elapsed:.3f}s)")
            return None, None
        
        try:
            import asyncio
            # Run blocking Redis operation in thread pool - prevents blocking event loop
            cached_data, redis_error = await asyncio.to_thread(_get_redis_cache_with_retry)
            if redis_error:
                logger.warning(f"⚠️  Health endpoint: {redis_error}")
        except Exception as e:
            redis_error = f"Unexpected error: {e}"
            logger.warning(f"⚠️  Health endpoint: {redis_error}")
        
        if not cached_data:
            # If Redis error occurred, include it in the response
            error_msg = "Health data not available - system monitor may not be running"
            if redis_error:
                error_msg += f" (Redis error: {redis_error})"
            else:
                error_msg += " (health:cache key not found in Redis after retries)"
            
            logger.error(f"❌ Health endpoint returning 503: {error_msg}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "hostname": socket.gethostname(),
                    "error": error_msg,
                    "redis_error": redis_error,
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )
        
        try:
            health_data = json.loads(cached_data)
            cache_timestamp = health_data.get("timestamp", 0)
            age_seconds = current_time - cache_timestamp
            
            # If cache is older than 90 seconds, return error
            if age_seconds > 90:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "hostname": socket.gethostname(),
                        "error": f"Health data is stale ({age_seconds:.0f}s old, max 90s)",
                        "cache_age_seconds": age_seconds,
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                )
            
            # Use cached data
            gpu_info = health_data.get("gpu", {})
            celery_info = health_data.get("celery", {})
            job_queues = health_data.get("jobs", {})
            version = health_data.get("version", "unknown")
            git_info = health_data.get("git", {"commit": "unknown", "branch": "unknown"})
            cached_uptime = health_data.get("uptime_seconds", 0)

            # Format uptime helper
            def format_uptime(seconds):
                days = int(seconds // 86400)
                hours = int((seconds % 86400) // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                if days > 0:
                    return f"{days}d {hours}h {minutes}m {secs}s"
                elif hours > 0:
                    return f"{hours}h {minutes}m {secs}s"
                elif minutes > 0:
                    return f"{minutes}m {secs}s"
                else:
                    return f"{secs}s"
            
            # Calculate training capacity from cached data
            ready_for_training = False
            training_capacity_info = {}
            try:
                no_training_running = job_queues.get("training_jobs", {}).get("running", 0) == 0
                gpu_capacity_ok = False
                gpu_free_pct = 0
                if isinstance(gpu_info, dict) and gpu_info.get("available"):
                    total_free = gpu_info.get("total_free_gb", 0)
                    total_capacity = gpu_info.get("total_capacity_gb", 0)
                    if total_capacity > 0:
                        gpu_free_pct = (total_free / total_capacity) * 100
                        gpu_capacity_ok = gpu_free_pct >= 50.0
                ready_for_training = no_training_running and gpu_capacity_ok
                training_capacity_info = {
                    "ready_for_training": ready_for_training,
                    "reasons": {
                        "no_training_jobs_running": no_training_running,
                        "gpu_capacity_available": gpu_capacity_ok,
                        "gpu_free_pct": round(gpu_free_pct, 1) if gpu_free_pct > 0 else None,
                    },
                }
            except Exception as e:
                training_capacity_info = {"ready_for_training": False, "error": str(e)}
            
            # Supervisor/system info from cached health data
            supervisor_processes = health_data.get("supervisor", {"available": False, "error": "Not in cached health data"})
            system_info = health_data.get("system", {})
            
            # Check prediction server health
            try:
                from prediction_client import get_prediction_server_health
                prediction_server = get_prediction_server_health()
            except Exception as e:
                prediction_server = {"available": False, "error": str(e)}
            
            return JSONResponse(
                {
                    "status": "healthy",
                    "service": "featrix-sphere-compute-api",
                    "hostname": socket.gethostname(),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "version": version,
                    "git": git_info,
                    "ready_for_training": ready_for_training,
                    "training_capacity": training_capacity_info,
                    "uptime": {
                        "api_seconds": round(uptime_seconds, 2),
                        "api_formatted": format_uptime(uptime_seconds),
                        "api_started_at": datetime.datetime.fromtimestamp(SERVER_STARTUP_TIME).isoformat(),
                        "monitor_seconds": round(cached_uptime, 2) if cached_uptime else None,
                        "monitor_formatted": format_uptime(cached_uptime) if cached_uptime else None,
                    },
                    "gpu": gpu_info,
                    "celery": celery_info,
                    "jobs": job_queues,
                    "supervisor": supervisor_processes,
                    "system": system_info,
                    "prediction_server": prediction_server,
                    "cache_age_seconds": round(age_seconds, 2),
                }
            )
        except json.JSONDecodeError as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "hostname": socket.gethostname(),
                    "error": f"Invalid health data in cache: {e}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "hostname": socket.gethostname(),
                    "error": f"Error reading health cache: {e}",
                    "timestamp": datetime.datetime.now().isoformat(),
                }
            )

    # -------------------------------------------------------------------------------
    # Agent Endpoints
    # -------------------------------------------------------------------------------
    
    class SinglePredictorSpec(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        target_column: str
        target_column_type: str  # "set" or "scalar"
        epochs: int = 50
        batch_size: int = 256
        learning_rate: float = 0.001
        name: str | None = None  # Optional name for the single predictor

    class CreateSessionRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings
        input_filename: str | None = None
        session_type: str = "sphere"
        name: str | None = None  # Optional name for the session/model (for identification and metadata)
        session_name_prefix: str | None = (
            None  # Optional prefix for session ID. Session will be named <prefix>-<full-uuid>
        )
        single_predictors: list[SinglePredictorSpec] = []
        # Movie frame and WeightWatcher intervals (default to 3 for better performance)
        movie_frame_interval: int = 3
        weightwatcher_save_every: int = 5
        # VISUALIZATION ONLY: Prefer rows with non-null values in these columns for epoch projections
        # ⚠️ IMPORTANT: This parameter ONLY affects visualization sampling and has NO EFFECT on model training
        # Use this to ensure important columns are represented in training movie visualizations
        important_columns_for_visualization: list[str] = []

    # ============================================================================
    # String Server Proxy Endpoints
    # ============================================================================
    # These endpoints proxy requests to the local string embedding server at
    # http://localhost:9000. They provide a fallback when clients can't reach
    # taco.local:9000 directly and ensure the response format matches what the
    # string server client expects.
    
    @app.post("/strings/encode")
    async def proxy_string_encode(request: Request) -> JSONResponse:
        """
        Proxy endpoint for single string encoding.
        Forwards requests to local string server at http://localhost:9000/encode.
        
        Request body: {"text": "string to encode"}
        Response: {"embedding": [float, ...], "dimension": int}
        """
        import requests
        
        try:
            # Get request body
            request_data = await request.json()
            
            # Forward to local string server (using requests in async context)
            def _make_request():
                response = requests.post(
                    "http://localhost:9000/encode",
                    json=request_data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            
            # Run blocking request in thread pool
            result = await aio.to_thread(_make_request)
            return JSONResponse(content=result)
                
        except requests.RequestException as e:
            logger.error(f"String server proxy error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"String server unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"String encoding error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"String encoding failed: {str(e)}"
            )
    
    @app.post("/strings/encode/batch")
    async def proxy_string_encode_batch(request: Request) -> JSONResponse:
        """
        Proxy endpoint for batch string encoding.
        Forwards requests to local string server at http://localhost:9000/encode/batch.
        
        Request body: {"texts": ["string1", "string2", ...]}
        Response: {"embeddings": [[float, ...], ...], "dimension": int, "count": int}
        """
        import requests
        
        try:
            # Get request body
            request_data = await request.json()
            
            # Forward to local string server (using requests in async context)
            def _make_request():
                response = requests.post(
                    "http://localhost:9000/encode/batch",
                    json=request_data,
                    timeout=60.0  # Longer timeout for batches
                )
                response.raise_for_status()
                return response.json()
            
            # Run blocking request in thread pool
            result = await aio.to_thread(_make_request)
            
            # Ensure response has dimension field (client expects it)
            if "embeddings" in result and len(result["embeddings"]) > 0:
                if "dimension" not in result:
                    # Infer dimension from first embedding
                    result["dimension"] = len(result["embeddings"][0])
                if "count" not in result:
                    # Add count field
                    result["count"] = len(result["embeddings"])
            
            return JSONResponse(content=result)
                
        except requests.RequestException as e:
            logger.error(f"String server batch proxy error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"String server unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Batch string encoding error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Batch string encoding failed: {str(e)}"
            )
    
    @app.get("/strings/health")
    async def proxy_string_health() -> JSONResponse:
        """
        Proxy endpoint for string server health check.
        Forwards requests to local string server at http://localhost:9000/health.
        
        Response: {"status": "healthy", "model_loaded": bool, ...}
        """
        import requests
        
        try:
            def _make_request():
                response = requests.get("http://localhost:9000/health", timeout=5.0)
                response.raise_for_status()
                return response.json()
            
            # Run blocking request in thread pool
            result = await aio.to_thread(_make_request)
            return JSONResponse(content=result)
                
        except requests.RequestException as e:
            logger.error(f"String server health check proxy error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"String server unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"String server health check error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}"
            )

    @app.post("/session")
    async def create_session_endpoint(request: CreateSessionRequest | None = None) -> JSONResponse:
        """Create agent."""

        # Handle both empty requests and requests with parameters
        input_filename = None
        session_type = "sphere"
        name = None
        session_name_prefix = None
        single_predictors = []
        movie_frame_interval = 3
        weightwatcher_save_every = 5
        important_columns_for_visualization = []

        if request:
            input_filename = request.input_filename
            session_type = request.session_type
            name = request.name
            session_name_prefix = request.session_name_prefix
            single_predictors = request.single_predictors
            movie_frame_interval = request.movie_frame_interval
            weightwatcher_save_every = request.weightwatcher_save_every
            important_columns_for_visualization = request.important_columns_for_visualization

        # Validate single predictor specifications
        for i, predictor in enumerate(single_predictors):
            if predictor.target_column_type not in ["set", "scalar"]:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"single_predictors[{i}].target_column_type must be 'set' or 'scalar'",
                )

        # Initialize agent
        try:
            session = create_session(
                session_type=session_type,
                start=True,
                input_filename=input_filename,
                name=name,
                session_name_prefix=session_name_prefix,
                single_predictors=single_predictors,
                movie_frame_interval=movie_frame_interval,
                weightwatcher_save_every=weightwatcher_save_every,
                important_columns_for_visualization=important_columns_for_visualization,
            )
        except Exception as e:
            # Check if this is a NodeUpgradingException
            if isinstance(e, NodeUpgradingException):
                logger.warning(f"Node is upgrading: {e}")
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))
            raise

        logger.info(
            f"Created new session: {session.get('session_id')} with input_filename: {input_filename} and {len(single_predictors)} single predictors"
        )
        logger.debug(f"Session details: {session}")
        logger.debug(f"Single predictors: {[{sp.target_column: sp.target_column_type} for sp in single_predictors]}")

        serialized_session = serialize_session(session)

        return JSONResponse(serialized_session)

    @app.get("/session/{id}")
    async def get_session_endpoint(id: str) -> JSONResponse:
        """Get agent status and results.
        
        CRITICAL: Runs get_session_info() in thread pool to avoid blocking the event loop.
        Without this, slow disk I/O (backplane searches, file locks) blocks ALL requests.
        """

        try:
            # Run blocking I/O in thread pool - prevents blocking the entire API
            import asyncio
            session_info = await asyncio.to_thread(get_session_info, session_id=id)
        except FileNotFoundError:
            # Session not found is a normal condition, not an error - just log at debug level
            logger.debug(f"Session {id} not found (normal condition)")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Session {id} not found")
        except Exception as e:
            logger.error(f"❌ Unexpected error loading session {id}: {type(e).__name__}: {e}")
            logger.error(f"   Exception details: {repr(e)}")

            logger.error(f"   Full traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error loading session: {str(e)}")

        # logger.debug(f"Raw session info for {id}: {session_info}")

        # Defensive check: ensure session_info has expected structure
        if not isinstance(session_info, dict):
            logger.error(f"❌ get_session_info returned unexpected type: {type(session_info)}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Invalid session info format")
        
        if "session" not in session_info:
            logger.error(f"❌ get_session_info missing 'session' key. Keys: {list(session_info.keys())}")
            logger.error(f"   session_info: {session_info}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Session info missing 'session' key")

        # CRITICAL: Include status in API response (it's computed dynamically, not stored)
        serialized_session = serialize_session(session_info["session"], include_status=True)
        serialized_jobs = {job_id: serialize_job(job) for job_id, job in session_info.get("jobs", {}).items()}

        output = {
            "session": serialized_session,
            "jobs": serialized_jobs,
            "job_queue_positions": session_info.get("job_queue_positions", {}),
            "detailed_queue_info": session_info.get("detailed_queue_info", {}),  # Enhanced queue information
        }

        # logger.debug(f"Session {id} output: {output}")

        return JSONResponse(output)

    @app.post("/session/{session_id}/notify")
    async def set_notification_email(session_id: str, request: Request) -> JSONResponse:
        """Set notification email for session."""

        data = await request.json()
        to_address = data.get("to_address")

        if not to_address:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="to_address is required")

        validated_address = validate_and_normalize_email(to_address)
        if validated_address is None:
            logger.warning(f"Invalid email address provided for session {session_id}: {to_address}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Address {to_address} is invalid.")

        add_notification_email_to_session(session_id, validated_address)
        logger.info(f"Notification email {validated_address} added to session {session_id}")

        return JSONResponse(
            {
                "session_id": session_id,
                "notification_email": validated_address,
            }
        )

    @app.get("/session/{id}/projections")
    async def get_session_projections(id: str) -> JSONResponse:
        session = load_session(id)

        projections = session.get("projections")

        if projections is None:
            post_slack_alert(f"session={id}; error getting projections")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Projections not found")

        projections_path = Path(projections)
        if not projections_path.exists():
            post_slack_alert(f"session={id}; error getting projections")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Projections not found")

        projections = json.loads(projections_path.read_text())

        return JSONResponse(
            {
                "projections": projections,
            }
        )

    @app.get("/session/{id}/epoch_projections")
    async def get_session_epoch_projections(id: str) -> JSONResponse:
        """Get epoch projection files for training movies."""

        logger.info(f"📥 Fetching epoch projections for session {id}")
        
        # Load session with detailed error handling
        try:
            session = load_session(id)
            logger.info(f"✅ Session loaded successfully (keys: {list(session.keys())})")
        except FileNotFoundError as fnf_err:
            logger.error(f"❌ Session {id} not found: {fnf_err}")
            post_slack_alert(f"session={id}; session file not found for epoch_projections")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Session not found: {str(fnf_err)}")
        except Exception as load_err:
            logger.error(f"❌ Error loading session {id}: {load_err}")
            logger.error(f"   Full traceback: {traceback.format_exc()}")
            post_slack_alert(f"session={id}; error loading session for epoch_projections: {load_err}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error loading session: {str(load_err)}"
            )

        # Find the epoch projections directory by looking in job output directories
        try:
            logger.info(f"🔍 Getting session info for {id}")
            session_info = get_session_info(session_id=id)
            logger.info(f"✅ Session info retrieved (jobs: {len(session_info.get('jobs', {}))})")
            jobs = session_info.get("jobs", {})

            # Look for epoch projections in train_es job output (including running and done jobs)
            epoch_projections_found = {}
            metadata_found = None
            search_details = []

            for job_id, job in jobs.items():
                job_type = job.get("type", "")
                job_status = job.get("status", "unknown")

                if job_type == "train_es":  # Check both running and done ES jobs
                    # Check for epoch projections in this job's output directory
                    session_id = job.get("session_id")
                    job_output_dir = get_job_output_path(job_id, session_id, job_type)
                    epoch_dir = job_output_dir / "epoch_projections"

                    search_details.append(
                        {
                            "job_id": job_id,
                            "job_status": str(job_status),  # Convert to string for JSON serialization
                            "job_output_dir": str(job_output_dir),
                            "epoch_dir": str(epoch_dir),
                            "epoch_dir_exists": epoch_dir.exists(),
                        }
                    )

                    if epoch_dir.exists():
                        # Load movie metadata if available
                        metadata_file = epoch_dir / "movie_metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file) as f:
                                    metadata_found = json.load(f)
                                logger.info(f"✅ Loaded epoch metadata from {metadata_file}")
                            except json.JSONDecodeError as json_err:
                                logger.warning(f"⚠️  Metadata file is corrupted (invalid JSON): {json_err}")
                            except PermissionError as perm_err:
                                logger.warning(f"⚠️  Permission denied reading metadata: {perm_err}")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not load epoch metadata: {e}")

                        # Load all epoch projection files
                        try:
                            projection_files = list(epoch_dir.glob("projections_epoch_*.json"))
                            logger.info(f"🔍 Found {len(projection_files)} epoch projection files in {epoch_dir}")
                        except PermissionError as perm_err:
                            logger.error(f"❌ Permission denied listing epoch directory {epoch_dir}: {perm_err}")
                            post_slack_alert(f"session={id}; permission denied accessing epoch_projections directory")
                            raise HTTPException(
                                status_code=HTTPStatus.FORBIDDEN,
                                detail=f"Permission denied accessing epoch projections directory"
                            )

                        for proj_file in sorted(projection_files):
                            try:
                                with open(proj_file) as f:
                                    proj_data = json.load(f)
                                    epoch_num = proj_data.get("epoch", 0)
                                    epoch_projections_found[f"epoch_{epoch_num}"] = proj_data
                                    logger.info(f"✅ Loaded epoch {epoch_num} from {proj_file}")
                            except json.JSONDecodeError as json_err:
                                logger.warning(f"⚠️  Projection file {proj_file.name} is corrupted (invalid JSON): {json_err}")
                            except PermissionError as perm_err:
                                logger.warning(f"⚠️  Permission denied reading {proj_file.name}: {perm_err}")
                            except Exception as e:
                                logger.warning(f"⚠️  Could not load epoch projection {proj_file.name}: {e}")

                        # If we found projections, no need to check other jobs
                        if epoch_projections_found:
                            break

            # Enhanced error reporting with search details
            if not epoch_projections_found:
                logger.error(f"❌ No epoch projections found for session {id}")
                logger.error(f"   Searched jobs: {search_details}")

                # Check if ES training is still running
                running_es_jobs = [detail for detail in search_details if str(detail["job_status"]) == "running"]
                if running_es_jobs:
                    logger.info("ℹ️  ES training still running - epoch projections may be generated soon")
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail="Epoch projections not yet available - ES training in progress",
                    )

                # FALLBACK: Try to generate epoch projections from completed ES training
                logger.info("🔍 Attempting to generate epoch projections from embedding space...")
                try:
                    # Look for completed ES training with embedding space
                    embedding_space_path = session.get("embedding_space")
                    if embedding_space_path and embedding_space_path_exists(embedding_space_path):
                        logger.info(f"✅ Found embedding space at {embedding_space_path}")
                        logger.info("⚠️ Epoch projections can be generated manually if needed")
                        raise HTTPException(
                            status_code=HTTPStatus.NOT_FOUND,
                            detail="Epoch projections not found - training completed without epoch projection generation enabled",
                        )
                    else:
                        logger.error("❌ No embedding space found for fallback generation")

                except Exception as fallback_error:
                    logger.error(f"❌ Fallback epoch projection check failed: {fallback_error}")

                post_slack_alert(
                    f"session={id}; epoch projections not found after searching {len(search_details)} ES jobs"
                )
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Epoch projections not found - may not have been enabled during training",
                )

            response_data = {
                "epoch_projections": epoch_projections_found,
                # "search_details": search_details  # Removed to avoid JSON serialization issues
            }

            if metadata_found:
                response_data["metadata"] = metadata_found

            logger.info(f"✅ Returning {len(epoch_projections_found)} epoch projections for session {id}")
            
            # Try to create JSONResponse - catch serialization errors explicitly
            try:
                return JSONResponse(response_data)
            except (TypeError, ValueError) as json_err:
                logger.error(f"❌ JSON serialization error: {json_err}")
                logger.error(f"   Response data keys: {list(response_data.keys())}")
                logger.error(f"   Epoch projections keys: {list(epoch_projections_found.keys())}")
                post_slack_alert(f"session={id}; JSON serialization error in epoch_projections: {json_err}")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Failed to serialize epoch projection data: {str(json_err)}"
                )

        except FileNotFoundError:
            logger.error(f"❌ Session {id} not found for epoch projections")
            post_slack_alert(f"session={id}; session not found for epoch projections")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
        except HTTPException:
            # Re-raise HTTP exceptions without modification
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error getting epoch projections for session {id}: {e}")

            logger.error(f"Full traceback: {traceback.format_exc()}")
            post_slack_alert(f"session={id}; error getting epoch projections: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error retrieving epoch projections: {str(e)}"
            )

    @app.get("/session/{id}/training_movie")
    async def get_session_training_movie(id: str) -> JSONResponse:
        """Get ES training movie JSON with complete trajectory data."""

        session = load_session(id)

        # Find the training movie JSON by looking in job output directories
        try:
            session_info = get_session_info(session_id=id)
            jobs = session_info.get("jobs", {})

            # Look for training movie in train_es job output
            training_movie_found = None

            for job_id, job in jobs.items():
                job_type = job.get("type", "")
                if job_type == "train_es" and job.get("status") == "done":
                    # Check for training movie in this job's output directory
                    session_id = job.get("session_id")
                    job_output_dir = get_job_output_path(job_id, session_id, job_type)

                    # Look for training movie files with different naming patterns
                    possible_files = [
                        job_output_dir / f"training_movie_{job_id}.json",
                        job_output_dir / "training_movie.json",
                    ]

                    for movie_file in possible_files:
                        if movie_file.exists():
                            try:
                                with open(movie_file) as f:
                                    training_movie_found = json.load(f)
                                break
                            except Exception as e:
                                logger.warning(f"Could not load training movie {movie_file}: {e}")

                    if training_movie_found:
                        break

            if not training_movie_found:
                post_slack_alert(f"session={id}; training movie not found")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Training movie not found")

            # Apply NaN cleaning to prevent JSON encoding errors
            cleaned_movie_data = replace_nans_with_nulls(training_movie_found)

            return JSONResponse(
                {
                    "training_movie": cleaned_movie_data,
                }
            )

        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for training movie")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
        except Exception as e:
            post_slack_alert(f"session={id}; error getting training movie: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error retrieving training movie")

    @app.get("/session/{id}/preview")
    async def get_session_preview(id: str) -> JSONResponse:
        session = load_session(id)

        preview = session.get("preview_png")

        if preview is None:
            post_slack_alert(f"session={id}; error getting preview")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="preview not found")

        preview_path = Path(preview)
        if not preview_path.exists():
            post_slack_alert(f"session={id}; error getting preview")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="preview not found")

        return FileResponse(preview_path, media_type="image/png")

    def encode_record_both(es, record):
        """
        Efficiently encode a record once and return both short and full embeddings.
        This avoids the 2x performance penalty of calling encode_record() twice.
        """
        from featrix.neural.featrix_token import create_token_batch

        # Apply JSON transformations if available (from encode_record)
        if hasattr(es, "json_transformations") and es.json_transformations:
            record = es._apply_json_transformations(record)

        # Tokenize the record (from encode_record)
        record_tokens = {}
        for field, value in record.items():
            field = field.strip()

            # Skip __featrix internal fields
            if field.startswith("__featrix"):
                continue

            # Skip fields without codecs
            if field not in es.col_codecs:
                continue

            codec = es.col_codecs[field]
            token = codec.tokenize(value)
            record_tokens[field] = token

        # Get base token dict and populate with record tokens
        batch_tokens = es._get_base_token_dict()
        for field, token in record_tokens.items():
            batch_tokens[field] = create_token_batch([token])

        # Set encoder to eval mode
        was_training = es.encoder.training
        if was_training:
            es.encoder.eval()

        # Encode once and get BOTH embeddings
        device = next(es.encoder.parameters()).device
        with torch.no_grad():
            short_encoding, full_encoding = es.encoder.encode(batch_tokens)

        # Restore training mode if needed
        if was_training:
            es.encoder.train()

        # Squeeze and move to CPU
        short_encoding = short_encoding.squeeze(dim=0).detach().cpu()
        full_encoding = full_encoding.squeeze(dim=0).detach().cpu()

        return short_encoding, full_encoding

    @app.post("/session/{id}/encode_records")
    async def get_session_encode_records(id: str, request: Request) -> JSONResponse:
        """
        Encode one or more records using the trained embedding space.

        Accepts either:
        - Single record: {"query_record": {...}}
        - Multiple records: {"query_records": [{...}, {...}]}

        Returns embeddings in the same format (single or list).
        """
        fix_paths()

        session = load_session(id)

        request_data = await request.json()

        # Support both single record and batch encoding
        is_batch = "query_records" in request_data

        # Validate that at least one of the required fields is present
        if not is_batch and "query_record" not in request_data:
            available_fields = list(request_data.keys())
            logger.error(f"Missing required field. Request contains fields: {available_fields}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Missing required field 'query_record' or 'query_records'. Request contains: {available_fields}",
            )

        query_records = request_data.get("query_records") if is_batch else [request_data["query_record"]]

        es_path_str = session.get("embedding_space")

        if es_path_str is None:
            post_slack_alert(f"session={id}; embedding space not found #1")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Embedding space not found")

        # Resolve path, checking published location first
        es_path = resolve_session_path(id, es_path_str)

        if not es_path.exists():
            post_slack_alert(f"session={id}; embedding space not found #2")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Embedding space not found at {es_path}")

        # Try to get embedding space from cache first
        es_path_str = str(es_path)
        es = embedding_space_cache.get(es_path_str)

        if es is None:
            # Cache miss - load from disk
            logger.info(f"🔄 ES CACHE MISS - Loading embedding space from disk: {es_path_str}")
            es = load_embedded_space(es_path)

            # Hydrate to GPU if available
            if hasattr(es, "hydrate_to_gpu_if_needed"):
                es.hydrate_to_gpu_if_needed()

            # Add to cache
            embedding_space_cache.put(es_path_str, es)

        # Process all records efficiently - encode once and get both embeddings
        results = []
        for query_record in query_records:
            # Encode once to get BOTH short and full embeddings (2x speedup!)
            # NO ERROR HANDLING - crash hard if anything fails
            theEmbedding, fullEmbedding = encode_record_both(es, query_record)
            theEmbedding = theEmbedding.tolist()
            fullEmbedding = fullEmbedding.tolist()

            results.append(
                {
                    "query_record": query_record,
                    "embedding": theEmbedding,
                    "embedding_long": fullEmbedding,
                }
            )

        # Return single result or list depending on input
        if is_batch:
            response = {
                "results": results,
                "__featrix_help": "embedding is the 3d embedding; embedding_long is the full length embedding; query_record is your input record echoed back to you",
            }
            logger.info(f"📦 Returning batch response: {len(results)} results, keys={list(response.keys())}")
            return JSONResponse(response)
        else:
            response = {
                **results[0],
                "__featrix_help": "embedding is the 3d embedding; embedding_long is the full length embedding; query_record is your input record echoed back to you",
            }
            logger.info(f"📦 Returning single response: keys={list(response.keys())}")
            return JSONResponse(response)

    class SimilaritySearchRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        query_record: Any

    class AddRecordsRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        records: List[Dict[str, Any]]

    @app.post("/session/{id}/similarity_search")
    async def get_session_similarity_search(id: str, request: SimilaritySearchRequest) -> JSONResponse:
        try:
            search_result = find_closest_points(id, request.query_record)

        except ValueError as e:
            # Handle missing vector database or embedding space
            error_msg = str(e)
            if "does not have a vector_db" in error_msg or "does not have an embedding space" in error_msg:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Internal error: no vector database found for {id}"
                )
            # Re-raise other ValueErrors as 500
            traceback.print_exc()
            post_slack_alert(f"session={id}; error with similarity search: {error_msg}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error with similarity search")
        except Exception:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error with similarity search")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error with similarity search")

        try:
            search_result = replace_nans_with_nulls(search_result)
        except:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error with similarity search -- converting nans -> nones")
        # print("get_session_similarity_search... results = ", search_result)
        return JSONResponse(
            {
                "query_record": request.query_record,
                "results": search_result.get("results", []),
                "stats": search_result.get("stats", {}),
            }
        )

    @app.post("/session/{id}/add_records")
    async def add_records_to_vector_db(id: str, request: AddRecordsRequest) -> JSONResponse:
        """
        Add new records to an existing vector database for similarity search.

        This endpoint:
        1. Loads the existing embedding space for the session
        2. Encodes the new records using the trained embedding space
        3. Appends them to the existing LanceDB vector database

        Args:
            id: Session ID
            request: AddRecordsRequest containing list of records to add

        Returns:
            Statistics about the append operation including records added and failed
        """
        try:

            from featrix.neural.io_utils import load_embedded_space as load_embedding_space
            from lib.vector_db import CSVtoLanceDB

            session = load_session(id)
            if not session:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

            # Load the embedding space
            es_path = Path("jobs") / id / "featrix_embedding_space.pt"
            if not es_path.exists():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Embedding space not found. Train the embedding space first.",
                )

            es = load_embedding_space(es_path)

            # Load the vector database
            vector_db_path = Path("jobs") / id / "lance_db"
            sqlite_db_path = Path("jobs") / id / "data.db"

            if not vector_db_path.exists():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Vector database not found. Create vector DB first (wait for training to complete).",
                )

            # Initialize vector DB and load existing table
            vector_db = CSVtoLanceDB(
                featrix_es=es, sqlite_db_path=str(sqlite_db_path), lancedb_path=str(vector_db_path)
            )
            vector_db.load_existing()

            # Append the new records
            result = vector_db.append_records(request.records)

            return JSONResponse(
                {
                    "session_id": id,
                    "records_added": result["records_added"],
                    "records_failed": result["records_failed"],
                    "success": result["success"],
                    "message": result["message"],
                    "new_total": result.get("new_total", 0),
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding records to vector DB: {e}")
            traceback.print_exc()
            post_slack_alert(f"session={id}; error adding records to vector DB")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error adding records: {str(e)}")

    @app.get("/session/{id}/vectordb_size")
    async def get_vectordb_size(id: str) -> JSONResponse:
        """
        Get the number of records in the vector database.

        Returns:
            Dictionary containing the number of records in the vector database
        """
        try:

            from featrix.neural.io_utils import load_embedded_space as load_embedding_space
            from lib.vector_db import CSVtoLanceDB

            session = load_session(id)
            if not session:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

            # Load the embedding space
            es_path = Path("jobs") / id / "featrix_embedding_space.pt"
            if not es_path.exists():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Embedding space not found. Train the embedding space first.",
                )

            es = load_embedding_space(es_path)

            # Load the vector database
            vector_db_path = Path("jobs") / id / "lance_db"
            sqlite_db_path = Path("jobs") / id / "data.db"

            if not vector_db_path.exists():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Vector database not found. Create vector DB first (wait for training to complete).",
                )

            # Initialize vector DB and load existing table
            vector_db = CSVtoLanceDB(
                featrix_es=es, sqlite_db_path=str(sqlite_db_path), lancedb_path=str(vector_db_path)
            )
            vector_db.load_existing()

            # Get the size
            size = vector_db.vectordb_size()

            return JSONResponse({"session_id": id, "size": size})

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting vector DB size: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error getting vector DB size: {str(e)}"
            )

    @app.post("/session/{id}/notify")
    async def session_notify(id: str, request: Request) -> JSONResponse:
        session = load_session(id)
        js = await request.json()  # the embedding query
        return JSONResponse({"status": "in queue", "request_echo": js})

    @app.post("/upload_with_new_session/")
    async def upload_with_new_session(file: UploadFile = File(...), request: Request = None, background_tasks: BackgroundTasks = None):
        """
        Upload file and create a new session.
        
        NOTE: This endpoint may take several minutes for large files (50k+ rows, 100+ columns).
        The gateway (nginx/load balancer) must have a timeout >= 5 minutes to avoid 504 errors.
        If you see 504 Gateway Timeout errors, check the gateway timeout configuration.
        """
        import uuid
        trace_id = f"FASTAPI-{uuid.uuid4().hex[:8]}"
        request_start_time = time.time()
        logger.info(f"\n{'='*80}")
        logger.info(f"🔵 [FASTAPI] {trace_id} UPLOAD REQUEST RECEIVED - {datetime.datetime.now().isoformat()}")
        logger.info(f"{'='*80}")
        logger.info(f"   File: {file.filename}")
        logger.info(f"   Content type: {file.content_type}")
        try:
            # TODOs:
            # 1. create a separate collection for upload document, where
            # we'll keep the upload metadata.
            # 2. move to an async api.
            # 3. protect against files that are too large

            original_extension = Path(file.filename).suffix

            new_file_name = f"{str(uuid4())}{original_extension}"

            file_path = config.data_dir / new_file_name

            logger.info(f"🔵 [FASTAPI] {trace_id} Saving file to: {file_path}")
            upload_start_time = time.time()
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            upload_elapsed = time.time() - upload_start_time
            logger.info(f"🔵 [FASTAPI] {trace_id} File uploaded successfully: {file.filename} -> {new_file_name} (took {upload_elapsed:.2f}s)")

        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to save uploaded file {file.filename}: {error_type}: {error_msg}")
            traceback.print_exc()
            post_slack_alert(f"error with upload - failed to save data: {error_type}: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {error_type}: {error_msg}")

        # File size safeguard... be careful.
        sampling_warning = None
        try:
            fix_paths()
            import gzip
            import io

            import pandas as pd
            from featrix.neural.featrix_csv import featrix_wrap_pd_read_csv
            from lib.sphere_config import get_row_limit

            # Handle different file types
            try:
                file_ext = file_path.suffix.lower()
                read_start_time = time.time()
                
                if file_ext == ".gz":
                    logger.info(f"🔵 [FASTAPI] {trace_id} Detected gzipped file: {file_path}")
                    # Read gzipped CSV directly with pandas
                    df = pd.read_csv(file_path, compression="gzip")
                elif file_ext == ".parquet":
                    logger.info(f"🔵 [FASTAPI] {trace_id} Detected Parquet file: {file_path}")
                    # Read Parquet file - use engine='pyarrow' for better performance if available
                    try:
                        df = pd.read_parquet(file_path, engine='pyarrow')
                    except Exception:
                        # Fallback to default engine
                        df = pd.read_parquet(file_path)
                elif file_ext in [".json", ".jsonl"]:
                    logger.info(f"🔵 [FASTAPI] {trace_id} Detected JSON/JSONL file: {file_path}")
                    # Read JSON or JSONL file
                    if file_ext == ".jsonl":
                        df = pd.read_json(file_path, lines=True)
                    else:
                        df = pd.read_json(file_path)
                else:
                    # Assume CSV
                    logger.info(f"🔵 [FASTAPI] {trace_id} Reading CSV file: {file_path}")
                    df = featrix_wrap_pd_read_csv(file_path)
                
                read_elapsed = time.time() - read_start_time
                logger.info(f"🔵 [FASTAPI] {trace_id} DataFrame read completed in {read_elapsed:.2f}s ({len(df)} rows, {len(df.columns)} columns)")
                
                # Check if file is empty or has no columns
                if df.empty or len(df.columns) == 0:
                    error_msg = f"Uploaded file '{file.filename}' is empty or has no columns. Please upload a valid data file (CSV, Parquet, JSON, or JSONL) with data."
                    logger.error(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)
                
                original_row_count = len(df)
            except pd.errors.EmptyDataError as e:
                error_msg = f"Uploaded file '{file.filename}' is empty or has no columns. Please upload a valid data file (CSV, Parquet, JSON, or JSONL) with data."
                logger.error(f"{error_msg} Error: {e}")
                raise HTTPException(status_code=400, detail=error_msg)
            except Exception as e:
                error_type = type(e).__name__
                error_msg = f"Failed to read file '{file.filename}': {error_type}: {str(e)}. Supported formats: CSV, Parquet (.parquet), JSON (.json), JSONL (.jsonl)"
                logger.error(error_msg)
                traceback.print_exc()
                raise HTTPException(status_code=400, detail=error_msg)

            # Get row limit from config (can be customized per deployment via /sphere/app/config.json)
            MAX_ROWS_FOR_UPLOAD = get_row_limit()

            if original_row_count > MAX_ROWS_FOR_UPLOAD:
                logger.info(
                    f"Large dataset detected ({original_row_count} rows), sampling to {MAX_ROWS_FOR_UPLOAD:,} rows"
                )
                file_type = "CSV" if file_ext in [".csv", ".gz"] else "Parquet" if file_ext == ".parquet" else "JSON" if file_ext in [".json", ".jsonl"] else "file"
                sampling_warning = f"⚠️  Large dataset detected: Your {file_type} file had {original_row_count:,} rows. For faster processing, we randomly sampled {MAX_ROWS_FOR_UPLOAD:,} rows. Original file preserved as backup."

                os.rename(file_path, str(file_path) + ".orig")
                df = df.sample(MAX_ROWS_FOR_UPLOAD)
                df = df.reset_index(drop=True)

                # Save sampled data back in the same format as the original
                try:
                    if file_ext == ".parquet":
                        # Save as Parquet
                        df.to_parquet(file_path, index=False)
                        logger.info("Wrote sampled data back as Parquet")
                    elif file_ext in [".json", ".jsonl"]:
                        # Save as JSON/JSONL
                        if file_ext == ".jsonl":
                            df.to_json(file_path, orient="records", lines=True)
                        else:
                            df.to_json(file_path, orient="records")
                        logger.info(f"Wrote sampled data back as {file_ext.upper()}")
                    elif file_ext == ".gz":
                        # Handle gzipped CSV - detect delimiter first
                        orig_file_path = str(file_path) + ".orig"
                        delimiter = ","  # default
                        try:
                            with gzip.open(orig_file_path, "rt", encoding="utf-8") as f:
                                first_line = f.readline().strip()
                            # Simple delimiter detection
                            if ";" in first_line and first_line.count(";") > first_line.count(","):
                                delimiter = ";"
                            elif "\t" in first_line:
                                delimiter = "\t"
                            elif "|" in first_line and first_line.count("|") > first_line.count(","):
                                delimiter = "|"
                            logger.info(f"Detected CSV delimiter: '{delimiter}'")
                        except Exception as e:
                            logger.warning(f"Could not detect CSV delimiter, using default: {e}")
                        
                        # Save as gzipped CSV with detected delimiter
                        csv_buffer = io.StringIO()
                        df.to_csv(csv_buffer, index=False, sep=delimiter, quoting=1)
                        csv_data = csv_buffer.getvalue().encode("utf-8")
                        with gzip.open(file_path, "wb") as gz_file:
                            gz_file.write(csv_data)
                        logger.info("Wrote sampled data back as gzipped CSV")
                    else:
                        # Regular CSV - detect delimiter first
                        orig_file_path = str(file_path) + ".orig"
                        delimiter = ","  # default
                        try:
                            with open(orig_file_path, encoding="utf-8") as f:
                                first_line = f.readline().strip()
                            # Simple delimiter detection
                            if ";" in first_line and first_line.count(";") > first_line.count(","):
                                delimiter = ";"
                            elif "\t" in first_line:
                                delimiter = "\t"
                            elif "|" in first_line and first_line.count("|") > first_line.count(","):
                                delimiter = "|"
                            logger.info(f"Detected CSV delimiter: '{delimiter}'")
                        except Exception as e:
                            logger.warning(f"Could not detect CSV delimiter, using default: {e}")
                        
                        # Write back as regular CSV preserving the original format
                        df.to_csv(file_path, index=False, sep=delimiter, quoting=1)
                        logger.info("Wrote sampled data back as CSV")

                except Exception as e:
                    logger.error(f"Failed to save sampled data: {e}")
                    traceback.print_exc()
                    # Try to restore original file
                    try:
                        os.rename(str(file_path) + ".orig", file_path)
                    except:
                        pass
                    raise HTTPException(status_code=500, detail=f"Failed to save sampled data: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to process uploaded data for file {new_file_name}: {error_type}: {error_msg}")
            traceback.print_exc()
            post_slack_alert(f"error with upload - failed to process data: {error_type}: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to process uploaded data: {error_type}: {error_msg}")

        try:
            # Check for quick_run and epochs parameters from form data
            form_data = {}
            if request:
                try:
                    form_data = await request.form()
                except:
                    form_data = {}

            # Extract parameters
            quick_run = form_data.get("quick_run", "").lower() == "true"
            epochs = None

            # Extract session name and prefix
            name = form_data.get("name")  # Optional name for embedding space
            session_name_prefix = form_data.get("session_name_prefix")  # Optional prefix for session ID

            # Extract column overrides and string_list_delimiter
            column_overrides = None
            string_list_delimiter = "|"  # default
            important_columns_for_visualization = []  # default

            # Extract movie frame and weightwatcher intervals
            movie_frame_interval = int(form_data.get("movie_frame_interval", "3"))  # Changed default from 5 to 3
            weightwatcher_save_every = int(form_data.get("weightwatcher_save_every", "5"))

            if "column_overrides" in form_data:
                try:
                    import json

                    column_overrides = json.loads(form_data.get("column_overrides"))
                    logger.info(f"Column overrides received: {column_overrides}")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Invalid column_overrides JSON: {e}")

            if "string_list_delimiter" in form_data:
                string_list_delimiter = form_data.get("string_list_delimiter", "|")
                logger.info(f"String list delimiter: '{string_list_delimiter}'")

            if "important_columns_for_visualization" in form_data:
                try:
                    import json

                    important_columns_for_visualization = json.loads(
                        form_data.get("important_columns_for_visualization")
                    )
                    logger.info(f"Important columns for visualization received: {important_columns_for_visualization}")
                    logger.info("⚠️  Note: This affects VISUALIZATION ONLY, not model training")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Invalid important_columns_for_visualization JSON: {e}")

            # Extract user_metadata
            user_metadata = None
            if "user_metadata" in form_data:
                try:
                    import json

                    user_metadata = json.loads(form_data.get("user_metadata"))
                    logger.info(f"User metadata received: {len(str(user_metadata))} chars")
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Invalid user_metadata JSON: {e}")

            if quick_run:
                epochs = int(form_data.get("epochs", "100"))
                logger.info(f"Quick run enabled: Using {epochs} epochs for faster training")
            elif "epochs" in form_data:
                # Allow epochs to be specified even without quick_run
                try:
                    epochs = int(form_data.get("epochs"))
                    logger.info(f"Epochs specified: {epochs}")
                except (ValueError, TypeError):
                    logger.warning(f"Invalid epochs value: {form_data.get('epochs')}, using auto-calculate")
                    epochs = None

            # Create session WITHOUT starting (start=False) to avoid blocking on job dispatch
            # We'll dispatch the job asynchronously after returning the response
            logger.info(f"🔵 [FASTAPI] {trace_id} Creating session (start=False)...")
            session_start_time = time.time()
            session = create_session(
                session_type="sphere",
                start=False,  # Don't dispatch job synchronously - do it after response
                input_filename=new_file_name,
                epochs=epochs,
                column_overrides=column_overrides,
                string_list_delimiter=string_list_delimiter,
                movie_frame_interval=movie_frame_interval,
                weightwatcher_save_every=weightwatcher_save_every,
                important_columns_for_visualization=important_columns_for_visualization,
                name=name,
                session_name_prefix=session_name_prefix,
                user_metadata=user_metadata,
            )
            session_elapsed = time.time() - session_start_time
            logger.info(f"🔵 [FASTAPI] {trace_id} Session creation completed in {session_elapsed:.2f}s")

            session_id = session.get('session_id')
            logger.info(f"🔵 [FASTAPI] {trace_id} Created new session: {session_id}")
            logger.info(f"🔵 [FASTAPI] {trace_id} Session status: {session.get('status', 'unknown')}")

            # GUARD: Validate job_plan exists and is not empty
            job_plan = session.get('job_plan', [])
            logger.info(f"🔵 [FASTAPI] {trace_id} Job plan has {len(job_plan)} jobs")

            if not job_plan:
                error_msg = f"CRITICAL: Session {session_id} created without job_plan - cannot dispatch jobs"
                logger.error(f"🔵 [FASTAPI] {trace_id} ❌ {error_msg}")
                logger.error(f"   Session keys: {list(session.keys())}")
                logger.error(f"   This indicates create_sphere_session() failed to create job_plan")
                post_slack_alert(f"CRITICAL: Session created without job_plan: {session_id}")
                # Still return the session, but log loudly
            else:
                # Log job_plan details for debugging
                logger.info(f"🔵 [FASTAPI] {trace_id} Job plan validation:")
                for idx, job_desc in enumerate(job_plan):
                    job_type = job_desc.get('job_type', 'unknown')
                    job_id = job_desc.get('job_id', 'None')
                    logger.info(f"   [{idx}] {job_type} (job_id: {job_id})")

            logger.debug(f"Upload session details: {session}")

            serialized_session = serialize_session(session)

            # Add warning if sampling occurred
            if sampling_warning:
                serialized_session["warnings"] = [sampling_warning]

            # Dispatch first job in chain asynchronously AFTER returning response
            # This prevents the HTTP request from hanging while dispatching
            
            # CRITICAL: background_tasks MUST NOT be None for job dispatch to work
            # If it's None, something is wrong with the endpoint definition - CRASH LOUDLY
            if job_plan and not background_tasks:
                error_msg = f"CRITICAL BUG: background_tasks is None but job_plan exists with {len(job_plan)} jobs. Jobs will NEVER be dispatched. This is a coding error in the endpoint definition."
                logger.error(f"🔵 [FASTAPI] {trace_id} ❌ {error_msg}")
                post_slack_alert(f"CRITICAL: {error_msg} Session: {session_id}")
                # CRASH LOUDLY - do not fail silently
                raise RuntimeError(error_msg)
            
            if session_id and background_tasks:
                # GUARD: Only schedule background task if job_plan exists
                if not job_plan:
                    logger.error(f"🔵 [FASTAPI] {trace_id} ❌ Cannot schedule background dispatch - no job_plan in session")
                    logger.error(f"   Session will be created but no jobs will be dispatched automatically")
                    logger.error(f"   Manual intervention required to start jobs for session {session_id}")
                else:
                    async def dispatch_job_background():
                        """Run blocking dispatch in thread pool to avoid blocking event loop."""
                        bg_trace_id = f"BG-{uuid.uuid4().hex[:8]}"
                        bg_start_time = time.time()
                        try:
                            from lib.session_chains import dispatch_next_job_in_chain
                            logger.info(f"🔵 [FASTAPI-BG] {bg_trace_id} Starting background job dispatch for session {session_id}")
                            logger.info(f"🔵 [FASTAPI-BG] {bg_trace_id} Timestamp: {datetime.datetime.now().isoformat()}")
                            logger.info(f"🔵 [FASTAPI-BG] {bg_trace_id} Calling dispatch_next_job_in_chain...")

                            # Run blocking operation in thread pool to avoid blocking event loop
                            # Use aio (asyncio) which is imported at module level
                            try:
                                # Python 3.9+ has asyncio.to_thread
                                task_id = await aio.to_thread(dispatch_next_job_in_chain, session_id=session_id)
                            except AttributeError:
                                # Fallback for Python < 3.9: use ThreadPoolExecutor
                                from concurrent.futures import ThreadPoolExecutor
                                loop = aio.get_event_loop()
                                with ThreadPoolExecutor() as executor:
                                    task_id = await loop.run_in_executor(executor, dispatch_next_job_in_chain, session_id)
                            bg_elapsed = time.time() - bg_start_time

                            if task_id:
                                logger.info(f"🔵 [FASTAPI-BG] {bg_trace_id} ✅ First job dispatched - Task ID: {task_id}")
                                logger.info(f"🔵 [FASTAPI-BG] {bg_trace_id} Dispatch completed in {bg_elapsed:.3f} seconds")
                            else:
                                logger.warning(f"🔵 [FASTAPI-BG] {bg_trace_id} ⚠️  dispatch_next_job_in_chain returned None (no job dispatched)")
                                logger.warning(f"🔵 [FASTAPI-BG] {bg_trace_id} This may indicate:")
                                logger.warning(f"   - All jobs already have job_ids")
                                logger.warning(f"   - Session is already DONE")
                                logger.warning(f"   - job_plan is empty or invalid")
                                logger.warning(f"   - Dispatch failed silently")
                        except Exception as dispatch_err:
                            bg_elapsed = time.time() - bg_start_time
                            logger.error(f"🔵 [FASTAPI-BG] {bg_trace_id} ❌ Failed to dispatch first job for session {session_id}")
                            logger.error(f"   Error type: {type(dispatch_err).__name__}")
                            logger.error(f"   Error message: {str(dispatch_err)}")
                            logger.error(f"   Elapsed time before failure: {bg_elapsed:.3f} seconds")
                            logger.error(f"   Traceback: {traceback.format_exc()}")
                            # CRITICAL: Alert on background task failure
                            try:
                                post_slack_alert(f"CRITICAL: Background job dispatch failed for session {session_id}: {type(dispatch_err).__name__}: {str(dispatch_err)}")
                            except Exception as slack_err:
                                logger.error(f"   ❌ Failed to send Slack alert: {slack_err}")
                                logger.error(f"      Error type: {type(slack_err).__name__}")
                                logger.error(f"      Traceback: {traceback.format_exc()}")
                                # Don't fail the dispatch if Slack fails, but log it

                    # Schedule the dispatch to run after response is sent
                    background_tasks.add_task(dispatch_job_background)
                    logger.info(f"🔵 [FASTAPI] {trace_id} Background task scheduled for job dispatch")
            elif not session_id:
                logger.error(f"🔵 [FASTAPI] {trace_id} ❌ Cannot schedule background dispatch - no session_id")
            elif not background_tasks:
                logger.error(f"🔵 [FASTAPI] {trace_id} ❌ Cannot schedule background dispatch - background_tasks is None")
                logger.error(f"   This should not happen in FastAPI - background_tasks should always be available")

            # GUARD: Ensure we always return a response, even if serialization fails
            try:
                total_elapsed = time.time() - request_start_time
                logger.info(f"🔵 [FASTAPI] {trace_id} Returning HTTP 200 response with session data")
                logger.info(f"🔵 [FASTAPI] {trace_id} Total request time: {total_elapsed:.2f}s")
                logger.info(f"{'='*80}\n")
                return JSONResponse(serialized_session)
            except Exception as response_err:
                logger.error(f"🔵 [FASTAPI] {trace_id} ❌ CRITICAL: Failed to return response: {response_err}")
                logger.error(f"   Error type: {type(response_err).__name__}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                # Return minimal response to prevent client hang
                return JSONResponse({
                    "session_id": session_id,
                    "status": "ready",
                    "error": "Response serialization failed, but session was created",
                    "message": f"Session {session_id} created successfully"
                }, status_code=200)
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to create new session for uploaded file {new_file_name}: {error_type}: {error_msg}")
            traceback.print_exc()
            post_slack_alert(f"error with upload - failed to create new session: {error_type}: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to create new session: {error_type}: {error_msg}")

        # return {"message": "File uploaded successfully", "filename": file.filename}

    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...), request: Request = None, background_tasks: BackgroundTasks = None):
        """
        Upload endpoint that the frontend expects.
        This is an alias for upload_with_new_session for frontend compatibility.
        """
        # CRITICAL: Must pass background_tasks or jobs won't be dispatched!
        return await upload_with_new_session(file=file, request=request, background_tasks=background_tasks)

    @app.post("/upload_file")
    async def upload_file_only(file: UploadFile = File(...)) -> JSONResponse:
        """
        Upload a file without creating a session. Returns just the filename.
        Used by clients that need to upload files for training on foundation models.
        """
        try:
            from uuid import uuid4

            original_extension = Path(file.filename).suffix
            new_file_name = f"{str(uuid4())}{original_extension}"
            file_path = config.data_dir / new_file_name

            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            logger.info(f"File uploaded (no session): {file.filename} -> {new_file_name}")

            return JSONResponse({"filename": new_file_name, "original_filename": file.filename})
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to upload file {file.filename}: {error_type}: {error_msg}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Failed to upload file: {error_type}: {error_msg}"
            )

    def get_model_expiration_info(session: dict) -> Optional[Dict[str, Any]]:
        """
        Get model expiration information from session metadata.
        Returns None if model is not deprecated/expiring.

        Returns:
            dict with:
                - expiration_timestamp: ISO format timestamp when model expires
                - seconds_until_expiration: seconds from now until expiration
                - reason: reason for expiration (e.g., "model_deprecated", "new_model_expected")
        """

        # Check if session is deprecated
        if session.get("deprecated"):
            expiration_date_str = session.get("deprecation_expiration")
            if expiration_date_str:
                try:
                    expiration_dt = convert_from_iso(expiration_date_str)
                    now = datetime.datetime.now(tz=ZoneInfo("America/New_York"))
                    seconds_until = int((expiration_dt - now).total_seconds())

                    if seconds_until > 0:
                        return {
                            "expiration_timestamp": expiration_date_str,
                            "seconds_until_expiration": seconds_until,
                            "reason": "model_deprecated",
                            "warning_message": session.get("deprecation_warning", "This model has been deprecated"),
                        }
                    else:
                        # Already expired
                        return {
                            "expiration_timestamp": expiration_date_str,
                            "seconds_until_expiration": 0,
                            "reason": "model_expired",
                            "warning_message": session.get("deprecation_warning", "This model has expired"),
                        }
                except Exception as e:
                    logger.warning(f"Failed to parse expiration date: {e}")
                    return None

        # Could add other expiration reasons here (e.g., "new_model_expected" based on training status)
        # For now, only return info if deprecated

        return None

    @app.post("/session/{id}/predict")
    async def predict_with_single_predictor(id: str, request: Request) -> JSONResponse:
        """Make predictions using a trained single predictor."""


        try:
            request_data = await request.json()
            logger.info(
                f"🔍 PREDICT REQUEST - Raw request data keys: {list(request_data.keys()) if isinstance(request_data, dict) else type(request_data)}"
            )
        except Exception as json_error:
            logger.error(f"❌ PREDICT REQUEST - Failed to parse JSON for session {id}: {json_error}")
            logger.error(f"❌ PREDICT REQUEST - Request body: {await request.body()}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid JSON in request body: {str(json_error)}"
            )

        # Find predictor and call prediction server
        from lib.model_card_repair import find_predictor_pickle
        from prediction_client import predict_batch
        
        predictor_path = find_predictor_pickle(id)
        if not predictor_path:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"No predictor found for session {id}"
            )
        
        # Extract query record from request
        if "query_record" in request_data:
            query_record = request_data["query_record"]
            if isinstance(query_record, list) and len(query_record) == 1:
                query_record = query_record[0]
        else:
            query_record = request_data
        
        logger.info(f"🔍 PREDICT - Session {id}, predictor: {predictor_path}")
        
        # Call prediction server
        result = predict_batch(str(predictor_path), [query_record])
        
        if not result.get('success'):
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Prediction failed')
            )
        
        # Build response
        predictions = result.get('predictions', [])
        prediction = predictions[0] if predictions else {}
        
        # New format: prediction already contains prediction/confidence/probabilities/threshold
        # Fallback for old format where prediction was just the probs dict
        if 'prediction' in prediction:
            # New format from single_predictor
            response_data = {
                "prediction": prediction.get('prediction'),
                "confidence": prediction.get('confidence'),
                "probabilities": prediction.get('probabilities', prediction.get('results', {})),
                "target_column": result.get('target_col_name'),
                "target_column_type": result.get('target_col_type'),
                "predictor_path": str(predictor_path),
                "cache_stats": result.get('cache_stats'),
            }
            if prediction.get('threshold') is not None:
                response_data["threshold"] = prediction.get('threshold')
        else:
            # Old format fallback - extract prediction from probabilities
            results = prediction.get("results", prediction)
            predicted_label = None
            confidence = None
            if isinstance(results, dict) and results:
                prob_items = [(k, v) for k, v in results.items() 
                             if isinstance(v, (int, float)) and k not in ('calibration', '_meta')]
                if prob_items:
                    predicted_label, confidence = max(prob_items, key=lambda x: x[1])
            
            response_data = {
                "prediction": predicted_label,
                "confidence": confidence,
                "probabilities": results,
                "target_column": result.get('target_col_name'),
                "target_column_type": result.get('target_col_type'),
                "predictor_path": str(predictor_path),
                "cache_stats": result.get('cache_stats'),
            }
        
        return JSONResponse(replace_nans_with_nulls(response_data))

    @app.post("/session/{id}/explain")
    async def explain_prediction(id: str, request: Request) -> JSONResponse:
        """Explain a prediction using gradient attribution."""
        fix_paths()
        
        try:
            request_data = await request.json()
        except Exception as json_error:
            logger.error(f"❌ EXPLAIN REQUEST - Failed to parse JSON for session {id}: {json_error}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid JSON in request body: {str(json_error)}"
            )
        
        # Extract query record(s) from request
        if "query_record" in request_data:
            query_record = request_data["query_record"]
        else:
            query_record = request_data
        
        # Support record_b for comparison
        query_record_b = request_data.get("query_record_b")
        
        class_idx = request_data.get("class_idx")  # Optional: target class for attribution
        target_column = request_data.get("target_column")
        predictor_id = request_data.get("predictor_id")
        
        logger.info(f"🔍 EXPLAIN - Session {id}")
        
        # Use Celery task to load model and compute explanation
        try:
            from celery_app import explain_prediction as celery_explain
            
            explain_options = {}
            if class_idx is not None:
                explain_options['class_idx'] = class_idx
            if target_column:
                explain_options['target_column'] = target_column
            if predictor_id:
                explain_options['predictor_id'] = predictor_id
            if query_record_b is not None:
                explain_options['record_b'] = query_record_b
            
            # Submit to Celery
            task = celery_explain.delay(id, query_record, explain_options)
            
            # Wait for result (synchronous for now, could be async with polling)
            result = task.get(timeout=300)  # 5 minute timeout
            
            if not result.get('success'):
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=result.get('error', 'Explanation failed')
                )
            
            # Build response - handle different result types
            if 'explanations' in result:
                # List of explanations
                response_data = {
                    "explanations": result.get('explanations', [])
                }
            elif 'difference' in result:
                # Two-record comparison
                response_data = {
                    "record_a": result.get('record_a', {}),
                    "record_b": result.get('record_b', {}),
                    "difference": result.get('difference', {}),
                    "heatmap": result.get('heatmap', {}),  # Heatmap data for visualization
                }
            else:
                # Single record
                response_data = {
                    "feature_scores": result.get('feature_scores', {}),
                    "pair_scores": result.get('pair_scores', {}),
                    "target_class_idx": result.get('target_class_idx'),
                    "logit": result.get('logit'),
                }
            
            return JSONResponse(replace_nans_with_nulls(response_data))
            
        except Exception as e:
            logger.error(f"❌ EXPLAIN - Failed: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Failed to explain prediction: {str(e)}"
            )

    @app.post("/session/{id}/predict_table")
    async def predict_table_with_single_predictor(id: str, request: Request) -> JSONResponse:
        """Make batch predictions using JSON Tables format."""
        fix_paths()

        # Initialize variables for logging
        request_data = None
        session = None

        try:
            logger.info(f"🔍 PREDICT_TABLE REQUEST - Starting batch prediction for session {id}")

            session = load_session(id)

            # Handle both old single predictor format and new multiple predictors format
            single_predictors = session.get("single_predictors")
            single_predictor = session.get("single_predictor")

            # Log session info for debugging
            logger.info(
                f"🔍 PREDICT_TABLE REQUEST - Session {id}: single_predictors={bool(single_predictors)}, single_predictor={bool(single_predictor)}"
            )

            # Helper function to generate predictor ID
            def generate_predictor_id(predictor_path: str) -> str:
                import hashlib
                import os

                filename = os.path.basename(predictor_path) if predictor_path else "unknown"
                # Remove .pickle extension from user-facing ID
                if filename.endswith(".pickle"):
                    filename = filename[:-7]
                path_hash = hashlib.md5(predictor_path.encode("utf-8")).hexdigest()[:8]
                return f"{filename}_{path_hash}"

            # NEW: Parse request to get target_column or predictor_id if specified
            # NOTE: Request body can only be read once! Save it for later use
            requested_target_column = None
            requested_predictor_id = None
            predictor_index = 0

            try:
                request_body = await request.body()
                request_json = json.loads(request_body) if request_body else {}

                # Only try to extract these fields if request is a dict (not a list of records)
                if isinstance(request_json, dict):
                    requested_target_column = request_json.get("target_column")
                    requested_predictor_id = request_json.get("predictor_id")
                    best_metric_preference = request_json.get("best_metric_preference")  # "roc_auc", "pr_auc", or None
                    predictor_index = request_json.get("predictor_index", 0)

                logger.info(
                    f"🔍 PREDICT_TABLE REQUEST - target_column='{requested_target_column}', predictor_id='{requested_predictor_id}', best_metric_preference='{best_metric_preference}', predictor_index={predictor_index}"
                )
            except Exception as parse_error:
                logger.warning(
                    f"⚠️  PREDICT_TABLE REQUEST - Could not parse request body for target_column/predictor_id: {parse_error}"
                )
                request_json = {}
                requested_target_column = None
                requested_predictor_id = None
                best_metric_preference = None
                predictor_index = 0

            predictor_path = None

            if single_predictors and isinstance(single_predictors, list):
                # New format: multiple predictors
                logger.info(f"🔍 PREDICT_TABLE REQUEST - Multiple predictors available: {len(single_predictors)}")

                # NEW: If multiple predictors exist, REQUIRE target_column or predictor_id
                if len(single_predictors) > 1 and not requested_predictor_id and not requested_target_column:
                    # Get available targets for error message
                    available_targets = []
                    available_ids = []
                    for pred_path in single_predictors:
                        # Skip None or empty paths
                        if not pred_path:
                            continue

                        # Get predictor_id
                        if Path(pred_path).exists():
                            available_ids.append(generate_predictor_id(pred_path))

                        # Get target_column from metadata
                        metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                        if Path(metadata_path).exists():
                            try:
                                with open(metadata_path) as f:
                                    metadata = json.load(f)
                                    target_col = metadata.get("target_column")
                                    if target_col:
                                        available_targets.append(target_col)
                            except Exception:
                                pass

                    error_msg = f"Multiple predictors found ({len(single_predictors)}) - you must specify 'target_column' or 'predictor_id' in request. Available targets: {available_targets}, Available IDs: {available_ids}"
                    logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)

                # PRIORITY 1: predictor_id (most precise)
                if requested_predictor_id:
                    logger.info(
                        f"🔍 PREDICT_TABLE REQUEST - Looking for predictor with predictor_id='{requested_predictor_id}'"
                    )
                    predictor_found = False
                    available_predictor_ids = []

                    for pred_path in single_predictors:
                        # Skip None or empty paths
                        if not pred_path:
                            continue

                        if Path(pred_path).exists():
                            current_predictor_id = generate_predictor_id(pred_path)
                            available_predictor_ids.append(current_predictor_id)

                            if current_predictor_id == requested_predictor_id:
                                predictor_path = pred_path
                                predictor_found = True
                                logger.info(f"✅ PREDICT_TABLE REQUEST - Found matching predictor by ID: {pred_path}")
                                break

                    if not predictor_found:
                        error_msg = f"No predictor found for predictor_id '{requested_predictor_id}'. Available IDs: {available_predictor_ids}"
                        logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                        logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} predictors: {single_predictors}")
                        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)

                # PRIORITY 2: target_column (semantic match)
                elif requested_target_column:
                    logger.info(
                        f"🔍 PREDICT_TABLE REQUEST - Looking for predictor with target_column='{requested_target_column}'"
                    )
                    predictor_found = False

                    for pred_path in single_predictors:
                        # Skip None or empty paths
                        if not pred_path:
                            logger.warning(
                                "⚠️  PREDICT_TABLE REQUEST - Skipping None/empty predictor path in single_predictors"
                            )
                            continue

                        # Load predictor metadata to check target_column
                        metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                        if Path(metadata_path).exists():
                            try:
                                with open(metadata_path) as f:
                                    metadata = json.load(f)
                                    target_col = metadata.get("target_column")

                                    logger.info(
                                        f"🔍 PREDICT_TABLE REQUEST - Checking predictor {pred_path}: target_column='{target_col}'"
                                    )

                                    if target_col == requested_target_column:
                                        predictor_path = pred_path
                                        predictor_found = True
                                        logger.info(f"✅ PREDICT_TABLE REQUEST - Found matching predictor: {pred_path}")
                                        break
                            except Exception as metadata_error:
                                logger.warning(
                                    f"⚠️  PREDICT_TABLE REQUEST - Could not read metadata for {pred_path}: {metadata_error}"
                                )
                                continue

                    if not predictor_found:
                        error_msg = f"No predictor found for target column '{requested_target_column}'"
                        logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                        logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} predictors: {single_predictors}")
                        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)

                # PRIORITY 3: predictor_index (backwards compatibility - only for single predictor)
                else:
                    # Only allow index fallback if there's exactly one predictor
                    if len(single_predictors) == 1:
                        predictor_path = single_predictors[0]
                        logger.info(
                            f"🔍 PREDICT_TABLE REQUEST - Single predictor session, using predictor: {predictor_path}"
                        )
                    elif 0 <= predictor_index < len(single_predictors):
                        # This branch should never be reached due to check above, but keep for safety
                        predictor_path = single_predictors[predictor_index]
                        logger.warning(
                            f"⚠️  PREDICT_TABLE REQUEST - Using predictor index {predictor_index} as fallback: {predictor_path}"
                        )
                    else:
                        error_msg = f"Predictor index {predictor_index} out of range. Available predictors: 0-{len(single_predictors)-1}"
                        logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                        logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} predictors: {single_predictors}")
                        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)
            elif single_predictor:
                # Old format: single predictor
                logger.info(f"🔍 PREDICT_TABLE REQUEST - Single predictor format: {single_predictor}")
                predictor_path = single_predictor
            else:
                error_msg = "No single predictors found"
                logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} details: {session}")
                post_slack_alert(f"session={id}; no single predictors found for table prediction")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

            # Resolve predictor path, checking published location first
            original_predictor_path = predictor_path
            predictor_path = resolve_session_path(id, predictor_path)

            if not predictor_path or not Path(predictor_path).exists():
                error_msg = f"Single predictor not found at: {predictor_path} (original: {original_predictor_path})"
                logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} predictor_path: {predictor_path}")
                post_slack_alert(f"session={id}; single predictor not found for table prediction")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

            # Check if user wants to use a specific metric checkpoint (ROC-AUC or PR-AUC best)
            if best_metric_preference:
                predictor_dir = Path(predictor_path).parent
                if predictor_dir.exists():
                    # Look for best checkpoint files
                    if best_metric_preference.lower() in ['roc_auc', 'roc-auc', 'auc']:
                        # Look for ROC-AUC best checkpoint
                        roc_auc_checkpoints = sorted(
                            predictor_dir.glob("best_single_predictor_roc_auc*.pickle"),
                            key=lambda p: p.stat().st_mtime,
                            reverse=True
                        )
                        if roc_auc_checkpoints:
                            predictor_path = str(roc_auc_checkpoints[0])
                            logger.info(f"🎯 PREDICT_TABLE - Using ROC-AUC best checkpoint: {predictor_path}")
                        else:
                            logger.warning(f"⚠️  PREDICT_TABLE - ROC-AUC best checkpoint requested but not found, using default: {predictor_path}")
                    elif best_metric_preference.lower() in ['pr_auc', 'pr-auc', 'precision_recall']:
                        # Look for PR-AUC best checkpoint
                        pr_auc_checkpoints = sorted(
                            predictor_dir.glob("best_single_predictor_pr_auc*.pickle"),
                            key=lambda p: p.stat().st_mtime,
                            reverse=True
                        )
                        if pr_auc_checkpoints:
                            predictor_path = str(pr_auc_checkpoints[0])
                            logger.info(f"🎯 PREDICT_TABLE - Using PR-AUC best checkpoint: {predictor_path}")
                        else:
                            logger.warning(f"⚠️  PREDICT_TABLE - PR-AUC best checkpoint requested but not found, using default: {predictor_path}")
                    else:
                        logger.warning(f"⚠️  PREDICT_TABLE - Unknown best_metric_preference='{best_metric_preference}', using default checkpoint")

            try:
                # NOTE: Use request_json that was already parsed above (can't read body twice!)
                request_data = request_json
                logger.info(f"🔍 PREDICT_TABLE REQUEST - Request data type: {type(request_data)}")
                if isinstance(request_data, dict):
                    logger.info(f"🔍 PREDICT_TABLE REQUEST - Request keys: {list(request_data.keys())}")
                elif isinstance(request_data, list):
                    logger.info(f"🔍 PREDICT_TABLE REQUEST - Request list length: {len(request_data)}")

                # Handle different input formats
                if is_json_table(request_data):
                    # Direct JSON Tables format
                    input_table = request_data
                    logger.info("🔍 PREDICT_TABLE REQUEST - Direct JSON Tables format")
                elif "table" in request_data and is_json_table(request_data["table"]):
                    # Wrapped in a "table" field
                    input_table = request_data["table"]
                    logger.info("🔍 PREDICT_TABLE REQUEST - Wrapped JSON Tables format")
                elif "records" in request_data and isinstance(request_data["records"], list):
                    # List of records - convert to JSON Tables
                    logger.info(
                        f"🔍 PREDICT_TABLE REQUEST - Records list format with {len(request_data['records'])} records"
                    )
                    input_table = JSONTablesEncoder.from_records(request_data["records"])
                elif detect_table_in_json(request_data):
                    logger.info("🔍 PREDICT_TABLE REQUEST - Auto-detected table format")
                    # Auto-detect table from list of objects
                    input_table = JSONTablesEncoder.from_records(request_data)
                else:
                    error_msg = (
                        "Input must be JSON Tables format, list of records, or include 'table' or 'records' field"
                    )
                    logger.error(f"❌ PREDICT_TABLE REQUEST - {error_msg}")
                    logger.error(f"❌ PREDICT_TABLE REQUEST - Session {id} request data structure:")
                    logger.error(f"  - Type: {type(request_data)}")
                    if isinstance(request_data, dict):
                        logger.error(f"  - Keys: {list(request_data.keys())}")
                        for key, value in request_data.items():
                            logger.error(f"  - {key}: {type(value)}")
                    elif isinstance(request_data, list):
                        logger.error(f"  - List length: {len(request_data)}")
                        if request_data:
                            logger.error(f"  - First item type: {type(request_data[0])}")
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)

                # Convert JSON Tables to records for prediction
                records = JSONTablesDecoder.to_records(input_table)
                if not records:
                    logger.error("❌ PREDICT_TABLE REQUEST - No records found after conversion")
                    logger.error(f"❌ PREDICT_TABLE REQUEST - Input table: {input_table}")
                    return JSONResponse(
                        {
                            "input_table": input_table,
                            "predictions": [],
                            "results_table": JSONTablesEncoder.from_records([]),
                            "error": "Invalid format of records request, please check your input.",
                            "summary": {
                                "total_records": 0,
                                "successful_predictions": 0,
                                "failed_predictions": 0,
                                "errors": [],
                            },
                        }
                    )

                logger.info(f"🔍 PREDICT_TABLE REQUEST - Successfully converted to {len(records)} records")

                # Determine prediction strategy based on dataset size
                CELERY_THRESHOLD = 1000  # Use Celery for datasets larger than this

                if len(records) >= CELERY_THRESHOLD:
                    # Large dataset: Use Celery for async processing
                    logger.info(
                        f"🚀 Large dataset detected ({len(records)} records) - using Celery async processing..."
                    )
                    logger.info("💡 Pickle import fixes applied - async should work now")

                    try:
                        from celery_app import predict_batch as celery_predict_batch

                        # NEW: Pass target_column or predictor_id to Celery so it can find the correct predictor
                        prediction_options = {
                            "batch_size": 256,
                            "target_column": requested_target_column,  # NEW: Pass target_column
                            "predictor_id": requested_predictor_id,  # NEW: Pass predictor_id
                        }

                        # Submit the job to Celery
                        task = celery_predict_batch.delay(id, records, prediction_options)

                        # Get model expiration info
                        model_expiration = get_model_expiration_info(session)

                        # Return job ID for polling
                        # Note: target_column will be in the final result when job completes
                        return JSONResponse(
                            {
                                "job_id": task.id,
                                "status": "submitted",
                                "message": f"Large prediction job submitted ({len(records)} records)",
                                "total_records": len(records),
                                "polling_url": f"/session/{id}/prediction_job/{task.id}",
                                "target_column": requested_target_column,  # Pass through requested target
                                "model_expiration": model_expiration,
                                "async": True,
                            }
                        )

                    except ImportError:
                        logger.warning("Celery not available, falling back to synchronous processing")
                        # Fall through to synchronous processing
                    except Exception as e:
                        logger.error(f"Error submitting Celery job: {e}")
                        # Fall through to synchronous processing

                # Use prediction server for ALL predictions (keeps models in GPU memory)
                logger.info(f"🚀 Calling prediction server for {len(records)} records...")
                
                # Check if prediction server is available
                if not is_prediction_server_available():
                    logger.error("❌ Prediction server not available")
                    raise HTTPException(
                        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        detail="Prediction server not available. Please try again later."
                    )
                
                # Call prediction server
                server_result = prediction_server_predict(
                    predictor_path=predictor_path,
                    records=records,
                    batch_size=2500
                )
                
                if not server_result.get('success'):
                    error_msg = server_result.get('error', 'Unknown prediction server error')
                    logger.error(f"❌ Prediction server error: {error_msg}")
                    raise HTTPException(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        detail=f"Prediction failed: {error_msg}"
                    )
                
                # Extract results from prediction server response
                batch_predictions = server_result.get('predictions', [])
                target_col_name = server_result.get('target_col_name')
                target_col_type = server_result.get('target_col_type')
                model_quality_metrics = server_result.get('model_quality_metrics')
                
                logger.info(f"✅ Prediction server returned {len(batch_predictions)} predictions")
                
                # Process predictions into our response format
                predictions = []
                successful_predictions = 0
                failed_predictions = 0
                errors = []
                
                for i, prediction_result in enumerate(batch_predictions):
                    # Handle extended result format
                    if isinstance(prediction_result, dict) and "results" in prediction_result:
                        prediction = prediction_result["results"]
                        guardrails = prediction_result.get("guardrails", {})
                        metadata = {
                            "original_query": prediction_result.get("original_query", {}),
                            "actual_query": prediction_result.get("actual_query", {}),
                            "available_query_columns": prediction_result.get("available_query_columns", []),
                            "ignored_query_columns": prediction_result.get("ignored_query_columns", []),
                            "guardrails": guardrails,
                        }
                    else:
                        prediction = prediction_result
                        metadata = {}
                    
                    predictions.append({
                        "row_index": i,
                        "prediction_id": None,
                        "prediction": prediction,
                        "metadata": metadata,
                        "error": None,
                    })
                    successful_predictions += 1
                
                # Convert results back to JSON Tables format
                results_records = []
                for i, (original_record, pred_result) in enumerate(zip(records, predictions)):
                    result_record = original_record.copy()

                    if pred_result["prediction"] is not None:
                        result_record["prediction_id"] = pred_result["prediction_id"]

                        if isinstance(pred_result["prediction"], dict):
                            # Classification - add probability columns
                            for class_name, prob in pred_result["prediction"].items():
                                result_record[f"pred_{class_name}"] = prob
                            predicted_class = max(pred_result["prediction"], key=pred_result["prediction"].get)
                            result_record["predicted_class"] = predicted_class
                        else:
                            result_record["prediction"] = pred_result["prediction"]
                    else:
                        result_record["prediction_error"] = pred_result["error"]

                    results_records.append(result_record)

                results_table = JSONTablesEncoder.from_records(results_records)

                logger.info(
                    f"🔍 PREDICT_TABLE REQUEST - Success! Processed {successful_predictions}/{len(records)} records"
                )

                # Get model expiration info
                model_expiration = get_model_expiration_info(session)

                # Build response using metadata from prediction server
                response_data = {
                    "input_table": input_table,
                    "predictions": predictions,
                    "results_table": results_table,
                    "target_column": target_col_name,
                    "target_column_type": target_col_type,
                    "model_quality_metrics": model_quality_metrics,
                    "model_expiration": model_expiration,
                    "summary": {
                        "total_records": len(records),
                        "successful_predictions": successful_predictions,
                        "failed_predictions": failed_predictions,
                        "errors": errors[:10] if errors else [],
                    },
                }

                # Apply NaN cleaning to prevent JSON encoding errors
                cleaned_response_data = replace_nans_with_nulls(response_data)

                return JSONResponse(cleaned_response_data)

            except Exception as e:
                logger.error(f"❌ PREDICT_TABLE REQUEST - Error during prediction processing for session {id}: {e}")
                logger.error(f"❌ PREDICT_TABLE REQUEST - Request data: {request_data}")
                logger.error(f"❌ PREDICT_TABLE REQUEST - Predictor path: {predictor_path}")
                logger.exception(e)
                traceback.print_exc()
                post_slack_alert(f"session={id}; error with table prediction")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error making table predictions: {str(e)}"
                )

        except HTTPException:
            # Re-raise HTTP exceptions (already logged above)
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"❌ PREDICT_TABLE REQUEST - Unexpected error for session {id}: {e}")
            logger.error(f"❌ PREDICT_TABLE REQUEST - Request data: {request_data}")
            logger.error(f"❌ PREDICT_TABLE REQUEST - Session data: {session}")
            logger.exception(e)
            traceback.print_exc()
            post_slack_alert(f"session={id}; unexpected error in predict_table endpoint")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Unexpected error processing batch prediction request",
            )

    @app.post("/session/{id}/test_model")
    async def test_model(id: str, request: Request) -> JSONResponse:
        """
        Load and test a model (predictor) from a session.
        Similar to load_and_test_model.py CLI tool functionality.
        
        Request body (optional):
        {
            "test_record": {"col1": "value1", "col2": 123},  # Optional: test record for encoding/prediction
            "target_column": "target_col",  # Optional: specific target column predictor
            "predictor_id": "predictor_id",  # Optional: specific predictor ID
            "cpu_only": false  # Optional: force CPU-only mode
        }
        """
        fix_paths()
        
        try:
            logger.info(f"🔍 TEST_MODEL REQUEST - Starting model test for session {id}")
            
            # Load session
            try:
                session = load_session(id)
            except FileNotFoundError:
                logger.warning(f"❌ TEST_MODEL REQUEST - Session {id} not found")
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Session {id} not found or no longer exists"
                )
            except ValueError as ve:
                logger.error(f"❌ TEST_MODEL REQUEST - Session {id} file is corrupted: {ve}")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Session {id} file is corrupted and cannot be loaded",
                )
            
            # Parse request body
            try:
                request_data = await request.json()
            except Exception as json_error:
                logger.error(f"❌ TEST_MODEL REQUEST - Failed to parse JSON: {json_error}")
                request_data = {}
            
            test_record = request_data.get("test_record")
            requested_target_column = request_data.get("target_column")
            requested_predictor_id = request_data.get("predictor_id")
            cpu_only = request_data.get("cpu_only", False)
            
            # Helper function to generate predictor ID
            def generate_predictor_id(predictor_path: str) -> str:
                import hashlib
                import os
                filename = os.path.basename(predictor_path) if predictor_path else "unknown"
                if filename.endswith(".pickle"):
                    filename = filename[:-7]
                path_hash = hashlib.md5(predictor_path.encode("utf-8")).hexdigest()[:8]
                return f"{filename}_{path_hash}"
            
            # Find predictor path (similar logic to predict endpoint)
            single_predictors = session.get("single_predictors")
            single_predictor = session.get("single_predictor")
            
            predictor_path = None
            
            if single_predictors and isinstance(single_predictors, list):
                # Multiple predictors - need target_column or predictor_id
                if len(single_predictors) > 1 and not requested_predictor_id and not requested_target_column:
                    available_targets = []
                    available_ids = []
                    for pred_path in single_predictors:
                        if pred_path and Path(pred_path).exists():
                            available_ids.append(generate_predictor_id(pred_path))
                            metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                            if Path(metadata_path).exists():
                                try:
                                    with open(metadata_path) as f:
                                        metadata = json.load(f)
                                        target_col = metadata.get("target_column")
                                        if target_col:
                                            available_targets.append(target_col)
                                except Exception:
                                    pass
                    
                    error_msg = f"Multiple predictors found ({len(single_predictors)}) - you must specify 'target_column' or 'predictor_id' in request. Available targets: {available_targets}, Available IDs: {available_ids}"
                    logger.error(f"❌ TEST_MODEL REQUEST - {error_msg}")
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_msg)
                
                # Find by predictor_id
                if requested_predictor_id:
                    predictor_found = False
                    for pred_path in single_predictors:
                        if pred_path and Path(pred_path).exists():
                            if generate_predictor_id(pred_path) == requested_predictor_id:
                                predictor_path = pred_path
                                predictor_found = True
                                break
                    if not predictor_found:
                        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"No predictor found for predictor_id '{requested_predictor_id}'")
                
                # Find by target_column
                elif requested_target_column:
                    predictor_found = False
                    for pred_path in single_predictors:
                        if pred_path and Path(pred_path).exists():
                            metadata_path = str(Path(pred_path).parent / "model_metadata.json")
                            if Path(metadata_path).exists():
                                try:
                                    with open(metadata_path) as f:
                                        metadata = json.load(f)
                                        if metadata.get("target_column") == requested_target_column:
                                            predictor_path = pred_path
                                            predictor_found = True
                                            break
                                except Exception:
                                    continue
                    if not predictor_found:
                        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"No predictor found for target column '{requested_target_column}'")
                
                # Single predictor fallback
                else:
                    predictor_path = single_predictors[0] if single_predictors else None
                    
            elif single_predictor:
                predictor_path = single_predictor
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No single predictors found in session")
            
            # Resolve predictor path
            original_predictor_path = predictor_path
            predictor_path = resolve_session_path(id, predictor_path)
            
            if not predictor_path or not Path(predictor_path).exists():
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Predictor not found at: {predictor_path}")
            
            # Set CPU-only mode if requested
            if cpu_only:
                import os
                os.environ['CUDA_VISIBLE_DEVICES'] = ''
                os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
            
            # Load predictor (use cache if available)
            fsp = predictor_cache.get(predictor_path)
            
            if fsp is None:
                logger.info(f"📦 Loading predictor from: {predictor_path}")
                with open(predictor_path, "rb") as f:
                    fsp = pickle.load(f)
                
                # Hydrate to GPU if available and not CPU-only
                import torch
                if torch.cuda.is_available() and not cpu_only:
                    logger.info("🔄 Hydrating to GPU...")
                    fsp.hydrate_to_gpu_if_needed()
                    if hasattr(fsp, 'embedding_space') and fsp.embedding_space is not None:
                        fsp.embedding_space.hydrate_to_gpu_if_needed()
                
                # Cache the predictor
                predictor_cache.put(predictor_path, fsp)
            else:
                logger.info(f"✅ Using cached predictor: {predictor_path}")
            
            # Build response with model info
            response_data = {
                "success": True,
                "session_id": id,
                "predictor_path": str(predictor_path),
                "predictor_id": generate_predictor_id(str(predictor_path)),
                "target_column": getattr(fsp, 'target_col_name', 'Unknown'),
                "target_type": getattr(fsp, 'target_col_type', 'Unknown'),
            }
            
            # Get embedding space info
            es = None
            if hasattr(fsp, 'embedding_space') and fsp.embedding_space is not None:
                es = fsp.embedding_space
                response_data["embedding_space"] = {
                    "d_model": es.d_model,
                    "columns": list(es.col_codecs.keys()) if hasattr(es, 'col_codecs') else [],
                    "num_codecs": len(es.col_codecs) if hasattr(es, 'col_codecs') else 0,
                }
            
            # Check device
            import torch
            if hasattr(fsp, 'predictor') and fsp.predictor is not None:
                device = next(fsp.predictor.parameters()).device if list(fsp.predictor.parameters()) else 'cpu'
                response_data["device"] = str(device)
            
            # Test encoding if test_record provided
            if test_record and es is not None:
                try:
                    encoding = es.encode_record(test_record, squeeze=False, short=False)
                    response_data["encoding_test"] = {
                        "success": True,
                        "shape": list(encoding.shape),
                        "dtype": str(encoding.dtype),
                        "device": str(encoding.device),
                        "stats": {
                            "min": float(encoding.min().item()),
                            "max": float(encoding.max().item()),
                            "mean": float(encoding.mean().item()),
                        }
                    }
                except Exception as e:
                    response_data["encoding_test"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Test prediction if test_record provided
            if test_record and fsp is not None:
                try:
                    prediction_result = fsp.predict(test_record, debug_print=False, extended_result=True)
                    
                    if isinstance(prediction_result, dict):
                        results = prediction_result.get('results', {})
                        prediction_data = {
                            "success": True,
                            "results": results,
                        }
                        
                        if isinstance(results, dict) and results:
                            predicted_class = max(results, key=results.get)
                            prediction_data["predicted_class"] = predicted_class
                            prediction_data["confidence"] = float(results[predicted_class])
                        
                        # Add guardrails if present
                        if 'guardrails' in prediction_result:
                            prediction_data["guardrails"] = prediction_result['guardrails']
                        
                        # Add query metadata if present
                        if 'original_query' in prediction_result:
                            prediction_data["original_query"] = prediction_result['original_query']
                        if 'actual_query' in prediction_result:
                            prediction_data["actual_query"] = prediction_result['actual_query']
                        if 'available_query_columns' in prediction_result:
                            prediction_data["available_query_columns"] = prediction_result['available_query_columns']
                        if 'ignored_query_columns' in prediction_result:
                            prediction_data["ignored_query_columns"] = prediction_result['ignored_query_columns']
                        
                        response_data["prediction_test"] = prediction_data
                    else:
                        response_data["prediction_test"] = {
                            "success": True,
                            "result": prediction_result
                        }
                except Exception as e:
                    response_data["prediction_test"] = {
                        "success": False,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
            
            logger.info(f"✅ TEST_MODEL REQUEST - Successfully tested model for session {id}")
            return JSONResponse(response_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ TEST_MODEL REQUEST - Error testing model for session {id}: {e}")
            logger.exception(e)
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error testing model: {str(e)}"
            )

    @app.get("/session/{id}/columns")
    async def get_embedding_space_columns(id: str) -> JSONResponse:
        """Get column names from the embedding space.
        
        If embedding space is still training, falls back to schema_metadata.json
        from create_structured_data job output.
        """
        try:
            session = load_session(id)

            # Try to get columns from trained embedding space first
            embedding_space_path = session.get("embedding_space")
            resolved_es_path = resolve_embedding_space_path(embedding_space_path) if embedding_space_path else None
            
            if resolved_es_path and resolved_es_path.exists():
                try:
                    embedding_space_path = str(resolved_es_path)
                    # Load embedding space from cache or file
                    es_path_str = str(embedding_space_path)
                    es = embedding_space_cache.get(es_path_str)

                    if es is None:
                        lib_path = Path(__file__).parent / "lib"
                        if str(lib_path.resolve()) not in sys.path:
                            sys.path.insert(0, str(lib_path.resolve()))

                        from featrix.neural.io_utils import load_embedded_space
                            
                        es = load_embedded_space(embedding_space_path)
                        embedding_space_cache.put(es_path_str, es)

                    # Get column names
                    column_names = es.get_column_names()

                    # Get column types if available
                    column_types = {}
                    if hasattr(es, "col_codecs"):
                        for col_name in column_names:
                            codec = es.col_codecs.get(col_name)
                            if codec:
                                column_types[col_name] = es.get_codec_type_for_column(col_name)

                    return JSONResponse(
                        {"column_names": column_names, "column_types": column_types, "num_columns": len(column_names)}
                    )
                except Exception as es_error:
                    logger.debug(f"Could not load embedding space (may still be training): {es_error}")
                    # Fall through to fallback methods
            
            # Fallback: Try to get columns from create_structured_data schema_metadata.json
            # This works even when ES is still training
            session_output_dir = config.output_dir / id
            create_sd_dir = session_output_dir / "create_structured_data"
            
            if create_sd_dir.exists():
                # Find most recent create_structured_data job
                sd_jobs = sorted([d for d in create_sd_dir.iterdir() if d.is_dir()], 
                               key=lambda x: x.stat().st_mtime, reverse=True)
                for sd_job in sd_jobs[:1]:  # Just check most recent
                    schema_file = sd_job / "schema_metadata.json"
                    if schema_file.exists():
                        try:
                            with open(schema_file, 'r') as f:
                                schema = json.load(f)
                                columns = schema.get('columns', {})
                                if columns:
                                    column_names = list(columns.keys())
                                    column_types = {}
                                    for col_name, col_info in columns.items():
                                        if isinstance(col_info, dict):
                                            # Map schema types to ES types
                                            col_type = col_info.get('type', 'unknown')
                                            if col_type in ['int64', 'float64']:
                                                column_types[col_name] = 'scalar'
                                            elif col_type == 'object' or col_info.get('is_categorical', False):
                                                column_types[col_name] = 'set'
                                            else:
                                                column_types[col_name] = 'free_string'
                                    
                                    logger.info(f"✅ Got columns from schema_metadata.json for session {id} (ES still training)")
                                    return JSONResponse(
                                        {"column_names": column_names, "column_types": column_types, "num_columns": len(column_names)}
                                    )
                        except Exception as schema_error:
                            logger.debug(f"Could not read schema_metadata.json: {schema_error}")
            
            # If we get here, no columns found
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, 
                detail="Embedding space not found and no schema metadata available. Session may still be initializing."
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting embedding space columns: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    @app.get("/session/{id}/predictor_schema")
    async def get_predictor_schema(id: str, predictor_index: int = 0) -> JSONResponse:
        """Get predictor schema/metadata for validating input data."""
        try:
            session = load_session(id)

            # Get predictor path
            single_predictors = session.get("single_predictors")
            single_predictor = session.get("single_predictor")

            predictor_path = None
            if single_predictors and isinstance(single_predictors, list):
                if predictor_index < len(single_predictors):
                    predictor_path = single_predictors[predictor_index]
            elif single_predictor:
                predictor_path = single_predictor

            if not predictor_path:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No predictor found")

            # Load predictor
            fsp = predictor_cache.get(predictor_path)
            if fsp is None:
                import sys

                lib_path = Path(__file__).parent / "lib"
                if str(lib_path.resolve()) not in sys.path:
                    sys.path.insert(0, str(lib_path.resolve()))

                with open(predictor_path, "rb") as f:
                    fsp = pickle.load(f)
                predictor_cache.put(predictor_path, fsp)

            # Extract schema from embedding space codecs
            input_columns = {}
            for col_name, codec in fsp.embedding_space.col_codecs.items():
                if col_name == fsp.target_col_name:
                    continue

                col_info = {"required": True}

                # Get type and stats from codec
                if hasattr(codec, "token_dtype"):
                    if codec.token_dtype == "int64" or codec.token_dtype == "float64":
                        col_info["type"] = "numeric"
                        if hasattr(codec, "mean"):
                            col_info["mean"] = float(codec.mean) if codec.mean is not None else None
                        if hasattr(codec, "std"):
                            col_info["std"] = float(codec.std) if codec.std is not None else None
                        if hasattr(codec, "min"):
                            col_info["min"] = float(codec.min) if codec.min is not None else None
                        if hasattr(codec, "max"):
                            col_info["max"] = float(codec.max) if codec.max is not None else None
                    else:
                        col_info["type"] = "categorical"
                        if hasattr(codec, "vocabulary"):
                            vocab = codec.vocabulary
                            col_info["cardinality"] = len(vocab)
                            if len(vocab) < 100:
                                col_info["value_set"] = list(vocab)
                            else:
                                col_info["top_values"] = list(vocab)[:20]

                input_columns[col_name] = col_info

            # Get target info
            target_info = {
                "target_column": fsp.target_col_name,
                "target_column_type": fsp.target_col_type,
                "input_columns": input_columns,
            }

            # Add target classes for classification
            if fsp.target_col_type == "set" and hasattr(fsp, "target_codec"):
                if hasattr(fsp.target_codec, "vocabulary"):
                    target_info["target_classes"] = list(fsp.target_codec.vocabulary)

            return JSONResponse(target_info)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting predictor schema: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    @app.get("/session/{session_id}/prediction_job/{job_id}")
    async def get_prediction_job_status(session_id: str, job_id: str) -> JSONResponse:
        """Get the status of a Celery prediction job."""

        try:
            from celery_app import app as celery_app

            # Get task result
            task_result = celery_app.AsyncResult(job_id)

            # Also get Redis progress data for debugging
            redis_progress = None
            progress_messages = []
            try:
                import redis

                redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

                # Get current progress state
                redis_key = f"prediction_progress:{job_id}"
                progress_data = redis_client.get(redis_key)
                if progress_data:
                    redis_progress = json.loads(progress_data)
                    redis_progress["redis_ttl_seconds"] = redis_client.ttl(redis_key)

                # Get progress message history (last 30 messages)
                messages_key = f"prediction_messages:{job_id}"
                message_list = redis_client.lrange(messages_key, 0, -1)  # Get all messages
                for msg in message_list:
                    try:
                        progress_messages.append(json.loads(msg))
                    except:
                        pass

            except Exception as redis_err:
                logger.warning(f"Failed to get Redis progress for {job_id}: {redis_err}")

            if task_result.state == "PENDING":
                # Job is waiting to be processed
                response = {
                    "job_id": job_id,
                    "session_id": session_id,
                    "status": "pending",
                    "message": "Job is waiting to be processed",
                    "progress_messages": progress_messages,  # Include message history
                }
            elif task_result.state == "PROGRESS":
                # Job is running
                info = task_result.info or {}
                response = {
                    "job_id": job_id,
                    "session_id": session_id,
                    "status": "running",
                    "current": info.get("current", 0),
                    "total": info.get("total", 0),
                    "message": info.get("status", "Processing..."),
                    "progress_messages": progress_messages,  # Include message history
                }

                # Add progress percentage
                if info.get("total", 0) > 0:
                    progress = (info.get("current", 0) / info.get("total", 1)) * 100
                    response["progress_percent"] = round(progress, 1)

            elif task_result.state == "SUCCESS":
                # Job completed - check if it was actually successful or failed
                result = task_result.result

                # DEBUG: Log what we got from Celery
                logger.info(
                    f"🔍 Celery result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
                )
                logger.info(f"🔍 results_table type: {type(result.get('results_table'))}")
                logger.info(f"🔍 results_table is None: {result.get('results_table') is None}")
                if result.get("results_table"):
                    if isinstance(result["results_table"], dict):
                        logger.info(f"🔍 results_table keys: {list(result['results_table'].keys())[:10]}")

                # Check if the result indicates success or failure
                if result.get("success", True):
                    # Get model expiration info from session
                    try:
                        session = load_session(session_id)
                        model_expiration = get_model_expiration_info(session)
                    except Exception as e:
                        logger.warning(f"Could not load session for expiration info: {e}")
                        model_expiration = None

                    # Actually successful - return SAME format as synchronous endpoint
                    response = {
                        "job_id": job_id,
                        "session_id": session_id,
                        "status": "completed",
                        "message": "Prediction job completed successfully",
                        "predictions": result.get("predictions", []),  # Legacy format
                        "results_table": result.get("results_table"),  # JSON Tables format
                        "target_column": result.get("target_column"),
                        "target_column_type": result.get("target_column_type"),
                        "model_expiration": model_expiration,  # NEW: Model expiration info
                        "summary": {
                            "total_records": result.get("total_records", 0),
                            "successful_predictions": result.get("successful_predictions", 0),
                            "failed_predictions": result.get("failed_predictions", 0),
                            "errors": [],
                        },
                        "progress_messages": progress_messages,  # Include message history
                    }

                    # DEBUG: Log what we're about to return
                    logger.info(f"🔍 Response results_table type before clean: {type(response.get('results_table'))}")
                    logger.info(
                        f"🔍 Response results_table is None before clean: {response.get('results_table') is None}"
                    )
                else:
                    # Task returned failure result
                    error_info = result.get("error", "Unknown error")
                    traceback_info = result.get("traceback")

                    # Log full error details server-side
                    logger.error(f"Prediction job {job_id} failed:")
                    logger.error(f"  Session: {session_id}")
                    logger.error(f"  Error: {error_info}")
                    if traceback_info:
                        logger.error(f"  Traceback:\n{traceback_info}")
                    else:
                        logger.error("  No traceback available")

                    # Return failure response
                    response = {
                        "job_id": job_id,
                        "session_id": session_id,
                        "status": "failed",
                        "message": "Prediction job failed due to server error. Please check server logs or contact support.",
                        "error_code": "PREDICTION_JOB_FAILED",
                        "error_details": error_info,
                    }
            else:
                # Job failed or unknown state
                error_info = "Unknown error"
                traceback_info = None

                try:
                    if hasattr(task_result, "info") and task_result.info:
                        if isinstance(task_result.info, dict):
                            error_info = task_result.info.get("error", str(task_result.info))
                            traceback_info = task_result.info.get("traceback")
                        else:
                            error_info = str(task_result.info)
                    elif hasattr(task_result, "result") and task_result.result:
                        error_info = str(task_result.result)
                except Exception:
                    error_info = f"Task in state: {task_result.state}"

                # Log full error details server-side
                logger.error(f"Prediction job {job_id} failed:")
                logger.error(f"  Session: {session_id}")
                logger.error(f"  Error: {error_info}")
                if traceback_info:
                    logger.error(f"  Traceback: {traceback_info}")
                else:
                    logger.error("  Traceback: None (check Celery worker logs)")
                    logger.error(
                        f"  Task result info: {task_result.info if hasattr(task_result, 'info') else 'No info'}"
                    )
                    logger.error(
                        f"  Task result state: {task_result.state if hasattr(task_result, 'state') else 'No state'}"
                    )

                # Return generic message to client
                response = {
                    "job_id": job_id,
                    "session_id": session_id,
                    "status": "failed",
                    "message": "Prediction job failed due to server error. Please check server logs or contact support.",
                    "error_code": "PREDICTION_JOB_FAILED",
                }

            # Add Redis progress data for debugging
            if redis_progress:
                response["redis_progress"] = redis_progress
                # If we have more detailed Redis progress, prefer it
                if redis_progress.get("percentage") is not None:
                    response["progress_percent"] = redis_progress["percentage"]
                if redis_progress.get("status"):
                    response["detailed_status"] = redis_progress["status"]

            # Apply NaN cleaning to prevent JSON encoding errors
            cleaned_response = replace_nans_with_nulls(response)

            # DEBUG: Log after cleaning
            if response.get("status") == "completed":
                logger.info(
                    f"🔍 Response results_table type after clean: {type(cleaned_response.get('results_table'))}"
                )
                logger.info(
                    f"🔍 Response results_table is None after clean: {cleaned_response.get('results_table') is None}"
                )

            return JSONResponse(cleaned_response)

        except ImportError:
            raise HTTPException(
                status_code=HTTPStatus.NOT_IMPLEMENTED, detail="Celery not available - async predictions not supported"
            )
        except Exception as e:
            logger.error(f"Error checking prediction job status: {e}")

            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error checking job status: {str(e)}"
            )

    @app.get("/session/{id}/model_card")
    async def get_model_card(id: str) -> JSONResponse:
        """Get model card JSON for a session.
        
        If model card doesn't exist (e.g., during training), returns 202 Accepted
        with a message suggesting to use /columns endpoint instead.
        """
        from lib.model_card_repair import find_model_card, get_or_generate_model_card
        
        # Check if card exists on disk
        card_path = find_model_card(id)
        if card_path:
            with open(card_path) as f:
                model_card = json.load(f)
            model_card = sanitize_datetime_for_json(model_card)
            return JSONResponse(model_card)
        
        # Card doesn't exist - ask prediction server to generate it
        model_card, is_generating = get_or_generate_model_card(id)
        
        if model_card:
            model_card = sanitize_datetime_for_json(model_card)
            return JSONResponse(model_card)
        elif is_generating:
            return JSONResponse(
                {"status": "generating", "message": "Model card is being generated. Please retry in 2 minutes.", "session_id": id},
                status_code=HTTPStatus.ACCEPTED
            )
        else:
            # Model card doesn't exist - session may still be training
            # Suggest using /columns endpoint which works during training
            try:
                # Check if session exists (might still be training)
                session = load_session(id)
                # Session exists but model card doesn't - likely still training
                return JSONResponse(
                    {
                        "status": "training",
                        "message": "Model card not available - session may still be training. Use /session/{id}/columns endpoint to get column information during training.",
                        "session_id": id,
                        "alternative_endpoint": f"/session/{id}/columns"
                    },
                    status_code=HTTPStatus.ACCEPTED
                )
            except FileNotFoundError:
                # Session doesn't exist at all
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No model files found for session {id}")

    @app.post("/session/{id}/model_card")
    async def recreate_model_card(id: str) -> JSONResponse:
        """Force recreation of model card for a session. Returns the newly created model card.

        POST endpoint supports the same functionality as GET - both methods work identically.
        This allows clients to use either GET or POST without issues.
        """
        # POST just calls the GET handler - they do the same thing
        return await get_model_card(id)

    @app.get("/session/{id}/debug")
    async def debug_session_document(id: str) -> JSONResponse:
        """Debug endpoint to show raw session document structure."""

        try:
            session = load_session(id)

            # Show key fields for debugging
            debug_info = {
                "session_id": id,
                "raw_session_keys": list(session.keys()),
                "single_predictor": session.get("single_predictor"),
                "single_predictors": session.get("single_predictors"),
                "training_metrics": session.get("training_metrics"),
                "job_plan": session.get("job_plan"),
                "status": session.get("status"),
            }

            # Check if files actually exist
            single_predictors = session.get("single_predictors", [])
            training_metrics = session.get("training_metrics", [])

            debug_info["single_predictors_file_check"] = []
            if isinstance(single_predictors, list):
                for i, path in enumerate(single_predictors):
                    debug_info["single_predictors_file_check"].append(
                        {"index": i, "path": path, "exists": Path(path).exists() if path else False}
                    )

            debug_info["training_metrics_file_check"] = []
            if isinstance(training_metrics, list):
                for i, path in enumerate(training_metrics):
                    debug_info["training_metrics_file_check"].append(
                        {"index": i, "path": path, "exists": Path(path).exists() if path else False}
                    )

            # Check job output directories for this session
            session_timestamp = id.split("_")[0] if "_" in id else id[:13]
            matching_jobs = list(config.output_dir.glob(f"*{session_timestamp}*"))
            debug_info["matching_job_directories"] = []
            for job_dir in matching_jobs:
                if job_dir.is_dir():
                    metrics_file = job_dir / "training_metrics.json"
                    debug_info["matching_job_directories"].append(
                        {"name": job_dir.name, "path": str(job_dir), "has_training_metrics": metrics_file.exists(), "location": "local"}
                    )
            
            # Also check backplane
            backplane_root = Path("/backplane/backplane1/sphere")
            if backplane_root.exists():
                for host_dir in backplane_root.iterdir():
                    if host_dir.is_dir() and host_dir.name.startswith("host-"):
                        backplane_output_dir = host_dir / "app" / "featrix_output" / id
                        if backplane_output_dir.exists():
                            # Add all subdirectories
                            for subdir in backplane_output_dir.iterdir():
                                if subdir.is_dir():
                                    metrics_file = subdir / "training_metrics.json"
                                    debug_info["matching_job_directories"].append(
                                        {"name": subdir.name, "path": str(subdir), "has_training_metrics": metrics_file.exists(), "location": f"backplane/{host_dir.name}"}
                                    )

            return JSONResponse(debug_info)

        except Exception as e:
            return JSONResponse({"error": str(e), "session_id": id})

    @app.get("/session/{id}/training_metrics")
    async def get_session_training_metrics(id: str) -> JSONResponse:
        """
        Get training metrics for a single predictor (not embedding space).

        Note: This endpoint returns 404 if no single predictor has been trained yet.
        For embedding space training progress, use epoch_projections or training_movie endpoints.
        """

        session = load_session(id)
        metrics_path = session.get("training_metrics")

        # Enhanced debugging for training metrics issues
        logger.info(f"🔍 TRAINING METRICS DEBUG for session {id}:")
        logger.info(f"   Raw metrics_path from session: {metrics_path}")
        logger.info(f"   Type: {type(metrics_path)}")

        # Handle both old format (single string) and new format (list of paths)
        if not metrics_path:
            logger.warning(f"⚠️ No training_metrics field found in session {id}")
            logger.warning(f"   Session keys: {list(session.keys())}")
            logger.warning(f"   Session job_plan: {session.get('job_plan', 'No job_plan')}")

            # FALLBACK: Search for training metrics files in job output directories
            logger.info("🔍 Attempting fallback search for training metrics files...")
            try:
                session_info = get_session_info(session_id=id)
                jobs = session_info.get("jobs", {})

                # Look for training metrics in single predictor job outputs
                fallback_paths = []
                for job_id, job in jobs.items():
                    job_type = job.get("type", "")
                    if job_type == "train_single_predictor":
                        session_id = job.get("session_id")
                        job_output_dir = get_job_output_path(job_id, session_id, job_type)
                        metrics_file = job_output_dir / "training_metrics.json"
                        if metrics_file.exists():
                            fallback_paths.append(str(metrics_file))
                            logger.info(f"✅ Found fallback training metrics: {metrics_file}")

                # If not found in job outputs, search backplane
                if not fallback_paths:
                    logger.info("🔍 Job-based search failed, checking backplane...")
                    backplane_root = Path("/backplane/backplane1/sphere")
                    if backplane_root.exists():
                        for host_dir in backplane_root.iterdir():
                            if host_dir.is_dir() and host_dir.name.startswith("host-"):
                                backplane_output_dir = host_dir / "app" / "featrix_output" / id
                                if backplane_output_dir.exists():
                                    # Look for training metrics in subdirectories
                                    for subdir in backplane_output_dir.glob("train_single_predictor_*"):
                                        metrics_file = subdir / "training_metrics.json"
                                        if metrics_file.exists():
                                            fallback_paths.append(str(metrics_file))
                                            logger.info(f"✅ Found fallback training metrics in backplane ({host_dir.name}): {metrics_file}")
                
                if fallback_paths:
                    logger.info(f"✅ Fallback successful: found {len(fallback_paths)} training metrics files")
                    metrics_path = fallback_paths  # Use fallback paths
                else:
                    logger.error("❌ Fallback failed: no training metrics files found in job outputs or backplane")
                    post_slack_alert(f"session={id}; no training metrics found in session or job outputs")
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail="Training metrics not available - no single predictor has been trained yet for this session",
                    )

            except Exception as fallback_error:
                logger.error(f"❌ Fallback search failed: {fallback_error}")
                post_slack_alert(
                    f"session={id}; training metrics field missing and fallback search failed: {fallback_error}"
                )
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Training metrics not available - no single predictor has been trained yet for this session",
                )

        # For backward compatibility, if it's a list, take the first one
        # In the future, we might want to support specifying which predictor's metrics to get
        if isinstance(metrics_path, list):
            logger.info(f"   List format: {len(metrics_path)} entries")
            for i, path in enumerate(metrics_path):
                logger.info(f"     [{i}]: {path} (exists: {Path(path).exists() if path else False})")

            # Find the first non-null path that exists
            actual_path = None
            for i, path in enumerate(metrics_path):
                if path and Path(path).exists():
                    actual_path = path
                    logger.info(f"   ✅ Using metrics from predictor {i}: {path}")
                    break

            if not actual_path:
                logger.error(f"❌ No valid training metrics found in list of {len(metrics_path)} entries")
                logger.error(f"   All entries: {metrics_path}")

                # Additional debugging - check if any training_metrics.json files exist for this session
                try:
                    session_timestamp = id.split("_")[0] if "_" in id else id[:13]
                    matching_jobs = list(config.output_dir.glob(f"train_single_predictor_{session_timestamp}*"))
                    logger.error(f"   Found {len(matching_jobs)} matching job directories in local output_dir:")
                    for job_dir in matching_jobs:
                        metrics_file = job_dir / "training_metrics.json"
                        logger.error(f"     {job_dir.name}: metrics file exists = {metrics_file.exists()}")
                    
                    # Also check backplane
                    backplane_root = Path("/backplane/backplane1/sphere")
                    if backplane_root.exists():
                        logger.error(f"   Searching backplane for session {id}...")
                        backplane_count = 0
                        for host_dir in backplane_root.iterdir():
                            if host_dir.is_dir() and host_dir.name.startswith("host-"):
                                backplane_output_dir = host_dir / "app" / "featrix_output" / id
                                if backplane_output_dir.exists():
                                    backplane_count += 1
                                    # Look for training metrics in subdirectories
                                    for subdir in backplane_output_dir.glob("train_single_predictor_*"):
                                        metrics_file = subdir / "training_metrics.json"
                                        if metrics_file.exists():
                                            logger.error(f"     {host_dir.name}/{subdir.name}: metrics file exists = True")
                        logger.error(f"   Found session output in {backplane_count} backplane hosts")
                except Exception as e:
                    logger.error(f"   Could not search for job directories: {e}")

                post_slack_alert(f"session={id}; no valid training metrics files found in array of {len(metrics_path)}")
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail=f"Training metrics files not found on disk - single predictor training may not have completed yet (checked {len(metrics_path)} paths)",
                )

        else:
            logger.info(f"   String format: {metrics_path}")
            actual_path = metrics_path

        logger.info(f"   Using path: {actual_path}")

        if not Path(actual_path).exists():
            logger.error(f"❌ Training metrics file not found at: {actual_path}")

            # Additional debugging - check if file exists in working directory
            try:
                working_dir = Path(actual_path).parent
                existing_files = list(working_dir.glob("*")) if working_dir.exists() else []
                logger.error(f"   Working directory ({working_dir}) exists: {working_dir.exists()}")
                logger.error(f"   Files in working directory: {existing_files}")

                # Check for any training_metrics.json files
                tm_files = list(working_dir.glob("**/training_metrics.json")) if working_dir.exists() else []
                logger.error(f"   Found training_metrics.json files: {tm_files}")

            except Exception as debug_error:
                logger.error(f"   Could not debug file paths: {debug_error}")

            post_slack_alert(f"session={id}; training metrics file not found at {actual_path}")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f"Training metrics file not found at {actual_path}"
            )

        try:
            logger.info(f"✅ Reading training metrics from: {actual_path}")
            metrics = json.loads(Path(actual_path).read_text())

            # Apply NaN cleaning to prevent JSON encoding errors
            cleaned_metrics = replace_nans_with_nulls(metrics)

            logger.info(f"✅ Successfully loaded training metrics with keys: {list(cleaned_metrics.keys())}")

            return JSONResponse(
                {
                    "training_metrics": cleaned_metrics,
                }
            )
        except Exception as e:
            logger.error(f"❌ Error loading training metrics from {actual_path}: {e}")
            post_slack_alert(f"session={id}; error loading training metrics from {actual_path}: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error loading training metrics: {str(e)}"
            )

    @app.get("/compute/session/{id}/single_predictor_metrics")
    async def get_training_metrics_alias(id: str) -> JSONResponse:
        """Alias for backward compatibility - redirects to training_metrics."""
        return await get_session_training_metrics(id)

    class TrainPredictorRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        target_column: str
        target_column_type: str  # "set" or "scalar"
        epochs: int = 0  # 0 = auto-calculate using ideal_epochs_predictor
        batch_size: int = 0  # 0 = auto-calculate using ideal_batch_size
        learning_rate: Optional[float] = None  # None = auto-select based on fine_tune (1e-3 standard, 1e-5 fine-tune)
        rare_label_value: Optional[str] = None  # Rare label (minority class) for binary classification
        use_class_weights: bool = True  # Enable class weighting by default for imbalanced data
        class_imbalance: Optional[dict] = None  # Expected class ratios/counts from real world (set codec only)
        cost_false_positive: Optional[float] = (
            None  # Cost of false positive (only for set columns). If not provided, defaults to 1.0.
        )
        cost_false_negative: Optional[float] = (
            None  # Cost of false negative (only for set columns). If not provided, defaults to negatives/positives ratio.
        )
        webhooks: Optional[Dict[str, str]] = (
            None  # Webhook configuration (webhook_callback_secret, s3_backup_url, model_id_update_url)
        )

    class TrainPredictorMoreRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        predictor_id: Optional[str] = None  # Predictor ID to continue training (highest priority)
        target_column: Optional[str] = None  # Target column name to find predictor (alternative to predictor_id)
        epochs: int = 50  # Additional epochs to train (required)
        batch_size: int = 0  # 0 = use existing batch_size from predictor
        learning_rate: Optional[float] = None  # None = use existing learning rate from predictor
        webhooks: Optional[Dict[str, str]] = (
            None  # Webhook configuration (webhook_callback_secret, s3_backup_url, model_id_update_url)
        )

    class TrainFoundationModelMoreRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        es_id: Optional[str] = None  # Embedding space ID (optional, uses session's ES if not provided)
        data_passes: int = 50  # Additional epochs to train (required)
        webhooks: Optional[Dict[str, str]] = (
            None  # Webhook configuration (webhook_callback_secret, s3_backup_url, model_id_update_url)
        )

    class TrainOnFoundationModelRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        foundation_model_id: str  # Session ID of the foundation model (must have trained embedding space)
        target_column: str
        target_column_type: str  # "set" or "scalar"
        input_filename: Optional[str] = None  # Optional input data file (uses foundation model's data if not provided)
        name: Optional[str] = None  # Optional name for the new session
        session_name_prefix: Optional[str] = (
            None  # Optional prefix for session ID. Session will be named <prefix>-<uuid> or <prefix>-<uuid6>-<timestamp>
        )
        epochs: int = 0  # 0 = auto-calculate using ideal_epochs_predictor
        batch_size: int = 0  # 0 = auto-calculate using ideal_batch_size
        learning_rate: float = 0.001
        rare_label_value: Optional[str] = None  # Rare label (minority class) for binary classification
        use_class_weights: bool = True  # Enable class weighting by default for imbalanced data
        class_imbalance: Optional[dict] = None  # Expected class ratios/counts from real world (set codec only)
        optimize_for: Optional[str] = None  # DEPRECATED: Ignored, kept for backward compatibility
        webhooks: Optional[Dict[str, str]] = (
            None  # Webhook configuration (webhook_callback_secret, s3_backup_url, model_id_update_url)
        )
    
    class TrainOnPartialFoundationRequest(BaseModel):
        """Train a predictor on a partial/in-progress foundation model."""
        model_config = ConfigDict(
            protected_namespaces=()
        )
        
        # Removed - foundation_session_id comes from URL path {id}
        checkpoint_epoch: Optional[int] = None  # Which epoch checkpoint to use (None = best/latest available)
        target_column: str
        target_column_type: str  # "set" or "scalar"
        name: Optional[str] = None  # Optional name for the new session
        session_name_prefix: Optional[str] = None  # Optional prefix for session ID
        epochs: int = 0  # Predictor epochs (0 = auto)
        rare_label_value: Optional[str] = None
        use_class_weights: bool = True
        class_imbalance: Optional[dict] = None
        cost_false_positive: Optional[float] = None
        cost_false_negative: Optional[float] = None
        webhooks: Optional[Dict[str, str]] = None
    
    class PublishPartialFoundationRequest(BaseModel):
        """Publish a checkpoint from in-progress training as a standalone foundation model."""
        model_config = ConfigDict(
            protected_namespaces=()
        )
        
        checkpoint_epoch: Optional[int] = None  # Which epoch (None = best/latest)
        name: str  # Name for the new foundation model (required)
        session_name_prefix: Optional[str] = None  # Optional prefix for session ID
        publish: bool = True  # Move to /backplane/backplane1/sphere/PUBLISHED/ directory
        org_id: Optional[str] = None  # Organization ID for publishing (required if publish=True)

    class UpdateLabelRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        prediction_id: str
        user_label: str

    class CreateEmbeddingSpaceRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings

        name: str
        s3_file_data_set_training: str
        s3_file_data_set_validation: str
        user_metadata: dict | None = None  # User metadata for identification (max 32KB)

    class CloneEmbeddingSpaceRequest(BaseModel):
        model_config = ConfigDict(
            protected_namespaces=()
        )  # Allow fields starting with "model_" to avoid Pydantic warnings
        from_compute: str | None = None
        to_compute: str | None = None
        to_compute_url: str | None = None
        es_id: str | None = None
        new_session_name: str | None = None

    class FineTuneEmbeddingSpaceRequest(BaseModel):
        name: str
        parent_session_id: str | None = None  # Session ID of parent embedding space
        parent_embedding_space_path: str | None = None  # Direct path to parent embedding space pickle file
        s3_file_data_set_training: str
        s3_file_data_set_validation: str
        user_metadata: dict | None = None  # User metadata for identification (max 32KB)

    class ExtendEmbeddingSpaceRequest(BaseModel):
        name: str
        parent_session_id: str | None = None  # Session ID of parent embedding space
        parent_embedding_space_path: str | None = None  # Direct path to parent embedding space pickle file
        s3_file_data_set_training: str  # Training data with new feature columns
        s3_file_data_set_validation: str  # Validation data with new feature columns
        n_epochs: int | None = None  # Number of epochs for extension (default: original_epochs / 4)
        user_metadata: dict | None = None  # User metadata for identification (max 32KB)

    # Note: CloneReceiveChunkRequest uses Form data (not BaseModel) for file upload

    @app.post("/create-embedding-space")
    async def create_embedding_space(request: CreateEmbeddingSpaceRequest) -> JSONResponse:
        """Create a new embedding space with S3 training and validation datasets."""

        try:
            # Validate S3 paths
            if not request.s3_file_data_set_training.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_training must be a valid S3 URL (s3://...)",
                )

            if not request.s3_file_data_set_validation.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_validation must be a valid S3 URL (s3://...)",
                )

            # Create a session with embedding space configuration
            embedding_space_config = {
                "name": request.name,
                "training_dataset": request.s3_file_data_set_training,
                "validation_dataset": request.s3_file_data_set_validation,
                "created_at": datetime.datetime.now(timezone.utc).isoformat(),
            }

            session = create_embedding_space_session(
                name=request.name,
                s3_training_path=request.s3_file_data_set_training,
                s3_validation_path=request.s3_file_data_set_validation,
                user_metadata=request.user_metadata,
            )

            # Dispatch first job in chain (Celery will handle the rest automatically)
            from lib.session_chains import dispatch_next_job_in_chain

            dispatch_next_job_in_chain(session_id=session.get("session_id"))

            logger.info(f"Created embedding space session: {session.get('session_id')} with name: {request.name}")
            logger.debug(f"Embedding space config: {embedding_space_config}")

            serialized_session = serialize_session(session)

            # Add the embedding space configuration to the response
            serialized_session["embedding_space_config"] = embedding_space_config

            return JSONResponse(serialized_session)

        except HTTPException:
            raise
        except Exception as e:
            # Check if this is a NodeUpgradingException
            if isinstance(e, NodeUpgradingException):
                logger.warning(f"Node is upgrading: {e}")
                raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e))
            logger.error(f"Error creating embedding space: {e}")
            traceback.print_exc()
            post_slack_alert(f"error creating embedding space with name={request.name}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error creating embedding space: {str(e)}"
            )

    @app.post("/fine-tune-embedding-space")
    async def fine_tune_embedding_space(request: FineTuneEmbeddingSpaceRequest) -> JSONResponse:
        """Fine-tune an existing embedding space on a new dataset.

        Takes a pre-trained embedding space (parent) and fine-tunes it on new data.
        The number of epochs is automatically calculated as: original_epochs / F
        where F = len(new_dataset) / len(old_dataset)
        """
        try:
            # Validate S3 paths
            if not request.s3_file_data_set_training.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_training must be a valid S3 URL (s3://...)",
                )

            if not request.s3_file_data_set_validation.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_validation must be a valid S3 URL (s3://...)",
                )

            # Validate that we have either parent_session_id or parent_embedding_space_path
            if not request.parent_session_id and not request.parent_embedding_space_path:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Either parent_session_id or parent_embedding_space_path must be provided",
                )

            # Import fine-tuning function

            # Create fine-tuning session
            session = create_fine_tune_embedding_space_session(
                name=request.name,
                parent_session_id=request.parent_session_id,
                parent_embedding_space_path=request.parent_embedding_space_path,
                s3_training_path=request.s3_file_data_set_training,
                s3_validation_path=request.s3_file_data_set_validation,
                user_metadata=request.user_metadata,
            )

            # Dispatch first job in chain (Celery will handle the rest automatically)
            from lib.session_chains import dispatch_next_job_in_chain

            dispatch_next_job_in_chain(session_id=session.get("session_id"))

            logger.info(f"Created fine-tuning session: {session.get('session_id')} with name: {request.name}")

            serialized_session = serialize_session(session)

            return JSONResponse(serialized_session)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fine-tuning embedding space: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error fine-tuning embedding space: {str(e)}"
            )

    @app.post("/extend-embedding-space")
    async def extend_embedding_space(request: ExtendEmbeddingSpaceRequest) -> JSONResponse:
        """Extend an existing embedding space with new feature columns.

        Takes a pre-trained embedding space (parent) and extends it with new feature columns
        from enriched training/validation data. The extended ES preserves existing encoder
        weights and creates new codecs for the new columns.
        """
        try:
            # Validate S3 paths
            if not request.s3_file_data_set_training.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_training must be a valid S3 URL (s3://...)",
                )

            if not request.s3_file_data_set_validation.startswith("s3://"):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="s3_file_data_set_validation must be a valid S3 URL (s3://...)",
                )

            # Validate that we have either parent_session_id or parent_embedding_space_path
            if not request.parent_session_id and not request.parent_embedding_space_path:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Either parent_session_id or parent_embedding_space_path must be provided",
                )

            # Create extension session
            from lib.session_manager import create_extend_embedding_space_session

            session = create_extend_embedding_space_session(
                name=request.name,
                parent_session_id=request.parent_session_id,
                parent_embedding_space_path=request.parent_embedding_space_path,
                s3_training_path=request.s3_file_data_set_training,
                s3_validation_path=request.s3_file_data_set_validation,
                n_epochs=request.n_epochs,
                user_metadata=request.user_metadata,
            )

            # Dispatch first job in chain (Celery will handle the rest automatically)
            from lib.session_chains import dispatch_next_job_in_chain

            dispatch_next_job_in_chain(session_id=session.get("session_id"))

            logger.info(f"Created extend ES session: {session.get('session_id')} with name: {request.name}")

            serialized_session = serialize_session(session)

            return JSONResponse(serialized_session)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extending embedding space: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error extending embedding space: {str(e)}"
            )

    # Compute node configuration - fetched from Flask API on startup
    # (Defined in create_app() function above)

    def get_es_host_mapping(es_path: str) -> Optional[str]:
        """Get cached host for an embedding space path."""
        try:
            import redis

            redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True, socket_timeout=1, socket_connect_timeout=1
            )
            redis_client.ping()
            host = redis_client.get(f"es_host:{es_path}")
            return host
        except Exception:
            return None

    def cache_es_host_mapping(es_path: str, host: str, ttl: int = 86400):
        """Cache host mapping for an embedding space."""
        try:
            import redis

            redis_client = redis.Redis(
                host="localhost", port=6379, db=0, decode_responses=True, socket_timeout=1, socket_connect_timeout=1
            )
            redis_client.ping()
            redis_client.setex(f"es_host:{es_path}", ttl, host)
            logger.info(f"💾 Cached ES host mapping: {es_path} -> {host}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache ES host mapping: {e}")
            return False

    def check_node_health(node_name: str, node_url: str, timeout: float = 2.0) -> Optional[Dict]:
        """Check health of a compute node, focusing on GPU availability."""
        try:
            import requests

            response = requests.get(f"{node_url}/health", timeout=timeout)
            if response.status_code == 200:
                health_data = response.json()

                # Check GPU availability
                gpu_info = health_data.get("gpu", {})
                gpu_available = False
                gpu_free_gb = 0.0
                gpu_count = 0

                if isinstance(gpu_info, dict) and gpu_info.get("available"):
                    gpu_count = gpu_info.get("gpu_count", 0)
                    total_free_gb = gpu_info.get("total_free_gb", 0.0)
                    gpu_free_gb = total_free_gb
                    # Consider GPU available if we have at least 1GB free
                    gpu_available = total_free_gb >= 1.0

                return {
                    "node_name": node_name,
                    "node_url": node_url,
                    "available": gpu_available,
                    "gpu_available": gpu_available,
                    "gpu_free_gb": round(gpu_free_gb, 2),
                    "gpu_count": gpu_count,
                    "health_data": health_data,
                }
            else:
                return {
                    "node_name": node_name,
                    "node_url": node_url,
                    "available": False,
                    "gpu_available": False,
                    "error": f"HTTP {response.status_code}",
                }
        except Exception as e:
            return {
                "node_name": node_name,
                "node_url": node_url,
                "available": False,
                "gpu_available": False,
                "error": str(e),
            }

    def get_available_nodes() -> List[Dict]:
        """Check health of all compute nodes and return availability info."""
        node_healths = []
        for node_name, node_url in COMPUTE_NODES.items():
            health = check_node_health(node_name, node_url)
            if health:
                node_healths.append(health)
        return node_healths

    def recommend_host(es_path: str = None) -> Optional[str]:
        """Recommend a host with available GPU."""
        available_nodes = get_available_nodes()

        # Filter to only nodes with available GPU
        available = [n for n in available_nodes if n.get("gpu_available", False)]

        if not available:
            logger.warning("No compute nodes with available GPU found")
            return None

        # Sort by GPU free memory (higher is better) - prefer nodes with more free GPU memory
        available.sort(key=lambda x: -x.get("gpu_free_gb", 0.0))

        recommended = available[0]
        recommended_host = recommended.get("node_name")

        logger.info(
            f"🎯 Recommended host: {recommended_host} (GPU free: {recommended.get('gpu_free_gb')} GB, GPUs: {recommended.get('gpu_count')})"
        )

        # Cache the recommendation if ES path provided
        if es_path and recommended_host:
            cache_es_host_mapping(es_path, recommended_host)

        return recommended_host

    # File-based cache for JSON encoder API queries (persists across restarts, works across processes)
    # Cache TTL: 60 seconds (new ES sessions may be created, so we need some freshness)
    _json_encoder_cache = JsonEncoderCache(cache_file=Path("/sphere/app/json_encoder_cache.json"), ttl_seconds=60)

    @app.get("/api-sphere/json-encoders")
    async def get_json_encoders(
        schema_fields: str = Query(..., description="Comma-separated list of schema field names"),
    ):
        """
        Query for embedding spaces that match a JSON schema.
        Returns ES info along with host information and recommendations.

        Args:
            schema_fields: Comma-separated list of field names in the JSON schema

        Returns:
            Matching embedding space information with host assignment/recommendation
        """
        try:
            # Parse schema fields
            fields = [f.strip() for f in schema_fields.split(",") if f.strip()]
            fields_set = set(fields)

            if not fields:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail="schema_fields must contain at least one field name"
                )

            # Check cache first (use sorted fields as key for consistency)
            schema_fields_key = ",".join(sorted(fields))
            cached_result = _json_encoder_cache.get(schema_fields_key)
            if cached_result is not None:
                logger.info(
                    f"✅ Returning cached JSON encoder result for schema fields: {fields[:5]}{'...' if len(fields) > 5 else ''}"
                )
                return JSONResponse(cached_result)

            logger.info(f"🔍 Querying JSON encoders for schema fields: {fields} (cache miss)")

            # Search through all embedding space sessions (using Redis)
            from lib.session_manager import iterate_over_sessions

            # Load all embedding space sessions from Redis
            matching_es = None
            best_match_score = 0

            for session in iterate_over_sessions():
                try:
                    session_id = session.get("session_id")
                    if not session_id:
                        continue
                    
                    # Only check embedding space sessions
                    if session.get("session_type") != "embedding_space":
                        continue

                    # Check if embedding space file exists
                    embedding_space_path = session.get("embedding_space")
                    resolved_es_path = resolve_embedding_space_path(embedding_space_path) if embedding_space_path else None
                    if not resolved_es_path:
                        continue
                    embedding_space_path = str(resolved_es_path)

                    # Load embedding space to get schema
                    try:
                        es = load_embedded_space(embedding_space_path)

                        # Get column names from embedding space
                        es_columns = set(es.get_column_names())

                        # Calculate match score (how many fields match)
                        matched_fields = fields_set.intersection(es_columns)
                        match_score = len(matched_fields) / len(fields_set) if fields_set else 0

                        # Require at least 80% match to consider it a match
                        if match_score >= 0.8 and match_score > best_match_score:
                            best_match_score = match_score
                            matching_es = {
                                "session_id": session.get("session_id"),
                                "name": session.get("name"),
                                "embedding_space_path": embedding_space_path,
                                "schema_fields": sorted(list(es_columns)),
                                "matched_fields": sorted(list(matched_fields)),
                                "match_score": match_score,
                                "created_at": session.get("created_at").isoformat()
                                if session.get("created_at")
                                else None,
                            }
                            logger.info(f"✅ Found matching ES: {session.get('name')} (score: {match_score:.2f})")

                    except Exception as e:
                        logger.warning(f"Failed to load ES from {embedding_space_path}: {e}")
                        continue

                except Exception as e:
                    logger.warning(f"Failed to process session {session_id if 'session_id' in locals() else 'unknown'}: {e}")
                    continue

            # Get host information
            host_info = None
            recommended_host = None

            if matching_es:
                es_path = matching_es.get("embedding_space_path")

                # Check if we have a cached host for this ES
                cached_host = get_es_host_mapping(es_path)

                if cached_host:
                    # Verify the cached host still has available GPU
                    host_health = check_node_health(cached_host, COMPUTE_NODES.get(cached_host))
                    if host_health and host_health.get("gpu_available"):
                        host_info = {
                            "host": cached_host,
                            "host_url": COMPUTE_NODES.get(cached_host),
                            "source": "cached",
                            "health": host_health,
                        }
                        logger.info(
                            f"✅ Using cached host: {cached_host} (GPU free: {host_health.get('gpu_free_gb')} GB)"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Cached host {cached_host} no longer has available GPU, will recommend new host"
                        )
                        cached_host = None

                # If no cached host or cached host unavailable, recommend one
                if not cached_host:
                    recommended_host = recommend_host(es_path)
                    if recommended_host:
                        host_info = {
                            "host": recommended_host,
                            "host_url": COMPUTE_NODES.get(recommended_host),
                            "source": "recommended",
                            "health": check_node_health(recommended_host, COMPUTE_NODES.get(recommended_host)),
                        }
                        logger.info(f"🎯 Recommended host: {recommended_host}")
            else:
                # No matching ES, but still provide host recommendation for future use
                recommended_host = recommend_host()
                if recommended_host:
                    host_info = {
                        "host": recommended_host,
                        "host_url": COMPUTE_NODES.get(recommended_host),
                        "source": "recommended",
                        "health": check_node_health(recommended_host, COMPUTE_NODES.get(recommended_host)),
                    }

            # Get all node health for reference
            all_nodes_health = get_available_nodes()

            if matching_es:
                matching_es["host"] = host_info
                logger.info(
                    f"📋 Returning matched ES: {matching_es['name']} (session: {matching_es['session_id']}, host: {host_info.get('host') if host_info else 'none'})"
                )
                result = {
                    "matched_es": matching_es,
                    "available_nodes": all_nodes_health,
                    "message": f"Found matching embedding space: {matching_es['name']}",
                }
            else:
                logger.info(f"❌ No matching embedding space found for schema: {fields}")
                result = {
                    "matched_es": None,
                    "host": host_info,
                    "available_nodes": all_nodes_health,
                    "message": f"No matching embedding space found for schema fields: {fields}",
                    "requested_fields": fields,
                }

            # Cache the result before returning
            _json_encoder_cache.set(schema_fields_key, result)
            return JSONResponse(result)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error querying JSON encoders: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error querying JSON encoders: {str(e)}"
            )

    @app.post("/session/{id}/train_predictor")
    async def train_single_predictor_on_session(id: str, request: TrainPredictorRequest) -> JSONResponse:
        """Add predictor training to an existing session. Multiple predictors are supported."""

        logger.info(f"Training single predictor on session {id} with request {request}")
        try:
            session = load_session(id)
        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for predictor training")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

        # Check if there's an ES job in the session - predictor can be queued even if ES is still training
        logger.info("🔍 Checking if session has ES training in job plan...")
        embedding_space_path = session.get("embedding_space")
        job_plan = session.get("job_plan", [])
        has_es_job = any(job.get("job_type") == "train_es" for job in job_plan)

        if not has_es_job and (not embedding_space_path or not Path(embedding_space_path).exists()):
            # No ES job in plan and no existing embedding space - can't train predictor
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="No embedding space found or planned. Train an embedding space first before training a predictor.",
            )

        if embedding_space_path and Path(embedding_space_path).exists():
            logger.info(f"✅ Embedding space found: {embedding_space_path}")
        else:
            logger.info("⏳ Embedding space not ready yet - predictor will wait in queue for ES training to complete")

        # Validate request parameters
        if request.target_column_type not in ["set", "scalar"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="target_column_type must be 'set' or 'scalar'"
            )

        try:
            from lib.session_chains import dispatch_next_job_in_chain

            # Check if any non-predictor jobs are currently running - wait for them to complete
            # session_jobs = load_session_jobs(session)
            # running_jobs = [job_id for job_id, job in session_jobs.items()
            #               if job.get("status").value == "running" and job.get("type") != "train_single_predictor"]

            # if running_jobs:
            #     raise HTTPException(
            #         status_code=HTTPStatus.CONFLICT,
            #         detail=f"Cannot add predictor training while other jobs are running: {', '.join(running_jobs)}. Please wait for current jobs to complete."
            #     )

            # Validate cost parameters if provided
            if request.cost_false_positive is not None or request.cost_false_negative is not None:
                if request.cost_false_positive is None or request.cost_false_negative is None:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail="Both cost_false_positive and cost_false_negative must be specified together",
                    )
                if request.target_column_type != "set":
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail="cost_false_positive and cost_false_negative are only valid for target_column_type='set' (classification), not 'scalar' (regression)",
                    )
                if request.cost_false_positive <= 0 or request.cost_false_negative <= 0:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail="cost_false_positive and cost_false_negative must be positive numbers",
                    )
                logger.info(
                    f"💰 User-provided costs: FP cost={request.cost_false_positive}, FN cost={request.cost_false_negative}"
                )

            # Create the training spec for the single predictor
            # CRITICAL: Grid search results hardcoded here - fine_tune=True (+3.18pp), n_hidden_layers=7 (peak AUC 0.7409)
            training_spec = {
                "target_column": request.target_column,
                "target_column_type": request.target_column_type,
                "n_epochs": request.epochs,  # Use "n_epochs" to match job runner expectations
                "batch_size": request.batch_size,
                "learning_rate": request.learning_rate,
                "fine_tune": True,  # HARDCODED: Grid search showed +3.18pp AUC improvement
                "n_hidden_layers": 7,  # HARDCODED: Grid search showed peak performance (AUC 0.7409)
                "positive_label": request.rare_label_value,  # Map rare_label_value to internal positive_label parameter
                "use_class_weights": request.use_class_weights,  # Enable/disable class weighting (default True)
                "class_imbalance": request.class_imbalance,  # Pass expected class ratios/counts from real world
                "webhooks": request.webhooks,  # Pass webhook configuration
            }
            if request.cost_false_positive is not None and request.cost_false_negative is not None:
                training_spec["cost_false_positive"] = request.cost_false_positive
                training_spec["cost_false_negative"] = request.cost_false_negative

            logger.info(
                f"📋 Adding predictor #{len([j for j in session.get('job_plan', []) if j.get('job_type') == 'train_single_predictor'])} to job plan..."
            )
            # Add the single predictor job to the session's job plan
            job_plan = session.get("job_plan", [])

            # Count existing single predictor jobs to assign predictor_index
            existing_predictors = [job for job in job_plan if job.get("job_type") == "train_single_predictor"]
            predictor_index = len(existing_predictors)

            logger.info(f"🎯 Creating predictor job for '{request.target_column}' (index: {predictor_index})")
            # Always add new single predictor job - multiple predictors are supported
            job_plan.append(
                {
                    "job_type": "train_single_predictor",
                    "spec": training_spec,
                    "job_id": None,
                    "predictor_index": predictor_index,  # Track which predictor this is
                }
            )
            session["job_plan"] = job_plan

            logger.info(f"💾 Saving updated session with {len(job_plan)} jobs in plan...")
            logger.info(f"   Job plan now contains: {[j.get('job_type') for j in job_plan]}")
            
            # Save the updated session
            try:
                save_session(session_id=id, session_doc=session, exist_ok=True)
                logger.info(f"✅ Session saved successfully")
            except Exception as save_err:
                logger.error(f"❌ CRITICAL: Failed to save session after adding predictor job: {save_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save session with predictor job: {str(save_err)}"
                )
            
            # CRITICAL: Verify the save actually worked by reloading the session
            logger.info(f"🔍 Verifying session save by reloading...")
            try:
                verification_session = load_session(id)
                verification_job_plan = verification_session.get("job_plan", [])
                verification_predictor_jobs = [j for j in verification_job_plan if j.get("job_type") == "train_single_predictor"]
                
                if len(verification_predictor_jobs) != len(existing_predictors) + 1:
                    error_msg = (
                        f"CRITICAL: Session save verification FAILED! "
                        f"Expected {len(existing_predictors) + 1} predictor job(s) in job_plan, "
                        f"but found {len(verification_predictor_jobs)}. "
                        f"Session save did not persist the predictor job!"
                    )
                    logger.error(f"❌ {error_msg}")
                    logger.error(f"   Original job_plan length: {len(job_plan)}")
                    logger.error(f"   Verification job_plan length: {len(verification_job_plan)}")
                    logger.error(f"   Original predictor count: {len(existing_predictors)}")
                    logger.error(f"   Verification predictor count: {len(verification_predictor_jobs)}")
                    
                    # Try to save again as a last resort
                    logger.warning(f"🔄 Attempting emergency re-save...")
                    try:
                        save_session(session_id=id, session_doc=session, exist_ok=True)
                        verification_session2 = load_session(id)
                        verification_job_plan2 = verification_session2.get("job_plan", [])
                        verification_predictor_jobs2 = [j for j in verification_job_plan2 if j.get("job_type") == "train_single_predictor"]
                        
                        if len(verification_predictor_jobs2) == len(existing_predictors) + 1:
                            logger.info(f"✅ Emergency re-save succeeded!")
                        else:
                            raise HTTPException(
                                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=error_msg
                            )
                    except Exception as retry_err:
                        logger.error(f"❌ Emergency re-save also failed: {retry_err}")
                        raise HTTPException(
                            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            detail=error_msg
                        )
                else:
                    logger.info(f"✅ Session save verified: {len(verification_predictor_jobs)} predictor job(s) in job_plan")
            except Exception as verify_err:
                logger.error(f"❌ CRITICAL: Failed to verify session save: {verify_err}")
                logger.error(f"   Traceback: {traceback.format_exc()}")
                # Don't fail the request - the save might have worked, we just couldn't verify
                logger.warning(f"   Continuing anyway - save may have succeeded")

            # Dispatch the training job (Celery will handle chaining automatically)
            logger.info("▶️  Dispatching predictor training job...")
            dispatch_result = dispatch_next_job_in_chain(session_id=id)
            if dispatch_result:
                logger.info(f"✅ Predictor job dispatched successfully (task_id: {dispatch_result})")
            else:
                logger.warning(f"⚠️  dispatch_next_job_in_chain returned None - job may not have been dispatched")
                logger.warning(f"   This could mean:")
                logger.warning(f"   - Session status prevented dispatch")
                logger.warning(f"   - No workers available")
                logger.warning(f"   - Job was already dispatched")
                # Don't fail - the job is in the job_plan and will be dispatched when conditions are right
            return JSONResponse(
                {
                    "message": f"Single predictor #{predictor_index + 1} training added (targeting '{request.target_column}')",
                    "session_id": id,
                    "target_column": request.target_column,
                    "target_column_type": request.target_column_type,
                    "predictor_index": predictor_index,
                    "training_spec": training_spec,
                }
            )

        except Exception as e:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error starting predictor training")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error starting predictor training: {str(e)}"
            )

    @app.post("/session/{id}/train_predictor_more")
    async def train_predictor_more(id: str, request: TrainPredictorMoreRequest) -> JSONResponse:
        """
        Continue training an existing single predictor for more epochs.
        Loads the existing predictor and resumes training from where it left off.
        """
        logger.info(f"Continuing training for predictor on session {id} with request {request}")

        try:
            session = load_session(id)
        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for predictor continuation")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

        # Find the predictor to continue training
        single_predictors = session.get("single_predictors", [])
        if not single_predictors or not isinstance(single_predictors, list):
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="No trained predictors found in session. Train a predictor first.",
            )

        predictor_path = None
        predictor_index = None

        # Priority 1: Find by predictor_id
        if request.predictor_id:
            logger.info(f"🔍 Looking for predictor with ID: {request.predictor_id}")
            for i, pred_path in enumerate(single_predictors):
                if pred_path and Path(pred_path).exists():
                    # Generate predictor ID (same logic as in predict endpoint)
                    import hashlib

                    filename = os.path.basename(pred_path)
                    path_hash = hashlib.md5(pred_path.encode()).hexdigest()[:8]
                    current_predictor_id = f"{filename}_{path_hash}"

                    if current_predictor_id == request.predictor_id:
                        predictor_path = pred_path
                        predictor_index = i
                        logger.info(f"✅ Found predictor by ID at index {i}: {pred_path}")
                        break

        # Priority 2: Find by target_column
        if not predictor_path and request.target_column:
            logger.info(f"🔍 Looking for predictor with target_column: {request.target_column}")
            for i, pred_path in enumerate(single_predictors):
                if pred_path and Path(pred_path).exists():
                    # Load metadata to check target_column
                    metadata_path = Path(pred_path).parent / "model_metadata.json"
                    if metadata_path.exists():
                        try:
                            with open(metadata_path) as f:
                                metadata = json.load(f)
                                target_col = metadata.get("target_column")
                                if target_col == request.target_column:
                                    predictor_path = pred_path
                                    predictor_index = i
                                    logger.info(f"✅ Found predictor by target_column at index {i}: {pred_path}")
                                    break
                        except Exception as e:
                            logger.warning(f"Failed to read metadata for {pred_path}: {e}")
                            continue

        # Priority 3: Use first available predictor if only one exists
        if not predictor_path and len(single_predictors) == 1:
            pred_path = single_predictors[0]
            if pred_path and Path(pred_path).exists():
                predictor_path = pred_path
                predictor_index = 0
                logger.info(f"✅ Using single available predictor at index 0: {pred_path}")

        if not predictor_path or not Path(predictor_path).exists():
            available_predictors = []
            for i, pred_path in enumerate(single_predictors):
                if pred_path:
                    if Path(pred_path).exists():
                        # Try to get target_column from metadata
                        metadata_path = Path(pred_path).parent / "model_metadata.json"
                        target_col = "unknown"
                        if metadata_path.exists():
                            try:
                                with open(metadata_path) as f:
                                    metadata = json.load(f)
                                    target_col = metadata.get("target_column", "unknown")
                            except:
                                pass
                        available_predictors.append(f"  [{i}]: {pred_path} (target: {target_col})")
                    else:
                        available_predictors.append(f"  [{i}]: {pred_path} (file missing)")

            error_msg = "No valid predictor found to continue training."
            if available_predictors:
                error_msg += "\nAvailable predictors:\n" + "\n".join(available_predictors)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_msg)

        # Load predictor metadata to get training parameters
        metadata_path = Path(predictor_path).parent / "model_metadata.json"
        existing_metadata = {}
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    existing_metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read existing metadata: {e}")

        target_column = existing_metadata.get("target_column") or request.target_column
        target_column_type = existing_metadata.get("target_column_type")

        if not target_column:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Could not determine target_column. Please specify target_column in request.",
            )
        if not target_column_type:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Could not determine target_column_type from predictor metadata.",
            )

        # Create training spec for continuation
        training_spec = {
            "target_column": target_column,
            "target_column_type": target_column_type,
            "n_epochs": request.epochs,
            "batch_size": request.batch_size,  # 0 = use existing
            "learning_rate": request.learning_rate,  # None = use existing
            "resume_from_predictor": predictor_path,  # Key: path to existing predictor
            "predictor_index": predictor_index,
        }

        # Add webhooks if provided
        if request.webhooks:
            training_spec["webhooks"] = request.webhooks

        logger.info("📋 Setting up predictor continuation...")
        logger.info(f"   Predictor: {predictor_path}")
        logger.info(f"   Additional epochs: {request.epochs}")
        logger.info(f"   Predictor index: {predictor_index}")

        try:
            # Find the existing job in job_plan for this predictor
            job_plan = session.get("job_plan", [])
            existing_job_entry = None
            existing_job_id = None
            updated_existing_job = False

            for job_entry in job_plan:
                if (
                    job_entry.get("job_type") == "train_single_predictor"
                    and job_entry.get("predictor_index") == predictor_index
                ):
                    existing_job_entry = job_entry
                    existing_job_id = job_entry.get("job_id")
                    break

            if existing_job_entry and existing_job_id:
                # Found existing job - try to update it
                try:
                    from lib.job_manager import load_job as redis_load_job
                    existing_job = redis_load_job(existing_job_id)
                    if not existing_job:
                        raise FileNotFoundError(f"Job {existing_job_id} not found in Redis")
                    job_status = existing_job.get("status")

                    # Convert JobStatus enum to string if needed
                    if hasattr(job_status, "value"):
                        job_status = job_status.value

                    # Check if job is completed (DONE) or failed
                    if job_status in ["done", "failed"]:
                        logger.info(f"🔄 Found existing completed job {existing_job_id}, updating for continuation...")

                        # Update job spec to add continuation parameters
                        job_spec = existing_job.get("spec", {}).copy()
                        original_epochs = job_spec.get("n_epochs", 0)
                        new_total_epochs = original_epochs + request.epochs

                        # Update spec with continuation info
                        job_spec["n_epochs"] = new_total_epochs  # Total epochs (original + additional)
                        job_spec["resume_from_predictor"] = predictor_path  # Key: path to existing predictor
                        if request.batch_size > 0:
                            job_spec["batch_size"] = request.batch_size
                        if request.learning_rate is not None:
                            job_spec["learning_rate"] = request.learning_rate
                        if request.webhooks:
                            job_spec["webhooks"] = request.webhooks

                        # Reset job to READY for continuation
                        job_content = existing_job.copy()
                        job_content["status"] = JobStatus.READY.value
                        job_content["started_at"] = None
                        job_content["finished_at"] = None
                        job_content["progress"] = None
                        job_content["error_message"] = None
                        job_content["spec"] = job_spec

                        # Add continuation metadata
                        now = datetime.datetime.now(tz=ZoneInfo("America/New_York"))
                        if "recovery_info" not in job_content:
                            job_content["recovery_info"] = []
                        version_info = get_version_info()
                        job_content["recovery_info"].append(
                            {
                                "recovered_at": convert_to_iso(now),
                                "reason": "continuation_training",
                                "previous_status": job_status,
                                "original_epochs": original_epochs,
                                "additional_epochs": request.epochs,
                                "total_epochs": new_total_epochs,
                                "version": version_info,
                            }
                        )

                        # Save updated job
                        from lib.job_manager import save_job as redis_save_job
                        redis_save_job(
                            existing_job_id,
                            job_content,
                            existing_job.get("session_id", id),
                            "train_single_predictor"
                        )

                        # Update job_plan entry
                        existing_job_entry["spec"] = job_spec
                        session["job_plan"] = job_plan
                        save_session(session_id=id, session_doc=session, exist_ok=True)

                        logger.info(
                            f"✅ Updated job {existing_job_id} for continuation: {original_epochs} → {new_total_epochs} epochs"
                        )
                        logger.info("▶️  Job will resume from existing predictor and continue training")

                        updated_existing_job = True

                        # Job is already in queue, just needs to be picked up
                        # No need to call step_session - the job is READY and will be picked up automatically

                    else:
                        # Job is still running or in another state - create new continuation job
                        logger.warning(
                            f"⚠️  Existing job {existing_job_id} is in status '{job_status}', creating new continuation job instead"
                        )
                        raise ValueError("Job still running")

                except (FileNotFoundError, ValueError):
                    # Job not found or still running - create new continuation job
                    logger.info("📋 Creating new continuation job (existing job not found or still running)")
                    job_plan.append(
                        {
                            "job_type": "train_single_predictor_more",
                            "spec": training_spec,
                            "job_id": None,
                            "predictor_index": predictor_index,
                        }
                    )
                    session["job_plan"] = job_plan
                    save_session(session_id=id, session_doc=session, exist_ok=True)
                    from lib.session_chains import dispatch_next_job_in_chain

                    dispatch_next_job_in_chain(session_id=id)
            else:
                # No existing job found - create new continuation job
                logger.info(
                    f"📋 No existing job found for predictor_index {predictor_index}, creating new continuation job"
                )
                job_plan.append(
                    {
                        "job_type": "train_single_predictor_more",
                        "spec": training_spec,
                        "job_id": None,
                        "predictor_index": predictor_index,
                    }
                )
                session["job_plan"] = job_plan
                save_session(session_id=id, session_doc=session, exist_ok=True)
                from lib.session_chains import dispatch_next_job_in_chain

                dispatch_next_job_in_chain(session_id=id)

            # Determine message based on whether we updated existing job or created new one
            if updated_existing_job and existing_job_id:
                message = (
                    f"Existing job {existing_job_id} updated for continuation (additional {request.epochs} epochs)"
                )
            else:
                message = f"Predictor continuation training started (additional {request.epochs} epochs)"

            return JSONResponse(
                {
                    "message": message,
                    "session_id": id,
                    "predictor_path": predictor_path,
                    "predictor_index": predictor_index,
                    "target_column": target_column,
                    "target_column_type": target_column_type,
                    "additional_epochs": request.epochs,
                    "existing_job_id": existing_job_id if updated_existing_job else None,
                    "training_spec": training_spec,
                }
            )

        except Exception as e:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error starting predictor continuation")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error starting predictor continuation: {str(e)}"
            )

    @app.post("/session/{id}/train_foundation_model_more")
    async def train_foundation_model_more(id: str, request: TrainFoundationModelMoreRequest) -> JSONResponse:
        """
        Continue training an existing foundation model (embedding space) for more epochs.
        Loads the existing embedding space and resumes training from where it left off.
        """
        logger.info(f"Continuing training for foundation model on session {id} with request {request}")

        try:
            session = load_session(id)
        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for foundation model continuation")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

        # Get embedding space path - check multiple sources
        embedding_space_path = session.get("embedding_space")
        foundation_model_id = session.get("foundation_model_id")

        # If this is a predictor session, look up the foundation model's embedding space
        if not embedding_space_path and foundation_model_id:
            logger.info(f"📋 Session {id} is a predictor session based on foundation model {foundation_model_id}")
            logger.info("   Looking up foundation model session to get embedding space...")
            try:
                foundation_session = load_session(foundation_model_id)
                embedding_space_path = foundation_session.get("embedding_space")
                logger.info(f"   Found embedding space in foundation model: {embedding_space_path}")
            except FileNotFoundError:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Foundation model session {foundation_model_id} not found"
                )

        # If still no embedding space path, check if there's a train_es job and look for the output
        if not embedding_space_path or not Path(embedding_space_path).exists():
            logger.info("🔍 Embedding space path not found in session, checking for train_es job output...")
            job_plan = session.get("job_plan", [])
            train_es_job = None
            for job in job_plan:
                if job.get("job_type") == "train_es":
                    train_es_job = job
                    break

            if train_es_job:
                job_id = train_es_job.get("job_id")
                session_id = session.get("session_id", id)
                if job_id and session_id:
                    logger.info(f"   Found train_es job {job_id}, searching for embedding space in output directory...")
                    # Use get_job_output_path to find the job output directory
                    job_output_dir = get_job_output_path(job_id, session_id, "train_es")

                    # Check common locations for embedding space
                    search_paths = [
                        job_output_dir / "embedded_space.pickle",
                        job_output_dir / "embedding_space.pickle",
                        job_output_dir / "best_model_package" / "best_model.pickle",
                        job_output_dir / "best_model_package" / "embedded_space.pickle",
                        job_output_dir / "best_model_package" / "embedding_space.pickle",
                    ]

                    for search_path in search_paths:
                        if search_path.exists():
                            embedding_space_path = str(search_path.resolve())
                            logger.info(f"   ✅ Found embedding space at: {embedding_space_path}")
                            # Update session with the found path
                            session["embedding_space"] = embedding_space_path
                            save_session(id, session, exist_ok=True)
                            break

        if not embedding_space_path or not Path(embedding_space_path).exists():
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="No trained embedding space found in session. Train an embedding space first.",
            )

        logger.info(f"📂 Found embedding space at: {embedding_space_path}")

        # Load embedding space to get current training state
        try:
            es = load_embedded_space(str(embedding_space_path))
        except Exception as e:
            logger.error(f"Failed to load embedding space: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Failed to load embedding space: {str(e)}"
            )

        # Get current epoch from training info
        current_epoch = None
        if hasattr(es, "_training_timeline") and es._training_timeline:
            current_epoch = len(es._training_timeline) - 1
        elif hasattr(es, "training_info") and es.training_info:
            training_info = es.training_info
            progress_info = training_info.get("progress_info", {})
            loss_history = progress_info.get("loss_history", [])
            if loss_history:
                current_epoch = len(loss_history) - 1
            elif "epochs" in training_info:
                current_epoch = training_info.get("epochs", 0)

        if current_epoch is None:
            current_epoch = 0
            logger.warning("⚠️  Could not determine current epoch, assuming 0")

        logger.info(f"📊 Current training state: epoch {current_epoch}")
        logger.info(
            f"🔄 Will continue training for {request.data_passes} additional epochs (from epoch {current_epoch})"
        )

        # Get training parameters from existing ES or use defaults
        # Get data file path from session
        sqlite_db_path = session.get("sqlite_db")
        if sqlite_db_path and Path(sqlite_db_path).exists():
            data_file = str(Path(sqlite_db_path).resolve())
            logger.info(f"✅ Using processed SQLite database: {data_file}")
        else:
            # Try to find the original data file
            data_file = session.get("input_file")
            if not data_file or not Path(data_file).exists():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND,
                    detail="Could not find training data file. Session must have sqlite_db or input_file.",
                )
            logger.info(f"✅ Using session data file: {data_file}")

        # Get strings cache path (optional - not used anymore, just pass through)
        strings_cache = session.get("strings_cache")

        # Create training spec for continuation
        training_spec = {
            "n_epochs": request.data_passes,  # Additional epochs
            "resume_from_epoch": current_epoch,  # Resume from current epoch
            "resume_from_embedding_space": embedding_space_path,  # Path to existing ES
        }

        # Add webhooks if provided
        if request.webhooks:
            training_spec["webhooks"] = request.webhooks

        logger.info("📋 Setting up foundation model continuation...")
        logger.info(f"   Embedding space: {embedding_space_path}")
        logger.info(f"   Resume from epoch: {current_epoch}")
        logger.info(f"   Additional epochs: {request.data_passes}")

        try:
            # Find the existing train_es job in job_plan
            job_plan = session.get("job_plan", [])
            existing_job_entry = None
            existing_job_id = None
            updated_existing_job = False

            for job_entry in job_plan:
                if job_entry.get("job_type") == "train_es":
                    existing_job_entry = job_entry
                    existing_job_id = job_entry.get("job_id")
                    break

            if existing_job_entry and existing_job_id:
                # Found existing job - try to update it
                try:
                    from lib.job_manager import load_job as redis_load_job
                    existing_job = redis_load_job(existing_job_id)
                    if not existing_job:
                        raise FileNotFoundError(f"Job {existing_job_id} not found in Redis")
                    job_status = existing_job.get("status")

                    # Convert JobStatus enum to string if needed
                    if hasattr(job_status, "value"):
                        job_status = job_status.value

                    # Check if job is completed (DONE) or failed
                    if job_status in ["done", "failed"]:
                        logger.info(f"🔄 Found existing completed job {existing_job_id}, updating for continuation...")

                        # Update job spec to add continuation parameters
                        job_spec = existing_job.get("spec", {}).copy()
                        original_epochs = job_spec.get("n_epochs", 0)
                        new_total_epochs = original_epochs + request.data_passes

                        # Update spec with continuation info
                        job_spec["n_epochs"] = new_total_epochs  # Total epochs (original + additional)
                        job_spec["resume_from_epoch"] = current_epoch
                        job_spec["resume_from_embedding_space"] = embedding_space_path
                        if request.webhooks:
                            job_spec["webhooks"] = request.webhooks

                        # Reset job to READY for continuation
                        job_content = existing_job.copy()
                        job_content["status"] = JobStatus.READY.value
                        job_content["started_at"] = None
                        job_content["finished_at"] = None
                        job_content["progress"] = None
                        job_content["error_message"] = None
                        job_content["spec"] = job_spec

                        # Add continuation metadata
                        now = datetime.datetime.now(tz=ZoneInfo("America/New_York"))
                        if "recovery_info" not in job_content:
                            job_content["recovery_info"] = []
                        version_info = get_version_info()
                        job_content["recovery_info"].append(
                            {
                                "recovered_at": convert_to_iso(now),
                                "reason": "continuation_training",
                                "previous_status": job_status,
                                "original_epochs": original_epochs,
                                "additional_epochs": request.data_passes,
                                "total_epochs": new_total_epochs,
                                "webhooks": request.webhooks if request.webhooks else None,
                                "resume_from_epoch": current_epoch,
                                "version": version_info,
                            }
                        )

                        from lib.job_manager import save_job as redis_save_job
                        redis_save_job(
                            existing_job_id,
                            job_content,
                            existing_job.get("session_id", session_id),
                            "train_es"
                        )
                        updated_existing_job = True
                        logger.info(f"✅ Updated existing job {existing_job_id} for continuation")
                    else:
                        logger.warning(
                            f"⚠️  Existing job {existing_job_id} is still {job_status}, cannot update. Creating new job."
                        )
                        existing_job_id = None
                except Exception as e:
                    logger.warning(f"Failed to update existing job: {e}, creating new job")
                    existing_job_id = None

            if not updated_existing_job:
                # No existing job or couldn't update - create new continuation job
                logger.info("📋 Creating new continuation job for foundation model")
                job_plan.append(
                    {
                        "job_type": "train_es",
                        "spec": training_spec,
                        "job_id": None,
                    }
                )
                session["job_plan"] = job_plan
                save_session(session_id=id, session_doc=session, exist_ok=True)
                from lib.session_chains import dispatch_next_job_in_chain

                dispatch_next_job_in_chain(session_id=id)

            # Determine message based on whether we updated existing job or created new one
            if updated_existing_job and existing_job_id:
                message = f"Existing job {existing_job_id} updated for continuation (additional {request.data_passes} epochs from epoch {current_epoch})"
            else:
                message = f"Foundation model continuation training started (additional {request.data_passes} epochs from epoch {current_epoch})"

            return JSONResponse(
                {
                    "message": message,
                    "session_id": id,
                    "embedding_space_path": embedding_space_path,
                    "resume_from_epoch": current_epoch,
                    "additional_epochs": request.data_passes,
                    "existing_job_id": existing_job_id if updated_existing_job else None,
                    "training_spec": training_spec,
                }
            )

        except Exception as e:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error starting foundation model continuation")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error starting foundation model continuation: {str(e)}",
            )

    @app.post("/compute/train_on_foundational_model")
    async def train_on_foundational_model(
        request: Request,  # CRITICAL: Need Request object to access headers
        foundation_model_id: str = Form(...),
        target_column: str = Form(...),
        target_column_type: str = Form(...),
        file: Optional[UploadFile] = File(None),
        input_filename: Optional[str] = Form(None),
        name: Optional[str] = Form(None),
        session_name_prefix: Optional[str] = Form(None),
        epochs: int = Form(0),
        batch_size: int = Form(0),
        learning_rate: Optional[float] = Form(None),  # None = auto-select based on fine_tune
        rare_label_value: Optional[str] = Form(None),
        class_imbalance: Optional[str] = Form(None),  # JSON string
        use_class_weights: bool = Form(True),
        optimize_for: Optional[str] = Form(None),  # DEPRECATED: Ignored, kept for backward compatibility
        webhooks: Optional[str] = Form(None),  # JSON string
        user_metadata: Optional[str] = Form(None),  # JSON string
    ) -> JSONResponse:
        """
        Train a single predictor on a foundation model (existing embedding space).

        Creates a new session that uses the foundation model's embedding space and trains
        a predictor for the specified target column. The foundation model's embedding space
        and strings cache are reused, so no ES training is needed.
        """
        from uuid import uuid4
        from lib.session_chains import dispatch_next_job_in_chain

        # Log all request details for debugging intermittent 404s
        logger.info("=" * 80)
        logger.info("🔵 /compute/train_on_foundational_model CALLED")
        logger.info(f"   Method: {request.method}")
        logger.info(f"   URL: {request.url}")
        logger.info(f"   Client: {request.client.host if request.client else 'unknown'}")
        logger.info(f"   Headers: {dict(request.headers)}")
        logger.info(f"   Foundation model: {foundation_model_id}")
        logger.info(f"   Target column: {target_column} ({target_column_type})")
        logger.info(f"   Has file: {file is not None}")
        logger.info(f"   Input filename: {input_filename}")
        logger.info("=" * 80)

        logger.info(f"Training predictor on foundation model {foundation_model_id} with target: {target_column}")

        # CRITICAL: Check if client requested specific compute node via X-Featrix-Node header
        # If so, verify this IS that node, otherwise return error
        current_node = socket.gethostname()
        requested_node = request.headers.get('X-Featrix-Node') or request.headers.get('x-featrix-node')
        
        if requested_node and requested_node != current_node:
            error_msg = (
                f"Cannot create session on {current_node} - client requested {requested_node}. "
                f"Foundation model must be on {requested_node} or client must not specify compute node."
            )
            logger.warning(f"⚠️  Compute node mismatch: requested={requested_node}, current={current_node}")
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=error_msg
            )
        
        logger.info(f"📍 Creating session on {current_node}" + (f" (as requested by client)" if requested_node else " (no node preference specified)"))

        # Validate request parameters
        if target_column_type not in ["set", "scalar"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="target_column_type must be 'set' or 'scalar'"
            )

        # Parse JSON strings
        import json

        class_imbalance_dict = None
        if class_imbalance:
            try:
                class_imbalance_dict = json.loads(class_imbalance)
            except json.JSONDecodeError:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="class_imbalance must be valid JSON")

        webhooks_dict = None
        if webhooks:
            try:
                webhooks_dict = json.loads(webhooks)
            except json.JSONDecodeError:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="webhooks must be valid JSON")

        user_metadata_dict = None
        if user_metadata:
            try:
                user_metadata_dict = json.loads(user_metadata)
                logger.info(f"User metadata received: {len(str(user_metadata_dict))} chars")
            except json.JSONDecodeError:
                logger.warning(f"Invalid user_metadata JSON: {user_metadata}")
                user_metadata_dict = None

        try:
            # Handle file upload if provided
            final_input_filename = input_filename
            if file:
                import shutil
                from uuid import uuid4

                # Save uploaded file to data directory
                data_dir = config.data_dir
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = Path(file.filename).suffix
                saved_filename = f"{str(uuid4())}{file_ext}"
                file_path = data_dir / saved_filename

                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                logger.info(f"✅ Saved uploaded file to: {file_path}")
                final_input_filename = saved_filename

            # Validate input file exists if provided
            if final_input_filename:

                data_dir = config.data_dir


                # Check if it's an absolute path or relative
                input_path = Path(final_input_filename)
                if input_path.is_absolute():
                    if input_path.exists():
                        # Absolute path exists - use it directly
                        logger.info(f"✅ Using absolute path for input file: {input_path}")
                        # Normalize to use the absolute path
                        final_input_filename = str(input_path.resolve())
                    else:
                        # Absolute path doesn't exist - try extracting filename and checking data directory
                        filename_only = input_path.name
                        logger.warning(f"⚠️  Absolute path not found: {input_path}")
                        logger.info(f"   Trying filename in data directory: {filename_only}")

                        data_file = data_dir / filename_only
                        if data_file.exists():
                            logger.info(f"✅ Found file in data directory: {data_file}")
                            final_input_filename = filename_only
                        else:
                            raise HTTPException(
                                status_code=HTTPStatus.BAD_REQUEST,
                                detail=f"Input file not found. Tried absolute path '{input_path}' and data directory '{data_file}'. Please upload the file first using the upload endpoint.",
                            )
                else:
                    # Relative path - check in data directory
                    data_file = data_dir / final_input_filename
                    if not data_file.exists():
                        raise HTTPException(
                            status_code=HTTPStatus.BAD_REQUEST,
                            detail=f"Input file not found: {final_input_filename}. The file must exist in the data directory ({data_dir}) before creating the session. Please upload the file first.",
                        )
                    logger.info(f"✅ Verified input file exists: {data_file}")

            # Generate new session ID
            created_at = datetime.datetime.now(tz=ZoneInfo("America/New_York"))
            full_uuid = str(uuid4())

            # Handle session_name_prefix if provided
            if session_name_prefix:
                # Sanitize prefix: replace slashes and dots with underscores
                sanitized_prefix = session_name_prefix.replace("/", "_").replace(".", "_")
                # Format as <prefix>-<full-uuid>
                new_session_id = f"{sanitized_prefix}-{full_uuid}"
                logger.info(f"📋 Created session_id with prefix: {new_session_id}")
            else:
                # When no prefix, use full UUID to satisfy validation requirements
                # The validation expects format with UUID suffix, so we use full UUID
                new_session_id = full_uuid
                logger.info(f"📋 Created session_id without prefix (full UUID): {new_session_id}")

            # Build target_spec from form data
            target_spec = {
                "target_column": target_column,
                "target_column_type": target_column_type,
                "n_epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "positive_label": rare_label_value,  # Map rare_label_value to internal positive_label parameter
                "use_class_weights": use_class_weights,
                "class_imbalance": class_imbalance_dict,
                "webhooks": webhooks_dict,
            }

            # Create the foundation model session
            session = create_foundation_model_session(
                session_id=new_session_id,
                created_at=created_at,
                foundation_model_id=foundation_model_id,
                target_spec=target_spec,
                input_filename=final_input_filename,
                name=name,
                user_metadata=user_metadata_dict,
            )

            # Save the session
            save_session(session_id=new_session_id, session_doc=session, exist_ok=False)

            # Step the session to start processing
            from lib.session_chains import dispatch_next_job_in_chain

            dispatch_next_job_in_chain(session_id=new_session_id)

            logger.info(f"✅ Created predictor session {new_session_id} on foundation model {foundation_model_id}")

            # Get compute cluster from session (shows which node created it)
            compute_cluster = session.get("compute_cluster", socket.gethostname())
            
            serialized_session = serialize_session(session)
            return JSONResponse(
                {
                    "message": f"Predictor training started on foundation model {foundation_model_id}",
                    "session_id": new_session_id,
                    "foundation_model_id": foundation_model_id,
                    "target_column": target_column,
                    "target_column_type": target_column_type,
                    "compute_cluster": compute_cluster,  # CRITICAL: Tell client which node created it
                    "session": serialized_session,
                }
            )

        except FileNotFoundError as e:
            logger.error("=" * 80)
            logger.error("🔴 train_on_foundational_model - FileNotFoundError (404)")
            logger.error(f"   Foundation model: {foundation_model_id}")
            logger.error(f"   Target: {target_column} ({target_column_type})")
            logger.error(f"   Error: {e}")
            logger.error("=" * 80)
            if "foundation model" in str(e).lower() or "session" in str(e).lower():
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Foundation model not found: {foundation_model_id}"
                )
            raise
        except ValueError as e:
            logger.error("=" * 80)
            logger.error("🔴 train_on_foundational_model - ValueError (400)")
            logger.error(f"   Foundation model: {foundation_model_id}")
            logger.error(f"   Target: {target_column} ({target_column_type})")
            logger.error(f"   ValueError: {e}")
            logger.error("=" * 80)
            logger.exception(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e)
            if not error_msg:
                error_msg = f"Unknown error: {type(e).__name__}"
            logger.error("=" * 80)
            logger.error("🔴 train_on_foundational_model - Exception (500)")
            logger.error(f"   Foundation model: {foundation_model_id}")
            logger.error(f"   Target: {target_column} ({target_column_type})")
            logger.error(f"   Exception type: {type(e).__name__}")
            logger.error(f"   Exception message: {error_msg}")
            logger.error("=" * 80)
            traceback.print_exc()
            post_slack_alert(
                f"foundation_model={foundation_model_id}; error starting predictor training on foundation model: {error_msg}"
            )
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error starting predictor training on foundation model: {error_msg}",
            )

    @app.post("/session/{id}/dump-to-backplane")
    async def dump_session_to_backplane(id: str) -> JSONResponse:
        """
        Dispatch a Celery task to copy a session's workspace to /backplane/backplane1.

        This task:
        1. Verifies /backplane/backplane1 is mounted and different from /backplane
        2. Rsyncs the session workspace to the backplane
        3. Creates a LAST_HOST_DUMP.json marker file with metadata

        Args:
            id: Session ID to dump

        Returns:
            dict with task_id for polling
        """
        try:
            from celery_app import dump_to_backplane

            # Verify session exists
            session = load_session(id)

            # Dispatch Celery task
            task = dump_to_backplane.delay(id)

            logger.info(f"✅ Dispatched dump_to_backplane task for session {id} (task_id: {task.id})")

            return JSONResponse(
                {
                    "task_id": task.id,
                    "status": "submitted",
                    "session_id": id,
                    "message": f"Dump task submitted for session {id}",
                }
            )

        except FileNotFoundError:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Session not found: {id}")
        except ImportError as e:
            logger.error(f"❌ Celery not available: {e}")
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="Celery service not available - dump_to_backplane requires Celery",
            )
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e)
            logger.error(f"❌ DUMP_TO_BACKPLANE - Exception: {error_msg}")
            logger.exception(e)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error dispatching dump task: {error_msg}"
            )

    @app.post("/compute/session/{id}/mark_for_deletion")
    async def mark_session_for_deletion(id: str) -> JSONResponse:
        """
        Mark a session for deletion. Creates a DELETEME file that the garbage collection process will pick up.

        Args:
            id: Session ID to mark for deletion
        """
        logger.info(f"Marking session {id} for deletion")

        try:
            # Verify session exists
            session = load_session(id)

            # Create DELETEME file in session directory
            session_dir = config.session_dir
            deleteme_path = session_dir / f"{id}.DELETEME"
            
            # Save directory's original mtime before modifying it
            # This preserves ls -lrt sorting in featrix_sessions/
            import os
            try:
                dir_stat = session_dir.stat()
                original_atime = dir_stat.st_atime
                original_mtime = dir_stat.st_mtime
            except Exception as e:
                logger.warning(f"Could not read dir times for {session_dir}: {e}")
                original_atime = None
                original_mtime = None

            # Create DELETEME file with metadata
            deleteme_data = {
                "session_id": id,
                "marked_at": datetime.datetime.now().isoformat(),
                "marked_unix_time": time.time(),
                "marked_by": "api",
            }

            with open(deleteme_path, "w") as f:
                json.dump(deleteme_data, f, indent=2)
            
            # Restore directory's original mtime so ls -lrt still works
            if original_atime is not None and original_mtime is not None:
                os.utime(session_dir, (original_atime, original_mtime))

            logger.info(f"✅ Marked session {id} for deletion (DELETEME file created)")

            return JSONResponse(
                {
                    "status": "marked",
                    "session_id": id,
                    "message": "Session marked for deletion. Will be deleted by garbage collection process.",
                }
            )

        except FileNotFoundError:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Session {id} not found")
        except Exception as e:
            logger.error(f"Error marking session {id} for deletion: {e}", exc_info=True)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error marking session for deletion: {str(e)}"
            )

    @app.delete("/session/{id}/predictor")
    async def remove_predictor_from_session(
        id: str,
        target_column: str = Query(None, description="Target column of predictor to remove"),
        predictor_id: str = Query(None, description="Predictor ID to remove"),
    ) -> JSONResponse:
        """
        Remove a predictor from a session by target_column or predictor_id.

        Args:
            id: Session ID
            target_column: Target column of the predictor to remove (optional)
            predictor_id: Predictor ID to remove (optional)

        At least one of target_column or predictor_id must be provided.
        """
        logger.info(
            f"Removing predictor from session {id} (target_column={target_column}, predictor_id={predictor_id})"
        )

        if not target_column and not predictor_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="Either target_column or predictor_id must be provided"
            )

        try:
            session = load_session(id)
        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for predictor removal")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

        try:
            import os

            # Get predictor lists
            single_predictors = session.get("single_predictors", [])
            training_metrics = session.get("training_metrics", [])
            job_plan = session.get("job_plan", [])

            if not single_predictors:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No predictors found in this session")

            # Helper to generate predictor ID from path
            def generate_predictor_id(predictor_path: str) -> str:
                if not predictor_path:
                    return None
                try:
                    import hashlib

                    # Extract meaningful part from path
                    path_obj = Path(predictor_path)
                    filename = path_obj.name
                    # Generate short hash
                    hash_obj = hashlib.sha256(predictor_path.encode())
                    short_hash = hash_obj.hexdigest()[:8]
                    return f"sp-{short_hash}"
                except:
                    return None

            # Find the predictor index to remove
            predictor_index_to_remove = None
            removed_predictor_info = None

            for idx, predictor_path in enumerate(single_predictors):
                if predictor_path is None:
                    continue

                # Get predictor metadata if available
                tm = training_metrics[idx] if idx < len(training_metrics) and training_metrics[idx] else {}
                pred_target_column = tm.get("target_column") if isinstance(tm, dict) else None
                pred_id = generate_predictor_id(predictor_path)

                # Match by predictor_id or target_column
                match_by_id = predictor_id and pred_id == predictor_id
                match_by_target = target_column and pred_target_column == target_column

                if match_by_id or match_by_target:
                    predictor_index_to_remove = idx
                    removed_predictor_info = {
                        "predictor_index": idx,
                        "predictor_id": pred_id,
                        "target_column": pred_target_column,
                        "path": predictor_path,
                    }
                    logger.info(f"🎯 Found predictor to remove at index {idx}: {removed_predictor_info}")
                    break

            if predictor_index_to_remove is None:
                search_criteria = (
                    f"predictor_id='{predictor_id}'" if predictor_id else f"target_column='{target_column}'"
                )
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"No predictor found matching {search_criteria}"
                )

            # Remove the predictor from arrays
            logger.info(f"🗑️  Removing predictor at index {predictor_index_to_remove}")

            # Delete predictor file if it exists
            predictor_path = single_predictors[predictor_index_to_remove]
            if predictor_path and os.path.exists(predictor_path):
                try:
                    os.remove(predictor_path)
                    logger.info(f"✅ Deleted predictor file: {predictor_path}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not delete predictor file {predictor_path}: {e}")

            # Remove from arrays (don't reindex, just set to None to preserve indices)
            single_predictors[predictor_index_to_remove] = None
            if predictor_index_to_remove < len(training_metrics):
                training_metrics[predictor_index_to_remove] = None

            # Remove corresponding job from job_plan
            updated_job_plan = []
            for job in job_plan:
                if (
                    job.get("job_type") == "train_single_predictor"
                    and job.get("predictor_index") == predictor_index_to_remove
                ):
                    logger.info(f"🗑️  Removing job from job_plan: {job.get('job_id')}")
                    continue
                updated_job_plan.append(job)

            # Update session
            session["single_predictors"] = single_predictors
            session["training_metrics"] = training_metrics
            session["job_plan"] = updated_job_plan

            # Save updated session
            save_session(session_id=id, session_doc=session, exist_ok=True)
            logger.info("✅ Predictor removed and session saved")

            return JSONResponse(
                {
                    "message": "Predictor removed successfully",
                    "session_id": id,
                    "removed_predictor": removed_predictor_info,
                    "remaining_predictors": len([p for p in single_predictors if p is not None]),
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            traceback.print_exc()
            post_slack_alert(f"session={id}; error removing predictor")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error removing predictor: {str(e)}"
            )

    @app.post("/session/{id}/train_predictor_with_file")
    async def train_single_predictor_with_custom_file(
        id: str,
        file: UploadFile = File(...),
        target_column: str = Form(...),
        target_column_type: str = Form(...),
        epochs: int = Form(0),
        batch_size: int = Form(0),
        learning_rate: Optional[float] = Form(None),  # None = auto-select based on fine_tune
        rare_label_value: Optional[str] = Form(None),
        class_imbalance: Optional[str] = Form(None),  # JSON string of class ratios/counts
        optimize_for: Optional[str] = Form(None),  # DEPRECATED: Ignored, kept for backward compatibility
        webhooks: Optional[str] = Form(None),  # JSON string of webhook configuration
    ) -> JSONResponse:
        """
        Train a single predictor using a custom training file.
        This allows training predictors on different data than the embedding space was trained on.
        """
        logger.info(f"Training single predictor on session {id} with custom file: {file.filename}")

        try:
            session = load_session(id)
        except FileNotFoundError:
            post_slack_alert(f"session={id}; session not found for predictor training with custom file")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

        # Check if there's an ES job in the session - predictor can be queued even if ES is still training
        logger.info("🔍 Checking if session has ES training in job plan...")
        embedding_space_path = session.get("embedding_space")
        job_plan = session.get("job_plan", [])
        has_es_job = any(job.get("job_type") == "train_es" for job in job_plan)

        if not has_es_job and (not embedding_space_path or not Path(embedding_space_path).exists()):
            # No ES job in plan and no existing embedding space - can't train predictor
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="No embedding space found or planned. Train an embedding space first before training a predictor.",
            )

        if embedding_space_path and Path(embedding_space_path).exists():
            logger.info(f"✅ Embedding space found: {embedding_space_path}")
        else:
            logger.info("⏳ Embedding space not ready yet - predictor will wait in queue for ES training to complete")

        # Validate request parameters
        if target_column_type not in ["set", "scalar"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="target_column_type must be 'set' or 'scalar'"
            )

        try:
            import shutil

            from lib.session_chains import dispatch_next_job_in_chain

            # Save the uploaded file to a temporary location in the session directory
            session_dir = Path(config.session_dir) / id
            custom_data_dir = session_dir / "custom_predictor_data"
            custom_data_dir.mkdir(exist_ok=True, parents=True)

            # Generate unique filename for this predictor training file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file.filename).suffix
            custom_file_path = custom_data_dir / f"predictor_train_{timestamp}{file_ext}"

            # Save the uploaded file
            with custom_file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"✅ Saved custom training file to: {custom_file_path}")

            # Parse class_imbalance if provided (comes as JSON string from Form)
            class_imbalance_dict = None
            if class_imbalance:
                try:
                    import json

                    class_imbalance_dict = json.loads(class_imbalance)
                    logger.info(f"📊 Parsed class_imbalance: {class_imbalance_dict}")
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️  Failed to parse class_imbalance JSON: {e}")
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid class_imbalance JSON format: {e}"
                    )

            # Parse webhooks if provided (comes as JSON string from Form)
            webhooks_dict = None
            if webhooks:
                try:
                    import json

                    webhooks_dict = json.loads(webhooks)
                    logger.info(f"📊 Parsed webhooks: {webhooks_dict}")
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️  Failed to parse webhooks JSON: {e}")
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid webhooks JSON format: {e}")

            # Create the training spec for the single predictor
            training_spec = {
                "target_column": target_column,
                "target_column_type": target_column_type,
                "n_epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "positive_label": rare_label_value,  # Map rare_label_value to internal positive_label parameter
                "class_imbalance": class_imbalance_dict,  # Pass expected class ratios/counts from real world
                "custom_training_file": str(custom_file_path),  # Store path to custom file
                "webhooks": webhooks_dict,  # Pass webhook configuration
            }

            # Add the single predictor job to the session's job plan
            job_plan = session.get("job_plan", [])

            # Count existing single predictor jobs to assign predictor_index
            existing_predictors = [job for job in job_plan if job.get("job_type") == "train_single_predictor"]
            predictor_index = len(existing_predictors)

            # Add new single predictor job with custom file
            job_plan.append(
                {
                    "job_type": "train_single_predictor",
                    "spec": training_spec,
                    "job_id": None,
                    "predictor_index": predictor_index,
                }
            )
            session["job_plan"] = job_plan

            # Save the updated session
            save_session(session_id=id, session_doc=session, exist_ok=True)

            # Dispatch the training job (Celery will handle chaining automatically)
            dispatch_next_job_in_chain(session_id=id)

            return JSONResponse(
                {
                    "message": f"Single predictor #{predictor_index + 1} training added with custom file (targeting '{target_column}')",
                    "session_id": id,
                    "target_column": target_column,
                    "target_column_type": target_column_type,
                    "predictor_index": predictor_index,
                    "training_spec": training_spec,
                    "custom_file": str(custom_file_path),
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error training single predictor with custom file: {e}")
            traceback.print_exc()
            post_slack_alert(f"session={id}; error training single predictor with custom file: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error training single predictor with custom file: {str(e)}",
            )
    
    @app.post("/session/{id}/train_on_partial_foundation")
    async def train_on_partial_foundation(
        id: str,
        file: UploadFile = File(...),
        checkpoint_epoch: Optional[int] = Form(None),
        target_column: str = Form(...),
        target_column_type: str = Form(...),
        epochs: int = Form(0),
        rare_label_value: Optional[str] = Form(None),
        use_class_weights: bool = Form(True),
        class_imbalance: Optional[str] = Form(None),
        cost_false_positive: Optional[float] = Form(None),
        cost_false_negative: Optional[float] = Form(None),
        name: Optional[str] = Form(None),
        session_name_prefix: Optional[str] = Form(None),
        webhooks: Optional[str] = Form(None),
    ) -> JSONResponse:
        """
        Train a predictor on a partial/in-progress foundation model.
        
        Designed for use while the foundation model is STILL TRAINING, allowing you to
        test predictor performance on intermediate checkpoints without waiting for full
        training to complete. Also works with completed training.
        
        Creates a NEW session using:
        - A checkpoint from the foundation's ES training (specific epoch or best/latest)
        - Your uploaded data file (for predictor training)
        - Metadata about foundation training progress when checkpoint was created
        
        Args:
            id: Foundation session ID (with ES training job)
            file: CSV file to upload for predictor training
            checkpoint_epoch: Which epoch checkpoint to use (None = best/latest available)
            target_column: Column to predict
            target_column_type: "set" or "scalar"
            epochs: Predictor training epochs (0 = auto-calculate)
        
        Returns:
            New session ID, checkpoint metadata, training progress info
        """
        logger.info(f"Training on partial foundation {id}, file: {file.filename}, epoch: {checkpoint_epoch}")
        
        try:
            # Load foundation session
            foundation_session = load_session(id)
            
            # Find the ES training job directory
            job_plan = foundation_session.get("job_plan", [])
            es_job = next((j for j in job_plan if j.get("job_type") == "train_es"), None)
            
            if not es_job:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Foundation session {id} has no ES training job"
                )
            
            es_job_id = es_job.get("job_id")
            if not es_job_id:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Foundation session ES job has no job_id"
                )
            
            # Find checkpoint file
            from lib.job_manager import get_job_output_path
            es_job_dir = get_job_output_path(es_job_id, session_id=id, job_type="train_es")
            
            checkpoint_path = None
            checkpoint_epoch_used = None
            
            if checkpoint_epoch is not None:
                # Use specific epoch checkpoint
                checkpoint_path = es_job_dir / f"checkpoint_inference_e-{checkpoint_epoch}.pt"
                if not checkpoint_path.exists():
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Checkpoint for epoch {checkpoint_epoch} not found: {checkpoint_path}"
                    )
                checkpoint_epoch_used = checkpoint_epoch
                logger.info(f"✅ Using epoch {checkpoint_epoch} checkpoint: {checkpoint_path}")
            else:
                # Find best checkpoint or latest
                best_checkpoint = es_job_dir / "checkpoint_inference_BEST.pt"
                if best_checkpoint.exists():
                    checkpoint_path = best_checkpoint
                    # Try to extract epoch from checkpoint
                    try:
                        import torch
                        ckpt = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu')
                        checkpoint_epoch_used = ckpt.get('epoch_idx') or ckpt.get('epoch', 0)
                    except:
                        checkpoint_epoch_used = 0
                    logger.info(f"✅ Using BEST checkpoint (epoch {checkpoint_epoch_used}): {checkpoint_path}")
                else:
                    # Find latest epoch checkpoint
                    epoch_checkpoints = sorted(es_job_dir.glob("checkpoint_inference_e-*.pt"))
                    if not epoch_checkpoints:
                        raise HTTPException(
                            status_code=HTTPStatus.NOT_FOUND,
                            detail=f"No checkpoints found in {es_job_dir}"
                        )
                    checkpoint_path = epoch_checkpoints[-1]
                    # Extract epoch from filename
                    import re
                    match = re.search(r'e-(\d+)\.pt', checkpoint_path.name)
                    checkpoint_epoch_used = int(match.group(1)) if match else 0
                    logger.info(f"✅ Using latest checkpoint (epoch {checkpoint_epoch_used}): {checkpoint_path}")
            
            # Save uploaded file to temp location
            import shutil
            temp_dir = Path(config.data_dir) / "checkpoint_training_uploads"
            temp_dir.mkdir(exist_ok=True, parents=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file.filename).suffix
            temp_file_path = temp_dir / f"train_on_checkpoint_{timestamp}{file_ext}"
            
            with temp_file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"✅ Saved uploaded data to: {temp_file_path}")
            
            # Parse class_imbalance if provided
            class_imbalance_dict = None
            if class_imbalance:
                try:
                    import json
                    class_imbalance_dict = json.loads(class_imbalance)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse class_imbalance JSON: {e}")
            
            # Parse webhooks if provided
            webhooks_dict = None
            if webhooks:
                try:
                    import json
                    webhooks_dict = json.loads(webhooks)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse webhooks JSON: {e}")
            
            # Create NEW session with the checkpoint as its embedding space
            from lib.session_manager import create_session
            import uuid
            
            new_session_name = name or f"Checkpoint-epoch-{checkpoint_epoch_used}-from-{id[:8]}"
            
            # Generate session ID with optional prefix
            if session_name_prefix:
                new_session_id = f"{session_name_prefix}-{uuid.uuid4()}"
            else:
                new_session_id = str(uuid.uuid4())
            
            logger.info(f"📝 Creating new session {new_session_id} from checkpoint...")
            
            new_session = create_session(
                input_filename=str(temp_file_path),
                session_id=new_session_id,
                session_type="predictor_only",
                name=new_session_name,
                user_metadata=foundation_session.get('user_metadata')
            )
            
            # Store reference to foundation session and checkpoint info
            # Also store metadata about foundation training progress
            new_session['foundation_session_id'] = id
            new_session['checkpoint_epoch'] = checkpoint_epoch_used
            new_session['checkpoint_path'] = str(checkpoint_path)
            
            # Extract foundation training progress metadata from checkpoint
            foundation_training_metadata = {
                'checkpoint_epoch': checkpoint_epoch_used,
                'foundation_session_id': id,
                'foundation_session_name': foundation_session.get('name'),
                'checkpoint_created_at': datetime.datetime.now().isoformat(),
            }
            
            # Try to get training progress info from checkpoint
            try:
                import torch
                ckpt_data = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu')
                
                # Extract training metrics if available
                if 'validation_loss' in ckpt_data:
                    foundation_training_metadata['validation_loss_at_checkpoint'] = float(ckpt_data['validation_loss'])
                if 'training_loss' in ckpt_data:
                    foundation_training_metadata['training_loss_at_checkpoint'] = float(ckpt_data['training_loss'])
                if 'epoch_idx' in ckpt_data:
                    foundation_training_metadata['checkpoint_epoch'] = int(ckpt_data['epoch_idx'])
                
                # Get total epochs planned for foundation
                foundation_n_epochs = foundation_session.get('n_epochs')
                if foundation_n_epochs and checkpoint_epoch_used:
                    progress_pct = (checkpoint_epoch_used / foundation_n_epochs) * 100
                    foundation_training_metadata['foundation_total_epochs'] = foundation_n_epochs
                    foundation_training_metadata['training_progress_percent'] = round(progress_pct, 1)
                    foundation_training_metadata['foundation_training_complete'] = checkpoint_epoch_used >= foundation_n_epochs
                
                logger.info(f"📊 Foundation training progress: {foundation_training_metadata.get('training_progress_percent', 'unknown')}%")
                
            except Exception as e:
                logger.warning(f"Could not extract training metadata from checkpoint: {e}")
            
            new_session['foundation_training_metadata'] = foundation_training_metadata
            
            # Reconstruct ES from checkpoint and save as the session's embedding space
            from lib.featrix.neural.io_utils import _reconstruct_es_from_checkpoint_dict
            import torch
            
            logger.info(f"🔄 Reconstructing ES from checkpoint...")
            checkpoint_dict = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
            es = _reconstruct_es_from_checkpoint_dict(checkpoint_dict, str(es_job_dir), logger=logger)
            
            if not es:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Failed to reconstruct embedding space from checkpoint"
                )
            
            # Save the reconstructed ES to the new session
            session_dir = Path(config.session_dir) / new_session_id
            session_dir.mkdir(exist_ok=True, parents=True)
            es_pickle_path = session_dir / get_embedding_space_pickle_filename()
            
            # Use write_embedding_space_pickle for proper saving
            write_embedding_space_pickle(es, str(session_dir), filename=get_embedding_space_pickle_filename(), show_progress=False)
            es_pickle_path = session_dir / get_embedding_space_pickle_filename()
            
            logger.info(f"✅ Saved reconstructed ES to: {es_pickle_path}")
            
            new_session['embedding_space'] = str(es_pickle_path)
            
            # Add predictor training job to job plan
            training_spec = {
                "target_column": target_column,
                "target_column_type": target_column_type,
                "n_epochs": epochs,
                "batch_size": 0,  # Auto-calculate
                "positive_label": rare_label_value,
                "use_class_weights": use_class_weights,
                "class_imbalance": class_imbalance_dict,
                "webhooks": webhooks_dict,
            }
            
            if cost_false_positive is not None and cost_false_negative is not None:
                training_spec["cost_false_positive"] = cost_false_positive
                training_spec["cost_false_negative"] = cost_false_negative
            
            new_session["job_plan"] = [
                {
                    "job_type": "train_single_predictor",
                    "spec": training_spec,
                    "job_id": None,
                    "predictor_index": 0,
                }
            ]
            
            # Save the new session
            save_session(session_id=new_session_id, session_doc=new_session, exist_ok=True)
            
            # Dispatch the predictor training job
            from lib.session_chains import dispatch_next_job_in_chain
            dispatch_next_job_in_chain(session_id=new_session_id)
            
            logger.info(f"✅ Created session {new_session_id} and dispatched predictor training")
            
            return JSONResponse(
                {
                    "message": f"Predictor training started on partial foundation (epoch {checkpoint_epoch_used})",
                    "new_session_id": new_session_id,
                    "foundation_session_id": id,
                    "checkpoint_epoch": checkpoint_epoch_used,
                    "target_column": target_column,
                    "predictor_epochs": epochs,
                    "foundation_training_metadata": foundation_training_metadata,
                },
                status_code=HTTPStatus.ACCEPTED,
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error training on checkpoint from session {id}: {e}", exc_info=True)
            post_slack_alert(f"session={id}; error training on checkpoint: {str(e)}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error training on checkpoint: {str(e)}",
            )

    @app.post("/session/{id}/clone_embedding_space")
    async def clone_embedding_space(id: str, request: CloneEmbeddingSpaceRequest) -> JSONResponse:
        """
        Clone embedding space from this node to another compute node.

        This endpoint:
        1. Loads the session and embedding space
        2. Validates ES selection (single vs multiple)
        3. Extracts training metadata
        4. Chunks files (ES pickle and strings cache) into 512MB segments
        5. Uploads chunks to destination node
        """
        import hashlib

        import requests as req_lib

        try:
            # Load session
            session = load_session(id)

            # Get destination node - auto-select if not provided
            to_compute = request.to_compute
            if not to_compute:
                # Find an available compute node
                recommended_host = recommend_host()
                if not recommended_host:
                    raise HTTPException(
                        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                        detail="No available compute nodes found. Please try again later.",
                    )
                to_compute = recommended_host
                logger.info(f"Auto-selected destination node: {to_compute}")

            # Get destination node URL
            to_compute_url = request.to_compute_url
            if not to_compute_url:
                # Look up from COMPUTE_NODES
                to_compute_url = COMPUTE_NODES.get(to_compute)
                if not to_compute_url:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f"Unknown destination node: {to_compute}. Available nodes: {list(COMPUTE_NODES.keys())}",
                    )

            # ES Selection Logic
            embedding_space_path = session.get("embedding_space")

            # Check if session has multiple ES (for future support)
            # For now, assume single ES unless we have a list/array
            if isinstance(embedding_space_path, list) or isinstance(embedding_space_path, dict):
                # Multiple ES found
                if not request.es_id:
                    available_es_ids = (
                        list(embedding_space_path.keys())
                        if isinstance(embedding_space_path, dict)
                        else [f"es_{i}" for i in range(len(embedding_space_path))]
                    )
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f"Session has multiple embedding spaces. Please specify es_id. Available: {available_es_ids}",
                    )
                # Find specific ES
                if isinstance(embedding_space_path, dict):
                    embedding_space_path = embedding_space_path.get(request.es_id)
                else:
                    # List - find by index or ID
                    try:
                        es_index = int(request.es_id.replace("es_", ""))
                        embedding_space_path = embedding_space_path[es_index]
                    except (ValueError, IndexError):
                        raise HTTPException(
                            status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid es_id: {request.es_id}"
                        )

            resolved_es_path = resolve_embedding_space_path(embedding_space_path) if embedding_space_path else None
            if not resolved_es_path:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Embedding space not found: {embedding_space_path}"
                )

            # Load embedding space to extract metadata
            logger.info(f"Loading embedding space from {embedding_space_path}")
            es = load_embedded_space(embedding_space_path)

            # Extract training metadata
            training_info = getattr(es, "training_info", {})
            progress_info = training_info.get("progress_info", {})

            # Get current validation loss and epoch
            current_validation_loss = None
            current_epoch = None

            # Try to get from training_info first
            if hasattr(es, "training_info"):
                d = training_info.get("progress_info", {})
                current_validation_loss = d.get("current_validation_loss")
                # Get epoch from timeline or training_info
                if hasattr(es, "_training_timeline") and es._training_timeline:
                    current_epoch = len(es._training_timeline) - 1
                elif "epochs" in training_info:
                    current_epoch = training_info.get("epochs", 0)

            # Fallback: try to get from history_db if available
            if current_validation_loss is None and hasattr(es, "history_db") and es.history_db:
                try:
                    loss_history = es.history_db.get_all_loss_history()
                    if loss_history:
                        last_entry = loss_history[-1]
                        current_validation_loss = last_entry.get("validation_loss")
                        current_epoch = last_entry.get("epoch", len(loss_history) - 1)
                except Exception as e:
                    logger.warning(f"Could not get validation loss from history_db: {e}")

            # Prepare training metadata
            training_metadata = {
                "training_info": training_info,
                "d_model": getattr(es, "d_model", None),
                "name": getattr(es, "name", None),
            }

            # Get strings cache path
            strings_cache_path = session.get("strings_cache")
            if not strings_cache_path or not Path(strings_cache_path).exists():
                # Try to find strings.sqlite3 in session directory
                session_dir = Path(config.session_dir) / f"{id}.session"
                if session_dir.parent.exists():
                    # Look for strings.sqlite3 in common locations
                    possible_paths = [
                        session_dir.parent / "strings.sqlite3",
                        Path(embedding_space_path).parent / "strings.sqlite3",
                    ]
                    for path in possible_paths:
                        if path.exists():
                            strings_cache_path = str(path)
                            break

            # Chunk and upload files
            CHUNK_SIZE = 512 * 1024 * 1024  # 512MB

            files_to_upload = [
                ("es_pickle", embedding_space_path),
                ("strings_cache", strings_cache_path)
                if strings_cache_path and Path(strings_cache_path).exists()
                else None,
            ]
            files_to_upload = [f for f in files_to_upload if f is not None]

            # Upload each file in chunks
            for file_type, file_path in files_to_upload:
                if not file_path or not Path(file_path).exists():
                    logger.warning(f"File {file_type} not found: {file_path}, skipping")
                    continue

                file_size = Path(file_path).stat().st_size
                total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

                logger.info(f"Uploading {file_type} ({file_size / (1024**2):.1f} MB) in {total_chunks} chunks")
                # Don't expose chunk details to caller - this is implementation detail

                with open(file_path, "rb") as f:
                    for chunk_index in range(total_chunks):
                        chunk_data = f.read(CHUNK_SIZE)
                        if not chunk_data:
                            break

                        # Calculate checksum
                        chunk_checksum = hashlib.sha256(chunk_data).hexdigest()

                        # Prepare form data
                        form_data = {
                            "chunk_index": str(chunk_index),
                            "total_chunks": str(total_chunks),
                            "file_type": file_type,
                            "chunk_checksum": chunk_checksum,
                            "source_session_id": id,
                            "source_compute": get_compute_cluster_name(),
                            "validation_loss": str(current_validation_loss)
                            if current_validation_loss is not None
                            else "",
                            "epoch": str(current_epoch) if current_epoch is not None else "",
                            "training_metadata": json.dumps(training_metadata),
                            "new_session_name": request.new_session_name or "",
                        }

                        # Upload chunk
                        files = {
                            "chunk_data": (f"{file_type}_chunk_{chunk_index}", chunk_data, "application/octet-stream")
                        }

                        try:
                            response = req_lib.post(
                                f"{to_compute_url}/session/clone_receive_embedding_space",
                                data=form_data,
                                files=files,
                                timeout=600,  # 10 minute timeout per chunk
                            )
                            response.raise_for_status()
                            logger.info(f"Uploaded chunk {chunk_index + 1}/{total_chunks} of {file_type}")
                        except req_lib.RequestException as e:
                            logger.error(f"Failed to upload chunk {chunk_index + 1}/{total_chunks} of {file_type}: {e}")
                            raise HTTPException(
                                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                detail=f"Failed to upload chunk {chunk_index + 1}/{total_chunks}: {str(e)}",
                            )

            # Get new session_id from destination status endpoint
            # The destination creates the session when ES pickle is complete
            new_session_id = None
            try:
                # Wait a moment for session creation
                import time

                time.sleep(1)

                # Make a status request to get the new session_id
                status_response = req_lib.get(
                    f"{to_compute_url}/session/clone_receive_embedding_space/status",
                    params={"source_session_id": id},
                    timeout=30,
                )
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    new_session_id = status_data.get("new_session_id")
            except Exception as e:
                logger.warning(f"Could not get new session_id from status endpoint: {e}")

            if new_session_id:
                return JSONResponse(
                    {
                        "new_session_id": new_session_id,
                        "message": f"Embedding space cloned successfully to {request.to_compute}",
                        "source_session_id": id,
                        "destination_compute": request.to_compute,
                    }
                )
            else:
                # Fallback: return success without session_id (destination should have created it)
                return JSONResponse(
                    {
                        "message": f"Embedding space cloning initiated to {request.to_compute}. Check destination node for new session_id.",
                        "source_session_id": id,
                        "destination_compute": request.to_compute,
                    }
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cloning embedding space: {e}")
            traceback.print_exc()
            post_slack_alert(f"session={id}; error cloning embedding space: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error cloning embedding space: {str(e)}"
            )

    # In-memory storage for chunk assembly (keyed by source_session_id + file_type)
    _clone_chunk_storage: Dict[str, Dict[str, Any]] = {}

    @app.post("/session/clone_receive_embedding_space")
    async def clone_receive_embedding_space(
        chunk_index: int = Form(...),
        total_chunks: int = Form(...),
        file_type: str = Form(...),
        chunk_data: UploadFile = File(...),
        chunk_checksum: str = Form(...),
        source_session_id: str = Form(...),
        source_compute: str = Form(...),
        validation_loss: str = Form(None),
        epoch: str = Form(None),
        training_metadata: str = Form(None),
        new_session_name: str = Form(None),
    ) -> JSONResponse:
        """
        Receive a chunk of cloned embedding space data and reassemble files.

        When all chunks are received, creates a new ready session with the cloned ES.
        """

        try:
            # Validate file_type
            if file_type not in ["es_pickle", "strings_cache"]:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Invalid file_type: {file_type}. Must be 'es_pickle' or 'strings_cache'",
                )

            # Read chunk data
            chunk_bytes = await chunk_data.read()

            # Verify checksum
            calculated_checksum = hashlib.sha256(chunk_bytes).hexdigest()
            if calculated_checksum != chunk_checksum:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Checksum mismatch for chunk {chunk_index}. Expected {chunk_checksum}, got {calculated_checksum}",
                )

            # Storage key
            storage_key = f"{source_session_id}_{file_type}"

            # Initialize storage if needed
            if storage_key not in _clone_chunk_storage:
                _clone_chunk_storage[storage_key] = {
                    "chunks": {},
                    "total_chunks": total_chunks,
                    "file_type": file_type,
                    "source_session_id": source_session_id,
                    "source_compute": source_compute,
                    "validation_loss": float(validation_loss) if validation_loss else None,
                    "epoch": int(epoch) if epoch else None,
                    "training_metadata": json.loads(training_metadata) if training_metadata else None,
                    "new_session_name": new_session_name,
                }

            # Store chunk
            storage = _clone_chunk_storage[storage_key]
            storage["chunks"][chunk_index] = chunk_bytes

            logger.info(
                f"Received chunk {chunk_index + 1}/{total_chunks} of {file_type} for session {source_session_id}"
            )

            # Check if all chunks received
            if len(storage["chunks"]) == total_chunks:
                logger.info(f"All chunks received for {file_type}, reassembling...")

                # Reassemble file
                temp_dir = Path(config.data_dir) / "clone_temp" / source_session_id
                temp_dir.mkdir(parents=True, exist_ok=True)

                if file_type == "es_pickle":
                    reassembled_path = temp_dir / get_embedding_space_pickle_filename()
                else:  # strings_cache
                    reassembled_path = temp_dir / "strings.sqlite3"

                with open(reassembled_path, "wb") as f:
                    for i in range(total_chunks):
                        if i not in storage["chunks"]:
                            raise HTTPException(
                                status_code=HTTPStatus.BAD_REQUEST, detail=f"Missing chunk {i} for {file_type}"
                            )
                        f.write(storage["chunks"][i])

                logger.info(f"Reassembled {file_type} to {reassembled_path}")

                # Clean up chunk storage
                del storage["chunks"]

                # Check if both files are ready
                es_pickle_key = f"{source_session_id}_es_pickle"
                strings_cache_key = f"{source_session_id}_strings_cache"

                # ES is ready if it's in storage and has no chunks (already reassembled)
                es_ready = es_pickle_key in _clone_chunk_storage and "chunks" not in _clone_chunk_storage[es_pickle_key]
                # Strings cache is ready if it's not in storage (not needed) or if it's in storage and has no chunks
                strings_ready = strings_cache_key not in _clone_chunk_storage or (
                    strings_cache_key in _clone_chunk_storage
                    and "chunks" not in _clone_chunk_storage[strings_cache_key]
                )

                # If ES pickle is ready and (strings cache is ready or not needed), create session
                if es_ready and (strings_ready or strings_cache_key not in _clone_chunk_storage):
                    logger.info("All files ready, creating cloned session...")

                    # Get metadata from ES pickle storage
                    es_storage = _clone_chunk_storage[es_pickle_key]

                    # Extract prefix from source_session_id if present
                    # Format: {prefix}-{uuid} or {uuid}-{timestamp}
                    source_session_id_parts = source_session_id.split("-")
                    session_name_prefix = None
                    if len(source_session_id_parts) > 6:  # Likely has prefix (prefix is usually multiple parts)
                        # Extract prefix (everything except last 6 parts which are UUID)
                        # UUID format: 8-4-4-4-12 = 5 parts, but we also have timestamp potentially
                        # Try to extract prefix by finding where UUID starts
                        # Simple heuristic: if session_id has more than 6 parts, first N-6 parts are prefix
                        if len(source_session_id_parts) > 6:
                            prefix_parts = source_session_id_parts[:-6]
                            session_name_prefix = "-".join(prefix_parts)

                    # Generate new session_id
                    full_uuid = str(uuid4())
                    created_at = datetime.datetime.now(tz=ZoneInfo("America/New_York"))

                    if session_name_prefix:
                        new_session_id = f"{session_name_prefix}-{full_uuid}"
                    else:
                        # Use standard format
                        unique_string = full_uuid[:6]
                        session_timestamp = created_at.strftime("%Y%m%d-%H%M%S")
                        new_session_id = f"{unique_string}-{session_timestamp}"

                    # Move files to final location
                    session_dir = Path(config.session_dir)
                    final_es_path = session_dir / f"{new_session_id}_{get_embedding_space_pickle_filename()}"
                    final_strings_path = session_dir / f"{new_session_id}_strings.sqlite3" if strings_ready else None

                    shutil.move(str(temp_dir / get_embedding_space_pickle_filename()), str(final_es_path))
                    if strings_ready and (temp_dir / "strings.sqlite3").exists():
                        shutil.move(str(temp_dir / "strings.sqlite3"), str(final_strings_path))

                    # Clean up temp directory
                    shutil.rmtree(temp_dir, ignore_errors=True)

                    # Get strings cache path if available
                    strings_storage = _clone_chunk_storage.get(strings_cache_key)
                    strings_cache_path = str(final_strings_path) if strings_ready and final_strings_path else None

                    # Create session
                    session_doc = create_cloned_session(
                        session_id=new_session_id,
                        created_at=created_at,
                        embedding_space_path=str(final_es_path),
                        strings_cache_path=strings_cache_path,
                        source_session_id=source_session_id,
                        source_compute=source_compute,
                        validation_loss=es_storage.get("validation_loss"),
                        epoch=es_storage.get("epoch"),
                        training_metadata=es_storage.get("training_metadata"),
                        name=es_storage.get("new_session_name") or new_session_name,
                    )

                    # Save session
                    save_session(session_id=new_session_id, session_doc=session_doc)

                    # Clean up storage
                    _clone_chunk_storage.pop(es_pickle_key, None)
                    _clone_chunk_storage.pop(strings_cache_key, None)

                    logger.info(f"Created cloned session {new_session_id} from {source_session_id}")

                    return JSONResponse(
                        {
                            "new_session_id": new_session_id,
                            "message": "Embedding space cloned successfully",
                            "source_session_id": source_session_id,
                            "destination_compute": get_compute_cluster_name(),
                        }
                    )
                else:
                    # Not all files ready yet
                    return JSONResponse(
                        {
                            "message": f"Chunk {chunk_index + 1}/{total_chunks} received. Waiting for remaining chunks...",
                            "chunks_received": len(storage.get("chunks", {})) if "chunks" in storage else total_chunks,
                            "total_chunks": total_chunks,
                        }
                    )
            else:
                # More chunks coming
                return JSONResponse(
                    {
                        "message": f"Chunk {chunk_index + 1}/{total_chunks} received",
                        "chunks_received": len(storage["chunks"]),
                        "total_chunks": total_chunks,
                    }
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error receiving clone chunk: {e}")
            traceback.print_exc()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error receiving clone chunk: {str(e)}"
            )

    @app.get("/session/clone_receive_embedding_space/status")
    async def clone_receive_status(source_session_id: str = Query(...)) -> JSONResponse:
        """Get status of clone operation (for retrieving new_session_id)."""
        # Check if session was created (using Redis)
        try:
            from lib.session_manager import iterate_over_sessions
            # Look for sessions in Redis
            for session in iterate_over_sessions():
                try:
                    clone_metadata = session.get("clone_metadata", {})
                    if clone_metadata.get("source_session_id") == source_session_id:
                        return JSONResponse(
                            {
                                "new_session_id": session.get("session_id"),
                                "status": "completed",
                                "source_session_id": source_session_id,
                            }
                        )
                except:
                    continue

            return JSONResponse({"status": "in_progress", "message": "Clone operation still in progress or not found"})
        except Exception as e:
            logger.error(f"Error checking clone status: {e}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error checking clone status: {str(e)}"
            )

    @app.post("/session/{id}/extend_embedding_space_data")
    async def extend_embedding_space_data(
        id: str,
        file: UploadFile = File(...),
        data_passes: int = Form(...),
        name: str = Form(None),
        session_name_prefix: str = Form(None),
    ) -> JSONResponse:
        """
        Extend embedding space training with new data.

        This endpoint:
        1. Loads the source session and embedding space
        2. Gets the current training state (epoch, checkpoint)
        3. Creates a new session
        4. Clones the embedding space to the new session
        5. Processes and combines the new data with existing data
        6. Starts training from the previous checkpoint for additional epochs

        Args:
            id: Source session ID containing the embedding space to extend
            file: New data file (CSV or .csv.gz)
            data_passes: Number of additional training epochs
            name: Optional name for the new extended session
            session_name_prefix: Optional prefix for the new session ID

        Returns:
            JSONResponse with new_session_id
        """

        try:
            # Load source session
            source_session = load_session(id)
            if not source_session:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Source session not found: {id}")

            # Get embedding space path
            embedding_space_path = source_session.get("embedding_space")
            resolved_es_path = resolve_embedding_space_path(embedding_space_path) if embedding_space_path else None
            if not resolved_es_path:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail=f"Embedding space not found for session {id}"
                )

            logger.info(f"📂 Loading embedding space from {embedding_space_path}")
            es = load_embedded_space(embedding_space_path)

            # Get current training state
            training_info = getattr(es, "training_info", {})
            progress_info = training_info.get("progress_info", {})

            # Get current epoch from training info
            current_epoch = None
            if hasattr(es, "_training_timeline") and es._training_timeline:
                current_epoch = len(es._training_timeline) - 1
            elif "epochs" in training_info:
                current_epoch = training_info.get("epochs", 0)
            elif progress_info:
                # Try to get from loss history
                loss_history = progress_info.get("loss_history", [])
                if loss_history:
                    current_epoch = len(loss_history) - 1

            if current_epoch is None:
                current_epoch = 0
                logger.warning("⚠️  Could not determine current epoch, assuming 0")

            logger.info(f"📊 Current training state: epoch {current_epoch}")
            logger.info(f"🔄 Will continue training for {data_passes} additional epochs (from epoch {current_epoch})")

            # Save uploaded file
            original_extension = Path(file.filename).suffix
            new_file_name = f"{str(uuid4())}{original_extension}"
            new_file_path = config.data_dir / new_file_name

            with open(new_file_path, "wb") as buffer:
                buffer.write(await file.read())

            logger.info(f"✅ New data file saved: {new_file_name}")

            # Get column overrides and other settings from source session
            column_overrides = source_session.get("column_overrides", {})
            string_list_delimiter = source_session.get("string_list_delimiter", "|")
            movie_frame_interval = source_session.get("movie_frame_interval", 3)
            weightwatcher_save_every = source_session.get("weightwatcher_save_every", 5)
            important_columns_for_visualization = source_session.get("important_columns_for_visualization", [])

            # Create new session name
            new_session_name = name or f"{source_session.get('name', 'Extended')} (extended)"

            # Create new session with the new data file
            # The session will clone the ES and continue training
            created_at = datetime.datetime.now(tz=ZoneInfo("America/New_York"))

            # Generate new session ID
            if session_name_prefix:
                session_name_prefix = session_name_prefix.replace("/", "_").replace(".", "_")
                full_uuid = str(uuid4())
                new_session_id = f"{session_name_prefix}-{full_uuid}"
            else:
                unique_string = str(uuid4())[:6]
                session_timestamp = created_at.strftime("%Y%m%d-%H%M%S")
                new_session_id = f"{unique_string}-{session_timestamp}"

            logger.info(f"🆕 Creating extended session: {new_session_id}")

            # Combine old and new data
            # Get old data file from source session
            old_data_file = source_session.get("input_data")
            combined_file_name = None

            if old_data_file and Path(config.data_dir / old_data_file).exists():
                logger.info("📊 Combining old and new data...")
                logger.info(f"   Old data: {old_data_file}")
                logger.info(f"   New data: {new_file_name}")

                import gzip
                import io

                import pandas as pd

                # Read old data
                old_data_path = config.data_dir / old_data_file
                if old_data_path.suffix == ".gz":
                    old_df = pd.read_csv(old_data_path, compression="gzip")
                else:
                    old_df = pd.read_csv(old_data_path)

                # Read new data
                new_data_path = config.data_dir / new_file_name
                if new_data_path.suffix == ".gz":
                    new_df = pd.read_csv(new_data_path, compression="gzip")
                else:
                    new_df = pd.read_csv(new_data_path)

                # Combine dataframes
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                logger.info(f"   Combined: {len(old_df)} + {len(new_df)} = {len(combined_df)} rows")

                # Save combined data
                combined_file_name = f"{str(uuid4())}.csv.gz"
                combined_file_path = config.data_dir / combined_file_name

                # Compress and save
                compressed_buffer = io.BytesIO()
                csv_buffer = io.StringIO()
                combined_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue().encode("utf-8")

                with gzip.GzipFile(fileobj=compressed_buffer, mode="wb") as gz:
                    gz.write(csv_data)

                with open(combined_file_path, "wb") as f:
                    f.write(compressed_buffer.getvalue())

                logger.info(f"✅ Combined data saved: {combined_file_name}")
                data_file_to_use = combined_file_name
            else:
                logger.info("⚠️  Old data file not found, using only new data")
                data_file_to_use = new_file_name

            # Create session document

            new_session = create_sphere_session(
                session_id=new_session_id,
                created_at=created_at,
                input_filename=data_file_to_use,
                name=new_session_name,
                epochs=data_passes,  # Additional epochs to train
                column_overrides=column_overrides,
                string_list_delimiter=string_list_delimiter,
                movie_frame_interval=movie_frame_interval,
                weightwatcher_save_every=weightwatcher_save_every,
                important_columns_for_visualization=important_columns_for_visualization,
            )

            # Add resume_from_epoch to the train_es job spec
            # This tells the training to continue from the checkpoint
            job_plan = new_session.get("job_plan", [])
            for job_desc in job_plan:
                if job_desc.get("job_type") == "train_es":
                    job_spec = job_desc.get("spec", {})
                    job_spec["resume_from_epoch"] = current_epoch
                    job_spec["resume_from_embedding_space"] = str(embedding_space_path)
                    logger.info(f"✅ Set resume_from_epoch={current_epoch} in train_es job spec")
                    break

            # Add extension metadata
            new_session["extension_metadata"] = {
                "source_session_id": id,
                "source_epoch": current_epoch,
                "additional_epochs": data_passes,
                "extended_at": created_at.isoformat(),
                "combined_data": combined_file_name is not None,
            }

            # Clone embedding space to new session
            # Copy ES pickle and strings cache
            strings_cache_path = source_session.get("strings_cache")

            # Create session directory
            session_dir = Path(config.session_dir) / new_session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Copy embedding space
            new_es_path = session_dir / get_embedding_space_pickle_filename()
            shutil.copy2(Path(embedding_space_path), new_es_path)
            new_session["embedding_space"] = str(new_es_path.resolve())
            logger.info(f"✅ Cloned embedding space to: {new_es_path}")

            # Copy strings cache if it exists
            if strings_cache_path and Path(strings_cache_path).exists():
                new_strings_cache_path = session_dir / "strings.sqlite3"
                shutil.copy2(Path(strings_cache_path), new_strings_cache_path)
                new_session["strings_cache"] = str(new_strings_cache_path.resolve())
                logger.info(f"✅ Cloned strings cache to: {new_strings_cache_path}")

            # Also set resume_from_epoch at session level for reference
            new_session["resume_from_epoch"] = current_epoch
            new_session["resume_from_session"] = id  # Track source for reference

            # Save the new session
            save_session(session_id=new_session_id, session_doc=new_session, exist_ok=False)

            # Start the session (will trigger training with resume)
            from lib.session_chains import dispatch_next_job_in_chain

            dispatch_next_job_in_chain(session_id=new_session_id)

            logger.info(f"✅ Extended session created and training started: {new_session_id}")

            return JSONResponse(
                {
                    "session_id": new_session_id,
                    "message": f"Embedding space extended. Training will continue from epoch {current_epoch} for {data_passes} additional epochs.",
                    "source_session_id": id,
                    "source_epoch": current_epoch,
                    "additional_epochs": data_passes,
                }
            )

        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Failed to extend embedding space: {error_type}: {error_msg}")
            traceback.print_exc()
            post_slack_alert(f"error extending embedding space for session {id}: {error_type}: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to extend embedding space: {error_type}: {error_msg}")

    def _get_model_architecture_from_metadata(model_path: str) -> dict:
        """Load model architecture details from metadata file (if exists) or fall back to loading model."""
        try:
            # First try to load from metadata file (fast path)
            model_dir = Path(model_path).parent
            metadata_path = model_dir / "model_metadata.json"

            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                arch = metadata.get("model_architecture", {})
                logger.debug(f"✅ Loaded model metadata from {metadata_path}")
                return {"layer_count": arch.get("layer_count"), "parameter_count": arch.get("parameter_count")}

            # Fall back to loading the model (slow path, but still works for old models)
            logger.warning(f"No metadata file found at {metadata_path}, falling back to loading model")
            return {}

        except Exception as e:
            logger.warning(f"Failed to get model architecture: {e}")
            return {}

    def _get_training_stats_from_timeline(timeline_path: str) -> dict:
        """Extract training statistics from training_timeline.json file."""
        try:
            if not Path(timeline_path).exists():
                return {}

            with open(timeline_path) as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            final_summary = data.get("final_summary", {})
            timeline = data.get("training_trajectory", [])

            return {
                "model_param_count": metadata.get("model_param_count"),
                "num_rows": metadata.get("num_rows"),
                "num_cols": metadata.get("num_cols"),
                "compute_device": metadata.get("compute_device"),
                "epochs_completed": final_summary.get("total_epochs", len(timeline)),
                "final_training_loss": final_summary.get("final_training_loss"),
                "final_validation_loss": final_summary.get("final_validation_loss"),
                "total_training_time_seconds": final_summary.get("total_training_time"),
                "converged": final_summary.get("converged"),
                "convergence_epoch": final_summary.get("convergence_epoch"),
            }
        except Exception as e:
            logger.warning(f"Failed to read training timeline from {timeline_path}: {e}")
            return {}

    def _check_model_card_availability(session_id: str, embedding_space_path: str) -> dict:
        """Check if model card exists for a session. Returns dict with availability info."""
        try:
            if not embedding_space_path:
                return {"available": False, "endpoint": f"/session/{session_id}/model_card"}

            embedding_space_path_obj = resolve_session_path(session_id, embedding_space_path)

            if not embedding_space_path_obj.exists():
                return {"available": False, "endpoint": f"/session/{session_id}/model_card"}

            # Check for model card in expected locations
            job_output_dir = embedding_space_path_obj.parent
            model_card_path = None

            # Try session-level directory first
            if job_output_dir.name.startswith("train_") or job_output_dir.parent.name in [
                "train_es",
                "train_single_predictor",
            ]:
                potential_session_dir = job_output_dir.parent.parent
                if potential_session_dir.exists() and session_id in potential_session_dir.name:
                    model_card_path = potential_session_dir / "best_model_package" / "model_card.json"
                else:
                    model_card_path = job_output_dir / "best_model_package" / "model_card.json"
            else:
                model_card_path = job_output_dir / "best_model_package" / "model_card.json"

            if model_card_path and model_card_path.exists():
                return {
                    "available": True,
                    "path": str(model_card_path),
                    "endpoint": f"/session/{session_id}/model_card",
                }

            # Fallback: search in config.output_dir
            job_dir = None
            if config.output_dir.exists():
                exact_match = config.output_dir / session_id
                if exact_match.exists() and exact_match.is_dir():
                    job_dir = exact_match
                else:
                    # Search for directories containing the session ID
                    for job_dir in config.output_dir.glob("*"):
                        if job_dir.is_dir() and session_id in job_dir.name:
                            break
                    else:
                        job_dir = None
            
            # If not found locally, search backplane
            if not job_dir:
                backplane_root = Path("/backplane/backplane1/sphere")
                if backplane_root.exists():
                    for host_dir in backplane_root.iterdir():
                        if host_dir.is_dir() and host_dir.name.startswith("host-"):
                            backplane_output_dir = host_dir / "app" / "featrix_output" / session_id
                            if backplane_output_dir.exists() and backplane_output_dir.is_dir():
                                job_dir = backplane_output_dir
                                break
            
            # Check if model card exists in found directory
            if job_dir:
                model_card_path = job_dir / "best_model_package" / "model_card.json"
                if model_card_path.exists():
                    return {
                        "available": True,
                        "path": str(model_card_path),
                        "endpoint": f"/session/{session_id}/model_card",
                    }

            return {"available": False, "endpoint": f"/session/{session_id}/model_card"}
        except Exception as e:
            logger.warning(f"Failed to check model card availability: {e}")
            return {"available": False, "endpoint": f"/session/{session_id}/model_card", "error": str(e)}

    def _get_training_stats_from_metrics(metrics_path: str) -> dict:
        """Extract training statistics from training_metrics.json file."""
        try:
            if not Path(metrics_path).exists():
                return {}

            with open(metrics_path) as f:
                data = json.load(f)

            training_info = data.get("training_info", [])

            stats = {
                "target_column": data.get("target_column"),
                "target_column_type": data.get("target_column_type"),
                "epochs_completed": len(training_info),
                "final_loss": training_info[-1].get("loss") if training_info else None,
                "final_validation_loss": training_info[-1].get("validation_loss") if training_info else None,
                "final_accuracy": data.get("final_accuracy"),
            }

            # Add quality metrics if available (classification models)
            quality_metrics = data.get("quality_metrics", {})
            if quality_metrics:
                stats["quality_metrics"] = {
                    "f1_score": quality_metrics.get("f1"),
                    "precision": quality_metrics.get("precision"),
                    "recall": quality_metrics.get("recall"),
                    "accuracy": quality_metrics.get("accuracy"),
                    "auc": quality_metrics.get("auc"),
                    "confusion_matrix": quality_metrics.get("confusion_matrix"),
                }

            return stats
        except Exception as e:
            logger.warning(f"Failed to read training metrics from {metrics_path}: {e}")
            return {}

    def _get_job_training_stats(job: dict) -> dict:
        """Extract training statistics from job metadata."""
        started_at = job.get("started_at")
        finished_at = job.get("finished_at")

        training_duration = None
        if started_at and finished_at:
            try:
                if isinstance(started_at, str):
                    started_at = datetime.datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                if isinstance(finished_at, str):
                    finished_at = datetime.datetime.fromisoformat(finished_at.replace("Z", "+00:00"))

                duration = finished_at - started_at
                training_duration = duration.total_seconds()
            except Exception as e:
                logger.warning(f"Failed to calculate training duration: {e}")

        return {
            "started_at": convert_to_iso(started_at) if started_at else None,
            "finished_at": convert_to_iso(finished_at) if finished_at else None,
            "training_duration_seconds": training_duration,
            "current_epoch": job.get("current_epoch"),
            "current_loss": job.get("current_loss"),
            "validation_loss": job.get("validation_loss"),
            "progress": job.get("progress"),
        }

    @app.get("/session/{id}/models")
    async def get_session_models(id: str) -> JSONResponse:
        """
        Get available models and embedding spaces for a session with comprehensive training statistics.

        Returns:
        - Embedding space with training stats and downstream models
        - Single predictors linked to their embedding space
        - Training duration, epochs, status (trained/training/failed/not started)
        - Crash/error information if applicable
        """

        try:
            session = load_session(id)
        except FileNotFoundError:
            # Session not found is a normal condition (e.g., session on different node)
            # Don't spam Slack with expected 404s
            logger.debug(f"Session {id} not found for models list (normal condition)")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")
        except Exception as e:

            traceback.print_exc()
            print(f"ERROR loading session {id}: {str(e)}")
            post_slack_alert(f"session={id}; error loading session: {str(e)}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error loading session: {str(e)}")

        try:
            # Get session info including job statuses
            session_info = get_session_info(session_id=id)
            jobs = session_info.get("jobs", {})
            detailed_queue_info = session_info.get("detailed_queue_info", {})

            models = {}

            # ==================== EMBEDDING SPACE ====================
            embedding_space_path = session.get("embedding_space")
            es_job = None
            es_job_id = None

            # Find the ES training job
            for job_id, job in jobs.items():
                if job.get("type") == "train_es":
                    es_job = job
                    es_job_id = job_id
                    break

            if embedding_space_path and Path(embedding_space_path).exists():
                try:
                    import os

                    stat = Path(embedding_space_path).stat()

                    # Get training statistics from timeline file
                    es_dir = Path(embedding_space_path).parent
                    timeline_path = es_dir / "training_timeline.json"
                    training_stats = _get_training_stats_from_timeline(str(timeline_path))

                    # Get model architecture details from metadata file
                    arch_details = _get_model_architecture_from_metadata(embedding_space_path)

                    # Get job training stats
                    job_stats = _get_job_training_stats(es_job) if es_job else {}

                    # Determine status
                    if es_job:
                        job_status = es_job.get("status")
                        if job_status == JobStatus.DONE:
                            status = "trained"
                            status_detail = "Training completed successfully"
                        elif job_status == JobStatus.RUNNING:
                            status = "training"
                            status_detail = f"Training in progress - epoch {job_stats.get('current_epoch', '?')}"
                        elif job_status == JobStatus.FAILED:
                            status = "failed"
                            status_detail = "Training failed - check logs"
                            error_info = es_job.get("error", "Unknown error")
                            job_stats["error"] = str(error_info)
                        elif job_status == JobStatus.READY:
                            status = "queued"
                            status_detail = "Waiting in queue"
                        elif job_status == JobStatus.PAUSED:
                            status = "paused"
                            status_detail = es_job.get("pause_reason", "Job paused")
                        else:
                            status = "unknown"
                            status_detail = f"Status: {job_status}"
                    else:
                        status = "trained"
                        status_detail = "Training completed (job info not available)"

                    # Check for model card availability
                    model_card_info = _check_model_card_availability(id, embedding_space_path)

                    models["embedding_space"] = {
                        "available": True,
                        "path": embedding_space_path,
                        "type": "embedding_space",
                        "description": "Trained embedding space for vector representations",
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "modified_at": stat.st_mtime,
                        "status": status,
                        "status_detail": status_detail,
                        "job_id": es_job_id,
                        "model_architecture": {
                            "layer_count": arch_details.get("layer_count"),
                            "parameter_count": arch_details.get("parameter_count")
                            or training_stats.get("model_param_count"),
                            "num_rows": training_stats.get("num_rows"),
                            "num_cols": training_stats.get("num_cols"),
                            "compute_device": training_stats.get("compute_device"),
                        },
                        "training_statistics": {**training_stats, **job_stats},
                        "model_card": model_card_info,
                        "endpoints": [
                            f"/session/{id}/encode_records",
                            f"/session/{id}/similarity_search",
                            f"/session/{id}/model_card",
                        ],
                        "downstream_models": [],  # Will be populated later
                    }
                except Exception as e:
                    print(f"ERROR processing embedding space: {str(e)}")
                    models["embedding_space"] = {
                        "available": False,
                        "path": embedding_space_path,
                        "status": "error",
                        "error": str(e),
                    }
            else:
                # ES not trained yet - check job status
                if es_job:
                    job_status = es_job.get("status")
                    if job_status == JobStatus.RUNNING:
                        status = "training"
                        status_detail = "Training in progress"
                        job_stats = _get_job_training_stats(es_job)
                    elif job_status == JobStatus.READY:
                        status = "queued"
                        status_detail = "Waiting in queue"
                        job_stats = {}
                    elif job_status == JobStatus.FAILED:
                        status = "failed"
                        status_detail = "Training failed"
                        job_stats = {"error": str(es_job.get("error", "Unknown error"))}
                    elif job_status == JobStatus.PAUSED:
                        status = "paused"
                        status_detail = es_job.get("pause_reason", "Job paused")
                        job_stats = {}
                    else:
                        status = "not_started"
                        status_detail = "Not started"
                        job_stats = {}
                else:
                    status = "not_started"
                    status_detail = "Embedding space training not initiated"
                    job_stats = {}

                # Check for model card even if ES not trained (might exist from previous training)
                model_card_info = (
                    _check_model_card_availability(id, embedding_space_path)
                    if embedding_space_path
                    else {"available": False, "endpoint": f"/session/{id}/model_card"}
                )

                models["embedding_space"] = {
                    "available": False,
                    "path": embedding_space_path,
                    "status": status,
                    "status_detail": status_detail,
                    "job_id": es_job_id,
                    "training_statistics": job_stats,
                    "description": "Embedding space not trained yet",
                    "model_card": model_card_info,
                    "endpoints": [f"/session/{id}/model_card"],
                }

            # ==================== SINGLE PREDICTORS ====================
            single_predictor_path = session.get("single_predictor")
            single_predictors_paths = session.get("single_predictors")
            training_metrics_path = session.get("training_metrics")

            # Find all single predictor training jobs
            sp_jobs = []
            for job_id, job in jobs.items():
                if job.get("type") == "train_single_predictor":
                    sp_jobs.append((job_id, job))

            # Handle both old format (single predictor) and new format (multiple predictors)
            predictor_info = []

            # Check new format first (multiple predictors)
            if single_predictors_paths and isinstance(single_predictors_paths, list):
                for i, path in enumerate(single_predictors_paths):
                    # Find corresponding job
                    sp_job = sp_jobs[i] if i < len(sp_jobs) else None
                    sp_job_id = sp_job[0] if sp_job else None
                    sp_job_data = sp_job[1] if sp_job else None

                    # Get corresponding metrics path
                    metrics_path = None
                    if training_metrics_path:
                        if isinstance(training_metrics_path, list) and i < len(training_metrics_path):
                            metrics_path = training_metrics_path[i]
                        elif isinstance(training_metrics_path, str) and i == 0:
                            metrics_path = training_metrics_path

                    # Resolve path (handles backplane, published sessions, etc.)
                    resolved_path = resolve_session_path(id, path) if path else None
                    if resolved_path and resolved_path.exists():
                        try:
                            stat = resolved_path.stat()
                            path = str(resolved_path)  # Use resolved path

                            # Get training statistics from metrics file
                            metrics_stats = _get_training_stats_from_metrics(metrics_path) if metrics_path else {}

                            # Get model architecture details from metadata file
                            arch_details = _get_model_architecture_from_metadata(path)

                            # Get job training stats
                            job_stats = _get_job_training_stats(sp_job_data) if sp_job_data else {}

                            # Determine status
                            if sp_job_data:
                                job_status = sp_job_data.get("status")
                                if job_status == JobStatus.DONE:
                                    status = "trained"
                                    status_detail = "Training completed successfully"
                                elif job_status == JobStatus.RUNNING:
                                    status = "training"
                                    status_detail = (
                                        f"Training in progress - epoch {job_stats.get('current_epoch', '?')}"
                                    )
                                elif job_status == JobStatus.FAILED:
                                    status = "failed"
                                    status_detail = "Training failed - check logs"
                                    error_info = sp_job_data.get("error", "Unknown error")
                                    job_stats["error"] = str(error_info)
                                elif job_status == JobStatus.READY:
                                    status = "queued"
                                    status_detail = "Waiting in queue"
                                elif job_status == JobStatus.PAUSED:
                                    status = "paused"
                                    status_detail = sp_job_data.get("pause_reason", "Job paused")
                                else:
                                    status = "unknown"
                                    status_detail = f"Status: {job_status}"
                            else:
                                status = "trained"
                                status_detail = "Training completed (job info not available)"

                            import hashlib
                            import os

                            filename = os.path.basename(path) if path else "unknown"
                            path_hash = hashlib.md5(path.encode("utf-8")).hexdigest()[:8]

                            predictor_info.append(
                                {
                                    "predictor_index": i,
                                    "predictor_id": f"{filename}_{path_hash}",
                                    "path": path,
                                    "file_size": stat.st_size,
                                    "created_at": stat.st_ctime,
                                    "modified_at": stat.st_mtime,
                                    "status": status,
                                    "status_detail": status_detail,
                                    "job_id": sp_job_id,
                                    "target_column": metrics_stats.get("target_column"),
                                    "target_column_type": metrics_stats.get("target_column_type"),
                                    "model_architecture": {
                                        "layer_count": arch_details.get("layer_count"),
                                        "parameter_count": arch_details.get("parameter_count"),
                                    },
                                    "training_statistics": {**metrics_stats, **job_stats},
                                }
                            )
                        except Exception as e:
                            print(f"ERROR processing single predictor {i}: {str(e)}")
                            predictor_info.append(
                                {"predictor_index": i, "path": path, "status": "error", "error": str(e)}
                            )
                    else:
                        # Predictor not trained yet - check job status
                        if sp_job_data:
                            job_status = sp_job_data.get("status")
                            if job_status == JobStatus.RUNNING:
                                status = "training"
                                status_detail = "Training in progress"
                                job_stats = _get_job_training_stats(sp_job_data)
                            elif job_status == JobStatus.READY:
                                status = "queued"
                                status_detail = "Waiting in queue"
                                job_stats = {}
                            elif job_status == JobStatus.FAILED:
                                status = "failed"
                                status_detail = "Training failed"
                                job_stats = {"error": str(sp_job_data.get("error", "Unknown error"))}
                            elif job_status == JobStatus.PAUSED:
                                status = "paused"
                                status_detail = sp_job_data.get("pause_reason", "Job paused")
                                job_stats = {}
                            else:
                                status = "not_started"
                                status_detail = "Not started"
                                job_stats = {}
                        else:
                            status = "not_started"
                            status_detail = "Predictor training not initiated"
                            job_stats = {}

                        predictor_info.append(
                            {
                                "predictor_index": i,
                                "path": path,
                                "status": status,
                                "status_detail": status_detail,
                                "job_id": sp_job_id,
                                "training_statistics": job_stats,
                            }
                        )

            # Check old format (single predictor)
            elif single_predictor_path and isinstance(single_predictor_path, str):
                sp_job = sp_jobs[0] if sp_jobs else None
                if sp_job and isinstance(sp_job, (tuple, list)) and len(sp_job) >= 2:
                    sp_job_id = sp_job[0]  # pylint: disable=unsubscriptable-object
                    sp_job_data = sp_job[1]  # pylint: disable=unsubscriptable-object
                else:
                    sp_job_id = None
                    sp_job_data = None

                metrics_path = training_metrics_path if isinstance(training_metrics_path, str) else None

                # Resolve path (handles backplane, published sessions, etc.)
                resolved_single_predictor_path = resolve_session_path(id, single_predictor_path) if single_predictor_path else None
                if resolved_single_predictor_path and resolved_single_predictor_path.exists():
                    try:
                        stat = resolved_single_predictor_path.stat()
                        single_predictor_path = str(resolved_single_predictor_path)  # Use resolved path

                        # Get training statistics from metrics file
                        metrics_stats = _get_training_stats_from_metrics(metrics_path) if metrics_path else {}

                        # Get model architecture details from metadata file
                        arch_details = _get_model_architecture_from_metadata(single_predictor_path)

                        # Get job training stats
                        job_stats = _get_job_training_stats(sp_job_data) if sp_job_data else {}

                        # Determine status
                        if sp_job_data:
                            job_status = sp_job_data.get("status")
                            if job_status == JobStatus.DONE:
                                status = "trained"
                                status_detail = "Training completed successfully"
                            elif job_status == JobStatus.RUNNING:
                                status = "training"
                                status_detail = "Training in progress"
                            elif job_status == JobStatus.FAILED:
                                status = "failed"
                                status_detail = "Training failed"
                                job_stats["error"] = str(sp_job_data.get("error", "Unknown error"))
                            elif job_status == JobStatus.PAUSED:
                                status = "paused"
                                status_detail = sp_job_data.get("pause_reason", "Job paused")
                            else:
                                status = "unknown"
                                status_detail = f"Status: {job_status}"
                        else:
                            status = "trained"
                            status_detail = "Training completed"

                        import hashlib
                        import os

                        filename = os.path.basename(single_predictor_path)
                        path_hash = hashlib.md5(single_predictor_path.encode("utf-8")).hexdigest()[:8]

                        predictor_info.append(
                            {
                                "predictor_index": 0,
                                "predictor_id": f"{filename}_{path_hash}",
                                "path": single_predictor_path,
                                "file_size": stat.st_size,
                                "created_at": stat.st_ctime,
                                "modified_at": stat.st_mtime,
                                "status": status,
                                "status_detail": status_detail,
                                "job_id": sp_job_id,
                                "target_column": metrics_stats.get("target_column"),
                                "target_column_type": metrics_stats.get("target_column_type"),
                                "model_architecture": {
                                    "layer_count": arch_details.get("layer_count"),
                                    "parameter_count": arch_details.get("parameter_count"),
                                },
                                "training_statistics": {**metrics_stats, **job_stats},
                            }
                        )
                    except Exception as e:
                        print(f"ERROR processing single predictor: {str(e)}")
                        predictor_info.append(
                            {"predictor_index": 0, "path": single_predictor_path, "status": "error", "error": str(e)}
                        )

            # Build single predictor model info
            if predictor_info:
                first_predictor_path = predictor_info[0]["path"] if predictor_info else None

                models["single_predictor"] = {
                    "available": any(
                        p.get("status") == "trained" or 
                        (p.get("path") and Path(p.get("path")).exists() and p.get("file_size"))
                        for p in predictor_info
                    ),
                    "path": first_predictor_path,
                    "type": "single_predictor",
                    "description": f"Single predictor models for making predictions ({len(predictor_info)} predictors)",
                    "predictors": predictor_info,
                    "endpoints": [
                        f"/session/{id}/predict",
                        f"/session/{id}/predict_table",
                        f"/session/{id}/training_metrics",
                    ],
                }

                # Link predictors to embedding space as downstream models
                if "embedding_space" in models and models["embedding_space"].get("available"):
                    models["embedding_space"]["downstream_models"] = [
                        {
                            "type": "single_predictor",
                            "predictor_id": p.get("predictor_id"),
                            "target_column": p.get("target_column"),
                            "status": p.get("status"),
                        }
                        for p in predictor_info
                        if p.get("predictor_id")
                    ]
            else:
                models["single_predictor"] = {
                    "available": False,
                    "path": single_predictor_path or single_predictors_paths,
                    "status": "not_started",
                    "description": "Single predictor not trained yet",
                    "predictors": [],
                }

            # Check vector database (for similarity search)
            vector_db_path = session.get("vector_db")
            if vector_db_path and Path(vector_db_path).exists():
                try:
                    # For LanceDB, check if it's a directory with data
                    vector_path = Path(vector_db_path)
                    if vector_path.is_dir():
                        # Count files in the directory
                        file_count = len(list(vector_path.rglob("*")))
                        models["vector_database"] = {
                            "available": True,
                            "path": vector_db_path,
                            "type": "vector_database",
                            "description": "Vector database for similarity search",
                            "file_count": file_count,
                            "created_at": vector_path.stat().st_ctime,
                            "modified_at": vector_path.stat().st_mtime,
                            "endpoints": [f"/session/{id}/similarity_search"],
                        }
                    else:
                        models["vector_database"] = {
                            "available": False,
                            "path": vector_db_path,
                            "error": "Vector database path is not a directory",
                        }
                except Exception as e:
                    print(f"ERROR processing vector database: {str(e)}")
                    models["vector_database"] = {"available": False, "path": vector_db_path, "error": str(e)}
            else:
                models["vector_database"] = {
                    "available": False,
                    "path": vector_db_path,
                    "description": "Vector database not built yet",
                }

            # Check 3D projections (for sphere visualization)
            projections_path = session.get("projections")
            if projections_path and Path(projections_path).exists():
                try:
                    stat = Path(projections_path).stat()
                    models["projections"] = {
                        "available": True,
                        "path": projections_path,
                        "type": "projections",
                        "description": "3D projections for sphere visualization (x, y, z coordinates)",
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "modified_at": stat.st_mtime,
                        "endpoints": [f"/session/{id}/projections"],
                    }
                except Exception as e:
                    print(f"ERROR processing projections: {str(e)}")
                    models["projections"] = {"available": False, "path": projections_path, "error": str(e)}
            else:
                models["projections"] = {
                    "available": False,
                    "path": projections_path,
                    "description": "3D projections not generated yet",
                }

            # Check training metrics
            training_metrics_path = session.get("training_metrics")

            # Handle both old format (single string) and new format (list of paths)
            training_metrics_info = []
            if training_metrics_path:
                if isinstance(training_metrics_path, list):
                    # New format: multiple training metrics files
                    for i, path in enumerate(training_metrics_path):
                        if path and Path(path).exists():
                            try:
                                stat = Path(path).stat()
                                training_metrics_info.append(
                                    {
                                        "predictor_index": i,
                                        "path": path,
                                        "file_size": stat.st_size,
                                        "created_at": stat.st_ctime,
                                        "modified_at": stat.st_mtime,
                                    }
                                )
                            except Exception as e:
                                print(f"ERROR processing training metrics {i}: {str(e)}")
                elif isinstance(training_metrics_path, str):
                    # Old format: single training metrics file
                    if Path(training_metrics_path).exists():
                        try:
                            stat = Path(training_metrics_path).stat()
                            training_metrics_info.append(
                                {
                                    "predictor_index": 0,
                                    "path": training_metrics_path,
                                    "file_size": stat.st_size,
                                    "created_at": stat.st_ctime,
                                    "modified_at": stat.st_mtime,
                                }
                            )
                        except Exception as e:
                            print(f"ERROR processing training metrics: {str(e)}")

            # Build training metrics model info
            if training_metrics_info:
                # Get the first valid path for display purposes
                first_metrics_path = training_metrics_info[0]["path"] if training_metrics_info else None

                models["training_metrics"] = {
                    "available": True,
                    "path": first_metrics_path,  # Add the path for client compatibility
                    "type": "training_metrics",
                    "description": f"Training metrics and loss history ({len(training_metrics_info)} predictors)",
                    "predictors": training_metrics_info,
                    "endpoints": [f"/session/{id}/training_metrics"],
                }
            else:
                models["training_metrics"] = {
                    "available": False,
                    "path": training_metrics_path,
                    "description": "Training metrics not available",
                }

            # Check SQLite database (original data)
            sqlite_db_path = session.get("sqlite_db")
            if sqlite_db_path and Path(sqlite_db_path).exists():
                try:
                    stat = Path(sqlite_db_path).stat()
                    models["data_database"] = {
                        "available": True,
                        "path": sqlite_db_path,
                        "type": "data_database",
                        "description": "Processed data in SQLite format",
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "modified_at": stat.st_mtime,
                        "endpoints": [],
                    }
                except Exception as e:
                    print(f"ERROR processing SQLite database: {str(e)}")
                    models["data_database"] = {"available": False, "path": sqlite_db_path, "error": str(e)}
            else:
                models["data_database"] = {
                    "available": False,
                    "path": sqlite_db_path,
                    "description": "Data database not created yet",
                }

            # Summary information with aggregate statistics
            available_models = [k for k, v in models.items() if v.get("available", False)]
            total_models = len(models)

            # Calculate aggregate training statistics
            total_training_time = 0
            total_epochs = 0
            total_parameters = 0

            # ES training time
            es_train_time = (
                models.get("embedding_space", {}).get("training_statistics", {}).get("total_training_time_seconds")
            )
            if es_train_time:
                total_training_time += es_train_time

            # ES epochs
            es_epochs = models.get("embedding_space", {}).get("training_statistics", {}).get("epochs_completed")
            if es_epochs:
                total_epochs += es_epochs

            # ES parameters
            es_params = models.get("embedding_space", {}).get("model_architecture", {}).get("parameter_count")
            if es_params:
                total_parameters += es_params

            # SP training time and epochs
            sp_predictors = models.get("single_predictor", {}).get("predictors", [])
            for pred in sp_predictors:
                pred_train_time = pred.get("training_statistics", {}).get("training_duration_seconds")
                if pred_train_time:
                    total_training_time += pred_train_time

                pred_epochs = pred.get("training_statistics", {}).get("epochs_completed")
                if pred_epochs:
                    total_epochs += pred_epochs

                pred_params = pred.get("model_architecture", {}).get("parameter_count")
                if pred_params:
                    total_parameters += pred_params

            # Count models by status
            status_counts = {"trained": 0, "training": 0, "failed": 0, "queued": 0, "not_started": 0}

            # Check ES status
            es_status = models.get("embedding_space", {}).get("status")
            if es_status in status_counts:
                status_counts[es_status] += 1

            # Check SP statuses
            for pred in sp_predictors:
                pred_status = pred.get("status")
                if pred_status in status_counts:
                    status_counts[pred_status] += 1

            result = {
                "session_id": id,
                "models": models,
                "summary": {
                    "total_models": total_models,
                    "available_models": len(available_models),
                    "available_model_types": available_models,
                    "training_complete": models["embedding_space"].get("available", False),
                    "prediction_ready": models["single_predictor"].get("available", False),
                    "similarity_search_ready": (
                        models["embedding_space"].get("available", False)
                        and models["vector_database"].get("available", False)
                    ),
                    "visualization_ready": models["projections"].get("available", False),
                    "aggregate_statistics": {
                        "total_training_time_seconds": total_training_time if total_training_time > 0 else None,
                        "total_epochs_trained": total_epochs if total_epochs > 0 else None,
                        "total_model_parameters": total_parameters if total_parameters > 0 else None,
                        "models_by_status": status_counts,
                        "num_embedding_spaces": 1 if models.get("embedding_space", {}).get("available") else 0,
                        "num_predictors": len([p for p in sp_predictors if p.get("status") == "trained"]),
                        "num_predictors_total": len(sp_predictors),
                    },
                },
            }

            print(f"Successfully processed models for session {id}")
            return JSONResponse(result)

        except Exception as e:

            traceback.print_exc()
            print(f"UNEXPECTED ERROR in get_session_models for session {id}: {str(e)}")
            post_slack_alert(f"session={id}; unexpected error in models endpoint: {str(e)}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error processing models: {str(e)}"
            )

    def is_private_network_ip(ip: str) -> bool:
        """Check if IP address is from allowed admin network."""
        try:
            # Allow only from our public IP, sphere-api server, or localhost
            return (
                ip == "75.150.77.37" or  # Admin public IP
                ip == "206.189.235.152" or  # sphere-api.featrix.com server
                ip.startswith("127.") or  # localhost
                ip == "localhost"
            )
        except:
            return False

    def get_client_ip(request: Request) -> str:
        """Get the real client IP address, considering proxies."""
        # Check common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        client_host = request.client.host if request.client else "unknown"
        return client_host

    def require_private_network(request: Request):
        """Dependency to ensure request comes from allowed admin IP."""
        client_ip = get_client_ip(request)
        if not is_private_network_ip(client_ip):
            logger.warning(f"Access denied to admin endpoint from IP: {client_ip}")
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail=f"Access denied. Admin endpoints only accessible from authorized IP. Your IP: {client_ip}",
            )
        logger.debug(f"Admin access granted to IP: {client_ip}")

    @app.get("/admin/logs/{job_dir}/{log_file}")
    async def admin_view_log(request: Request, job_dir: str, log_file: str, _: None = Depends(require_private_network)):
        """View job log files (authorized IP only)."""
        try:
            job_path = config.output_dir / job_dir
            log_path = job_path / "logs" / log_file

            if not log_path.exists():
                raise HTTPException(status_code=404, detail="Log file not found")

            content = log_path.read_text()

            # Apply syntax highlighting
            lines = content.split("\n")
            highlighted_lines = []

            for line in lines:
                css_class = ""
                lower_line = line.lower()

                if any(word in lower_line for word in ["error", "exception", "traceback", "failed"]):
                    css_class = "log-error"
                elif any(word in lower_line for word in ["warning", "warn"]):
                    css_class = "log-warning"
                elif any(word in lower_line for word in ["info", "starting", "completed"]):
                    css_class = "log-info"

                # Escape HTML
                escaped_line = (
                    line.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&#39;")
                )

                highlighted_lines.append(f'<div class="log-line {css_class}">{escaped_line}</div>')

            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Log Viewer - {job_dir}/{log_file}</title>
    <style>
        body {{ font-family: monospace; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; }}
        .log-container {{ background: #1e1e1e; padding: 20px; white-space: pre-wrap; }}
        .log-line {{ margin: 2px 0; }}
        .log-error {{ background-color: rgba(244, 67, 54, 0.2); color: #ff6b6b; }}
        .log-warning {{ background-color: rgba(255, 152, 0, 0.2); color: #ffb74d; }}
        .log-info {{ color: #81c784; }}
        .header {{ background: #333; color: white; padding: 10px; margin: -20px -20px 20px -20px; }}
        .back-link {{ color: #81c784; text-decoration: none; }}
    </style>
    <script>
        // Auto-refresh every 5 seconds
        setInterval(() => {{ window.location.reload(); }}, 5000);
    </script>
</head>
<body>
    <div class="header">
        <a href="/admin/inventory" class="back-link">← Back to Inventory</a>
        <h2>{job_dir} - {log_file}</h2>
    </div>
    <div class="log-container">
        {"".join(highlighted_lines)}
    </div>
</body>
</html>
"""
            return HTMLResponse(content=html_content)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading log: {str(e)}")

    @app.get("/admin/job_metrics/{job_dir}")
    async def admin_get_job_metrics(request: Request, job_dir: str, _: None = Depends(require_private_network)):
        """Get training metrics for loss plotting (authorized IP only)."""
        try:
            job_path = config.output_dir / job_dir

            # Look for training metrics files
            metrics_files = []

            # Single predictor metrics
            sp_metrics = job_path / "training_metrics.json"
            if sp_metrics.exists():
                with open(sp_metrics) as f:
                    data = json.load(f)
                    metrics_files.append({"type": "single_predictor", "file": str(sp_metrics), "data": data})

            # Embedding space metrics (if available)
            es_metrics = job_path / "embedded_space.pickle"  # Would need to extract metrics

            # Return available metrics
            return JSONResponse(
                {"job_dir": job_dir, "metrics_available": len(metrics_files) > 0, "metrics": metrics_files}
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

    @app.get("/sessions-for-org")
    async def get_sessions_for_org(request: Request, name_prefix: str = "alphafreight"):
        """
        Get all sessions matching a search term by searching featrix_output directory names.
        Uses partial match (not just prefix).
        PUBLIC ENDPOINT - no admin authentication required.

        Args:
            name_prefix: Term to match anywhere in session directory names (default: "alphafreight")

        Returns:
            List of matching session directory names
        """
        # This is a PUBLIC endpoint - explicitly log access
        client_ip = get_client_ip(request)
        logger.info(f"PUBLIC endpoint /sessions-for-org accessed from {client_ip} with name_prefix={name_prefix}")

        try:
            output_dir = config.output_dir
            if not output_dir.exists():
                logger.warning(f"Output directory {output_dir} does not exist")
                return JSONResponse({"sessions": [], "compute_cluster": socket.gethostname().split(".")[0]})

            matching_sessions = []
            for item in os.listdir(output_dir):
                item_path = output_dir / item
                # Only include directories
                if item_path.is_dir():
                    # Check if directory name contains the search term (partial match)
                    if name_prefix.lower() in item.lower():
                        matching_sessions.append(item)

            # Sort alphabetically
            matching_sessions.sort()

            logger.info(f"Found {len(matching_sessions)} sessions matching '{name_prefix}' in {output_dir}")

            return JSONResponse(
                {
                    "sessions": matching_sessions,
                    "compute_cluster": socket.gethostname().split(".")[0],
                    "name_prefix": name_prefix,
                }
            )

        except Exception as e:
            logger.exception(f"Error getting sessions for org '{name_prefix}': {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


    @app.post("/prediction/{prediction_id}/update_label")
    async def update_prediction_label(prediction_id: str, request: UpdateLabelRequest) -> JSONResponse:
        """Update the user label for a prediction to enable retraining."""

        try:
            # Initialize Redis store
            from redis_prediction_store import RedisPredictionStore

            redis_store = RedisPredictionStore()

            # Update the prediction label in Redis
            success = redis_store.update_prediction_label(prediction_id, request.user_label)

            if not success:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Prediction not found")

            # Get updated prediction data
            prediction_data = redis_store.get_prediction(prediction_id)

            return JSONResponse(
                {
                    "message": "Label updated successfully",
                    "prediction_id": prediction_id,
                    "user_label": request.user_label,
                    "session_id": prediction_data.get("session_id"),
                    "prediction": prediction_data,
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating prediction label: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error updating prediction label")

    @app.get("/session/{session_id}/predictions")
    async def get_session_predictions(session_id: str, corrected_only: bool = False, limit: int = 100) -> JSONResponse:
        """Get predictions for a session from Redis."""

        try:
            # Initialize Redis store
            from redis_prediction_store import RedisPredictionStore

            redis_store = RedisPredictionStore()

            # Get predictions from Redis
            predictions = redis_store.get_session_predictions(session_id, limit)

            # Filter for corrected predictions if requested
            if corrected_only:
                predictions = [p for p in predictions if p.get("is_corrected", False)]

            return JSONResponse(
                {
                    "session_id": session_id,
                    "predictions": predictions,
                    "total_count": len(predictions),
                    "corrected_only": corrected_only,
                    "source": "redis",
                }
            )

        except Exception as e:
            logger.error(f"Error retrieving session predictions: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error retrieving predictions")

    @app.post("/session/{session_id}/create_retraining_batch")
    async def create_retraining_batch(session_id: str) -> JSONResponse:
        """Create a retraining batch from corrected predictions."""

        # Get predictions DB path from session
        try:
            session = load_session(session_id)
            session_dir = Path(session.get("input_data", "")).parent
            db_path = session_dir / "predictions.db"
        except Exception:
            session_dir = Path("jobs") / f"session_{session_id}"
            db_path = session_dir / "predictions.db"

        if not db_path.exists():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="No predictions database found for this session"
            )

        with sqlite3.connect(db_path, timeout=10.0) as conn:
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")

            cursor = conn.cursor()

            # Count corrected predictions
            cursor.execute(
                """
                SELECT COUNT(*) FROM predictions 
                WHERE session_id = ? AND is_corrected = TRUE
            """,
                (session_id,),
            )
            correction_count = cursor.fetchone()[0]

            if correction_count == 0:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail="No corrected predictions found for retraining"
                )

            # Count total predictions
            cursor.execute(
                """
                SELECT COUNT(*) FROM predictions 
                WHERE session_id = ?
            """,
                (session_id,),
            )
            total_count = cursor.fetchone()[0]

            # Create retraining batch
            batch_id = str(uuid4())
            now = datetime.datetime.now(timezone.utc).isoformat()

            cursor.execute(
                """
                INSERT INTO retraining_batches (
                    batch_id, session_id, prediction_count, correction_count, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (batch_id, session_id, total_count, correction_count, now),
            )
            conn.commit()

        return JSONResponse(
            {
                "batch_id": batch_id,
                "session_id": session_id,
                "total_predictions": total_count,
                "corrected_predictions": correction_count,
                "created_at": now,
                "status": "pending",
                "message": f"Retraining batch created with {correction_count} corrected predictions",
            }
        )

    class PublishSessionRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())
        
        org_id: str  # Organization ID for subdirectory organization
        name: str  # Name for the published session (creates subdirectory under org_id)

    @app.post("/session/{id}/publish")
    async def publish_session_endpoint(id: str, request: PublishSessionRequest) -> JSONResponse:
        """
        Publish a session by moving it to /backplane/backplane1/sphere/PUBLISHED/<org_id>/<name>/<sessionId>.
        Moves both the session file and output directory.
        """
        try:
            result = publish_session(id, request.org_id, request.name)
            return JSONResponse(result)
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
        except FileNotFoundError as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error publishing session {id}: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    class DeprecateSessionRequest(BaseModel):
        model_config = ConfigDict(protected_namespaces=())

        warning_message: str  # Warning message about deprecation
        expiration_date: str  # ISO format date string when session will be removed

    @app.post("/session/{id}/deprecate")
    async def deprecate_session_endpoint(id: str, request: DeprecateSessionRequest) -> JSONResponse:
        """
        Deprecate a published session with a warning message and expiration date.
        The session remains available until the expiration date.
        """
        try:
            result = deprecate_session(id, request.warning_message, request.expiration_date)
            return JSONResponse(result)
        except FileNotFoundError as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error deprecating session {id}: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    @app.post("/session/{id}/unpublish")
    async def unpublish_session_endpoint(id: str) -> JSONResponse:
        """
        Unpublish a session by moving it back from /sphere/published/<sessionId>.
        """
        try:
            result = unpublish_session(id)
            return JSONResponse(result)
        except FileNotFoundError as e:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error unpublishing session {id}: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
    
    @app.post("/session/{id}/publish_partial_foundation")
    async def publish_partial_foundation_endpoint(id: str, request: PublishPartialFoundationRequest) -> JSONResponse:
        """
        Publish a checkpoint from in-progress training as a standalone foundation model.
        
        Creates a NEW foundation session from a checkpoint, preserving full provenance
        (parent session, checkpoint epoch, training progress). Useful for snapshotting
        good intermediate models while training continues.
        
        Args:
            id: Source session ID with ES training (in-progress or completed)
            request: Contains checkpoint_epoch, name, session_name_prefix, publish flag
        
        Returns:
            New foundation session ID, checkpoint metadata, provenance info
        """
        logger.info(f"Publishing partial foundation from {id}, epoch: {request.checkpoint_epoch}")
        
        try:
            # Load source session
            source_session = load_session(id)
            
            # Find the ES training job
            job_plan = source_session.get("job_plan", [])
            es_job = next((j for j in job_plan if j.get("job_type") == "train_es"), None)
            
            if not es_job:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Source session {id} has no ES training job"
                )
            
            es_job_id = es_job.get("job_id")
            if not es_job_id:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Source session ES job has no job_id"
                )
            
            # Find checkpoint file
            from lib.job_manager import get_job_output_path
            es_job_dir = get_job_output_path(es_job_id, session_id=id, job_type="train_es")
            
            checkpoint_path = None
            checkpoint_epoch_used = None
            
            if request.checkpoint_epoch is not None:
                # Use specific epoch checkpoint
                checkpoint_path = es_job_dir / f"checkpoint_inference_e-{request.checkpoint_epoch}.pt"
                if not checkpoint_path.exists():
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Checkpoint for epoch {request.checkpoint_epoch} not found: {checkpoint_path}"
                    )
                checkpoint_epoch_used = request.checkpoint_epoch
                logger.info(f"✅ Using epoch {checkpoint_epoch_used} checkpoint")
            else:
                # Find best checkpoint or latest
                best_checkpoint = es_job_dir / "checkpoint_inference_BEST.pt"
                if best_checkpoint.exists():
                    checkpoint_path = best_checkpoint
                    # Extract epoch from checkpoint
                    try:
                        import torch
                        ckpt = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu')
                        checkpoint_epoch_used = ckpt.get('epoch_idx') or ckpt.get('epoch', 0)
                    except:
                        checkpoint_epoch_used = 0
                    logger.info(f"✅ Using BEST checkpoint (epoch {checkpoint_epoch_used})")
                else:
                    # Find latest epoch checkpoint
                    epoch_checkpoints = sorted(es_job_dir.glob("checkpoint_inference_e-*.pt"))
                    if not epoch_checkpoints:
                        raise HTTPException(
                            status_code=HTTPStatus.NOT_FOUND,
                            detail=f"No checkpoints found in {es_job_dir}"
                        )
                    checkpoint_path = epoch_checkpoints[-1]
                    import re
                    match = re.search(r'e-(\d+)\.pt', checkpoint_path.name)
                    checkpoint_epoch_used = int(match.group(1)) if match else 0
                    logger.info(f"✅ Using latest checkpoint (epoch {checkpoint_epoch_used})")
            
            # Reconstruct ES from checkpoint
            from lib.featrix.neural.io_utils import _reconstruct_es_from_checkpoint_dict
            import torch
            
            logger.info(f"🔄 Reconstructing ES from checkpoint...")
            checkpoint_dict = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
            es = _reconstruct_es_from_checkpoint_dict(checkpoint_dict, str(es_job_dir), logger=logger)
            
            if not es:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Failed to reconstruct embedding space from checkpoint"
                )
            
            # Generate new session ID
            import uuid
            if request.session_name_prefix:
                new_session_id = f"{request.session_name_prefix}-{uuid.uuid4()}"
            else:
                new_session_id = str(uuid.uuid4())
            
            logger.info(f"📝 Creating foundation session {new_session_id}...")
            
            # Create foundation session directory
            session_dir = Path(config.session_dir) / new_session_id
            session_dir.mkdir(exist_ok=True, parents=True)
            
            # Save ES as foundation model
            es_pickle_path = session_dir / get_embedding_space_pickle_filename()
            # Use write_embedding_space_pickle for proper saving
            write_embedding_space_pickle(es, str(session_dir), filename=get_embedding_space_pickle_filename(), show_progress=False)
            es_pickle_path = session_dir / get_embedding_space_pickle_filename()
            
            file_size_mb = es_pickle_path.stat().st_size / (1024**2)
            logger.info(f"✅ Saved foundation ES: {file_size_mb:.1f} MB")
            
            # Copy strings cache if available
            strings_cache_path = None
            source_strings_cache = source_session.get('strings_cache')
            if source_strings_cache and Path(source_strings_cache).exists():
                new_strings_cache_path = session_dir / "strings.sqlite3"
                import shutil
                shutil.copy2(source_strings_cache, new_strings_cache_path)
                strings_cache_path = str(new_strings_cache_path)
                cache_size_mb = new_strings_cache_path.stat().st_size / (1024**2)
                logger.info(f"✅ Copied strings cache: {cache_size_mb:.1f} MB")
            
            # Extract provenance metadata from checkpoint
            provenance_metadata = {
                'parent_session_id': id,
                'parent_session_name': source_session.get('name'),
                'checkpoint_epoch': checkpoint_epoch_used,
                'checkpoint_path': str(checkpoint_path),
                'published_at': datetime.datetime.now().isoformat(),
                'published_from': 'partial_foundation',
            }
            
            # Get training progress from checkpoint
            try:
                import torch
                ckpt_data = torch.load(str(checkpoint_path), weights_only=False, map_location='cpu')
                
                if 'validation_loss' in ckpt_data:
                    provenance_metadata['validation_loss_at_checkpoint'] = float(ckpt_data['validation_loss'])
                if 'training_loss' in ckpt_data:
                    provenance_metadata['training_loss_at_checkpoint'] = float(ckpt_data['training_loss'])
                
                # Calculate training progress
                parent_n_epochs = source_session.get('n_epochs')
                if parent_n_epochs and checkpoint_epoch_used:
                    progress_pct = (checkpoint_epoch_used / parent_n_epochs) * 100
                    provenance_metadata['parent_total_epochs'] = parent_n_epochs
                    provenance_metadata['training_progress_percent'] = round(progress_pct, 1)
                    provenance_metadata['parent_training_complete'] = checkpoint_epoch_used >= parent_n_epochs
                
            except Exception as e:
                logger.warning(f"Could not extract checkpoint metadata: {e}")
            
            # Create foundation session document
            from lib.session_manager import create_session
            foundation_session = create_session(
                input_filename=None,  # Foundation models have no input data
                session_id=new_session_id,
                session_type="foundation_model",
                name=request.name,
                user_metadata=source_session.get('user_metadata')
            )
            
            # Store provenance and ES references
            foundation_session['embedding_space'] = str(es_pickle_path)
            foundation_session['strings_cache'] = strings_cache_path
            foundation_session['provenance'] = provenance_metadata
            foundation_session['d_model'] = getattr(es, 'd_model', None)
            foundation_session['n_epochs'] = checkpoint_epoch_used  # Epochs trained when snapshotted
            foundation_session['column_spec'] = getattr(es, 'column_spec', {})
            foundation_session['col_order'] = getattr(es, 'col_order', [])
            
            # Save session
            save_session(session_id=new_session_id, session_doc=foundation_session, exist_ok=True)
            logger.info(f"✅ Created foundation session: {new_session_id}")
            
            # Optionally publish to /backplane/backplane1/sphere/PUBLISHED/
            published_path = None
            if request.publish:
                if not request.org_id:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail="org_id is required when publish=True"
                    )
                try:
                    logger.info(f"📦 Publishing to /backplane/backplane1/sphere/PUBLISHED/{request.org_id}/{request.name}/...")
                    publish_result = publish_session(new_session_id, request.org_id, request.name)
                    published_path = publish_result.get('published_path')
                    logger.info(f"✅ Published to: {published_path}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not publish to /backplane/backplane1/sphere/PUBLISHED/: {e}")
                    # Continue anyway - session is created, just not published
            
            return JSONResponse(
                {
                    "message": f"Published partial foundation from epoch {checkpoint_epoch_used}",
                    "foundation_session_id": new_session_id,
                    "source_session_id": id,
                    "checkpoint_epoch": checkpoint_epoch_used,
                    "published_path": published_path,
                    "provenance": provenance_metadata,
                    "embedding_space_path": str(es_pickle_path),
                    "strings_cache_path": strings_cache_path,
                },
                status_code=HTTPStatus.CREATED,
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error publishing partial foundation from {id}: {e}", exc_info=True)
            post_slack_alert(f"session={id}; error publishing partial foundation: {str(e)}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Error publishing partial foundation: {str(e)}",
            )

    @app.post("/backend-code-update-ping")
    async def github_webhook(request: Request) -> JSONResponse:
        """GitHub webhook to signal that new code has been pushed. Testing webhook system again."""
        try:
            # Create the flag file locally as the current user
            flags_dir = "/sphere/flags"
            flag_file = os.path.join(flags_dir, "NEED_GITPULL")
            try:
                os.makedirs(flags_dir, exist_ok=True)
                with open(flag_file, "a"):
                    os.utime(flag_file, None)
            except Exception as e:
                logger.error(f"Failed to create flag file locally: {e}")
                raise Exception(f"Failed to create flag file locally: {e}")

            # Set 777 permissions
            try:
                os.chmod(flag_file, 0o777)
            except Exception as e:
                logger.warning(f"Failed to set permissions on flag file: {e}")

            logger.info(
                "GitHub webhook received - created /sphere/flags/NEED_GITPULL flag file on churro as mitch user"
            )

            # Log the webhook payload for debugging
            try:
                payload = await request.json()
                if payload and "head_commit" in payload:
                    commit_msg = payload["head_commit"].get("message", "")[:100]
                    logger.info(f"New commit: {commit_msg}")
            except Exception:
                pass

            return JSONResponse(
                {
                    "status": "success",
                    "message": "Git pull flag created on churro as mitch user",
                    "flag_file": "/sphere/flags/NEED_GITPULL",
                }
            )

        except Exception as e:
            logger.error(f"Error handling GitHub webhook: {e}")
            post_slack_alert(f"GitHub webhook error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to handle webhook: {e}")

    def sanitize_predictor_path(full_path: str) -> str:
        """
        Remove sensitive server path prefixes from predictor paths before returning to clients.

        Args:
            full_path: Full server path like "/sphere/app/featrix_output/train_single_predictor_20250708-162950_8ccd07/single_predictor.pickle"

        Returns:
            Sanitized path like "train_single_predictor_20250708-162950_8ccd07/single_predictor.pickle"
        """
        # Remove common server path prefixes
        prefixes_to_remove = [
            "/sphere/app/featrix_output/",
            "/sphere/app/",
            "featrix_output/",
        ]

        sanitized_path = full_path
        for prefix in prefixes_to_remove:
            if sanitized_path.startswith(prefix):
                sanitized_path = sanitized_path[len(prefix) :]
                break

        return sanitized_path

    @app.get("/admin/predictor_cache")
    async def admin_predictor_cache(request: Request, _: None = Depends(require_private_network)):
        """View predictor cache statistics."""

        cache_stats = predictor_cache.stats()

        # Add memory usage information if available
        try:
            import psutil

            process = psutil.Process()
            memory_info = {
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 1),
                "memory_percent": round(process.memory_percent(), 1),
            }
        except ImportError:
            memory_info = {"error": "psutil not available"}

        # Add GPU memory info via subprocess (API workers are CPU-only)
        gpu_info = get_gpu_stats_via_subprocess()

        return JSONResponse(
            {
                "cache_stats": cache_stats,
                "memory_info": memory_info,
                "gpu_info": gpu_info,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    @app.post("/admin/predictor_cache/clear")
    async def admin_clear_predictor_cache(request: Request, _: None = Depends(require_private_network)):
        """Clear the predictor cache and free GPU memory."""

        old_stats = predictor_cache.stats()
        predictor_cache.clear()

        # Force garbage collection
        import gc

        gc.collect()

        # Clear GPU cache (API workers are CPU-only, so this is a no-op)
        # GPU cache is managed by Celery workers, not API workers
        # Keeping this for API compatibility but it does nothing

        return JSONResponse(
            {
                "message": "Predictor cache cleared successfully",
                "previous_cache_size": old_stats["size"],
                "cleared_predictors": old_stats["cached_predictors"],
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    @app.get("/admin/queue_summary")
    async def admin_queue_summary(request: Request, _: None = Depends(require_private_network)):
        """Get detailed summary of all queue states (authorized IP only)."""

        try:
            queue_summary = get_queue_summary()

            # Add overall system status
            total_ready = sum(q.get("ready_jobs", 0) for q in queue_summary.values())
            total_running = sum(q.get("running_jobs", 0) for q in queue_summary.values())
            active_queues = sum(1 for q in queue_summary.values() if q.get("status") == "active")

            return JSONResponse(
                {
                    "queue_summary": queue_summary,
                    "system_overview": {
                        "total_ready_jobs": total_ready,
                        "total_running_jobs": total_running,
                        "active_queues": active_queues,
                        "total_queues": len(queue_summary),
                        "system_busy": total_running > 0,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error getting queue summary: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting queue summary: {str(e)}")

    @app.get("/admin/monitor/crashes")
    async def get_recent_crashes() -> JSONResponse:
        """Return recent crashes from local database."""
        try:
            from lib.crash_tracker import get_recent_crashes, get_crash_stats
            
            crashes = get_recent_crashes(limit=50, include_acknowledged=False)
            stats = get_crash_stats()
            
            return JSONResponse({
                "crashes": crashes,
                "stats": stats,
                "count": len(crashes)
            })
        except Exception as e:
            logger.error(f"Error getting crashes: {e}")
            return JSONResponse(
                {"crashes": [], "stats": {}, "count": 0, "error": str(e)},
                status_code=500
            )
    
    @app.post("/admin/monitor/crashes/{crash_id}/acknowledge")
    async def acknowledge_crash_endpoint(crash_id: str) -> JSONResponse:
        """Acknowledge a crash."""
        try:
            from lib.crash_tracker import acknowledge_crash
            
            success = acknowledge_crash(crash_id)
            if success:
                return JSONResponse({"success": True, "crash_id": crash_id})
            else:
                return JSONResponse(
                    {"success": False, "error": "Crash not found"},
                    status_code=404
                )
        except Exception as e:
            logger.error(f"Error acknowledging crash: {e}")
            return JSONResponse(
                {"success": False, "error": str(e)},
                status_code=500
            )
    
    # Cache for GPU processes (reduces nvidia-smi + psutil overhead)
    _gpu_processes_cache = {"data": None, "timestamp": 0}
    
    def get_gpu_processes_with_job_info():
        """
        Parse nvidia-smi to get all GPU compute processes and map them to job IDs.
        
        Returns list of dicts with: pid, gpu_memory_mb, job_id, job_type, session_id, command
        """
        import subprocess
        import re
        import psutil
        import time
        
        # Check cache (1 second TTL - nvidia-smi is expensive)
        now = time.time()
        if _gpu_processes_cache["data"] and (now - _gpu_processes_cache["timestamp"]) < 1.0:
            return _gpu_processes_cache["data"]
        
        gpu_processes = []
        
        try:
            # Get GPU processes from nvidia-smi
            result = subprocess.run(
                ['nvidia-smi', '--query-compute-apps=pid,used_memory', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return gpu_processes
            
            # Parse nvidia-smi output
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                
                try:
                    pid = int(parts[0].strip())
                    gpu_mem_mb = int(parts[1].strip())
                except (ValueError, IndexError):
                    continue
                
                # Get process info
                proc_info = {
                    'pid': pid,
                    'gpu_memory_mb': gpu_mem_mb,
                    'job_id': None,
                    'job_type': None,
                    'session_id': None,
                    'command': None,
                    'cpu_percent': None,
                    'memory_rss_gb': None,
                    'num_threads': None
                }
                
                # Try to get process details and extract job info
                try:
                    proc = psutil.Process(pid)
                    cmdline = proc.cmdline()
                    proc_info['command'] = ' '.join(cmdline) if cmdline else None
                    
                    # Extract job_id from command line
                    # Pattern: --job-id <job_id> or FEATRIX_JOB_ID env var
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        
                        # Try to find --job-id argument
                        job_id_match = re.search(r'--job-id\s+([a-f0-9\-]+)', cmdline_str)
                        if job_id_match:
                            proc_info['job_id'] = job_id_match.group(1)
                        
                        # Determine job type from command
                        if 'es_training_wrapper.py' in cmdline_str or 'es_training.py' in cmdline_str:
                            proc_info['job_type'] = 'train_es'
                        elif 'sp_training.py' in cmdline_str or 'single_predictor' in cmdline_str:
                            proc_info['job_type'] = 'train_single_predictor'
                        elif 'celery' in cmdline_str or 'worker' in cmdline_str:
                            proc_info['job_type'] = 'celery_worker'
                    
                    # Try to get job_id from environment if not found in cmdline
                    if not proc_info['job_id']:
                        try:
                            environ = proc.environ()
                            proc_info['job_id'] = environ.get('FEATRIX_JOB_ID')
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass
                    
                    # Get process metrics
                    try:
                        # CPU percent needs interval > 0 to get real data (not zero)
                        # Use interval=0.1 for fast but accurate measurement
                        proc_info['cpu_percent'] = proc.cpu_percent(interval=0.1)
                        mem_info = proc.memory_info()
                        proc_info['memory_rss_gb'] = mem_info.rss / (1024**3)
                        proc_info['num_threads'] = proc.num_threads()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process doesn't exist or we don't have access
                    pass
                
                gpu_processes.append(proc_info)
        
        except Exception as e:
            logger.warning(f"Error getting GPU processes: {e}")
        
        # Update cache
        _gpu_processes_cache["data"] = gpu_processes
        _gpu_processes_cache["timestamp"] = now
        
        return gpu_processes
    
    # Cache for training jobs endpoint (reduces load from 5-second polling)
    _training_jobs_cache = {"data": None, "timestamp": 0}
    
    @app.get("/admin/monitor/training_jobs")
    async def get_training_jobs_local() -> JSONResponse:
        """Return information about currently running training jobs on this compute node."""
        try:
            import re
            import time
            
            # Check cache (2 second TTL - endpoint is polled every 5 seconds)
            now = time.time()
            if _training_jobs_cache["data"] and (now - _training_jobs_cache["timestamp"]) < 2.0:
                return JSONResponse(_training_jobs_cache["data"])

            training_jobs = []
            
            # Get GPU processes first (all processes using GPU)
            gpu_processes = get_gpu_processes_with_job_info()

            # Get all running jobs from training queues (OPTIMIZED with status filter)
            for job_type in ["train_es", "train_single_predictor"]:
                try:
                    # OPTIMIZATION: Use status_filter to query only RUNNING jobs from Redis SET
                    for job in iterate_over_jobs_in_queue(job_type, status_filter=JobStatus.RUNNING):
                        try:
                            job_id = job.get("job_id")
                            if not job_id:
                                continue

                            session_id = job.get("session_id")
                            if not session_id:
                                continue

                            # Get job type from job, fallback to job_type parameter
                            job_type_value = job.get("type") or job_type

                            # Get job output directory using the proper function
                            job_output_dir = get_job_output_path(job_id, session_id=session_id, job_type=job_type)
                            log_file = job_output_dir / "logs" / "stdout.log"

                            # Extract information
                            job_info = {
                                "job_id": job_id,
                                "session_id": session_id,
                                "job_type": job_type,
                                "name": job.get("name") or session_id,
                                "epoch_count": 0,
                                "initial_val_loss": None,
                                "current_val_loss": None,
                                "log_lines": [],
                                # Process metrics (will be populated below)
                                "pid": None,
                                "cpu_percent": None,
                                "memory_rss_gb": None,
                                "memory_vms_gb": None,
                                "gpu_memory_mb": None,
                                "num_threads": None,
                            }

                            # Get last 10 log lines
                            if log_file.exists():
                                try:
                                    with open(log_file, encoding="utf-8", errors="ignore") as f:
                                        lines = f.readlines()
                                        job_info["log_lines"] = [line.rstrip("\n\r") for line in lines[-10:]]
                                except Exception as e:
                                    job_info["log_lines"] = [f"Error reading log: {e}"]

                            # Extract losses and epoch from log (OPTIMIZED: read only last 200 lines)
                            if log_file.exists():
                                try:
                                    # Patterns to match validation loss
                                    # ES training: [epoch=1] VAL LOSS: 0.1234
                                    epoch_val_pattern = re.compile(r"\[epoch=(\d+)\].*?VAL LOSS:\s+([\d.]+)")
                                    # ES training: Epoch 1/100 ... validation_loss=0.1234
                                    train_epoch_pattern = re.compile(r"Epoch (\d+)/\d+.*?validation_loss=([\d.]+)")
                                    # Single predictor: 🎯 SP Epoch 1/10: ... validation_loss=0.1234
                                    sp_epoch_pattern = re.compile(r"SP Epoch (\d+)/\d+.*?validation_loss=([\d.]+)")
                                    # Single predictor from single_predictor.py: [epoch=1/10] Train Loss: ... | Val Loss: 0.1234
                                    sp_epoch_log_pattern = re.compile(
                                        r"\[epoch=(\d+)/\d+\].*?Val Loss:\s+([\d.]+)", re.IGNORECASE
                                    )

                                    # OPTIMIZATION: Only read last 200 lines instead of entire file
                                    # This is much faster for large log files (can be 100s of MB)
                                    with open(log_file, encoding="utf-8", errors="ignore") as f:
                                        # Seek to end and read backwards
                                        try:
                                            # Try to seek to a reasonable position (last ~50KB)
                                            f.seek(0, 2)  # End of file
                                            file_size = f.tell()
                                            # Read last 50KB or entire file if smaller
                                            seek_pos = max(0, file_size - 50000)
                                            f.seek(seek_pos)
                                            # Skip partial line if we seeked
                                            if seek_pos > 0:
                                                f.readline()
                                            lines = f.readlines()
                                        except:
                                            # Fallback: read entire file
                                            f.seek(0)
                                            lines = f.readlines()
                                        
                                        for line in lines:
                                            # Try different patterns
                                            match = (
                                                epoch_val_pattern.search(line)
                                                or train_epoch_pattern.search(line)
                                                or sp_epoch_pattern.search(line)
                                                or sp_epoch_log_pattern.search(line)
                                            )
                                            if match:
                                                epoch = int(match.group(1))
                                                val_loss = float(match.group(2))
                                                if job_info["initial_val_loss"] is None:
                                                    job_info["initial_val_loss"] = val_loss
                                                if epoch >= job_info["epoch_count"]:
                                                    job_info["epoch_count"] = epoch
                                                    job_info["current_val_loss"] = val_loss
                                except Exception:
                                    pass

                            # Get process metrics (CPU, RAM, VRAM)
                            # First check if we already have this job_id in GPU processes
                            gpu_proc_match = next((gp for gp in gpu_processes if gp['job_id'] == job_id), None)
                            
                            if gpu_proc_match:
                                # Use GPU process data
                                job_info["pid"] = gpu_proc_match['pid']
                                job_info["cpu_percent"] = gpu_proc_match['cpu_percent']
                                job_info["memory_rss_gb"] = gpu_proc_match['memory_rss_gb']
                                job_info["gpu_memory_mb"] = gpu_proc_match['gpu_memory_mb']
                                job_info["num_threads"] = gpu_proc_match['num_threads']
                            else:
                                # Fallback: Search for process manually
                                try:
                                    import psutil
                                    import glob
                                    
                                    # CRITICAL: First try Celery mapping files (more reliable)
                                    job_pid = None
                                    try:
                                        mapping_files = glob.glob('/tmp/featrix-celery-*.json')
                                        for mapping_file in mapping_files:
                                            try:
                                                with open(mapping_file, 'r') as f:
                                                    import json
                                                    mapping = json.load(f)
                                                    if mapping.get('job_id') == job_id:
                                                        job_pid = mapping.get('training_pid')
                                                        logger.debug(f"✅ Found training PID {job_pid} for job {job_id} from mapping file")
                                                        break
                                            except Exception:
                                                continue
                                    except Exception as e:
                                        logger.debug(f"Could not read mapping files: {e}")
                                    
                                    # REMOVED: psutil.process_iter() fallback - TOO SLOW (3+ seconds on busy systems)
                                    # If mapping file doesn't exist, skip process metrics rather than scan all processes
                                    
                                    if job_pid:
                                        proc = psutil.Process(job_pid)
                                        job_info["pid"] = job_pid
                                        
                                        # CPU usage (non-blocking)
                                        job_info["cpu_percent"] = proc.cpu_percent()
                                        
                                        # Memory info
                                        mem_info = proc.memory_info()
                                        job_info["memory_rss_gb"] = mem_info.rss / (1024**3)
                                        job_info["memory_vms_gb"] = mem_info.vms / (1024**3)
                                        
                                        # Thread count
                                        job_info["num_threads"] = proc.num_threads()
                                        
                                        # GPU memory from GPU processes list if available
                                        gpu_match = next((gp for gp in gpu_processes if gp['pid'] == job_pid), None)
                                        if gpu_match:
                                            job_info["gpu_memory_mb"] = gpu_match['gpu_memory_mb']
                                except Exception as e:
                                    logger.debug(f"Could not get process metrics for job {job_id}: {e}")
                            
                            training_jobs.append(job_info)
                        except Exception as e:
                            logger.warning(f"⚠️  Error processing job {job_id}: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"⚠️  Error getting jobs of type {job_type}: {e}")
                    continue

            # Build response
            response_data = {
                "training_jobs": training_jobs,
                "count": len(training_jobs),
                "gpu_processes": gpu_processes,
                "gpu_process_count": len(gpu_processes)
            }
            
            # Update cache
            _training_jobs_cache["data"] = response_data
            _training_jobs_cache["timestamp"] = now
            
            return JSONResponse(response_data)
        except Exception as e:
            logger.error(f"❌ Error in get_training_jobs_local: {e}")

            traceback.print_exc()
            return JSONResponse({
                "training_jobs": [],
                "count": 0,
                "gpu_processes": [],
                "gpu_process_count": 0,
                "error": str(e)
            }), 500

    @app.get("/admin/prediction_progress/{job_id}")
    async def admin_get_prediction_progress(request: Request, job_id: str, _: None = Depends(require_private_network)):
        """Get raw Redis progress data for a prediction job (authorized IP only)."""

        try:
            import redis

            redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
            redis_key = f"prediction_progress:{job_id}"

            # Get progress data
            progress_data = redis_client.get(redis_key)

            if progress_data:
                progress_info = json.loads(progress_data)

                # Add Redis key TTL info
                ttl = redis_client.ttl(redis_key)
                progress_info["redis_ttl_seconds"] = ttl

                return JSONResponse(
                    {"job_id": job_id, "redis_key": redis_key, "found": True, "progress": progress_info}
                )
            else:
                return JSONResponse(
                    {
                        "job_id": job_id,
                        "redis_key": redis_key,
                        "found": False,
                        "message": "No progress data found in Redis",
                    }
                )

        except Exception as e:
            logger.error(f"Error querying Redis progress: {e}")
            raise HTTPException(status_code=500, detail=f"Error querying progress: {str(e)}")

    @app.get("/admin/monitor/training_metrics/{job_type}/{job_id}")
    async def get_training_metrics(
        request: Request, 
        job_type: str, 
        job_id: str, 
        start_epoch: int = 0,
        limit: int = 1000,
        _: None = Depends(require_private_network)
    ):
        """
        Get detailed training metrics timeline for a specific job.
        
        Returns epoch-by-epoch metrics including:
        - For ES training: learning_rate, train_loss, validation_loss, spread, joint, marginal, marginal_weighted
        - For predictor: learning_rate, train_loss, validation_loss, auc, accuracy, f1, etc.
        
        Args:
            job_type: Job queue type (train_es or train_single_predictor)
            job_id: Job ID
            start_epoch: Starting epoch (default 0)
            limit: Maximum number of epochs to return (default 1000)
        """
        try:
            from redis_job_progress import get_redis_job_progress
            
            redis_progress = get_redis_job_progress()
            if not redis_progress.redis_available:
                return JSONResponse({
                    "job_id": job_id,
                    "job_type": job_type,
                    "found": False,
                    "error": "Redis not available",
                    "metrics": []
                }, status_code=503)
            
            metrics = redis_progress.get_training_metrics(
                job_type=job_type,
                job_id=job_id,
                start_epoch=start_epoch,
                limit=limit
            )
            
            return JSONResponse({
                "job_id": job_id,
                "job_type": job_type,
                "found": len(metrics) > 0,
                "count": len(metrics),
                "metrics": metrics
            })
            
        except Exception as e:
            logger.error(f"Error retrieving training metrics: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error retrieving training metrics: {str(e)}")

    @app.get("/admin/monitor/job_logs/{job_type}/{job_id}")
    async def get_job_logs(
        request: Request,
        job_type: str,
        job_id: str,
        limit: int = 100,
        _: None = Depends(require_private_network)
    ):
        """
        Get recent log messages and tracebacks for a specific job.
        
        Args:
            job_type: Job queue type
            job_id: Job ID
            limit: Maximum number of log entries to return (default 100)
        """
        try:
            from pathlib import Path
            from redis_job_progress import get_redis_job_progress
            
            # Get logs from Redis (recent in-memory logs)
            redis_progress = get_redis_job_progress()
            redis_logs = []
            if redis_progress.redis_available:
                redis_logs = redis_progress.get_log_messages(job_type, job_id, limit=limit)
            
            # Get job output directory for file-based logs
            from lib.job_manager import load_job
            job_data = load_job(job_id)
            
            file_logs = []
            traceback_content = None
            
            if job_data:
                session_id = job_data.get('session_id')
                if session_id:
                    from lib.job_manager import get_job_output_path
                    job_output_dir = get_job_output_path(job_id, session_id=session_id, job_type=job_type)
                    
                    # Read stdout.log
                    log_file = job_output_dir / "logs" / "stdout.log"
                    if log_file.exists():
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                # Get last N lines
                                file_logs = [line.rstrip('\n\r') for line in lines[-limit:]]
                        except Exception as e:
                            logger.warning(f"Failed to read log file: {e}")
                    
                    # Check for traceback file
                    traceback_file = job_output_dir / "logs" / "traceback.log"
                    if traceback_file.exists():
                        try:
                            with open(traceback_file, 'r', encoding='utf-8', errors='ignore') as f:
                                traceback_content = f.read()
                        except Exception as e:
                            logger.warning(f"Failed to read traceback file: {e}")
            
            return JSONResponse({
                "job_id": job_id,
                "job_type": job_type,
                "redis_logs": redis_logs,
                "file_logs": file_logs,
                "traceback": traceback_content,
                "has_traceback": traceback_content is not None
            })
            
        except Exception as e:
            logger.error(f"Error retrieving job logs: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error retrieving job logs: {str(e)}")

    # ===================================================================
    # QUERY SCHEMA - Async LLM-based schema analysis
    # ===================================================================
    
    @app.post("/query-schema/async")
    async def query_schema_async(request: Request) -> JSONResponse:
        """
        Submit an async schema analysis job.
        
        Returns immediately with job_id and status_url for polling.
        Worker processes job from Redis queue.
        """
        from uuid import uuid4
        from pathlib import Path
        import time
        
        try:
            body = await request.json()
            columns = body.get("columns", [])
            question = body.get("question", "")
            
            if not columns:
                raise HTTPException(status_code=400, detail="columns array is required")
            
            # Generate job ID
            job_id = str(uuid4())
            
            # Create job directory
            job_dir = Path("/tmp/query-schema-jobs")
            job_dir.mkdir(parents=True, exist_ok=True)
            
            # Store job data
            job_file = job_dir / f"job_{job_id}.json"
            job_data = {
                "job_id": job_id,
                "status": "queued",
                "columns": columns,
                "question": question,
                "submitted_at": time.time(),
                "runtime_seconds": None,
                "result": None,
                "error": None
            }
            
            with open(job_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            # Add to Redis queue
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            r.rpush("query-schema-queue", job_id)
            
            logger.info(f"✅ Queued schema analysis job {job_id} ({len(columns)} columns)")
            
            return JSONResponse({
                "job_id": job_id,
                "status": "queued",
                "status_url": f"/query-schema/status/{job_id}"
            })
            
        except Exception as e:
            logger.error(f"❌ Error queuing schema analysis job: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/query-schema/status/{job_id}")
    async def query_schema_status(job_id: str) -> JSONResponse:
        """
        Poll status of a schema analysis job.
        
        Returns status: queued|processing|completed|failed
        Includes runtime and result when completed.
        """
        from pathlib import Path
        
        try:
            job_file = Path(f"/tmp/query-schema-jobs/job_{job_id}.json")
            
            if not job_file.exists():
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            response = {
                "job_id": job_id,
                "status": job_data["status"],
                "runtime_seconds": job_data.get("runtime_seconds")
            }
            
            if job_data["status"] == "completed":
                response["result"] = job_data.get("result")
            elif job_data["status"] == "failed":
                response["error"] = job_data.get("error")
            
            return JSONResponse(response)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting job status for {job_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/query-schema/result/{job_id}")
    async def query_schema_result(job_id: str) -> JSONResponse:
        """
        Get final result of a schema analysis job.
        
        Returns same format as synchronous endpoint.
        Raises 404 if job not found, 425 if not completed yet.
        """
        from pathlib import Path
        
        try:
            job_file = Path(f"/tmp/query-schema-jobs/job_{job_id}.json")
            
            if not job_file.exists():
                raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
            
            with open(job_file, 'r') as f:
                job_data = json.load(f)
            
            if job_data["status"] == "completed":
                return JSONResponse(job_data["result"])
            elif job_data["status"] == "failed":
                raise HTTPException(status_code=500, detail=job_data.get("error", "Job failed"))
            else:
                # Job still processing or queued
                raise HTTPException(
                    status_code=425,  # Too Early
                    detail=f"Job not ready yet. Status: {job_data['status']}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting job result for {job_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return app


# NOTE: Do NOT create app at module level when using uvicorn --factory mode
# The --factory flag will call create_app() for each worker process
# Creating it here causes it to be called multiple times and can cause deadlocks
# 
# If you need a module-level app instance (e.g. for testing), use:
#   if __name__ != "__main__":
#       app = create_app()
# 
# app = create_app()  # REMOVED - causes deadlock with --factory and --workers
