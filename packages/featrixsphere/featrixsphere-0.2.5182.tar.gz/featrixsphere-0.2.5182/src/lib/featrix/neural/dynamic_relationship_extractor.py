#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
DynamicRelationshipExtractor: Multi-operation relationship learning with progressive pruning.

Phase 1 (Exploration): Compute all N*(N-1)/2 pairs with 9 operations
Phase 2 (Focused): Prune to top 25% relationships per column

FUSION MODE (use_fusion=True, default):
- All 9 operations are computed then FUSED into 1 token per pair
- 9x reduction in output tokens: N_pairs * 1 instead of N_pairs * 9
- Much more scalable for high column counts

UNFUSED MODE (use_fusion=False):
- Original behavior: 9 separate tokens per pair
- More expressive but higher memory/compute cost

SCALABILITY FEATURES:
- Chunked computation: Process pairs in batches to avoid memory overflow
- Coarse exploration sampling: Sample subset of pairs for very large column counts
- History-aware prioritization: Use meta-learning API to prioritize known-good pairs
"""
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple, Set

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Causal importance scoring and validation
from .causal_relationship_scorer import CausalRelationshipScorer
from .relationship_importance_validator import ImportanceScoringValidator

logger = logging.getLogger(__name__)


def smoothstep01(t: float) -> float:
    """0..1 -> 0..1 with zero slope at ends."""
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return t * t * (3 - 2 * t)


def ramp_plateau(C: int, *, start: int, cap: int, C0: int, C1: int) -> int:
    """
    Start at/below C0, smoothly ramps, hits cap at/above C1.
    
    Args:
        C: Column count
        start: Value at/below C0
        cap: Value at/above C1
        C0: Column count where ramp begins
        C1: Column count where ramp reaches cap
    """
    if C <= C0:
        return start
    if C >= C1:
        return cap
    t = (C - C0) / (C1 - C0)
    s = smoothstep01(t)
    return int(round(start + (cap - start) * s))


def _get_gpu_memory_gb() -> Optional[float]:
    """
    Get total GPU memory in GB.
    
    Returns:
        Total GPU memory in GB, or None if no GPU available.
    """
    if not torch.cuda.is_available():
        return None
    try:
        device_idx = torch.cuda.current_device()
        total_bytes = torch.cuda.get_device_properties(device_idx).total_memory
        return total_bytes / (1024 ** 3)
    except Exception:
        return None


def _compute_max_pairs_for_gpu(
    gpu_memory_gb: Optional[float],
    n_cols: int,
    batch_size: int = 128,
    d_model: int = 128,
) -> int:
    """
    Compute safe max pairs based on GPU memory.
    
    Memory usage for relationship computation is MASSIVE because of:
        1. 8 operations per pair, each creating batch_size × d_model tensors
        2. PyTorch autograd keeping ALL intermediates for backprop
        3. Fusion MLP with multiple layers
        4. Memory fragmentation from many small allocations
    
    EMPIRICAL DATA (this is what actually matters):
        - 5000 pairs on 24GB GPU with batch=128, d_model=128, 149 cols = 22GB usage
        - That's 22GB / 5000 pairs = ~4.4 MB per pair (not KB!)
        - The autograd graph retention is the killer
    
    Safe limits based on empirical 4.4MB/pair at batch=128:
        - 24GB GPU, batch=128 → ~500 pairs (uses ~2.2GB, leaves headroom)
        - 48GB GPU, batch=128 → ~1000 pairs (uses ~4.4GB)
        - 80GB GPU, batch=128 → ~2000 pairs (uses ~8.8GB)
        - 95GB GPU, batch=256 → ~1000 pairs (batch doubles memory)
    
    Args:
        gpu_memory_gb: Total GPU memory in GB (None = no GPU)
        n_cols: Number of columns
        batch_size: Training batch size
        d_model: Model dimension
        
    Returns:
        Maximum number of pairs to compute at once.
    """
    if gpu_memory_gb is None:
        # CPU - be very conservative
        return 100
    
    # Reserve GPU memory for relationship pairs - more conservative for 24GB GPUs
    # The rest is for: model, column encodings, attention, gradients, optimizer, fragmentation
    if gpu_memory_gb <= 24:
        # 24GB GPUs: use only 5% (was 10%) to leave more headroom
        available_for_pairs_gb = gpu_memory_gb * 0.05
    else:
        # Larger GPUs: use 10% as before
        available_for_pairs_gb = gpu_memory_gb * 0.10
    
    # EMPIRICAL: ~4.4 MB per pair at batch=128, d_model=128
    # From: 22GB / 5000 pairs = 4.4MB
    mb_per_pair_base = 4.4  # MB per pair at batch=128, d_model=128
    
    # Scale by batch size (linear relationship with memory)
    batch_scale = batch_size / 128.0
    mb_per_pair = mb_per_pair_base * batch_scale
    
    # Scale by d_model (affects tensor sizes)
    dim_scale = d_model / 128.0
    mb_per_pair = mb_per_pair * dim_scale
    
    # Convert to pairs
    available_mb = available_for_pairs_gb * 1024
    max_pairs = int(available_mb / mb_per_pair)
    
    # Apply sensible bounds: at least 50, at most 1000
    # For 24GB GPUs, cap at 300 pairs (was ~550) to be more conservative
    # Even on huge GPUs, limit to 1000 to avoid fragmentation and ensure stability
    if gpu_memory_gb and gpu_memory_gb <= 24:
        max_pairs = max(50, min(max_pairs, 300))  # Cap at 300 for 24GB
    else:
        max_pairs = max(50, min(max_pairs, 1000))
    
    return max_pairs

# Try to import meta-learning client for relationship history
# Relationship pairs are stored as feature suggestions with type "relationship_pair"
try:
    from meta_learning_client import (
        push_feature_engineering_suggestions,
        retrieve_feature_engineering_suggestions,
        get_dataset_characteristics
    )
    _HAS_META_LEARNING = True
except ImportError:
    _HAS_META_LEARNING = False
    logger.debug("meta_learning_client not available - relationship history disabled")


class DynamicRelationshipExtractor(nn.Module):
    """
    Multi-operation relationship extractor with dynamic pruning.
    
    Operations per pair (A, B):
        Symmetric (compute once):
          - A * B  (multiplication)
          - A + B  (addition)
          - cosine(A, B)  (angular similarity - ignores magnitude)
          - |A - B|  (absolute difference - symmetric "how different")
        
        Asymmetric (compute both directions):
          - A - B, B - A  (subtraction)
          - A / B, B / A  (division)
        
        Presence pattern (null-correlation):
          - 4 flags: both_present, only_a_present, only_b_present, neither_present
    
    Output (configurable via use_fusion flag):
        - use_fusion=True (default):  1 fused token per pair (9x more efficient)
        - use_fusion=False:           9 separate tokens per pair (original)
    
    Pruning Strategy:
        - Epochs 1-N: Compute ALL N*(N-1)/2 pairs, track contributions
        - Epochs N+1 onwards: Each column keeps top 25% partners (~75% reduction)
    """
    
    def __init__(
        self,
        d_model: int,
        col_names_in_order: List[str],
        exploration_epochs: int = 10,
        top_k_fraction: float = 0.40,
        enable_operation_pruning: bool = False,  # Future: prune operations within pairs
        progressive_pruning: bool = True,  # Gradually disable relationships instead of hard cutoff
        pairs_to_prune_per_epoch: int = None,  # How many pairs to disable each epoch (None = auto-calculate)
        target_pruning_epochs: int = None,  # How many epochs to spread pruning over (None = auto from n_epochs)
        min_relationships_to_keep: int = None,  # Minimum relationships to always keep (None = auto: max(5, n_cols/2))
        ucb_alpha: float = 1.5,  # UCB exploration parameter for Phase 2 (default 1.5, typical range 1.0-2.0)
        use_ucb_selection: bool = True,  # Phase 2: Enable UCB selection instead of simple score sorting
        edge_dropout_prob: float = 0.2,  # Edge dropout probability (0.1-0.3 early, reduces hub dominance, free regularization)
        confidence_weight_n0: int = 40,  # Confidence weighting threshold: score = ema_lift × min(1, n_ij/n0) (default 40, range 30-50)
        # ============================================================================
        # COARSE EXPLORATION: Evaluate relationships at lower resolution initially
        # ============================================================================
        # With 1000 columns: 499,500 pairs × 8 ops × 128 dims = 512M elements per batch
        # At coarse_dim=32: 499,500 pairs × 8 ops × 32 dims = 128M elements (4x reduction)
        # This allows exploring ALL pairs cheaply, then focusing on top-K at full resolution
        coarse_exploration_dim: int = 32,  # Dimension for coarse exploration (None = full d_model)
        max_coarse_pairs: int = None,  # Max pairs to evaluate (None = auto based on GPU memory)
        # ============================================================================
        # GPU MEMORY AWARENESS: Limit pairs based on available GPU RAM
        # ============================================================================
        # Empirically, ~4.4MB per pair at batch=128 (autograd graph is huge!)
        # 24GB GPU @ batch=128 → ~550 pairs; 95GB @ batch=256 → ~1000 pairs
        gpu_memory_gb: float = None,  # GPU memory override (None = auto-detect)
        batch_size_hint: int = 128,  # Expected batch size for memory estimation
        # ============================================================================
        # FUSION MODE: Combine all 9 ops into 1 token per pair (9x token reduction)
        # ============================================================================
        use_fusion: bool = True,  # True = 1 fused token/pair, False = 9 separate tokens/pair
    ):
        super().__init__()
        
        self.d_model = d_model
        self.col_names = col_names_in_order
        self.n_cols = len(col_names_in_order)
        self.exploration_epochs = exploration_epochs
        self.top_k_fraction = top_k_fraction
        self.enable_operation_pruning = enable_operation_pruning
        self.progressive_pruning = progressive_pruning
        self.pairs_to_prune_per_epoch = pairs_to_prune_per_epoch
        self.ucb_alpha = ucb_alpha  # UCB exploration parameter
        self.use_ucb_selection = use_ucb_selection  # Phase 2: Enable UCB selection
        self.edge_dropout_prob = edge_dropout_prob  # Edge dropout probability (free regularization)
        self.confidence_weight_n0 = confidence_weight_n0  # Confidence weighting threshold for lift scores
        
        # ============================================================================
        # GPU-AWARE PAIR LIMITING
        # ============================================================================
        # Auto-detect GPU memory if not provided
        if gpu_memory_gb is None:
            gpu_memory_gb = _get_gpu_memory_gb()
        
        # Compute safe max pairs based on GPU memory
        computed_max_pairs = _compute_max_pairs_for_gpu(
            gpu_memory_gb=gpu_memory_gb,
            n_cols=self.n_cols,
            batch_size=batch_size_hint,
            d_model=d_model,
        )
        
        # Use provided max_coarse_pairs if given, otherwise use computed limit
        if max_coarse_pairs is not None:
            self.max_coarse_pairs = max_coarse_pairs
        else:
            self.max_coarse_pairs = computed_max_pairs
        
        # Also limit chunk size for non-exploration (post-pruning) phases
        self.max_pairs_per_chunk = computed_max_pairs
        
        # Log GPU-aware settings
        gpu_str = f"{gpu_memory_gb:.1f}GB" if gpu_memory_gb else "CPU"
        logger.info(f"   🔧 GPU-aware limits ({gpu_str}): max_pairs_per_chunk={self.max_pairs_per_chunk}, "
                   f"max_coarse_pairs={self.max_coarse_pairs}")
        
        # Coarse exploration settings
        self.coarse_exploration_dim = coarse_exploration_dim
        
        # Fusion mode: combine all ops into 1 token per pair
        self.use_fusion = use_fusion
        self.ops_per_pair = 1 if use_fusion else 9  # For external callers to query
        
        # History-aware exploration (uses feature suggestion infrastructure)
        self._session_id: Optional[str] = None
        self._known_good_pairs: Set[Tuple[int, int]] = set()
        self._known_bad_pairs: Set[Tuple[int, int]] = set()
        self._history_loaded = False
        
        # Pair scoring system for meta-learning
        # Track scores: +1 when kept (significant), -1 when culled (worst performing)
        self._pair_scores: Dict[Tuple[int, int], int] = {}
        self._dataset_hash: Optional[str] = None
        
        # Track current epoch (updated externally)
        self.current_epoch = 0
        
        # Store gradient norms captured right after backward() (before zero_grad/step clears them)
        self._stored_grad_norms: Dict[str, float] = {}  # {op_name: grad_norm}
        
        # Track dropout stats per epoch (for coverage reporting)
        self._epoch_dropout_stats = {
            'total_edges_before': 0,
            'total_edges_after': 0,
            'total_dropped': 0,
            'steps_with_dropout': 0,
        }
        
        # Track active edges per step (for coverage reporting)
        self._epoch_active_edges = []  # List of active directed edge counts per step
        
        # Generate all unique pairs (i < j to avoid duplicates)
        # This gives us N*(N-1)/2 pairs, not N*N
        self.all_pairs = []
        for i in range(self.n_cols):
            for j in range(i + 1, self.n_cols):
                self.all_pairs.append((i, j))
        
        # ============================================================================
        # DIRECTED PAIRS: Store as directed edges for proper lift tracking
        # ============================================================================
        # For lift calculation, we need to track (i->j) and (j->i) separately
        # since lift(i->j) measures effect on j when paired with i
        # This is different from the undirected pair (i,j) used for relationship tokens
        self._directed_pairs: Set[Tuple[int, int]] = set()
        for i in range(self.n_cols):
            for j in range(self.n_cols):
                if i != j:
                    self._directed_pairs.add((i, j))
        
        # Support thresholds (split by action type)
        # Scale based on expected observations per pair over a time window
        
        # Parameters:
        # N = n_cols (columns)
        # M = total possible undirected pairs = N*(N-1)/2
        # B = active pairs per batch (limited by GPU memory, ~500-1000)
        # W = time window in steps/batches (how many steps to consider "recent")
        # Expected observations per pair: E[n_ij] = (B * W) / M
        
        total_undirected_pairs = len(self.all_pairs)  # M = N*(N-1)/2
        active_pairs_per_batch = self.max_pairs_per_chunk  # B (limited by GPU memory)
        
        # Time window: consider last W steps/batches as "recent enough"
        # For embedding space training, ~2000 steps ≈ 1-2 epochs (depends on dataset size)
        # Use a conservative window that ensures pairs get observed if they're in active set
        time_window_steps = 2000  # W: steps over which we expect to see pairs
        
        # Compute expected observations per pair in this window
        # Formula: E[n_ij] = (B * W) / M
        # Where:
        #   B = active undirected pairs per batch (limited by GPU memory)
        #   W = time window in steps
        #   M = total possible undirected pairs = N*(N-1)/2
        
        if total_undirected_pairs > 0:
            # B is already undirected pairs per batch (from max_pairs_per_chunk)
            # This accounts for GPU memory limits, not per-column quotas
            # If per-column exploration floor is active, actual B might be higher,
            # but we use the GPU-limited B as the conservative estimate
            expected_obs_per_pair = (active_pairs_per_batch * time_window_steps) / total_undirected_pairs
        else:
            expected_obs_per_pair = float('inf')  # No pairs, thresholds don't matter

        # Scale thresholds based on expected observations, with clamps
        # Clamps prevent thresholds from exploding (small N) or going to zero (large N)

        # TRACK: small multiple of expected (but at least 2-3)
        # Handle infinity: if expected_obs_per_pair is inf, use default minimum
        if math.isinf(expected_obs_per_pair):
            track_from_expected = 2
        else:
            track_from_expected = max(2, int(0.3 * expected_obs_per_pair))
        # Clamp: [2, 20]
        self.MIN_SUPPORT_TRACK = max(2, min(20, track_from_expected))

        # RANK: enough samples to stabilize
        # Use smooth ramp based on column count - simple and predictable
        # For small column counts: start low (15) to allow relationships to be ranked early
        # For large column counts: ramp up to higher values (more pairs = need more samples)
        # Get GPU memory for cap calculation
        actual_gpu_memory = gpu_memory_gb if gpu_memory_gb else (_get_gpu_memory_gb() or 24.0)
        cap = 200 if actual_gpu_memory >= 96 else 200  # Same cap for now, can tune later
        self.MIN_SUPPORT_RANK = ramp_plateau(
            self.n_cols,
            start=15,  # Start value for small column counts
            cap=cap,   # Cap value for large column counts
            C0=20,     # Ramp begins at 20 columns
            C1=100,    # Ramp reaches cap at 100 columns
        )
        # Ensure minimum of 10
        self.MIN_SUPPORT_RANK = max(10, self.MIN_SUPPORT_RANK)

        # PRUNE: rank threshold + safety margin (2.5x expected, but at least 20)
        # Handle infinity: if expected_obs_per_pair is inf, use default minimum
        if math.isinf(expected_obs_per_pair):
            prune_from_expected = 20
        else:
            prune_from_expected = max(20, int(2.5 * expected_obs_per_pair))
        # Clamp: [20, 500] - will be adjusted adaptively based on actual observations
        self.MIN_SUPPORT_PRUNE = max(20, min(500, prune_from_expected))
        
        # Store initial values for reference
        self._initial_min_support_rank = self.MIN_SUPPORT_RANK
        
        # Track when we last checked for adaptive adjustment (to avoid doing it every step)
        self._last_adaptive_check_step = -1
        self._adaptive_check_interval = 100  # Check every 100 steps
        
        # Log scaling decision if significant
        if expected_obs_per_pair < 100 or expected_obs_per_pair > 1:
            logger.info(f"📊 Support thresholds scaled based on expected observations:")
            logger.info(f"   Total undirected pairs (M): {total_undirected_pairs}")
            logger.info(f"   Active pairs per batch (B): {active_pairs_per_batch}")
            logger.info(f"   Time window (W): {time_window_steps} steps")
            logger.info(f"   Expected obs per pair: E[n_ij] = (B*W)/M = {expected_obs_per_pair:.2f}")
            logger.info(f"   MIN_SUPPORT_TRACK: {self.MIN_SUPPORT_TRACK} (clamped from {track_from_expected})")
            logger.info(f"   MIN_SUPPORT_RANK: {self.MIN_SUPPORT_RANK} (from ramp_plateau: C0=20, C1=100)")
            logger.info(f"   MIN_SUPPORT_PRUNE: {self.MIN_SUPPORT_PRUNE} (clamped from {prune_from_expected})")
        
        # Pair statistics for directed edges (i -> j)
        # Track: n_ij (count), lift_ema (EMA of lift), source tracking
        # Structure: {(i,j): {'n': int, 'lift_ema': float, 'last_step': int, 'source_counts': {'null': int, 'bootstrap': int}}}
        self._pair_stats: Dict[Tuple[int, int], Dict] = {}
        self._pair_lift_alpha = 0.1  # EMA decay for lift (0.05-0.2 range, adjust based on noise)
        
        # Track active pairs per batch for lift computation
        # Reset each batch, accumulates pairs from all forward() calls in the batch
        self._active_pairs_this_batch: Set[Tuple[int, int]] = set()
        
        # Track last step's active pairs for exploit candidate fallback
        self._last_step_active_pairs: Optional[Set[Tuple[int, int]]] = None
        
        # Initialize scores for ALL pairs - persists throughout the entire run
        # Score meaning: positive = kept more often, negative = culled more often
        for pair in self.all_pairs:
            self._pair_scores[pair] = 0
        
        logger.info(f"🔗 DynamicRelationshipExtractor: {len(self.all_pairs)} unique pairs "
                   f"({self.n_cols}*({self.n_cols}-1)/2)")
        logger.info(f"   Exploration epochs: {exploration_epochs}")
        logger.info(f"   Top-k fraction: {top_k_fraction} ({int(self.n_cols * top_k_fraction)} partners per column)")
        logger.info(f"   Operations per pair: 8 (multiply, add, cosine, abs_diff, subtract*2, divide*2)")
        logger.info(f"   Tokens during exploration: {len(self.all_pairs) * 8}")
        
        # Log scalability info
        if len(self.all_pairs) > self.max_pairs_per_chunk:
            logger.info(f"   ⚡ SCALABILITY MODE: Chunked computation (≤{self.max_pairs_per_chunk} pairs per chunk)")
            logger.info(f"      This allows training with {self.n_cols} columns ({len(self.all_pairs)} pairs)")
        
        # Operation MLPs
        # Symmetric operations (same result regardless of order)
        self.multiply_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        self.add_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # Cosine similarity: angular relationship between columns (ignores magnitude)
        # Input: 1D scalar per element, we'll project to d_model
        self.cosine_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # Absolute difference: |A - B| - symmetric "how different" measure
        self.abs_diff_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # Asymmetric operations (different result depending on order)
        self.subtract_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # Division MLP: safe division (denominator clamped to prevent explosion)
        # MEMORY FIX: Changed from 4*d_model input (which just repeated data 4x wastefully)
        # to d_model input matching other MLPs - 4x memory reduction for this operation
        self.divide_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # Presence pattern MLP: captures null-correlation structure between column pairs
        # 4 mutually exclusive patterns:
        #   - both_present:    A=1, B=1 (can compute meaningful relationship)
        #   - only_a_present:  A=1, B=0 (B often missing when A exists)
        #   - only_b_present:  A=0, B=1 (A often missing when B exists)  
        #   - neither_present: A=0, B=0 (correlated missingness)
        # Input: 4 binary flags (one-hot style) -> d_model embedding
        self.presence_mlp = nn.Sequential(
            nn.Linear(4, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, d_model)
        )
        
        # FUSION MLP: Combines all 9 operation outputs into a SINGLE token per pair
        # This is a 9x reduction in output tokens (9 ops → 1 fused token)
        # Input: 9 * d_model (concatenated outputs from all operation MLPs)
        # Output: d_model (single fused relationship token)
        self.fusion_mlp = nn.Sequential(
            nn.Linear(9 * d_model, d_model * 2),  # Expand for mixing
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model * 2, d_model)  # Compress to single token
        )
        
        # ============================================================================
        # NULL RELATIONSHIP TOKEN: Represents "no relationship" baseline
        # ============================================================================
        # Contextual NULL: base + column-specific context via MLP
        # This allows NULL to represent "no relationship for this column's context"
        # rather than a global bias vector
        self.null_relationship_base = nn.Parameter(torch.zeros(1, d_model))
        self.null_relationship_mlp = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, d_model)
        )
        self.null_scale = 0.1  # Scale control to prevent NULL from dominating early (anneal later)
        self.null_layer_norm = nn.LayerNorm(d_model)  # Keep NULL comparable to relationship tokens
        
        # NULL baseline tracking (EMA per column)
        self._null_baseline_ema: Dict[str, float] = {}  # {col_name: EMA of NULL-only loss}
        self._null_baseline_source: Dict[str, str] = {}  # {col_name: "null" or "bootstrap"}
        self._null_baseline_n: Dict[str, int] = {}  # {col_name: count of observations}
        self._null_baseline_alpha = 0.1  # EMA decay rate
        if self.n_cols > 0:
            self._null_sample_rate = 20.0 / self.n_cols
        else:
            self._null_sample_rate = 1.0  # No columns, use 100%
        # Adaptive evaluation frequency (more frequent early in training)
        self._null_every_steps_early = 5   # Every 5 steps early (high LR)
        self._null_every_steps_late = 10   # Every 10 steps later (stable)
        self._null_early_epochs = 20       # Use early frequency for first N epochs
        self._step_counter = 0  # Track steps for NULL baseline evaluation
        self._null_evaluation_pending = False  # Flag to trigger NULL-only evaluation
        self._null_batch_mask_modes = []  # Track mode (True=null, False=normal) for each mask in current batch
        self._null_baseline_losses_this_batch: Dict[str, List[float]] = {}  # Accumulate losses across masks
        self._null_baseline_mask_count = 0  # Track how many masks processed this batch
        
        # Track contribution of each pair (for pruning)
        # Key: (i, j) where i < j -> contribution score
        self.pair_contributions = {}
        for pair in self.all_pairs:
            self.pair_contributions[pair] = 0.0
        
        # After exploration, store pruned pairs per column (old hard pruning method)
        self.pruned_pairs_per_column: Optional[Dict[int, List[int]]] = None
        self._pruned_pairs_list: Optional[List[Tuple[int, int]]] = None
        
        # Progressive pruning: track disabled pairs (set of (i,j) tuples)
        
        # LEARNING TRACKING: Track if operation MLPs are learning
        # Store weight snapshots to measure change over time
        self._weight_snapshots = {}  # {epoch: {op_name: weight_norm}}
        self._weight_deltas = {}  # {op_name: [delta_per_epoch]}
        
        self.disabled_pairs: set = set()
        
        # Calculate minimum relationships to always keep (safety floor)
        if min_relationships_to_keep is None:
            # Keep at least max(5, n_cols/2) most important relationships
            # This ensures each column keeps relationships with ~half of other columns at minimum
            # Prevents over-pruning asymmetric relationships where easy columns provide context for hard ones
            min_keep = max(5, self.n_cols // 2)
            self.min_relationships_to_keep = min(min_keep, self.n_cols)
        else:
            self.min_relationships_to_keep = min_relationships_to_keep
        
        # Calculate how many pairs to disable per epoch (auto-calculate if not specified)
        if self.progressive_pruning:
            total_pairs = len(self.all_pairs)
            
            # Edge case: 0 or 1 columns means no pairs to prune
            if total_pairs == 0:
                self.target_pruning_epochs = 0
                self.pairs_to_prune_per_epoch = 0
                logger.info("🔪 Progressive pruning: disabled (no pairs with < 2 columns)")
            else:
                # Auto-calculate target_pruning_epochs if not specified
                if target_pruning_epochs is None:
                    # Assume 15 epochs after exploration (conservative estimate)
                    target_pruning_epochs = 15
                self.target_pruning_epochs = target_pruning_epochs
                
                # Calculate target remaining pairs
                target_remaining = int(total_pairs * self.top_k_fraction)
                # But never go below the minimum floor
                target_remaining = max(target_remaining, self.min_relationships_to_keep)
                pairs_to_remove = total_pairs - target_remaining
                
                # Calculate pairs to prune per epoch: pairs_to_remove / target_epochs, min 1
                if self.pairs_to_prune_per_epoch is None:
                    self.pairs_to_prune_per_epoch = max(1, pairs_to_remove // target_pruning_epochs)
                
                logger.info(
                    f"🔪 Progressive pruning enabled:"
                )
                logger.info(
                    f"   Will disable ~{self.pairs_to_prune_per_epoch} pairs/epoch starting at epoch {exploration_epochs}"
                )
                logger.info(
                    f"   Target: {target_remaining}/{total_pairs} pairs ({100*target_remaining/total_pairs:.1f}%)"
                )
                logger.info(
                    f"   Minimum floor: {self.min_relationships_to_keep} most important pairs (always kept)"
                )
        
        # For gradient tracking during exploration
        self._contribution_ema_alpha = 0.1  # Exponential moving average factor
        
        # Store tokens with pair info for post-backward gradient checking
        # Format: [(pair, token), ...] - populated during forward, consumed after backward
        self._tokens_for_gradient_check: List[Tuple[Tuple[int, int], torch.Tensor]] = []
        
        # Batch counter for throttling logs (log every N batches)
        self._batch_counter = 0
        self._log_every_n_batches = 20  # Log gradient updates every 20 batches
        
        # Track operation-specific contributions (for analysis)
        self.operation_contributions = {
            'multiply': 0.0,
            'add': 0.0,
            'cosine': 0.0,
            'abs_diff': 0.0,
            'subtract': 0.0,
            'divide': 0.0,
        }
        
        # Track contribution history for stability analysis
        self.contribution_history: List[Dict[Tuple[int, int], float]] = []
        
        # Store mutual information estimates (for potential future use)
        self.col_mi_estimates: Dict[str, Optional[float]] = {}
        self.joint_mi_estimate: Optional[float] = None
        
        # CRITICAL: Store per-column marginal losses (NEW METRIC for importance)
        # This tells us which columns are HARD to predict
        # Relationships between hard columns are most valuable
        self.col_marginal_losses: Dict[str, float] = {}  # {col_name: avg_marginal_loss}
        
        # ============================================================================
        # STAGE 1: HISTORY TRACKING
        # ============================================================================
        # Track which pairs were active in which epochs
        self._pair_active_epochs: Dict[Tuple[int, int], Set[int]] = {}
        # Track per-column losses over time
        self._column_loss_history: Dict[str, List[float]] = {}
        # Track all epochs
        self._all_epochs: Set[int] = set()
        
        # ============================================================================
        # STAGE 2: CAUSAL IMPORTANCE SCORING
        # ============================================================================
        self.causal_scorer = CausalRelationshipScorer(
            col_names=col_names_in_order,
            window=5,              # Lookback window for improvement rate
            decay_rate=0.95,       # Exponential decay for recency
            lcb_confidence=1.96,   # 95% confidence interval
            min_observations=3,    # Minimum observations for trust
        )
        logger.info("   🧮 Causal relationship scorer initialized")
        logger.info(f"      Window={5}, Decay={0.95}, LCB confidence={1.96}")
        
        # ============================================================================
        # STAGE 3: VALIDATION
        # ============================================================================
        self.validator = ImportanceScoringValidator(col_names=col_names_in_order)
        logger.info("   ✅ Importance scoring validator initialized")
    
    # ============================================================================
    # RELATIONSHIP HISTORY (META-LEARNING)
    # ============================================================================
    
    def load_relationship_history(
        self,
        df,  # pandas DataFrame for dataset hash
        session_id: str,
    ) -> None:
        """
        Load historical relationship data using the feature suggestion infrastructure.
        
        Relationship pairs are stored as feature suggestions with type "relationship_pair".
        
        Args:
            df: pandas DataFrame (used to compute dataset hash)
            session_id: Current training session ID
        """
        self._session_id = session_id
        
        if not _HAS_META_LEARNING:
            logger.info("ℹ️  Meta-learning client not available - using default pair ordering")
            return
        
        try:
            # Get all feature suggestions for this dataset
            suggestions = retrieve_feature_engineering_suggestions(df, min_votes=1)
            
            # Filter for relationship_pair type
            pair_suggestions = [s for s in suggestions if s.get('suggestion_type') == 'relationship_pair']
            
            if not pair_suggestions:
                logger.info(f"ℹ️  No relationship history for this dataset - will build it during training")
                return
            
            # Build column name to index mapping
            col_to_idx = {name: i for i, name in enumerate(self.col_names)}
            
            # Categorize pairs based on history
            for suggestion in pair_suggestions:
                cols = suggestion.get('columns', [])
                if len(cols) != 2:
                    continue
                col_a, col_b = cols
                if col_a not in col_to_idx or col_b not in col_to_idx:
                    continue
                    
                i, j = col_to_idx[col_a], col_to_idx[col_b]
                if i > j:
                    i, j = j, i  # Ensure i < j
                pair = (i, j)
                
                contribution = suggestion.get('contribution', 0)
                was_pruned = suggestion.get('was_pruned', False)
                votes = suggestion.get('votes', 1)
                
                # Categorize based on history
                if not was_pruned and contribution > 0.1 and votes >= 2:
                    self._known_good_pairs.add(pair)
                elif was_pruned and votes >= 2:
                    self._known_bad_pairs.add(pair)
            
            # ============================================================================
            # CULL BAD PAIRS: Pre-disable known-bad pairs so we don't waste time on them
            # ============================================================================
            # These are pairs that were consistently pruned in previous runs.
            # Skip them entirely instead of wasting compute re-discovering they're bad.
            for pair in self._known_bad_pairs:
                self.disabled_pairs.add(pair)
            
            # Reorder remaining pairs: known-good first, unknown middle
            # (known-bad are already disabled, won't be computed)
            remaining_pairs = [p for p in self.all_pairs if p not in self._known_bad_pairs]
            
            def priority_key(pair):
                if pair in self._known_good_pairs:
                    return 0  # Known-good first
                else:
                    return 1  # Unknown second
            
            self.all_pairs = sorted(remaining_pairs, key=priority_key)
            self._history_loaded = True
            
            logger.info(f"📊 Relationship history loaded from feature suggestions:")
            logger.info(f"   ✅ Known-good pairs: {len(self._known_good_pairs)} (explore first)")
            logger.info(f"   ❌ Known-bad pairs: {len(self._known_bad_pairs)} (pre-disabled, skipped)")
            logger.info(f"   ❓ Unknown pairs: {len(self.all_pairs) - len(self._known_good_pairs)}")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to load relationship history: {e}")
            self._history_loaded = False
    
    def save_relationship_history(
        self,
        df,  # pandas DataFrame for dataset hash
        job_id: Optional[str] = None,
    ) -> bool:
        """
        Save relationship contribution data using the feature suggestion infrastructure.
        
        Relationship pairs are stored as feature suggestions with type "relationship_pair".
        
        Args:
            df: pandas DataFrame (used to compute dataset hash)
            job_id: Optional job ID
            
        Returns:
            True if successfully saved, False otherwise
        """
        if not _HAS_META_LEARNING:
            logger.info("ℹ️  Meta-learning client not available - relationship history not saved")
            return False
        
        try:
            # Convert pair contributions to feature suggestions format
            suggestions = []
            for (i, j), contribution in self.pair_contributions.items():
                if i < len(self.col_names) and j < len(self.col_names):
                    col_a, col_b = self.col_names[i], self.col_names[j]
                    was_pruned = (i, j) in self.disabled_pairs
                    
                    suggestions.append({
                        "suggestion_type": "relationship_pair",
                        "columns": [col_a, col_b],
                        "contribution": float(contribution),
                        "was_pruned": was_pruned,
                        "epoch": self.current_epoch,
                        "description": f"Relationship between {col_a} and {col_b}"
                    })
            
            if not suggestions:
                logger.warning("No relationship data to save")
                return False
            
            # Use the existing feature suggestion infrastructure
            success = push_feature_engineering_suggestions(
                df=df,
                suggestions=suggestions,
                session_id=self._session_id,
                job_id=job_id,
                epoch=self.current_epoch
            )
            
            if success:
                logger.info(f"✅ Relationship history saved ({len(suggestions)} pairs)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to save relationship history: {e}")
            return False
    
    def get_pair_priority(self, pair: Tuple[int, int]) -> int:
        """
        Get priority level for a pair based on history.
        
        Returns:
            0 = known-good (explore first)
            1 = unknown (normal priority)
            2 = known-bad (explore last)
        """
        if pair in self._known_good_pairs:
            return 0
        elif pair in self._known_bad_pairs:
            return 2
        else:
            return 1
    
    def get_null_token(self, col_embedding: torch.Tensor) -> torch.Tensor:
        """
        Get contextual NULL token for a column.
        
        Args:
            col_embedding: (batch_size, d_model) - column i's encoding
        
        Returns:
            null_token: (batch_size, d_model) - contextual NULL for this column
        """
        batch_size = col_embedding.shape[0]
        # Base NULL (global)
        base_null = self.null_relationship_base.expand(batch_size, -1)
        # Column-specific context (scaled to prevent early domination)
        contextual_null = self.null_scale * self.null_relationship_mlp(col_embedding)
        # Combine and normalize
        null_token = base_null + contextual_null
        null_token = self.null_layer_norm(null_token)
        return null_token
    
    def _select_active_directed_pairs_with_candidates(
        self,
        scores_dict: Optional[Dict[Tuple[int, int], float]] = None,
        last_step_actives: Optional[Set[Tuple[int, int]]] = None,
    ) -> Tuple[List[Tuple[int, int]], Dict]:
        """
        Two-stage per-column exploit/explore selection: candidates → scores → finalize.
        
        Stage 1: Build candidate pool per column (cheap, no scoring)
        Stage 2: Score only candidates (not all pairs - critical for large N)
        Stage 3: Finalize selection per column
        
        For each target column j:
        - Exploit candidates: top K_exploit from _pair_stats (if exist) or last step's actives
        - Explore candidates: E random incoming edges (i→j)
        - Score candidates only
        - Exploit: top K_exploit from candidates with valid scores (score = -inf if missing)
        - Explore: K_explore random from candidates (fills gaps even if scores missing)
        
        Args:
            scores_dict: Optional pre-computed scores {(i,j): score}
            last_step_actives: Optional set of pairs from last step (fallback for exploit)
        
        Returns:
            (final_active_pairs, diagnostics_dict)
        """
        N = self.n_cols
        
        # ============================================================================
        # EXPLICIT PARAMETERS: E, K_exploit, K_explore
        # ============================================================================
        # CRITICAL: Use same E computation as forward() to ensure consistency
        # This includes the reduction for large column counts to prevent OOM
        log2_N = np.log2(max(2, N))  # Avoid log(1) = 0
        base_E = max(1, min(32, int(np.ceil(log2_N))))
        # Scale down E for large column counts to prevent OOM (same logic as forward())
        if N > 100:
            # More aggressive reduction: reduce by 1 for every 25 columns above 100
            reduction = min(4, (N - 100) // 25)  # Max reduction of 4
            E = max(2, base_E - reduction)  # Minimum E=2 to preserve some exploration
        else:
            E = base_E
        K_exploit = E  # Initially same as E, but distinct for future tuning
        K_explore = E  # Initially same as E, but distinct for future tuning
        
        # Initialize random number generator (seed once per run, advance per step)
        # This ensures uniform sampling without bias toward hub columns
        if not hasattr(self, '_selection_rng'):
            # Seed once per run (not per step) to avoid fixed patterns
            self._selection_rng = np.random.RandomState(42)  # pylint: disable=no-member
        # RNG advances naturally with each call (no need to reseed per step)
        
        # ============================================================================
        # STAGE 1: BUILD CANDIDATE POOL PER COLUMN (cheap, no scoring)
        # ============================================================================
        selection_start_time = time.time()
        
        candidate_pool_per_column = {}  # {j: set of (i, j) candidates}
        exploit_candidates_per_column = {}  # {j: list of (i, j)} for diagnostics
        explore_candidates_per_column = {}  # {j: list of (i, j)} for diagnostics
        
        for j in range(N):
            exploit_candidates = []
            explore_candidates = []
            
            # Exploit candidates: top K_exploit from _pair_stats (if exist) or last step's actives
            # Get all incoming edges (i→j) with scores from _pair_stats
            # CRITICAL: Only incoming edges (i→j) for target j, not outgoing (j→i)
            incoming_with_stats = []
            for i in range(N):
                if i == j:
                    continue
                if (i, j) in self.disabled_pairs:
                    continue  # Respect disabled pairs
                
                # ASSERT: This must be an incoming edge (i→j) where j is the target
                # The lift definition is: baseline_null_ema[j] - loss_j, so we need (i→j)
                assert i != j, f"Invalid edge: source and target cannot be the same: ({i}, {j})"
                
                stats = self._pair_stats.get((i, j), {})
                lift_ema = stats.get('lift_ema')
                if lift_ema is not None and math.isfinite(lift_ema):
                    incoming_with_stats.append((i, j, lift_ema))
            
            # Sort by lift_ema descending and take top K_exploit
            incoming_with_stats.sort(key=lambda t: t[2], reverse=True)
            exploit_candidates = [(i, j) for (i, j, _) in incoming_with_stats[:K_exploit]]
            
            # Fallback: if no stats available, use last step's actives for this column
            if not exploit_candidates and last_step_actives:
                last_step_for_j = [(i, j_pair) for (i, j_pair) in last_step_actives if j_pair == j]
                exploit_candidates = last_step_for_j[:K_exploit]
            
            # Explore candidates: E random incoming edges (i→j) not disabled
            # Uniform sampling over all i != j to avoid hub bias
            all_incoming = [(i, j) for i in range(N) if i != j and (i, j) not in self.disabled_pairs]
            if len(all_incoming) > 0:
                n_explore = min(K_explore, len(all_incoming))
                if n_explore > 0:
                    # Uniform sampling without replacement (RNG advances naturally)
                    explore_indices = self._selection_rng.choice(len(all_incoming), n_explore, replace=False)
                    explore_candidates = [all_incoming[idx] for idx in explore_indices]
            
            # Combine into candidate pool
            candidate_pool = set(exploit_candidates) | set(explore_candidates)
            candidate_pool_per_column[j] = candidate_pool
            exploit_candidates_per_column[j] = exploit_candidates
            explore_candidates_per_column[j] = explore_candidates
            
            # ASSERT: All candidates must be incoming edges (i→j) for target j
            for edge in candidate_pool:
                assert edge[1] == j, f"Invalid candidate: edge[1]={edge[1]} != target j={j}. Edge must be incoming (i→j)"
        
        # ============================================================================
        # STAGE 2: SCORE ONLY CANDIDATES (not all pairs - critical for large N)
        # ============================================================================
        # Convert candidate pool to undirected pairs for scoring
        candidate_undirected = set()
        for j, candidates in candidate_pool_per_column.items():
            for (i, j) in candidates:
                if i < j:
                    candidate_undirected.add((i, j))
                else:
                    candidate_undirected.add((j, i))
        
        # Score candidates using _compute_pair_scores (only scores the candidate pool)
        if scores_dict is None:
            scores_dict, score_diagnostics = self._compute_pair_scores(list(candidate_undirected))
        else:
            # Use provided scores_dict, but only for candidates
            score_diagnostics = {}
        
        # ============================================================================
        # STAGE 3: FINALIZE SELECTION PER COLUMN
        # ============================================================================
        final_active = set()
        exploit_selected = set()
        explore_selected = set()
        
        for j in range(N):
            candidates = candidate_pool_per_column[j]
            
            # Exploit: top K_exploit from candidates with valid scores
            # Missing scores treated as -inf (not eligible for exploit)
            exploit_scores = []
            for (i, j_candidate) in candidates:
                # ASSERT: Candidate must be incoming edge (i→j) for target j
                assert j_candidate == j, f"Invalid candidate: edge[1]={j_candidate} != target j={j}"
                
                # Get score for undirected pair (i,j) or (j,i)
                undirected_pair = (i, j) if i < j else (j, i)
                score = scores_dict.get(undirected_pair, float('-inf'))
                if score != float('-inf'):
                    exploit_scores.append((i, j, score))
            
            # ========================================================================
            # PHASE 2: UCB SELECTION (design - ready to implement)
            # ========================================================================
            # UCB formula: score_ij^UCB = lift_ema + α * sqrt(log(1 + T) / (1 + n_ij))
            #
            # Where:
            #   - lift_ema: from _pair_stats[(i,j)]['lift_ema']
            #   - α: UCB exploration parameter (self.ucb_alpha, default 1.5)
            #   - T: total steps (self._step_counter)
            #   - n_ij: observation count from _pair_stats[(i,j)]['n']
            #
            # When use_ucb_selection=True, replace simple score with UCB score:
            # ========================================================================
            
            if self.use_ucb_selection:
                # PHASE 2: UCB selection - balances exploration vs exploitation
                exploit_scores_ucb = []
                T = getattr(self, '_step_counter', 1)  # Total steps
                
                for (i, j_candidate) in candidates:
                    assert j_candidate == j, f"Invalid candidate: edge[1]={j_candidate} != target j={j}"
                    
                    # Get lift_ema and n_ij from pair stats
                    stats = self._pair_stats.get((i, j), {})
                    lift_ema = stats.get('lift_ema', 0.0)
                    n_ij = stats.get('n', 0)
                    
                    # UCB bonus: uncertainty decreases with more observations
                    # Low n_ij → high bonus (explore more)
                    # High n_ij → low bonus (exploit lift_ema)
                    if n_ij > 0:
                        ucb_bonus = self.ucb_alpha * math.sqrt(math.log(1 + T) / (1 + n_ij))
                    else:
                        # Never observed: maximum exploration bonus
                        ucb_bonus = self.ucb_alpha * math.sqrt(math.log(1 + T))
                    
                    ucb_score = lift_ema + ucb_bonus
                    exploit_scores_ucb.append((i, j, ucb_score))
                
                # Sort by UCB score descending and take top K_exploit
                exploit_scores_ucb.sort(key=lambda t: t[2], reverse=True)
                exploit = [(i, j) for (i, j, _) in exploit_scores_ucb[:K_exploit]]
            else:
                # PHASE 1: Simple score sorting (current implementation)
                # Sort by score descending and take top K_exploit
                exploit_scores.sort(key=lambda t: t[2], reverse=True)
                exploit = [(i, j) for (i, j, _) in exploit_scores[:K_exploit]]
            
            # Explore: K_explore random from candidates (fills gaps even if scores missing)
            used = set(exploit)
            explore_candidates = [(i, j) for (i, j) in candidates if (i, j) not in used]
            n_explore = min(K_explore, len(explore_candidates))
            if n_explore > 0:
                explore_indices = self._selection_rng.choice(len(explore_candidates), n_explore, replace=False)
                explore = [explore_candidates[idx] for idx in explore_indices]
            else:
                explore = []
            
            # Add to final active set
            for pair in exploit + explore:
                # ASSERT: Final selected edge must be incoming (i→j) for target j
                assert pair[1] == j, f"Invalid final selection: edge[1]={pair[1]} != target j={j}"
                final_active.add(pair)
                if pair in exploit:
                    exploit_selected.add(pair)
                else:
                    explore_selected.add(pair)
        
        selection_time_ms = (time.time() - selection_start_time) * 1000
        
        # ============================================================================
        # DIAGNOSTICS
        # ============================================================================
        # Count columns with NULL baseline available
        cols_with_baseline = 0
        for j in range(N):
            col_j_name = self.col_names[j] if j < len(self.col_names) else None
            if col_j_name and col_j_name in self._null_baseline_ema:
                baseline_val = self._null_baseline_ema[col_j_name]
                if baseline_val is not None and math.isfinite(baseline_val):
                    cols_with_baseline += 1
        
        # Count selected edges with valid scores (not -inf)
        edges_with_valid_score = 0
        for edge in final_active:
            i, j = edge
            undirected_pair = (i, j) if i < j else (j, i)
            score = scores_dict.get(undirected_pair, float('-inf'))
            if score != float('-inf') and math.isfinite(score):
                edges_with_valid_score += 1
        
        diagnostics = {
            'E': E,
            'K_exploit': K_exploit,
            'K_explore': K_explore,
            'total_candidates': sum(len(candidates) for candidates in candidate_pool_per_column.values()),
            'total_final': len(final_active),
            'exploit_count': len(exploit_selected),
            'explore_count': len(explore_selected),
            'exploit_selected': exploit_selected,  # Set of exploit edges (for dropout)
            'explore_selected': explore_selected,  # Set of explore edges (protected from dropout)
            'scored_count': len([p for p in final_active if (p[0] < p[1] and (p[0], p[1]) in scores_dict) or (p[1] < p[0] and (p[1], p[0]) in scores_dict)]),
            'edges_with_valid_score': edges_with_valid_score,  # Edges with valid score (not -inf)
            'cols_with_baseline': cols_with_baseline,  # Columns with NULL baseline available
            'selection_time_ms': selection_time_ms,  # CPU time for selection (diagnostic for large N)
            'score_diagnostics': score_diagnostics,
        }
        
        return list(final_active), diagnostics
    
    def forward(
        self,
        column_encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor] = None,  # (batch_size, n_cols)
        relationship_mode: str = "normal",  # "normal", "null_only", or "single_pair"
        single_pair: Optional[Tuple[int, int]] = None,  # For "single_pair" mode
    ) -> List[torch.Tensor]:
        """
        Extract relationship features from column encodings.
        
        Returns:
            List of relationship token tensors, each (batch_size, d_model)
        """
        # Ensure all attributes are initialized (for backward compatibility with old checkpoints)
        self._ensure_pair_stats_attributes()
        
        # Clear previous batch's tokens to avoid accumulation
        self._tokens_for_gradient_check.clear()
        
        batch_size, n_cols, d_model = column_encodings.shape
        
        # ============================================================================
        # RELATIONSHIP MODE HANDLING
        # ============================================================================
        if relationship_mode == "null_only":
            # NULL-only mode: return NULL tokens for all columns
            # These will be pooled and injected into CLS, giving us NULL baseline
            # CRITICAL: This runs in the same train/eval mode as normal forward
            # (inherited from the calling context), ensuring consistent dropout/training semantics
            null_tokens = []
            for col_idx in range(n_cols):
                col_embedding = column_encodings[:, col_idx, :]  # (batch_size, d_model)
                null_token = self.get_null_token(col_embedding)  # (batch_size, d_model)
                null_tokens.append(null_token)
            # Store empty pairs for Tier 3 (no relationships in null mode)
            self._last_pairs_to_compute = []
            self._last_step_active_pairs = set()
            return null_tokens
        elif relationship_mode == "single_pair":
            # Single pair mode: compute only one relationship (for debugging/targeted lift)
            if single_pair is None:
                raise ValueError("single_pair must be provided when relationship_mode='single_pair'")
            pairs_to_compute = [single_pair]
            is_exploration = False
            # Store for Tier 3
            self._last_pairs_to_compute = pairs_to_compute
            self._last_step_active_pairs = {single_pair, (single_pair[1], single_pair[0])}  # Both directions
        else:
            # Normal mode: determine pairs based on pruning state
            pairs_to_compute = None  # Will be set below
            is_exploration = False  # Set default, will be updated below
        
        # Determine which pairs to compute (normal mode only)
        if relationship_mode == "normal":
            # ========================================================================
            # ALWAYS USE EXPLOIT+EXPLORE SELECTION (every step, not just exploration phase)
            # ========================================================================
            # Get last step's actives for fallback (if available)
            last_step_actives = getattr(self, '_last_step_active_pairs', None)
            
            # Two-stage selection: candidates → scores → finalize
            active_directed_pairs, selection_diagnostics = self._select_active_directed_pairs_with_candidates(
                scores_dict=None,  # Will be computed internally from candidates
                last_step_actives=last_step_actives,
            )
            
            # ========================================================================
            # HARD CAP: Prevent activating all pairs (sanity check)
            # ========================================================================
            # Maximum allowed: N * (K_exploit + K_explore) directed edges
            # This ensures we never fall back to "all pairs" mode
            # The selection function should already respect this, but add safety check
            # MEMORY FIX: Scale down E for large column counts to prevent OOM
            # With 149 cols, E=8 gives 2,384 edges → ~1,192 pairs → massive activation memory
            # Reduce E for large column counts to keep pairs manageable
            log2_N = np.log2(max(2, n_cols))
            base_E = max(1, min(32, int(np.ceil(log2_N))))
            # Scale down E for large column counts to prevent OOM
            # Target: keep max pairs around 500-800 for memory safety
            # Formula: E scales with log2(N) but caps at lower values for large N
            if n_cols > 100:
                # More aggressive reduction: reduce by 1 for every 25 columns above 100
                reduction = min(4, (n_cols - 100) // 25)  # Max reduction of 4
                E = max(2, base_E - reduction)  # Minimum E=2 to preserve some exploration
            else:
                E = base_E
            K_exploit = E
            K_explore = E
            max_allowed_directed = n_cols * (K_exploit + K_explore)
            
            if len(active_directed_pairs) > max_allowed_directed:
                logger.warning(f"⚠️  Selection returned {len(active_directed_pairs)} edges, "
                             f"exceeds max {max_allowed_directed} (N={n_cols}, E={E}). "
                             f"This indicates a bug - selection should respect per-column quotas.")
                # Clamp to max (random sample to avoid bias)
                if len(active_directed_pairs) > max_allowed_directed:
                    # Ensure RNG exists
                    if not hasattr(self, '_selection_rng'):
                        self._selection_rng = np.random.RandomState(42)  # pylint: disable=no-member
                    indices = self._selection_rng.choice(len(active_directed_pairs), max_allowed_directed, replace=False)
                    active_directed_pairs = [active_directed_pairs[i] for i in indices]
            
            # Convert directed pairs to undirected for pairs_to_compute
            # (we track both directions but only compute once per undirected pair)
            undirected_set = set()
            for i, j in active_directed_pairs:
                if i < j:
                    undirected_set.add((i, j))
                else:
                    undirected_set.add((j, i))
            pairs_to_compute = [p for p in undirected_set if p not in self.disabled_pairs]
            
            # MEMORY FIX: Hard cap on total pairs to prevent OOM
            # Even with reduced E, large column counts can still create too many pairs
            # Cap at max_pairs_per_chunk to ensure we can process in a single chunk
            max_safe_pairs = min(self.max_pairs_per_chunk, 800)  # Conservative cap
            if len(pairs_to_compute) > max_safe_pairs:
                logger.warning(f"⚠️  Too many pairs ({len(pairs_to_compute)}) for safe memory usage, "
                             f"capping at {max_safe_pairs} pairs to prevent OOM")
                # Randomly sample to avoid bias
                if not hasattr(self, '_selection_rng'):
                    self._selection_rng = np.random.RandomState(42)  # pylint: disable=no-member
                indices = self._selection_rng.choice(len(pairs_to_compute), max_safe_pairs, replace=False)
                pairs_to_compute = [pairs_to_compute[i] for i in indices]
            
            # ========================================================================
            # EDGE DROPOUT: Drop only exploit edges (preserves exploration floor)
            # ========================================================================
            # STRATEGY: Drop only exploit edges, never explore edges
            # This preserves the exploration floor (K_explore per column) by construction
            # Benefits:
            # - Robustness: prevents over-reliance on specific relationships
            # - No starvation: exploration floor guaranteed (no resampling needed)
            # - Simpler: no complex resampling logic
            # 
            # Higher dropout (0.2-0.3) early, lower (0.1) later as relationships stabilize
            # ========================================================================
            if self.training and self.edge_dropout_prob > 0 and len(pairs_to_compute) > 0:
                # Get exploit vs explore classification from selection diagnostics
                exploit_selected = selection_diagnostics.get('exploit_selected', set())
                explore_selected = selection_diagnostics.get('explore_selected', set())
                
                # Convert exploit/explore sets to undirected pairs for matching
                exploit_undirected = set()
                explore_undirected = set()
                for (i, j) in exploit_selected:
                    undirected = (i, j) if i < j else (j, i)
                    exploit_undirected.add(undirected)
                for (i, j) in explore_selected:
                    undirected = (i, j) if i < j else (j, i)
                    explore_undirected.add(undirected)
                
                # Reuse selection RNG (or create if needed) for consistency
                if not hasattr(self, '_selection_rng'):
                    self._selection_rng = np.random.RandomState(42)  # pylint: disable=no-member
                
                # Drop only exploit edges (never drop explore edges)
                pairs_before_dropout = len(pairs_to_compute)
                pairs_after_dropout = []
                dropped_count = 0
                
                for pair in pairs_to_compute:
                    if pair in exploit_undirected:
                        # This is an exploit edge - drop with probability p
                        keep = self._selection_rng.random() >= self.edge_dropout_prob
                        if keep:
                            pairs_after_dropout.append(pair)
                        else:
                            dropped_count += 1
                    elif pair in explore_undirected:
                        # This is an explore edge - always keep (preserves exploration floor)
                        pairs_after_dropout.append(pair)
                    else:
                        # Edge not classified (shouldn't happen, but be safe)
                        # Default: keep it (conservative)
                        pairs_after_dropout.append(pair)
                
                pairs_to_compute = pairs_after_dropout
                pairs_to_compute_set = set(pairs_to_compute)
                
                # Track dropout stats for epoch summary
                self._epoch_dropout_stats['total_edges_before'] += pairs_before_dropout
                self._epoch_dropout_stats['total_edges_after'] += len(pairs_to_compute)
                self._epoch_dropout_stats['total_dropped'] += dropped_count
                self._epoch_dropout_stats['steps_with_dropout'] += 1
                
                # Count incoming edges per column after dropout
                # For each undirected pair (i, j) where i < j, it contributes:
                # - One incoming edge (i→j) to column j
                # - One incoming edge (j→i) to column i
                incoming_after_dropout = {}  # {j: set of (i, j) edges}
                for j in range(n_cols):
                    incoming_after_dropout[j] = set()
                
                # Count incoming edges from pairs_to_compute (undirected pairs where i < j)
                for pair in pairs_to_compute_set:
                    i, j = pair  # pair is (i, j) where i < j (undirected)
                    # This undirected pair contributes:
                    # - (i→j) incoming edge to column j
                    # - (j→i) incoming edge to column i
                    incoming_after_dropout[j].add((i, j))
                    incoming_after_dropout[i].add((j, i))
                
                # Log dropout stats occasionally
                if hasattr(self, '_step_counter') and self._step_counter % 100 == 0:
                    # Compute per-column statistics before and after dropout
                    # Before dropout: count from active_directed_pairs
                    incoming_before = {}
                    for j in range(n_cols):
                        incoming_before[j] = len([(i, j_edge) for (i, j_edge) in active_directed_pairs if j_edge == j])
                    
                    # After dropout: count from pairs_to_compute_set
                    incoming_after = {}
                    for j in range(n_cols):
                        incoming_after[j] = len(incoming_after_dropout[j])
                    
                    avg_before = np.mean(list(incoming_before.values())) if incoming_before else 0.0
                    avg_after = np.mean(list(incoming_after.values())) if incoming_after else 0.0
                    cols_with_zero = sum(1 for count in incoming_after.values() if count == 0)
                    pct_zero = (cols_with_zero / n_cols * 100) if n_cols > 0 else 0.0
                    
                    # Count exploit vs explore edges dropped
                    exploit_dropped = sum(1 for p in exploit_undirected if p not in pairs_to_compute_set)
                    explore_dropped = sum(1 for p in explore_undirected if p not in pairs_to_compute_set)
                    
                    logger.debug(f"🔗 Edge dropout (exploit-only): kept {len(pairs_to_compute_set)}/{pairs_before_dropout} pairs "
                               f"({dropped_count} dropped: {exploit_dropped} exploit, {explore_dropped} explore)")
                    logger.debug(f"   Strategy: drop only exploit edges (explore floor preserved)")
                    logger.debug(f"   Avg edges/col: {avg_before:.1f} → {avg_after:.1f} "
                               f"(expected: {avg_before - exploit_dropped/len(incoming_before) if incoming_before else avg_before:.1f})")
                    logger.debug(f"   Columns with 0 edges: {cols_with_zero}/{n_cols} ({pct_zero:.1f}%) "
                               f"{'⚠️ INSTABILITY RISK' if pct_zero > 1.0 else '✅ OK'}")
            
            # ========================================================================
            # TRACK ACTIVE DIRECTED PAIRS FOR LIFT COMPUTATION (CRITICAL: after dropout!)
            # ========================================================================
            # CRITICAL: Only track edges that survive dropout + resampling.
            # If an edge is dropped, it should NOT be included in _active_pairs_this_batch
            # and should NOT count toward n_ij. Otherwise you're "observing" edges you
            # didn't actually use, corrupting lift statistics.
            # ========================================================================
            # Convert final pairs_to_compute (after dropout + resampling) back to directed pairs
            # NOTE: Relationships are symmetric - they're pooled and injected into CLS token,
            # affecting all column predictions equally. So we track both (i,j) and (j,i)
            # because both columns receive information from the relationship.
            # This is correct because the pooled relationship vector affects all columns via
            # transformer attention, not just one direction.
            final_active_directed_pairs = set()
            for pair in pairs_to_compute:
                i, j = pair  # pair is (i, j) where i < j (undirected)
                # Track both directions for lift computation
                final_active_directed_pairs.add((i, j))
                final_active_directed_pairs.add((j, i))
            
            # Only track edges that actually survived dropout + resampling
            for directed_pair in final_active_directed_pairs:
                self._active_pairs_this_batch.add(directed_pair)
            
            # Track active edges for epoch summary (count per step)
            self._epoch_active_edges.append(len(final_active_directed_pairs))
            
            # Store this step's actives for next step's fallback (use final pairs after dropout)
            # This ensures fallback uses edges that actually survived dropout
            self._last_step_active_pairs = final_active_directed_pairs
            
            # Store pairs_to_compute (undirected) for Tier 3 local attention mapping
            # This allows JointEncoder to map relationship tokens back to their pairs
            self._last_pairs_to_compute = pairs_to_compute
            
            # ========================================================================
            # SANITY CHECK: Verify system is working (DEBUG, once per step)
            # ========================================================================
            step_counter = getattr(self, '_step_counter', 0)
            if step_counter % 50 == 0:  # Log every 50 steps
                # Count edges before/after dropout
                edges_before_dropout = len(active_directed_pairs)
                edges_after_dropout = len(final_active_directed_pairs)
                
                # Count null baseline columns available
                null_baseline_cols = sum(1 for col_name in self.col_names 
                                        if col_name in self._null_baseline_ema 
                                        and self._null_baseline_ema[col_name] is not None 
                                        and math.isfinite(self._null_baseline_ema[col_name]))
                
                # Count pair_stats entries with n > 0
                pair_stats_with_n = [stats for stats in self._pair_stats.values() if stats.get('n', 0) > 0]
                n_ij_values = [stats.get('n', 0) for stats in self._pair_stats.values() if stats.get('n', 0) > 0]
                
                max_n_ij = max(n_ij_values) if n_ij_values else 0
                median_n_ij = np.median(n_ij_values) if n_ij_values else 0
                
                logger.debug(f"🔍 SANITY CHECK (step {step_counter}):")
                logger.debug(f"   Selected edges: {edges_before_dropout} → {edges_after_dropout} (after dropout)")
                logger.debug(f"   Pair stats updated: {len(pair_stats_with_n)} pairs with n>0")
                logger.debug(f"   NULL baseline columns: {null_baseline_cols}/{len(self.col_names)}")
                logger.debug(f"   n_ij stats: max={max_n_ij}, median={median_n_ij:.1f}")
                logger.debug(f"   Status: {'✅ OK' if (edges_after_dropout > 0 and len(pair_stats_with_n) > 0 and null_baseline_cols > 0) else '⚠️ CHECK'}")
            
            # Set is_exploration for coarse exploration logic (based on epoch, not selection method)
            is_exploration = (self.current_epoch < self.exploration_epochs)
            
            # ========================================================================
            # DIAGNOSTIC LOGGING (every ~50 steps)
            # ========================================================================
            step_counter = getattr(self, '_step_counter', 0)
            if step_counter % 50 == 0 and selection_diagnostics:
                # Per-column statistics (use final pairs after dropout for accuracy)
                incoming_counts = []
                for j in range(n_cols):
                    count = len([p for p in final_active_directed_pairs if p[1] == j])
                    incoming_counts.append(count)
                
                if incoming_counts:
                    min_incoming = min(incoming_counts)
                    mean_incoming = np.mean(incoming_counts)
                    max_incoming = max(incoming_counts)
                else:
                    min_incoming = mean_incoming = max_incoming = 0
                
                # Exploit vs explore breakdown
                exploit_count = selection_diagnostics.get('exploit_count', 0)
                explore_count = selection_diagnostics.get('explore_count', 0)
                total_final = selection_diagnostics.get('total_final', 0)
                
                # Score coverage
                scored_count = selection_diagnostics.get('scored_count', 0)
                edges_with_valid_score = selection_diagnostics.get('edges_with_valid_score', 0)
                cols_with_baseline = selection_diagnostics.get('cols_with_baseline', 0)
                
                logger.info(f"📊 Pair selection stats (step {step_counter}):")
                logger.info(f"   Incoming edges per column: min={min_incoming}, "
                           f"mean={mean_incoming:.1f}, max={max_incoming}")
                if total_final > 0:
                    logger.info(f"   Selection breakdown: exploit={exploit_count} ({exploit_count/total_final*100:.1f}%), "
                               f"explore={explore_count} ({explore_count/total_final*100:.1f}%)")
                    logger.info(f"   Score coverage: {scored_count}/{total_final} ({scored_count/total_final*100:.1f}%)")
                    # % selected edges with valid score (not -inf) - indicates learning vs random walk
                    valid_score_pct = (edges_with_valid_score / total_final * 100) if total_final > 0 else 0.0
                    logger.info(f"   Valid scores: {edges_with_valid_score}/{total_final} ({valid_score_pct:.1f}%) - {'learning' if valid_score_pct > 50 else 'exploring'}")
                # % columns with NULL baseline available - indicates system readiness
                baseline_pct = (cols_with_baseline / n_cols * 100) if n_cols > 0 else 0.0
                logger.info(f"   NULL baseline coverage: {cols_with_baseline}/{n_cols} columns ({baseline_pct:.1f}%)")
                logger.info(f"   Parameters: E={selection_diagnostics.get('E', 0)}, "
                           f"K_exploit={selection_diagnostics.get('K_exploit', 0)}, "
                           f"K_explore={selection_diagnostics.get('K_explore', 0)}")
                selection_time = selection_diagnostics.get('selection_time_ms', 0)
                if selection_time > 0:
                    logger.info(f"   Selection time: {selection_time:.2f}ms")
        
        # ============================================================================
        # COARSE EXPLORATION SAMPLING
        # ============================================================================
        # For very large pair counts (e.g., 1000 columns = 499,500 pairs), sample a 
        # subset during exploration to get coarse signal. We don't need to evaluate
        # ALL pairs at full resolution - just enough to identify promising ones.
        # ============================================================================
        if is_exploration and len(pairs_to_compute) > self.max_coarse_pairs:
            # Sample a random subset for this batch
            # Use different samples each forward pass to eventually cover all pairs
            if not hasattr(self, '_sample_rng'):
                self._sample_rng = np.random.RandomState(42)  # pylint: disable=no-member
            
            # Sample indices (not pairs) to keep the list structure
            n_pairs = len(pairs_to_compute)
            sample_indices = self._sample_rng.choice(n_pairs, self.max_coarse_pairs, replace=False)
            pairs_to_compute = [pairs_to_compute[i] for i in sample_indices]
            
            # Log once per training session (not every forward pass)
            if not hasattr(self, '_coarse_sample_logged'):
                logger.info(f"🎯 Coarse exploration: sampling {self.max_coarse_pairs}/{n_pairs} pairs "
                           f"({100*self.max_coarse_pairs/n_pairs:.1f}%)")
                self._coarse_sample_logged = True
        
        # ============================================================================
        # SCALABLE CHUNKED COMPUTATION
        # ============================================================================
        # Problem: With 200 columns, we have 19,900 pairs × 8 ops = 159,200 tokens
        # Computing all at once can exceed memory limits on MPS/CUDA.
        # EMPIRICAL: Each pair uses ~4.4MB at batch=128 due to autograd graph!
        #
        # Solution: Chunk pairs into manageable batches based on GPU memory
        # GPU-aware max_pairs_per_chunk is computed in __init__ based on available RAM
        # 24GB GPU @ batch=128 → ~550 pairs; 95GB @ batch=256 → ~1000 pairs
        # ============================================================================
        max_chunk = self.max_pairs_per_chunk  # GPU-aware limit from __init__
        
        n_pairs = len(pairs_to_compute)
        
        if n_pairs <= max_chunk:
            # Small enough to compute in one go
            return self._compute_operations_batched(
                column_encodings, 
                mask, 
                pairs_to_compute, 
                is_exploration
            )
        else:
            # Chunk the pairs
            all_tokens = []
            n_chunks = (n_pairs + max_chunk - 1) // max_chunk
            
            # Log once per training session (not every forward pass)
            if not hasattr(self, '_chunking_logged'):
                logger.info(f"🔗 Relationship chunking: {n_pairs} pairs → {n_chunks} chunks of ≤{max_chunk}")
                self._chunking_logged = True
            
            for chunk_idx, chunk_start in enumerate(range(0, n_pairs, max_chunk)):
                chunk_end = min(chunk_start + max_chunk, n_pairs)
                chunk_pairs = pairs_to_compute[chunk_start:chunk_end]
                
                chunk_tokens = self._compute_operations_batched(
                    column_encodings,
                    mask,
                    chunk_pairs,
                    is_exploration
                )
                
                # Extend all_tokens directly WITHOUT detaching
                # The original detach() was breaking gradient flow entirely, preventing
                # the operation MLPs from learning. PyTorch's autograd handles chunked
                # computations correctly without needing manual detach.
                # 
                # NOTE: Tokens MUST stay on GPU with autograd enabled because:
                # 1. They need gradients to flow back to the relationship MLPs (multiply_mlp, add_mlp, etc.)
                # 2. They're used in transformer attention which runs on GPU
                # 3. The transformer indexes into them: R[:, tgt, slot, :] = relationship_tokens[token_idx]
                #
                # The memory issue is that keeping many tokens in a Python list means each
                # tensor keeps its own autograd graph reference. The real solution is to:
                # - Reduce the number of pairs (already done with E scaling and hard cap)
                # - Use gradient checkpointing (already enabled in JointEncoder)
                # - Consider keeping tokens as a single stacked tensor (requires transformer changes)
                all_tokens.extend(chunk_tokens)
                
                # Clear references to allow garbage collection
                del chunk_tokens
                
                # Clear GPU cache between chunks
                if chunk_idx < n_chunks - 1:
                    try:
                        if column_encodings.is_cuda:
                            torch.cuda.empty_cache()
                    except Exception:
                        pass
            
            return all_tokens
    
    def _compute_operations_batched(
        self,
        column_encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor],    # (batch_size, n_cols)
        pairs_to_compute: List[Tuple[int, int]],
        is_exploration: bool,
    ) -> List[torch.Tensor]:
        """
        Compute operations for all pairs in a batched way (MUCH faster than looping).
        
        Instead of:
          for (i, j) in pairs:
              multiply = emb_i * emb_j
              multiply_token = multiply_mlp(multiply)
        
        We do:
          all_multiplies = [emb_i * emb_j for all pairs]  # Shape: (n_pairs*batch, d_model)
          all_multiply_tokens = multiply_mlp(all_multiplies)  # Single MLP call
        
        This reduces Python loop overhead and improves GPU utilization.
        """
        batch_size, n_cols, d_model = column_encodings.shape
        n_pairs = len(pairs_to_compute)
        # CRITICAL: eps must be large enough to prevent division explosion
        # Embeddings are typically in [-0.5, 0.5] range after normalization
        # eps=1e-8 causes gradients to explode to 268M when dividing by near-zero values
        # eps=0.1 is ~20-50% of typical embedding magnitude, preventing extreme ratios
        eps = 0.1
        
        if n_pairs == 0:
            return []
        
        # Apply mask if provided
        if mask is not None:
            # Ensure mask is on the same device as column_encodings (MPS/CUDA/CPU)
            if mask.device != column_encodings.device:
                mask = mask.to(column_encodings.device)
            mask_expanded = mask.unsqueeze(-1)  # (batch_size, n_cols, 1)
            masked_encodings = column_encodings * mask_expanded
        else:
            masked_encodings = column_encodings
        
        # Extract all pairs at once
        indices_i = torch.tensor([i for i, j in pairs_to_compute], device=column_encodings.device)
        indices_j = torch.tensor([j for i, j in pairs_to_compute], device=column_encodings.device)
        
        # (n_pairs, batch_size, d_model) - gather all i and j embeddings
        emb_i_all = masked_encodings[:, indices_i, :].transpose(0, 1)  # (n_pairs, batch_size, d_model)
        emb_j_all = masked_encodings[:, indices_j, :].transpose(0, 1)
        
        # Compute pair masks and presence patterns
        if mask is not None:
            mask_i_all = mask[:, indices_i].transpose(0, 1).unsqueeze(-1)  # (n_pairs, batch_size, 1)
            mask_j_all = mask[:, indices_j].transpose(0, 1).unsqueeze(-1)
            pair_masks = mask_i_all * mask_j_all
            
            # Compute 4 mutually exclusive presence patterns for null-correlation learning
            # These capture structural relationships between column presence/absence
            both_present = mask_i_all * mask_j_all                    # A=1, B=1
            only_a_present = mask_i_all * (1 - mask_j_all)            # A=1, B=0
            only_b_present = (1 - mask_i_all) * mask_j_all            # A=0, B=1
            neither_present = (1 - mask_i_all) * (1 - mask_j_all)     # A=0, B=0
        else:
            pair_masks = torch.ones(n_pairs, batch_size, 1, device=column_encodings.device)
            # When no mask provided, assume all present
            both_present = torch.ones(n_pairs, batch_size, 1, device=column_encodings.device)
            only_a_present = torch.zeros(n_pairs, batch_size, 1, device=column_encodings.device)
            only_b_present = torch.zeros(n_pairs, batch_size, 1, device=column_encodings.device)
            neither_present = torch.zeros(n_pairs, batch_size, 1, device=column_encodings.device)
        
        # Reshape to (n_pairs * batch_size, d_model) for MLP processing
        emb_i_flat = emb_i_all.reshape(n_pairs * batch_size, d_model)
        emb_j_flat = emb_j_all.reshape(n_pairs * batch_size, d_model)
        pair_masks_flat = pair_masks.reshape(n_pairs * batch_size, 1)
        
        # Compute all operations at once
        multiply_all = (emb_i_flat * emb_j_flat) * pair_masks_flat
        add_all = (emb_i_flat + emb_j_flat) * pair_masks_flat
        subtract_ab_all = (emb_i_flat - emb_j_flat) * pair_masks_flat
        subtract_ba_all = (emb_j_flat - emb_i_flat) * pair_masks_flat
        
        # NEW: Absolute difference - symmetric "how different" measure
        abs_diff_all = torch.abs(emb_i_flat - emb_j_flat) * pair_masks_flat
        
        # NEW: Cosine similarity - angular relationship (ignores magnitude)
        # Compute cosine similarity per element-pair, then broadcast to d_model dimensions
        # Normalize along d_model dimension for proper cosine similarity
        emb_i_norm = F.normalize(emb_i_flat, p=2, dim=-1, eps=1e-8)  # (n_pairs * batch, d_model)
        emb_j_norm = F.normalize(emb_j_flat, p=2, dim=-1, eps=1e-8)
        # Element-wise product of normalized vectors gives cosine similarity contribution per dimension
        # Sum gives scalar cosine sim, but we want to preserve d_model dimensions for the MLP
        # So we use element-wise product (which captures directional agreement per dimension)
        cosine_all = (emb_i_norm * emb_j_norm) * pair_masks_flat  # (n_pairs * batch, d_model)
        
        # SAFE DIVISION: Ensure denominator absolute value is at least eps
        # BUG FIX: "x + eps" doesn't guarantee |x + eps| >= eps!
        # If x = -0.12 and eps = 0.1, then x + eps = -0.02 → division explodes
        # Solution: sign(x) * (|x| + eps) ensures denominator is always >= eps from zero
        # Handle x=0 case: when sign returns 0, default to +eps
        def safe_divisor(x):
            sign = torch.sign(x)
            sign = torch.where(sign == 0, torch.ones_like(sign), sign)  # Replace 0 sign with 1
            return sign * (torch.abs(x) + eps)
        
        divide_ab_all = (emb_i_flat / safe_divisor(emb_j_flat)) * pair_masks_flat
        divide_ba_all = (emb_j_flat / safe_divisor(emb_i_flat)) * pair_masks_flat
        # MEMORY FIX: Removed 4x concatenation - divide_mlp now takes d_model input like other MLPs
        
        # MEMORY FIX: Delete intermediate tensors no longer needed
        del emb_i_flat, emb_j_flat, emb_i_norm, emb_j_norm, pair_masks_flat
        del emb_i_all, emb_j_all, pair_masks
        if mask is not None:
            del mask_i_all, mask_j_all
        
        # Build presence pattern input: 4 binary flags concatenated
        # Shape: (n_pairs, batch_size, 4) -> flatten to (n_pairs * batch_size, 4)
        presence_patterns = torch.cat([
            both_present,       # (n_pairs, batch_size, 1)
            only_a_present,     # (n_pairs, batch_size, 1)
            only_b_present,     # (n_pairs, batch_size, 1)
            neither_present,    # (n_pairs, batch_size, 1)
        ], dim=-1)  # (n_pairs, batch_size, 4)
        presence_patterns_flat = presence_patterns.reshape(n_pairs * batch_size, 4)
        
        # MEMORY OPTIMIZATION: Apply MLPs sequentially and delete inputs after use
        # This reduces peak memory by ~50% compared to holding all intermediates
        multiply_tokens = self.multiply_mlp(multiply_all)  # (n_pairs * batch_size, d_model)
        del multiply_all
        
        add_tokens = self.add_mlp(add_all)
        del add_all
        
        cosine_tokens = self.cosine_mlp(cosine_all)
        del cosine_all
        
        abs_diff_tokens = self.abs_diff_mlp(abs_diff_all)
        del abs_diff_all
        
        subtract_ab_tokens = self.subtract_mlp(subtract_ab_all)
        del subtract_ab_all
        
        subtract_ba_tokens = self.subtract_mlp(subtract_ba_all)
        del subtract_ba_all
        
        divide_ab_tokens = self.divide_mlp(divide_ab_all)
        del divide_ab_all
        
        divide_ba_tokens = self.divide_mlp(divide_ba_all)
        del divide_ba_all
        
        presence_tokens = self.presence_mlp(presence_patterns_flat)  # Null-correlation pattern
        del presence_patterns_flat
        
        # All individual operation tokens are (n_pairs * batch_size, d_model)
        # Stack them for fusion or reshape for separate mode
        
        if self.use_fusion:
            # FUSION MODE: Concatenate all 9 ops and fuse into 1 token per pair
            # Stack: (n_pairs * batch_size, 9 * d_model)
            all_ops_concat = torch.cat([
                multiply_tokens,
                add_tokens,
                cosine_tokens,
                abs_diff_tokens,
                subtract_ab_tokens,
                subtract_ba_tokens,
                divide_ab_tokens,
                divide_ba_tokens,
                presence_tokens,
            ], dim=-1)  # (n_pairs * batch_size, 9 * d_model)
            
            # MEMORY FIX: Delete individual MLP outputs now that they're concatenated
            del multiply_tokens, add_tokens, cosine_tokens, abs_diff_tokens
            del subtract_ab_tokens, subtract_ba_tokens, divide_ab_tokens, divide_ba_tokens
            del presence_tokens
            
            # Apply fusion MLP to get single token per pair
            fused_tokens = self.fusion_mlp(all_ops_concat)  # (n_pairs * batch_size, d_model)
            
            # MEMORY FIX: Delete concat now that fusion is done
            del all_ops_concat
            
            # Reshape to (n_pairs, batch_size, d_model)
            fused_tokens = fused_tokens.reshape(n_pairs, batch_size, d_model)
            
            # Build output list: 1 fused token per pair
            # Use contiguous() to ensure clean memory layout (avoids keeping parent tensor alive)
            relationship_tokens = []
            for pair_idx, (i, j) in enumerate(pairs_to_compute):
                relationship_tokens.append(fused_tokens[pair_idx].contiguous())  # (batch_size, d_model)
            
            # MEMORY FIX: Delete fused_tokens now that we've extracted the slices
            del fused_tokens
            
            return relationship_tokens
        else:
            # UNFUSED MODE: Return all 9 separate tokens per pair (original behavior)
            # Reshape back to (n_pairs, batch_size, d_model)
            multiply_tokens = multiply_tokens.reshape(n_pairs, batch_size, d_model)
            add_tokens = add_tokens.reshape(n_pairs, batch_size, d_model)
            cosine_tokens = cosine_tokens.reshape(n_pairs, batch_size, d_model)
            abs_diff_tokens = abs_diff_tokens.reshape(n_pairs, batch_size, d_model)
            subtract_ab_tokens = subtract_ab_tokens.reshape(n_pairs, batch_size, d_model)
            subtract_ba_tokens = subtract_ba_tokens.reshape(n_pairs, batch_size, d_model)
            divide_ab_tokens = divide_ab_tokens.reshape(n_pairs, batch_size, d_model)
            divide_ba_tokens = divide_ba_tokens.reshape(n_pairs, batch_size, d_model)
            presence_tokens = presence_tokens.reshape(n_pairs, batch_size, d_model)
            
            # Build output list: for each pair, add 9 tokens in order
            # Use contiguous() to create clean copies instead of views (avoids keeping parent tensors alive)
            relationship_tokens = []
            for pair_idx, (i, j) in enumerate(pairs_to_compute):
                tokens = [
                    multiply_tokens[pair_idx].contiguous(),      # (batch_size, d_model) - symmetric
                    add_tokens[pair_idx].contiguous(),           # symmetric
                    cosine_tokens[pair_idx].contiguous(),        # symmetric: cosine similarity
                    abs_diff_tokens[pair_idx].contiguous(),      # symmetric: absolute difference
                    subtract_ab_tokens[pair_idx].contiguous(),   # asymmetric: A - B
                    subtract_ba_tokens[pair_idx].contiguous(),   # asymmetric: B - A
                    divide_ab_tokens[pair_idx].contiguous(),     # asymmetric: A / B
                    divide_ba_tokens[pair_idx].contiguous(),     # asymmetric: B / A
                    presence_tokens[pair_idx].contiguous(),      # presence pattern (null-correlation)
                ]
                relationship_tokens.extend(tokens)
            
            # MEMORY FIX: Delete the reshaped tensors now that we've extracted slices
            del multiply_tokens, add_tokens, cosine_tokens, abs_diff_tokens
            del subtract_ab_tokens, subtract_ba_tokens, divide_ab_tokens, divide_ba_tokens
            del presence_tokens
            
            return relationship_tokens
    
    def _compute_operations(
        self,
        emb_a: torch.Tensor,  # (batch, d_model)
        emb_b: torch.Tensor,  # (batch, d_model)
        mask: torch.Tensor,   # (batch, 1) - pair mask (A*B present)
        mask_a: Optional[torch.Tensor] = None,  # (batch, 1) - A present
        mask_b: Optional[torch.Tensor] = None,  # (batch, 1) - B present
        track_operations: bool = False,  # Track operation-specific contributions
    ) -> List[torch.Tensor]:
        """
        Compute all 9 operations between two column embeddings.
        
        Returns:
            List of 9 tokens (batch, d_model) each:
              - 4 symmetric: multiply, add, cosine, abs_diff
              - 4 asymmetric: subtract_ab, subtract_ba, divide_ab, divide_ba
              - 1 presence pattern: null-correlation structure
        """
        # CRITICAL FIX: Detach inputs to break computation graph from previous batches
        # Without this, the computation graph accumulates across batches causing
        # "backward through graph twice" errors
        # NOTE: We still want gradients to flow through the MLPs themselves,
        # so we only detach the INPUT column embeddings, not the MLP outputs
        # Actually, wait - we DO want gradients to flow back to the column encoders!
        # So we should NOT detach here. The issue must be elsewhere.
        
        tokens = []
        # CRITICAL: eps must be large enough to prevent division explosion
        # eps=1e-8 caused 268M gradients when dividing by near-zero embedding values
        # eps=0.1 prevents extreme ratios and stabilizes training
        eps = 0.1
        
        # SYMMETRIC OPERATIONS (order doesn't matter)
        
        # 1. Multiplication: A * B = B * A
        multiply = (emb_a * emb_b) * mask
        multiply_token = self.multiply_mlp(multiply)
        # DISABLED: Hook registration causes "backward through graph twice" error
        # if track_operations and self.training:
        #     multiply_token.register_hook(
        #         lambda grad: self._update_operation_contribution('multiply', grad)
        #     )
        tokens.append(multiply_token)
        
        # 2. Addition: A + B = B + A
        add = (emb_a + emb_b) * mask
        add_token = self.add_mlp(add)
        # DISABLED: Hook registration causes "backward through graph twice" error
        # if track_operations and self.training:
        #     add_token.register_hook(
        #         lambda grad: self._update_operation_contribution('add', grad)
        #     )
        tokens.append(add_token)
        
        # 3. Cosine similarity: angular relationship (ignores magnitude)
        emb_a_norm = F.normalize(emb_a, p=2, dim=-1, eps=1e-8)
        emb_b_norm = F.normalize(emb_b, p=2, dim=-1, eps=1e-8)
        cosine = (emb_a_norm * emb_b_norm) * mask
        cosine_token = self.cosine_mlp(cosine)
        tokens.append(cosine_token)
        
        # 4. Absolute difference: |A - B| - symmetric "how different"
        abs_diff = torch.abs(emb_a - emb_b) * mask
        abs_diff_token = self.abs_diff_mlp(abs_diff)
        tokens.append(abs_diff_token)
        
        # ASYMMETRIC OPERATIONS (order matters, need both directions)
        
        # 5. Subtraction: A - B
        subtract_ab = (emb_a - emb_b) * mask
        subtract_ab_token = self.subtract_mlp(subtract_ab)
        # DISABLED: Hook registration causes "backward through graph twice" error
        # if track_operations and self.training:
        #     subtract_ab_token.register_hook(
        #         lambda grad: self._update_operation_contribution('subtract', grad)
        #     )
        tokens.append(subtract_ab_token)
        
        # 6. Subtraction: B - A (different from A - B!)
        subtract_ba = (emb_b - emb_a) * mask
        subtract_ba_token = self.subtract_mlp(subtract_ba)
        # DISABLED: Hook registration causes "backward through graph twice" error
        # if track_operations and self.training:
        #     subtract_ba_token.register_hook(
        #         lambda grad: self._update_operation_contribution('subtract', grad)
        #     )
        tokens.append(subtract_ba_token)
        
        # 7. Division: A / B (safe division - denominator abs value >= eps)
        # BUG FIX: "x + eps" doesn't guarantee |x + eps| >= eps when x is negative!
        def safe_divisor(x):
            sign = torch.sign(x)
            sign = torch.where(sign == 0, torch.ones_like(sign), sign)
            return sign * (torch.abs(x) + eps)
        
        divide_ab = (emb_a / safe_divisor(emb_b)) * mask
        # MEMORY FIX: divide_mlp now takes d_model input (no more 4x concat)
        divide_ab_token = self.divide_mlp(divide_ab)
        tokens.append(divide_ab_token)
        
        # 8. Division: B / A (safe division - denominator abs value >= eps)
        divide_ba = (emb_b / safe_divisor(emb_a)) * mask
        divide_ba_token = self.divide_mlp(divide_ba)
        tokens.append(divide_ba_token)
        
        # 9. Presence pattern: null-correlation structure (4 mutually exclusive patterns)
        if mask_a is not None and mask_b is not None:
            both_present = mask_a * mask_b                    # A=1, B=1
            only_a_present = mask_a * (1 - mask_b)            # A=1, B=0
            only_b_present = (1 - mask_a) * mask_b            # A=0, B=1
            neither_present = (1 - mask_a) * (1 - mask_b)     # A=0, B=0
        else:
            # When individual masks not provided, assume all present
            batch_size = emb_a.shape[0]
            device = emb_a.device
            both_present = torch.ones(batch_size, 1, device=device)
            only_a_present = torch.zeros(batch_size, 1, device=device)
            only_b_present = torch.zeros(batch_size, 1, device=device)
            neither_present = torch.zeros(batch_size, 1, device=device)
        
        presence_pattern = torch.cat([both_present, only_a_present, only_b_present, neither_present], dim=-1)
        presence_token = self.presence_mlp(presence_pattern)
        tokens.append(presence_token)
        
        if self.use_fusion:
            # FUSION MODE: Concatenate all 9 ops and fuse into 1 token
            all_ops_concat = torch.cat(tokens, dim=-1)  # (batch, 9 * d_model)
            fused_token = self.fusion_mlp(all_ops_concat)  # (batch, d_model)
            return [fused_token]  # Return as list with single token
        else:
            # UNFUSED MODE: Return all 9 separate tokens
            return tokens
    
    def _update_contribution(self, pair: Tuple[int, int], gradient: torch.Tensor):
        """
        Update contribution score for a pair based on gradient magnitude.
        
        Called via backward hook during training.
        Uses exponential moving average to smooth contributions over batches.
        """
        if not self.training:
            return
        
        # Measure contribution as mean absolute gradient
        contribution = gradient.abs().mean().item()
        
        # Exponential moving average
        alpha = self._contribution_ema_alpha
        self.pair_contributions[pair] = (
            alpha * contribution + 
            (1 - alpha) * self.pair_contributions[pair]
        )
    
    def _update_operation_contribution(self, op_name: str, gradient: torch.Tensor):
        """
        Update contribution score for an operation type.
        
        Tracks which operations (multiply, add, subtract, divide) are most effective.
        """
        if not self.training:
            return
        
        # Measure contribution as mean absolute gradient
        contribution = gradient.abs().mean().item()
        
        # Exponential moving average
        alpha = self._contribution_ema_alpha
        self.operation_contributions[op_name] = (
            alpha * contribution + 
            (1 - alpha) * self.operation_contributions[op_name]
        )
    
    def track_contribution_snapshot(self):
        """Save contribution snapshot for stability analysis."""
        snapshot = self.pair_contributions.copy()
        self.contribution_history.append(snapshot)
    
    def update_contributions_from_gradients(self):
        """
        Update pair contributions by checking gradients on retained tokens.
        
        Call this AFTER loss.backward() in the training loop.
        The gradients tell us how much each relationship token contributed to the loss.
        """
        if not self._tokens_for_gradient_check:
            logger.warning("⚠️  DynamicRelationshipExtractor: No tokens to check gradients - retain_grad() may not be working!")
            return
        
        updates_made = 0
        grad_stats = []
        missing_grads = 0
        
        for (i, j), token in self._tokens_for_gradient_check:
            if token.grad is not None:
                grad_magnitude = token.grad.abs().mean().item()
                grad_stats.append(grad_magnitude)
                # Pass the raw gradient tensor to _update_contribution
                # It will compute abs().mean().item() and apply EMA smoothing
                self._update_contribution((i, j), token.grad)
                updates_made += 1
            else:
                missing_grads += 1
        
        # Clear the list for next batch
        self._tokens_for_gradient_check.clear()
        
        # Increment batch counter and log periodically
        self._batch_counter += 1
        should_log = (self._batch_counter % self._log_every_n_batches == 0) or self._batch_counter == 1
        
        # Log every N batches during exploration with detailed stats
        if (updates_made > 0 or missing_grads > 0) and should_log:
            nonzero = sum(1 for c in self.pair_contributions.values() if c > 1e-9)
            if grad_stats:
                avg_grad = sum(grad_stats) / len(grad_stats)
                max_grad = max(grad_stats)
                min_grad = min(grad_stats)
                logger.info(
                    f"🔗 [Epoch {self.current_epoch}, Batch {self._batch_counter}] Updated {updates_made} relationship contributions, "
                    f"{nonzero}/{len(self.pair_contributions)} non-zero pairs | "
                    f"Grad: avg={avg_grad:.6f}, max={max_grad:.6f}, min={min_grad:.6f}"
                )
            
            if missing_grads > 0:
                logger.warning(
                    f"⚠️  [Epoch {self.current_epoch}] {missing_grads}/{updates_made+missing_grads} tokens had NO gradient! "
                    f"This means retain_grad() isn't working properly."
                )
    
    def capture_gradient_norms(self):
        """
        Capture gradient norms right after loss.backward(), before optimizer.step()/zero_grad().
        
        Call this immediately after loss.backward() in the training loop.
        Stores the MAX gradient norm seen across batches (most representative of learning activity).
        """
        current_grad_norms = {}
        for op_name, mlp in [
            ('multiply', self.multiply_mlp),
            ('add', self.add_mlp),
            ('cosine', self.cosine_mlp),
            ('abs_diff', self.abs_diff_mlp),
            ('subtract', self.subtract_mlp),
            ('divide', self.divide_mlp),
            ('presence', self.presence_mlp),  # NULL-correlation pattern
            ('null', self.null_relationship_mlp),  # Contextual NULL - no gradients are good on this one
        ]:
            total_grad_norm = 0.0
            has_grad = False
            
            for param in mlp.parameters():
                if param.requires_grad and param.grad is not None:
                    grad_norm_sq = param.grad.norm().item() ** 2
                    total_grad_norm += grad_norm_sq
                    has_grad = True
            
            current_norm = (total_grad_norm ** 0.5) if has_grad else 0.0
            current_grad_norms[op_name] = current_norm
            
            # Store max across batches (most representative of learning activity)
            if op_name not in self._stored_grad_norms:
                self._stored_grad_norms[op_name] = current_norm
            else:
                self._stored_grad_norms[op_name] = max(self._stored_grad_norms[op_name], current_norm)
    
    def _compute_weight_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Compute weight statistics for each operation MLP.
        
        Uses stored gradient norms if available (captured after backward()),
        otherwise tries to read from current gradients (may be 0 if already zeroed).
        """
        stats = {}
        for op_name, mlp in [
            ('multiply', self.multiply_mlp),
            ('add', self.add_mlp),
            ('cosine', self.cosine_mlp),
            ('abs_diff', self.abs_diff_mlp),
            ('subtract', self.subtract_mlp),
            ('divide', self.divide_mlp),
            ('presence', self.presence_mlp),  # NULL-correlation pattern
            ('null', self.null_relationship_mlp),  # Contextual NULL - no gradients are good on this one
        ]:
            total_params = 0
            total_norm = 0.0
            total_grad_norm = 0.0
            has_grad = False
            
            # Try to use stored gradient norm first (captured after backward())
            if op_name in self._stored_grad_norms:
                total_grad_norm = self._stored_grad_norms[op_name]
                has_grad = total_grad_norm > 0.0
            else:
                # Fallback: try to read from current gradients (may be 0 if already zeroed)
                for param in mlp.parameters():
                    if param.requires_grad:
                        if param.grad is not None:
                            total_grad_norm += param.grad.norm().item() ** 2
                            has_grad = True
            
            # Always compute weight norm from current weights
            for param in mlp.parameters():
                if param.requires_grad:
                    total_params += param.numel()
                    total_norm += param.data.norm().item() ** 2
            
            stats[op_name] = {
                'weight_norm': total_norm ** 0.5,
                'grad_norm': total_grad_norm if has_grad else 0.0,
                'n_params': total_params,
                'has_grad': has_grad,
            }
        return stats
    
    def _compute_operation_similarity(self) -> Dict[Tuple[str, str], float]:
        """
        Compute pairwise cosine similarity between operation MLPs.
        
        This tells us if the MLPs are learning distinct transformations (low similarity)
        or collapsing to the same function (high similarity).
        
        Compares multiply/add/subtract/divide - all have identical architectures now.
        (divide_mlp was changed from 4*d_model to d_model input in memory optimization)
        
        Returns:
            Dict mapping (op1, op2) -> cosine_similarity
        """
        # Extract flattened weight vectors for same-architecture MLPs
        def get_flat_weights(mlp: nn.Module) -> torch.Tensor:
            """Flatten all parameters into a single vector."""
            weights = []
            for param in mlp.parameters():
                weights.append(param.data.view(-1))
            return torch.cat(weights)
        
        # Compare same-architecture MLPs (all now have d_model -> d_model/2 -> d_model)
        same_arch_ops = [
            ('multiply', self.multiply_mlp),
            ('add', self.add_mlp),
            ('subtract', self.subtract_mlp),
            ('divide', self.divide_mlp),
        ]
        
        # Extract weight vectors
        weight_vectors = {}
        for op_name, mlp in same_arch_ops:
            weight_vectors[op_name] = get_flat_weights(mlp)
        
        # Compute pairwise cosine similarity
        similarities = {}
        op_names = list(weight_vectors.keys())
        for i in range(len(op_names)):
            for j in range(i + 1, len(op_names)):
                op1, op2 = op_names[i], op_names[j]
                v1, v2 = weight_vectors[op1], weight_vectors[op2]
                
                # Cosine similarity: dot(v1, v2) / (norm(v1) * norm(v2))
                cos_sim = F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()
                similarities[(op1, op2)] = cos_sim
        
        return similarities
    
    def _track_weight_learning(self) -> Dict[str, float]:
        """Track weight changes since last epoch. Returns delta per operation."""
        current_stats = self._compute_weight_stats()
        
        # Save snapshot for this epoch
        self._weight_snapshots[self.current_epoch] = {
            op: stats['weight_norm'] for op, stats in current_stats.items()
        }
        
        # Compute deltas from previous epoch
        deltas = {}
        if self.current_epoch > 0 and (self.current_epoch - 1) in self._weight_snapshots:
            prev_snapshot = self._weight_snapshots[self.current_epoch - 1]
            for op, stats in current_stats.items():
                prev_norm = prev_snapshot.get(op, stats['weight_norm'])
                delta = abs(stats['weight_norm'] - prev_norm)
                deltas[op] = delta
                
                # Track history
                if op not in self._weight_deltas:
                    self._weight_deltas[op] = []
                self._weight_deltas[op].append(delta)
        
        return deltas
    
    def log_epoch_summary(self):
        """
        Log detailed epoch summary showing what relationships are being learned.
        Call this at the END of each epoch.
        """
        # Reset batch counter for next epoch
        self._batch_counter = 0
        
        # CRITICAL: Record epoch history for causal importance calculation
        # This must be called every epoch, not just during pruning
        active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        if self.col_marginal_losses:
            self._record_epoch_history(self.current_epoch, active_pairs, self.col_marginal_losses)
        
        logger.info("")
        logger.info("=" * 100)
        logger.info(f"🔗 DYNAMIC RELATIONSHIP EXTRACTOR - EPOCH {self.current_epoch} SUMMARY")
        logger.info("=" * 100)
        
        # LEARNING CHECK: Are the operation MLPs learning?
        # CRITICAL: Compute stats BEFORE resetting stored gradient norms (they're needed for logging)
        weight_stats = self._compute_weight_stats()
        weight_deltas = self._track_weight_learning()
        
        logger.info(f"")
        logger.info(f"📈 Operation MLP Learning Status:")
        logger.info(f"   {'Operation':<12} {'Weights':>10} {'Grad Norm':>12} {'Δ (epoch)':>12} {'Learning?':>12}")
        logger.info(f"   {'-'*12} {'-'*10} {'-'*12} {'-'*12} {'-'*12}")
        
        any_learning = False
        for op, stats in weight_stats.items():
            delta = weight_deltas.get(op, 0.0)
            is_learning = delta > 1e-6 or stats['grad_norm'] > 1e-6
            any_learning = any_learning or is_learning
            learning_str = "✓ YES" if is_learning else "✗ NO"
            
            # Format grad_norm in scientific notation if very small (to avoid showing 0.000000)
            grad_norm = stats['grad_norm']
            if grad_norm > 0 and grad_norm < 1e-3:
                grad_norm_str = f"{grad_norm:.3e}"
            else:
                grad_norm_str = f"{grad_norm:.6f}"
            
            logger.info(f"   {op:<12} {stats['weight_norm']:>10.4f} {grad_norm_str:>12} {delta:>12.6f} {learning_str:>12}")
        
        if not any_learning:
            logger.warning(f"   ⚠️  NO RELATIONSHIP OPERATIONS ARE LEARNING! Check gradient flow.")
        else:
            logger.info(f"   ✅ Relationships are actively learning")
        
        # OPERATION DIFFERENTIATION CHECK: Are MLPs learning distinct functions?
        similarities = self._compute_operation_similarity()
        if similarities:
            logger.info(f"")
            logger.info(f"🔀 Operation MLP Differentiation (cosine similarity: -1=opposite, 0=orthogonal, +1=same):")
            
            # Determine health status using absolute values (closer to 0 = more distinct)
            max_abs_sim = max(abs(s) for s in similarities.values())
            avg_sim = sum(similarities.values()) / len(similarities)
            
            for (op1, op2), sim in sorted(similarities.items()):
                # Color-code based on absolute similarity (closer to 0 = more distinct)
                abs_sim = abs(sim)
                if abs_sim > 0.95:
                    status = "⚠️  COLLAPSED"  # Almost identical/opposite - bad
                elif abs_sim > 0.80:
                    status = "⚡ similar"     # Concerning
                elif abs_sim > 0.50:
                    status = "✓ distinct"    # Good differentiation
                else:
                    status = "✓✓ very distinct"  # Excellent - near orthogonal
                
                logger.info(f"   {op1:>10} vs {op2:<10}: {sim:>6.3f} {status}")
            
            # Summary based on absolute similarity
            if max_abs_sim > 0.95:
                logger.warning(f"   ⚠️  Operations may be collapsing to same function (max |similarity|={max_abs_sim:.3f})")
            elif max_abs_sim > 0.80:
                logger.info(f"   ⚡ Operations are similar but differentiating (max |sim|={max_abs_sim:.3f})")
            else:
                logger.info(f"   ✅ Operations are learning distinct transformations (avg={avg_sim:.3f})")
        
        # 1. COLUMN MARGINAL LOSSES (which columns are hard to predict?)
        if self.col_marginal_losses:
            logger.info(f"📊 Column Marginal Losses (higher = harder to predict = more important):")
            sorted_cols = sorted(self.col_marginal_losses.items(), key=lambda x: x[1], reverse=True)
            for i, (col, loss) in enumerate(sorted_cols[:15], 1):
                logger.info(f"   {i:2d}. {col:<30}: {loss:.4f}")
            logger.info("")
        
        # ============================================================================
        # COVERAGE STATS: Track relationship learning progress
        # ============================================================================
        # Compute E, K_exploit, K_explore for this epoch
        log2_N = np.log2(max(2, self.n_cols))
        E = max(1, min(32, int(np.ceil(log2_N))))
        K_exploit = E
        K_explore = E
        
        # Count active directed edges (average per step this epoch)
        if self._epoch_active_edges:
            avg_active_edges_per_step = np.mean(self._epoch_active_edges)
            active_directed_count = int(avg_active_edges_per_step)
        else:
            # Fallback: estimate from active pairs (each undirected pair = 2 directed)
            active_directed_count = len(active_pairs) * 2
        
        # Count columns with baseline available (NULL baseline)
        # Baseline is per-column, not per-pair
        cols_with_baseline = 0
        for col_name in self.col_names:
            if col_name in self._null_baseline_ema and self._null_baseline_ema[col_name] is not None:
                cols_with_baseline += 1
        
        # Count pairs eligible for NULL-source lift (both columns have baseline)
        pairs_eligible_for_null = 0
        for pair in active_pairs:
            i, j = pair
            col_i = self.col_names[i] if i < len(self.col_names) else None
            col_j = self.col_names[j] if j < len(self.col_names) else None
            has_baseline_i = col_i and col_i in self._null_baseline_ema and self._null_baseline_ema[col_i] is not None
            has_baseline_j = col_j and col_j in self._null_baseline_ema and self._null_baseline_ema[col_j] is not None
            if has_baseline_i or has_baseline_j:
                pairs_eligible_for_null += 1
        
        # Collect n_ij statistics (directed edges)
        n_ij_values = []
        for directed_pair in self._pair_stats.keys():
            stats = self._pair_stats[directed_pair]
            n_ij = stats.get('n', 0)
            if n_ij > 0:
                n_ij_values.append(n_ij)
        
        # Compute n_ij statistics
        max_n_ij = max(n_ij_values) if n_ij_values else 0
        mean_n_ij = np.mean(n_ij_values) if n_ij_values else 0.0
        p95_n_ij = np.percentile(n_ij_values, 95) if n_ij_values else 0.0
        
        # Compute n_total statistics (n_ij + n_ji) for undirected pairs - this is what's used for ranking
        n_total_values = []
        for pair in active_pairs:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            n_ij = stats_ij.get('n', 0)
            n_ji = stats_ji.get('n', 0)
            n_total = n_ij + n_ji
            if n_total > 0:
                n_total_values.append(n_total)
        
        max_n_total = max(n_total_values) if n_total_values else 0
        
        # ============================================================================
        # ADAPTIVE THRESHOLDS: Adjust based on actual observed support statistics
        # ============================================================================
        # Use percentile-based approach: set thresholds so that a reasonable fraction
        # of pairs with actual observations can be rankable
        original_min_support_rank = self.MIN_SUPPORT_RANK
        if n_total_values and len(n_total_values) >= 10:  # Need enough data to compute percentiles
            # Compute percentiles of actual observed support
            p50_n_total = np.percentile(n_total_values, 50)
            p75_n_total = np.percentile(n_total_values, 75)
            
            # Adaptive MIN_SUPPORT_RANK: use 50th percentile so ~50% of observed pairs can be rankable
            # But ensure it's not too low (at least 2x tracking threshold) or too high (not above 75th percentile)
            adaptive_rank = max(int(p50_n_total), self.MIN_SUPPORT_TRACK * 2)
            adaptive_rank = min(adaptive_rank, int(p75_n_total))  # Don't go above 75th percentile
            adaptive_rank = max(10, min(adaptive_rank, self._initial_min_support_rank))  # Clamp to [10, initial_value]
            
            if adaptive_rank < self.MIN_SUPPORT_RANK:
                self.MIN_SUPPORT_RANK = adaptive_rank
                logger.info(f"   ⚠️  Adaptive MIN_SUPPORT_RANK: {original_min_support_rank} → {self.MIN_SUPPORT_RANK} "
                          f"(p50_n_total={p50_n_total:.1f}, p75_n_total={p75_n_total:.1f}, max_n_total={max_n_total})")
        elif max_n_total > 0 and max_n_total < self.MIN_SUPPORT_RANK * 0.5:
            # Fallback: if we don't have enough data for percentiles, use max-based adjustment
            # Actual support is less than 50% of expected - lower threshold adaptively
            adaptive_rank = max(int(max_n_total * 1.5), self.MIN_SUPPORT_TRACK * 2)
            adaptive_rank = max(10, min(adaptive_rank, self.MIN_SUPPORT_RANK))
            if adaptive_rank < self.MIN_SUPPORT_RANK:
                self.MIN_SUPPORT_RANK = adaptive_rank
                logger.info(f"   ⚠️  Adaptive MIN_SUPPORT_RANK (fallback): {original_min_support_rank} → {self.MIN_SUPPORT_RANK} "
                          f"(max_n_total={max_n_total}, max_n_ij={max_n_ij})")
        
        # Count pairs with lift computed (has lift_ema in _pair_stats) - UNDIRECTED
        pairs_with_lift_undirected = 0
        for pair in active_pairs:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            lift_ij = stats_ij.get('lift_ema')
            lift_ji = stats_ji.get('lift_ema')
            if (lift_ij is not None and math.isfinite(lift_ij)) or (lift_ji is not None and math.isfinite(lift_ji)):
                pairs_with_lift_undirected += 1
        
        # Count directed edges with lift computed
        directed_edges_with_lift = 0
        for directed_pair, stats in self._pair_stats.items():
            lift_ema = stats.get('lift_ema')
            if lift_ema is not None and math.isfinite(lift_ema):
                directed_edges_with_lift += 1
        
        # Count rankable pairs (n >= MIN_SUPPORT_RANK && has null source) - UNDIRECTED
        # CRITICAL: For consistency with candidate selection, use n_total = n_ij + n_ji
        # This matches _compute_pair_scores which uses n_total for ranking
        rankable_pairs_undirected = 0
        for pair in active_pairs:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            n_ij = stats_ij.get('n', 0)
            n_ji = stats_ji.get('n', 0)
            n_total = n_ij + n_ji  # Sum of both directions (consistent with _compute_pair_scores)
            
            # Check if has null baseline source (either direction)
            source_counts_ij = stats_ij.get('source_counts', {})
            source_counts_ji = stats_ji.get('source_counts', {})
            has_null_ij = source_counts_ij.get('null', 0) > 0
            has_null_ji = source_counts_ji.get('null', 0) > 0
            
            # Rankable if: n_total >= MIN_SUPPORT_RANK AND has null baseline in at least one direction
            # Note: n_total can be ≥ MIN_SUPPORT_RANK even if individual n_ij < MIN_SUPPORT_RANK
            # This is consistent with how _compute_pair_scores computes rankability
            if n_total >= self.MIN_SUPPORT_RANK and (has_null_ij or has_null_ji):
                rankable_pairs_undirected += 1
        
        # Count rankable directed edges (n >= MIN_SUPPORT_RANK && has null source)
        rankable_directed_edges = 0
        for directed_pair, stats in self._pair_stats.items():
            n_ij = stats.get('n', 0)
            source_counts = stats.get('source_counts', {})
            has_null = source_counts.get('null', 0) > 0
            if n_ij >= self.MIN_SUPPORT_RANK and has_null:
                rankable_directed_edges += 1
        
        # Compute dropout stats
        dropout_stats = self._epoch_dropout_stats
        if dropout_stats['steps_with_dropout'] > 0:
            avg_edges_before = dropout_stats['total_edges_before'] / dropout_stats['steps_with_dropout']
            avg_edges_after = dropout_stats['total_edges_after'] / dropout_stats['steps_with_dropout']
            avg_dropped = dropout_stats['total_dropped'] / dropout_stats['steps_with_dropout']
            # Correct formula: drop_rate = (before - after) / before, then convert to percent
            observed_drop_rate = ((dropout_stats['total_edges_before'] - dropout_stats['total_edges_after']) / dropout_stats['total_edges_before']) if dropout_stats['total_edges_before'] > 0 else 0.0
        else:
            avg_edges_before = avg_edges_after = avg_dropped = 0
            observed_drop_rate = 0.0
        
        # Total possible directed edges
        total_possible_directed = self.n_cols * (self.n_cols - 1)
        total_possible_undirected = len(self.all_pairs)
        
        logger.info(f"📈 Relationship Coverage Stats:")
        logger.info(f"   Active directed edges (avg per step): {active_directed_count}")
        logger.info(f"   Columns with baseline available: {cols_with_baseline}/{len(self.col_names)} ({cols_with_baseline/len(self.col_names)*100:.1f}%)")
        logger.info(f"   Pairs eligible for NULL-source lift: {pairs_eligible_for_null}/{len(active_pairs)} ({pairs_eligible_for_null/len(active_pairs)*100:.1f}%)")
        logger.info(f"")
        logger.info(f"   n_ij statistics (directed edges): max={max_n_ij}, p95={p95_n_ij:.1f}, mean={mean_n_ij:.1f}")
        logger.info(f"")
        logger.info(f"   DIRECTED EDGES (i→j):")
        logger.info(f"      Total possible: {total_possible_directed}")
        logger.info(f"      With lift computed: {directed_edges_with_lift}/{total_possible_directed} ({directed_edges_with_lift/total_possible_directed*100:.1f}%)")
        logger.info(f"      Rankable (n≥{self.MIN_SUPPORT_RANK} && null_source): {rankable_directed_edges}/{total_possible_directed} ({rankable_directed_edges/total_possible_directed*100:.1f}%)")
        logger.info(f"")
        logger.info(f"   UNDIRECTED PAIRS (i,j) collapsed:")
        logger.info(f"      Total possible: {total_possible_undirected}")
        logger.info(f"      With lift computed (either direction): {pairs_with_lift_undirected}/{total_possible_undirected} ({pairs_with_lift_undirected/total_possible_undirected*100:.1f}%)")
        logger.info(f"      Rankable (n_total≥{self.MIN_SUPPORT_RANK} && null_source): {rankable_pairs_undirected}/{total_possible_undirected} ({rankable_pairs_undirected/total_possible_undirected*100:.1f}%)")
        logger.info(f"         Note: n_total = n_ij + n_ji (sum of both directions), so pairs can be rankable even if max(n_ij) < MIN_SUPPORT_RANK")
        logger.info(f"")
        logger.info(f"   MIN_SUPPORT_RANK: {self.MIN_SUPPORT_RANK}")
        logger.info(f"   Selection params: E={E}, K_exploit={K_exploit}, K_explore={K_explore}")
        if self.edge_dropout_prob > 0:
            logger.info(f"   Edge dropout: p={self.edge_dropout_prob:.1%}, observed={observed_drop_rate:.1%} "
                       f"(avg {avg_edges_before:.1f} → {avg_edges_after:.1f} edges/step)")
        else:
            logger.info(f"   Edge dropout: disabled")
        logger.info("")
        
        # Reset stats for next epoch
        self._epoch_dropout_stats = {
            'total_edges_before': 0,
            'total_edges_after': 0,
            'total_dropped': 0,
            'steps_with_dropout': 0,
        }
        self._epoch_active_edges = []
        
        # 2. RELATIONSHIP IMPORTANCE (using lift-based causal importance)
        # UNIFIED: Always use lift-based scores, not old loss-based heuristic
        importance_scores = self._compute_causal_importance(active_pairs)
        
        # DEBUG: Check for saturation issue
        importance_values = list(importance_scores.values())
        if importance_values:
            unique_values = set(importance_values)
            all_same = len(unique_values) == 1
            min_imp = min(importance_values)
            max_imp = max(importance_values)
            mean_imp = np.mean(importance_values)
            std_imp = np.std(importance_values) if len(importance_values) > 1 else 0.0
            
            if all_same or (max_imp - min_imp < 1e-6):
                logger.warning(f"⚠️  IMPORTANCE SCORE SATURATION DETECTED!")
                logger.warning(f"   All scores are identical: {importance_values[0]:.6f}")
                logger.warning(f"   This indicates a bug in importance calculation or normalization")
            else:
                logger.debug(f"📊 Importance score stats: mean={mean_imp:.6f}, std={std_imp:.6f}, range=[{min_imp:.6f}, {max_imp:.6f}]")
        
        # Sort by importance DESCENDING (higher = more important)
        sorted_pairs = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        total_pairs = len(sorted_pairs)
        active_pairs_count = total_pairs - len(self.disabled_pairs)
        
        logger.info(f"🏆 Top 20 Most Important Relationships (by lift-based importance; Δ = |loss_i - loss_j| shows easy↔hard pairing):")
        logger.info(f"   Note: Relationships are directional (i→j). Display shows dominant direction or both if similar.")
        # Show detailed debug for first pair in top list
        if sorted_pairs:
            (i_first, j_first), importance_first = sorted_pairs[0]
            col_i_first = self.col_names[i_first] if i_first < len(self.col_names) else f"col_{i_first}"
            col_j_first = self.col_names[j_first] if j_first < len(self.col_names) else f"col_{j_first}"
            loss_i_first = self.col_marginal_losses.get(col_i_first, 0.0)
            loss_j_first = self.col_marginal_losses.get(col_j_first, 0.0)
            abs_diff_first = abs(loss_i_first - loss_j_first)
            
            # Get breakdown from causal scorer if available
            if hasattr(self, 'causal_scorer'):
                try:
                    _, breakdown = self.causal_scorer.compute_importance((i_first, j_first))
                    logger.info(f"   🔍 DEBUG (first pair):")
                    logger.info(f"      pair=({col_i_first},{col_j_first})")
                    logger.info(f"      loss_i={loss_i_first:.4f} loss_j={loss_j_first:.4f} abs_diff={abs_diff_first:.4f}")
                    logger.info(f"      raw_importance={importance_first:.6f}")
                    logger.info(f"      breakdown: lcb_score={breakdown.get('lcb_score', 'N/A'):.6f}, "
                              f"lift_ij_mean={breakdown.get('lift_ij_mean', 'N/A'):.6f}, "
                              f"lift_ji_mean={breakdown.get('lift_ji_mean', 'N/A'):.6f}")
                except Exception as e:
                    logger.debug(f"   Could not get breakdown: {e}")
        
        # Build table rows
        table_rows = []
        for rank, ((i, j), importance) in enumerate(sorted_pairs[:20], 1):
            col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
            col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
            loss_i = self.col_marginal_losses.get(col_i, 0.0)
            loss_j = self.col_marginal_losses.get(col_j, 0.0)
            # Compute actual Δ = |loss_i - loss_j| (easy↔hard pairing difference)
            delta_loss = abs(loss_i - loss_j)
            is_active = (i, j) not in self.disabled_pairs
            status = "✓" if is_active else "✗"
            
            # Get directional lift information
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            lift_ij = stats_ij.get('lift_ema', 0.0) if stats_ij.get('lift_ema') is not None else 0.0
            lift_ji = stats_ji.get('lift_ema', 0.0) if stats_ji.get('lift_ema') is not None else 0.0
            
            # Format relationship (show dominant direction or bidirectional)
            # Store columns separately for table display
            if abs(lift_ij - lift_ji) > 0.01:  # Significant difference
                if lift_ij > lift_ji:
                    # i→j is stronger
                    col1 = col_i
                    col2 = col_j
                    direction = "→"
                else:
                    # j→i is stronger
                    col1 = col_j
                    col2 = col_i
                    direction = "→"
                lift_display = f"i→j={lift_ij:.4f}, j→i={lift_ji:.4f}"
            else:
                # Both directions similar - show as bidirectional
                col1 = col_i
                col2 = col_j
                direction = "↔"
                lift_display = f"i→j={lift_ij:.4f}, j→i={lift_ji:.4f}"
            
            table_rows.append({
                'rank': rank,
                'col1': col1,
                'col2': col2,
                'direction': direction,
                'delta': delta_loss,
                'importance': importance,
                'lift': lift_display,
                'loss_i': loss_i,
                'loss_j': loss_j,
                'status': status
            })
        
        # Print table
        if table_rows:
            # Calculate column widths
            max_col1_len = max(len(row['col1']) for row in table_rows)
            max_col1_len = max(max_col1_len, len('Col 1'))
            max_col2_len = max(len(row['col2']) for row in table_rows)
            max_col2_len = max(max_col2_len, len('Col 2'))
            max_lift_len = max(len(row['lift']) for row in table_rows)
            max_lift_len = max(max_lift_len, len('Lift (i→j, j→i)'))
            
            # Header - 4 spaces between columns
            header = f"   {'Rank':<6}    {'Col 1':<{max_col1_len}}    {'Col 2':<{max_col2_len}}    {'Δ':<9}    {'Imp':<9}    {'Lift (i→j, j→i)':<{max_lift_len}}    {'Loss (i vs j)':<22}    {'Status':<8}"
            logger.info(header)
            # Separator line (same length as header, but with dashes)
            separator_len = len(header) - 3  # Subtract leading "   "
            logger.info("   " + "-" * separator_len)
            
            # Rows - 4 spaces between columns
            for row in table_rows:
                loss_str = f"{row['loss_i']:.4f} vs {row['loss_j']:.4f}"
                logger.info(f"   {row['rank']:<6}    {row['col1']:<{max_col1_len}}    {row['col2']:<{max_col2_len}}    {row['delta']:<9.4f}    {row['importance']:<9.4f}    {row['lift']:<{max_lift_len}}    {loss_str:<22}    {row['status']:<8}")
        
        # Bottom 20 relationships (lowest importance = both columns at similar difficulty = prune candidates)
        logger.info(f"")
        logger.info(f"📉 Bottom 20 Least Important Relationships (by lift-based importance; low Δ = same-tier pairing):")
        logger.info(f"   Note: Relationships are directional (i→j). Display shows dominant direction or both if similar.")
        # Show detailed debug for first pair in bottom list
        if sorted_pairs:
            (i_last, j_last), importance_last = sorted_pairs[-1]
            col_i_last = self.col_names[i_last] if i_last < len(self.col_names) else f"col_{i_last}"
            col_j_last = self.col_names[j_last] if j_last < len(self.col_names) else f"col_{j_last}"
            loss_i_last = self.col_marginal_losses.get(col_i_last, 0.0)
            loss_j_last = self.col_marginal_losses.get(col_j_last, 0.0)
            abs_diff_last = abs(loss_i_last - loss_j_last)
            
            # Get breakdown from causal scorer if available
            if hasattr(self, 'causal_scorer'):
                try:
                    _, breakdown = self.causal_scorer.compute_importance((i_last, j_last))
                    logger.info(f"   🔍 DEBUG (last pair):")
                    logger.info(f"      pair=({col_i_last},{col_j_last})")
                    logger.info(f"      loss_i={loss_i_last:.4f} loss_j={loss_j_last:.4f} abs_diff={abs_diff_last:.4f}")
                    logger.info(f"      raw_importance={importance_last:.6f}")
                    logger.info(f"      breakdown: lcb_score={breakdown.get('lcb_score', 'N/A'):.6f}, "
                              f"lift_ij_mean={breakdown.get('lift_ij_mean', 'N/A'):.6f}, "
                              f"lift_ji_mean={breakdown.get('lift_ji_mean', 'N/A'):.6f}")
                except Exception as e:
                    logger.debug(f"   Could not get breakdown: {e}")
        
        # Build table rows
        table_rows = []
        for rank, ((i, j), importance) in enumerate(reversed(sorted_pairs[-20:]), 1):
            col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
            col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
            loss_i = self.col_marginal_losses.get(col_i, 0.0)
            loss_j = self.col_marginal_losses.get(col_j, 0.0)
            # Compute actual Δ = |loss_i - loss_j| (easy↔hard pairing difference)
            delta_loss = abs(loss_i - loss_j)
            is_active = (i, j) not in self.disabled_pairs
            status = "✓" if is_active else "✗"
            
            # Get directional lift information
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            lift_ij = stats_ij.get('lift_ema', 0.0) if stats_ij.get('lift_ema') is not None else 0.0
            lift_ji = stats_ji.get('lift_ema', 0.0) if stats_ji.get('lift_ema') is not None else 0.0
            
            # Format relationship (show dominant direction or bidirectional)
            # Store columns separately for table display
            if abs(lift_ij - lift_ji) > 0.01:  # Significant difference
                if lift_ij > lift_ji:
                    # i→j is stronger
                    col1 = col_i
                    col2 = col_j
                    direction = "→"
                else:
                    # j→i is stronger
                    col1 = col_j
                    col2 = col_i
                    direction = "→"
                lift_display = f"i→j={lift_ij:.4f}, j→i={lift_ji:.4f}"
            else:
                # Both directions similar - show as bidirectional
                col1 = col_i
                col2 = col_j
                direction = "↔"
                lift_display = f"i→j={lift_ij:.4f}, j→i={lift_ji:.4f}"
            
            table_rows.append({
                'rank': rank,
                'col1': col1,
                'col2': col2,
                'direction': direction,
                'delta': delta_loss,
                'importance': importance,
                'lift': lift_display,
                'loss_i': loss_i,
                'loss_j': loss_j,
                'status': status
            })
        
        # Print table
        if table_rows:
            # Calculate column widths
            max_col1_len = max(len(row['col1']) for row in table_rows)
            max_col1_len = max(max_col1_len, len('Col 1'))
            max_col2_len = max(len(row['col2']) for row in table_rows)
            max_col2_len = max(max_col2_len, len('Col 2'))
            max_lift_len = max(len(row['lift']) for row in table_rows)
            max_lift_len = max(max_lift_len, len('Lift (i→j, j→i)'))
            
            # Header - 4 spaces between columns
            header = f"   {'Rank':<6}    {'Col 1':<{max_col1_len}}    {'Col 2':<{max_col2_len}}    {'Δ':<9}    {'Imp':<9}    {'Lift (i→j, j→i)':<{max_lift_len}}    {'Loss (i vs j)':<22}    {'Status':<8}"
            logger.info(header)
            # Separator line (same length as header, but with dashes)
            separator_len = len(header) - 3  # Subtract leading "   "
            logger.info("   " + "-" * separator_len)
            
            # Rows - 4 spaces between columns
            for row in table_rows:
                loss_str = f"{row['loss_i']:.4f} vs {row['loss_j']:.4f}"
                logger.info(f"   {row['rank']:<6}    {row['col1']:<{max_col1_len}}    {row['col2']:<{max_col2_len}}    {row['delta']:<9.4f}    {row['importance']:<9.4f}    {row['lift']:<{max_lift_len}}    {loss_str:<22}    {row['status']:<8}")
        
        # Pruning status
        logger.info(f"")
        if self.progressive_pruning:
            total_pairs = len(self.all_pairs)
            active_pairs = total_pairs - len(self.disabled_pairs)
            target_remaining = int(total_pairs * self.top_k_fraction)
            
            if self.current_epoch < self.exploration_epochs:
                epochs_until_pruning = self.exploration_epochs - self.current_epoch
                logger.info(f"")
                logger.info(f"⏳ Exploration Phase: {epochs_until_pruning} epochs until progressive pruning starts")
            else:
                logger.info(f"")
                logger.info(f"🔪 Progressive Pruning Active:")
                logger.info(f"   Active pairs: {active_pairs}/{total_pairs} ({100*active_pairs/total_pairs:.1f}%)")
                logger.info(f"   Disabled: {len(self.disabled_pairs)} pairs")
                logger.info(f"   Target: {target_remaining} pairs ({self.top_k_fraction*100:.0f}%)")
                if active_pairs > target_remaining:
                    remaining_to_disable = active_pairs - target_remaining
                    logger.info(f"   Still need to disable: {remaining_to_disable} pairs")
                else:
                    logger.info(f"   ✅ Target reached!")
        elif self.pruned_pairs_per_column is None:
            epochs_until_pruning = max(0, self.exploration_epochs - self.current_epoch)
            logger.info(f"")
            logger.info(f"⏳ Exploration Phase: {epochs_until_pruning} epochs until pruning")
        else:
            # Show pruning statistics (old hard pruning method)
            total_active_pairs = sum(len(partners) for partners in self.pruned_pairs_per_column.values())
            pruning_ratio = total_active_pairs / total_pairs if total_pairs > 0 else 0
            logger.info(f"")
            logger.info(f"✂️  Pruning Active: {total_active_pairs}/{total_pairs} pairs ({100*pruning_ratio:.1f}%)")
        
        # Reset stored gradient norms for next epoch (AFTER logging, so we can use them above)
        # They will be captured during training in the next epoch
        self._stored_grad_norms = {}
        
        logger.info("=" * 100)
        logger.info("")
    
    def log_exploration_progress(self):
        """
        DEPRECATED: This method is kept for backward compatibility but now uses
        the unified lift-based causal importance system instead of the old
        loss-based heuristic.
        
        The unified system is always active (from epoch 0), so this is just
        a logging wrapper that shows the same information as log_epoch_summary().
        """
        if not self.training:
            return
        
        logger.info("")
        logger.info(f"🔍 RELATIONSHIP EXPLORATION (epoch {self.current_epoch})")
        
        # Use unified lift-based causal importance (same as normal phase)
        active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        if not active_pairs:
            logger.info("   ⏳ No active pairs to analyze...")
            return
        
        # Calculate importance scores using lift-based system
        importance_scores = self._compute_causal_importance(active_pairs)
        
        # Calculate statistics
        importance_values = list(importance_scores.values())
        if len(importance_values) == 0:
            mean_importance = 0.0
            std_importance = 0.0
            max_importance = 0.0
            min_importance = 0.0
        else:
            mean_importance = np.mean(importance_values)
            std_importance = np.std(importance_values) if len(importance_values) > 1 else 0.0
            max_importance = np.max(importance_values)
            min_importance = np.min(importance_values)
        
        active_pairs_count = len(active_pairs)
        
        logger.info(f"   Lift-based importance (causal lift from NULL baseline):")
        logger.info(f"   Mean: {mean_importance:.4f} ± {std_importance:.4f}")
        logger.info(f"   Range: [{min_importance:.4f}, {max_importance:.4f}]")
        logger.info(f"   Active pairs: {active_pairs_count}/{len(self.all_pairs)}")
        
        # Top 5 pairs by importance
        sorted_pairs = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"   Top 5 pairs:")
        for (i, j), importance in sorted_pairs[:5]:
            col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
            col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
            logger.info(f"      {col_i:<20} ↔ {col_j:<20}: lift={importance:.4f}")
    
    def log_operation_statistics(self):
        """Log which operations are most effective."""
        logger.info("")
        logger.info("📊 OPERATION EFFECTIVENESS:")
        
        total = sum(self.operation_contributions.values())
        if total == 0:
            logger.info("   ⚠️  No operation contributions tracked yet")
            return
        
        for op, contrib in sorted(self.operation_contributions.items(), key=lambda x: x[1], reverse=True):
            pct = (contrib / total * 100) if total > 0 else 0
            logger.info(f"   {op:12s}: {contrib:.6f} ({pct:.1f}%)")
    
    def log_column_importance(self):
        """Log which columns have the most important relationships."""
        # Calculate total contribution for each column
        col_importance = {i: 0.0 for i in range(self.n_cols)}
        
        for (i, j), contrib in self.pair_contributions.items():
            col_importance[i] += contrib
            col_importance[j] += contrib
        
        # Sort by importance
        sorted_cols = sorted(
            col_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        logger.info("")
        logger.info("📊 COLUMN IMPORTANCE (by relationship strength):")
        logger.info(f"   {'Rank':<6} {'Column':<30} {'Total Contribution':<20} {'Rel %'}")
        logger.info(f"   {'-'*6} {'-'*30} {'-'*20} {'-'*6}")
        
        total_contrib = sum(col_importance.values())
        for rank, (col_idx, importance) in enumerate(sorted_cols[:20], 1):  # Top 20
            rel_pct = (importance / total_contrib * 100) if total_contrib > 0 else 0
            col_name = self.col_names[col_idx]
            # Truncate long column names
            if len(col_name) > 30:
                col_name = col_name[:27] + "..."
            logger.info(f"   {rank:<6} {col_name:<30} {importance:<20.6f} {rel_pct:>5.1f}%")
    
    def log_pruning_analysis(self):
        """Detailed analysis of pruning decisions."""
        if self.pruned_pairs_per_column is None:
            return
        
        # Analyze kept vs dropped pairs
        kept_pairs = set(self._pruned_pairs_list)
        dropped_pairs = set(self.all_pairs) - kept_pairs
        
        kept_contribs = [self.pair_contributions[p] for p in kept_pairs]
        dropped_contribs = [self.pair_contributions[p] for p in dropped_pairs]
        
        logger.info("")
        logger.info("📊 PRUNING DECISION ANALYSIS:")
        logger.info(f"   Kept pairs ({len(kept_pairs)}):")
        if kept_contribs:
            logger.info(f"      Mean contribution: {np.mean(kept_contribs):.6f}")
            logger.info(f"      Min contribution:  {np.min(kept_contribs):.6f}")
            logger.info(f"      Max contribution:  {np.max(kept_contribs):.6f}")
        else:
            logger.info(f"      (no kept pairs)")
        
        if dropped_contribs:
            logger.info(f"   Dropped pairs ({len(dropped_pairs)}):")
            logger.info(f"      Mean contribution: {np.mean(dropped_contribs):.6f}")
            logger.info(f"      Min contribution:  {np.min(dropped_contribs):.6f}")
            logger.info(f"      Max contribution:  {np.max(dropped_contribs):.6f}")
        
        # Calculate effectiveness of pruning
        kept_contrib_sum = sum(kept_contribs)
        total_contrib_sum = sum(self.pair_contributions.values())
        retained_signal = (kept_contrib_sum / total_contrib_sum * 100) if total_contrib_sum > 0 else 0
        
        logger.info(f"   📈 Signal retention: {retained_signal:.1f}% of total contribution")
        logger.info(f"   ⚡ Efficiency gain: {len(dropped_pairs) / len(self.all_pairs) * 100:.1f}% fewer pairs")
    
    def log_relationship_stability(self):
        """Analyze how stable relationships are over epochs."""
        if len(self.contribution_history) < 2:
            logger.info("   ⚠️  Need at least 2 epochs to analyze stability")
            return
        
        # Calculate correlation between consecutive epochs
        correlations = []
        for i in range(1, len(self.contribution_history)):
            prev = self.contribution_history[i-1]
            curr = self.contribution_history[i]
            
            # Pearson correlation
            prev_vals = [prev[p] for p in self.all_pairs]
            curr_vals = [curr[p] for p in self.all_pairs]
            
            # Handle edge cases: empty arrays or zero variance
            if len(prev_vals) == 0 or len(curr_vals) == 0:
                corr = 0.0
            elif len(prev_vals) == 1 or len(curr_vals) == 1:
                corr = 0.0  # Can't compute correlation with single value
            elif np.std(prev_vals) == 0 or np.std(curr_vals) == 0:
                corr = 0.0
            else:
                corr = np.corrcoef(prev_vals, curr_vals)[0, 1]
                if np.isnan(corr):
                    corr = 0.0
            correlations.append(corr)
        
        logger.info("")
        logger.info("📊 RELATIONSHIP STABILITY:")
        if correlations:
            logger.info(f"   Mean epoch-to-epoch correlation: {np.mean(correlations):.3f}")
        else:
            logger.info(f"   Mean epoch-to-epoch correlation: N/A (need at least 2 epochs)")
        logger.info(f"   Stability trend:")
        for epoch, corr in enumerate(correlations, 2):
            logger.info(f"      Epoch {epoch-1} → {epoch}: {corr:.3f}")
    
    def prune_to_top_relationships(self):
        """
        Prune to top k% relationships per column after exploration phase.
        
        Each column keeps only its top k% partners (by contribution).
        This is done PER COLUMN, so different columns can focus on different partners.
        """
        # Log pre-pruning analysis
        self.log_relationship_stability()
        self.log_operation_statistics()
        self.log_column_importance()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🔪 PRUNING RELATIONSHIPS (epoch {self.current_epoch})")
        logger.info("=" * 80)
        
        # Calculate top_k per column
        top_k = max(1, int(self.n_cols * self.top_k_fraction))
        logger.info(f"   Each column will keep top {top_k} partners ({self.top_k_fraction*100:.0f}%)")
        
        # Build dict: col_idx -> list of (partner_idx, contribution) tuples
        col_to_partners = {i: [] for i in range(self.n_cols)}
        
        for (i, j), contribution in self.pair_contributions.items():
            # Add j as partner of i
            col_to_partners[i].append((j, contribution))
            # Add i as partner of j (symmetric)
            col_to_partners[j].append((i, contribution))
        
        # Sort and select top_k for each column
        self.pruned_pairs_per_column = {}
        pruned_pairs_set = set()
        
        logger.info("")
        logger.info("   Top partners per column (keeping smallest gradients = most important):")
        for col_idx in range(self.n_cols):
            partners = col_to_partners[col_idx]
            
            # Sort by contribution (SMALLEST first = most important = already optimized)
            partners_sorted = sorted(partners, key=lambda x: x[1], reverse=False)
            
            # Select top_k
            top_partners = [partner_idx for partner_idx, _ in partners_sorted[:top_k]]
            self.pruned_pairs_per_column[col_idx] = top_partners
            
            # Add to pruned set (ensure i < j for uniqueness)
            for partner_idx in top_partners:
                pair = tuple(sorted([col_idx, partner_idx]))
                pruned_pairs_set.add(pair)
            
            # Log top 3 partners for this column
            col_name = self.col_names[col_idx]
            # Truncate long column names
            if len(col_name) > 25:
                col_name = col_name[:22] + "..."
            
            top_3_info = ", ".join([
                f"{self.col_names[p_idx][:20]}({contrib:.4f})"
                for p_idx, contrib in partners_sorted[:3]
            ])
            logger.info(f"   {col_name:<25}: {top_3_info}")
        
        # Convert to list for forward pass
        self._pruned_pairs_list = list(pruned_pairs_set)
        
        total_pairs_before = len(self.all_pairs)
        total_pairs_after = len(pruned_pairs_set)
        reduction = (1 - total_pairs_after / total_pairs_before) * 100
        
        logger.info("")
        logger.info(f"📊 PRUNING SUMMARY:")
        logger.info(f"   Pairs before: {total_pairs_before}")
        logger.info(f"   Pairs after:  {total_pairs_after}")
        logger.info(f"   Reduction:    {reduction:.1f}%")
        logger.info(f"   Tokens before: {total_pairs_before * 6}")
        logger.info(f"   Tokens after:  {total_pairs_after * 6}")
        logger.info("=" * 80)
        logger.info("")
        
        # Log post-pruning analysis
        self.log_pruning_analysis()
    
    def update_mi_estimates(
        self,
        col_mi_estimates: Dict[str, Optional[float]],
        joint_mi_estimate: Optional[float] = None,
    ):
        """
        Update mutual information estimates from encoder.
        
        Note: DynamicRelationshipExtractor uses contribution-based pruning rather than
        MI-based pair selection, so this method primarily stores the estimates for
        potential future use (e.g., logging, analysis, or hybrid pruning strategies).
        """
        # Store MI estimates for potential future use
        self.col_mi_estimates = col_mi_estimates.copy() if col_mi_estimates else {}
        self.joint_mi_estimate = joint_mi_estimate
        
        # Log MI estimates if available (useful for debugging)
        if logger.isEnabledFor(logging.DEBUG) and col_mi_estimates:
            mi_values = [f"{k}={v:.4f}" for k, v in col_mi_estimates.items() if v is not None]
            if mi_values:
                logger.debug(f"📊 DynamicRelationshipExtractor: Updated MI estimates: {', '.join(mi_values[:5])}{'...' if len(mi_values) > 5 else ''}")
    
    def update_column_losses(
        self, 
        col_losses_dict: Dict[str, float],
        is_null_baseline: bool = False,
    ):
        """
        Update per-column marginal losses from encoder.
        
        This is the CRITICAL metric for relationship importance!
        
        Args:
            col_losses_dict: {col_name: avg_marginal_loss_for_column}
                Higher loss = harder to predict = more important column
            is_null_baseline: If True, these losses are from NULL-only forward pass
                and should update NULL baseline EMA instead of normal losses
        
        Relationships between high-loss (hard) columns are most valuable.
        Relationships between low-loss (easy) columns can be pruned.
        """
        if is_null_baseline:
            # The aggregated_col_losses already aggregates across all 4 masks
            # So we can use it directly (no need to accumulate across multiple calls)
            # But we need to track that we've processed this batch
            self._null_baseline_mask_count += 1
            
            # Store aggregated losses (already averaged across masks)
            # This matches the normal loss aggregation regime
            for col_name, aggregated_loss in col_losses_dict.items():
                if col_name not in self._null_baseline_losses_this_batch:
                    self._null_baseline_losses_this_batch[col_name] = []
                # Store the aggregated loss (already averaged across masks)
                self._null_baseline_losses_this_batch[col_name].append(aggregated_loss)
            
            # Note: _finalize_null_baseline_batch() will be called after all processing
            # It will average across any multiple calls and update EMA
        else:
            # Normal loss update
            self.col_marginal_losses = col_losses_dict.copy() if col_losses_dict else {}
            
            # Compute lift for active pairs in this batch
            # Lift = baseline_null_ema[i] - loss_i_with_pair
            # This is the core metric for ranking pairs
            self._update_pair_lift_stats(col_losses_dict)
            
            # Log column losses if available (useful for debugging)
            if logger.isEnabledFor(logging.DEBUG) and col_losses_dict:
                loss_items = sorted(col_losses_dict.items(), key=lambda x: x[1], reverse=True)[:5]
                loss_strs = [f"{k}={v:.4f}" for k, v in loss_items]
                logger.debug(f"📊 DynamicRelationshipExtractor: Updated column losses (top 5 hardest): {', '.join(loss_strs)}")
            
            # Clear active pairs after processing (reset for next batch)
            self._active_pairs_this_batch.clear()
    
    def _ensure_null_baseline_attributes(self):
        """
        Ensure NULL baseline evaluation attributes are initialized.
        This is needed when models are loaded from older checkpoints that don't have these attributes.
        """
        if not hasattr(self, '_null_evaluation_pending'):
            self._null_evaluation_pending = False
        if not hasattr(self, '_step_counter'):
            self._step_counter = 0
        if not hasattr(self, '_null_every_steps_early'):
            self._null_every_steps_early = 5
        if not hasattr(self, '_null_every_steps_late'):
            self._null_every_steps_late = 10
        if not hasattr(self, '_null_early_epochs'):
            self._null_early_epochs = 20
        if not hasattr(self, '_null_batch_mask_modes'):
            self._null_batch_mask_modes = []
        if not hasattr(self, '_null_baseline_losses_this_batch'):
            self._null_baseline_losses_this_batch = {}
        if not hasattr(self, '_null_baseline_mask_count'):
            self._null_baseline_mask_count = 0
        if not hasattr(self, 'current_epoch'):
            # Default to a high epoch number so we use late frequency during prediction
            self.current_epoch = 999
        if not hasattr(self, '_null_baseline_alpha'):
            self._null_baseline_alpha = 0.1  # EMA decay rate
        if not hasattr(self, '_null_sample_rate'):
            # Default based on column count if available
            if hasattr(self, 'n_cols') and self.n_cols > 0:
                self._null_sample_rate = 20.0 / self.n_cols
            else:
                self._null_sample_rate = 1.0
    
    def _ensure_pair_stats_attributes(self):
        """
        Ensure pair statistics attributes are initialized.
        This is needed when models are loaded from older checkpoints that don't have these attributes.
        """
        if not hasattr(self, '_pair_stats'):
            self._pair_stats: Dict[Tuple[int, int], Dict] = {}
        if not hasattr(self, '_pair_lift_alpha'):
            self._pair_lift_alpha = 0.1
        if not hasattr(self, '_active_pairs_this_batch'):
            self._active_pairs_this_batch: Set[Tuple[int, int]] = set()
        if not hasattr(self, 'pair_contributions'):
            self.pair_contributions = {}
            # Initialize for all pairs if all_pairs exists
            if hasattr(self, 'all_pairs'):
                for pair in self.all_pairs:
                    self.pair_contributions[pair] = 0.0
        if not hasattr(self, '_pair_scores'):
            self._pair_scores: Dict[Tuple[int, int], int] = {}
            # Initialize scores for all pairs if all_pairs exists
            if hasattr(self, 'all_pairs'):
                for pair in self.all_pairs:
                    self._pair_scores[pair] = 0
        if not hasattr(self, 'col_marginal_losses'):
            self.col_marginal_losses: Dict[str, float] = {}
        if not hasattr(self, 'col_mi_estimates'):
            self.col_mi_estimates: Dict[str, Optional[float]] = {}
        if not hasattr(self, '_null_baseline_ema'):
            self._null_baseline_ema: Dict[str, float] = {}
        if not hasattr(self, '_null_baseline_source'):
            self._null_baseline_source: Dict[str, str] = {}
        if not hasattr(self, '_null_baseline_n'):
            self._null_baseline_n: Dict[str, int] = {}
        if not hasattr(self, '_last_step_active_pairs'):
            self._last_step_active_pairs: Optional[Set[Tuple[int, int]]] = None
        if not hasattr(self, 'MIN_SUPPORT_TRACK'):
            self.MIN_SUPPORT_TRACK = 10  # Default: reasonable minimum for tracking
        if not hasattr(self, 'MIN_SUPPORT_RANK'):
            self.MIN_SUPPORT_RANK = 20  # Default: reasonable minimum for ranking
        if not hasattr(self, 'MIN_SUPPORT_PRUNE'):
            self.MIN_SUPPORT_PRUNE = 50  # Default: reasonable minimum for pruning
        if not hasattr(self, '_initial_min_support_rank'):
            self._initial_min_support_rank = self.MIN_SUPPORT_RANK
        if not hasattr(self, 'use_ucb_selection'):
            self.use_ucb_selection = True  # Default: enable UCB selection
        if not hasattr(self, 'ucb_alpha'):
            self.ucb_alpha = 1.5  # Default UCB exploration parameter
        if not hasattr(self, 'edge_dropout_prob'):
            self.edge_dropout_prob = 0.2  # Default edge dropout probability
        if not hasattr(self, 'confidence_weight_n0'):
            self.confidence_weight_n0 = 40  # Default confidence weighting threshold
        if not hasattr(self, 'exploration_epochs'):
            self.exploration_epochs = 10  # Default exploration epochs
        if not hasattr(self, '_epoch_dropout_stats'):
            self._epoch_dropout_stats = {
                'total_edges_before': 0,
                'total_edges_after': 0,
                'total_dropped': 0,
                'steps_with_dropout': 0,
            }
        if not hasattr(self, '_epoch_active_edges'):
            self._epoch_active_edges = []  # List of active directed edge counts per step
        if not hasattr(self, 'top_k_fraction'):
            self.top_k_fraction = 0.40  # Default top-k fraction
        if not hasattr(self, 'progressive_pruning'):
            self.progressive_pruning = True  # Default: enable progressive pruning
        if not hasattr(self, 'current_epoch'):
            self.current_epoch = 0
        if not hasattr(self, '_stored_grad_norms'):
            self._stored_grad_norms: Dict[str, float] = {}
        if not hasattr(self, 'all_pairs'):
            # Generate all unique pairs if not exists
            if hasattr(self, 'n_cols'):
                self.all_pairs = []
                for i in range(self.n_cols):
                    for j in range(i + 1, self.n_cols):
                        self.all_pairs.append((i, j))
            else:
                self.all_pairs = []
        if not hasattr(self, '_directed_pairs'):
            self._directed_pairs: Set[Tuple[int, int]] = set()
            if hasattr(self, 'n_cols'):
                for i in range(self.n_cols):
                    for j in range(self.n_cols):
                        if i != j:
                            self._directed_pairs.add((i, j))
        if not hasattr(self, '_last_adaptive_check_step'):
            self._last_adaptive_check_step = -1
        if not hasattr(self, '_adaptive_check_interval'):
            self._adaptive_check_interval = 100
        if not hasattr(self, 'disabled_pairs'):
            self.disabled_pairs: set = set()
        if not hasattr(self, 'min_relationships_to_keep'):
            # Default: keep at least max(5, n_cols/2)
            if hasattr(self, 'n_cols'):
                min_keep = max(5, self.n_cols // 2)
                self.min_relationships_to_keep = min(min_keep, self.n_cols) if self.n_cols > 0 else 5
            else:
                self.min_relationships_to_keep = 5
        if not hasattr(self, 'target_pruning_epochs'):
            self.target_pruning_epochs = 15  # Default
        if not hasattr(self, 'pairs_to_prune_per_epoch'):
            self.pairs_to_prune_per_epoch = 0  # Will be calculated if progressive_pruning is enabled
        if not hasattr(self, '_contribution_ema_alpha'):
            self._contribution_ema_alpha = 0.1
        if not hasattr(self, '_tokens_for_gradient_check'):
            self._tokens_for_gradient_check: List[Tuple[Tuple[int, int], torch.Tensor]] = []
        if not hasattr(self, '_batch_counter'):
            self._batch_counter = 0
        if not hasattr(self, '_log_every_n_batches'):
            self._log_every_n_batches = 20
        if not hasattr(self, 'operation_contributions'):
            self.operation_contributions = {
                'multiply': 0.0,
                'add': 0.0,
                'cosine': 0.0,
                'abs_diff': 0.0,
                'subtract': 0.0,
                'divide': 0.0,
            }
        if not hasattr(self, 'contribution_history'):
            self.contribution_history: List[Dict[Tuple[int, int], float]] = []
        if not hasattr(self, 'joint_mi_estimate'):
            self.joint_mi_estimate: Optional[float] = None
        if not hasattr(self, '_pair_active_epochs'):
            self._pair_active_epochs: Dict[Tuple[int, int], Set[int]] = {}
        if not hasattr(self, '_column_loss_history'):
            self._column_loss_history: Dict[str, List[float]] = {}
        if not hasattr(self, '_all_epochs'):
            self._all_epochs: Set[int] = set()
        if not hasattr(self, 'pruned_pairs_per_column'):
            self.pruned_pairs_per_column: Optional[Dict[int, List[int]]] = None
        if not hasattr(self, '_pruned_pairs_list'):
            self._pruned_pairs_list: Optional[List[Tuple[int, int]]] = None
        if not hasattr(self, '_weight_snapshots'):
            self._weight_snapshots = {}  # {epoch: {op_name: weight_norm}}
        if not hasattr(self, '_weight_deltas'):
            self._weight_deltas = {}  # {op_name: [delta_per_epoch]}
        if not hasattr(self, '_session_id'):
            self._session_id: Optional[str] = None
        if not hasattr(self, '_known_good_pairs'):
            self._known_good_pairs: Set[Tuple[int, int]] = set()
        if not hasattr(self, '_known_bad_pairs'):
            self._known_bad_pairs: Set[Tuple[int, int]] = set()
        if not hasattr(self, '_history_loaded'):
            self._history_loaded = False
        if not hasattr(self, '_dataset_hash'):
            self._dataset_hash: Optional[str] = None
        if not hasattr(self, 'use_fusion'):
            self.use_fusion = True  # Default: use fusion mode
        if not hasattr(self, 'ops_per_pair'):
            self.ops_per_pair = 1 if getattr(self, 'use_fusion', True) else 9
        if not hasattr(self, 'max_pairs_per_chunk'):
            # Default: conservative limit
            self.max_pairs_per_chunk = 300
        if not hasattr(self, 'max_coarse_pairs'):
            self.max_coarse_pairs = 300
        if not hasattr(self, 'coarse_exploration_dim'):
            self.coarse_exploration_dim = 32
        if not hasattr(self, '_median_abs_lift'):
            self._median_abs_lift: Optional[float] = None
        if not hasattr(self, '_last_pairs_to_compute'):
            self._last_pairs_to_compute: Optional[List[Tuple[int, int]]] = None
        if not hasattr(self, '_selection_rng'):
            # Will be created on demand when needed
            pass  # Don't create here, created lazily
        if not hasattr(self, '_sample_rng'):
            # Will be created on demand when needed
            pass  # Don't create here, created lazily
        if not hasattr(self, '_coarse_sample_logged'):
            self._coarse_sample_logged = False
        if not hasattr(self, '_chunking_logged'):
            self._chunking_logged = False
    
    def should_evaluate_null_baseline(self, is_first_mask: bool = True) -> bool:
        """
        Check if we should evaluate NULL baseline this step.
        
        Note: This is called multiple times per batch (for mask_1, mask_2, short_1, short_2).
        We evaluate on ALL masks in the batch to match the aggregation regime.
        
        Args:
            is_first_mask: True if this is the first mask call (mask_1), False for subsequent masks
        
        Returns:
            True if NULL-only evaluation should be run for this mask
        """
        # Ensure attributes are initialized (for backward compatibility with old checkpoints)
        self._ensure_null_baseline_attributes()
        
        # During prediction/inference, never evaluate NULL baseline
        if not self.training:
            return False
        
        # On first mask call, check if we should start evaluation
        if is_first_mask:
            # Check if already evaluating this batch
            if self._null_evaluation_pending:
                return True  # Continue evaluating for remaining masks
            
            # Increment counter (once per batch)
            self._step_counter += 1
            
            # Adaptive frequency: more frequent early in training
            if self.current_epoch < self._null_early_epochs:
                every_steps = self._null_every_steps_early
            else:
                every_steps = self._null_every_steps_late
            
            # Check if we should start evaluation
            should_start = (self._step_counter % every_steps == 0)
            
            if should_start:
                self._null_evaluation_pending = True
                self._null_baseline_losses_this_batch = {}  # Reset accumulator
                self._null_baseline_mask_count = 0  # Reset counter
                self._null_batch_mask_modes = []  # Reset mode tracking for invariant check
                return True
            else:
                return False
        else:
            # For subsequent masks, continue evaluation if pending
            return self._null_evaluation_pending
    
    def _finalize_null_baseline_batch(self):
        """
        Finalize NULL baseline EMA update after batch is processed.
        
        The losses passed to update_column_losses() are already aggregated
        across all 4 masks (matching normal loss aggregation), so we use them directly.
        """
        # Ensure attributes are initialized (for backward compatibility with old checkpoints)
        self._ensure_null_baseline_attributes()
        
        if not self._null_baseline_losses_this_batch:
            return  # No losses accumulated
        
        # The losses are already aggregated per mask call
        # If we got multiple calls (shouldn't happen, but be safe), average them
        aggregated_losses = {}
        for col_name, losses in self._null_baseline_losses_this_batch.items():
            if losses:
                # Average across calls (should be 1, but handle multiple gracefully)
                aggregated_losses[col_name] = sum(losses) / len(losses)
        
        # Update EMA with aggregated losses
        for col_name, aggregated_loss in aggregated_losses.items():
            if col_name not in self._null_baseline_ema:
                # Initialize on first observation
                self._null_baseline_ema[col_name] = aggregated_loss
                self._null_baseline_n[col_name] = 1
                self._null_baseline_source[col_name] = "null"
            else:
                # Update EMA
                # Use adaptive alpha: higher early (0.2) for fast adaptation, lower later (0.1)
                if self.current_epoch < self._null_early_epochs:
                    alpha = 0.2  # Faster adaptation early
                else:
                    alpha = self._null_baseline_alpha  # Slower adaptation later
                
                self._null_baseline_ema[col_name] = (
                    (1 - alpha) * self._null_baseline_ema[col_name] + alpha * aggregated_loss
                )
                self._null_baseline_n[col_name] += 1
                self._null_baseline_source[col_name] = "null"
        
        # CRITICAL INVARIANT CHECK: All 4 masks (full_1, full_2, short_1, short_2) must use the same mode
        # 
        # Expected structure:
        # - modes[0] = mask_1 mode (generates full_1 and short_1 from same joint_encoder() call)
        # - modes[1] = mask_2 mode (generates full_2 and short_2 from same joint_encoder() call)
        # - modes[2] = unmasked mode (if present, doesn't contribute to marginal losses)
        #
        # Since short and full come from the same joint_encoder() call, checking mask_1 == mask_2
        # is sufficient to ensure all 4 masks are consistent, AS LONG AS we verify:
        # 1. We have at least 2 entries (mask_1 and mask_2)
        # 2. The first two entries correspond to mask_1 and mask_2 (not reordered)
        # 3. They match each other
        #
        # ASSUMPTION: The unmasked call (if present) doesn't affect masked calls through cached state.
        # This is safe because:
        # - Relationship extractor forward() is stateless (no caching between calls)
        # - Joint encoder uses a transformer (stateless by design)
        # - All state updates happen via update_column_losses(), not during forward()
        
        # DEBUG: Log modes list contents for debugging
        logger.debug(
            f"NULL baseline batch modes: {self._null_batch_mask_modes} "
            f"(len={len(self._null_batch_mask_modes)}, "
            f"flag={'SET' if self._null_evaluation_pending else 'CLEAR'})"
        )
        
        # Invariant 1: Must have at least 2 entries (mask_1 and mask_2)
        if len(self._null_batch_mask_modes) < 2:
            # This should never happen - we expect at least mask_1 and mask_2
            logger.error(f"🚨 CRITICAL: Insufficient mode tracking entries!")
            logger.error(f"   Expected at least 2 entries (mask_1 and mask_2), got {len(self._null_batch_mask_modes)}")
            logger.error(f"   This suggests a bug in the mode tracking logic.")
            raise AssertionError(
                f"Insufficient mode tracking: expected at least 2 entries (mask_1 and mask_2), "
                f"got {len(self._null_batch_mask_modes)}. This suggests a bug in mode tracking."
            )
        
        # Extract mask_1 and mask_2 modes (first two entries)
        mask_1_mode = self._null_batch_mask_modes[0]
        mask_2_mode = self._null_batch_mask_modes[1]
        
        # Check that mask_1 and mask_2 used the same mode
        if mask_1_mode != mask_2_mode:
            # This is a critical bug - mixing NULL-only and normal modes in the same batch
            logger.error(f"🚨 CRITICAL: Mixed NULL-only and normal modes in same batch!")
            logger.error(f"   mask_1 mode (modes[0]): {'NULL-only' if mask_1_mode else 'normal'}")
            logger.error(f"   mask_2 mode (modes[1]): {'NULL-only' if mask_2_mode else 'normal'}")
            logger.error(f"   Total entries: {len(self._null_batch_mask_modes)}")
            logger.error(f"   This violates the invariant that all 4 masks must use the same mode.")
            logger.error(f"   Aggregated losses will be biased. This should never happen.")
            raise AssertionError(
                f"Mixed NULL-only and normal modes in same batch: "
                f"mask_1={'NULL-only' if mask_1_mode else 'normal'}, "
                f"mask_2={'NULL-only' if mask_2_mode else 'normal'}. "
                f"All 4 masks (full_1, full_2, short_1, short_2) must use the same mode."
            )
        
        # Optional: Log if there are additional entries (unmasked call)
        if len(self._null_batch_mask_modes) > 2:
            unmasked_mode = self._null_batch_mask_modes[2]
            logger.debug(
                f"   Unmasked call mode: {'NULL-only' if unmasked_mode else 'normal'} "
                f"(doesn't affect marginal loss aggregation)"
            )
        
        # Invariant 3: If this is a NULL baseline batch (flag was set), ensure modes[0] == True
        # This is a sanity check: if we're updating NULL baseline, all masks should be NULL-only
        if self._null_evaluation_pending and not mask_1_mode:
            logger.error(f"🚨 CRITICAL: NULL baseline flag is set but mask_1 used normal mode!")
            logger.error(f"   This suggests a bug in the mode tracking or flag management.")
            logger.error(f"   Flag state: {self._null_evaluation_pending}, mask_1 mode: {mask_1_mode}")
            raise AssertionError(
                f"NULL baseline flag is set but mask_1 used normal mode. "
                f"This suggests a bug in mode tracking or flag management."
            )
        
        # Clear accumulator, flag, and mode tracking
        self._null_baseline_losses_this_batch = {}
        self._null_evaluation_pending = False
        self._null_baseline_mask_count = 0
        self._null_batch_mask_modes = []
        
        # Log coverage (DEBUG level, more frequent for debugging)
        # Also log at INFO level every 10 steps for visibility
        coverage = self.get_null_baseline_coverage()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"📊 NULL Baseline updated: {coverage['cols_with_baseline']}/{coverage['total_cols']} cols ({coverage['coverage_pct']:.1f}%)")
        
        # INFO level logging every 10 steps (more frequent than epoch-based)
        if self._step_counter % 50 == 0:  # Every 50 steps = ~5 batches at 10 steps/batch
            logger.info(f"📊 NULL Baseline Coverage (step {self._step_counter}):")
            logger.info(f"   Columns with baseline: {coverage['cols_with_baseline']}/{coverage['total_cols']} ({coverage['coverage_pct']:.1f}%)")
            logger.info(f"   Source: {coverage['null_source']} NULL-only, {coverage['bootstrap_source']} bootstrap")
            
            if coverage['coverage_pct'] < 50:
                logger.warning(f"⚠️  Low NULL baseline coverage ({coverage['coverage_pct']:.1f}%) - lift calculations may be unreliable")
    
    def get_null_baseline_coverage(self) -> Dict[str, float]:
        """
        Get NULL baseline coverage metrics.
        
        Returns:
            Dict with coverage statistics
        """
        total_cols = len(self.col_names)
        cols_with_baseline = len(self._null_baseline_ema)
        coverage_pct = (cols_with_baseline / total_cols * 100) if total_cols > 0 else 0
        
        # Get baseline sources
        null_count = sum(1 for src in self._null_baseline_source.values() if src == "null")
        bootstrap_count = sum(1 for src in self._null_baseline_source.values() if src == "bootstrap")
        
        return {
            'total_cols': total_cols,
            'cols_with_baseline': cols_with_baseline,
            'coverage_pct': coverage_pct,
            'null_source': null_count,
            'bootstrap_source': bootstrap_count,
        }
    
    def _record_epoch_history(
        self,
        epoch_idx: int,
        active_pairs: List[Tuple[int, int]],
        col_losses: Dict[str, float],
    ):
        """
        STAGE 1: Record epoch history for causal inference and validation.
        
        Tracks:
        - Which pairs were active this epoch
        - Per-column losses over time
        - All epochs seen
        
        This data enables:
        - Causal lift calculation (paired vs unpaired improvement)
        - Validation (does importance predict actual lift?)
        """
        self._all_epochs.add(epoch_idx)
        
        # Store column losses
        for col_name, loss in col_losses.items():
            if col_name not in self._column_loss_history:
                self._column_loss_history[col_name] = []
            self._column_loss_history[col_name].append(loss)
        
        # Track which pairs were active (undirected)
        for pair in active_pairs:
            if pair not in self._pair_active_epochs:
                self._pair_active_epochs[pair] = set()
            self._pair_active_epochs[pair].add(epoch_idx)
        
        # Update pair stats counts (directed)
        # When pair (i,j) is active, increment counts for both (i->j) and (j->i)
        for pair in active_pairs:
            i, j = pair
            # Initialize if needed
            if (i, j) not in self._pair_stats:
                self._pair_stats[(i, j)] = {'n': 0, 'lift_ema': 0.0}
            if (j, i) not in self._pair_stats:
                self._pair_stats[(j, i)] = {'n': 0, 'lift_ema': 0.0}
            
            # Note: We don't increment 'n' here - that happens when we compute lift
            # This just ensures the stats dict exists
        
        # Also record in causal scorer and validator
        self.causal_scorer.record_epoch(epoch_idx, active_pairs, col_losses)
        self.validator.record_epoch(epoch_idx, active_pairs, col_losses)
    
    def _compute_lift_from_null_baseline(
        self,
        directed_pair: Tuple[int, int],  # (i -> j): effect of i on j
    ) -> Optional[float]:
        """
        Phase 1 lift calculation: lift = NULL_baseline - current_loss
        
        Args:
            directed_pair: (i, j) where we measure effect on j when paired with i
        
        Returns:
            lift value (positive = helps, negative = hurts) or None if baseline missing
        """
        i, j = directed_pair
        col_j_name = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
        
        # Get NULL baseline for target column
        if col_j_name not in self._null_baseline_ema:
            return None  # No baseline yet
        
        null_baseline = self._null_baseline_ema[col_j_name]
        
        # Get current loss for target column
        current_loss = self.col_marginal_losses.get(col_j_name)
        if current_loss is None:
            return None  # No current loss
        
        # Lift = improvement from NULL baseline
        lift = null_baseline - current_loss
        
        return lift
    
    def _update_pair_lift_stats(
        self,
        col_losses_dict: Dict[str, float],
    ):
        """
        Update lift statistics for all active pairs in this batch.
        
        For each directed pair (i->j) that was active:
        - Compute lift = baseline_null_ema[j] - loss_j_with_pair
        - Update _pair_stats with EMA of lift
        
        Args:
            col_losses_dict: {col_name: aggregated_marginal_loss} from this batch
                These losses are already aggregated across all 4 masks, matching NULL baseline regime
        """
        if not self._active_pairs_this_batch:
            return  # No active pairs this batch
        
        # Increment step counter (once per batch)
        self._step_counter += 1
        
        # Track lift statistics for diagnostics
        lift_values = []  # Track all lift values for this batch
        negative_lifts = 0
        
        # Initialize median absolute lift if not already set (for outlier clipping)
        if not hasattr(self, '_median_abs_lift'):
            self._median_abs_lift = None
        
        # For each active directed pair (i->j), compute lift
        # NOTE: Relationships are symmetric (pooled and injected into CLS, affecting all columns),
        # so tracking both (i,j) and (j,i) is correct. All columns receive information from all relationships.
        # Lift measures: how much does the relationship help predict j?
        for directed_pair in self._active_pairs_this_batch:
            i, j = directed_pair
            
            # Get column name for target column j
            if j >= len(self.col_names):
                continue  # Invalid column index
            col_j_name = self.col_names[j]
            
            # Get loss for column j (when paired with i)
            loss_j_with_pair = col_losses_dict.get(col_j_name)
            if loss_j_with_pair is None:
                continue  # No loss for this column
            
            # Sanity check: loss should be finite
            if not (math.isfinite(loss_j_with_pair) and loss_j_with_pair >= 0):
                logger.warning(
                    f"⚠️ Invalid loss for {col_j_name} in pair ({i}->{j}): {loss_j_with_pair}"
                )
                continue
            
            # Get NULL baseline for column j
            null_baseline = self._null_baseline_ema.get(col_j_name)
            
            if null_baseline is None:
                # No baseline yet - can't compute lift
                # This is OK during early training, but we won't rank/prune without baseline
                continue
            
            # Sanity check: baseline should be finite
            if not (math.isfinite(null_baseline) and null_baseline >= 0):
                logger.warning(
                    f"⚠️ Invalid NULL baseline for {col_j_name}: {null_baseline}"
                )
                continue
            
            # CRITICAL: Detect training divergence - if current loss is >> baseline, training may have exploded
            # Skip lift updates in this case to avoid corrupting statistics
            if loss_j_with_pair > null_baseline * 10:
                # Loss is 10x+ higher than baseline - likely training divergence
                if logger.isEnabledFor(logging.DEBUG) or self._step_counter % 50 == 0:
                    logger.warning(
                        f"⚠️ Training divergence detected for {col_j_name}: "
                        f"current_loss={loss_j_with_pair:.2f} >> baseline={null_baseline:.2f} "
                        f"(ratio={loss_j_with_pair/null_baseline:.1f}x). "
                        f"Skipping lift update to avoid corrupting statistics."
                    )
                continue
            
            # Compute lift: improvement from NULL baseline
            # Positive lift = relationship helps (reduces loss)
            # Negative lift = relationship hurts (increases loss) - THIS IS VALID SIGNAL
            lift = null_baseline - loss_j_with_pair
            
            # Sanity check: lift should be finite (but can be negative!)
            if not math.isfinite(lift):
                logger.warning(
                    f"⚠️ Invalid lift for pair ({i}->{j}): {lift} "
                    f"(baseline={null_baseline}, loss={loss_j_with_pair})"
                )
                continue
            
            # Optional: Clip extreme outliers (but preserve negative signal)
            # Use median absolute lift as reference for clipping
            if self._median_abs_lift is not None and self._median_abs_lift > 0:
                clip_range = 10.0 * self._median_abs_lift
                if abs(lift) > clip_range:
                    lift = math.copysign(clip_range, lift)  # Preserve sign
            
            # Track for diagnostics
            lift_values.append(lift)
            if lift < 0:
                negative_lifts += 1
            
            # Update pair stats with lift (source is always "null" when we have baseline)
            self._update_pair_lift_ema(directed_pair, lift, source="null")
            
            # DEBUG: Log occasionally for sanity checking
            if logger.isEnabledFor(logging.DEBUG) and self._step_counter % 50 == 0:
                logger.debug(
                    f"Lift update: ({i}->{j}) lift={lift:.4f} "
                    f"(baseline={null_baseline:.4f}, loss={loss_j_with_pair:.4f})"
                )
        
        # Update median absolute lift for outlier clipping (EMA)
        if lift_values:
            median_abs_lift = sorted([abs(l) for l in lift_values])[len(lift_values) // 2]
            if self._median_abs_lift is None:
                self._median_abs_lift = median_abs_lift
            else:
                # EMA update
                self._median_abs_lift = 0.9 * self._median_abs_lift + 0.1 * median_abs_lift
            
            # Log negative lift percentage (great diagnostic)
            negative_pct = (negative_lifts / len(lift_values)) * 100 if lift_values else 0
            if logger.isEnabledFor(logging.DEBUG) or (self._step_counter % 100 == 0 and negative_pct > 10):
                logger.info(
                    f"📊 Lift stats (step {self._step_counter}): "
                    f"{len(lift_values)} updates, {negative_pct:.1f}% negative lifts "
                    f"(median_abs={self._median_abs_lift:.4f})"
                )
    
    def _update_pair_lift_ema(
        self,
        directed_pair: Tuple[int, int],
        lift: float,
        source: str = "null",  # "null" or "bootstrap"
    ):
        """
        Update EMA of lift for a directed pair.
        
        Args:
            directed_pair: (i, j) directed pair
            lift: Lift value (baseline - current_loss)
            source: "null" if from NULL baseline, "bootstrap" if from unpaired fallback
        """
        if directed_pair not in self._pair_stats:
            self._pair_stats[directed_pair] = {
                'n': 0,
                'lift_ema': 0.0,
                'last_step': 0,
                'source_counts': {'null': 0, 'bootstrap': 0}
            }
        
        stats = self._pair_stats[directed_pair]
        
        # Ensure source_counts exists (backward compatibility for old entries)
        if 'source_counts' not in stats:
            stats['source_counts'] = {'null': 0, 'bootstrap': 0}
        
        stats['n'] += 1
        stats['last_step'] = self._step_counter
        
        # Track source
        if source in stats['source_counts']:
            stats['source_counts'][source] += 1
        
        # Update EMA
        if stats['n'] == 1:
            stats['lift_ema'] = lift
        else:
            alpha = self._pair_lift_alpha
            stats['lift_ema'] = (1 - alpha) * stats['lift_ema'] + alpha * lift
    
    def _compute_pair_scores(
        self,
        active_pairs: List[Tuple[int, int]],
    ) -> Tuple[Dict[Tuple[int, int], float], Dict]:
        """
        Phase 1: Compute pair scores using NULL baseline lift.
        
        Returns:
            (scores_dict, diagnostics_dict)
            scores_dict: {(i,j): score} for rankable pairs only
            diagnostics: coverage metrics and skip counts
        """
        scores = {}
        diagnostics = {
            'total_pairs': len(active_pairs),
            'observed_pairs': 0,  # Pairs with at least 1 observation
            'trackable_pairs': 0,  # Pairs with n_total >= MIN_SUPPORT_TRACK
            'skipped_track': 0,
            'skipped_no_baseline': 0,
            'skipped_rank': 0,
            'rankable': 0,  # Pairs with n_total >= MIN_SUPPORT_RANK and has baseline
            'prunable': 0,  # Pairs with n_total >= MIN_SUPPORT_PRUNE and has baseline
        }
        
        # For each undirected pair (i,j), compute scores for both directions
        # CRITICAL: Use n_total = n_ij + n_ji (undirected pair support) for all support gating
        # This is consistent with sparse sampling where individual directions may have low counts
        # but the undirected pair accumulates enough observations across both directions
        for pair in active_pairs:
            i, j = pair
            
            # Get pair stats for both directions
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            
            n_ij = stats_ij.get('n', 0)
            n_ji = stats_ji.get('n', 0)
            n_total = n_ij + n_ji  # Undirected pair support (sum of both directions)
            
            # Track observed pairs (at least 1 observation)
            if n_total > 0:
                diagnostics['observed_pairs'] += 1
            
            # Skip if insufficient support for tracking (using n_total)
            if n_total < self.MIN_SUPPORT_TRACK:
                diagnostics['skipped_track'] += 1
                continue
            
            # Track trackable pairs (n_total >= MIN_SUPPORT_TRACK)
            diagnostics['trackable_pairs'] += 1
            
            # Get lift EMA for both directions
            lift_ema_ij = stats_ij.get('lift_ema')
            lift_ema_ji = stats_ji.get('lift_ema')
            
            # Check source: only use NULL baseline, block bootstrap
            source_counts_ij = stats_ij.get('source_counts', {})
            source_counts_ji = stats_ji.get('source_counts', {})
            
            # CRITICAL: Block bootstrap from ranking/pruning
            # Only use pairs where we have NULL baseline (not bootstrap fallback)
            has_null_baseline_ij = (
                lift_ema_ij is not None and 
                source_counts_ij.get('null', 0) > 0
            )
            has_null_baseline_ji = (
                lift_ema_ji is not None and 
                source_counts_ji.get('null', 0) > 0
            )
            
            # Skip if no NULL baseline for either direction
            if not has_null_baseline_ij and not has_null_baseline_ji:
                diagnostics['skipped_no_baseline'] += 1
                continue
            
            # Skip if insufficient support for ranking (using n_total)
            if n_total < self.MIN_SUPPORT_RANK:
                diagnostics['skipped_rank'] += 1
                continue
            
            # Skip if lift_ema is not finite (sanity check)
            if (lift_ema_ij is not None and not math.isfinite(lift_ema_ij)) or \
               (lift_ema_ji is not None and not math.isfinite(lift_ema_ji)):
                continue  # Invalid lift, skip
            
            # Compute combined score using lift_ema from stats
            # Use 0.0 if direction doesn't have valid lift
            lift_ema_ij_val = lift_ema_ij if has_null_baseline_ij else 0.0
            lift_ema_ji_val = lift_ema_ji if has_null_baseline_ji else 0.0
            
            # Confidence-weighted score: downweight edges with low support
            # Formula: score = ema_lift × min(1, n_ij / n_0)
            # This prevents pruning on noisy early estimates, especially important for large N
            confidence_weight_ij = min(1.0, n_ij / self.confidence_weight_n0) if n_ij > 0 else 0.0
            confidence_weight_ji = min(1.0, n_ji / self.confidence_weight_n0) if n_ji > 0 else 0.0
            
            score = (lift_ema_ij_val * confidence_weight_ij) + (lift_ema_ji_val * confidence_weight_ji)
            
            # Store score (use undirected pair as key for compatibility)
            scores[pair] = score
            diagnostics['rankable'] += 1
            
            # Track prunable pairs (n_total >= MIN_SUPPORT_PRUNE)
            if n_total >= self.MIN_SUPPORT_PRUNE:
                diagnostics['prunable'] += 1
        
        return scores, diagnostics
    
    def _compute_causal_importance(
        self,
        active_pairs: List[Tuple[int, int]],
    ) -> Dict[Tuple[int, int], float]:
        """
        Phase 1: Compute pair importance using NULL baseline lift.
        
        This replaces the old heuristic with controlled lift calculation.
        Uses NULL baseline EMA instead of unpaired epochs for stability.
        
        Returns:
            {(col_i, col_j): importance_score} for rankable pairs only
        """
        # Use Phase 1 scoring (NULL baseline lift)
        scores, diagnostics = self._compute_pair_scores(active_pairs)
        
        # Log comprehensive coverage metrics
        total = diagnostics['total_pairs']
        observed = diagnostics['observed_pairs']
        trackable = diagnostics['trackable_pairs']
        rankable = diagnostics['rankable']
        prunable = diagnostics['prunable']
        
        # Calculate percentages
        observed_pct = (observed / total * 100) if total > 0 else 0
        trackable_pct = (trackable / total * 100) if total > 0 else 0
        rankable_pct = (rankable / total * 100) if total > 0 else 0
        prunable_pct = (prunable / total * 100) if total > 0 else 0
        
        if self.current_epoch % 10 == 0:  # Log every 10 epochs
            logger.info(f"📊 Relationship coverage (epoch {self.current_epoch}):")
            logger.info(f"   Total directed pairs possible: {self.n_cols * (self.n_cols - 1)}")
            logger.info(f"   Total undirected pairs: {total}")
            logger.info(f"   Observed pairs (n≥1): {observed} ({observed_pct:.1f}%)")
            logger.info(f"   Trackable pairs (n_total≥{self.MIN_SUPPORT_TRACK}): {trackable} ({trackable_pct:.1f}%)")
            logger.info(f"   Rankable pairs (n_total≥{self.MIN_SUPPORT_RANK}, has baseline): {rankable} ({rankable_pct:.1f}%)")
            logger.info(f"   Prunable pairs (n_total≥{self.MIN_SUPPORT_PRUNE}, has baseline): {prunable} ({prunable_pct:.1f}%)")
            logger.info(f"   Skipped (tracking): {diagnostics['skipped_track']}")
            logger.info(f"   Skipped (no baseline): {diagnostics['skipped_no_baseline']}")
            logger.info(f"   Skipped (ranking): {diagnostics['skipped_rank']}")
            
            # Only warn after epoch 5 - early training naturally has low coverage
            if self.current_epoch >= 5:
                if rankable_pct < 20:
                    logger.warning(f"⚠️  Low rankable coverage ({rankable_pct:.1f}%) - most pairs have insufficient data or missing NULL baseline")
                if prunable_pct < 10:
                    logger.warning(f"⚠️  Low prunable coverage ({prunable_pct:.1f}%) - pruning decisions may be limited")
        
        return scores
    
    def _compute_relationship_importance(self) -> Dict[Tuple[int, int], float]:
        """
        DEPRECATED: Old heuristic-based importance.
        
        This method is kept for backward compatibility but now delegates
        to _compute_causal_importance. The old heuristic (|loss_i - loss_j|)
        is replaced with causal lift calculation.
        
        Returns:
            {(col_i, col_j): importance_score}
        """
        active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        return self._compute_causal_importance(active_pairs)
    
    def should_prune(self) -> bool:
        """Check if we should prune now (at end of exploration phase)."""
        # If progressive pruning is enabled, use progressive_prune_relationships() instead
        if self.progressive_pruning:
            return False  # Don't trigger hard prune
        
        return (
            self.pruned_pairs_per_column is None and 
            self.current_epoch >= self.exploration_epochs
        )
    
    def should_progressive_prune(self) -> bool:
        """Check if we should progressively disable some relationships this epoch."""
        if not self.progressive_pruning:
            return False
        
        # Start pruning after exploration phase
        if self.current_epoch < self.exploration_epochs:
            return False
        
        # Continue pruning until we reach target
        total_pairs = len(self.all_pairs)
        target_remaining = int(total_pairs * self.top_k_fraction)
        current_active = total_pairs - len(self.disabled_pairs)
        
        return current_active > target_remaining
    
    def progressive_prune_relationships(self):
        """
        Progressively disable the least important relationships based on CAUSAL LIFT.
        Called once per epoch after exploration phase.
        
        METRIC: LCB(lift(i→j) + lift(j→i)) - complexity_penalty
        
        lift(i→j) = improvement_rate(j | paired) - improvement_rate(j | unpaired)
          
        Higher lift = relationship ACTUALLY HELPS learning
        Negative lift = relationship HURTS learning (prune immediately)
        
        Causal approach with counterfactual reasoning:
        - Compares improvement when paired vs unpaired (not just static difference)
        - Uses lower confidence bounds (LCB) to penalize uncertain estimates
        - Recency-weighted (recent epochs matter more as model evolves)
        - Complexity penalty for under-explored pairs
        
        Rules:
        1. Sort all pairs by causal importance (HIGHEST LCB = most benefit)
        2. Always keep top min_relationships_to_keep pairs (safety floor)
        3. From remaining pairs, disable pairs_to_prune_per_epoch with LOWEST LCB
        """
        if not self.should_progressive_prune():
            return
        
        # Get currently active pairs
        active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        
        if not active_pairs:
            return
        
        # ============================================================================
        # STAGE 1: RECORD HISTORY (for causal inference and validation)
        # ============================================================================
        self._record_epoch_history(self.current_epoch, active_pairs, self.col_marginal_losses)
        
        # ============================================================================
        # STAGE 2: COMPUTE CAUSAL IMPORTANCE (replaces heuristic)
        # ============================================================================
        importance_scores = self._compute_causal_importance(active_pairs)
        
        # ============================================================================
        # LOG IMPORTANCE SCORE DISTRIBUTION - Are pairs differentiated or all the same?
        # ============================================================================
        # Only include pairs that have scores (rankable pairs)
        active_importance_values = [importance_scores[p] for p in active_pairs if p in importance_scores]
        
        # AGGRESSIVE PRUNING: When lift is flat (low CV), relationships are not adding
        # meaningful signal - they're just noise. Prune more aggressively to reduce burden.
        # Normal: pairs_to_prune_per_epoch (typically 9)
        # Flat lift (CV < 0.1): disable 10-20 per epoch until we hit target
        base_prune_count = self.pairs_to_prune_per_epoch
        num_to_disable_target = base_prune_count  # Default to base count
        
        if active_importance_values and len(active_importance_values) > 1:
            mean_imp = np.mean(active_importance_values)
            std_imp = np.std(active_importance_values)
            min_imp = np.min(active_importance_values)
            max_imp = np.max(active_importance_values)
            # Coefficient of variation: std/mean - if low, scores are undifferentiated
            cv = std_imp / mean_imp if mean_imp > 1e-8 else 0.0
            
            logger.info(f"📊 Importance score distribution (n={len(active_pairs)} active pairs):")
            logger.info(f"   Mean: {mean_imp:.6f}  Std: {std_imp:.6f}  CV: {cv:.2f}")
            logger.info(f"   Range: [{min_imp:.6f}, {max_imp:.6f}]")
            
            if cv < 0.1:
                logger.warning(f"   ⚠️  LOW DIFFERENTIATION (CV={cv:.2f} < 0.1) - pairs look similar, pruning may be random!")
                
                # Very flat lift - prune aggressively (10-20 per epoch)
                # Scale based on how far we are from target
                current_active = len(active_pairs)
                target_remaining = getattr(self, 'target_relationships', self.min_relationships_to_keep)
                excess = current_active - target_remaining
                
                if excess > 0:
                    # Prune min(20, excess/2) per epoch to make progress
                    aggressive_prune = min(20, max(10, excess // 2))
                    logger.warning(f"🔪 FLAT LIFT DETECTED (CV={cv:.2f}): Aggressive pruning {aggressive_prune} pairs/epoch (target: {target_remaining}, current: {current_active})")
                    num_to_disable_target = aggressive_prune
            elif cv < 0.3:
                logger.info(f"   ⚡ Moderate differentiation (CV={cv:.2f}) - some signal for pruning")
            else:
                logger.info(f"   ✅ Good differentiation (CV={cv:.2f}) - clear signal for pruning")
        
        # Sort all active pairs by importance (HIGHEST first = most important first)
        # Only include pairs that have scores (rankable pairs)
        # Pairs without scores get default score of -inf (lowest priority)
        pairs_by_importance = [
            (p, importance_scores.get(p, float('-inf'))) 
            for p in active_pairs
        ]
        pairs_by_importance.sort(key=lambda x: x[1], reverse=True)  # HIGHEST first
        
        # ============================================================================
        # PROTECTED FLOOR: Per-column protection to avoid hub lock-in
        # ============================================================================
        # Instead of "top N globally" (which creates hub lock-in), protect:
        # - Top 1-2 pairs per column (ensures each column has some relationships)
        # - With degree cap: max 4 protected edges per column (prevents hub dominance)
        # ============================================================================
        protected_set = set()
        protected_pairs = []
        max_protected_per_column = 4  # Degree cap to prevent hub lock-in
        min_protected_per_column = 1  # Ensure each column has at least 1 protected edge
        
        # Count protected edges per column
        protected_count_per_column = {j: 0 for j in range(self.n_cols)}
        
        # First pass: protect top pairs per column (up to degree cap)
        for pair, importance in pairs_by_importance:
            if len(protected_set) >= self.min_relationships_to_keep:
                break  # Reached global minimum
            
            i, j = pair
            # Check if we can protect this pair without exceeding degree caps
            can_protect_i = protected_count_per_column[i] < max_protected_per_column
            can_protect_j = protected_count_per_column[j] < max_protected_per_column
            
            if can_protect_i and can_protect_j:
                protected_set.add(pair)
                protected_pairs.append((pair, importance))
                protected_count_per_column[i] += 1
                protected_count_per_column[j] += 1
        
        # Second pass: ensure minimum per column (if we haven't hit global cap)
        if len(protected_set) < self.min_relationships_to_keep:
            for pair, importance in pairs_by_importance:
                if len(protected_set) >= self.min_relationships_to_keep:
                    break
                
                if pair in protected_set:
                    continue  # Already protected
                
                i, j = pair
                needs_protection_i = protected_count_per_column[i] < min_protected_per_column
                needs_protection_j = protected_count_per_column[j] < min_protected_per_column
                
                if needs_protection_i or needs_protection_j:
                    protected_set.add(pair)
                    protected_pairs.append((pair, importance))
                    protected_count_per_column[i] += 1
                    protected_count_per_column[j] += 1
        
        # CRITICAL FIX: Eligible for disabling = active pairs that are NOT protected
        # This ensures we're selecting from the right set (active + eligible)
        # NOT from all pairs, NOT only pairs with lift, but active pairs excluding protected
        eligible_pairs = [p for p in active_pairs if p not in protected_set]
        
        # DIAGNOSTIC: Log eligible pairs breakdown
        eligible_with_lift = [p for p in eligible_pairs if p in importance_scores]
        eligible_without_lift = [p for p in eligible_pairs if p not in importance_scores]
        logger.info(f"🔪 Pruning eligibility: {len(eligible_pairs)} eligible (active - protected)")
        logger.info(f"   Eligible with lift: {len(eligible_with_lift)}/{len(eligible_pairs)}")
        logger.info(f"   Eligible without lift: {len(eligible_without_lift)}/{len(eligible_pairs)}")
        
        if not eligible_pairs:
            logger.info(f"🔪 Progressive pruning: All {len(active_pairs)} active pairs are protected (below minimum floor)")
            return
        
        # Filter eligible pairs: only allow pruning if n_total >= MIN_SUPPORT_PRUNE
        # CRITICAL: Use n_total = n_ij + n_ji (undirected pair support) for all support gating
        # This is consistent with sparse sampling where individual directions may have low counts
        # but the undirected pair accumulates enough observations across both directions
        prunable_pairs = []
        prunable_with_lift = 0
        prunable_without_lift = 0
        for pair in eligible_pairs:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            n_ij = stats_ij.get('n', 0)
            n_ji = stats_ji.get('n', 0)
            n_total = n_ij + n_ji  # Undirected pair support (sum of both directions)
            
            # CRITICAL: Only allow pruning if we have sufficient support (using n_total)
            if n_total >= self.MIN_SUPPORT_PRUNE:
                # Use score if available, otherwise use -inf (lowest priority)
                score = importance_scores.get(pair, float('-inf'))
                prunable_pairs.append((pair, score))
                if pair in importance_scores:
                    prunable_with_lift += 1
                else:
                    prunable_without_lift += 1
            else:
                # Pair doesn't have enough data yet - skip pruning
                continue
        
        # DIAGNOSTIC: Log prunable pairs breakdown
        logger.info(f"🔪 Prunable pairs: {len(prunable_pairs)}/{len(eligible_pairs)} (n_total≥{self.MIN_SUPPORT_PRUNE})")
        logger.info(f"   Prunable with lift: {prunable_with_lift}/{len(prunable_pairs)}")
        logger.info(f"   Prunable without lift: {prunable_without_lift}/{len(prunable_pairs)}")
        
        if not prunable_pairs:
            logger.info(f"🔪 Progressive pruning: No pairs have sufficient support (n_total≥{self.MIN_SUPPORT_PRUNE}) for pruning")
            logger.info(f"   Eligible pairs: {len(eligible_pairs)}, but none meet support threshold")
            # Show why pairs aren't prunable
            insufficient_support = 0
            for pair in eligible_pairs[:10]:  # Check first 10
                i, j = pair
                stats_ij = self._pair_stats.get((i, j), {})
                stats_ji = self._pair_stats.get((j, i), {})
                n_total = stats_ij.get('n', 0) + stats_ji.get('n', 0)
                if n_total < self.MIN_SUPPORT_PRUNE:
                    insufficient_support += 1
            if insufficient_support > 0:
                logger.info(f"   Example: {insufficient_support}/10 checked pairs have n_total < {self.MIN_SUPPORT_PRUNE}")
            return
        
        # Sort prunable pairs by importance (LOWEST = least important = disable first)
        prunable_pairs.sort(key=lambda x: x[1], reverse=False)  # LOWEST first
        
        # Disable the N least important prunable pairs
        # Use aggressive target if lift is flat, otherwise use base count
        num_to_disable = min(num_to_disable_target, len(prunable_pairs))
        newly_disabled = []
        
        for pair, importance in prunable_pairs[:num_to_disable]:
            self.disabled_pairs.add(pair)
            newly_disabled.append((pair, importance))
            
            # Score tracking: -1 when culled (worst performing)
            if pair not in self._pair_scores:
                self._pair_scores[pair] = 0
            self._pair_scores[pair] -= 1
        
        # ============================================================================
        # SWAP: Bring in fresh pairs from disabled pool to maintain exploration
        # ============================================================================
        # CRITICAL: Always reactivate at least K_explore pairs per epoch to maintain exploration
        # This ensures the selector can explore alternatives, not just shrink the graph
        # ============================================================================
        newly_reactivated = []
        
        # Calculate K_explore for this run
        log2_N = np.log2(max(2, self.n_cols))
        E = max(1, min(32, int(np.ceil(log2_N))))
        K_explore = E
        
        # Minimum reactivation: K_explore pairs per epoch (ensures exploration continues)
        # Also reactivate up to num_to_disable to maintain pool size (if we're not at target yet)
        min_reactivate = K_explore
        max_reactivate = max(num_to_disable, min_reactivate)  # At least match what we disabled
        
        if self.disabled_pairs:
            # Exclude the ones we JUST disabled - give them at least one epoch off
            just_disabled_set = set(p for p, _ in newly_disabled)
            reactivation_pool = list(self.disabled_pairs - just_disabled_set)
            
            if reactivation_pool:
                # CRITICAL: Reactivate pairs from disabled pool REGARDLESS of lift status
                # - Pairs without lift (never computed, or lost lift when disabled) are eligible
                # - When reactivated, they become active and will regain lift tracking automatically
                # - Lift tracking resumes when they're selected and computed in future batches
                # - This ensures exploration continues even if lift coverage drops
                
                # Reactivate at least K_explore (if available), up to max_reactivate, but never more than pool size
                # Order matters: first cap to pool size, then enforce minimum (but not above pool)
                num_to_reactivate = min(max_reactivate, len(reactivation_pool))
                num_to_reactivate = max(min(min_reactivate, len(reactivation_pool)), num_to_reactivate)
                
                # Sample randomly from disabled pool (no filtering by lift)
                # CRITICAL: Ensure we don't try to sample more than available
                if num_to_reactivate <= 0:
                    logger.warning(f"⚠️  Cannot reactivate: pool size={len(reactivation_pool)}, min_reactivate={min_reactivate}, max_reactivate={max_reactivate}")
                    pairs_to_reactivate = []
                else:
                    pairs_to_reactivate = random.sample(reactivation_pool, num_to_reactivate)
                
                # Track which reactivated pairs have lift vs don't (for diagnostics)
                reactivated_with_lift = 0
                reactivated_without_lift = 0
                
                for pair in pairs_to_reactivate:
                    self.disabled_pairs.remove(pair)
                    newly_reactivated.append(pair)
                    
                    # Check if pair has lift (for diagnostics)
                    i, j = pair
                    stats_ij = self._pair_stats.get((i, j), {})
                    stats_ji = self._pair_stats.get((j, i), {})
                    has_lift_ij = stats_ij.get('lift_ema') is not None
                    has_lift_ji = stats_ji.get('lift_ema') is not None
                    if has_lift_ij or has_lift_ji:
                        reactivated_with_lift += 1
                    else:
                        reactivated_without_lift += 1
                    
                    # Score tracking: +1 when reactivated (exploration)
                    if pair not in self._pair_scores:
                        self._pair_scores[pair] = 0
                    self._pair_scores[pair] += 1  # Increment for being selected/explored
                
                # Log reactivation diagnostics
                if reactivated_without_lift > 0:
                    logger.info(f"   🔄 Reactivation: {reactivated_without_lift}/{len(pairs_to_reactivate)} pairs without lift (will regain tracking when computed)")
        
        # Log what we disabled
        total_pairs = len(self.all_pairs)
        active_after = total_pairs - len(self.disabled_pairs)
        target_remaining = int(total_pairs * self.top_k_fraction)
        target_remaining = max(target_remaining, self.min_relationships_to_keep)
        
        logger.info("")
        logger.info("🔄" * 40)
        logger.info(f"🔄 RELATIONSHIP SWAP - Epoch {self.current_epoch}")
        logger.info(f"   Strategy: Swap out weak pairs, bring in fresh ones to explore")
        logger.info(f"   Metric: Lift-based importance (EMA of causal lift from NULL baseline)")
        logger.info(f"   Disabled {num_to_disable} relationships (lowest lift = least helpful)")
        logger.info(f"   Reactivated {len(newly_reactivated)} relationships (min {K_explore} for exploration)")
        logger.info(f"   Net change: {len(newly_reactivated) - num_to_disable:+d} active pairs")
        logger.info(f"   Active: {active_after}/{total_pairs} ({100*active_after/total_pairs:.1f}%)")
        logger.info(f"   Protected floor: {len(protected_set)} pairs (per-column, degree-capped, max {max_protected_per_column}/col)")
        logger.info(f"   Target: {target_remaining} pairs ({self.top_k_fraction*100:.0f}%)")
        
        if newly_disabled:
            logger.info(f"")
            logger.info(f"   Newly disabled (worst {len(newly_disabled[:5])} of {len(newly_disabled)}):")
            for pair, importance in newly_disabled[:5]:  # Show first 5
                i, j = pair
                col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                # Show lift-based importance (not Δ)
                stats_ij = self._pair_stats.get((i, j), {})
                stats_ji = self._pair_stats.get((j, i), {})
                lift_ij = stats_ij.get('lift_ema', 0.0)
                lift_ji = stats_ji.get('lift_ema', 0.0)
                lift_total = lift_ij + lift_ji
                logger.info(f"      ({col_i} ↔ {col_j}): lift={lift_total:.4f} (i→j={lift_ij:.4f}, j→i={lift_ji:.4f})")
            if len(newly_disabled) > 5:
                logger.info(f"      ... and {len(newly_disabled)-5} more")
        
        # Show reactivated pairs
        if newly_reactivated:
            logger.info(f"")
            logger.info(f"   🔄 Reactivated (random from disabled pool, first {min(5, len(newly_reactivated))} of {len(newly_reactivated)}):")
            logger.info(f"   NOTE: Reactivated pairs will regain lift tracking when computed in future batches")
            for pair in newly_reactivated[:5]:
                i, j = pair
                col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                # Check if pair has lift (may have been computed before being disabled)
                stats_ij = self._pair_stats.get((i, j), {})
                stats_ji = self._pair_stats.get((j, i), {})
                has_lift = stats_ij.get('lift_ema') is not None or stats_ji.get('lift_ema') is not None
                lift_status = "has lift" if has_lift else "no lift (will regain when computed)"
                # These pairs haven't been evaluated recently, so no loss info
                prev_score = self._pair_scores.get(pair, 0)
                logger.info(f"      ({col_i} ↔ {col_j}): prev_score={prev_score} [{lift_status}]")
            if len(newly_reactivated) > 5:
                logger.info(f"      ... and {len(newly_reactivated)-5} more")
        
        # Show top 5 protected relationships
        if protected_set:
            logger.info(f"")
            logger.info(f"   Top 5 protected relationships (will NEVER be disabled):")
            for pair, importance in protected_pairs[:5]:
                i, j = pair
                col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                # Show lift-based importance (not Δ)
                stats_ij = self._pair_stats.get((i, j), {})
                stats_ji = self._pair_stats.get((j, i), {})
                lift_ij = stats_ij.get('lift_ema', 0.0)
                lift_ji = stats_ji.get('lift_ema', 0.0)
                lift_total = lift_ij + lift_ji
                logger.info(f"      ({col_i} ↔ {col_j}): lift={lift_total:.4f} (i→j={lift_ij:.4f}, j→i={lift_ji:.4f})")
        
        # Log score distribution across ALL pairs (not just active)
        all_scores = list(self._pair_scores.values())
        if all_scores:
            score_mean = np.mean(all_scores)
            score_std = np.std(all_scores) if len(all_scores) > 1 else 0.0
            score_min = np.min(all_scores)
            score_max = np.max(all_scores)
            n_positive = sum(1 for s in all_scores if s > 0)
            n_negative = sum(1 for s in all_scores if s < 0)
            n_zero = sum(1 for s in all_scores if s == 0)
            logger.info(f"")
            logger.info(f"   📈 Cumulative scores across ALL {len(all_scores)} pairs:")
            logger.info(f"      Mean: {score_mean:.2f}  Std: {score_std:.2f}  Range: [{score_min}, {score_max}]")
            logger.info(f"      Positive (kept often): {n_positive}  Negative (culled often): {n_negative}  Zero (neutral): {n_zero}")
        
        # ============================================================================
        # DIAGNOSTIC A: Lift quantiles (to see tail mass shrinking)
        # ============================================================================
        # Get active pairs AFTER pruning (for accurate diagnostics)
        active_pairs_after = [p for p in self.all_pairs if p not in self.disabled_pairs]
        
        active_lift_values = []
        for pair in active_pairs_after:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            lift_ij = stats_ij.get('lift_ema')
            lift_ji = stats_ji.get('lift_ema')
            
            # Use total lift if both directions available, otherwise use available one
            if lift_ij is not None and lift_ji is not None:
                lift_total = lift_ij + lift_ji
                if math.isfinite(lift_total):
                    active_lift_values.append(lift_total)
            elif lift_ij is not None and math.isfinite(lift_ij):
                active_lift_values.append(lift_ij)
            elif lift_ji is not None and math.isfinite(lift_ji):
                active_lift_values.append(lift_ji)
        
        if active_lift_values:
            quantiles = np.percentile(active_lift_values, [10, 25, 50, 75, 90])
            logger.info(f"")
            logger.info(f"   📊 Lift quantiles (active pairs, n={len(active_lift_values)}):")
            logger.info(f"      p10: {quantiles[0]:.4f}  p25: {quantiles[1]:.4f}  p50: {quantiles[2]:.4f}  p75: {quantiles[3]:.4f}  p90: {quantiles[4]:.4f}")
        
        # ============================================================================
        # DIAGNOSTIC B: Pruning gain proxy (active_mean - disabled_mean)
        # ============================================================================
        # Compute mean lift of active pairs
        if active_lift_values:
            active_mean_lift = np.mean(active_lift_values)
        else:
            active_mean_lift = None
        
        # Compute mean lift of disabled pairs (if they still have cached lift)
        disabled_lift_values = []
        for pair in self.disabled_pairs:
            i, j = pair
            stats_ij = self._pair_stats.get((i, j), {})
            stats_ji = self._pair_stats.get((j, i), {})
            lift_ij = stats_ij.get('lift_ema')
            lift_ji = stats_ji.get('lift_ema')
            
            # Use total lift if both directions available, otherwise use available one
            if lift_ij is not None and lift_ji is not None:
                lift_total = lift_ij + lift_ji
                if math.isfinite(lift_total):
                    disabled_lift_values.append(lift_total)
            elif lift_ij is not None and math.isfinite(lift_ij):
                disabled_lift_values.append(lift_ij)
            elif lift_ji is not None and math.isfinite(lift_ji):
                disabled_lift_values.append(lift_ji)
        
        if disabled_lift_values:
            disabled_mean_lift = np.mean(disabled_lift_values)
        else:
            disabled_mean_lift = None
        
        # Print pruning gain proxy
        if active_mean_lift is not None and disabled_mean_lift is not None:
            pruning_gap = active_mean_lift - disabled_mean_lift
            logger.info(f"")
            logger.info(f"   🎯 Pruning gain proxy:")
            logger.info(f"      Active mean lift: {active_mean_lift:.4f} (n={len(active_lift_values)})")
            logger.info(f"      Disabled mean lift: {disabled_mean_lift:.4f} (n={len(disabled_lift_values)})")
            logger.info(f"      Gap (active - disabled): {pruning_gap:+.4f} {'✅' if pruning_gap > 0 else '⚠️'}")
        elif active_mean_lift is not None:
            logger.info(f"")
            logger.info(f"   🎯 Pruning gain proxy:")
            logger.info(f"      Active mean lift: {active_mean_lift:.4f} (n={len(active_lift_values)})")
            logger.info(f"      Disabled mean lift: N/A (no cached lift in disabled pairs)")
        elif disabled_mean_lift is not None:
            logger.info(f"")
            logger.info(f"   🎯 Pruning gain proxy:")
            logger.info(f"      Active mean lift: N/A (no lift in active pairs)")
            logger.info(f"      Disabled mean lift: {disabled_mean_lift:.4f} (n={len(disabled_lift_values)})")
        
        logger.info("🔄" * 40)
        logger.info("")
        
        # Score tracking and batch update to monitor
        # Only update pairs that were EVALUATED this epoch (eligible + protected)
        # Don't send all active pairs - only the ones we considered for pruning
        
        # Keeps: Eligible pairs that SURVIVED this pruning (were at risk but kept)
        # These are the pairs that were evaluated and decided to keep for now
        surviving_eligible = [p for p in eligible_pairs if p not in self.disabled_pairs]
        
        # ============================================================================
        # CUMULATIVE SCORE TRACKING: Track selection frequency for UCB/exploration
        # ============================================================================
        # CRITICAL: Increment scores for ALL pairs that are ACTIVE this epoch
        # This ensures "kept often" reflects actual selection frequency, not just
        # "never disabled" (which would be all pairs initially)
        # ============================================================================
        # All pairs that are currently active (after pruning) were selected/kept
        final_active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        for pair in final_active_pairs:
            if pair not in self._pair_scores:
                self._pair_scores[pair] = 0
            self._pair_scores[pair] += 1  # Increment for being selected/kept this epoch
        
        # Post scores to featrix-monitor if we have a dataset hash
        if self._dataset_hash and (newly_disabled or surviving_eligible):
            try:
                from featrix_monitor import create_client
                client = create_client()
                
                # Build keeps list (eligible pairs that survived this pruning)
                keeps = []
                for pair in surviving_eligible:
                    i, j = pair
                    col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                    col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                    keeps.append({
                        "columns": [col_i, col_j],
                        "difficulty_scores": {
                            col_i: self.col_marginal_losses.get(col_i, 0.0),
                            col_j: self.col_marginal_losses.get(col_j, 0.0)
                        },
                        "epoch_idx": self.current_epoch,
                        "metadata": {
                            "session_id": self._session_id or "unknown",
                            "importance": importance_scores.get(pair, 0.0)
                        }
                    })
                
                # Build culls list (pairs that were just disabled)
                culls = []
                for pair, importance in newly_disabled:
                    i, j = pair
                    col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                    col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                    culls.append({
                        "columns": [col_i, col_j],
                        "difficulty_scores": {
                            col_i: self.col_marginal_losses.get(col_i, 0.0),
                            col_j: self.col_marginal_losses.get(col_j, 0.0)
                        },
                        "epoch_idx": self.current_epoch,
                        "metadata": {
                            "session_id": self._session_id or "unknown",
                            "importance": importance,
                            "reason": "lowest importance (easiest columns)"
                        }
                    })
                
                # Batch update all at once (async, non-blocking)
                result = client.batch_update_pair_scores(
                    dataset_hash=self._dataset_hash,
                    keeps=keeps,
                    culls=culls
                )
                
                logger.info(f"📊 Batch updated pair scores: {result['keeps_updated']} keeps, {result['culls_updated']} culls")
                if result.get('errors'):
                    logger.warning(f"   ⚠️  {len(result['errors'])} pairs failed to update")
                
            except Exception as e:
                logger.debug(f"Failed to post relationship scores to monitor: {e}")
                # Don't fail training if monitor posting fails
    
    def finalize_training_and_validate(self):
        """
        STAGE 3: Validate importance scoring at end of training.
        
        This validates that our causal importance scores actually predict
        which pairs help vs hurt. Reports:
        - Rank correlation (high importance → high actual lift?)
        - Top 20% pairs: Do they actually help? (mean lift > 0)
        - Bottom 20% pairs: Do they hurt/neutral? (mean lift ≤ 0)
        - False positives: High importance but negative lift
        - False negatives: Low importance but positive lift
        
        This is FREE validation - uses data we're already tracking.
        """
        logger.info("")
        logger.info("="*80)
        logger.info("🔍 VALIDATING IMPORTANCE SCORING")
        logger.info("="*80)
        
        try:
            # Get final importance scores
            importance_scores = self._compute_relationship_importance()
            
            # Validate against actual observed lift
            report = self.validator.validate_importance_scoring(importance_scores)
            
            # Print detailed report
            self.validator.print_validation_report(report)
            
            # Save to file for analysis
            try:
                import json
                import os
                
                validation_path = 'importance_validation.json'
                with open(validation_path, 'w') as f:
                    json.dump({
                        'grade': report.grade(),
                        'valid': report.is_valid(),
                        'rank_correlation': report.rank_correlation,
                        'rank_correlation_pvalue': report.rank_correlation_pvalue,
                        'top_20_mean_lift': report.top_20_mean_lift,
                        'top_20_pct_positive': report.top_20_pct_positive,
                        'bottom_20_mean_lift': report.bottom_20_mean_lift,
                        'bottom_20_pct_positive': report.bottom_20_pct_positive,
                        'n_false_positives': len(report.false_positives),
                        'n_false_negatives': len(report.false_negatives),
                        'n_pairs_total': report.n_pairs_total,
                    }, f, indent=2)
                
                logger.info(f"📄 Validation report saved to: {validation_path}")
            except Exception as e:
                logger.warning(f"Failed to save validation report: {e}")
            
            # Return validation result
            return report
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def __getstate__(self):
        """
        Custom pickle state - save all instance attributes that aren't automatically saved by nn.Module.
        nn.Module's default __getstate__ only saves parameters and buffers, not regular instance attributes.
        """
        # Get the default state (parameters, buffers, etc.)
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self, state):
        """
        Custom unpickle state - restore all instance attributes.
        After restoring, ensure any missing attributes are initialized for backward compatibility.
        """
        # Restore all attributes
        self.__dict__.update(state)
        
        # Ensure all required attributes are initialized (for backward compatibility)
        # This handles cases where old checkpoints don't have newer attributes
        self._ensure_pair_stats_attributes()
        self._ensure_null_baseline_attributes()

