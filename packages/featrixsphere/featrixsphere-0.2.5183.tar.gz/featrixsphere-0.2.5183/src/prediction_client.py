"""
Prediction client for communicating with the persistent prediction server.

The prediction server keeps models loaded in GPU memory for fast inference.
This client provides a clean API for the main API server to use.
"""
import json
import logging
import urllib.request
import urllib.error
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default prediction server URL (localhost, same machine)
DEFAULT_PREDICTION_SERVER_URL = "http://127.0.0.1:8765"


class PredictionClient:
    """Client for the persistent prediction server."""
    
    def __init__(self, server_url: str = DEFAULT_PREDICTION_SERVER_URL, timeout: int = 300):
        self.server_url = server_url
        self.timeout = timeout
        self._healthy = None
    
    def is_healthy(self) -> bool:
        """Check if prediction server is available."""
        try:
            req = urllib.request.Request(f"{self.server_url}/health")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.getcode() == 200:
                    self._healthy = True
                    return True
        except (urllib.error.URLError, Exception) as e:
            logger.debug(f"Prediction server health check failed: {e}")
            self._healthy = False
        return False
    
    def get_cache_stats(self) -> Optional[dict]:
        """Get cache statistics from prediction server."""
        try:
            req = urllib.request.Request(f"{self.server_url}/health")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('cache_stats', {})
        except Exception:
            return None
    
    def get_health(self) -> dict:
        """Get full health info from prediction server."""
        try:
            req = urllib.request.Request(f"{self.server_url}/health")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                data['available'] = True
                return data
        except (urllib.error.URLError, Exception) as e:
            return {
                'available': False,
                'status': 'unavailable',
                'error': str(e)
            }
    
    def predict_batch(
        self,
        predictor_path: str,
        records: list,
        batch_size: int = 2500,
    ) -> dict:
        """
        Make batch predictions via the prediction server.
        
        Args:
            predictor_path: Path to the predictor pickle file
            records: List of record dicts to predict
            batch_size: Batch size for prediction
            
        Returns:
            dict with:
                - success: bool
                - predictions: list of prediction results (if success)
                - total_records: int
                - target_col_name: str - the target column name
                - target_col_type: str - the target column type (classification/regression)
                - model_quality_metrics: dict - confusion matrix, accuracy, etc.
                - cache_stats: dict
                - error: str (if not success)
                - traceback: str (if not success)
        """
        request_payload = {
            'predictor_path': predictor_path,
            'records': records,
            'batch_size': batch_size
        }
        
        try:
            req = urllib.request.Request(
                self.server_url,
                data=json.dumps(request_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"🚀 Calling prediction server: {len(records)} records, batch_size={batch_size}")
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                logger.info(f"✅ Prediction server completed: {result.get('total_records')} records")
            else:
                logger.error(f"❌ Prediction server error: {result.get('error')}")
            
            return result
            
        except urllib.error.URLError as e:
            logger.error(f"❌ Prediction server connection failed: {e}")
            return {
                'success': False,
                'error': f"Prediction server connection failed: {e}",
                'predictions': [],
                'total_records': 0
            }
        except Exception as e:
            logger.error(f"❌ Prediction client error: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions': [],
                'total_records': 0
            }


# Global client instance (lazy initialization)
_client: Optional[PredictionClient] = None


def get_client() -> PredictionClient:
    """Get or create the global prediction client."""
    global _client
    if _client is None:
        _client = PredictionClient()
    return _client


def predict_batch(
    predictor_path: str,
    records: list,
    batch_size: int = 2500,
) -> dict:
    """
    Convenience function for batch predictions.
    
    Uses the global prediction client instance.
    """
    return get_client().predict_batch(predictor_path, records, batch_size)


def is_prediction_server_available() -> bool:
    """Check if prediction server is running and healthy."""
    return get_client().is_healthy()


def get_prediction_server_health() -> dict:
    """Get full health info from prediction server."""
    return get_client().get_health()

