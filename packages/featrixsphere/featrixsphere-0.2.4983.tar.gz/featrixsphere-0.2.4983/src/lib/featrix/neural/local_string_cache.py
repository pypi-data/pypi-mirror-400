# -*- coding: utf-8 -*-
"""
Local string cache for warming up SimpleStringCache.

This module provides:
1. Saving string embeddings to pickle files (keyed by string columns)
2. Loading cached embeddings to warm up SimpleStringCache
3. Finding best-matching cache files based on column names

Cache files are stored in {featrix_root}/strings_cache/
"""
import hashlib
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import torch

logger = logging.getLogger(__name__)


def _get_strings_cache_dir() -> str:
    """
    Get the strings cache directory path.
    
    Uses featrix_get_root() from platform_utils to determine the root,
    then returns {root}/strings_cache/
    
    Returns:
        Path to strings_cache directory (created if it doesn't exist)
    """
    from featrix.neural.platform_utils import featrix_get_root
    
    root = featrix_get_root()
    cache_dir = Path(root) / "strings_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return str(cache_dir)


def _get_cache_filename(string_columns: List[str]) -> str:
    """
    Generate cache filename from string column names.
    
    Args:
        string_columns: List of string column names
        
    Returns:
        Base filename (without extension) based on MD5 of sorted, lowercase column names
    """
    # Sort and lowercase column names
    sorted_cols = sorted([col.lower() for col in string_columns])
    
    # Join and compute MD5
    joined = "|".join(sorted_cols)
    md5_hash = hashlib.md5(joined.encode('utf-8')).hexdigest()
    
    return f"local_string_cache_{md5_hash}"


def save_local_string_cache(
    string_embeddings: Dict[str, np.ndarray],
    string_columns: List[str],
    cache_dir: Optional[str] = None
) -> Tuple[str, str]:
    """
    Save local string cache to pickle and JSON files.
    
    Args:
        string_embeddings: Dict mapping string -> numpy array embedding
        string_columns: List of string column names used to generate this cache
        cache_dir: Directory to save cache files (default: {featrix_root}/strings_cache/)
        
    Returns:
        Tuple of (pickle_file_path, json_file_path)
    """
    if cache_dir is None:
        cache_dir = _get_strings_cache_dir()
    
    cache_dir_path = Path(cache_dir)
    cache_dir_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename based on column names
    base_name = _get_cache_filename(string_columns)
    pickle_path = cache_dir_path / f"{base_name}.pkl"
    json_path = cache_dir_path / f"{base_name}.json"
    
    # Save pickle file with embeddings dict
    logger.info(f"💾 Saving local string cache: {pickle_path}")
    logger.info(f"   Columns: {string_columns}")
    logger.info(f"   Embeddings: {len(string_embeddings)} strings")
    
    with open(pickle_path, 'wb') as f:
        pickle.dump(string_embeddings, f)
    
    # Save JSON file with column names
    metadata = {
        "string_columns": string_columns,
        "num_embeddings": len(string_embeddings),
        "embedding_dim": next(iter(string_embeddings.values())).shape[0] if string_embeddings else None
    }
    
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✅ Local string cache saved: {pickle_path.name} ({pickle_path.stat().st_size / 1024:.1f} KB)")
    logger.info(f"   Metadata: {json_path.name}")
    
    return str(pickle_path), str(json_path)


def load_local_string_cache(pickle_path: str) -> Dict[str, np.ndarray]:
    """
    Load local string cache from pickle file.
    
    Args:
        pickle_path: Path to pickle file
        
    Returns:
        Dict mapping string -> numpy array embedding
    """
    pickle_path_obj = Path(pickle_path)
    if not pickle_path_obj.exists():
        raise FileNotFoundError(f"Cache file not found: {pickle_path}")
    
    logger.info(f"📦 Loading local string cache: {pickle_path}")
    
    with open(pickle_path_obj, 'rb') as f:
        embeddings = pickle.load(f)
    
    logger.info(f"✅ Loaded {len(embeddings)} string embeddings")
    
    return embeddings


def find_best_cache_match(
    target_columns: List[str],
    cache_dir: Optional[str] = None
) -> Optional[Tuple[str, Dict]]:
    """
    Find best-matching cache file based on column name overlap.
    
    Args:
        target_columns: List of string column names we're looking for
        cache_dir: Directory to search for cache files (default: {featrix_root}/strings_cache/)
        
    Returns:
        Tuple of (pickle_path, metadata_dict) if match found, else None
    """
    if cache_dir is None:
        cache_dir = _get_strings_cache_dir()
    
    cache_dir_path = Path(cache_dir)
    if not cache_dir_path.exists():
        return None
    
    # Find all JSON metadata files
    json_files = list(cache_dir_path.glob("local_string_cache_*.json"))
    
    if not json_files:
        logger.debug(f"No cache files found in {cache_dir}")
        return None
    
    # Normalize target columns (lowercase, sorted)
    target_set = set(col.lower() for col in target_columns)
    
    best_match = None
    best_score = 0
    best_metadata = None
    
    # Score each cache file by column overlap
    for json_path in json_files:
        try:
            with open(json_path, 'r') as f:
                metadata = json.load(f)
            
            cache_columns = metadata.get("string_columns", [])
            cache_set = set(col.lower() for col in cache_columns)
            
            # Calculate overlap score
            # Score = (intersection / union) * (intersection / target)
            # This favors caches that have most/all of our columns
            intersection = target_set & cache_set
            union = target_set | cache_set
            
            if len(intersection) == 0:
                continue
            
            # Jaccard similarity weighted by coverage of target columns
            jaccard = len(intersection) / len(union) if union else 0
            coverage = len(intersection) / len(target_set) if target_set else 0
            
            # Combined score: prioritize coverage of target columns
            score = coverage * 0.7 + jaccard * 0.3
            
            if score > best_score:
                best_score = score
                best_metadata = metadata
                # Find corresponding pickle file
                base_name = json_path.stem
                pickle_path = json_path.parent / f"{base_name}.pkl"
                if pickle_path.exists():
                    best_match = str(pickle_path)
        except Exception as e:
            logger.warning(f"Failed to read cache metadata {json_path}: {e}")
            continue
    
    if best_match and best_score > 0:
        logger.info(f"🎯 Found best cache match: {best_match}")
        logger.info(f"   Score: {best_score:.2f}")
        logger.info(f"   Cache columns: {best_metadata.get('string_columns', [])}")
        logger.info(f"   Target columns: {target_columns}")
        return best_match, best_metadata
    
    return None


def warm_up_simple_string_cache_from_local(
    string_cache_instance,
    string_columns: List[str],
    cache_dir: Optional[str] = None
) -> Tuple[int, Optional[set]]:
    """
    Warm up SimpleStringCache from local cache file if available.
    
    This function:
    1. Searches for best-matching cache file
    2. Loads embeddings from pickle
    3. Temporarily patches the string server client to return cached embeddings
    4. Calls get_embedding_from_cache for each string to populate @lru_cache
    5. Restores original string server client
    
    Args:
        string_cache_instance: SimpleStringCache instance to warm up
        string_columns: List of string column names
        cache_dir: Directory to search for cache files (default: {featrix_root}/strings_cache/)
        
    Returns:
        Tuple of (number of strings loaded from cache, set of cached strings)
        Returns (0, None) if no cache found
    """
    if cache_dir is None:
        cache_dir = _get_strings_cache_dir()
    
    # Find best matching cache
    result = find_best_cache_match(string_columns, cache_dir)
    
    if result is None:
        logger.info("ℹ️  No matching local string cache found - will warm up from string server")
        return 0, None
    
    pickle_path, metadata = result
    
    # Load embeddings
    try:
        embeddings_dict = load_local_string_cache(pickle_path)
    except Exception as e:
        logger.warning(f"⚠️  Failed to load cache file {pickle_path}: {e}")
        return 0, None
    
    # Warm up the cache by temporarily patching the string server client
    logger.info(f"🔥 Warming up SimpleStringCache from local cache...")
    logger.info(f"   Loading {len(embeddings_dict)} strings...")
    
    # Get the string server client from the instance
    original_client = string_cache_instance._string_server_client
    
    # Create a wrapper that returns cached embeddings
    class CachedStringServerClient:
        def __init__(self, embeddings_dict, original_client):
            self._embeddings = embeddings_dict
            self._original = original_client
        
        def encode(self, text):
            # Return cached embedding if available, otherwise fall back to original
            if text in self._embeddings:
                # Convert numpy array to list (string server returns list)
                return self._embeddings[text].tolist()
            # Fall back to original if not in cache
            return self._original.encode(text)
        
        def encode_batch(self, texts):
            # Return cached embeddings for batch
            results = []
            for text in texts:
                if text in self._embeddings:
                    results.append(self._embeddings[text].tolist())
                else:
                    results.append(self._original.encode(text))
            return results
    
    # Temporarily replace the client
    cached_client = CachedStringServerClient(embeddings_dict, original_client)
    string_cache_instance._string_server_client = cached_client
    
    # Also update the global registry
    from featrix.neural.simple_string_cache import _STRING_SERVER_CLIENTS
    _STRING_SERVER_CLIENTS[string_cache_instance._client_id] = cached_client
    
    try:
        # Now call get_embedding_from_cache for each string to populate @lru_cache
        # This will use our cached client and populate the cache
        from featrix.neural.simple_string_cache import _cached_encode
        
        client_id = string_cache_instance._client_id
        client_encode_func_key = string_cache_instance._client_encode_func_key
        
        num_warmed = 0
        log_interval = max(1000, len(embeddings_dict) // 10)
        
        for i, (text, embedding) in enumerate(embeddings_dict.items(), 1):
            # Call _cached_encode which will use our patched client and cache the result
            _cached_encode(client_id, text, client_encode_func_key)
            num_warmed += 1
            
            if i % log_interval == 0:
                logger.info(f"   Progress: {i}/{len(embeddings_dict)} ({100*i//len(embeddings_dict)}%)")
        
        logger.info(f"✅ Warmed up {num_warmed} strings in SimpleStringCache")
        
        # Return the set of strings that were loaded from cache
        cached_strings_set = set(embeddings_dict.keys())
        
    finally:
        # Restore original client
        string_cache_instance._string_server_client = original_client
        _STRING_SERVER_CLIENTS[string_cache_instance._client_id] = original_client
    
    return num_warmed, cached_strings_set


def get_string_columns_from_dataset(dataset: Any) -> List[str]:
    """
    Extract list of string column names from a FeatrixInputDataSet.
    
    Args:
        dataset: FeatrixInputDataSet instance
        
    Returns:
        List of string column names
    """
    from featrix.neural.model_config import ColumnType
    
    string_columns = []
    for col_name, codec in dataset.column_codecs().items():
        if codec == ColumnType.FREE_STRING:
            string_columns.append(col_name)
    
    return string_columns


def extract_embeddings_from_simple_string_cache(
    string_cache_instance,
    string_list: List[str]
) -> Dict[str, np.ndarray]:
    """
    Extract embeddings from SimpleStringCache's @lru_cache for given strings.
    
    This function accesses the internal @lru_cache to extract already-computed
    embeddings. Only works for strings that have already been encoded.
    
    Args:
        string_cache_instance: SimpleStringCache instance
        string_list: List of strings to extract embeddings for
        
    Returns:
        Dict mapping string -> numpy array embedding (only for strings found in cache)
    """
    from featrix.neural.simple_string_cache import _cached_encode
    
    embeddings_dict = {}
    client_id = string_cache_instance._client_id
    client_encode_func_key = string_cache_instance._client_encode_func_key
    
    # Access the @lru_cache's internal cache dict
    # @lru_cache stores results in a .cache attribute which is a dict-like object
    # The cache key is (client_id, sentence_text, client_encode_func_key)
    try:
        # Access the cache's internal storage
        # @lru_cache stores cache in a .cache attribute (but it's a _lru_cache_wrapper)
        # We can access it via the function's __wrapped__ or directly
        if hasattr(_cached_encode, 'cache'):
            cache_storage = _cached_encode.cache
            # The cache is a dict-like object with keys as tuples: (client_id, text, func_key)
            for text in string_list:
                if not text or not isinstance(text, str):
                    continue
                
                text = text.strip()
                if not text:
                    continue
                
                # Check if this string is in the cache
                cache_key = (client_id, text, client_encode_func_key)
                if cache_key in cache_storage:
                    # Get the cached embedding (list of floats)
                    embedding_list = cache_storage[cache_key]
                    # Convert to numpy array
                    embeddings_dict[text] = np.array(embedding_list, dtype=np.float32)
    except Exception as e:
        logger.warning(f"⚠️  Could not access @lru_cache directly: {e}")
        logger.warning("   Falling back to checking cache via get_embedding_from_cache")
        
        # Fallback: try to get from cache (but this will encode if not cached)
        # We'll check cache_info first to see if it's likely cached
        # pylint: disable=no-value-for-parameter
        cache_info = _cached_encode.cache_info()
        if cache_info.currsize > 0:
            # Some strings are cached, try to get them
            # But this is risky as it might trigger encoding
            logger.warning("   Note: This may trigger string server calls for uncached strings")
    
    return embeddings_dict


def save_cache_from_dataset(
    dataset: Any,
    cache_dir: Optional[str] = None,
    extract_from_cache: bool = False,
    string_cache_instance: Optional[Any] = None
) -> Optional[Tuple[str, str]]:
    """
    Save local string cache from a dataset.
    
    This function:
    1. Extracts string columns from dataset
    2. Collects all unique string values from those columns
    3. Optionally extracts embeddings from SimpleStringCache if already computed
    4. Saves to pickle and JSON files
    
    Args:
        dataset: FeatrixInputDataSet instance
        cache_dir: Directory to save cache files (default: {featrix_root}/strings_cache/)
        extract_from_cache: If True, try to extract embeddings from string_cache_instance
        string_cache_instance: SimpleStringCache instance (required if extract_from_cache=True)
        
    Returns:
        Tuple of (pickle_path, json_path) if saved, else None
    """
    if cache_dir is None:
        cache_dir = _get_strings_cache_dir()
    
    # Get string columns
    string_columns = get_string_columns_from_dataset(dataset)
    
    if not string_columns:
        logger.info("ℹ️  No string columns found in dataset - nothing to cache")
        return None
    
    # Collect all unique string values
    all_strings = set()
    for col in string_columns:
        if col in dataset.df.columns:
            # Get all non-null string values
            col_values = dataset.df[col].astype(str).dropna()
            all_strings.update(col_values.unique())
    
    if not all_strings:
        logger.info("ℹ️  No string values found - nothing to cache")
        return None
    
    string_list = sorted(list(all_strings))
    logger.info(f"📝 Found {len(string_list)} unique strings across {len(string_columns)} string columns")
    
    # Get embeddings
    embeddings_dict = {}
    
    if extract_from_cache and string_cache_instance is not None:
        # Try to extract from cache
        logger.info("🔍 Extracting embeddings from SimpleStringCache...")
        embeddings_dict = extract_embeddings_from_simple_string_cache(
            string_cache_instance,
            string_list
        )
        logger.info(f"   Found {len(embeddings_dict)} cached embeddings")
    
    if not embeddings_dict:
        logger.warning("⚠️  No embeddings found in cache. Embeddings must be computed first.")
        logger.warning("   To save cache, ensure strings have been encoded via SimpleStringCache first.")
        return None
    
    # Save cache
    return save_local_string_cache(embeddings_dict, string_columns, cache_dir)

