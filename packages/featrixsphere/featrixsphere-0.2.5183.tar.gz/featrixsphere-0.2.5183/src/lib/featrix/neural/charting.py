#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#

"""
Charting utilities for training visualization.
"""

import logging
import os
import traceback
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def plot_training_timeline(
    training_timeline: List[Dict],
    output_dir: str,
    n_epochs: int,
    optimizer_params: Optional[Dict] = None,
    training_info: Optional[Dict] = None
) -> None:
    """Plot comprehensive training timeline: loss, LR, events, and model health metrics as PNG.
    
    Creates a multi-panel plot showing:
    - Training and validation loss over epochs
    - Learning rate schedule
    - Model health metrics (WW alpha, embedding std, column loss std, gradient norms)
    - Timeline events (corrective actions, failures, interventions)
    
    Args:
        training_timeline: List of epoch entry dictionaries from training
        output_dir: Directory to save the plot
        n_epochs: Total number of epochs
        optimizer_params: Optional optimizer parameters for metadata
        training_info: Optional training info dict (for best checkpoint epoch)
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import matplotlib.cm as cm
    except ImportError:
        logger.warning("⚠️  matplotlib not available, skipping timeline plot")
        return
    
    if not training_timeline:
        logger.warning("⚠️  No timeline data available for plotting")
        return
    
    try:
        # Extract data from timeline
        epochs = []
        train_losses = []
        val_losses = []
        learning_rates = []
        dropout_rates = []
        failures = []  # List of (epoch, failure_type) tuples
        corrective_actions = []  # List of (epoch, action_type, trigger) tuples
        early_stop_blocked = []  # List of epochs where early stop was blocked
        
        # Health metrics arrays (aligned with epochs list)
        ww_alpha = []
        embedding_std = []
        column_loss_std = []
        gradient_norms = []
        
        # Track all timeline events (warnings, errors, etc.)
        timeline_events = []  # List of (epoch, event_type, event_subtype, description) tuples
        
        for entry in training_timeline:
            if not isinstance(entry, dict):
                continue
            
            epoch = entry.get('epoch')
            if epoch is None:
                # Some timeline entries might not have epoch (shouldn't happen, but be safe)
                continue
            
            # Check if this is an event entry (warning, error, etc.) vs epoch entry
            # Event entries have 'event_type' field, epoch entries have 'train_loss' or 'learning_rate'
            event_type = entry.get('event_type')
            has_epoch_metrics = entry.get('train_loss') is not None or entry.get('learning_rate') is not None
            
            if event_type and not has_epoch_metrics:
                # This is a timeline event (warning_start, warning_resolved, error, etc.)
                event_subtype = entry.get('warning_type') or entry.get('error_type') or entry.get('action_type', 'UNKNOWN')
                description = entry.get('description', entry.get('warning_type', entry.get('error_type', 'Event')))
                timeline_events.append((epoch, event_type, event_subtype, description))
                # Continue to next entry - don't process as epoch entry
                continue
            
            # This is an epoch entry - extract metrics
            epochs.append(epoch)
            train_losses.append(entry.get('train_loss'))
            val_losses.append(entry.get('validation_loss'))
            learning_rates.append(entry.get('learning_rate'))
            dropout_rates.append(entry.get('dropout_rate'))
            
            # Extract health metrics for this epoch entry (aligned with epochs list)
            # WeightWatcher alpha
            ww_data = entry.get('weightwatcher')
            if ww_data and isinstance(ww_data, dict):
                ww_alpha.append(ww_data.get('avg_alpha'))
            else:
                ww_alpha.append(None)
            
            # Embedding std (from collapse diagnostics if available)
            collapse_diag = entry.get('collapse_diagnostics', {})
            if collapse_diag and isinstance(collapse_diag, dict):
                je = collapse_diag.get('joint_embedding', {})
                if je and isinstance(je, dict):
                    embedding_std.append(je.get('std_per_dim_mean'))
                else:
                    embedding_std.append(None)
            else:
                embedding_std.append(None)
            
            # Column loss std (computed from relationship extractor data if available)
            col_loss_std_val = entry.get('column_loss_std')
            column_loss_std.append(col_loss_std_val)
            
            # Gradient norm
            grad_data = entry.get('gradients', {})
            if grad_data and isinstance(grad_data, dict):
                gradient_norms.append(grad_data.get('unclipped_norm'))
            else:
                # Fallback to direct gradient_norm field
                gradient_norms.append(entry.get('gradient_norm'))
            
            # Track failures
            failures_detected = entry.get('failures_detected', [])
            if failures_detected:
                for failure in failures_detected:
                    failures.append((epoch, failure))
            
            # Track corrective actions
            actions = entry.get('corrective_actions', [])
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get('action_type', 'UNKNOWN')
                    trigger = action.get('trigger', 'UNKNOWN')
                    corrective_actions.append((epoch, action_type, trigger))
            
            # Track early stop blocking
            if entry.get('early_stop_blocked', False):
                early_stop_blocked.append(epoch)
        
        if not epochs:
            logger.warning("⚠️  No valid epoch data in timeline for plotting")
            return
        
        # Create figure with subplots (now 7 panels: loss, LR, and 4 health metrics, events)
        # All share the same x-axis (epochs)
        fig = plt.figure(figsize=(16, 20))
        gs = fig.add_gridspec(7, 1, hspace=0.25, height_ratios=[1, 1, 0.8, 0.8, 0.8, 0.8, 0.8])

        ax1 = fig.add_subplot(gs[0])  # Loss curves
        ax2 = fig.add_subplot(gs[1], sharex=ax1)  # Learning rate
        ax3 = fig.add_subplot(gs[2], sharex=ax1)  # WW Alpha
        ax4 = fig.add_subplot(gs[3], sharex=ax1)  # Embedding std
        ax5 = fig.add_subplot(gs[4], sharex=ax1)  # Column loss std
        ax6 = fig.add_subplot(gs[5], sharex=ax1)  # Gradient norm
        ax7 = fig.add_subplot(gs[6], sharex=ax1)  # Events timeline
        
        # ========== SUBPLOT 1: Loss Curves ==========
        epochs_array = np.array(epochs)
        
        # Plot training loss
        train_mask = np.array([x is not None for x in train_losses])
        if train_mask.any():
            ax1.plot(epochs_array[train_mask], np.array(train_losses)[train_mask], 
                    '-', linewidth=2, color='#dc2626', label='Train Loss', 
                    marker='o', markersize=3, alpha=0.8)
        
        # Plot validation loss
        val_mask = np.array([x is not None for x in val_losses])
        if val_mask.any():
            ax1.plot(epochs_array[val_mask], np.array(val_losses)[val_mask], 
                    '--', linewidth=2, color='#f97316', label='Val Loss', 
                    marker='s', markersize=3, alpha=0.8)
            
            # Mark best epoch (lowest val loss)
            valid_val_losses = [(e, v) for e, v in zip(epochs_array[val_mask], np.array(val_losses)[val_mask]) if v is not None and not np.isnan(v)]
            if valid_val_losses:
                best_epoch, best_loss = min(valid_val_losses, key=lambda x: x[1])
                ax1.scatter([best_epoch], [best_loss], s=200, c='gold', marker='*',
                          zorder=10, edgecolors='black', linewidths=2, label='Best Epoch')
        
        ax1.set_ylabel('Loss', fontsize=12, fontweight='bold')
        ax1.set_title('Training Timeline: Loss + LR + Events', fontsize=16, fontweight='bold', pad=20)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(left=-1)
        
        # ========== SUBPLOT 2: Learning Rate ==========
        lr_mask = np.array([x is not None and x > 0 for x in learning_rates])
        if lr_mask.any():
            ax2.plot(epochs_array[lr_mask], np.array(learning_rates)[lr_mask], 
                    '-', linewidth=2.5, color='#2563eb', label='Learning Rate', 
                    marker='o', markersize=3, alpha=0.8)
        
        # Mark LR adjustments from corrective actions
        lr_actions = [(e, t) for e, a, t in corrective_actions if 'LR' in a.upper()]
        for epoch, trigger in lr_actions:
            if epoch < len(epochs_array) and lr_mask[epochs_array == epoch].any():
                idx = np.where(epochs_array == epoch)[0][0]
                if idx < len(learning_rates) and learning_rates[idx] is not None:
                    ax2.scatter([epoch], [learning_rates[idx]], s=120, c='#dc2626', 
                               marker='^', zorder=10, edgecolors='black', linewidths=1.5)
        
        ax2.set_ylabel('Learning Rate', fontsize=12, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        ax2.set_xlim(left=-1)

        # ========== SUBPLOT 3: WeightWatcher Alpha ==========
        ww_mask = np.array([x is not None and not np.isnan(x) for x in ww_alpha])
        if ww_mask.any():
            ax3.plot(epochs_array[ww_mask], np.array(ww_alpha)[ww_mask],
                    '-', linewidth=2, color='#10b981', label='WW Alpha',
                    marker='o', markersize=3, alpha=0.8)
            ax3.set_ylabel('WW Alpha', fontsize=11, fontweight='bold')
            ax3.set_title('WeightWatcher Alpha', fontsize=12, fontweight='bold', pad=8)
            ax3.legend(loc='best', fontsize=9)
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'No WW Alpha data', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=10, color='gray')
            ax3.set_ylabel('WW Alpha', fontsize=11, fontweight='bold')
        ax3.set_xlim(left=-1)

        # ========== SUBPLOT 4: Embedding Std/Dim ==========
        emb_std_mask = np.array([x is not None and not np.isnan(x) for x in embedding_std])
        if emb_std_mask.any():
            ax4.plot(epochs_array[emb_std_mask], np.array(embedding_std)[emb_std_mask],
                     '-', linewidth=2, color='#8b5cf6', label='Embedding Std/Dim',
                     marker='s', markersize=3, alpha=0.8)
            ax4.set_ylabel('Embedding Std/Dim', fontsize=11, fontweight='bold')
            ax4.set_title('Embedding Std/Dim', fontsize=12, fontweight='bold', pad=8)
            ax4.legend(loc='best', fontsize=9)
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No embedding std data', ha='center', va='center',
                    transform=ax4.transAxes, fontsize=10, color='gray')
            ax4.set_ylabel('Embedding Std/Dim', fontsize=11, fontweight='bold')
        ax4.set_xlim(left=-1)

        # ========== SUBPLOT 5: Column Loss Std ==========
        col_std_mask = np.array([x is not None and not np.isnan(x) for x in column_loss_std])
        if col_std_mask.any():
            ax5.plot(epochs_array[col_std_mask], np.array(column_loss_std)[col_std_mask],
                     '-', linewidth=2, color='#f59e0b', label='Column Loss Std',
                     marker='^', markersize=3, alpha=0.8)
            ax5.set_ylabel('Column Loss Std', fontsize=11, fontweight='bold')
            ax5.set_title('Column Loss Std', fontsize=12, fontweight='bold', pad=8)
            ax5.legend(loc='best', fontsize=9)
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'No column loss std data', ha='center', va='center',
                    transform=ax5.transAxes, fontsize=10, color='gray')
            ax5.set_ylabel('Column Loss Std', fontsize=11, fontweight='bold')
        ax5.set_xlim(left=-1)

        # ========== SUBPLOT 6: Gradient Norm ==========
        grad_mask = np.array([x is not None and x > 0 for x in gradient_norms])
        if grad_mask.any():
            ax6.plot(epochs_array[grad_mask], np.array(gradient_norms)[grad_mask],
                     '-', linewidth=2, color='#6366f1', label='Gradient Norm',
                     marker='x', markersize=3, alpha=0.8)
            ax6.set_ylabel('Gradient Norm', fontsize=11, fontweight='bold')
            ax6.set_title('Gradient Norm', fontsize=12, fontweight='bold', pad=8)
            ax6.set_yscale('log')
            ax6.legend(loc='best', fontsize=9)
            ax6.grid(True, alpha=0.3)
        else:
            ax6.text(0.5, 0.5, 'No gradient norm data', ha='center', va='center',
                    transform=ax6.transAxes, fontsize=10, color='gray')
            ax6.set_ylabel('Gradient Norm', fontsize=11, fontweight='bold')
        ax6.set_xlim(left=-1)
        
        # ========== SUBPLOT 7: Events Timeline ==========
        # Create event markers
        # Combine all event types: failures, corrective actions, early stop blocking, and timeline events
        all_events = []

        # Add failures
        for epoch, failure_type in failures:
            all_events.append((epoch, 'failure', failure_type, f'Failure: {failure_type}'))

        # Add corrective actions
        for epoch, action_type, trigger in corrective_actions:
            all_events.append((epoch, 'corrective_action', action_type, f'Action: {action_type}'))

        # Add early stop blocking
        for epoch in early_stop_blocked:
            all_events.append((epoch, 'early_stop_blocked', 'EARLY_STOP_BLOCKED', 'Early Stop Blocked'))

        # Add timeline events (warnings, errors, etc.)
        for epoch, event_type, event_subtype, description in timeline_events:
            all_events.append((epoch, event_type, event_subtype, description))

        if all_events:
            # Group events by type for better visualization
            event_groups = {
                'failure': [],
                'corrective_action': [],
                'early_stop_blocked': [],
                'warning_start': [],
                'warning_resolved': [],
                'train_val_gradual_rotation': [],
                'error': [],
                'other': []
            }

            for epoch, event_type, event_subtype, description in all_events:
                if event_type in event_groups:
                    event_groups[event_type].append((epoch, event_subtype, description))
                else:
                    event_groups['other'].append((epoch, event_subtype, description))

            # Plot each event group with different markers and colors
            y_offset = 0
            y_spacing = 0.3
            plotted_labels = set()  # Track labels to avoid duplicates

            # 1. Failures (red X markers)
            if event_groups['failure']:
                unique_failures = list(set([subtype for _, subtype, _ in event_groups['failure']]))
                set3_cmap = plt.get_cmap('Set3')
                colors_failures = set3_cmap(np.linspace(0, 1, len(unique_failures)))
                failure_color_map = {ft: colors_failures[i] for i, ft in enumerate(unique_failures)}

                for epoch, failure_type, description in event_groups['failure']:
                    y_pos = y_offset + unique_failures.index(failure_type) * y_spacing
                    label = f'Failure: {failure_type}' if f'Failure: {failure_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=150, c=[failure_color_map[failure_type]],
                               marker='x', zorder=10, linewidths=2, label=label)
                y_offset += len(unique_failures) * y_spacing + 0.2

            # 2. Warning starts (yellow triangle up)
            if event_groups['warning_start']:
                unique_warnings = list(set([subtype for _, subtype, _ in event_groups['warning_start']]))
                for epoch, warning_type, description in event_groups['warning_start']:
                    y_pos = y_offset + unique_warnings.index(warning_type) * y_spacing
                    label = f'Warning: {warning_type}' if f'Warning: {warning_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=120, c='yellow', marker='^',
                               zorder=10, edgecolors='black', linewidths=1.5, label=label, alpha=0.8)
                y_offset += len(unique_warnings) * y_spacing + 0.2

            # 3. Warning resolved (green triangle down)
            if event_groups['warning_resolved']:
                unique_warnings = list(set([subtype for _, subtype, _ in event_groups['warning_resolved']]))
                for epoch, warning_type, description in event_groups['warning_resolved']:
                    y_pos = y_offset + unique_warnings.index(warning_type) * y_spacing
                    label = f'Resolved: {warning_type}' if f'Resolved: {warning_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=120, c='lightgreen', marker='v',
                               zorder=10, edgecolors='black', linewidths=1.5, label=label, alpha=0.8)
                y_offset += len(unique_warnings) * y_spacing + 0.2

            # 4. Corrective actions (blue circles)
            if event_groups['corrective_action']:
                unique_actions = list(set([subtype for _, subtype, _ in event_groups['corrective_action']]))
                pastel1_cmap = plt.get_cmap('Pastel1')
                colors_actions = pastel1_cmap(np.linspace(0, 1, len(unique_actions)))
                action_color_map = {at: colors_actions[i] for i, at in enumerate(unique_actions)}

                for epoch, action_type, description in event_groups['corrective_action']:
                    y_pos = y_offset + unique_actions.index(action_type) * y_spacing
                    label = f'Action: {action_type}' if f'Action: {action_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=100, c=[action_color_map[action_type]],
                               marker='o', zorder=10, edgecolors='black', linewidths=1, label=label)
                y_offset += len(unique_actions) * y_spacing + 0.2

            # 5. Early stop blocking (orange squares)
            if event_groups['early_stop_blocked']:
                y_pos = y_offset
                label = 'Early Stop Blocked' if 'Early Stop Blocked' not in plotted_labels else ''
                if label:
                    plotted_labels.add(label)
                epochs_blocked = [e for e, _, _ in event_groups['early_stop_blocked']]
                ax7.scatter(epochs_blocked, [y_pos] * len(epochs_blocked),
                           s=80, c='orange', marker='s', zorder=10, edgecolors='black', linewidths=1,
                           label=label, alpha=0.7)
                y_offset += y_spacing + 0.2

            # 6. Errors (red diamonds)
            if event_groups['error']:
                unique_errors = list(set([subtype for _, subtype, _ in event_groups['error']]))
                for epoch, error_type, description in event_groups['error']:
                    y_pos = y_offset + unique_errors.index(error_type) * y_spacing
                    label = f'Error: {error_type}' if f'Error: {error_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=130, c='red', marker='D',
                               zorder=10, edgecolors='black', linewidths=1.5, label=label, alpha=0.8)
                y_offset += len(unique_errors) * y_spacing + 0.2

            # 7. Data rotation events (cyan diamonds)
            if event_groups['train_val_gradual_rotation']:
                y_pos = y_offset
                label = 'Data Rotation' if 'Data Rotation' not in plotted_labels else ''
                if label:
                    plotted_labels.add(label)
                rotation_epochs = [e for e, _, _ in event_groups['train_val_gradual_rotation']]
                ax7.scatter(rotation_epochs, [y_pos] * len(rotation_epochs),
                           s=110, c='cyan', marker='D', zorder=10, edgecolors='black', linewidths=1,
                           label=label, alpha=0.7)
                y_offset += y_spacing + 0.2

            # 8. Other events (gray stars)
            if event_groups['other']:
                unique_others = list(set([subtype for _, subtype, _ in event_groups['other']]))
                for epoch, other_type, description in event_groups['other']:
                    y_pos = y_offset + unique_others.index(other_type) * y_spacing
                    label = f'Other: {other_type}' if f'Other: {other_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax7.scatter([epoch], [y_pos], s=90, c='gray', marker='*',
                               zorder=10, edgecolors='black', linewidths=1, label=label, alpha=0.6)

            ax7.set_ylabel('Events', fontsize=12, fontweight='bold')
            ax7.set_xlabel('Epoch', fontsize=12, fontweight='bold')
            ax7.legend(loc='upper right', fontsize=8, ncol=2)
            ax7.grid(True, alpha=0.3, axis='x')
            ax7.set_yticks([])
        else:
            ax7.text(0.5, 0.5, 'No events recorded', ha='center', va='center',
                    transform=ax7.transAxes, fontsize=12, color='gray')
            ax7.set_ylabel('Events', fontsize=12, fontweight='bold')
            ax7.set_xlabel('Epoch', fontsize=12, fontweight='bold')

        ax7.set_xlim(left=-1, right=max(epochs) + 1 if epochs else n_epochs)
        
        # Add metadata text
        metadata_text = []
        if optimizer_params:
            metadata_text.append(f"Initial LR: {optimizer_params.get('lr', 'N/A')}")
        if training_info and 'best_checkpoint_epoch' in training_info:
            metadata_text.append(f"Best Epoch: {training_info.get('best_checkpoint_epoch', 'N/A')}")
        if metadata_text:
            fig.text(0.02, 0.02, ' | '.join(metadata_text), fontsize=9, 
                    verticalalignment='bottom', style='italic', color='gray')
        
        # Save plot
        plot_path = os.path.join(output_dir, "training_timeline.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Training timeline plot saved to: {plot_path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to plot training timeline: {e}")
        logger.error(traceback.format_exc())


def plot_sp_training_timeline(
    training_timeline: List[Dict],
    output_dir: str,
    n_epochs: int,
    optimizer_params: Optional[Dict] = None,
    training_info: Optional[Dict] = None
) -> None:
    """Plot comprehensive Single Predictor training timeline: loss, LR, metrics, and events as PNG.
    
    Creates a multi-panel plot showing:
    - Training and validation loss over epochs
    - Learning rate schedule
    - Metrics (AUC, accuracy, etc.)
    - Timeline events (warnings, errors, corrective actions)
    
    Args:
        training_timeline: List of epoch entry dictionaries from SP training
        output_dir: Directory to save the plot
        n_epochs: Total number of epochs
        optimizer_params: Optional optimizer parameters for metadata
        training_info: Optional training info dict (for best checkpoint epoch)
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import matplotlib.cm as cm
    except ImportError:
        logger.warning("⚠️  matplotlib not available, skipping timeline plot")
        return
    
    if not training_timeline:
        logger.warning("⚠️  No timeline data available for plotting")
        return
    
    try:
        # Extract data from timeline
        epochs = []
        train_losses = []
        val_losses = []
        learning_rates = []
        es_learning_rates = []  # ES (Embedding Space) learning rates
        aucs = []
        accuracies = []
        pr_aucs = []
        roc_aucs = []
        gradient_norms = []
        
        # Track all timeline events
        timeline_events = []
        warnings = []
        corrective_actions = []
        
        for entry in training_timeline:
            if not isinstance(entry, dict):
                continue
            
            epoch = entry.get('epoch')
            if epoch is None:
                continue
            
            # Check if this is an event entry vs epoch entry
            event_type = entry.get('event_type')
            has_epoch_metrics = entry.get('train_loss') is not None or entry.get('learning_rate') is not None
            
            if event_type and not has_epoch_metrics:
                # Timeline event
                event_subtype = entry.get('warning_type') or entry.get('error_type') or entry.get('action_type', 'UNKNOWN')
                description = entry.get('description', entry.get('warning_type', entry.get('error_type', 'Event')))
                timeline_events.append((epoch, event_type, event_subtype, description))
                continue
            
            # Epoch entry - extract metrics
            epochs.append(epoch)
            train_losses.append(entry.get('train_loss'))
            val_losses.append(entry.get('validation_loss'))
            learning_rates.append(entry.get('learning_rate'))
            es_learning_rates.append(entry.get('es_learning_rate'))  # Extract ES LR
            
            # Extract metrics
            metrics = entry.get('metrics', {})
            if isinstance(metrics, dict):
                aucs.append(metrics.get('auc'))
                accuracies.append(metrics.get('accuracy'))
                pr_aucs.append(metrics.get('pr_auc'))
                roc_aucs.append(metrics.get('roc_auc'))
            else:
                aucs.append(None)
                accuracies.append(None)
                pr_aucs.append(None)
                roc_aucs.append(None)
            
            # Gradient norm
            grad_data = entry.get('gradients', {})
            if grad_data and isinstance(grad_data, dict):
                gradient_norms.append(grad_data.get('unclipped_norm'))
            else:
                gradient_norms.append(entry.get('gradient_norm'))
            
            # Track warnings and corrective actions
            if entry.get('warnings'):
                for warning in entry.get('warnings', []):
                    warnings.append((epoch, warning.get('type', 'UNKNOWN')))
            
            if entry.get('corrective_actions'):
                for action in entry.get('corrective_actions', []):
                    if isinstance(action, dict):
                        corrective_actions.append((epoch, action.get('action_type', 'UNKNOWN'), action.get('trigger', 'UNKNOWN')))
        
        if not epochs:
            logger.warning("⚠️  No valid epoch data in timeline for plotting")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 14))
        gs = fig.add_gridspec(4, 1, hspace=0.35, height_ratios=[1, 1, 1, 0.8])
        
        ax1 = fig.add_subplot(gs[0])  # Loss curves
        ax2 = fig.add_subplot(gs[1])  # Learning rate
        ax3 = fig.add_subplot(gs[2])  # Metrics
        ax4 = fig.add_subplot(gs[3])  # Events timeline
        
        epochs_array = np.array(epochs)
        
        # ========== SUBPLOT 1: Loss Curves ==========
        train_mask = np.array([x is not None for x in train_losses])
        if train_mask.any():
            ax1.plot(epochs_array[train_mask], np.array(train_losses)[train_mask], 
                    '-', linewidth=2, color='#dc2626', label='Train Loss', 
                    marker='o', markersize=3, alpha=0.8)
        
        val_mask = np.array([x is not None for x in val_losses])
        if val_mask.any():
            ax1.plot(epochs_array[val_mask], np.array(val_losses)[val_mask], 
                    '--', linewidth=2, color='#f97316', label='Val Loss', 
                    marker='s', markersize=3, alpha=0.8)
            
            # Mark best epoch
            valid_val_losses = [(e, v) for e, v in zip(epochs_array[val_mask], np.array(val_losses)[val_mask]) if v is not None and not np.isnan(v)]
            if valid_val_losses:
                best_epoch, best_loss = min(valid_val_losses, key=lambda x: x[1])
                ax1.scatter([best_epoch], [best_loss], s=200, c='gold', marker='*',
                          zorder=10, edgecolors='black', linewidths=2, label='Best Epoch')
        
        ax1.set_ylabel('Loss', fontsize=12, fontweight='bold')
        ax1.set_title('SP Training Timeline: Loss + LR + Metrics + Events', fontsize=16, fontweight='bold', pad=20)
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(left=-1)
        
        # ========== SUBPLOT 2: Learning Rate ==========
        lr_mask = np.array([x is not None and x > 0 for x in learning_rates])
        if lr_mask.any():
            ax2.plot(epochs_array[lr_mask], np.array(learning_rates)[lr_mask], 
                    '-', linewidth=2.5, color='#2563eb', label='SP Learning Rate', 
                    marker='o', markersize=3, alpha=0.8)
        
        # Plot ES LR if available
        es_lr_mask = np.array([x is not None and x > 0 for x in es_learning_rates])
        if es_lr_mask.any():
            ax2.plot(epochs_array[es_lr_mask], np.array(es_learning_rates)[es_lr_mask], 
                    '--', linewidth=2.5, color='#10b981', label='ES Learning Rate', 
                    marker='s', markersize=3, alpha=0.8)
        
        # Mark ES freeze/unfreeze events on LR plot
        for epoch, event_type, event_subtype, description in timeline_events:
            if event_type == 'es_frozen':
                # Mark ES frozen with vertical line
                ax2.axvline(epoch, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
                           label='ES Frozen' if epoch == min([e for e, et, _, _ in timeline_events if et == 'es_frozen'], default=epoch) else '')
            elif event_type == 'es_unfrozen':
                # Mark ES unfrozen with vertical line
                ax2.axvline(epoch, color='purple', linestyle=':', linewidth=2, alpha=0.7,
                           label='ES Unfrozen' if epoch == min([e for e, et, _, _ in timeline_events if et == 'es_unfrozen'], default=epoch) else '')
                # Also mark the ES LR start point
                if es_lr_mask.any() and epoch < len(es_learning_rates):
                    es_lr_at_unfreeze = es_learning_rates[epoch] if epoch < len(es_learning_rates) else None
                    if es_lr_at_unfreeze is not None and es_lr_at_unfreeze > 0:
                        ax2.scatter([epoch], [es_lr_at_unfreeze], s=200, c='purple', marker='D',
                                   zorder=10, edgecolors='black', linewidths=2, alpha=0.9)
            elif event_type == 'lr_adjustment':
                # Mark LR adjustments with markers
                if epoch >= 0 and epoch < len(learning_rates) and learning_rates[epoch] is not None:
                    lr_at_epoch = learning_rates[epoch]
                    adjustment_type = event_subtype if isinstance(event_subtype, str) else 'unknown'
                    # Use different markers/colors based on adjustment type
                    if 'encoder_increase' in adjustment_type or 'encoder' in adjustment_type.lower():
                        ax2.scatter([epoch], [lr_at_epoch], s=150, c='green', marker='^',
                                   zorder=10, edgecolors='black', linewidths=1.5, alpha=0.8,
                                   label='ES LR ↑' if epoch == min([e for e, et, _, _ in timeline_events if et == 'lr_adjustment'], default=epoch) else '')
                    elif 'predictor_decrease' in adjustment_type or 'predictor' in adjustment_type.lower():
                        ax2.scatter([epoch], [lr_at_epoch], s=150, c='red', marker='v',
                                   zorder=10, edgecolors='black', linewidths=1.5, alpha=0.8,
                                   label='SP LR ↓' if epoch == min([e for e, et, _, _ in timeline_events if et == 'lr_adjustment'], default=epoch) else '')
                    elif 'adaptive_initial' in adjustment_type:
                        # Initial adaptive adjustment (epoch -1, show at epoch 0)
                        if epoch == -1 and len(learning_rates) > 0 and learning_rates[0] is not None:
                            ax2.scatter([0], [learning_rates[0]], s=150, c='blue', marker='*',
                                       zorder=10, edgecolors='black', linewidths=1.5, alpha=0.8,
                                       label='Initial LR Adjust')
            elif event_type == 'training_restart':
                # Mark training restart with vertical line
                ax2.axvline(epoch, color='red', linestyle='--', linewidth=2, alpha=0.7,
                           label='Training Restart' if epoch == min([e for e, et, _, _ in timeline_events if et == 'training_restart'], default=epoch) else '')
            elif event_type == 'best_epoch':
                # Mark best epoch with star
                if epoch >= 0 and epoch < len(learning_rates) and learning_rates[epoch] is not None:
                    lr_at_epoch = learning_rates[epoch]
                    ax2.scatter([epoch], [lr_at_epoch], s=250, c='gold', marker='*',
                               zorder=11, edgecolors='black', linewidths=2, alpha=0.9,
                               label='Best Epoch' if epoch == min([e for e, et, _, _ in timeline_events if et == 'best_epoch'], default=epoch) else '')
        
        ax2.set_ylabel('Learning Rate', fontsize=12, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        ax2.set_xlim(left=-1)
        
        # ========== SUBPLOT 3: Metrics ==========
        has_metrics = False
        
        # Plot AUC (primary)
        auc_mask = np.array([x is not None and not np.isnan(x) for x in aucs])
        if auc_mask.any():
            has_metrics = True
            ax3.plot(epochs_array[auc_mask], np.array(aucs)[auc_mask], 
                    '-', linewidth=2, color='#10b981', label='AUC', 
                    marker='o', markersize=3, alpha=0.8)
            ax3.set_ylabel('AUC', fontsize=12, fontweight='bold', color='#10b981')
            ax3.tick_params(axis='y', labelcolor='#10b981')
        
        # Plot ROC-AUC and PR-AUC on secondary axis
        ax3b = None
        roc_mask = np.array([x is not None and not np.isnan(x) for x in roc_aucs])
        pr_mask = np.array([x is not None and not np.isnan(x) for x in pr_aucs])
        
        if roc_mask.any() or pr_mask.any():
            has_metrics = True
            if ax3b is None:
                ax3b = ax3.twinx()
            
            if roc_mask.any():
                ax3b.plot(epochs_array[roc_mask], np.array(roc_aucs)[roc_mask], 
                         '--', linewidth=2, color='#8b5cf6', label='ROC-AUC', 
                         marker='s', markersize=3, alpha=0.8)
                ax3.plot([], [], '--', linewidth=2, color='#8b5cf6', label='ROC-AUC', 
                        marker='s', markersize=3, alpha=0.8)
            
            if pr_mask.any():
                ax3b.plot(epochs_array[pr_mask], np.array(pr_aucs)[pr_mask], 
                         ':', linewidth=2, color='#f59e0b', label='PR-AUC', 
                         marker='^', markersize=3, alpha=0.8)
                ax3.plot([], [], ':', linewidth=2, color='#f59e0b', label='PR-AUC', 
                        marker='^', markersize=3, alpha=0.8)
            
            if roc_mask.any() or pr_mask.any():
                ax3b.set_ylabel('ROC-AUC / PR-AUC', fontsize=12, fontweight='bold', color='#6366f1')
                ax3b.tick_params(axis='y', labelcolor='#6366f1')
        
        # Plot accuracy on secondary axis
        acc_mask = np.array([x is not None and not np.isnan(x) for x in accuracies])
        if acc_mask.any():
            has_metrics = True
            if ax3b is None:
                ax3b = ax3.twinx()
            ax3b.plot(epochs_array[acc_mask], np.array(accuracies)[acc_mask], 
                     '-.', linewidth=1.5, color='#6366f1', label='Accuracy', 
                     marker='x', markersize=2, alpha=0.6)
            ax3.plot([], [], '-.', linewidth=1.5, color='#6366f1', label='Accuracy', 
                    marker='x', markersize=2, alpha=0.6)
            if not roc_mask.any() and not pr_mask.any():
                ax3b.set_ylabel('Accuracy', fontsize=12, fontweight='bold', color='#6366f1')
                ax3b.tick_params(axis='y', labelcolor='#6366f1')
        
        if has_metrics:
            ax3.set_title('Metrics', fontsize=14, fontweight='bold', pad=10)
            ax3.set_xlabel('Epoch', fontsize=12, fontweight='bold')
            ax3.legend(loc='upper left', fontsize=9)
            ax3.grid(True, alpha=0.3)
            ax3.set_xlim(left=-1)
        else:
            ax3.text(0.5, 0.5, 'No metrics available', ha='center', va='center',
                    transform=ax3.transAxes, fontsize=12, color='gray')
            ax3.set_ylabel('Metrics', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Epoch', fontsize=12, fontweight='bold')
        
        # ========== SUBPLOT 4: Events Timeline ==========
        # Use same event plotting logic as ES
        all_events = []
        
        for epoch, warning_type in warnings:
            all_events.append((epoch, 'warning', warning_type, f'Warning: {warning_type}'))
        
        for epoch, action_type, trigger in corrective_actions:
            all_events.append((epoch, 'corrective_action', action_type, f'Action: {action_type}'))
        
        for epoch, event_type, event_subtype, description in timeline_events:
            all_events.append((epoch, event_type, event_subtype, description))
        
        if all_events:
            # Group and plot events (same logic as ES plot)
            event_groups = {
                'warning': [],
                'corrective_action': [],
                'warning_start': [],
                'warning_resolved': [],
                'error': [],
                'other': []
            }
            
            for epoch, event_type, event_subtype, description in all_events:
                if event_type in event_groups:
                    event_groups[event_type].append((epoch, event_subtype, description))
                else:
                    event_groups['other'].append((epoch, event_subtype, description))
            
            y_offset = 0
            y_spacing = 0.3
            plotted_labels = set()
            
            # Plot each event group (same as ES)
            if event_groups['warning']:
                unique_warnings = list(set([subtype for _, subtype, _ in event_groups['warning']]))
                for epoch, warning_type, description in event_groups['warning']:
                    y_pos = y_offset + unique_warnings.index(warning_type) * y_spacing
                    label = f'Warning: {warning_type}' if f'Warning: {warning_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax4.scatter([epoch], [y_pos], s=120, c='yellow', marker='^', 
                               zorder=10, edgecolors='black', linewidths=1.5, label=label, alpha=0.8)
                y_offset += len(unique_warnings) * y_spacing + 0.2
            
            if event_groups['corrective_action']:
                unique_actions = list(set([subtype for _, subtype, _ in event_groups['corrective_action']]))
                pastel1_cmap = plt.get_cmap('Pastel1')
                colors_actions = pastel1_cmap(np.linspace(0, 1, len(unique_actions)))
                action_color_map = {at: colors_actions[i] for i, at in enumerate(unique_actions)}
                
                for epoch, action_type, description in event_groups['corrective_action']:
                    y_pos = y_offset + unique_actions.index(action_type) * y_spacing
                    label = f'Action: {action_type}' if f'Action: {action_type}' not in plotted_labels else ''
                    if label:
                        plotted_labels.add(label)
                    ax4.scatter([epoch], [y_pos], s=100, c=[action_color_map[action_type]],
                               marker='o', zorder=10, edgecolors='black', linewidths=1, label=label)
                y_offset += len(unique_actions) * y_spacing + 0.2
            
            # Add other event types (warning_start, warning_resolved, error, other) same as ES
            for event_type in ['warning_start', 'warning_resolved', 'error', 'other']:
                if event_groups[event_type]:
                    unique_events = list(set([subtype for _, subtype, _ in event_groups[event_type]]))
                    colors = {'warning_start': 'yellow', 'warning_resolved': 'lightgreen', 
                             'error': 'red', 'other': 'gray'}
                    markers = {'warning_start': '^', 'warning_resolved': 'v', 
                              'error': 'D', 'other': '*'}
                    
                    for epoch, event_subtype, description in event_groups[event_type]:
                        y_pos = y_offset + unique_events.index(event_subtype) * y_spacing
                        label = f'{event_type}: {event_subtype}' if f'{event_type}: {event_subtype}' not in plotted_labels else ''
                        if label:
                            plotted_labels.add(label)
                        ax4.scatter([epoch], [y_pos], s=120, c=colors[event_type], 
                                   marker=markers[event_type], zorder=10, edgecolors='black', 
                                   linewidths=1.5, label=label, alpha=0.8)
                    y_offset += len(unique_events) * y_spacing + 0.2
            
            ax4.set_ylabel('Events', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Epoch', fontsize=12, fontweight='bold')
            ax4.legend(loc='upper right', fontsize=8, ncol=2)
            ax4.grid(True, alpha=0.3, axis='x')
            ax4.set_yticks([])
        else:
            ax4.text(0.5, 0.5, 'No events recorded', ha='center', va='center',
                    transform=ax4.transAxes, fontsize=12, color='gray')
            ax4.set_ylabel('Events', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Epoch', fontsize=12, fontweight='bold')
        
        ax4.set_xlim(left=-1, right=max(epochs) + 1 if epochs else n_epochs)
        
        # Add metadata
        metadata_text = []
        if optimizer_params:
            metadata_text.append(f"Initial LR: {optimizer_params.get('lr', 'N/A')}")
        if training_info and 'best_checkpoint_epoch' in training_info:
            metadata_text.append(f"Best Epoch: {training_info.get('best_checkpoint_epoch', 'N/A')}")
        if metadata_text:
            fig.text(0.02, 0.02, ' | '.join(metadata_text), fontsize=9, 
                    verticalalignment='bottom', style='italic', color='gray')
        
        # Save plot
        plot_path = os.path.join(output_dir, "sp_training_timeline.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 SP training timeline plot saved to: {plot_path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to plot SP training timeline: {e}")
        logger.error(traceback.format_exc())

