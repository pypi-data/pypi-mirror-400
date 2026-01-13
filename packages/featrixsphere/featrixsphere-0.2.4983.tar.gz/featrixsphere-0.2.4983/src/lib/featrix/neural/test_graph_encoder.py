#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Test script for GraphEncoder functionality.
"""
import pandas as pd
import torch

from featrix.neural.multi_table_dataset import MultiTableDataset
from featrix.neural.graph_encoder import GraphEncoder
from featrix.neural.model_config import (
    GraphEncoderConfig,
    RelationshipEncoderConfig,
    CrossTableAttentionConfig,
    FusionLayerConfig,
    KeyMatcherConfig,
    SimpleMLPConfig,
)


def create_example_data():
    """Create example multi-table data for testing."""
    # Users table
    users_df = pd.DataFrame({
        'user_id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
    })
    
    # Orders table
    orders_df = pd.DataFrame({
        'order_id': [101, 102, 103, 104],
        'user_id': [1, 1, 2, 3],  # Foreign key to users
        'total': [100.0, 200.0, 150.0, 300.0],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
    })
    
    # Products table
    products_df = pd.DataFrame({
        'product_id': [201, 202, 203],
        'name': ['Widget', 'Gadget', 'Thing'],
        'price': [10.0, 20.0, 30.0],
    })
    
    # Order items (junction table for N:M relationship)
    order_items_df = pd.DataFrame({
        'order_id': [101, 101, 102, 103, 104],
        'product_id': [201, 202, 201, 203, 202],
        'quantity': [2, 1, 3, 1, 2],
    })
    
    return {
        'users': users_df,
        'orders': orders_df,
        'products': products_df,
        'order_items': order_items_df,
    }


def test_multi_table_dataset():
    """Test MultiTableDataset functionality."""
    print("=" * 80)
    print("Testing MultiTableDataset")
    print("=" * 80)
    
    tables = create_example_data()
    
    # Define relationships
    shared_keys = {
        ('users', 'orders'): ['user_id'],  # 1:N
        ('orders', 'order_items'): ['order_id'],  # 1:N
        ('products', 'order_items'): ['product_id'],  # 1:N
    }
    
    relationship_types = {
        ('users', 'orders'): '1:N',
        ('orders', 'order_items'): '1:N',
        ('products', 'order_items'): '1:N',
    }
    
    # Create dataset
    dataset = MultiTableDataset(
        tables=tables,
        shared_keys=shared_keys,
        relationship_types=relationship_types,
    )
    
    print(f"✅ Created MultiTableDataset with {len(dataset.get_all_tables())} tables")
    print(f"   Tables: {dataset.get_all_tables()}")
    
    # Test getting related indices
    related = dataset.get_related_indices('users', 'orders', [0, 1])
    print(f"✅ Related indices: user 0 -> orders {related[0]}, user 1 -> orders {related[1]}")
    
    # Test batch generation
    batch = dataset.get_batch('users', [0, 1])
    print(f"✅ Generated batch for users table with {len(batch)} columns")
    
    return dataset


def test_graph_encoder_config():
    """Test GraphEncoder configuration creation."""
    print("\n" + "=" * 80)
    print("Testing GraphEncoder Configuration")
    print("=" * 80)
    
    d_model = 128
    
    # Create config
    key_matcher_config = KeyMatcherConfig(
        use_hash_matching=True,
        hash_bucket_size=10000,
    )
    
    relationship_config = RelationshipEncoderConfig(
        d_model=d_model,
        key_matcher_config=key_matcher_config,
        n_hidden_layers=2,
        dropout=0.1,
        aggregation_method="mean",
    )
    
    attention_config = CrossTableAttentionConfig(
        d_model=d_model,
        n_heads=8,
        dropout=0.1,
        use_relationship_weights=True,
    )
    
    fusion_config = FusionLayerConfig(
        d_model=d_model,
        n_hidden_layers=2,
        use_gating=True,
        dropout=0.1,
    )
    
    graph_config = GraphEncoderConfig(
        d_model=d_model,
        relationship_config=relationship_config,
        attention_config=attention_config,
        fusion_config=fusion_config,
        freeze_table_encoders=False,
    )
    
    print(f"✅ Created GraphEncoderConfig with d_model={d_model}")
    return graph_config


if __name__ == '__main__':
    print("GraphEncoder Test Suite")
    print("=" * 80)
    
    # Test MultiTableDataset
    dataset = test_multi_table_dataset()
    
    # Test configuration
    config = test_graph_encoder_config()
    
    print("\n" + "=" * 80)
    print("✅ All basic tests passed!")
    print("=" * 80)
    print("\nNote: Full GraphEncoder testing requires trained TableEncoders.")
    print("See integration tests in embedded_space.py for complete examples.")

