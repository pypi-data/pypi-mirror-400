#!/usr/bin/env python3
"""
Integration test for DynamicRelationshipExtractor - ON vs OFF comparison.

This test:
1. Creates synthetic data with KNOWN relationships between columns
2. Trains an EmbeddingSpace WITH relationship features enabled
3. Trains an EmbeddingSpace WITHOUT relationship features
4. Compares validation loss, embedding quality, and relationship learning

The synthetic data has explicit relationships:
- total = price * quantity (scalar-scalar relationship)
- discount depends on category (cat-scalar relationship)
- brand and category are correlated (cat-cat relationship)

If relationships work correctly, the model WITH relationships should:
- Learn faster (lower loss at same epoch)
- Produce embeddings that better capture inter-column dependencies
"""
import gc
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Add paths for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "lib"))
sys.path.insert(0, str(project_root / "src"))

from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.model_config import RelationshipFeatureConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def create_synthetic_data_with_relationships(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Create synthetic data with KNOWN relationships between columns.
    
    Relationships:
    1. total = price * quantity + noise (scalar-scalar: multiplication)
    2. discount = f(category) + noise (cat-scalar: category determines discount range)
    3. brand correlates with category (cat-cat: luxury brands in electronics)
    4. tax = price * 0.08 (scalar-scalar: linear)
    5. margin = (price - cost) / price (scalar-scalar: ratio)
    
    Column types:
    - category: categorical (Electronics, Clothing, Food, Books, Sports)
    - brand: categorical (Premium, Standard, Budget)
    - price: scalar (continuous)
    - quantity: scalar (integer-ish)
    - cost: scalar (derived from price)
    - total: scalar (price * quantity)
    - discount: scalar (depends on category)
    - tax: scalar (price * 0.08)
    - margin: scalar ((price - cost) / price)
    """
    np.random.seed(seed)
    
    # Categories and brands
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Sports']
    brands = ['Premium', 'Standard', 'Budget']
    
    # Generate base columns
    category = np.random.choice(categories, n_samples)
    
    # Brand correlates with category (cat-cat relationship)
    # Electronics more likely to be Premium, Food more likely to be Budget
    brand = []
    for cat in category:
        if cat == 'Electronics':
            brand.append(np.random.choice(brands, p=[0.5, 0.3, 0.2]))
        elif cat == 'Food':
            brand.append(np.random.choice(brands, p=[0.1, 0.3, 0.6]))
        else:
            brand.append(np.random.choice(brands, p=[0.33, 0.34, 0.33]))
    brand = np.array(brand)
    
    # Price depends on brand (cat-scalar relationship)
    price = np.zeros(n_samples)
    for i, b in enumerate(brand):
        if b == 'Premium':
            price[i] = np.random.uniform(100, 500)
        elif b == 'Standard':
            price[i] = np.random.uniform(50, 150)
        else:
            price[i] = np.random.uniform(10, 60)
    
    # Quantity is somewhat random but inversely related to price
    quantity = np.maximum(1, np.round(100 / np.sqrt(price) + np.random.randn(n_samples) * 2))
    
    # Cost is 40-70% of price
    cost = price * np.random.uniform(0.4, 0.7, n_samples)
    
    # EXPLICIT RELATIONSHIPS (what we want the model to learn):
    
    # 1. total = price * quantity + small noise (scalar-scalar multiplication)
    total = price * quantity + np.random.randn(n_samples) * 10
    
    # 2. discount depends on category (cat-scalar)
    discount = np.zeros(n_samples)
    for i, cat in enumerate(category):
        if cat == 'Electronics':
            discount[i] = np.random.uniform(0.05, 0.15)  # Low discount
        elif cat == 'Food':
            discount[i] = np.random.uniform(0.0, 0.05)   # Very low
        elif cat == 'Clothing':
            discount[i] = np.random.uniform(0.15, 0.40)  # High discount
        else:
            discount[i] = np.random.uniform(0.05, 0.20)  # Medium
    
    # 3. tax = price * 0.08 (scalar-scalar linear)
    tax = price * 0.08 + np.random.randn(n_samples) * 1
    
    # 4. margin = (price - cost) / price (scalar-scalar ratio)
    margin = (price - cost) / price
    
    df = pd.DataFrame({
        'category': category,
        'brand': brand,
        'price': price,
        'quantity': quantity,
        'cost': cost,
        'total': total,
        'discount': discount,
        'tax': tax,
        'margin': margin,
    })
    
    return df


def train_embedding_space(
    df: pd.DataFrame,
    output_dir: str,
    enable_relationships: bool,
    n_epochs: int = 15,
    batch_size: int = 32,
    d_model: int = 64,
) -> dict:
    """
    Train an EmbeddingSpace and return training metrics.
    
    Args:
        df: Training data
        output_dir: Where to save outputs
        enable_relationships: Whether to enable DynamicRelationshipExtractor
        n_epochs: Training epochs
        batch_size: Batch size
        d_model: Embedding dimension
        
    Returns:
        Dict with training metrics
    """
    # Create dataset
    dataset = FeatrixInputDataSet(
        df=df.copy(),
        ignore_cols=[],
        limit_rows=None,
        encoder_overrides=None,
    )
    
    # Detect column types
    detected_types = {}
    for col_name, detector in dataset._detectors.items():
        detected_types[col_name] = detector.get_codec_name()
    dataset.encoderOverrides = detected_types
    
    # Split
    train_data, val_data = dataset.split(fraction=0.2)
    
    # Configure relationship features
    if enable_relationships:
        rel_config = RelationshipFeatureConfig(
            exploration_epochs=5,
            top_k_fraction=0.40,
        )
        label = "WITH_RELATIONSHIPS"
    else:
        rel_config = None
        label = "NO_RELATIONSHIPS"
    
    logger.info(f"\n{'='*80}")
    logger.info(f"TRAINING: {label}")
    logger.info(f"{'='*80}")
    logger.info(f"  Columns: {list(df.columns)}")
    logger.info(f"  Column types: {detected_types}")
    logger.info(f"  Relationship features: {enable_relationships}")
    logger.info(f"  Epochs: {n_epochs}, Batch size: {batch_size}, d_model: {d_model}")
    
    # Create EmbeddingSpace
    es = EmbeddingSpace(
        train_input_data=train_data,
        val_input_data=val_data,
        output_debug_label=f"relationship_test_{label}",
        output_dir=output_dir,
        d_model=d_model,
        n_transformer_layers=2,
        n_attention_heads=4,
        relationship_features=rel_config,
    )
    
    # Track training start time
    start_time = time.time()
    
    # Train
    es.train(
        batch_size=batch_size,
        n_epochs=n_epochs,
        movie_frame_interval=None,
    )
    
    training_time = time.time() - start_time
    
    # Collect metrics
    metrics = {
        'label': label,
        'enable_relationships': enable_relationships,
        'training_time_seconds': training_time,
        'n_epochs': n_epochs,
        'd_model': d_model,
    }
    
    # Get epoch history from the encoder's epoch records if available
    if hasattr(es, 'encoder') and hasattr(es.encoder, 'epoch_records'):
        epoch_records = es.encoder.epoch_records
        if epoch_records:
            # Get losses over time
            val_losses = [r.get('validation_loss', r.get('val_loss')) for r in epoch_records if r]
            val_losses = [v for v in val_losses if v is not None]
            
            if val_losses:
                metrics['initial_val_loss'] = val_losses[0] if val_losses else None
                metrics['final_val_loss'] = val_losses[-1] if val_losses else None
                metrics['best_val_loss'] = min(val_losses) if val_losses else None
                metrics['val_loss_history'] = val_losses
    
    # Alternative: get from history_db
    if 'final_val_loss' not in metrics and hasattr(es, 'history_db') and es.history_db:
        try:
            loss_history = es.history_db.get_recent_loss_history(num_epochs=1)
            if loss_history:
                metrics['final_val_loss'] = loss_history[-1].get('validation_loss')
        except Exception:
            pass
    
    # Get relationship extractor info if enabled
    if enable_relationships and hasattr(es, 'encoder') and hasattr(es.encoder, 'joint_encoder'):
        je = es.encoder.joint_encoder
        if hasattr(je, 'relationship_extractor') and je.relationship_extractor is not None:
            re = je.relationship_extractor
            metrics['n_pairs'] = len(re.all_pairs)
            metrics['disabled_pairs'] = len(re.disabled_pairs)
            metrics['active_pairs'] = len(re.all_pairs) - len(re.disabled_pairs)
            
            # Get column losses (importance metric)
            if re.col_marginal_losses:
                metrics['col_marginal_losses'] = dict(re.col_marginal_losses)
    
    # Clean up
    del es
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return metrics


def test_relationship_quality(
    df: pd.DataFrame,
    metrics_with: dict,
    metrics_without: dict,
):
    """
    Analyze the quality of relationship learning.
    
    Compare embeddings and predictions between models.
    """
    logger.info(f"\n{'='*80}")
    logger.info("RELATIONSHIP QUALITY ANALYSIS")
    logger.info(f"{'='*80}")
    
    # Compare validation losses
    logger.info("\n📊 VALIDATION LOSS COMPARISON:")
    
    if 'final_val_loss' in metrics_with and 'final_val_loss' in metrics_without:
        loss_with = metrics_with['final_val_loss']
        loss_without = metrics_without['final_val_loss']
        
        if loss_with is not None and loss_without is not None:
            improvement = (loss_without - loss_with) / loss_without * 100
            logger.info(f"  WITH relationships:    {loss_with:.4f}")
            logger.info(f"  WITHOUT relationships: {loss_without:.4f}")
            logger.info(f"  Improvement: {improvement:+.1f}%")
            
            if improvement > 0:
                logger.info(f"  ✅ Relationship features IMPROVED validation loss")
            else:
                logger.info(f"  ⚠️  Relationship features did not improve validation loss")
    
    # Compare training speed
    logger.info("\n⏱️  TRAINING TIME COMPARISON:")
    time_with = metrics_with.get('training_time_seconds', 0)
    time_without = metrics_without.get('training_time_seconds', 0)
    overhead = (time_with - time_without) / time_without * 100 if time_without > 0 else 0
    
    logger.info(f"  WITH relationships:    {time_with:.1f}s")
    logger.info(f"  WITHOUT relationships: {time_without:.1f}s")
    logger.info(f"  Overhead: {overhead:+.1f}%")
    
    # Show loss curves if available
    logger.info("\n📈 VALIDATION LOSS CURVE:")
    hist_with = metrics_with.get('val_loss_history', [])
    hist_without = metrics_without.get('val_loss_history', [])
    
    if hist_with and hist_without:
        max_epochs = max(len(hist_with), len(hist_without))
        logger.info(f"  {'Epoch':<8} {'WITH':>12} {'WITHOUT':>12} {'Diff':>12}")
        logger.info(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*12}")
        
        for i in range(min(max_epochs, 15)):  # Show first 15 epochs
            loss_w = hist_with[i] if i < len(hist_with) else None
            loss_wo = hist_without[i] if i < len(hist_without) else None
            
            if loss_w is not None and loss_wo is not None:
                diff = loss_w - loss_wo
                logger.info(f"  {i+1:<8} {loss_w:>12.4f} {loss_wo:>12.4f} {diff:>+12.4f}")
            elif loss_w is not None:
                logger.info(f"  {i+1:<8} {loss_w:>12.4f} {'N/A':>12} {'N/A':>12}")
            elif loss_wo is not None:
                logger.info(f"  {i+1:<8} {'N/A':>12} {loss_wo:>12.4f} {'N/A':>12}")
    
    # Show relationship extractor stats
    if 'n_pairs' in metrics_with:
        logger.info(f"\n🔗 RELATIONSHIP EXTRACTOR STATS:")
        logger.info(f"  Total pairs: {metrics_with.get('n_pairs', 0)}")
        logger.info(f"  Active pairs: {metrics_with.get('active_pairs', 0)}")
        logger.info(f"  Disabled pairs: {metrics_with.get('disabled_pairs', 0)}")
        
        if 'col_marginal_losses' in metrics_with:
            losses = metrics_with['col_marginal_losses']
            sorted_cols = sorted(losses.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"\n  Column marginal losses (higher = harder to predict):")
            for col, loss in sorted_cols:
                logger.info(f"    {col:<20}: {loss:.4f}")


def run_integration_test(
    n_samples: int = 500,
    n_epochs: int = 10,
    batch_size: int = 32,
    d_model: int = 64,
):
    """
    Run the full integration test comparing relationship features ON vs OFF.
    """
    logger.info("\n" + "="*80)
    logger.info("DYNAMIC RELATIONSHIP EXTRACTOR - INTEGRATION TEST")
    logger.info("Comparing training WITH vs WITHOUT relationship features")
    logger.info("="*80)
    
    # Create synthetic data
    logger.info("\n📊 Creating synthetic data with known relationships...")
    df = create_synthetic_data_with_relationships(n_samples=n_samples)
    
    logger.info(f"  Samples: {len(df)}")
    logger.info(f"  Columns: {list(df.columns)}")
    
    # Show data stats
    logger.info("\n  Column statistics:")
    for col in df.columns:
        if df[col].dtype == 'object':
            n_unique = df[col].nunique()
            logger.info(f"    {col:<15}: categorical, {n_unique} unique values")
        else:
            logger.info(f"    {col:<15}: scalar, range [{df[col].min():.2f}, {df[col].max():.2f}]")
    
    # Show known relationships
    logger.info("\n  Known relationships in data:")
    logger.info("    1. total ≈ price × quantity (scalar-scalar multiplication)")
    logger.info("    2. discount ~ f(category) (cat-scalar dependency)")
    logger.info("    3. brand ~ category (cat-cat correlation)")
    logger.info("    4. tax = price × 0.08 (scalar-scalar linear)")
    logger.info("    5. margin = (price - cost) / price (scalar-scalar ratio)")
    logger.info("    6. price ~ brand (cat-scalar: Premium > Standard > Budget)")
    
    # Create temp directories
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir_with = os.path.join(tmpdir, "with_relationships")
        output_dir_without = os.path.join(tmpdir, "without_relationships")
        os.makedirs(output_dir_with, exist_ok=True)
        os.makedirs(output_dir_without, exist_ok=True)
        
        # Train WITHOUT relationships first (baseline)
        metrics_without = train_embedding_space(
            df=df,
            output_dir=output_dir_without,
            enable_relationships=False,
            n_epochs=n_epochs,
            batch_size=batch_size,
            d_model=d_model,
        )
        
        # Train WITH relationships
        metrics_with = train_embedding_space(
            df=df,
            output_dir=output_dir_with,
            enable_relationships=True,
            n_epochs=n_epochs,
            batch_size=batch_size,
            d_model=d_model,
        )
        
        # Analyze results
        test_relationship_quality(df, metrics_with, metrics_without)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    success = True
    
    # Check that relationship features were actually used
    if 'n_pairs' in metrics_with:
        logger.info(f"  ✅ Relationship extractor created {metrics_with['n_pairs']} pairs")
    else:
        logger.info(f"  ❌ Relationship extractor NOT created")
        success = False
    
    # Check training completed
    if metrics_with.get('final_val_loss') is not None:
        logger.info(f"  ✅ Training WITH relationships completed (loss={metrics_with['final_val_loss']:.4f})")
    else:
        logger.info(f"  ❌ Training WITH relationships may have failed")
        success = False
    
    if metrics_without.get('final_val_loss') is not None:
        logger.info(f"  ✅ Training WITHOUT relationships completed (loss={metrics_without['final_val_loss']:.4f})")
    else:
        logger.info(f"  ❌ Training WITHOUT relationships may have failed")
        success = False
    
    if success:
        logger.info("\n  🎉 Integration test completed successfully!")
    else:
        logger.info("\n  ⚠️  Integration test completed with issues")
    
    return success, metrics_with, metrics_without


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration test for DynamicRelationshipExtractor')
    parser.add_argument('--samples', type=int, default=500, help='Number of samples (default: 500)')
    parser.add_argument('--epochs', type=int, default=10, help='Training epochs (default: 10)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size (default: 32)')
    parser.add_argument('--d-model', type=int, default=64, help='Embedding dimension (default: 64)')
    args = parser.parse_args()
    
    success, metrics_with, metrics_without = run_integration_test(
        n_samples=args.samples,
        n_epochs=args.epochs,
        batch_size=args.batch_size,
        d_model=args.d_model,
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())






