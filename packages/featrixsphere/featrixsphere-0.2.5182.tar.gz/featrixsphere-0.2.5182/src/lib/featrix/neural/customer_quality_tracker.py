"""
Customer Quality Tracker - Track customer-facing quality metrics

Tracks quality checks that are shown to customers, separate from internal training metrics.
Each quality check records:
- name/enum: Quality check identifier
- graded_score: Letter grade (A, B, C, D, F) or Pass/Fail
- epoch: Training epoch when check was performed
- metadata: Additional context about the check
"""

import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class QualityCheckName(Enum):
    """Enumeration of quality check types."""
    # Embedding Space checks
    EMBEDDING_QUALITY = "embedding_quality"
    SEPARATION = "separation"
    CLUSTERING = "clustering"
    INTERPOLATION = "interpolation"
    OVERALL_QUALITY = "overall_quality"
    COLUMN_SENSITIVITY = "column_sensitivity"
    VALIDATION_IMPROVEMENT = "validation_improvement"
    TRAINING_STABILITY = "training_stability"
    
    # Single Predictor checks
    MODEL_PERFORMANCE = "model_performance"
    CALIBRATION_QUALITY = "calibration_quality"
    TRAINING_FAILURE_DETECTION = "training_failure_detection"
    ENCODER_QUALITY = "encoder_quality"
    CLASS_BALANCE = "class_balance"
    PROBABILITY_DISTRIBUTION = "probability_distribution"


class QualityGrade:
    """Quality grade constants."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
    PASS = "Pass"
    FAIL = "Fail"
    
    @staticmethod
    def is_valid(grade: str) -> bool:
        """Check if grade is valid."""
        valid_grades = {QualityGrade.A, QualityGrade.B, QualityGrade.C, 
                       QualityGrade.D, QualityGrade.F, QualityGrade.PASS, QualityGrade.FAIL}
        return grade in valid_grades
    
    @staticmethod
    def from_score(score: float, thresholds: tuple = (0.9, 0.8, 0.7, 0.6)) -> str:
        """
        Convert a score (0-1, higher is better) to a letter grade.
        
        Args:
            score: Score from 0.0 to 1.0
            thresholds: Tuple of (A, B, C, D) thresholds, default (0.9, 0.8, 0.7, 0.6)
        
        Returns:
            Letter grade (A, B, C, D, or F)
        """
        if score >= thresholds[0]:
            return QualityGrade.A
        elif score >= thresholds[1]:
            return QualityGrade.B
        elif score >= thresholds[2]:
            return QualityGrade.C
        elif score >= thresholds[3]:
            return QualityGrade.D
        else:
            return QualityGrade.F
    
    @staticmethod
    def from_improvement_pct(improvement_pct: float) -> str:
        """
        Convert validation improvement percentage to Pass/Fail.
        
        Args:
            improvement_pct: Percentage improvement (can be negative)
        
        Returns:
            "Pass" if improved >1%, "Fail" otherwise
        """
        return QualityGrade.PASS if improvement_pct > 1.0 else QualityGrade.FAIL


class CustomerQualityTracker:
    """
    Track customer-facing quality checks per epoch.
    
    Can be used in two ways:
    1. One tracker per epoch (create new instance each epoch)
    2. One tracker for all epochs (reuse same instance)
    
    Example:
        # Per-epoch usage:
        qt = CustomerQualityTracker(epoch=5)
        qt.record_check(
            name=QualityCheckName.EMBEDDING_QUALITY,
            grade=QualityGrade.A,
            metadata={"overall_score": 0.95}
        )
        
        # Multi-epoch usage:
        qt = CustomerQualityTracker()
        qt.record_check(
            name=QualityCheckName.EMBEDDING_QUALITY,
            grade=QualityGrade.B,
            epoch=10,
            metadata={"overall_score": 0.85}
        )
    """
    
    def __init__(self, epoch: Optional[int] = None):
        """
        Initialize quality tracker.
        
        Args:
            epoch: Optional epoch number. If provided, all checks recorded
                   without explicit epoch will use this epoch.
        """
        self.default_epoch = epoch
        self.checks: List[Dict[str, Any]] = []
    
    def record_check(
        self,
        name: Union[QualityCheckName, str],
        graded_score: str,
        epoch: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a quality check.
        
        Args:
            name: Quality check name (enum or string)
            graded_score: Letter grade (A, B, C, D, F) or Pass/Fail
            epoch: Epoch number (uses default_epoch if not provided)
            metadata: Optional metadata dict with additional context
        """
        # Resolve epoch
        if epoch is None:
            if self.default_epoch is None:
                raise ValueError("epoch must be provided if default_epoch not set")
            epoch = self.default_epoch
        
        # Resolve name to string
        if isinstance(name, QualityCheckName):
            name_str = name.value
        else:
            name_str = str(name)
        
        # Validate grade
        if not QualityGrade.is_valid(graded_score):
            logger.warning(f"Invalid grade '{graded_score}' - should be A, B, C, D, F, Pass, or Fail")
        
        # Create check record
        check = {
            "name": name_str,
            "graded_score": graded_score,
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.checks.append(check)
        
        logger.debug(f"📊 Quality check recorded: {name_str} = {graded_score} @ epoch {epoch}")
    
    def get_checks_by_epoch(self, epoch: int) -> List[Dict[str, Any]]:
        """Get all quality checks for a specific epoch."""
        return [check for check in self.checks if check["epoch"] == epoch]
    
    def get_checks_by_name(self, name: Union[QualityCheckName, str]) -> List[Dict[str, Any]]:
        """Get all quality checks with a specific name."""
        if isinstance(name, QualityCheckName):
            name_str = name.value
        else:
            name_str = str(name)
        return [check for check in self.checks if check["name"] == name_str]
    
    def get_latest_check(self, name: Union[QualityCheckName, str]) -> Optional[Dict[str, Any]]:
        """Get the most recent check with a specific name."""
        checks = self.get_checks_by_name(name)
        if not checks:
            return None
        # Sort by epoch (descending), then by timestamp
        checks.sort(key=lambda c: (c["epoch"], c["timestamp"]), reverse=True)
        return checks[0]
    
    def get_all_checks(self) -> List[Dict[str, Any]]:
        """Get all quality checks."""
        return self.checks.copy()
    
    def get_epochs_with_checks(self) -> List[int]:
        """Get list of epochs that have quality checks."""
        epochs = sorted(set(check["epoch"] for check in self.checks))
        return epochs
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics.
        
        Returns:
            Dict with summary info:
            - total_checks: Total number of checks
            - epochs_checked: Number of unique epochs
            - checks_by_name: Count of checks per name
            - latest_epoch: Most recent epoch with checks
        """
        checks_by_name = {}
        for check in self.checks:
            name = check["name"]
            checks_by_name[name] = checks_by_name.get(name, 0) + 1
        
        epochs = self.get_epochs_with_checks()
        
        return {
            "total_checks": len(self.checks),
            "epochs_checked": len(epochs),
            "checks_by_name": checks_by_name,
            "latest_epoch": max(epochs) if epochs else None,
            "earliest_epoch": min(epochs) if epochs else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize tracker to dict for saving."""
        return {
            "default_epoch": self.default_epoch,
            "checks": self.checks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerQualityTracker":
        """Deserialize tracker from dict."""
        tracker = cls(epoch=data.get("default_epoch"))
        tracker.checks = data.get("checks", [])
        return tracker
    
    def log_summary(self):
        """Log a summary of all quality checks."""
        if not self.checks:
            logger.info("📊 No quality checks recorded")
            return
        
        summary = self.get_summary()
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 CUSTOMER QUALITY TRACKER SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total checks: {summary['total_checks']}")
        logger.info(f"Epochs checked: {summary['epochs_checked']}")
        if summary['latest_epoch'] is not None:
            logger.info(f"Epoch range: {summary['earliest_epoch']} - {summary['latest_epoch']}")
        
        logger.info("")
        logger.info("Checks by name:")
        for name, count in sorted(summary['checks_by_name'].items()):
            logger.info(f"  {name}: {count}")
        
        logger.info("")
        logger.info("Recent checks (latest 10):")
        recent_checks = sorted(self.checks, key=lambda c: (c["epoch"], c["timestamp"]), reverse=True)[:10]
        for check in recent_checks:
            logger.info(f"  Epoch {check['epoch']}: {check['name']} = {check['graded_score']}")
        
        logger.info("=" * 80)
        logger.info("")

