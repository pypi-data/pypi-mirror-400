#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Training Timeline System

Pre-calculates all training hyperparameters for each epoch and tracks actual results.
Provides complete transparency and observability for training runs.

FAIL-SAFE: All operations wrapped in try/except to never crash training.
If timeline fails, training continues normally with error logging.
"""

import logging
import time
import json
import os
import traceback
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class EpochPlan:
    """Pre-calculated plan for a single epoch."""
    epoch_idx: int
    
    # Hyperparameters
    learning_rate: float  # Base LR for this epoch
    dropout_rate: float
    
    # Loss weights (ES-specific)
    spread_weight: float
    marginal_weight: float
    joint_weight: float
    
    # Curriculum phase
    curriculum_phase: str
    training_progress: float  # 0.0 to 1.0
    
    # Scheduled events
    data_rotation: bool
    data_rotation_fraction: Optional[float] = None
    
    # Early stopping eligibility
    early_stop_eligible: bool = False
    
    # Monitoring
    expected_behavior: str = ""
    milestones: List[str] = field(default_factory=list)


@dataclass
class EpochResult:
    """Actual results recorded during/after epoch execution."""
    epoch_idx: int
    
    # Loss & Metrics
    train_loss: Optional[float] = None
    val_loss: Optional[float] = None
    
    # Loss components (ES)
    spread_loss: Optional[float] = None
    marginal_loss: Optional[float] = None
    joint_loss: Optional[float] = None
    
    val_spread_loss: Optional[float] = None
    val_marginal_loss: Optional[float] = None
    val_joint_loss: Optional[float] = None
    
    # Actual hyperparameters
    actual_learning_rate: Optional[float] = None
    actual_dropout_rate: Optional[float] = None
    
    # Timing
    epoch_start_time: Optional[float] = None
    epoch_end_time: Optional[float] = None
    epoch_duration: Optional[float] = None
    
    # Resource usage
    gpu_memory_allocated_mb: Optional[float] = None
    gpu_memory_reserved_mb: Optional[float] = None
    
    # Status
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    deviations: List[str] = field(default_factory=list)
    is_best_epoch: bool = False


class TrainingTimeline:
    """Complete training timeline: plan + execution results."""
    
    def __init__(
        self,
        n_epochs: int,
        training_type: str = "embedding_space",
        hyperparameters: Optional[Dict[str, Any]] = None,
        training_start_time: Optional[float] = None,
    ):
        self.n_epochs = n_epochs
        self.training_type = training_type
        self.hyperparameters = hyperparameters or {}
        self.training_start_time = training_start_time or time.time()
        
        # Pre-calculated plans
        self.epoch_plans: List[EpochPlan] = []
        
        # Execution results (filled during training)
        self.epoch_results: List[Optional[EpochResult]] = [None] * n_epochs
        
        # Global milestones
        self.milestones: List[Dict[str, Any]] = []
        
        # Metadata
        self.metadata: Dict[str, Any] = {}
        
        # Summary (computed after training)
        self.summary: Optional[Dict[str, Any]] = None
    
    def add_epoch_plan(self, plan: EpochPlan):
        """Add a pre-calculated epoch plan."""
        self.epoch_plans.append(plan)
    
    def update_epoch_result(self, epoch_idx: int, result: EpochResult):
        """Update actual results for an epoch."""
        if 0 <= epoch_idx < self.n_epochs:
            self.epoch_results[epoch_idx] = result
        else:
            logger.warning(f"⚠️  Epoch index {epoch_idx} out of range (0-{self.n_epochs-1})")
    
    def get_epoch_plan(self, epoch_idx: int) -> Optional[EpochPlan]:
        """Get the pre-calculated plan for an epoch."""
        if 0 <= epoch_idx < len(self.epoch_plans):
            return self.epoch_plans[epoch_idx]
        return None
    
    def get_epoch_result(self, epoch_idx: int) -> Optional[EpochResult]:
        """Get the actual results for an epoch."""
        if 0 <= epoch_idx < len(self.epoch_results):
            return self.epoch_results[epoch_idx]
        return None
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics after training."""
        try:
            completed_epochs = [r for r in self.epoch_results if r is not None]
            
            if not completed_epochs:
                return {"error": "No completed epochs"}
            
            # Find best epoch
            best_epoch_idx = None
            best_val_loss = float('inf')
            for r in completed_epochs:
                if r.val_loss is not None and r.val_loss < best_val_loss:
                    best_val_loss = r.val_loss
                    best_epoch_idx = r.epoch_idx
            
            # Count warnings by type
            warning_counts = {}
            for r in completed_epochs:
                for w in r.warnings:
                    wtype = w.get("type", "UNKNOWN")
                    warning_counts[wtype] = warning_counts.get(wtype, 0) + 1
            
            # Compute average epoch time
            epoch_times = [r.epoch_duration for r in completed_epochs if r.epoch_duration is not None]
            avg_epoch_time = sum(epoch_times) / len(epoch_times) if epoch_times else None
            
            summary = {
                "total_epochs_planned": self.n_epochs,
                "total_epochs_executed": len(completed_epochs),
                "best_epoch": best_epoch_idx,
                "best_val_loss": best_val_loss if best_val_loss != float('inf') else None,
                "warning_counts": warning_counts,
                "avg_epoch_time_seconds": avg_epoch_time,
                "total_training_time_seconds": None,
                "deviations_from_plan": [],
            }
            
            # Check for deviations
            for r in completed_epochs:
                if r.deviations:
                    summary["deviations_from_plan"].extend([
                        {"epoch": r.epoch_idx, "deviation": d} for d in r.deviations
                    ])
            
            # Compute total training time
            if completed_epochs:
                last_result = completed_epochs[-1]
                if last_result.epoch_end_time is not None:
                    summary["total_training_time_seconds"] = last_result.epoch_end_time - self.training_start_time
            
            self.summary = summary
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to generate timeline summary: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def save_to_json(self, filepath: str):
        """Save timeline to JSON for inspection/debugging."""
        try:
            data = {
                "n_epochs": self.n_epochs,
                "training_type": self.training_type,
                "hyperparameters": self.hyperparameters,
                "training_start_time": self.training_start_time,
                "milestones": self.milestones,
                "metadata": self.metadata,
                "epoch_plans": [asdict(p) for p in self.epoch_plans],
                "epoch_results": [asdict(r) if r else None for r in self.epoch_results],
                "summary": self.summary,
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"📋 Timeline saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save timeline to {filepath}: {e}")
            logger.error(traceback.format_exc())
            return False


# ============================================================================
# Timeline Generation for Embedding Space
# ============================================================================

def create_embedding_space_timeline(
    n_epochs: int,
    batch_size: int,
    batches_per_epoch: int,
    optimizer_params: Dict[str, Any],
    use_lr_scheduler: bool,
    dropout_schedule_type: str,
    initial_dropout: float,
    final_dropout: float,
    curriculum_config: Optional[Any] = None,  # CurriculumLearningConfig
    rotation_fraction: float = 0.05,
    rotation_epoch: Optional[int] = None,
    val_loss_early_stop_patience: int = 100,
    **kwargs
) -> Optional[TrainingTimeline]:
    """
    Generate complete training timeline for Embedding Space training.
    
    FAIL-SAFE: Returns None on error, never crashes.
    
    Args:
        n_epochs: Total epochs to train
        batch_size: Batch size
        batches_per_epoch: Batches per epoch
        optimizer_params: Optimizer parameters dict
        use_lr_scheduler: Whether using LR scheduler
        dropout_schedule_type: Dropout schedule type
        initial_dropout: Initial dropout rate
        final_dropout: Final dropout rate
        curriculum_config: Curriculum learning config (optional)
        rotation_fraction: Data rotation fraction (default 0.05)
        rotation_epoch: Epoch for data rotation (default: halfway)
        val_loss_early_stop_patience: Early stop patience
        **kwargs: Additional hyperparameters
    
    Returns:
        TrainingTimeline object or None if generation fails
    """
    try:
        logger.info("📋 Generating training timeline...")
        
        timeline = TrainingTimeline(
            n_epochs=n_epochs,
            training_type="embedding_space",
            hyperparameters={
                "batch_size": batch_size,
                "batches_per_epoch": batches_per_epoch,
                "optimizer_params": optimizer_params,
                "dropout_schedule_type": dropout_schedule_type,
                "use_lr_scheduler": use_lr_scheduler,
                "initial_dropout": initial_dropout,
                "final_dropout": final_dropout,
                **kwargs
            }
        )
        
        # Pre-calculate LR schedule using LRTimeline (matches actual training)
        base_lr = optimizer_params.get('lr', 1e-4)
        lrs_per_epoch = []
        
        if use_lr_scheduler:
            try:
                # Use LRTimeline to match actual training scheduler
                max_lr = base_lr
                min_lr = base_lr / 100.0
                base_lr_for_schedule = base_lr / 10.0
                
                from featrix.neural.lr_timeline import LRTimeline
                scheduler = LRTimeline(
                    n_epochs=n_epochs,
                    base_lr=base_lr_for_schedule,
                    max_lr=max_lr,
                    min_lr=min_lr,
                    aggressive_warmup_pct=0.05,
                    gentle_warmup_pct=0.05,
                    onecycle_pct=0.50,
                )
                
                # Extract LR for each epoch
                for epoch_idx in range(n_epochs):
                    scheduler.set_epoch(epoch_idx)
                    lr = scheduler.get_current_lr()
                    lrs_per_epoch.append(lr)
                
                logger.info(f"   ✅ LR schedule pre-calculated using LRTimeline: {len(lrs_per_epoch)} epochs")
            except Exception as e:
                logger.warning(f"⚠️  Failed to pre-calculate LR schedule: {e}")
                # Fall back to constant LR
                lrs_per_epoch = [base_lr] * n_epochs
        else:
            # Constant LR
            lrs_per_epoch = [base_lr] * n_epochs
        
        # Pre-calculate dropout schedule
        dropout_rates = []
        try:
            from featrix.neural.dropout_scheduler import DropoutScheduler
            dropout_scheduler = DropoutScheduler(
                schedule_type=dropout_schedule_type,
                initial_dropout=initial_dropout,
                final_dropout=final_dropout,
                total_epochs=n_epochs,
            )
            for epoch_idx in range(n_epochs):
                dropout_rate = dropout_scheduler.get_dropout_rate(epoch_idx)
                dropout_rates.append(dropout_rate)
            logger.info(f"   ✅ Dropout schedule pre-calculated: {len(dropout_rates)} epochs")
        except Exception as e:
            logger.warning(f"⚠️  Failed to pre-calculate dropout schedule: {e}")
            # Fall back to linear interpolation
            for epoch_idx in range(n_epochs):
                progress = epoch_idx / max(1, n_epochs - 1)
                dropout_rate = initial_dropout + (final_dropout - initial_dropout) * progress
                dropout_rates.append(dropout_rate)
        
        # Determine data rotation epoch
        if rotation_epoch is None:
            rotation_epoch = int(n_epochs * 0.5)
        
        # Early stopping eligibility (70% of training)
        min_early_stop_epoch = int(n_epochs * 0.70)
        
        # Generate epoch plans
        for epoch_idx in range(n_epochs):
            try:
                # Learning rate
                lr = lrs_per_epoch[epoch_idx] if epoch_idx < len(lrs_per_epoch) else base_lr
                
                # Dropout rate
                dropout = dropout_rates[epoch_idx] if epoch_idx < len(dropout_rates) else initial_dropout
                
                # Loss weights (curriculum learning)
                training_progress = epoch_idx / n_epochs
                spread_weight, marginal_weight, joint_weight = _compute_loss_weights(
                    epoch_idx, n_epochs, curriculum_config
                )
                
                # Curriculum phase
                curriculum_phase = _get_curriculum_phase_name(training_progress, curriculum_config)
                
                # Data rotation
                data_rotation = (epoch_idx == rotation_epoch)
                
                # Early stopping eligibility
                early_stop_eligible = (epoch_idx >= min_early_stop_epoch)
                
                # Expected behavior
                expected_behavior = _generate_expected_behavior(
                    epoch_idx, n_epochs, curriculum_phase, lr, dropout
                )
                
                # Milestones
                milestones = []
                if epoch_idx == 0:
                    milestones.append("Training start")
                if use_lr_scheduler:
                    warmup_fraction = 0.1 if n_epochs > 1000 else 0.3
                    warmup_end = int(n_epochs * warmup_fraction)
                    if epoch_idx == warmup_end:
                        milestones.append("Peak LR reached")
                if data_rotation:
                    milestones.append(f"Data rotation ({rotation_fraction*100:.0f}% swap)")
                if early_stop_eligible and epoch_idx == min_early_stop_epoch:
                    milestones.append("Early stopping now eligible")
                
                # Check for phase transitions
                if epoch_idx > 0 and curriculum_config is not None:
                    prev_phase = _get_curriculum_phase_name((epoch_idx - 1) / n_epochs, curriculum_config)
                    if prev_phase != curriculum_phase:
                        milestones.append(f"Phase transition: {prev_phase} → {curriculum_phase}")
                
                plan = EpochPlan(
                    epoch_idx=epoch_idx,
                    learning_rate=lr,
                    dropout_rate=dropout,
                    spread_weight=spread_weight,
                    marginal_weight=marginal_weight,
                    joint_weight=joint_weight,
                    curriculum_phase=curriculum_phase,
                    training_progress=training_progress,
                    data_rotation=data_rotation,
                    data_rotation_fraction=rotation_fraction if data_rotation else None,
                    early_stop_eligible=early_stop_eligible,
                    expected_behavior=expected_behavior,
                    milestones=milestones,
                )
                
                timeline.add_epoch_plan(plan)
                
                # Add to global milestones if any
                if milestones:
                    for m in milestones:
                        timeline.milestones.append({
                            "epoch": epoch_idx,
                            "event": m,
                            "description": expected_behavior,
                        })
            
            except Exception as e:
                logger.error(f"❌ Failed to generate plan for epoch {epoch_idx}: {e}")
                logger.error(traceback.format_exc())
                # Continue with next epoch
                continue
        
        logger.info(f"✅ Timeline generated: {len(timeline.epoch_plans)} epoch plans")
        logger.info(f"   Milestones: {len(timeline.milestones)}")
        
        # Log first few milestones
        for milestone in timeline.milestones[:5]:
            logger.info(f"      Epoch {milestone['epoch']}: {milestone['event']}")
        if len(timeline.milestones) > 5:
            logger.info(f"      ... and {len(timeline.milestones) - 5} more")
        
        return timeline
        
    except Exception as e:
        logger.error("❌ Failed to generate training timeline")
        logger.error(f"   Error: {e}")
        logger.error(traceback.format_exc())
        return None


def _compute_loss_weights(
    epoch_idx: int,
    n_epochs: int,
    curriculum_config: Optional[Any]
) -> Tuple[float, float, float]:
    """
    Compute loss weights for a given epoch.
    
    FAIL-SAFE: Returns default weights on error.
    """
    try:
        if curriculum_config is None:
            # Default: equal weights
            return (1.0, 1.0, 1.0)
        
        progress = epoch_idx / max(1, n_epochs)
        
        # Find current phase
        current_phase = None
        for phase in curriculum_config.phases:
            if phase.start_progress <= progress <= phase.end_progress:
                current_phase = phase
                break
        
        if current_phase is None:
            # Default to last phase if out of range
            if hasattr(curriculum_config, 'phases') and curriculum_config.phases:
                current_phase = curriculum_config.phases[-1]
            else:
                return (1.0, 1.0, 1.0)
        
        # Get weights from phase
        spread_weight = getattr(current_phase, 'spread_weight', 1.0)
        marginal_weight = getattr(current_phase, 'marginal_weight', 1.0)
        joint_weight = getattr(current_phase, 'joint_weight', 1.0)
        
        return (spread_weight, marginal_weight, joint_weight)
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to compute loss weights for epoch {epoch_idx}: {e}")
        return (1.0, 1.0, 1.0)


def _get_curriculum_phase_name(progress: float, curriculum_config: Optional[Any]) -> str:
    """Get the name of the curriculum phase at a given progress."""
    try:
        if curriculum_config is None:
            return "constant"
        
        for phase in curriculum_config.phases:
            if phase.start_progress <= progress <= phase.end_progress:
                return getattr(phase, 'name', 'unknown')
        
        # Default to last phase
        if hasattr(curriculum_config, 'phases') and curriculum_config.phases:
            return getattr(curriculum_config.phases[-1], 'name', 'unknown')
        
        return "unknown"
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to get curriculum phase name: {e}")
        return "unknown"


def _generate_expected_behavior(
    epoch_idx: int,
    n_epochs: int,
    curriculum_phase: str,
    lr: float,
    dropout: float
) -> str:
    """Generate human-readable expected behavior description."""
    try:
        progress_pct = (epoch_idx / max(1, n_epochs)) * 100
        
        descriptions = []
        
        # Phase-specific behavior
        if "spread" in curriculum_phase.lower():
            descriptions.append("establishing geometry")
        elif "reconstruction" in curriculum_phase.lower() or "marginal" in curriculum_phase.lower():
            descriptions.append("learning reconstructions")
        elif "refinement" in curriculum_phase.lower() or "joint" in curriculum_phase.lower():
            descriptions.append("fine-tuning")
        
        # LR-based behavior
        if lr > 0.0003:
            descriptions.append("high LR")
        elif lr > 0.00005:
            descriptions.append("moderate LR")
        else:
            descriptions.append("low LR")
        
        # Dropout-based behavior
        if dropout > 0.4:
            descriptions.append("strong dropout")
        elif dropout > 0.2:
            descriptions.append("moderate dropout")
        
        phase_desc = curriculum_phase.replace('_', ' ').title()
        return f"[{progress_pct:.1f}%] {phase_desc}: {', '.join(descriptions)}"
        
    except Exception as e:
        logger.warning(f"⚠️  Failed to generate expected behavior: {e}")
        return f"Epoch {epoch_idx}/{n_epochs}"


# ============================================================================
# Timeline Integration Helpers (called from embedded_space.py)
# ============================================================================

def safe_create_timeline(
    n_epochs: int,
    **kwargs
) -> Optional[TrainingTimeline]:
    """
    Safely create timeline with full error handling.
    
    FAIL-SAFE: Returns None on error, never crashes.
    """
    try:
        return create_embedding_space_timeline(n_epochs=n_epochs, **kwargs)
    except Exception as e:
        logger.error("❌ Timeline creation failed (continuing without timeline)")
        logger.error(f"   Error: {e}")
        logger.error(traceback.format_exc())
        return None


def safe_save_timeline(timeline: Optional[TrainingTimeline], filepath: str) -> bool:
    """
    Safely save timeline to JSON.
    
    FAIL-SAFE: Returns False on error, never crashes.
    """
    if timeline is None:
        return False
    
    try:
        return timeline.save_to_json(filepath)
    except Exception as e:
        logger.error(f"❌ Timeline save failed: {e}")
        logger.error(traceback.format_exc())
        return False


def safe_update_epoch_result(
    timeline: Optional[TrainingTimeline],
    epoch_idx: int,
    **kwargs
) -> bool:
    """
    Safely update epoch result in timeline.
    
    FAIL-SAFE: Returns False on error, never crashes.
    """
    if timeline is None:
        return False
    
    try:
        result = EpochResult(epoch_idx=epoch_idx, **kwargs)
        timeline.update_epoch_result(epoch_idx, result)
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update epoch {epoch_idx} result: {e}")
        logger.error(traceback.format_exc())
        return False


def safe_generate_summary(timeline: Optional[TrainingTimeline]) -> Optional[Dict[str, Any]]:
    """
    Safely generate timeline summary.
    
    FAIL-SAFE: Returns None on error, never crashes.
    """
    if timeline is None:
        return None
    
    try:
        return timeline.generate_summary()
    except Exception as e:
        logger.error(f"❌ Failed to generate timeline summary: {e}")
        logger.error(traceback.format_exc())
        return None






