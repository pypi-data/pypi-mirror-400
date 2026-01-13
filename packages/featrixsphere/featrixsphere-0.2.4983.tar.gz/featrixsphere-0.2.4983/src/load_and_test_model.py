#!/usr/bin/env python3
"""
Tool to load and test models (predictors with embedded spaces).

Usage:
    python3 load_and_test_model.py <predictor_path|directory|session_id> [--test-record <json>] [--cpu-only]
    python3 load_and_test_model.py --embedding-space <es_path> [--test-record <json>] [--cpu-only]

The tool accepts:
    - Direct path to predictor pickle file
    - Directory containing a predictor (searches for single_predictor.pickle, etc.)
    - Session ID (loads session and finds predictor path)

Examples:
    # Load predictor by file path
    python3 load_and_test_model.py /sphere/app/featrix_output/.../single_predictor.pickle

    # Load predictor from directory (auto-finds single_predictor.pickle)
    python3 load_and_test_model.py /featrix-output/predictor-dot_model_20260105_5d3-02a8e524-5931-4344-8468-6c674e776c84/train_single_predictor_4e74b82e-ccef-486b-ba26-eab115c6a168/

    # Load predictor from session ID
    python3 load_and_test_model.py predictor-dot_model_20260105_5d3-02a8e524-5931-4344-8468-6c674e776c84

    # Load predictor and test with a record
    python3 load_and_test_model.py <path> --test-record '{"col1": "value1", "col2": 123}'

    # Force CPU-only mode
    python3 load_and_test_model.py <path> --cpu-only

    # Load just an embedding space (if no predictor available)
    python3 load_and_test_model.py --embedding-space /sphere/app/featrix_output/.../foundation_embedding_space.pickle
"""

import sys
import json
import argparse
import logging
import traceback
from pathlib import Path
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)-45s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def setup_paths():
    """Set up Python paths for imports."""
    current_path = Path(__file__).parent
    lib_path = current_path / "lib"
    
    if str(lib_path.resolve()) not in sys.path:
        sys.path.insert(0, str(lib_path.resolve()))
    if str(current_path.resolve()) not in sys.path:
        sys.path.insert(0, str(current_path.resolve()))
    
    logger.info(f"✅ Paths configured: lib={lib_path}, current={current_path}")

def find_predictor_in_directory(directory: Path) -> Optional[Path]:
    """Find predictor pickle file in a directory."""
    # Common predictor filenames to search for (in priority order)
    predictor_patterns = [
        "best_single_predictor.pickle",  # Symlink to canonical best model (highest priority)
        "single_predictor.pickle",  # Final saved model
        "predictor.pickle",
        "model.pickle",
        "*_best_single_predictor_auc_roc_*.pickle",  # Best ROC-AUC checkpoint (new format)
        "*_best_single_predictor_auc_pr_*.pickle",  # Best PR-AUC checkpoint (new format)
        "*_best_single_predictor_valloss_*.pickle",  # Best validation loss checkpoint (new format)
        "*_best_single_predictor_roc_auc*.pickle",  # Best ROC-AUC checkpoint (old format, for compatibility)
        "*_best_single_predictor_pr_auc*.pickle",  # Best PR-AUC checkpoint (old format, for compatibility)
        "*_best_single_predictor*_valloss_*.pickle",  # Best validation loss checkpoint (old format, for compatibility)
        "single_predictor_latest.pickle",
        "*_single_predictor_epoch_*.pickle",  # Epoch checkpoints
    ]
    
    for pattern in predictor_patterns:
        matches = list(directory.glob(pattern))
        if matches:
            # Sort by modification time, newest first
            matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            logger.info(f"🔍 Found predictor: {matches[0]} (pattern: {pattern})")
            return matches[0]
    
    # Also search recursively one level deep
    for subdir in directory.iterdir():
        if subdir.is_dir():
            for pattern in predictor_patterns:
                matches = list(subdir.glob(pattern))
                if matches:
                    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    logger.info(f"🔍 Found predictor: {matches[0]} (pattern: {pattern})")
                    return matches[0]
    
    return None

def resolve_predictor_path(input_path: str) -> Path:
    """Resolve predictor path from various inputs: file, directory, or session ID."""
    path_obj = Path(input_path)
    
    # If it's a file, return it
    if path_obj.is_file():
        logger.info(f"✅ Found predictor file: {path_obj}")
        return path_obj
    
    # If it's a directory, search for predictor inside
    if path_obj.is_dir():
        logger.info(f"🔍 Input is a directory, searching for predictor...")
        predictor = find_predictor_in_directory(path_obj)
        if predictor:
            return predictor
        else:
            raise FileNotFoundError(f"No predictor file found in directory: {input_path}")
    
    # Check if it might be a session ID
    setup_paths()  # Ensure paths are set up for imports
    try:
        from lib.session_manager import load_session, resolve_session_path
        from config import config
        
        # Try to load as session ID
        session_id = input_path
        session_path = config.output_dir / f"{session_id}.session"
        
        if session_path.exists():
            logger.info(f"🔍 Input appears to be a session ID, loading session...")
            session = load_session(session_id)
            
            # Try to find predictor path from session
            predictor_path = None
            
            # Check new format (multiple predictors)
            single_predictors = session.get("single_predictors")
            if single_predictors and isinstance(single_predictors, list) and single_predictors:
                predictor_path = single_predictors[0]  # Use first predictor
                logger.info(f"   Found predictor in single_predictors: {predictor_path}")
            
            # Check old format (single predictor)
            if not predictor_path:
                single_predictor = session.get("single_predictor")
                if single_predictor:
                    predictor_path = single_predictor
                    logger.info(f"   Found predictor in single_predictor: {predictor_path}")
            
            if predictor_path:
                # Resolve the path (handles relative/absolute/published paths)
                resolved = resolve_session_path(session_id, predictor_path)
                if resolved.exists():
                    logger.info(f"✅ Resolved predictor path from session: {resolved}")
                    return resolved
                else:
                    raise FileNotFoundError(f"Predictor path from session does not exist: {resolved}")
            else:
                raise FileNotFoundError(f"Session {session_id} does not contain a predictor path")
        else:
            # Not a file, not a directory, not a session - error
            raise FileNotFoundError(f"Path not found: {input_path} (not a file, directory, or session ID)")
    except ImportError as e:
        # If we can't import session_manager, just treat as file path error
        raise FileNotFoundError(f"Path not found: {input_path} (and cannot check if it's a session ID: {e})")
    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is
        raise
    except Exception as e:
        # Other errors - might not be a session ID, treat as file path error
        raise FileNotFoundError(f"Path not found: {input_path} (error checking session: {e})")

def load_embedding_space(es_path: str, force_cpu: bool = False):
    """Load the foundation embedding space."""
    logger.info(f"📦 Loading embedding space from: {es_path}")
    
    if not Path(es_path).exists():
        raise FileNotFoundError(f"Embedding space file not found: {es_path}")
    
    # Set CPU-only mode if requested
    if force_cpu:
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
        logger.info("🔧 Forcing CPU-only mode")
    
    from featrix.neural.io_utils import load_embedded_space
    
    es = load_embedded_space(es_path, force_cpu=force_cpu, skip_datasets=True)
    
    logger.info(f"✅ Embedding space loaded successfully")
    logger.info(f"   d_model: {es.d_model}")
    logger.info(f"   Columns: {list(es.col_codecs.keys())}")
    logger.info(f"   Number of codecs: {len(es.col_codecs)}")
    
    # Check device
    import torch
    if hasattr(es, 'encoder') and es.encoder is not None:
        device = next(es.encoder.parameters()).device if list(es.encoder.parameters()) else 'cpu'
        logger.info(f"   Encoder device: {device}")
    
    return es

def load_predictor(predictor_path: str, force_cpu: bool = False):
    """Load a single predictor - the ES is embedded in the predictor."""
    logger.info(f"📦 Loading predictor from: {predictor_path}")
    
    if not Path(predictor_path).exists():
        raise FileNotFoundError(f"Predictor file not found: {predictor_path}")
    
    import pickle
    
    # Set CPU-only mode if requested
    if force_cpu:
        import os
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        os.environ['FEATRIX_FORCE_CPU_SINGLE_PREDICTOR'] = '1'
    
    with open(predictor_path, 'rb') as f:
        fsp = pickle.load(f)
    
    logger.info(f"✅ Predictor loaded successfully")
    logger.info(f"   Target column: {getattr(fsp, 'target_col_name', 'Unknown')}")
    logger.info(f"   Target type: {getattr(fsp, 'target_col_type', 'Unknown')}")
    
    # Extract embedding space from predictor
    es = None
    if hasattr(fsp, 'embedding_space') and fsp.embedding_space is not None:
        es = fsp.embedding_space
        logger.info(f"✅ Embedding space found in predictor")
        logger.info(f"   d_model: {es.d_model}")
        logger.info(f"   Columns: {list(es.col_codecs.keys()) if hasattr(es, 'col_codecs') else 'N/A'}")
        logger.info(f"   Number of codecs: {len(es.col_codecs) if hasattr(es, 'col_codecs') else 'N/A'}")
    else:
        logger.warning(f"⚠️  No embedding space found in predictor")
    
    # Check device
    import torch
    if torch.cuda.is_available() and not force_cpu:
        logger.info("🔄 Hydrating to GPU...")
        fsp.hydrate_to_gpu_if_needed()
        if es is not None:
            es.hydrate_to_gpu_if_needed()
    else:
        logger.info("ℹ️  Model stays on CPU (CUDA not available or CPU-only mode)")
    
    return fsp, es

def test_encoding(es, test_record: dict):
    """Test encoding a record with the embedding space."""
    if es is None:
        logger.error("❌ No embedding space available for encoding test")
        return None
    
    logger.info(f"🧪 Testing encoding with record: {json.dumps(test_record, indent=2)}")
    
    try:
        encoding = es.encode_record(test_record, squeeze=False, short=False)
        logger.info(f"✅ Encoding successful")
        logger.info(f"   Encoding shape: {encoding.shape}")
        logger.info(f"   Encoding dtype: {encoding.dtype}")
        logger.info(f"   Encoding device: {encoding.device}")
        logger.info(f"   Encoding stats: min={encoding.min().item():.4f}, max={encoding.max().item():.4f}, mean={encoding.mean().item():.4f}")
        return encoding
    except Exception as e:
        logger.error(f"❌ Encoding failed: {e}")
        logger.error(traceback.format_exc())
        return None

def test_prediction(fsp, test_record: dict):
    """Test making a prediction with the predictor."""
    logger.info(f"🧪 Testing prediction with record: {json.dumps(test_record, indent=2)}")
    
    try:
        prediction_result = fsp.predict(test_record, debug_print=False, extended_result=True)
        
        logger.info(f"✅ Prediction successful")
        
        if isinstance(prediction_result, dict):
            results = prediction_result.get('results', {})
            if isinstance(results, dict):
                logger.info(f"   Prediction results:")
                for key, value in results.items():
                    logger.info(f"      {key}: {value}")
                
                # Find predicted class if classification
                if results:
                    predicted_class = max(results, key=results.get)
                    confidence = results[predicted_class]
                    logger.info(f"   Predicted class: {predicted_class} (confidence: {confidence:.4f})")
            else:
                logger.info(f"   Prediction value: {results}")
            
            # Show guardrails if present
            if 'guardrails' in prediction_result:
                guardrails = prediction_result['guardrails']
                logger.info(f"   Guardrails:")
                if guardrails.get('issues'):
                    logger.info(f"      Issues: {guardrails['issues']}")
                if guardrails.get('missing_columns'):
                    logger.info(f"      Missing columns: {guardrails['missing_columns']}")
                if guardrails.get('ignored_columns'):
                    logger.info(f"      Ignored columns: {guardrails['ignored_columns']}")
        else:
            logger.info(f"   Prediction result: {prediction_result}")
        
        return prediction_result
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        logger.error(traceback.format_exc())
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Load and test models (predictors with embedded spaces)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'predictor_path',
        type=str,
        nargs='?',
        default=None,
        help='Path to predictor pickle file, directory containing predictor, or session ID (contains embedded space)'
    )
    
    parser.add_argument(
        '--embedding-space',
        type=str,
        default=None,
        help='Path to embedding space pickle file (only if no predictor available)'
    )
    
    parser.add_argument(
        '--test-record',
        type=str,
        default=None,
        help='JSON string of test record to encode/predict (optional)'
    )
    
    parser.add_argument(
        '--cpu-only',
        action='store_true',
        help='Force CPU-only mode (no GPU)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.predictor_path and not args.embedding_space:
        parser.error("Either predictor_path or --embedding-space must be provided")
    
    if args.predictor_path and args.embedding_space:
        parser.error("Cannot specify both predictor_path and --embedding-space")
    
    try:
        # Set up paths
        setup_paths()
        
        fsp = None
        es = None
        
        # Load predictor (which contains the ES) or just ES
        if args.predictor_path:
            # Resolve predictor path (handles directories and session IDs)
            resolved_path = resolve_predictor_path(args.predictor_path)
            fsp, es = load_predictor(str(resolved_path), force_cpu=args.cpu_only)
            if es is None:
                logger.error("❌ Predictor does not contain an embedding space")
                sys.exit(1)
        elif args.embedding_space:
            es = load_embedding_space(args.embedding_space, force_cpu=args.cpu_only)
        
        # Test encoding if test record provided
        if args.test_record:
            try:
                test_record = json.loads(args.test_record)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in --test-record: {e}")
                sys.exit(1)
            
            # Test encoding
            encoding = test_encoding(es, test_record)
            
            # Test prediction if predictor loaded
            if fsp:
                prediction = test_prediction(fsp, test_record)
        
        logger.info("✅ Model loading and testing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()

