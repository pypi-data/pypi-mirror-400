#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Relationship Complexity Analysis: Calculate and analyze the number of
relationship features that would be generated for different column counts.
"""
import logging
from typing import Dict, List, Optional, Tuple

import torch

from featrix.neural.model_config import ColumnType

logger = logging.getLogger(__name__)


def calculate_relationship_complexity(
    n_cols: int,
    enable_ratios: bool = True,
    enable_correlations: bool = True,
    enable_factors: int = 4,
    enable_mi_hints: bool = True,
    max_pairwise_ratios: Optional[int] = None,
    col_types: Optional[Dict[str, ColumnType]] = None,
) -> Dict[str, int]:
    """
    Calculate the total number of relationship tokens that would be generated.
    
    Args:
        n_cols: Number of columns
        enable_ratios: Whether to enable pairwise ratios
        enable_correlations: Whether to enable correlation matrix
        enable_factors: Number of learned factors
        enable_mi_hints: Whether to enable MI-weighted hints
        max_pairwise_ratios: Maximum number of ratio pairs (None = all pairs)
        col_types: Optional dict mapping column names to types (for type-aware counting)
    
    Returns:
        Dict with breakdown of relationship token counts:
        - 'total': Total number of relationship tokens
        - 'ratios': Number of ratio tokens
        - 'correlations': Number of correlation tokens (0 or 1)
        - 'factors': Number of factor tokens
        - 'mi_hints': Number of MI hint tokens (0 or 1)
        - 'pairwise_combinations': Number of unique column pairs
        - 'sequence_length': Total sequence length (1 CLS + n_cols + relationship_tokens)
    """
    # Pairwise combinations: C(n, 2) = n * (n-1) / 2
    pairwise_combinations = n_cols * (n_cols - 1) // 2
    
    # Ratio tokens: one per pair (or limited by max_pairwise_ratios)
    if enable_ratios:
        if max_pairwise_ratios is not None:
            ratio_count = min(pairwise_combinations, max_pairwise_ratios)
        else:
            ratio_count = pairwise_combinations
    else:
        ratio_count = 0
    
    # Correlation tokens: 1 token (flattened correlation matrix)
    correlation_count = 1 if enable_correlations else 0
    
    # Factor tokens: n_factors tokens
    factor_count = enable_factors if isinstance(enable_factors, int) else (4 if enable_factors else 0)
    
    # MI hint tokens: 1 token
    mi_hint_count = 1 if enable_mi_hints else 0
    
    total_relationship_tokens = ratio_count + correlation_count + factor_count + mi_hint_count
    
    # Total sequence length: CLS (1) + columns (n_cols) + relationship tokens
    sequence_length = 1 + n_cols + total_relationship_tokens
    
    return {
        'total': total_relationship_tokens,
        'ratios': ratio_count,
        'correlations': correlation_count,
        'factors': factor_count,
        'mi_hints': mi_hint_count,
        'pairwise_combinations': pairwise_combinations,
        'sequence_length': sequence_length,
        'relationship_token_ratio': total_relationship_tokens / n_cols if n_cols > 0 else 0,
    }


def analyze_complexity_by_column_count(
    max_cols: int = 200,
    step: int = 10,
    enable_ratios: bool = True,
    enable_correlations: bool = True,
    enable_factors: int = 4,
    enable_mi_hints: bool = True,
    max_pairwise_ratios: Optional[int] = None,
) -> List[Dict[str, int]]:
    """
    Analyze relationship complexity for different column counts.
    
    Returns:
        List of complexity dicts, one per column count
    """
    results = []
    for n_cols in range(step, max_cols + 1, step):
        complexity = calculate_relationship_complexity(
            n_cols=n_cols,
            enable_ratios=enable_ratios,
            enable_correlations=enable_correlations,
            enable_factors=enable_factors,
            enable_mi_hints=enable_mi_hints,
            max_pairwise_ratios=max_pairwise_ratios,
        )
        complexity['n_cols'] = n_cols
        results.append(complexity)
    
    return results


def print_complexity_analysis(
    n_cols: int,
    enable_ratios: bool = True,
    enable_correlations: bool = True,
    enable_factors: int = 4,
    enable_mi_hints: bool = True,
    max_pairwise_ratios: Optional[int] = None,
):
    """Print a formatted complexity analysis."""
    complexity = calculate_relationship_complexity(
        n_cols=n_cols,
        enable_ratios=enable_ratios,
        enable_correlations=enable_correlations,
        enable_factors=enable_factors,
        enable_mi_hints=enable_mi_hints,
        max_pairwise_ratios=max_pairwise_ratios,
    )
    
    logger.info("=" * 80)
    logger.info(f"RELATIONSHIP COMPLEXITY ANALYSIS: {n_cols} columns")
    logger.info("=" * 80)
    logger.info(f"Pairwise combinations: {complexity['pairwise_combinations']:,}")
    logger.info(f"")
    logger.info(f"Relationship Tokens:")
    logger.info(f"  • Ratios:           {complexity['ratios']:,}")
    logger.info(f"  • Correlations:     {complexity['correlations']:,}")
    logger.info(f"  • Factors:          {complexity['factors']:,}")
    logger.info(f"  • MI Hints:         {complexity['mi_hints']:,}")
    logger.info(f"  ─────────────────────────────")
    logger.info(f"  • TOTAL:            {complexity['total']:,}")
    logger.info(f"")
    logger.info(f"Sequence Length:")
    logger.info(f"  • CLS token:        1")
    logger.info(f"  • Column tokens:    {n_cols:,}")
    logger.info(f"  • Relationship tokens: {complexity['total']:,}")
    logger.info(f"  ─────────────────────────────")
    logger.info(f"  • TOTAL SEQUENCE:   {complexity['sequence_length']:,}")
    logger.info(f"")
    logger.info(f"Relationship/Column Ratio: {complexity['relationship_token_ratio']:.2f}x")
    logger.info("=" * 80)
    
    # Memory estimate (rough)
    # Assuming d_model=256, float32 (4 bytes per element)
    d_model = 256
    bytes_per_token = d_model * 4  # float32
    memory_mb = (complexity['sequence_length'] * bytes_per_token) / (1024 ** 2)
    logger.info(f"Estimated Memory (d_model={d_model}, float32):")
    logger.info(f"  • Per batch element: {memory_mb:.2f} MB")
    logger.info(f"  • Batch size 32:     {memory_mb * 32:.2f} MB")
    logger.info(f"  • Batch size 64:      {memory_mb * 64:.2f} MB")
    logger.info("=" * 80)


def recommend_max_pairwise_ratios(
    n_cols: int,
    target_ratio_tokens: Optional[int] = None,
    target_sequence_length: Optional[int] = None,
) -> Tuple[int, Dict[str, int]]:
    """
    Recommend max_pairwise_ratios based on targets.
    
    Args:
        n_cols: Number of columns
        target_ratio_tokens: Target number of ratio tokens (None = no limit)
        target_sequence_length: Target total sequence length (None = no limit)
    
    Returns:
        Tuple of (recommended_max_pairwise_ratios, complexity_dict)
    """
    pairwise_combinations = n_cols * (n_cols - 1) // 2
    
    # Default: use all pairs
    recommended = pairwise_combinations
    
    # If target_ratio_tokens is set, limit to that
    if target_ratio_tokens is not None:
        recommended = min(recommended, target_ratio_tokens)
    
    # If target_sequence_length is set, calculate how many ratio tokens fit
    if target_sequence_length is not None:
        # sequence_length = 1 (CLS) + n_cols + ratios + correlations (1) + factors (4) + mi_hints (1)
        # So: ratios = target_sequence_length - 1 - n_cols - 1 - 4 - 1
        max_ratios_for_target = max(0, target_sequence_length - 1 - n_cols - 1 - 4 - 1)
        recommended = min(recommended, max_ratios_for_target)
    
    # Calculate complexity with recommended value
    complexity = calculate_relationship_complexity(
        n_cols=n_cols,
        enable_ratios=True,
        enable_correlations=True,
        enable_factors=4,
        enable_mi_hints=True,
        max_pairwise_ratios=recommended,
    )
    
    return recommended, complexity


if __name__ == "__main__":
    # Configure logging for script output
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # Example: Analyze different column counts
    import sys
    
    if len(sys.argv) > 1:
        n_cols = int(sys.argv[1])
        print_complexity_analysis(n_cols)
    else:
        # Show analysis for common column counts
        print("\n" + "=" * 80)
        print("COMPLEXITY ANALYSIS: Different Column Counts")
        print("=" * 80 + "\n")
        
        for n_cols in [10, 25, 50, 100, 200]:
            print_complexity_analysis(n_cols)
            print()
        
        # Show with different max_pairwise_ratios limits
        print("\n" + "=" * 80)
        print("COMPARISON: 100 columns with different ratio limits")
        print("=" * 80 + "\n")
        
        for max_ratios in [None, 100, 500, 1000, 2000, 4950]:
            limit_str = "unlimited" if max_ratios is None else str(max_ratios)
            print(f"\nMax pairwise ratios: {limit_str}")
            complexity = calculate_relationship_complexity(
                n_cols=100,
                max_pairwise_ratios=max_ratios,
            )
            print(f"  Total relationship tokens: {complexity['total']:,}")
            print(f"  Total sequence length: {complexity['sequence_length']:,}")
            print(f"  Ratio tokens: {complexity['ratios']:,}")
            print(f"  Relationship/Column ratio: {complexity['relationship_token_ratio']:.2f}x")
        
        # Show recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS: 100 columns")
        print("=" * 80 + "\n")
        
        for target_seq_len in [256, 512, 1024]:
            recommended, complexity = recommend_max_pairwise_ratios(
                n_cols=100,
                target_sequence_length=target_seq_len,
            )
            print(f"Target sequence length: {target_seq_len}")
            print(f"  Recommended max_pairwise_ratios: {recommended:,}")
            print(f"  Actual sequence length: {complexity['sequence_length']:,}")
            print(f"  Ratio tokens: {complexity['ratios']:,}")
            print()

