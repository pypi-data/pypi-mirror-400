#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import copy

import logging
import sys
import os
from pathlib import Path
from typing import List
import time
import traceback

# CRITICAL: Set up Python path FIRST before any imports
# This ensures config.py and other modules can be found
lib_path = Path(__file__).parent
current_path = lib_path.parent

if str(lib_path.resolve()) not in sys.path:
    sys.path.insert(0, str(lib_path.resolve()))
if str(current_path.resolve()) not in sys.path:
    sys.path.insert(0, str(current_path.resolve()))

# CRITICAL: Redirect stderr to stdout IMMEDIATELY so all errors/crashes go to one log
# BUT: Save original stderr first so celery_app can restore it
if not hasattr(sys, '_original_stderr_saved'):
    sys._original_stderr_saved = sys.stderr
sys.stderr = sys.stdout
print("🔧 STDERR REDIRECTED TO STDOUT - all output in one place!", flush=True)
print(f"📍 TRACE: knn_training.py module-level code executing (import in progress)", flush=True)
print(f"📍 TRACE: PID={os.getpid()}, PPID={os.getppid()}", flush=True)


print(f"📍 TRACE: PID={os.getpid()}, About to import featrix.neural.device...", flush=True)
try:
    from featrix.neural import device
    print(f"📍 TRACE: PID={os.getpid()}, Successfully imported featrix.neural.device", flush=True)
except ModuleNotFoundError:
    p = Path(__file__).parent
    sys.path.insert(0, str(p))
    from featrix.neural import device
    print(f"📍 TRACE: PID={os.getpid()}, Successfully imported featrix.neural.device (after path fix)", flush=True)

print(f"📍 TRACE: PID={os.getpid()}, About to import EmbeddingSpace (this is a large import)...", flush=True)
print(f"📍 TRACE: PID={os.getpid()}, About to execute: from featrix.neural.embedded_space import EmbeddingSpace", flush=True)
print(f"📍 TRACE: PID={os.getpid()}, Current time: {time.time()}", flush=True)
import_start = time.time()
try:
    print(f"📍 TRACE: PID={os.getpid()}, Executing import statement NOW...", flush=True)
    from featrix.neural.embedded_space import EmbeddingSpace
    import_duration = time.time() - import_start
    print(f"📍 TRACE: PID={os.getpid()}, Import statement completed after {import_duration:.2f}s, EmbeddingSpace class available", flush=True)
    print(f"📍 TRACE: PID={os.getpid()}, EmbeddingSpace type: {type(EmbeddingSpace)}", flush=True)
    print(f"📍 TRACE: PID={os.getpid()}, Successfully imported EmbeddingSpace", flush=True)
except Exception as import_err:
    import_duration = time.time() - import_start
    print(f"❌ CRITICAL: PID={os.getpid()}, Exception during EmbeddingSpace import after {import_duration:.2f}s: {import_err}", flush=True)
    print(f"❌ Traceback: {traceback.format_exc()}", flush=True)
    raise
except KeyboardInterrupt:
    import_duration = time.time() - import_start
    print(f"❌ CRITICAL: PID={os.getpid()}, Import interrupted after {import_duration:.2f}s", flush=True)
    raise

print(f"📍 TRACE: PID={os.getpid()}, About to import FeatrixInputDataFile...", flush=True)
from featrix.neural.input_data_file import FeatrixInputDataFile
print(f"📍 TRACE: Successfully imported FeatrixInputDataFile", flush=True)

print(f"📍 TRACE: About to import FeatrixInputDataSet...", flush=True)
from featrix.neural.input_data_set import FeatrixInputDataSet
print(f"📍 TRACE: Successfully imported FeatrixInputDataSet", flush=True)

print(f"📍 TRACE: About to import CSVtoLanceDB...", flush=True)
from vector_db import CSVtoLanceDB
print(f"📍 TRACE: Successfully imported CSVtoLanceDB", flush=True)

# Import standardized logging configuration
print(f"📍 TRACE: About to configure logging...", flush=True)
from featrix.neural.logging_config import configure_logging
configure_logging()
print(f"📍 TRACE: Logging configured, module import complete", flush=True)

logger = logging.getLogger(__name__)


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


from featrix.neural.io_utils import load_embedded_space
from featrix.neural.embedding_space_utils import find_embedding_space_pickle

# #sys.path.append(".")

# class LightTrainingArgs:
#     epochs: int = 500
#     row_limit: int = 25000
#     is_production: bool = True
#     input_file: str = "test.csv"
#     ignore_cols: List[str] = []
#     learning_rate: float = 0.001
#     batch_size: int = 1024

def train_knn(es_path: Path, sqlite_db_path: Path, job_id: str = None):
    print("=" * 80, flush=True)
    print("🚨🚨🚨 TRAIN_KNN FUNCTION CALLED 🚨🚨🚨", flush=True)
    print(f"   es_path: {es_path}", flush=True)
    print(f"   sqlite_db_path: {sqlite_db_path}", flush=True)
    print(f"   job_id: {job_id}", flush=True)
    print(f"   PID: {os.getpid()}", flush=True)
    print(f"   CWD: {os.getcwd()}", flush=True)
    print("=" * 80, flush=True)

    # Logging is already configured via logging_config.py at module import
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🚨🚨🚨 TRAIN_KNN FUNCTION CALLED 🚨🚨🚨")
    logger.info(f"   es_path: {es_path}")
    logger.info(f"   sqlite_db_path: {sqlite_db_path}")
    logger.info(f"   job_id: {job_id}")
    logger.info(f"   PID: {os.getpid()}")
    logger.info(f"   PPID: {os.getppid()}")
    logger.info(f"   Current working directory: {os.getcwd()}")
    logger.info(f"   Python executable: {sys.executable}")
    logger.info(f"   Python version: {sys.version}")
    logger.info("=" * 80)

    # DEBUGGING: Comment out everything and just return HELLO WORLD
    logger.info("🔧 DEBUGGING MODE: Commenting out all actual work, just logging HELLO WORLD")
    logger.info("HELLO WORLD - train_knn function executed successfully!")
    print("HELLO WORLD - train_knn function executed successfully!", flush=True)
    logger.info("=" * 80)
    logger.info("✅ DEBUGGING: train_knn returning early with dummy output")
    logger.info("=" * 80)
    
    return {
        "vector_db": "DEBUGGING - HELLO WORLD",
        "status": "success",
        "message": "This is a debugging run - actual work is commented out"
    }

    # ============================================================================
    # COMMENTED OUT FOR DEBUGGING - UNCOMMENT WHEN READY TO TEST ACTUAL WORK
    # ============================================================================
    # # KNN training runs on CPU (doesn't need GPU)
    # # Device is already handled by gpu_utils
    # logger.info("🖥️  KNN training running on CPU (GPU not needed for vector DB operations)")
    # 
    # # load the ES...
    # # Use resolve function to handle both embedding_space.pickle and embedded_space.pickle
    # logger.info(f"🔧 DEBUGGING: About to resolve embedding space path...")
    # logger.info(f"   Original es_path: {es_path}")
    # from featrix.neural.embedding_space_utils import resolve_embedding_space_path
    # resolved_path = resolve_embedding_space_path(es_path)
    # logger.info(f"   Resolved path: {resolved_path}")
    # if not resolved_path:
    #     raise FileNotFoundError(f"Embedding space not found at {es_path} or in parent directory")
    # 
    # actual_es_path = str(resolved_path)
    # logger.info(f"📁 Loading embedding space from: {actual_es_path}")
    # logger.info(f"   Path exists: {Path(actual_es_path).exists()}")
    # logger.info(f"   Path size: {Path(actual_es_path).stat().st_size if Path(actual_es_path).exists() else 'N/A'} bytes")
    # es = load_embedded_space(actual_es_path)
    # logger.info(f"✅ Successfully loaded embedding space")
    # logger.info(f"   EmbeddingSpace type: {type(es)}")
    # 
    # logger.info(f"📁 SQLite DB path: {sqlite_db_path}")
    # logger.info(f"📁 SQLite DB exists: {Path(sqlite_db_path).exists()}")
    # if Path(sqlite_db_path).exists():
    #     logger.info(f"   SQLite DB size: {Path(sqlite_db_path).stat().st_size} bytes")
    # 
    # logger.info(f"🔧 Creating CSVtoLanceDB instance...")
    # logger.info(f"   About to call CSVtoLanceDB.__init__()...")
    # try:
    #     vector_db = CSVtoLanceDB(featrix_es=es, sqlite_db_path=sqlite_db_path, job_id=job_id)
    #     logger.info(f"✅ Successfully created CSVtoLanceDB instance")
    #     logger.info(f"   vector_db type: {type(vector_db)}")
    # except Exception as e:
    #     logger.error(f"❌ Failed to create CSVtoLanceDB instance: {type(e).__name__}: {e}")
    #     import traceback
    #     logger.error(f"Traceback: {traceback.format_exc()}")
    #     raise
    # 
    # logger.info(f"🔧 Calling vector_db.create_table()...")
    # logger.info(f"   About to call vector_db.create_table() method...")
    # try:
    #     vector_db.create_table()
    #     logger.info(f"✅ Successfully created LanceDB table")
    # except Exception as e:
    #     logger.error(f"❌ Failed to create LanceDB table: {type(e).__name__}: {e}")
    #     import traceback
    #     logger.error(f"Traceback: {traceback.format_exc()}")
    #     raise
    # 
    # logger.info(f"✅ KNN training completed successfully")
    # 
    # logger.info(f"🔧 Getting output files from vector_db...")
    # output_files = vector_db.get_output_files()
    # logger.info(f"📁 Output files: {output_files}")
    # logger.info(f"   Output files type: {type(output_files)}")
    # logger.info(f"   Output files keys: {list(output_files.keys()) if isinstance(output_files, dict) else 'N/A'}")
    # 
    # return output_files


if __name__ == "__main__":
    print("Starting up!")
    train_knn(
        es_path=Path("embedded_space.pickle"),
        sqlite_db_path=Path("test.csv")    
    )


