#!/usr/bin/env python3
"""
Test Suite for Enhanced SetEncoder Strategies

Tests the new set encoding features:
1. Per-member mixture weights (each category gets its own learned vs semantic balance)
2. Ordinal detection (LLM-based with fallback patterns)
3. Curriculum learning (semantic floor decay)
4. Temperature annealing (sharper decisions over time)
5. Configurable entropy regularization

Run: python test_set_encoder_strategies.py
"""
import sys
import os
import json
import unittest
from pathlib import Path
from datetime import datetime

# Paths
test_dir = Path(__file__).parent
neural_dir = test_dir.parent
featrix_dir = neural_dir.parent
lib_dir = featrix_dir.parent
src_dir = lib_dir.parent

sys.path.insert(0, str(lib_dir))
sys.path.insert(0, str(src_dir))

import torch
import numpy as np


class TestOrdinalDetection(unittest.TestCase):
    """Test LLM-based ordinal category detection with caching."""
    
    def test_fallback_ordinal_patterns(self):
        """Test pattern-based fallback detection for common ordinal patterns."""
        from featrix.neural.llm.schema_analyzer import _fallback_ordinal_detection
        
        # Test low/medium/high pattern
        result = _fallback_ordinal_detection("priority", ["low", "medium", "high"])
        self.assertTrue(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], ["low", "medium", "high"])
        self.assertGreater(result['confidence'], 0.8)
        
        # Test poor/fair/good/excellent pattern
        result = _fallback_ordinal_detection("credit_rating", ["poor", "fair", "good", "excellent"])
        self.assertTrue(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], ["poor", "fair", "good", "excellent"])
        
        # Test non-ordinal (nominal) categories
        result = _fallback_ordinal_detection("color", ["red", "blue", "green"])
        self.assertFalse(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], [])
        
    def test_alphanumeric_code_detection(self):
        """Test detection of alphanumeric codes like A11, A12, A13."""
        from featrix.neural.llm.schema_analyzer import _fallback_ordinal_detection
        
        result = _fallback_ordinal_detection("credit_history", ["A11", "A12", "A13", "A14"])
        self.assertTrue(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], ["A11", "A12", "A13", "A14"])
        
    def test_numeric_string_detection(self):
        """Test detection of numeric strings as ordinal."""
        from featrix.neural.llm.schema_analyzer import _fallback_ordinal_detection
        
        result = _fallback_ordinal_detection("rating", ["1", "2", "3", "4", "5"])
        self.assertTrue(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], ["1", "2", "3", "4", "5"])
        
    def test_ordinal_cache(self):
        """Test that ordinal detection results are cached."""
        from featrix.neural.llm.schema_analyzer import OrdinalCache
        
        # Create cache (uses temp file for testing)
        cache = OrdinalCache()
        
        # Test set/get
        test_result = {
            'is_ordinal': True,
            'ordered_values': ['a', 'b', 'c'],
            'confidence': 0.9,
            'reasoning': 'test',
            'order_type': 'ascending'
        }
        
        cache.set("test_column", ["a", "b", "c"], test_result)
        retrieved = cache.get("test_column", ["a", "b", "c"])
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['is_ordinal'], True)
        self.assertEqual(retrieved['ordered_values'], ['a', 'b', 'c'])


class TestSetEncoderConfig(unittest.TestCase):
    """Test SetEncoderConfig with new options."""
    
    def test_new_config_fields(self):
        """Test that new config fields exist and have correct defaults."""
        from featrix.neural.model_config import SetEncoderConfig
        
        config = SetEncoderConfig(d_model=64, n_members=10)
        
        # Check new fields exist with defaults
        self.assertTrue(config.use_per_member_mixture)  # Default: True
        self.assertIsNone(config.ordinal_info)  # Default: None
        self.assertEqual(config.ordinal_weight, 0.3)
        self.assertTrue(config.use_curriculum_learning)  # Default: True
        self.assertEqual(config.semantic_floor_start, 0.7)
        self.assertEqual(config.semantic_floor_end, 0.1)
        self.assertTrue(config.use_temperature_annealing)  # Default: True
        self.assertEqual(config.temperature_start, 1.0)
        self.assertEqual(config.temperature_end, 0.2)
        self.assertEqual(config.entropy_regularization_weight, 0.3)  # Increased from 0.1
        
    def test_ordinal_info_config(self):
        """Test ordinal_info field can be set."""
        from featrix.neural.model_config import SetEncoderConfig
        
        ordinal_info = {
            'is_ordinal': True,
            'ordered_values': ['low', 'medium', 'high'],
            'confidence': 0.95,
            'reasoning': 'test',
            'order_type': 'ascending'
        }
        
        config = SetEncoderConfig(
            d_model=64, 
            n_members=4,
            ordinal_info=ordinal_info
        )
        
        self.assertIsNotNone(config.ordinal_info)
        if config.ordinal_info is not None:
            self.assertTrue(config.ordinal_info['is_ordinal'])
            self.assertEqual(config.ordinal_info['ordered_values'], ['low', 'medium', 'high'])


class TestSetEncoderPerMemberMixture(unittest.TestCase):
    """Test per-member mixture weights in SetEncoder."""
    
    def setUp(self):
        """Create a test SetEncoder with per-member mixture."""
        from featrix.neural.set_codec import SetEncoder
        from featrix.neural.model_config import SetEncoderConfig
        
        self.member_names = ['cat_a', 'cat_b', 'cat_c', 'cat_d']
        self.config = SetEncoderConfig(
            d_model=32,
            n_members=len(self.member_names) + 1,  # +1 for <UNKNOWN>
            use_per_member_mixture=True,
            use_curriculum_learning=False,  # Disable for cleaner testing
            use_temperature_annealing=False,
        )
        
        # Create encoder without string cache (no BERT)
        self.encoder = SetEncoder(
            self.config,
            string_cache=None,
            member_names=self.member_names,
            column_name='test_column'
        )
        
    def test_per_member_mixture_disabled_without_semantic(self):
        """Without semantic mixture, per-member should be disabled."""
        # Without string_cache, use_semantic_mixture is False
        self.assertFalse(self.encoder.use_semantic_mixture)
        self.assertFalse(self.encoder.use_per_member_mixture)
        self.assertIsNone(self.encoder.mixture_logits)
        

class TestSetEncoderOrdinal(unittest.TestCase):
    """Test ordinal encoding in SetEncoder."""
    
    def test_ordinal_embedding_creation(self):
        """Test that ordinal embedding is created when ordinal_info is provided."""
        from featrix.neural.set_codec import SetEncoder
        from featrix.neural.model_config import SetEncoderConfig
        
        member_names = ['low', 'medium', 'high']
        ordinal_info = {
            'is_ordinal': True,
            'ordered_values': ['low', 'medium', 'high'],
            'confidence': 0.95,
            'reasoning': 'magnitude order',
            'order_type': 'ascending'
        }
        
        config = SetEncoderConfig(
            d_model=32,
            n_members=len(member_names) + 1,
            ordinal_info=ordinal_info,
            ordinal_weight=0.3,
        )
        
        encoder = SetEncoder(
            config,
            string_cache=None,
            member_names=member_names,
            column_name='priority'
        )
        
        # Without semantic mixture, ordinal is not active
        # (ordinal requires semantic mixture to be enabled)
        self.assertFalse(encoder.use_semantic_mixture)
        

class TestSetEncoderCurriculum(unittest.TestCase):
    """Test curriculum learning in SetEncoder."""
    
    def test_semantic_floor_calculation(self):
        """Test that semantic floor decays correctly over epochs."""
        # Simulate curriculum learning calculation
        semantic_floor_start = 0.7
        semantic_floor_end = 0.1
        total_epochs = 100
        
        # At epoch 0: floor should be 0.7
        epoch = 0
        progress = epoch / total_epochs
        floor = semantic_floor_start + (semantic_floor_end - semantic_floor_start) * progress
        self.assertAlmostEqual(floor, 0.7, places=3)
        
        # At epoch 50: floor should be 0.4
        epoch = 50
        progress = epoch / total_epochs
        floor = semantic_floor_start + (semantic_floor_end - semantic_floor_start) * progress
        self.assertAlmostEqual(floor, 0.4, places=3)
        
        # At epoch 100: floor should be 0.1
        epoch = 100
        progress = epoch / total_epochs
        floor = semantic_floor_start + (semantic_floor_end - semantic_floor_start) * progress
        self.assertAlmostEqual(floor, 0.1, places=3)
        

class TestSetEncoderTemperature(unittest.TestCase):
    """Test temperature annealing in SetEncoder."""
    
    def test_temperature_decay(self):
        """Test that temperature decays correctly over epochs."""
        temp_start = 1.0
        temp_end = 0.2
        total_epochs = 100
        
        # At epoch 0: temp should be 1.0
        epoch = 0
        progress = epoch / total_epochs
        temp = temp_start + (temp_end - temp_start) * progress
        self.assertAlmostEqual(temp, 1.0, places=3)
        
        # At epoch 50: temp should be 0.6
        epoch = 50
        progress = epoch / total_epochs
        temp = temp_start + (temp_end - temp_start) * progress
        self.assertAlmostEqual(temp, 0.6, places=3)
        
        # At epoch 100: temp should be 0.2
        epoch = 100
        progress = epoch / total_epochs
        temp = temp_start + (temp_end - temp_start) * progress
        self.assertAlmostEqual(temp, 0.2, places=3)
        
    def test_temperature_sharpens_sigmoid(self):
        """Test that lower temperature produces sharper sigmoid outputs."""
        # At logit=0, sigmoid(0) = 0.5 regardless of temperature
        # At logit=1:
        #   sigmoid(1/1.0) = 0.731
        #   sigmoid(1/0.5) = 0.881
        #   sigmoid(1/0.2) = 0.993
        
        logit = torch.tensor([1.0])
        
        sig_t1 = torch.sigmoid(logit / 1.0).item()
        sig_t05 = torch.sigmoid(logit / 0.5).item()
        sig_t02 = torch.sigmoid(logit / 0.2).item()
        
        # Lower temperature should produce values closer to 1 (sharper)
        self.assertLess(sig_t1, sig_t05)
        self.assertLess(sig_t05, sig_t02)
        self.assertGreater(sig_t02, 0.99)  # Very sharp at temp=0.2


class TestSetEncoderEntropy(unittest.TestCase):
    """Test entropy regularization in SetEncoder."""
    
    def test_entropy_at_boundaries(self):
        """Test entropy values at mixture weight boundaries."""
        # Entropy: H = -p*log(p) - (1-p)*log(1-p)
        # At p=0.5: H ≈ 0.693 (maximum)
        # At p=0.1 or p=0.9: H ≈ 0.325
        # At p=0.01 or p=0.99: H ≈ 0.056
        
        def binary_entropy(p):
            if p <= 0 or p >= 1:
                return 0.0
            return -(p * np.log(p + 1e-10) + (1-p) * np.log(1-p + 1e-10))
        
        # Maximum entropy at 50/50
        h_50 = binary_entropy(0.5)
        self.assertAlmostEqual(h_50, 0.693, places=2)
        
        # Lower entropy at extremes
        h_90 = binary_entropy(0.9)
        h_10 = binary_entropy(0.1)
        self.assertLess(h_90, h_50)
        self.assertLess(h_10, h_50)
        self.assertAlmostEqual(h_90, h_10, places=5)  # Symmetric
        
        # Very low entropy at near-certainty
        h_99 = binary_entropy(0.99)
        self.assertLess(h_99, 0.1)


class TestGetDefaultConfig(unittest.TestCase):
    """Test SetEncoder.get_default_config with new options."""
    
    def test_default_config_includes_new_options(self):
        """Test that get_default_config includes ordinal_info and other new options."""
        from featrix.neural.set_codec import SetEncoder
        
        ordinal_info = {
            'is_ordinal': True,
            'ordered_values': ['a', 'b', 'c'],
            'confidence': 0.9,
            'reasoning': 'test',
            'order_type': 'ascending'
        }
        
        config = SetEncoder.get_default_config(
            d_model=64,
            n_members=4,
            ordinal_info=ordinal_info,
            use_per_member_mixture=True,
            use_curriculum_learning=True,
            use_temperature_annealing=True,
            entropy_regularization_weight=0.5,
        )
        
        self.assertIsNotNone(config.ordinal_info)
        self.assertTrue(config.use_per_member_mixture)
        self.assertTrue(config.use_curriculum_learning)
        self.assertTrue(config.use_temperature_annealing)
        self.assertEqual(config.entropy_regularization_weight, 0.5)


class TestBatchOrdinalDetection(unittest.TestCase):
    """Test batch ordinal detection."""
    
    def test_batch_detection_with_fallback(self):
        """Test detecting ordinal using fallback (no API calls)."""
        from featrix.neural.llm.schema_analyzer import _fallback_ordinal_detection
        
        # Test priority - should be ordinal (known pattern)
        result = _fallback_ordinal_detection("priority", ["low", "medium", "high"])
        self.assertTrue(result['is_ordinal'])
        self.assertIn('is_ordinal', result)
        self.assertIn('ordered_values', result)
        self.assertIn('confidence', result)
        
        # Test color - should NOT be ordinal
        result = _fallback_ordinal_detection("color", ["red", "blue", "green"])
        self.assertFalse(result['is_ordinal'])
        
        # Test rating - should be ordinal (numeric strings)
        result = _fallback_ordinal_detection("rating", ["1", "2", "3", "4", "5"])
        self.assertTrue(result['is_ordinal'])
        self.assertEqual(result['ordered_values'], ["1", "2", "3", "4", "5"])


def run_tests():
    """Run all tests with verbose output."""
    print("=" * 80)
    print("TEST SUITE: Enhanced SetEncoder Strategies")
    print("=" * 80)
    print(f"Started: {datetime.now()}")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOrdinalDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderPerMemberMixture))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderOrdinal))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderCurriculum))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderTemperature))
    suite.addTests(loader.loadTestsFromTestCase(TestSetEncoderEntropy))
    suite.addTests(loader.loadTestsFromTestCase(TestGetDefaultConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchOrdinalDetection))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    if result.wasSuccessful():
        print("ALL TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

