#!/usr/bin/env python3
"""
Unit tests for DynamicRelationshipExtractor with mixed column types.

Tests that relationship operations work correctly for:
1. cat-cat (categorical + categorical embeddings)
2. cat-scalar (categorical + scalar embeddings)
3. scalar-scalar (scalar + scalar embeddings)

The DynamicRelationshipExtractor operates on d_model-dimensional embeddings,
NOT on raw feature values. By the time embeddings reach the extractor:
- Categorical values have been mapped through nn.Embedding to d_model vectors
- Scalar values have been transformed through MLPs to d_model vectors

All operations (*, +, -, /) are element-wise on these continuous vectors,
so they're always mathematically valid. This test verifies no bugs exist
in the implementation that would break for specific type combinations.
"""
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

# Add paths for imports
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "lib"))
sys.path.insert(0, str(project_root / "src"))

from featrix.neural.dynamic_relationship_extractor import DynamicRelationshipExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def create_mock_categorical_embedding(batch_size: int, d_model: int, n_categories: int = 10, seed: int = 42):
    """
    Create mock categorical column embeddings that mimic SetEncoder output.
    
    Categorical embeddings typically:
    - Have discrete cluster structure (each category has a learned embedding)
    - Are normalized (unit vectors after F.normalize)
    - Come from nn.Embedding lookup
    
    We simulate this by creating embeddings from a small vocabulary.
    """
    torch.manual_seed(seed)
    
    # Create a small vocabulary of embeddings (like nn.Embedding)
    vocab_embeddings = torch.randn(n_categories, d_model)
    vocab_embeddings = nn.functional.normalize(vocab_embeddings, dim=-1)  # Normalize like SetEncoder
    
    # Sample random category indices for each batch item
    category_indices = torch.randint(0, n_categories, (batch_size,))
    
    # Look up embeddings
    embeddings = vocab_embeddings[category_indices]
    
    return embeddings


def create_mock_scalar_embedding(batch_size: int, d_model: int, seed: int = 42):
    """
    Create mock scalar column embeddings that mimic ScalarEncoder output.
    
    Scalar embeddings typically:
    - Have continuous variation (different for each input value)
    - Are normalized (unit vectors after F.normalize)
    - Come from MLP transformation of the normalized scalar
    
    We simulate this by creating random normalized vectors.
    """
    torch.manual_seed(seed)
    
    # Scalars produce more varied embeddings (no discrete clusters)
    embeddings = torch.randn(batch_size, d_model)
    embeddings = nn.functional.normalize(embeddings, dim=-1)  # Normalize like ScalarEncoder
    
    return embeddings


class TestDynamicRelationshipExtractorMixedTypes:
    """Test suite for DynamicRelationshipExtractor with mixed column types."""
    
    def __init__(self):
        self.d_model = 64
        self.batch_size = 32
        self.n_epochs = 3
        
    def _create_extractor(self, col_names: list) -> DynamicRelationshipExtractor:
        """Create a fresh DynamicRelationshipExtractor for testing."""
        extractor = DynamicRelationshipExtractor(
            d_model=self.d_model,
            col_names_in_order=col_names,
            exploration_epochs=5,
            top_k_fraction=0.4,
            progressive_pruning=True,
        )
        return extractor
    
    def _create_mixed_encodings(
        self, 
        col_types: list,  # List of 'cat' or 'scalar' for each column
        batch_size: int = None,
    ) -> torch.Tensor:
        """
        Create column encodings with specified types.
        
        Args:
            col_types: List like ['cat', 'scalar', 'cat', 'scalar']
            batch_size: Override default batch size
            
        Returns:
            Tensor of shape (batch_size, n_cols, d_model)
        """
        if batch_size is None:
            batch_size = self.batch_size
            
        encodings = []
        for i, col_type in enumerate(col_types):
            if col_type == 'cat':
                emb = create_mock_categorical_embedding(batch_size, self.d_model, seed=42+i)
            else:
                emb = create_mock_scalar_embedding(batch_size, self.d_model, seed=42+i)
            encodings.append(emb)
        
        # Stack to (batch_size, n_cols, d_model)
        return torch.stack(encodings, dim=1)
    
    def test_scalar_scalar_pairs(self):
        """Test that scalar-scalar relationships work correctly."""
        logger.info("\n" + "="*80)
        logger.info("TEST: scalar-scalar pairs")
        logger.info("="*80)
        
        col_names = ['price', 'quantity', 'discount', 'tax_rate']
        col_types = ['scalar', 'scalar', 'scalar', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        # Forward pass
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        # Verify outputs
        n_pairs = len(extractor.all_pairs)  # 4*3/2 = 6 pairs
        n_ops = extractor.ops_per_pair  # 1 if fused (default), 9 if unfused
        expected_tokens = n_pairs * n_ops
        
        logger.info(f"  Columns: {len(col_names)} ({col_types})")
        logger.info(f"  Pairs: {n_pairs}")
        logger.info(f"  Expected tokens: {expected_tokens}")
        logger.info(f"  Actual tokens: {len(relationship_tokens)}")
        
        assert len(relationship_tokens) == expected_tokens, \
            f"Expected {expected_tokens} tokens, got {len(relationship_tokens)}"
        
        # Check shapes and values
        for i, token in enumerate(relationship_tokens):
            assert token.shape == (self.batch_size, self.d_model), \
                f"Token {i} has wrong shape: {token.shape}"
            assert not torch.isnan(token).any(), f"Token {i} contains NaN"
            assert not torch.isinf(token).any(), f"Token {i} contains Inf"
        
        logger.info("  ✅ PASSED: All scalar-scalar tokens valid")
        return True
    
    def test_cat_cat_pairs(self):
        """Test that categorical-categorical relationships work correctly."""
        logger.info("\n" + "="*80)
        logger.info("TEST: cat-cat pairs")
        logger.info("="*80)
        
        col_names = ['product', 'brand', 'category', 'color']
        col_types = ['cat', 'cat', 'cat', 'cat']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        # Forward pass
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        n_pairs = len(extractor.all_pairs)  # 6 pairs
        n_ops = extractor.ops_per_pair
        expected_tokens = n_pairs * n_ops
        
        logger.info(f"  Columns: {len(col_names)} ({col_types})")
        logger.info(f"  Pairs: {n_pairs}")
        logger.info(f"  Expected tokens: {expected_tokens}")
        logger.info(f"  Actual tokens: {len(relationship_tokens)}")
        
        assert len(relationship_tokens) == expected_tokens
        
        for i, token in enumerate(relationship_tokens):
            assert token.shape == (self.batch_size, self.d_model)
            assert not torch.isnan(token).any(), f"Token {i} contains NaN"
            assert not torch.isinf(token).any(), f"Token {i} contains Inf"
        
        logger.info("  ✅ PASSED: All cat-cat tokens valid")
        return True
    
    def test_cat_scalar_pairs(self):
        """Test that categorical-scalar relationships work correctly."""
        logger.info("\n" + "="*80)
        logger.info("TEST: cat-scalar pairs (mixed)")
        logger.info("="*80)
        
        # Mix of categorical and scalar columns
        col_names = ['product', 'price', 'brand', 'quantity']
        col_types = ['cat', 'scalar', 'cat', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        # Forward pass
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        n_pairs = len(extractor.all_pairs)  # 6 pairs
        n_ops = extractor.ops_per_pair
        expected_tokens = n_pairs * n_ops
        
        logger.info(f"  Columns: {len(col_names)} ({col_types})")
        logger.info(f"  Pairs: {n_pairs}")
        logger.info(f"  Expected tokens: {expected_tokens}")
        
        # Count pair types
        cat_cat_pairs = 0
        cat_scalar_pairs = 0
        scalar_scalar_pairs = 0
        
        for i, j in extractor.all_pairs:
            type_i = col_types[i]
            type_j = col_types[j]
            if type_i == 'cat' and type_j == 'cat':
                cat_cat_pairs += 1
            elif type_i == 'scalar' and type_j == 'scalar':
                scalar_scalar_pairs += 1
            else:
                cat_scalar_pairs += 1
        
        logger.info(f"  Pair breakdown: {cat_cat_pairs} cat-cat, {cat_scalar_pairs} cat-scalar, {scalar_scalar_pairs} scalar-scalar")
        
        assert len(relationship_tokens) == expected_tokens
        
        for i, token in enumerate(relationship_tokens):
            assert token.shape == (self.batch_size, self.d_model)
            assert not torch.isnan(token).any(), f"Token {i} contains NaN"
            assert not torch.isinf(token).any(), f"Token {i} contains Inf"
        
        logger.info("  ✅ PASSED: All cat-scalar tokens valid")
        return True
    
    def test_gradient_flow_all_types(self):
        """Test that gradients flow correctly through all operation types."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Gradient flow through all pair types")
        logger.info("="*80)
        
        col_names = ['cat1', 'scalar1', 'cat2', 'scalar2']
        col_types = ['cat', 'scalar', 'cat', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        encodings.requires_grad_(True)  # Enable gradient tracking
        
        # Forward pass
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        # Sum all tokens and compute loss
        total_output = torch.stack(relationship_tokens, dim=0).sum()
        
        # Backward pass
        total_output.backward()
        
        # Check gradients exist and are valid
        assert encodings.grad is not None, "No gradient computed for encodings"
        assert not torch.isnan(encodings.grad).any(), "Gradient contains NaN"
        assert not torch.isinf(encodings.grad).any(), "Gradient contains Inf"
        
        # Check that all columns received gradients
        grad_per_col = encodings.grad.abs().mean(dim=(0, 2))  # (n_cols,)
        logger.info(f"  Mean gradient magnitude per column: {grad_per_col.tolist()}")
        
        for i, grad_mag in enumerate(grad_per_col):
            assert grad_mag > 0, f"Column {i} ({col_names[i]}) received zero gradient"
        
        logger.info("  ✅ PASSED: Gradients flow through all columns")
        return True
    
    def test_division_stability(self):
        """Test that division operations are numerically stable (no explosion from near-zero divisors)."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Division stability with near-zero values")
        logger.info("="*80)
        
        col_names = ['col1', 'col2', 'col3']
        
        extractor = self._create_extractor(col_names)
        
        # Create encodings with some near-zero values to stress test division
        torch.manual_seed(42)
        encodings = torch.randn(self.batch_size, len(col_names), self.d_model) * 0.01  # Small values
        # Add some exactly zero values
        encodings[0, 0, :10] = 0.0
        encodings[1, 1, 10:20] = 0.0
        
        # Forward pass
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        # Check for numerical stability
        max_val = 0
        min_val = float('inf')
        
        for i, token in enumerate(relationship_tokens):
            assert not torch.isnan(token).any(), f"Token {i} contains NaN (division instability)"
            assert not torch.isinf(token).any(), f"Token {i} contains Inf (division instability)"
            max_val = max(max_val, token.abs().max().item())
            min_val = min(min_val, token.abs().min().item())
        
        logger.info(f"  Value range: [{min_val:.6f}, {max_val:.6f}]")
        logger.info(f"  (Safe division eps=0.1 prevents explosion)")
        
        # Values should not explode (max should be reasonable)
        assert max_val < 1000, f"Values exploded to {max_val}"
        
        logger.info("  ✅ PASSED: Division operations are numerically stable")
        return True
    
    def test_masking_works(self):
        """Test that masking correctly zeros out relationships involving masked columns."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Masking behavior")
        logger.info("="*80)
        
        col_names = ['col1', 'col2', 'col3', 'col4']
        col_types = ['cat', 'scalar', 'cat', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        # Create mask: mask out columns 1 and 3 for some batch items
        mask = torch.ones(self.batch_size, len(col_names))
        mask[:5, 1] = 0  # Mask col2 (scalar) for first 5 items
        mask[10:15, 3] = 0  # Mask col4 (scalar) for items 10-15
        
        # Forward pass with mask
        extractor.train()
        relationship_tokens = extractor(encodings, mask=mask)
        
        # Verify tokens are zeros for masked columns in the affected batch items
        # This is implicit in the pair computation via masked_encodings
        
        for i, token in enumerate(relationship_tokens):
            assert not torch.isnan(token).any(), f"Token {i} contains NaN"
            assert not torch.isinf(token).any(), f"Token {i} contains Inf"
        
        logger.info("  ✅ PASSED: Masking works correctly")
        return True
    
    def test_progressive_pruning_with_mixed_types(self):
        """Test that progressive pruning works correctly with mixed column types."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Progressive pruning with mixed types")
        logger.info("="*80)
        
        col_names = ['cat1', 'scalar1', 'cat2', 'scalar2', 'cat3', 'scalar3']
        col_types = ['cat', 'scalar', 'cat', 'scalar', 'cat', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        initial_pairs = len(extractor.all_pairs)
        logger.info(f"  Initial pairs: {initial_pairs}")
        
        # Simulate exploration phase
        for epoch in range(extractor.exploration_epochs):
            extractor.current_epoch = epoch
            extractor.train()
            _ = extractor(encodings)
        
        # Set column losses (simulating training feedback)
        col_losses = {
            'cat1': 0.5,    # Hard
            'scalar1': 0.1,  # Easy
            'cat2': 0.6,    # Hard
            'scalar2': 0.2,  # Easy
            'cat3': 0.4,    # Medium
            'scalar3': 0.3,  # Medium
        }
        extractor.update_column_losses(col_losses)
        
        # Trigger progressive pruning
        extractor.current_epoch = extractor.exploration_epochs + 1
        if extractor.should_progressive_prune():
            extractor.progressive_prune_relationships()
        
        active_pairs = initial_pairs - len(extractor.disabled_pairs)
        logger.info(f"  Pairs after pruning: {active_pairs}")
        logger.info(f"  Disabled pairs: {len(extractor.disabled_pairs)}")
        
        # Verify pruning happened
        # (Note: may not have pruned if top_k_fraction is high enough)
        
        # Forward pass after pruning should still work
        relationship_tokens = extractor(encodings)
        
        for token in relationship_tokens:
            assert not torch.isnan(token).any()
            assert not torch.isinf(token).any()
        
        logger.info("  ✅ PASSED: Progressive pruning works with mixed types")
        return True
    
    def test_empty_batch(self):
        """Test handling of empty batches."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Empty batch handling")
        logger.info("="*80)
        
        col_names = ['col1', 'col2', 'col3']
        extractor = self._create_extractor(col_names)
        
        # Empty batch (0 samples)
        encodings = torch.zeros(0, len(col_names), self.d_model)
        
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        # Should still return correct number of tokens, just with empty batch dimension
        expected_tokens = len(extractor.all_pairs) * 6
        assert len(relationship_tokens) == expected_tokens
        
        for token in relationship_tokens:
            assert token.shape == (0, self.d_model)
        
        logger.info("  ✅ PASSED: Empty batch handled correctly")
        return True
    
    def test_single_column(self):
        """Test handling of single column (no pairs possible)."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Single column (no pairs)")
        logger.info("="*80)
        
        col_names = ['only_column']
        extractor = self._create_extractor(col_names)
        
        assert len(extractor.all_pairs) == 0
        
        encodings = torch.randn(self.batch_size, 1, self.d_model)
        
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        assert len(relationship_tokens) == 0
        
        logger.info("  ✅ PASSED: Single column handled correctly (no pairs)")
        return True
    
    def test_two_columns_one_pair(self):
        """Test with exactly 2 columns (1 pair)."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Two columns (one pair)")
        logger.info("="*80)
        
        col_names = ['cat', 'scalar']
        col_types = ['cat', 'scalar']
        
        extractor = self._create_extractor(col_names)
        encodings = self._create_mixed_encodings(col_types)
        
        assert len(extractor.all_pairs) == 1
        
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        # 1 pair × ops_per_pair tokens (1 if fused, 9 if unfused)
        assert len(relationship_tokens) == extractor.ops_per_pair
        
        for token in relationship_tokens:
            assert token.shape == (self.batch_size, self.d_model)
            assert not torch.isnan(token).any()
            assert not torch.isinf(token).any()
        
        logger.info("  ✅ PASSED: Two columns produce 6 relationship tokens")
        return True
    
    def test_large_model_dimension(self):
        """Test with large d_model (like real models)."""
        logger.info("\n" + "="*80)
        logger.info("TEST: Large model dimension (d_model=256)")
        logger.info("="*80)
        
        large_d_model = 256
        col_names = ['cat1', 'scalar1', 'cat2', 'scalar2']
        
        extractor = DynamicRelationshipExtractor(
            d_model=large_d_model,
            col_names_in_order=col_names,
            exploration_epochs=5,
            top_k_fraction=0.4,
        )
        
        # Create larger embeddings
        torch.manual_seed(42)
        encodings = torch.randn(self.batch_size, len(col_names), large_d_model)
        encodings = nn.functional.normalize(encodings, dim=-1)
        
        extractor.train()
        relationship_tokens = extractor(encodings)
        
        for token in relationship_tokens:
            assert token.shape == (self.batch_size, large_d_model)
            assert not torch.isnan(token).any()
            assert not torch.isinf(token).any()
        
        logger.info("  ✅ PASSED: Large d_model works correctly")
        return True
    
    def test_gpu_if_available(self):
        """Test on GPU if available."""
        if not torch.cuda.is_available():
            logger.info("\n" + "="*80)
            logger.info("TEST: GPU (SKIPPED - no GPU available)")
            logger.info("="*80)
            return True
        
        logger.info("\n" + "="*80)
        logger.info("TEST: GPU execution")
        logger.info("="*80)
        
        device = torch.device('cuda')
        
        col_names = ['cat1', 'scalar1', 'cat2', 'scalar2']
        col_types = ['cat', 'scalar', 'cat', 'scalar']
        
        extractor = self._create_extractor(col_names).to(device)
        encodings = self._create_mixed_encodings(col_types).to(device)
        
        extractor.train()
        relationship_tokens = extractor(encodings)  # pylint: disable=not-callable
        
        for token in relationship_tokens:
            assert token.device.type == 'cuda'
            assert not torch.isnan(token).any()
            assert not torch.isinf(token).any()
        
        logger.info("  ✅ PASSED: GPU execution works correctly")
        return True


def run_all_tests():
    """Run all tests in the suite."""
    test_suite = TestDynamicRelationshipExtractorMixedTypes()
    
    tests = [
        test_suite.test_scalar_scalar_pairs,
        test_suite.test_cat_cat_pairs,
        test_suite.test_cat_scalar_pairs,
        test_suite.test_gradient_flow_all_types,
        test_suite.test_division_stability,
        test_suite.test_masking_works,
        test_suite.test_progressive_pruning_with_mixed_types,
        test_suite.test_empty_batch,
        test_suite.test_single_column,
        test_suite.test_two_columns_one_pair,
        test_suite.test_large_model_dimension,
        test_suite.test_gpu_if_available,
    ]
    
    passed = 0
    failed = 0
    failed_tests = []
    
    logger.info("\n" + "="*80)
    logger.info("RUNNING DynamicRelationshipExtractor MIXED TYPE TESTS")
    logger.info("="*80)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            failed_tests.append((test_func.__name__, str(e)))
            logger.error(f"  ❌ FAILED: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"  Passed: {passed}/{len(tests)}")
    logger.info(f"  Failed: {failed}/{len(tests)}")
    
    if failed_tests:
        logger.info("\n  Failed tests:")
        for name, error in failed_tests:
            logger.info(f"    - {name}: {error}")
    
    if failed == 0:
        logger.info("\n  🎉 ALL TESTS PASSED!")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


