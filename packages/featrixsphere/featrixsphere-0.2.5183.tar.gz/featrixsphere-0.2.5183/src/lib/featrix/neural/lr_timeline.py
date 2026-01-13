"""
Learning Rate Timeline - Custom LR Schedule

Implements a sophisticated LR curve:
- 0-5%: Aggressive warmup ramp
- 5-10%: Gentler warmup ramp (back off)
- 10-60%: OneCycle pattern (peak at middle, 50% of training)
- 60-100%: Smooth linear cooldown

This gives better control than standard OneCycleLR, with a careful warmup
that doesn't shock the model, a productive training phase, and a gentle
cooldown that helps convergence.

Dynamic Adjustments:
- Can increase/decrease LR mid-training (e.g., due to training instability)
- Adjustments are smoothly interpolated over remaining epochs
- Multiple adjustments can be applied while maintaining smoothness
"""
import math
import logging
import csv
from pathlib import Path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


class LRTimeline:
    """
    Compute learning rate schedule for training.
    
    The schedule has 4 phases:
    1. Aggressive warmup (0-5%): Rapid increase to get model moving
    2. Gentle warmup (5-10%): Slower increase to avoid instability
    3. OneCycle productive phase (10-60%): Peak LR in middle, good for learning
    4. Linear cooldown (60-100%): Smooth descent to help convergence
    """
    
    def __init__(
        self, 
        n_epochs: int,
        base_lr: Optional[float] = None,  # Required for 'complex', optional for 'simple'
        max_lr: Optional[float] = None,   # Required for 'complex', optional for 'simple'
        min_lr: Optional[float] = None,   # Optional, defaults based on schedule_type
        aggressive_warmup_pct: float = 0.05,
        gentle_warmup_pct: float = 0.05,
        onecycle_pct: float = 0.50,
        mode: str = 'sp_only',  # 'sp_only' or 'sp_plus_es'
        schedule_type: str = 'complex',  # 'complex' (4-phase) or 'simple' (linear warmup + cosine decay)
        warmup_epochs: int = 5,  # For simple schedule: epochs for warmup
        warmup_start_lr: Optional[float] = None,  # For simple schedule: start LR for warmup
        warmup_end_lr: Optional[float] = None,  # For simple schedule: end LR for warmup (peak)
        decay_end_lr: Optional[float] = None,  # For simple schedule: final LR after cosine decay
        # Remaining % is linear cooldown
    ):
        """
        Initialize LR timeline.
        
        Args:
            n_epochs: Total number of epochs
            base_lr: Base learning rate (required for 'complex', ignored for 'simple')
            max_lr: Maximum learning rate (required for 'complex', ignored for 'simple')
            min_lr: Minimum LR at end of training (default: base_lr / 10 for 'complex', ignored for 'simple')
            aggressive_warmup_pct: Fraction for aggressive warmup (default: 0.05 = 5%, only for 'complex')
            gentle_warmup_pct: Fraction for gentle warmup (default: 0.05 = 5%, only for 'complex')
            onecycle_pct: Fraction for OneCycle phase (default: 0.50 = 50%, only for 'complex')
            mode: 'sp_only' (SP only) or 'sp_plus_es' (SP + ES coordination)
            schedule_type: 'complex' (4-phase) or 'simple' (linear warmup + cosine decay)
            warmup_epochs: For simple schedule: number of epochs for warmup (default: 5)
            warmup_start_lr: For simple schedule: start LR for warmup (default: 5e-5)
            warmup_end_lr: For simple schedule: end LR for warmup/peak (default: 6e-4)
            decay_end_lr: For simple schedule: final LR after cosine decay (default: 1e-5)
        """
        self.n_epochs = n_epochs
        self.schedule_type = schedule_type
        
        # Validate required parameters based on schedule_type
        if schedule_type == 'complex':
            if base_lr is None or max_lr is None:
                raise ValueError("base_lr and max_lr are required for schedule_type='complex'")
            self.base_lr = base_lr
            self.max_lr = max_lr
            self.min_lr = min_lr if min_lr is not None else base_lr / 10.0
        else:  # simple
            # For simple schedule, base_lr/max_lr/min_lr are not used
            # Use dummy values to avoid errors in code that references them
            self.base_lr = warmup_start_lr if warmup_start_lr is not None else 5e-5
            self.max_lr = warmup_end_lr if warmup_end_lr is not None else 6e-4
            self.min_lr = decay_end_lr if decay_end_lr is not None else 1e-5
        self.mode = mode
        
        # Simple schedule parameters
        self.warmup_epochs = warmup_epochs
        self.warmup_start_lr = warmup_start_lr if warmup_start_lr is not None else 5e-5
        self.warmup_end_lr = warmup_end_lr if warmup_end_lr is not None else 6e-4
        self.decay_end_lr = decay_end_lr if decay_end_lr is not None else 1e-5
        
        self.aggressive_warmup_pct = aggressive_warmup_pct
        self.gentle_warmup_pct = gentle_warmup_pct
        self.onecycle_pct = onecycle_pct
        self.cooldown_pct = 1.0 - (aggressive_warmup_pct + gentle_warmup_pct + onecycle_pct)
        
        # Validate
        if self.cooldown_pct < 0:
            raise ValueError(f"Phase percentages sum to > 1.0: {aggressive_warmup_pct + gentle_warmup_pct + onecycle_pct}")
        
        # ES coordination settings (only used in sp_plus_es mode)
        self._es_unfreeze_epoch = None  # Set via set_es_unfreeze_epoch()
        self._es_warmup_epochs = None  # Calculated when unfreeze is set
        self._es_start_lr_ratio = 0.1  # Start at 10% of SP's current LR
        self._es_target_lr_ratio = 0.4  # Cap at 40% of SP's LR
        
        # Compute epoch boundaries
        # Phase 1: Flat start (0-5%)
        self.aggressive_warmup_end = int(n_epochs * aggressive_warmup_pct)
        # Phase 2: Hard ramp up (5-10%) - ramp from base_lr to max_lr
        self.gentle_warmup_end = int(n_epochs * (aggressive_warmup_pct + gentle_warmup_pct))
        # Phase 3: OneCycle (10-60%) - peaks at middle, then descends
        self.onecycle_end = int(n_epochs * (aggressive_warmup_pct + gentle_warmup_pct + onecycle_pct))
        
        # Ensure at least 1 epoch per phase
        self.aggressive_warmup_end = max(1, self.aggressive_warmup_end)
        self.gentle_warmup_end = max(self.aggressive_warmup_end + 1, self.gentle_warmup_end)
        self.onecycle_end = max(self.gentle_warmup_end + 1, self.onecycle_end)
        
        # Pre-compute the entire LR schedule
        self.schedule = self._compute_schedule()
        
        # Track adjustments and deltas for history/debugging
        self.adjustments = []  # List of (epoch, adjustment_type, factor, reason) tuples
        self.deltas = []  # List of (epoch, delta_lr) tuples - actual LR changes applied
        
        # Track active boosts: List of (start_epoch, duration, scale_factor, reason, boost_type)
        # Each boost creates a smooth curve over its duration window
        self.active_boosts = []  # List of boost tuples
        
        # Track current epoch for get_current_lr()
        self.current_epoch = 0
        
        # Store original baseline schedule for comparison plotting
        self.baseline_schedule = self.schedule.copy()
        
        # Track actual LR that was used (including boost multipliers)
        self.actual_lr_used = {}  # {epoch: actual_lr_value}
        
        # Track training metrics alongside LR
        self.metrics = {
            'train_loss': {},    # {epoch: value}
            'val_loss': {},      # {epoch: value}
            'auc': {},          # {epoch: value}
            'custom': {}        # {metric_name: {epoch: value}}
        }
        
        logger.info("📈 LR Timeline Initialized:")
        logger.info(f"   Mode: {mode}")
        logger.info(f"   Schedule Type: {schedule_type}")
        logger.info(f"   Total epochs: {n_epochs}")
        
        if schedule_type == 'simple':
            logger.info(f"   Simple Schedule:")
            logger.info(f"     Epochs 0-{self.warmup_epochs-1}: Linear warmup {self.warmup_start_lr:.6e} → {self.warmup_end_lr:.6e}")
            logger.info(f"     Epochs {self.warmup_epochs}-{n_epochs-1}: Cosine decay {self.warmup_end_lr:.6e} → {self.decay_end_lr:.6e}")
        else:
            logger.info(f"   Base LR: {base_lr:.6e}, Max LR: {max_lr:.6e}, Min LR: {self.min_lr:.6e}")
            logger.info(f"   Phase 1 (0-{self.aggressive_warmup_end}): Aggressive warmup")
            logger.info(f"   Phase 2 ({self.aggressive_warmup_end}-{self.gentle_warmup_end}): Gentle warmup")
            logger.info(f"   Phase 3 ({self.gentle_warmup_end}-{self.onecycle_end}): OneCycle productive")
            logger.info(f"   Phase 4 ({self.onecycle_end}-{n_epochs}): Linear cooldown")
    
    def _compute_schedule(self) -> List[float]:
        """Pre-compute LR for each epoch."""
        schedule = []
        
        for epoch in range(self.n_epochs):
            lr = self.get_lr_for_epoch(epoch)
            schedule.append(lr)
        
        return schedule
    
    def get_lr_for_epoch(self, epoch: int) -> float:
        """
        Get learning rate for a specific epoch.
        
        OneCycleLR-like schedule but:
        1. Start flat/slow for a few epochs
        2. Ramp up hard
        3. Peak at middle
        4. Come down smoothly
        5. Allow dynamic adjustments during training (handled by get_lr())
        
        Args:
            epoch: Epoch number (0-indexed)
            
        Returns:
            Learning rate for that epoch (baseline, before boosts)
        """
        # Simple schedule: linear warmup + cosine decay
        if self.schedule_type == 'simple':
            if epoch < self.warmup_epochs:
                # Linear warmup from warmup_start_lr to warmup_end_lr
                progress = epoch / self.warmup_epochs  # 0.0 to 1.0
                lr = self.warmup_start_lr + (self.warmup_end_lr - self.warmup_start_lr) * progress
                return lr
            else:
                # Cosine decay from warmup_end_lr to decay_end_lr
                decay_start_epoch = self.warmup_epochs
                decay_length = self.n_epochs - decay_start_epoch
                decay_progress = (epoch - decay_start_epoch) / decay_length  # 0.0 to 1.0
                # Cosine: cos(0) = 1, cos(π) = -1
                # Map to [decay_end_lr, warmup_end_lr]
                cosine_value = math.cos(math.pi * decay_progress)
                lr = self.decay_end_lr + (self.warmup_end_lr - self.decay_end_lr) * (1 + cosine_value) / 2
                return lr
        
        # Complex schedule (original 4-phase)
        # Phase 1: Flat start (0-5%) - stay at base_lr
        if epoch < self.aggressive_warmup_end:
            # Stay flat at base_lr for first few epochs
            return self.base_lr
        
        # Phase 2: Hard ramp up (5-15%) - go up hard with smooth transition to Phase 3
        elif epoch < self.gentle_warmup_end:
            phase_start = self.aggressive_warmup_end
            phase_end = self.gentle_warmup_end
            phase_length = phase_end - phase_start
            progress = (epoch - phase_start) / phase_length
            
            # Add smooth transition window at the end of Phase 2 (last 30% of phase)
            transition_start = 0.7  # Start transition at 70% through Phase 2
            if progress < transition_start:
                # Early Phase 2: Cubic ramp for aggressive increase
                early_progress = progress / transition_start  # Normalize to [0, 1]
                lr = self.base_lr + (self.max_lr - self.base_lr) * (early_progress ** 3)
            else:
                # Transition region (last 30% of Phase 2): Smooth cosine transition to max_lr
                transition_progress = (progress - transition_start) / (1.0 - transition_start)  # [0, 1]
                # Cubic value at transition start
                cubic_at_transition = transition_start ** 3
                cubic_lr = self.base_lr + (self.max_lr - self.base_lr) * cubic_at_transition
                # Smooth cosine interpolation from cubic value to max_lr
                # Use smoothstep-like function for extra smoothness
                smooth_t = transition_progress * transition_progress * (3.0 - 2.0 * transition_progress)  # Smoothstep
                lr = cubic_lr + (self.max_lr - cubic_lr) * smooth_t
            return lr
        
        # Phase 3: OneCycle productive phase (10-60%) - peak at middle, then descend
        elif epoch < self.onecycle_end:
            phase_start = self.gentle_warmup_end
            phase_end = self.onecycle_end
            phase_length = phase_end - phase_start
            phase_progress = (epoch - phase_start) / phase_length
            
            # OneCycle curve: maintain max_lr for first half, then cosine descend to base_lr
            # The transition from Phase 2 already brings us smoothly to max_lr, so we start at max_lr
            if phase_progress <= 0.5:
                # First half: stay at max_lr (productive phase)
                lr = self.max_lr
            else:
                # Second half: cosine descent from max_lr to base_lr
                # Map phase_progress from [0.5, 1.0] to [0, 1] for cosine
                cosine_progress = (phase_progress - 0.5) * 2.0  # 0.0 to 1.0
                cosine_value = math.cos(math.pi * cosine_progress)  # 1 at start, -1 at end
                # Map from [1, -1] to [max_lr, base_lr]
                lr = self.base_lr + (self.max_lr - self.base_lr) * (1 + cosine_value) / 2
            return lr
        
        # Phase 4: Linear cooldown (60-100%) - smooth descent to min_lr
        else:
            phase_start = self.onecycle_end
            phase_end = self.n_epochs
            progress = (epoch - phase_start) / (phase_end - phase_start)
            # Linear interpolation from base_lr to min_lr
            lr = self.base_lr + (self.min_lr - self.base_lr) * progress
            return lr
    
    def get_lr(self, epoch: int) -> float:
        """
        Get LR for epoch: baseline + sum of all active boosts at this epoch.
        
        Each boost creates a smooth curve over its duration window.
        All active boosts are summed together.
        
        Args:
            epoch: Epoch number (0-indexed)
            
        Returns:
            Learning rate for that epoch (baseline + sum of boost contributions)
        """
        # Get baseline LR for this epoch
        if epoch < len(self.baseline_schedule):
            baseline_lr = self.baseline_schedule[epoch]
        else:
            baseline_lr = self.min_lr
        
        # Sum contributions from all active boosts at this epoch
        total_boost = 0.0
        for start_epoch, duration, scale_factor, reason, boost_type in self.active_boosts:
            if start_epoch <= epoch < start_epoch + duration:
                # Calculate boost contribution for this epoch
                boost_contribution = self._compute_boost_contribution(
                    epoch, start_epoch, duration, scale_factor, baseline_lr, boost_type
                )
                total_boost += boost_contribution
        
        return baseline_lr + total_boost
    
    def _compute_boost_contribution(
        self, 
        epoch: int, 
        start_epoch: int, 
        duration: int, 
        scale_factor: float, 
        baseline_lr: float,
        boost_type: str
    ) -> float:
        """
        Compute the boost contribution for a specific epoch.
        
        Creates a OneCycleLR-like curve: starts slow/flat (0-10%), 
        goes up hard (10-50%), then comes down smoothly (50-100%).
        
        Args:
            epoch: Current epoch
            start_epoch: When boost started
            duration: How long boost lasts
            scale_factor: Multiplier (e.g., 1.2 = 20% increase, 0.8 = 20% decrease)
            baseline_lr: Baseline LR at this epoch (for calculating absolute boost)
            boost_type: "increase" or "decrease"
            
        Returns:
            Boost contribution to add to baseline LR (positive for increase, negative for decrease)
        """
        # Position within boost window (0.0 to 1.0)
        position = (epoch - start_epoch) / duration
        
        # Calculate target boost amount (absolute, not relative)
        # For increase: add (scale_factor - 1) * baseline_lr
        # For decrease: subtract (1 - scale_factor) * baseline_lr
        if boost_type == "increase":
            target_boost = (scale_factor - 1.0) * baseline_lr
        else:  # decrease
            target_boost = -(1.0 - scale_factor) * baseline_lr  # Negative for decrease
        
        # OneCycleLR-like curve: start slow/flat (0-10%), go up hard (10-50%), then come down (50-100%)
        # This creates a smooth bell curve that peaks in the middle
        if position < 0.1:
            # Start slow/flat: very gradual ramp
            ramp_progress = position / 0.1
            curve_value = ramp_progress * 0.2  # Slow start, only 20% of peak
        elif position < 0.5:
            # Go up hard: rapid increase to peak
            ramp_progress = (position - 0.1) / 0.4  # 0.0 to 1.0 over 10-50%
            curve_value = 0.2 + 0.8 * (ramp_progress ** 2)  # Quadratic ramp up to 1.0
        else:
            # Come down: smooth cosine decay
            decay_progress = (position - 0.5) / 0.5  # 0.0 to 1.0 over 50-100%
            # Cosine decay: cos(0) = 1, cos(π) = -1, map to [1.0, 0.0]
            cosine_value = math.cos(math.pi * decay_progress)
            curve_value = (1.0 + cosine_value) / 2  # Smooth decay from 1.0 to 0.0
        
        return target_boost * curve_value
    
    def get_current_lr(self) -> float:
        """
        Get current learning rate based on internal epoch counter.
        
        Returns:
            Current LR for the current epoch
        """
        return self.get_lr(self.current_epoch)
    
    def step(self) -> float:
        """
        Advance to next epoch and return new LR.
        
        Returns:
            LR for the new epoch
        """
        self.current_epoch += 1
        return self.get_current_lr()
    
    def set_epoch(self, epoch: int) -> None:
        """Set current epoch (useful for resuming training)."""
        self.current_epoch = epoch
    
    def set_es_unfreeze_epoch(self, epoch: int) -> None:
        """
        Set the epoch when ES (Embedding Space) is unfrozen.
        
        This is used in 'sp_plus_es' mode to coordinate ES LR with SP LR.
        ES LR will start at 10% of SP's current LR and linearly warmup to 40% of SP's LR
        over max(5 epochs, 10% of total training).
        
        Args:
            epoch: Epoch number (0-indexed) when ES is unfrozen
        """
        if self.mode != 'sp_plus_es':
            logger.warning(f"set_es_unfreeze_epoch() called but mode is '{self.mode}' (not 'sp_plus_es')")
            return
        
        self._es_unfreeze_epoch = epoch
        # Calculate warmup period: max(5 epochs, 10% of total training)
        self._es_warmup_epochs = max(5, int(self.n_epochs * 0.10))
        
        if self.schedule_type == 'simple':
            logger.info(f"🔓 ES unfreeze set: epoch {epoch}")
            logger.info(f"   ES LR: lr_es = lr_sp / 10 (same cosine shape, just scaled)")
        else:
            logger.info(f"🔓 ES unfreeze set: epoch {epoch}, warmup over {self._es_warmup_epochs} epochs")
            logger.info(f"   ES LR: starts at 10% of SP LR, ramps to 40% of SP LR (capped)")
    
    def get_sp_lr(self, epoch: int) -> float:
        """
        Get SP (Single Predictor) learning rate for a specific epoch.
        
        This is the main LR schedule - same as get_lr() but with clearer naming.
        
        Args:
            epoch: Epoch number (0-indexed)
            
        Returns:
            SP learning rate for that epoch
        """
        return self.get_lr(epoch)
    
    def get_es_lr(self, epoch: int) -> float:
        """
        Get ES (Embedding Space) learning rate for a specific epoch.
        
        Only valid in 'sp_plus_es' mode. ES LR is coordinated with SP LR:
        - Before unfreeze: returns 0.0 (ES is frozen)
        - After unfreeze: ES LR = 40% of SP's current LR (constant ratio)
        
        Args:
            epoch: Epoch number (0-indexed)
            
        Returns:
            ES learning rate for that epoch (0.0 if ES not unfrozen or mode is 'sp_only')
        """
        if self.mode != 'sp_plus_es':
            return 0.0
        
        if self._es_unfreeze_epoch is None:
            # ES not unfrozen yet
            return 0.0
        
        if epoch < self._es_unfreeze_epoch:
            # Before unfreeze
            return 0.0
        
        # Get SP's current LR
        sp_lr = self.get_sp_lr(epoch)
        
        # Always use 40% of SP's LR after unfreeze
        return sp_lr * 0.4
    
    def get_state_dict(self) -> dict:
        """
        Get scheduler state for checkpointing.
        
        Returns:
            Dictionary containing all state needed to restore the scheduler
        """
        return {
            'n_epochs': self.n_epochs,
            'base_lr': self.base_lr,
            'max_lr': self.max_lr,
            'min_lr': self.min_lr,
            'aggressive_warmup_pct': self.aggressive_warmup_pct,
            'gentle_warmup_pct': self.gentle_warmup_pct,
            'onecycle_pct': self.onecycle_pct,
            'cooldown_pct': self.cooldown_pct,
            'current_epoch': self.current_epoch,
            'schedule': self.schedule.copy(),
            'baseline_schedule': self.baseline_schedule.copy(),
            'adjustments': self.adjustments.copy(),
            'deltas': self.deltas.copy(),
            'actual_lr_used': self.actual_lr_used.copy(),
            'metrics': {
                'train_loss': self.metrics['train_loss'].copy(),
                'val_loss': self.metrics['val_loss'].copy(),
                'auc': self.metrics['auc'].copy(),
                'custom': {k: v.copy() for k, v in self.metrics['custom'].items()}
            }
        }
    
    def load_state_dict(self, state_dict: dict) -> None:
        """
        Load scheduler state from checkpoint.
        
        Args:
            state_dict: Dictionary containing saved scheduler state
        """
        self.n_epochs = state_dict.get('n_epochs', self.n_epochs)
        self.base_lr = state_dict.get('base_lr', self.base_lr)
        self.max_lr = state_dict.get('max_lr', self.max_lr)
        self.min_lr = state_dict.get('min_lr', self.min_lr)
        self.aggressive_warmup_pct = state_dict.get('aggressive_warmup_pct', self.aggressive_warmup_pct)
        self.gentle_warmup_pct = state_dict.get('gentle_warmup_pct', self.gentle_warmup_pct)
        self.onecycle_pct = state_dict.get('onecycle_pct', self.onecycle_pct)
        self.cooldown_pct = state_dict.get('cooldown_pct', self.cooldown_pct)
        self.current_epoch = state_dict.get('current_epoch', 0)
        
        # Restore schedules
        if 'schedule' in state_dict:
            self.schedule = state_dict['schedule'].copy()
        if 'baseline_schedule' in state_dict:
            self.baseline_schedule = state_dict['baseline_schedule'].copy()
        
        # Restore history
        self.adjustments = state_dict.get('adjustments', []).copy()
        self.deltas = state_dict.get('deltas', []).copy()
        self.actual_lr_used = state_dict.get('actual_lr_used', {}).copy()
        
        # Restore metrics
        if 'metrics' in state_dict:
            metrics = state_dict['metrics']
            self.metrics = {
                'train_loss': metrics.get('train_loss', {}).copy(),
                'val_loss': metrics.get('val_loss', {}).copy(),
                'auc': metrics.get('auc', {}).copy(),
                'custom': {k: v.copy() for k, v in metrics.get('custom', {}).items()}
            }
        
        logger.info(f"🔄 LRTimeline state restored: current_epoch={self.current_epoch}, n_epochs={self.n_epochs}")
    
    def record_actual_lr(self, epoch: int, actual_lr: float) -> None:
        """
        Record the actual learning rate that was used (including boost multipliers).
        
        Args:
            epoch: Epoch number (0-indexed)
            actual_lr: The actual LR value that was applied to the optimizer
        """
        self.actual_lr_used[epoch] = actual_lr
    
    def get_phase_info(self, epoch: int) -> Tuple[str, float]:
        """
        Get phase name and progress through that phase.
        
        Args:
            epoch: Epoch number (0-indexed)
            
        Returns:
            (phase_name, progress_pct) where progress_pct is 0-100
        """
        if epoch < self.aggressive_warmup_end:
            progress = 100.0 * epoch / self.aggressive_warmup_end
            return ("aggressive_warmup", progress)
        elif epoch < self.gentle_warmup_end:
            phase_start = self.aggressive_warmup_end
            phase_end = self.gentle_warmup_end
            progress = 100.0 * (epoch - phase_start) / (phase_end - phase_start)
            return ("gentle_warmup", progress)
        elif epoch < self.onecycle_end:
            phase_start = self.gentle_warmup_end
            phase_end = self.onecycle_end
            progress = 100.0 * (epoch - phase_start) / (phase_end - phase_start)
            return ("onecycle_productive", progress)
        else:
            phase_start = self.onecycle_end
            phase_end = self.n_epochs
            if phase_end > phase_start:
                progress = 100.0 * (epoch - phase_start) / (phase_end - phase_start)
            else:
                progress = 100.0
            return ("linear_cooldown", progress)
    
    def plot_schedule(self, save_path: Optional[str] = None) -> None:
        """
        Plot the LR schedule (requires matplotlib).
        
        Args:
            save_path: Optional path to save plot image
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            logger.warning("matplotlib not available, cannot plot LR schedule")
            return
        
        epochs = list(range(self.n_epochs))
        lrs = self.schedule
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot LR curve
        ax.plot(epochs, lrs, linewidth=2, color='#2563eb', label='Learning Rate')
        
        # Mark phase boundaries
        ax.axvline(self.aggressive_warmup_end, color='orange', linestyle='--', alpha=0.5, label='End Aggressive Warmup')
        ax.axvline(self.gentle_warmup_end, color='green', linestyle='--', alpha=0.5, label='End Gentle Warmup')
        ax.axvline(self.onecycle_end, color='red', linestyle='--', alpha=0.5, label='End OneCycle')
        
        # Labels and title
        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel('Learning Rate', fontsize=12)
        ax.set_title('Custom LR Timeline Schedule', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis in scientific notation
        ax.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"📊 LR schedule plot saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def export_to_csv(self, save_path: str) -> None:
        """
        Export LR schedule to CSV file.
        
        Args:
            save_path: Path to save CSV file
        """
        path = Path(save_path)
        
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['epoch', 'learning_rate', 'phase', 'phase_progress_pct'])
            
            # Data rows
            for epoch in range(self.n_epochs):
                lr = self.get_lr(epoch)  # Use get_lr() to compute with active boosts
                phase, progress = self.get_phase_info(epoch)
                writer.writerow([epoch, f"{lr:.10e}", phase, f"{progress:.2f}"])
        
        logger.info(f"📊 LR schedule exported to: {path}")
        logger.info(f"   {self.n_epochs} epochs written")
    
    def increase_lr(self, current_epoch: int, scale_factor: float = 1.5, reason: str = "manual adjustment") -> None:
        """
        Increase learning rate for a fixed window (5% of epochs or 5 epochs, whichever is bigger).
        
        Creates a smooth boost curve that ramps up, holds, then ramps down.
        Multiple boosts can overlap and will sum together.
        
        Args:
            current_epoch: Current epoch number (boost starts at next epoch)
            scale_factor: Multiply LR by this factor (default: 1.5 = 50% increase)
            reason: Reason for adjustment (for logging/visualization)
        """
        if current_epoch >= self.n_epochs - 1:
            logger.warning(f"Cannot increase LR at epoch {current_epoch} (training ending)")
            return
        
        # Calculate boost duration: 5% of total epochs or 5 epochs, whichever is bigger
        duration_pct = 0.05  # 5%
        duration_epochs = max(5, int(self.n_epochs * duration_pct))
        
        # Ensure boost doesn't extend beyond training
        end_epoch = min(current_epoch + 1 + duration_epochs, self.n_epochs)
        actual_duration = end_epoch - (current_epoch + 1)
        
        if actual_duration <= 0:
            logger.warning(f"Cannot create boost at epoch {current_epoch} (insufficient remaining epochs)")
            return
        
        # Add boost to active list
        boost_start = current_epoch + 1
        self.active_boosts.append((boost_start, actual_duration, scale_factor, reason, "increase"))
        
        # Track adjustment for history
        self.adjustments.append((current_epoch, "increase", scale_factor, reason))
        
        logger.info(f"📈 LR INCREASED at epoch {current_epoch}:")
        logger.info(f"   Scale factor: {scale_factor}x")
        logger.info(f"   Boost window: epochs {boost_start} to {boost_start + actual_duration - 1} ({actual_duration} epochs)")
        logger.info(f"   Total active boosts: {len(self.active_boosts)}")
    
    def decrease_lr(self, current_epoch: int, scale_factor: float = 0.5, reason: str = "manual adjustment") -> None:
        """
        Decrease learning rate for a fixed window (5% of epochs or 5 epochs, whichever is bigger).
        
        Creates a smooth reduction curve that ramps down, holds, then ramps back up.
        Multiple adjustments can overlap and will sum together.
        
        Args:
            current_epoch: Current epoch number (reduction starts at next epoch)
            scale_factor: Multiply LR by this factor (default: 0.5 = 50% decrease)
            reason: Reason for adjustment (for logging/visualization)
        """
        if current_epoch >= self.n_epochs - 1:
            logger.warning(f"Cannot decrease LR at epoch {current_epoch} (training ending)")
            return
        
        # Calculate reduction duration: 5% of total epochs or 5 epochs, whichever is bigger
        duration_pct = 0.05  # 5%
        duration_epochs = max(5, int(self.n_epochs * duration_pct))
        
        # Ensure reduction doesn't extend beyond training
        end_epoch = min(current_epoch + 1 + duration_epochs, self.n_epochs)
        actual_duration = end_epoch - (current_epoch + 1)
        
        if actual_duration <= 0:
            logger.warning(f"Cannot create reduction at epoch {current_epoch} (insufficient remaining epochs)")
            return
        
        # Add reduction to active list
        reduction_start = current_epoch + 1
        self.active_boosts.append((reduction_start, actual_duration, scale_factor, reason, "decrease"))
        
        # Track adjustment for history
        self.adjustments.append((current_epoch, "decrease", scale_factor, reason))
        
        logger.info(f"📉 LR DECREASED at epoch {current_epoch}:")
        logger.info(f"   Scale factor: {scale_factor}x")
        logger.info(f"   Reduction window: epochs {reduction_start} to {reduction_start + actual_duration - 1} ({actual_duration} epochs)")
        logger.info(f"   Total active boosts: {len(self.active_boosts)}")
    
    def get_adjustment_history(self) -> List[Tuple[int, str, float, str]]:
        """
        Get history of all LR adjustments made during training.
        
        Returns:
            List of (epoch, adjustment_type, scale_factor, reason) tuples
        """
        return self.adjustments.copy()
    
    def get_delta_history(self) -> List[Tuple[int, float]]:
        """
        Get history of all LR deltas applied to the schedule.
        
        Each adjustment can modify multiple epochs. This returns the actual
        delta (change in LR) applied to each affected epoch.
        
        Returns:
            List of (epoch, delta_lr) tuples
        """
        return self.deltas.copy()
    
    def record_loss(self, epoch: int, train_loss: float, val_loss: Optional[float] = None) -> None:
        """
        Record training and validation loss for an epoch.
        
        Args:
            epoch: Epoch number
            train_loss: Training loss value
            val_loss: Optional validation loss value
        """
        self.metrics['train_loss'][epoch] = train_loss
        if val_loss is not None:
            self.metrics['val_loss'][epoch] = val_loss
    
    def record_auc(self, epoch: int, auc: float) -> None:
        """
        Record AUC metric for an epoch.
        
        Args:
            epoch: Epoch number
            auc: AUC value
        """
        self.metrics['auc'][epoch] = auc
    
    def record_metric(self, epoch: int, metric_name: str, value: float) -> None:
        """
        Record a custom metric for an epoch.
        
        Args:
            epoch: Epoch number
            metric_name: Name of the metric (e.g., 'alpha', 'f1', 'precision')
            value: Metric value
        """
        if metric_name not in self.metrics['custom']:
            self.metrics['custom'][metric_name] = {}
        self.metrics['custom'][metric_name][epoch] = value
    
    def get_metrics(self) -> dict:
        """Get all recorded metrics."""
        return self.metrics.copy()
    
    def export_enhanced_csv(self, filepath: str) -> None:
        """
        Export LR schedule + all recorded metrics to comprehensive CSV.
        
        Args:
            filepath: Path to save CSV file
        """
        filepath = Path(filepath)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Build header
            header = ['epoch', 'baseline_lr', 'adjusted_lr', 'actual_lr_used', 'phase', 'phase_progress_pct']
            header.extend(['train_loss', 'val_loss', 'auc'])
            
            # Add custom metric names
            custom_metrics = sorted(self.metrics['custom'].keys())
            header.extend(custom_metrics)
            
            header.extend(['adjustment_type', 'adjustment_factor', 'adjustment_reason'])
            
            writer.writerow(header)
            
            # Data rows
            for epoch in range(self.n_epochs):
                baseline_lr = self.baseline_schedule[epoch]
                adjusted_lr = self.get_lr(epoch)  # Use get_lr() to compute with active boosts
                actual_lr = self.actual_lr_used.get(epoch, adjusted_lr)
                phase, progress = self.get_phase_info(epoch)
                
                row = [
                    epoch,
                    f"{baseline_lr:.10e}",
                    f"{adjusted_lr:.10e}",
                    f"{actual_lr:.10e}",
                    f"{baseline_lr:.10e}",
                    phase,
                    f"{progress:.2f}"
                ]
                
                # Add loss values
                row.append(f"{self.metrics['train_loss'].get(epoch, ''):.6f}" if epoch in self.metrics['train_loss'] else '')
                row.append(f"{self.metrics['val_loss'].get(epoch, ''):.6f}" if epoch in self.metrics['val_loss'] else '')
                row.append(f"{self.metrics['auc'].get(epoch, ''):.6f}" if epoch in self.metrics['auc'] else '')
                
                # Add custom metrics
                for metric_name in custom_metrics:
                    val = self.metrics['custom'][metric_name].get(epoch, '')
                    row.append(f"{val:.6f}" if val != '' else '')
                
                # Add adjustment info if this epoch had an adjustment
                adj_info = ['', '', '']
                for adj_epoch, adj_type, factor, reason in self.adjustments:
                    if adj_epoch == epoch:
                        adj_info = [adj_type, f"{factor:.4f}", reason]
                        break
                row.extend(adj_info)
                
                writer.writerow(row)
        
        logger.info(f"📊 Enhanced CSV exported to: {filepath}")
        logger.info(f"   Includes: LR schedule + {len(self.metrics['train_loss'])} loss records")
        logger.info(f"   Custom metrics: {', '.join(custom_metrics) if custom_metrics else 'none'}")
    
    def plot_lr_comparison(self, save_path: str, figsize=(14, 8)) -> None:
        """
        Plot detailed LR comparison showing baseline vs adjusted curves with annotations.
        
        Args:
            save_path: Path to save the plot
            figsize: Figure size (width, height) in inches
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Rectangle
        except ImportError:
            logger.warning("matplotlib not available, cannot plot LR comparison")
            return
        
        epochs = list(range(self.n_epochs))
        baseline_lrs = self.baseline_schedule
        adjusted_lrs = [self.get_lr(e) for e in epochs]  # Compute with active boosts
        
        # Get actual LR used (if recorded)
        actual_lrs = [self.actual_lr_used.get(e, adjusted_lrs[e]) for e in epochs]
        has_actual = any(self.actual_lr_used.values())
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot baseline (original schedule)
        ax.plot(epochs, baseline_lrs, '--', linewidth=2, color='#94a3b8', 
                label='Original Plan', alpha=0.7, zorder=1)
        
        # Plot adjusted schedule
        ax.plot(epochs, adjusted_lrs, '-', linewidth=2, color='#2563eb',
                label='Adjusted Schedule', alpha=0.8, zorder=2)
        
        # Plot actual LR used (if different from adjusted)
        if has_actual and any(abs(actual_lrs[i] - adjusted_lrs[i]) > 1e-10 for i in range(len(epochs))):
            ax.plot(epochs, actual_lrs, '-', linewidth=2.5, color='#10b981',
                    label='Actual Used', zorder=3, marker='o', markersize=3)
        
        # Fill area between curves to show impact of adjustments
        for i in range(len(epochs)):
            if adjusted_lrs[i] > baseline_lrs[i]:
                # Increase - yellow fill
                ax.fill_between([epochs[i], epochs[i]+1] if i < len(epochs)-1 else [epochs[i]], 
                                [baseline_lrs[i]], [adjusted_lrs[i]],
                                color='#fef3c7', alpha=0.5, zorder=2)
            elif adjusted_lrs[i] < baseline_lrs[i]:
                # Decrease - blue fill
                ax.fill_between([epochs[i], epochs[i]+1] if i < len(epochs)-1 else [epochs[i]], 
                                [adjusted_lrs[i]], [baseline_lrs[i]],
                                color='#dbeafe', alpha=0.5, zorder=2)
        
        # Mark adjustments with callouts
        for adj_epoch, adj_type, factor, reason in self.adjustments:
            if adj_epoch < self.n_epochs:
                lr_at_adj = adjusted_lrs[adj_epoch]
                
                # Arrow and text
                arrow_props = dict(arrowstyle='->', lw=1.5, color='#dc2626' if adj_type == 'increase' else '#2563eb')
                
                # Position text above or below based on LR value
                y_offset = max(adjusted_lrs) * 0.15 if adj_type == 'increase' else -max(adjusted_lrs) * 0.15
                
                ax.annotate(f"Epoch {adj_epoch}\n{adj_type.upper()}\n{factor}x\n'{reason}'",
                           xy=(adj_epoch, lr_at_adj),
                           xytext=(adj_epoch, lr_at_adj + y_offset),
                           bbox=dict(boxstyle='round,pad=0.5', fc='yellow' if adj_type == 'increase' else 'lightblue', alpha=0.7),
                           arrowprops=arrow_props,
                           fontsize=8,
                           ha='center',
                           zorder=10)
                
                # Vertical line at adjustment epoch
                ax.axvline(adj_epoch, color='red' if adj_type == 'increase' else 'blue',
                          linestyle=':', alpha=0.3, zorder=1)
        
        # Phase boundaries
        ax.axvline(self.aggressive_warmup_end, color='orange', linestyle='--', alpha=0.3, label='Phase boundaries')
        ax.axvline(self.gentle_warmup_end, color='green', linestyle='--', alpha=0.3)
        ax.axvline(self.onecycle_end, color='red', linestyle='--', alpha=0.3)
        
        # Labels and formatting
        ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
        ax.set_ylabel('Learning Rate', fontsize=12, fontweight='bold')
        ax.set_title('Learning Rate Schedule: Baseline vs Adjusted\nwith Dynamic Adjustment Impacts', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 LR comparison plot saved to: {save_path}")
    
    def plot_training_history(self, save_path: str, figsize=(14, 10)) -> None:
        """
        Plot comprehensive training history with LR, loss, and metrics.
        
        Creates a 3-subplot figure:
        - Top: Learning rate curve with adjustments
        - Middle: Loss curves (train/val)
        - Bottom: Metrics (AUC, custom metrics)
        
        Args:
            save_path: Path to save the plot
            figsize: Figure size (width, height) in inches
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            logger.warning("matplotlib not available, cannot plot training history")
            return
        
        epochs = list(range(self.n_epochs))
        
        # Create figure with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, sharex=True)
        
        # ========== SUBPLOT 1: Learning Rate ==========
        baseline_lrs = self.baseline_schedule
        adjusted_lrs = self.schedule
        
        # Get actual LR used (if recorded)
        actual_lrs = [self.actual_lr_used.get(e, adjusted_lrs[e]) for e in epochs]
        has_actual = any(self.actual_lr_used.values()) and any(abs(actual_lrs[i] - adjusted_lrs[i]) > 1e-10 for i in range(len(epochs)))
        
        ax1.plot(epochs, baseline_lrs, '--', linewidth=1.5, color='#94a3b8', 
                label='Original Plan', alpha=0.6)
        ax1.plot(epochs, adjusted_lrs, '-', linewidth=2, color='#2563eb',
                label='Adjusted Schedule', alpha=0.8)
        
        # Plot actual LR used (if different from adjusted)
        if has_actual:
            ax1.plot(epochs, actual_lrs, '-', linewidth=2.5, color='#10b981',
                    label='Actual Used', marker='o', markersize=2)
        
        # Mark adjustments
        for adj_epoch, adj_type, factor, reason in self.adjustments:
            if adj_epoch < self.n_epochs:
                color = '#dc2626' if adj_type == 'increase' else '#10b981'
                symbol = '↑' if adj_type == 'increase' else '↓'
                ax1.scatter([adj_epoch], [adjusted_lrs[adj_epoch]], 
                           s=100, c=color, marker='o', zorder=10, edgecolors='black', linewidths=1.5)
                ax1.text(adj_epoch, adjusted_lrs[adj_epoch], f" {symbol}{factor}x", 
                        fontsize=8, va='bottom' if adj_type == 'increase' else 'top')
        
        ax1.set_ylabel('Learning Rate', fontsize=11, fontweight='bold')
        ax1.set_title('Training History: LR Schedule + Loss + Metrics', fontsize=14, fontweight='bold', pad=15)
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
        
        # ========== SUBPLOT 2: Loss Curves ==========
        if self.metrics['train_loss'] or self.metrics['val_loss']:
            train_epochs = sorted(self.metrics['train_loss'].keys())
            train_losses = [self.metrics['train_loss'][e] for e in train_epochs]
            
            ax2.plot(train_epochs, train_losses, '-', linewidth=2, color='#dc2626',
                    label='Train Loss', marker='o', markersize=3)
            
            if self.metrics['val_loss']:
                val_epochs = sorted(self.metrics['val_loss'].keys())
                val_losses = [self.metrics['val_loss'][e] for e in val_epochs]
                ax2.plot(val_epochs, val_losses, '--', linewidth=2, color='#f97316',
                        label='Val Loss', marker='s', markersize=3)
                
                # Mark best epoch (lowest val loss)
                if val_losses:
                    best_epoch = val_epochs[np.argmin(val_losses)]
                    best_loss = min(val_losses)
                    ax2.scatter([best_epoch], [best_loss], s=150, c='gold', marker='*',
                               zorder=10, edgecolors='black', linewidths=1.5, label='Best Epoch')
            
            ax2.set_ylabel('Loss', fontsize=11, fontweight='bold')
            ax2.legend(loc='best', fontsize=9)
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No loss data recorded', ha='center', va='center',
                    transform=ax2.transAxes, fontsize=12, color='gray')
            ax2.set_ylabel('Loss', fontsize=11, fontweight='bold')
        
        # ========== SUBPLOT 3: Metrics (AUC, etc.) ==========
        has_metrics = False
        
        # Plot AUC
        if self.metrics['auc']:
            auc_epochs = sorted(self.metrics['auc'].keys())
            auc_values = [self.metrics['auc'][e] for e in auc_epochs]
            ax3.plot(auc_epochs, auc_values, '-', linewidth=2, color='#10b981',
                    label='AUC', marker='o', markersize=3)
            has_metrics = True
        
        # Plot custom metrics
        colors = ['#8b5cf6', '#ec4899', '#f59e0b', '#06b6d4', '#84cc16']
        for i, (metric_name, metric_data) in enumerate(self.metrics['custom'].items()):
            if metric_data:
                m_epochs = sorted(metric_data.keys())
                m_values = [metric_data[e] for e in m_epochs]
                color = colors[i % len(colors)]
                ax3.plot(m_epochs, m_values, '-', linewidth=2, color=color,
                        label=metric_name, marker='o', markersize=3)
                has_metrics = True
        
        if has_metrics:
            ax3.set_ylabel('Metrics', fontsize=11, fontweight='bold')
            ax3.legend(loc='best', fontsize=9)
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No metrics recorded', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=12, color='gray')
            ax3.set_ylabel('Metrics', fontsize=11, fontweight='bold')
        
        ax3.set_xlabel('Epoch', fontsize=11, fontweight='bold')
        
        # Overall formatting
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Training history plot saved to: {save_path}")
    
    def summary(self) -> str:
        """Get a text summary of the schedule."""
        lines = []
        lines.append("=" * 60)
        lines.append("LR TIMELINE SCHEDULE SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Total Epochs: {self.n_epochs}")
        lines.append(f"Base LR: {self.base_lr:.6e}, Max LR: {self.max_lr:.6e}, Min LR: {self.min_lr:.6e}")
        lines.append("")
        lines.append("Phase Breakdown:")
        lines.append(f"  1. Aggressive Warmup (epochs 0-{self.aggressive_warmup_end}): {self.base_lr:.6e} → {self.max_lr:.6e}")
        lines.append(f"     Strategy: Quadratic ramp (fast acceleration)")
        lines.append(f"  2. Gentle Warmup (epochs {self.aggressive_warmup_end}-{self.gentle_warmup_end}): Continue → {self.max_lr:.6e}")
        lines.append(f"     Strategy: Linear ramp (steady increase)")
        lines.append(f"  3. OneCycle Productive (epochs {self.gentle_warmup_end}-{self.onecycle_end}): {self.max_lr:.6e} → {self.base_lr:.6e}")
        lines.append(f"     Strategy: Cosine annealing (peak at middle)")
        lines.append(f"  4. Linear Cooldown (epochs {self.onecycle_end}-{self.n_epochs}): {self.base_lr:.6e} → {self.min_lr:.6e}")
        lines.append(f"     Strategy: Linear descent (smooth convergence)")
        
        if self.adjustments:
            lines.append("")
            lines.append("Dynamic Adjustments Made:")
            for epoch, adj_type, scale, reason in self.adjustments:
                lines.append(f"  - Epoch {epoch}: {adj_type.upper()} by {scale}x ({reason})")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def test_lr_timeline_comprehensive():
    """Comprehensive test with metrics tracking and visualization."""
    import numpy as np
    
    print("=" * 80)
    print("COMPREHENSIVE LR TIMELINE TEST WITH METRICS TRACKING")
    print("=" * 80)
    print()
    
    # Create timeline
    timeline = LRTimeline(
        n_epochs=50,
        base_lr=1e-04,
        max_lr=1e-03,
        min_lr=1e-05
    )
    
    print(timeline.summary())
    print()
    
    # Simulate training with metrics
    print("Simulating training with metrics...")
    np.random.seed(42)
    
    for epoch in range(50):
        # Simulate loss decreasing with noise
        train_loss = 1.0 * np.exp(-epoch/15) + np.random.normal(0, 0.05)
        val_loss = train_loss * 1.1 + np.random.normal(0, 0.03)
        
        # Simulate AUC increasing
        auc = 0.5 + 0.4 * (1 - np.exp(-epoch/10)) + np.random.normal(0, 0.02)
        auc = np.clip(auc, 0, 1)
        
        # Simulate custom metric (alpha)
        alpha = 0.1 + epoch * 0.01
        
        # Record metrics
        timeline.record_loss(epoch, train_loss, val_loss)
        timeline.record_auc(epoch, auc)
        timeline.record_metric(epoch, 'alpha', alpha)
        
        # Simulate dynamic adjustments based on training behavior
        if epoch == 10 and train_loss > 0.4:
            timeline.increase_lr(epoch, scale_factor=1.5, reason="training too slow")
        elif epoch == 25 and abs(val_loss - timeline.metrics['val_loss'].get(24, 0)) < 0.01:
            timeline.decrease_lr(epoch, scale_factor=0.7, reason="loss plateau")
        elif epoch == 35:
            timeline.increase_lr(epoch, scale_factor=1.2, reason="resumed learning")
        
        timeline.step()
    
    print("\n✅ Training simulation complete!")
    print(f"   Recorded {len(timeline.metrics['train_loss'])} epochs of loss data")
    print(f"   Recorded {len(timeline.metrics['auc'])} epochs of AUC data")
    print(f"   Made {len(timeline.adjustments)} dynamic LR adjustments")
    print()
    
    # Export data
    print("=" * 80)
    print("EXPORTING DATA")
    print("=" * 80)
    
    timeline.export_to_csv("lr_timeline_basic.csv")
    timeline.export_enhanced_csv("lr_timeline_enhanced.csv")
    print()
    
    # Generate visualizations
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    
    try:
        timeline.plot_lr_comparison("lr_comparison.png")
        timeline.plot_training_history("training_history.png")
        timeline.plot_schedule("lr_schedule_simple.png")
        print("\n✅ All visualizations generated successfully!")
    except Exception as e:
        print(f"\n⚠️  Visualization error: {e}")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Generated files:")
    print("  Data:")
    print("    - lr_timeline_basic.csv (LR schedule only)")
    print("    - lr_timeline_enhanced.csv (LR + all metrics)")
    print("  Visualizations:")
    print("    - lr_schedule_simple.png (basic LR curve)")
    print("    - lr_comparison.png (baseline vs adjusted with callouts)")
    print("    - training_history.png (comprehensive 3-subplot view)")
    print()


if __name__ == "__main__":
    test_lr_timeline_comprehensive()

