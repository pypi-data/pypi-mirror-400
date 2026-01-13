#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Relationship Performance Estimation: Estimate computational cost and memory
usage of relationship features for different column counts and configurations.
"""
import logging
import time
from typing import Dict, Optional

import torch

from featrix.neural.relationship_complexity import calculate_relationship_complexity
from featrix.neural.gpu_utils import synchronize_gpu

logger = logging.getLogger(__name__)


def estimate_relationship_performance(
    n_cols: int,
    d_model: int = 256,
    batch_size: int = 32,
    enable_ratios: bool = True,
    enable_correlations: bool = True,
    enable_factors: int = 4,
    enable_mi_hints: bool = True,
    max_pairwise_ratios: Optional[int] = None,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Estimate performance characteristics of relationship features.
    
    Returns:
        Dict with performance metrics:
        - 'memory_mb': Estimated memory usage (MB)
        - 'compute_flops': Estimated FLOPs (floating point operations)
        - 'forward_time_ms': Estimated forward pass time (ms)
        - 'ratio_compute_time_ms': Estimated time for ratio computation (ms)
        - 'correlation_compute_time_ms': Estimated time for correlation computation (ms)
        - 'factor_compute_time_ms': Estimated time for factor computation (ms)
        - 'mi_hint_compute_time_ms': Estimated time for MI hint computation (ms)
    """
    complexity = calculate_relationship_complexity(
        n_cols=n_cols,
        enable_ratios=enable_ratios,
        enable_correlations=enable_correlations,
        enable_factors=enable_factors,
        enable_mi_hints=enable_mi_hints,
        max_pairwise_ratios=max_pairwise_ratios,
    )
    
    # Memory estimation (rough)
    # Sequence length * d_model * batch_size * 4 bytes (float32)
    sequence_length = complexity['sequence_length']
    memory_bytes = sequence_length * d_model * batch_size * 4
    memory_mb = memory_bytes / (1024 ** 2)
    
    # FLOPs estimation (rough)
    # Ratios: batch_size * n_ratios * d_model (element-wise ops + MLP)
    # Correlations: batch_size * n_cols^2 * d_model (matrix ops + MLP)
    # Factors: batch_size * n_factors * n_cols * d_model (matrix ops + MLP)
    # MI hints: batch_size * n_cols * d_model (weighted sum + MLP)
    
    flops_ratios = 0
    if enable_ratios:
        # Element-wise division: d_model ops per ratio
        # MLP forward: ~2 * d_model^2 ops (simplified)
        flops_ratios = batch_size * complexity['ratios'] * (d_model + 2 * d_model * d_model)
    
    flops_correlations = 0
    if enable_correlations:
        # Correlation matrix: n_cols^2 * d_model ops
        # MLP forward: ~2 * (n_cols^2) * d_model ops
        flops_correlations = batch_size * (n_cols * n_cols * d_model + 2 * n_cols * n_cols * d_model)
    
    flops_factors = 0
    if enable_factors:
        # Factor computation: n_factors * n_cols * d_model ops
        # MLP forward: ~2 * d_model^2 ops per factor
        flops_factors = batch_size * (enable_factors * n_cols * d_model + enable_factors * 2 * d_model * d_model)
    
    flops_mi_hints = 0
    if enable_mi_hints:
        # Weighted sum: n_cols * d_model ops
        # MLP forward: ~2 * d_model^2 ops
        flops_mi_hints = batch_size * (n_cols * d_model + 2 * d_model * d_model)
    
    total_flops = flops_ratios + flops_correlations + flops_factors + flops_mi_hints
    
    # Time estimation (very rough, based on typical GPU/CPU speeds)
    # Assumes: GPU ~10 TFLOPS, CPU ~100 GFLOPS
    if device == "cuda":
        flops_per_second = 10e12  # 10 TFLOPS
    elif device == "mps":
        flops_per_second = 5e12  # ~5 TFLOPS (MPS is slower than CUDA)
    else:
        flops_per_second = 100e9  # 100 GFLOPS
    
    estimated_time_seconds = total_flops / flops_per_second
    estimated_time_ms = estimated_time_seconds * 1000
    
    # Breakdown by component
    ratio_time_ms = (flops_ratios / flops_per_second) * 1000 if enable_ratios else 0
    correlation_time_ms = (flops_correlations / flops_per_second) * 1000 if enable_correlations else 0
    factor_time_ms = (flops_factors / flops_per_second) * 1000 if enable_factors else 0
    mi_hint_time_ms = (flops_mi_hints / flops_per_second) * 1000 if enable_mi_hints else 0
    
    return {
        'memory_mb': memory_mb,
        'compute_flops': total_flops,
        'forward_time_ms': estimated_time_ms,
        'ratio_compute_time_ms': ratio_time_ms,
        'correlation_compute_time_ms': correlation_time_ms,
        'factor_compute_time_ms': factor_time_ms,
        'mi_hint_compute_time_ms': mi_hint_time_ms,
        'sequence_length': sequence_length,
        'n_relationship_tokens': complexity['total'],
    }


def benchmark_relationship_extractor(
    relationship_extractor,
    batch_size: int = 32,
    n_warmup: int = 5,
    n_iterations: int = 20,
    device: str = "cpu",
) -> Dict[str, float]:
    """
    Benchmark actual relationship extractor performance.
    
    Args:
        relationship_extractor: RelationshipFeatureExtractor instance
        batch_size: Batch size for benchmarking
        n_warmup: Number of warmup iterations
        n_iterations: Number of benchmark iterations
        device: Device to run on
    
    Returns:
        Dict with actual performance metrics:
        - 'forward_time_ms': Average forward pass time (ms)
        - 'forward_time_std_ms': Standard deviation (ms)
        - 'memory_mb': Peak memory usage (MB, if available)
    """
    n_cols = relationship_extractor.n_cols
    d_model = relationship_extractor.d_model
    
    # Create dummy input
    encodings = torch.randn(batch_size, n_cols, d_model, device=device)
    mask = torch.ones(batch_size, n_cols, device=device)
    
    # Warmup
    for _ in range(n_warmup):
        with torch.no_grad():
            _ = relationship_extractor(encodings, mask)
    
    # Benchmark
    times = []
    if device != "cpu":
        synchronize_gpu()
    
    for _ in range(n_iterations):
        if device != "cpu":
            synchronize_gpu()
        
        start_time = time.time()
        with torch.no_grad():
            _ = relationship_extractor(encodings, mask)
        
        if device != "cpu":
            synchronize_gpu()
        
        end_time = time.time()
        times.append((end_time - start_time) * 1000)  # Convert to ms
    
    avg_time = sum(times) / len(times)
    std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
    
    # Memory estimation (rough)
    complexity = calculate_relationship_complexity(
        n_cols=n_cols,
        enable_ratios=relationship_extractor.enable_ratios,
        enable_correlations=relationship_extractor.enable_correlations,
        enable_factors=relationship_extractor.n_factors if relationship_extractor.enable_factors else 0,
        enable_mi_hints=relationship_extractor.enable_mi_hints,
        max_pairwise_ratios=relationship_extractor.max_pairwise_ratios,
    )
    memory_mb = (complexity['sequence_length'] * d_model * batch_size * 4) / (1024 ** 2)
    
    return {
        'forward_time_ms': avg_time,
        'forward_time_std_ms': std_time,
        'memory_mb': memory_mb,
    }


def print_performance_analysis(
    n_cols: int,
    d_model: int = 256,
    batch_size: int = 32,
    enable_ratios: bool = True,
    enable_correlations: bool = True,
    enable_factors: int = 4,
    enable_mi_hints: bool = True,
    max_pairwise_ratios: Optional[int] = None,
    device: str = "cpu",
):
    """Print formatted performance analysis."""
    perf = estimate_relationship_performance(
        n_cols=n_cols,
        d_model=d_model,
        batch_size=batch_size,
        enable_ratios=enable_ratios,
        enable_correlations=enable_correlations,
        enable_factors=enable_factors,
        enable_mi_hints=enable_mi_hints,
        max_pairwise_ratios=max_pairwise_ratios,
        device=device,
    )
    
    logger.info("=" * 80)
    logger.info(f"RELATIONSHIP PERFORMANCE ESTIMATION: {n_cols} columns, batch_size={batch_size}, device={device}")
    logger.info("=" * 80)
    logger.info(f"Memory Usage:")
    logger.info(f"  • Estimated: {perf['memory_mb']:.2f} MB per batch")
    logger.info(f"")
    logger.info(f"Compute Time Breakdown (estimated):")
    logger.info(f"  • Ratios:           {perf['ratio_compute_time_ms']:.2f} ms ({perf['ratio_compute_time_ms']/perf['forward_time_ms']*100:.1f}%)")
    logger.info(f"  • Correlations:      {perf['correlation_compute_time_ms']:.2f} ms ({perf['correlation_compute_time_ms']/perf['forward_time_ms']*100:.1f}%)")
    logger.info(f"  • Factors:          {perf['factor_compute_time_ms']:.2f} ms ({perf['factor_compute_time_ms']/perf['forward_time_ms']*100:.1f}%)")
    logger.info(f"  • MI Hints:         {perf['mi_hint_compute_time_ms']:.2f} ms ({perf['mi_hint_compute_time_ms']/perf['forward_time_ms']*100:.1f}%)")
    logger.info(f"  ─────────────────────────────")
    logger.info(f"  • TOTAL:            {perf['forward_time_ms']:.2f} ms")
    logger.info(f"")
    logger.info(f"Compute Complexity:")
    logger.info(f"  • Total FLOPs:      {perf['compute_flops']/1e9:.2f} GFLOPs")
    logger.info(f"  • Sequence length:  {perf['sequence_length']:,}")
    logger.info(f"  • Relationship tokens: {perf['n_relationship_tokens']:,}")
    logger.info("=" * 80)
    
    # Compare to baseline (no relationship features)
    baseline_seq_len = 1 + n_cols  # CLS + columns
    baseline_memory_mb = (baseline_seq_len * d_model * batch_size * 4) / (1024 ** 2)
    memory_overhead = perf['memory_mb'] / baseline_memory_mb if baseline_memory_mb > 0 else 1.0
    
    logger.info(f"Overhead vs Baseline (no relationship features):")
    logger.info(f"  • Memory: {memory_overhead:.2f}x ({perf['memory_mb'] - baseline_memory_mb:.2f} MB additional)")
    logger.info(f"  • Sequence length: {perf['sequence_length'] / baseline_seq_len:.2f}x")
    logger.info("=" * 80)


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if len(sys.argv) > 1:
        n_cols = int(sys.argv[1])
        device = sys.argv[2] if len(sys.argv) > 2 else "cpu"
        print_performance_analysis(n_cols, device=device)
    else:
        # Show analysis for common column counts
        print("\n" + "=" * 80)
        print("PERFORMANCE ANALYSIS: Different Column Counts (CPU)")
        print("=" * 80 + "\n")
        
        for n_cols in [10, 25, 50, 100]:
            print_performance_analysis(n_cols, device="cpu")
            print()
        
        print("\n" + "=" * 80)
        print("PERFORMANCE ANALYSIS: 100 columns, different limits (GPU)")
        print("=" * 80 + "\n")
        
        for max_ratios in [None, 100, 500, 1000]:
            limit_str = "unlimited" if max_ratios is None else str(max_ratios)
            print(f"\nMax pairwise ratios: {limit_str}")
            print_performance_analysis(100, max_pairwise_ratios=max_ratios, device="cuda")
            print()

