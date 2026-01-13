"""
Redis-based job progress storage.

This module provides fast, efficient storage for job progress updates using Redis Hashes.
Redis Hashes allow partial updates without reading/writing the entire job data.

Redis persistence should be configured with:
- RDB snapshots (save points)
- AOF (Append Only File) for durability
"""

import redis
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RedisJobProgress:
    """Redis-based storage for job progress updates."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/2", decode_responses: bool = True):
        """
        Initialize Redis connection for job progress.
        
        Uses Redis DB 2 to avoid conflicts with:
        - DB 0: Predictions
        - DB 1: Celery broker/backend
        
        Args:
            redis_url: Redis connection URL
            decode_responses: If True, automatically decode bytes to strings
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=decode_responses)
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info(f"✅ Redis connected for job progress tracking (DB 2)")
        except Exception as e:
            logger.warning(f"⚠️  Redis not available for job progress: {e}")
            self.redis_available = False
            self.redis_client = None
    
    def _get_progress_key(self, job_type: str, job_id: str) -> str:
        """Get Redis key for job progress hash."""
        return f"job_progress:{job_type}:{job_id}"
    
    def _get_metadata_key(self, job_type: str, job_id: str) -> str:
        """Get Redis key for job metadata (full job data)."""
        return f"job_metadata:{job_type}:{job_id}"
    
    def update_progress(
        self,
        job_type: str,
        job_id: str,
        progress: Optional[float] = None,
        current_epoch: Optional[int] = None,
        current_loss: Optional[float] = None,
        validation_loss: Optional[float] = None,
        metrics: Optional[Dict[str, Any]] = None,
        time_now: Optional[float] = None,
        **kwargs
    ) -> bool:
        """
        Update job progress fields in Redis Hash (partial update).
        
        This is very efficient - only updates the fields provided without
        reading/writing the entire job data.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            progress: Progress (0.0 to 1.0)
            current_epoch: Current epoch number
            current_loss: Current training loss
            validation_loss: Current validation loss
            metrics: Metrics dictionary
            time_now: Timestamp
            **kwargs: Additional fields to update
        
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            progress_key = self._get_progress_key(job_type, job_id)
            
            # Build update dictionary - only include non-None values
            updates = {}
            if progress is not None:
                updates['progress'] = str(progress)
            if current_epoch is not None:
                updates['current_epoch'] = str(current_epoch)
            if current_loss is not None:
                updates['current_loss'] = str(current_loss)
            if validation_loss is not None:
                updates['validation_loss'] = str(validation_loss)
            if metrics is not None:
                updates['metrics'] = json.dumps(metrics)
            if time_now is not None:
                updates['time_now'] = str(time_now)
            
            # Add any additional kwargs
            for key, value in kwargs.items():
                if value is not None:
                    if isinstance(value, (dict, list)):
                        updates[key] = json.dumps(value)
                    else:
                        updates[key] = str(value)
            
            if not updates:
                return True  # Nothing to update
            
            # Update hash fields (partial update - very efficient)
            self.redis_client.hset(progress_key, mapping=updates)
            
            # Update last_updated timestamp
            self.redis_client.hset(progress_key, 'last_updated', str(datetime.now().timestamp()))
            
            # Set expiration (24 hours) - progress data is temporary
            self.redis_client.expire(progress_key, 86400)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to update job progress in Redis: {e}")
            return False
    
    def get_progress(self, job_type: str, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current job progress from Redis.
        
        Args:
            job_type: Queue name
            job_id: Job ID
        
        Returns:
            Dictionary with progress fields, or None if not found/Redis unavailable
        """
        if not self.redis_available:
            return None
        
        try:
            progress_key = self._get_progress_key(job_type, job_id)
            progress_data = self.redis_client.hgetall(progress_key)
            
            if not progress_data:
                return None
            
            # Parse the data
            result = {}
            for key, value in progress_data.items():
                # Try to parse JSON fields
                if key in ('metrics',) or key.endswith('_json'):
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
                # Try to parse numeric fields
                elif key in ('progress', 'current_loss', 'validation_loss', 'time_now', 'last_updated'):
                    try:
                        result[key] = float(value)
                    except (ValueError, TypeError):
                        result[key] = value
                elif key == 'current_epoch':
                    try:
                        result[key] = int(value)
                    except (ValueError, TypeError):
                        result[key] = value
                else:
                    result[key] = value
            
            return result
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to get job progress from Redis: {e}")
            return None
    
    def store_full_job_metadata(self, job_type: str, job_id: str, job_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Store full job metadata in Redis (for quick access without reading disk).
        
        This is a backup/cache of the full job file. The disk file is still the source of truth.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            job_data: Full job data dictionary
            ttl: Time to live in seconds (default 24 hours)
        
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            metadata_key = self._get_metadata_key(job_type, job_id)
            serialized = json.dumps(job_data)
            self.redis_client.setex(metadata_key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to store job metadata in Redis: {e}")
            return False
    
    def get_full_job_metadata(self, job_type: str, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full job metadata from Redis cache.
        
        Args:
            job_type: Queue name
            job_id: Job ID
        
        Returns:
            Job data dictionary, or None if not found
        """
        if not self.redis_available:
            return None
        
        try:
            metadata_key = self._get_metadata_key(job_type, job_id)
            data = self.redis_client.get(metadata_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"⚠️  Failed to get job metadata from Redis: {e}")
            return None
    
    def append_log_message(self, job_type: str, job_id: str, message: str, max_messages: int = 100) -> bool:
        """
        Append a log message to job's log history (stored as Redis List).
        
        This is efficient - appends to a list without reading existing messages.
        Automatically trims to keep only the last N messages.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            message: Log message to append
            max_messages: Maximum number of messages to keep (default 100)
        
        Returns:
            True if appended successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            log_key = f"job_logs:{job_type}:{job_id}"
            
            # Append message with timestamp
            log_entry = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'time': datetime.now().timestamp()
            }
            
            # Push to right (end) of list
            self.redis_client.rpush(log_key, json.dumps(log_entry))
            
            # Trim list to keep only last max_messages
            self.redis_client.ltrim(log_key, -max_messages, -1)
            
            # Set expiration (24 hours)
            self.redis_client.expire(log_key, 86400)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to append log message to Redis: {e}")
            return False
    
    def get_log_messages(self, job_type: str, job_id: str, limit: int = 50) -> list:
        """
        Get recent log messages for a job.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            limit: Maximum number of messages to return (default 50)
        
        Returns:
            List of log message dictionaries
        """
        if not self.redis_available:
            return []
        
        try:
            log_key = f"job_logs:{job_type}:{job_id}"
            
            # Get last N messages from list
            messages = self.redis_client.lrange(log_key, -limit, -1)
            
            result = []
            for msg_json in messages:
                try:
                    result.append(json.loads(msg_json))
                except (json.JSONDecodeError, TypeError):
                    # Fallback for old format (plain strings)
                    result.append({'message': msg_json, 'timestamp': None})
            
            return result
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to get log messages from Redis: {e}")
            return []
    
    def append_to_field(self, job_type: str, job_id: str, field_name: str, value: str, max_length: int = 10000) -> bool:
        """
        Append to a string field in Redis Hash.
        
        Note: This reads the current value, appends, and writes back.
        For frequent appends, consider using append_log_message() with a list instead.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            field_name: Name of the field to append to
            value: Value to append
            max_length: Maximum length of the field (truncates from start if exceeded)
        
        Returns:
            True if appended successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            progress_key = self._get_progress_key(job_type, job_id)
            
            # Get current value
            current = self.redis_client.hget(progress_key, field_name) or ""
            
            # Append
            new_value = current + value
            
            # Truncate if too long (keep end of string)
            if len(new_value) > max_length:
                new_value = new_value[-max_length:]
            
            # Write back
            self.redis_client.hset(progress_key, field_name, new_value)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to append to field in Redis: {e}")
            return False
    
    def delete_progress(self, job_type: str, job_id: str) -> bool:
        """
        Delete job progress data from Redis.
        
        Args:
            job_type: Queue name
            job_id: Job ID
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            progress_key = self._get_progress_key(job_type, job_id)
            metadata_key = self._get_metadata_key(job_type, job_id)
            log_key = f"job_logs:{job_type}:{job_id}"
            metrics_timeline_key = f"training_metrics:{job_type}:{job_id}"
            self.redis_client.delete(progress_key, metadata_key, log_key, metrics_timeline_key)
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to delete job progress from Redis: {e}")
            return False
    
    def append_training_metrics(self, job_type: str, job_id: str, epoch: int, metrics: Dict[str, Any], max_epochs: int = 1000) -> bool:
        """
        Append training metrics for a specific epoch to the training timeline.
        
        This stores a time-series of metrics for each epoch, allowing us to plot
        learning curves and track training progress over time.
        
        For ES training, metrics should include:
        - learning_rate
        - validation_loss
        - spread_loss, joint_loss, marginal_loss, marginal_weighted_loss
        - loss components (spread_full, spread_short, joint_full, joint_short, etc.)
        
        For predictor training, metrics should include:
        - learning_rate
        - train_loss
        - validation_loss
        - auc, pr_auc, accuracy, f1, precision, recall, etc.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            epoch: Epoch number
            metrics: Dictionary of metrics for this epoch
            max_epochs: Maximum number of epochs to store (default 1000)
        
        Returns:
            True if appended successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            metrics_key = f"training_metrics:{job_type}:{job_id}"
            
            # Create epoch entry
            epoch_entry = {
                'epoch': epoch,
                'timestamp': datetime.now().timestamp(),
                'metrics': metrics
            }
            
            # Append to list
            self.redis_client.rpush(metrics_key, json.dumps(epoch_entry))
            
            # Trim to max epochs (keep most recent)
            self.redis_client.ltrim(metrics_key, -max_epochs, -1)
            
            # Set expiration (7 days for training metrics - longer than progress)
            self.redis_client.expire(metrics_key, 604800)
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to append training metrics to Redis: {e}")
            return False
    
    def get_training_metrics(self, job_type: str, job_id: str, start_epoch: int = 0, limit: int = 1000) -> list:
        """
        Get training metrics timeline for a job.
        
        Args:
            job_type: Queue name
            job_id: Job ID
            start_epoch: Starting epoch (default 0)
            limit: Maximum number of epochs to return (default 1000)
        
        Returns:
            List of epoch metric dictionaries, sorted by epoch
        """
        if not self.redis_available:
            return []
        
        try:
            metrics_key = f"training_metrics:{job_type}:{job_id}"
            
            # Get all metrics entries
            all_entries = self.redis_client.lrange(metrics_key, 0, -1)
            
            result = []
            for entry_json in all_entries:
                try:
                    entry = json.loads(entry_json)
                    epoch_num = entry.get('epoch', 0)
                    
                    # Filter by start_epoch
                    if epoch_num >= start_epoch:
                        result.append(entry)
                        
                        # Stop if we hit the limit
                        if len(result) >= limit:
                            break
                            
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to parse metrics entry: {e}")
                    continue
            
            return result
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to get training metrics from Redis: {e}")
            return []


# Global instance
_redis_job_progress = None


def get_redis_job_progress() -> RedisJobProgress:
    """Get or create global RedisJobProgress instance."""
    global _redis_job_progress
    if _redis_job_progress is None:
        _redis_job_progress = RedisJobProgress()
    return _redis_job_progress

