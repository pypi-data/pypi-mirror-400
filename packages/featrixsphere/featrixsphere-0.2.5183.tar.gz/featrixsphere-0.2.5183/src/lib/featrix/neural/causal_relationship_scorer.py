"""
Causal Relationship Importance Scorer

Not bullshit. Measures actual marginal benefit of keeping pairs.

Core principle:
    importance(i,j) = LCB(lift(i→j) + lift(j→i)) + recency_bonus - complexity_penalty

Where lift(i→j) = improvement rate of j when paired with i minus baseline rate for j.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LiftEstimate:
    """Lift estimate with uncertainty."""
    mean: float
    std: float  # Standard error
    n_treated: int  # Number of paired observations
    n_control: int  # Number of unpaired observations
    
    def lcb(self, confidence: float = 1.96) -> float:
        """Lower confidence bound."""
        return self.mean - confidence * self.std
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        """Is lift significantly different from zero?"""
        z_score = self.mean / max(self.std, 1e-9)
        critical_value = 1.96  # Two-tailed test at alpha=0.05
        return abs(z_score) > critical_value


class CausalRelationshipScorer:
    """
    Score relationships based on causal effect with uncertainty.
    
    Maintains history and computes lift using counterfactual reasoning.
    """
    
    def __init__(
        self,
        col_names: List[str],
        window: int = 5,              # Lookback window for improvement rate
        decay_rate: float = 0.95,      # Exponential decay for recency
        lcb_confidence: float = 1.96,  # 95% confidence interval
        min_observations: int = 3,     # Minimum observations for trust
    ):
        self.col_names = col_names
        self.window = window
        self.decay_rate = decay_rate
        self.lcb_confidence = lcb_confidence
        self.min_observations = min_observations
        
        # History tracking
        self._column_loss_history: Dict[str, List[float]] = {}
        self._pair_active_epochs: Dict[Tuple[int, int], Set[int]] = {}
        self._all_epochs: Set[int] = set()
        self.current_epoch: int = 0
    
    def record_epoch(
        self,
        epoch_idx: int,
        active_pairs: List[Tuple[int, int]],
        col_losses: Dict[str, float],
    ):
        """
        Record state for this epoch.
        
        Args:
            epoch_idx: Current epoch number
            active_pairs: Pairs that were active (computed) this epoch
            col_losses: {col_name: marginal_loss} for all columns
        """
        self.current_epoch = epoch_idx
        self._all_epochs.add(epoch_idx)
        
        # Store column losses
        for col_name, loss in col_losses.items():
            if col_name not in self._column_loss_history:
                self._column_loss_history[col_name] = []
            self._column_loss_history[col_name].append(loss)
        
        # Track which pairs were active
        for pair in active_pairs:
            if pair not in self._pair_active_epochs:
                self._pair_active_epochs[pair] = set()
            self._pair_active_epochs[pair].add(epoch_idx)
    
    def compute_lift(
        self,
        pair: Tuple[int, int],
        target_col_name: str,
        use_recency: bool = True,
    ) -> Optional[LiftEstimate]:
        """
        Compute causal lift: improvement when paired vs unpaired.
        
        Args:
            pair: (col_i_idx, col_j_idx) - we're measuring effect on target_col
            target_col_name: Column whose improvement we're measuring
            use_recency: Apply exponential recency weighting
        
        Returns:
            LiftEstimate with mean, std, and observation counts
        """
        # CRITICAL: Crash if we don't have the data we need
        assert target_col_name in self._column_loss_history, (
            f"CRITICAL BUG: Column '{target_col_name}' not in _column_loss_history. "
            f"Available columns: {list(self._column_loss_history.keys())}. "
            f"This means record_epoch() was not called with loss data for this column."
        )
        
        losses = self._column_loss_history[target_col_name]
        paired_epochs = self._pair_active_epochs.get(pair, set())
        unpaired_epochs = self._all_epochs - paired_epochs
        
        # CRITICAL: We need both paired and unpaired epochs for comparison
        assert len(paired_epochs) > 0 or len(unpaired_epochs) > 0, (
            f"CRITICAL BUG: Pair {pair} has no paired epochs ({len(paired_epochs)}) "
            f"and no unpaired epochs ({len(unpaired_epochs)}). "
            f"Total epochs: {len(self._all_epochs)}. "
            f"This means the pair was never active AND we have no control data."
        )
        
        # Compute improvement rates when PAIRED (treatment)
        paired_improvements = []
        paired_weights = []
        
        for epoch in paired_epochs:
            if epoch < self.window or epoch >= len(losses):
                continue
            
            # Improvement over window
            loss_then = losses[epoch - self.window]
            loss_now = losses[epoch]
            improvement_rate = (loss_then - loss_now) / self.window
            
            paired_improvements.append(improvement_rate)
            
            if use_recency:
                age = self.current_epoch - epoch
                weight = self.decay_rate ** age
                paired_weights.append(weight)
            else:
                paired_weights.append(1.0)
        
        # Compute improvement rates when UNPAIRED (control)
        unpaired_improvements = []
        unpaired_weights = []
        
        for epoch in unpaired_epochs:
            if epoch < self.window or epoch >= len(losses):
                continue
            
            loss_then = losses[epoch - self.window]
            loss_now = losses[epoch]
            improvement_rate = (loss_then - loss_now) / self.window
            
            unpaired_improvements.append(improvement_rate)
            
            if use_recency:
                age = self.current_epoch - epoch
                weight = self.decay_rate ** age
                unpaired_weights.append(weight)
            else:
                unpaired_weights.append(1.0)
        
        # Graceful degradation: return None if insufficient data (don't crash)
        if not paired_improvements:
            return None  # Signal "insufficient data, skip this pair"
        
        if not unpaired_improvements:
            return None  # Signal "insufficient data, skip this pair"
        
        # Weighted means
        mean_paired = np.average(paired_improvements, weights=paired_weights)
        mean_unpaired = np.average(unpaired_improvements, weights=unpaired_weights)
        
        # Lift = treatment effect
        lift_mean = mean_paired - mean_unpaired
        
        # Standard error of difference
        # For weighted data, use effective sample size
        if use_recency:
            # Effective sample size: (sum weights)^2 / (sum weights^2)
            eff_n_paired = (sum(paired_weights) ** 2 / 
                           sum(w**2 for w in paired_weights))
            eff_n_unpaired = (sum(unpaired_weights) ** 2 / 
                             sum(w**2 for w in unpaired_weights))
        else:
            eff_n_paired = len(paired_improvements)
            eff_n_unpaired = len(unpaired_improvements)
        
        # Graceful degradation: return None if insufficient sample size
        if eff_n_paired <= 1 or eff_n_unpaired <= 1:
            return None  # Signal "insufficient data, skip this pair"
        
        # Variance (unweighted for simplicity - could do weighted)
        var_paired = np.var(paired_improvements, ddof=1)
        var_unpaired = np.var(unpaired_improvements, ddof=1)
        
        # Standard error of difference in means
        se_diff = np.sqrt(var_paired / eff_n_paired + 
                         var_unpaired / eff_n_unpaired)
        
        # Graceful degradation: return None if standard error is not finite
        if not np.isfinite(se_diff):
            return None  # Signal "insufficient data, skip this pair"
        
        return LiftEstimate(
            mean=lift_mean,
            std=se_diff,
            n_treated=len(paired_improvements),
            n_control=len(unpaired_improvements),
        )
    
    def compute_importance(
        self,
        pair: Tuple[int, int],
    ) -> Tuple[float, Dict]:
        """
        Compute full importance score with breakdown.
        
        Returns:
            (importance_score, breakdown_dict)
        """
        i, j = pair
        col_i_name = self.col_names[i]
        col_j_name = self.col_names[j]
        
        # Lift in both directions
        lift_ij = self.compute_lift(pair, col_j_name, use_recency=True)
        lift_ji = self.compute_lift(pair, col_i_name, use_recency=True)
        
        # Combined lift (bidirectional benefit)
        total_lift_mean = lift_ij.mean + lift_ji.mean
        total_lift_std = np.sqrt(lift_ij.std**2 + lift_ji.std**2)
        
        # Lower confidence bound (conservative estimate)
        lcb_base = total_lift_mean - self.lcb_confidence * total_lift_std
        
        # Sample size penalty
        min_n = min(
            min(lift_ij.n_treated, lift_ij.n_control),
            min(lift_ji.n_treated, lift_ji.n_control),
        )
        
        if min_n < self.min_observations:
            # Penalize insufficient data
            sample_penalty = np.sqrt(self.min_observations / max(1, min_n))
            lcb_score = lcb_base / sample_penalty
        else:
            lcb_score = lcb_base
        
        # Complexity penalty (insufficient observations)
        total_obs = (lift_ij.n_treated + lift_ij.n_control + 
                    lift_ji.n_treated + lift_ji.n_control) / 2
        
        if total_obs < 2 * self.min_observations:
            missing = 2 * self.min_observations - total_obs
            complexity_penalty = missing * 0.05
        else:
            complexity_penalty = 0.0
        
        # Final importance
        importance = lcb_score - complexity_penalty
        
        # Breakdown for debugging
        breakdown = {
            'importance': importance,
            'lcb_score': lcb_score,
            'complexity_penalty': complexity_penalty,
            # Direction i→j
            'lift_ij_mean': lift_ij.mean,
            'lift_ij_std': lift_ij.std,
            'lift_ij_lcb': lift_ij.lcb(self.lcb_confidence),
            'lift_ij_significant': lift_ij.is_significant(),
            'lift_ij_n_paired': lift_ij.n_treated,
            'lift_ij_n_unpaired': lift_ij.n_control,
            # Direction j→i
            'lift_ji_mean': lift_ji.mean,
            'lift_ji_std': lift_ji.std,
            'lift_ji_lcb': lift_ji.lcb(self.lcb_confidence),
            'lift_ji_significant': lift_ji.is_significant(),
            'lift_ji_n_paired': lift_ji.n_treated,
            'lift_ji_n_unpaired': lift_ji.n_control,
            # Combined
            'total_lift_mean': total_lift_mean,
            'total_lift_std': total_lift_std,
            'confidence_interval_width': 2 * self.lcb_confidence * total_lift_std,
        }
        
        return importance, breakdown
    
    def rank_pairs(
        self,
        pairs: List[Tuple[int, int]],
    ) -> List[Tuple[Tuple[int, int], float, Dict]]:
        """
        Rank pairs by importance (highest first).
        
        Returns:
            List of (pair, importance, breakdown) sorted by importance
        """
        scored_pairs = []
        for pair in pairs:
            importance, breakdown = self.compute_importance(pair)
            scored_pairs.append((pair, importance, breakdown))
        
        # Sort by importance (highest first = most beneficial)
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_pairs
    
    def log_pruning_decision(
        self,
        pairs_to_disable: List[Tuple[Tuple[int, int], float, Dict]],
        pairs_to_keep: List[Tuple[Tuple[int, int], float, Dict]],
        n_show: int = 5,
    ):
        """
        Log pruning decisions with causal interpretation.
        
        Args:
            pairs_to_disable: List of (pair, importance, breakdown) being pruned
            pairs_to_keep: List of (pair, importance, breakdown) being kept
            n_show: Number of pairs to show in log
        """
        print(f"\n{'='*80}")
        print(f"CAUSAL RELATIONSHIP PRUNING - Epoch {self.current_epoch}")
        print(f"{'='*80}")
        
        if pairs_to_disable:
            print(f"\n🔪 PRUNING (worst {n_show} of {len(pairs_to_disable)}):")
            for pair, importance, breakdown in pairs_to_disable[:n_show]:
                i, j = pair
                col_i = self.col_names[i]
                col_j = self.col_names[j]
                
                print(f"\n   ({col_i} ↔ {col_j}): importance={importance:+.4f}")
                print(f"      ├─ lift({col_i}→{col_j}): {breakdown['lift_ij_mean']:+.4f} ± {breakdown['lift_ij_std']:.4f}")
                print(f"      │  └─ {col_j} {'improves' if breakdown['lift_ij_mean'] > 0 else 'worsens'} by {abs(breakdown['lift_ij_mean']):.4f}/epoch when paired")
                print(f"      ├─ lift({col_j}→{col_i}): {breakdown['lift_ji_mean']:+.4f} ± {breakdown['lift_ji_std']:.4f}")
                print(f"      │  └─ {col_i} {'improves' if breakdown['lift_ji_mean'] > 0 else 'worsens'} by {abs(breakdown['lift_ji_mean']):.4f}/epoch when paired")
                print(f"      ├─ LCB (conservative): {breakdown['lcb_score']:+.4f}")
                print(f"      └─ Observations: {breakdown['lift_ij_n_paired']} paired, {breakdown['lift_ij_n_unpaired']} unpaired")
                
                if breakdown['lift_ij_mean'] < 0 and breakdown['lift_ji_mean'] < 0:
                    print(f"      ⚠️  HARMFUL: Both columns worse when paired!")
                elif abs(breakdown['total_lift_mean']) < 0.01:
                    print(f"      ~ NEUTRAL: No clear benefit")
        
        if pairs_to_keep:
            print(f"\n✅ KEEPING (best {n_show} of {len(pairs_to_keep)}):")
            for pair, importance, breakdown in pairs_to_keep[:n_show]:
                i, j = pair
                col_i = self.col_names[i]
                col_j = self.col_names[j]
                
                print(f"\n   ({col_i} ↔ {col_j}): importance={importance:+.4f}")
                print(f"      ├─ lift({col_i}→{col_j}): {breakdown['lift_ij_mean']:+.4f} ± {breakdown['lift_ij_std']:.4f}")
                print(f"      │  └─ {col_j} improves by {breakdown['lift_ij_mean']:.4f}/epoch when paired")
                print(f"      ├─ lift({col_j}→{col_i}): {breakdown['lift_ji_mean']:+.4f} ± {breakdown['lift_ji_std']:.4f}")
                print(f"      │  └─ {col_i} improves by {breakdown['lift_ji_mean']:.4f}/epoch when paired")
                print(f"      ├─ LCB (conservative): {breakdown['lcb_score']:+.4f}")
                print(f"      └─ Observations: {breakdown['lift_ij_n_paired']} paired, {breakdown['lift_ij_n_unpaired']} unpaired")
                
                if breakdown['lift_ij_significant'] and breakdown['lift_ji_significant']:
                    print(f"      ✅ SIGNIFICANT: High-confidence mutual benefit")
        
        print(f"\n{'='*80}\n")


# Example usage in DynamicRelationshipExtractor
"""
class DynamicRelationshipExtractor(nn.Module):
    def __init__(self, ...):
        ...
        self.causal_scorer = CausalRelationshipScorer(
            col_names=col_names_in_order,
            window=5,
            decay_rate=0.95,
            lcb_confidence=1.96,  # 95% CI
            min_observations=3,
        )
    
    def progressive_prune_relationships(self):
        # Record this epoch
        self.causal_scorer.record_epoch(
            epoch_idx=self.current_epoch,
            active_pairs=active_pairs,
            col_losses=self.col_marginal_losses,
        )
        
        # Rank all pairs by causal importance
        ranked_pairs = self.causal_scorer.rank_pairs(active_pairs)
        
        # Prune bottom N pairs (negative or low LCB)
        pairs_to_disable = ranked_pairs[-num_to_prune:]
        pairs_to_keep = ranked_pairs[:-num_to_prune]
        
        # Log with causal interpretation
        self.causal_scorer.log_pruning_decision(
            pairs_to_disable=pairs_to_disable,
            pairs_to_keep=pairs_to_keep,
            n_show=5,
        )
        
        # Disable low-importance pairs
        for pair, importance, breakdown in pairs_to_disable:
            self.disabled_pairs.add(pair)
"""

