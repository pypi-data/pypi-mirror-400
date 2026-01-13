#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Relationship Pre-Analysis: Pre-compute relationship features and select optimal
pairs during the pre-analysis phase before training begins.
"""
import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

from featrix.neural.model_config import ColumnType
from featrix.neural.relationship_complexity import calculate_relationship_complexity

logger = logging.getLogger(__name__)


def analyze_column_relationships(
    df: pd.DataFrame,
    col_types: Dict[str, ColumnType],
    cols_in_order: List[str],
    target_max_pairs: Optional[int] = None,
    target_sequence_length: Optional[int] = None,
) -> Dict[str, any]:
    """
    Analyze column relationships during pre-analysis to select optimal pairs.
    
    This can be run before training to:
    1. Compute correlation/co-occurrence statistics
    2. Select top pairs based on statistical relationships
    3. Cache selected pairs for use during training
    
    Args:
        df: DataFrame with data
        col_types: Dict mapping column names to ColumnType
        cols_in_order: List of column names in order
        target_max_pairs: Target number of pairs to select
        target_sequence_length: Target sequence length (alternative to target_max_pairs)
    
    Returns:
        Dict with:
        - 'selected_pairs': List of (col_i_idx, col_j_idx) tuples
        - 'pair_scores': Dict mapping (col_i, col_j) to score
        - 'complexity': Complexity analysis dict
        - 'recommendations': Dict with recommendations
    """
    n_cols = len(cols_in_order)
    
    # Calculate target_max_pairs if target_sequence_length is set
    if target_sequence_length is not None and target_max_pairs is None:
        # sequence_length = 1 (CLS) + n_cols + ratios + correlations (1) + factors (4) + mi_hints (1)
        target_max_pairs = max(0, target_sequence_length - 1 - n_cols - 1 - 4 - 1)
    
    # Calculate complexity
    complexity = calculate_relationship_complexity(
        n_cols=n_cols,
        max_pairwise_ratios=target_max_pairs,
    )
    
    # Score pairs based on statistical relationships
    pair_scores = {}
    pair_correlations = {}  # Track actual correlations (with sign)
    selected_pairs = []
    
    if target_max_pairs is not None and target_max_pairs > 0:
        # Score all pairs
        for i, col_i in enumerate(cols_in_order):
            for j, col_j in enumerate(cols_in_order[i+1:], start=i+1):
                score, raw_corr = _score_pair(df, col_i, col_j, col_types.get(col_i), col_types.get(col_j))
                pair_scores[(i, j)] = score
                pair_scores[(col_i, col_j)] = score
                if raw_corr is not None:
                    pair_correlations[(col_i, col_j)] = raw_corr
        
        # Select top pairs
        sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1] if isinstance(x[0], tuple) and len(x[0]) == 2 else 0, reverse=True)
        selected_pairs = [pair for pair, score in sorted_pairs[:target_max_pairs] if isinstance(pair, tuple) and len(pair) == 2 and isinstance(pair[0], int)]
        
        # Count inverse relationships in selected pairs
        inverse_count = 0
        strong_inverse = []  # Track strong inverse relationships (corr < -0.5)
        for pair in selected_pairs:
            if isinstance(pair, tuple) and len(pair) == 2:
                i, j = pair
                col_i = cols_in_order[i]
                col_j = cols_in_order[j]
                corr = pair_correlations.get((col_i, col_j))
                if corr is not None and corr < 0:
                    inverse_count += 1
                    if corr < -0.5:
                        strong_inverse.append((col_i, col_j, corr))
        
        logger.info(
            f"🔍 Pre-analysis: Selected {len(selected_pairs)} top pairs "
            f"from {n_cols * (n_cols - 1) // 2} total combinations"
        )
        
        # Report inverse relationships
        if inverse_count > 0:
            logger.info(
                f"   ↕️  Inverse relationships detected: {inverse_count}/{len(selected_pairs)} pairs "
                f"({100.0 * inverse_count / len(selected_pairs):.1f}%)"
            )
            if strong_inverse:
                logger.info(f"   🔴 Strong inverse correlations (< -0.5):")
                for col_i, col_j, corr in strong_inverse[:5]:  # Show top 5
                    logger.info(f"      • {col_i} ↔ {col_j}: r = {corr:.3f}")
                if len(strong_inverse) > 5:
                    logger.info(f"      ... and {len(strong_inverse) - 5} more")
    
    # Generate recommendations
    recommendations = {
        'max_pairwise_ratios': target_max_pairs,
        'estimated_sequence_length': complexity['sequence_length'],
        'estimated_memory_mb': (complexity['sequence_length'] * 256 * 32 * 4) / (1024 ** 2),  # Rough estimate
        'complexity_level': _classify_complexity(n_cols, complexity['total']),
    }
    
    return {
        'selected_pairs': selected_pairs,
        'pair_scores': pair_scores,
        'pair_correlations': pair_correlations,  # Include correlations with sign
        'inverse_count': inverse_count if target_max_pairs else 0,
        'strong_inverse': strong_inverse if target_max_pairs else [],
        'complexity': complexity,
        'recommendations': recommendations,
    }


def _score_pair(
    df: pd.DataFrame,
    col_i: str,
    col_j: str,
    type_i: Optional[ColumnType],
    type_j: Optional[ColumnType],
) -> Tuple[float, Optional[float]]:
    """
    Score a pair of columns based on their statistical relationship.
    
    Returns:
        Tuple of (score, raw_correlation):
        - score: higher = more important relationship (always positive)
        - raw_correlation: actual correlation with sign (None if not numeric pair)
    """
    if col_i not in df.columns or col_j not in df.columns:
        return 0.0, None
    
    score = 0.0
    raw_corr = None
    
    # Both numeric (SCALAR, VECTOR, TIMESTAMP)
    if type_i in [ColumnType.SCALAR, ColumnType.VECTOR, ColumnType.TIMESTAMP] and \
       type_j in [ColumnType.SCALAR, ColumnType.VECTOR, ColumnType.TIMESTAMP]:
        # Use correlation
        try:
            numeric_i = pd.to_numeric(df[col_i], errors='coerce')
            numeric_j = pd.to_numeric(df[col_j], errors='coerce')
            corr = numeric_i.corr(numeric_j)
            if pd.notna(corr):
                raw_corr = corr  # Keep sign for reporting
                score = abs(corr)  # Use absolute correlation for ranking
        except:
            pass
    
    # Both categorical (SET, LIST_OF_A_SET)
    elif type_i in [ColumnType.SET, ColumnType.LIST_OF_A_SET] and \
         type_j in [ColumnType.SET, ColumnType.LIST_OF_A_SET]:
        # Use co-occurrence / mutual information approximation
        try:
            # Simple co-occurrence: how often do values co-occur?
            # This is a simplified MI approximation
            unique_i = df[col_i].nunique()
            unique_j = df[col_j].nunique()
            if unique_i > 0 and unique_j > 0:
                # Higher diversity → potentially more informative relationship
                score = min(unique_i, unique_j) / max(unique_i, unique_j)
        except:
            pass
    
    # Mixed types: use simple co-occurrence
    else:
        # For mixed types, use a simple co-occurrence score
        try:
            # Check if non-null values co-occur
            non_null_both = df[[col_i, col_j]].notna().all(axis=1).sum()
            total = len(df)
            if total > 0:
                score = non_null_both / total  # Co-occurrence rate
        except:
            pass
    
    return score, raw_corr


def _classify_complexity(n_cols: int, n_relationship_tokens: int) -> str:
    """Classify complexity level."""
    ratio = n_relationship_tokens / n_cols if n_cols > 0 else 0
    
    if ratio < 2:
        return "LOW"
    elif ratio < 10:
        return "MEDIUM"
    elif ratio < 50:
        return "HIGH"
    else:
        return "VERY_HIGH"


def print_preanalysis_summary(analysis_result: Dict[str, any]):
    """Print formatted pre-analysis summary."""
    logger.info("=" * 80)
    logger.info("RELATIONSHIP PRE-ANALYSIS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Selected pairs: {len(analysis_result['selected_pairs'])}")
    logger.info(f"")
    logger.info(f"Recommendations:")
    rec = analysis_result['recommendations']
    logger.info(f"  • Max pairwise ratios: {rec['max_pairwise_ratios']}")
    logger.info(f"  • Estimated sequence length: {rec['estimated_sequence_length']}")
    logger.info(f"  • Estimated memory: {rec['estimated_memory_mb']:.2f} MB")
    logger.info(f"  • Complexity level: {rec['complexity_level']}")
    logger.info("=" * 80)

