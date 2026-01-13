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

try:
    from featrix.neural import device
except ModuleNotFoundError:
    p = Path(__file__).parent
    sys.path.insert(0, str(p))
    from featrix.neural import device

from featrix.neural.embedded_space import EmbeddingSpace

from featrix.neural.input_data_file import FeatrixInputDataFile
from featrix.neural.input_data_set import FeatrixInputDataSet

# from vector_db import CSVToFAISS

# Import standardized logging configuration
from featrix.neural.logging_config import configure_logging
configure_logging()

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

from render_sphere import write_preview_image

from featrix.neural.io_utils import load_embedded_space
import sqlite3
import json

import pandas as pd
from featrix.neural.es_projection import ESProjection

import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert NumPy array to list
        return super().default(obj)

def run_clustering(model_path, sqlite_db_path):
    import os
    import sys
    print("=" * 80, flush=True)
    print("🚨🚨🚨 RUN_CLUSTERING FUNCTION CALLED 🚨🚨🚨", flush=True)
    print(f"   model_path: {model_path}", flush=True)
    print(f"   sqlite_db_path: {sqlite_db_path}", flush=True)
    print(f"   PID: {os.getpid()}", flush=True)
    print(f"   CWD: {os.getcwd()}", flush=True)
    print("=" * 80, flush=True)

    # Logging is already configured via logging_config.py at module import
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("🚨🚨🚨 RUN_CLUSTERING FUNCTION CALLED 🚨🚨🚨")
    logger.info(f"   model_path: {model_path}")
    logger.info(f"   sqlite_db_path: {sqlite_db_path}")
    logger.info(f"   PID: {os.getpid()}")
    logger.info(f"   PPID: {os.getppid()}")
    logger.info(f"   Current working directory: {os.getcwd()}")
    logger.info(f"   Python executable: {sys.executable}")
    logger.info(f"   Python version: {sys.version}")
    logger.info("=" * 80)

    # DEBUGGING: Comment out everything and just return HELLO WORLD
    logger.info("🔧 DEBUGGING MODE: Commenting out all actual work, just logging HELLO WORLD")
    logger.info("HELLO WORLD - run_clustering function executed successfully!")
    print("HELLO WORLD - run_clustering function executed successfully!", flush=True)
    logger.info("=" * 80)
    logger.info("✅ DEBUGGING: run_clustering returning early with dummy output")
    logger.info("=" * 80)
    
    return {
        "projections": "DEBUGGING - HELLO WORLD",
        "preview_png": "DEBUGGING - HELLO WORLD",
        "status": "success",
        "message": "This is a debugging run - actual work is commented out"
    }

    # ============================================================================
    # COMMENTED OUT FOR DEBUGGING - UNCOMMENT WHEN READY TO TEST ACTUAL WORK
    # ============================================================================
    # logger.info(f"🔧 DEBUGGING: About to load embedding space...")
    # logger.info(f"   model_path: {model_path}")
    # logger.info(f"   model_path exists: {os.path.exists(model_path) if model_path else 'N/A'}")
    # es = load_embedded_space(model_path)
    # logger.info(f"✅ Successfully loaded embedding space")
    # logger.info(f"   EmbeddingSpace type: {type(es)}")
    # 
    # logger.info(f"🔧 DEBUGGING: About to connect to SQLite database...")
    # logger.info(f"   sqlite_db_path: {sqlite_db_path}")
    # logger.info(f"   sqlite_db_path exists: {os.path.exists(sqlite_db_path) if sqlite_db_path else 'N/A'}")
    # sql_conn = sqlite3.connect(sqlite_db_path)
    # assert sql_conn is not None
    # logger.info(f"✅ Connected to SQLite database")
    # 
    # logger.info(f"🔧 DEBUGGING: About to read data from SQLite...")
    # df = pd.read_sql_query("SELECT rowid AS __featrix_row_id, * from data ORDER BY rowid", sql_conn)
    # logger.info(f"✅ Read {len(df)} rows from SQLite")
    # 
    # logger.info(f"🔧 DEBUGGING: About to create ESProjection instance...")
    # projection = ESProjection(es=es, df=df, sqlite_conn=sql_conn)
    # logger.info(f"✅ Created ESProjection instance")
    # 
    # logger.info(f"🔧 DEBUGGING: About to call projection.run()...")
    # projection_js = projection.run()
    # logger.info(f"✅ projection.run() completed")
    # logger.info(f"   projection_js type: {type(projection_js)}")
    # logger.info(f"   projection_js keys: {list(projection_js.keys()) if isinstance(projection_js, dict) else 'N/A'}")
    # 
    # logger.info(f"🔧 DEBUGGING: About to write projections JSON...")
    # with open("embedded_space_projections.json", "w") as fp:
    #     json.dump(projection_js, fp, cls=NumpyEncoder)
    # logger.info(f"✅ Wrote embedded_space_projections.json")
    # 
    # assert os.path.exists("embedded_space_projections.json")
    # logger.info(f"✅ Verified embedded_space_projections.json exists")
    # 
    # sphere_file = "sphere_preview.png"
    # logger.info(f"🔧 DEBUGGING: About to write preview image...")
    # try:
    #     write_preview_image("embedded_space_projections.json", sphere_file)
    #     logger.info(f"✅ Wrote preview image: {sphere_file}")
    # except Exception as img_err:
    #     logger.error(f"❌ Failed to write preview image: {img_err}")
    #     traceback.print_exc()
    #     sphere_file = None
    # 
    # logger.info(f"✅ run_clustering completed successfully")
    # return { "projections": "embedded_space_projections.json", "preview_png": sphere_file }


if __name__ == "__main__":
    print("Starting up!")
    import sys
    if len(sys.argv) < 3:
        print("Usage: python es_projections.py <model_path> <sqlite_db_path>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    sqlite_db_path = sys.argv[2]
    run_clustering(model_path, sqlite_db_path)


