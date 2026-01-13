#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
import logging
import math
import os
import random
from typing import Dict

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from pydantic import BaseModel
from torch import nn

from featrix.neural.gpu_utils import (
    get_device,
    is_gpu_available,
    aggressive_clear_gpu_cache,
    get_gpu_memory_allocated,
    get_gpu_memory_reserved,
    get_max_gpu_memory_allocated,
    empty_gpu_cache,
)

def _log_gpu_memory_encoders(context: str = ""):
    """Quick GPU memory logging for tracing memory usage in encoders."""
    try:
        if not is_gpu_available():
            return
        allocated = get_gpu_memory_allocated()
        reserved = get_gpu_memory_reserved()
        logger.info(f"📊 GPU [{context}]: Alloc={allocated:.2f}GB Reserved={reserved:.2f}GB")
    except Exception:
        pass
from featrix.neural.featrix_token import TokenStatus
from featrix.neural.featrix_module_dict import FeatrixModuleDict
from featrix.neural.model_config import ColumnEncoderConfigType
from featrix.neural.model_config import ColumnType
from featrix.neural.model_config import FeatrixTableEncoderConfig
from featrix.neural.model_config import JointEncoderConfig
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.scalar_codec import ScalarCodec
from featrix.neural.scalar_codec import ScalarEncoder
from featrix.neural.set_codec import SetCodec
from featrix.neural.set_codec import SetEncoder
from featrix.neural.setlist_codec import ListOfASetEncoder
from featrix.neural.setlist_codec import ListsOfASetCodec
from featrix.neural.simple_mlp import SimpleMLP
# from featrix.neural.stopwatch import StopWatch
from featrix.neural.string_codec import StringCodec
from featrix.neural.string_codec import StringEncoder
from featrix.neural.transformer_encoder import JointEncoder
from featrix.neural.vector_codec import VectorCodec
from featrix.neural.vector_codec import VectorEncoder

# Import hybrid encoders for type checking in parameter counts
try:
    from featrix.neural.hybrid_encoders import AddressHybridEncoder, CoordinateHybridEncoder
    HYBRID_ENCODERS_AVAILABLE = True
except ImportError:
    HYBRID_ENCODERS_AVAILABLE = False
    AddressHybridEncoder = None
    CoordinateHybridEncoder = None

logger = logging.getLogger(__name__)


def compute_ranking_metrics(logits: torch.Tensor) -> Dict[str, float]:
    """
    Compute three ranking-aligned metrics from InfoNCE logits.
    
    Args:
        logits: (batch_size, batch_size) similarity matrix where logits[i, j] is the
                similarity between row i (context) and row j (sample).
                Diagonal elements (logits[i, i]) are positive pairs.
                Off-diagonal elements are negative pairs.
    
    Returns:
        Dictionary with:
        - 'positive_rank_mean': Mean rank of positive logit (1 = best, batch_size = worst)
        - 'positive_rank_median': Median rank of positive logit
        - 'recall_at_1': Fraction of rows where positive is top-1
        - 'recall_at_5': Fraction of rows where positive is in top-5
        - 'margin_mean': Mean margin (positive_logit - max_negative_logit) per row
        - 'margin_pct_positive': Fraction of rows where margin > 0
        - 'auc': AUC score (probability that random positive > random negative)
    """
    batch_size = logits.shape[0]
    device = logits.device
    
    # Extract diagonal (positive logits) and off-diagonal (negatives)
    positive_logits = logits.diag()  # (batch_size,)
    
    # For each row, get the rank of the positive logit
    # Rank 1 = best, rank batch_size = worst
    ranks = []
    recall_at_1_count = 0
    recall_at_5_count = 0
    margins = []
    margin_positive_count = 0
    
    for i in range(batch_size):
        row_logits = logits[i, :]  # (batch_size,)
        
        # Rank: how many negatives have higher logit than positive?
        # Use argsort to get sorted indices, then find position of diagonal element
        sorted_indices = torch.argsort(row_logits, descending=True)
        rank = (sorted_indices == i).nonzero(as_tuple=True)[0].item() + 1  # 1-indexed
        ranks.append(rank)
        
        # Recall@k: is positive in top-k?
        if rank == 1:
            recall_at_1_count += 1
        if rank <= 5:
            recall_at_5_count += 1
        
        # Margin: positive - max(negatives)
        # Get all logits except the diagonal
        mask_off_diag = torch.arange(batch_size, device=device) != i
        negative_logits = row_logits[mask_off_diag]
        if len(negative_logits) > 0:
            max_negative = negative_logits.max().item()
            margin = positive_logits[i].item() - max_negative
            margins.append(margin)
            if margin > 0:
                margin_positive_count += 1
    
    # Compute metrics
    ranks_array = np.array(ranks)
    positive_rank_mean = float(ranks_array.mean())
    positive_rank_median = float(np.median(ranks_array))
    recall_at_1 = recall_at_1_count / batch_size
    recall_at_5 = recall_at_5_count / batch_size
    
    margins_array = np.array(margins) if margins else np.array([0.0])
    margin_mean = float(margins_array.mean())
    margin_pct_positive = margin_positive_count / batch_size if batch_size > 0 else 0.0
    
    # AUC: Flatten all positives and negatives, compute AUC
    # This is equivalent to: P(positive > negative) when sampling randomly
    positive_flat = positive_logits.detach().cpu().numpy()
    
    # Sample negatives (all off-diagonal elements, but sample if too many)
    mask_off_diag_full = ~torch.eye(batch_size, dtype=torch.bool, device=device)
    negative_flat = logits[mask_off_diag_full].detach().cpu().numpy()
    
    # If too many negatives, sample for efficiency
    if len(negative_flat) > 10000:
        indices = np.random.choice(len(negative_flat), size=10000, replace=False)
        negative_flat = negative_flat[indices]
    
    # Compute AUC: fraction of (positive, negative) pairs where positive > negative
    # This is a simple approximation: count how many negatives each positive beats
    auc_sum = 0.0
    for pos_val in positive_flat:
        auc_sum += (negative_flat < pos_val).sum() / len(negative_flat)
    auc = auc_sum / len(positive_flat)
    
    return {
        'positive_rank_mean': positive_rank_mean,
        'positive_rank_median': positive_rank_median,
        'recall_at_1': recall_at_1,
        'recall_at_5': recall_at_5,
        'margin_mean': margin_mean,
        'margin_pct_positive': margin_pct_positive,
        'auc': auc,
    }


def _token_status_to_binary_mask(token_status_mask: torch.Tensor) -> torch.Tensor:
    """
    Convert TokenStatus mask to binary mask for relationship extractor.
    
    Args:
        token_status_mask: (batch_size, n_cols) tensor of TokenStatus values
            - TokenStatus.OK (2) or TokenStatus.MARGINAL (3) → 1 (present)
            - TokenStatus.NOT_PRESENT (0) or TokenStatus.UNKNOWN (1) → 0 (masked)
    
    Returns:
        Binary mask (batch_size, n_cols) where 1 = present, 0 = masked
    """
    # OK (2) and MARGINAL (3) are considered present
    # NOT_PRESENT (0) and UNKNOWN (1) are masked
    binary_mask = (token_status_mask >= TokenStatus.OK).float()
    return binary_mask


# FIXME: I think these functions can all go away by standardizing the Codec
# FIXME: constructor to (df_col, detector) and let the codec ask the detector
# FIXME: for whatever it needs--uniques, metadata will have been calculated by
# FIXME: the detector. [MH 27 Sep 2023]
def create_set_codec(df_col, embed_dim, loss_type="cross_entropy", detector=None, string_cache=None, vocabulary_override=None):
    """
    Create a SetCodec for a column.
    
    Args:
        df_col: DataFrame column to extract vocabulary from
        embed_dim: Embedding dimension
        loss_type: Loss type for training
        detector: Column detector (for sparsity info)
        string_cache: String cache path for semantic initialization
        vocabulary_override: Optional set of vocabulary members to use instead of extracting from df_col.
                            This is used when reconstructing from checkpoint to ensure vocabulary matches.
    """
    # If vocabulary override is provided, use it directly (for checkpoint reconstruction)
    if vocabulary_override is not None:
        uniques = set(vocabulary_override)
        logger.debug(f"   Using vocabulary override: {len(uniques)} members")
    else:
        # Convert all values in the column to strings.
        # TODO: how will this affect encoding values from other dataframes
        # that have the same column? We will need to make sure the same pre-processing
        # is applied to both.
        df_col = df_col.astype(str)
        
        # CRITICAL: Normalize numeric strings to prevent "1" vs "1.0" from being different classes
        # This ensures that 1, 1.0, "1", "1.0" all become "1"
        def normalize_numeric_string(val):
            if pd.isna(val) or val in ['nan', 'NaN', 'None', '', ' ']:
                return val
            try:
                # Try to convert to float, then back to int if it's a whole number
                float_val = float(val)
                if float_val.is_integer():
                    return str(int(float_val))
                return str(float_val)
            except (ValueError, TypeError):
                # Not numeric, return as-is
                return str(val)
        
        df_col_normalized = df_col.apply(normalize_numeric_string)
        uniques = set(df_col_normalized.unique())
    
    # Calculate sparsity ratio from detector (if available) or from data
    sparsity_ratio = 0.0
    if detector is not None and hasattr(detector, '_numNulls'):
        # Use pre-calculated null counts from detector
        total_count = detector._numNulls + detector._numNotNulls
        if total_count > 0:
            sparsity_ratio = float(detector._numNulls) / float(total_count)
    else:
        # Fallback: calculate from data (for backward compatibility)
        null_values = {"nan", "NaN", "Nan", "NAN", "None", "none", "NONE", "", " "}
        null_count = df_col.isin(null_values).sum()
        total_count = len(df_col)
        sparsity_ratio = float(null_count / total_count) if total_count > 0 else 0.0
    
    # print("@@@@@@@ uniques = ", uniques)
    return SetCodec(uniques, embed_dim, loss_type=loss_type, sparsity_ratio=sparsity_ratio, string_cache=string_cache)


def create_scalar_codec(df_col, embed_dim):
    # Convert scalar columns to floats.
    # This converts nan values to float("nan").
    df_col = df_col.astype(float, errors="ignore")
    
    # Compute rich statistics for adaptive encoding
    df_clean = df_col.dropna()
    
    if len(df_clean) == 0:
        # All NaN column - use dummy stats
        stats = {
            'mean': 0.0,
            'std': 1.0,
            'median': 0.0,
            'q10': 0.0,
            'q90': 1.0,
            'q25': 0.0,
            'q75': 1.0,
            'min': 0.0,
            'max': 1.0,
        }
    else:
        stats = {
            'mean': float(df_clean.mean()),
            'std': float(df_clean.std()) if len(df_clean) > 1 else 1.0,
            'median': float(df_clean.median()),
            'q10': float(df_clean.quantile(0.10)),
            'q90': float(df_clean.quantile(0.90)),
            'q25': float(df_clean.quantile(0.25)),
            'q75': float(df_clean.quantile(0.75)),
            'min': float(df_clean.min()),
            'max': float(df_clean.max()),
        }
    
    return ScalarCodec(stats, embed_dim)


def create_timestamp_codec(df_col, embed_dim):
    """
    Create a TimestampCodec for timestamp columns.
    
    Args:
        df_col: DataFrame column with datetime values
        embed_dim: Embedding dimension
        
    Returns:
        TimestampCodec instance
    """
    from featrix.neural.timestamp_codec import TimestampCodec
    return TimestampCodec(enc_dim=embed_dim)


# def create_lists_of_a_set_codec(df_col, detector, embed_dim):
#     df_col = df_col.astype(str)
#     uniques = set(df_col.unique())
#     return ListsOfASetCodec(uniques, detector.get_delimiter(), embed_dim)


def create_string_codec(df_col, detector, embed_dim, string_cache, sentence_model=None, validation_df_col=None):
    """
    Create StringCodec with adaptive string analysis.
    
    Analyzes the column to detect:
    - Random strings (UUIDs, hashes) → mark as random
    - Delimited fields ("a,b,c") → preprocess with newlines
    - Null variants ("N/A", "none") → handled by semantic similarity
    
    Args:
        df_col: DataFrame column from training data
        detector: Column detector
        embed_dim: Embedding dimension
        string_cache: Path to string cache
        sentence_model: BERT model for analysis (optional)
        validation_df_col: Optional DataFrame column from validation data (to ensure all values are cached)
    """
    from featrix.neural.string_analysis import (
        precompute_string_properties,
        detect_random_strings,
        detect_delimiter
    )
    
    col_name = detector._debugColName
    
    # Precompute all expensive operations once
    logger.info(f"🔍 Analyzing string column: '{col_name}'")
    precomputed = precompute_string_properties(df_col, col_name, sentence_model)
    
    # Check if random (UUIDs, hashes, transaction IDs)
    random_result = detect_random_strings(precomputed)
    is_random = random_result["is_random"]
    
    if is_random:
        logger.warning(f"   🚫 RANDOM STRING DETECTED (confidence: {random_result['confidence']:.2f})")
        logger.warning(f"      Signals: {', '.join(random_result['signals'][:3])}")
        logger.warning(f"      → Creating codec with ZERO contribution")
    
    # Check for delimiters - controlled by config.json
    from featrix.neural.sphere_config import get_config
    if get_config().use_delimiter_preprocessing():
        delimiter_result = detect_delimiter(precomputed)
        delimiter = delimiter_result["delimiter"] if delimiter_result["has_delimiter"] else None
        
        if delimiter:
            logger.info(f"   🔧 DELIMITER DETECTED: '{delimiter}' → will preprocess strings before BERT encoding")
    else:
        delimiter = None
        logger.debug(f"   Delimiter preprocessing disabled (config.json: use_delimiter_preprocessing=false)")
    
    # Collect unique values from BOTH training and validation data
    # This ensures all values encountered during training are cached
    train_unique_values = df_col.dropna().astype(str).unique().tolist()
    
    # Also collect from validation data if provided
    if validation_df_col is not None:
        val_unique_values = validation_df_col.dropna().astype(str).unique().tolist()
        # Combine and deduplicate
        all_unique_values = list(set(train_unique_values + val_unique_values))
        train_count = len(train_unique_values)
        val_count = len(val_unique_values)
        logger.info(f"   📊 Collected {train_count} unique values from training, {val_count} from validation")
        logger.info(f"   📊 Total unique values: {len(all_unique_values)} (after deduplication)")
    else:
        all_unique_values = train_unique_values
        logger.info(f"   📊 Collected {len(all_unique_values)} unique values from training data")
    
    # Apply delimiter preprocessing to cache keys (must match tokenize() behavior)
    if delimiter:
        from featrix.neural.string_analysis import preprocess_delimited_string
        preprocessed_values = [preprocess_delimited_string(v, delimiter) for v in all_unique_values]
        logger.info(f"   📊 Caching {len(preprocessed_values)} unique values (delimiter-preprocessed)")
    else:
        preprocessed_values = all_unique_values
        logger.info(f"   📊 Caching {len(preprocessed_values)} unique values (no delimiter preprocessing)")
    
    # Create codec with preprocessed initial values for cache
    codec = StringCodec(
        enc_dim=embed_dim,
        debugName=col_name,
        initial_values=preprocessed_values,  # Preprocessed to match tokenize() lookup keys
        string_cache=string_cache,
        delimiter=delimiter,  # Codec will apply same preprocessing during tokenize()
        is_random_column=is_random
    )
    
    # Store adaptive analysis for encoder config selection
    codec._adaptive_analysis = {
        "precomputed": precomputed,
        "is_random": is_random,
        "delimiter": delimiter,
    }
    
    return codec


def create_vector_codec(df_col, detector, embed_dim):
    in_dim_len = detector.get_input_embedding_length()
    return VectorCodec(
        in_dim=in_dim_len,
        enc_dim=embed_dim,
        # bert_encoding_length=bl,
        debugName=detector._debugColName,
    )


def create_url_codec(df_col, detector, embed_dim, string_cache):
    """
    Create URLCodec for URL/domain columns.
    
    Args:
        df_col: DataFrame column containing URLs
        detector: Column detector
        embed_dim: Embedding dimension
        string_cache: StringCache for encoding domain/path components
    """
    from featrix.neural.url_codec import URLCodec
    
    col_name = detector._debugColName
    logger.info(f"🌐 Creating URL codec for column: '{col_name}'")
    
    codec = URLCodec(
        embed_dim=embed_dim,
        string_cache=string_cache,
        debugName=col_name
    )
    
    return codec


def create_domain_codec(df_col, detector, embed_dim, string_cache):
    """
    Create DomainCodec for domain name columns.
    
    Args:
        df_col: DataFrame column containing domain names
        detector: Column detector
        embed_dim: Embedding dimension
        string_cache: StringCache for encoding domain components
    """
    from featrix.neural.domain_codec import DomainCodec
    
    col_name = detector._debugColName
    logger.info(f"🌐 Creating domain codec for column: '{col_name}'")
    
    # DomainCodec needs a StringCache instance, not just a filename
    # If string_cache is a string (filename), we need to create a StringCache
    if isinstance(string_cache, str):
        from featrix.neural.simple_string_cache import SimpleStringCache as StringCache
        cache_instance = StringCache(string_cache_filename=string_cache, readonly=False)
    else:
        cache_instance = string_cache
    
    codec = DomainCodec(
        enc_dim=embed_dim,
        string_cache=cache_instance,
        debugName=col_name
    )
    
    return codec


def create_json_codec(df_col, detector, embed_dim, json_cache_filename=None, child_es_session_id: str = None):
    """
    Create JsonCodec with ES lookup for JSON columns.
    
    Extracts schema fields from JSON values, queries API for matching ES,
    and creates JsonCodec with the ES if found.
    
    Args:
        df_col: DataFrame column with JSON values
        detector: Column detector
        embed_dim: Embedding dimension
        json_cache_filename: Path to JSON cache file
        child_es_session_id: Session ID of child ES to use for encoding (via API)
        
    Returns:
        JsonCodec instance
    """
    from featrix.neural.json_codec import JsonCodec
    import json
    import ast
    from collections import Counter
    
    col_name = detector._debugColName if hasattr(detector, '_debugColName') else "json_col"
    
    # Extract schema fields from JSON values
    schema_fields = set()
    sample_values = df_col.dropna().head(100)  # Sample first 100 non-null values
    
    for value in sample_values:
        try:
            # Parse JSON value
            if isinstance(value, str):
                value = value.strip()
                if value.startswith('{'):
                    try:
                        parsed = json.loads(value)
                    except:
                        try:
                            parsed = ast.literal_eval(value)
                        except:
                            continue
                elif value.startswith('['):
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            parsed = parsed[0]  # Use first dict
                    except:
                        try:
                            parsed = ast.literal_eval(value)
                            if isinstance(parsed, list) and len(parsed) > 0:
                                parsed = parsed[0]
                        except:
                            continue
                else:
                    continue
            elif isinstance(value, dict):
                parsed = value
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                parsed = value[0]
            else:
                continue
            
            # Extract keys from dict
            if isinstance(parsed, dict):
                schema_fields.update(parsed.keys())
        except Exception:
            continue
    
    schema_fields = sorted(list(schema_fields))
    logger.info(f"🔍 JsonCodec '{col_name}': Extracted {len(schema_fields)} schema fields: {schema_fields[:10]}{'...' if len(schema_fields) > 10 else ''}")
    
    # Query API for matching ES
    embedding_space = None
    if schema_fields:
        try:
            import requests
            from config import config as app_config
            
            # Build API URL
            api_base = getattr(app_config, 'api_base_url', 'http://localhost:8000')
            if not api_base.startswith('http'):
                api_base = f"http://{api_base}"
            
            # Query endpoint
            schema_fields_str = ','.join(schema_fields)
            url = f"{api_base}/api-sphere/json-encoders"
            params = {"schema_fields": schema_fields_str}
            
            logger.info(f"🔍 Querying JSON encoder API: {url} with fields: {schema_fields_str}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                matched_es = result.get("matched_es")
                
                if matched_es:
                    es_path = matched_es.get("embedding_space_path")
                    logger.info(f"✅ Found matching ES: {matched_es.get('name')} at {es_path}")
                    
                    # Load embedding space
                    try:
                        import pickle
                        with open(es_path, 'rb') as f:
                            embedding_space = pickle.load(f)
                        logger.info(f"✅ Loaded embedding space for JsonCodec '{col_name}'")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load ES from {es_path}: {e}")
                else:
                    logger.info(f"ℹ️ No matching ES found for schema: {schema_fields}")
            else:
                logger.warning(f"⚠️ API query failed with status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to query JSON encoder API: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    # Get initial values for caching
    initial_values = df_col.dropna().tolist()[:1000]  # Limit to first 1000 for caching
    
    # Create JsonCodec
    # Prefer child_es_session_id over embedding_space (for API calls)
    codec = JsonCodec(
        enc_dim=embed_dim,
        debugName=col_name,
        initial_values=initial_values,
        json_cache_filename=json_cache_filename,
        embedding_space=embedding_space if not child_es_session_id else None,  # Only use local ES if no child ES session
        schema_fields=schema_fields,
        child_es_session_id=child_es_session_id
    )
    
    return codec


class LayerEncoder(nn.Module):
    def __init__(self, segments):
        super().__init__()

        modules, input_lengths = list(zip(*segments))
        self.layer_modules = nn.ModuleList(modules)
        self.input_lengths = input_lengths

        self.total_length = sum(self.input_lengths)

    def forward(self, input):
        assert input.shape[1] == self.total_length, (
            "input.shape = %s; total_length = %s; input_lengths = %s"
            % (
                input.shape,
                self.total_length,
                self.input_lengths,
            )
        )

        segments = torch.split(input, self.input_lengths, dim=1)
        encodings = [
            module(segment) for module, segment in zip(self.layer_modules, segments)
        ]

        return torch.cat(encodings, dim=1)


class ColumnEncoders(nn.Module):
    # This is the first layer that takes in a dictionary-like batch, and
    # returns a completely vectorized batch.

    # NOTE: col_order can contain duplicates, e.g. when the same columns is
    # fed into multiple encoders.

    def __init__(self, col_configs, col_order, col_types, col_codecs, hybrid_groups=None):
        super().__init__()

        self.col_order = col_order
        # CRITICAL: Store col_codecs so they can be extracted during checkpoint reconstruction
        # When loading old checkpoints or reconstructing from .pth files, we need access to codecs
        self.col_codecs = col_codecs
        self.hybrid_groups = hybrid_groups or {}

        # Track which columns are merged into hybrid encoders
        self.merged_columns = set()
        self.hybrid_encoder_map = {}  # Maps column names to their hybrid group name
        
        self.encoders = FeatrixModuleDict()
        
        # Step 1: Create hybrid encoders for MERGE strategy
        if self.hybrid_groups:
            logger.info(f"🔗 HYBRID ENCODERS: Processing {len(self.hybrid_groups)} detected groups")
            
            for group_name, group_info in self.hybrid_groups.items():
                strategy = group_info.get('strategy')
                group_type = group_info.get('type')
                columns = group_info.get('columns', [])
                
                logger.info(f"   📦 {group_name}: type={group_type}, strategy={strategy}, columns={columns}")
                
                if strategy == 'merge':
                    # Create composite encoder
                    try:
                        if group_type == 'address' and HYBRID_ENCODERS_AVAILABLE:
                            # Get string cache from one of the column codecs
                            string_cache = None
                            for col in columns:
                                codec = col_codecs.get(col)
                                if hasattr(codec, 'string_cache') and codec.string_cache:
                                    from featrix.neural.string_codec import get_global_string_cache
                                    string_cache = get_global_string_cache(
                                        cache_filename=codec.string_cache,
                                        initial_values=None,
                                        debug_name=group_name
                                    )
                                    break
                            
                            # Create address encoder with same config as first column
                            first_col = columns[0]
                            col_config = col_configs[first_col]
                            
                            encoder = AddressHybridEncoder(
                                config=col_config,
                                string_cache=string_cache,
                                column_names=columns,
                                column_name=group_name
                            )
                            self.encoders[group_name] = encoder
                            self.merged_columns.update(columns)
                            
                            # Map each column to its hybrid group
                            for col in columns:
                                self.hybrid_encoder_map[col] = group_name
                            
                            logger.info(f"      ✅ Created AddressHybridEncoder: {group_name}")
                            logger.info(f"         Merged columns: {columns}")
                        
                        elif group_type == 'coordinates' and HYBRID_ENCODERS_AVAILABLE:
                            if len(columns) >= 2:
                                lat_col = columns[0]
                                long_col = columns[1]
                                
                                # Use config from first column
                                col_config = col_configs[lat_col]
                                
                                encoder = CoordinateHybridEncoder(
                                    config=col_config,
                                    lat_col=lat_col,
                                    long_col=long_col,
                                    column_name=group_name
                                )
                                self.encoders[group_name] = encoder
                                self.merged_columns.update(columns)
                                
                                # Map each column to its hybrid group
                                for col in columns:
                                    self.hybrid_encoder_map[col] = group_name
                                
                                logger.info(f"      ✅ Created CoordinateHybridEncoder: {group_name}")
                                logger.info(f"         Merged columns: {columns}")
                            else:
                                logger.warning(f"      ⚠️  Coordinates group needs 2 columns, got {len(columns)}")
                        
                        else:
                            if not HYBRID_ENCODERS_AVAILABLE:
                                logger.warning(f"      ⚠️  Hybrid encoders not available - falling back to individual encoding")
                            else:
                                logger.warning(f"      ⚠️  Unknown group type '{group_type}' - skipping")
                    
                    except Exception as e:
                        logger.error(f"      ❌ Failed to create hybrid encoder for {group_name}: {e}")
                        logger.error(f"         Falling back to individual column encoding")
                
                elif strategy == 'relationship':
                    logger.info(f"      ℹ️  RELATIONSHIP strategy - handled by JointEncoder, not ColumnEncoders")
                
                else:
                    logger.warning(f"      ⚠️  Unknown strategy '{strategy}' - skipping")
            
            if self.merged_columns:
                logger.info(f"   ✅ Total columns merged: {len(self.merged_columns)}")
                logger.info(f"      Merged: {sorted(self.merged_columns)}")
            else:
                logger.info(f"   ℹ️  No columns merged (all groups use RELATIONSHIP strategy or failed)")
        
        # Step 2: Create individual encoders for non-merged columns
        logger.info(f"🔧 Creating individual encoders for {len([c for c in col_types if c not in self.merged_columns])} columns")
        
        for col_name, col_type in col_types.items():
            # Skip columns that were merged into hybrid encoders
            if col_name in self.merged_columns:
                logger.debug(f"   ⏭️  Skipping {col_name} (merged into {self.hybrid_encoder_map[col_name]})")
                continue
            
            col_config = col_configs[col_name]
            if col_type == ColumnType.SET:
                # Pass column_name for semantic initialization
                codec = col_codecs.get(col_name)
                member_names = codec.member_names if hasattr(codec, 'member_names') else None
                # ALWAYS get string cache for semantic initialization (make all SetEncoders adaptive)
                from featrix.neural.string_codec import get_global_string_cache
                # Try to get string cache from codec, or use default global cache
                cache_filename = None
                if hasattr(codec, 'string_cache') and codec.string_cache:
                    cache_filename = codec.string_cache
                # Always get the global string cache object (will use default if filename is None)
                string_cache_obj = get_global_string_cache(
                    cache_filename=cache_filename,
                    initial_values=None,  # Values already cached during codec creation
                    debug_name=col_name
                )
                
                # ORDINAL DETECTION: Check if this SET column has ordinal semantics
                ordinal_info = None
                if member_names and len(member_names) >= 2 and len(member_names) <= 20:
                    # Only detect ordinal for reasonable cardinality (2-20 categories)
                    try:
                        from featrix.neural.llm.schema_analyzer import detect_ordinal_categories
                        ordinal_result = detect_ordinal_categories(col_name, member_names)
                        if ordinal_result.get('is_ordinal', False):
                            ordinal_info = ordinal_result
                            logger.info(f"   📊 {col_name}: ORDINAL detected (confidence={ordinal_result.get('confidence', 0):.2f})")
                            logger.info(f"      Order: {ordinal_result.get('ordered_values', [])[:5]}{'...' if len(ordinal_result.get('ordered_values', [])) > 5 else ''}")
                    except Exception as e:
                        logger.debug(f"   ⚠️  Ordinal detection failed for {col_name}: {e}")
                
                # Update config with ordinal info if detected
                if ordinal_info:
                    # Create a new config with ordinal_info added
                    config_dict = col_config.model_dump() if hasattr(col_config, 'model_dump') else col_config.__dict__.copy()
                    config_dict['ordinal_info'] = ordinal_info
                    from featrix.neural.model_config import SetEncoderConfig
                    col_config = SetEncoderConfig(**config_dict)
                
                encoder = SetEncoder(col_config, string_cache=string_cache_obj, column_name=col_name, member_names=member_names)
            elif col_type == ColumnType.SCALAR:
                # Use AdaptiveScalarEncoder with stats from codec
                codec = col_codecs[col_name]
                from featrix.neural.scalar_codec import AdaptiveScalarEncoder
                # Pass normalize flag from config to prevent double normalization
                normalize = col_config.normalize if hasattr(col_config, 'normalize') else True
                encoder = AdaptiveScalarEncoder(codec.stats, col_config.d_out, column_name=col_name, normalize=normalize)
            elif col_type == ColumnType.TIMESTAMP:
                # Use TimestampEncoder
                from featrix.neural.timestamp_codec import TimestampEncoder
                encoder = TimestampEncoder(col_config, column_name=col_name)
            elif col_type == ColumnType.FREE_STRING:
                encoder = StringEncoder(col_config, column_name=col_name)
            elif col_type == ColumnType.LIST_OF_A_SET:
                encoder = ListOfASetEncoder(col_config)
            elif col_type == ColumnType.VECTOR:
                encoder = VectorEncoder(col_config)
            elif col_type == ColumnType.URL:
                # URL codec handles its own encoding, just pass through
                codec = col_codecs[col_name]
                encoder = codec.encoder
            elif col_type == ColumnType.JSON:
                # JSON codec handles its own encoding via embedding space
                # The codec's tokenize() already produces the final embedding
                # We just need a pass-through encoder
                from featrix.neural.json_codec import JsonEncoder
                codec = col_codecs[col_name]
                encoder = JsonEncoder(col_config, codec)

            self.encoders[col_name] = encoder
    
    def __setstate__(self, state):
        """
        Restore state and validate/fix col_order if it's empty.
        This handles cases where col_order might be lost during unpickling.
        """
        logger = logging.getLogger(__name__)
        
        # DIAGNOSTIC: Log what's in the state before restoring
        col_order_in_state = state.get('col_order', 'NOT_IN_STATE')
        encoders_in_state = 'encoders' in state
        codecs_in_state = 'col_codecs' in state
        
        if col_order_in_state == 'NOT_IN_STATE':
            logger.error(f"🚨 ColumnEncoders.__setstate__: col_order is NOT IN STATE DICT!")
        elif isinstance(col_order_in_state, list) and len(col_order_in_state) == 0:
            logger.error(f"🚨 ColumnEncoders.__setstate__: col_order is EMPTY LIST in state dict!")
        else:
            logger.info(f"✅ ColumnEncoders.__setstate__: col_order found in state: {len(col_order_in_state) if isinstance(col_order_in_state, list) else 'not a list'}")
        
        logger.info(f"   State has encoders: {encoders_in_state}, codecs: {codecs_in_state}")
        if encoders_in_state and state.get('encoders'):
            encoder_count = len(state['encoders']) if hasattr(state['encoders'], '__len__') else 'unknown'
            logger.info(f"   Encoders in state: {encoder_count}")
        
        # Restore state first
        self.__dict__.update(state)
        
        # CRITICAL: Validate and fix col_order after unpickling
        # This handles cases where col_order might be empty in the pickle file
        # or lost during unpickling
        if not hasattr(self, 'col_order') or len(self.col_order) == 0:
            logger.warning(f"⚠️  ColumnEncoders.__setstate__: col_order is empty after unpickling - attempting recovery")
            
            # Try to recover from encoders (most reliable)
            if hasattr(self, 'encoders') and self.encoders and len(self.encoders) > 0:
                encoder_keys = list(self.encoders.keys())
                self.col_order = encoder_keys.copy()
                logger.warning(f"   ✅ Recovered col_order from {len(encoder_keys)} encoders during unpickling")
            # Try to recover from codecs
            elif hasattr(self, 'col_codecs') and self.col_codecs:
                codec_keys = list(self.col_codecs.keys())
                self.col_order = codec_keys.copy()
                logger.warning(f"   ✅ Recovered col_order from {len(codec_keys)} codecs during unpickling")
            else:
                logger.error(f"   ❌ Cannot recover col_order - no encoders or codecs available")
                logger.error(f"   Model is corrupted - col_order will remain empty")
    
    def get_effective_column_order(self):
        """
        Get column order with hybrid group names replacing merged columns.
        
        Example:
            Original: ['id', 'shipping_addr1', 'shipping_city', 'shipping_state', 'price']
            Effective: ['id', 'hybrid_group_1', 'price']
        
        Returns:
            List of column/group names in order
        """
        # Defensive check: ensure hybrid_groups exists (for backward compatibility with old checkpoints)
        if not hasattr(self, 'hybrid_groups'):
            self.hybrid_groups = {}
        if not hasattr(self, 'merged_columns'):
            self.merged_columns = set()
        if not hasattr(self, 'hybrid_encoder_map'):
            self.hybrid_encoder_map = {}
        
        if not self.hybrid_groups or not self.merged_columns:
            return self.col_order
        
        effective_order = []
        seen_groups = set()
        
        for col in self.col_order:
            if col in self.merged_columns:
                # This column is part of a hybrid group
                group_name = self.hybrid_encoder_map[col]
                if group_name not in seen_groups:
                    # Add the group name at the position of the first column in the group
                    effective_order.append(group_name)
                    seen_groups.add(group_name)
                # Skip the individual column
            else:
                # Regular column, keep it
                effective_order.append(col)
        
        return effective_order

    def forward(self, batch_data):
        # Defensive check: ensure hybrid-related attributes exist (for backward compatibility with old checkpoints)
        if not hasattr(self, 'hybrid_groups'):
            self.hybrid_groups = {}
        if not hasattr(self, 'merged_columns'):
            self.merged_columns = set()
        if not hasattr(self, 'hybrid_encoder_map'):
            self.hybrid_encoder_map = {}
        
        short_encoding_list = []
        full_encoding_list = []
        
        # CRITICAL: Check if col_order is empty - try to recover from encoders or codecs
        if len(self.col_order) == 0:
            logger.error(f"💥 CRITICAL: col_order is EMPTY! No columns to encode!")
            logger.error(f"   Available encoders: {list(self.encoders.keys())}")
            logger.error(f"   Batch data columns: {list(batch_data.keys())}")
            logger.error(f"   Available codecs: {list(self.col_codecs.keys()) if hasattr(self, 'col_codecs') and self.col_codecs else 'None'}")
            
            # Try to recover col_order from encoders or codecs
            recovered_col_order = None
            
            # First, try to recover from encoders (most reliable - these are the actual encoders that exist)
            if self.encoders and len(self.encoders) > 0:
                # Use encoder keys directly as col_order
                # These keys may be individual column names or hybrid group names (for MERGE strategy)
                # The get_effective_column_order() method will handle any transformations needed
                encoder_keys = list(self.encoders.keys())
                recovered_col_order = encoder_keys.copy()
                
                if recovered_col_order:
                    logger.warning(f"   ⚠️  RECOVERY: Reconstructed col_order from {len(self.encoders)} encoders")
                    logger.warning(f"   Recovered {len(recovered_col_order)} columns: {recovered_col_order[:20]}{'...' if len(recovered_col_order) > 20 else ''}")
                    self.col_order = recovered_col_order
                    logger.warning(f"   ✅ Successfully recovered col_order - continuing with encoding")
            
            # Fallback: try to recover from codecs if encoders didn't work
            if not recovered_col_order and hasattr(self, 'col_codecs') and self.col_codecs:
                codec_keys = list(self.col_codecs.keys())
                if codec_keys:
                    logger.warning(f"   ⚠️  RECOVERY: Attempting to reconstruct col_order from {len(self.col_codecs)} codecs")
                    logger.warning(f"   Codec keys: {codec_keys[:20]}{'...' if len(codec_keys) > 20 else ''}")
                    # Use codec keys as col_order (may not match encoder order exactly, but better than nothing)
                    recovered_col_order = codec_keys
                    self.col_order = recovered_col_order
                    logger.warning(f"   ⚠️  Recovered col_order from codecs - order may not match encoder order exactly")
            
            # If recovery failed, raise error
            if not recovered_col_order or len(self.col_order) == 0:
                logger.error(f"   ❌ RECOVERY FAILED: Could not reconstruct col_order from encoders or codecs")
                raise RuntimeError(
                    f"Encoder has empty col_order - cannot encode any columns. "
                    f"This indicates the encoder was saved incorrectly or the model is corrupted. "
                    f"Available encoders: {list(self.encoders.keys())}, "
                    f"Available codecs: {list(self.col_codecs.keys()) if hasattr(self, 'col_codecs') and self.col_codecs else 'None'}"
                )
        
        # Handle missing columns gracefully for fine-tuning on different datasets
        from featrix.neural.featrix_token import TokenBatch, Token
        batch_columns = set(batch_data.keys())
        missing_columns = [col for col in self.col_order if col not in batch_columns]
        
        if missing_columns:
            # Log once per column encoder instance (not every batch)
            if not hasattr(self, '_missing_columns_logged'):
                logger.warning(f"⚠️  Fine-tuning: {len(missing_columns)} columns from ES not in current data - using NULL values. Missing: {missing_columns}")
                self._missing_columns_logged = True
            
            # Create empty TokenBatch for missing columns (will use NOT_PRESENT tokens)
            # Get batch size from first available column
            batch_size = None
            for col_name in self.col_order:
                if col_name in batch_data:
                    batch_size = len(batch_data[col_name].value) if hasattr(batch_data[col_name], 'value') else len(batch_data[col_name])
                    break
            
            if batch_size is None:
                logger.error(f"💥 CRITICAL: All columns missing from batch data!")
                raise ValueError("Cannot encode: all expected columns are missing from batch data")
            
            # Create NOT_PRESENT token batches for missing columns
            for col_name in missing_columns:
                # Get the codec for this column to create proper NOT_PRESENT tokens
                encoder = self.encoders.get(col_name)
                if encoder and hasattr(encoder, 'codec') and hasattr(encoder.codec, 'get_not_present_token'):
                    # Use codec's proper NOT_PRESENT token (preserves correct dimensionality for each type)
                    not_present_token = encoder.codec.get_not_present_token()
                    null_tokens = [not_present_token] * batch_size
                else:
                    # Fallback: Create generic NOT_PRESENT tokens (None values that TokenBatch converts to NOT_PRESENT)
                    # This will create scalar tokens which may cause dimension issues for some encoder types
                    null_tokens = [None] * batch_size
                batch_data[col_name] = TokenBatch(null_tokens)
            
        # Use effective column order (which includes hybrid group names)
        effective_col_order = self.get_effective_column_order()
        
        for col_or_group_name in effective_col_order:
            encoder = self.encoders[col_or_group_name]
            
            # Check if this is a hybrid encoder
            if col_or_group_name in self.hybrid_groups:
                # This is a hybrid group - collect data from all merged columns
                group_info = self.hybrid_groups[col_or_group_name]
                columns = group_info.get('columns', [])
                
                # Create dict of column data for hybrid encoder
                group_batch_data = {col: batch_data[col] for col in columns if col in batch_data}
                
                # Call hybrid encoder with dict of column data
                short_col_encoding, full_col_encoding = encoder(group_batch_data)
            else:
                # Regular column encoder
                col_data = batch_data[col_or_group_name]
                short_col_encoding, full_col_encoding = encoder(col_data)
            
            # CRITICAL: Ensure encodings are 2D [batch_size, d_model]
            # Some encoders might accidentally return 3D tensors [batch_size, seq_len, d_model]
            if len(full_col_encoding.shape) == 3:
                logger.error(f"💥 ENCODER BUG: Column '{col_or_group_name}' encoder returned 3D tensor: {full_col_encoding.shape}")
                logger.error(f"   Encoder type: {type(encoder).__name__}")
                logger.error(f"   Expected 2D [batch_size, d_model], got 3D [batch_size, seq_len, d_model]")
                logger.error(f"   Auto-fixing by averaging over sequence dimension")
                # Fix by averaging over sequence dimension
                full_col_encoding = full_col_encoding.mean(dim=1)
                if len(short_col_encoding.shape) == 3:
                    short_col_encoding = short_col_encoding.mean(dim=1)
            
            short_encoding_list.append(short_col_encoding)
            full_encoding_list.append(full_col_encoding)

        # Create a tensor with all the token statuses
        # For hybrid groups, use status from first column in group
        status_list = []
        for col_or_group_name in effective_col_order:
            if col_or_group_name in self.hybrid_groups:
                # Use status from first column in hybrid group
                group_info = self.hybrid_groups[col_or_group_name]
                first_col = group_info['columns'][0]
                status_list.append(batch_data[first_col].status)
            else:
                status_list.append(batch_data[col_or_group_name].status)

        # return torch.stack(encoding_list, dim=1), torch.stack(status_list, dim=1)
        return short_encoding_list, full_encoding_list, status_list


class NormalizedPoolJointEncoder(nn.Module):
    """Simplest possible joint encoder."""

    def forward(self, batch):
        # Batch is a tensor of dimensions (b, n, d)
        # use keepdim=True to retain the fact that the output is a sequence of length 1
        return nn.functional.normalize(torch.sum(batch, dim=1, keepdim=True), dim=-1)


class PassThroughJointEncoder(nn.Module):
    def forward(self, batch):
        return batch


# def sample_marginal_masks(batch_mask):
#     new_mask_A = batch_mask.clone()  # Clone the original mask to create a new mask
#     new_mask_B = batch_mask.clone()

#     for i in range(batch_mask.size(0)):  # Iterate over rows
#         # Find indices where mask is not NOT_PRESENT
#         # The output looks something like
#         # This gives the indices in the row that are NOT equal to NOT_PRESENT
#         # This means that these are the indices that CAN be masked out
#         # For a row equal to [TokenStatus.NOT_PRESENT, TokenStatus.OK, TokenStatus.OK, TokenStatus.NOT_PRESENT],
#         # present will be torch.tensor([1, 2])
#         present = torch.nonzero(
#             batch_mask[i] != TokenStatus.NOT_PRESENT, as_tuple=True
#         )[0]

#         # If there is only one present token (or zero), leave the mask row as-is.
#         if len(present) > 1:
#             # Make sure at least one present token is left unmasked
#             max_selected = len(present) - 1
#             # Randomly choose number of elements to select for masking in one of the returned masks.
#             # we want to select at least one token to mask because otherwise the second mask will have no unmasked tokens.
#             min_selected = 1
#             num_to_select = random.randint(min_selected, max_selected)

#             # Randomly select indices
#             # Make sure that masks A and B are complimentary - i.e. a token that is masked in one is not masked in the other.
#             permutation = torch.randperm(len(present))
#             selected_indices_A = present[permutation[:num_to_select]]
#             selected_indices_B = present[permutation[num_to_select:]]

#             # Set the status for the selected token to MARGINAL
#             new_mask_A[i, selected_indices_A] = TokenStatus.MARGINAL
#             new_mask_B[i, selected_indices_B] = TokenStatus.MARGINAL

#     return new_mask_A, new_mask_B

# Feature flag: Set to True to use ratio-limited masking strategy
# Old strategy: Random split anywhere from 1 to n-1 columns
# New strategy: Limit masking to configurable range (default: 40-60% for balanced complementary)
TRY_NEW_MASKING = True

# Import mask bias tracker
from featrix.neural.mask_bias_tracker import get_mask_bias_tracker


def sample_marginal_masks(batch_mask, min_mask_ratio=0.40, max_mask_ratio=0.60, mean_nulls_per_row=None, col_names=None, track_bias=True):
    """
    Sample two complementary masks for marginal reconstruction.
    
    Args:
        batch_mask: Input mask tensor
        min_mask_ratio: Minimum fraction of columns to mask (default: 0.40)
        max_mask_ratio: Maximum fraction of columns to mask (default: 0.60)
        mean_nulls_per_row: Mean number of NULL columns per row (for masking constraint)
        
    Returns:
        (new_mask_A, new_mask_B, rows_skipped): Two complementary masks + count of skipped rows
        
    Masking strategies:
        - Balanced (min=0.40, max=0.60): ~50/50 split, symmetric difficulty
        - Asymmetric (min=0.10, max=0.30): 10-30% vs 70-90%, imbalanced
        - Extreme (min=0.01, max=0.99): Old strategy, very imbalanced
    
    Masking constraint:
        - If mean_nulls_per_row is provided, will NOT mask more than mean_nulls/3 columns
        - Rows with >66% nulls are SKIPPED from masking entirely (kept in batch but no marginal loss)
        - This prevents over-masking when data is already sparse
    """
    # Move the batch mask to the cpu, so we can iterate over rows on the cpu,
    # which eliminates the need to shuffle data back and forth.
    # We move all masks back to the GPU at the end of this function.
    batch_mask = batch_mask.to(torch.device("cpu"))

    # Clone the original mask to create new masks
    new_mask_A = batch_mask.clone()
    new_mask_B = batch_mask.clone()
    
    # Find indices where each row has tokens present
    # present_indices is a tensor, where each row corresponds to an INDIVIDUAL ENTRY
    # in batch_mask that does NOT correspond to a NOT_PRESENT token, and has two elements
    # that represent the index of that element in batch_mask.
    present_indices = (batch_mask != TokenStatus.NOT_PRESENT).nonzero(as_tuple=False)
    rows, cols = present_indices[:, 0], present_indices[:, 1]
    
    # Count how many columns are NOT_PRESENT (null) per row to skip sparse rows
    batch_size, n_cols = batch_mask.shape
    null_counts_per_row = (batch_mask == TokenStatus.NOT_PRESENT).sum(dim=1)
    
    # Skip masking threshold: rows with >66% nulls
    max_null_ratio = 0.66
    max_nulls_allowed = int(n_cols * max_null_ratio)
    
    # Track how many rows we skip
    rows_skipped = 0
    
    # Group by row index and perform vectorized selection of tokens to mask
    unique_rows = torch.unique(rows)
    
    for row in unique_rows:
        # CRITICAL: Skip masking if this row has too many nulls
        row_null_count = null_counts_per_row[row].item()
        if row_null_count > max_nulls_allowed:
            # Skip masking for this row - leave masks unchanged (all OK)
            # Row will be in the batch but won't contribute to marginal loss
            rows_skipped += 1
            continue
        
        # Get the column indices where tokens are present in the current row
        present = cols[rows == row]
        
        if len(present) > 1:
            # Ensure at least one token is left unmasked in one of the masks
            max_selected = len(present) - 1
            
            if TRY_NEW_MASKING:
                # NEW STRATEGY: Configurable masking ratio
                # Default 40-60% creates balanced complementary masks (~50/50 split)
                # This ensures both prediction tasks have similar difficulty
                min_to_mask = max(1, int(len(present) * min_mask_ratio))
                max_to_mask = min(max_selected, int(len(present) * max_mask_ratio))
                
                # CRITICAL: Apply null constraint - don't mask more than mean_nulls/3
                # This prevents over-masking when data is already sparse
                if mean_nulls_per_row is not None:
                    max_mask_from_nulls = int(mean_nulls_per_row / 3.0)
                    if max_mask_from_nulls > 0:
                        max_to_mask = min(max_to_mask, max_mask_from_nulls)
                
                # Ensure valid range
                if min_to_mask > max_to_mask:
                    # Fallback for very small column counts or tight null constraint
                    num_to_select = random.randint(1, max_to_mask) if max_to_mask > 0 else 1
                else:
                    num_to_select = random.randint(min_to_mask, max_to_mask)
            else:
                # OLD STRATEGY: Random split anywhere from 1 to n-1
                # Can result in very imbalanced masks (e.g., 1:199 or 100:100)
                num_to_select = random.randint(1, max_selected)
            
            # Shuffle the present indices and split them into two groups for masks A and B
            # permutation = torch.randperm(len(present), device=batch_mask.device)
            permutation = torch.randperm(len(present))
            selected_indices_A = present[permutation[:num_to_select]]
            selected_indices_B = present[permutation[num_to_select:]]
            
            # Assign MARGINAL to selected indices in each mask
            new_mask_A[row, selected_indices_A] = TokenStatus.MARGINAL
            new_mask_B[row, selected_indices_B] = TokenStatus.MARGINAL

    # Move everything back to the GPU (or CPU if forced)
    force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
    target_device = torch.device('cpu') if force_cpu else get_device()
    batch_mask = batch_mask.to(target_device)
    new_mask_A = new_mask_A.to(target_device)
    new_mask_B = new_mask_B.to(target_device)
    
    # Track mask patterns for bias analysis (if enabled)
    if track_bias:
        try:
            tracker = get_mask_bias_tracker()
            # Record masks before moving to GPU (tracker handles CPU conversion)
            tracker.record_batch(new_mask_A, new_mask_B, col_names=col_names)
        except Exception as e:
            # Don't fail masking if tracking fails
            logger.debug(f"Mask bias tracking failed: {e}")
    
    # Log if we skipped any rows (debug level to avoid spam)
    if rows_skipped > 0:
        logger.debug(f"Skipped masking on {rows_skipped}/{batch_size} rows (>{max_null_ratio:.0%} nulls)")

    return new_mask_A, new_mask_B, rows_skipped


def apply_replacement_mask(base_tensor, replacement_tensor, replacement_mask):
    # Replaces the entires in base tensor with the corresponding entries in replacement tensor.
    # Which entries are replaced is controlled by the replacement_mask tensor.

    # replacement vectors must be a (B, N, D) tensor
    # that carries replacement vectors for each column in the batch.

    batch_size, n_elements, d_features = base_tensor.shape

    assert replacement_tensor.shape == (batch_size, n_elements, d_features)
    assert replacement_mask.shape == (batch_size, n_elements, 1)

    remain_mask = replacement_mask.logical_not()

    remain = base_tensor * remain_mask
    replace = replacement_tensor * replacement_mask

    return remain + replace


class ColumnPredictor(nn.Module):
    def __init__(self, cols_in_order, col_configs):
        super().__init__()

        self.cols_in_order = cols_in_order
        self.col_predictors = FeatrixModuleDict()
        for col_name, col_config in col_configs.items():
            self.col_predictors[col_name] = SimpleMLP(col_config)

    def forward(self, joint_embeddings):
        predictions = []
        for col_name in self.cols_in_order:
            prediction = self.col_predictors[col_name](joint_embeddings)
            predictions.append(prediction)

        return predictions


class ShortColumnPredictor(nn.Module):
    """Same as ColumnPredictor, but shares a single config across all columns."""

    def __init__(self, cols_in_order, config):
        super().__init__()

        self.cols_in_order = cols_in_order
        self.col_predictors = FeatrixModuleDict()
        for col_name in cols_in_order:
            # This is just for UI and display, so we hard-code the same
            # parameters for all column.
            self.col_predictors[col_name] = SimpleMLP(config)

    def forward(self, joint_embeddings):
        predictions = []
        for col_name in self.cols_in_order:
            prediction = self.col_predictors[col_name](joint_embeddings)
            predictions.append(prediction)

        return predictions


# Should there be different objects for data-space batches (which are per-column, whether tokens or actual data),
# and encoding batches, which are just tensors?
# each tensor batch, as opposed to a column batch, would have values and status_masks, which would be 2D tensors, not
# dictionaries of elements.
# The "collate" function in DataLoader could handle much of the complexity of constructing the batch.


def get_infoNCE_targets(batch_size, shuffle_n=0):
    force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
    target_device = torch.device('cpu') if force_cpu else get_device()
    
    N = batch_size

    tensor = torch.arange(N).to(target_device)  # Tensor: [1, 2, 3, ..., N]

    if shuffle_n < 1:
        return tensor

    # # Set K, the number of elements to shuffle
    K = shuffle_n

    # # Ensure K is not greater than N
    K = min(K, N)

    # # Indices of the last K elements
    last_k_indices = torch.arange(N - K, N).to(target_device)

    # # Generate a random permutation of these indices
    shuffled_indices = last_k_indices[torch.randperm(K)]

    # # Shuffle the last K elements
    tensor[N - K :] = tensor[shuffled_indices]

    return tensor


class FeatrixTableEncoder(nn.Module):
    def __init__(self, col_codecs, config: FeatrixTableEncoderConfig, min_mask_ratio=0.40, max_mask_ratio=0.60, mean_nulls_per_row=None, hybrid_groups=None, enable_hybrid_encoders=True):
        super().__init__()

        self.config = config
        self.d_model = config.d_model
        self.min_mask_ratio = min_mask_ratio
        self.max_mask_ratio = max_mask_ratio
        self.mean_nulls_per_row = mean_nulls_per_row  # For masking constraint (don't mask more than mean_nulls/3)
        self.hybrid_groups = hybrid_groups or {}
        self.enable_hybrid_encoders = enable_hybrid_encoders
        
        # Filter hybrid groups if feature is disabled
        active_hybrid_groups = self.hybrid_groups if enable_hybrid_encoders else {}
        if not enable_hybrid_encoders and self.hybrid_groups:
            logger.info(f"🔗 HYBRID ENCODERS: Feature disabled (enable_hybrid_encoders=False)")
            logger.info(f"   Detected {len(self.hybrid_groups)} groups but not using them")

        self.column_encoder = ColumnEncoders(
            config.column_encoders_config, config.cols_in_order, config.col_types, col_codecs,
            hybrid_groups=active_hybrid_groups
        )
        
        # Get effective column order (with hybrid groups replacing merged columns)
        self.effective_col_order = self.column_encoder.get_effective_column_order()
        
        # Log the transformation
        if self.effective_col_order != config.cols_in_order:
            logger.info(f"🔗 HYBRID ENCODERS: Column order transformed")
            logger.info(f"   Original columns: {len(config.cols_in_order)}")
            logger.info(f"   Effective columns: {len(self.effective_col_order)}")
            logger.info(f"   Reduction: {len(config.cols_in_order) - len(self.effective_col_order)} columns merged")
            
            # Show which columns were replaced by which groups (first few examples)
            for group_name in active_hybrid_groups.keys():
                if group_name in self.effective_col_order:
                    group_info = active_hybrid_groups[group_name]
                    if group_info.get('strategy') == 'merge':
                        logger.info(f"   {group_name} ← {group_info['columns']}")
        else:
            logger.info(f"🔗 HYBRID ENCODERS: No column order changes (no MERGE groups active)")

        self.column_predictor = ColumnPredictor(
            cols_in_order=config.cols_in_order,
            col_configs=config.column_predictors_config,
        )
        self.short_column_predictor = ShortColumnPredictor(
            cols_in_order=config.cols_in_order,
            config=config.column_predictors_short_config,
        )

        # Use effective column order for joint encoder (includes hybrid group names)
        self.joint_encoder = JointEncoder(
            d_embed=self.d_model,
            col_names_in_order=self.effective_col_order,  # Use effective order with hybrid groups
            config=config.joint_encoder_config,
            hybrid_groups=active_hybrid_groups,  # Pass active hybrid groups to joint encoder
            enable_gradient_checkpointing=True,  # Always enable to save GPU memory
        )

        self.joint_predictor = SimpleMLP(config.joint_predictor_config)
        # This is just for UI and display, so we hard-code the parameters here.
        self.joint_predictor_short = SimpleMLP(config.joint_predictor_short_config)

        self.idx_to_col_name = {
            i: col_name for i, col_name in enumerate(config.cols_in_order)
        }
        self.col_mi_estimates = {col_name: None for col_name in config.cols_in_order}
        self.col_loss_estimates = {col_name: None for col_name in config.cols_in_order}  # Track raw losses
        self.joint_mi_estimate = None

        # TODO: create "column encoders" and "column predictors" as separate models here.
        # That's pretty much the only place they are needed I think.
        # TODO: look into what's being done in SinglePredictor - I think they use the encoders
        self.n_codecs = config.n_cols
        self.column_order = config.cols_in_order
        self.col_codecs_in_order = [
            col_codecs[col_name] for col_name in self.column_order
        ]

        # defines how much noise is applied to the sample embeddings for CPC
        # self.latent_noise = 0.01
        self.latent_noise = 0
        # We do not reduce the loss so that we can mask out loss associated with fields
        # that are NOT_PRESENT (or not in schema).
        self.ce_loss = nn.CrossEntropyLoss(reduction="none")

        # We use separate stopwatches for the encoder and loss computation becase we don't want
        # to have to synchronize the start/stop of stopwatches between encoder and loss
        # computation to retain the flexibility to use them independently, e.g. in testing.
        self.encoder_stopwatch = None #StopWatch()
        self.loss_stopwatch = None #StopWatch()
        
        # SCALAR RECONSTRUCTION: Decoders are now inside AdaptiveScalarEncoder
        # Count how many scalar columns have reconstruction enabled
        from featrix.neural.model_config import ColumnType
        scalar_decoder_count = 0
        for col_name in config.cols_in_order:
            col_type = config.col_types.get(col_name)
            if col_type == ColumnType.SCALAR:
                encoder = self.column_encoder.encoders.get(col_name)
                if encoder and hasattr(encoder, 'enable_reconstruction') and encoder.enable_reconstruction:
                    scalar_decoder_count += 1
        
        if scalar_decoder_count > 0:
            logger.info(f"🔢 SCALAR RECONSTRUCTION: {scalar_decoder_count} numeric columns have decoders enabled")

    def __setstate__(self, state):
        """Force CPU during unpickling to prevent GPU allocation."""
        logger = logging.getLogger(__name__)
        
        # Log GPU memory before unpickling
        if is_gpu_available():
            allocated_before = get_gpu_memory_allocated()
            logger.info(f"📊 FeatrixTableEncoder.__setstate__: GPU memory BEFORE: Allocated={allocated_before:.3f} GB")
        
        # Restore state
        self.__dict__.update(state)
        
        # Log GPU memory after unpickling
        if is_gpu_available():
            allocated_after = get_gpu_memory_allocated()
            logger.info(f"📊 FeatrixTableEncoder.__setstate__: GPU memory AFTER dict.update: Allocated={allocated_after:.3f} GB")
        
        # CRITICAL: Move everything to CPU if in CPU mode
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        if force_cpu:
            logger.info(f"📊 FeatrixTableEncoder.__setstate__: Moving all components to CPU")
            self.cpu()
            
            # AGGRESSIVE GPU MEMORY CLEANUP
            # Use gpu_utils function - handles all GPU type checking internally
            logger.info(f"📊 FeatrixTableEncoder.__setstate__: Aggressively freeing GPU memory...")
            memory_stats = aggressive_clear_gpu_cache(iterations=3, do_gc=True)
            
            if memory_stats:
                # Log memory stats after clearing
                final = memory_stats.get('final', {})
                allocated = final.get('allocated_gb', 0)
                reserved = final.get('reserved_gb', 0)
                logger.info(f"📊 FeatrixTableEncoder.__setstate__: GPU memory FINAL: Allocated={allocated:.3f} GB, Reserved={reserved:.3f} GB")
            else:
                logger.info(f"📊 FeatrixTableEncoder.__setstate__: GPU not available, skipped cache clearing")

    def count_model_parameters(self):
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)

        # Column and joint encoders are the parts of the model involved in inference.
        # "predictors" and encoders for "short" embeddings are not counted because they're
        # not used in inference in production.
        column_encoders_params = sum(
            p.numel() for p in self.column_encoder.parameters()
        )
        column_encoders_trainable_params = sum(
            p.numel() for p in self.column_encoder.parameters() if p.requires_grad
        )

        # Break down column encoders into regular vs hybrid
        regular_col_params = 0
        regular_col_trainable_params = 0
        hybrid_merge_params = 0
        hybrid_merge_trainable_params = 0
        hybrid_merge_count = 0
        
        if hasattr(self.column_encoder, 'encoders'):
            for col_name, encoder in self.column_encoder.encoders.items():
                encoder_params = sum(p.numel() for p in encoder.parameters())
                encoder_trainable_params = sum(p.numel() for p in encoder.parameters() if p.requires_grad)
                
                # Check if this is a hybrid encoder
                is_hybrid = False
                if HYBRID_ENCODERS_AVAILABLE and (
                    isinstance(encoder, AddressHybridEncoder) or 
                    isinstance(encoder, CoordinateHybridEncoder)
                ):
                    is_hybrid = True
                    hybrid_merge_count += 1
                
                if is_hybrid:
                    hybrid_merge_params += encoder_params
                    hybrid_merge_trainable_params += encoder_trainable_params
                else:
                    regular_col_params += encoder_params
                    regular_col_trainable_params += encoder_trainable_params

        joint_encoder_params = sum(
            p.numel() for p in self.joint_encoder.parameters() if p.requires_grad
        )
        joint_encoder_trainable_params = sum(
            p.numel() for p in self.joint_encoder.parameters() if p.requires_grad
        )
        
        # Break down joint encoder into transformer vs relationship groups
        transformer_params = joint_encoder_params
        transformer_trainable_params = joint_encoder_trainable_params
        relationship_group_params = 0
        relationship_group_trainable_params = 0
        relationship_group_count = 0
        
        if hasattr(self.joint_encoder, 'group_embeddings') and self.joint_encoder.group_embeddings is not None:
            # group_embeddings is a nn.Parameter (single tensor), not a Module
            relationship_group_params = self.joint_encoder.group_embeddings.numel()
            relationship_group_trainable_params = (
                relationship_group_params if self.joint_encoder.group_embeddings.requires_grad else 0
            )
            relationship_group_count = self.joint_encoder.group_embeddings.shape[0]  # Number of groups
            transformer_params -= relationship_group_params
            transformer_trainable_params -= relationship_group_trainable_params

        result = {
            "total_params": total_params,
            "total_trainable_params": trainable_params,
            "column_encoders_params": column_encoders_params,
            "column_encoders_trainable_params": column_encoders_trainable_params,
            "joint_encoder_params": joint_encoder_params,
            "joint_encoder_trainable_params": joint_encoder_trainable_params,
        }
        
        # Add breakdown if there are hybrid or relationship components
        if hybrid_merge_params > 0 or relationship_group_params > 0:
            result["column_encoders_breakdown"] = {
                "regular_columns": regular_col_params,
                "regular_columns_trainable": regular_col_trainable_params,
                "hybrid_merge_encoders": hybrid_merge_params,
                "hybrid_merge_trainable": hybrid_merge_trainable_params,
                "hybrid_merge_count": hybrid_merge_count,
            }
            result["joint_encoder_breakdown"] = {
                "transformer": transformer_params,
                "transformer_trainable": transformer_trainable_params,
                "relationship_groups": relationship_group_params,
                "relationship_groups_trainable": relationship_group_trainable_params,
                "relationship_group_count": relationship_group_count,
            }
        
        return result

    def get_marginal_tensor(self, batch_size):
        # Create columns of marginal embeddings, one for each codec.
        column_marginal_embeddings_list = [
            # codec.marginal_embedding.repeat(batch_size, 1)
            self.column_encoder.encoders[col_name].marginal_embedding.repeat(
                batch_size, 1
            )
            # for codec in self.col_codecs_in_order
            for col_name in self.column_order
        ]

        # Combine the columns of embeddings into a single tensor.
        # The columns are stacked side-by-side, i.e. along the first dimension.
        column_marginal_embeddings = torch.stack(column_marginal_embeddings_list, dim=1)

        return column_marginal_embeddings

    def apply_marginal_mask(self, tensor, marginal_tensor, mask):
        # We want to replace the vectors that correspond to the MARGINAL tokens in
        # the batch_mask. The batch mask is 2D (batch_size, n_cols) so we add
        # a third dimension to explicity broadcast the mask to the same shape as the
        # tensors whose values need to be replaced.
        replacement_mask = (mask == TokenStatus.MARGINAL).unsqueeze(dim=-1)

        return apply_replacement_mask(
            tensor,
            marginal_tensor,
            replacement_mask,
        )

    def infoNCE_loss(
        self,
        context_enc,
        sample_enc,
        mask=None,
        unknown_targets=False,
        random_fraction=0,
        temperature=None,
        return_logits=False,
    ):
        sample_enc = sample_enc + torch.randn_like(sample_enc) * self.latent_noise
        sample_enc = nn.functional.normalize(sample_enc, dim=1)

        # Apply temperature scaling to logits (if provided)
        if temperature is not None and temperature > 0:
            logits = context_enc @ sample_enc.T / temperature
        else:
            logits = context_enc @ sample_enc.T

        batch_size = context_enc.shape[0]
        shuffle_n = int(batch_size * random_fraction)
        targets = get_infoNCE_targets(batch_size, shuffle_n=shuffle_n)

        # If the mask indicatest that the token is not present, set
        # the corresponding logit to -inf so it does not affect the loss.
        # The columns in the logits tensor correspond to individual tokens
        # in the column for which we're computing the loss
        if mask is not None:
            # do NOT mask MARGINAL tokens becasuse marginal encodings are not
            # at all related to MARGINAL tokens because these are only
            # created for the joint encoder.

            # select all rows, but only the columns where we did not
            logits[:, mask == TokenStatus.NOT_PRESENT] = float("-inf")

        # NOTE: for columns where ALL the elements are NOT_PRESENT, e.g.
        # because the particular column does not exist in the segment
        # that the batch came from, all the entries in the `logits`
        # tensor will be float("-inf"), and therefore the loss
        # below will be torch.tensor([nan, ..., nan]) where there will
        # be as many `nan`s as there are rows in the batch.

        loss = self.ce_loss(logits, targets)

        if return_logits:
            return loss, logits
        return loss

    def compute_spread_loss(
        self, unmasked_encoding, joint_encoding_1, joint_encoding_2, temp=None, temp_multiplier=1.0
    ):
        """
        Compute spread loss with adaptive temperature.
        
        Temperature controls the sharpness of the contrastive learning objective:
        - Lower temp (e.g., 0.01) = sharper, more aggressive separation
        - Higher temp (e.g., 0.1) = softer, more forgiving of nearby embeddings
        
        Args:
            temp: Temperature value. If None, computed adaptively based on batch size and n_columns
            temp_multiplier: Multiplier applied to temperature during NO_LEARNING recovery (default 1.0)
        """
        force_cpu = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR') == '1'
        target_device = torch.device('cpu') if force_cpu else get_device()
        
        batch_size = unmasked_encoding.shape[0]
        targets = torch.arange(batch_size).to(target_device)
        
        # Compute adaptive temperature if not provided
        if temp is None:
            # Get number of columns from the encoder config
            n_columns = len(self.col_codecs_in_order)
            
            # Adaptive temperature formula:
            # - Scales with batch size: larger batches can handle sharper temp
            # - Scales with data richness: more columns = more discriminative power
            # Base temp of 0.2 (increased from 0.05 to make task harder)
            base_temp = 0.2
            
            # Batch size factor: normalize to batch_size=128
            # Larger batches → lower temp (sharper)
            batch_factor = max(0.5, min(2.0, batch_size / 128.0))
            
            # Column factor: normalize to 20 columns
            # More columns → lower temp (sharper) because embeddings are more discriminative
            column_factor = max(0.5, min(1.5, n_columns / 20.0))
            
            # Compute adaptive temp
            temp = base_temp / (batch_factor * column_factor)
        
        # Apply temp multiplier for NO_LEARNING recovery
        temp = temp * temp_multiplier
        
        # Clamp to reasonable range
        temp = max(0.01, min(0.4, temp))  # Increased max to 0.4 for multiplier support
        
        # Store temperature for logging (convert to float for JSON serialization)
        self._last_spread_temp = float(temp)

        logits_joint = unmasked_encoding @ unmasked_encoding.T / temp
        spread_loss_joint = F.cross_entropy(logits_joint, targets)

        logits_1 = joint_encoding_1 @ joint_encoding_1.T / temp
        spread_loss_1 = F.cross_entropy(logits_1, targets)

        logits_2 = joint_encoding_2 @ joint_encoding_2.T / temp
        spread_loss_2 = F.cross_entropy(logits_2, targets)

        loss_config = self.config.loss_config.spread_loss_config

        total = (
            loss_config.joint_weight * spread_loss_joint
            + loss_config.marginal_weight * spread_loss_1
            + loss_config.marginal_weight * spread_loss_2
        )

        dict = {
            "joint": spread_loss_joint.item(),
            "mask_1": spread_loss_1.item(),
            "mask_2": spread_loss_2.item(),
            "temperature": self._last_spread_temp,
        }

        return total, dict

    def update_col_mi(self, col_name, update_value):
        ema_coeff = 0.99

        old_value = self.col_mi_estimates[col_name]
        if old_value is None:
            new_value = update_value
        else:
            new_value = (1 - ema_coeff) * update_value + ema_coeff * old_value

        self.col_mi_estimates[col_name] = new_value
        
        # Update MI estimates in relationship extractor
        if hasattr(self.joint_encoder, 'update_mi_estimates'):
            self.joint_encoder.update_mi_estimates(
                self.col_mi_estimates, self.joint_mi_estimate
            )

    def update_joint_mi(self, update_value):
        ema_coeff = 0.99

        if self.joint_mi_estimate is None:
            self.joint_mi_estimate = update_value
        else:
            self.joint_mi_estimate = (
                1 - ema_coeff
            ) * update_value + ema_coeff * self.joint_mi_estimate
        
        # Update MI estimates in relationship extractor
        if hasattr(self.joint_encoder, 'update_mi_estimates'):
            self.joint_encoder.update_mi_estimates(
                self.col_mi_estimates, self.joint_mi_estimate
            )

    def compute_marginal_infoNCE_loss(
        self,
        batch_size,
        column_predictions,
        column_encodings,
        status_mask,
        update_mi=False,
    ):
        # def compute_marginal_infoNCE_loss(self, marginal_encodings, column_encodings, status_mask):
        """
        column_encodings: a 3D tensor (batch_size, n_cols, d_model)
        column_predictions: list of tensors, each tensor is of shape (batch_size, d_model)
                            There's one tensor per column in the dataset.
        """
        # We ONLY want to focus on predicting marginals that have been replaced in the
        # status mask.
        prediction_mask = status_mask == TokenStatus.MARGINAL

        # CRITICAL: Compute adaptive temperature for all marginal predictions
        # Use same formula as joint loss for consistency
        temperature = self._compute_adaptive_temperature(batch_size)

        # Compute the infoNCE loss for each marginal distribution.
        # This requries matching predictions and encodings for each column.
        mean_loss_per_column = []

        # We iterate over the codecs, extrac the relevant predictions and column encodigns, and
        # compute the average loss over the MARGINAL tokens, which signify the predictions we
        # actually need to make
        # for i, codec in enumerate(self.col_codecs_in_order):
        col_losses_dict = dict()
        for i, col_prediction in enumerate(column_predictions):
            # the shape of column_encodings is (batch_size, n_cols, model_dim)
            col_target = column_encodings[:, i, :]
            # mask shape is (batch_size, n_col). The third dimension is not present because
            # the mask is a boolean
            col_status_mask = status_mask[:, i]

            # col_losses is a 1D tensor of losses for each row
            # CRITICAL: Pass temperature to infoNCE_loss (was missing before!)
            col_losses = self.infoNCE_loss(
                col_prediction, col_target, col_status_mask, unknown_targets=False,
                temperature=temperature
            )

            # pick out the losses corresponding to the MARGINAL tokens
            col_prediction_mask = prediction_mask[:, i]
            col_prediction_losses = col_losses[col_prediction_mask]

            col_name = self.idx_to_col_name[i]

            if len(col_prediction_losses) == 0:
                # Make this a tensor for consistency - using a bare float causes issues
                # if we e.g. want to call .item() on it.
                col_loss_avg = torch.tensor(0.0)

                # If there are no predictions, which can happen e.g. for columns that are
                # not present in a particular data segment (for multi-segment datasets),
                # we do not update MI because col_loss_avg=0 is just a neural component
                # when it comes to computing gradients, but it does NOT fit in with the
                # formula used to compute mutual information.
            else:
                # This is where we average the loss across all the MARGINAL tokens,
                # i.e. across all the valid predictions.
                col_loss_avg = torch.mean(col_prediction_losses)
                
                # Store raw loss (more interpretable than derived MI score!)
                raw_loss = col_loss_avg.detach().item()
                ema_coeff = 0.99
                old_loss = self.col_loss_estimates[col_name]
                if old_loss is None:
                    self.col_loss_estimates[col_name] = raw_loss
                else:
                    self.col_loss_estimates[col_name] = (1 - ema_coeff) * raw_loss + ema_coeff * old_loss

                # Compute predictability score: how well can we predict this column from context?
                # 
                # We use a simple percentage-based score derived from loss vs random baseline:
                # - log(N) is the theoretical maximum loss for random predictions (all negatives equally likely)
                # - loss < log(N) means better than random (positive predictability)
                # - loss > log(N) means worse than random (can happen with poor temperature or model failure)
                #
                # Score formula: predictability = (log(N) - loss) / log(N) * 100
                # - 0% = random baseline (loss = log(N))
                # - 100% = perfect prediction (loss = 0)
                # - Negative = worse than random (clamped to 0 for display)
                #
                # NOTE: Temperature scaling is already applied in infoNCE_loss(), so the raw_loss
                # values are computed with the correct temperature. The theoretical maximum log(N) is
                # temperature-independent (random baseline is always log(N) regardless of temperature).
                # With proper temperature (e.g., 0.1), good learning produces losses well below log(N).
                log_n = math.log(batch_size)
                
                # Compute percentage predictability (0-100 scale, clamped)
                # Higher = more predictable from other columns
                predictability_pct = ((log_n - raw_loss) / log_n) * 100 if log_n > 0 else 0
                predictability_pct = max(0, min(100, predictability_pct))
                
                if update_mi:
                    self.update_col_mi(col_name, predictability_pct)

            col_losses_dict[col_name] = col_loss_avg.detach().item()
            mean_loss_per_column.append(col_loss_avg)

        total = sum(mean_loss_per_column)
        # sum the loss over all columns
        return total, col_losses_dict

    def _compute_adaptive_temperature(self, batch_size, temp_override=None):
        """
        Compute adaptive temperature for InfoNCE loss.
        
        Temperature controls sharpness of contrastive learning:
        - Lower temp (e.g., 0.01) = sharper, more aggressive separation
        - Higher temp (e.g., 0.2) = softer, more forgiving
        
        Args:
            batch_size: Current batch size
            temp_override: If provided, use this temperature instead of computing
            
        Returns:
            Temperature value (float)
        """
        if temp_override is not None:
            return temp_override
        
        n_columns = len(self.col_codecs_in_order)
        
        # Base temperature: reasonable default for most datasets
        base_temp = 0.1
        
        # Batch size factor: larger batches can handle sharper temp
        # Normalize to batch_size=256 (more common for real training)
        # Larger batches → more negatives → can use lower temp (sharper)
        batch_factor = max(0.7, min(1.5, batch_size / 256.0))
        
        # Column factor: more columns = more discriminative embeddings
        # Use log scaling so it doesn't blow up for large datasets
        # log(10) ≈ 1.0, log(100) ≈ 2.0, log(200) ≈ 2.3
        # This provides gentle scaling: 10 cols → 1.0×, 100 cols → 1.15×, 200 cols → 1.25×
        column_factor = 1.0 + (math.log10(max(10, n_columns)) - 1.0) * 0.15
        column_factor = max(0.8, min(1.5, column_factor))
        
        # Compute adaptive temp
        temp = base_temp / (batch_factor * column_factor)
        
        # Clamp to reasonable range
        # Lower bound: 0.05 (sharp but not too extreme)
        # Upper bound: 0.3 (soft but still learning)
        temp = max(0.05, min(0.3, temp))
        
        # Log temperature computation (only first few times to avoid spam)
        if not hasattr(self, '_temp_log_count'):
            self._temp_log_count = 0
        
        if self._temp_log_count < 10:  # Log first 10 calls
            logger.info(f"🌡️  InfoNCE Temperature: {temp:.4f} (batch={batch_size}, cols={n_columns}, "
                       f"batch_factor={batch_factor:.3f}, col_factor={column_factor:.3f})")
            self._temp_log_count += 1
        
        return temp

    def compute_joint_infoNCE_loss(
        self, joint_encoding, unmasked_encoding, short=False, temp=None, return_logits=False
    ):
        # Calculate adaptive temperature
        batch_size = joint_encoding.shape[0]
        temp = self._compute_adaptive_temperature(batch_size, temp_override=temp)
        
        if short:
            prediction = self.joint_predictor_short(joint_encoding)
        else:
            prediction = self.joint_predictor(joint_encoding)
        
        # CRITICAL: Pass temperature to infoNCE_loss
        if return_logits:
            loss, logits = self.infoNCE_loss(prediction, unmasked_encoding, temperature=temp, return_logits=True)
            return loss.mean(), logits
        return self.infoNCE_loss(prediction, unmasked_encoding, temperature=temp).mean()

    def compute_total_loss(
        self,
        batch_size,
        #
        full_joint_encodings_unmasked,
        full_joint_encodings_1,
        full_joint_encodings_2,
        #
        full_column_encodings,
        short_column_encodings,
        #
        short_joint_encodings_unmasked,
        short_joint_encodings_1,
        short_joint_encodings_2,
        #
        mask_1,
        mask_2,
        #
        full_column_predictions_1,
        full_column_predictions_2,
        full_column_predictions_unmasked,
        #
        short_column_predictions_1,
        short_column_predictions_2,
        short_column_predictions_unmasked,
        #
        rows_skipped,  # Number of rows skipped from masking (not used in loss, but matches encoder output)
        #
        temp_multiplier=1.0
    ):
        # MARGINAL LOSS
        (
            marginal_cpc_loss_1_total,
            marginal_cpc_loss_1_col_dict,
        ) = self.compute_marginal_infoNCE_loss(
            batch_size,
            full_column_predictions_1,
            full_column_encodings,
            mask_1,
            update_mi=True,
        )
        (
            marginal_cpc_loss_2_total,
            marginal_cpc_loss_2_col_dict,
        ) = self.compute_marginal_infoNCE_loss(
            batch_size,
            full_column_predictions_2,
            full_column_encodings,
            mask_2,
            update_mi=True,
        )
        # marginal_cpc_loss_unmasked = self.compute_marginal_infoNCE_loss(
        #     batch_size, full_column_predictions_unmasked, full_column_encodings, torch.ones_like(mask_2) * TokenStatus.OK,
        # )
        (
            short_marginal_cpc_loss_1_total,
            short_marginal_cpc_loss_1_col_dict,
        ) = self.compute_marginal_infoNCE_loss(
            batch_size, short_column_predictions_1, short_column_encodings, mask_1
        )
        (
            short_marginal_cpc_loss_2_total,
            short_marginal_cpc_loss_2_col_dict,
        ) = self.compute_marginal_infoNCE_loss(
            batch_size, short_column_predictions_2, short_column_encodings, mask_2
        )
        # short_marginal_cpc_loss_unmasked = self.compute_marginal_infoNCE_loss(
        #     batch_size, short_column_predictions_unmasked, short_column_encodings, torch.ones_like(mask_2) * TokenStatus.OK,
        # )

        # CRITICAL: Update relationship extractor with per-column losses (for importance calculation)
        # Average losses across all 4 views for more stable estimates
        # NOTE: Only update if training (not during validation/test)
        aggregated_col_losses = {}  # Initialize outside if block for anti-collapse loss calculation
        if self.training:
            try:
                for col_name in self.idx_to_col_name.values():
                    losses = []
                    if col_name in marginal_cpc_loss_1_col_dict:
                        loss_val = marginal_cpc_loss_1_col_dict[col_name]
                        if not (math.isnan(loss_val) or math.isinf(loss_val)):
                            losses.append(loss_val)
                    if col_name in marginal_cpc_loss_2_col_dict:
                        loss_val = marginal_cpc_loss_2_col_dict[col_name]
                        if not (math.isnan(loss_val) or math.isinf(loss_val)):
                            losses.append(loss_val)
                    if col_name in short_marginal_cpc_loss_1_col_dict:
                        loss_val = short_marginal_cpc_loss_1_col_dict[col_name]
                        if not (math.isnan(loss_val) or math.isinf(loss_val)):
                            losses.append(loss_val)
                    if col_name in short_marginal_cpc_loss_2_col_dict:
                        loss_val = short_marginal_cpc_loss_2_col_dict[col_name]
                        if not (math.isnan(loss_val) or math.isinf(loss_val)):
                            losses.append(loss_val)
                    
                    if losses:
                        aggregated_col_losses[col_name] = sum(losses) / len(losses)
                
                # Forward to joint encoder (which forwards to relationship extractor)
                # Only update if we have valid losses
                if aggregated_col_losses and hasattr(self.joint_encoder, 'update_column_losses'):
                    # Check if this was a NULL-only evaluation
                    relationship_extractor = getattr(self.joint_encoder, 'relationship_extractor', None)
                    is_null_baseline = (
                        relationship_extractor is not None and 
                        getattr(relationship_extractor, '_null_evaluation_pending', False)
                    )
                    
                    self.joint_encoder.update_column_losses(aggregated_col_losses)
                    
                    # If NULL-only, update NULL baseline EMA
                    # Note: aggregated_col_losses already aggregates across all 4 masks
                    # (full_1, full_2, short_1, short_2), matching normal loss aggregation regime.
                    # This ensures NULL baseline and normal losses use the same masking/computation,
                    # preventing systematic bias in lift calculations.
                    # CRITICAL: Both NULL baseline and normal losses run in the same train/eval mode
                    # (inherited from encoder.training), ensuring consistent dropout/training semantics.
                    if is_null_baseline and relationship_extractor is not None:
                        relationship_extractor.update_column_losses(aggregated_col_losses, is_null_baseline=True)
                        # Finalize after processing (aggregates and updates EMA)
                        relationship_extractor._finalize_null_baseline_batch()
            except Exception as e:
                # Don't break training if column loss update fails
                logger.warning(f"Failed to update column losses: {e}")

        # --- NEW: normalize over 4 views * number of active columns ---
        # each *_total is a SUM over columns of per-column mean InfoNCE.
        # we want an average over views and columns so the magnitude
        # is ~log(batch_size) instead of ~4 * n_cols * log(batch_size)
        # Count active columns in this batch (columns with at least one OK token)
        # This is more precise than using total n_cols when some columns are completely masked out
        n_cols_total = len(self.idx_to_col_name) if hasattr(self, "idx_to_col_name") else full_column_encodings.shape[1]
        
        # Count columns that have at least one OK token in any of the masks
        # mask_1 and mask_2 have shape (batch_size, n_cols)
        # A column is "active" if it has at least one OK token across all rows
        effective_n_cols = n_cols_total
        try:
            if mask_1 is not None and mask_2 is not None:
                # Check mask_1: columns with at least one OK token
                has_ok_mask1 = (mask_1 == TokenStatus.OK).any(dim=0)  # (n_cols,)
                # Check mask_2: columns with at least one OK token
                has_ok_mask2 = (mask_2 == TokenStatus.OK).any(dim=0)  # (n_cols,)
                # A column is active if it has OK tokens in either mask
                active_cols = (has_ok_mask1 | has_ok_mask2)
                effective_n_cols = active_cols.sum().item()
                # Ensure at least 1 column (safety check)
                if effective_n_cols == 0:
                    effective_n_cols = n_cols_total
        except Exception:
            # If counting fails for any reason, fall back to total columns
            effective_n_cols = n_cols_total
        
        # CRITICAL FIX: REMOVED MARGINAL LOSS NORMALIZER
        # The normalizer was dividing by 4*n_cols (e.g., 328 for 82 columns)
        # This divided GRADIENTS by 328 during backprop, preventing marginal loss from improving
        # Now we use raw loss and let the curriculum weight handle relative importance
        normalizer = 4.0 * max(1, effective_n_cols)  # Keep for logging/debugging

        marginal_loss_raw = (
            marginal_cpc_loss_1_total
            + marginal_cpc_loss_2_total
            + short_marginal_cpc_loss_1_total
            + short_marginal_cpc_loss_2_total
        )

        # NO NORMALIZATION - use raw loss (curriculum weight adjusted to compensate)
        marginal_loss = marginal_loss_raw
        
        # Store raw and normalizer in loss dict for debugging

        # marginal_loss = (
        #     marginal_cpc_loss_1_total
        #     + marginal_cpc_loss_2_total
        #     # + marginal_cpc_loss_unmasked
        #     + short_marginal_cpc_loss_1_total
        #     + short_marginal_cpc_loss_2_total
        #     # + short_marginal_cpc_loss_unmasked
        # )

        # COMPUTE SCALAR RECONSTRUCTION LOSS
        # For masked scalar columns, decode predictions and compare to actual values
        # This provides explicit training signal for numeric feature encoding
        reconstruction_loss = None
        reconstruction_col_losses = {}
        
        if self.training:
            reconstruction_losses = []
            
            # Only compute reconstruction for MARGINAL (masked) columns
            # mask_1 and mask_2 have shape (batch_size, n_cols)
            prediction_mask_1 = mask_1 == TokenStatus.MARGINAL
            prediction_mask_2 = mask_2 == TokenStatus.MARGINAL
            
            # Iterate through encoders to find those with decoders
            for col_name, encoder in self.column_encoder.encoders.items():
                # Check if this encoder has reconstruction enabled
                if not (hasattr(encoder, 'enable_reconstruction') and 
                       encoder.enable_reconstruction and 
                       encoder.decoder is not None):
                    continue
                
                # Handle featrix_ prefix mismatch between encoder keys and column_order
                # The encoder dict keys sometimes have featrix_ prefix, but column_order doesn't
                actual_col_name = col_name
                if col_name not in self.column_order:
                    # Try without featrix_ prefix if it has one
                    if col_name.startswith("featrix_") and col_name[8:] in self.column_order:
                        actual_col_name = col_name[8:]
                    # Try with featrix_ prefix if it doesn't have one
                    elif f"featrix_{col_name}" in self.column_order:
                        actual_col_name = f"featrix_{col_name}"
                    else:
                        # Column not in column_order at all (e.g., synthetic columns)
                        continue
                
                # Get decoder from encoder
                decoder = encoder.decoder
                
                # Get column index using the actual name in column_order
                col_idx = self.column_order.index(actual_col_name)
                
                # Check if this column was masked in either mask
                col_mask_1 = prediction_mask_1[:, col_idx]  # (batch_size,)
                col_mask_2 = prediction_mask_2[:, col_idx]  # (batch_size,)
                
                # Get actual column encodings (ground truth)
                col_encoding = full_column_encodings[:, col_idx, :]  # (batch_size, d_model)
                
                # Get predictions for this column
                col_prediction_1 = full_column_predictions_1[col_idx]  # (batch_size, d_model)
                col_prediction_2 = full_column_predictions_2[col_idx]  # (batch_size, d_model)
                
                # Decode predictions to normalized values
                decoded_1 = decoder(col_prediction_1)  # (batch_size, 1)
                decoded_2 = decoder(col_prediction_2)  # (batch_size, 1)
                
                # Also decode actual encodings to get target values
                # This is more stable than trying to extract from tokenized batch
                with torch.no_grad():
                    target_normalized = decoder(col_encoding)  # (batch_size, 1)
                
                # Compute MSE loss only for masked positions
                if col_mask_1.any():
                    masked_decoded_1 = decoded_1[col_mask_1]
                    masked_target_1 = target_normalized[col_mask_1]
                    loss_1 = F.mse_loss(masked_decoded_1, masked_target_1)
                    reconstruction_losses.append(loss_1)
                    
                if col_mask_2.any():
                    masked_decoded_2 = decoded_2[col_mask_2]
                    masked_target_2 = target_normalized[col_mask_2]
                    loss_2 = F.mse_loss(masked_decoded_2, masked_target_2)
                    reconstruction_losses.append(loss_2)
                
                # Store per-column loss for logging
                col_loss_total = 0.0
                if col_mask_1.any():
                    col_loss_total += loss_1.detach().item()
                if col_mask_2.any():
                    col_loss_total += loss_2.detach().item()
                if col_loss_total > 0:
                    reconstruction_col_losses[col_name] = col_loss_total
            
            if reconstruction_losses:
                reconstruction_loss = sum(reconstruction_losses) / len(reconstruction_losses)
            else:
                reconstruction_loss = torch.tensor(0.0, device=marginal_loss.device, requires_grad=False)
        else:
            # Not training
            reconstruction_loss = torch.tensor(0.0, device=marginal_loss.device, requires_grad=False)

        # COMPUTRE JOINT LOSS
        # The mask for joint embedding_space loss is not necessary because there's
        # no NOT_PRESENT tokens to worry about because all tokens are guaranteed present
        # because we created the joint encodings ourselves.
        joint_loss_1 = self.compute_joint_infoNCE_loss(
            full_joint_encodings_1, full_joint_encodings_unmasked
        )
        joint_loss_2 = self.compute_joint_infoNCE_loss(
            full_joint_encodings_2, full_joint_encodings_unmasked
        )
        short_joint_loss_1 = self.compute_joint_infoNCE_loss(
            short_joint_encodings_1,
            short_joint_encodings_unmasked,
            short=True,
        )
        short_joint_loss_2 = self.compute_joint_infoNCE_loss(
            short_joint_encodings_2,
            short_joint_encodings_unmasked,
            short=True,
        )
        joint_loss = (
            joint_loss_1 + joint_loss_2 + short_joint_loss_1 + short_joint_loss_2
        )
        
        # Capture logits from one of the joint losses for ranking metrics
        # Use the first full joint loss as representative (all should be similar)
        joint_logits_for_metrics = None
        try:
            _, joint_logits_for_metrics = self.compute_joint_infoNCE_loss(
                full_joint_encodings_1, full_joint_encodings_unmasked, return_logits=True
            )
        except Exception as e:
            logger.debug(f"Failed to capture joint logits for metrics: {e}")

        # COMPUTE SPREAD LOSS
        spread_loss_full_total, spread_loss_full_dict = self.compute_spread_loss(
            full_joint_encodings_unmasked,
            full_joint_encodings_1,
            full_joint_encodings_2,
            temp_multiplier=temp_multiplier
        )
        spread_loss_short_total, spread_loss_short_dict = self.compute_spread_loss(
            short_joint_encodings_unmasked,
            short_joint_encodings_1,
            short_joint_encodings_2,
            temp_multiplier=temp_multiplier
        )

        spread_loss = spread_loss_full_total + spread_loss_short_total

        # Compute a "mutual information-like" joint score for the two masks.
        # This measures how well we can predict joint representations, not true MI.
        # Formula: predictability = (log(N) - loss) / log(N) * 100
        # - 0% = random baseline (loss = log(N))
        # - 100% = perfect prediction (loss = 0)
        # - Negative = worse than random (clamped to 0 for display)
        #
        # NOTE: Temperature scaling is already applied in compute_joint_infoNCE_loss(),
        # so the joint_loss values are computed with the correct temperature. The theoretical
        # maximum log(N) is temperature-independent (random baseline is always log(N)).
        log_n = math.log(batch_size)
        
        # Compute percentage predictability (0-100 scale, same as column MI)
        joint_loss_1_val = joint_loss_1.detach().item()
        joint_loss_2_val = joint_loss_2.detach().item()
        
        predictability_1_pct = ((log_n - joint_loss_1_val) / log_n) * 100 if log_n > 0 else 0
        predictability_2_pct = ((log_n - joint_loss_2_val) / log_n) * 100 if log_n > 0 else 0
        
        # Clamp to 0-100% range (negative values mean worse than random, show as 0%)
        predictability_1_pct = max(0, min(100, predictability_1_pct))
        predictability_2_pct = max(0, min(100, predictability_2_pct))
        
        # Update joint MI as percentage (consistent with column MI scale)
        self.update_joint_mi(predictability_1_pct)
        self.update_joint_mi(predictability_2_pct)

        # Collect entropy regularization losses from adaptive encoders
        # This encourages sharper strategy selection (one strategy dominates)
        entropy_regularization_loss = None
        if self.training:
            entropy_losses = []
            for col_name, encoder in self.column_encoder.encoders.items():
                if hasattr(encoder, '_current_entropy_loss'):
                    entropy_loss = encoder._current_entropy_loss
                    if entropy_loss is not None and entropy_loss.requires_grad:
                        entropy_losses.append(entropy_loss)
            
            if entropy_losses:
                # Sum all entropy losses from adaptive encoders
                entropy_regularization_loss = sum(entropy_losses)
            else:
                # No entropy losses - create zero tensor on correct device
                entropy_regularization_loss = torch.tensor(0.0, device=joint_loss.device, requires_grad=False)
        else:
            # Not training - no entropy regularization
            entropy_regularization_loss = torch.tensor(0.0, device=joint_loss.device, requires_grad=False)

        loss_config = self.config.loss_config
        # CRITICAL: NO SCALING COEFFICIENT - marginal weight handles relative importance
        # The scaling coefficient was multiplying by ~0.017 (another 60× reduction!)
        # Combined with the old /normalizer, marginal gradients were 20,000× too small!
        # Now we use raw marginal loss and let the curriculum weight (0.005-0.03) handle it
        marginal_loss_scaled = marginal_loss  # No scaling - use raw loss
        
        # Add entropy regularization to encourage sharper strategy selection
        # Weight it relatively low (0.01) so it guides but doesn't dominate
        entropy_weight = 0.01
        
        # Add scalar reconstruction loss weight
        # Start low (0.05) to guide without dominating - can be increased if needed
        reconstruction_weight = getattr(loss_config, 'reconstruction_loss_weight', 0.05)
        
        # ANTI-COLLAPSE DIVERSITY FLOOR: Prevent column loss equalization
        # When column losses collapse to near-constant, the model stops differentiating
        # "what's hard" vs "what's easy", making relationship ranking signal junk.
        # This term rewards spread in per-column losses (variance above minimum threshold).
        # 
        # NOTE: We compute this from aggregated_col_losses which are detached floats.
        # While this doesn't provide direct gradients, the penalty encourages the model
        # to maintain diversity in per-column losses through the overall loss signal.
        # The gradients still flow through the marginal_loss computation itself.
        anti_collapse_loss = None
        if self.training and aggregated_col_losses and len(aggregated_col_losses) > 1:
            # Compute std from aggregated values (detached, but still informative)
            col_loss_values_list = list(aggregated_col_losses.values())
            col_loss_mean = sum(col_loss_values_list) / len(col_loss_values_list)
            col_loss_var = sum((v - col_loss_mean) ** 2 for v in col_loss_values_list) / len(col_loss_values_list)
            col_loss_std = math.sqrt(col_loss_var + 1e-8)  # Add small epsilon for numerical stability
            
            # Target minimum std: 0.1 early training, anneal down to 0.01 later
            # This ensures columns maintain meaningful differentiation
            # We track epoch via a simple counter (approximate)
            if not hasattr(self, '_anti_collapse_epoch_counter'):
                self._anti_collapse_epoch_counter = 0
            self._anti_collapse_epoch_counter += 1
            
            # Anneal threshold: 0.1 → 0.01 over ~100 epochs
            # Use a simple linear decay (can be made more sophisticated)
            progress = min(1.0, self._anti_collapse_epoch_counter / 100.0)
            target_std = 0.1 * (1.0 - progress) + 0.01 * progress
            
            # Penalty: max(0, target_std - actual_std)^2
            # This encourages std to stay above target_std
            # Convert to tensor for loss computation (no gradients, but adds to loss signal)
            std_deficit = target_std - col_loss_std
            if std_deficit > 0:
                anti_collapse_loss = torch.tensor(
                    (std_deficit ** 2),
                    device=marginal_loss.device,
                    dtype=marginal_loss.dtype,
                    requires_grad=False  # No direct gradients, but loss signal still guides training
                )
            else:
                anti_collapse_loss = torch.tensor(0.0, device=marginal_loss.device, requires_grad=False)
            
            # Weight: start at 0.1, can be tuned
            # This should be strong enough to prevent collapse but not dominate other losses
            anti_collapse_weight = 0.1
        else:
            anti_collapse_loss = torch.tensor(0.0, device=marginal_loss.device, requires_grad=False)
            anti_collapse_weight = 0.0
        
        # DEBUG: Log loss components on first few batches (simplified, readable format)
        if not hasattr(self, '_loss_debug_counter'):
            self._loss_debug_counter = 0
        
        total = (
            loss_config.joint_loss_weight * joint_loss
            + loss_config.marginal_loss_weight * marginal_loss_scaled
            + loss_config.spread_loss_weight * spread_loss
            + entropy_weight * entropy_regularization_loss
            + reconstruction_weight * reconstruction_loss
            + anti_collapse_weight * anti_collapse_loss
        )
        
        # Only log loss breakdown for first batch of first epoch (minimal verbosity)
        if self._loss_debug_counter < 1:
            batch_num = getattr(self, '_debug_mps_batch_count', 0)
            spread_val = (loss_config.spread_loss_weight * spread_loss).item()
            joint_val = (loss_config.joint_loss_weight * joint_loss).item()
            marginal_val = (loss_config.marginal_loss_weight * marginal_loss_scaled).item()
            recon_val = (reconstruction_weight * reconstruction_loss).item()
            total_val = total.item()
            
            # Single compact line showing only essential info
            logger.info(f"📊 Loss (b={batch_num}): spread={spread_val:.1f}  joint={joint_val:.1f}  marginal={marginal_val:.1f}  recon={recon_val:.3f}  → total={total_val:.1f}")
            self._loss_debug_counter += 1

        # COLLAPSE DIAGNOSTICS: Compute metrics to distinguish real collapse from metric artifacts
        collapse_diagnostics = {}
        if self.training:
            try:
                # 1. Joint embedding norms and std
                # Compute ||joint embedding|| for each sample
                joint_norms = torch.norm(full_joint_encodings_unmasked, dim=1)  # (batch_size,)
                joint_norm_mean = joint_norms.mean().item()
                joint_norm_std = joint_norms.std().item()
                
                # Compute std of joint embeddings per dimension
                joint_std_per_dim = full_joint_encodings_unmasked.std(dim=0)  # (d_model,)
                joint_std_mean = joint_std_per_dim.mean().item()
                joint_std_std = joint_std_per_dim.std().item()
                
                collapse_diagnostics['joint_embedding'] = {
                    'norm_mean': joint_norm_mean,
                    'norm_std': joint_norm_std,
                    'std_per_dim_mean': joint_std_mean,
                    'std_per_dim_std': joint_std_std,
                }
                
                # 2. Mask entropy (entropy of masking distribution)
                # Compute entropy of mask distribution: how uniform/random is the masking?
                # For each mask, compute the fraction of MARGINAL tokens per column
                if mask_1 is not None and mask_2 is not None:
                    # Count MARGINAL tokens per column across batch
                    mask_1_marginal = (mask_1 == TokenStatus.MARGINAL).float()  # (batch_size, n_cols)
                    mask_2_marginal = (mask_2 == TokenStatus.MARGINAL).float()
                    
                    # Average masking probability per column (across batch)
                    mask_1_probs = mask_1_marginal.mean(dim=0)  # (n_cols,)
                    mask_2_probs = mask_2_marginal.mean(dim=0)
                    
                    # Compute entropy: H = -sum(p * log(p) + (1-p) * log(1-p))
                    # High entropy = uniform masking (good), low entropy = biased masking (bad)
                    eps = 1e-10
                    mask_1_entropy = -(mask_1_probs * torch.log(mask_1_probs + eps) + 
                                      (1 - mask_1_probs) * torch.log(1 - mask_1_probs + eps)).mean().item()
                    mask_2_entropy = -(mask_2_probs * torch.log(mask_2_probs + eps) + 
                                      (1 - mask_2_probs) * torch.log(1 - mask_2_probs + eps)).mean().item()
                    
                    collapse_diagnostics['mask_entropy'] = {
                        'mask_1': mask_1_entropy,
                        'mask_2': mask_2_entropy,
                        'mean': (mask_1_entropy + mask_2_entropy) / 2.0,
                    }
                
                # 3. Logit distribution per column (from marginal predictions)
                # Compute logits from marginal predictions for a sample of columns
                # This shows if predictions are collapsing to similar values
                if aggregated_col_losses and len(aggregated_col_losses) > 0:
                    # Sample a few columns to compute logit stats
                    sample_cols = list(aggregated_col_losses.keys())[:min(5, len(aggregated_col_losses))]
                    logit_stats_per_col = {}
                    
                    for col_idx, col_name in enumerate(self.idx_to_col_name.values()):
                        if col_name not in sample_cols:
                            continue
                        
                        # Get predictions and targets for this column from one of the masks
                        # Use mask_1 predictions as sample
                        if col_idx < len(full_column_predictions_1):
                            col_pred = full_column_predictions_1[col_idx]  # (batch_size, d_model)
                            col_target = full_column_encodings[:, col_idx, :]  # (batch_size, d_model)
                            
                            # Normalize for logit computation
                            col_pred_norm = F.normalize(col_pred, dim=1)
                            col_target_norm = F.normalize(col_target, dim=1)
                            
                            # Compute logits (similarity matrix)
                            temperature = self._compute_adaptive_temperature(batch_size)
                            logits = col_pred_norm @ col_target_norm.T / temperature  # (batch_size, batch_size)
                            
                            # Get diagonal (correct predictions) and off-diagonal (negatives)
                            logits_diag = logits.diag()  # (batch_size,)
                            # Get off-diagonal (sample a subset to avoid O(n²))
                            mask_off_diag = ~torch.eye(batch_size, dtype=torch.bool, device=logits.device)
                            logits_off_diag = logits[mask_off_diag]
                            if len(logits_off_diag) > 1000:
                                logits_off_diag = logits_off_diag[::len(logits_off_diag)//1000]  # Sample
                            
                            logit_stats_per_col[col_name] = {
                                'diag_mean': logits_diag.mean().item(),
                                'diag_std': logits_diag.std().item(),
                                'off_diag_mean': logits_off_diag.mean().item(),
                                'off_diag_std': logits_off_diag.std().item(),
                                'separation': (logits_diag.mean() - logits_off_diag.mean()).item(),  # Higher = better separation
                            }
                    
                    collapse_diagnostics['logit_distribution'] = logit_stats_per_col
                    
            except Exception as e:
                # Don't break training if diagnostics fail
                logger.debug(f"Failed to compute collapse diagnostics: {e}")
                collapse_diagnostics = {'error': str(e)}
        
        # Compute ranking metrics from joint loss logits
        ranking_metrics = None
        if joint_logits_for_metrics is not None:
            try:
                with torch.no_grad():
                    ranking_metrics = compute_ranking_metrics(joint_logits_for_metrics)
                    collapse_diagnostics['ranking_metrics'] = ranking_metrics
            except Exception as e:
                logger.debug(f"Failed to compute ranking metrics: {e}")
                # Don't fail if ranking metrics computation fails
        
        loss_dict = {
            "total": total.item(),
            "batch_size": batch_size,
            "collapse_diagnostics": collapse_diagnostics,
            "reconstruction_loss": {
                "total": reconstruction_loss.item() if hasattr(reconstruction_loss, 'item') else 0.0,
                "cols": reconstruction_col_losses,
            },
            "entropy_regularization": {
                "total": entropy_regularization_loss.item() if hasattr(entropy_regularization_loss, 'item') else 0.0,
            },
            "spread_loss": {
                "total": spread_loss.item(),
                "full": {
                    "total": spread_loss_full_total.item(),
                    **spread_loss_full_dict,
                },
                "short": {
                    "total": spread_loss_short_total.item(),
                    **spread_loss_short_dict,
                },
            },
            "joint_loss": {
                "total": joint_loss.item(),
                "joint_loss_full_1": joint_loss_1.item(),
                "joint_loss_full_2": joint_loss_2.item(),
                "joint_loss_short_1": short_joint_loss_1.item(),
                "joint_loss_short_2": short_joint_loss_2.item(),
            },
            "marginal_loss": {
                "total": marginal_loss.item(),
                "raw": marginal_loss_raw.item(),  # Before normalization
                "normalizer": normalizer,  # Divisor used for normalization
                "marginal_loss_full_1": {
                    "total": marginal_cpc_loss_1_total.item(),
                    "cols": marginal_cpc_loss_1_col_dict,
                },
                "marginal_loss_full_2": {
                    "total": marginal_cpc_loss_2_total.item(),
                    "cols": marginal_cpc_loss_2_col_dict,
                },
                "marginal_loss_short_1": {
                    "total": short_marginal_cpc_loss_1_total.item(),
                    "cols": short_marginal_cpc_loss_1_col_dict,
                },
                "marginal_loss_short_2": {
                    "total": short_marginal_cpc_loss_2_total.item(),
                    "cols": short_marginal_cpc_loss_2_col_dict,
                },
            },
        }

        return total, loss_dict

    def compute_proportionality_loss(self, batch, n_samples=8, perturbation_scale=0.1):
        """
        Compute proportionality loss for scalar (numeric) columns.
        
        This loss encourages the embedding distance to be proportional to the 
        input distance for numeric columns. Without this, discrete encoding 
        strategies (buckets, ranks) can dominate and cause small input changes 
        to produce zero embedding change.
        
        Args:
            batch: Dict of column_name -> TokenBatch
            n_samples: Number of rows to sample for perturbation test
            perturbation_scale: Scale of perturbation as fraction of column std
            
        Returns:
            Tuple of (loss tensor, loss_dict with details)
        """
        from featrix.neural.featrix_token import TokenBatch
        
        device = next(self.parameters()).device
        
        # Find scalar columns
        scalar_cols = []
        for col_name in self.config.cols_in_order:
            col_type = self.config.col_types.get(col_name)
            if col_type == ColumnType.SCALAR and col_name in batch:
                scalar_cols.append(col_name)
        
        if not scalar_cols:
            # No scalar columns to test
            return torch.tensor(0.0, device=device, requires_grad=True), {'total': 0.0, 'n_cols': 0}
        
        total_loss = torch.tensor(0.0, device=device, requires_grad=True)
        col_losses = {}
        
        # Sample indices from batch
        batch_size = len(next(iter(batch.values())).value)
        sample_indices = torch.randperm(batch_size, device=device)[:min(n_samples, batch_size)]
        
        for col_name in scalar_cols[:5]:  # Limit to 5 columns for efficiency
            try:
                token_batch = batch[col_name]
                original_values = token_batch.value[sample_indices].clone()
                
                # Skip if all values are the same (no variation to learn)
                if original_values.std() < 1e-6:
                    continue
                
                # Create perturbed values (add random noise proportional to column std)
                col_std = original_values.std().clamp(min=1e-6)
                perturbation = torch.randn_like(original_values) * perturbation_scale * col_std
                perturbed_values = original_values + perturbation
                
                # Create perturbed batch - clone the token batch structure
                perturbed_batch = {}
                for c_name, tb in batch.items():
                    if c_name == col_name:
                        # Create modified token batch for this column
                        new_values = tb.value.clone()
                        new_values[sample_indices] = perturbed_values
                        perturbed_batch[c_name] = TokenBatch.__new__(TokenBatch)
                        perturbed_batch[c_name].value = new_values
                        perturbed_batch[c_name].status = tb.status.clone()
                        perturbed_batch[c_name].attention_mask = tb.attention_mask.clone() if tb.attention_mask is not None else None
                    else:
                        # Keep other columns unchanged
                        perturbed_batch[c_name] = tb
                
                # Encode both original and perturbed
                with torch.no_grad():
                    # Get original embeddings for sampled rows
                    orig_short, orig_full, _, _ = self.column_encoder(batch)
                    pert_short, pert_full, _, _ = self.column_encoder(perturbed_batch)
                
                # We need gradients through the forward pass for training
                # Re-encode with gradients enabled
                orig_short_grad, orig_full_grad, _, _ = self.column_encoder(batch)
                pert_short_grad, pert_full_grad, _, _ = self.column_encoder(perturbed_batch)
                
                # Get column index
                col_idx = self.config.cols_in_order.index(col_name)
                
                # Extract embeddings for this column
                orig_emb = orig_full_grad[sample_indices, col_idx, :]  # [n_samples, d_model]
                pert_emb = pert_full_grad[sample_indices, col_idx, :]  # [n_samples, d_model]
                
                # Compute embedding distances
                emb_distances = torch.norm(orig_emb - pert_emb, dim=1)  # [n_samples]
                
                # Compute expected distances (normalized input change)
                input_distances = torch.abs(perturbation) / col_std  # [n_samples]
                
                # Target: embedding distance should scale with input distance
                # Loss: penalize when they don't match (squared difference)
                # We use a soft target: emb_dist should be roughly proportional to input_dist
                # scaled by some learned factor. For now, just minimize variance of ratio.
                ratio = emb_distances / (input_distances + 1e-6)
                
                # Loss: variance of ratio (ideally all ratios should be similar = proportional)
                # Plus: penalize if mean ratio is too small (embedding not responding)
                ratio_mean = ratio.mean()
                ratio_var = ratio.var()
                
                # Proportionality loss: high variance = bad proportionality
                # Also penalize if mean ratio is < 0.01 (embedding barely moves)
                min_response_penalty = F.relu(0.01 - ratio_mean) * 10.0
                
                col_loss = ratio_var + min_response_penalty
                total_loss = total_loss + col_loss
                
                col_losses[col_name] = {
                    'loss': col_loss.item(),
                    'ratio_mean': ratio_mean.item(),
                    'ratio_var': ratio_var.item(),
                    'min_response_penalty': min_response_penalty.item(),
                }
                
            except Exception as e:
                # Don't crash training if proportionality loss fails for one column
                logger.debug(f"Proportionality loss failed for {col_name}: {e}")
                continue
        
        # Average over columns
        n_cols = len(col_losses)
        if n_cols > 0:
            total_loss = total_loss / n_cols
        
        loss_dict = {
            'total': total_loss.item() if hasattr(total_loss, 'item') else 0.0,
            'n_cols': n_cols,
            'cols': col_losses,
        }
        
        return total_loss, loss_dict

    def encode(self, column_batches, apply_noise=False):
        """This is the method that should be called at query time."""
        
        # Get logger from the current module
        
        # CRITICAL: Force CPU mode for single predictor training
        force_cpu_env = os.environ.get('FEATRIX_FORCE_CPU_SINGLE_PREDICTOR')
        if force_cpu_env == '1':
            # Ensure encoder and all submodules are on CPU
            if list(self.parameters()):
                encoder_device = next(self.parameters()).device
                if encoder_device.type != 'cpu':
                    self.cpu()
                    if is_gpu_available():
                        empty_gpu_cache()
            
            # CRITICAL: Move all input TokenBatch objects to CPU
            cpu_device = torch.device('cpu')
            for col_name, token_batch in column_batches.items():
                if hasattr(token_batch, 'to'):
                    token_batch.to(cpu_device)
        
        # Debug counter for tracking problematic batches
        # debug_count = getattr(self, '_encode_debug_count', 0)
        # should_debug = debug_count < 3  # Debug first 3 batches
        
        # CRITICAL: Check if column_encoder has empty col_order before attempting encoding
        if hasattr(self.column_encoder, 'col_order') and len(self.column_encoder.col_order) == 0:
            logger.error(f"💥 CRITICAL: column_encoder.col_order is EMPTY before encoding!")
            logger.error(f"   Input column_batches keys: {list(column_batches.keys()) if column_batches else 'None'}")
            logger.error(f"   Column encoder encoders: {list(self.column_encoder.encoders.keys()) if hasattr(self.column_encoder, 'encoders') else 'None'}")
            logger.error(f"   Column encoder codecs: {list(self.column_encoder.col_codecs.keys()) if hasattr(self.column_encoder, 'col_codecs') and self.column_encoder.col_codecs else 'None'}")
            raise RuntimeError(
                f"Column encoder has empty col_order - cannot encode. "
                f"This indicates the encoder was saved incorrectly or the model is corrupted. "
                f"Input had {len(column_batches) if column_batches else 0} columns: {list(column_batches.keys())[:10] if column_batches else []}"
            )
        
        # if should_debug:
        #     logger.info(f"🔍 ENCODER DEBUG #{debug_count}: Starting encoder.encode")
        #     logger.info(f"   Input columns: {list(column_batches.keys())}")
        #     logger.info(f"   Apply noise: {apply_noise}")
        
        (
            short_column_encoding_list,
            full_column_encoding_list,
            token_status_list,
        ) = self.column_encoder(column_batches)
        
        # CRITICAL: Check for empty encoding lists before stacking
        # This prevents "stack expects a non-empty TensorList" errors
        if len(full_column_encoding_list) == 0:
            logger.error(f"💥 CRITICAL: full_column_encoding_list is EMPTY!")
            logger.error(f"   This causes 'stack expects a non-empty TensorList' error")
            logger.error(f"   Column encoder returned no encodings")
            logger.error(f"   Input columns: {list(column_batches.keys()) if column_batches else 'None'}")
            logger.error(f"   Number of input columns: {len(column_batches) if column_batches else 0}")
            raise RuntimeError("No columns were encoded - check column setup and codec creation. This usually means the query record has no fields that match the trained codecs.")
        
        if len(short_column_encoding_list) == 0:
            logger.error(f"💥 CRITICAL: short_column_encoding_list is EMPTY!")
            logger.error(f"   This causes 'stack expects a non-empty TensorList' error")
            logger.error(f"   Column encoder returned no short encodings")
            logger.error(f"   Input columns: {list(column_batches.keys()) if column_batches else 'None'}")
            raise RuntimeError("No columns were encoded (short) - check column setup and codec creation")
        
        # if should_debug:
        #     logger.info(f"   Column encoder output - lists length: {len(short_column_encoding_list)}")
        #     for i, (short_enc, full_enc) in enumerate(zip(short_column_encoding_list, full_column_encoding_list)):
        #         if torch.isnan(short_enc).any() or torch.isnan(full_enc).any():
        #             col_name = list(column_batches.keys())[i] if i < len(column_batches) else f"col_{i}"
        #             logger.error(f"🚨 COLUMN ENCODER OUTPUT HAS NaN: {col_name}")
        #             if torch.isnan(short_enc).any():
        #                 logger.error(f"   Short encoding NaN count: {torch.isnan(short_enc).sum()}/{short_enc.numel()}")
        #             if torch.isnan(full_enc).any():
        #                 logger.error(f"   Full encoding NaN count: {torch.isnan(full_enc).sum()}/{full_enc.numel()}")
        
        # CRITICAL: Check tensor shapes before stacking to provide better error messages
        try:
            column_encodings, token_status_mask = (
                torch.stack(full_column_encoding_list, dim=1),
                torch.stack(token_status_list, dim=1),
            )
        except RuntimeError as e:
            if "stack expects each tensor to be equal size" in str(e):
                logger.error(f"💥 TENSOR SHAPE MISMATCH in column encoding stacking:")
                logger.error(f"   Error: {e}")
                logger.error(f"   Number of columns: {len(full_column_encoding_list)}")
                for i, enc in enumerate(full_column_encoding_list):
                    logger.error(f"   Column {i} shape: {enc.shape}")
                logger.error(f"   This usually means an encoder is returning 3D instead of 2D tensors")
                logger.error(f"   Check hybrid column encoders or text/sequence encoders")
            raise

        # if should_debug:
        #     if torch.isnan(column_encodings).any():
        #         logger.error(f"🚨 STACKED COLUMN ENCODINGS HAVE NaN: {torch.isnan(column_encodings).sum()}/{column_encodings.numel()}")
        #     logger.info(f"   Stacked encodings shape: {column_encodings.shape}")

        self.column_encodings = column_encodings
        self.token_status_mask = token_status_mask

        if apply_noise is True:
            batch_size = column_encodings.shape[0]
            column_marginal_embeddings = self.get_marginal_tensor(batch_size)
            column_encodings = self.apply_marginal_mask(
                column_encodings, column_marginal_embeddings, token_status_mask
            )
            
            # if should_debug:
            #     if torch.isnan(column_encodings).any():
            #         logger.error(f"🚨 AFTER MARGINAL MASK ENCODINGS HAVE NaN: {torch.isnan(column_encodings).sum()}/{column_encodings.numel()}")

        # ROOT CAUSE DEBUGGING: Check for zero vectors before joint encoder
        # if should_debug:
        #     # Check for zero vectors that could cause NaN during normalization
        #     zero_tensor = torch.zeros_like(column_encodings)
        #     zero_vectors = torch.allclose(column_encodings, zero_tensor, atol=1e-8)
        #     if zero_vectors:
        #         logger.error(f"🚨 ZERO VECTORS DETECTED before joint encoder!")
        #         logger.error(f"   column_encodings contains all zeros: {column_encodings}")
            
        #     # Check for individual zero rows/columns
        #     for i in range(column_encodings.shape[0]):  # batch dimension
        #         for j in range(column_encodings.shape[1]):  # column dimension
        #             vec = column_encodings[i, j, :]
        #             zero_vec = torch.zeros_like(vec)
        #             if torch.allclose(vec, zero_vec, atol=1e-8):
        #                 col_name = list(column_batches.keys())[j] if j < len(column_batches) else f"col_{j}"
        #                 logger.error(f"🚨 Zero vector for batch {i}, column '{col_name}': {vec}")

        # Convert token_status_mask to binary mask for relationship extractor
        binary_mask = _token_status_to_binary_mask(token_status_mask) if token_status_mask is not None else None
        
        # CRITICAL: Ensure column_encodings is on the same device as joint_encoder
        # This prevents device mismatch errors when column encodings are on CPU but joint_encoder is on CUDA
        # This can happen when string encodings come from CPU or DataLoader creates tensors on CPU
        try:
            joint_encoder_device = next(self.joint_encoder.parameters()).device
            if column_encodings.device != joint_encoder_device:
                column_encodings = column_encodings.to(device=joint_encoder_device)
                if binary_mask is not None and binary_mask.device != joint_encoder_device:
                    binary_mask = binary_mask.to(device=joint_encoder_device)
        except (StopIteration, AttributeError):
            # Joint encoder has no parameters or can't determine device - skip device placement
            pass
        
        short_joint_encodings, full_joint_encodings = self.joint_encoder(
            column_encodings, mask=binary_mask
        )

        # if should_debug:
        #     if torch.isnan(short_joint_encodings).any():
        #         logger.error(f"🚨 JOINT ENCODER SHORT OUTPUT HAS NaN: {torch.isnan(short_joint_encodings).sum()}/{short_joint_encodings.numel()}")
        #     if torch.isnan(full_joint_encodings).any():
        #         logger.error(f"🚨 JOINT ENCODER FULL OUTPUT HAS NaN: {torch.isnan(full_joint_encodings).sum()}/{full_joint_encodings.numel()}")
        #     logger.info(f"   Joint encoder output shapes: short={short_joint_encodings.shape}, full={full_joint_encodings.shape}")
        #     self._encode_debug_count = debug_count + 1

        return short_joint_encodings, full_joint_encodings

    def forward(self, column_batches):
        # DEBUG: MPS INT_MAX - Track batch for debugging
        _debug_mps = getattr(self, '_debug_mps_batch_count', 0)
        self._debug_mps_batch_count = _debug_mps + 1
        
        # Debug on first 3 batches, OR on pruning epochs (every 5th epoch starting at 5)
        # Get current epoch from any scalar codec that has it
        _current_epoch = 0
        try:
            for codec in self.column_encoder.column_codecs.values():
                if hasattr(codec, '_current_epoch'):
                    _current_epoch = codec._current_epoch.item() if hasattr(codec._current_epoch, 'item') else codec._current_epoch
                    break
        except Exception:
            pass
        
        _is_prune_epoch = _current_epoch >= 5 and _current_epoch % 5 == 0
        _should_debug = _debug_mps < 3 or (_is_prune_epoch and _debug_mps % 33 == 0)  # First batch of prune epochs
        
        if _should_debug:
            logger.info(f"[DEBUG] FeatrixTableEncoder.forward() - batch #{_debug_mps}, epoch={_current_epoch}")
            logger.info(f"[DEBUG]   Input column_batches: {len(column_batches)} columns")
            _log_gpu_memory_encoders("BEFORE column_encoder (start of forward)")

        # Encode the columns invidividually
        (
            short_column_encoding_list,
            full_column_encoding_list,
            token_status_list,
        ) = self.column_encoder(column_batches)
        
        if _should_debug:
            _log_gpu_memory_encoders("After column_encoder")
            logger.info(f"[DEBUG]   After column_encoder: {len(full_column_encoding_list)} encodings")

        # Combine the individual column encodings and masks into tensors for easier handling
        # the resulting tensors have shapes (batch_size, n_cols, d_model) and (batch_size, n_cols), respectively
        # The ease of handling is mostly related to masking - it's much easier to carry out the masking procedure
        # on a single tensor object that contains the embeddings for all the columns because that makes
        # the coordination of how many columns to mask out much easier.
        
        # DEBUG: Check for empty encoding lists before stacking
        if len(short_column_encoding_list) == 0:
            logger.error(f"💥 CRITICAL: short_column_encoding_list is EMPTY!")
            logger.error(f"   This causes 'stack expects a non-empty TensorList' error")
            logger.error(f"   Column encoder returned no encodings")
            raise RuntimeError("No columns were encoded - check column setup and codec creation")
            
        short_column_encodings, full_column_encodings, token_status_mask = (
            torch.stack(short_column_encoding_list, dim=1),
            torch.stack(full_column_encoding_list, dim=1),
            torch.stack(token_status_list, dim=1),
        )

        batch_size = full_column_encodings.shape[0]
        
        if _should_debug:
            _log_gpu_memory_encoders("After stacking")
            logger.info(f"[DEBUG]   After stacking: full_column_encodings shape = {full_column_encodings.shape}")
            logger.info(f"[DEBUG]   batch_size = {batch_size}, numel = {full_column_encodings.numel()}")

        # with stopwatch.interval("sample_marginal_masks"):
        # Each row is randomly split into two non-overlapping parts. We do that so we
        # can embed each part separately and then use it to predict the other part.
        # We take in the batch status mask, and return two mask that are complimentary.
        mask_1, mask_2, rows_skipped = sample_marginal_masks(
            token_status_mask, 
            self.min_mask_ratio, 
            self.max_mask_ratio, 
            self.mean_nulls_per_row,
            col_names=self.config.cols_in_order,
            track_bias=True
        )

        # with stopwatch.interval("get_marginal_tensor"):
        full_column_marginal_embeddings = self.get_marginal_tensor(batch_size)

        # with stopwatch.interval("apply_marginal_masks"):
        masked_column_encodings_1 = self.apply_marginal_mask(
            full_column_encodings, full_column_marginal_embeddings, mask_1
        )
        masked_column_encodings_2 = self.apply_marginal_mask(
            full_column_encodings, full_column_marginal_embeddings, mask_2
        )

        # with stopwatch.interval("joint_encoding"):
        # Convert token_status_mask to binary mask for relationship extractor
        binary_mask = _token_status_to_binary_mask(token_status_mask) if token_status_mask is not None else None
        
        # For masked encodings, use the corresponding mask (mask_1 or mask_2)
        # These masks indicate which columns are masked for marginal prediction
        mask_1_binary = _token_status_to_binary_mask(mask_1) if mask_1 is not None else binary_mask
        mask_2_binary = _token_status_to_binary_mask(mask_2) if mask_2 is not None else binary_mask
        
        if _should_debug:
            _log_gpu_memory_encoders("Before joint_encoder")
            logger.info(f"[DEBUG]   Before joint_encoder calls:")
            logger.info(f"[DEBUG]     masked_column_encodings_1 shape: {masked_column_encodings_1.shape}")
            logger.info(f"[DEBUG]     About to call joint_encoder...")
        
        short_joint_encodings_1, full_joint_encodings_1 = self.joint_encoder(
            masked_column_encodings_1, mask=mask_1_binary
        )
        
        if _should_debug:
            _log_gpu_memory_encoders("After joint_encoder #1")
            logger.info(f"[DEBUG]   After joint_encoder #1: full_joint_encodings_1 shape = {full_joint_encodings_1.shape}")
        
        short_joint_encodings_2, full_joint_encodings_2 = self.joint_encoder(
            masked_column_encodings_2, mask=mask_2_binary
        )
        
        if _should_debug:
            logger.info(f"[DEBUG]   After joint_encoder #2: full_joint_encodings_2 shape = {full_joint_encodings_2.shape}")
        
        (
            short_joint_encodings_unmasked,
            full_joint_encodings_unmasked,
        ) = self.joint_encoder(full_column_encodings, mask=binary_mask)
        
        if _should_debug:
            logger.info(f"[DEBUG]   After joint_encoder #3: full_joint_encodings_unmasked shape = {full_joint_encodings_unmasked.shape}")

        # Column predictions are a list of torch.tensors. Each element of the list
        # corresponds to the predictions made for the corresponding column.
        # The list elements are ordered by config.cols_in_order.
        # The list elements all have shape (batch_size, model_dim)
        # with stopwatch.interval("column_predictors"):
        full_column_predictions_unmasked = self.column_predictor(
            full_joint_encodings_unmasked
        )
        full_column_predictions_1 = self.column_predictor(full_joint_encodings_1)
        full_column_predictions_2 = self.column_predictor(full_joint_encodings_2)

        # with stopwatch.interval("column_predictors_short"):
        short_column_predictions_1 = self.short_column_predictor(
            short_joint_encodings_1
        )
        short_column_predictions_2 = self.short_column_predictor(
            short_joint_encodings_2
        )
        short_column_predictions_unmasked = self.short_column_predictor(
            short_joint_encodings_unmasked
            )

        # stopwatch.stop()

        return (
            batch_size,
            #
            full_joint_encodings_unmasked,
            full_joint_encodings_1,
            full_joint_encodings_2,
            #
            full_column_encodings,
            short_column_encodings,
            #
            short_joint_encodings_unmasked,
            short_joint_encodings_1,
            short_joint_encodings_2,
            #
            mask_1,
            mask_2,
            #
            full_column_predictions_1,
            full_column_predictions_2,
            full_column_predictions_unmasked,
            #
            short_column_predictions_1,
            short_column_predictions_2,
            short_column_predictions_unmasked,
            #
            rows_skipped,  # Number of rows skipped from masking (too many nulls)
        )
