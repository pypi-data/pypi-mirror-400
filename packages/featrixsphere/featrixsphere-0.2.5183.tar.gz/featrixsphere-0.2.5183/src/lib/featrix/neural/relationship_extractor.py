#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
RelationshipFeatureExtractor: Pre-computes explicit relationship features
(ratios, correlations, factors) from column encodings and MLP-izes them
for use as relationship tokens in the joint encoder.
"""
import logging
import math
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.simple_mlp import SimpleMLP

logger = logging.getLogger(__name__)


class RelationshipFeatureExtractor(nn.Module):
    """
    Extracts explicit relationship features from column encodings:
    - Pairwise ratios (for numeric relationships)
    - Batch-level correlations/covariances
    - Learned relationship factors
    - Upstream hints (MI-weighted relationships)
    
    All features are MLP-ized to transformer dimension for use as relationship tokens.
    """
    
    def __init__(
        self,
        d_model: int,
        col_names_in_order: List[str],
        enable_ratios: bool = True,
        enable_correlations: bool = True,
        enable_factors: bool = True,
        enable_mi_hints: bool = True,
        n_factors: int = 4,  # Number of learned relationship factors
        max_pairwise_ratios: Optional[int] = None,  # Limit number of ratio pairs (None = auto-calculate)
        use_mi_filtering: bool = True,  # Use MI to select top pairs (if max_pairwise_ratios is set)
        target_sequence_length: Optional[int] = None,  # Target total sequence length (auto-calculates max_pairwise_ratios)
        mlp_config: Optional[SimpleMLPConfig] = None,
    ):
        super().__init__()
        
        self.d_model = d_model
        self.col_names_in_order = col_names_in_order
        self.n_cols = len(col_names_in_order)
        self.enable_ratios = enable_ratios
        self.enable_correlations = enable_correlations
        self.enable_factors = enable_factors
        self.enable_mi_hints = enable_mi_hints
        self.n_factors = n_factors
        self.use_mi_filtering = use_mi_filtering
        self.target_sequence_length = target_sequence_length
        
        # Auto-calculate max_pairwise_ratios if target_sequence_length is set
        if target_sequence_length is not None and max_pairwise_ratios is None:
            # sequence_length = 1 (CLS) + n_cols + ratios + correlations (1) + factors (n_factors) + mi_hints (1)
            # So: ratios = target_sequence_length - 1 - n_cols - 1 - n_factors - 1
            max_pairwise_ratios = max(0, target_sequence_length - 1 - self.n_cols - 1 - self.n_factors - 1)
            logger.info(
                f"🔗 RelationshipFeatureExtractor: Auto-calculated max_pairwise_ratios={max_pairwise_ratios} "
                f"for target_sequence_length={target_sequence_length} with {self.n_cols} columns"
            )
        
        # Auto-calculate reasonable default if not set and we have many columns
        if max_pairwise_ratios is None:
            pairwise_combinations = self.n_cols * (self.n_cols - 1) // 2
            # Default: limit to reasonable number based on column count
            if self.n_cols <= 25:
                # Small datasets: use all pairs
                max_pairwise_ratios = pairwise_combinations
            elif self.n_cols <= 50:
                # Medium datasets: limit to ~500 pairs
                max_pairwise_ratios = min(500, pairwise_combinations)
            elif self.n_cols <= 100:
                # Large datasets: limit to ~1000 pairs
                max_pairwise_ratios = min(1000, pairwise_combinations)
            else:
                # Very large datasets: limit to ~2000 pairs
                max_pairwise_ratios = min(2000, pairwise_combinations)
            
            logger.info(
                f"🔗 RelationshipFeatureExtractor: Auto-selected max_pairwise_ratios={max_pairwise_ratios} "
                f"for {self.n_cols} columns (total combinations: {pairwise_combinations})"
            )
        
        self.max_pairwise_ratios = max_pairwise_ratios
        
        # Store selected pairs (will be populated when MI estimates are available)
        self.selected_pairs: Optional[List[Tuple[int, int]]] = None
        
        # Default MLP config for relationship features
        if mlp_config is None:
            mlp_config = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=d_model,
                n_hidden_layers=1,
                dropout=0.1,
                normalize=True,
                residual=True,
                use_batch_norm=True,
            )
        
        # MLPs for different relationship types
        if enable_ratios:
            # Each ratio is a single vector → MLP projects to d_model
            self.ratio_mlp = SimpleMLP(mlp_config)
        
        if enable_correlations:
            # Correlation matrix flattened → MLP projects to d_model
            # Input: flattened correlation matrix (n_cols * n_cols)
            correlation_input_dim = self.n_cols * self.n_cols
            correlation_mlp_config = SimpleMLPConfig(
                d_in=correlation_input_dim,
                d_out=d_model,
                d_hidden=d_model * 2,
                n_hidden_layers=1,
                dropout=0.1,
                normalize=True,
                residual=True,
                use_batch_norm=True,
            )
            self.correlation_mlp = SimpleMLP(correlation_mlp_config)
        
        if enable_factors:
            # Learned factors: project column encodings to factor space
            # Each factor is a weighted combination of columns
            self.factor_weights = nn.Parameter(
                torch.randn(n_factors, self.n_cols) / math.sqrt(self.n_cols)
            )
            # MLP to project factor embeddings to d_model
            factor_mlp_config = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=d_model,
                n_hidden_layers=1,
                dropout=0.1,
                normalize=True,
                residual=True,
                use_batch_norm=True,
            )
            self.factor_mlp = SimpleMLP(factor_mlp_config)
        
        if enable_mi_hints:
            # MI-weighted summary → MLP projects to d_model
            mi_mlp_config = SimpleMLPConfig(
                d_in=d_model,
                d_out=d_model,
                d_hidden=d_model,
                n_hidden_layers=1,
                dropout=0.1,
                normalize=True,
                residual=True,
                use_batch_norm=True,
            )
            self.mi_hint_mlp = SimpleMLP(mi_mlp_config)
            # Store MI estimates (updated during training)
            self.col_mi_estimates: Dict[str, Optional[float]] = {
                col_name: None for col_name in col_names_in_order
            }
            self.joint_mi_estimate: Optional[float] = None
    
    def update_mi_estimates(
        self,
        col_mi_estimates: Dict[str, Optional[float]],
        joint_mi_estimate: Optional[float] = None,
    ):
        """Update mutual information estimates from encoder and select top pairs for ratios."""
        self.col_mi_estimates = col_mi_estimates.copy()
        if joint_mi_estimate is not None:
            self.joint_mi_estimate = joint_mi_estimate
        
        # Select top pairs based on MI if filtering is enabled
        if self.enable_ratios and self.use_mi_filtering and self.max_pairwise_ratios is not None:
            self._select_top_pairs_by_mi()
    
    def _select_top_pairs_by_mi(self):
        """Select top pairs for ratio computation based on MI estimates."""
        pairwise_combinations = self.n_cols * (self.n_cols - 1) // 2
        
        # If we don't need filtering, use all pairs
        if self.max_pairwise_ratios is None or self.max_pairwise_ratios >= pairwise_combinations:
            self.selected_pairs = None  # None = use all pairs
            return
        
        # Score each pair by MI
        pair_scores = []
        for i in range(self.n_cols):
            for j in range(i + 1, self.n_cols):
                col_i_name = self.col_names_in_order[i]
                col_j_name = self.col_names_in_order[j]
                
                mi_i = self.col_mi_estimates.get(col_i_name)
                mi_j = self.col_mi_estimates.get(col_j_name)
                
                # Score: product of MIs (higher = more important relationship)
                # If MI is None, use 0 (lowest priority)
                score = 0.0
                if mi_i is not None and mi_j is not None:
                    score = mi_i * mi_j
                elif mi_i is not None:
                    score = mi_i
                elif mi_j is not None:
                    score = mi_j
                
                pair_scores.append((score, i, j))
        
        # Sort by score (descending) and take top max_pairwise_ratios
        pair_scores.sort(reverse=True, key=lambda x: x[0])
        self.selected_pairs = [(i, j) for _, i, j in pair_scores[:self.max_pairwise_ratios]]
        
        logger.info(
            f"🔗 RelationshipFeatureExtractor: Selected {len(self.selected_pairs)} top pairs "
            f"based on MI (from {pairwise_combinations} total combinations)"
        )
    
    def forward(
        self,
        column_encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor] = None,  # (batch_size, n_cols) - TokenStatus mask
    ) -> List[torch.Tensor]:
        """
        Extract relationship features from column encodings.
        
        Returns:
            List of relationship token tensors, each (batch_size, d_model)
        """
        batch_size, n_cols, d_model = column_encodings.shape
        relationship_tokens = []
        
        # Apply mask if provided (zero out masked columns)
        if mask is not None:
            # mask: (batch_size, n_cols) where 1 = present, 0 = masked
            # Expand to (batch_size, n_cols, 1) for broadcasting
            mask_expanded = mask.unsqueeze(-1)  # (batch_size, n_cols, 1)
            masked_encodings = column_encodings * mask_expanded
        else:
            masked_encodings = column_encodings
        
        # 1. Pairwise Ratios (for numeric relationships)
        if self.enable_ratios:
            ratio_tokens = self._compute_pairwise_ratios(masked_encodings, mask)
            relationship_tokens.extend(ratio_tokens)
        
        # 2. Batch-level Correlations/Covariances
        if self.enable_correlations:
            correlation_token = self._compute_correlations(masked_encodings, mask)
            if correlation_token is not None:
                relationship_tokens.append(correlation_token)
        
        # 3. Learned Relationship Factors
        if self.enable_factors:
            factor_tokens = self._compute_factors(masked_encodings, mask)
            relationship_tokens.extend(factor_tokens)
        
        # 4. Upstream Hints (MI-weighted relationships)
        if self.enable_mi_hints:
            mi_hint_token = self._compute_mi_hints(masked_encodings, mask)
            if mi_hint_token is not None:
                relationship_tokens.append(mi_hint_token)
        
        return relationship_tokens
    
    def _compute_pairwise_ratios(
        self,
        encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor],  # (batch_size, n_cols)
    ) -> List[torch.Tensor]:
        """
        Compute pairwise ratios between column encodings.
        Uses element-wise division with epsilon to avoid division by zero.
        
        Returns:
            List of ratio vectors, each (batch_size, d_model)
        """
        batch_size, n_cols, d_model = encodings.shape
        ratio_tokens = []
        
        # Get pairs to compute (either selected pairs or all pairs)
        if self.selected_pairs is not None:
            # Use MI-selected pairs
            pairs = self.selected_pairs
        else:
            # Generate all pairs (i, j) where i < j
            pairs = []
            for i in range(n_cols):
                for j in range(i + 1, n_cols):
                    pairs.append((i, j))
            
            # Limit number of pairs if specified (fallback if MI filtering not available)
            if self.max_pairwise_ratios is not None and len(pairs) > self.max_pairwise_ratios:
                # Select first max_pairwise_ratios pairs (simple fallback)
                pairs = pairs[:self.max_pairwise_ratios]
        
        # Compute ratios for each pair
        eps = 1e-8
        for i, j in pairs:
            # Element-wise ratio: encodings[:, i, :] / (encodings[:, j, :] + eps)
            col_i = encodings[:, i, :]  # (batch_size, d_model)
            col_j = encodings[:, j, :]  # (batch_size, d_model)
            
            # Handle masking: if either column is masked, set ratio to zero
            if mask is not None:
                mask_i = mask[:, i].unsqueeze(-1)  # (batch_size, 1)
                mask_j = mask[:, j].unsqueeze(-1)  # (batch_size, 1)
                both_present = (mask_i * mask_j)  # (batch_size, 1)
            else:
                both_present = torch.ones(batch_size, 1, device=encodings.device)
            
            # Compute ratio with epsilon
            ratio = col_i / (col_j + eps)  # (batch_size, d_model)
            
            # Apply mask: zero out ratios where either column is masked
            ratio = ratio * both_present
            
            # MLP-ize the ratio
            ratio_token = self.ratio_mlp(ratio)  # (batch_size, d_model)
            ratio_tokens.append(ratio_token)
        
        return ratio_tokens
    
    def _compute_correlations(
        self,
        encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor],  # (batch_size, n_cols)
    ) -> Optional[torch.Tensor]:
        """
        Compute batch-level correlation matrix between columns.
        Uses cosine similarity between column encodings.
        
        Returns:
            Correlation token (batch_size, d_model) or None if insufficient columns
        """
        batch_size, n_cols, d_model = encodings.shape
        
        if n_cols < 2:
            return None
        
        # Normalize encodings for cosine similarity
        encodings_norm = F.normalize(encodings, p=2, dim=-1)  # (batch_size, n_cols, d_model)
        
        # Compute pairwise cosine similarities: (batch_size, n_cols, n_cols)
        # Using einsum: 'bnd,bmd->bnm'
        correlation_matrix = torch.einsum('bnd,bmd->bnm', encodings_norm, encodings_norm)
        # correlation_matrix[i, j] = cosine_similarity(col_i, col_j)
        
        # Store raw correlation matrix for diagnostics (before masking)
        self._last_correlation_matrix = correlation_matrix.detach()
        
        # Apply mask: zero out correlations involving masked columns
        if mask is not None:
            mask_expanded_i = mask.unsqueeze(1)  # (batch_size, 1, n_cols)
            mask_expanded_j = mask.unsqueeze(2)  # (batch_size, n_cols, 1)
            both_present = mask_expanded_i * mask_expanded_j  # (batch_size, n_cols, n_cols)
            correlation_matrix = correlation_matrix * both_present
        
        # Flatten correlation matrix: (batch_size, n_cols * n_cols)
        correlation_flat = correlation_matrix.flatten(start_dim=1)
        
        # MLP-ize the flattened correlation matrix
        correlation_token = self.correlation_mlp(correlation_flat)  # (batch_size, d_model)
        
        return correlation_token
    
    def log_correlation_analysis(self) -> Dict[str, any]:
        """
        Analyze and log the distribution of correlations in the last batch.
        Useful for verifying that inverse relationships are being detected.
        
        Returns:
            Dict with correlation statistics
        """
        if not hasattr(self, '_last_correlation_matrix') or self._last_correlation_matrix is None:
            logger.warning("No correlation matrix available. Run forward() first.")
            return {}
        
        corr_matrix = self._last_correlation_matrix  # (batch_size, n_cols, n_cols)
        batch_size, n_cols, _ = corr_matrix.shape
        
        # Get off-diagonal elements (exclude self-correlations)
        mask = ~torch.eye(n_cols, dtype=torch.bool, device=corr_matrix.device)
        off_diag = corr_matrix[:, mask].flatten()  # All off-diagonal correlations
        
        # Statistics
        n_negative = (off_diag < 0).sum().item()
        n_positive = (off_diag > 0).sum().item()
        n_total = off_diag.numel()
        
        # Strong relationships
        n_strong_negative = (off_diag < -0.5).sum().item()
        n_strong_positive = (off_diag > 0.5).sum().item()
        
        min_corr = off_diag.min().item()
        max_corr = off_diag.max().item()
        mean_corr = off_diag.mean().item()
        
        # Log results
        logger.info("=" * 80)
        logger.info("CORRELATION ANALYSIS (from column encodings)")
        logger.info("-" * 80)
        logger.info(f"Batch size: {batch_size}, Columns: {n_cols}, Pairs: {n_total}")
        logger.info(f"Range: [{min_corr:.3f}, {max_corr:.3f}], Mean: {mean_corr:.3f}")
        logger.info(f"")
        logger.info(f"Positive correlations: {n_positive:>6} ({100.0 * n_positive / n_total:>5.1f}%)")
        logger.info(f"Negative correlations: {n_negative:>6} ({100.0 * n_negative / n_total:>5.1f}%) ↕️")
        logger.info(f"")
        logger.info(f"Strong positive (>0.5): {n_strong_positive:>6} ({100.0 * n_strong_positive / n_total:>5.1f}%)")
        logger.info(f"Strong negative (<-0.5): {n_strong_negative:>6} ({100.0 * n_strong_negative / n_total:>5.1f}%) 🔴")
        
        if n_strong_negative > 0:
            logger.info(f"")
            logger.info(f"✅ INVERSE RELATIONSHIPS DETECTED AND PRESERVED")
            logger.info(f"   The model is seeing {n_strong_negative} strong inverse correlations")
            logger.info(f"   These are being encoded in the correlation token for attention")
        else:
            logger.info(f"")
            logger.info(f"⚠️  No strong inverse relationships detected in this batch")
            logger.info(f"   (Either none exist in data, or encodings aren't capturing them)")
        
        logger.info("=" * 80)
        
        return {
            'n_total': n_total,
            'n_positive': n_positive,
            'n_negative': n_negative,
            'n_strong_positive': n_strong_positive,
            'n_strong_negative': n_strong_negative,
            'min_correlation': min_corr,
            'max_correlation': max_corr,
            'mean_correlation': mean_corr,
            'inverse_percentage': 100.0 * n_negative / n_total if n_total > 0 else 0,
        }
    
    def _compute_factors(
        self,
        encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor],  # (batch_size, n_cols)
    ) -> List[torch.Tensor]:
        """
        Compute learned relationship factors.
        Each factor is a weighted combination of column encodings.
        
        Returns:
            List of factor tokens, each (batch_size, d_model)
        """
        batch_size, n_cols, d_model = encodings.shape
        
        # Apply learned factor weights: (n_factors, n_cols) @ (batch_size, n_cols, d_model)
        # Result: (batch_size, n_factors, d_model)
        factor_embeddings = torch.einsum('fn,bnd->bfd', self.factor_weights, encodings)
        
        # Apply mask: zero out factors involving masked columns
        if mask is not None:
            # Weight factors by mask: (batch_size, n_factors)
            mask_sum = mask.sum(dim=1, keepdim=True)  # (batch_size, 1)
            factor_mask = (mask_sum > 0).float().unsqueeze(-1)  # (batch_size, 1, 1)
            factor_embeddings = factor_embeddings * factor_mask
        
        # MLP-ize each factor
        factor_tokens = []
        for factor_idx in range(self.n_factors):
            factor_emb = factor_embeddings[:, factor_idx, :]  # (batch_size, d_model)
            factor_token = self.factor_mlp(factor_emb)  # (batch_size, d_model)
            factor_tokens.append(factor_token)
        
        return factor_tokens
    
    def _compute_mi_hints(
        self,
        encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor],  # (batch_size, n_cols)
    ) -> Optional[torch.Tensor]:
        """
        Compute MI-weighted summary of column encodings.
        Uses mutual information estimates to weight columns.
        
        Returns:
            MI hint token (batch_size, d_model) or None if no MI estimates available
        """
        batch_size, n_cols, d_model = encodings.shape
        
        # Get MI weights for each column
        mi_weights = torch.zeros(n_cols, device=encodings.device)
        has_mi = False
        
        for i, col_name in enumerate(self.col_names_in_order):
            mi_value = self.col_mi_estimates.get(col_name)
            if mi_value is not None and mi_value > 0:
                mi_weights[i] = mi_value
                has_mi = True
        
        if not has_mi:
            # No MI estimates available yet → return None
            return None
        
        # Normalize MI weights
        mi_weights = mi_weights / (mi_weights.sum() + 1e-8)
        
        # Apply mask: zero out weights for masked columns
        if mask is not None:
            mi_weights = mi_weights.unsqueeze(0) * mask  # (batch_size, n_cols)
            # Renormalize per batch
            mi_weights = mi_weights / (mi_weights.sum(dim=1, keepdim=True) + 1e-8)
        
        # Weighted sum of column encodings: (batch_size, n_cols) @ (batch_size, n_cols, d_model)
        # Using einsum: 'bn,bnd->bd'
        if mask is not None:
            weighted_sum = torch.einsum('bn,bnd->bd', mi_weights, encodings)
        else:
            mi_weights_expanded = mi_weights.unsqueeze(0).expand(batch_size, -1)  # (batch_size, n_cols)
            weighted_sum = torch.einsum('bn,bnd->bd', mi_weights_expanded, encodings)
        
        # MLP-ize the weighted sum
        mi_hint_token = self.mi_hint_mlp(weighted_sum)  # (batch_size, d_model)
        
        return mi_hint_token

