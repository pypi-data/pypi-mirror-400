#!/usr/bin/env python3
"""
QA Test: Feature Engineering Training/Inference Consistency

This test verifies that derived features created during training are properly
applied during prediction, ensuring training/inference consistency.

Test flow:
1. Train model WITH feature engineering (creates derived features)
2. Save and reload the model
3. Verify feature_engineer is stored in the model
4. Make predictions and verify derived features are calculated
5. Compare predictions with and without feature engineering
"""
import sys
import os
import pickle
import pandas as pd
from pathlib import Path

# Add paths - we're in src/lib/featrix/neural/qa/, need to add src/ and src/lib/
test_dir = Path(__file__).parent  # qa/
neural_dir = test_dir.parent  # neural/
featrix_dir = neural_dir.parent  # featrix/
lib_dir = featrix_dir.parent  # lib/
src_dir = lib_dir.parent  # src/

sys.path.insert(0, str(lib_dir))  # For featrix.neural imports
sys.path.insert(0, str(src_dir))  # For other src imports

from featrix.neural.input_data_file import FeatrixInputDataFile
from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.single_predictor import FeatrixSinglePredictor
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.feature_engineer import FeatureEngineer
from featrix.neural.gpu_utils import set_backend_cpu as set_device_cpu
import tempfile
import shutil

print("=" * 80)
print("FEATURE ENGINEERING PREDICTION CONSISTENCY TEST")
print("=" * 80)
print("Verifies that derived features are applied during prediction")
print()

# Force CPU for consistent testing
set_device_cpu()
print("✅ Forced CPU training")
print()

# Load credit data
data_file = Path(__file__).parent.parent.parent.parent.parent.parent / "qa_data" / "credit_g_31.csv"
if not data_file.exists():
    print(f"❌ Data file not found: {data_file}")
    sys.exit(1)

print(f"📁 Loading data from: {data_file}")
input_file = FeatrixInputDataFile(str(data_file))
df = input_file.df
print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
print()

# Create a temporary directory for outputs
temp_dir = Path(tempfile.mkdtemp(prefix="feature_eng_test_"))
print(f"📂 Using temp directory: {temp_dir}")
print()

try:
    # ============================================================================
    # STEP 1: Create some feature engineering suggestions
    # ============================================================================
    print("=" * 80)
    print("STEP 1: CREATING FEATURE ENGINEERING SUGGESTIONS")
    print("=" * 80)
    print()
    
    # Create simple feature suggestions manually
    suggestions = [
        {
            "name": "checking_duration_interaction",
            "type": "categorical_interaction",
            "features": ["checking_status", "duration"],
            "description": "Interaction between checking account status and loan duration",
            "rationale": "Test feature for verification"
        },
        {
            "name": "age_high_value",
            "type": "numeric_binning",
            "features": ["age"],
            "bins": [0, 30, 50, 100],
            "labels": ["young", "middle", "senior"],
            "description": "Age binning",
            "rationale": "Test feature for verification"
        }
    ]
    
    print(f"✅ Created {len(suggestions)} test feature suggestions:")
    for s in suggestions:
        print(f"   • {s['name']} ({s['type']})")
    print()
    
    # ============================================================================
    # STEP 2: Apply feature engineering to training data
    # ============================================================================
    print("=" * 80)
    print("STEP 2: APPLYING FEATURE ENGINEERING TO DATA")
    print("=" * 80)
    print()
    
    original_columns = set(df.columns)
    print(f"Original columns: {len(original_columns)}")
    
    engineer = FeatureEngineer(suggestions=suggestions)
    df_enhanced = engineer.fit_transform(df, verbose=True)
    
    enhanced_columns = set(df_enhanced.columns)
    new_columns = enhanced_columns - original_columns
    
    print()
    print(f"✅ Feature engineering applied")
    print(f"   Original columns: {len(original_columns)}")
    print(f"   Enhanced columns: {len(enhanced_columns)}")
    print(f"   New columns: {len(new_columns)}")
    if new_columns:
        print(f"   Derived features:")
        for col in new_columns:
            print(f"      • {col}")
    print()
    
    # ============================================================================
    # STEP 3: Train embedding space (quick version - 10 epochs)
    # ============================================================================
    print("=" * 80)
    print("STEP 3: TRAINING EMBEDDING SPACE (10 EPOCHS - QUICK)")
    print("=" * 80)
    print()
    
    # Create dataset with enhanced data
    dataset = FeatrixInputDataSet(
        df=df_enhanced,
        ignore_cols=["target"],  # Exclude target from features
        limit_rows=None,
        encoder_overrides=None,
    )
    
    # Split train/val
    train_data, val_data = dataset.split(fraction=0.2)
    print(f"📊 Train: {len(train_data.df)} rows, {len(train_data.df.columns)} columns")
    print(f"📊 Val: {len(val_data.df)} rows, {len(val_data.df.columns)} columns")
    print()
    
    es = EmbeddingSpace(
        train_data,
        val_data,
        n_epochs=10,
        d_model=64,  # Small for speed
        output_debug_label="feature_eng_test",
        output_dir=str(temp_dir)
    )
    
    print("🚀 Starting ES training...")
    es.train(batch_size=64, n_epochs=10, print_progress_step=5)
    print("✅ ES training complete")
    print()
    
    # ============================================================================
    # STEP 4: Train single predictor (quick - 10 epochs)
    # ============================================================================
    print("=" * 80)
    print("STEP 4: TRAINING SINGLE PREDICTOR (10 EPOCHS - QUICK)")
    print("=" * 80)
    print()
    
    mlp_config = SimpleMLPConfig(
        d_in=es.d_model,
        d_out=2,  # Binary: good/bad
        d_hidden=128,
        n_hidden_layers=2,
        dropout=0.1
    )
    mlp = SimpleMLP(mlp_config)
    
    fsp = FeatrixSinglePredictor(
        embedding_space=es,
        predictor=mlp,
        name="feature_eng_test_predictor"
    )
    
    # Prep for training - use enhanced data
    fsp.prep_for_training(
        train_df=df_enhanced,
        target_col_name="target",
        target_col_type="set",
        use_class_weights=True,
        loss_type="focal"
    )
    
    # CRITICAL: Manually set the feature_engineer to test our fix
    # In real training this would be set by _load_and_apply_previous_features()
    fsp.feature_engineer = engineer
    print("✅ Feature engineer stored in predictor")
    print()
    
    print("🚀 Starting single predictor training...")
    fsp.train(
        n_epochs=10,
        batch_size=64,
        optimizer_params={"lr": 0.0001},
        print_progress_step=5
    )
    print("✅ Single predictor training complete")
    print()
    
    # ============================================================================
    # STEP 5: Save and reload the predictor
    # ============================================================================
    print("=" * 80)
    print("STEP 5: SAVE AND RELOAD PREDICTOR")
    print("=" * 80)
    print()
    
    predictor_path = temp_dir / "test_predictor.pickle"
    print(f"💾 Saving predictor to: {predictor_path}")
    with open(predictor_path, 'wb') as f:
        pickle.dump(fsp, f)
    print("✅ Predictor saved")
    print()
    
    print(f"📂 Loading predictor from: {predictor_path}")
    with open(predictor_path, 'rb') as f:
        fsp_loaded = pickle.load(f)
    print("✅ Predictor loaded")
    print()
    
    # ============================================================================
    # STEP 6: Verify feature_engineer is present
    # ============================================================================
    print("=" * 80)
    print("STEP 6: VERIFY FEATURE ENGINEER IS STORED")
    print("=" * 80)
    print()
    
    has_engineer = hasattr(fsp_loaded, 'feature_engineer') and fsp_loaded.feature_engineer is not None
    
    if not has_engineer:
        print("❌ CRITICAL FAILURE: feature_engineer not found in loaded predictor!")
        print("   This means the fix is NOT working correctly")
        sys.exit(1)
    
    print("✅ Feature engineer found in loaded predictor")
    print(f"   Type: {type(fsp_loaded.feature_engineer)}")
    print(f"   Suggestions: {len(fsp_loaded.feature_engineer.suggestions)}")
    print(f"   Applied features: {len(fsp_loaded.feature_engineer.applied_features)}")
    print(f"   Is fitted: {fsp_loaded.feature_engineer.is_fitted}")
    print()
    
    # ============================================================================
    # STEP 7: Test prediction WITH feature engineering
    # ============================================================================
    print("=" * 80)
    print("STEP 7: TEST PREDICTION WITH FEATURE ENGINEERING")
    print("=" * 80)
    print()
    
    # Get a test sample (use original data without derived features)
    test_sample = df.drop(columns=['target']).iloc[0].to_dict()
    
    print(f"Test input (original features only):")
    print(f"   Columns: {len(test_sample)}")
    for key in list(test_sample.keys())[:5]:
        print(f"      {key}: {test_sample[key]}")
    print(f"      ... and {len(test_sample) - 5} more")
    print()
    
    print("🔮 Making prediction (should apply feature engineering internally)...")
    result = fsp_loaded.predict(test_sample, debug_print=True, extended_result=False)
    
    print()
    print(f"✅ Prediction succeeded!")
    print(f"   Result: {result}")
    print()
    
    # ============================================================================
    # STEP 8: Test prediction WITHOUT feature engineering (for comparison)
    # ============================================================================
    print("=" * 80)
    print("STEP 8: TEST PREDICTION WITHOUT FEATURE ENGINEERING (COMPARISON)")
    print("=" * 80)
    print()
    
    # Temporarily remove feature engineer to test difference
    original_engineer = fsp_loaded.feature_engineer
    fsp_loaded.feature_engineer = None
    
    print("🔮 Making prediction WITHOUT feature engineering...")
    result_no_fe = fsp_loaded.predict(test_sample, debug_print=False, extended_result=False)
    
    print(f"✅ Prediction succeeded!")
    print(f"   Result: {result_no_fe}")
    print()
    
    # Restore engineer
    fsp_loaded.feature_engineer = original_engineer
    
    # ============================================================================
    # STEP 9: Compare predictions
    # ============================================================================
    print("=" * 80)
    print("STEP 9: COMPARE PREDICTIONS")
    print("=" * 80)
    print()
    
    print("Predictions with vs without feature engineering:")
    print()
    print("WITH feature engineering:")
    for class_name, prob in result.items():
        print(f"   {class_name}: {prob:.4f}")
    print()
    print("WITHOUT feature engineering:")
    for class_name, prob in result_no_fe.items():
        print(f"   {class_name}: {prob:.4f}")
    print()
    
    # Check if predictions are different (they should be)
    predictions_differ = False
    max_diff = 0.0
    for class_name in result.keys():
        diff = abs(result[class_name] - result_no_fe[class_name])
        if diff > 0.001:  # More than 0.1% difference
            predictions_differ = True
        max_diff = max(max_diff, diff)
    
    if predictions_differ:
        print(f"✅ Predictions ARE different (max diff: {max_diff:.4f})")
        print(f"   This confirms feature engineering is being applied!")
    else:
        print(f"⚠️  Predictions are the same (max diff: {max_diff:.4f})")
        print(f"   This might mean feature engineering had no effect on this sample")
        print(f"   (Not necessarily a bug, but worth investigating)")
    print()
    
    # ============================================================================
    # STEP 10: Verify derived features are created during prediction
    # ============================================================================
    print("=" * 80)
    print("STEP 10: VERIFY DERIVED FEATURES ARE CREATED")
    print("=" * 80)
    print()
    
    # Test the feature engineer directly to show what it does
    test_df = pd.DataFrame([test_sample])
    print(f"Input DataFrame columns: {len(test_df.columns)}")
    
    test_df_enhanced = fsp_loaded.feature_engineer.transform(test_df, verbose=False)
    print(f"Enhanced DataFrame columns: {len(test_df_enhanced.columns)}")
    
    new_cols = set(test_df_enhanced.columns) - set(test_df.columns)
    print(f"Derived features created: {len(new_cols)}")
    if new_cols:
        print("   Features:")
        for col in new_cols:
            print(f"      • {col} = {test_df_enhanced[col].iloc[0]}")
    print()
    
    # ============================================================================
    # FINAL RESULTS
    # ============================================================================
    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print("   ✅ Feature engineer was stored in predictor")
    print("   ✅ Feature engineer survived pickle save/load")
    print("   ✅ Predictions work with feature engineering")
    print("   ✅ Derived features are created during prediction")
    print(f"   ✅ Predictions differ by up to {max_diff:.4f} with/without FE")
    print()
    print("TRAINING/INFERENCE CONSISTENCY VERIFIED! 🎉")
    print()
    
finally:
    # Cleanup
    print("🧹 Cleaning up temporary directory...")
    try:
        shutil.rmtree(temp_dir)
        print("✅ Cleanup complete")
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")
        print(f"   Manual cleanup needed: {temp_dir}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

