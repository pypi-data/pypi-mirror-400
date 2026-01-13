#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Event logging system for tracking events on sessions.

This module provides functions to log events such as:
- Training events
- Prediction events
- Webhook events
- __featrix field updates

All events are stored in Redis - no file-based storage.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def get_event_log_redis_client():
    """Get Redis client for event log storage (uses session Redis db 3)."""
    try:
        from lib.session_manager import get_session_redis_client
        return get_session_redis_client()
    except ImportError:
        logger.warning("Redis not available - event logging disabled")
        return None


def init_session_event_log_db(session_id: str):
    """
    Initialize the event log for a specific session (no-op for Redis-based storage).
    
    Args:
        session_id: Session ID
    """
    # No initialization needed for Redis - events are stored as JSON in Redis lists
    pass


def log_event(
    session_id: str,
    event_type: str,
    event_name: str,
    event_target: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None
):
    """
    Log an event to Redis for the session.
    
    Args:
        session_id: Session ID
        event_type: Type of event (e.g., "training", "prediction", "webhook", "__featrix_field_update")
        event_name: Name of the event (e.g., "training_started", "webhook_sent", "__featrix_row_id_set")
        event_target: Target of the event (e.g., predictor_id, webhook_url, field_name)
        payload: Optional JSON-serializable payload with additional event data
    """
    try:
        redis_client = get_event_log_redis_client()
        if not redis_client:
            logger.debug(f"Redis not available - skipping event log for session {session_id}")
            return
        
        # Get current timestamp
        event_time = datetime.now(tz=ZoneInfo("America/New_York"))
        created_at = event_time.isoformat()
        
        # Use session_id as default event_target if not provided
        if event_target is None:
            event_target = session_id
        
        # Create event document
        event_doc = {
            "event_time": event_time.isoformat(),
            "event_type": event_type,
            "event_name": event_name,
            "event_target": event_target,
            "payload": payload,
            "created_at": created_at
        }
        
        # Store in Redis as a list (append to session's event log)
        event_key = f"event_log:{session_id}"
        event_json = json.dumps(event_doc)
        redis_client.lpush(event_key, event_json)
        redis_client.expire(event_key, 86400 * 30)  # 30 day TTL
        
        # Keep only last 1000 events per session to prevent unbounded growth
        redis_client.ltrim(event_key, 0, 999)
            
        logger.debug(f"📝 Logged event: {event_type}/{event_name} for session {session_id}")
        
    except Exception as e:
        # Don't fail the main operation if event logging fails
        logger.warning(f"⚠️  Failed to log event for session {session_id}: {e}")


def log_featrix_field_update(
    session_id: str,
    field_name: str,
    row_id: Optional[int] = None,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Log when a __featrix field is updated in the database.
    
    Args:
        session_id: Session ID
        field_name: Name of the __featrix field (e.g., "__featrix_row_id", "__featrix_sentence_embedding_384d")
        row_id: Optional row ID that was updated
        additional_info: Optional additional information about the update
    """
    payload = {
        "field_name": field_name,
    }
    if row_id is not None:
        payload["row_id"] = row_id
    if additional_info:
        payload.update(additional_info)
    
    log_event(
        session_id=session_id,
        event_type="__featrix_field_update",
        event_name=f"__featrix_field_set",
        event_target=field_name,
        payload=payload
    )


def log_training_event(
    session_id: str,
    event_name: str,
    predictor_id: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Log a training-related event.
    
    Args:
        session_id: Session ID
        event_name: Name of the training event (e.g., "training_started", "training_completed", "training_failed")
        predictor_id: Optional predictor ID
        additional_info: Optional additional information about the event
    """
    payload = additional_info or {}
    if predictor_id:
        payload["predictor_id"] = predictor_id
    
    log_event(
        session_id=session_id,
        event_type="training",
        event_name=event_name,
        event_target=predictor_id or session_id,
        payload=payload
    )


def log_webhook_event(
    session_id: str,
    event_name: str,
    webhook_url: str,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Log a webhook-related event.
    
    Args:
        session_id: Session ID
        event_name: Name of the webhook event (e.g., "webhook_sent", "webhook_failed", "webhook_received")
        webhook_url: URL of the webhook
        additional_info: Optional additional information about the event
    """
    payload = additional_info or {}
    payload["webhook_url"] = webhook_url
    
    log_event(
        session_id=session_id,
        event_type="webhook",
        event_name=event_name,
        event_target=webhook_url,
        payload=payload
    )


def log_prediction_event(
    session_id: str,
    event_name: str,
    prediction_id: Optional[str] = None,
    additional_info: Optional[Dict[str, Any]] = None
):
    """
    Log a prediction-related event.
    
    Args:
        session_id: Session ID
        event_name: Name of the prediction event (e.g., "prediction_made", "prediction_corrected")
        prediction_id: Optional prediction ID
        additional_info: Optional additional information about the event
    """
    payload = additional_info or {}
    if prediction_id:
        payload["prediction_id"] = prediction_id
    
    log_event(
        session_id=session_id,
        event_type="prediction",
        event_name=event_name,
        event_target=prediction_id or session_id,
        payload=payload
    )

