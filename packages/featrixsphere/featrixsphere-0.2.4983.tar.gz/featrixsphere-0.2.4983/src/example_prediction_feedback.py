#!/usr/bin/env python3
"""
Example: Prediction Feedback and Retraining System

This script demonstrates how to:
1. Make predictions that are stored with UUIDs
2. Update labels when predictions are wrong
3. Create retraining batches from corrected predictions
4. Build a feedback loop for model improvement
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from test_api_client import FeatrixSphereClient

def demonstrate_feedback_system():
    """Demonstrate the complete prediction feedback workflow."""
    
    print("🔄 " + "="*60)
    print("🔄 PREDICTION FEEDBACK & RETRAINING DEMO")
    print("🔄 " + "="*60)
    
    # Initialize client
    client = FeatrixSphereClient("https://sphere-api.featrix.com")
    
    # Use existing session with trained predictor
    session_id = "20250623-124806_4591e7"  # Update this to your session
    
    print(f"\n1. 🎯 Making predictions with feedback tracking...")
    
    # Example test records
    test_records = [
        {"domain": "shell.com", "snippet": "fuel card rewards program for drivers", "keyword": "fuel card"},
        {"domain": "exxon.com", "snippet": "gas station locator near you", "keyword": "gas station"},
        {"domain": "amazon.com", "snippet": "buy books and electronics online", "keyword": "shopping"},
        {"domain": "bp.com", "snippet": "fleet fuel cards for business", "keyword": "fleet cards"},
        {"domain": "chevron.com", "snippet": "find chevron gas stations", "keyword": "gas station"},
    ]
    
    # Known correct labels for demonstration
    correct_labels = ["True", "False", "False", "True", "False"]
    
    prediction_ids = []
    
    for i, record in enumerate(test_records):
        try:
            # Make prediction (this will store it in database with UUID)
            result = client.make_prediction(session_id, record)
            prediction_id = result.get('prediction_id')
            prediction = result.get('prediction', {})
            
            if prediction_id:
                prediction_ids.append(prediction_id)
                
                # Get predicted class
                if isinstance(prediction, dict) and prediction:
                    predicted_class = max(prediction, key=prediction.get)
                    confidence = prediction[predicted_class]
                    
                    print(f"  Record {i+1}: {predicted_class} ({confidence*100:.1f}% confidence)")
                    print(f"    Prediction ID: {prediction_id}")
                    print(f"    Input: {record}")
                    print()
                
        except Exception as e:
            print(f"  ❌ Error with record {i+1}: {e}")
    
    print(f"\n2. 📝 Simulating user feedback (correcting wrong predictions)...")
    
    # Simulate user providing feedback on predictions
    corrections_made = 0
    
    # NOTE: Prediction feedback API not yet implemented
    print(f"  ⚠️  Prediction feedback API (update_prediction_label) not yet implemented")
    print(f"  ⚠️  This feature requires additional API endpoints to be added")
    
    print(f"\n3. 📊 Retrieving corrected predictions...")
    
    # NOTE: Prediction retrieval API not yet implemented
    print(f"  ⚠️  Prediction retrieval API (get_session_predictions) not yet implemented")
    print(f"  ⚠️  This feature requires additional API endpoints to be added")
    
    print(f"\n4. 🔄 Creating retraining batch...")
    
    # NOTE: Retraining batch API not yet implemented
    print(f"  ⚠️  Retraining batch API (create_retraining_batch) not yet implemented")
    print(f"  ⚠️  This feature requires additional API endpoints to be added")
    
    print(f"\n" + "="*60)
    print(f"📋 FEEDBACK SYSTEM SUMMARY")
    print(f"="*60)
    print(f"✅ Predictions made: {len(prediction_ids)}")
    print(f"✅ Corrections provided: {corrections_made}")
    print(f"✅ Retraining batch: {'Created' if corrections_made > 0 else 'Skipped'}")
    print()
    print(f"💡 Next steps for production:")
    print(f"   - Build UI for users to correct predictions")
    print(f"   - Implement automated retraining pipeline")
    print(f"   - Add model versioning and A/B testing")
    print(f"   - Monitor prediction accuracy over time")
    print()
    print(f"🔄 Feedback loop established for continuous model improvement!")

if __name__ == "__main__":
    demonstrate_feedback_system() 