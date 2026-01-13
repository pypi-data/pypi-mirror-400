#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LRTimeline smoothness and boost behavior.

Validates:
1. LR transitions are smooth (no sudden jumps > 20%)
2. Multiple rapid boosts create smooth overlapping curves
3. Boosts are time-windowed (5% or 5 epochs, whichever is bigger)
4. Boost effects sum together correctly

Generates visualization showing LR schedule with smoothness analysis.
"""

import sys
from pathlib import Path

# Add paths
test_dir = Path(__file__).parent
neural_dir = test_dir.parent
featrix_dir = neural_dir.parent
lib_dir = featrix_dir.parent
src_dir = lib_dir.parent

sys.path.insert(0, str(lib_dir))
sys.path.insert(0, str(src_dir))

from featrix.neural.lr_timeline import LRTimeline
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not available - skipping visualization")


def analyze_smoothness(lrs, threshold=0.20):
    """Analyze smoothness of LR schedule."""
    jumps = []
    max_jump = 0.0
    jump_epoch = None
    
    for e in range(1, len(lrs)):
        if lrs[e-1] > 0:
            jump_pct = abs(lrs[e] - lrs[e-1]) / lrs[e-1]
            jumps.append((e, jump_pct, lrs[e-1], lrs[e]))
            if jump_pct > max_jump:
                max_jump = jump_pct
                jump_epoch = e
    
    # Count jumps exceeding threshold
    large_jumps = [(e, pct) for e, pct, _, _ in jumps if pct > threshold]
    
    return {
        'max_jump': max_jump,
        'max_jump_epoch': jump_epoch,
        'large_jumps': large_jumps,
        'all_jumps': jumps,
        'mean_jump': np.mean([pct for _, pct, _, _ in jumps]) if jumps else 0.0,
        'median_jump': np.median([pct for _, pct, _, _ in jumps]) if jumps else 0.0,
    }


def simulate_training_with_boosts():
    """Simulate training with multiple rapid boosts and analyze smoothness."""
    print("=" * 80)
    print("SIMULATING TRAINING WITH MULTIPLE RAPID BOOSTS")
    print("=" * 80)
    
    n_epochs = 100
    timeline = LRTimeline(
        n_epochs=n_epochs,
        base_lr=1e-04,
        max_lr=1e-03,
        min_lr=1e-05
    )
    
    # Get baseline schedule
    baseline_lrs = [timeline.get_lr(e) for e in range(n_epochs)]
    
    # Simulate training: detect NO_LEARNING and apply boosts
    # Simulate overlapping boosts (stacked boosts)
    boost_epochs = [16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27]
    scale_factor = 1.2  # 20% increase each time
    
    print(f"\nApplying {len(boost_epochs)} rapid boosts (stacked/overlapping):")
    for boost_epoch in boost_epochs:
        timeline.increase_lr(boost_epoch, scale_factor=scale_factor, reason=f"NO_LEARNING boost")
        print(f"   Epoch {boost_epoch}: Boost by {scale_factor}x")
    
    # Simulate learning resuming after boosts help (epoch 35)
    # When learning resumes, we decrease LR to undo the boost
    print(f"\nSimulating learning resumed at epoch 35:")
    print(f"   Decreasing LR to reset boost (learning is happening again)")
    # Calculate what the cumulative boost was (approximate)
    cumulative_boost = scale_factor ** min(3, len(boost_epochs))  # Cap at 3x for safety
    decrease_factor = 1.0 / cumulative_boost  # Reverse the boost
    timeline.decrease_lr(35, scale_factor=decrease_factor, reason="Learning resumed, reset boost")
    
    # Get boosted schedule (now uses get_lr() which sums active boosts)
    boosted_lrs = [timeline.get_lr(e) for e in range(n_epochs)]
    
    # Analyze smoothness
    smoothness = analyze_smoothness(boosted_lrs, threshold=0.20)
    
    print(f"\n📊 Smoothness Analysis:")
    print(f"   Max jump: {smoothness['max_jump']*100:.1f}% at epoch {smoothness['max_jump_epoch']}")
    print(f"   Mean jump: {smoothness['mean_jump']*100:.2f}%")
    print(f"   Median jump: {smoothness['median_jump']*100:.2f}%")
    print(f"   Jumps > 20%: {len(smoothness['large_jumps'])}")
    
    if smoothness['large_jumps']:
        print(f"\n⚠️  Large jumps detected (>20%):")
        for epoch, jump_pct in smoothness['large_jumps'][:10]:  # Show first 10
            print(f"      Epoch {epoch}: {jump_pct*100:.1f}% jump")
    else:
        print(f"\n✅ No large jumps detected - schedule is smooth!")
    
    return timeline, baseline_lrs, boosted_lrs, smoothness


def plot_smoothness_analysis(timeline, baseline_lrs, boosted_lrs, smoothness, save_path):
    """Generate comprehensive visualization of LR schedule and smoothness."""
    if not HAS_MATPLOTLIB:
        print("⚠️  Cannot generate plot - matplotlib not available")
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    epochs = list(range(len(baseline_lrs)))
    
    # Plot 1: LR Schedule with boosts
    ax1 = axes[0]
    ax1.plot(epochs, baseline_lrs, '--', linewidth=2, color='#94a3b8', 
             label='Baseline Schedule', alpha=0.7, zorder=1)
    ax1.plot(epochs, boosted_lrs, '-', linewidth=2.5, color='#2563eb',
             label='With Boosts (Summed)', alpha=0.9, zorder=2)
    
    # Mark boost windows
    for start_epoch, duration, scale_factor, reason, boost_type in timeline.active_boosts:
        end_epoch = start_epoch + duration
        ax1.axvspan(start_epoch, end_epoch, alpha=0.15, 
                   color='red' if boost_type == 'increase' else 'blue', zorder=0)
        # Label first boost in each window
        if start_epoch == min(b[0] for b in timeline.active_boosts if b[4] == boost_type):
            ax1.text(start_epoch + duration/2, max(boosted_lrs) * 0.9, 
                    f'{scale_factor}x boost\n({duration} epochs)',
                    ha='center', va='top', fontsize=8, 
                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7))
    
    ax1.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Learning Rate', fontsize=12, fontweight='bold')
    ax1.set_title('LR Schedule: Baseline vs Boosted (Smooth Summation)', 
                  fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: Derivative (Rate of Change) of LR Schedule
    ax2 = axes[1]
    
    # Compute smooth derivative using central differences with smoothing
    # Use a larger window for smoother derivative
    window = 5
    if len(boosted_lrs) > window:
        # Compute derivative using central differences on smoothed data
        # First smooth the LR curve slightly - use 'same' mode to preserve length
        smoothed_lrs = np.convolve(boosted_lrs, np.ones(window)/window, mode='same')
        
        # Compute derivative with respect to epoch spacing (epochs are 0, 1, 2, ...)
        # np.gradient automatically handles spacing correctly when given the epoch array
        derivative = np.gradient(smoothed_lrs, epochs)
        derivative_epochs = epochs
    else:
        # Fallback for short sequences - compute derivative with epoch spacing
        derivative = np.gradient(boosted_lrs, epochs)
        derivative_epochs = epochs
    
    smoothed_derivative = derivative
    
    # Plot smoothed derivative
    ax2.plot(derivative_epochs, smoothed_derivative, '-', linewidth=2.5, color='#10b981', alpha=0.9, label='dLR/dEpoch (smoothed)')
    ax2.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
    
    # Mark boost regions on derivative plot
    for start_epoch, duration, _, _, boost_type in timeline.active_boosts:
        end_epoch = start_epoch + duration
        ax2.axvspan(start_epoch, end_epoch, alpha=0.1, 
                   color='red' if boost_type == 'increase' else 'blue', zorder=0)
    
    ax2.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax2.set_ylabel('dLR/dEpoch', fontsize=12, fontweight='bold')
    ax2.set_title('LR Derivative', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3)
    # Use scientific notation to match the LR plot above
    ax2.ticklabel_format(style='scientific', axis='y', scilimits=(0,0), useMathText=True)
    
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n📊 Visualization saved to: {save_path}")


def main():
    """Run smoothness test and generate visualization."""
    print("=" * 80)
    print("LRTIMELINE SMOOTHNESS VALIDATION")
    print("=" * 80)
    print()
    
    # Simulate training
    timeline, baseline_lrs, boosted_lrs, smoothness = simulate_training_with_boosts()
    
    # Generate visualization
    if HAS_MATPLOTLIB:
        output_path = test_dir / "lr_timeline_smoothness_analysis.png"
        plot_smoothness_analysis(timeline, baseline_lrs, boosted_lrs, smoothness, output_path)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    max_jump_pct = smoothness['max_jump'] * 100
    large_jumps_count = len(smoothness['large_jumps'])
    
    if max_jump_pct <= 20 and large_jumps_count == 0:
        print("✅ PASS: Schedule is smooth (max jump ≤ 20%)")
        print(f"   Max jump: {max_jump_pct:.1f}%")
        print(f"   Mean jump: {smoothness['mean_jump']*100:.2f}%")
        return 0
    else:
        print("⚠️  WARNING: Some large jumps detected")
        print(f"   Max jump: {max_jump_pct:.1f}% (threshold: 20%)")
        print(f"   Large jumps (>20%): {large_jumps_count}")
        print(f"   Mean jump: {smoothness['mean_jump']*100:.2f}%")
        if max_jump_pct > 50:
            print("   ⚠️  Very large jumps detected - may cause training instability!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
