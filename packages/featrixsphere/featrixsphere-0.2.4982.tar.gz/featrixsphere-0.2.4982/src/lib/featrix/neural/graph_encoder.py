#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
GraphEncoder: Bridges multiple TableEncoders to model N:M relationships.

Architecture:
- Each table has its own FeatrixTableEncoder
- GraphEncoder learns relationships between tables via shared keys
- Outputs unified embeddings that capture cross-table relationships
"""
import logging
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from featrix.neural.encoders import FeatrixTableEncoder
from featrix.neural.model_config import (
    GraphEncoderConfig,
    RelationshipEncoderConfig,
    CrossTableAttentionConfig,
    FusionLayerConfig,
    KeyMatcherConfig,
    SimpleMLPConfig,
)
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.featrix_module_dict import FeatrixModuleDict

logger = logging.getLogger(__name__)


# ============================================================================
# Key Matching
# ============================================================================

class KeyMatcher(nn.Module):
    """
    Efficiently matches keys between tables for relationship computation.
    """
    
    def __init__(self, n_keys: int, config: KeyMatcherConfig):
        super().__init__()
        self.n_keys = n_keys
        self.config = config
        self.use_hash = config.use_hash_matching
    
    def forward(
        self,
        keys_a: torch.Tensor,  # (batch_a, n_keys) - key values from table A
        keys_b: torch.Tensor,  # (batch_b, n_keys) - key values from table B
    ) -> torch.Tensor:
        """
        Match keys between two tables.
        
        Returns:
            Match indices: (batch_a, max_matches) tensor where each row contains
            indices into table_b that match the corresponding row in table_a.
            Padded with -1 for no match.
        """
        batch_a = keys_a.shape[0]
        batch_b = keys_b.shape[0]
        
        if self.use_hash:
            return self._hash_match(keys_a, keys_b)
        else:
            return self._exact_match(keys_a, keys_b)
    
    def _hash_match(self, keys_a: torch.Tensor, keys_b: torch.Tensor) -> torch.Tensor:
        """Hash-based matching for efficiency."""
        # Simple hash: sum of key values modulo bucket size
        hash_a = (keys_a.sum(dim=1) % self.config.hash_bucket_size).long()
        hash_b = (keys_b.sum(dim=1) % self.config.hash_bucket_size).long()
        
        # Find matches
        matches = []
        for i, h_a in enumerate(hash_a):
            matching_indices = torch.where(hash_b == h_a)[0]
            matches.append(matching_indices)
        
        # Pad to same length
        max_matches = max(len(m) for m in matches) if matches else 0
        if max_matches == 0:
            return torch.full((keys_a.shape[0], 1), -1, dtype=torch.long, device=keys_a.device)
        
        padded = []
        for m in matches:
            if len(m) == 0:
                padded.append(torch.full((max_matches,), -1, dtype=torch.long, device=keys_a.device))
            else:
                pad_len = max_matches - len(m)
                padded_m = torch.cat([m, torch.full((pad_len,), -1, dtype=torch.long, device=keys_a.device)])
                padded.append(padded_m)
        
        return torch.stack(padded)
    
    def _exact_match(self, keys_a: torch.Tensor, keys_b: torch.Tensor) -> torch.Tensor:
        """Exact matching by comparing all key values."""
        batch_a = keys_a.shape[0]
        matches = []
        
        for i in range(batch_a):
            # Compare this row's keys with all rows in table_b
            key_a = keys_a[i:i+1]  # (1, n_keys)
            diff = torch.abs(keys_b - key_a)  # (batch_b, n_keys)
            match_mask = (diff.sum(dim=1) < self.config.exact_match_threshold)  # (batch_b,)
            matching_indices = torch.where(match_mask)[0]
            matches.append(matching_indices)
        
        # Pad to same length
        max_matches = max(len(m) for m in matches) if matches else 0
        if max_matches == 0:
            return torch.full((batch_a, 1), -1, dtype=torch.long, device=keys_a.device)
        
        padded = []
        for m in matches:
            if len(m) == 0:
                padded.append(torch.full((max_matches,), -1, dtype=torch.long, device=keys_a.device))
            else:
                pad_len = max_matches - len(m)
                padded_m = torch.cat([m, torch.full((pad_len,), -1, dtype=torch.long, device=keys_a.device)])
                padded.append(padded_m)
        
        return torch.stack(padded)


# ============================================================================
# Relationship Encoders
# ============================================================================

class OneToOneEncoder(nn.Module):
    """Encoder for 1:1 relationships."""
    
    def __init__(self, d_model: int, config: RelationshipEncoderConfig):
        super().__init__()
        self.d_model = d_model
        self.encoder = SimpleMLP(
            config=SimpleMLPConfig(
                d_in=d_model * 2,  # Concatenate both embeddings
                d_out=d_model,
                d_hidden=d_model * 2,
                n_hidden_layers=config.n_hidden_layers,
                dropout=config.dropout,
            )
        )
    
    def forward(
        self,
        table_a_emb: torch.Tensor,  # (batch_a, d_model)
        table_b_emb: torch.Tensor,  # (batch_b, d_model)
        match_indices: torch.Tensor,  # (batch_a, max_matches)
    ) -> torch.Tensor:
        """Encode 1:1 relationship."""
        batch_a = table_a_emb.shape[0]
        device = table_a_emb.device
        
        # For 1:1, we expect exactly one match per row
        # Extract matched embeddings from table_b
        matched_b = []
        for i in range(batch_a):
            match_idx = match_indices[i, 0]  # Take first match
            if match_idx >= 0:
                matched_b.append(table_b_emb[match_idx])
            else:
                # No match - use zero embedding
                matched_b.append(torch.zeros(self.d_model, device=device))
        
        matched_b_emb = torch.stack(matched_b)  # (batch_a, d_model)
        
        # Concatenate and encode
        combined = torch.cat([table_a_emb, matched_b_emb], dim=-1)  # (batch_a, d_model * 2)
        return self.encoder(combined)


class OneToManyEncoder(nn.Module):
    """Encoder for 1:N relationships."""
    
    def __init__(self, d_model: int, config: RelationshipEncoderConfig):
        super().__init__()
        self.d_model = d_model
        self.aggregation_method = config.aggregation_method
        
        self.encoder = SimpleMLP(
            config=SimpleMLPConfig(
                d_in=d_model * 2,
                d_out=d_model,
                d_hidden=d_model * 2,
                n_hidden_layers=config.n_hidden_layers,
                dropout=config.dropout,
            )
        )
        
        # Attention for aggregation if needed
        if self.aggregation_method == "attention":
            self.attention = nn.MultiheadAttention(
                embed_dim=d_model,
                num_heads=4,
                batch_first=True,
            )
    
    def forward(
        self,
        table_a_emb: torch.Tensor,  # (batch_a, d_model)
        table_b_emb: torch.Tensor,  # (batch_b, d_model)
        match_indices: torch.Tensor,  # (batch_a, max_matches)
    ) -> torch.Tensor:
        """Encode 1:N relationship."""
        batch_a = table_a_emb.shape[0]
        device = table_a_emb.device
        
        # Aggregate multiple matches per row
        aggregated_b = []
        for i in range(batch_a):
            matches = match_indices[i]  # (max_matches,)
            valid_matches = matches[matches >= 0]
            
            if len(valid_matches) == 0:
                # No matches - use zero embedding
                aggregated_b.append(torch.zeros(self.d_model, device=device))
            else:
                # Get matched embeddings
                matched_embs = table_b_emb[valid_matches]  # (n_matches, d_model)
                
                # Aggregate based on method
                if self.aggregation_method == "mean":
                    agg = matched_embs.mean(dim=0)
                elif self.aggregation_method == "max":
                    agg = matched_embs.max(dim=0)[0]
                elif self.aggregation_method == "sum":
                    agg = matched_embs.sum(dim=0)
                elif self.aggregation_method == "attention":
                    # Use attention to aggregate
                    query = table_a_emb[i:i+1].unsqueeze(1)  # (1, 1, d_model)
                    key_value = matched_embs.unsqueeze(0).unsqueeze(0)  # (1, n_matches, d_model)
                    attn_out, _ = self.attention(query, key_value, key_value)
                    agg = attn_out.squeeze()
                else:
                    agg = matched_embs.mean(dim=0)
                
                aggregated_b.append(agg)
        
        aggregated_b_emb = torch.stack(aggregated_b)  # (batch_a, d_model)
        
        # Concatenate and encode
        combined = torch.cat([table_a_emb, aggregated_b_emb], dim=-1)
        return self.encoder(combined)


class ManyToManyEncoder(nn.Module):
    """Encoder for N:M relationships."""
    
    def __init__(self, d_model: int, config: RelationshipEncoderConfig):
        super().__init__()
        self.d_model = d_model
        self.encoder = SimpleMLP(
            config=SimpleMLPConfig(
                d_in=d_model * 2,
                d_out=d_model,
                d_hidden=d_model * 2,
                n_hidden_layers=config.n_hidden_layers,
                dropout=config.dropout,
            )
        )
    
    def forward(
        self,
        table_a_emb: torch.Tensor,  # (batch_a, d_model)
        table_b_emb: torch.Tensor,  # (batch_b, d_model)
        match_indices: torch.Tensor,  # (batch_a, max_matches)
    ) -> torch.Tensor:
        """Encode N:M relationship."""
        # For N:M, we create relationship embeddings for each match pair
        batch_a = table_a_emb.shape[0]
        device = table_a_emb.device
        
        # Aggregate all matches (similar to 1:N but bidirectional)
        relationship_embs = []
        for i in range(batch_a):
            matches = match_indices[i]
            valid_matches = matches[matches >= 0]
            
            if len(valid_matches) == 0:
                relationship_embs.append(torch.zeros(self.d_model, device=device))
            else:
                # Get matched embeddings and aggregate
                matched_embs = table_b_emb[valid_matches]  # (n_matches, d_model)
                agg_b = matched_embs.mean(dim=0)  # Average of matches
                
                # Combine with source embedding
                combined = torch.cat([table_a_emb[i], agg_b], dim=-1)
                # Process in eval mode to avoid BatchNorm issues with single samples
                was_training = self.encoder.training
                if was_training:
                    self.encoder.eval()
                rel_emb = self.encoder(combined.unsqueeze(0)).squeeze(0)
                if was_training:
                    self.encoder.train()
                relationship_embs.append(rel_emb)
        
        return torch.stack(relationship_embs)


class RelationshipEncoder(nn.Module):
    """
    Encodes relationships between two tables via shared keys.
    
    Handles:
    - 1:1 relationships (one-to-one mapping)
    - 1:N relationships (one-to-many)
    - N:M relationships (many-to-many)
    """
    
    def __init__(
        self,
        d_model: int,
        relationship_type: str,  # "1:1" | "1:N" | "N:M"
        n_keys: int,
        config: RelationshipEncoderConfig,
    ):
        super().__init__()
        
        self.relationship_type = relationship_type
        self.d_model = d_model
        
        # Key matching mechanism
        self.key_matcher = KeyMatcher(n_keys=n_keys, config=config.key_matcher_config)
        
        # Relationship type-specific encoders
        if relationship_type == "1:1":
            self.rel_encoder = OneToOneEncoder(d_model, config)
        elif relationship_type == "1:N":
            self.rel_encoder = OneToManyEncoder(d_model, config)
        elif relationship_type == "N:M":
            self.rel_encoder = ManyToManyEncoder(d_model, config)
        else:
            raise ValueError(f"Unknown relationship type: {relationship_type}")
        
        # Output projection
        self.output_proj = nn.Linear(d_model, d_model)
    
    def forward(
        self,
        table_a_emb: torch.Tensor,  # (batch_a, d_model)
        table_b_emb: torch.Tensor,  # (batch_b, d_model)
        keys_a: torch.Tensor,  # (batch_a, n_keys) - key values from table A
        keys_b: torch.Tensor,  # (batch_b, n_keys) - key values from table B
    ) -> torch.Tensor:
        """
        Encode relationship between two tables.
        
        Returns:
            Relationship embedding: (batch_a, d_model)
        """
        # Match keys to determine which rows are related
        match_indices = self.key_matcher(keys_a, keys_b)
        
        # Encode relationship based on type
        rel_emb = self.rel_encoder(
            table_a_emb,
            table_b_emb,
            match_indices,
        )
        
        return self.output_proj(rel_emb)


# ============================================================================
# Cross-Table Attention
# ============================================================================

class CrossTableAttention(nn.Module):
    """
    Attention mechanism that allows tables to attend to related tables.
    
    Uses relationship embeddings to guide attention:
    - Strong relationships → higher attention weights
    - Weak relationships → lower attention weights
    """
    
    def __init__(
        self,
        d_model: int,
        n_tables: int,
        config: CrossTableAttentionConfig,
    ):
        super().__init__()
        
        self.d_model = d_model
        self.n_tables = n_tables
        self.config = config
        
        # Multi-head attention for cross-table relationships
        self.attention = nn.MultiheadAttention(
            embed_dim=d_model,
            num_heads=config.n_heads,
            dropout=config.dropout,
            batch_first=True,
        )
        
        # Relationship weight projection
        if config.use_relationship_weights:
            self.rel_weight_proj = nn.Linear(d_model, 1)
    
    def forward(
        self,
        table_embeddings: Dict[str, torch.Tensor],
        relationship_embeddings: Dict[Tuple[str, str], torch.Tensor],
    ) -> Dict[str, torch.Tensor]:
        """
        Apply cross-table attention.
        
        Returns:
            Dict mapping table names to attended embeddings
        """
        attended = {}
        
        for table_name, table_emb in table_embeddings.items():
            # Find all related tables
            related_tables = []
            for (t1, t2), rel_emb in relationship_embeddings.items():
                if t1 == table_name:
                    related_tables.append((t2, rel_emb))
                elif t2 == table_name:
                    related_tables.append((t1, rel_emb))
            
            if not related_tables:
                # No relationships, return original embedding
                attended[table_name] = table_emb
                continue
            
            # Limit number of related tables if configured
            if self.config.max_related_tables and len(related_tables) > self.config.max_related_tables:
                # Keep top relationships by weight
                if self.config.use_relationship_weights:
                    weights = [torch.sigmoid(self.rel_weight_proj(rel_emb).mean()) for _, rel_emb in related_tables]
                    sorted_indices = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)
                    related_tables = [related_tables[i] for i in sorted_indices[:self.config.max_related_tables]]
                else:
                    related_tables = related_tables[:self.config.max_related_tables]
            
            # Build attention query/key/value
            # Query: current table embedding
            query = table_emb.unsqueeze(1)  # (batch, 1, d_model)
            
            keys = []
            values = []
            for other_table, rel_emb in related_tables:
                other_emb = table_embeddings[other_table]
                
                # Weight by relationship strength if enabled
                if self.config.use_relationship_weights:
                    rel_weight = torch.sigmoid(self.rel_weight_proj(rel_emb))
                    weighted_emb = other_emb * rel_weight
                else:
                    weighted_emb = other_emb
                
                keys.append(weighted_emb.unsqueeze(1))
                values.append(weighted_emb.unsqueeze(1))
            
            if not keys:
                attended[table_name] = table_emb
                continue
            
            key = torch.cat(keys, dim=1)  # (batch, n_related, d_model)
            value = torch.cat(values, dim=1)
            
            # Apply attention
            attn_output, _ = self.attention(query, key, value)
            attended[table_name] = attn_output.squeeze(1)  # (batch, d_model)
        
        return attended


# ============================================================================
# Fusion Layer
# ============================================================================

class FusionLayer(nn.Module):
    """
    Fuses table embeddings with relationship embeddings.
    
    Combines:
    - Original table embeddings
    - Cross-table attended embeddings
    - Relationship embeddings
    """
    
    def __init__(
        self,
        d_model: int,
        n_tables: int,
        config: FusionLayerConfig,
    ):
        super().__init__()
        
        self.d_model = d_model
        self.config = config
        
        # Fusion MLP
        self.fusion_mlp = SimpleMLP(
            config=SimpleMLPConfig(
                d_in=d_model * 3,  # table_emb + attended_emb + rel_emb
                d_out=d_model,
                d_hidden=d_model * 2,
                n_hidden_layers=config.n_hidden_layers,
                dropout=config.dropout,
            )
        )
        
        # Gating mechanism to control fusion strength
        if config.use_gating:
            self.gate = nn.Sequential(
                nn.Linear(d_model * 3, d_model),
                nn.Sigmoid(),
            )
        else:
            self.gate = None
    
    def forward(
        self,
        table_embeddings: Dict[str, torch.Tensor],
        attended_embeddings: Dict[str, torch.Tensor],
        relationship_embeddings: Dict[Tuple[str, str], torch.Tensor],
    ) -> Dict[str, torch.Tensor]:
        """
        Fuse embeddings from all sources.
        
        Returns:
            Dict mapping table names to fused embeddings
        """
        fused = {}
        
        for table_name in table_embeddings.keys():
            table_emb = table_embeddings[table_name]
            attended_emb = attended_embeddings[table_name]
            
            # Aggregate relationship embeddings for this table
            rel_embs = []
            for (t1, t2), rel_emb in relationship_embeddings.items():
                if t1 == table_name or t2 == table_name:
                    rel_embs.append(rel_emb)
            
            if rel_embs:
                rel_emb = torch.stack(rel_embs).mean(dim=0)  # Average relationship embeddings
            else:
                rel_emb = torch.zeros_like(table_emb)
            
            # Concatenate all sources
            combined = torch.cat([table_emb, attended_emb, rel_emb], dim=-1)
            
            # Fusion
            fused_emb = self.fusion_mlp(combined)
            
            # Gating if enabled
            if self.gate is not None:
                gate_weights = self.gate(combined)
                fused_emb = fused_emb * gate_weights + table_emb * (1 - gate_weights)
            
            fused[table_name] = fused_emb
        
        return fused


# ============================================================================
# Graph Encoder (Main Class)
# ============================================================================

class GraphEncoder(nn.Module):
    """
    Bridges multiple TableEncoders to model N:M relationships.
    
    Architecture:
    - Each table has its own TableEncoder
    - GraphEncoder learns relationships between tables via shared keys
    - Outputs unified embeddings that capture cross-table relationships
    """
    
    def __init__(
        self,
        table_encoders: Dict[str, FeatrixTableEncoder],
        shared_keys: Dict[Tuple[str, str], List[str]],  # (table_a, table_b) -> [key_cols]
        relationship_types: Dict[Tuple[str, str], str],  # (table_a, table_b) -> "1:N" | "N:M"
        d_model: int,
        config: GraphEncoderConfig,
    ):
        super().__init__()
        
        self.table_encoders = FeatrixModuleDict(table_encoders)
        self.shared_keys = shared_keys
        self.relationship_types = relationship_types
        self.d_model = d_model
        self.config = config
        
        # Relationship encoders for each table pair
        self.relationship_encoders = FeatrixModuleDict()
        for (table_a, table_b), keys in shared_keys.items():
            rel_type = relationship_types.get((table_a, table_b), "N:M")
            rel_config = config.relationship_config
            self.relationship_encoders[f"{table_a}→{table_b}"] = RelationshipEncoder(
                d_model=d_model,
                relationship_type=rel_type,
                n_keys=len(keys),
                config=rel_config,
            )
        
        # Cross-table attention mechanism
        self.cross_table_attention = CrossTableAttention(
            d_model=d_model,
            n_tables=len(table_encoders),
            config=config.attention_config,
        )
        
        # Fusion layer to combine table embeddings
        self.fusion_layer = FusionLayer(
            d_model=d_model,
            n_tables=len(table_encoders),
            config=config.fusion_config,
        )
    
    def forward(
        self,
        table_batches: Dict[str, Dict[str, any]],  # {table_name: {col_name: TokenBatch}}
        extract_keys_fn: Optional[callable] = None,  # Function to extract key values from batches
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through GraphEncoder.
        
        Args:
            table_batches: Dict mapping table names to their column batches
            extract_keys_fn: Optional function to extract key values from TokenBatch objects
        
        Returns:
            Dict mapping table names to their fused embeddings
        """
        # Step 1: Encode each table independently
        table_embeddings = {}
        for table_name, table_batch in table_batches.items():
            encoder = self.table_encoders[table_name]
            table_emb = encoder.encode(table_batch)
            table_embeddings[table_name] = table_emb  # (batch_size, d_model)
        
        # Step 2: Compute relationship embeddings for each table pair
        relationship_embeddings = {}
        for (table_a, table_b), keys in self.shared_keys.items():
            rel_encoder = self.relationship_encoders[f"{table_a}→{table_b}"]
            
            # Extract key values from batches
            if extract_keys_fn:
                key_values_a = extract_keys_fn(table_batches[table_a], keys)
                key_values_b = extract_keys_fn(table_batches[table_b], keys)
            else:
                # Default: extract from TokenBatch.value
                key_values_a = self._extract_keys_default(table_batches[table_a], keys)
                key_values_b = self._extract_keys_default(table_batches[table_b], keys)
            
            # Compute relationship embedding
            rel_emb = rel_encoder(
                table_embeddings[table_a],
                table_embeddings[table_b],
                key_values_a,
                key_values_b,
            )
            relationship_embeddings[(table_a, table_b)] = rel_emb
        
        # Step 3: Cross-table attention
        # Each table attends to related tables via relationships
        attended_embeddings = self.cross_table_attention(
            table_embeddings,
            relationship_embeddings,
        )
        
        # Step 4: Fusion
        fused_embeddings = self.fusion_layer(
            table_embeddings,
            attended_embeddings,
            relationship_embeddings,
        )
        
        return fused_embeddings
    
    def _extract_keys_default(
        self,
        table_batch: Dict[str, any],
        keys: List[str],
    ) -> torch.Tensor:
        """Default key extraction from TokenBatch objects."""
        key_tensors = []
        for key in keys:
            if key in table_batch:
                token_batch = table_batch[key]
                if hasattr(token_batch, 'value'):
                    # TokenBatch.value is (batch_size, ...)
                    key_val = token_batch.value
                    if key_val.dim() > 1:
                        # Flatten to (batch_size,)
                        key_val = key_val[:, 0] if key_val.shape[1] > 0 else torch.zeros(key_val.shape[0])
                    key_tensors.append(key_val)
                else:
                    # Fallback: create zero tensor
                    batch_size = len(table_batch.get(list(table_batch.keys())[0], []))
                    key_tensors.append(torch.zeros(batch_size, device=next(iter(table_batch.values())).device if hasattr(next(iter(table_batch.values())), 'device') else 'cpu'))
            else:
                # Key not found - use zeros
                batch_size = len(table_batch.get(list(table_batch.keys())[0], []))
                key_tensors.append(torch.zeros(batch_size))
        
        if not key_tensors:
            return torch.zeros((0, len(keys)))
        
        # Stack to (batch_size, n_keys)
        return torch.stack(key_tensors, dim=1)

