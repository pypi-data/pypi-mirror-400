"""
Model Integrity Checker and Repair Tool

This tool loads a model, checks its integrity, and attempts to repair common issues.
If repairs are made, it saves a repaired version as 'repaired-<original-filename>'.
"""

import os
import pickle
import logging
import traceback
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

logger = logging.getLogger(__name__)


class ModelRepairResult:
    """Result of model integrity check and repair."""
    
    def __init__(self, is_valid: bool, issues_found: List[str], repairs_made: List[str], repaired_path: Optional[str] = None):
        self.is_valid = is_valid
        self.issues_found = issues_found
        self.repairs_made = repairs_made
        self.repaired_path = repaired_path


def check_and_repair_model(predictor_path: str, force_repair: bool = False) -> ModelRepairResult:
    """
    Check model integrity and repair if needed.
    
    Args:
        predictor_path: Path to the predictor pickle file
        force_repair: If True, always attempt repair even if no issues found
        
    Returns:
        ModelRepairResult with status and details
    """
    predictor_path = Path(predictor_path)
    
    if not predictor_path.exists():
        raise FileNotFoundError(f"Predictor file not found: {predictor_path}")
    
    logger.info(f"🔍 Checking model integrity: {predictor_path}")
    
    issues_found = []
    repairs_made = []
    
    # Load the model
    try:
        with open(predictor_path, "rb") as f:
            fsp = pickle.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return ModelRepairResult(
            is_valid=False,
            issues_found=[f"Failed to load model: {str(e)}"],
            repairs_made=[],
            repaired_path=None
        )
    
    # Check 1: Embedding space exists
    if not hasattr(fsp, 'embedding_space') or fsp.embedding_space is None:
        issues_found.append("Missing embedding_space attribute")
        logger.error("❌ Missing embedding_space")
        return ModelRepairResult(
            is_valid=False,
            issues_found=issues_found,
            repairs_made=[],
            repaired_path=None
        )
    
    es = fsp.embedding_space
    
    # Check 2: Encoder exists
    if not hasattr(es, 'encoder') or es.encoder is None:
        issues_found.append("Missing encoder in embedding_space")
        logger.error("❌ Missing encoder")
        return ModelRepairResult(
            is_valid=False,
            issues_found=issues_found,
            repairs_made=[],
            repaired_path=None
        )
    
    encoder = es.encoder
    
    # Check 3: Column encoder exists
    if not hasattr(encoder, 'column_encoder') or encoder.column_encoder is None:
        issues_found.append("Missing column_encoder")
        logger.error("❌ Missing column_encoder")
        return ModelRepairResult(
            is_valid=False,
            issues_found=issues_found,
            repairs_made=[],
            repaired_path=None
        )
    
    column_encoder = encoder.column_encoder
    
    # Check 4: col_order is not empty
    needs_repair = False
    col_order_recovered = False
    if not hasattr(column_encoder, 'col_order') or len(column_encoder.col_order) == 0:
        issues_found.append("Empty col_order in column_encoder")
        logger.warning("⚠️  Empty col_order detected")
        needs_repair = True
        
        # Attempt repair: recover from encoders or codecs
        if hasattr(column_encoder, 'encoders') and column_encoder.encoders and len(column_encoder.encoders) > 0:
            encoder_keys = list(column_encoder.encoders.keys())
            column_encoder.col_order = encoder_keys.copy()
            repairs_made.append(f"Recovered col_order from {len(encoder_keys)} encoders: {encoder_keys[:10]}{'...' if len(encoder_keys) > 10 else ''}")
            logger.info(f"✅ Repaired: Recovered col_order from encoders")
            needs_repair = False  # Fixed!
            col_order_recovered = True
        elif hasattr(column_encoder, 'col_codecs') and column_encoder.col_codecs:
            codec_keys = list(column_encoder.col_codecs.keys())
            column_encoder.col_order = codec_keys.copy()
            repairs_made.append(f"Recovered col_order from {len(codec_keys)} codecs: {codec_keys[:10]}{'...' if len(codec_keys) > 10 else ''}")
            logger.info(f"✅ Repaired: Recovered col_order from codecs")
            needs_repair = False  # Fixed!
            col_order_recovered = True
        else:
            logger.error("❌ Cannot repair: No encoders or codecs available")
            return ModelRepairResult(
                is_valid=False,
                issues_found=issues_found,
                repairs_made=repairs_made,
                repaired_path=None
            )
    
    # Check 5: col_codecs exists and is not empty
    if not hasattr(column_encoder, 'col_codecs') or not column_encoder.col_codecs or len(column_encoder.col_codecs) == 0:
        issues_found.append("Missing or empty col_codecs in column_encoder")
        logger.warning("⚠️  Missing or empty col_codecs")
        
        # Attempt repair: try to get from embedding space
        if hasattr(es, 'col_codecs') and es.col_codecs:
            column_encoder.col_codecs = es.col_codecs
            repairs_made.append(f"Recovered col_codecs from embedding_space ({len(es.col_codecs)} codecs)")
            logger.info(f"✅ Repaired: Recovered col_codecs from embedding_space")
        else:
            logger.warning("⚠️  Cannot repair: No codecs available in embedding_space")
            # Don't fail - codecs might be reconstructed during encoding
    
    # Check 6: ALWAYS fix pos_embedding and try to load pending encoder state dict
    # This handles the case where col_order was recovered by ColumnEncoders.__setstate__ during pickle.load(),
    # but the encoder state dict couldn't be loaded due to pos_embedding shape mismatch
    import torch
    import torch.nn as nn
    
    effective_col_count = len(column_encoder.col_order) if hasattr(column_encoder, 'col_order') and column_encoder.col_order else 0
    logger.info(f"🔧 Checking pos_embedding shape (col_order has {effective_col_count} columns)")
    
    # ALWAYS fix pos_embedding shape if needed
    if effective_col_count > 0:
        if hasattr(encoder, 'joint_encoder') and encoder.joint_encoder is not None:
            if hasattr(encoder.joint_encoder, 'col_encoder') and encoder.joint_encoder.col_encoder is not None:
                if hasattr(encoder.joint_encoder.col_encoder, 'pos_embedding') and encoder.joint_encoder.col_encoder.pos_embedding is not None:
                    current_shape = encoder.joint_encoder.col_encoder.pos_embedding.shape
                    expected_shape = (effective_col_count, current_shape[1])
                    logger.info(f"   📏 pos_embedding current shape: {current_shape}, expected: {expected_shape}")
                    if current_shape[0] != expected_shape[0]:
                        logger.warning(f"   ⚠️  FIXING pos_embedding shape from {current_shape} to {expected_shape}")
                        device = encoder.joint_encoder.col_encoder.pos_embedding.device
                        dtype = encoder.joint_encoder.col_encoder.pos_embedding.dtype
                        encoder.joint_encoder.col_encoder.pos_embedding = nn.Parameter(
                            torch.zeros(expected_shape[0], expected_shape[1], device=device, dtype=dtype)
                        )
                        repairs_made.append(f"Fixed pos_embedding shape from {current_shape} to {expected_shape}")
                        logger.warning(f"   ✅ Reinitialized pos_embedding with shape {expected_shape}")
                    else:
                        logger.info(f"   ✅ pos_embedding shape is already correct")
    
    # ALWAYS try to load pending encoder state dict if it exists
    # This handles the case where col_order was recovered by ColumnEncoders.__setstate__,
    # not by this model_repair tool
    if hasattr(fsp, '_pending_state_dicts') and fsp._pending_state_dicts:
        if '_finetuned_encoder_state_dict' in fsp._pending_state_dicts:
            logger.info(f"🔧 Found pending encoder state dict - attempting to load now")
            encoder_state = fsp._pending_state_dicts['_finetuned_encoder_state_dict']
            try:
                encoder.load_state_dict(encoder_state, strict=False)
                logger.info(f"✅ Successfully loaded encoder state dict ({len(encoder_state)} keys)")
                repairs_made.append(f"Loaded pending encoder state dict ({len(encoder_state)} keys)")
                # Clear the pending state dict since we loaded it
                del fsp._pending_state_dicts['_finetuned_encoder_state_dict']
            except Exception as e:
                logger.error(f"❌ Failed to load encoder state dict: {e}")
                logger.error(traceback.format_exc())
                # Don't fail - we'll check if encoders exist below
    
    if not hasattr(column_encoder, 'encoders') or not column_encoder.encoders or len(column_encoder.encoders) == 0:
        issues_found.append("Missing or empty encoders in column_encoder")
        logger.error("❌ Missing or empty encoders - cannot repair automatically")
        logger.error("   This is a critical issue - the model cannot be used without encoders")
        logger.error("   Even though col_order was recovered, the model is still corrupted")
        # Don't return early - save what we can (col_order recovery), but mark as invalid
        # The model might be partially usable if encoders can be reconstructed later
        # Set needs_repair to True so we know the model is still broken
        needs_repair = True
    
    # Check 7: Predictor exists - try to reconstruct it if missing
    if not hasattr(fsp, 'predictor') or fsp.predictor is None:
        logger.warning("⚠️  Missing predictor - attempting reconstruction...")
        try:
            # Call the lazy reconstruction method
            fsp._ensure_predictor_available()
            if hasattr(fsp, 'predictor') and fsp.predictor is not None:
                logger.info("✅ Repaired: Reconstructed predictor from state_dict")
                repairs_made.append("Reconstructed predictor from state_dict")
            else:
                issues_found.append("Missing predictor - reconstruction failed")
                logger.error("❌ Could not reconstruct predictor")
        except Exception as e:
            issues_found.append(f"Missing predictor - reconstruction failed: {str(e)}")
            logger.error(f"❌ Could not reconstruct predictor: {e}")
    
    # Check 8: Target column info exists
    if not hasattr(fsp, 'target_col_name') or not fsp.target_col_name:
        issues_found.append("Missing target_col_name")
        logger.warning("⚠️  Missing target_col_name")
    
    # If repairs were made or force_repair is True, save repaired version
    repaired_path = None
    if repairs_made or force_repair:
        # Generate repaired filename
        original_name = predictor_path.name
        repaired_name = f"repaired-{original_name}"
        repaired_path = predictor_path.parent / repaired_name
        
        logger.info(f"💾 Saving repaired model to: {repaired_path}")
        
        try:
            with open(repaired_path, "wb") as f:
                pickle.dump(fsp, f)
            logger.info(f"✅ Repaired model saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to save repaired model: {e}")
            return ModelRepairResult(
                is_valid=False,
                issues_found=issues_found + [f"Failed to save repaired model: {str(e)}"],
                repairs_made=repairs_made,
                repaired_path=None
            )
    
    # Determine if model is valid
    # Model is valid if:
    # 1. No issues found, OR
    # 2. Repairs were made AND no critical issues remain (needs_repair is False)
    # Critical issues: missing encoders, missing column_encoder, etc.
    is_valid = len(issues_found) == 0 or (len(repairs_made) > 0 and not needs_repair)
    
    # If we have critical issues (like missing encoders), model is not valid even if we made some repairs
    critical_issues = [issue for issue in issues_found if 'encoders' in issue.lower() or 'column_encoder' in issue.lower()]
    if critical_issues:
        is_valid = False
    
    if is_valid:
        logger.info(f"✅ Model integrity check passed")
    else:
        logger.warning(f"⚠️  Model has issues that could not be repaired")
    
    return ModelRepairResult(
        is_valid=is_valid,
        issues_found=issues_found,
        repairs_made=repairs_made,
        repaired_path=str(repaired_path) if repaired_path else None
    )


def find_repaired_model(original_path: str) -> Optional[str]:
    """
    Check if a repaired version of the model exists.
    
    Args:
        original_path: Path to the original predictor file
        
    Returns:
        Path to repaired model if it exists, None otherwise
    """
    original_path = Path(original_path)
    repaired_name = f"repaired-{original_path.name}"
    repaired_path = original_path.parent / repaired_name
    
    logger.info(f"🔍 Checking for repaired model:")
    logger.info(f"   Original path: {original_path}")
    logger.info(f"   Repaired path: {repaired_path}")
    logger.info(f"   Original exists: {original_path.exists()}")
    logger.info(f"   Repaired exists: {repaired_path.exists()}")
    
    if repaired_path.exists():
        logger.info(f"✅ Found repaired model: {repaired_path}")
        return str(repaired_path)
    
    logger.info(f"❌ Repaired model not found")
    return None


def get_best_model_path(predictor_path: str) -> str:
    """
    Get the best available model path, preferring repaired version if it exists.
    
    Args:
        predictor_path: Path to the original predictor file
        
    Returns:
        Path to use (repaired if available, otherwise original)
    """
    logger.info(f"🔍 get_best_model_path called with: {predictor_path}")
    repaired_path = find_repaired_model(predictor_path)
    if repaired_path:
        logger.info(f"✅ get_best_model_path returning repaired: {repaired_path}")
        return repaired_path
    logger.info(f"⚠️  get_best_model_path returning original: {predictor_path}")
    return predictor_path

