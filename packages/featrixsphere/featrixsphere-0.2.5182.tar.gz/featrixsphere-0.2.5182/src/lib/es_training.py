#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import copy
import json
import logging
import os
import socket
import sys
import traceback

# CRITICAL: Redirect stderr to stdout IMMEDIATELY so all errors/crashes go to one log
sys.stderr = sys.stdout
print("🔧 STDERR REDIRECTED TO STDOUT - all output in one place!", flush=True)

import pickle
import tempfile
import shutil
import json
import socket
import time
import sys

from datetime import datetime
from zoneinfo import ZoneInfo

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects, Pydantic models, and other non-serializable types."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Handle Pydantic BaseModel instances
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # Handle objects with __dict__ (fallback for custom classes)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        # Handle objects with a dict() method
        if hasattr(obj, 'dict') and callable(obj.dict):
            try:
                return obj.dict()
            except Exception:
                pass
        # Last resort: convert to string
        try:
            return str(obj)
        except Exception:
            return f"<non-serializable: {type(obj).__name__}>"


def sanitize_datetime_for_json(obj):
    """
    Recursively convert datetime objects, Pydantic models, and other non-serializable types
    to JSON-serializable formats. Handles nested dicts, lists, and tuples.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, BaseModel):
        # Pydantic models: use model_dump()
        return sanitize_datetime_for_json(obj.model_dump())
    elif isinstance(obj, dict):
        return {key: sanitize_datetime_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(sanitize_datetime_for_json(item) for item in obj)
    elif hasattr(obj, '__dict__'):
        # Custom objects with __dict__
        return sanitize_datetime_for_json(obj.__dict__)
    elif hasattr(obj, 'dict') and callable(obj.dict):
        # Objects with dict() method (old Pydantic style)
        try:
            return sanitize_datetime_for_json(obj.dict())
        except Exception:
            return str(obj)
    else:
        return obj

# Set up Python path for featrix imports
try:
    from featrix.neural.logging_config import configure_logging
except ModuleNotFoundError:
    # Add current directory to path for featrix imports
    p = Path(__file__).parent
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
    
    try:
        from featrix.neural.logging_config import configure_logging
    except ModuleNotFoundError:
        # Fallback to basic logging if module not found
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)-8s] %(name)-45s: %(message)s'
        )
        def configure_logging():
            pass

configure_logging()
logger = logging.getLogger(__name__)

try:
    from featrix.neural import device
except ModuleNotFoundError:
    p = Path(__file__).parent
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

    from featrix.neural import device

from featrix.neural.embedded_space import EmbeddingSpace, check_abort_and_raise
from featrix.neural.input_data_file import FeatrixInputDataFile
from featrix.neural.input_data_set import FeatrixInputDataSet

from featrix.neural.gpu_utils import (
    get_device,
    is_gpu_available,
    get_gpu_memory_summary,
    get_gpu_current_device_id,
    empty_gpu_cache,
    synchronize_gpu,
)
device = get_device()  # Get device once at module level
from featrix.neural.utils import ideal_batch_size, ideal_epochs_embedding_space

from lib.job_manager import load_job, save_job, update_job_status, JobStatus
from lib.session_manager import load_session
from config import config
from featrix.neural.training_exceptions import TrainingFailureException
from featrix.neural.exceptions import FeatrixRestartTrainingException, FeatrixTrainingAbortedException, RestartConfig

# Add parent directory to path for slack, version, and training_monitor imports
# es_training.py is in src/lib/, so we need to add src/ to path
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from slack import send_slack_message, get_hostname
from version import get_version, print_version_banner
from lib.training_monitor import post_training_progress, collect_es_training_data, post_training_data
from lib.meta_learning_client import mark_config_training_started, get_dataset_characteristics, log_training_metadata_v2

from featrix.neural.io_utils import load_embedded_space
from featrix.neural.utils import ideal_batch_size
from sklearn.model_selection import KFold, train_test_split


# ADD IMPORT FOR EPOCH PROJECTIONS
# CRITICAL: Check if we're in a DataLoader worker process - if so, don't log anything
# Workers are spawned frequently and logging here causes massive log spam
_is_dataloader_worker = os.environ.get('PYTORCH_DATALOADER_WORKER') == '1'

try:
    from lib.epoch_projections import EpochProjectionCallback, generate_epoch_projections, create_projection_movie_metadata
    EPOCH_PROJECTIONS_AVAILABLE = True
    # Don't log this - it's imported by every worker process and creates log spam
    # The import either works or it doesn't (we'll see a warning if it fails)
    # CRITICAL: Never log during import - workers spawn constantly and this creates spam
except ImportError as e:
    # Only log warnings if NOT in a DataLoader worker (workers spawn constantly)
    if not _is_dataloader_worker:
        logger.warning(f"⚠️ Epoch projections not available: {e}")
        logger.warning("ℹ️  Training will proceed without movie generation")
    EPOCH_PROJECTIONS_AVAILABLE = False
    # Create dummy classes/functions to avoid errors
    class EpochProjectionCallback:
        def __init__(self, *args, **kwargs):
            logger.warning("🎬 Epoch projections disabled - using dummy callback")
            pass
        def __call__(self, *args, **kwargs):
            pass
    def generate_epoch_projections(*args, **kwargs):
        pass
    def create_projection_movie_metadata(*args, **kwargs):
        return {'movie_ready': False, 'total_epochs': 0, 'output_directory': ''}

# Note: Logger was defined earlier after configure_logging()


# Removed test debug messages


for noisy in [
    "aiobotocore",
    "asyncio",
    "botocore",
    "com",
    "fastapi",
    "dotenv",
    "concurrent",
    "aiohttp",
    "filelock",
    "fsspec",
    "httpcore",
    "httpx",
    "requests",
    "s3fs",
    "tornado",
    "twilio",
    "urllib3",
    "com.supertokens",
    "kombu.pidbox"
]:
    logging.getLogger(noisy).setLevel(logging.WARNING)


def _emergency_cleanup_before_exit():
    """
    CRITICAL: Kill all child processes (DataLoader workers) BEFORE any logging.
    
    When an OOM error occurs, the DataLoader workers may crash. If we try to log
    before killing them, the logging can block forever on a pipe to a dead worker
    whose buffer is full. This causes the process to hang indefinitely with zombie
    children, never actually exiting and holding GPU memory.
    
    Call this FIRST thing in any fatal error handler, BEFORE any logging!
    
    This function:
    1. Kills all child processes immediately (terminate, then kill)
    2. Flushes stdout to ensure we're not blocked on a buffer
    3. Uses only direct sys.stdout.write() - no logging (which could block)
    """
    import signal
    
    # 1. Kill all child processes IMMEDIATELY - don't wait for graceful shutdown
    try:
        import psutil
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        
        if children:
            # Use sys.stdout.write directly - logger.error() could block on dead worker pipes!
            sys.stdout.write(f"⚠️  EMERGENCY CLEANUP: Killing {len(children)} child processes before exit\n")
            sys.stdout.flush()
            
            # Send SIGTERM first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            
            # Give them 1 second to die
            _, alive = psutil.wait_procs(children, timeout=1)
            
            # Force kill any survivors
            for child in alive:
                try:
                    if child.is_running():
                        sys.stdout.write(f"   Force killing PID {child.pid}\n")
                        child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            # Wait another second for force kills
            psutil.wait_procs(alive, timeout=1)
            
            sys.stdout.write(f"   ✅ Child processes terminated\n")
            sys.stdout.flush()
    except ImportError:
        pass  # psutil not available
    except Exception as e:
        # Don't let cleanup errors prevent exit
        sys.stdout.write(f"   ⚠️  Cleanup error (non-fatal): {e}\n")
        sys.stdout.flush()
    
    # 2. Flush all output buffers
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except:
        pass


#sys.path.append(".")

class LightTrainingArgs(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Allow fields starting with "model_" to avoid Pydantic warnings
    
    epochs: int = 0
    batch_size: int = 0  # 0 = auto-calculate based on dataset size and GPU
    learning_rate: Optional[float] = None  # None = auto-select based on training phase
    row_limit: int = 1_000_000
    is_production: bool = True
    input_file: str = "test.csv"
    ignore_cols: List[str] = []
    job_id: str = "no_job_id"
    job_queue: str = "train_es"
    string_cache: str = None
    session_id: str = None
    name: str = None  # Name for the embedding space
    parent_embedding_space_path: str = None  # Path to parent embedding space for fine-tuning
    
    # VISUALIZATION ONLY: Prefer rows with non-null values in these columns for epoch projections
    # ⚠️ IMPORTANT: Has NO EFFECT on model training, only affects visualization sampling
    important_columns_for_visualization: List[str] = []
        
    # JSON transformation metadata from create_structured_data
    json_transformations: dict = {}
    
    # Column overrides from create_structured_data
    column_overrides: dict = {}
    
    # User metadata - arbitrary dict for user identification (max 32KB when serialized)
    user_metadata: Optional[dict] = None
    
    # Resume training from a specific epoch (used in K-fold CV to track cumulative epochs)
    resume_from_epoch: Optional[int] = None
    
    # Never load/resume from checkpoints - always start fresh (useful for QA tests)
    disable_recovery: bool = False
    
    # Gradient clipping parameters (optional - defaults used if not provided)
    max_grad_norm: Optional[float] = None  # None = use default (20.0) in training
    adaptive_grad_clip_ratio: Optional[float] = None  # None = use default (2.0) in training
    grad_clip_warning_multiplier: Optional[float] = None  # None = use default (5.0) in training


# validate_user_metadata moved to lib.utils to avoid circular import with featrix_queue
from lib.utils import validate_user_metadata


def write_embedded_space(es, local_path: str):
    """
    Save embedding space as pickle file.
    Wrapper around write_embedding_space_pickle for backward compatibility.
    """
    from featrix.neural.embedding_space_utils import write_embedding_space_pickle
    write_embedding_space_pickle(es, local_path)
    return


def get_es_detailed_info(client, session_id):
    """
    Get detailed information about a trained embedding space from the FeatrixSphere API.
    
    Args:
        client: FeatrixSphere client
        session_id: Session ID
        
    Returns:
        dict: Detailed ES information including model stats
    """
    try:
        # Get session info to find ES details
        session_info = client._get_json(f"/compute/session/{session_id}")
        
        es_info = {}
        
        # Extract embedding space ID
        es_info['es_id'] = session_info.get('embedding_space_id') or session_info.get('es_id')
        es_info['status'] = session_info.get('status')
        es_info['trained_at'] = session_info.get('trained_at')
        
        # Extract model architecture info
        model_info = session_info.get('model_info', {}) or session_info.get('embedding_space', {})
        es_info['parameter_count'] = model_info.get('parameter_count') or model_info.get('num_parameters')
        es_info['layer_count'] = model_info.get('layer_count') or model_info.get('num_layers')
        es_info['d_model'] = model_info.get('d_model') or model_info.get('embedding_dim')
        
        # Extract training statistics
        training_stats = session_info.get('training_stats', {}) or session_info.get('stats', {})
        es_info['final_epoch'] = training_stats.get('final_epoch') or training_stats.get('epochs_trained')
        es_info['final_loss'] = training_stats.get('final_loss') or training_stats.get('loss')
        es_info['final_val_loss'] = training_stats.get('final_val_loss') or training_stats.get('validation_loss')
        es_info['training_time_seconds'] = training_stats.get('training_time') or training_stats.get('elapsed_seconds')
        
        # Get column types from the session
        column_info = session_info.get('columns', {}) or session_info.get('column_types', {})
        if column_info:
            es_info['column_types'] = column_info
        
        # Get encoding information
        encoding_info = session_info.get('encoding', {}) or session_info.get('encodings', {})
        if encoding_info:
            es_info['column_encodings'] = encoding_info
            
        # Get training host/cluster info
        es_info['training_cluster'] = session_info.get('cluster') or session_info.get('compute_cluster')
        es_info['training_host'] = session_info.get('host') or session_info.get('compute_host')
        
        return es_info
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to get detailed ES info: {e}")
        return {}


def save_es_metadata(
    session_id,
    epochs=None,  # None = use from args or session, 0 = auto-calculate
    training_response=None,
    csv_file=None,
    client=None,
    training_start_time=None,
    es=None
):
    """
    Save comprehensive embedding space training metadata to a JSON file for future reference.
    
    This captures all critical information about the trained embedding space including:
    - Model architecture (parameter count, layer count, d_model)
    - Training statistics (final loss, validation loss, etc.)
    - Column types and encodings
    - Training environment details
    
    Args:
        session_id: FeatrixSphere session ID
        epochs: Number of training epochs requested
        training_response: Initial training API response
        csv_file: Source CSV file path
        client: FeatrixSphere client (for fetching detailed stats)
        training_start_time: When training started (timestamp)
        es: EmbeddingSpace instance (for local model info)
        
    Returns:
        str: Path to saved metadata file
    """
    try:
        # Convert training_start_time to ISO format string if it's a datetime object
        if isinstance(training_start_time, datetime):
            start_time_str = training_start_time.isoformat()
        elif training_start_time:
            start_time_str = training_start_time
        else:
            start_time_str = datetime.now().isoformat()
        
        # Basic metadata
        metadata = {
            "session_id": session_id,
            "epochs_requested": epochs,
            "started_at": start_time_str,
            "completed_at": datetime.now().isoformat(),
            "training_response": training_response,
            "source_csv": csv_file,
            "status": "completed",
            "metadata_version": "2.0",
            "training_type": "embedding_space"
        }
        
        # Add training host information
        try:
            metadata['training_client_host'] = socket.gethostname()
            metadata['training_client_fqdn'] = socket.getfqdn()
        except Exception:
            pass
        
        # Calculate training time if we have start time
        if training_start_time:
            try:
                start_dt = datetime.fromisoformat(training_start_time) if isinstance(training_start_time, str) else training_start_time
                end_dt = datetime.now()
                metadata['training_duration_seconds'] = (end_dt - start_dt).total_seconds()
            except Exception:
                pass
        
        # Get local model info from EmbeddingSpace if available
        if es:
            try:
                # Add name if available
                if hasattr(es, 'name') and es.name:
                    metadata['name'] = es.name
                
                # Count layers and parameters with detailed breakdown
                linear_count = 0
                batchnorm_count = 0
                dropout_count = 0
                activation_count = 0
                other_count = 0
                total_leaf_modules = 0
                param_count = 0
                
                if hasattr(es, 'encoder'):
                    for name, module in es.encoder.named_modules():
                        if len(list(module.children())) == 0:  # Leaf modules only
                            total_leaf_modules += 1
                            
                            # Categorize the module type
                            module_type = type(module).__name__
                            if 'Linear' in module_type:
                                linear_count += 1
                            elif 'BatchNorm' in module_type or 'LayerNorm' in module_type:
                                batchnorm_count += 1
                            elif 'Dropout' in module_type:
                                dropout_count += 1
                            elif 'ReLU' in module_type or 'LeakyReLU' in module_type or 'GELU' in module_type or 'Tanh' in module_type:
                                activation_count += 1
                            else:
                                other_count += 1
                    
                    # Count parameters
                    param_count = es.model_param_count if hasattr(es, 'model_param_count') else sum(p.numel() for p in es.encoder.parameters())
                
                metadata['parameter_count'] = param_count
                metadata['total_leaf_modules'] = total_leaf_modules
                metadata['linear_layers'] = linear_count
                metadata['norm_layers'] = batchnorm_count
                metadata['dropout_layers'] = dropout_count
                metadata['activation_layers'] = activation_count
                metadata['other_layers'] = other_count
                # Keep layer_count for backward compatibility
                metadata['layer_count'] = total_leaf_modules
                metadata['d_model'] = es.d_model if hasattr(es, 'd_model') else None
                metadata['num_columns'] = len(es.availableColumns) if hasattr(es, 'availableColumns') else None
                
                # Get training info if available
                if hasattr(es, 'training_info') and es.training_info:
                    metadata['training_info'] = es.training_info
                
                # Get version info if available
                if hasattr(es, 'version_info') and es.version_info:
                    metadata['version_info'] = es.version_info
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not extract local ES info: {e}")
        
        # Get detailed ES information from API if client provided
        if client:
            try:
                detailed_info = get_es_detailed_info(client, session_id)
                # Merge API info (don't override local info if it exists)
                for key, value in detailed_info.items():
                    if key not in metadata or metadata[key] is None:
                        metadata[key] = value
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch detailed ES info from API: {e}")
        
        # Save to local metadata directory
        metadata_dir = Path("es_metadata")
        metadata_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_file = metadata_dir / f"{session_id}_es_{timestamp}.json"
        
        # Sanitize metadata to ensure all datetime objects are converted to strings
        sanitized_metadata = sanitize_datetime_for_json(metadata)
        
        with open(metadata_file, 'w') as f:
            json.dump(sanitized_metadata, f, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"📝 ES Metadata saved to: {metadata_file}")
        logger.info(f"   - Session ID: {session_id}")
        if 'es_id' in metadata:
            logger.info(f"   - Embedding space ID: {metadata['es_id']}")
        if 'parameter_count' in metadata:
            param_count = metadata['parameter_count']
            # Handle case where parameter_count might be a dict, None, or a number
            if isinstance(param_count, (int, float)):
                logger.info(f"   - Parameter count: {param_count}")
            elif param_count is not None:
                logger.info(f"   - Parameter count: {param_count}")
        if 'layer_count' in metadata:
            # Show detailed layer breakdown if available
            if 'linear_layers' in metadata:
                logger.info(f"   - Network architecture:")
                logger.info(f"      • Linear (trainable) modules: {metadata['linear_layers']}")
                logger.info(f"      • Normalization modules: {metadata['norm_layers']}")
                logger.info(f"      • Dropout modules: {metadata['dropout_layers']}")
                logger.info(f"      • Activation modules: {metadata['activation_layers']}")
                if metadata.get('other_layers', 0) > 0:
                    logger.info(f"      • Other modules: {metadata['other_layers']}")
                logger.info(f"      • Total leaf modules: {metadata['layer_count']}")
                logger.info(f"      • Approximate layer groups: ~{metadata['linear_layers']} (Linear+Norm+Dropout+Activation counted as 1)")
            else:
                # Backward compatibility - just show total
                layer_count = metadata['layer_count']
                if isinstance(layer_count, (int, float)):
                    logger.info(f"   - Layer count: {layer_count}")
                elif layer_count is not None:
                    logger.info(f"   - Layer count: {layer_count}")
        if 'd_model' in metadata:
            d_model = metadata['d_model']
            if isinstance(d_model, (int, float)):
                logger.info(f"   - Embedding dimension (d_model): {d_model}")
            elif d_model is not None:
                logger.info(f"   - Embedding dimension (d_model): {d_model}")
        if 'num_columns' in metadata:
            num_cols = metadata['num_columns']
            if isinstance(num_cols, (int, float)):
                logger.info(f"   - Number of columns: {num_cols}")
            elif num_cols is not None:
                logger.info(f"   - Number of columns: {num_cols}")
        if 'final_val_loss' in metadata:
            final_val_loss = metadata['final_val_loss']
            if isinstance(final_val_loss, (int, float)):
                logger.info(f"   - Final validation loss: {final_val_loss}")
            elif final_val_loss is not None:
                logger.info(f"   - Final validation loss: {final_val_loss}")
        if 'training_duration_seconds' in metadata:
            duration = metadata['training_duration_seconds']
            if isinstance(duration, (int, float)):
                logger.info(f"   - Training time: {duration}s")
            elif duration is not None:
                logger.info(f"   - Training time: {duration}")
        
        return str(metadata_file)
    except Exception as e:
        logger.error(f"⚠️ Failed to save ES metadata: {e}")
        traceback.print_exc()
        return None


def check_gpu_memory_preflight(min_free_gb: float = 10.0):
    """
    Check GPU memory before starting training to prevent OOM errors.
    
    This function:
    1. Logs current GPU memory state (global and process-specific)
    2. Warns if memory is low (< 20GB free)
    3. Raises RuntimeError if insufficient memory (< min_free_gb) to start training
    
    Args:
        min_free_gb: Minimum free GPU memory required to start training (default: 10.0 GB)
    
    Raises:
        RuntimeError: If GPU memory is insufficient to start training
    """
    logger = logging.getLogger(__name__)
    
    if not is_gpu_available():
        return
    
    try:
        import torch
        free_mem, total_mem = torch.cuda.mem_get_info()
        free_gb = free_mem / (1024**3)
        total_gb = total_mem / (1024**3)
        used_gb = total_gb - free_gb
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        
        logger.info(f"=" * 80)
        logger.info(f"📊 GPU MEMORY CHECK [pre-flight - CRITICAL]")
        logger.info(f"   Global GPU state: {used_gb:.1f}GB used / {total_gb:.1f}GB total ({free_gb:.1f}GB free)")
        logger.info(f"   This process: {allocated:.3f}GB allocated, {reserved:.3f}GB reserved")
        
        # Warn if less than 20GB free - something is likely wrong
        if free_gb < 20.0:
            logger.warning(f"   ⚠️  LOW GPU MEMORY: Only {free_gb:.1f}GB free!")
            logger.warning(f"   ⚠️  This process has {allocated:.3f}GB - another process may be using {used_gb - allocated:.1f}GB")
            logger.warning(f"   ⚠️  Check nvidia-smi for stuck/zombie training processes")
        logger.info(f"=" * 80)
        
        # Check if we have enough memory to start training
        if free_gb < min_free_gb:
            logger.error(f"=" * 80)
            logger.error(f"❌ GPU MEMORY EXHAUSTED - CANNOT START TRAINING")
            logger.error(f"=" * 80)
            logger.error(f"   Total GPU memory: {total_gb:.1f} GB")
            logger.error(f"   Used by other processes: {used_gb:.1f} GB")
            logger.error(f"   Free: {free_gb:.1f} GB")
            logger.error(f"   Minimum required: {min_free_gb:.1f} GB")
            logger.error(f"")
            logger.error(f"   ⚠️  Another training job is likely still running!")
            logger.error(f"   Check with: nvidia-smi")
            logger.error(f"   Wait for it to complete, or kill it if stuck.")
            logger.error(f"=" * 80)
            raise RuntimeError(
                f"GPU memory exhausted: only {free_gb:.1f}GB free of {total_gb:.1f}GB total. "
                f"Another process is using {used_gb:.1f}GB. Wait for it to complete or kill it."
            )
        else:
            logger.info(f"✅ GPU memory check: {free_gb:.1f}GB free / {total_gb:.1f}GB total ({used_gb:.1f}GB used by other processes)")
    except Exception as mem_check_err:
        logger.warning(f"⚠️  Could not check GPU memory: {mem_check_err}")


def save_embedding_space_and_package(es, output_dir: str = None):
    """
    Save embedding space to disk and ensure model package is created.
    
    This function:
    1. Saves the embedding space pickle file
    2. Creates model package if it doesn't exist
    3. Handles disk space errors by raising FeatrixRestartTrainingException
    
    Args:
        es: EmbeddingSpace instance to save
        output_dir: Directory to save to (default: current working directory)
    
    Returns:
        str: Path to saved embedding space pickle file
    
    Raises:
        FeatrixRestartTrainingException: If disk space error occurs (retryable)
        OSError: For other OS errors
    """
    logger = logging.getLogger(__name__)
    
    if output_dir is None:
        output_dir = os.getcwd()
    
    logger.info(f"💾 Saving embedding space to current directory: {output_dir}")
    try:
        from featrix.neural.embedding_space_utils import write_embedding_space_pickle
        embedding_space_path = write_embedding_space_pickle(es, output_dir, show_progress=True)
        logger.info(f"💾 Final embedding space saved to {embedding_space_path}")
        
        # Ensure model package is created if it doesn't exist
        package_dir = Path(output_dir) / "best_model_package"
        model_card_path = package_dir / "model_card.json"
        if not model_card_path.exists():
            logger.info(f"📦 Model package not found, creating it now...")
            try:
                # Get best epoch index
                best_epoch_idx = getattr(es, 'best_epoch_idx', None)
                if best_epoch_idx is None and hasattr(es, 'training_info'):
                    # Try to find best epoch from training info
                    progress_info = es.training_info.get('progress_info', {})
                    loss_history = progress_info.get('loss_history', [])
                    if loss_history:
                        best_val_loss = float('inf')
                        best_epoch_idx = 0
                        for i, entry in enumerate(loss_history):
                            val_loss = entry.get('val_loss')
                            if val_loss and val_loss < best_val_loss:
                                best_val_loss = val_loss
                                best_epoch_idx = i
                    else:
                        # Fallback to last epoch
                        best_epoch_idx = len(loss_history) - 1 if loss_history else 0
                
                if best_epoch_idx is not None:
                    logger.info(f"   Creating model package with best epoch: {best_epoch_idx}")
                    es._create_model_package(best_epoch_idx)
                    logger.info(f"✅ Model package created successfully")
                else:
                    logger.warning(f"⚠️  Could not determine best epoch index, skipping model package creation")
            except Exception as package_err:
                logger.warning(f"⚠️  Failed to create model package: {package_err}")
                logger.debug(traceback.format_exc())
        
        return embedding_space_path
    except OSError as e:
        # Check if it's a disk space error - convert to retryable exception
        if e.errno == 28 or "No space left on device" in str(e) or "No space" in str(e):
            logger.error(f"❌ Disk space error while saving embedding space: {e}")
            logger.error(f"   This is a retryable error - job will be restarted when disk space is available")
            # Convert to FeatrixRestartTrainingException so job can be retried
            restart_config = RestartConfig(
                reason="DISK_SPACE_ERROR",
                epoch_detected=getattr(es, 'current_epoch', 0) if hasattr(es, 'current_epoch') else 0,
                lr_multiplier=1.0,  # Don't change LR for disk space errors
                reset_optimizer_state=False,  # Don't reset optimizer
                reset_scheduler=False,
                load_best_checkpoint=False,
                metadata={"error": str(e), "output_dir": output_dir}
            )
            raise FeatrixRestartTrainingException(f"Disk space error: {e}", restart_config) from e
        raise


def generate_and_register_dataset_hash(es, train_input_data):
    """
    Generate dataset_hash and register column pairs with monitor (early, for progress tracking).
    
    This is done early in training for progress tracking, before post_training_data_to_monitor.
    If dataset_hash already exists, this function does nothing.
    
    Args:
        es: EmbeddingSpace instance (will store _dataset_hash attribute)
        train_input_data: Training input data object with .df attribute
    
    Returns:
        str or None: The dataset_hash if generated, None otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check if dataset_hash already exists
    if hasattr(es, '_dataset_hash') and es._dataset_hash is not None:
        return es._dataset_hash
    
    try:
        from featrix_monitor import generate_dataset_hash, create_client
        dataset_hash = generate_dataset_hash(train_input_data.df)
        es._dataset_hash = dataset_hash
        logger.info(f"📊 Generated dataset_hash: {dataset_hash}")
        
        # Register all possible column pairs with monitor (idempotent)
        try:
            client = create_client()
            column_names = list(train_input_data.df.columns)
            result = client.register_pair_columns(
                dataset_hash=dataset_hash,
                columns=column_names
            )
            logger.info(f"📊 Registered {result['total_pairs']} possible pairs with monitor:")
            logger.info(f"   {result['pairs_created']} new pairs created, {result['pairs_existing']} already existed")
        except Exception as reg_err:
            logger.warning(f"⚠️  Failed to register pair columns with monitor: {reg_err}")
            # Don't fail training if monitor registration fails
        
        return dataset_hash
    except Exception as hash_err:
        logger.warning(f"⚠️  Failed to generate dataset_hash: {hash_err}")
        return None


def post_training_data_to_monitor(
    es,
    train_input_data,
    val_input_data,
    training_start_time,
    training_end_time,
    epochs,
    batch_size,
    args: LightTrainingArgs
):
    """
    Post training data to monitor.featrix.com and log to meta-learning API.
    
    This function:
    1. Generates dataset_hash if not already set
    2. Registers column pairs with monitor
    3. Collects and posts training data to monitor
    4. Logs training metadata to meta-learning API
    
    Args:
        es: EmbeddingSpace instance
        train_input_data: Training input data object with .df attribute
        val_input_data: Validation input data object with .df attribute
        training_start_time: Start time of training
        training_end_time: End time of training
        epochs: Number of epochs trained
        batch_size: Batch size used
        args: LightTrainingArgs instance with training configuration
    
    Note:
        This function catches all exceptions and logs warnings - it never fails training.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("="*80)
        logger.info("📊 POSTING ES TRAINING DATA TO MONITOR")
        logger.info("="*80)
        
        # Get session_id from args (prefer session_id, fallback to job_id)
        session_id = getattr(args, 'session_id', None) or getattr(args, 'job_id', None)
        
        # Generate and store dataset_hash if not already set (uses helper to avoid duplication)
        dataset_hash = generate_and_register_dataset_hash(es, train_input_data)
        
        # Build optimal_params from embedding_space
        optimal_params = {
            "d_model": getattr(es, 'd_model', None),
            "n_transformer_layers": getattr(es, 'n_transformer_layers', None),
            "n_attention_heads": getattr(es, 'n_attention_heads', None),
        }
        
        training_data = collect_es_training_data(
            embedding_space=es,
            train_df=train_input_data.df,
            val_df=val_input_data.df,
            training_start_time=training_start_time,
            training_end_time=training_end_time,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=args.learning_rate if args.learning_rate is not None else 0.001,  # Default LR if not specified
            customer_id=getattr(args, 'customer_id', None),
            remote_hostname=getattr(args, 'remote_hostname', None),
            s3_path=getattr(args, 's3_path', None),
            session_id=session_id,
            deployment_id=getattr(args, 'deployment_id', None),
            optimal_params=optimal_params,
        )
        
        # Add dataset_hash to training_data metadata if we got it
        if dataset_hash:
            if 'metadata' not in training_data:
                training_data['metadata'] = {}
            training_data['metadata']['dataset_hash'] = dataset_hash
            logger.info(f"📊 Including dataset_hash in ES training metadata: {dataset_hash}")
        
        post_training_data(training_data)
        
        # Log training metadata to meta-learning API
        try:
            logger.info("="*80)
            logger.info("📊 LOGGING ES TRAINING METADATA TO META-LEARNING API")
            logger.info("="*80)
            
            from lib.meta_learning_client import (
                get_dataset_characteristics,
                log_training_metadata,
                get_meta_next_config
            )
            
            # Get dataset characteristics
            dataset_chars = get_dataset_characteristics(train_input_data.df)
            n_rows = dataset_chars['n_rows']
            n_cols = dataset_chars['n_cols']
            target_type = dataset_chars.get('target_type', 'regression')
            
            # Get pre-analysis configs from session if available
            pre_analysis_epochs = None
            if args.session_id:
                try:
                    from lib.session_manager import load_session
                    session = load_session(args.session_id)
                    pre_analysis_results = session.get('pre_analysis_results', {})
                    if pre_analysis_results:
                        # Extract configs that were tested during pre-analysis
                        all_tested = pre_analysis_results.get('all_tested_configs', [])
                        experimental_configs = pre_analysis_results.get('experimental_configs', [])
                        
                        # Combine both lists and format for API
                        all_configs = (all_tested or []) + (experimental_configs or [])
                        if all_configs:
                            pre_analysis_epochs = [
                                {
                                    'd_model': c.get('d_model'),
                                    'n_transformer_layers': c.get('n_transformer_layers'),
                                    'n_attention_heads': c.get('n_attention_heads')
                                }
                                for c in all_configs
                                if all([c.get('d_model'), c.get('n_transformer_layers'), c.get('n_attention_heads')])
                            ]
                            logger.info(f"   Found {len(pre_analysis_epochs)} pre-analysis configs to log")
                except Exception as e:
                    logger.warning(f"⚠️  Could not load pre-analysis configs: {e}")
            
            # Build final results from training data
            final_results = {}
            if training_data:
                # Extract metrics from training data
                metrics = training_data.get('metrics', {})
                if metrics:
                    if 'auc' in metrics:
                        final_results['auc'] = metrics['auc']
                    if 'accuracy' in metrics:
                        final_results['accuracy'] = metrics['accuracy']
                    if 'f1' in metrics:
                        final_results['f1'] = metrics['f1']
            
            # Log to meta-learning API
            metadata_id = log_training_metadata_v2(
                n_rows=n_rows,
                n_cols=n_cols,
                target_type=target_type,
                optimal_parameters=optimal_params,
                pre_analysis_epochs=pre_analysis_epochs,
                final_results=final_results if final_results else None
            )
            
            if metadata_id:
                logger.info(f"✅ Training metadata logged to meta-learning API: {metadata_id}")
            else:
                logger.warning(f"⚠️  Failed to log training metadata (returned None)")
            
            logger.info("="*80)
        except Exception as meta_err:
            logger.warning(f"⚠️  Failed to log training metadata to meta-learning API: {meta_err}")
            logger.debug(f"   Full traceback: {traceback.format_exc()}")
            # Don't fail training if meta-learning logging fails
        
        logger.info("="*80)
    except Exception as e:
        logger.warning(f"⚠️  Failed to post ES training data to monitor: {e}")
        logger.debug(f"   Full traceback: {traceback.format_exc()}")
        # Don't fail training if monitor posting fails


def save_training_metadata_and_finish_flag(
    es,
    args: LightTrainingArgs,
    epochs: int,
    training_start_time: datetime
):
    """
    Save comprehensive ES training metadata and handle FINISH flag.
    
    This function:
    1. Saves comprehensive ES training metadata JSON
    2. Checks if training was interrupted by FINISH flag and creates FINISHED flag
    
    Args:
        es: EmbeddingSpace instance
        args: LightTrainingArgs instance with training configuration
        epochs: Number of epochs trained
        training_start_time: Start time of training
    
    Note:
        This function catches all exceptions and logs warnings - it never fails training.
    """
    logger = logging.getLogger(__name__)
    
    # Save comprehensive ES training metadata JSON
    try:
        logger.info("="*80)
        logger.info("📝 SAVING COMPREHENSIVE ES TRAINING METADATA")
        logger.info("="*80)
        
        metadata_file = save_es_metadata(
            session_id=args.session_id or args.job_id or "no_session",
            epochs=epochs,
            training_response=None,  # Could add initial API response if available
            csv_file=args.input_file,
            client=None,  # No API client available in local training
            training_start_time=training_start_time,
            es=es  # Pass the trained embedding space for local model info
        )
        
        if metadata_file:
            logger.info(f"✅ ES training metadata successfully saved to: {metadata_file}")
        else:
            logger.warning("⚠️ Failed to save ES training metadata")
            
        logger.info("="*80)
    except Exception as e:
        logger.error(f"❌ Error saving ES training metadata: {e}")
        traceback.print_exc()
        # Don't fail the training if metadata save fails
    
    # Check if training was interrupted by FINISH flag
    # If so, create a FINISHED flag to indicate successful completion
    try:
        progress_info = es.training_info.get("progress_info", {})
        interrupted_reason = progress_info.get("interrupted", None)
        
        if interrupted_reason == "FINISH file detected":
            logger.info("🏁 Training was interrupted by FINISH flag - creating FINISHED flag")
            finished_file = Path(".") / "FINISHED"
            with open(finished_file, 'w') as f:
                f.write(f"FINISHED flag created at {datetime.now().isoformat()}\n")
                f.write(f"Training completed gracefully after FINISH flag was detected\n")
                f.write(f"Model saved successfully\n")
            logger.info(f"✅ FINISHED flag created: {finished_file}")
    except Exception as e:
        logger.warning(f"Failed to create FINISHED flag: {e}")
        # Don't fail the job if we can't create the flag


def prepare_train_val_split(data_set, args: LightTrainingArgs):
    """
    Prepare training and validation splits from dataset.
    
    Args:
        data_set: FeatrixInputDataSet instance
        args: LightTrainingArgs with batch_size configuration
    
    Returns:
        tuple: (train_input_data, val_input_data, system_meta, batch_size)
    """
    logger = logging.getLogger(__name__)
    system_meta = {}
    
    if len(data_set) < 200:
        train_input_data = data_set
        val_input_data = copy.deepcopy(train_input_data)
        system_meta['validation_set_warning'] = True
        system_meta['validation_set'] = f"Your data set is very small ({len(data_set)} records). We are using a copy of the data set as the validation set for the embedding space. We recommend adding more data to improve training and validation (at least 200 records total)."
        logger.warning(f"⚠️  Small dataset ({len(data_set)} rows): Using duplicate as validation set")
        batch_size = args.batch_size if args.batch_size else ideal_batch_size(len(data_set))
    else:
        # Calculate validation set as 20% of dataset, rounded down to nearest multiple of batch_size
        # to avoid incomplete batches during training
        # Determine batch size (same logic as in EmbeddingSpace.train())
        if args.batch_size == 0:
            batch_size = ideal_batch_size(len(data_set))
        else:
            batch_size = args.batch_size
        
        # Calculate 20% of dataset
        val_size_20pct = int(len(data_set) * 0.2)
        
        # Round down to nearest multiple of batch_size to avoid partial batches
        val_size = (val_size_20pct // batch_size) * batch_size
        
        # Ensure we have at least one batch for validation
        if val_size < batch_size:
            val_size = batch_size
            logger.warning(f"⚠️  Dataset too small for 20% validation. Using one batch ({batch_size} rows) instead.")
        
        # CRITICAL: Cap val_size to ensure we don't exceed dataset size
        # Must leave at least 1 sample for training
        dataset_size = len(data_set)
        max_val_size = dataset_size - 1
        if val_size > max_val_size:
            logger.warning(f"⚠️  Calculated val_size ({val_size}) exceeds dataset size ({dataset_size}). Using 20% fraction instead.")
            # Use 20% as a fraction instead of absolute number when dataset is too small
            val_size = 0.2
        elif val_size >= dataset_size:
            # Edge case: val_size equals dataset size (shouldn't happen, but be safe)
            logger.warning(f"⚠️  Calculated val_size ({val_size}) equals dataset size ({dataset_size}). Using 20% fraction instead.")
            val_size = 0.2
        
        logger.info(f"📊 Validation set calculation: 20% of {len(data_set)} = {val_size_20pct}, rounded to {val_size} (divisible by batch_size={batch_size})")
        
        train_input_data, val_input_data = data_set.split(val_size)
        
        system_meta['validation_set_warning'] = False
        system_meta['validation_set'] = f"Validation data is set to {val_size} records out of the input {len(data_set)} for training your embedding space."
        logger.info(f"📈 Training split: {len(train_input_data)} rows for training, {len(val_input_data)} rows for validation")
    
    system_meta['validation_set_length'] = len(val_input_data)
    system_meta['training_set_length'] = len(train_input_data)
    
    return train_input_data, val_input_data, system_meta, batch_size


def validate_and_prepare_user_metadata(args: LightTrainingArgs):
    """
    Validate and prepare user metadata from args.
    
    Args:
        args: LightTrainingArgs with optional user_metadata
    
    Returns:
        dict or None: Validated user metadata, or None if not provided
    
    Raises:
        ValueError: If user_metadata is invalid
    """
    logger = logging.getLogger(__name__)
    
    if args.user_metadata is not None:
        try:
            validated_user_metadata = validate_user_metadata(args.user_metadata, max_size_kb=32)
            logger.info(f"✅ User metadata validated: {len(json.dumps(validated_user_metadata))} bytes")
            return validated_user_metadata
        except ValueError as e:
            logger.error(f"❌ Invalid user_metadata: {e}")
            raise
    return None


def find_sqlite_db_path(args: LightTrainingArgs):
    """
    Find SQLite database path for PCA initialization.
    
    Priority:
    1. Get from session (from create_structured_data job)
    2. Check if input_file is a SQLite database
    3. Search for .db file in same directory with similar name
    4. Use any .db file in the directory
    
    Args:
        args: LightTrainingArgs with session_id and input_file
    
    Returns:
        str or None: Path to SQLite database, or None if not found
    """
    logger = logging.getLogger(__name__)
    sqlite_db_path = None
    
    # First, try to get from session (most reliable)
    if args.session_id:
        try:
            session = load_session(args.session_id)
            # Check if session has sqlite_db from create_structured_data job output
            session_sqlite_db = session.get('sqlite_db')
            if session_sqlite_db and Path(session_sqlite_db).exists():
                sqlite_db_path = str(Path(session_sqlite_db).resolve())
                logger.info(f"✅ Found SQLite database from session: {sqlite_db_path}")
        except Exception as e:
            logger.debug(f"Could not get sqlite_db from session: {e}")
    
    # Fallback: search based on input_file if not found in session
    if sqlite_db_path is None and args.input_file:
        input_file_path = Path(args.input_file)
        # Check if input_file is already a SQLite database
        if input_file_path.suffix.lower() in ['.db', '.sqlite', '.sqlite3']:
            if input_file_path.exists():
                sqlite_db_path = str(input_file_path)
                logger.info(f"🔍 Found SQLite database (matches input_file): {sqlite_db_path}")
        else:
            # Try to find a .db file in the same directory with similar name
            input_dir = input_file_path.parent
            input_stem = input_file_path.stem
            # Try common database file names
            for db_ext in ['.db', '.sqlite', '.sqlite3']:
                potential_db = input_dir / f"{input_stem}{db_ext}"
                if potential_db.exists():
                    sqlite_db_path = str(potential_db)
                    logger.info(f"🔍 Found SQLite database for PCA initialization: {sqlite_db_path}")
                    break
            # If not found, try looking for any .db file in the directory
            if sqlite_db_path is None:
                db_files = list(input_dir.glob("*.db"))
                if db_files:
                    sqlite_db_path = str(db_files[0])
                    logger.info(f"🔍 Using SQLite database for PCA initialization: {sqlite_db_path}")
    
    if sqlite_db_path is None:
        logger.warning(f"⚠️  Could not find SQLite database for PCA initialization - PCA init will be skipped")
    
    return sqlite_db_path


def get_optimal_es_config(args: LightTrainingArgs, input_data_file):
    """
    Get optimal ES configuration from pre-analysis or meta-learning API.
    
    Priority:
    1. Get from session (pre-analysis results)
    2. Query meta-learning API
    
    Args:
        args: LightTrainingArgs with session_id
        input_data_file: Input data file for dataset characteristics
    
    Returns:
        dict or None: Optimal config with d_model, n_transformer_layers, n_attention_heads, or None
    """
    logger = logging.getLogger(__name__)
    optimal_config = None
    
    # Check if pre-analysis determined optimal architecture config
    if args.session_id:
        try:
            session = load_session(args.session_id)
            optimal_config = session.get('optimal_es_config')
            if optimal_config:
                logger.info(f"🎯 Using optimal architecture from pre-analysis:")
                logger.info(f"   d_model: {optimal_config.get('d_model')}")
                logger.info(f"   n_transformer_layers: {optimal_config.get('n_transformer_layers')}")
                logger.info(f"   n_attention_heads: {optimal_config.get('n_attention_heads')}")
                logger.info(f"   Estimated AUC: {optimal_config.get('estimated_auc', 'N/A')}")
        except Exception as e:
            logger.warning(f"⚠️  Could not load optimal config from session: {e}")
            optimal_config = None
    
    # If no optimal config from pre-analysis, try meta-learning API
    if not optimal_config:
        try:
            logger.info("="*80)
            logger.info("🧠 QUERYING META-LEARNING API FOR NEXT CONFIG")
            logger.info("="*80)
            
            from lib.meta_learning_client import (
                get_dataset_characteristics,
                get_meta_next_config
            )
            
            # Get dataset characteristics
            dataset_chars = get_dataset_characteristics(input_data_file.df)
            n_rows = dataset_chars['n_rows']
            n_cols = dataset_chars['n_cols']
            target_type = dataset_chars.get('target_type', 'regression')
            
            # Query meta-learning API for next config
            next_config_result = get_meta_next_config(
                n_rows=n_rows,
                n_cols=n_cols,
                target_type=target_type,
                min_epochs=25
            )
            
            if next_config_result and next_config_result.get('next_config'):
                next_config = next_config_result['next_config']
                optimal_config = {
                    'd_model': next_config.get('d_model'),
                    'n_transformer_layers': next_config.get('n_transformer_layers'),
                    'n_attention_heads': next_config.get('n_attention_heads'),
                    'estimated_auc': next_config.get('final_auc'),
                    'source': 'meta_learning_api'
                }
                logger.info(f"✅ Got config recommendation from meta-learning API:")
                logger.info(f"   d_model: {optimal_config['d_model']}")
                logger.info(f"   n_transformer_layers: {optimal_config['n_transformer_layers']}")
                logger.info(f"   n_attention_heads: {optimal_config['n_attention_heads']}")
                if optimal_config.get('estimated_auc'):
                    logger.info(f"   Expected AUC: {optimal_config['estimated_auc']:.4f}")
                logger.info("="*80)
            else:
                logger.info(f"ℹ️  No config recommendation available from meta-learning API")
                logger.info(f"   Total tested: {next_config_result.get('total_tested', 0) if next_config_result else 0}")
                logger.info("="*80)
        except Exception as meta_err:
            logger.warning(f"⚠️  Failed to query meta-learning API: {meta_err}")
            logger.debug(f"   Full traceback: {traceback.format_exc()}")
            # Don't fail training if meta-learning query fails
    
    return optimal_config


def update_session_with_embedding_space_path(args: LightTrainingArgs, embedding_space_path: str):
    """
    Update session file with embedding_space path.
    
    This must happen BEFORE the subprocess exits so the Celery task can read it.
    
    Args:
        args: LightTrainingArgs with session_id
        embedding_space_path: Path to the saved embedding space
    """
    logger = logging.getLogger(__name__)
    
    if not args.session_id:
        logger.warning(f"⚠️  No session_id provided - cannot update session with embedding_space path")
        return
    
    try:
        logger.info(f"🔄 Updating session {args.session_id} with embedding_space path...")
        logger.info(f"   Embedding space path to save: {embedding_space_path}")
        logger.info(f"   Path exists: {Path(embedding_space_path).exists()}")
        from lib.session_manager import load_session, save_session
        session = load_session(args.session_id)
        logger.info(f"   Session loaded, current embedding_space: {session.get('embedding_space')}")
        session['embedding_space'] = embedding_space_path
        logger.info(f"   About to save session with embedding_space: {embedding_space_path}")
        save_session(args.session_id, session, exist_ok=True)
        logger.info(f"   ✅ Session save completed")
        
        # VERIFY the update worked
        verify_session = load_session(args.session_id)
        verified_path = verify_session.get('embedding_space')
        logger.info(f"   🔍 VERIFICATION: Session embedding_space after save: {verified_path}")
        if verified_path == embedding_space_path:
            logger.info(f"   ✅ VERIFIED: Session correctly updated with embedding_space path")
        else:
            logger.error(f"   ❌ VERIFICATION FAILED: Expected {embedding_space_path}, got {verified_path}")
            logger.error(f"   ⚠️  Session update may have failed silently!")
    except Exception as session_err:
        logger.error(f"❌ CRITICAL: Failed to update session with embedding_space path: {session_err}")
        logger.error(f"   Traceback: {traceback.format_exc()}")
        # Don't fail training - Celery task can construct the path as fallback


def warm_string_server_cache(train_input_data, val_input_data, args: LightTrainingArgs, extended_coder):
    """
    Pre-warm string server cache with train+val data.
    
    Args:
        train_input_data: Training input data
        val_input_data: Validation input data
        args: LightTrainingArgs with ignore_cols
        extended_coder: Column overrides dictionary
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔥 Pre-warming string server cache with train+val data...")
    try:
        # Combine train and val data for cache warming
        import pandas as pd
        
        # Create combined dataset for cache warming
        combined_df = pd.concat([train_input_data.df, val_input_data.df], ignore_index=True)
        combined_data_set = FeatrixInputDataSet(
            df=combined_df,
            ignore_cols=args.ignore_cols,
            limit_rows=None,  # Use all rows
            encoder_overrides=extended_coder,
        )
        combined_data_set.warm_string_server_cache()
        logger.info(f"✅ String server cache pre-warmed with {len(combined_df)} rows")
    except Exception as e:
        logger.error(f"❌ Failed to pre-warm string server cache: {e}")
        logger.error(traceback.format_exc())
        # Don't fail training, but log the error


def log_column_overrides(column_overrides):
    """
    Log column overrides information for debugging.
    
    Args:
        column_overrides: Dictionary of column overrides to log
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 COLUMN_OVERRIDES DEBUG: args.column_overrides = {column_overrides}")
    logger.info(f"🔍 COLUMN_OVERRIDES DEBUG: extended_coder = {column_overrides}")
    if column_overrides:
        logger.info(f"🔧 Applying column overrides: {column_overrides}")
    else:
        logger.info("ℹ️  No column overrides to apply")


def send_es_training_start_slack_notification(args: LightTrainingArgs, training_start_time: datetime):
    """
    Send Slack notification when ES training starts.
    
    Args:
        args: LightTrainingArgs instance with training configuration
        training_start_time: Start time of training
    
    Note:
        This function catches all exceptions and logs warnings - it never fails training.
    """
    logger = logging.getLogger(__name__)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        hostname = get_hostname()
        version_info = get_version()
        current_time = training_start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        slack_msg = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        slack_msg += f"🚀 *ES Training Started on `{hostname}`*\n"
        slack_msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        slack_msg += f"```\n"
        slack_msg += f"Version:   {version_info.semantic_version}\n"
        slack_msg += f"Date:      {current_time}\n"
        slack_msg += f"```\n\n"
        slack_msg += f"```\n"
        slack_msg += f"Field              Value\n"
        slack_msg += f"─────────────────────────────────────\n"
        slack_msg += f"Session ID         {args.session_id}\n"
        slack_msg += f"Job ID             {args.job_id}\n"
        slack_msg += f"Epochs             {args.epochs or 'auto'}\n"
        slack_msg += f"Row Limit          {args.row_limit or 'unlimited'}\n"
        slack_msg += f"Batch Size         {args.batch_size or 'auto'}\n"
        slack_msg += f"Learning Rate      {args.learning_rate or 'default'}\n"
        slack_msg += f"```"
        
        # pylint: disable=unexpected-keyword-arg
        send_slack_message(slack_msg, throttle=False, skip_hostname_prefix=True)  # Critical - don't throttle, hostname already in message
        logger.info("✅ Slack notification sent for ES training start")
    except Exception as slack_error:
        logger.warning(f"Failed to send Slack notification: {slack_error}")


def train_es(args: LightTrainingArgs):
    """Main entry point for ES training - auto-selects CV or single training."""
    logger = logging.getLogger(__name__)
    
    # Print version info at start of training
    try:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add src to path
        print_version_banner("Featrix Sphere ES Training")
        
        # Explicitly log version to syslog
        version_info = get_version()
        logger.info(f"📦 ES Training Version: {version_info.semantic_version} (git: {version_info.git_hash[:8] if version_info.git_hash else 'unknown'})")
        logger.info(f"📅 Version Date: {version_info.git_date or 'unknown'}")
    except Exception as e:
        logger.warning(f"⚠️ Could not load version info: {e}")
        print(f"⚠️ Could not load version info: {e}")
    
    # Capture training start time for metadata
    training_start_time = datetime.now()
    
    print("@@@@ Hello!.....")
    
    # ============================================================================
    # 🔍 COMPREHENSIVE CONFIGURATION AND STATE LOGGING
    # ============================================================================
    logger.info("=" * 100)
    logger.info("🚀 ES TRAINING STARTED - FULL CONFIGURATION DUMP")
    logger.info("=" * 100)
    
    logger.info(f"⏰ Training Start Time: {training_start_time.isoformat()}")
    logger.info(f"🔑 Session ID: {args.session_id or 'NOT PROVIDED'}")
    logger.info(f"🆔 Job ID: {args.job_id}")
    logger.info(f"📂 Input File: {args.input_file}")
    logger.info(f"🔢 Requested epochs: {args.epochs} (will be divided by number of folds if using CV)")
    logger.info(f"📊 Row Limit: {args.row_limit}")
    batch_size_display = args.batch_size if args.batch_size > 0 else "AUTO"
    learning_rate_display = args.learning_rate if args.learning_rate is not None else "AUTO"
    logger.info(f"🔢 Batch Size: {batch_size_display}")
    logger.info(f"📉 Learning Rate: {learning_rate_display}")
    logger.info(f"🏭 Is Production: {args.is_production}")
    logger.info(f"📝 Job Queue: {args.job_queue}")
    
    logger.info("")
    logger.info("🎯 IMPORTANT COLUMNS FOR VISUALIZATION:")
    if args.important_columns_for_visualization:
        logger.info(f"   Count: {len(args.important_columns_for_visualization)}")
        logger.info(f"   Columns: {args.important_columns_for_visualization}")
    else:
        logger.info("   ⚠️  NONE SPECIFIED - using random sampling for training movies")
    
    logger.info("")
    logger.info("🚫 IGNORE COLUMNS:")
    if args.ignore_cols:
        logger.info(f"   Count: {len(args.ignore_cols)}")
        logger.info(f"   Columns: {args.ignore_cols}")
    else:
        logger.info("   None")
    
    logger.info("")
    logger.info("🔧 COLUMN OVERRIDES:")
    if args.column_overrides:
        logger.info(f"   Count: {len(args.column_overrides)}")
        for col, override in list(args.column_overrides.items())[:10]:
            logger.info(f"   - {col}: {override}")
        if len(args.column_overrides) > 10:
            logger.info(f"   ... and {len(args.column_overrides) - 10} more")
    else:
        logger.info("   None")
    
    logger.info("")
    logger.info("📦 JSON TRANSFORMATIONS:")
    if args.json_transformations:
        logger.info(f"   Count: {len(args.json_transformations)}")
        for col, transform in list(args.json_transformations.items())[:5]:
            logger.info(f"   - {col}: {transform}")
        if len(args.json_transformations) > 5:
            logger.info(f"   ... and {len(args.json_transformations) - 5} more")
    else:
        logger.info("   None")
    
    # logger.info("")
    # logger.info("✂️  GRADIENT CLIPPING:")
    # logger.info(f"   Max Grad Norm (legacy): {args.max_grad_norm}")
    # logger.info(f"   Adaptive Grad Clip Ratio: {args.adaptive_grad_clip_ratio}")
    # logger.info(f"   Grad Clip Warning Multiplier: {args.grad_clip_warning_multiplier}")
    
    logger.info("")
    logger.info("💾 STRING CACHE:")
    logger.info(f"   Using in-memory string server cache (no SQLite files)")
    
    logger.info("=" * 100)
    logger.info("📋 FULL ARGS JSON:")
    logger.info(args.model_dump_json(indent=2))
    logger.info("=" * 100)
    
        # Post to Slack that ES training is starting
    send_es_training_start_slack_notification(args, training_start_time)
    
    # Load data file
    logger.info(f"no transient_upload_file_name -- doing things like a normal person")
    input_data_file = FeatrixInputDataFile(args.input_file)
    
    # Handle __featrix_train_predictor column for ES training
    PREDICTOR_FILTER_COLUMN = "__featrix_train_predictor"
    logger.info("=" * 80)
    logger.info("🔍 ES TRAINING: Checking for __featrix_train_predictor column")
    logger.info(f"📊 Initial data shape: {input_data_file.df.shape}")
    logger.info(f"📋 Columns present: {list(input_data_file.df.columns)}")
    
    if PREDICTOR_FILTER_COLUMN in input_data_file.df.columns:
        logger.info(f"✅ Found {PREDICTOR_FILTER_COLUMN} column in data")
        logger.info(f"📊 Column dtype: {input_data_file.df[PREDICTOR_FILTER_COLUMN].dtype}")
        logger.info(f"📊 Column value counts:\n{input_data_file.df[PREDICTOR_FILTER_COLUMN].value_counts()}")
        logger.info(f"📊 Column null count: {input_data_file.df[PREDICTOR_FILTER_COLUMN].isna().sum()}")
        
        # For ES training: drop the column but keep all rows
        logger.info(f"🗑️  ES Training: Dropping {PREDICTOR_FILTER_COLUMN} column (using ALL rows)")
        input_data_file.df.drop(columns=[PREDICTOR_FILTER_COLUMN], inplace=True)
        
        logger.info(f"✅ Column dropped successfully")
        logger.info(f"📊 Final data shape after dropping column: {input_data_file.df.shape}")
        logger.info(f"📋 Remaining columns: {list(input_data_file.df.columns)}")
    else:
        logger.info(f"ℹ️  No {PREDICTOR_FILTER_COLUMN} column found - proceeding with all data as-is")
    
    logger.info("=" * 80)
    
    # Automatic cross-validation for small datasets (more repeatable behavior)
    # For large datasets (>= 10000 rows), CV is computationally expensive and unnecessary
    # A single train/val split is sufficient for large datasets
    n_rows = len(input_data_file.df)
    CV_THRESHOLD = 10000  # Don't use CV for datasets with >= 10000 rows
    use_cv = n_rows < CV_THRESHOLD
    
    if use_cv:
        logger.info(f"🔀 Dataset has {n_rows} rows (< {CV_THRESHOLD}) - using 5-fold cross-validation for robust training")
        return _train_es_with_cv(args, input_data_file, training_start_time=training_start_time, cv_threshold=CV_THRESHOLD)
    else:
        logger.info(f"📊 Dataset has {n_rows} rows (>= {CV_THRESHOLD}) - using standard single train/val split (CV disabled for large datasets)")
        return _train_es_single(args, input_data_file, training_start_time=training_start_time, cv_threshold=CV_THRESHOLD, use_cv=False)


def _train_es_with_cv(args: LightTrainingArgs, input_data_file, training_start_time=None, cv_threshold=10000):
    """Train embedding space by rotating through 80/20 train/val splits.
    
    Simple approach: Just rotate through different data splits to improve coverage.
    ES continues training across splits - no complex fold tracking needed.
    
    Args:
        args: Training arguments
        input_data_file: Input data file
        training_start_time: When training started (for metadata tracking)
        cv_threshold: Threshold used to decide whether to use CV
    """    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("📊 SINGLE TRAIN/VAL SPLIT: Using one 80/20 split (K-fold rotation disabled)")
    logger.info("   Faster training, simpler debugging, curriculum/LR work correctly")
    logger.info("="*80)
    
    n_folds = 1  # DISABLED: K-fold rotation has curriculum/LR bugs, use single split
    df = input_data_file.df
    n_rows = len(df)
    
    # Add CV decision to timeline (will be added to ES timeline after first fold creates ES)
    cv_decision_info = {
        "use_cross_validation": False,  # Disabled K-fold rotation
        "cv_threshold": cv_threshold,
        "dataset_rows": n_rows,
        "reason": f"Dataset has {n_rows} rows (< {cv_threshold} threshold) - using single split (K-fold disabled)"
    }
    
    # Calculate epochs per fold (divide total epochs across folds)
    # If epochs is 0, it will be auto-calculated in _train_es_single based on dataset size
    total_epochs = args.epochs if args.epochs > 0 else 0  # 0 = auto-calculate in _train_es_single
    epochs_per_fold = total_epochs  # Single fold = train for full epoch count
    logger.info(f"📊 Training plan:")
    logger.info(f"   Total epochs: {total_epochs}")
    logger.info(f"   Single 80/20 train/val split")
    logger.info(f"   No K-fold rotation (curriculum and LR work correctly)")
    
    # Create single 80/20 train/val split (no KFold needed for n_splits=1)
    all_indices = list(range(n_rows))
    train_idx, val_idx = train_test_split(all_indices, test_size=0.2, shuffle=True, random_state=42)
    splits = [(train_idx, val_idx)]
    
    es = None  # Will hold the embedding space across splits
    cumulative_epochs = 0  # Track total epochs trained across all splits
    
    for fold_idx, (train_idx, val_idx) in enumerate(splits):
        logger.info("="*80)
        if n_folds > 1:
            logger.info(f"🔄 Split {fold_idx + 1}/{n_folds}: Training on {len(train_idx)} rows ({len(train_idx)/len(df)*100:.1f}%), validating on {len(val_idx)} rows ({len(val_idx)/len(df)*100:.1f}%)")
        else:
            logger.info(f"📊 Single train/val split: Training on {len(train_idx)} rows ({len(train_idx)/len(df)*100:.1f}%), validating on {len(val_idx)} rows ({len(val_idx)/len(df)*100:.1f}%)")
        logger.info("="*80)
        
        # Create split-specific data
        fold_train_df = df.iloc[train_idx]
        fold_val_df = df.iloc[val_idx]
        
        # Create temporary data file for this split
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            fold_data_file = tmp.name
            fold_train_df.to_csv(fold_data_file, index=False)
        
        try:
            # Create split-specific args
            fold_args = args.model_copy()
            fold_args.input_file = fold_data_file
            fold_args.epochs = epochs_per_fold
            # Set resume_from_epoch to cumulative epochs so epoch tracking continues across splits
            if fold_idx > 0:
                fold_args.resume_from_epoch = cumulative_epochs
            
            # Create input file object
            fold_input_file = FeatrixInputDataFile(fold_data_file)
            
            # Train this split (will resume from existing ES if provided)
            # Pass training_start_time only for first split (for metadata), subsequent splits are continuations
            fold_training_start_time = training_start_time if fold_idx == 0 else None
            # Pass cumulative_epochs offset so epochs are reported as cumulative (makes splits invisible)
            es = _train_es_single(fold_args, fold_input_file, resume_from_es=es, training_start_time=fold_training_start_time, cv_decision_info=cv_decision_info if fold_idx == 0 else None, kv_fold_offset=cumulative_epochs)
            
            # Update cumulative epoch count after training
            cumulative_epochs += epochs_per_fold
            if n_folds > 1:
                logger.info(f"✅ Split {fold_idx + 1}/{n_folds} completed (cumulative epochs: {cumulative_epochs})")
            else:
                logger.info(f"✅ Training completed ({cumulative_epochs} epochs)")
        
        finally:
            # Clean up temporary data file
            try:
                os.unlink(fold_data_file)
            except Exception as e:
                logger.warning(f"Could not delete temporary split file {fold_data_file}: {e}")
    
    logger.info("="*80)
    logger.info(f"✅ TRAINING COMPLETE: ES has been trained on {n_rows} rows using single train/val split")
    logger.info("="*80)
    
    # Save final embedding space and create model package
    # CRITICAL: We're already in the job directory ({output_dir}/{session_id}/train_es/{job_id}/)
    # Don't create a subdirectory - just save to current directory
    output_dir = os.getcwd()
    embedding_space_path = save_embedding_space_and_package(es, output_dir=output_dir)
    
    # Update session file with embedding_space path
    update_session_with_embedding_space_path(args, embedding_space_path)
    
    # Save model architecture metadata separately
    metadata_path = os.path.join(output_dir, "model_metadata.json")
    try:
        # Count layers in the encoder
        layer_count = 0
        param_count = 0
        
        if hasattr(es, 'encoder'):
            for name, module in es.encoder.named_modules():
                if len(list(module.children())) == 0:  # Leaf modules only
                    layer_count += 1
            
            # Count parameters (should match es.model_param_count)
            # model_param_count might be a dict with 'total_params' key, or a number
            if hasattr(es, 'model_param_count'):
                if isinstance(es.model_param_count, dict):
                    param_count = es.model_param_count.get('total_params', 0)
                else:
                    param_count = es.model_param_count
            else:
                param_count = sum(p.numel() for p in es.encoder.parameters())
        
        metadata = {
            "name": es.name if hasattr(es, 'name') else None,
            "model_architecture": {
                "layer_count": layer_count,
                "parameter_count": param_count
            },
            "d_model": es.d_model if hasattr(es, 'd_model') else None,
            "num_columns": len(es.availableColumns) if hasattr(es, 'availableColumns') else None,
        }
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Safely format param_count - it might be a dict or other non-numeric type
        if isinstance(param_count, (int, float)):
            param_str = f"{param_count:,}"
        else:
            param_str = str(param_count)
        
        logger.info(f"💾 Model metadata saved: {layer_count} layers, {param_str} parameters")
    except Exception as e:
        logger.warning(f"Failed to save model metadata: {e}")
    
    return es


def _train_es_single(args: LightTrainingArgs, input_data_file, resume_from_es=None, training_start_time=None, cv_threshold=10000, use_cv=None, cv_decision_info=None, kv_fold_offset=0):
    """Train a single embedding space (no cross-validation).
    
    Args:
        args: Training arguments
        input_data_file: Input data file
        resume_from_es: Optional existing EmbeddingSpace to continue training from (used in K-fold)
        training_start_time: When training started (for metadata tracking)
        cv_threshold: Threshold used to decide whether to use CV
        use_cv: Whether CV was used (False for this function, but tracks the decision)
        cv_decision_info: Pre-computed CV decision info (for CV path)
    """
    logger = logging.getLogger(__name__)
    
    # ========================================================================
    # EARLY ABORT CHECK: Check for ABORT file BEFORE doing any expensive work
    # ========================================================================
    job_id = getattr(args, 'job_id', None)
    if job_id:
        output_dir = os.getcwd()
        logger.info(f"🔍 Early abort check for job {job_id} in {output_dir}")
        check_abort_and_raise(job_id, output_dir=output_dir, context="job start")
    
    # Capture start time if not provided
    if training_start_time is None:
        training_start_time = datetime.now()
    
    # Log whether we're creating new or resuming
    if resume_from_es is not None:
        logger.info(f"🔄 Resuming training from existing EmbeddingSpace (K-fold continuation)")
        logger.info(f"   is_production = {args.is_production}, trial_row_limit = {args.row_limit}")
    else:
        logger.info(f"creating embedding space... here we go...is_production = {args.is_production}, trial_row_limit = {args.row_limit}")
    sys.stdout.flush()

    # Use column overrides from session instead of empty dict
    extended_coder = args.column_overrides
    log_column_overrides(extended_coder)
    
    logger.info(f"starting input dataset... args.input_file = __{args.input_file}__")
    
    system_meta = {}

    data_set = FeatrixInputDataSet(
        df=input_data_file.df,
        ignore_cols=args.ignore_cols,
        limit_rows=args.row_limit,
        encoder_overrides=extended_coder,
        project_row_meta_data=None,
    )

    logger.info(f"📊 Dataset loaded: {len(data_set)} rows x {len(data_set.df.columns)} columns")
    if args.row_limit is not None and args.row_limit < len(input_data_file.df):
        logger.info(f"⚠️  Dataset was sampled down from {len(input_data_file.df)} rows to {len(data_set)} rows (training limit: {args.row_limit})")
    else:
        logger.info(f"✅ Using full dataset for training ({len(data_set)} rows)")

    training_worked = False
    try:
        logger.debug("....creating embedding_space space...")

        # Prepare train/val split
        train_input_data, val_input_data, system_meta, batch_size = prepare_train_val_split(data_set, args)
        
        # Pre-warm string server cache with train+val data
        warm_string_server_cache(train_input_data, val_input_data, args, extended_coder)
        
        # Warn if dataset is very small
        total_rows = len(train_input_data) + len(val_input_data)
        if total_rows < 50:
            logger.warning(f"⚠️  VERY SMALL DATASET: Only {total_rows} total rows ({len(train_input_data)} train, {len(val_input_data)} val)")
            logger.warning(f"   This may result in poor training quality. Consider adding more data.")
        elif total_rows < 100:
            logger.warning(f"⚠️  Small dataset: {total_rows} total rows ({len(train_input_data)} train, {len(val_input_data)} val)")
            logger.warning(f"   Training quality may be limited. Recommend at least 100 rows for better results.")
        
        batch_size_display = args.batch_size if args.batch_size > 0 else "AUTO"
        lr_display = args.learning_rate if args.learning_rate is not None else "AUTO"
        logger.info(f"🔧 Training configuration: {args.epochs} epochs, batch size {batch_size_display}, learning rate {lr_display}")

        logger.info(f"... embedding_meta      = {system_meta}")
        #embedding_meta.stash_attrs(es)

        logger.info(f">>> training now for {args.epochs} epochs; lr = {lr_display} >>>")
        
        # Validate and prepare user_metadata
        validated_user_metadata = validate_and_prepare_user_metadata(args)

        # OLD: Blocking epoch projection callback (DISABLED - replaced by async movie frames)
        # epoch_projection_callback = None
        epoch_projection_callback = None  # DISABLED
        
        # Use combined training + validation data for projections (same as full projections)
        full_df = data_set.df.copy()
        if '__featrix_row_id' not in full_df.columns:
            # Add row IDs if not present
            full_df.reset_index(inplace=True)
            full_df['__featrix_row_id'] = full_df.index
        
        # 🔍 DEBUGGING: Log what dataframe we're using
        logger.info(f"🔍 EPOCH PROJECTION SETUP DEBUG:")
        logger.info(f"   Using data_set.df (encoded dataframe) for projections")
        logger.info(f"   Encoded dataframe shape: {full_df.shape}")
        logger.info(f"   Encoded dataframe columns ({len(full_df.columns)} total): {list(full_df.columns)[:20]}{'...' if len(full_df.columns) > 20 else ''}")
        logger.info(f"   Using input_data_file.df (original dataframe) for important_columns matching")
        logger.info(f"   Original dataframe shape: {input_data_file.df.shape}")
        logger.info(f"   Original dataframe columns ({len(input_data_file.df.columns)} total): {list(input_data_file.df.columns)[:20]}{'...' if len(input_data_file.df.columns) > 20 else ''}")
        if args.important_columns_for_visualization:
            logger.info(f"   Important columns requested: {args.important_columns_for_visualization[:10]}{'...' if len(args.important_columns_for_visualization) > 10 else ''}")
            
        # DISABLED - old blocking callback replaced by async movie frames
        # try:
        #     if EPOCH_PROJECTIONS_AVAILABLE:
        #         epoch_projection_callback = EpochProjectionCallback(...)
        # except Exception as e:
        #     epoch_projection_callback = None

        class TrainingCallback:
            def __init__(self, args, epoch_projection_callback, kv_fold_offset=0):
                self.args = args
                self.epoch_projection_callback = epoch_projection_callback
                self.embedding_space = None
                self.total_epochs = 0  # Will be set before training starts
                self.last_posted_epoch = -1  # Track last epoch posted to avoid duplicates
                self.kv_fold_offset = kv_fold_offset  # K-fold CV epoch offset (cumulative epochs from previous folds)
                
            def set_embedding_space(self, es):
                self.embedding_space = es
            
            def set_total_epochs(self, epochs):
                self.total_epochs = epochs
                
            def __call__(self, training_event_dict):
                try:
                    # Import here to avoid scoping issues
                    import torch
                    
                    # Original job progress tracking
                    # Only update job progress if the job actually exists in the queue
                    # (e.g., QA tests call _train_es_single directly without creating jobs)
                    # Update job progress in Redis
                    if hasattr(self.args, 'job_id') and self.args.job_id:
                        try:
                            from lib.job_manager import load_job, save_job
                            job_data = load_job(self.args.job_id)
                            
                            if job_data:
                                # Use .get() with defaults to avoid KeyError
                                progress = training_event_dict.get('progress_counter', 0)
                                progress_max = training_event_dict.get('max_progress', 1)

                                try:
                                    if progress_max > 0:
                                        job_data['progress'] = progress / progress_max
                                    else:
                                        job_data['progress'] = None
                                except Exception:
                                    job_data['progress'] = None

                                # Save updated job data
                                session_id = job_data.get('session_id') or (self.args.session_id if hasattr(self.args, 'session_id') else 'unknown')
                                job_type = job_data.get('job_type') or (self.args.job_queue if hasattr(self.args, 'job_queue') else 'unknown')
                                save_job(self.args.job_id, job_data, session_id, job_type)
                            else:
                                logger.debug(f"Job {self.args.job_id} not found in Redis, skipping progress update")
                        except Exception as job_err:
                            # Log but don't fail training if job update fails
                            logger.debug(f"Failed to update job progress: {job_err}")

                    # Extract epoch and loss info from training_event_dict
                    # The dict contains epoch_idx directly, and loss_history is a list
                    epoch_idx = training_event_dict.get('epoch_idx', None)
                    loss_history = training_event_dict.get('loss_history', [])
                    
                    # Apply K-fold CV offset to epoch numbers for cumulative reporting
                    # epoch_idx is 0-indexed within the fold, so we add the offset
                    cumulative_epoch_idx = epoch_idx + self.kv_fold_offset if epoch_idx is not None else None
                    
                    # Find the current epoch's loss entry (match on original epoch_idx within fold)
                    current_loss_entry = None
                    if epoch_idx is not None and loss_history:
                        for entry in loss_history:
                            if isinstance(entry, dict) and entry.get('epoch') == epoch_idx:
                                current_loss_entry = entry
                                break
                    
                    # Extract loss values
                    if current_loss_entry:
                        # Use cumulative epoch number for reporting
                        epoch = cumulative_epoch_idx if cumulative_epoch_idx is not None else current_loss_entry.get('epoch', '?')
                        loss = current_loss_entry.get('loss', '?')
                        val_loss = current_loss_entry.get('validation_loss', '?')
                        learning_rate = current_loss_entry.get('current_learning_rate', self.args.learning_rate if self.args.learning_rate is not None else 'AUTO')
                        duration = current_loss_entry.get('duration', None)
                        
                        # Store detailed metrics to Redis for monitoring UI
                        if epoch != '?' and hasattr(self.args, 'job_id') and self.args.job_id and hasattr(self.args, 'job_queue'):
                            try:
                                from redis_job_progress import get_redis_job_progress
                                redis_progress = get_redis_job_progress()
                                if redis_progress.redis_available:
                                    # Collect all available metrics
                                    detailed_metrics = {
                                        'learning_rate': learning_rate if learning_rate != '?' else None,
                                        'train_loss': float(loss) if loss != '?' and isinstance(loss, (int, float)) else None,
                                        'validation_loss': float(val_loss) if val_loss != '?' and isinstance(val_loss, (int, float)) else None,
                                    }
                                    
                                    # Add ES-specific loss components if available
                                    for key in ['spread', 'joint', 'marginal', 'marginal_weighted']:
                                        if key in current_loss_entry and current_loss_entry[key] is not None:
                                            detailed_metrics[key] = float(current_loss_entry[key])
                                    
                                    redis_progress.append_training_metrics(
                                        job_type=self.args.job_queue,
                                        job_id=self.args.job_id,
                                        epoch=int(epoch),
                                        metrics=detailed_metrics
                                    )
                            except Exception as redis_err:
                                logger.debug(f"Failed to store training metrics to Redis: {redis_err}")
                    elif epoch_idx is not None:
                        # Fallback: use cumulative epoch_idx for reporting
                        epoch = cumulative_epoch_idx
                        loss = '?'
                        val_loss = '?'
                        learning_rate = self.args.learning_rate or 'AUTO'
                        duration = None
                    else:
                        epoch = '?'
                        loss = '?'
                        val_loss = '?'
                        learning_rate = self.args.learning_rate or 'AUTO'
                        duration = None
                    
                    if epoch != '?' and loss != '?' and val_loss != '?':
                        # Safe formatting - check types before using format specifiers
                        loss_str = f"{loss}" if isinstance(loss, (int, float)) else str(loss)
                        val_loss_str = f"{val_loss}" if isinstance(val_loss, (int, float)) else str(val_loss)
                        lr_str = f"{learning_rate}" if isinstance(learning_rate, (int, float)) else str(learning_rate)
                        logger.info(f"🚂 Epoch {epoch}/{self.total_epochs}: training_loss={loss_str}, validation_loss={val_loss_str}, lr={lr_str}")
                    
                    # Post progress to monitor (only on epoch completion, not every batch)
                    # Only post when epoch changes (new epoch completed)
                    if epoch != '?' and isinstance(epoch, (int, float)) and epoch >= 0 and epoch != self.last_posted_epoch:
                        try:
                            # Check if GPU is being used
                            ran_on_gpu = is_gpu_available() and get_gpu_current_device_id() is not None
                            
                            # Calculate estimated time remaining if we have timing info
                            estimated_time_remaining = None
                            if duration and epoch > 0:
                                remaining_epochs = max(0, self.total_epochs - epoch)
                                if duration > 0 and remaining_epochs > 0:
                                    total_seconds = duration * remaining_epochs
                                    minutes = int(total_seconds / 60)
                                    if minutes > 0:
                                        estimated_time_remaining = f"{minutes}m"
                                    else:
                                        estimated_time_remaining = f"{int(total_seconds)}s"
                            
                            # Get session_id from args (prefer session_id, fallback to job_id, or generate one)
                            session_id = (
                                getattr(self.args, 'session_id', None) or 
                                self.args.job_id if hasattr(self.args, 'job_id') and self.args.job_id else 
                                f"es-{id(self)}"
                            )
                            
                            # Build metadata with dataset_hash
                            progress_metadata = {}
                            if self.embedding_space and hasattr(self.embedding_space, '_dataset_hash'):
                                progress_metadata['dataset_hash'] = self.embedding_space._dataset_hash
                            
                            post_training_progress(
                                session_id=session_id,
                                training_type="embedding_space",
                                current_epoch=int(epoch),
                                total_epochs=self.total_epochs,
                                current_training_loss=float(loss) if loss != '?' else None,
                                current_validation_loss=float(val_loss) if val_loss != '?' else None,
                                estimated_time_remaining=estimated_time_remaining,
                                ran_on_gpu=ran_on_gpu,
                                metadata=progress_metadata if progress_metadata else None,
                            )
                            # Mark this epoch as posted
                            self.last_posted_epoch = int(epoch)
                        except Exception as monitor_err:
                            # Don't let monitor errors break training
                            logger.debug(f"Monitor progress post failed: {monitor_err}")
                    
                    # NEW: Add epoch projection generation (if available)
                    if self.embedding_space is not None and self.epoch_projection_callback is not None:
                        training_event_dict['embedding_space'] = self.embedding_space
                        # Call epoch projection callback
                        self.epoch_projection_callback(training_event_dict)
                    
                except Exception as err:
                    logger.error("❌ Error during saving job progress or epoch projections:")
                    logger.error(f"   Exception type: {type(err).__name__}")
                    logger.error(f"   Exception message: {str(err)}")
                    logger.error("   Full traceback:")
                    logger.error(traceback.format_exc())
        
        # Create the callback instance
        callback = TrainingCallback(args, epoch_projection_callback, kv_fold_offset=kv_fold_offset)

        # Ensure ideal_batch_size is available (import at top may not be in scope)
        batch_size = ideal_batch_size(len(input_data_file.df)) #args.batch_size or 1024
        # reset_device() was removed - device is set at module level now
        using_cpu = False
        es = None  # Initialize es before try block so it's in scope for return
        logger.info(f"@@@ batch_size = {batch_size}; epochs = {args.epochs}; using_cpu = {using_cpu}")
        
        # Check GPU memory before starting training - prevents OOM errors
        check_gpu_memory_preflight(min_free_gb=10.0)
        
        try:
            import torch
            if is_gpu_available():
                empty_gpu_cache()
                synchronize_gpu()

            epochs = args.epochs or 0 #if using_cpu == False else int(args.epochs / 4)
            logger.info(f"@@@ ... specified epochs = {epochs}")
            if epochs == 0:
                logger.info("...getting ideal epochs for embedding space")
                epochs = ideal_epochs_embedding_space(len(input_data_file.df), batch_size)
                logger.info(f"@@@ ... ideal epochs = {epochs}")

            logger.info(f"@@@ batch_size = {batch_size}; epochs = {epochs}; using_cpu = {using_cpu}")
            
            # Pass JSON transformations to EmbeddingSpace for consistent encoding
            if args.json_transformations:
                logger.info(f"🔧 Passing JSON transformations to EmbeddingSpace:")
                for orig_col, transform_info in args.json_transformations.items():
                    logger.info(f"   • {orig_col} → {len(transform_info.get('expanded_columns', []))} expanded columns")
            
            # Get version info for ES metadata
            try:
                version_info = get_version()
                logger.info(f"📦 Embedding version info: {version_info}")
            except Exception as e:
                logger.warning(f"Failed to get version info: {e}")
                version_info = None
            
            # Create or resume embedding space
            # Check if we should load existing ES from session (for extension)
            # First, check for resume_epoch to determine if we should load existing ES
            resume_epoch_check = None
            if hasattr(args, 'resume_from_epoch') and args.resume_from_epoch is not None:
                resume_epoch_check = args.resume_from_epoch
            elif hasattr(args, 'job_spec') and args.job_spec:
                resume_epoch_check = args.job_spec.get('resume_from_epoch')
            
            existing_es_path = None
            if resume_epoch_check is not None:
                # Check if there's an existing ES in the working directory (copied by job runner)
                from featrix.neural.embedding_space_utils import find_embedding_space_pickle
                existing_es_path = find_embedding_space_pickle(Path("."))
                if existing_es_path:
                    logger.info(f"📂 Found existing ES in working directory for resume: {existing_es_path}")
            
            if resume_from_es is not None:
                logger.info(f"🔄 Resuming training from existing EmbeddingSpace (passed as parameter)")
                es = resume_from_es
                # Update data for this fold
                es.train_data = train_input_data
                es.val_data = val_input_data
                # Store K-fold offset so timeline entries use cumulative epochs
                es._kv_fold_epoch_offset = kv_fold_offset
            elif existing_es_path and existing_es_path.exists():
                # Load existing ES from file (for extension scenarios)
                logger.info(f"🔄 Loading existing EmbeddingSpace from {existing_es_path} for resume")
                es = load_embedded_space(str(existing_es_path))
                # Update data with new combined data
                es.train_input_data = train_input_data
                es.val_input_data = val_input_data
                # Update output directory to current job directory
                es.output_dir = os.getcwd()
            elif hasattr(args, 'parent_embedding_space_path') and args.parent_embedding_space_path:
                # Fine-tuning: Load parent embedding space and initialize new one from it
                logger.info(f"🎯 Fine-tuning: Loading parent embedding space from {args.parent_embedding_space_path}")
                
                parent_es_path = Path(args.parent_embedding_space_path)
                # Path should already be resolved by featrix_queue.py, but check if it exists
                if not parent_es_path.exists():
                    raise FileNotFoundError(f"Parent embedding space not found at: {parent_es_path}")
                
                parent_es = load_embedded_space(str(parent_es_path))
                if not parent_es:
                    raise ValueError(f"Failed to load parent embedding space from: {parent_es_path}")
                
                logger.info(f"✅ Loaded parent embedding space with {len(parent_es.train_input_data)} original training rows")
                
                # Create new embedding space using parent's encoder/model
                # We need to use the parent's codecs and encoder config
                logger.info(f"🔧 Creating new embedding space from parent for fine-tuning...")
                
                # Get parent's encoder config and codecs
                parent_encoder_config = parent_es.encoder_config if hasattr(parent_es, 'encoder_config') else None
                parent_codecs = parent_es.col_codecs if hasattr(parent_es, 'col_codecs') else {}
                parent_string_cache = parent_es.string_cache if hasattr(parent_es, 'string_cache') else None
                parent_json_transformations = parent_es.json_transformations if hasattr(parent_es, 'json_transformations') else {}
                parent_required_child_es_mapping = parent_es.required_child_es_mapping if hasattr(parent_es, 'required_child_es_mapping') else {}
                
                # Create new embedding space with parent's configuration
                # Validate user_metadata for fine-tuning
                validated_user_metadata = validate_and_prepare_user_metadata(args)
                
                es = EmbeddingSpace(
                    train_input_data=train_input_data,
                    val_input_data=val_input_data,
                    output_debug_label=f"Fine-tuned from {parent_es_path.name}",
                    n_epochs=epochs,
                    d_model=parent_es.d_model if hasattr(parent_es, 'd_model') else None,
                    encoder_config=parent_encoder_config,
                    string_cache=parent_string_cache,
                    json_transformations=parent_json_transformations,
                    version_info=version_info,
                    output_dir=os.getcwd(),
                    user_metadata=validated_user_metadata,
                    name=args.name or f"Fine-tuned {parent_es.name if hasattr(parent_es, 'name') and parent_es.name else 'ES'}",
                    required_child_es_mapping=parent_required_child_es_mapping,
                )
                
                # Copy parent's encoder model weights to new ES
                logger.info(f"📋 Copying encoder weights from parent embedding space...")
                if hasattr(parent_es, 'encoder') and parent_es.encoder:
                    es.encoder.load_state_dict(parent_es.encoder.state_dict())
                    logger.info(f"✅ Copied encoder weights from parent")
                else:
                    logger.warning(f"⚠️  Parent embedding space has no encoder to copy")
                
                logger.info(f"✅ Created fine-tuning embedding space with {len(train_input_data)} training rows")
                logger.info(f"   ✅ Loaded ES and updated with new data (train: {len(train_input_data)}, val: {len(val_input_data)})")
            else:
                # CRITICAL: Use current working directory (which is the job-specific directory)
                # instead of falling back to global config.output_dir
                job_output_dir = os.getcwd()
                logger.info(f"📁 Creating EmbeddingSpace with output_dir: {job_output_dir}")
                
                # Get required_child_es_mapping from args for JSON column dependencies
                required_child_es_mapping = getattr(args, 'required_child_es_mapping', None) or {}
                if required_child_es_mapping:
                    logger.info(f"🔗 ES has {len(required_child_es_mapping)} child ES dependencies: {list(required_child_es_mapping.keys())}")
                
                # Find SQLite database path for PCA initialization
                sqlite_db_path = find_sqlite_db_path(args)
                
                # Get optimal ES configuration from pre-analysis or meta-learning API
                optimal_config = get_optimal_es_config(args, input_data_file)
                
                # Build ES kwargs with optimal config if available
                es_kwargs = {
                    'train_input_data': train_input_data,
                    'val_input_data': val_input_data,
                    'json_transformations': args.json_transformations,
                    'version_info': version_info,
                    'output_dir': job_output_dir,
                    'name': args.name,
                    'required_child_es_mapping': required_child_es_mapping,
                    'sqlite_db_path': sqlite_db_path,
                    'user_metadata': validated_user_metadata,
                }
                
                # Add optimal architecture params if available
                if optimal_config:
                    if 'd_model' in optimal_config:
                        es_kwargs['d_model'] = optimal_config['d_model']
                    if 'n_transformer_layers' in optimal_config:
                        es_kwargs['n_transformer_layers'] = optimal_config['n_transformer_layers']
                    if 'n_attention_heads' in optimal_config:
                        es_kwargs['n_attention_heads'] = optimal_config['n_attention_heads']
                
                es = EmbeddingSpace(**es_kwargs)
                # Store K-fold offset so timeline entries use cumulative epochs
                es._kv_fold_epoch_offset = kv_fold_offset
                
                # Generate and store dataset_hash early for progress tracking
                generate_and_register_dataset_hash(es, train_input_data)
                
                # Mark config as training started in monitor to prevent duplicate training
                if optimal_config and not resume_from_es:
                    try:
                        config_to_mark = {
                            'd_model': optimal_config.get('d_model'),
                            'n_transformer_layers': optimal_config.get('n_transformer_layers'),
                            'n_attention_heads': optimal_config.get('n_attention_heads')
                        }
                        # Only mark if we have all required fields
                        if all(config_to_mark.values()):
                            mark_config_training_started(
                                df=input_data_file.df,
                                config=config_to_mark,
                                session_id=args.session_id or args.job_id or "unknown",
                                target_type=None  # Will be auto-detected
                            )
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to mark config as training started: {e}")
                        # Don't fail training if this fails
            
            # Store job_id and session_id for tracking and movie frames
            es.job_id = args.job_id
            es.session_id = args.session_id  # Needed for async movie frame queue jobs
            es.training_info['job_id'] = args.job_id
            
            # Add CV decision to timeline if this is a new ES (not resuming)
            if cv_decision_info is not None:
                # Pre-computed CV decision info (from CV path)
                if not hasattr(es, '_training_timeline'):
                    es._training_timeline = []
                cv_timeline_entry = {
                    "epoch": 0,
                    "timestamp": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
                    "event_type": "cv_decision",
                    "description": cv_decision_info["reason"],
                    "use_cross_validation": cv_decision_info["use_cross_validation"],
                    "cv_threshold": cv_decision_info["cv_threshold"],
                    "dataset_rows": cv_decision_info["dataset_rows"]
                }
                es._training_timeline.append(cv_timeline_entry)
                logger.info(f"📊 Added CV decision to timeline: {cv_decision_info['reason']}")
            elif use_cv is False and resume_from_es is None:
                # Non-CV path - add decision entry
                if not hasattr(es, '_training_timeline'):
                    es._training_timeline = []
                n_rows = len(input_data_file.df)
                cv_timeline_entry = {
                    "epoch": 0,
                    "timestamp": datetime.now(tz=ZoneInfo("America/New_York")).isoformat(),
                    "event_type": "cv_decision",
                    "description": f"Dataset has {n_rows} rows (>= {cv_threshold} threshold) - CV disabled for large datasets",
                    "use_cross_validation": False,
                    "cv_threshold": cv_threshold,
                    "dataset_rows": n_rows
                }
                es._training_timeline.append(cv_timeline_entry)
                logger.info(f"📊 Added CV decision to timeline: CV disabled (dataset has {n_rows} rows >= {cv_threshold} threshold)")
            
            # Set the embedding space on the callback for epoch projections
            callback.set_embedding_space(es)
            
            # Set actual epoch count after auto-calculation
            callback.set_total_epochs(epochs)
            
            logger.info(f"🚀 Starting training with {len(train_input_data)} training rows, {len(val_input_data)} validation rows...")
            logger.info(f"📊 Training for {epochs} epochs with batch size {batch_size}")
            
            # Check for resume parameters from job recovery
            resume_epoch = None
            logger.info(f"🔍 Checking for resume parameters...")
            logger.info(f"   args has resume_from_epoch: {hasattr(args, 'resume_from_epoch')}")
            logger.info(f"   args has job_spec: {hasattr(args, 'job_spec')}")
            
            if hasattr(args, 'resume_from_epoch') and args.resume_from_epoch is not None:
                resume_epoch = args.resume_from_epoch
                logger.info(f"📁 Resuming training from epoch {resume_epoch} (from args.resume_from_epoch)")
            elif hasattr(args, 'job_spec') and args.job_spec:
                resume_epoch = args.job_spec.get('resume_from_epoch')
                if resume_epoch is not None:
                    logger.info(f"📁 Resuming training from epoch {resume_epoch} (from job spec)")
                else:
                    logger.info(f"ℹ️  No resume_from_epoch found in job_spec")
            else:
                logger.info(f"ℹ️  No resume parameters found - starting from epoch 1")
            
            # Additional debug: try to find resume info from job file directly
            if resume_epoch is None:
                try:
                    job_data = load_job(args.job_id)
                    job_spec = job_data.get('spec', {})
                    resume_from_spec = job_spec.get('resume_from_epoch')
                    if resume_from_spec is not None:
                        resume_epoch = resume_from_spec
                        logger.info(f"📁 Found resume_from_epoch in job file: {resume_epoch}")
                    else:
                        logger.info(f"ℹ️  No resume_from_epoch in job file spec")
                except Exception as e:
                    logger.warning(f"Failed to check job file for resume info: {e}")
            
            # CRITICAL: If resuming from ES object (K-fold CV), don't load from checkpoint
            # The ES object already has the training state, but we need to pass existing_epochs
            # to prevent architecture selection from running again
            if resume_from_es is not None:
                logger.info(f"🔄 Resuming from ES object (K-fold CV) - skipping checkpoint load")
                logger.info(f"   ES object already has training state, will continue from current state")
                # CRITICAL: Use resume_from_epoch from args to prevent architecture selection from running again
                # Architecture selection should only run on the first fold (when existing_epochs is None)
                if hasattr(args, 'resume_from_epoch') and args.resume_from_epoch is not None:
                    resume_epoch = args.resume_from_epoch
                    logger.info(f"   Using resume_from_epoch={resume_epoch} to prevent architecture selection (already selected in fold 1)")
                else:
                    resume_epoch = None  # First fold - architecture selection will run
            
            if resume_epoch is not None:
                logger.info(f"🎯 FINAL: Will resume training from epoch {resume_epoch} (loading from checkpoint)")
            else:
                if resume_from_es is not None:
                    logger.info(f"🎯 FINAL: Continuing training from ES object state (no checkpoint load needed)")
                else:
                    logger.info(f"🎯 FINAL: Starting training from epoch 1")
            
            # Build optimizer params - use learning_rate if provided, otherwise let training auto-select
            optimizer_params = {"weight_decay": 1e-4}
            if args.learning_rate is not None:
                optimizer_params["lr"] = args.learning_rate
            
            es.train(
                batch_size=batch_size,
                n_epochs=epochs,
                print_progress_step=100,
                training_event_callback=callback,
                optimizer_params=optimizer_params,
                use_lr_scheduler=True,  # Enable learning rate scheduler
                existing_epochs=resume_epoch,  # Pass resume epoch to training (prevents architecture selection on subsequent folds)
                save_state_after_every_epoch=True,  # Enable checkpointing
                enable_weightwatcher=True,  # Analyze joint_encoder component 
                weightwatcher_save_every=5,  # Default WeightWatcher interval
                weightwatcher_out_dir="ww_metrics",  # Output directory
                movie_frame_interval=3,  # Default movie frame interval
                # DropoutScheduler parameters (using defaults)
                enable_dropout_scheduler=True,
                dropout_schedule_type="linear_decay",
                initial_dropout=0.5,
                final_dropout=0.1,
                # Validation loss early stopping parameters
                val_loss_early_stop_patience=10,  # Stop if no improvement for 10 epochs
                val_loss_min_delta=0.0001,  # Minimum improvement to count as progress
                # Gradient clipping parameters
                max_grad_norm=getattr(args, 'max_grad_norm', None),
                adaptive_grad_clip_ratio=getattr(args, 'adaptive_grad_clip_ratio', None),
                # Recovery control
                disable_recovery=args.disable_recovery,  # Never resume from checkpoints if True (QA tests)
                grad_clip_warning_multiplier=getattr(args, 'grad_clip_warning_multiplier', None),
            )
            logger.info("@@@ it worked! @@@")
            logger.info("✅ Training completed successfully!")
            
            # Update job status to DONE when training completes successfully
            try:
                job_id = getattr(args, 'job_id', None)
                if job_id:
                    logger.info(f"✅ Setting job {job_id} status to DONE (training completed successfully)")
                    update_job_status(job_id=job_id, status=JobStatus.DONE)
                else:
                    logger.debug("⚠️  Cannot set job status to DONE: job_id not available (may be direct call, not via Celery)")
            except Exception as status_err:
                logger.warning(f"⚠️  Failed to set job status to DONE: {status_err}")
            
            # Generate movie metadata after successful training
            # Always try to generate movie metadata - graceful fallback if not available
            try:
                logger.info("🎬 Generating epoch projection movie metadata...")
                movie_metadata = create_projection_movie_metadata(output_dir="epoch_projections")
                if movie_metadata['movie_ready']:
                    logger.info(f"🎉 Movie ready! {movie_metadata['total_epochs']} epoch projections available for movie creation")
                    logger.info(f"   Projection files saved in: {movie_metadata['output_directory']}")
                    logger.info(f"   Movie metadata: {movie_metadata['output_directory']}/movie_metadata.json")
                else:
                    logger.info("ℹ️  Only one epoch available - need multiple epochs for movie")
            except Exception as e:
                logger.warning(f"⚠️  Failed to create movie metadata: {e}")
                logger.info("ℹ️  Check epoch_projections.py module and epoch projection files")
                    
        except (TrainingFailureException, FeatrixRestartTrainingException) as e:
            # Featrix-specific exceptions - log and re-raise
            logger.error(f"❌ Training failed: {type(e).__name__}: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
        except FeatrixTrainingAbortedException as e:
            # ABORT file detected - don't retry, fail immediately
            logger.error(f"🚫 Training aborted: {type(e).__name__}: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
        except Exception as e:
            # For non-Featrix exceptions (RuntimeError, AssertionError, etc.), don't retry
            logger.error(f"💥 Training failed with exception: {type(e).__name__}: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise

        training_worked = not es.gotInterrupted()

        # Save embedding space and create model package
        save_embedding_space_and_package(es, output_dir=os.getcwd())
        
        # Post training data to monitor and meta-learning API
        training_end_time = datetime.now()
        post_training_data_to_monitor(
            es=es,
            train_input_data=train_input_data,
            val_input_data=val_input_data,
            training_start_time=training_start_time,
            training_end_time=training_end_time,
            epochs=epochs,
            batch_size=batch_size,
            args=args
        )
        
        # Save training metadata and handle FINISH flag
        save_training_metadata_and_finish_flag(
            es=es,
            args=args,
            epochs=epochs,
            training_start_time=training_start_time
        )


    except Exception as err:
        try:
            import torch
            if is_gpu_available():
                logger.info("CUDA memory summary:")
                logger.info(get_gpu_memory_summary(abbreviated=False))
        except Exception as cuda_err:
            logger.error(f"Error while trying to print cuda memory usage: {cuda_err}")
        training_worked = False
        logger.error("Training process failed with exception:")
        logger.error(traceback.format_exc())
        
        # Post training crash to Slack
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            hostname = get_hostname()
            version_info = get_version()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Truncate long error messages for readability
            error_msg = str(err)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            
            # Make crash message very prominent with visual separators
            slack_msg =  f"═══════════════════════════════════════════════════════════\n"
            slack_msg += f"  💥 *ES TRAINING CRASHED on `{hostname}`* 💥              \n"
            slack_msg += f"═══════════════════════════════════════════════════════════\n\n"
            slack_msg += f"```\n"
            slack_msg += f"Version:   {version_info.semantic_version}\n"
            slack_msg += f"Date:      {current_time}\n"
            slack_msg += f"```\n\n"
            slack_msg += f"*Error Details:*\n"
            slack_msg += f"```\n"
            slack_msg += f"Field              Value\n"
            slack_msg += f"─────────────────────────────────────\n"
            slack_msg += f"Session ID         {args.session_id}\n"
            slack_msg += f"Job ID             {args.job_id}\n"
            slack_msg += f"Error Type         {type(err).__name__}\n"
            slack_msg += f"Error Message      {error_msg}\n"
            slack_msg += f"```\n\n"
            slack_msg += f"*Full Traceback:*\n"
            slack_msg += f"```\n"
            slack_msg += f"{traceback.format_exc()}\n"
            slack_msg += f"```"
            
            # pylint: disable=unexpected-keyword-arg
            send_slack_message(slack_msg, skip_hostname_prefix=True)
            logger.info("✅ Slack notification sent for ES training crash")
        except Exception as slack_error:
            logger.warning(f"Failed to send Slack notification for crash: {slack_error}")
        
        # Check if it's a disk space error - convert to retryable exception
        if isinstance(err, OSError) and (getattr(err, 'errno', None) == 28 or "No space left on device" in str(err) or "No space" in str(err)):
            logger.error(f"❌ Disk space error detected: {err}")
            logger.error(f"   Converting to retryable exception - job will be restarted when disk space is available")
            # Get current epoch if available
            current_epoch = 0
            if 'es' in locals() and hasattr(es, 'current_epoch'):
                current_epoch = getattr(es, 'current_epoch', 0)
            restart_config = RestartConfig(
                reason="DISK_SPACE_ERROR",
                epoch_detected=current_epoch,
                lr_multiplier=1.0,  # Don't change LR for disk space errors
                reset_optimizer_state=False,  # Don't reset optimizer
                reset_scheduler=False,
                load_best_checkpoint=False,
                metadata={"error": str(err), "error_type": type(err).__name__}
            )
            err = FeatrixRestartTrainingException(f"Disk space error: {err}", restart_config)
        
        # For non-Featrix training exceptions, set job status to FAILED and exit
        # FeatrixTrainingAbortedException is a Featrix exception (explicit abort, not a retryable failure)
        if not isinstance(err, (TrainingFailureException, FeatrixRestartTrainingException, FeatrixTrainingAbortedException)):
            # Check if this is an OOM (Out of Memory) error
            error_msg = str(err).lower()
            error_type = type(err).__name__
            oom_indicators = [
                'out of memory',
                'cuda out of memory',
                'oom',
                'torch.outofmemoryerror',
                'cuda oom',
                'gpu memory',
                'memory allocation',
                'allocation failed'
            ]
            is_oom = any(indicator in error_msg for indicator in oom_indicators) or 'OutOfMemoryError' in error_type
            
            if is_oom:
                # CRITICAL: Kill all child processes FIRST, BEFORE any logging!
                # When workers crash from OOM, their pipe buffers can fill up. Any logging
                # (which writes to stdout/pipes) can block forever, causing the process to
                # hang indefinitely holding GPU memory with zombie children.
                _emergency_cleanup_before_exit()
                
                logger.error("")
                logger.error("=" * 100)
                logger.error("🚫 OUT OF MEMORY (OOM) ERROR DETECTED")
                logger.error("=" * 100)
                logger.error(f"   Error Type: {error_type}")
                logger.error(f"   Error Message: {str(err)[:500]}")
                logger.error("")
                logger.error("   ⚠️  This job will NOT be automatically retried.")
                logger.error("   ⚠️  OOM errors indicate insufficient GPU/system memory.")
                logger.error("   ⚠️  Retrying would likely fail again with the same error.")
                logger.error("")
                logger.error("   Possible solutions:")
                logger.error("   - Reduce batch_size in training configuration")
                logger.error("   - Free up GPU memory (kill other processes)")
                logger.error("   - Use a GPU with more memory")
                logger.error("   - Reduce model size (d_model, n_layers, etc.)")
                logger.error("=" * 100)
                logger.error("")
            
            try:
                # Determine queue name from job_id or args
                job_id = getattr(args, 'job_id', None)
                if job_id:
                    from lib.job_manager import determine_failure_reason
                    error_metadata = {'error': str(err), 'error_type': error_type}
                    if is_oom:
                        error_metadata['is_oom'] = True
                        error_metadata['oom_detected'] = True
                    # Determine failure reason
                    failure_reason = determine_failure_reason(exception=err, exception_type=error_type, is_oom=is_oom)
                    error_metadata['failure_reason'] = failure_reason
                    logger.error(f"❌ Setting job {job_id} status to FAILED due to non-Featrix exception")
                    update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata=error_metadata)
                else:
                    logger.warning(f"⚠️  Cannot set job status to FAILED: job_id not available")
            except Exception as status_err:
                logger.error(f"⚠️  Failed to set job status to FAILED: {status_err}")
            
            # Exit with error code
            # Use os._exit() to forcefully terminate, killing any persistent DataLoader workers
            if is_oom:
                logger.error(f"💥 Exiting due to OOM error - job will NOT be retried")
            else:
                logger.error(f"💥 Exiting due to non-Featrix training exception")
            os._exit(1)
        
        # Handle FeatrixTrainingAbortedException - mark job as FAILED and exit
        if isinstance(err, FeatrixTrainingAbortedException):
            try:
                job_id = getattr(args, 'job_id', None)
                if job_id:
                    from lib.job_manager import determine_failure_reason
                    failure_reason = determine_failure_reason(is_user_abort=True)
                    logger.info(f"🚫 Setting job {job_id} status to FAILED due to training abort")
                    update_job_status(job_id=job_id, status=JobStatus.FAILED, metadata={'failure_reason': failure_reason})
                else:
                    logger.warning(f"⚠️  Cannot set job status to FAILED: job_id not available")
            except Exception as status_err:
                logger.error(f"⚠️  Failed to set job status to FAILED: {status_err}")
            
            # Exit with error code
            logger.error(f"💥 Exiting due to training abort")
            os._exit(1)
        
        # Handle FeatrixRestartTrainingException - check if it's a disk space error
        if isinstance(err, FeatrixRestartTrainingException):
            restart_config = err.restart_config
            if restart_config.reason == "DISK_SPACE_ERROR":
                # For disk space errors, reset job to READY so it can be retried
                try:
                    job_id = getattr(args, 'job_id', None)
                    if job_id:
                        logger.info(f"🔄 Resetting job {job_id} to READY for disk space retry")
                        update_job_status(job_id=job_id, status=JobStatus.READY)
                        logger.info(f"   Job will be retried when disk space is available")
                    else:
                        logger.warning(f"⚠️  Cannot reset job status to READY: job_id not available")
                except Exception as status_err:
                    logger.error(f"⚠️  Failed to reset job status to READY: {status_err}")
                
                # Exit cleanly (not as error) so job can be retried
                # Use os._exit() to forcefully terminate, killing any persistent DataLoader workers
                logger.info(f"💤 Exiting - job will be retried when disk space is available")
                os._exit(0)
        
        # Re-raise other Featrix training exceptions (they may be retried differently)
        raise err
    logger.debug(f"training_worked = {training_worked}")
    
    # Check if training was interrupted by FINISH flag - if so, mark as DONE, not FAILED
    was_finish_flag = False
    if 'es' in locals():
        try:
            progress_info = es.training_info.get("progress_info", {})
            interrupted_reason = progress_info.get("interrupted", None)
            if interrupted_reason == "FINISH file detected":
                was_finish_flag = True
        except Exception:
            pass
    
    if not training_worked:
        if was_finish_flag:
            # Training was interrupted by FINISH flag - mark as DONE (successful completion)
            try:
                job_id = getattr(args, 'job_id', None)
                if job_id:
                    logger.info(f"✅ Setting job {job_id} status to DONE (training completed via FINISH flag)")
                    update_job_status(job_id=job_id, status=JobStatus.DONE)
                else:
                    logger.warning(f"⚠️  Cannot set job status to DONE: job_id not available")
            except Exception as status_err:
                logger.error(f"⚠️  Failed to set job status to DONE: {status_err}")
            # Return successfully - don't raise exception
            if 'es' in locals():
                return es
            else:
                raise Exception("Training failed: embedding space was not created")
        else:
            # Set job status to FAILED before raising
            try:
                job_id = getattr(args, 'job_id', None)
                if job_id:
                    logger.error(f"❌ Setting job {job_id} status to FAILED due to training failure")
                    update_job_status(job_id=job_id, status=JobStatus.FAILED)
                else:
                    logger.warning(f"⚠️  Cannot set job status to FAILED: job_id not available")
            except Exception as status_err:
                logger.error(f"⚠️  Failed to set job status to FAILED: {status_err}")
            
            raise Exception("Training failed")
    
    # Return the trained embedding space
    if 'es' not in locals():
        raise Exception("Training failed: embedding space was not created")
    
    # Final check: Ensure job status is set to DONE if training succeeded
    # (This is a safety net in case the status update above was missed)
    if training_worked:
        try:
            job_id = getattr(args, 'job_id', None)
            if job_id:
                # Check current status - only update if not already DONE
                job_data = load_job(job_id)
                if job_data and job_data.get('status') != JobStatus.DONE.value:
                    logger.info(f"✅ Final check: Setting job {job_id} status to DONE (training completed)")
                    update_job_status(job_id=job_id, status=JobStatus.DONE)
        except Exception as status_err:
            logger.debug(f"Could not update job status in final check: {status_err}")
    
    return es


def extend_es(args: LightTrainingArgs):
    """Extend an existing embedding space with new feature columns.
    
    This function loads an existing ES, downloads enriched training/validation data with new columns,
    and creates an extended ES that includes codecs for the new columns while preserving existing weights.
    """
    logger = logging.getLogger(__name__)
    
    # Print version info
    try:
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        print_version_banner("Featrix Sphere Extend ES")
        version_info = get_version()
        logger.info(f"📦 Extend ES Version: {version_info.semantic_version} (git: {version_info.git_hash[:8] if version_info.git_hash else 'unknown'})")
    except Exception as e:
        logger.warning(f"⚠️ Could not load version info: {e}")
    
    training_start_time = datetime.now()
    
    logger.info("=" * 100)
    logger.info("🚀 EXTEND ES STARTED")
    logger.info("=" * 100)
    logger.info(f"⏰ Start Time: {training_start_time.isoformat()}")
    logger.info(f"🔑 Session ID: {args.session_id}")
    logger.info(f"🆔 Job ID: {args.job_id}")
    logger.info(f"📂 Input File: {args.input_file}")
    logger.info(f"🔢 Epochs: {args.epochs}")
    
    # Load session to get parent ES path
    from lib.session_manager import load_session
    session = load_session(args.session_id)
    if not session:
        raise ValueError(f"Session {args.session_id} not found")
    
    parent_es_path = session.get("parent_embedding_space_path")
    if not parent_es_path or not Path(parent_es_path).exists():
        raise FileNotFoundError(f"Parent embedding space not found: {parent_es_path}")
    
    logger.info(f"📂 Parent ES path: {parent_es_path}")
    
    # Load parent ES
    from featrix.neural.io_utils import load_embedded_space
    logger.info("📥 Loading parent embedding space...")
    parent_es = load_embedded_space(parent_es_path, force_cpu=False)
    
    # Load enriched training/validation data
    logger.info(f"📥 Loading enriched training data from: {args.input_file}")
    import pandas as pd
    train_df = pd.read_csv(args.input_file)
    
    # Load validation data (should be in same directory)
    val_file = Path(args.input_file).parent / f"{Path(args.input_file).stem}_validation.csv"
    if not val_file.exists():
        # Try alternate naming
        val_file = Path(args.input_file).with_name("validation_data.csv")
    
    if not val_file.exists():
        raise FileNotFoundError(f"Validation data not found: {val_file}")
    
    logger.info(f"📥 Loading validation data from: {val_file}")
    val_df = pd.read_csv(val_file)
    
    logger.info(f"📊 Training data: {len(train_df)} rows, {len(train_df.columns)} columns")
    logger.info(f"📊 Validation data: {len(val_df)} rows, {len(val_df.columns)} columns")
    
    # Extend the embedding space
    from featrix.neural.embedded_space import EmbeddingSpace
    logger.info("🔧 Extending embedding space with new features...")
    
    output_dir = str(Path(args.input_file).parent / "extended_es")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    extended_es = EmbeddingSpace.extend_from_existing(
        existing_es=parent_es,
        enriched_train_df=train_df,
        enriched_val_df=val_df,
        n_epochs=args.epochs,
        output_dir=output_dir,
        name=f"{parent_es.name}_extended"
    )
    
    logger.info(f"✅ Extended ES created with {len(extended_es.col_codecs)} columns")
    
    # Save extended ES
    from featrix.neural.embedding_space_utils import write_embedding_space_pickle
    output_path = str(Path(args.input_file).parent / "embedding_space.pkl")
    logger.info(f"💾 Saving extended ES to: {output_path}")
    write_embedding_space_pickle(extended_es, str(Path(args.input_file).parent), filename="embedding_space.pkl")
    
    # Update session with extended ES path
    from lib.session_manager import save_session
    session["embedding_space"] = output_path
    save_session(args.session_id, session)
    
    # Update job status
    try:
        from lib.job_manager import JobStatus, update_job_status
        if args.job_id:
            update_job_status(job_id=args.job_id, status=JobStatus.DONE)
            logger.info(f"✅ Job {args.job_id} marked as DONE")
    except Exception as e:
        logger.warning(f"⚠️  Could not update job status: {e}")
    
    logger.info("=" * 100)
    logger.info("✅ EXTEND ES COMPLETED")
    logger.info("=" * 100)
    
    return extended_es




if __name__ == "__main__":
    print("Starting up!")

    args = LightTrainingArgs()

    train_es(args=args)
