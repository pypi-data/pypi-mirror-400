"""
Feature Effectiveness Tracker - Track which feature combinations actually improve metrics

Maintains a history of training runs with different feature combinations and their
resulting metrics, enabling data-driven decisions about which features to keep.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class FeatureEffectivenessTracker:
    """
    Track effectiveness of feature combinations across training runs.
    
    Workflow:
        1. Each training run records: features used + final metrics
        2. Compare against baseline (no features) to compute improvement
        3. On next run, filter out features that hurt performance
        4. Gradually accumulate only beneficial features
    
    Example:
        tracker = FeatureEffectivenessTracker()
        tracker.load_history("feature_effectiveness.json")
        
        # At end of training:
        tracker.record_run(
            features=["younger_borrower", "high_debt_ratio"],
            metrics={"roc_auc": 0.84, "val_loss": 0.38}
        )
        tracker.export_history("feature_effectiveness.json")
        
        # Next run - check if features are worth using:
        if tracker.should_use_features(["younger_borrower"]):
            # Use them
    """
    
    def __init__(self):
        """Initialize empty effectiveness tracker."""
        self.baseline: Optional[Dict[str, Any]] = None
        self.feature_combinations: List[Dict[str, Any]] = []
        self.best_combination: Optional[Dict[str, Any]] = None
    
    def load_history(self, filepath: str) -> bool:
        """
        Load effectiveness history from JSON file.
        
        Args:
            filepath: Path to feature_effectiveness.json
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            path = Path(filepath)
            if not path.exists():
                logger.debug(f"No effectiveness history found at {filepath} - starting fresh")
                return False
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.baseline = data.get('baseline')
            self.feature_combinations = data.get('feature_combinations', [])
            self.best_combination = data.get('best_combination')
            
            logger.info(f"📊 Loaded effectiveness history: {len(self.feature_combinations)} runs tracked")
            if self.baseline:
                logger.info(f"   Baseline: {self._format_metrics(self.baseline['metrics'])}")
            if self.best_combination:
                features_str = ', '.join(self.best_combination['features'])
                logger.info(f"   Best: [{features_str}] = {self.best_combination['value']:.3f} {self.best_combination['metric']}")
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load effectiveness history from {filepath}: {e}")
            return False
    
    def record_run(
        self,
        features: List[str],
        metrics: Dict[str, float],
        run_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record results from a training run.
        
        Args:
            features: List of feature names used (empty list = baseline)
            metrics: Dict of metric_name -> value (e.g. {"roc_auc": 0.84, "val_loss": 0.38})
            run_metadata: Optional metadata (job_id, dataset_hash, etc.)
        """
        run_data = {
            'features': sorted(features),  # Sort for consistent comparison
            'run_date': datetime.now().isoformat(),
            'metrics': metrics,
            'metadata': run_metadata or {}
        }
        
        # If no features, this is the baseline
        if not features:
            self.baseline = run_data
            logger.info("📊 Recorded baseline metrics (no features)")
        else:
            # Compute improvement vs baseline if we have one
            if self.baseline:
                improvements = {}
                for metric_name, value in metrics.items():
                    baseline_value = self.baseline['metrics'].get(metric_name)
                    if baseline_value is not None:
                        # For loss: negative improvement is good
                        # For AUC/F1: positive improvement is good
                        is_loss_metric = 'loss' in metric_name.lower()
                        pct_change = ((value - baseline_value) / abs(baseline_value)) * 100
                        if is_loss_metric:
                            pct_change = -pct_change  # Invert so negative loss = positive improvement
                        improvements[metric_name] = round(pct_change, 2)
                
                run_data['improvement_vs_baseline'] = improvements
            
            # Check if this is the best combination seen so far
            self._update_best_combination(run_data)
            
            # Add to history
            self.feature_combinations.append(run_data)
            
            features_str = ', '.join(features)
            logger.info(f"📊 Recorded run with features: [{features_str}]")
            logger.info(f"   Metrics: {self._format_metrics(metrics)}")
            if run_data.get('improvement_vs_baseline'):
                logger.info(f"   vs Baseline: {self._format_improvements(run_data['improvement_vs_baseline'])}")
    
    def _update_best_combination(self, run_data: Dict[str, Any]):
        """Update best_combination if this run is better."""
        # Primary metric for comparison (prefer ROC-AUC, then PR-AUC, then F1, then val_loss)
        metrics = run_data['metrics']
        
        for metric_name in ['roc_auc', 'pr_auc', 'f1', 'accuracy']:
            if metric_name in metrics:
                value = metrics[metric_name]
                if self.best_combination is None or value > self.best_combination['value']:
                    self.best_combination = {
                        'features': run_data['features'],
                        'metric': metric_name,
                        'value': value,
                        'run_date': run_data['run_date']
                    }
                return
        
        # Fallback: use val_loss (lower is better)
        if 'val_loss' in metrics:
            value = metrics['val_loss']
            if self.best_combination is None or value < self.best_combination['value']:
                self.best_combination = {
                    'features': run_data['features'],
                    'metric': 'val_loss',
                    'value': value,
                    'run_date': run_data['run_date']
                }
    
    def should_use_features(
        self,
        features: List[str],
        min_improvement_pct: float = 1.0,
        metric: str = 'roc_auc'
    ) -> bool:
        """
        Check if a feature combination is worth using based on historical data.
        
        Args:
            features: List of feature names to check
            min_improvement_pct: Minimum improvement % required (default: 1%)
            metric: Metric to use for comparison (default: roc_auc)
            
        Returns:
            True if features should be used, False otherwise
        """
        if not self.baseline:
            # No baseline data - allow features (optimistic)
            logger.debug(f"No baseline data - allowing features: {features}")
            return True
        
        # Find runs with exactly these features
        features_sorted = sorted(features)
        matching_runs = [
            run for run in self.feature_combinations
            if run['features'] == features_sorted
        ]
        
        if not matching_runs:
            # No data for this combination - allow it (exploratory)
            logger.debug(f"No historical data for features {features} - allowing (exploratory)")
            return True
        
        # Use most recent run
        most_recent = max(matching_runs, key=lambda r: r['run_date'])
        
        # Check improvement
        improvements = most_recent.get('improvement_vs_baseline', {})
        improvement = improvements.get(metric)
        
        if improvement is None:
            # Metric not available - allow features
            logger.debug(f"No {metric} data for features {features} - allowing")
            return True
        
        # Decision based on improvement threshold
        if improvement >= min_improvement_pct:
            logger.debug(f"Features {features} improved {metric} by {improvement:.1f}% - allowing")
            return True
        else:
            logger.info(f"⚠️  Features {features} only improved {metric} by {improvement:.1f}% (< {min_improvement_pct}%) - consider skipping")
            return False
    
    def get_recommended_features(
        self,
        metric: str = 'roc_auc',
        min_improvement_pct: float = 1.0
    ) -> List[str]:
        """
        Get list of features from the best performing combination.
        
        Args:
            metric: Metric to optimize for
            min_improvement_pct: Minimum improvement required
            
        Returns:
            List of recommended feature names
        """
        if not self.best_combination:
            return []
        
        # Check if best combination meets threshold
        if self.baseline:
            # Find the run data for best combination
            best_features = sorted(self.best_combination['features'])
            matching_run = next(
                (run for run in self.feature_combinations if run['features'] == best_features),
                None
            )
            
            if matching_run:
                improvements = matching_run.get('improvement_vs_baseline', {})
                improvement = improvements.get(metric, 0)
                
                if improvement >= min_improvement_pct:
                    return self.best_combination['features']
        
        # Default: return best combination even if below threshold
        return self.best_combination['features']
    
    def export_history(self, filepath: str):
        """
        Export effectiveness history to JSON file.
        
        Args:
            filepath: Path to save feature_effectiveness.json
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'baseline': self.baseline,
            'feature_combinations': self.feature_combinations,
            'best_combination': self.best_combination,
            'statistics': {
                'total_runs': len(self.feature_combinations) + (1 if self.baseline else 0),
                'total_feature_combinations_tested': len(set(
                    tuple(sorted(run['features'])) for run in self.feature_combinations
                )),
                'has_baseline': self.baseline is not None
            }
        }
        
        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"💾 Exported effectiveness history to: {path}")
        logger.info(f"   Total runs: {export_data['statistics']['total_runs']}")
        logger.info(f"   Combinations tested: {export_data['statistics']['total_feature_combinations_tested']}")
    
    def log_summary(self):
        """Log a summary of tracked effectiveness data."""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 FEATURE EFFECTIVENESS SUMMARY")
        logger.info("=" * 80)
        
        if self.baseline:
            logger.info(f"Baseline (no features): {self._format_metrics(self.baseline['metrics'])}")
        else:
            logger.info("Baseline: Not yet recorded")
        
        logger.info("")
        logger.info(f"Feature combinations tested: {len(self.feature_combinations)}")
        
        if self.best_combination:
            features_str = ', '.join(self.best_combination['features'])
            logger.info(f"Best combination: [{features_str}]")
            logger.info(f"  {self.best_combination['metric']} = {self.best_combination['value']:.4f}")
        
        # Show top 5 combinations
        if self.feature_combinations:
            logger.info("")
            logger.info("Top performing combinations:")
            
            # Sort by primary metric
            sorted_runs = sorted(
                self.feature_combinations,
                key=lambda r: r['metrics'].get('roc_auc', r['metrics'].get('f1', 0)),
                reverse=True
            )
            
            for i, run in enumerate(sorted_runs[:5], 1):
                features_str = ', '.join(run['features']) if run['features'] else '(none)'
                metrics_str = self._format_metrics(run['metrics'])
                improvement_str = ""
                if run.get('improvement_vs_baseline'):
                    improvement_str = f" ({self._format_improvements(run['improvement_vs_baseline'])})"
                logger.info(f"  {i}. [{features_str}]: {metrics_str}{improvement_str}")
        
        logger.info("=" * 80)
        logger.info("")
    
    @staticmethod
    def _format_metrics(metrics: Dict[str, float]) -> str:
        """Format metrics dict for logging."""
        parts = []
        for key in ['roc_auc', 'pr_auc', 'f1', 'accuracy', 'val_loss']:
            if key in metrics:
                parts.append(f"{key}={metrics[key]:.4f}")
        return ', '.join(parts)
    
    @staticmethod
    def _format_improvements(improvements: Dict[str, float]) -> str:
        """Format improvements dict for logging."""
        parts = []
        for key, value in improvements.items():
            sign = '+' if value > 0 else ''
            parts.append(f"{key} {sign}{value:.1f}%")
        return ', '.join(parts)









