# -*- coding: utf-8 -*-
"""
Simple in-memory string cache using only @lru_cache + string server.
Uses Redis for cross-process caching (workers can read from Redis).
"""
import logging
import time
from functools import lru_cache
import torch
import numpy as np
import hashlib

logger = logging.getLogger(__name__)

# Redis connection (lazy init)
_redis_client = None
_redis_init_attempted = False
REDIS_EMBEDDING_PREFIX = "featrix:emb:"  # Key prefix for embeddings
REDIS_EMBEDDING_TTL = 86400 * 7  # 7 days TTL


def _get_redis_client():
    """Get or create Redis client. Returns None if Redis unavailable."""
    global _redis_client, _redis_init_attempted
    
    if _redis_client is not None:
        return _redis_client
    
    if _redis_init_attempted:
        return None
    
    _redis_init_attempted = True
    
    try:
        import redis
        # Use db=2 to avoid conflicts with other Redis usage
        _redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=2,
            socket_timeout=2,
            socket_connect_timeout=2,
            decode_responses=False  # We store binary data
        )
        _redis_client.ping()
        logger.info("✅ Redis connection established for string embedding cache")
        return _redis_client
    except Exception as e:
        logger.warning(f"⚠️  Redis not available for embedding cache: {e}")
        _redis_client = None
        return None


def _redis_key(string_value):
    """Generate Redis key for a string. Uses hash to handle long strings."""
    # Hash the string to get a fixed-length key
    string_hash = hashlib.sha256(string_value.encode('utf-8')).hexdigest()[:32]
    return f"{REDIS_EMBEDDING_PREFIX}{string_hash}"


def _get_from_redis_cache(sentence_text):
    """
    Check Redis for a cached embedding.
    
    Returns:
        list: Embedding as list of floats, or None if not found
    """
    try:
        client = _get_redis_client()
        if client is None:
            return None
        
        key = _redis_key(sentence_text)
        embedding_blob = client.get(key)
        
        if embedding_blob is not None:
            # Convert bytes back to list of floats
            embedding_array = np.frombuffer(embedding_blob, dtype=np.float32)
            return embedding_array.tolist()
        
        return None
    except Exception as e:
        logger.debug(f"Redis cache lookup failed: {e}")
        return None


def _add_to_redis_cache(sentence_text, embedding_list):
    """
    Add embedding to Redis cache.
    
    Args:
        sentence_text: The string
        embedding_list: Embedding as list of floats
        
    Returns:
        bool: True if added successfully
    """
    try:
        client = _get_redis_client()
        if client is None:
            return False
        
        key = _redis_key(sentence_text)
        embedding_array = np.array(embedding_list, dtype=np.float32)
        embedding_blob = embedding_array.tobytes()
        
        client.setex(key, REDIS_EMBEDDING_TTL, embedding_blob)
        return True
    except Exception as e:
        logger.debug(f"Redis cache add failed: {e}")
        return False


def _add_batch_to_redis_cache(embeddings_dict):
    """
    Add multiple embeddings to Redis cache using pipeline for efficiency.
    
    Args:
        embeddings_dict: dict of {string: embedding_list}
        
    Returns:
        int: Number of embeddings added
    """
    try:
        client = _get_redis_client()
        if client is None:
            return 0
        
        pipe = client.pipeline()
        count = 0
        
        for sentence_text, embedding_list in embeddings_dict.items():
            key = _redis_key(sentence_text)
            embedding_array = np.array(embedding_list, dtype=np.float32)
            embedding_blob = embedding_array.tobytes()
            pipe.setex(key, REDIS_EMBEDDING_TTL, embedding_blob)
            count += 1
        
        pipe.execute()
        return count
    except Exception as e:
        logger.warning(f"Redis batch add failed: {e}")
        return 0


def get_redis_cache_stats():
    """Get Redis cache statistics for debugging."""
    try:
        client = _get_redis_client()
        if client is None:
            return {"status": "unavailable"}
        
        # Count keys with our prefix
        keys = client.keys(f"{REDIS_EMBEDDING_PREFIX}*")
        return {
            "status": "connected",
            "embedding_count": len(keys),
            "prefix": REDIS_EMBEDDING_PREFIX,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Legacy shared memory functions - now just redirect to Redis
def _get_from_shared_memory_cache(sentence_text):
    """DEPRECATED: Use _get_from_redis_cache instead. This is a compatibility shim."""
    return _get_from_redis_cache(sentence_text)


def log_shared_memory_cache_status():
    """Log the status of the Redis embedding cache for debugging."""
    stats = get_redis_cache_stats()
    if stats["status"] == "connected":
        logger.info(f"📦 REDIS EMBEDDING CACHE: {stats['embedding_count']} entries cached")
    elif stats["status"] == "unavailable":
        logger.warning("📦 REDIS EMBEDDING CACHE: NOT AVAILABLE")
    else:
        logger.warning(f"📦 REDIS EMBEDDING CACHE: Error - {stats.get('error', 'unknown')}")


# Track string server outage state (for Slack notifications)
_STRING_SERVER_OUTAGE_NOTIFIED = False
_STRING_SERVER_RECOVERY_NOTIFIED = False
_STRING_SERVER_SLACK_ALERT_SENT = False


# Module-level cache for string embeddings
# Key: (client_id, sentence_text) -> embedding_list
# This allows @lru_cache to work properly (doesn't work well with instance methods)
@lru_cache(maxsize=131072)  # Increased from 32768 (2^15) to 131072 (2^17) for better hit rates
def _cached_encode(client_id, sentence_text, client_encode_func_key):
    """
    Cached encoding function at module level with retry logic for string server outages.
    On firmware boxes: waits up to 30 minutes, sends Slack alert after 2 minutes.
    On development: waits up to 10 minutes.
    
    Args:
        client_id: Unique ID for the string server client (for cache keying)
        sentence_text: String to encode
        client_encode_func_key: Key to retrieve the encode function (ignored, just for cache invalidation)
        
    Returns:
        list: Embedding vector as list of floats
    """
    global _STRING_SERVER_OUTAGE_NOTIFIED, _STRING_SERVER_RECOVERY_NOTIFIED, _STRING_SERVER_SLACK_ALERT_SENT
    
    # Get the string server client from the global registry
    client = _STRING_SERVER_CLIENTS.get(client_id)
    if client is None:
        raise RuntimeError(f"String server client {client_id} not found in registry")
    
    # Check if we're on firmware box
    from featrix.neural.platform_utils import os_is_featrix_firmware
    is_firmware = os_is_featrix_firmware()
    
    # Firmware boxes: 30 minute timeout, fail hard. Development: 10 minute timeout.
    if is_firmware:
        max_retry_time = 1800.0  # 30 minutes on firmware
        slack_alert_threshold = 120.0  # 2 minutes
    else:
        max_retry_time = 600.0  # 10 minutes on development
        slack_alert_threshold = None  # No early alert on development
    
    base_delay = 1.0  # Start with 1 second
    max_delay = 30.0  # Cap at 30 seconds between retries
    
    attempt = 0
    retry_start = time.time()
    last_error = None
    slack_alert_sent = False
    
    # Track time spent on remote fetch (cache miss)
    fetch_start = time.time()
    
    while (time.time() - retry_start) < max_retry_time:
        try:
            # Try to encode via string server
            result = client.encode(sentence_text)
            
            # Track time spent on successful remote fetch
            fetch_elapsed = time.time() - fetch_start
            _CACHE_MISS_TIMING['total_seconds'] += fetch_elapsed
            _CACHE_MISS_TIMING['miss_count'] += 1
            _CACHE_MISS_TIMING['min_seconds'] = min(_CACHE_MISS_TIMING['min_seconds'], fetch_elapsed)
            _CACHE_MISS_TIMING['max_seconds'] = max(_CACHE_MISS_TIMING['max_seconds'], fetch_elapsed)
            
            # If we succeed and had previously notified about an outage, notify about recovery
            if _STRING_SERVER_OUTAGE_NOTIFIED and not _STRING_SERVER_RECOVERY_NOTIFIED:
                elapsed = time.time() - retry_start
                logger.info(f"✅ String server recovered after {elapsed:.1f}s")
                _send_slack_recovery_notification(elapsed)
                _STRING_SERVER_RECOVERY_NOTIFIED = True
                _STRING_SERVER_OUTAGE_NOTIFIED = False
                _STRING_SERVER_SLACK_ALERT_SENT = False
            
            return result
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Check if it's a connection/timeout error (retriable)
            is_retriable = any(x in error_str for x in [
                'connection refused', 
                'connection error', 
                'timeout',
                'timed out',
                '503',
                'service unavailable',
                'max retries exceeded',
                'failed to establish'
            ])
            
            if not is_retriable:
                # Not a retriable error (e.g., bad data format) - fail immediately
                raise
            
            elapsed = time.time() - retry_start
            
            # On firmware: Send Slack alert after 2 minutes of downtime (only once)
            if is_firmware and slack_alert_threshold and elapsed >= slack_alert_threshold and not slack_alert_sent:
                logger.error(f"🚨 FIRMWARE: taco.local has been down for {elapsed:.1f}s (>{slack_alert_threshold:.0f}s threshold)")
                _send_slack_firmware_downtime_alert(elapsed)
                slack_alert_sent = True
                _STRING_SERVER_SLACK_ALERT_SENT = True
            
            # Send Slack notification on first outage detection (for non-firmware or initial alert)
            if not _STRING_SERVER_OUTAGE_NOTIFIED and attempt == 0:
                if is_firmware:
                    logger.error(f"🚨 FIRMWARE: String server outage detected: {error_str[:200]}")
                    logger.error(f"   Will retry for up to 30 minutes (will fail hard if still down)")
                else:
                    logger.error(f"🚨 String server outage detected: {error_str[:200]}")
                    logger.error(f"   Will retry for up to 10 minutes...")
                _send_slack_outage_notification(error_str, is_firmware)
                _STRING_SERVER_OUTAGE_NOTIFIED = True
                _STRING_SERVER_RECOVERY_NOTIFIED = False
            
            # Check if we've exceeded max retry time
            if elapsed >= max_retry_time:
                if is_firmware:
                    logger.error(f"❌❌❌ FIRMWARE: String server failed after {elapsed:.1f}s (30 minute timeout): {error_str[:200]} ❌❌❌")
                    logger.error(f"   This is a CRITICAL failure - taco.local MUST be accessible on firmware boxes")
                    _send_slack_firmware_critical_failure(elapsed, error_str)
                    raise RuntimeError(
                        f"CRITICAL: String server (taco.local:9000) unavailable for {elapsed:.1f}s on firmware box. "
                        f"This is a hard failure - taco.local MUST be accessible. "
                        f"Last error: {error_str}"
                    ) from last_error
                else:
                    logger.error(f"❌ String server failed after {elapsed:.1f}s (10 minute timeout): {error_str[:200]}")
                    raise RuntimeError(
                        f"String server unavailable for {elapsed:.1f}s. "
                        f"Giving up after 10 minutes of retries. Last error: {error_str}"
                    ) from last_error
            
            # Calculate exponential backoff delay (capped at max_delay)
            delay = min(base_delay * (1.5 ** attempt), max_delay)
            remaining = max_retry_time - elapsed
            
            # Log retry attempts periodically (every 5th attempt or every 60s)
            if attempt % 5 == 0 or attempt == 1 or elapsed % 60 < delay:
                logger.warning(
                    f"⚠️  String server retry attempt {attempt + 1} "
                    f"(elapsed: {elapsed:.1f}s, remaining: {remaining:.1f}s, "
                    f"next retry in {delay:.1f}s): {error_str[:100]}"
                )
            
            time.sleep(delay)
            attempt += 1


def _send_slack_outage_notification(error_str: str, is_firmware: bool = False):
    """Send Slack notification about string server outage."""
    try:
        from slack import send_slack_message
        if is_firmware:
            message = (
                "🚨 *FIRMWARE: String Server Outage Detected*\n"
                f"The string encoding server (taco.local:9000) is unreachable on firmware box.\n"
                f"Error: `{error_str[:200]}`\n"
                f"Will retry for up to 30 minutes. Will send alert after 2 minutes if still down.\n"
                f"Training is paused."
            )
        else:
            message = (
                "🚨 *String Server Outage Detected*\n"
                f"The string encoding server (taco.local:9000) is unreachable.\n"
                f"Error: `{error_str[:200]}`\n"
                f"Will retry for up to 10 minutes. Training is paused."
            )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")


def _send_slack_firmware_downtime_alert(downtime_seconds: float):
    """Send Slack alert when taco.local has been down for more than 2 minutes on firmware."""
    try:
        from slack import send_slack_message
        message = (
            "🚨🚨🚨 *FIRMWARE CRITICAL: taco.local Down > 2 Minutes* 🚨🚨🚨\n"
            f"The string encoding server (taco.local:9000) has been unreachable for {downtime_seconds:.1f} seconds.\n"
            f"This is a critical issue on a firmware box - taco.local MUST be accessible.\n"
            f"Will continue retrying for up to 30 minutes total, then fail hard.\n"
            f"Training is paused."
        )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack alert: {e}")


def _send_slack_firmware_critical_failure(downtime_seconds: float, error_str: str):
    """Send Slack alert when firmware box fails hard after 30 minutes."""
    try:
        from slack import send_slack_message
        message = (
            "❌❌❌ *FIRMWARE CRITICAL FAILURE: taco.local Unreachable for 30 Minutes* ❌❌❌\n"
            f"The string encoding server (taco.local:9000) has been unreachable for {downtime_seconds:.1f} seconds.\n"
            f"This is a HARD FAILURE on a firmware box - training has been terminated.\n"
            f"Error: `{error_str[:200]}`\n"
            f"**IMMEDIATE ACTION REQUIRED**: Check taco.local network connectivity and string server status."
        )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack alert: {e}")


def _send_slack_recovery_notification(downtime_seconds: float):
    """Send Slack notification about string server recovery."""
    try:
        from slack import send_slack_message
        message = (
            "✅ *String Server Recovered*\n"
            f"The string encoding server is back online after {downtime_seconds:.1f}s.\n"
            "Training will resume."
        )
        send_slack_message(message, throttle=False, skip_hostname_prefix=False)
    except Exception as e:
        logger.warning(f"Failed to send Slack notification: {e}")


# Global registry of string server clients (for module-level caching)
_STRING_SERVER_CLIENTS = {}
_NEXT_CLIENT_ID = [0]  # Use list for mutability

# Global timing tracking for cache misses (remote fetches)
# Track total time spent waiting for remote fetches on cache misses
_CACHE_MISS_TIMING = {
    'total_seconds': 0.0,
    'miss_count': 0,
    'min_seconds': float('inf'),
    'max_seconds': 0.0,
}


class SimpleStringCache:
    """
    Dead simple string cache:
    - @lru_cache for in-memory caching (131,072 entries)
    - String server for encoding with batch support
    - No SQLite, no shared memory, no files
    """
    def __init__(self, initial_values=None, debugName="simple_cache", string_columns=None, **kwargs):
        """
        Args:
            initial_values: Optional list of strings to pre-warm the cache
            debugName: Debug name for logging
            string_columns: Optional list of string column names (enables local cache lookup)
            **kwargs: Ignored (for compatibility with old StringCache interface)
            
        Note:
            Job tracking information (FEATRIX_JOB_TYPE, FEATRIX_JOB_ID, FEATRIX_JOB_COMPUTE_NODE)
            is automatically read from environment variables when the string server client is initialized.
        """
        self.debugName = debugName
        self._string_server_client = None
        self._client_id = None
        self._client_encode_func_key = None
        self._log_every_n_misses = 10000  # Log stats every 10,000 cache misses
        self._last_logged_misses = 0
        self._last_logged_timing_misses = 0  # Track when we last logged timing stats
        
        # Lazy initialization: Only initialize string server client if we have initial_values to pre-warm
        # Otherwise, initialize on first use (avoids initialization in DataLoader workers that may not need it)
        if initial_values and len(initial_values) > 0:
            self._ensure_string_client_initialized()
            logger.info(f"🔥 Pre-warming cache with {len(initial_values)} strings...")
            self._pre_warm_cache(initial_values, string_columns=string_columns)
    
    def _ensure_string_client_initialized(self):
        """Lazily initialize string server client on first use."""
        if self._string_server_client is not None:
            return  # Already initialized
        
        logger.info(f"SimpleStringCache ({self.debugName}): Initializing string server client...")
        from featrix.neural.string_codec import _init_string_server_client
        
        self._string_server_client = _init_string_server_client()
        if self._string_server_client is None:
            raise RuntimeError(
                "String server client not available. "
                "Set 'string_server_host' in config.json to 'taco', 'taco.local', or 'localhost'."
            )
        
        # Register client in global registry for module-level caching
        self._client_id = _NEXT_CLIENT_ID[0]
        _NEXT_CLIENT_ID[0] += 1
        _STRING_SERVER_CLIENTS[self._client_id] = self._string_server_client
        self._client_encode_func_key = id(self._string_server_client.encode)  # For cache invalidation
        
        # Pre-populated cache for batch-encoded results (populated during pre-warming)
        # This allows us to avoid string server calls for strings we've already batch-encoded
        self._pre_warmed_cache = {}
        
        # Create instance-level cache using @lru_cache
        # TIERED CACHING: @lru_cache → Redis → String Server (taco)
        # When string server is called, result is stored in Redis for other processes
        @lru_cache(maxsize=131072)
        def _instance_encode(sentence_text):
            """Instance-level cached encode method with tiered caching."""
            # 1. Check pre-warmed cache first (populated from batch encoding)
            if sentence_text in self._pre_warmed_cache:
                return self._pre_warmed_cache[sentence_text]
            
            # 2. Check Redis cache (shared across processes, persistent)
            redis_result = _get_from_redis_cache(sentence_text)
            if redis_result is not None:
                return redis_result
            
            # 3. Fall back to string server (taco) - CACHE MISS
            # This should NOT happen in workers! Workers should only use Redis.
            embedding_list = self._string_server_client.encode(sentence_text)
            
            # Store in Redis for other processes (async-friendly, won't block)
            _add_to_redis_cache(sentence_text, embedding_list)
            
            return embedding_list
        
        self._encode = _instance_encode
    
    def get_embedding_from_cache(self, sentence_text, add_if_missing=True, do_not_log_if_missing=False, batch_size=None):
        """
        Get embedding from cache (or encode via string server).
        
        Args:
            sentence_text: String to encode
            add_if_missing: Ignored (always encodes via server)
            do_not_log_if_missing: Ignored
            batch_size: Optional batch size for logging purposes
            
        Returns:
            torch.Tensor: Embedding vector (float32)
        """
        if sentence_text is None:
            sentence_text = ""
        if type(sentence_text) != str:
            sentence_text = str(sentence_text)
        
        sentence_text = sentence_text.strip()
        
        # Empty strings return None
        if not sentence_text:
            return None
        
        # WORKER MODE: Only use Redis cache, don't initialize string server client
        if getattr(self, '_is_worker_cache', False):
            redis_result = _get_from_redis_cache(sentence_text)
            if redis_result is not None:
                return torch.tensor(redis_result, dtype=torch.float32)
            else:
                # Worker cache miss - this is CRITICAL, should not happen
                logger.error(f"❌ WORKER CACHE MISS: '{sentence_text[:50]}...' not in Redis cache!")
                logger.error(f"   Workers should NEVER call string server - all strings must be pre-cached in Redis!")
                return None
        
        # Lazy initialization: Initialize string client on first use
        self._ensure_string_client_initialized()
        
        try:
            # Encode via string server (using instance-level cache)
            embedding_list = self._encode(sentence_text)
            embedding = torch.tensor(embedding_list, dtype=torch.float32)
            
            # Periodic logging of cache stats (every 10,000 misses)
            info = self._encode.cache_info()  # pylint: disable=no-value-for-parameter
            if info.misses > 0 and (info.misses - self._last_logged_misses) >= self._log_every_n_misses:
                total = info.hits + info.misses
                hit_rate = info.hits / max(total, 1)
                
                # Calculate timing stats for new misses since last log
                new_misses = info.misses - self._last_logged_timing_misses
                if new_misses > 0 and _CACHE_MISS_TIMING['miss_count'] > 0:
                    # Get timing stats for all misses (global, not just this cache instance)
                    total_wait_seconds = _CACHE_MISS_TIMING['total_seconds']
                    total_miss_count = _CACHE_MISS_TIMING['miss_count']
                    avg_wait_seconds = total_wait_seconds / max(total_miss_count, 1)
                    
                    # Estimate time for recent misses (approximate)
                    # This is an approximation since timing is global across all cache instances
                    estimated_recent_wait = avg_wait_seconds * new_misses
                    total_wait_minutes = total_wait_seconds / 60.0
                    
                    logger.info(
                        f"📊 SimpleStringCache ({self.debugName}): "
                        f"{info.hits} hits, {info.misses} misses "
                        f"({hit_rate:.1%} hit rate), "
                        f"{info.currsize}/{info.maxsize} entries | "
                        f"⏱️  Cache miss wait time: {total_wait_minutes:.1f} min total "
                        f"({avg_wait_seconds*1000:.1f}ms avg per miss)"
                    )
                else:
                    logger.info(
                        f"📊 SimpleStringCache ({self.debugName}): "
                        f"{info.hits} hits, {info.misses} misses "
                        f"({hit_rate:.1%} hit rate), "
                        f"{info.currsize}/{info.maxsize} entries"
                    )
                
                self._last_logged_misses = info.misses
                self._last_logged_timing_misses = info.misses
            
            return embedding
        except Exception as e:
            logger.error(f"SimpleStringCache: Failed to encode '{sentence_text[:50]}...': {e}")
            return None
    
    def get_embeddings_batch(self, string_list):
        """
        Get embeddings for a batch of strings (much faster than one-at-a-time).
        Includes retry logic with up to 10 minutes wait for string server outages.
        
        Returns:
            List of torch.Tensor embeddings (or None for empty strings)
        """
        if not string_list:
            return []
        
        # Lazy initialization: Initialize string client on first use
        self._ensure_string_client_initialized()
        
        # Split into cached vs uncached
        results = [None] * len(string_list)
        uncached_indices = []
        uncached_strings = []
        
        for i, s in enumerate(string_list):
            if s is None or (isinstance(s, str) and not s.strip()):
                results[i] = None
                continue
            
            s_str = str(s).strip()
            # Check cache first (will be fast after @lru_cache warms up)
            # Note: We can't check cache without calling the method, so just collect uncached
            uncached_indices.append(i)
            uncached_strings.append(s_str)
        
        # Batch encode all uncached strings with retry logic
        if uncached_strings:
            max_retry_time = 600.0  # 10 minutes
            base_delay = 1.0
            max_delay = 30.0
            attempt = 0
            retry_start = time.time()
            last_error = None
            
            # Track time spent on batch remote fetch (cache miss)
            batch_fetch_start = time.time()
            
            while (time.time() - retry_start) < max_retry_time:
                try:
                    embeddings = self._string_server_client.encode_batch(uncached_strings)
                    
                    # Track time spent on successful batch remote fetch
                    batch_fetch_elapsed = time.time() - batch_fetch_start
                    # For batch encoding, we count each string as a separate miss for timing purposes
                    # This gives us accurate per-string timing even in batch mode
                    per_string_time = batch_fetch_elapsed / max(len(uncached_strings), 1)
                    for _ in uncached_strings:
                        _CACHE_MISS_TIMING['total_seconds'] += per_string_time
                        _CACHE_MISS_TIMING['miss_count'] += 1
                        _CACHE_MISS_TIMING['min_seconds'] = min(_CACHE_MISS_TIMING['min_seconds'], per_string_time)
                        _CACHE_MISS_TIMING['max_seconds'] = max(_CACHE_MISS_TIMING['max_seconds'], per_string_time)
                    
                    for idx, embedding_list in zip(uncached_indices, embeddings):
                        # Store in cache via get_embedding_from_cache (populates @lru_cache)
                        embedding = torch.tensor(embedding_list, dtype=torch.float32)
                        results[idx] = embedding
                    break  # Success - exit retry loop
                    
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    
                    # Check if it's a connection/timeout error (retriable)
                    is_retriable = any(x in error_str for x in [
                        'connection refused', 
                        'connection error', 
                        'timeout',
                        'timed out',
                        '503',
                        'service unavailable',
                        'max retries exceeded',
                        'failed to establish'
                    ])
                    
                    if not is_retriable:
                        # Not retriable - fallback to one-at-a-time
                        logger.error(f"SimpleStringCache: Batch encoding failed with non-retriable error: {e}")
                        batch_size_for_logging = len(string_list)
                        for idx, s in zip(uncached_indices, uncached_strings):
                            results[idx] = self.get_embedding_from_cache(s, batch_size=batch_size_for_logging)
                        break
                    
                    elapsed = time.time() - retry_start
                    
                    # Check if we've exceeded max retry time
                    if elapsed >= max_retry_time:
                        logger.error(f"❌ Batch encoding failed after {elapsed:.1f}s (10 minute timeout): {error_str[:200]}")
                        # Fallback to one-at-a-time (which has its own retry logic)
                        logger.info(f"   Falling back to one-at-a-time encoding for {len(uncached_strings)} strings...")
                        batch_size_for_logging = len(string_list)
                        for idx, s in zip(uncached_indices, uncached_strings):
                            results[idx] = self.get_embedding_from_cache(s, batch_size=batch_size_for_logging)
                        break
                    
                    # Calculate exponential backoff delay (capped at max_delay)
                    delay = min(base_delay * (1.5 ** attempt), max_delay)
                    remaining = max_retry_time - elapsed
                    
                    # Log retry attempts periodically
                    if attempt % 5 == 0 or attempt == 1:
                        logger.warning(
                            f"⚠️  Batch encoding retry attempt {attempt + 1} "
                            f"(elapsed: {elapsed:.1f}s, remaining: {remaining:.1f}s, "
                            f"next retry in {delay:.1f}s): {error_str[:100]}"
                        )
                    
                    time.sleep(delay)
                    attempt += 1
        
        return results
    
    def _pre_warm_cache(self, string_list, string_columns=None):
        """
        Pre-warm the @lru_cache by encoding all strings via the string server.
        This populates the cache upfront to avoid cache misses during training.
        
        First tries to load from local string cache if string_columns are provided,
        then falls back to string server encoding for any remaining strings.
        
        Args:
            string_list: List of strings to pre-warm
            string_columns: Optional list of string column names (enables local cache lookup)
        """
        import time
        start_time = time.time()
        
        # Clean and deduplicate strings
        unique_strings = []
        seen = set()
        for s in string_list:
            if s is None:
                continue
            s_str = str(s).strip()
            if not s_str or s_str in seen:
                continue
            seen.add(s_str)
            unique_strings.append(s_str)
        
        if not unique_strings:
            logger.info(f"   No valid strings to pre-warm")
            return
        
        num_strings = len(unique_strings)
        logger.info(f"   Pre-warming {num_strings} unique strings (from {len(string_list)} total)...")
        
        # Try to warm up from local cache first if string_columns are provided
        cached_strings_set = None
        if string_columns:
            try:
                from featrix.neural.local_string_cache import warm_up_simple_string_cache_from_local
                logger.info(f"🔍 Attempting to warm up from local string cache...")
                num_cached, cached_strings_set = warm_up_simple_string_cache_from_local(
                    self,
                    string_columns,
                    cache_dir=None  # Uses default {featrix_root}/strings_cache/
                )
                
                if num_cached > 0:
                    logger.info(f"✅ Loaded {num_cached} strings from local cache")
                    # Check which strings are now in cache by testing a sample
                    # We'll encode remaining strings via string server below
                    cache_info = self._encode.cache_info()  # pylint: disable=no-value-for-parameter
                    logger.info(f"   Cache now has {cache_info.currsize} entries")
            except Exception as e:
                logger.warning(f"⚠️  Failed to warm up from local cache: {e}")
                logger.info(f"   Falling back to string server encoding...")
        
        # Filter out strings that were already loaded from local cache
        strings_to_encode = unique_strings
        if cached_strings_set is not None:
            strings_to_encode = [s for s in unique_strings if s not in cached_strings_set]
            skipped_count = len(unique_strings) - len(strings_to_encode)
            if skipped_count > 0:
                logger.info(f"   Skipping {skipped_count} strings already in local cache (only encoding {len(strings_to_encode)} new strings)")
        
        # ALSO filter out strings already in REDIS cache (from previous columns or runs)
        # This prevents re-encoding the same strings when multiple columns have overlapping values
        redis_hit_count = 0
        strings_from_redis = []
        for s in strings_to_encode:
            cached = _get_from_redis_cache(s)
            if cached is not None:
                self._pre_warmed_cache[s] = cached
                self._encode(s)  # Populates @lru_cache from pre_warmed_cache
                strings_from_redis.append(s)
                redis_hit_count += 1
        
        if redis_hit_count > 0:
            logger.info(f"   ✅ Loaded {redis_hit_count} strings from Redis cache")
            strings_to_encode = [s for s in strings_to_encode if s not in strings_from_redis]
        
        # Initialize new_misses for tracking
        new_misses = 0
        
        # BATCH ENCODE: Use batch encoding to avoid tight loop of individual HTTP requests
        # This is much more efficient than calling encode() one at a time
        if len(strings_to_encode) > 0:
            try:
                cache_misses_before = self._encode.cache_info().misses  # pylint: disable=no-value-for-parameter
                cache_hits_before = self._encode.cache_info().hits  # pylint: disable=no-value-for-parameter
                
                # Get the string server client
                client = _STRING_SERVER_CLIENTS.get(self._client_id)
                if client is None:
                    raise RuntimeError(f"String server client {self._client_id} not found in registry")
                
                # Batch encode in chunks to avoid huge requests
                batch_size = 1000  # Encode 1000 strings per batch
                total_batches = (len(strings_to_encode) + batch_size - 1) // batch_size
                log_interval = max(1, total_batches // 10)  # Log every 10% of batches
                
                all_embeddings = {}
                max_retry_seconds = 300  # 5 minutes max retry time per batch
                
                for batch_idx in range(0, len(strings_to_encode), batch_size):
                    batch_strings = strings_to_encode[batch_idx:batch_idx + batch_size]
                    batch_num = (batch_idx // batch_size) + 1
                    
                    # Batch encode with retry - exponential backoff up to 5 minutes
                    # If string server is temporarily down, give it time to recover
                    # But if it's still failing after 5 minutes, abort - don't waste time
                    batch_embeddings = None
                    retry_start = time.time()
                    retry_delay = 2  # Start with 2 second delay
                    attempt = 0
                    last_error = None
                    
                    while batch_embeddings is None:
                        attempt += 1
                        try:
                            batch_embeddings = client.encode_batch(batch_strings)
                        except Exception as e:
                            last_error = e
                            elapsed_retry = time.time() - retry_start
                            
                            if elapsed_retry >= max_retry_seconds:
                                # 5 minutes of retrying - give up
                                error_msg = (
                                    f"❌ CRITICAL: Batch {batch_num}/{total_batches} failed after {elapsed_retry:.0f}s of retrying. "
                                    f"Last error: {e}. "
                                    f"String server is not recoverable - aborting cache population."
                                )
                                logger.error("=" * 100)
                                logger.error(error_msg)
                                logger.error("=" * 100)
                                raise RuntimeError(error_msg) from e
                            
                            # Log and retry with exponential backoff
                            logger.warning(
                                f"⚠️  Batch {batch_num} attempt {attempt} failed: {e}. "
                                f"Retrying in {retry_delay}s... ({elapsed_retry:.0f}s/{max_retry_seconds}s elapsed)"
                            )
                            time.sleep(retry_delay)
                            retry_delay = min(retry_delay * 2, 30)  # Cap at 30 second delay
                    
                    # Log if we recovered after retries
                    if attempt > 1:
                        elapsed_retry = time.time() - retry_start
                        logger.info(f"✅ Batch {batch_num} succeeded after {attempt} attempts ({elapsed_retry:.1f}s)")
                    
                    # Verify we got the expected number of embeddings
                    if len(batch_embeddings) != len(batch_strings):
                        error_msg = (
                            f"❌ CRITICAL: Batch {batch_num} returned {len(batch_embeddings)} embeddings "
                            f"but expected {len(batch_strings)}. String server returned incomplete results."
                        )
                        logger.error("=" * 100)
                        logger.error(error_msg)
                        logger.error("=" * 100)
                        raise RuntimeError(error_msg)
                    
                    # Store results in dict for @lru_cache population
                    for s, emb in zip(batch_strings, batch_embeddings):
                        all_embeddings[s] = emb
                    
                    # Progress logging
                    if total_batches > 1 and batch_num % log_interval == 0:
                        elapsed_so_far = time.time() - start_time
                        rate = (batch_idx + len(batch_strings)) / max(elapsed_so_far, 0.001)
                        remaining = (len(strings_to_encode) - batch_idx - len(batch_strings)) / max(rate, 1)
                        logger.info(f"   Progress: {batch_idx + len(batch_strings)}/{len(strings_to_encode)} ({100*(batch_idx + len(batch_strings))//len(strings_to_encode)}%) - {rate:.0f} strings/sec - ETA: {remaining:.0f}s")
                
                # Populate pre-warmed cache and @lru_cache with batch-encoded results
                # Store in pre-warmed cache (checked first by _instance_encode)
                # Then call _encode() to also populate the @lru_cache
                # ALSO populate Redis cache for worker processes
                for s, emb in all_embeddings.items():
                    # Store in pre-warmed cache (checked first by _instance_encode)
                    self._pre_warmed_cache[s] = emb
                    # Call _encode() to populate the @lru_cache (will use pre-warmed cache, so no string server call)
                    self._encode(s)
                
                # Batch add all embeddings to Redis for worker processes
                redis_added = _add_batch_to_redis_cache(all_embeddings)
                if redis_added > 0:
                    logger.info(f"   ✅ Added {redis_added} embeddings to Redis cache for workers")
                
                elapsed = time.time() - start_time
                cache_misses_after = self._encode.cache_info().misses  # pylint: disable=no-value-for-parameter
                cache_hits_after = self._encode.cache_info().hits  # pylint: disable=no-value-for-parameter
                new_misses = cache_misses_after - cache_misses_before
                new_hits = cache_hits_after - cache_hits_before
                
                logger.info(f"✅ Pre-warmed {len(strings_to_encode)} strings in {elapsed:.1f}s ({len(strings_to_encode)/max(elapsed,0.001):.0f} strings/sec) via batch encoding")
                logger.info(f"   Cache populated: {new_misses} new entries from string server, {new_hits} hits from cache")
                if cached_strings_set and len(cached_strings_set) > 0:
                    logger.info(f"   Total: {num_strings} strings ({len(cached_strings_set)} from local cache + {new_misses} newly encoded)")
                
                # FINAL VERIFICATION: Ensure ALL strings are now in cache
                # This catches cases where batch encoding silently returns fewer embeddings than expected
                missing_from_cache = []
                for s in strings_to_encode:
                    if s not in all_embeddings:
                        missing_from_cache.append(s)
                
                if missing_from_cache:
                    error_msg = (
                        f"❌ CRITICAL: {len(missing_from_cache)} strings were not cached after encoding. "
                        f"String server may have returned incomplete results. "
                        f"First few missing: {missing_from_cache[:5]}"
                    )
                    logger.error("=" * 100)
                    logger.error(error_msg)
                    logger.error("=" * 100)
                    raise RuntimeError(error_msg)
                
            except Exception as e:
                logger.error(f"❌ CRITICAL: String cache population failed: {e}")
                logger.error("   Training CANNOT proceed without a fully populated cache.")
                raise
        else:
            logger.info(f"✅ All {num_strings} strings already in cache - skipping encoding")
            new_misses = 0
        
        # Log cache stats
        info = self._encode.cache_info()  # pylint: disable=no-value-for-parameter
        logger.info(f"📊 Cache stats: {info.currsize}/{info.maxsize} entries, {info.hits} hits, {info.misses} misses")
        
        # Save to local cache for next time (if we got new embeddings from string server)
        if string_columns and new_misses > 0:
            try:
                from featrix.neural.local_string_cache import save_local_string_cache
                
                # Extract embeddings from the instance-level cache
                embeddings_dict = {}
                for s in unique_strings:
                    # Get from the in-memory cache (we just populated it above)
                    embedding = self._encode(s)
                    embeddings_dict[s] = np.array(embedding, dtype=np.float32)
                
                if embeddings_dict:
                    save_local_string_cache(embeddings_dict, string_columns)
                    logger.info(f"💾 Saved {len(embeddings_dict)} string embeddings to local cache")
            except Exception as e:
                logger.warning(f"⚠️  Failed to save local string cache: {e}")
    
    def run_batch(self, initial_values, string_columns=None):
        """Compatibility method for pre-warming"""
        if initial_values:
            self._pre_warm_cache(initial_values, string_columns=string_columns)
    
    def get_cache_stats(self):
        """Get cache hit/miss statistics from @lru_cache"""
        if not hasattr(self, '_encode'):
            return {'hits': 0, 'misses': 0, 'currsize': 0, 'maxsize': 0, 'hit_rate': 0.0}
        info = self._encode.cache_info()  # pylint: disable=no-value-for-parameter
        total = info.hits + info.misses
        hit_rate = info.hits / max(total, 1)
        return {
            'hits': info.hits,
            'misses': info.misses,
            'hit_rate': hit_rate,
            'current_size': info.currsize,
            'max_size': info.maxsize
        }
    
    def log_cache_stats(self):
        """Log current cache statistics"""
        stats = self.get_cache_stats()
        logger.info(
            f"📊 SimpleStringCache ({self.debugName}): "
            f"{stats['hits']} hits, {stats['misses']} misses "
            f"({stats['hit_rate']:.1%} hit rate), "
            f"{stats['current_size']}/{stats['max_size']} entries"
        )
    
    def log_final_string_cache_stats(self):
        """
        Log final string cache statistics including timing information.
        Should be called when dataloader shuts down or training completes.
        """
        stats = self.get_cache_stats()
        
        # Get timing stats
        total_wait_seconds = _CACHE_MISS_TIMING['total_seconds']
        total_miss_count = _CACHE_MISS_TIMING['miss_count']
        
        if total_miss_count > 0:
            avg_wait_seconds = total_wait_seconds / total_miss_count
            min_wait_seconds = _CACHE_MISS_TIMING['min_seconds'] if _CACHE_MISS_TIMING['min_seconds'] != float('inf') else 0.0
            max_wait_seconds = _CACHE_MISS_TIMING['max_seconds']
            total_wait_minutes = total_wait_seconds / 60.0
            total_wait_hours = total_wait_seconds / 3600.0
            
            logger.info("=" * 100)
            logger.info(f"📊 FINAL STRING CACHE STATS ({self.debugName})")
            logger.info("=" * 100)
            logger.info(f"   Cache Performance:")
            logger.info(f"      Hits: {stats['hits']:,}")
            logger.info(f"      Misses: {stats['misses']:,}")
            logger.info(f"      Hit Rate: {stats['hit_rate']:.1%}")
            logger.info(f"      Cache Size: {stats['current_size']:,}/{stats['max_size']:,} entries")
            logger.info("")
            logger.info(f"   ⏱️  Cache Miss Wait Time (Remote Fetch):")
            logger.info(f"      Total Time: {total_wait_minutes:.1f} minutes ({total_wait_hours:.2f} hours)")
            logger.info(f"      Total Misses: {total_miss_count:,}")
            logger.info(f"      Average per Miss: {avg_wait_seconds*1000:.1f}ms")
            if min_wait_seconds > 0:
                logger.info(f"      Min: {min_wait_seconds*1000:.1f}ms, Max: {max_wait_seconds*1000:.1f}ms")
            logger.info("=" * 100)
        else:
            logger.info("=" * 100)
            logger.info(f"📊 FINAL STRING CACHE STATS ({self.debugName})")
            logger.info("=" * 100)
            logger.info(f"   Cache Performance:")
            logger.info(f"      Hits: {stats['hits']:,}")
            logger.info(f"      Misses: {stats['misses']:,}")
            logger.info(f"      Hit Rate: {stats['hit_rate']:.1%}")
            logger.info(f"      Cache Size: {stats['current_size']:,}/{stats['max_size']:,} entries")
            logger.info(f"   ⏱️  No cache misses (all hits) - no remote fetch time")
            logger.info("=" * 100)
    
    @property
    def filename(self):
        """Compatibility property - no file backing"""
        return None
