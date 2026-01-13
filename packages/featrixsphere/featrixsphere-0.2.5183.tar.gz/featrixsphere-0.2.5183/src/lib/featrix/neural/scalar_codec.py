#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import base64
import hashlib
import io
import logging
import math
import os 

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from featrix.neural.featrix_token import create_token_batch
from featrix.neural.featrix_token import Token
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.model_config import ColumnType
from featrix.neural.model_config import ScalarEncoderConfig
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.gpu_utils import is_gpu_available, empty_gpu_cache

logger = logging.getLogger(__name__)

# print("DEVICE ______________________:", device)

#
# class SLERP(nn.Module):
#     # perform spherical linear interpolation.
#
#     def __init__(self, embed_dim):
#         super().__init__()
#
#         self.low = nn.Parameter(torch.randn(embed_dim))
#         self.high = nn.Parameter(torch.randn(embed_dim))
#
#     def forward(self, input):
#         t = input
#
#         low_norm = nn.functional.normalize(self.low, dim=-1)
#         high_norm = nn.functional.normalize(self.high, dim=-1)
#
#         dot = torch.dot(low_norm, high_norm)
#
#         omega = torch.acos(dot)
#         so = torch.sin(omega)
#
#         a = (torch.sin((1.0 - t) * omega) / so).unsqueeze(1)
#         b = (torch.sin(t * omega) / so).unsqueeze(1)
#
#         res = a * low_norm + b * high_norm
#
#         return res


class AdaptiveScalarEncoder(nn.Module):
    """
    Learnable scalar encoder with mixture of 20 transform strategies.
    
    The model automatically learns which transformation works best for each column.
    Every 5 epochs (starting from epoch 1), the worst-performing strategy is pruned.
    Pruning stops when 3 strategies remain to maintain diversity.
    
    Original 9 strategies:
    - Linear: Standard normalization (good for normally distributed data)
    - Log: Log transform (good for heavy-tailed/exponential distributions)  
    - Robust: Quantile-based (good for data with outliers)
    - Rank: Rank percentile transform (ultimate outlier immunity, order-preserving)
    - Periodic: Sin/Cos encoding (for cyclical/temporal features)
    - Bucket: Discretize into 10 quantile buckets (noise reduction, easier relationships)
    - Is Positive (> 0): Binary indicator for positive values (useful for "has_thingy" features)
    - Is Negative (< 0): Binary indicator for negative values (useful for detecting negative values)
    - Is Outlier (> 2 std from mean): Binary indicator for outliers (useful for detecting anomalous values)
    
    New 11 strategies:
    - Z-Score: Forces zero-mean, unit variance (classic standardization)
    - Min-Max: Maps to [0, 1] range (useful for fixed-range features)
    - Quantile: Uniform distribution transform
    - Yeo-Johnson: Power transform for skewed data (handles zero/negative values)
    - Winsorization: Gentle outlier handling (clips to percentiles)
    - Sigmoid: Soft-squash extreme values (smooth clipping)
    - Inverse: Reciprocal transform (1/x, captures diminishing returns)
    - Polynomial: x² and √x features (2nd-order interactions)
    - Frequency: Count encoding for integer scalars that are categorical
    - Target-Guided Binning: Quantile-based bins (approximated)
    - Clipped Log: log(1+x) with clipping for stability
    
    TODO: Connect uncertainty estimation to <UNKNOWN> token
          When model has high reconstruction error (residual), it indicates uncertainty.
          We could use this to emit UNKNOWN tokens or flag predictions as low-confidence.
          This would make the model "know what it doesn't know" for OOD detection.
    """
    def __init__(self, stats, d_model, column_name=None, normalize=True, enable_reconstruction=True):
        super().__init__()
        self.stats = stats
        self.d_model = d_model
        self.column_name = column_name  # Store column name for logging
        self.normalize = normalize  # Control whether to normalize output (matches ScalarEncoder/StringEncoder)
        self.enable_reconstruction = enable_reconstruction  # Whether to create decoder for reconstruction loss
        
        # Get hidden dimension from config (defaults to 16 for speed)
        from featrix.neural.sphere_config import get_config
        hidden_dim = get_config().get_adaptive_scalar_hidden_dim()
        
        # Log once per process (not per column)
        if not hasattr(AdaptiveScalarEncoder, '_logged_hidden_dim'):
            logger.info(f"🔧 AdaptiveScalarEncoder using hidden_dim={hidden_dim} (configurable via adaptive_scalar_hidden_dim)")
            AdaptiveScalarEncoder._logged_hidden_dim = True
        
        # Register statistics as buffers (non-trainable, saved with model)
        for key, val in stats.items():
            self.register_buffer(key, torch.tensor(float(val)))
        
        # Compute 10 quantile-based bucket boundaries (deciles)
        # Buckets: [min→q10, q10→q25, q25→median, median→q75, q75→q90, q90→max, etc.]
        self.n_buckets = 10
        self.register_buffer('bucket_boundaries', self._compute_bucket_boundaries(stats))
        
        # Strategy 1: Linear transform (standard normalization)
        self.linear_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 2: Log transform (for heavy-tailed distributions)
        self.log_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 3: Robust transform (quantile-based, immune to outliers)
        self.robust_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 4: Rank transform (extreme outlier immunity, only cares about ordering)
        self.rank_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 5: Periodic transform (for cyclical/temporal features)
        # Takes 2 inputs: sin and cos
        self.periodic_mlp = nn.Sequential(
            nn.Linear(2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 6: Bucket transform (discretize into quantile buckets)
        # Uses ordered embeddings like SetEncoder
        self.bucket_embedding = nn.Embedding(self.n_buckets, d_model)
        nn.init.xavier_uniform_(self.bucket_embedding.weight)
        
        # Strategy 7: Is Positive (> 0) - binary indicator for positive values
        # Useful for "has_thingy" features where you just care about presence
        self.is_positive_embedding = nn.Embedding(2, d_model)  # 0 = not positive, 1 = positive
        nn.init.xavier_uniform_(self.is_positive_embedding.weight)
        
        # Strategy 8: Is Negative (< 0) - binary indicator for negative values
        # Useful for detecting negative values as a feature
        self.is_negative_embedding = nn.Embedding(2, d_model)  # 0 = not negative, 1 = negative
        nn.init.xavier_uniform_(self.is_negative_embedding.weight)
        
        # Strategy 9: Is Outlier (> 2 std from mean) - binary indicator for outliers
        # Useful for detecting anomalous values that are far from the distribution
        self.is_outlier_embedding = nn.Embedding(2, d_model)  # 0 = not outlier, 1 = outlier
        nn.init.xavier_uniform_(self.is_outlier_embedding.weight)
        
        # Strategy 10: Z-Score Standardization (forces zero-mean, unit variance)
        self.zscore_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 11: Min-Max Scaling (maps to [0, 1] range)
        self.minmax_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 12: Quantile Normalization (uniform distribution)
        self.quantile_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 13: Yeo-Johnson Power Transform (handles zero/negative values)
        self.yeojohnson_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 14: Winsorization (gentle outlier handling)
        self.winsor_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 15: Sigmoid Transform (soft-squash extreme values)
        self.sigmoid_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 16: Inverse/Reciprocal Transform (1/x, captures diminishing returns)
        self.inverse_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 17: Polynomial Features (x², √x)
        # Takes 2 inputs: x² and √x
        self.polynomial_mlp = nn.Sequential(
            nn.Linear(2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 18: Frequency/Count Encoding (for integer scalars that are categorical)
        # Uses embedding based on value frequency
        # For now, we'll use a simple embedding - in practice, this would use actual frequency
        self.frequency_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Strategy 19: Target-Guided Binning (approximated using quantile-based bins)
        # In practice, this would use target distribution, but we'll use quantiles as proxy
        self.target_bin_embedding = nn.Embedding(self.n_buckets, d_model)
        nn.init.xavier_uniform_(self.target_bin_embedding.weight)
        
        # Strategy 20: Clipped Log (log(1+x) with clipping for stability)
        self.clipped_log_mlp = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # ============================================================================
        # DUAL-PATH ARCHITECTURE: Continuous + Binned paths with learned mixer
        # ============================================================================
        # This addresses the linearity problem by separating smooth continuous
        # transforms from discrete binned transforms, then mixing them.
        #
        # Path 1 (Continuous): All smooth, differentiable transforms → single MLP
        #   Inputs: linear, log, robust, rank, zscore, minmax, quantile, yeojohnson,
        #           winsor, sigmoid, inverse, clipped_log (12) + periodic (2) + 
        #           polynomial (2) + frequency (1) = 17 scalar inputs
        #
        # Path 2 (Binned): All discrete/flag transforms → embeddings → MLP
        #   Inputs: bucket, is_positive, is_negative, is_outlier, target_bin (5 embeddings)
        #
        # Mixer: Learns when to use continuous vs binned representation
        # ============================================================================
        
        # Continuous path: 17 scalar transforms → d_model
        # This should produce HIGH LINEARITY since all inputs are smooth
        continuous_input_dim = 17  # 12 scalars + 2 periodic + 2 polynomial + 1 frequency
        self.continuous_path = nn.Sequential(
            nn.Linear(continuous_input_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, d_model)
        )
        
        # Binned path: 5 embeddings (each d_model) → concatenate → MLP → d_model
        # This captures categorical-like structure
        binned_input_dim = 5 * d_model  # bucket, is_pos, is_neg, is_outlier, target_bin
        self.binned_path = nn.Sequential(
            nn.Linear(binned_input_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim * 2, d_model)
        )
        
        # Mixer: Gating network decides continuous vs binned blend
        # Input: continuous_output (d_model) + binned_output (d_model) → gate [0,1]
        self.mixer_gate = nn.Sequential(
            nn.Linear(2 * d_model, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Output in [0, 1]
        )
        
        # Final projection after mixing (optional residual refinement)
        self.mixer_projection = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.LayerNorm(d_model),
        )
        
        # Track gate values for logging
        self._last_gate_value = 0.5  # Start balanced
        
        # Flag to enable/disable dual-path (for A/B testing)
        # When False, uses original 20-strategy weighted mixture
        self._use_dual_path = True
        
        # STATISTICAL INITIALIZATION: Initialize MLP biases based on data statistics
        # This helps the network start closer to the data distribution
        mlp_strategies = [
            self.linear_mlp, self.log_mlp, self.robust_mlp, self.rank_mlp,
            self.periodic_mlp, self.zscore_mlp, self.minmax_mlp, self.quantile_mlp,
            self.yeojohnson_mlp, self.winsor_mlp, self.sigmoid_mlp, self.inverse_mlp,
            self.polynomial_mlp, self.frequency_mlp, self.clipped_log_mlp
        ]
        for mlp in mlp_strategies:
            self._initialize_mlp_biases_from_stats(mlp, stats)
        
        # Learnable mixture weights (model learns which strategy to use)
        # Initialize with distribution-aware bias based on data statistics
        # Total: 20 strategies (9 original + 11 new)
        base_logits = torch.randn(20) * 0.1  # Small random init to break symmetry
        biased_logits = self._bias_strategy_logits_from_stats(base_logits, stats)
        self.strategy_logits = nn.Parameter(biased_logits)
        
        # Strategy pruning: mask to disable worst-performing strategies
        # Every 5 epochs, we'll disable the worst strategy
        self.register_buffer('_strategy_mask', torch.ones(20, dtype=torch.float32))
        self._pruning_enabled = False
        self.register_buffer('_last_prune_epoch', torch.tensor(-1, dtype=torch.long))
        
        # Track epoch for pruning (set externally by training loop)
        self.register_buffer('_current_epoch', torch.tensor(0, dtype=torch.long))
        self.register_buffer('_total_epochs', torch.tensor(300, dtype=torch.long))  # Default, will be set
        
        # Replacement embedding for special tokens
        self._replacement_embedding = nn.Parameter(torch.zeros(d_model))
        nn.init.normal_(self._replacement_embedding, mean=0.0, std=0.01)
        
        # SCALAR RECONSTRUCTION: Optional decoder for reconstruction loss training
        # encoder(value) → embedding → decoder(embedding) → reconstructed_value
        # This provides explicit training signal for preserving numeric properties
        if self.enable_reconstruction:
            self.decoder = nn.Sequential(
                nn.Linear(d_model, 128),
                nn.LayerNorm(128),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(128, 64),
                nn.LayerNorm(64),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(64, 1),  # Output: single normalized value
            )
            # Initialize with smaller weights for stability
            for module in self.decoder.modules():
                if isinstance(module, nn.Linear):
                    if module.weight.ndim >= 2:
                        nn.init.xavier_uniform_(module.weight, gain=0.5)
                    if module.bias is not None:
                        nn.init.zeros_(module.bias)
        else:
            self.decoder = None
        
        # Progressive pruning: track if this encoder has been disabled
        self._disabled = False
    
    def __setstate__(self, state):
        """Move to CPU during unpickling if in CPU mode. Handle backward compatibility."""
        
        # Restore state
        self.__dict__.update(state)
        
        # BACKWARD COMPATIBILITY: Add normalize attribute if missing (old checkpoints)
        if not hasattr(self, 'normalize'):
            self.normalize = True
            logger.debug(f"AdaptiveScalarEncoder: Added missing 'normalize' attribute (old checkpoint)")
        
        # BACKWARD COMPATIBILITY: Add dual-path attributes if missing (old checkpoints)
        if not hasattr(self, '_use_dual_path'):
            self._use_dual_path = False  # Old checkpoints use original 20-strategy mixture
            self._last_gate_value = 0.5
            logger.debug(f"AdaptiveScalarEncoder: Old checkpoint - using legacy 20-strategy mode")
        
        # CRITICAL: Move all embedding tables and MLPs to CPU if in CPU mode
        # AdaptiveScalarEncoder has many nn.Embedding tables and MLPs that might be on GPU
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        if force_cpu:
            column_name = getattr(self, 'column_name', 'unknown')
            if list(self.parameters()):
                device = next(self.parameters()).device
                if device.type == 'cuda':
                    logger.info(f"📊 AdaptiveScalarEncoder '{column_name}': Moving embedding tables/MLPs to CPU")
                    self.cpu()
            if is_gpu_available():
                empty_gpu_cache()
    
    def _bias_strategy_logits_from_stats(self, base_logits, stats):
        """
        Bias strategy logits based on data distribution characteristics.
        This provides a warm start by favoring strategies that are likely to work well.
        
        Strategy indices:
        0: linear, 1: log, 2: robust, 3: rank, 4: periodic, 5: bucket,
        6: is_positive, 7: is_negative, 8: is_outlier, 9: zscore,
        10: minmax, 11: quantile, 12: yeojohnson, 13: winsor,
        14: sigmoid, 15: inverse, 16: polynomial, 17: frequency,
        18: target_bin, 19: clipped_log
        """
        biased = base_logits.clone()
        
        # Extract statistics (with safe defaults)
        mean = stats.get('mean', 0.0)
        std = stats.get('std', 1.0)
        min_val = stats.get('min', 0.0)
        max_val = stats.get('max', 1.0)
        median = stats.get('median', mean)
        q25 = stats.get('q25', median * 0.75)
        q75 = stats.get('q75', median * 1.25)
        
        # Compute distribution characteristics
        if std > 0:
            cv = abs(std / mean) if mean != 0 else float('inf')  # Coefficient of variation
            skewness_approx = (mean - median) / std if std > 0 else 0  # Approximate skewness
            iqr = q75 - q25 if q25 is not None and q75 is not None else std * 1.35
            outlier_ratio = iqr / abs(median) if median != 0 else 0
        else:
            cv = 0
            skewness_approx = 0
            outlier_ratio = 0
        
        # Bias strategies based on distribution characteristics
        
        # Heavy-tailed/exponential distributions → favor log transforms
        if cv > 1.0 or skewness_approx > 1.0:
            biased[1] += 1.5  # log transform
            biased[19] += 1.0  # clipped_log
            if min_val >= 0:  # Only if no negatives
                biased[12] += 0.5  # yeojohnson (handles positive skew)
        
        # Many outliers → favor robust/rank transforms
        if outlier_ratio > 0.5:
            biased[2] += 1.5  # robust
            biased[3] += 1.5  # rank
            biased[13] += 1.0  # winsorization
            biased[8] += 0.5  # is_outlier indicator
        
        # Normal-like distribution → favor linear/zscore
        if 0.3 < cv < 1.0 and abs(skewness_approx) < 0.5:
            biased[0] += 1.0  # linear
            biased[9] += 1.0  # zscore
        
        # Bounded range → favor minmax
        if max_val - min_val < 100 and max_val > min_val:
            biased[10] += 0.8  # minmax
        
        # Has negative values → favor is_negative indicator
        if min_val < 0:
            biased[7] += 0.5  # is_negative
        
        # Has positive values → favor is_positive indicator
        if max_val > 0:
            biased[6] += 0.5  # is_positive
        
        # Uniform-like (low variance relative to range) → favor quantile/bucket
        if std > 0 and (max_val - min_val) / std > 3:
            biased[11] += 0.8  # quantile
            biased[5] += 0.8  # bucket
        
        # Extreme values → favor sigmoid/winsorization
        if abs(mean) > 10 * std or (max_val - min_val) > 1000:
            biased[14] += 0.8  # sigmoid
            biased[13] += 0.5  # winsorization
        
        # Log the biasing decisions for debugging
        if self.column_name:
            logger.debug(f"📊 Distribution-aware initialization for '{self.column_name}': "
                        f"cv={cv:.2f}, skew≈{skewness_approx:.2f}, outliers={outlier_ratio:.2f}")
        
        return biased
    
    def _initialize_mlp_biases_from_stats(self, mlp, stats):
        """
        Initialize MLP first layer bias based on data statistics.
        This helps the network start closer to the data distribution.
        """
        mean = stats.get('mean', 0.0)
        
        # Find the first Linear layer
        for module in mlp.modules():
            if isinstance(module, nn.Linear) and module.bias is not None:
                # Initialize bias to approximate mean (scaled by a small factor)
                # This helps the network start closer to the data distribution
                with torch.no_grad():
                    # Scale mean by a small factor to avoid extreme initializations
                    bias_init = torch.clamp(torch.tensor(mean * 0.1), min=-1.0, max=1.0)
                    module.bias.fill_(bias_init.item())
                break  # Only initialize first layer
    
    def _compute_bucket_boundaries(self, stats):
        """
        Compute 10 quantile-based bucket boundaries.
        
        Uses deciles (10%, 20%, ..., 90%) with min and max as endpoints.
        Returns tensor of 11 values (boundaries for 10 buckets).
        """
        # Create 10 buckets using available quantiles
        # We have: min, q10, q25, median, q75, q90, max
        # Interpolate to get 10 equal-probability buckets
        
        min_val = stats['min']
        q10 = stats['q10']
        q25 = stats['q25']
        median = stats['median']
        q75 = stats['q75']
        q90 = stats['q90']
        max_val = stats['max']
        
        # 10 buckets = 11 boundaries (0%, 10%, 20%, ..., 100%)
        # Approximate decile boundaries by interpolation
        boundaries = torch.tensor([
            min_val,                                    # 0%
            q10,                                        # 10%
            (q10 + q25) / 2,                           # ~17.5% (interpolate)
            q25,                                        # 25%
            (q25 + median) / 2,                        # ~37.5%
            median,                                     # 50%
            (median + q75) / 2,                        # ~62.5%
            q75,                                        # 75%
            (q75 + q90) / 2,                           # ~82.5%
            q90,                                        # 90%
            max_val                                     # 100%
        ])
        
        return boundaries
        
    def compute_transforms(self, x):
        """
        Compute all 20 transform strategies on input.
        
        Returns tuple of 20 transformed values.
        """
        # Strategy 1: Standard normalization with outlier clipping
        x_linear = (x - self.mean) / (self.std + 1e-8)
        x_linear = torch.clamp(x_linear, -10, 10)  # Clip extreme outliers
        
        # Strategy 2: Log transform (handles heavy tails/exponential distributions)
        # Use log1p for numerical stability, preserve sign
        x_centered = x - self.median
        x_log = torch.sign(x_centered) * torch.log1p(torch.abs(x_centered) / (self.std + 1e-8))
        x_log = torch.clamp(x_log, -10, 10)
        
        # Strategy 3: Robust (clip to 10-90 percentile, ignores outliers completely)
        x_robust = torch.clamp(x, self.q10, self.q90)
        x_robust = (x_robust - self.q10) / (self.q90 - self.q10 + 1e-8)
        x_robust = 2.0 * x_robust - 1.0  # Scale to [-1, 1]
        
        # Strategy 4: Rank transform (map to percentile rank [0, 1])
        # For inference, approximate rank using CDF of normal distribution
        # This gives smooth rank estimation without needing full dataset
        x_rank = (x - self.median) / (self.std + 1e-8)
        x_rank = torch.clamp(x_rank, -3, 3)  # Clip to ±3 sigma
        x_rank = (x_rank + 3.0) / 6.0  # Map to [0, 1]
        
        # Strategy 5: Periodic transform (for cyclical features)
        # Normalize to [0, 1] then map to angle [0, 2π]
        x_norm = (x - self.min) / (self.max - self.min + 1e-8)
        angle = x_norm * 2.0 * math.pi
        x_periodic = torch.stack([torch.sin(angle), torch.cos(angle)], dim=-1)
        
        # Strategy 6: Bucket transform (discretize into quantile buckets)
        # Assign each value to a bucket (0-9) based on boundaries
        x_bucket = torch.zeros_like(x, dtype=torch.long)
        for i in range(self.n_buckets):
            # Values in bucket i are: boundary[i] <= x < boundary[i+1]
            mask = (x >= self.bucket_boundaries[i]) & (x < self.bucket_boundaries[i + 1])
            x_bucket[mask] = i
        
        # Handle edge case: values exactly at max go to last bucket
        x_bucket[x >= self.bucket_boundaries[-1]] = self.n_buckets - 1
        
        # Strategy 7: Is Positive (> 0) - binary indicator
        x_is_positive = (x > 0).long()
        
        # Strategy 8: Is Negative (< 0) - binary indicator
        x_is_negative = (x < 0).long()
        
        # Strategy 9: Is Outlier (> 2 std from mean) - binary indicator
        x_normalized = (x - self.mean) / (self.std + 1e-8)
        x_is_outlier = (torch.abs(x_normalized) > 2.0).long()
        
        # Strategy 10: Z-Score Standardization (forces zero-mean, unit variance)
        x_zscore = (x - self.mean) / (self.std + 1e-8)
        # No clipping - let it be true z-score
        
        # Strategy 11: Min-Max Scaling (maps to [0, 1] range)
        x_minmax = (x - self.min) / (self.max - self.min + 1e-8)
        x_minmax = torch.clamp(x_minmax, 0.0, 1.0)
        
        # Strategy 12: Quantile Normalization (uniform distribution)
        # Map to uniform distribution using CDF approximation
        x_quantile = (x - self.min) / (self.max - self.min + 1e-8)
        x_quantile = torch.clamp(x_quantile, 0.0, 1.0)
        
        # Strategy 13: Yeo-Johnson Power Transform
        # Simplified version: for positive values use log, for negative use -log(-x+1)
        # Lambda=0 gives log transform, but we'll use a simple approximation
        x_yeojohnson = torch.zeros_like(x)
        pos_mask = x > 0
        neg_mask = x < 0
        zero_mask = x == 0
        x_yeojohnson[pos_mask] = torch.log1p(x[pos_mask] / (self.std + 1e-8))
        x_yeojohnson[neg_mask] = -torch.log1p(-x[neg_mask] / (self.std + 1e-8))
        x_yeojohnson[zero_mask] = 0.0
        x_yeojohnson = torch.clamp(x_yeojohnson, -10, 10)
        
        # Strategy 14: Winsorization (gentle outlier handling)
        # Clip to 5th and 95th percentile (gentler than hard clipping)
        # Use q10 and q90 as approximation
        x_winsor = torch.clamp(x, self.q10, self.q90)
        x_winsor = (x_winsor - self.q10) / (self.q90 - self.q10 + 1e-8)
        
        # Strategy 15: Sigmoid Transform (soft-squash extreme values)
        # Normalize first, then apply sigmoid
        x_sigmoid_input = (x - self.mean) / (self.std + 1e-8)
        x_sigmoid = torch.sigmoid(x_sigmoid_input / 2.0)  # Scale by 2 for gentler curve
        
        # Strategy 16: Inverse/Reciprocal Transform (1/x, captures diminishing returns)
        # Use 1/(1+|x|) to avoid division by zero and preserve sign
        x_inverse = torch.sign(x) / (1.0 + torch.abs(x) / (self.std + 1e-8))
        x_inverse = torch.clamp(x_inverse, -1.0, 1.0)
        
        # Strategy 17: Polynomial Features (x², √x)
        x_normalized_poly = (x - self.mean) / (self.std + 1e-8)
        x_squared = x_normalized_poly ** 2
        x_sqrt = torch.sign(x_normalized_poly) * torch.sqrt(torch.abs(x_normalized_poly) + 1e-8)
        x_polynomial = torch.stack([x_squared, x_sqrt], dim=-1)
        
        # Strategy 18: Frequency/Count Encoding (for integer scalars that are categorical)
        # For now, use normalized value as proxy (in practice would use actual frequency)
        x_frequency = (x - self.min) / (self.max - self.min + 1e-8)
        x_frequency = torch.clamp(x_frequency, 0.0, 1.0)
        
        # Strategy 19: Target-Guided Binning (approximated using quantile-based bins)
        # Use same bucket boundaries as Strategy 6
        x_target_bin = x_bucket.clone()  # Reuse bucket assignment
        
        # Strategy 20: Clipped Log (log(1+x) with clipping for stability)
        x_clipped_log = torch.log1p(torch.abs(x) / (self.std + 1e-8))
        x_clipped_log = torch.clamp(x_clipped_log, 0.0, 10.0)
        x_clipped_log = torch.sign(x) * x_clipped_log  # Preserve sign
        
        return (x_linear, x_log, x_robust, x_rank, x_periodic, x_bucket, x_is_positive, x_is_negative, x_is_outlier,
                x_zscore, x_minmax, x_quantile, x_yeojohnson, x_winsor, x_sigmoid, x_inverse, x_polynomial, 
                x_frequency, x_target_bin, x_clipped_log)
    
    @property
    def unknown_embedding(self):
        return nn.functional.normalize(self._replacement_embedding, dim=-1)

    @property
    def marginal_embedding(self):
        return nn.functional.normalize(self._replacement_embedding, dim=-1)

    @property
    def not_present_embedding(self):
        return nn.functional.normalize(self._replacement_embedding, dim=-1)
    
    def forward(self, token):
        """
        Encode scalar tokens using adaptive mixture of transforms.
        
        Args:
            token: Token object with .value (normalized scalar) and .status
            
        Returns:
            short_vec: 3D embedding (for visualization)
            full_vec: d_model embedding (for training)
        """
        # If disabled (pruned), return zero embeddings
        if self._disabled:
            batch_size = token.value.shape[0]
            zero_embedding = torch.zeros(batch_size, self.d_model, dtype=torch.float32, device=token.value.device)
            short_vec = zero_embedding[:, 0:3]
            full_vec = zero_embedding
            return short_vec, full_vec
        
        x = token.value.float()
        
        # CRITICAL: Ensure value is on the same device as module parameters
        # Respect FEATRIX_FORCE_CPU_SINGLE_PREDICTOR env var - force CPU if set
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        
        # Get device from first available MLP parameter
        module_device = None
        if not force_cpu:
            # Try to get device from any MLP
            for mlp in [self.linear_mlp, self.log_mlp, self.robust_mlp]:
                if mlp is not None:
                    try:
                        module_device = next(mlp.parameters()).device
                        break
                    except (StopIteration, AttributeError):
                        continue
        
        # Force CPU mode if env var is set
        if force_cpu:
            module_device = torch.device('cpu')
            if list(self.parameters()):
                first_param_device = next(self.parameters()).device
                if first_param_device.type != 'cpu':
                    self.cpu()
        
        # Move value to module device if there's a mismatch
        if module_device is not None and x.device != module_device:
            x = x.to(device=module_device)
        
        # Validate inputs
        if torch.isnan(x).any() or torch.isinf(x).any():
            nan_mask = torch.isnan(x) | torch.isinf(x)
            x = torch.where(nan_mask, torch.zeros_like(x), x)
            if not hasattr(self, '_nan_warning_logged'):
                logger.warning(f"⚠️  AdaptiveScalarEncoder: Replaced {nan_mask.sum().item()} NaN/Inf values")
                self._nan_warning_logged = True
        
        # Compute all 20 transforms
        transforms = self.compute_transforms(x)
        (x_linear, x_log, x_robust, x_rank, x_periodic, x_bucket, x_is_positive, x_is_negative, x_is_outlier,
         x_zscore, x_minmax, x_quantile, x_yeojohnson, x_winsor, x_sigmoid, x_inverse, x_polynomial,
         x_frequency, x_target_bin, x_clipped_log) = transforms
        
        # Encode each strategy
        enc_linear = self.linear_mlp(x_linear.unsqueeze(-1))
        enc_log = self.log_mlp(x_log.unsqueeze(-1))
        enc_robust = self.robust_mlp(x_robust.unsqueeze(-1))
        enc_rank = self.rank_mlp(x_rank.unsqueeze(-1))
        enc_periodic = self.periodic_mlp(x_periodic)  # Already has 2 dims
        enc_bucket = self.bucket_embedding(x_bucket)  # Discrete embeddings
        enc_is_positive = self.is_positive_embedding(x_is_positive)  # Binary embedding
        enc_is_negative = self.is_negative_embedding(x_is_negative)  # Binary embedding
        enc_is_outlier = self.is_outlier_embedding(x_is_outlier)  # Binary embedding
        enc_zscore = self.zscore_mlp(x_zscore.unsqueeze(-1))
        enc_minmax = self.minmax_mlp(x_minmax.unsqueeze(-1))
        enc_quantile = self.quantile_mlp(x_quantile.unsqueeze(-1))
        enc_yeojohnson = self.yeojohnson_mlp(x_yeojohnson.unsqueeze(-1))
        enc_winsor = self.winsor_mlp(x_winsor.unsqueeze(-1))
        enc_sigmoid = self.sigmoid_mlp(x_sigmoid.unsqueeze(-1))
        enc_inverse = self.inverse_mlp(x_inverse.unsqueeze(-1))
        enc_polynomial = self.polynomial_mlp(x_polynomial)  # Already has 2 dims
        enc_frequency = self.frequency_mlp(x_frequency.unsqueeze(-1))
        enc_target_bin = self.target_bin_embedding(x_target_bin)  # Discrete embeddings
        enc_clipped_log = self.clipped_log_mlp(x_clipped_log.unsqueeze(-1))
        
        # Weighted mixture (softmax ensures valid probability distribution)
        # Compute softmax only over active (non-pruned) strategies
        # This ensures pruned strategies get EXACTLY 0 weight (not ~3% from exp(0)=1)
        active_mask = self._strategy_mask > 0
        active_indices = torch.where(active_mask)[0]
        
        if active_indices.numel() > 0:
            # Softmax only over active strategies
            active_logits = self.strategy_logits[active_indices]
            active_weights = F.softmax(active_logits, dim=0)
            
            # Full weight vector (zeros for pruned)
            weights = torch.zeros(20, device=self.strategy_logits.device, dtype=self.strategy_logits.dtype)
            weights[active_indices] = active_weights
        else:
            # Fallback if somehow all pruned (shouldn't happen with MIN_STRATEGIES=3)
            weights = torch.ones(20, device=self.strategy_logits.device, dtype=self.strategy_logits.dtype) / 20.0
        
        # STRATEGY PRUNING: Every 5 epochs, drop the worst performing strategy
        # Keep at least 3 strategies to maintain diversity
        # CRITICAL: Wrap in no_grad to prevent gradient graph pollution
        MIN_STRATEGIES = 3
        PRUNE_START_EPOCH = 1  # Start pruning after epoch 1 (was 5)
        PRUNE_INTERVAL = 5    # Prune every 5 epochs
        
        # Helper to get GPU memory (used for extensive debug logging)
        def _get_gpu_mem():
            try:
                if torch.cuda.is_available():
                    return torch.cuda.memory_allocated() / (1024**3)
            except:
                pass
            return None
        
        if self.training:
            with torch.no_grad():
                current_epoch = self._current_epoch.item()
                last_prune = self._last_prune_epoch.item()
                # Prune every PRUNE_INTERVAL epochs, starting from PRUNE_START_EPOCH
                if current_epoch >= PRUNE_START_EPOCH and (current_epoch - last_prune) >= PRUNE_INTERVAL:
                    # Find worst strategy (lowest weight among active strategies)
                    if active_indices.numel() > MIN_STRATEGIES:  # Only prune if more than MIN_STRATEGIES are active
                        # EXTENSIVE GPU MEMORY LOGGING
                        gpu_0 = _get_gpu_mem()
                        
                        # Detach weights to avoid gradient graph issues
                        active_weights_for_pruning = weights[active_indices].detach()
                        gpu_1 = _get_gpu_mem()
                        
                        worst_idx_in_active = torch.argmin(active_weights_for_pruning)
                        gpu_2 = _get_gpu_mem()
                        
                        worst_idx = active_indices[worst_idx_in_active].item()  # Convert to Python int
                        gpu_3 = _get_gpu_mem()
                        
                        # Free temporary tensors immediately
                        del active_weights_for_pruning
                        del worst_idx_in_active
                        gpu_4 = _get_gpu_mem()
                        
                        # Disable worst strategy
                        self._strategy_mask[worst_idx] = 0.0
                        self._last_prune_epoch.fill_(current_epoch)
                        gpu_5 = _get_gpu_mem()
                        
                        strategy_names = ['linear', 'log', 'robust', 'rank', 'periodic', 'bucket', 'is_positive', 
                                        'is_negative', 'is_outlier', 'zscore', 'minmax', 'quantile', 'yeojohnson',
                                        'winsor', 'sigmoid', 'inverse', 'polynomial', 'frequency', 'target_bin', 'clipped_log']
                        col_name_str = f"column '{self.column_name}': " if self.column_name else ""
                        weight_val = weights[worst_idx].detach().item()  # Detach before .item()
                        gpu_6 = _get_gpu_mem()
                        
                        # Recompute weights ONLY after pruning actually changed the mask
                        active_mask = self._strategy_mask > 0
                        active_indices = torch.where(active_mask)[0]
                        gpu_7 = _get_gpu_mem()
                        
                        if active_indices.numel() > 0:
                            active_logits = self.strategy_logits[active_indices]
                            gpu_8a = _get_gpu_mem()
                            active_weights = F.softmax(active_logits, dim=0)
                            gpu_8b = _get_gpu_mem()
                            
                            weights = torch.zeros(20, device=self.strategy_logits.device, dtype=self.strategy_logits.dtype)
                            weights[active_indices] = active_weights
                            gpu_8c = _get_gpu_mem()
                        else:
                            weights = torch.ones(20, device=self.strategy_logits.device, dtype=self.strategy_logits.dtype) / 20.0
                            gpu_8a = gpu_8b = gpu_8c = _get_gpu_mem()
                        
                        gpu_9 = _get_gpu_mem()
                        
                        # Build detailed GPU log
                        if gpu_0 is not None:
                            delta_total = gpu_9 - gpu_0 if gpu_9 else 0
                            gpu_trace = (f"[GPU TRACE: start={gpu_0:.3f} → detach={gpu_1:.3f} → argmin={gpu_2:.3f} → "
                                        f"item={gpu_3:.3f} → del={gpu_4:.3f} → mask={gpu_5:.3f} → weight_val={gpu_6:.3f} → "
                                        f"recompute_mask={gpu_7:.3f} → logits={gpu_8a:.3f} → softmax={gpu_8b:.3f} → "
                                        f"assign={gpu_8c:.3f} → end={gpu_9:.3f} (Δ{delta_total:+.4f}GB)]")
                        else:
                            gpu_trace = ""
                        
                        logger.info(f"🔪 AdaptiveScalarEncoder PRUNING at epoch {current_epoch} ({col_name_str}Disabled worst strategy '{strategy_names[worst_idx]}' (weight={weight_val:.3f}))")
                        logger.info(f"   Active strategies: {active_indices.numel()}/{len(strategy_names)}")
                        if gpu_trace:
                            logger.info(f"   {gpu_trace}")
        
        # ============================================================================
        # DUAL-PATH FORWARD PASS
        # ============================================================================
        if self._use_dual_path:
            # DEBUG: Track GPU memory through dual-path (first column only to avoid spam)
            _debug_gpu = self.training and self.column_name and self.column_name.startswith('a')
            if _debug_gpu:
                try:
                    _gpu_start = torch.cuda.memory_allocated() / (1024**3) if torch.cuda.is_available() else 0
                except:
                    _debug_gpu = False
            
            # PATH 1: Continuous transforms → single embedding
            # Gather all continuous scalar transforms into one vector
            # Order: linear, log, robust, rank, zscore, minmax, quantile, yeojohnson,
            #        winsor, sigmoid, inverse, clipped_log (12) + periodic (2) + polynomial (2) + frequency (1)
            continuous_inputs = torch.cat([
                x_linear.unsqueeze(-1),      # [batch, 1]
                x_log.unsqueeze(-1),         # [batch, 1]
                x_robust.unsqueeze(-1),      # [batch, 1]
                x_rank.unsqueeze(-1),        # [batch, 1]
                x_zscore.unsqueeze(-1),      # [batch, 1]
                x_minmax.unsqueeze(-1),      # [batch, 1]
                x_quantile.unsqueeze(-1),    # [batch, 1]
                x_yeojohnson.unsqueeze(-1),  # [batch, 1]
                x_winsor.unsqueeze(-1),      # [batch, 1]
                x_sigmoid.unsqueeze(-1),     # [batch, 1]
                x_inverse.unsqueeze(-1),     # [batch, 1]
                x_clipped_log.unsqueeze(-1), # [batch, 1]
                x_periodic,                   # [batch, 2] - sin, cos
                x_polynomial,                 # [batch, 2] - x², √x
                x_frequency.unsqueeze(-1),   # [batch, 1]
            ], dim=-1)  # [batch, 17]
            
            if _debug_gpu:
                _gpu_after_cat1 = torch.cuda.memory_allocated() / (1024**3)
            
            continuous_out = self.continuous_path(continuous_inputs)  # [batch, d_model]
            del continuous_inputs  # Free immediately
            
            if _debug_gpu:
                _gpu_after_path1 = torch.cuda.memory_allocated() / (1024**3)
            
            # PATH 2: Binned/flag embeddings → single embedding
            # Gather all discrete embeddings
            binned_inputs = torch.cat([
                enc_bucket,       # [batch, d_model]
                enc_is_positive,  # [batch, d_model]
                enc_is_negative,  # [batch, d_model]
                enc_is_outlier,   # [batch, d_model]
                enc_target_bin,   # [batch, d_model]
            ], dim=-1)  # [batch, 5*d_model]
            
            if _debug_gpu:
                _gpu_after_cat2 = torch.cuda.memory_allocated() / (1024**3)
            
            binned_out = self.binned_path(binned_inputs)  # [batch, d_model]
            del binned_inputs  # Free immediately
            
            if _debug_gpu:
                _gpu_after_path2 = torch.cuda.memory_allocated() / (1024**3)
            
            # MIXER: Learn gate to blend continuous vs binned
            mixer_input = torch.cat([continuous_out, binned_out], dim=-1)  # [batch, 2*d_model]
            gate = self.mixer_gate(mixer_input)  # [batch, 1]
            del mixer_input  # Free immediately
            
            # Blend: gate=1 → all continuous, gate=0 → all binned
            out = gate * continuous_out + (1 - gate) * binned_out  # [batch, d_model]
            del continuous_out, binned_out  # Free immediately
            
            # Optional final projection with residual
            out = self.mixer_projection(out) + out * 0.1  # Residual connection
            
            # Track gate for logging (detach to avoid keeping gradient graph)
            if self.training:
                self._last_gate_value = gate.detach().mean().item()
            del gate  # Free immediately
            
            if _debug_gpu:
                _gpu_end = torch.cuda.memory_allocated() / (1024**3)
                _delta = _gpu_end - _gpu_start
                if abs(_delta) > 0.001:  # Only log if >1MB change
                    logger.debug(f"🔍 DUAL-PATH GPU ({self.column_name}): start={_gpu_start:.3f}→cat1={_gpu_after_cat1:.3f}→path1={_gpu_after_path1:.3f}→cat2={_gpu_after_cat2:.3f}→path2={_gpu_after_path2:.3f}→end={_gpu_end:.3f} (Δ{_delta:+.4f}GB)")
        else:
            # FALLBACK: Original 20-strategy weighted mixture
            out = (weights[0] * enc_linear + 
                   weights[1] * enc_log + 
                   weights[2] * enc_robust +
                   weights[3] * enc_rank +
                   weights[4] * enc_periodic +
                   weights[5] * enc_bucket +
                   weights[6] * enc_is_positive +
                   weights[7] * enc_is_negative +
                   weights[8] * enc_is_outlier +
                   weights[9] * enc_zscore +
                   weights[10] * enc_minmax +
                   weights[11] * enc_quantile +
                   weights[12] * enc_yeojohnson +
                   weights[13] * enc_winsor +
                   weights[14] * enc_sigmoid +
                   weights[15] * enc_inverse +
                   weights[16] * enc_polynomial +
                   weights[17] * enc_frequency +
                   weights[18] * enc_target_bin +
                   weights[19] * enc_clipped_log)
        
        # ENCOURAGE SHARP STRATEGIES: Add entropy penalty to push towards decisive choices
        # Low entropy = sharp/decisive (one strategy dominates)
        # High entropy = uniform/indecisive (all strategies equal)
        # We want LOW entropy, so we subtract it (negative regularization)
        if self.training:
            entropy = -(weights * torch.log(weights + 1e-10)).sum()
            # Scale entropy loss - higher penalty = sharper strategies
            # Use 0.1 * entropy as penalty (encouraging sharper distributions)
            entropy_loss = 0.1 * entropy
            # Store for logging/debugging (detach to avoid keeping gradient graph in logging vars)
            if not hasattr(self, '_last_entropy'):
                self._last_entropy = entropy.detach().item()
                self._last_entropy_loss = entropy_loss.detach().item()
            else:
                self._last_entropy = 0.9 * self._last_entropy + 0.1 * entropy.detach().item()  # EMA
                self._last_entropy_loss = 0.9 * self._last_entropy_loss + 0.1 * entropy_loss.detach().item()
            # Store entropy loss so it can be collected and added to total loss
            # NOTE: We intentionally keep the gradient here so it can be backpropagated
            # This tensor is cleared/overwritten on the next forward pass
            self._current_entropy_loss = entropy_loss
        else:
            # Not training - clear entropy loss
            self._current_entropy_loss = None
        
        # Check for NaN in output
        if torch.isnan(out).any() or torch.isinf(out).any():
            logger.error(f"💥 AdaptiveScalarEncoder output contains NaN/Inf!")
            out = self._replacement_embedding.unsqueeze(0).expand(out.shape[0], -1)
        
        # Override embeddings for special tokens
        out[token.status == TokenStatus.NOT_PRESENT] = self._replacement_embedding
        out[token.status == TokenStatus.UNKNOWN] = self._replacement_embedding
        out[token.status == TokenStatus.MARGINAL] = self._replacement_embedding
        
        # CONDITIONAL NORMALIZATION based on config (matches ScalarEncoder/StringEncoder behavior)
        # This prevents double normalization when using with JointEncoder that also normalizes
        if self.normalize:
            # Add epsilon for numerical stability during normalization
            short_vec = nn.functional.normalize(out[:, 0:3], dim=1, eps=1e-8)
            full_vec = nn.functional.normalize(out, dim=1, eps=1e-8)
        else:
            # No normalization at column level - only joint encoder will normalize
            short_vec = out[:, 0:3]
            full_vec = out
        
        # EXTENSIVE DEBUG: Log GPU memory at end of forward for first column alphabetically
        if self.training and self.column_name and self.column_name.startswith('a'):
            try:
                if torch.cuda.is_available():
                    gpu_end = torch.cuda.memory_allocated() / (1024**3)
                    gpu_reserved = torch.cuda.memory_reserved() / (1024**3)
                    logger.debug(f"📊 AdaptiveScalarEncoder END ({self.column_name}): GPU={gpu_end:.3f}GB alloc, {gpu_reserved:.3f}GB reserved")
            except:
                pass
        
        return short_vec, full_vec
    
    def get_dual_path_info(self):
        """Return dual-path gate and mode info for logging."""
        return {
            'use_dual_path': self._use_dual_path,
            'gate_value': self._last_gate_value,
            'gate_interpretation': 'continuous' if self._last_gate_value > 0.5 else 'binned',
        }
    
    def get_strategy_weights(self):
        """Return current mixture weights for logging/debugging"""
        try:
            # Safety checks: ensure tensors exist and are on same device
            if not hasattr(self, 'strategy_logits') or not hasattr(self, '_strategy_mask'):
                return {'error': 'tensors_not_initialized'}
            
            # Move to CPU to avoid CUDA device-side assert errors during logging
            with torch.no_grad():
                strategy_logits_cpu = self.strategy_logits.cpu()
                strategy_mask_cpu = self._strategy_mask.cpu()
                
                masked_logits = strategy_logits_cpu * strategy_mask_cpu
                weights = F.softmax(masked_logits, dim=0)
                return {
                    'linear': weights[0].item(),
                    'log': weights[1].item(),
                    'robust': weights[2].item(),
                    'rank': weights[3].item(),
                    'periodic': weights[4].item(),
                    'bucket': weights[5].item(),
                    'is_positive': weights[6].item(),
                    'is_negative': weights[7].item(),
                    'is_outlier': weights[8].item(),
                    'zscore': weights[9].item(),
                    'minmax': weights[10].item(),
                    'quantile': weights[11].item(),
                    'yeojohnson': weights[12].item(),
                    'winsor': weights[13].item(),
                    'sigmoid': weights[14].item(),
                    'inverse': weights[15].item(),
                    'polynomial': weights[16].item(),
                    'frequency': weights[17].item(),
                    'target_bin': weights[18].item(),
                    'clipped_log': weights[19].item()
                }
        except Exception as e:
            # Return error dict instead of crashing - logging shouldn't break training
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to get strategy weights: {e}")
            return {'error': str(e)}


class ScalarEncoder(nn.Module):
    def __init__(self, config: ScalarEncoderConfig):
        super().__init__()

        self.config = config

        # CRITICAL FIX: Better parameter initialization to prevent NaN corruption
        self._replacement_embedding = nn.Parameter(torch.zeros(config.d_out))
        # Use normal initialization with small std instead of xavier
        nn.init.normal_(self._replacement_embedding, mean=0.0, std=0.01)

        self.mlp_encoder = SimpleMLP(config)
        
        # Additional initialization: ensure MLP weights are reasonable
        for name, param in self.mlp_encoder.named_parameters():
            if 'weight' in name and param.ndim >= 2:
                # Use xavier with smaller gain for stability
                nn.init.xavier_uniform_(param, gain=0.5)
            elif 'bias' in name:
                nn.init.zeros_(param)

    @property
    def unknown_embedding(self):
        # FIXME: what was the rationale for unknown embeddings again?
        return nn.functional.normalize(self._replacement_embedding, dim=-1)

    @property
    def marginal_embedding(self):
        # We return the same vector as NOT_PRESENT token because they are treated the
        # same from a probabilistic point of view by the network, and should be treated
        # the same when the model is queried.
        # However, they must remain distinct tokens because the masking strategy for the loss
        # function is affected by whether a field is NOT_PRESENT, or MARGINAL.
        return nn.functional.normalize(self._replacement_embedding, dim=-1)

    @property
    def not_present_embedding(self):
        return nn.functional.normalize(self._replacement_embedding, dim=-1)

    def forward(self, token):
        # We want to map (-1, 1) to (0, 1) to fit the traditional
        # SLERP formula.
        # TODO: the cast into float should not be necessary.
        # this has to do with the type that the batching code returns
        # the default is float64, but we want regular float32
        t = token.value.float()  # np.float32(token.value) #.float32()
        
        # CRITICAL: Ensure value is on the same device as module parameters
        # Respect FEATRIX_FORCE_CPU_SINGLE_PREDICTOR env var - force CPU if set
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        
        # Get device from MLP encoder
        module_device = None
        if not force_cpu:
            try:
                module_device = next(self.mlp_encoder.parameters()).device
            except (StopIteration, AttributeError):
                pass
        
        # Force CPU mode if env var is set
        if force_cpu:
            module_device = torch.device('cpu')
            if list(self.parameters()):
                first_param_device = next(self.parameters()).device
                if first_param_device.type != 'cpu':
                    self.cpu()
        
        # Move value to module device if there's a mismatch
        if module_device is not None and t.device != module_device:
            t = t.to(device=module_device)
        
        # CRITICAL FIX: Validate and clamp input values to prevent NaN propagation
        # Check for NaN/Inf in inputs and replace with zeros
        if torch.isnan(t).any() or torch.isinf(t).any():
            nan_mask = torch.isnan(t) | torch.isinf(t)
            t = torch.where(nan_mask, torch.zeros_like(t), t)
            # Log warning (but not too verbose)
            if not hasattr(self, '_nan_warning_logged'):
                logger.warning(f"⚠️  ScalarEncoder: Detected and replaced {nan_mask.sum().item()} NaN/Inf values in input")
                self._nan_warning_logged = True
        
        # Clamp extreme values to reasonable range to prevent gradient explosion
        t = torch.clamp(t, min=-100.0, max=100.0)

        # for basic encoding
        t = t.unsqueeze(dim=1)

        out = self.mlp_encoder(t)
        
        # CRITICAL FIX: Check for NaN in output before proceeding
        if torch.isnan(out).any() or torch.isinf(out).any():
            logger.error(f"💥 ScalarEncoder output contains NaN/Inf!")
            # Replace with replacement embedding to avoid total corruption
            out = self._replacement_embedding.unsqueeze(0).expand(out.shape[0], -1)

        # override embeddings for unknown and not present tokens
        out[token.status == TokenStatus.NOT_PRESENT] = self._replacement_embedding
        out[token.status == TokenStatus.UNKNOWN] = self._replacement_embedding
        out[token.status == TokenStatus.MARGINAL] = self._replacement_embedding

        # CONDITIONAL NORMALIZATION based on config
        # Phase 1 fix: Allow config to control whether column encoders normalize
        if self.config.normalize:
            # Add epsilon for numerical stability during normalization
            short_vec = nn.functional.normalize(out[:, 0:3], dim=1, eps=1e-8)
            full_vec = nn.functional.normalize(out, dim=1, eps=1e-8)
        else:
            # No normalization at column level - only joint encoder will normalize
            short_vec = out[:, 0:3]
            full_vec = out

        return short_vec, full_vec

    @staticmethod
    def get_default_config(d_model: int, dropout: float):
        # Import here to avoid circular import
        from .sphere_config import get_config
        
        # Get normalization setting from global config
        normalize_column_encoders = get_config().get_normalize_column_encoders()
        
        return ScalarEncoderConfig(
            d_out=d_model,
            d_hidden=200,
            n_hidden_layers=3,
            dropout=dropout,
            normalize=normalize_column_encoders,  # Config-controlled normalization
            residual=True,
            use_batch_norm=True,
        )


class ScalarCodec(nn.Module):
    def __init__(self, stats: dict, enc_dim: int):
        super().__init__()
        self._is_decodable = True

        # Store all statistics
        self.stats = stats
        self.mean = stats['mean']
        self.stdev = stats['std']
        self.enc_dim = enc_dim

        self.loss_fn = nn.MSELoss()

    def get_codec_name(self):
        from featrix.neural.model_config import ColumnType
        return ColumnType.SCALAR

    def get_codec_info(self):
        return {
            "mean": self.mean, 
            "std": self.stdev, 
            "enc_dim": self.enc_dim,
            **self.stats  # Include all statistics
        }

    # def set_device(self, device):
    #     self.basic_embed.to(get_device())
    #     self.mlp_encoder.to(get_device())
    #     return

    def get_not_present_token(self):
        return Token(
            value=np.float32(0.0),  # Use float32 instead of int
            status=TokenStatus.NOT_PRESENT,
        )

    def get_marginal_token(self):
        """Return a token representing a masked/marginal value for reconstruction testing."""
        return Token(
            value=np.float32(0.0),  # Value doesn't matter for MARGINAL tokens
            status=TokenStatus.MARGINAL,
        )

    def get_visualization_domain(self, _min=None, _max=None, _steps=40):
        n_std = 2
        if _steps is None:
            _steps = 40

        if _min is not None:
            min = _min
        else:
            min = self.mean - n_std * self.stdev

        if _max is not None:
            max = _max
        else:
            max = self.mean + n_std * self.stdev
        steps = _steps
        # FIXME: this needs some attention!!
        the_data = torch.linspace(min, max, steps)
        return the_data

    @property
    def token_dtype(self):
        return float  # torch.float32
        # return torch.float32

    def tokenize(self, value):
        try:
            # Clean currency symbols and thousands separators from string values
            if isinstance(value, str):
                # Remove common currency symbols ($, €, £, ¥, etc.) and percent signs
                value = value.strip()
                value = value.replace('$', '').replace('€', '').replace('£', '').replace('¥', '').replace('%', '')
                # Remove thousands separators (commas)
                value = value.replace(',', '')
            
            value = float(value)
            # if self.stdev == 0:
            #     print("self.stdev = 0 --> value %s, mean %s" % (value, self.mean))
            if not math.isnan(value):
                if self.stdev == 0:
                    token_value = float(value) - self.mean
                else:
                    token_value = (float(value) - self.mean) / self.stdev
                
                return Token(
                    value=np.float32(token_value),  # Ensure float32 type
                    status=TokenStatus.OK,
                )
            else:
                raise ValueError("ScalarCodec cannot tokenize NaN values.")
        except Exception:
            # TODO: this should be a custom exception

            # if something goes wrong, e.g. with conversion of value into a float,
            # return a token with "unknown" status.
            return Token(
                value=np.float32(0.0),  # Use float32 instead of int
                status=TokenStatus.UNKNOWN,
            )

    def detokenize(self, token: Token):
        if (
            token.status == TokenStatus.NOT_PRESENT
            or token.status == TokenStatus.UNKNOWN
        ):
            raise Exception(f"Cannot detokenize a token with status {token.status}")
        else:
            return (token.value * self.stdev) + self.mean

    def loss(self, predictions, targets):
        # The targets created by the batch loader are Doubles, and they need to be Floats
        # also need to add a dimension to match the dimension of the decoded scalars.
        targets = targets.float().unsqueeze(dim=1)
        return self.loss_fn(predictions, targets)

    def loss_single(self, predictions, targets):
        # Loss function specific to batches of size one, and single targets.

        # We assume that target can be the wrong type, because it's type depends on the
        # types of other target variables it's batched with, and that it's provided as a
        # single value. Therefore, it must be cast to the correct type, and extra dimensions
        # must be added via `unsqueeze`.
        # Preditions looks like `[[4.5]]` and targets looks like `3.4`, so two dimensions must
        # be added.
        # One dimension gets added in `self.loss`, so we add one more here.
        targets = targets.float().unsqueeze(dim=0)

        return self.loss(predictions, targets)

    def save(self):
        # we create a json dict.
        buffer = io.BytesIO()
        torch.save(self.state_dict(), buffer)

        buffer_b64 = "base64:" + str(
            base64.standard_b64encode(buffer.getvalue()).decode("utf8")
        )
        checksum = hashlib.md5(buffer.getvalue()).hexdigest()

        d = {
            "type": "ScalarCodec",
            "embedding": buffer_b64,
            "embedding_checksum": checksum,
            "enc_dim": self.enc_dim,
            "mean": self.mean,
            "stdev": self.stdev,
            "stats": self.stats,  # Save all statistics
        }
        return d

    def load(self, j):
        d_type = j.get("type")
        assert d_type == "ScalarCodec", "wrong load method called for __%s__" % d_type
        self.enc_dim = j.get("enc_dim")
        
        # Backward compatibility: handle old models with just mean/std
        if "stats" in j:
            self.stats = j.get("stats")
            self.mean = self.stats['mean']
            self.stdev = self.stats['std']
        else:
            # Old model format
            self.mean = j.get("mean")
            self.stdev = j.get("stdev")
            self.stats = {
                'mean': self.mean,
                'std': self.stdev,
                'median': self.mean,  # Approximation
                'q10': self.mean - 1.28 * self.stdev,  # -1.28 std ≈ 10th percentile
                'q90': self.mean + 1.28 * self.stdev,
                'q25': self.mean - 0.67 * self.stdev,
                'q75': self.mean + 0.67 * self.stdev,
                'min': self.mean - 3 * self.stdev,
                'max': self.mean + 3 * self.stdev,
            }
        
        embed = j.get("embedding")
        embed_checksum = j.get("embedding_checksum")

        if embed.startswith("base64:"):
            embed = embed[6:]

        r64 = base64.standard_b64decode(embed)
        r_checksum64 = hashlib.md5(r64).hexdigest()

        if r_checksum64 != embed_checksum:
            print(f"CHECKSUMS {r_checksum64} and {embed_checksum} DO NOT MATCH - !")
            return

        self.__init__(self.stats, self.enc_dim)

        buffer = io.BytesIO(r64)
        theDict = torch.load(buffer, weights_only=False)
        self.load_state_dict(theDict)
        return


def runScalerSaveLoadTest():
    data = torch.linspace(-1, 1, 11)  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(data)

    data_list = [float(x) for x in data]
    print(data_list)

    stats = {'mean': np.mean(data_list), 'std': np.std(data_list)}
    codec = ScalarCodec(stats, enc_dim=50)
    jj = codec.save()

    tokenBatch = create_token_batch([codec.tokenize(x) for x in data])
    print("tokenBatch:", tokenBatch)

    preSave_encodedTokens = codec.encode(tokenBatch)
    # print("preSave_encodedTokens = ", preSave_encodedTokens)

    preSave_decodedTokens = codec.decode(preSave_encodedTokens)
    print("preSave_decodedTokens = ", preSave_decodedTokens)

    # print(jj)
    jj_std = jj.get("stdev")
    jj_mean = jj.get("mean")
    jj_enc_dim = jj.get("enc_dim")

    codec = None  # remove from scope
    tokenBatch = None

    new_stats = {'mean': jj_mean, 'std': jj_std}
    newCodec = ScalarCodec(new_stats, jj_enc_dim)
    newCodec.load(jj)
    print(newCodec)

    loadTokenBatch = create_token_batch([newCodec.tokenize(x) for x in data])
    print("loadTokenBatch:", loadTokenBatch)

    postLoad_encodedTokens = newCodec.encode(loadTokenBatch)
    # print("postLoad_encodedTokens = ", postLoad_encodedTokens)

    postLoad_decodedTokens = newCodec.decode(postLoad_encodedTokens)
    print("postLoad_decodedTokens = ", postLoad_decodedTokens)

    assert torch.equal(postLoad_encodedTokens, preSave_encodedTokens)
    assert torch.equal(postLoad_decodedTokens, preSave_decodedTokens)

    return


def runTest():
    return


if __name__ == "__main__":
    runScalerSaveLoadTest()
