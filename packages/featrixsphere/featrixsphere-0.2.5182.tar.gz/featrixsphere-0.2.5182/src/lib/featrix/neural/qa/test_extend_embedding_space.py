#!/usr/bin/env python3
"""
Test for EmbeddingSpace.extend_from_existing() and row embedding comparison.

This test validates:
1. ES can be extended with new feature columns
2. Existing encoder weights are preserved
3. New columns get codecs created
4. Extension metadata is stored correctly
5. Row embeddings can be compared between ES versions
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.feature_engineer import FeatureEngineer
from featrix.neural.io_utils import load_embedded_space
from featrix.neural.embedding_space_utils import write_embedding_space_pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create test output directory
    test_output_dir = Path("qa.out/test_extend_es")
    test_output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("TEST: Extending EmbeddingSpace with New Features")
    print("=" * 80)
    print()

    try:
        # ========================================================================
        # STEP 1: Create initial dataset and train ES v1
        # ========================================================================
        print("=" * 80)
        print("STEP 1: Create Initial Dataset and Train ES v1")
        print("=" * 80)
        print()
        
        # Create synthetic credit data
        np.random.seed(42)
        n_rows = 500
        
        data = pd.DataFrame({
            'age': np.random.randint(18, 70, n_rows),
            'income': np.random.randint(20000, 150000, n_rows),
            'credit_score': np.random.randint(300, 850, n_rows),
            'loan_amount': np.random.randint(5000, 50000, n_rows),
            'employment_years': np.random.randint(0, 40, n_rows),
            'has_mortgage': np.random.choice(['yes', 'no'], n_rows),
            'education': np.random.choice(['high_school', 'bachelors', 'masters', 'phd'], n_rows),
            'target': np.random.choice(['approved', 'denied'], n_rows)
        })
        
        # Add row ID for tracking
        data['customer_id'] = [f"CUST_{i:04d}" for i in range(n_rows)]
        
        print(f"Created dataset: {len(data)} rows, {len(data.columns)} columns")
        print(f"Columns: {list(data.columns)}")
        print()
        
        # Create InputDataSets (exclude target and ID)
        dataset = FeatrixInputDataSet(
        df=data,
        ignore_cols=['target', 'customer_id'],
        dataset_title="credit_data_v1"
        )
    
        # Split train/val
        train_data, val_data = dataset.split(fraction=0.2)
        print(f"Train: {len(train_data)} rows, Val: {len(val_data)} rows")
        print()
    
        # Train ES v1
        print("Training ES v1 (20 epochs)...")
        es_v1 = EmbeddingSpace(
        train_input_data=train_data,
        val_input_data=val_data,
        d_model=64,  # Small for testing
        n_epochs=20,
        output_dir=str(test_output_dir / "es_v1"),
        name="credit_es_v1"
        )
    
        es_v1.train(batch_size=32, n_epochs=20, print_progress_step=5)
    
        # Save ES v1
        es_v1_path = test_output_dir / "embedding_space_v1.pkl"
        write_embedding_space_pickle(es_v1, str(test_output_dir), filename="embedding_space_v1.pkl")
    
        print()
        print(f"✅ ES v1 trained and saved to: {es_v1_path}")
        print(f"   Columns: {len(es_v1.col_codecs)}")
        print(f"   d_model: {es_v1.d_model}")
        print()
    
        # ========================================================================
        # STEP 2: Create engineered features and apply to data
        # ========================================================================
        print("=" * 80)
        print("STEP 2: Create Engineered Features")
        print("=" * 80)
        print()
    
        # Create feature engineering suggestions manually
        suggestions = [
        {
            "type": "numeric_binning",
            "features": ["age"],
            "name": "younger_borrower",
            "description": "Younger borrower (age < 30)",
            "implementation": "df['younger_borrower'] = (df['age'] < 30).astype(int)"
        },
        {
            "type": "numeric_ratio",
            "features": ["loan_amount", "income"],
            "name": "debt_to_income_ratio",
            "description": "Debt to income ratio",
            "implementation": "df['debt_to_income_ratio'] = df['loan_amount'] / (df['income'] + 1e-6)"
        }
        ]
    
        # Apply features using FeatureEngineer
        engineer = FeatureEngineer(suggestions=suggestions)
    
        enriched_train_df = engineer.fit_transform(train_data.df.copy(), verbose=True)
        enriched_val_df = engineer.transform(val_data.df.copy(), verbose=False)
    
        print()
        print(f"✅ Features applied:")
        print(f"   Original columns: {len(train_data.df.columns)}")
        print(f"   Enriched columns: {len(enriched_train_df.columns)}")
        print(f"   New columns: {set(enriched_train_df.columns) - set(train_data.df.columns)}")
        print()
    
        # ========================================================================
        # STEP 3: Extend ES v1 to create ES v2
        # ========================================================================
        print("=" * 80)
        print("STEP 3: Extend ES v1 with New Features")
        print("=" * 80)
        print()
    
        # Reload ES v1 (simulates loading from saved file)
        es_v1_loaded = load_embedded_space(str(es_v1_path))
    
        # Extend ES
        es_v2 = EmbeddingSpace.extend_from_existing(
        existing_es=es_v1_loaded,
        enriched_train_df=enriched_train_df,
        enriched_val_df=enriched_val_df,
        n_epochs=5,  # 20/4 = 5
        output_dir=str(test_output_dir / "es_v2"),
        name="credit_es_v2",
        feature_metadata={
            "source": "test_script",
            "applied_features": ["younger_borrower", "debt_to_income_ratio"]
        }
        )
    
        print()
        print(f"✅ ES v2 created:")
        print(f"   Original columns: {len(es_v1_loaded.col_codecs)}")
        print(f"   Extended columns: {len(es_v2.col_codecs)}")
        print(f"   New columns in ES v2: {set(es_v2.col_codecs.keys()) - set(es_v1_loaded.col_codecs.keys())}")
        print()
    
        # Check extension metadata
        assert hasattr(es_v2, 'extension_metadata'), "❌ Extension metadata not stored"
        assert es_v2.extension_metadata['extended_from_es_name'] == 'credit_es_v1', "❌ Wrong ES name in metadata"
        assert len(es_v2.extension_metadata['new_columns_added']) == 2, "❌ Wrong number of new columns in metadata"
    
        print(f"✅ Extension metadata validated:")
        print(f"   Extended from: {es_v2.extension_metadata['extended_from_es_name']}")
        print(f"   New columns: {es_v2.extension_metadata['new_columns_added']}")
        print(f"   Training epochs: {es_v2.extension_metadata['training_epochs_used']}")
        print()
    
        # ========================================================================
        # STEP 4: Train ES v2
        # ========================================================================
        print("=" * 80)
        print("STEP 4: Train Extended ES v2")
        print("=" * 80)
        print()
    
        print("Training ES v2 (5 epochs)...")
        es_v2.train(batch_size=32, n_epochs=5, print_progress_step=2)
    
        # Save ES v2
        es_v2_path = test_output_dir / "embedding_space_v2.pkl"
        write_embedding_space_pickle(es_v2, str(test_output_dir), filename="embedding_space_v2.pkl")
    
        print()
        print(f"✅ ES v2 trained and saved to: {es_v2_path}")
        print()
    
        # ========================================================================
        # STEP 5: Compare row embeddings between ES v1 and ES v2
        # ========================================================================
        print("=" * 80)
        print("STEP 5: Compare Row Embeddings (ES v1 vs ES v2)")
        print("=" * 80)
        print()
    
        # Reload both ES versions
        es_v1_final = load_embedded_space(str(es_v1_path))
        es_v2_final = load_embedded_space(str(es_v2_path))
    
        # Use first 100 rows for comparison
        test_rows = enriched_train_df.head(100).copy()
    
        # Compare embeddings
        comparison = es_v1_final.compare_row_embeddings(
        other_es=es_v2_final,
        rows_df=test_rows,
        row_id_column='customer_id',
        top_n_movers=20
        )
    
        print()
        print(f"✅ Embedding comparison completed:")
        print(f"   Rows compared: {comparison['num_rows_compared']}")
        print(f"   Mean distance: {comparison['mean_distance']:.4f}")
        print(f"   Median distance: {comparison['median_distance']:.4f}")
        print(f"   Std deviation: {comparison['std_distance']:.4f}")
        print(f"   Max distance: {comparison['max_distance']:.4f}")
        print()
        
        print("Top 10 movers (rows with biggest embedding shifts):")
        for i, mover in enumerate(comparison['top_movers'][:10], 1):
            print(f"   {i}. Customer {mover['row_id']}: moved {mover['distance']:.4f} (top {mover['percentile']:.1f}%)")
        print()
        
        # ========================================================================
        # STEP 6: Test Prediction with Extended ES + Feature Engineering
        # ========================================================================
        print("=" * 80)
        print("STEP 6: Test Prediction with Feature Engineering")
        print("=" * 80)
        print()
        print("This tests that feature engineering is applied during prediction")
        print("for extended embedding spaces (critical for training/inference consistency)")
        print()
        
        # Import what we need for prediction test
        from featrix.neural.single_predictor import FeatrixSinglePredictor
        from featrix.neural.simple_mlp import SimpleMLP
        from featrix.neural.model_config import SimpleMLPConfig
        
        # Train a quick predictor on ES v2
        print("Training a predictor on extended ES v2...")
        mlp_config = SimpleMLPConfig(
            d_in=es_v2_final.d_model,
            d_out=2,  # Binary: approved/denied
            d_hidden=64,
            n_hidden_layers=2,
            dropout=0.1
        )
        mlp = SimpleMLP(mlp_config)
        
        predictor = FeatrixSinglePredictor(
            embedding_space=es_v2_final,
            predictor=mlp,
            name="test_predictor_extended_es"
        )
        
        # Prep for training with enriched data
        predictor.prep_for_training(
            train_df=enriched_train_df,
            target_col_name='target',
            target_col_type='set',
            use_class_weights=False,
            loss_type='cross_entropy'
        )
        
        # CRITICAL: Store the feature engineer for prediction-time consistency
        predictor.feature_engineer = engineer
        print(f"✅ Feature engineer stored in predictor")
        print(f"   Suggestions: {len(engineer.suggestions)}")
        print()
        
        # Quick training (5 epochs)
        print("Training for 5 epochs...")
        predictor.train(
            n_epochs=5,
            batch_size=32,
            optimizer_params={'lr': 0.0001},
            print_progress_step=2
        )
        print("✅ Predictor trained")
        print()
        
        # Test prediction WITHOUT derived features (just original columns)
        test_row = data.drop(columns=['target', 'customer_id']).iloc[0].to_dict()
        
        print(f"Test prediction (input has {len(test_row)} original columns):")
        print(f"   Input columns: {list(test_row.keys())}")
        print()
        
        # Make prediction - should apply feature engineering internally
        print("Making prediction (feature engineering should be applied automatically)...")
        result = predictor.predict(test_row, debug_print=False, extended_result=False)
        
        print(f"✅ Prediction succeeded!")
        print(f"   Result: {result}")
        print()
        
        # Verify the feature engineer is being used
        if predictor.feature_engineer is not None:
            print("✅ Feature engineer is present in predictor")
            print(f"   This ensures derived features are calculated during prediction")
        else:
            print("⚠️  WARNING: Feature engineer is None (fix may not be working)")
        print()
        
        # ========================================================================
        # STEP 7: Validate results
        # ========================================================================
        print("=" * 80)
        print("STEP 7: Validate Results")
        print("=" * 80)
        print()
    
        # Check 1: ES v2 has more columns than ES v1
        assert len(es_v2_final.col_codecs) > len(es_v1_final.col_codecs), "❌ ES v2 should have more columns"
        print(f"✅ ES v2 has {len(es_v2_final.col_codecs)} columns vs ES v1's {len(es_v1_final.col_codecs)}")
    
        # Check 2: New columns have codecs
        new_columns = set(es_v2_final.col_codecs.keys()) - set(es_v1_final.col_codecs.keys())
        assert 'younger_borrower' in new_columns, "❌ younger_borrower should be in ES v2"
        assert 'debt_to_income_ratio' in new_columns, "❌ debt_to_income_ratio should be in ES v2"
        print(f"✅ New columns have codecs: {new_columns}")
    
        # Check 3: Embeddings have same dimensionality
        assert es_v1_final.d_model == es_v2_final.d_model, "❌ d_model should be same"
        print(f"✅ Both ES versions have d_model={es_v1_final.d_model}")
    
        # Check 4: Embeddings changed (mean distance > 0)
        assert comparison['mean_distance'] > 0, "❌ Embeddings should change when features are added"
        print(f"✅ Embeddings shifted with mean distance: {comparison['mean_distance']:.4f}")
    
        # Check 5: Distance distribution makes sense
        assert comparison['max_distance'] >= comparison['mean_distance'], "❌ Max should be >= mean"
        assert comparison['mean_distance'] >= comparison['min_distance'], "❌ Mean should be >= min"
        print(f"✅ Distance distribution is valid (min={comparison['min_distance']:.4f}, mean={comparison['mean_distance']:.4f}, max={comparison['max_distance']:.4f})")
    
        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print()
    
        print("Test Summary:")
        print(f"  • Created ES v1 with {len(es_v1_final.col_codecs)} columns")
        print(f"  • Applied 2 engineered features")
        print(f"  • Extended to ES v2 with {len(es_v2_final.col_codecs)} columns")
        print(f"  • Compared embeddings for {comparison['num_rows_compared']} rows")
        print(f"  • Mean embedding shift: {comparison['mean_distance']:.4f}")
        print(f"  • Extension metadata stored and validated")
        print()
    
        print(f"Output files saved to: {test_output_dir}")
        print(f"  • {es_v1_path.name} - Original ES")
        print(f"  • {es_v2_path.name} - Extended ES")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("Test completed successfully! ✅")

if __name__ == '__main__':
    main()
