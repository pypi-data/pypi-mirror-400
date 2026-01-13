#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Multi-table EmbeddingSpace wrapper that uses GraphEncoder to fuse multiple tables.
"""
import logging
from typing import Dict, List, Optional, Tuple

import torch

from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.graph_encoder import GraphEncoder
from featrix.neural.multi_table_dataset import MultiTableDataset
from featrix.neural.model_config import GraphEncoderConfig, RelationshipEncoderConfig, CrossTableAttentionConfig, FusionLayerConfig, KeyMatcherConfig, SimpleMLPConfig
from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.graph_encoder_training import train_graph_encoder
from featrix.neural.gpu_utils import get_device

logger = logging.getLogger(__name__)


class MultiTableEmbeddingSpace:
    """
    Wrapper for training GraphEncoder on multiple related tables.
    
    Architecture:
    1. Train individual EmbeddingSpace for each table
    2. Create GraphEncoder bridging the TableEncoders
    3. Train GraphEncoder on cross-table relationships
    """
    
    def __init__(
        self,
        input_datasets: Dict[str, FeatrixInputDataSet],
        shared_keys: Dict[Tuple[str, str], List[str]],
        relationship_types: Dict[Tuple[str, str], str],
        d_model: int = 128,
        graph_config: Optional[GraphEncoderConfig] = None,
        **embedding_space_kwargs,
    ):
        """
        Initialize MultiTableEmbeddingSpace.
        
        Args:
            input_datasets: Dict mapping table names to FeatrixInputDataSet
            shared_keys: Dict mapping (table_a, table_b) to list of shared key columns
            relationship_types: Dict mapping (table_a, table_b) to relationship type
            d_model: Embedding dimension
            graph_config: Optional GraphEncoderConfig (will create default if None)
            **embedding_space_kwargs: Additional kwargs passed to EmbeddingSpace.__init__
        """
        self.input_datasets = input_datasets
        self.shared_keys = shared_keys
        self.relationship_types = relationship_types
        self.d_model = d_model
        
        # Create individual EmbeddingSpaces for each table
        logger.info(f"🔧 Creating EmbeddingSpace for {len(input_datasets)} tables...")
        self.embedding_spaces: Dict[str, EmbeddingSpace] = {}
        
        for table_name, input_dataset in input_datasets.items():
            logger.info(f"   Creating EmbeddingSpace for '{table_name}'...")
            # Split into train/val (simple 80/20 split)
            train_size = int(len(input_dataset.df) * 0.8)
            train_df = input_dataset.df.iloc[:train_size]
            val_df = input_dataset.df.iloc[train_size:]
            
            train_input = FeatrixInputDataSet(df=train_df, dataset_title=f"{table_name}_train")
            val_input = FeatrixInputDataSet(df=val_df, dataset_title=f"{table_name}_val")
            
            es = EmbeddingSpace(
                train_input_data=train_input,
                val_input_data=val_input,
                d_model=d_model,
                name=f"{table_name}_es",
                **embedding_space_kwargs,
            )
            self.embedding_spaces[table_name] = es
            logger.info(f"   ✅ Created EmbeddingSpace for '{table_name}'")
        
        # Create GraphEncoder config if not provided
        if graph_config is None:
            graph_config = self._create_default_graph_config()
        
        self.graph_config = graph_config
        
        # Create MultiTableDataset
        tables = {name: ds.df for name, ds in input_datasets.items()}
        codecs = {name: ds.column_codecs() for name, ds in input_datasets.items()}
        
        self.multi_table_dataset = MultiTableDataset(
            tables=tables,
            shared_keys=shared_keys,
            relationship_types=relationship_types,
            codecs=codecs,
        )
        
        # GraphEncoder will be created after training individual encoders
        self.graph_encoder: Optional[GraphEncoder] = None
    
    def _create_default_graph_config(self) -> GraphEncoderConfig:
        """Create default GraphEncoderConfig."""
        key_matcher_config = KeyMatcherConfig(
            use_hash_matching=True,
            hash_bucket_size=10000,
        )
        
        relationship_config = RelationshipEncoderConfig(
            d_model=self.d_model,
            key_matcher_config=key_matcher_config,
            n_hidden_layers=2,
            dropout=0.1,
            aggregation_method="mean",
        )
        
        attention_config = CrossTableAttentionConfig(
            d_model=self.d_model,
            n_heads=8,
            dropout=0.1,
            use_relationship_weights=True,
        )
        
        fusion_config = FusionLayerConfig(
            d_model=self.d_model,
            n_hidden_layers=2,
            use_gating=True,
            dropout=0.1,
        )
        
        return GraphEncoderConfig(
            d_model=self.d_model,
            relationship_config=relationship_config,
            attention_config=attention_config,
            fusion_config=fusion_config,
            freeze_table_encoders=False,
        )
    
    def train_individual_encoders(self, n_epochs: int = 10):
        """Train individual TableEncoders for each table."""
        logger.info(f"🚀 Training individual TableEncoders for {len(self.embedding_spaces)} tables...")
        
        for table_name, es in self.embedding_spaces.items():
            logger.info(f"\n📊 Training EmbeddingSpace for '{table_name}'...")
            es.train(n_epochs=n_epochs)
            logger.info(f"✅ Completed training for '{table_name}'")
    
    def create_graph_encoder(self):
        """Create GraphEncoder from trained TableEncoders."""
        logger.info("🔗 Creating GraphEncoder from trained TableEncoders...")
        
        # Extract TableEncoders from EmbeddingSpaces
        table_encoders = {
            table_name: es.encoder
            for table_name, es in self.embedding_spaces.items()
        }
        
        # Create GraphEncoder
        self.graph_encoder = GraphEncoder(
            table_encoders=table_encoders,
            shared_keys=self.shared_keys,
            relationship_types=self.relationship_types,
            d_model=self.d_model,
            config=self.graph_config,
        )
        
        # Move to device
        self.graph_encoder.to(get_device())
        
        logger.info("✅ GraphEncoder created and moved to device")
        return self.graph_encoder
    
    def train_graph_encoder(
        self,
        n_epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 1e-4,
        relationship_weight: float = 1.0,
    ):
        """
        Train GraphEncoder on cross-table relationships.
        
        Args:
            n_epochs: Number of training epochs
            batch_size: Batch size per table
            learning_rate: Learning rate for optimizer
            relationship_weight: Weight for relationship loss
        """
        if self.graph_encoder is None:
            raise RuntimeError("GraphEncoder not created. Call create_graph_encoder() first.")
        
        train_graph_encoder(
            graph_encoder=self.graph_encoder,
            multi_table_dataset=self.multi_table_dataset,
            n_epochs=n_epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            relationship_weight=relationship_weight,
            freeze_table_encoders=self.graph_config.freeze_table_encoders,
        )
    
    def encode_multi_table(self, table_batches: Dict[str, Dict[str, any]]) -> Dict[str, torch.Tensor]:
        """
        Encode multiple tables using GraphEncoder.
        
        Args:
            table_batches: Dict mapping table names to their column batches
        
        Returns:
            Dict mapping table names to fused embeddings
        """
        if self.graph_encoder is None:
            raise RuntimeError("GraphEncoder not created. Call create_graph_encoder() first.")
        
        return self.graph_encoder(table_batches)

