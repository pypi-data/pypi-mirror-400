#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Training utilities for GraphEncoder with cross-table loss computation.
"""
import logging
import random
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from featrix.neural.multi_table_dataset import MultiTableDataset
from featrix.neural.graph_encoder import GraphEncoder
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.gpu_utils import get_device

logger = logging.getLogger(__name__)


class MultiTableBatchDataset(Dataset):
    """
    Dataset that generates batches for multi-table training.
    
    Samples batches from multiple tables maintaining relationships.
    """
    
    def __init__(
        self,
        multi_table_dataset: MultiTableDataset,
        batch_size: int = 32,
        mask_ratio: float = 0.5,
    ):
        """
        Initialize multi-table batch dataset.
        
        Args:
            multi_table_dataset: MultiTableDataset instance
            batch_size: Batch size per table
            mask_ratio: Ratio of columns to mask for cross-table prediction
        """
        self.multi_table_dataset = multi_table_dataset
        self.batch_size = batch_size
        self.mask_ratio = mask_ratio
        
        # Pre-compute all possible batch indices
        self.table_sizes = {
            table_name: multi_table_dataset.get_table_size(table_name)
            for table_name in multi_table_dataset.get_all_tables()
        }
        
        # Create batches for each table
        self.batches = {}
        for table_name, table_size in self.table_sizes.items():
            all_indices = list(range(table_size))
            random.shuffle(all_indices)
            table_batches = [
                all_indices[i:i + batch_size]
                for i in range(0, len(all_indices), batch_size)
            ]
            self.batches[table_name] = table_batches
        
        # Total number of batches (use max to ensure we have enough)
        self.num_batches = max(len(batches) for batches in self.batches.values())
    
    def __len__(self):
        return self.num_batches
    
    def __getitem__(self, idx):
        """
        Get a multi-table batch.
        
        Returns:
            Dict mapping table names to their batches
        """
        table_batches = {}
        codecs = {}
        
        for table_name in self.multi_table_dataset.get_all_tables():
            batches = self.batches[table_name]
            batch_idx = idx % len(batches)
            indices = batches[batch_idx]
            
            # Get codecs for this table
            table_codecs = self.multi_table_dataset.codecs.get(table_name, {})
            
            # Get batch
            batch = self.multi_table_dataset.get_batch(
                table_name,
                indices,
                codecs=table_codecs,
            )
            table_batches[table_name] = batch
            codecs[table_name] = table_codecs
        
        return {
            'table_batches': table_batches,
            'codecs': codecs,
        }


def compute_cross_table_loss(
    graph_encoder: GraphEncoder,
    table_batches: Dict[str, Dict[str, any]],
    target_table: str,
    source_tables: List[str],
    relationship_weight: float = 1.0,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    Compute cross-table prediction loss.
    
    Predicts columns in target_table from related source_tables.
    
    Args:
        graph_encoder: GraphEncoder instance
        table_batches: Dict mapping table names to their batches
        target_table: Table to predict
        source_tables: Tables to use for prediction
        relationship_weight: Weight for relationship loss
    
    Returns:
        Tuple of (total_loss, loss_dict)
    """
    # Get fused embeddings
    fused_embeddings = graph_encoder(table_batches)
    
    # Get target table encoder
    target_encoder = graph_encoder.table_encoders[target_table]
    
    # Encode target table to get ground truth
    target_batch = table_batches[target_table]
    target_embeddings = target_encoder.encode(target_batch)
    
    # Get source embeddings (aggregated from related tables)
    source_embeddings_list = []
    for source_table in source_tables:
        if source_table in fused_embeddings:
            source_embeddings_list.append(fused_embeddings[source_table])
    
    if not source_embeddings_list:
        # No source tables - return zero loss
        return torch.tensor(0.0, device=get_device()), {}
    
    # Aggregate source embeddings
    source_embeddings = torch.stack(source_embeddings_list).mean(dim=0)
    
    # Compute prediction loss (MSE between source and target)
    prediction_loss = F.mse_loss(source_embeddings, target_embeddings)
    
    # Relationship consistency loss (encourage relationship embeddings to be informative)
    relationship_loss = torch.tensor(0.0, device=get_device())
    if hasattr(graph_encoder, 'relationship_encoders'):
        # Compute variance of relationship embeddings (encourage diversity)
        for rel_name, rel_encoder in graph_encoder.relationship_encoders.items():
            # This is a placeholder - actual relationship loss would be computed during forward
            pass
    
    total_loss = prediction_loss + relationship_weight * relationship_loss
    
    loss_dict = {
        'cross_table_prediction': prediction_loss.item(),
        'relationship': relationship_loss.item(),
        'total': total_loss.item(),
    }
    
    return total_loss, loss_dict


def train_graph_encoder(
    graph_encoder: GraphEncoder,
    multi_table_dataset: MultiTableDataset,
    n_epochs: int = 10,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    relationship_weight: float = 1.0,
    freeze_table_encoders: bool = False,
):
    """
    Train GraphEncoder on multi-table relationships.
    
    Args:
        graph_encoder: GraphEncoder to train
        multi_table_dataset: MultiTableDataset with data
        n_epochs: Number of training epochs
        batch_size: Batch size per table
        learning_rate: Learning rate
        relationship_weight: Weight for relationship loss
        freeze_table_encoders: Whether to freeze individual table encoders
    """
    logger.info(f"🚀 Training GraphEncoder for {n_epochs} epochs...")
    
    # Freeze table encoders if requested
    if freeze_table_encoders:
        logger.info("🔒 Freezing table encoders...")
        for table_name, table_encoder in graph_encoder.table_encoders.items():
            for param in table_encoder.parameters():
                param.requires_grad = False
    
    # Create dataset and dataloader
    dataset = MultiTableBatchDataset(
        multi_table_dataset=multi_table_dataset,
        batch_size=batch_size,
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=1,  # Each item is already a multi-table batch
        shuffle=True,
        num_workers=0,  # Avoid multiprocessing issues
    )
    
    # Setup optimizer
    trainable_params = [
        p for p in graph_encoder.parameters()
        if p.requires_grad
    ]
    optimizer = torch.optim.Adam(trainable_params, lr=learning_rate)
    
    # Training loop
    graph_encoder.train()
    for epoch in range(n_epochs):
        epoch_losses = []
        epoch_loss_dicts = []
        
        for batch_idx, batch_data in enumerate(dataloader):
            # Extract table batches (DataLoader adds batch dimension)
            table_batches = batch_data['table_batches'][0]  # Remove DataLoader batch dimension
            
            # Move batches to device
            for table_name, table_batch in table_batches.items():
                for col_name, token_batch in table_batch.items():
                    if hasattr(token_batch, 'to'):
                        token_batch.to(get_device())
            
            optimizer.zero_grad()
            
            # Compute loss for each table predicting from related tables
            total_loss = torch.tensor(0.0, device=get_device())
            batch_loss_dict = {}
            
            # Get relationships
            relationships = multi_table_dataset.get_relationships()
            
            for target_table in multi_table_dataset.get_all_tables():
                # Find related tables
                source_tables = []
                for (t1, t2), rel_type in relationships.items():
                    if t1 == target_table:
                        source_tables.append(t2)
                    elif t2 == target_table:
                        source_tables.append(t1)
                
                if source_tables:
                    # Compute cross-table loss
                    loss, loss_dict = compute_cross_table_loss(
                        graph_encoder,
                        table_batches,
                        target_table,
                        source_tables,
                        relationship_weight=relationship_weight,
                    )
                    total_loss = total_loss + loss
                    batch_loss_dict[f"{target_table}_from_related"] = loss_dict
            
            # Backward pass
            if total_loss.item() > 0:
                total_loss.backward()
                optimizer.step()
            
            epoch_losses.append(total_loss.item())
            epoch_loss_dicts.append(batch_loss_dict)
            
            if batch_idx % 10 == 0:
                logger.info(
                    f"Epoch {epoch+1}/{n_epochs}, Batch {batch_idx}, "
                    f"Loss: {total_loss.item():.4f}"
                )
        
        # Epoch summary
        avg_loss = sum(epoch_losses) / len(epoch_losses) if epoch_losses else 0.0
        logger.info(f"✅ Epoch {epoch+1}/{n_epochs} complete. Average loss: {avg_loss:.4f}")
    
    logger.info("✅ GraphEncoder training complete!")
    graph_encoder.eval()

