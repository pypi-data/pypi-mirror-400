"""
Option A: In-Training Validation (FREE)

Validates importance scoring by observing whether high-scored pairs
actually have positive lift, and checking rank correlation.

Zero extra training time - just observes and reports.
"""

import numpy as np
from typing import Dict, List, Tuple, Set
from scipy.stats import spearmanr
from dataclasses import dataclass


@dataclass
class ValidationReport:
    """Results of importance scoring validation."""
    
    # Correlation between importance scores and actual lift
    rank_correlation: float  # Spearman ρ
    rank_correlation_pvalue: float
    
    # Top-ranked pairs (by importance)
    top_20_mean_lift: float
    top_20_std_lift: float
    top_20_pct_positive: float  # % with positive lift
    top_20_pairs: List[Tuple[Tuple[int, int], float, float]]  # (pair, importance, actual_lift)
    
    # Bottom-ranked pairs (by importance)
    bottom_20_mean_lift: float
    bottom_20_std_lift: float
    bottom_20_pct_positive: float
    bottom_20_pairs: List[Tuple[Tuple[int, int], float, float]]
    
    # Misclassified pairs
    false_positives: List[Tuple[Tuple[int, int], float, float]]  # High importance, negative lift
    false_negatives: List[Tuple[Tuple[int, int], float, float]]  # Low importance, positive lift
    
    # Overall stats
    n_pairs_total: int
    mean_importance: float
    mean_actual_lift: float
    
    def is_valid(self) -> bool:
        """Is the importance scoring working well?"""
        return (
            self.rank_correlation > 0.6 and  # Strong positive correlation
            self.top_20_mean_lift > 0.0 and  # Top pairs have positive lift
            self.top_20_pct_positive > 0.7   # Most top pairs are positive
        )
    
    def grade(self) -> str:
        """Letter grade for scoring quality."""
        if self.rank_correlation > 0.8 and self.top_20_pct_positive > 0.85:
            return "A (Excellent)"
        elif self.rank_correlation > 0.6 and self.top_20_pct_positive > 0.70:
            return "B (Good)"
        elif self.rank_correlation > 0.4 and self.top_20_pct_positive > 0.60:
            return "C (Acceptable)"
        elif self.rank_correlation > 0.2:
            return "D (Poor)"
        else:
            return "F (Broken)"


class ImportanceScoringValidator:
    """
    Validate importance scoring during training by observing actual effects.
    
    Usage:
        validator = ImportanceScoringValidator(col_names)
        
        # During training:
        validator.record_epoch(epoch, active_pairs, col_losses)
        
        # At end of training:
        report = validator.validate_importance_scoring(importance_scores)
        report.print_summary()
    """
    
    def __init__(self, col_names: List[str]):
        self.col_names = col_names
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
        """Record state for this epoch (same as causal scorer)."""
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
    
    def compute_actual_lift(
        self,
        pair: Tuple[int, int],
        window: int = 5,
    ) -> Tuple[float, int, int]:
        """
        Compute actual observed lift for a pair.
        
        Returns:
            (mean_lift, n_paired_observations, n_unpaired_observations)
        """
        i, j = pair
        col_i_name = self.col_names[i]
        col_j_name = self.col_names[j]
        
        # Get epochs when paired/unpaired
        paired_epochs = self._pair_active_epochs.get(pair, set())
        unpaired_epochs = self._all_epochs - paired_epochs
        
        # Compute lift for both directions
        lifts = []
        
        for col_name in [col_i_name, col_j_name]:
            if col_name not in self._column_loss_history:
                continue
            
            losses = self._column_loss_history[col_name]
            
            # Improvement rates when PAIRED
            paired_improvements = []
            for epoch in paired_epochs:
                if epoch < window or epoch >= len(losses):
                    continue
                loss_then = losses[epoch - window]
                loss_now = losses[epoch]
                improvement_rate = (loss_then - loss_now) / window
                paired_improvements.append(improvement_rate)
            
            # Improvement rates when UNPAIRED
            unpaired_improvements = []
            for epoch in unpaired_epochs:
                if epoch < window or epoch >= len(losses):
                    continue
                loss_then = losses[epoch - window]
                loss_now = losses[epoch]
                improvement_rate = (loss_then - loss_now) / window
                unpaired_improvements.append(improvement_rate)
            
            # Lift = difference in improvement rates
            if paired_improvements and unpaired_improvements:
                mean_paired = np.mean(paired_improvements)
                mean_unpaired = np.mean(unpaired_improvements)
                lift = mean_paired - mean_unpaired
                lifts.append(lift)
        
        if not lifts:
            return 0.0, 0, 0
        
        # Average lift across both directions
        mean_lift = np.mean(lifts)
        n_paired = len(paired_epochs)
        n_unpaired = len(unpaired_epochs)
        
        return mean_lift, n_paired, n_unpaired
    
    def validate_importance_scoring(
        self,
        importance_scores: Dict[Tuple[int, int], float],
        threshold_top: float = 0.8,    # Top 20%
        threshold_bottom: float = 0.2,  # Bottom 20%
    ) -> ValidationReport:
        """
        Validate importance scores against actual observed lift.
        
        Args:
            importance_scores: {(i,j): importance_score} from scoring system
            threshold_top: Percentile for "top" pairs (0.8 = top 20%)
            threshold_bottom: Percentile for "bottom" pairs (0.2 = bottom 20%)
        
        Returns:
            ValidationReport with correlation, top/bottom stats, misclassifications
        """
        # Compute actual lift for all pairs
        pairs_with_data = []
        for pair in importance_scores.keys():
            actual_lift, n_paired, n_unpaired = self.compute_actual_lift(pair)
            
            # Only include pairs with sufficient observations
            if n_paired >= 3 and n_unpaired >= 3:
                importance = importance_scores[pair]
                pairs_with_data.append((pair, importance, actual_lift))
        
        if not pairs_with_data:
            raise ValueError("No pairs with sufficient observations for validation")
        
        # Extract arrays for correlation
        pairs = [p[0] for p in pairs_with_data]
        importances = np.array([p[1] for p in pairs_with_data])
        actual_lifts = np.array([p[2] for p in pairs_with_data])
        
        # Compute rank correlation (Spearman)
        rho, pvalue = spearmanr(importances, actual_lifts)
        
        # Sort by importance (high to low)
        sorted_indices = np.argsort(importances)[::-1]
        sorted_pairs_data = [(pairs[i], importances[i], actual_lifts[i]) 
                             for i in sorted_indices]
        
        # Top 20% and Bottom 20%
        n_top = max(1, int(len(sorted_pairs_data) * (1 - threshold_top)))
        n_bottom = max(1, int(len(sorted_pairs_data) * threshold_bottom))
        
        top_pairs = sorted_pairs_data[:n_top]
        bottom_pairs = sorted_pairs_data[-n_bottom:]
        
        # Stats for top pairs
        top_lifts = np.array([p[2] for p in top_pairs])
        top_20_mean = np.mean(top_lifts)
        top_20_std = np.std(top_lifts)
        top_20_pct_pos = (top_lifts > 0).sum() / len(top_lifts)
        
        # Stats for bottom pairs
        bottom_lifts = np.array([p[2] for p in bottom_pairs])
        bottom_20_mean = np.mean(bottom_lifts)
        bottom_20_std = np.std(bottom_lifts)
        bottom_20_pct_pos = (bottom_lifts > 0).sum() / len(bottom_lifts)
        
        # Find misclassifications
        # False positives: High importance but negative lift
        median_importance = np.median(importances)
        false_positives = [
            (pair, imp, lift) 
            for pair, imp, lift in sorted_pairs_data
            if imp > median_importance and lift < -0.01  # Significantly negative
        ]
        
        # False negatives: Low importance but positive lift
        false_negatives = [
            (pair, imp, lift)
            for pair, imp, lift in sorted_pairs_data
            if imp < median_importance and lift > 0.05  # Significantly positive
        ]
        
        # Overall stats
        mean_importance = np.mean(importances)
        mean_actual_lift = np.mean(actual_lifts)
        
        return ValidationReport(
            rank_correlation=rho,
            rank_correlation_pvalue=pvalue,
            top_20_mean_lift=top_20_mean,
            top_20_std_lift=top_20_std,
            top_20_pct_positive=top_20_pct_pos,
            top_20_pairs=top_pairs[:10],  # Show top 10
            bottom_20_mean_lift=bottom_20_mean,
            bottom_20_std_lift=bottom_20_std,
            bottom_20_pct_positive=bottom_20_pct_pos,
            bottom_20_pairs=bottom_pairs[:10],  # Show worst 10
            false_positives=false_positives[:10],
            false_negatives=false_negatives[:10],
            n_pairs_total=len(pairs_with_data),
            mean_importance=mean_importance,
            mean_actual_lift=mean_actual_lift,
        )
    
    def print_validation_report(self, report: ValidationReport):
        """Print human-readable validation report."""
        print("\n" + "="*80)
        print("IMPORTANCE SCORING VALIDATION REPORT")
        print("="*80)
        
        # Overall grade
        grade = report.grade()
        valid = "✅ VALID" if report.is_valid() else "❌ INVALID"
        print(f"\nGrade: {grade} {valid}")
        print(f"Total pairs evaluated: {report.n_pairs_total}")
        
        # Correlation
        print(f"\n{'─'*80}")
        print("RANK CORRELATION (Does high importance = high actual lift?)")
        print(f"{'─'*80}")
        print(f"Spearman ρ: {report.rank_correlation:.3f} (p={report.rank_correlation_pvalue:.3e})")
        
        if report.rank_correlation > 0.7:
            print("✅ STRONG positive correlation - scoring works well")
        elif report.rank_correlation > 0.5:
            print("⚠️  MODERATE positive correlation - scoring works okay")
        elif report.rank_correlation > 0.3:
            print("⚠️  WEAK positive correlation - scoring needs improvement")
        else:
            print("❌ NO correlation - scoring is broken or random")
        
        # Top 20% pairs
        print(f"\n{'─'*80}")
        print(f"TOP 20% PAIRS (by importance score)")
        print(f"{'─'*80}")
        print(f"Mean actual lift: {report.top_20_mean_lift:+.4f} ± {report.top_20_std_lift:.4f}")
        print(f"% with positive lift: {report.top_20_pct_positive*100:.1f}%")
        
        if report.top_20_mean_lift > 0.05 and report.top_20_pct_positive > 0.7:
            print("✅ Top-ranked pairs are HELPING (scoring is correct)")
        elif report.top_20_mean_lift > 0:
            print("⚠️  Top-ranked pairs slightly positive (scoring okay)")
        else:
            print("❌ Top-ranked pairs NOT helping (scoring is wrong!)")
        
        print(f"\nExample top pairs:")
        for pair, importance, lift in report.top_20_pairs[:5]:
            i, j = pair
            col_i = self.col_names[i]
            col_j = self.col_names[j]
            status = "✅" if lift > 0 else "❌"
            print(f"  {status} ({col_i} ↔ {col_j}): importance={importance:+.3f}, actual_lift={lift:+.4f}")
        
        # Bottom 20% pairs
        print(f"\n{'─'*80}")
        print(f"BOTTOM 20% PAIRS (by importance score)")
        print(f"{'─'*80}")
        print(f"Mean actual lift: {report.bottom_20_mean_lift:+.4f} ± {report.bottom_20_std_lift:.4f}")
        print(f"% with positive lift: {report.bottom_20_pct_positive*100:.1f}%")
        
        if report.bottom_20_mean_lift < 0 and report.bottom_20_pct_positive < 0.3:
            print("✅ Bottom-ranked pairs are HURTING (scoring is correct)")
        elif report.bottom_20_mean_lift < 0.02:
            print("⚠️  Bottom-ranked pairs near zero (scoring okay)")
        else:
            print("❌ Bottom-ranked pairs are HELPING (scoring missed good pairs!)")
        
        print(f"\nExample bottom pairs:")
        for pair, importance, lift in report.bottom_20_pairs[:5]:
            i, j = pair
            col_i = self.col_names[i]
            col_j = self.col_names[j]
            status = "✅" if lift <= 0 else "❌"
            print(f"  {status} ({col_i} ↔ {col_j}): importance={importance:+.3f}, actual_lift={lift:+.4f}")
        
        # Misclassifications
        if report.false_positives:
            print(f"\n{'─'*80}")
            print(f"FALSE POSITIVES (High importance, negative lift)")
            print(f"{'─'*80}")
            print(f"Count: {len(report.false_positives)}")
            print("These pairs were KEPT but actually HURT:")
            for pair, importance, lift in report.false_positives[:5]:
                i, j = pair
                col_i = self.col_names[i]
                col_j = self.col_names[j]
                print(f"  ❌ ({col_i} ↔ {col_j}): importance={importance:+.3f}, actual_lift={lift:+.4f}")
        
        if report.false_negatives:
            print(f"\n{'─'*80}")
            print(f"FALSE NEGATIVES (Low importance, positive lift)")
            print(f"{'─'*80}")
            print(f"Count: {len(report.false_negatives)}")
            print("These pairs were PRUNED but actually HELP:")
            for pair, importance, lift in report.false_negatives[:5]:
                i, j = pair
                col_i = self.col_names[i]
                col_j = self.col_names[j]
                print(f"  ❌ ({col_i} ↔ {col_j}): importance={importance:+.3f}, actual_lift={lift:+.4f}")
        
        # Summary recommendation
        print(f"\n{'='*80}")
        print("RECOMMENDATION")
        print(f"{'='*80}")
        
        if report.is_valid():
            print("✅ Importance scoring is working well - keep using it!")
        elif report.rank_correlation > 0.4:
            print("⚠️  Importance scoring is okay but could be improved")
            print("   Consider: Tuning parameters or using causal lift directly")
        else:
            print("❌ Importance scoring is not working - needs major changes")
            print("   Recommend: Switch to causal lift calculation")
        
        print("="*80 + "\n")


# Example usage in DynamicRelationshipExtractor
"""
class DynamicRelationshipExtractor(nn.Module):
    def __init__(self, ...):
        ...
        # Add validator
        self.validator = ImportanceScoringValidator(col_names=col_names_in_order)
    
    def progressive_prune_relationships(self):
        # Record epoch for validation
        self.validator.record_epoch(
            epoch_idx=self.current_epoch,
            active_pairs=active_pairs,
            col_losses=self.col_marginal_losses,
        )
        
        # ... existing pruning logic ...
    
    def finalize_training(self):
        '''Call this at end of training to validate importance scoring.'''
        # Get final importance scores
        importance_scores = self._compute_relationship_importance()
        
        # Validate
        report = self.validator.validate_importance_scoring(importance_scores)
        self.validator.print_validation_report(report)
        
        # Log to file for analysis
        import json
        with open('importance_validation.json', 'w') as f:
            json.dump({
                'grade': report.grade(),
                'valid': report.is_valid(),
                'rank_correlation': report.rank_correlation,
                'top_20_mean_lift': report.top_20_mean_lift,
                'bottom_20_mean_lift': report.bottom_20_mean_lift,
            }, f, indent=2)
"""

