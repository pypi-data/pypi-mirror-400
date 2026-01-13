#!/usr/bin/env python3
"""
COMPREHENSIVE ADAPTIVE LOSS BENCHMARK

Tests ALL loss types: adaptive, focal, cross_entropy, prauc
Across multiple class imbalance scenarios to prove which is best.

This will definitively answer: Is AdaptiveLoss actually better?
"""
import sys
import os
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime
import numpy as np

# Paths
test_dir = Path(__file__).parent
neural_dir = test_dir.parent
featrix_dir = neural_dir.parent
lib_dir = featrix_dir.parent
src_dir = lib_dir.parent

sys.path.insert(0, str(lib_dir))
sys.path.insert(0, str(src_dir))

from featrix.neural.input_data_file import FeatrixInputDataFile
from featrix.neural.embedded_space import EmbeddingSpace
from featrix.neural.input_data_set import FeatrixInputDataSet
from featrix.neural.single_predictor import FeatrixSinglePredictor
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.gpu_utils import set_backend_cpu as set_device_cpu
import pandas as pd

set_device_cpu()

print("=" * 80)
print("🔥 ADAPTIVE LOSS BENCHMARK - PROVING WHICH LOSS IS BEST")
print("=" * 80)
print(f"Started: {datetime.now()}")
print()
print("Testing: adaptive, focal, cross_entropy, prauc")
print("Goal: Prove once and for all if AdaptiveLoss is worth the complexity")
print()

# Load data
data_file = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "qa_data" / "credit_g_31.csv"
if not data_file.exists():
    print(f"❌ ERROR: Data file not found: {data_file}")
    print("   Please ensure qa_data/credit_g_31.csv exists")
    sys.exit(1)

input_file = FeatrixInputDataFile(str(data_file))
df = input_file.df

print(f"📊 Dataset: {len(df)} samples")
target_counts = df["target"].value_counts()
total = len(df)
for label in sorted(target_counts.index):
    count = target_counts[label]
    pct = count / total * 100
    print(f"   {label}: {count} ({pct:.1f}%)")
print()

def create_dataset(df, pos_count, neg_count, pos_label="good"):
    """Sample specific counts WITHOUT replacement."""
    neg_label = "bad" if pos_label == "good" else "good"
    pos = df[df["target"] == pos_label].sample(n=pos_count, random_state=42, replace=False)
    neg = df[df["target"] == neg_label].sample(n=neg_count, random_state=42, replace=False)
    return pd.concat([pos, neg]).sample(frac=1, random_state=42).reset_index(drop=True)

def compute_enhanced_metrics(y_true, y_pred, y_prob, pos_label="good"):
    """Compute comprehensive metrics."""
    from sklearn.metrics import (
        confusion_matrix, matthews_corrcoef, 
        balanced_accuracy_score, average_precision_score,
        brier_score_loss, roc_auc_score
    )
    
    y_true_binary = [1 if y == pos_label else 0 for y in y_true]
    y_pred_binary = [1 if y == pos_label else 0 for y in y_pred]
    
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    return {
        "mcc": float(matthews_corrcoef(y_true_binary, y_pred_binary)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true_binary, y_pred_binary)),
        "specificity": float(specificity),
        "pr_auc": float(average_precision_score(y_true_binary, y_prob)),
        "brier_score": float(brier_score_loss(y_true_binary, y_prob)),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
    }

# Test configurations - covering key imbalance scenarios
configs = [
    (300, 300, "50/50 Balanced"),
    (225, 75, "75/25 Moderate"),
    (270, 30, "90/10 Extreme"),
    (75, 225, "25/75 Inverted"),
    (30, 270, "10/90 Extreme Inverted"),
]

# ALL loss types to compare
loss_types = ["adaptive", "focal", "cross_entropy", "prauc"]

results = []

# Train ES once (shared across all tests)
print("=" * 80)
print("Training Embedding Space (shared across all tests)...")
print("=" * 80)
dataset = FeatrixInputDataSet(df=df, ignore_cols=[], limit_rows=None, encoder_overrides=None)

detected_types = {}
for col_name, detector in dataset._detectors.items():
    detected_types[col_name] = detector.get_codec_name()

dataset.encoderOverrides = detected_types
train_data, val_data = dataset.split(fraction=0.2)

es = EmbeddingSpace(train_data, val_data, n_epochs=50, d_model=128, output_debug_label="adaptive_benchmark")
es.train(batch_size=128, n_epochs=50)
print("✅ ES training complete\n")

test_num = 0
total_tests = len(configs) * len(loss_types)

for pos_count, neg_count, ratio_name in configs:
    print("=" * 80)
    print(f"RATIO: {ratio_name} ({pos_count} pos / {neg_count} neg)")
    print("=" * 80)
    
    balanced_df = create_dataset(df, pos_count, neg_count)
    
    for loss_type in loss_types:
        test_num += 1
        run_id = f"[{ratio_name.replace('/', '_')}/{loss_type}]"
        
        print(f"\n[{test_num}/{total_tests}] {run_id} {loss_type.upper()}...", end=" ", flush=True)
        
        start_time = time.time()
        
        try:
            config = SimpleMLPConfig(
                d_in=128, d_out=2, d_hidden=256, 
                n_hidden_layers=2, dropout=0.1, 
                normalize=False, residual=True, use_batch_norm=True
            )
            predictor = SimpleMLP(config)
            fsp = FeatrixSinglePredictor(es, predictor)
            fsp.run_identifier = run_id
            
            fsp.prep_for_training(
                train_df=balanced_df, 
                target_col_name="target", 
                target_col_type="set", 
                use_class_weights=True,  # Use class weights for fair comparison
                loss_type=loss_type
            )
            
            # Track adaptive loss weights if using adaptive
            adaptive_weights_history = []
            
            def progress_callback(progress):
                epoch = progress.get("epoch", 0)
                if epoch % 10 == 0 and hasattr(fsp, 'target_codec') and hasattr(fsp.target_codec, 'loss_fn'):
                    from featrix.neural.set_codec import AdaptiveLoss
                    if isinstance(fsp.target_codec.loss_fn, AdaptiveLoss):
                        weights = fsp.target_codec.loss_fn.get_current_weights()
                        if weights is not None:
                            adaptive_weights_history.append({
                                "epoch": epoch,
                                "focal": float(weights[0]),
                                "prauc": float(weights[1]),
                                "ce": float(weights[2])
                            })
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            viz_id = f"{ratio_name.replace('/', '_')}_{loss_type}"
            sp_id = f"target_{ratio_name.replace('/', '_')}_{loss_type}"
            
            training_results = loop.run_until_complete(fsp.train(
                n_epochs=50, 
                batch_size=128, 
                fine_tune=True, 
                val_pos_label="good",
                print_callback=progress_callback,
                print_progress_step=10,
                network_viz_identifier=viz_id,
                sp_identifier=sp_id
            ))
            loop.close()
            
            elapsed_time = time.time() - start_time
            
            if training_results and len(training_results) > 0:
                final = training_results[-1]
                metrics = final.get("metrics", {})
                
                # Find best epoch (lowest validation loss)
                best_epoch_idx = min(range(len(training_results)), 
                                   key=lambda i: training_results[i].get("validation_loss", float('inf')))
                best_epoch_result = training_results[best_epoch_idx]
                best_epoch_metrics = best_epoch_result.get("metrics", {})
                
                # Get predictions for enhanced metrics
                val_df = balanced_df.sample(frac=0.2, random_state=42)
                # Convert DataFrame to list of dicts and use predict_batch
                val_records = val_df.drop(columns=["target"]).to_dict(orient="records")
                predictions = fsp.predict_batch(val_records, extended_result=True)
                
                y_true = val_df["target"].values
                y_pred = [p["prediction"] for p in predictions]
                y_prob = [p.get("probabilities", {}).get("good", 0.5) for p in predictions]
                
                enhanced = compute_enhanced_metrics(y_true, y_pred, y_prob)
                
                result = {
                    "ratio_name": ratio_name,
                    "pos_count": pos_count,
                    "neg_count": neg_count,
                    "loss_type": loss_type,
                    "validation_loss": float(final.get("validation_loss", 0)),
                    "training_loss": float(final.get("training_loss", 0)),
                    "best_epoch": int(best_epoch_idx),
                    "best_epoch_val_loss": float(best_epoch_result.get("validation_loss", 0)),
                    "best_epoch_train_loss": float(best_epoch_result.get("training_loss", 0)),
                    "accuracy": float(metrics.get("accuracy", 0)),
                    "f1": float(metrics.get("f1", 0)),
                    "precision": float(metrics.get("precision", 0)),
                    "recall": float(metrics.get("recall", 0)),
                    "auc": float(metrics.get("auc", 0)),
                    "mcc": enhanced["mcc"],
                    "balanced_accuracy": enhanced["balanced_accuracy"],
                    "specificity": enhanced["specificity"],
                    "pr_auc": enhanced["pr_auc"],
                    "brier_score": enhanced["brier_score"],
                    "tp": enhanced["tp"],
                    "fp": enhanced["fp"],
                    "tn": enhanced["tn"],
                    "fn": enhanced["fn"],
                    "training_time_seconds": float(elapsed_time),
                    "adaptive_weights_history": adaptive_weights_history if loss_type == "adaptive" else None,
                }
                
                results.append(result)
                
                print(f"✅ Loss={result['validation_loss']:.3f}, F1={result['f1']:.3f}, AUC={result['auc']:.3f}, Time={elapsed_time:.1f}s")
            else:
                print(f"❌ No training results")
                results.append({
                    "ratio_name": ratio_name,
                    "loss_type": loss_type,
                    "error": "No training results",
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "ratio_name": ratio_name,
                "loss_type": loss_type,
                "error": str(e),
            })

print()
print("=" * 80)
print("📊 RESULTS SUMMARY")
print("=" * 80)

# Group by ratio and compare
for ratio_name in [c[2] for c in configs]:
    print(f"\n{'='*80}")
    print(f"RATIO: {ratio_name}")
    print(f"{'='*80}")
    
    ratio_results = [r for r in results if r.get("ratio_name") == ratio_name and "error" not in r]
    
    if not ratio_results:
        print("  No results")
        continue
    
    # Sort by validation loss (lower is better)
    ratio_results.sort(key=lambda x: x.get("validation_loss", float('inf')))
    
    print(f"\n  📈 Validation Loss (lower is better):")
    for r in ratio_results:
        loss_type = r["loss_type"]
        val_loss = r.get("validation_loss", 0)
        f1 = r.get("f1", 0)
        auc = r.get("auc", 0)
        time_sec = r.get("training_time_seconds", 0)
        print(f"     {loss_type:15s}: {val_loss:.4f}  (F1={f1:.3f}, AUC={auc:.3f}, Time={time_sec:.1f}s)")
    
    # Winner by validation loss
    best_loss = ratio_results[0]
    print(f"\n  🏆 Best Loss: {best_loss['loss_type']} ({best_loss.get('validation_loss', 0):.4f})")
    
    # Sort by F1 (higher is better)
    ratio_results.sort(key=lambda x: x.get("f1", 0), reverse=True)
    best_f1 = ratio_results[0]
    print(f"  🏆 Best F1:   {best_f1['loss_type']} ({best_f1.get('f1', 0):.3f})")
    
    # Sort by AUC (higher is better)
    ratio_results.sort(key=lambda x: x.get("auc", 0), reverse=True)
    best_auc = ratio_results[0]
    print(f"  🏆 Best AUC:  {best_auc['loss_type']} ({best_auc.get('auc', 0):.3f})")
    
    # Show adaptive weights if available
    adaptive_result = next((r for r in ratio_results if r["loss_type"] == "adaptive"), None)
    if adaptive_result and adaptive_result.get("adaptive_weights_history"):
        weights = adaptive_result["adaptive_weights_history"]
        if weights:
            final_weights = weights[-1]
            print(f"\n  🧠 AdaptiveLoss Final Weights:")
            print(f"     Focal: {final_weights['focal']:.3f}")
            print(f"     PRAUC: {final_weights['prauc']:.3f}")
            print(f"     CE:    {final_weights['ce']:.3f}")

# Overall winner
print(f"\n{'='*80}")
print("🏆 OVERALL WINNERS")
print(f"{'='*80}")

# Count wins by metric
loss_wins = {"validation_loss": {}, "f1": {}, "auc": {}}

for ratio_name in [c[2] for c in configs]:
    ratio_results = [r for r in results if r.get("ratio_name") == ratio_name and "error" not in r]
    if not ratio_results:
        continue
    
    # Best validation loss
    best_loss = min(ratio_results, key=lambda x: x.get("validation_loss", float('inf')))
    loss_type = best_loss["loss_type"]
    loss_wins["validation_loss"][loss_type] = loss_wins["validation_loss"].get(loss_type, 0) + 1
    
    # Best F1
    best_f1 = max(ratio_results, key=lambda x: x.get("f1", 0))
    loss_type = best_f1["loss_type"]
    loss_wins["f1"][loss_type] = loss_wins["f1"].get(loss_type, 0) + 1
    
    # Best AUC
    best_auc = max(ratio_results, key=lambda x: x.get("auc", 0))
    loss_type = best_auc["loss_type"]
    loss_wins["auc"][loss_type] = loss_wins["auc"].get(loss_type, 0) + 1

print(f"\n  Wins by Validation Loss:")
for loss_type in loss_types:
    wins = loss_wins["validation_loss"].get(loss_type, 0)
    print(f"     {loss_type:15s}: {wins}/{len(configs)}")

print(f"\n  Wins by F1 Score:")
for loss_type in loss_types:
    wins = loss_wins["f1"].get(loss_type, 0)
    print(f"     {loss_type:15s}: {wins}/{len(configs)}")

print(f"\n  Wins by AUC:")
for loss_type in loss_types:
    wins = loss_wins["auc"].get(loss_type, 0)
    print(f"     {loss_type:15s}: {wins}/{len(configs)}")

# Save results
output_file = test_dir / f"adaptive_loss_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "configs": [{"ratio": c[2], "pos": c[0], "neg": c[1]} for c in configs],
        "loss_types": loss_types,
        "results": results,
        "summary": {
            "wins_by_validation_loss": loss_wins["validation_loss"],
            "wins_by_f1": loss_wins["f1"],
            "wins_by_auc": loss_wins["auc"],
        }
    }, f, indent=2)

print(f"\n✅ Results saved: {output_file}")
print(f"✅ Completed: {datetime.now()}")

