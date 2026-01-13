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
from typing import Dict, List, Optional, Tuple, Set

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


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
    
    # Reserve only 10% of GPU for relationship pairs
    # The rest is for: model, column encodings, attention, gradients, optimizer, fragmentation
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
    # Even on huge GPUs, limit to 1000 to avoid fragmentation and ensure stability
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
        
        # Generate all unique pairs (i < j to avoid duplicates)
        # This gives us N*(N-1)/2 pairs, not N*N
        self.all_pairs = []
        for i in range(self.n_cols):
            for j in range(i + 1, self.n_cols):
                self.all_pairs.append((i, j))
        
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
    
    def forward(
        self,
        column_encodings: torch.Tensor,  # (batch_size, n_cols, d_model)
        mask: Optional[torch.Tensor] = None,  # (batch_size, n_cols)
    ) -> List[torch.Tensor]:
        """
        Extract relationship features from column encodings.
        
        Returns:
            List of relationship token tensors, each (batch_size, d_model)
        """
        # Clear previous batch's tokens to avoid accumulation
        self._tokens_for_gradient_check.clear()
        
        batch_size, n_cols, d_model = column_encodings.shape
        
        # Determine which pairs to compute
        if self.progressive_pruning:
            # Progressive pruning: Start with all pairs, gradually disable unimportant ones
            # Filter out disabled pairs
            pairs_to_compute = [p for p in self.all_pairs if p not in self.disabled_pairs]
            # Still exploring if we haven't started disabling yet
            is_exploration = (self.current_epoch < self.exploration_epochs)
        elif self.pruned_pairs_per_column is None:
            # Old method: Hard cutoff at exploration_epochs
            pairs_to_compute = self.all_pairs
            is_exploration = True
        else:
            # Old method: Phase 2 focused - compute only pruned pairs
            pairs_to_compute = self._pruned_pairs_list
            is_exploration = False
        
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
                self._sample_rng = np.random.RandomState(42)
            
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
                
                # CRITICAL FIX: Detach tokens to prevent gradient accumulation across chunks
                # This breaks the computation graph, freeing intermediate tensors
                # Gradients will still flow within each chunk, just not across chunks
                chunk_tokens_detached = [t.detach() for t in chunk_tokens]
                all_tokens.extend(chunk_tokens_detached)
                
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
    
    def _compute_weight_stats(self) -> Dict[str, Dict[str, float]]:
        """Compute weight statistics for each operation MLP."""
        stats = {}
        for op_name, mlp in [
            ('multiply', self.multiply_mlp),
            ('add', self.add_mlp),
            ('subtract', self.subtract_mlp),
            ('divide', self.divide_mlp),
        ]:
            total_params = 0
            total_norm = 0.0
            total_grad_norm = 0.0
            has_grad = False
            
            for param in mlp.parameters():
                if param.requires_grad:
                    total_params += param.numel()
                    total_norm += param.data.norm().item() ** 2
                    if param.grad is not None:
                        total_grad_norm += param.grad.norm().item() ** 2
                        has_grad = True
            
            stats[op_name] = {
                'weight_norm': total_norm ** 0.5,
                'grad_norm': total_grad_norm ** 0.5 if has_grad else 0.0,
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
        
        logger.info("")
        logger.info("=" * 100)
        logger.info(f"🔗 DYNAMIC RELATIONSHIP EXTRACTOR - EPOCH {self.current_epoch} SUMMARY")
        logger.info("=" * 100)
        
        # LEARNING CHECK: Are the operation MLPs learning?
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
            
            logger.info(f"   {op:<12} {stats['weight_norm']:>10.4f} {stats['grad_norm']:>12.6f} {delta:>12.6f} {learning_str:>12}")
        
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
        
        # 2. RELATIONSHIP IMPORTANCE (using loss-based metric)
        importance_scores = self._compute_relationship_importance()
        
        # Sort by importance DESCENDING (higher = more important)
        sorted_pairs = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        total_pairs = len(sorted_pairs)
        active_pairs_count = total_pairs - len(self.disabled_pairs)
        
        logger.info(f"🏆 Top 20 Most Important Relationships (high Δ = easy↔hard pairing):")
        for rank, ((i, j), importance) in enumerate(sorted_pairs[:20], 1):
            col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
            col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
            loss_i = self.col_marginal_losses.get(col_i, 0.0)
            loss_j = self.col_marginal_losses.get(col_j, 0.0)
            is_active = (i, j) not in self.disabled_pairs
            status = "✓" if is_active else "✗"
            logger.info(f"   {rank:2d}. ({col_i} ↔ {col_j}): Δ={importance:.4f} ({loss_i:.4f} vs {loss_j:.4f}) [{status}]")
        
        # Bottom 20 relationships (lowest importance = both columns at similar difficulty = prune candidates)
        logger.info(f"")
        logger.info(f"📉 Bottom 20 Least Important Relationships (low Δ = same-tier pairing):")
        for rank, ((i, j), importance) in enumerate(reversed(sorted_pairs[-20:]), 1):
            col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
            col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
            loss_i = self.col_marginal_losses.get(col_i, 0.0)
            loss_j = self.col_marginal_losses.get(col_j, 0.0)
            is_active = (i, j) not in self.disabled_pairs
            status = "✓" if is_active else "✗"
            logger.info(f"   {rank:2d}. ({col_i} ↔ {col_j}): Δ={importance:.4f} ({loss_i:.4f} vs {loss_j:.4f}) [{status}]")
        
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
        
        logger.info("=" * 100)
        logger.info("")
    
    def log_exploration_progress(self):
        """Log relationship importance stats using loss-based metric."""
        if not self.training:
            return
        
        logger.info("")
        logger.info(f"🔍 RELATIONSHIP EXPLORATION (epoch {self.current_epoch})")
        
        # Use loss-based importance instead of gradient contributions
        if not self.col_marginal_losses:
            logger.info("   ⏳ Waiting for column loss data...")
            return
        
        # Calculate importance scores
        importance_scores = self._compute_relationship_importance()
        
        # Calculate statistics
        importance_values = list(importance_scores.values())
        mean_importance = np.mean(importance_values)
        std_importance = np.std(importance_values)
        max_importance = np.max(importance_values)
        min_importance = np.min(importance_values)
        
        active_pairs = len(self.all_pairs) - len(self.disabled_pairs)
        
        logger.info(f"   Loss-based importance (max of column losses):")
        logger.info(f"   Mean: {mean_importance:.4f} ± {std_importance:.4f}")
        logger.info(f"   Range: [{min_importance:.4f}, {max_importance:.4f}]")
        logger.info(f"   Active pairs: {active_pairs}/{len(self.all_pairs)}")
        
        # Top 5 pairs by importance
        sorted_pairs = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"   Top 5 pairs:")
        for (i, j), importance in sorted_pairs[:5]:
            col_i = self.col_names[i]
            col_j = self.col_names[j]
            loss_i = self.col_marginal_losses.get(col_i, 0.0)
            loss_j = self.col_marginal_losses.get(col_j, 0.0)
            logger.info(f"      {col_i:<20} ↔ {col_j:<20}: Δ={importance:.4f} ({loss_i:.4f} vs {loss_j:.4f})")
    
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
        logger.info(f"      Mean contribution: {np.mean(kept_contribs):.6f}")
        logger.info(f"      Min contribution:  {np.min(kept_contribs):.6f}")
        logger.info(f"      Max contribution:  {np.max(kept_contribs):.6f}")
        
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
            
            # Handle case where all values are zero
            if np.std(prev_vals) == 0 or np.std(curr_vals) == 0:
                corr = 0.0
            else:
                corr = np.corrcoef(prev_vals, curr_vals)[0, 1]
            correlations.append(corr)
        
        logger.info("")
        logger.info("📊 RELATIONSHIP STABILITY:")
        logger.info(f"   Mean epoch-to-epoch correlation: {np.mean(correlations):.3f}")
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
    
    def update_column_losses(self, col_losses_dict: Dict[str, float]):
        """
        Update per-column marginal losses from encoder.
        
        This is the CRITICAL metric for relationship importance!
        
        Args:
            col_losses_dict: {col_name: avg_marginal_loss_for_column}
                Higher loss = harder to predict = more important column
        
        Relationships between high-loss (hard) columns are most valuable.
        Relationships between low-loss (easy) columns can be pruned.
        """
        self.col_marginal_losses = col_losses_dict.copy() if col_losses_dict else {}
        
        # Log column losses if available (useful for debugging)
        if logger.isEnabledFor(logging.DEBUG) and col_losses_dict:
            loss_items = sorted(col_losses_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            loss_strs = [f"{k}={v:.4f}" for k, v in loss_items]
            logger.debug(f"📊 DynamicRelationshipExtractor: Updated column losses (top 5 hardest): {', '.join(loss_strs)}")
    
    def _compute_relationship_importance(self) -> Dict[Tuple[int, int], float]:
        """
        Compute importance score for each relationship based on PREDICTABILITY DISTANCE.
        
        METRIC: |loss_i - loss_j| (absolute difference in predictability)
        
        Importance(col_i ↔ col_j) = |marginal_loss[col_i] - marginal_loss[col_j]|
        
        Logic:
          - Pairs with columns FAR APART in predictability are most valuable
          - Easy ↔ Hard: High distance → TOP PRIORITY (easy can teach hard)
          - Easy ↔ Medium or Medium ↔ Hard: Moderate distance → USEFUL
          - Same tier pairs (Easy↔Easy, Medium↔Medium, Hard↔Hard): Low distance → PRUNE
          
        The intuition: if column A has "figured something out" (low loss) and column B
        is struggling (high loss), the relationship A ↔ B helps B learn from A.
        Pairing two columns at the same difficulty level provides no teaching signal.
        
        We keep the top ~25% of pairs by predictability distance (configurable via
        progressive_pruning settings). Pairs where both columns are similarly easy,
        medium, or hard get pruned as they add compute cost without teaching value.
        
        Returns:
            {(col_i, col_j): importance_score}
            Higher score = more important = keep this relationship
        """
        importance = {}
        
        if not self.col_marginal_losses:
            # Fallback: if no losses available yet, use uniform importance
            logger.debug("⚠️  No column marginal losses available yet for importance calculation (using uniform)")
            for pair in self.all_pairs:
                importance[pair] = 1.0
            return importance
        
        for (col_i, col_j) in self.all_pairs:
            col_i_name = self.col_names[col_i]
            col_j_name = self.col_names[col_j]
            
            # Get marginal losses (higher = harder to predict)
            loss_i = self.col_marginal_losses.get(col_i_name, 0.0)
            loss_j = self.col_marginal_losses.get(col_j_name, 0.0)
            
            # Safety: Skip pairs with invalid losses
            if math.isnan(loss_i) or math.isinf(loss_i) or math.isnan(loss_j) or math.isinf(loss_j):
                logger.warning(f"⚠️  Invalid loss for pair ({col_i_name}, {col_j_name}): {loss_i}, {loss_j}")
                importance[(col_i, col_j)] = 0.0
                continue
            
            # Importance = PREDICTABILITY DISTANCE
            # Pairs where columns are far apart (easy↔hard) score highest
            # Pairs where columns are similar (same tier) score lowest and get pruned
            importance[(col_i, col_j)] = abs(loss_i - loss_j)
        
        return importance
    
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
        Progressively disable the least important relationships based on PREDICTABILITY DISTANCE.
        Called once per epoch after exploration phase.
        
        METRIC: |marginal_loss[A] - marginal_loss[B]| (absolute difference)
        
        Importance(A ↔ B) = |marginal_loss[A] - marginal_loss[B]|
          
        Higher distance = easy↔hard pairing = relationship is VALUABLE (easy teaches hard)
        Lower distance = same-tier pairing = relationship is NOISE (can prune)
          
        Logic: pairs where one column has "figured it out" (low loss) and the other
        is struggling (high loss) are most valuable. Pairs where both columns are at
        the same difficulty level (both easy, both medium, both hard) add compute
        cost without teaching value.
        
        Rules:
        1. Sort all pairs by predictability distance (HIGHEST = most important)
        2. Always keep top min_relationships_to_keep pairs (safety floor)
        3. From remaining pairs, disable pairs_to_prune_per_epoch with LOWEST distance
        """
        if not self.should_progressive_prune():
            return
        
        # Get currently active pairs
        active_pairs = [p for p in self.all_pairs if p not in self.disabled_pairs]
        
        if not active_pairs:
            return
        
        # CRITICAL: Use new loss-based importance metric instead of gradients
        importance_scores = self._compute_relationship_importance()
        
        # Sort all active pairs by importance (HIGHEST first = most important first)
        pairs_by_importance = [(p, importance_scores[p]) for p in active_pairs]
        pairs_by_importance.sort(key=lambda x: x[1], reverse=True)  # HIGHEST first
        
        # Keep the most important pairs (safety floor)
        protected_pairs = pairs_by_importance[:self.min_relationships_to_keep]
        protected_set = {p for p, _ in protected_pairs}
        
        # Eligible for disabling: everything except protected pairs
        eligible_pairs = [p for p, _ in pairs_by_importance[self.min_relationships_to_keep:]]
        
        if not eligible_pairs:
            logger.info(f"🔪 Progressive pruning: All {len(active_pairs)} active pairs are protected (below minimum floor)")
            return
        
        # Sort eligible pairs by importance (LOWEST = least important = disable first)
        eligible_with_importance = [(p, importance_scores[p]) for p in eligible_pairs]
        eligible_with_importance.sort(key=lambda x: x[1], reverse=False)  # LOWEST first
        
        # Disable the N least important eligible pairs
        num_to_disable = min(self.pairs_to_prune_per_epoch, len(eligible_pairs))
        newly_disabled = []
        
        for pair, importance in eligible_with_importance[:num_to_disable]:
            self.disabled_pairs.add(pair)
            newly_disabled.append((pair, importance))
            
            # Score tracking: -1 when culled (worst performing)
            if pair not in self._pair_scores:
                self._pair_scores[pair] = 0
            self._pair_scores[pair] -= 1
        
        # Log what we disabled
        total_pairs = len(self.all_pairs)
        active_after = total_pairs - len(self.disabled_pairs)
        target_remaining = int(total_pairs * self.top_k_fraction)
        target_remaining = max(target_remaining, self.min_relationships_to_keep)
        
        logger.info("")
        logger.info("🔪" * 40)
        logger.info(f"🔪 PROGRESSIVE PRUNING - Epoch {self.current_epoch}")
        logger.info(f"   Strategy: Keep relationships where AT LEAST ONE column is hard to predict")
        logger.info(f"   Metric: importance = max(marginal_loss[col_i], marginal_loss[col_j])")
        logger.info(f"   Disabled {num_to_disable} relationships (lowest importance = easiest columns)")
        logger.info(f"   Active: {active_after}/{total_pairs} ({100*active_after/total_pairs:.1f}%)")
        logger.info(f"   Protected floor: {self.min_relationships_to_keep} most important pairs (never disabled)")
        logger.info(f"   Target: {target_remaining} pairs ({self.top_k_fraction*100:.0f}%)")
        
        if newly_disabled:
            logger.info(f"")
            logger.info(f"   Newly disabled (worst {len(newly_disabled[:5])} of {len(newly_disabled)}):")
            for pair, importance in newly_disabled[:5]:  # Show first 5
                i, j = pair
                col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                loss_i = self.col_marginal_losses.get(col_i, 0.0)
                loss_j = self.col_marginal_losses.get(col_j, 0.0)
                logger.info(f"      ({col_i} ↔ {col_j}): Δ={importance:.4f} ({loss_i:.4f} vs {loss_j:.4f})")
            if len(newly_disabled) > 5:
                logger.info(f"      ... and {len(newly_disabled)-5} more")
        
        # Show top 5 protected relationships
        if protected_set:
            logger.info(f"")
            logger.info(f"   Top 5 protected relationships (will NEVER be disabled):")
            for pair, importance in protected_pairs[:5]:
                i, j = pair
                col_i = self.col_names[i] if i < len(self.col_names) else f"col_{i}"
                col_j = self.col_names[j] if j < len(self.col_names) else f"col_{j}"
                loss_i = self.col_marginal_losses.get(col_i, 0.0)
                loss_j = self.col_marginal_losses.get(col_j, 0.0)
                logger.info(f"      ({col_i} ↔ {col_j}): Δ={importance:.4f} ({loss_i:.4f} vs {loss_j:.4f})")
        
        logger.info("🔪" * 40)
        logger.info("")
        
        # Score tracking and batch update to monitor
        # Only update pairs that were EVALUATED this epoch (eligible + protected)
        # Don't send all active pairs - only the ones we considered for pruning
        
        # Keeps: Eligible pairs that SURVIVED this pruning (were at risk but kept)
        # These are the pairs that were evaluated and decided to keep for now
        surviving_eligible = [p for p in eligible_pairs if p not in self.disabled_pairs]
        
        # Track scores for surviving pairs
        for pair in surviving_eligible:
            if pair not in self._pair_scores:
                self._pair_scores[pair] = 0
            self._pair_scores[pair] += 1
        
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

