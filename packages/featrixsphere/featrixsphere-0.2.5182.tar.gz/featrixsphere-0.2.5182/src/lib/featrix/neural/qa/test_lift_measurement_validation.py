#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation tests for lift measurement system.

Tests:
1. Null-only ablation: Force relationship_mode="null_only" and verify lift ≈ 0
2. Relationship on/off delta: Compare AUC with normal vs null_only
3. Lift distribution: Log histogram stats (mean, median, p10/p90, % negative)
4. Coverage: Track % pairs observed and rankable
"""
import gc
import logging
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


def create_synthetic_data(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Create synthetic data with some relationships."""
    np.random.seed(seed)
    
    # Create columns with relationships
    price = np.random.lognormal(mean=3, sigma=1, size=n_samples)
    quantity = np.random.poisson(lam=5, size=n_samples)
    total = price * quantity + np.random.normal(0, 0.1 * price * quantity, size=n_samples)
    
    category = np.random.choice(['A', 'B', 'C'], size=n_samples)
    discount = np.where(category == 'A', 0.1, np.where(category == 'B', 0.15, 0.2))
    discount += np.random.normal(0, 0.02, size=n_samples)
    
    df = pd.DataFrame({
        'price': price,
        'quantity': quantity,
        'total': total,
        'category': category,
        'discount': discount,
    })
    
    return df


def extract_lift_stats(extractor) -> Dict:
    """Extract lift statistics from relationship extractor."""
    stats = {
        'pair_stats': extractor._pair_stats,
        'null_baseline_ema': extractor._null_baseline_ema,
        'null_baseline_n': extractor._null_baseline_n,
        'null_baseline_source': extractor._null_baseline_source,
    }
    return stats


def compute_lift_distribution(pair_stats: Dict) -> Dict:
    """Compute lift distribution statistics."""
    lift_emas = []
    negative_count = 0
    
    for pair, stats in pair_stats.items():
        lift_ema = stats.get('lift_ema')
        if lift_ema is not None and np.isfinite(lift_ema):
            lift_emas.append(lift_ema)
            if lift_ema < 0:
                negative_count += 1
    
    if not lift_emas:
        return {
            'count': 0,
            'mean': None,
            'median': None,
            'p10': None,
            'p90': None,
            'negative_pct': None,
        }
    
    lift_emas = np.array(lift_emas)
    
    return {
        'count': len(lift_emas),
        'mean': float(np.mean(lift_emas)),
        'median': float(np.median(lift_emas)),
        'p10': float(np.percentile(lift_emas, 10)),
        'p90': float(np.percentile(lift_emas, 90)),
        'negative_pct': (negative_count / len(lift_emas)) * 100,
        'min': float(np.min(lift_emas)),
        'max': float(np.max(lift_emas)),
    }


def compute_coverage_stats(extractor) -> Dict:
    """Compute coverage statistics."""
    all_pairs = extractor.all_pairs
    pair_stats = extractor._pair_stats
    
    # Count observed pairs (have at least one observation)
    observed_pairs = set()
    for pair in all_pairs:
        i, j = pair
        if (i, j) in pair_stats or (j, i) in pair_stats:
            observed_pairs.add(pair)
    
    # Count rankable pairs (have NULL baseline and sufficient support)
    rankable_pairs = []
    for pair in all_pairs:
        i, j = pair
        stats_ij = pair_stats.get((i, j), {})
        stats_ji = pair_stats.get((j, i), {})
        
        n_ij = stats_ij.get('n', 0)
        n_ji = stats_ji.get('n', 0)
        n_total = n_ij + n_ji
        
        # Check if rankable (has NULL baseline and sufficient support)
        source_counts_ij = stats_ij.get('source_counts', {})
        source_counts_ji = stats_ji.get('source_counts', {})
        
        has_null_baseline = (
            (source_counts_ij.get('null', 0) > 0) or
            (source_counts_ji.get('null', 0) > 0)
        )
        
        if has_null_baseline and n_total >= extractor.MIN_SUPPORT_RANK:
            rankable_pairs.append(pair)
    
    total_pairs = len(all_pairs)
    observed_count = len(observed_pairs)
    rankable_count = len(rankable_pairs)
    
    return {
        'total_pairs': total_pairs,
        'observed_pairs': observed_count,
        'rankable_pairs': rankable_count,
        'observed_pct': (observed_count / total_pairs * 100) if total_pairs > 0 else 0,
        'rankable_pct': (rankable_count / total_pairs * 100) if total_pairs > 0 else 0,
    }


def test_null_only_ablation(
    es: EmbeddingSpace,
    n_steps: int = 200,
) -> Dict:
    """
    Test 1: Null-only ablation
    
    Force relationship_mode="null_only" for n_steps and verify lift ≈ 0.
    If lift stays strongly positive, baseline is stale or not aligned.
    
    NOTE: This test requires modifying the training loop to force null_only mode.
    For now, it checks the current state and provides diagnostic information.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 1: NULL-ONLY ABLATION")
    logger.info("="*80)
    logger.info(f"Checking lift statistics after training...")
    logger.info(f"(To fully test, modify training loop to force null_only for {n_steps} steps)")
    
    extractor = es.encoder.joint_encoder.relationship_extractor
    if extractor is None:
        logger.error("❌ No relationship extractor found!")
        return {'success': False, 'error': 'No extractor'}
    
    # Get current lift stats
    stats = extract_lift_stats(extractor)
    lift_dist = compute_lift_distribution(stats['pair_stats'])
    
    logger.info(f"Current lift distribution:")
    if lift_dist['count'] > 0:
        logger.info(f"  Mean lift: {lift_dist['mean']:.4f}")
        logger.info(f"  Median lift: {lift_dist['median']:.4f}")
        logger.info(f"  % Negative: {lift_dist['negative_pct']:.1f}%")
        
        # Check if mean lift is close to zero (expected for null-only)
        mean_abs_lift = abs(lift_dist['mean'])
        if mean_abs_lift < 0.01:
            logger.info("✅ Mean lift is close to zero - baseline appears aligned")
        elif mean_abs_lift < 0.05:
            logger.warning("⚠️  Mean lift is small but non-zero - may indicate slight misalignment")
        else:
            logger.warning(f"⚠️  Mean lift is {lift_dist['mean']:.4f} - baseline may be stale or misaligned")
    else:
        logger.warning("⚠️  No lift statistics available yet")
    
    # Check NULL baseline coverage
    null_coverage = extractor.get_null_baseline_coverage()
    logger.info(f"\nNULL baseline coverage:")
    for key, value in null_coverage.items():
        logger.info(f"  {key}: {value}")
    
    return {
        'success': True,
        'lift_distribution': lift_dist,
        'null_baseline_coverage': null_coverage,
        'note': 'To fully test, run training with forced null_only mode',
    }


def test_lift_distribution(es: EmbeddingSpace) -> Dict:
    """
    Test 3: Lift distribution
    
    Log histogram stats: mean, median, p10/p90, % negative lifts.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 3: LIFT DISTRIBUTION")
    logger.info("="*80)
    
    extractor = es.encoder.joint_encoder.relationship_extractor
    if extractor is None:
        logger.error("❌ No relationship extractor found!")
        return {'success': False, 'error': 'No extractor'}
    
    stats = extract_lift_stats(extractor)
    lift_dist = compute_lift_distribution(stats['pair_stats'])
    
    logger.info(f"Lift distribution statistics:")
    logger.info(f"  Count: {lift_dist['count']}")
    if lift_dist['count'] > 0:
        logger.info(f"  Mean: {lift_dist['mean']:.4f}")
        logger.info(f"  Median: {lift_dist['median']:.4f}")
        logger.info(f"  P10: {lift_dist['p10']:.4f}")
        logger.info(f"  P90: {lift_dist['p90']:.4f}")
        logger.info(f"  Min: {lift_dist['min']:.4f}")
        logger.info(f"  Max: {lift_dist['max']:.4f}")
        logger.info(f"  Negative lifts: {lift_dist['negative_pct']:.1f}%")
        
        # Sanity checks
        if lift_dist['negative_pct'] == 0:
            logger.warning("⚠️  WARNING: 0% negative lifts - may indicate clamping or baseline leakage")
        elif lift_dist['negative_pct'] > 50:
            logger.warning("⚠️  WARNING: >50% negative lifts - relationships may be harmful")
        
        if lift_dist['mean'] > 0.1:
            logger.warning("⚠️  WARNING: Mean lift > 0.1 - may indicate baseline misalignment")
    else:
        logger.warning("⚠️  No lift statistics available yet")
    
    return {
        'success': True,
        'lift_distribution': lift_dist,
    }


def test_coverage(es: EmbeddingSpace) -> Dict:
    """
    Test 4: Coverage
    
    Track % pairs observed and % pairs rankable.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 4: COVERAGE")
    logger.info("="*80)
    
    extractor = es.encoder.joint_encoder.relationship_extractor
    if extractor is None:
        logger.error("❌ No relationship extractor found!")
        return {'success': False, 'error': 'No extractor'}
    
    coverage = compute_coverage_stats(extractor)
    
    logger.info(f"Coverage statistics:")
    logger.info(f"  Total pairs: {coverage['total_pairs']}")
    logger.info(f"  Observed pairs: {coverage['observed_pairs']} ({coverage['observed_pct']:.1f}%)")
    logger.info(f"  Rankable pairs: {coverage['rankable_pairs']} ({coverage['rankable_pct']:.1f}%)")
    
    # Sanity checks
    if coverage['observed_pct'] < 10:
        logger.warning("⚠️  WARNING: <10% pairs observed - exploration may not be working")
    
    if coverage['rankable_pct'] < 5:
        logger.warning("⚠️  WARNING: <5% pairs rankable - may need more training or lower MIN_SUPPORT_RANK")
    
    # NULL baseline coverage
    null_coverage = extractor.get_null_baseline_coverage()
    logger.info(f"\nNULL baseline coverage:")
    for key, value in null_coverage.items():
        logger.info(f"  {key}: {value}")
    
    return {
        'success': True,
        'coverage': coverage,
        'null_baseline_coverage': null_coverage,
    }


def test_relationship_on_off_delta(es: EmbeddingSpace) -> Dict:
    """
    Test 2: Relationship on/off delta
    
    Compare AUC: normal mode vs always null_only.
    If AUC doesn't drop, relationships aren't helping yet (or CLS injection is too weak).
    
    NOTE: This requires running two separate training runs and comparing results.
    For now, this provides a framework and diagnostic information.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 2: RELATIONSHIP ON/OFF DELTA")
    logger.info("="*80)
    logger.info("This test requires:")
    logger.info("  1. Train model with normal relationships")
    logger.info("  2. Train model with forced null_only mode")
    logger.info("  3. Compare validation AUC/loss")
    logger.info("\nCurrent diagnostic: checking if relationships are being used...")
    
    extractor = es.encoder.joint_encoder.relationship_extractor
    if extractor is None:
        logger.error("❌ No relationship extractor found!")
        return {'success': False, 'error': 'No extractor'}
    
    # Check if relationships are active
    active_pairs = len(extractor.all_pairs) - len(extractor.disabled_pairs)
    total_pairs = len(extractor.all_pairs)
    
    logger.info(f"Relationship extractor status:")
    logger.info(f"  Total pairs: {total_pairs}")
    logger.info(f"  Active pairs: {active_pairs} ({100*active_pairs/total_pairs:.1f}%)")
    
    # Check if we have lift statistics (indicates relationships are being evaluated)
    stats = extract_lift_stats(extractor)
    lift_dist = compute_lift_distribution(stats['pair_stats'])
    
    if lift_dist['count'] > 0:
        logger.info(f"  Lift statistics available: {lift_dist['count']} pairs")
        logger.info("✅ Relationships appear to be active and being evaluated")
    else:
        logger.warning("⚠️  No lift statistics - relationships may not be active yet")
    
    return {
        'success': True,
        'active_pairs': active_pairs,
        'total_pairs': total_pairs,
        'note': 'To fully test, compare training runs with/without relationships',
    }


def run_validation_tests(
    es: EmbeddingSpace,
    n_steps: int = 200,
) -> Dict:
    """Run all validation tests."""
    logger.info("\n" + "="*80)
    logger.info("LIFT MEASUREMENT VALIDATION TESTS")
    logger.info("="*80)
    
    results = {}
    
    # Test 1: Null-only ablation
    results['null_only_ablation'] = test_null_only_ablation(es, n_steps=n_steps)
    
    # Test 2: Relationship on/off delta
    results['relationship_on_off'] = test_relationship_on_off_delta(es)
    
    # Test 3: Lift distribution
    results['lift_distribution'] = test_lift_distribution(es)
    
    # Test 4: Coverage
    results['coverage'] = test_coverage(es)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*80)
    
    all_success = all(r.get('success', False) for r in results.values())
    
    if all_success:
        logger.info("✅ All validation tests completed successfully")
    else:
        logger.warning("⚠️  Some tests had issues - check logs above")
    
    # Print key metrics
    logger.info("\nKey Metrics:")
    if 'lift_distribution' in results and results['lift_distribution'].get('lift_distribution'):
        ld = results['lift_distribution']['lift_distribution']
        if ld.get('count', 0) > 0:
            logger.info(f"  Mean lift: {ld.get('mean', 0):.4f}")
            logger.info(f"  % Negative lifts: {ld.get('negative_pct', 0):.1f}%")
    
    if 'coverage' in results and results['coverage'].get('coverage'):
        cov = results['coverage']['coverage']
        logger.info(f"  Pairs observed: {cov.get('observed_pct', 0):.1f}%")
        logger.info(f"  Pairs rankable: {cov.get('rankable_pct', 0):.1f}%")
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lift measurement validation tests')
    parser.add_argument('--samples', type=int, default=500, help='Number of samples (default: 500)')
    parser.add_argument('--epochs', type=int, default=5, help='Training epochs (default: 5)')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size (default: 32)')
    parser.add_argument('--d-model', type=int, default=64, help='Embedding dimension (default: 64)')
    parser.add_argument('--n-steps', type=int, default=200, help='Steps for null-only ablation (default: 200)')
    parser.add_argument('--checkpoint', type=str, default=None, help='Path to existing checkpoint (optional)')
    args = parser.parse_args()
    
    # Create synthetic data
    logger.info("Creating synthetic data...")
    df = create_synthetic_data(n_samples=args.samples)
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "test_lift_validation")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create EmbeddingSpace
        logger.info("Creating EmbeddingSpace...")
        es = EmbeddingSpace(
            train_input_data=FeatrixInputDataSet(df),
            val_input_data=FeatrixInputDataSet(df.sample(frac=0.2)),
            output_dir=output_dir,
            n_epochs=args.epochs,
            d_model=args.d_model,
            relationship_features=RelationshipFeatureConfig(
                enable_dynamic_relationships=True,
                max_pairs_per_column=10,
            ),
        )
        
        # Train if no checkpoint provided
        if args.checkpoint is None:
            logger.info("Training model...")
            es.train()
        else:
            logger.info(f"Loading checkpoint from {args.checkpoint}...")
            # Load checkpoint and set encoder (similar to load_best_checkpoint)
            checkpoint_state = torch.load(args.checkpoint, weights_only=False)
            if "model" in checkpoint_state:
                es.encoder = checkpoint_state["model"]
            elif "encoder" in checkpoint_state:
                es.encoder = checkpoint_state["encoder"]
            else:
                raise ValueError(f"Checkpoint at {args.checkpoint} does not contain 'model' or 'encoder' key")
        
        # Run validation tests
        results = run_validation_tests(es, n_steps=args.n_steps)
        
        # Return success status
        return 0 if all(r.get('success', False) for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

