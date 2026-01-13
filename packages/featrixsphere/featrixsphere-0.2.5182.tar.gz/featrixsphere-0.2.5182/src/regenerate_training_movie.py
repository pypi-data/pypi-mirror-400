#!/usr/bin/env python3
"""
Regenerate Training Movie Tool

Regenerates epoch projection files and training movie metadata after training has completed.
Useful for creating movies with different visualization preferences without re-training.

Usage:
    python regenerate_training_movie.py --job-dir /path/to/train_es_job --important-columns customer_name revenue
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
import shutil

# Add lib paths for imports
lib_path = Path(__file__).parent / "lib"
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

from featrix.neural.io_utils import load_embedded_space

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)-45s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_embedding_space(job_dir):
    """Load the trained embedding space from job directory."""
    
    es_pickle = Path(job_dir) / "embedded_space.pickle"
    
    if not es_pickle.exists():
        raise FileNotFoundError(f"Embedding space not found: {es_pickle}")
    
    logger.info(f"📦 Loading embedding space from {es_pickle}")
    es = load_embedded_space(str(es_pickle), force_cpu=True, skip_datasets=True)
    
    logger.info(f"✅ Embedding space loaded")
    return es


def load_training_data(job_dir):
    """Load the training data (SQLite DB or CSV)."""
    # First try SQLite database (preferred)
    sqlite_db = Path(job_dir) / "final_data.db"
    if sqlite_db.exists():
        logger.info(f"📊 Loading training data from SQLite: {sqlite_db}")
        import pandas as pd
        import sqlite3
        
        conn = sqlite3.connect(sqlite_db)
        df = pd.read_sql_query("SELECT * FROM data", conn)
        conn.close()
        logger.info(f"✅ Loaded {len(df)} rows from SQLite")
        return df
    
    # Fall back to CSV
    csv_files = list(Path(job_dir).glob("*.csv"))
    if csv_files:
        csv_file = csv_files[0]
        logger.info(f"📊 Loading training data from CSV: {csv_file}")
        import pandas as pd
        df = pd.read_csv(csv_file)
        logger.info(f"✅ Loaded {len(df)} rows from CSV")
        return df
    
    raise FileNotFoundError(f"No training data found in {job_dir}")


def find_movie_data_snapshot(job_dir):
    """Find the movie data snapshot file saved during training."""
    # Look for movie_data_snapshot.json in job directory
    snapshot_path = Path(job_dir) / "movie_data_snapshot.json"
    if snapshot_path.exists():
        logger.info(f"📸 Found movie data snapshot: {snapshot_path}")
        return snapshot_path
    
    # Also check in checkpoint directories
    checkpoint_dirs = list(Path(job_dir).glob("checkpoint_*"))
    for checkpoint_dir in checkpoint_dirs:
        snapshot_path = checkpoint_dir / "movie_data_snapshot.json"
        if snapshot_path.exists():
            logger.info(f"📸 Found movie data snapshot: {snapshot_path}")
            return snapshot_path
    
    return None


def find_checkpoint_path(job_dir, epoch):
    """Find the inference checkpoint path for a specific epoch."""
    # Checkpoint paths follow pattern: checkpoint_inference_e-{epoch}.pt
    # They can be saved in various locations:
    # 1. Job directory directly
    # 2. Checkpoint subdirectories
    # 3. Current working directory (if training_state_path was relative to cwd)
    
    # Try job directory first
    checkpoint_path = Path(job_dir) / f"checkpoint_inference_e-{epoch}.pt"
    if checkpoint_path.exists():
        return checkpoint_path
    
    # Try checkpoint subdirectories
    checkpoint_dirs = list(Path(job_dir).glob("checkpoint_*"))
    for checkpoint_dir in checkpoint_dirs:
        if checkpoint_dir.is_dir():
            checkpoint_path = checkpoint_dir / f"checkpoint_inference_e-{epoch}.pt"
            if checkpoint_path.exists():
                return checkpoint_path
    
    # Try current working directory (default training_state_path location)
    import os
    cwd_checkpoint = Path(os.getcwd()) / f"checkpoint_inference_e-{epoch}.pt"
    if cwd_checkpoint.exists():
        return cwd_checkpoint
    
    # Try recursively searching job directory
    for checkpoint_file in Path(job_dir).rglob(f"checkpoint_inference_e-{epoch}.pt"):
        if checkpoint_file.exists():
            return checkpoint_file
    
    return None


def load_es_from_checkpoint(checkpoint_path):
    """Load and reconstruct embedding space from epoch checkpoint."""
    import torch
    import pandas as pd
    from featrix.neural.embedded_space import EmbeddingSpace
    from featrix.neural.input_data_set import FeatrixInputDataSet
    
    logger.info(f"📦 Loading checkpoint from {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    
    # Extract embedding_space from checkpoint
    embedding_space = checkpoint.get("embedding_space")
    
    # If checkpoint has lightweight format (encoder + codecs), reconstruct minimal embedding_space
    if embedding_space is None:
        encoder = checkpoint.get("encoder")
        if encoder is None:
            raise ValueError("Checkpoint must contain 'embedding_space' or 'encoder'")
        
        # Create dummy input data (empty, we don't need the actual dataframes)
        dummy_train = FeatrixInputDataSet(df=pd.DataFrame(), standup_only=True)
        dummy_val = FeatrixInputDataSet(df=pd.DataFrame(), standup_only=True)
        
        # Reconstruct embedding_space with saved components
        embedding_space = EmbeddingSpace(
            train_input_data=dummy_train,
            val_input_data=dummy_val,
            encoder_config=checkpoint.get('encoder_config'),
            d_model=checkpoint.get('d_model')
        )
        # Restore the encoder and codecs
        embedding_space.encoder = encoder
        embedding_space.col_codecs = checkpoint.get('col_codecs', {})
        embedding_space.col_order = checkpoint.get('col_order', [])
        embedding_space.column_spec = checkpoint.get('column_spec', {})
        embedding_space.json_transformations = checkpoint.get('json_transformations', {})
        embedding_space.required_child_es_mapping = checkpoint.get('required_child_es_mapping', {})
    
    # Move everything to CPU and eval mode
    embedding_space.encoder.cpu()
    embedding_space.encoder.eval()
    
    logger.info(f"✅ Model loaded on CPU")
    return embedding_space


def regenerate_projections(job_dir, es, output_dir, save_every=1):
    """
    Regenerate epoch projection files using epoch-specific checkpoints.
    
    This loads the actual checkpoint for each epoch and encodes the saved data snapshot
    with that epoch's model, showing the true training progression.
    
    Args:
        job_dir: Job directory containing checkpoints and data snapshot
        es: Final trained EmbeddingSpace (for getting training info)
        output_dir: Directory to save projections
        save_every: Generate projection for every N epochs
    """
    import torch
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    epoch_projections_dir = output_dir / "epoch_projections"
    epoch_projections_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"🎬 Regenerating epoch projections from checkpoints")
    logger.info(f"   Output directory: {output_dir}")
    logger.info(f"   Save every: {save_every} epoch(s)")
    
    # 1. Find the movie data snapshot (saved rows)
    snapshot_path = find_movie_data_snapshot(job_dir)
    if not snapshot_path:
        raise FileNotFoundError(
            f"Movie data snapshot not found in {job_dir}. "
            f"This file is created during training. Cannot regenerate projections without it."
        )
    
    # Load data snapshot
    logger.info(f"📸 Loading data snapshot from {snapshot_path}")
    with open(snapshot_path, 'r') as f:
        data_snapshot = json.load(f)
    
    df = pd.DataFrame(data_snapshot['records'])
    logger.info(f"✅ Loaded {len(df)} records from snapshot")
    
    # Get total epochs from training info
    total_epochs = es.training_info.get('n_epochs', 100)
    logger.info(f"📊 Model was trained for {total_epochs} epochs")
    
    # Find which epochs have checkpoints
    epochs_with_checkpoints = []
    for epoch in range(1, total_epochs + 1):
        if epoch % save_every == 0 or epoch == total_epochs:
            checkpoint_path = find_checkpoint_path(job_dir, epoch)
            if checkpoint_path:
                epochs_with_checkpoints.append((epoch, checkpoint_path))
    
    logger.info(f"🎬 Found {len(epochs_with_checkpoints)} checkpoints to process")
    
    if not epochs_with_checkpoints:
        raise FileNotFoundError(
            f"No epoch checkpoints found in {job_dir}. "
            f"Checkpoints are saved during training as checkpoint_inference_e-{{epoch}}.pt"
        )
    
    # Process each epoch
    for epoch_idx, checkpoint_path in epochs_with_checkpoints:
        logger.info(f"📸 Processing epoch {epoch_idx}/{total_epochs} from {checkpoint_path.name}")
        
        try:
            # 2. Load the epoch-specific ES
            es_epoch = load_es_from_checkpoint(checkpoint_path)
            
            # 3. Encode the saved rows with this epoch's ES
            coords_3d = []
            rowids = []
            row_offsets = []
            set_columns_matrix = []
            scalar_columns_matrix = []
            string_columns_matrix = []
            
            # Get column info from embedding space
            set_columns_names = es_epoch.get_set_columns() if hasattr(es_epoch, 'get_set_columns') else {}
            scalar_columns_names = es_epoch.get_scalar_columns() if hasattr(es_epoch, 'get_scalar_columns') else {}
            string_columns_names = es_epoch.get_string_column_names() if hasattr(es_epoch, 'get_string_column_names') else []
            
            for idx, row in df.iterrows():
                try:
                    rowids.append(row.get('__featrix_row_id', idx))
                    row_offsets.append(idx)
                    
                    # 4. Encode on CPU using short (3D) embedding
                    with torch.no_grad():
                        embedding_short = es_epoch.encode_record(row, short=True, output_device=torch.device("cpu"))
                    
                    # Get the 3D points
                    coords_3d.append([
                        embedding_short[0].item(),
                        embedding_short[1].item(),
                        embedding_short[2].item()
                    ])
                    
                    # Extract column data for metadata
                    orig_set_data = {}
                    orig_scalar_data = {}
                    orig_string_data = {}
                    
                    for k, v in row.items():
                        if k in set_columns_names:
                            orig_set_data[k] = v
                        elif k in scalar_columns_names:
                            orig_scalar_data[k] = v
                        elif k in string_columns_names:
                            orig_string_data[k] = v
                    
                    set_columns_matrix.append(orig_set_data)
                    scalar_columns_matrix.append(orig_scalar_data)
                    string_columns_matrix.append(orig_string_data)
                    
                except Exception as e:
                    logger.warning(f"Failed to encode record {idx} in epoch {epoch_idx}: {e}")
                    continue
            
            # 5. Save the projection
            projection_df = pd.DataFrame(coords_3d, columns=['0', '1', '2'])
            projection_df['__featrix_row_id'] = rowids
            projection_df['__featrix_row_offset'] = row_offsets
            projection_df['set_columns'] = set_columns_matrix
            projection_df['scalar_columns'] = scalar_columns_matrix
            projection_df['string_columns'] = string_columns_matrix
            projection_df['cluster_pre'] = 0
            projection_df = projection_df.rename(columns={"0": "x", "1": "y", "2": "z"})
            
            projection_data = {
                'coords': json.loads(projection_df.to_json(orient='records')),
                'epoch': epoch_idx,
                'timestamp': datetime.utcnow().isoformat(),
                'sample_size': len(coords_3d),
                'total_records': data_snapshot['total_records'],
                'encoding_duration_seconds': 0,  # Not tracking for regeneration
                'cluster_messages': {},
                'is_epoch_projection': True,
                'entire_cluster_results': {},
                'consistent_sampling': True,
                'row_ids_for_tracking': rowids,
                'generated_from_checkpoint': True,
                'checkpoint_path': str(checkpoint_path)
            }
            
            output_file = epoch_projections_dir / f"projections_epoch_{epoch_idx:03d}.json"
            with open(output_file, "w") as fp:
                json.dump(projection_data, fp, indent=2)
            
            logger.info(f"✅ Saved: {output_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process epoch {epoch_idx}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue
    
    logger.info(f"🎉 Regeneration complete!")
    return output_dir


def create_movie_metadata(output_dir):
    """Create training movie metadata JSON."""
    from epoch_projections import create_projection_movie_metadata
    
    logger.info(f"🎬 Creating movie metadata")
    metadata_file = create_projection_movie_metadata(output_dir=str(output_dir))
    
    if metadata_file:
        logger.info(f"✅ Movie metadata created: {metadata_file}")
    else:
        logger.warning(f"❌ Failed to create movie metadata")
    
    return metadata_file


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate training movie projections with different visualization preferences"
    )
    parser.add_argument(
        "--job-dir",
        required=True,
        help="Path to training job directory (contains embedded_space.pickle)"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for projections (default: job_dir/epoch_projections_regenerated)"
    )
    parser.add_argument(
        "--important-columns",
        nargs="+",
        default=None,
        help="[DEPRECATED] Column names to prioritize (not used - uses saved snapshot)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=500,
        help="[DEPRECATED] Max samples (not used - uses saved snapshot)"
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=1,
        help="Generate projection for every N epochs (default: 1 = every epoch)"
    )
    parser.add_argument(
        "--backup-original",
        action="store_true",
        help="Backup original epoch_projections directory before regenerating"
    )
    
    args = parser.parse_args()
    
    # Validate job directory
    job_dir = Path(args.job_dir)
    if not job_dir.exists():
        logger.error(f"❌ Job directory not found: {job_dir}")
        return 1
    
    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = job_dir / "epoch_projections_regenerated"
    
    # Backup original if requested
    if args.backup_original:
        original_dir = job_dir / "epoch_projections"
        if original_dir.exists():
            backup_dir = job_dir / "epoch_projections_backup"
            logger.info(f"💾 Backing up original projections to {backup_dir}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(original_dir, backup_dir)
            logger.info(f"✅ Backup complete")
    
    try:
        # Load embedding space (needed for training info like n_epochs)
        es = load_embedding_space(job_dir)
        
        # Regenerate projections using epoch checkpoints
        regenerate_projections(
            job_dir=job_dir,
            es=es,
            output_dir=output_dir,
            save_every=args.save_every
        )
        
        # Create movie metadata
        create_movie_metadata(output_dir)
        
        logger.info(f"")
        logger.info(f"{'='*80}")
        logger.info(f"✅ SUCCESS: Training movie regenerated!")
        logger.info(f"{'='*80}")
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info(f"🎬 Movie metadata: {output_dir}/movie_metadata.json")
        logger.info(f"")
        logger.info(f"Next steps:")
        logger.info(f"  1. View projections in output directory")
        logger.info(f"  2. Use movie_metadata.json to create visualization")
        logger.info(f"  3. Compare with original projections if needed")
        logger.info(f"{'='*80}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

