#!/usr/bin/env python3
"""
Test MIN_SUPPORT_RANK scaling across different column counts.

This test creates DynamicRelationshipExtractor instances for column counts
from 1 to 200 and plots how MIN_SUPPORT_RANK scales with the number of columns.
"""

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Add paths for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "lib"))
sys.path.insert(0, str(project_root / "src"))

from featrix.neural.dynamic_relationship_extractor import DynamicRelationshipExtractor

logging.basicConfig(level=logging.WARNING)  # Suppress verbose logging
logger = logging.getLogger(__name__)


def compute_thresholds_for_n_cols(n_cols: int, gpu_memory_gb: float = 24.0) -> dict:
    """
    Compute MIN_SUPPORT thresholds for a given number of columns.
    
    Args:
        n_cols: Number of columns
        gpu_memory_gb: GPU memory in GB (default 24GB)
    
    Returns:
        Dictionary with threshold values and computed parameters
    """
    # Create dummy column names
    col_names = [f"col_{i}" for i in range(n_cols)]
    
    # Create extractor instance
    extractor = DynamicRelationshipExtractor(
        d_model=128,
        col_names_in_order=col_names,
        gpu_memory_gb=gpu_memory_gb,
        batch_size_hint=128,
    )
    
    # Compute expected observations per pair
    total_undirected_pairs = len(extractor.all_pairs)
    active_pairs_per_batch = extractor.max_pairs_per_chunk
    time_window_steps = 2000
    
    if total_undirected_pairs > 0:
        expected_obs_per_pair = (active_pairs_per_batch * time_window_steps) / total_undirected_pairs
    else:
        expected_obs_per_pair = float('inf')
    
    return {
        'n_cols': n_cols,
        'total_pairs': total_undirected_pairs,
        'active_pairs_per_batch': active_pairs_per_batch,
        'expected_obs_per_pair': expected_obs_per_pair,
        'MIN_SUPPORT_TRACK': extractor.MIN_SUPPORT_TRACK,
        'MIN_SUPPORT_RANK': extractor.MIN_SUPPORT_RANK,
        'MIN_SUPPORT_PRUNE': extractor.MIN_SUPPORT_PRUNE,
        'initial_min_support_rank': extractor._initial_min_support_rank,
    }


def simulate_adaptive_adjustment(extractor, n_cols: int) -> dict:
    """
    Simulate adaptive adjustment by creating fake observation statistics.
    
    Args:
        extractor: DynamicRelationshipExtractor instance
        n_cols: Number of columns
    
    Returns:
        Dictionary with adjusted threshold values
    """
    # Create some fake pair statistics with realistic n_total values
    # Simulate that we've observed pairs with varying support
    active_pairs = list(extractor.all_pairs)
    
    # Simulate observations: some pairs have high support, some low
    # Use a realistic distribution based on max_n_ij from the log (64)
    # But spread it across pairs so n_total varies
    np.random.seed(42)  # For reproducibility
    
    n_total_values = []
    for pair in active_pairs[:min(100, len(active_pairs))]:  # Sample up to 100 pairs
        i, j = pair
        # Simulate: most pairs have low support, few have high support
        # Use exponential distribution with mean around 30-40
        n_ij = int(np.random.exponential(30))
        n_ji = int(np.random.exponential(30))
        n_total = n_ij + n_ji
        
        # Store in pair_stats
        extractor._pair_stats[(i, j)] = {
            'n': n_ij,
            'lift_ema': 0.1,
            'source_counts': {'null': n_ij, 'bootstrap': 0},
        }
        extractor._pair_stats[(j, i)] = {
            'n': n_ji,
            'lift_ema': 0.1,
            'source_counts': {'null': n_ji, 'bootstrap': 0},
        }
        
        if n_total > 0:
            n_total_values.append(n_total)
    
    # Now simulate the adaptive adjustment logic
    original_rank = extractor.MIN_SUPPORT_RANK
    if n_total_values and len(n_total_values) >= 10:
        p50_n_total = np.percentile(n_total_values, 50)
        p75_n_total = np.percentile(n_total_values, 75)
        max_n_total = max(n_total_values)
        
        # Apply adaptive adjustment
        adaptive_rank = max(int(p50_n_total), extractor.MIN_SUPPORT_TRACK * 2)
        adaptive_rank = min(adaptive_rank, int(p75_n_total))
        adaptive_rank = max(10, min(adaptive_rank, extractor._initial_min_support_rank))
        
        if adaptive_rank < extractor.MIN_SUPPORT_RANK:
            extractor.MIN_SUPPORT_RANK = adaptive_rank
        
        return {
            'original_rank': original_rank,
            'adjusted_rank': extractor.MIN_SUPPORT_RANK,
            'p50_n_total': p50_n_total,
            'p75_n_total': p75_n_total,
            'max_n_total': max_n_total,
            'was_adjusted': adaptive_rank < original_rank,
        }
    else:
        return {
            'original_rank': original_rank,
            'adjusted_rank': original_rank,
            'was_adjusted': False,
        }


def main():
    """Run the test and generate plots."""
    print("Computing MIN_SUPPORT_RANK for column counts 1-200...")
    
    # Test different GPU memory sizes
    gpu_configs = [
        (24.0, "24GB GPU"),
        (48.0, "48GB GPU"),
        (95.0, "95GB GPU"),
    ]
    
    # Column counts to test (skip 1 column since it has 0 pairs)
    n_cols_range = list(range(2, 201))
    
    results = {}
    for gpu_memory, gpu_label in gpu_configs:
        print(f"\nTesting with {gpu_label}...")
        results[gpu_label] = {
            'n_cols': [],
            'min_support_rank': [],
            'min_support_track': [],
            'min_support_prune': [],
            'expected_obs_per_pair': [],
            'active_pairs_per_batch': [],
            'total_pairs': [],
        }
        
        for n_cols in n_cols_range:
            if n_cols % 20 == 0:
                print(f"  Processing {n_cols} columns...")
            
            try:
                data = compute_thresholds_for_n_cols(n_cols, gpu_memory)
                results[gpu_label]['n_cols'].append(data['n_cols'])
                results[gpu_label]['min_support_rank'].append(data['MIN_SUPPORT_RANK'])
                results[gpu_label]['min_support_track'].append(data['MIN_SUPPORT_TRACK'])
                results[gpu_label]['min_support_prune'].append(data['MIN_SUPPORT_PRUNE'])
                results[gpu_label]['expected_obs_per_pair'].append(
                    data['expected_obs_per_pair'] if data['expected_obs_per_pair'] != float('inf') else 0
                )
                results[gpu_label]['active_pairs_per_batch'].append(data['active_pairs_per_batch'])
                results[gpu_label]['total_pairs'].append(data['total_pairs'])
            except Exception as e:
                print(f"  Error at {n_cols} columns: {e}")
                continue
    
    # Create plots
    print("\nGenerating plots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('MIN_SUPPORT_RANK Scaling Across Column Counts', fontsize=16, fontweight='bold')
    
    # Plot 1: MIN_SUPPORT_RANK vs column count
    ax1 = axes[0, 0]
    for gpu_label, data in results.items():
        ax1.plot(data['n_cols'], data['min_support_rank'], label=gpu_label, linewidth=2)
    ax1.set_xlabel('Number of Columns', fontsize=12)
    ax1.set_ylabel('MIN_SUPPORT_RANK', fontsize=12)
    ax1.set_title('MIN_SUPPORT_RANK vs Column Count', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 200)
    ax1.axhline(y=200, color='r', linestyle='--', alpha=0.5, label='Max (200)')
    ax1.axhline(y=10, color='g', linestyle='--', alpha=0.5, label='Min (10)')
    
    # Plot 2: All three thresholds
    ax2 = axes[0, 1]
    # Use 24GB GPU as representative
    data_24gb = results['24GB GPU']
    ax2.plot(data_24gb['n_cols'], data_24gb['min_support_track'], label='MIN_SUPPORT_TRACK', linewidth=2)
    ax2.plot(data_24gb['n_cols'], data_24gb['min_support_rank'], label='MIN_SUPPORT_RANK', linewidth=2)
    ax2.plot(data_24gb['n_cols'], data_24gb['min_support_prune'], label='MIN_SUPPORT_PRUNE', linewidth=2)
    ax2.set_xlabel('Number of Columns', fontsize=12)
    ax2.set_ylabel('Threshold Value', fontsize=12)
    ax2.set_title('All Support Thresholds (24GB GPU)', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 200)
    
    # Plot 3: Expected observations per pair
    ax3 = axes[1, 0]
    for gpu_label, data in results.items():
        ax3.plot(data['n_cols'], data['expected_obs_per_pair'], label=gpu_label, linewidth=2)
    ax3.set_xlabel('Number of Columns', fontsize=12)
    ax3.set_ylabel('Expected Observations per Pair', fontsize=12)
    ax3.set_title('Expected Observations per Pair vs Column Count', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 200)
    ax3.set_yscale('log')
    
    # Plot 4: Active pairs per batch
    ax4 = axes[1, 1]
    for gpu_label, data in results.items():
        ax4.plot(data['n_cols'], data['active_pairs_per_batch'], label=gpu_label, linewidth=2)
    ax4.set_xlabel('Number of Columns', fontsize=12)
    ax4.set_ylabel('Active Pairs per Batch', fontsize=12)
    ax4.set_title('Active Pairs per Batch vs Column Count', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 200)
    
    plt.tight_layout()
    
    # Save plot
    output_file = Path(__file__).parent / 'min_support_rank_scaling.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    
    # Print summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    for gpu_label, data in results.items():
        print(f"\n{gpu_label}:")
        if data['min_support_rank']:
            print(f"  MIN_SUPPORT_RANK range: {min(data['min_support_rank'])} - {max(data['min_support_rank'])}")
            # Find indices for specific column counts
            n_cols_list = data['n_cols']
            for target_cols in [21, 50, 100, 200]:
                if target_cols in n_cols_list:
                    idx = n_cols_list.index(target_cols)
                    print(f"  MIN_SUPPORT_RANK at {target_cols} cols: {data['min_support_rank'][idx]}")
                elif target_cols < max(n_cols_list):
                    # Find closest
                    closest = min(n_cols_list, key=lambda x: abs(x - target_cols))
                    idx = n_cols_list.index(closest)
                    print(f"  MIN_SUPPORT_RANK at {closest} cols (closest to {target_cols}): {data['min_support_rank'][idx]}")
        
        # Find where it hits the max
        max_indices = [i for i, v in enumerate(data['min_support_rank']) if v == 200]
        if max_indices:
            print(f"  Hits max (200) starting at: {max_indices[0] + 1} columns")
        else:
            print(f"  Never hits max (200)")
    
    # Test adaptive adjustment for a few column counts
    print("\n" + "="*80)
    print("ADAPTIVE ADJUSTMENT SIMULATION")
    print("="*80)
    
    test_cols = [10, 21, 50, 100]
    for n_cols in test_cols:
        print(f"\n{n_cols} columns:")
        col_names = [f"col_{i}" for i in range(n_cols)]
        extractor = DynamicRelationshipExtractor(
            d_model=128,
            col_names_in_order=col_names,
            gpu_memory_gb=24.0,
            batch_size_hint=128,
        )
        original = extractor.MIN_SUPPORT_RANK
        adjustment = simulate_adaptive_adjustment(extractor, n_cols)
        print(f"  Initial MIN_SUPPORT_RANK: {original}")
        if adjustment['was_adjusted']:
            print(f"  After adaptive adjustment: {adjustment['adjusted_rank']}")
            print(f"  Adjustment based on: p50={adjustment['p50_n_total']:.1f}, "
                  f"p75={adjustment['p75_n_total']:.1f}, max={adjustment['max_n_total']}")
        else:
            print(f"  No adjustment needed (stays at {original})")


if __name__ == '__main__':
    main()

