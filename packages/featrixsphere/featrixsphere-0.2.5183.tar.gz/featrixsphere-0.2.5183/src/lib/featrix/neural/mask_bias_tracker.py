#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import logging
import numpy as np
import torch

from featrix.neural.featrix_token import TokenStatus

logger = logging.getLogger(__name__)


class MaskBiasTracker:
    """
    Tracks masking distribution to detect bias in column masking.
    
    Accumulates statistics per epoch:
    - Per-mask masking ratios (40-60% target)
    - Per-column mask counts per mask (for bias detection)
    - Complementary mask invariants (overlap, coverage, balance)
    - Union target coverage (sanity check - should be 100% for complementary masks)
    """
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all statistics for a new epoch."""
        # Union metric (renamed from "masked" - tracks if column is MARGINAL in either mask)
        self.union_target_coverage_per_column = {}  # col_idx -> count (marginal in mask_A OR mask_B)
        
        # Per-mask column counts (for bias detection)
        self.mask_A_count_per_column = {}  # col_idx -> count (marginal in mask_A)
        self.mask_B_count_per_column = {}  # col_idx -> count (marginal in mask_B)
        
        # Per-row masking ratios (using PRESENT columns only)
        self.mask_A_ratios = []  # List of ratioA = margA / present for each row
        self.mask_B_ratios = []  # List of ratioB = margB / present for each row
        
        # Complementary mask invariants
        self.overlap_violations = 0  # Count of rows where margA & margB != 0
        self.coverage_violations = 0  # Count of rows where (margA | margB) != present
        self.balance_diffs = []  # List of abs(margA - margB) for each row
        
        # Present columns per row
        self.present_cols_per_row = []  # Track number of PRESENT columns per row
        
        # Unique mask patterns
        self.unique_mask_patterns = set()  # Set of mask pattern strings
        
        self.total_batches = 0
        self.total_rows_masked = 0
    
    def record_batch(self, mask_1, mask_2, col_names=None):
        """
        Record mask patterns from a batch.
        
        Args:
            mask_1: (batch_size, n_cols) tensor with TokenStatus (mask_A)
            mask_2: (batch_size, n_cols) tensor with TokenStatus (mask_B)
            col_names: Optional list of column names for logging
        """
        self.total_batches += 1
        
        # Convert to CPU numpy for tracking
        mask_1_np = mask_1.cpu().numpy() if torch.is_tensor(mask_1) else mask_1
        mask_2_np = mask_2.cpu().numpy() if torch.is_tensor(mask_2) else mask_2
        
        batch_size, n_cols = mask_1_np.shape
        
        for row_idx in range(batch_size):
            self.total_rows_masked += 1
            
            # Identify PRESENT columns (not NOT_PRESENT)
            present_mask = (mask_1_np[row_idx] != TokenStatus.NOT_PRESENT) | (mask_2_np[row_idx] != TokenStatus.NOT_PRESENT)
            present_cols = np.where(present_mask)[0]
            n_present = len(present_cols)
            self.present_cols_per_row.append(n_present)
            
            # Count MARGINAL columns in each mask (among PRESENT columns only)
            marg_A_mask = (mask_1_np[row_idx] == TokenStatus.MARGINAL) & present_mask
            marg_B_mask = (mask_2_np[row_idx] == TokenStatus.MARGINAL) & present_mask
            
            marg_A_cols = np.where(marg_A_mask)[0]
            marg_B_cols = np.where(marg_B_mask)[0]
            
            n_marg_A = len(marg_A_cols)
            n_marg_B = len(marg_B_cols)
            
            # Compute masking ratios (using PRESENT columns only)
            if n_present > 0:
                ratio_A = n_marg_A / n_present
                ratio_B = n_marg_B / n_present
                self.mask_A_ratios.append(ratio_A)
                self.mask_B_ratios.append(ratio_B)
            else:
                # No present columns - skip ratio tracking for this row
                self.mask_A_ratios.append(0.0)
                self.mask_B_ratios.append(0.0)
            
            # Track per-column counts for each mask separately
            for col_idx in range(n_cols):
                # Union metric: marginal in either mask (for sanity check)
                if (mask_1_np[row_idx, col_idx] == TokenStatus.MARGINAL or 
                    mask_2_np[row_idx, col_idx] == TokenStatus.MARGINAL):
                    if col_idx not in self.union_target_coverage_per_column:
                        self.union_target_coverage_per_column[col_idx] = 0
                    self.union_target_coverage_per_column[col_idx] += 1
                
                # Per-mask counts (for bias detection)
                if mask_1_np[row_idx, col_idx] == TokenStatus.MARGINAL:
                    if col_idx not in self.mask_A_count_per_column:
                        self.mask_A_count_per_column[col_idx] = 0
                    self.mask_A_count_per_column[col_idx] += 1
                
                if mask_2_np[row_idx, col_idx] == TokenStatus.MARGINAL:
                    if col_idx not in self.mask_B_count_per_column:
                        self.mask_B_count_per_column[col_idx] = 0
                    self.mask_B_count_per_column[col_idx] += 1
            
            # Check complementary mask invariants (among PRESENT columns only)
            if n_present > 0:
                # Overlap check: margA & margB should be empty
                overlap = np.intersect1d(marg_A_cols, marg_B_cols)
                if len(overlap) > 0:
                    self.overlap_violations += 1
                
                # Coverage check: (margA | margB) should equal all present columns
                union_marg = np.union1d(marg_A_cols, marg_B_cols)
                if len(union_marg) != n_present or not np.array_equal(np.sort(union_marg), np.sort(present_cols)):
                    self.coverage_violations += 1
                
                # Balance: abs(margA - margB)
                balance_diff = abs(n_marg_A - n_marg_B)
                self.balance_diffs.append(balance_diff)
            
            # Track unique mask patterns (combine both masks into a single pattern)
            mask1_cols = tuple(sorted(marg_A_cols))
            mask2_cols = tuple(sorted(marg_B_cols))
            pattern = f"{mask1_cols}|{mask2_cols}"
            self.unique_mask_patterns.add(pattern)
    
    def compute_column_entropy(self, mask_count_per_column, n_cols):
        """
        Compute entropy over column masking distribution for a specific mask.
        
        This measures how uniformly columns are masked (the important metric).
        High entropy = uniform masking across columns
        Low entropy = biased masking (some columns masked much more than others)
        
        Args:
            mask_count_per_column: dict mapping col_idx -> count
            n_cols: total number of columns
        
        Returns normalized entropy value [0, 1] where 1.0 = uniform, 0.0 = completely biased.
        """
        if not mask_count_per_column or self.total_rows_masked == 0:
            return 0.0
        
        # Compute probability of each column being masked (per row)
        probs = []
        for col_idx in range(n_cols):
            count = mask_count_per_column.get(col_idx, 0)
            prob = count / self.total_rows_masked  # Probability this column is masked in a row
            probs.append(prob)
        
        # Compute entropy: H = -sum(p * log(p))
        eps = 1e-10
        entropy = -sum(p * np.log(p + eps) for p in probs if p > 0)
        
        # Normalize by max entropy (uniform distribution)
        max_entropy = np.log(n_cols) if n_cols > 0 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return max(0.0, normalized_entropy)  # Ensure non-negative
    
    def compute_gini_coefficient(self, mask_count_per_column, n_cols):
        """
        Compute Gini coefficient over column mask frequencies for a specific mask.
        
        Gini coefficient measures inequality:
        - 0.0 = perfectly uniform (all columns masked equally)
        - 1.0 = completely concentrated (one column gets all masks)
        
        Args:
            mask_count_per_column: dict mapping col_idx -> count
            n_cols: total number of columns
        
        Returns Gini coefficient [0, 1]
        """
        if not mask_count_per_column or n_cols == 0:
            return 0.0
        
        # Get mask counts for all columns (including zeros)
        counts = [mask_count_per_column.get(col_idx, 0) for col_idx in range(n_cols)]
        total = sum(counts)
        
        if total == 0:
            return 0.0
        
        # Sort counts in ascending order for Gini calculation
        sorted_counts = sorted(counts)
        n = len(sorted_counts)
        
        # Gini coefficient formula: G = (2 * sum(i * y_i)) / (n * sum(y_i)) - (n + 1) / n
        # where y_i are sorted values and i is rank (1-indexed)
        numerator = sum((i + 1) * y for i, y in enumerate(sorted_counts))
        gini = (2 * numerator) / (n * total) - (n + 1) / n
        
        return max(0.0, min(1.0, gini))  # Clamp to [0, 1]
    
    def log_stats(self, epoch_idx, col_names=None):
        """
        Log masking statistics for the current epoch.
        
        Args:
            epoch_idx: Current epoch number
            col_names: Optional list of column names for better logging
        """
        if self.total_batches == 0:
            logger.info(f"🔍 [Epoch {epoch_idx}] Mask bias tracking: No batches recorded")
            return
        
        # Get total number of columns (use col_names length if available, otherwise max index + 1)
        if col_names:
            n_cols = len(col_names)
        else:
            all_col_indices = set(self.union_target_coverage_per_column.keys())
            all_col_indices.update(self.mask_A_count_per_column.keys())
            all_col_indices.update(self.mask_B_count_per_column.keys())
            n_cols = max(all_col_indices) + 1 if all_col_indices else 0
        
        logger.info(f"🔍 [Epoch {epoch_idx}] MASK BIAS ANALYSIS:")
        logger.info(f"   Total batches: {self.total_batches}, Total rows masked: {self.total_rows_masked}")
        
        # Present columns per row
        if self.present_cols_per_row:
            present_mean = np.mean(self.present_cols_per_row)
            logger.info(f"   Present cols per row: mean={present_mean:.1f}")
        
        # Per-mask masking ratios (the key metric)
        if self.mask_A_ratios and self.mask_B_ratios:
            ratio_A_mean = np.mean(self.mask_A_ratios)
            ratio_A_std = np.std(self.mask_A_ratios)
            ratio_A_min = np.min(self.mask_A_ratios)
            ratio_A_max = np.max(self.mask_A_ratios)
            
            ratio_B_mean = np.mean(self.mask_B_ratios)
            ratio_B_std = np.std(self.mask_B_ratios)
            ratio_B_min = np.min(self.mask_B_ratios)
            ratio_B_max = np.max(self.mask_B_ratios)
            
            logger.info(f"   mask_A marginal ratio: mean={ratio_A_mean:.2f} std={ratio_A_std:.3f} min={ratio_A_min:.2f} max={ratio_A_max:.2f}")
            logger.info(f"   mask_B marginal ratio: mean={ratio_B_mean:.2f} std={ratio_B_std:.3f} min={ratio_B_min:.2f} max={ratio_B_max:.2f}")
            
            # Warn if ratios are outside expected 40-60% range
            if ratio_A_mean < 0.35 or ratio_A_mean > 0.65:
                logger.warning(f"   ⚠️  mask_A ratio ({ratio_A_mean:.2f}) outside expected 40-60% range!")
            if ratio_B_mean < 0.35 or ratio_B_mean > 0.65:
                logger.warning(f"   ⚠️  mask_B ratio ({ratio_B_mean:.2f}) outside expected 40-60% range!")
        
        # Complementary mask invariants
        if self.total_rows_masked > 0:
            overlap_pct = (self.overlap_violations / self.total_rows_masked * 100) if self.total_rows_masked > 0 else 0.0
            coverage_pct = (self.coverage_violations / self.total_rows_masked * 100) if self.total_rows_masked > 0 else 0.0
            
            logger.info(f"   Overlap (present(margA & margB)): {self.overlap_violations} rows ({overlap_pct:.1f}%)")
            logger.info(f"   Coverage (present((margA|margB)!=present)): {self.coverage_violations} rows ({coverage_pct:.1f}%)")
            
            if self.overlap_violations > 0:
                logger.warning(f"   ⚠️  {self.overlap_violations} rows have overlapping masks (should be 0 for complementary masks)!")
            if self.coverage_violations > 0:
                logger.warning(f"   ⚠️  {self.coverage_violations} rows have incomplete coverage (should be 0 for complementary masks)!")
            
            # Balance distribution
            if self.balance_diffs:
                balance_mean = np.mean(self.balance_diffs)
                balance_std = np.std(self.balance_diffs)
                balance_max = np.max(self.balance_diffs)
                logger.info(f"   Balance (abs(margA - margB)): mean={balance_mean:.2f} std={balance_std:.2f} max={balance_max}")
        
        # Column entropy per mask (for bias detection)
        if self.total_rows_masked > 0 and n_cols > 0:
            entropy_A = self.compute_column_entropy(self.mask_A_count_per_column, n_cols)
            entropy_B = self.compute_column_entropy(self.mask_B_count_per_column, n_cols)
            
            logger.info(f"   Column entropy: A={entropy_A:.2f} B={entropy_B:.2f} (1.0=uniform, 0.0=biased)")
            
            if entropy_A < 0.3:
                logger.warning(f"   ⚠️  LOW column entropy in mask_A ({entropy_A:.2f}) - masking is biased toward certain columns!")
            if entropy_B < 0.3:
                logger.warning(f"   ⚠️  LOW column entropy in mask_B ({entropy_B:.2f}) - masking is biased toward certain columns!")
            
            # Gini coefficients per mask
            gini_A = self.compute_gini_coefficient(self.mask_A_count_per_column, n_cols)
            gini_B = self.compute_gini_coefficient(self.mask_B_count_per_column, n_cols)
            
            logger.info(f"   Gini coefficient: A={gini_A:.3f} B={gini_B:.3f} (0.0=uniform, 1.0=concentrated)")
            
            if gini_A > 0.7:
                logger.warning(f"   ⚠️  High Gini in mask_A ({gini_A:.3f}) - mask distribution is highly concentrated!")
            if gini_B > 0.7:
                logger.warning(f"   ⚠️  High Gini in mask_B ({gini_B:.3f}) - mask distribution is highly concentrated!")
        
        # Union target coverage (sanity check - should be 100% for complementary masks)
        if self.union_target_coverage_per_column and self.total_rows_masked > 0:
            columns_covered = len(self.union_target_coverage_per_column)
            coverage_pct = (columns_covered / n_cols * 100) if n_cols > 0 else 0.0
            
            # Check if all columns are covered in 100% of rows
            always_covered = sum(1 for count in self.union_target_coverage_per_column.values() 
                                if count == self.total_rows_masked)
            
            logger.info(f"   Union target coverage across views: {always_covered}/{n_cols} columns ({coverage_pct:.1f}%)")
            
            # This is expected to be 100% for complementary masks with all-present data
            # No warnings - it's a sanity check, not a bias metric
        
        # Unique mask patterns
        unique_patterns = len(self.unique_mask_patterns)
        pattern_ratio = unique_patterns / self.total_rows_masked if self.total_rows_masked > 0 else 0.0
        logger.info(f"   Unique mask patterns: {unique_patterns} / {self.total_rows_masked} rows ({pattern_ratio*100:.1f}% unique)")
        
        if pattern_ratio < 0.1:
            logger.warning(f"   ⚠️  Very few unique patterns ({pattern_ratio*100:.1f}%) - masking may be too deterministic!")


# Global tracker instance (reset per epoch)
_mask_bias_tracker = MaskBiasTracker()


def reset_mask_bias_tracker():
    """Reset the global mask bias tracker (call at start of each epoch)."""
    global _mask_bias_tracker
    _mask_bias_tracker.reset()


def get_mask_bias_tracker():
    """Get the global mask bias tracker instance."""
    return _mask_bias_tracker

