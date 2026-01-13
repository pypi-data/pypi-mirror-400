import math
from dataclasses import dataclass
from typing import Optional
import logging

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

from featrix.neural.featrix_module_dict import FeatrixModuleDict
from featrix.neural.model_config import JointEncoderConfig
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.relationship_extractor import RelationshipFeatureExtractor
from featrix.neural.gpu_utils import is_gpu_available, get_gpu_memory_allocated, get_gpu_memory_reserved

logger = logging.getLogger(__name__)

def _log_gpu_memory_transformer(context: str = ""):
    """Quick GPU memory logging for tracing memory usage in transformer_encoder."""
    try:
        if not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()
        reserved = get_gpu_memory_reserved()
        logger.info(f"📊 GPU [{context}]: Alloc={allocated:.2f}GB Reserved={reserved:.2f}GB")
    except Exception:
        pass


class AddCLSToken(nn.Module):
    def __init__(self, d_model):
        super().__init__()

        self.d_model = d_model

        # Initialize the [CLS] token as a learnable parameter
        self.cls_token = nn.Parameter(
            torch.randn(self.d_model) / math.sqrt(self.d_model)
        )

    def forward(self, x):
        # x has shape (B, S, F)

        # Replicate the [CLS] token for all sequences in the batch
        # self.cls_token has shape (F,)
        cls_tokens = self.cls_token.repeat(x.size(0), 1, 1)  # Shape: (B, 1, F)

        # Concatenate the [CLS] token with sequences
        x = torch.cat([cls_tokens, x], dim=1)  # Shape: (B, S+1, F)

        return x


class ColumnEncoding(nn.Module):
    def __init__(self, d_model, seq_len):
        super().__init__()

        #  we add an encoding for the cls token, which always gets prepended as the 0th element
        n_encodings = seq_len

        # Initialize a tensor for positional encodings and set it as a learnable parameter
        # NOTE: this assumes the input comes in the form (sequence, feature)
        self.pos_embedding = nn.Parameter(
            torch.randn(n_encodings, d_model) / math.sqrt(d_model)
        )

        # NOTE: this could be accomplished with an Embedding module, but that would get more
        # cumbersome. Going with a simple single parameter as above is much better.

    def forward(self, x):
        # assume x is in the format (batch, seq, feat)
        # the positional embedding_space gets broadcast across the batch dimension

        return x + self.pos_embedding


# def apply_network_to_tensor(data, network):
#     N, M, K = data.shape

#     # Reshape data to (N*M, K) for batch processing
#     data_reshaped = data.view(N * M, K)

#     # Apply network
#     output = network(data_reshaped)

#     # Reshape output back to (N, M, output_dim)
#     # Assuming output dimension is the same as input K for simplicity
#     output_dim = output.shape[-1]
#     output_reshaped = output.view(N, M, output_dim)

#     return output_reshaped


class JointEncoder(nn.Module):
    def __init__(self, d_embed, col_names_in_order, config: JointEncoderConfig, hybrid_groups=None, enable_gradient_checkpointing: bool = True):
        super().__init__()

        self.d_embed = d_embed
        self.config = config
        self.enable_gradient_checkpointing = enable_gradient_checkpointing

        self.col_names_in_order = col_names_in_order
        self.hybrid_groups = hybrid_groups or {}
        
        # Create in_converters, handling hybrid group names
        in_converters_dict = {}
        for col_name in col_names_in_order:
            # Check if this is a hybrid group name
            if col_name in self.hybrid_groups:
                # For hybrid groups, use the config from the first original column
                group_info = self.hybrid_groups[col_name]
                original_columns = group_info.get('columns', [])
                if original_columns:
                    # Use config from first column in the group
                    original_col_name = original_columns[0]
                    if original_col_name in config.in_converter_configs:
                        in_converters_dict[col_name] = SimpleMLP(config.in_converter_configs[original_col_name])
                    else:
                        raise KeyError(f"Hybrid group '{col_name}' references column '{original_col_name}' which is not in in_converter_configs. Available keys: {list(config.in_converter_configs.keys())}")
                else:
                    raise ValueError(f"Hybrid group '{col_name}' has no columns defined")
            else:
                # Regular column, use its config directly
                if col_name in config.in_converter_configs:
                    in_converters_dict[col_name] = SimpleMLP(config.in_converter_configs[col_name])
                else:
                    raise KeyError(f"Column '{col_name}' not found in in_converter_configs. Available keys: {list(config.in_converter_configs.keys())}")
        
        self.in_converters = FeatrixModuleDict(in_converters_dict)

        self.out_converter = SimpleMLP(config=config.out_converter_config)
        self.batch_norm_out = nn.BatchNorm1d(d_embed)

        # Dynamic Relationship Extractor (always enabled if relationship_features config exists)
        self.relationship_extractor = None
        # Use getattr for backward compatibility with old pickles that don't have relationship_features
        relationship_features = getattr(config, 'relationship_features', None)
        if relationship_features is not None:
            from featrix.neural.dynamic_relationship_extractor import DynamicRelationshipExtractor
            
            rel_config = relationship_features
            exploration_epochs = getattr(rel_config, 'exploration_epochs', 5)
            top_k_fraction = getattr(rel_config, 'top_k_fraction', 0.25)
            
            self.relationship_extractor = DynamicRelationshipExtractor(
                d_model=config.d_model,
                col_names_in_order=col_names_in_order,
                exploration_epochs=exploration_epochs,
                top_k_fraction=top_k_fraction,
            )
            logger.info(
                f"🔗 JointEncoder: Dynamic relationship extractor enabled "
                f"(exploration_epochs={exploration_epochs}, "
                f"top_k_fraction={top_k_fraction}, "
                f"operations=6 per pair: *, +, -, /, both directions)"
            )

        # Trainable Positional Encoding
        # NOTE: Positional encoding needs to account for:
        # - Column tokens (positions 0 to n_cols-1) - ColumnEncoding receives input BEFORE CLS token
        # - CLS token (position n_cols) - added after ColumnEncoding
        # - Relationship tokens (positions n_cols+1 onwards, variable count)
        # ColumnEncoding is called BEFORE CLS token is added, so it only needs n_cols positions
        # Relationship tokens get positional encodings manually from the extended embedding
        col_seq_len = config.n_cols  # Columns only (CLS added later)
        
        # Calculate max sequence length for positional embedding
        # With POOLED RELATIONSHIP INJECTION, we no longer concatenate relationship tokens
        # to the sequence, so seq_len = 1 (CLS) + n_cols only
        # This is the key to scaling: attention is O(N²) not O((N + N²)²)
        max_seq_len = 1 + config.n_cols  # CLS + columns only
        
        if getattr(self, 'relationship_extractor', None):
            # Relationship tokens are now pooled and injected into CLS, not concatenated
            # Log the relationship token count for debugging purposes
            n_pairs = config.n_cols * (config.n_cols - 1) // 2
            # Query ops_per_pair from extractor (1 if fused, 9 if unfused)
            operations_per_pair = getattr(self.relationship_extractor, 'ops_per_pair', 1)
            n_rel_tokens = n_pairs * operations_per_pair
            fusion_mode = "FUSED" if operations_per_pair == 1 else "UNFUSED"
            logger.info(f"   Relationship tokens: {n_rel_tokens} ({fusion_mode}, pooled, not in sequence)")
            logger.info(f"   Sequence length: {max_seq_len} (CLS + {config.n_cols} cols) - SCALABLE")
        
        if config.use_col_encoding:
            # ColumnEncoding receives columns BEFORE CLS token, so use col_seq_len
            self.col_encoder = ColumnEncoding(self.config.d_model, col_seq_len)
            # Store max_seq_len for relationship token positional encoding
            self.max_seq_len = max_seq_len

        # simple module to add the cls token to create the joint encoding for the whole sequence
        self.add_cls_token = AddCLSToken(self.config.d_model)

        # HYBRID COLUMN SUPPORT: Setup hybrid relationships (hybrid_groups already stored above)
        self._setup_hybrid_relationships()

        # Transformer Encoder with batch_first=True for better performance
        encoder_layer = nn.TransformerEncoderLayer(
            self.config.d_model,
            self.config.n_heads,
            dim_feedforward=self.config.d_model * self.config.dim_feedforward_factor,
            dropout=self.config.dropout,
            batch_first=True,  # Enable nested tensor optimization
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=self.config.n_layers
        )
        
        # Enable gradient checkpointing to save memory (trades compute for memory)
        # This reduces activation memory by ~N_layers times at ~30% compute cost
        # Implemented using torch.utils.checkpoint.checkpoint() wrapper in forward()
        if self.enable_gradient_checkpointing and self.config.n_layers > 1:
            logger.info(f"🔋 Enabling gradient checkpointing on {self.config.n_layers}-layer transformer (saves ~{self.config.n_layers}× activation memory)")
        
        # ============================================================================
        # TIER 3: LOCAL ATTENTION FOR RELATIONSHIP SELECTION
        # ============================================================================
        # Local attention allows each column to selectively attend over its K relationship
        # candidates (exploit + explore + NULL) instead of pooling all relationships into CLS.
        # This enables per-column relationship selection and better scaling.
        # ============================================================================
        if self.relationship_extractor is not None:
            # Local attention for Tier 3 relationship selection
            self.local_attention = nn.MultiheadAttention(
                embed_dim=self.config.d_model,
                num_heads=self.config.n_heads,  # Use same number of heads as main transformer
                dropout=self.config.dropout if hasattr(self.config, 'dropout') else 0.1,
                batch_first=True,
            )
            self.local_attn_dropout = nn.Dropout(self.config.dropout if hasattr(self.config, 'dropout') else 0.1)
            
            # Gate for relationship injection (allows model to damp relationships early)
            self.local_attn_gate = nn.Sequential(
                nn.Linear(self.config.d_model, self.config.d_model),
                nn.Sigmoid()
            )
            logger.info(f"🔗 Tier 3 local attention enabled (per-column relationship selection)")
        else:
            self.local_attention = None
            self.local_attn_dropout = None
            self.local_attn_gate = None
        
        # Storage for attention weights (for diagnostics)
        self._attention_weights = None
        self._enable_attention_capture = False
    
    def update_mi_estimates(
        self,
        col_mi_estimates: dict,
        joint_mi_estimate: Optional[float] = None,
    ):
        """Update mutual information estimates in relationship extractor."""
        relationship_extractor = getattr(self, 'relationship_extractor', None)
        if relationship_extractor and hasattr(relationship_extractor, 'update_mi_estimates'):
            relationship_extractor.update_mi_estimates(
                col_mi_estimates, joint_mi_estimate
            )
    
    def update_column_losses(self, col_losses_dict: dict):
        """Update per-column marginal losses in relationship extractor (for importance calculation)."""
        relationship_extractor = getattr(self, 'relationship_extractor', None)
        if relationship_extractor and hasattr(relationship_extractor, 'update_column_losses'):
            relationship_extractor.update_column_losses(col_losses_dict)

    def _setup_hybrid_relationships(self):
        """
        Setup hybrid relationship embeddings and metadata.
        
        For RELATIONSHIP strategy groups, we add learned group embeddings
        that get added to related columns to help the transformer learn their relationships.
        """
        # Filter for RELATIONSHIP strategy groups only
        relationship_groups = {
            name: info for name, info in self.hybrid_groups.items()
            if info.get('strategy') == 'relationship'
        }
        
        if not relationship_groups:
            self.group_embeddings = None
            self.col_to_group = {}
            logger.debug("No RELATIONSHIP hybrid groups detected")
            return
        
        # Create learned group embeddings
        n_groups = len(relationship_groups)
        self.group_embeddings = nn.Parameter(
            torch.randn(n_groups, self.config.d_model) / math.sqrt(self.config.d_model)
        )
        
        # Create mapping from column index to group index
        self.col_to_group = {}
        for group_idx, (group_name, group_info) in enumerate(relationship_groups.items()):
            for col_name in group_info['columns']:
                if col_name in self.col_names_in_order:
                    col_idx = self.col_names_in_order.index(col_name)
                    self.col_to_group[col_idx] = group_idx
        
        logger.info(f"🔗 JointEncoder hybrid relationships: {n_groups} groups covering {len(self.col_to_group)} columns")
        for group_name, group_info in relationship_groups.items():
            logger.info(f"   {group_name}: {group_info['type']} - {group_info['columns']}")
    
    def enable_attention_capture(self):
        """Enable capturing attention weights for diagnostic analysis."""
        self._enable_attention_capture = True
    
    def disable_attention_capture(self):
        """Disable capturing attention weights (default, saves memory)."""
        self._enable_attention_capture = False
    
    def get_attention_weights(self):
        """Return captured attention weights. Returns None if capture is disabled."""
        return self._attention_weights

    def forward(self, x, mask: Optional[torch.Tensor] = None):
        # NOTE: we're using a typical transformer encoder here, where all columns get their
        # own encoding. Then we throw away all encodings except the one for the [CLS] token.
        # A more efficient implementation would apply attention directly to inputs and produce
        # only one encoding.

        # FIXME: should the converter be the same for all variables, or should we use different converters for
        # different input variables?
        # ANSWER: using one encoder is fine, at least on smaller datasets.
        # On larger datasets we may want to revisit.

        # x: (batch_size, n_cols, d_model) - column encodings
        # mask: (batch_size, n_cols) - TokenStatus mask (optional)
        
        # DEBUG: MPS INT_MAX - Track forward calls
        _debug_count = getattr(self, '_debug_forward_count', 0)
        self._debug_forward_count = _debug_count + 1
        _should_debug = _debug_count < 5  # Only first 5 calls
        
        if _should_debug:
            _log_gpu_memory_transformer(f"JointEncoder.forward #{_debug_count} START")
            logger.info(f"[DEBUG] JointEncoder.forward() #{_debug_count}")
            logger.info(f"[DEBUG]   Input x shape: {x.shape}, numel: {x.numel()}")

        col_x = []
        for i, col_name in enumerate(self.col_names_in_order):
            converter = self.in_converters[col_name]
            col_x.append(converter(x[:, i, :]))

        x = torch.stack(col_x, dim=1)  # (batch_size, n_cols, d_model)

        # Compute relationship features BEFORE positional encoding
        relationship_tokens = []
        relationship_extractor = getattr(self, 'relationship_extractor', None)
        if relationship_extractor is not None:
            # Check if we should evaluate NULL baseline this step
            # Only evaluate on first mask call (when flag is False)
            is_first_mask = not getattr(relationship_extractor, '_null_evaluation_pending', False)
            should_eval_func = getattr(relationship_extractor, 'should_evaluate_null_baseline', None)
            if should_eval_func:
                use_null_baseline = should_eval_func(is_first_mask)
            else:
                use_null_baseline = False
            
            if use_null_baseline:
                # Run NULL-only forward for baseline evaluation
                relationship_tokens = relationship_extractor.forward(x, mask, relationship_mode="null_only")
                # Flag is already set by should_evaluate_null_baseline()
                # Track that this mask used NULL-only mode
                if not hasattr(relationship_extractor, '_null_batch_mask_modes'):
                    relationship_extractor._null_batch_mask_modes = []
                relationship_extractor._null_batch_mask_modes.append(True)
            else:
                relationship_tokens = relationship_extractor.forward(x, mask)
                # Track that this mask used normal mode
                if not hasattr(relationship_extractor, '_null_batch_mask_modes'):
                    relationship_extractor._null_batch_mask_modes = []
                relationship_extractor._null_batch_mask_modes.append(False)
            # relationship_tokens: List of (batch_size, d_model) tensors
            if _should_debug:
                logger.info(f"[DEBUG]   Relationship tokens: {len(relationship_tokens)} tokens")

        # Add column encodings first, then cls token
        # this means the cls token does not get a positional encoding, but
        # that's OK because only one token gets placed in that position anyway.
        # This simplifies things because this way the positional encoder does
        # not need to worry about adding a positional encoding for the cls token.
        if self.config.use_col_encoding:
            x = self.col_encoder(x)

        # HYBRID COLUMN SUPPORT: Add group embeddings for RELATIONSHIP strategy
        # Backwards compatibility: older models don't have group_embeddings
        if hasattr(self, 'group_embeddings') and self.group_embeddings is not None and len(getattr(self, 'col_to_group', {})) > 0:
            for col_idx, group_idx in self.col_to_group.items():
                # Add group embedding to this column's encoding
                # This helps the transformer learn that these columns are related
                x[:, col_idx, :] = x[:, col_idx, :] + self.group_embeddings[group_idx]

        # ============================================================================
        # TIER 3: LOCAL ATTENTION OVER RELATIONSHIP CANDIDATES
        # ============================================================================
        # Instead of pooling all relationships into CLS, each column selectively
        # attends over its K relationship candidates (exploit + explore + NULL).
        # This allows the model to learn which relationships matter per column.
        # ============================================================================
        
        # Extract shapes BEFORE adding CLS token (needed for Tier 3)
        B = x.shape[0]  # batch_size
        N = x.shape[1]  # n_cols (before CLS)
        d = x.shape[2]  # d_model
        C = x  # (B, N, d) - column encodings before CLS
        
        # Apply Tier 3 local attention if relationships are available
        if relationship_tokens and relationship_extractor is not None and self.local_attention is not None:
            # Get active directed pairs from extractor (stored during forward)
            active_directed_pairs = getattr(relationship_extractor, '_last_step_active_pairs', None)
            
            # Ensure active_directed_pairs is iterable (pylint type check)
            if active_directed_pairs is not None and len(active_directed_pairs) > 0:
                # Convert to list for iteration (handles both set and list)
                active_directed_pairs = list(active_directed_pairs)
                # ========================================================================
                # STEP 1: Build IDX [N, K_total] - candidate indices per column
                # ========================================================================
                # Get K_exploit and K_explore from extractor
                log2_N = np.log2(max(2, N))
                E = max(1, min(32, int(np.ceil(log2_N))))
                K_exploit = E
                K_explore = E
                K_total = K_exploit + K_explore + 1  # +1 for NULL slot
                
                # Build IDX: [N, K_total] with NULL at slot 0
                IDX = torch.full((N, K_total), N, dtype=torch.long, device=x.device)  # N = NULL marker
                
                # Group active directed pairs by target column (vectorized where possible)
                # active_directed_pairs is a set of (src, tgt) tuples
                for tgt in range(N):
                    # Get all edges targeting this column
                    tgt_edges = [(src, t) for (src, t) in active_directed_pairs if t == tgt]
                    
                    if len(tgt_edges) > 0:
                        # Extract source indices
                        src_indices = torch.tensor([src for (src, _) in tgt_edges], dtype=torch.long, device=x.device)
                        
                        # Take first K_total-1 (already ordered by exploit/explore policy in extractor)
                        n_candidates = min(len(src_indices), K_total - 1)
                        if n_candidates > 0:
                            IDX[tgt, 1:n_candidates+1] = src_indices[:n_candidates]
                
                # ========================================================================
                # STEP 2: Build R [B, N, K_total, d] - relationship embeddings
                # ========================================================================
                # Map relationship tokens to their pairs
                # relationship_tokens is a list of (batch_size, d_model) tensors
                # We need to map each token to its (src, tgt) pair
                
                # Get pairs_to_compute from extractor (undirected pairs that were computed)
                # The extractor stores this for Tier 3 mapping
                pairs_to_compute = getattr(relationship_extractor, '_last_pairs_to_compute', None)
                if pairs_to_compute is None:
                    # Fallback: reconstruct from active_directed_pairs
                    pairs_to_compute = set()
                    for (src, tgt) in active_directed_pairs:
                        if src < tgt:
                            pairs_to_compute.add((src, tgt))
                        else:
                            pairs_to_compute.add((tgt, src))
                    pairs_to_compute = sorted(pairs_to_compute)  # Sort for consistent indexing
                else:
                    # Ensure it's sorted for consistent indexing
                    pairs_to_compute = sorted(pairs_to_compute)
                
                # Build mapping: (src, tgt) -> token index in relationship_tokens list
                # For fused mode: 1 token per pair
                # For unfused mode: 9 tokens per pair
                # Note: pairs_to_compute contains undirected pairs (i, j) where i < j
                # But we need to map directed pairs (src, tgt) - use the undirected version
                use_fusion = getattr(relationship_extractor, 'use_fusion', True)
                tokens_per_pair = 1 if use_fusion else 9
                
                pair_to_token_idx = {}
                token_idx = 0
                for pair in pairs_to_compute:
                    # Store mapping for both (i,j) and (j,i) since relationships are symmetric
                    i, j = pair
                    pair_to_token_idx[(i, j)] = token_idx
                    pair_to_token_idx[(j, i)] = token_idx  # Same token for reverse direction
                    token_idx += tokens_per_pair
                
                # Build R: [B, N, K_total, d]
                R = torch.zeros(B, N, K_total, d, device=x.device, dtype=x.dtype)
                
                # Fill relationship embeddings from tokens (slots 1:K_total-1)
                for tgt in range(N):
                    for slot in range(1, K_total):
                        src = IDX[tgt, slot].item()
                        if src < N:  # Valid candidate (not NULL)
                            # Find the pair (src, tgt) - use directed pair directly
                            # pair_to_token_idx has both (src,tgt) and (tgt,src) mapped to same token
                            if (src, tgt) in pair_to_token_idx:
                                token_idx = pair_to_token_idx[(src, tgt)]
                                if token_idx < len(relationship_tokens):
                                    # For fused mode: use the single token
                                    # For unfused mode: use first token (multiply) as representative
                                    # (In unfused mode, token_idx points to first of 9 tokens)
                                    R[:, tgt, slot, :] = relationship_tokens[token_idx]
                
                # NULL candidate at slot 0: use existing learned null_relationship_base
                if hasattr(relationship_extractor, 'null_relationship_base'):
                    null_base = relationship_extractor.null_relationship_base
                    if null_base.dim() == 1:
                        null_base = null_base.unsqueeze(0).unsqueeze(0)  # [1, 1, d]
                    R[:, :, 0, :] = null_base.expand(B, N, -1)  # Broadcast to [B, N, d]
                else:
                    R[:, :, 0, :] = 0.0
                
                # ========================================================================
                # STEP 3: Apply Local Attention
                # ========================================================================
                # Query: column encodings C = x (B, N, d)
                # Keys/Values: relationship embeddings R = [B, N, K_total, d]
                # Each column attends over its K_total relationship candidates
                
                K = K_total
                
                # Reshape for batch*columns attention
                # [B*N, 1, d] for queries, [B*N, K, d] for keys/values
                q = C.reshape(B * N, 1, d)  # (B*N, 1, d)
                kv = R.reshape(B * N, K, d)  # (B*N, K, d)
                
                # Local attention: each column attends over its K candidates
                attn_out, attn_weights = self.local_attention(q, kv, kv)  # (B*N, 1, d), (B*N, 1, K)
                attn_out = attn_out.reshape(B, N, d)  # (B, N, d)
                attn_weights = attn_weights.reshape(B, N, 1, K)  # (B, N, 1, K)
                
                # Gate: allow model to damp relationship injection
                gate_values = self.local_attn_gate(C)  # (B, N, d) - per-column gate
                attn_out_gated = gate_values * self.local_attn_dropout(attn_out)  # (B, N, d)
                
                # Residual connection
                C2 = C + attn_out_gated  # (B, N, d)
                
                # Replace column encodings
                x = C2  # (B, N, d) - relationship-enhanced column encodings
                
                # Logging (vectorized, no Python loops)
                if _should_debug:
                    # Attention entropy (measure of selection sharpness)
                    # CORRECTED: low entropy = sharp/selective, high entropy = diffuse/averaging
                    attn_probs = attn_weights.squeeze(2)  # (B, N, K)
                    entropy = -(attn_probs * (attn_probs + 1e-10).log()).sum(dim=-1)  # (B, N)
                    attn_entropy_mean = entropy.mean().item()
                    attn_entropy_std = entropy.std().item()
                    
                    # NULL selection rate
                    null_attn = attn_probs[:, :, 0].mean().item()  # Average attention on NULL slot
                    
                    # Degree stats (vectorized, not Python loops)
                    # Count how often each source column appears across all targets
                    IDX_valid = IDX[:, 1:]  # [N, K] (exclude NULL slot)
                    source_counts = torch.bincount(IDX_valid.flatten(), minlength=N)  # [N] - vectorized!
                    degree_mean = source_counts.float().mean().item()
                    degree_max = source_counts.max().item()
                    degree_std = source_counts.float().std().item()
                    
                    # Gate statistics
                    gate_mean = gate_values.mean().item()
                    gate_std = gate_values.std().item()
                    
                    logger.info(f"[TIER3]   Local attention applied:")
                    logger.info(f"[TIER3]     Attention entropy: {attn_entropy_mean:.4f} ± {attn_entropy_std:.4f} (low=selective, high=diffuse)")
                    logger.info(f"[TIER3]     NULL selection rate: {null_attn*100:.1f}%")
                    logger.info(f"[TIER3]     Source degree: mean={degree_mean:.1f}, max={degree_max}, std={degree_std:.1f}")
                    logger.info(f"[TIER3]     Gate: mean={gate_mean:.3f} ± {gate_std:.3f} (higher=more relationship injection)")
                
                # Store for gradient tracking (if needed)
                if self.training:
                    self._tier3_C = C
                    self._tier3_R = R
            else:
                if _should_debug:
                    logger.info(f"[TIER3]   No active relationships, skipping local attention")
        
        # Add CLS token AFTER Tier 3 local attention (if applied)
        x = self.add_cls_token(x)  # (batch_size, 1 + n_cols, d_model)
        
        # NOTE: x now has relationship-enhanced column encodings (if Tier 3 was applied)
        # or original column encodings (if no relationships)

        # DEBUG: Log shape before transformer encoder - this is where MPS INT_MAX can overflow
        if _should_debug:
            batch_size_debug = x.shape[0]
            seq_len_debug = x.shape[1]
            d_model_debug = x.shape[2]
            n_heads = self.config.n_heads
            # Attention matrix size: (batch * n_heads, seq_len, seq_len)
            attn_matrix_size = batch_size_debug * n_heads * seq_len_debug * seq_len_debug
            INT_MAX = 2**31 - 1
            logger.info(f"[DEBUG]   Before transformer_encoder:")
            logger.info(f"[DEBUG]     x shape: {x.shape} (batch={batch_size_debug}, seq={seq_len_debug}, d_model={d_model_debug})")
            logger.info(f"[DEBUG]     n_heads: {n_heads}")
            logger.info(f"[DEBUG]     Attention matrix elements: {batch_size_debug} × {n_heads} × {seq_len_debug}² = {attn_matrix_size:,}")
            if attn_matrix_size > INT_MAX:
                logger.error(f"[DEBUG]   ⚠️ ATTENTION MATRIX EXCEEDS INT_MAX ({INT_MAX:,})!")
            logger.info(f"[DEBUG]     About to call transformer_encoder...")

        # Pass through the transformer encoder (now using batch_first=True)
        # Use gradient checkpointing if enabled to save memory
        if self.enable_gradient_checkpointing and self.training:
            x = checkpoint(self.transformer_encoder, x, use_reentrant=False)
        else:
            x = self.transformer_encoder(x)
        
        if _should_debug:
            logger.info(f"[DEBUG]   After transformer_encoder: x shape = {x.shape}")

        # Use the output of the first token as the encoding of the whole sequence
        # This corresponds to the encoding of the [CLS] token. We throw out the encodings
        # for all other positions. With batch_first=True, CLS token is at position [:, 0, :]
        joint = x[:, 0, :]
        # marginal = x[1:]  # marginal encodings - we don's use these
        
        # ============================================================================
        # TIER 3: No pooled relationship injection needed
        # ============================================================================
        # With Tier 3 local attention, relationships are already selectively
        # attended per column before the transformer, so no CLS injection is needed.
        # The relationship information is already incorporated into column encodings.
        # ============================================================================

        # convert from trnsformer dim to embedding_space dim, and normalize
        joint = self.out_converter(joint)

        # CONDITIONAL NORMALIZATION based on config
        # This config check is for safety/future flexibility
        # In practice, this should almost always be True
        if self.config.normalize_output:
            short_vec = nn.functional.normalize(joint[:, 0:3], dim=1)
            full_vec = nn.functional.normalize(joint, dim=1)
        else:
            # This path should rarely/never be used
            # NOTE: Using module-level logger (don't import locally - causes shadowing issues)
            logger.warning("⚠️  Joint encoder normalization is disabled! Embeddings may not be unit norm.")
            short_vec = joint[:, 0:3]
            full_vec = joint

        return short_vec, full_vec
    
    def analyze_attention_head_redundancy(self, batch_data, top_k=5):
        """
        Analyze if attention heads are learning redundant patterns.
        
        This diagnostic helps determine if you need more attention heads:
        - High redundancy (>0.8 similarity) → heads are learning the same thing → need more heads
        - Low redundancy (<0.5 similarity) → heads are diverse → current head count is good
        
        Args:
            batch_data: Input tensor (batch_size, n_cols, d_model) 
            top_k: Number of top attention positions to consider per head
        
        Returns:
            dict with:
                - 'head_similarities': (n_heads, n_heads) pairwise cosine similarities
                - 'avg_similarity': Average pairwise similarity across all heads
                - 'max_similarity': Maximum pairwise similarity (most redundant pair)
                - 'redundant_pairs': List of (head_i, head_j, similarity) where sim > 0.7
                - 'diversity_score': 1 - avg_similarity (higher = more diverse)
                - 'recommendation': String suggesting if more heads are needed
        """
        if not self._enable_attention_capture:
            logger.warning("⚠️  Attention capture is disabled. Call enable_attention_capture() first.")
            return None
        
        # Run forward pass to populate attention weights
        self.eval()  # Set to eval mode to get consistent attention
        with torch.no_grad():
            _ = self.forward(batch_data)
        
        # NOTE: PyTorch's TransformerEncoder doesn't expose attention weights by default
        # We need to monkey-patch or use a custom implementation
        # For now, we'll extract attention from the encoder layers
        
        attention_patterns = []
        n_layers = self.config.n_layers
        n_heads = self.config.n_heads
        
        # Extract attention weights from each layer
        for layer_idx, layer in enumerate(self.transformer_encoder.layers):
            # Access the self-attention module
            self_attn = layer.self_attn
            
            # Need to hook into attention computation
            # This requires modifying the forward pass or using hooks
            # For now, we'll compute attention patterns manually
            pass
        
        # TODO: This requires deeper integration with PyTorch's attention mechanism
        # For now, return a placeholder
        logger.warning("⚠️  Full attention analysis requires attention weight extraction hooks.")
        logger.info("   Analyzing attention patterns via weight similarity instead...")
        
        # Alternative: Analyze attention weight matrices for similarity
        head_patterns = self._analyze_attention_weight_similarity()
        
        return head_patterns
    
    def _analyze_attention_weight_similarity(self):
        """
        Analyze similarity between attention heads by comparing their learned weight matrices.
        
        This is an approximation: instead of comparing attention patterns on specific inputs,
        we compare the learned Q, K, V projection matrices for each head.
        """
        n_heads = self.config.n_heads
        d_model = self.config.d_model
        
        # Collect Q, K, V weight matrices from first transformer layer
        first_layer = self.transformer_encoder.layers[0]
        
        # PyTorch's MultiheadAttention stores weights as (d_model, d_model)
        # Then splits into n_heads during forward pass
        q_weights = first_layer.self_attn.in_proj_weight[:d_model, :]  # Query weights
        k_weights = first_layer.self_attn.in_proj_weight[d_model:2*d_model, :]  # Key weights
        v_weights = first_layer.self_attn.in_proj_weight[2*d_model:, :]  # Value weights
        
        head_dim = d_model // n_heads
        
        # Split into per-head matrices
        q_heads = q_weights.reshape(n_heads, head_dim, d_model)
        k_heads = k_weights.reshape(n_heads, head_dim, d_model)
        v_heads = v_weights.reshape(n_heads, head_dim, d_model)
        
        # Compute pairwise similarities between heads
        # We'll use cosine similarity of flattened QK^T patterns
        head_similarities = torch.zeros(n_heads, n_heads)
        
        for i in range(n_heads):
            for j in range(i, n_heads):
                # Compute attention pattern similarity: compare QK^T for each head
                # QK^T shape would be (head_dim, head_dim) but we want to compare overall behavior
                # Simplified: compare Q and K weights directly
                
                q_i_flat = q_heads[i].flatten()
                q_j_flat = q_heads[j].flatten()
                k_i_flat = k_heads[i].flatten()
                k_j_flat = k_heads[j].flatten()
                
                # Cosine similarity of Q weights
                q_sim = F.cosine_similarity(q_i_flat.unsqueeze(0), q_j_flat.unsqueeze(0))
                
                # Cosine similarity of K weights  
                k_sim = F.cosine_similarity(k_i_flat.unsqueeze(0), k_j_flat.unsqueeze(0))
                
                # Average Q and K similarity
                sim = (q_sim + k_sim) / 2.0
                
                head_similarities[i, j] = sim.item()
                head_similarities[j, i] = sim.item()
        
        # Compute statistics
        # Exclude diagonal (self-similarity = 1.0)
        mask = ~torch.eye(n_heads, dtype=torch.bool)
        off_diagonal = head_similarities[mask]
        
        avg_similarity = off_diagonal.mean().item()
        max_similarity = off_diagonal.max().item()
        min_similarity = off_diagonal.min().item()
        
        # Find redundant pairs (similarity > 0.7)
        redundant_pairs = []
        for i in range(n_heads):
            for j in range(i+1, n_heads):
                sim = head_similarities[i, j].item()
                if sim > 0.7:
                    redundant_pairs.append((i, j, sim))
        
        # Sort by similarity (most redundant first)
        redundant_pairs.sort(key=lambda x: x[2], reverse=True)
        
        # Diversity score (higher = more diverse)
        diversity_score = 1.0 - avg_similarity
        
        # Generate recommendation
        if avg_similarity > 0.8:
            recommendation = "HIGH REDUNDANCY: Heads are learning very similar patterns. Consider increasing n_heads."
            status = "❌ REDUNDANT"
        elif avg_similarity > 0.6:
            recommendation = "MODERATE REDUNDANCY: Some overlap between heads. Current head count is okay, but could benefit from more."
            status = "⚠️  MODERATE"
        else:
            recommendation = "GOOD DIVERSITY: Heads are learning distinct patterns. Current head count is appropriate."
            status = "✅ DIVERSE"
        
        result = {
            'head_similarities': head_similarities.cpu().numpy(),
            'avg_similarity': avg_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'redundant_pairs': redundant_pairs,
            'diversity_score': diversity_score,
            'recommendation': recommendation,
            'status': status,
            'n_heads': n_heads,
            'n_redundant_pairs': len(redundant_pairs),
        }
        
        return result
    
    def log_attention_analysis(self, batch_data=None):
        """
        Log attention head diversity analysis.
        
        Args:
            batch_data: Optional input batch. If None, only analyzes weight similarity.
        """
        logger.info("🔍 ATTENTION HEAD DIVERSITY ANALYSIS")
        logger.info(f"   Number of heads: {self.config.n_heads}")
        logger.info(f"   Number of layers: {self.config.n_layers}")
        logger.info(f"   Model dimension: {self.config.d_model}")
        logger.info(f"   Head dimension: {self.config.d_model // self.config.n_heads}")
        
        # Analyze weight similarity
        analysis = self._analyze_attention_weight_similarity()
        
        logger.info(f"\n{analysis['status']} Attention Head Diversity:")
        logger.info(f"   Average head similarity: {analysis['avg_similarity']:.3f}")
        logger.info(f"   Diversity score: {analysis['diversity_score']:.3f} (higher is better)")
        logger.info(f"   Min similarity: {analysis['min_similarity']:.3f}")
        logger.info(f"   Max similarity: {analysis['max_similarity']:.3f}")
        
        if analysis['redundant_pairs']:
            logger.info(f"\n⚠️  Found {len(analysis['redundant_pairs'])} redundant head pairs (>0.7 similarity):")
            for i, j, sim in analysis['redundant_pairs'][:5]:  # Show top 5
                logger.info(f"      Head {i} ↔ Head {j}: {sim:.3f}")
        else:
            logger.info("\n✅ No redundant head pairs found (all < 0.7 similarity)")
        
        logger.info(f"\n💡 {analysis['recommendation']}")
        
        return analysis
