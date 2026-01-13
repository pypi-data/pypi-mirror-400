#!/usr/bin/env python3
"""
Schema history tracking - records when columns were added and from what source.

Tracks:
- Original upload columns (date of upload)
- Pre-loaded engineered features (date loaded + date discovered)
- Dynamically added features during training (epoch + timestamp)
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SchemaHistory:
    """
    Tracks the evolution of a dataset schema over time.
    
    Each column has:
    - added_epoch: Epoch when added to current training (0 for pre-training)
    - added_date: ISO timestamp when added
    - source: Where it came from (original_upload, feature_engineering_preload, feature_engineering_dynamic)
    - Additional metadata depending on source
    """
    
    def __init__(self):
        self.columns = {}  # {column_name: metadata_dict}
        self.creation_date = datetime.now().isoformat()
    
    def add_original_columns(self, column_names: List[str], upload_date: Optional[str] = None):
        """
        Record original columns from data upload.
        
        Args:
            column_names: List of column names
            upload_date: ISO timestamp of upload (defaults to now)
        """
        if upload_date is None:
            upload_date = datetime.now().isoformat()
        
        for col_name in column_names:
            self.columns[col_name] = {
                'added_epoch': 0,
                'added_date': upload_date,
                'source': 'original_upload',
                'column_type': 'data'
            }
        
        logger.info(f"📋 Registered {len(column_names)} original columns (upload: {upload_date})")
    
    def add_preloaded_features(self, feature_suggestions: List[Dict[str, Any]], load_date: Optional[str] = None):
        """
        Record engineered features loaded from JSON before training starts.
        
        Args:
            feature_suggestions: List of feature suggestion dicts
            load_date: ISO timestamp when loaded (defaults to now)
        """
        if load_date is None:
            load_date = datetime.now().isoformat()
        
        for suggestion in feature_suggestions:
            feature_name = suggestion.get('feature_name')
            if not feature_name:
                continue
            
            self.columns[feature_name] = {
                'added_epoch': 0,  # Added before training starts
                'added_date': load_date,
                'source': 'feature_engineering_preload',
                'column_type': 'engineered',
                'feature_type': suggestion.get('type'),
                'formula': suggestion.get('formula'),
                'base_columns': suggestion.get('base_columns', []),
                # Metadata from previous discovery run
                'discovered_date': suggestion.get('discovered_date'),
                'discovered_epoch': suggestion.get('discovered_epoch'),
                'discovery_votes': suggestion.get('votes', 1)
            }
        
        logger.info(f"📋 Registered {len(feature_suggestions)} pre-loaded engineered features (loaded: {load_date})")
    
    def add_dynamic_feature(self, feature_name: str, epoch: int, suggestion: Dict[str, Any]):
        """
        Record a feature added during training.
        
        Args:
            feature_name: Name of the feature
            epoch: Training epoch when added
            suggestion: Feature suggestion dict with metadata
        """
        add_date = datetime.now().isoformat()
        
        self.columns[feature_name] = {
            'added_epoch': epoch,
            'added_date': add_date,
            'source': 'feature_engineering_dynamic',
            'column_type': 'engineered',
            'feature_type': suggestion.get('type'),
            'formula': suggestion.get('formula'),
            'base_columns': suggestion.get('base_columns', []),
            'discovery_votes': suggestion.get('votes', 1)
        }
        
        logger.info(f"📋 Registered dynamic feature '{feature_name}' at epoch {epoch} ({add_date})")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of schema evolution."""
        # Group by source
        original = {k: v for k, v in self.columns.items() if v['source'] == 'original_upload'}
        preloaded = {k: v for k, v in self.columns.items() if v['source'] == 'feature_engineering_preload'}
        dynamic = {k: v for k, v in self.columns.items() if v['source'] == 'feature_engineering_dynamic'}
        
        # Get date ranges
        all_dates = [v['added_date'] for v in self.columns.values()]
        earliest_date = min(all_dates) if all_dates else None
        latest_date = max(all_dates) if all_dates else None
        
        return {
            'total_columns': len(self.columns),
            'original_columns': len(original),
            'preloaded_features': len(preloaded),
            'dynamic_features': len(dynamic),
            'earliest_date': earliest_date,
            'latest_date': latest_date,
            'creation_date': self.creation_date
        }
    
    def log_summary(self):
        """Log a human-readable summary of schema evolution."""
        summary = self.get_summary()
        
        logger.info("=" * 80)
        logger.info("📋 SCHEMA EVOLUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total columns: {summary['total_columns']}")
        logger.info(f"   Original (from upload): {summary['original_columns']}")
        logger.info(f"   Pre-loaded (from JSON): {summary['preloaded_features']}")
        logger.info(f"   Dynamic (during training): {summary['dynamic_features']}")
        logger.info(f"   Date range: {summary['earliest_date']} → {summary['latest_date']}")
        logger.info("=" * 80)
        
        # Show details by source
        original = {k: v for k, v in self.columns.items() if v['source'] == 'original_upload'}
        if original:
            logger.info(f"\n📊 Original Columns ({len(original)}):")
            upload_date = list(original.values())[0]['added_date'] if original else None
            logger.info(f"   Uploaded: {upload_date}")
            for col_name in sorted(original.keys())[:10]:  # Show first 10
                logger.info(f"      - {col_name}")
            if len(original) > 10:
                logger.info(f"      ... and {len(original) - 10} more")
        
        preloaded = {k: v for k, v in self.columns.items() if v['source'] == 'feature_engineering_preload'}
        if preloaded:
            logger.info(f"\n🔧 Pre-loaded Features ({len(preloaded)}):")
            load_date = list(preloaded.values())[0]['added_date'] if preloaded else None
            logger.info(f"   Loaded: {load_date}")
            for col_name, meta in sorted(preloaded.items()):
                discovered = meta.get('discovered_date', 'unknown')
                disc_epoch = meta.get('discovered_epoch', '?')
                logger.info(f"      - {col_name} (discovered: {discovered} at epoch {disc_epoch})")
        
        dynamic = {k: v for k, v in self.columns.items() if v['source'] == 'feature_engineering_dynamic'}
        if dynamic:
            logger.info(f"\n⚡ Dynamic Features ({len(dynamic)}):")
            for col_name, meta in sorted(dynamic.items()):
                epoch = meta.get('added_epoch', '?')
                date = meta.get('added_date', 'unknown')
                logger.info(f"      - {col_name} (added: epoch {epoch}, {date})")
        
        logger.info("")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for serialization."""
        return {
            'creation_date': self.creation_date,
            'columns': self.columns
        }
    
    def to_json(self, path: str):
        """Save to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"💾 Schema history saved to: {path}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SchemaHistory':
        """Load from dictionary."""
        history = cls()
        history.creation_date = data.get('creation_date', datetime.now().isoformat())
        history.columns = data.get('columns', {})
        return history
    
    @classmethod
    def from_json(cls, path: str) -> 'SchemaHistory':
        """Load from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

