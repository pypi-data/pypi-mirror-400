"""
Model card repair - finds model files on disk and generates missing model cards.
"""
import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Where to look for model files
OUTPUT_DIRS = [
    Path("/featrix-output"),
    Path("/sphere/app/featrix_output"),
]


def find_session_dir(session_id: str) -> Path | None:
    """Find session directory on disk by session ID."""
    for output_dir in OUTPUT_DIRS:
        if not output_dir.exists():
            continue
        session_dir = output_dir / session_id
        if session_dir.exists() and session_dir.is_dir():
            return session_dir
    return None


def find_model_card(session_id: str) -> Path | None:
    """Find existing model card for session."""
    session_dir = find_session_dir(session_id)
    if not session_dir:
        return None
    
    model_card_path = session_dir / "best_model_package" / "model_card.json"
    if model_card_path.exists():
        return model_card_path
    return None


def find_predictor_pickle(session_id: str) -> Path | None:
    """Find the latest single predictor pickle for a session."""
    session_dir = find_session_dir(session_id)
    if not session_dir:
        return None
    
    # Look for train_single_predictor_* directories
    for subdir in session_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith("train_single_predictor"):
            # Find latest pickle
            pickles = list(subdir.glob("*_latest.pickle"))
            if pickles:
                return pickles[0]
            # Fallback to any pickle
            pickles = list(subdir.glob("*.pickle"))
            if pickles:
                return sorted(pickles)[-1]
    return None


def find_embedding_space(session_id: str) -> Path | None:
    """Find the embedding space pickle for a session."""
    session_dir = find_session_dir(session_id)
    if not session_dir:
        return None
    
    # Check for foundation_embedding_space.pickle at session level
    es_path = session_dir / "foundation_embedding_space.pickle"
    if es_path.exists():
        return es_path
    
    # Look in train_es_* directories
    for subdir in session_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith("train_es"):
            es_path = subdir / "embedding_space.pickle"
            if es_path.exists():
                return es_path
    return None


def trigger_model_card_generation(session_id: str) -> bool:
    """
    Trigger model card generation via prediction server.
    The prediction server already knows how to load models correctly.
    Returns True if generation was started, False if not possible.
    """
    import requests
    
    session_dir = find_session_dir(session_id)
    if not session_dir:
        logger.warning(f"Cannot generate model card - session dir not found: {session_id}")
        return False
    
    predictor_path = find_predictor_pickle(session_id)
    if not predictor_path:
        logger.warning(f"Cannot generate model card - no predictor found: {session_id}")
        return False
    
    # Call prediction server to generate model card
    # The prediction server loads the model (knows how to do it with GPU)
    # and can generate the model card as a side effect
    try:
        # Tell prediction server to generate model card for this session
        response = requests.post(
            "http://localhost:8765/generate_model_card",
            json={
                "session_id": session_id,
                "predictor_path": str(predictor_path),
                "output_dir": str(session_dir / "best_model_package"),
            },
            timeout=5,  # Don't wait long - it runs in background
        )
        if response.status_code in [200, 202]:
            logger.info(f"Prediction server started model card generation for {session_id}")
            return True
        else:
            logger.warning(f"Prediction server returned {response.status_code}: {response.text}")
            return False
    except requests.exceptions.Timeout:
        # Timeout is OK - generation continues in background
        logger.info(f"Prediction server accepted model card request (timeout OK) for {session_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to call prediction server: {e}")
        return False


def get_or_generate_model_card(session_id: str) -> tuple[dict | None, bool]:
    """
    Get model card if exists, or trigger generation.
    
    Returns:
        (model_card_dict, is_generating)
        - (dict, False) if card exists
        - (None, True) if generation was started
        - (None, False) if no model files found
    """
    # Check if card already exists
    card_path = find_model_card(session_id)
    if card_path:
        with open(card_path) as f:
            return json.load(f), False
    
    # Try to trigger generation
    started = trigger_model_card_generation(session_id)
    return None, started


def check_model_card_availability(session_id: str, embedding_space_path: str = None) -> dict:
    """Check if model card exists for a session. Returns dict with availability info."""
    try:
        # First check using our find functions
        card_path = find_model_card(session_id)
        if card_path:
            return {
                "available": True,
                "path": str(card_path),
                "endpoint": f"/session/{session_id}/model_card",
            }
        
        # Check if session dir exists (means we could generate one)
        session_dir = find_session_dir(session_id)
        if session_dir:
            # Check for model files
            predictor = find_predictor_pickle(session_id)
            es = find_embedding_space(session_id)
            if predictor or es:
                return {
                    "available": False,
                    "can_generate": True,
                    "endpoint": f"/session/{session_id}/model_card",
                }
        
        return {"available": False, "endpoint": f"/session/{session_id}/model_card"}
    except Exception as e:
        logger.warning(f"Failed to check model card availability: {e}")
        return {"available": False, "endpoint": f"/session/{session_id}/model_card", "error": str(e)}

