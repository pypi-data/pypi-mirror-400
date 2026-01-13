#!/usr/bin/env python3
"""
Persistent prediction server that keeps models loaded in memory/GPU.
Celery tasks communicate with this server via HTTP to avoid reloading models.
"""

import sys
import json
import logging
import traceback
import pickle
import time
from pathlib import Path
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)-45s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Set up Python paths
current_path = Path(__file__).parent
lib_path = current_path / "lib"

if str(lib_path.resolve()) not in sys.path:
    sys.path.insert(0, str(lib_path.resolve()))
if str(current_path.resolve()) not in sys.path:
    sys.path.insert(0, str(current_path.resolve()))

logger.info(f"✅ Paths configured: lib={lib_path}, current={current_path}")


class ModelCache:
    """LRU cache for loaded models with GPU memory management."""
    
    def __init__(self, max_size: int = 3):
        self.max_size = max_size
        self.cache = {}  # predictor_path -> (model, last_access_time)
        self.access_times = {}  # predictor_path -> access_time
        logger.info(f"💾 Model cache initialized (max_size={max_size})")
    
    def get(self, predictor_path: str):
        """Get a model from cache if available."""
        if predictor_path in self.cache:
            current_time = time.time()
            self.cache[predictor_path] = (self.cache[predictor_path][0], current_time)
            self.access_times[predictor_path] = current_time
            logger.info(f"✅ CACHE HIT: {Path(predictor_path).name}")
            return self.cache[predictor_path][0]
        logger.info(f"❌ CACHE MISS: {Path(predictor_path).name}")
        return None
    
    def put(self, predictor_path: str, model):
        """Add a model to cache, evicting LRU if needed."""
        current_time = time.time()
        
        # If cache is full, remove least recently used
        if len(self.cache) >= self.max_size and predictor_path not in self.cache:
            lru_path = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            logger.info(f"🗑️  CACHE EVICT: {Path(lru_path).name}")
            
            # Clean up GPU memory for evicted model
            try:
                evicted_model = self.cache[lru_path][0]
                if hasattr(evicted_model, 'cleanup_gpu_memory'):
                    evicted_model.cleanup_gpu_memory()
                    logger.info("✅ GPU memory cleaned for evicted model")
            except Exception as e:
                logger.warning(f"Failed to cleanup evicted model: {e}")
            
            del self.cache[lru_path]
            del self.access_times[lru_path]
        
        # Add new model to cache
        self.cache[predictor_path] = (model, current_time)
        self.access_times[predictor_path] = current_time
        logger.info(f"✅ CACHE ADD: {Path(predictor_path).name}")
    
    def stats(self):
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "cached_models": [Path(p).name for p in self.cache.keys()]
        }


# Global model cache
model_cache = ModelCache(max_size=3)


class PredictionRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for prediction requests."""
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_POST(self):
        """Handle POST requests for predictions and model card generation."""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            request_body = self.rfile.read(content_length)
            request_data = json.loads(request_body.decode('utf-8'))
            
            # Route to appropriate handler
            if self.path == '/generate_model_card':
                self._handle_generate_model_card(request_data)
                return
            
            predictor_path = request_data.get('predictor_path')
            records = request_data.get('records', [])
            batch_size = request_data.get('batch_size', 256)
            
            if not predictor_path or not records:
                self.send_error(400, "Missing predictor_path or records")
                return
            
            logger.info(f"🔍 Prediction request: {len(records)} records for {Path(predictor_path).name}")
            
            # Load or get cached model
            fsp = model_cache.get(predictor_path)
            
            if fsp is None:
                logger.info(f"📦 Loading model from: {predictor_path}")
                
                # Import torch here (after fork)
                import torch
                
                # Load the model
                with open(predictor_path, 'rb') as f:
                    fsp = pickle.load(f)
                
                # Hydrate to GPU if available
                if torch.cuda.is_available():
                    logger.info("🔄 Hydrating to GPU...")
                    fsp.hydrate_to_gpu_if_needed()
                    if hasattr(fsp, 'embedding_space') and fsp.embedding_space is not None:
                        fsp.embedding_space.hydrate_to_gpu_if_needed()
                    
                    gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024
                    logger.info(f"🖥️  GPU Memory: {gpu_memory_mb:.1f}MB")
                
                # Cache the model
                model_cache.put(predictor_path, fsp)
            
            # Make predictions
            logger.info(f"🚀 Running batch prediction...")
            predictions = fsp.predict_batch(
                records,
                batch_size=batch_size,
                debug_print=False,
                extended_result=True
            )
            
            logger.info(f"✅ Completed {len(predictions)} predictions")
            
            # Extract model metadata that API needs
            target_col_name = getattr(fsp, 'target_col_name', None)
            target_col_type = getattr(fsp, 'target_col_type', None)
            
            # Load training metrics if available
            model_quality_metrics = None
            try:
                metrics_path = Path(predictor_path).parent / "training_metrics.json"
                if metrics_path.exists():
                    with open(metrics_path) as f:
                        metrics_data = json.load(f)
                        model_quality_metrics = metrics_data.get("quality_metrics", {})
                        if model_quality_metrics:
                            logger.info("✅ Loaded model quality metrics")
            except Exception as metrics_error:
                logger.warning(f"Could not load training metrics: {metrics_error}")
            
            # Build response with all metadata API needs
            response_data = {
                'success': True,
                'predictions': predictions,
                'total_records': len(records),
                'target_col_name': target_col_name,
                'target_col_type': target_col_type,
                'model_quality_metrics': model_quality_metrics,
                'cache_stats': model_cache.stats()
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            logger.error(traceback.format_exc())
            
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def _handle_generate_model_card(self, request_data):
        """Generate model card for a session using loaded model."""
        try:
            session_id = request_data.get('session_id')
            predictor_path = request_data.get('predictor_path')
            output_dir = request_data.get('output_dir')
            
            if not predictor_path or not output_dir:
                self.send_error(400, "Missing predictor_path or output_dir")
                return
            
            logger.info(f"📋 Model card request for: {session_id}")
            
            # Load or get cached model
            fsp = model_cache.get(predictor_path)
            
            if fsp is None:
                logger.info(f"📦 Loading model for model card: {predictor_path}")
                import torch
                
                with open(predictor_path, 'rb') as f:
                    fsp = pickle.load(f)
                
                if torch.cuda.is_available():
                    fsp.hydrate_to_gpu_if_needed()
                    if hasattr(fsp, 'embedding_space') and fsp.embedding_space is not None:
                        fsp.embedding_space.hydrate_to_gpu_if_needed()
                
                model_cache.put(predictor_path, fsp)
            
            # Generate model card
            if hasattr(fsp, '_create_model_card_json'):
                model_card = fsp._create_model_card_json()
                
                # Save to disk
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                card_path = output_path / "model_card.json"
                
                with open(card_path, 'w') as f:
                    json.dump(model_card, f, indent=2, default=str)
                
                logger.info(f"✅ Model card saved: {card_path}")
                
                response = {
                    'success': True,
                    'model_card_path': str(card_path),
                    'session_id': session_id
                }
            else:
                response = {
                    'success': False,
                    'error': 'Model does not have _create_model_card_json method'
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"❌ Model card generation failed: {e}")
            logger.error(traceback.format_exc())
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests for health check and stats."""
        if self.path == '/health':
            response = {
                'status': 'healthy',
                'cache_stats': model_cache.stats()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_error(404, "Not found")


def run_server(host='127.0.0.1', port=8765):
    """Run the prediction server."""
    logger.info(f"🚀 Starting prediction server on {host}:{port}")
    
    # Use ThreadingMixIn for concurrent requests
    class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
        daemon_threads = True
    
    server = ThreadedHTTPServer((host, port), PredictionRequestHandler)
    
    logger.info(f"✅ Prediction server ready - listening on http://{host}:{port}")
    logger.info(f"💾 Model cache size: {model_cache.max_size} models")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down prediction server...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Persistent prediction server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8765, help='Port to bind to')
    parser.add_argument('--cache-size', type=int, default=3, help='Max models to cache')
    
    args = parser.parse_args()
    
    # Update cache size if specified
    if args.cache_size != 3:
        model_cache.max_size = args.cache_size
        logger.info(f"💾 Model cache size set to: {args.cache_size}")
    
    run_server(host=args.host, port=args.port)

