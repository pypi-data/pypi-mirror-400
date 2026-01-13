#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
"""
Relationship Feature Search: Systematically explore relationship feature
configurations by trying 10 new combinations per training run until 50%
of search space is covered.
"""
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple

import requests

from featrix.neural.model_config import RelationshipFeatureConfig

logger = logging.getLogger(__name__)

# API endpoint for relationship feature search
RELATIONSHIP_SEARCH_API_URL = "https://sphere-api.featrix.com/meta/relationship-features"


def generate_relationship_combinations(
    n_cols: int,
    n_combinations: int = 10,
    exclude_combinations: Optional[List[str]] = None,
) -> List[RelationshipFeatureConfig]:
    """
    Generate n_combinations new relationship feature configurations.
    
    Args:
        n_cols: Number of columns
        n_combinations: Number of combinations to generate
        exclude_combinations: List of combination hashes to exclude (already tried)
    
    Returns:
        List of RelationshipFeatureConfig instances
    """
    exclude_hashes = set(exclude_combinations or [])
    
    # Define search space
    enable_options = [True, False]
    max_pairwise_ratios_options = [
        None,  # Auto-calculate
        100,
        250,
        500,
        1000,
        2000,
        min(5000, n_cols * (n_cols - 1) // 2),  # Up to all pairs
    ]
    target_sequence_length_options = [
        None,  # No target
        256,
        512,
        1024,
        2048,
    ]
    n_factors_options = [2, 4, 8, 16]
    
    combinations = []
    attempts = 0
    max_attempts = n_combinations * 100  # Try up to 100x to find unique combinations
    
    while len(combinations) < n_combinations and attempts < max_attempts:
        attempts += 1
        
        # Randomly sample from search space
        import random
        
        config_dict = {
            'enable_ratios': random.choice(enable_options),
            'enable_correlations': random.choice(enable_options),
            'enable_factors': random.choice(enable_options),
            'enable_mi_hints': random.choice(enable_options),
            'n_factors': random.choice(n_factors_options),
            'max_pairwise_ratios': random.choice(max_pairwise_ratios_options),
            'target_sequence_length': random.choice(target_sequence_length_options),
            'use_mi_filtering': random.choice(enable_options),
        }
        
        # At least one feature type must be enabled
        if not any([
            config_dict['enable_ratios'],
            config_dict['enable_correlations'],
            config_dict['enable_factors'],
            config_dict['enable_mi_hints'],
        ]):
            continue
        
        # Generate hash for this combination
        config_hash = _hash_combination(config_dict)
        
        # Skip if already tried
        if config_hash in exclude_hashes:
            continue
        
        # Create config
        try:
            config = RelationshipFeatureConfig(**config_dict)
            combinations.append(config)
            exclude_hashes.add(config_hash)
        except Exception as e:
            logger.warning(f"Failed to create RelationshipFeatureConfig: {e}")
            continue
    
    if len(combinations) < n_combinations:
        logger.warning(
            f"Only generated {len(combinations)}/{n_combinations} unique combinations "
            f"after {attempts} attempts"
        )
    
    return combinations


def _hash_combination(config_dict: Dict) -> str:
    """Generate hash for a relationship feature configuration."""
    # Sort keys for consistent hashing
    sorted_dict = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(sorted_dict.encode()).hexdigest()[:16]


def get_tried_combinations(
    n_cols: int,
    dataset_hash: Optional[str] = None,
) -> List[str]:
    """
    Query sphere-api for already-tried relationship feature combinations.
    
    Args:
        n_cols: Number of columns (for filtering)
        dataset_hash: Optional dataset hash to filter by dataset
    
    Returns:
        List of combination hashes that have been tried
    """
    try:
        response = requests.get(
            f"{RELATIONSHIP_SEARCH_API_URL}/tried",
            params={
                'n_cols': n_cols,
                'dataset_hash': dataset_hash,
            },
            timeout=5,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('combination_hashes', [])
        else:
            logger.warning(f"Failed to get tried combinations: {response.status_code}")
            return []
    except Exception as e:
        logger.warning(f"Error querying tried combinations: {e}")
        return []


def log_relationship_combination_result(
    n_cols: int,
    combination_config: RelationshipFeatureConfig,
    result: Dict[str, any],
    dataset_hash: Optional[str] = None,
    session_id: Optional[str] = None,
) -> bool:
    """
    Log relationship feature combination result to sphere-api.
    
    Args:
        n_cols: Number of columns
        combination_config: RelationshipFeatureConfig that was tried
        result: Dict with results (validation_loss, training_time, etc.)
        dataset_hash: Optional dataset hash
        session_id: Optional session ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert config to dict
        config_dict = combination_config.model_dump()
        combination_hash = _hash_combination(config_dict)
        
        payload = {
            'n_cols': n_cols,
            'combination_hash': combination_hash,
            'combination_config': config_dict,
            'result': result,
            'dataset_hash': dataset_hash,
            'session_id': session_id,
        }
        
        response = requests.post(
            f"{RELATIONSHIP_SEARCH_API_URL}/log",
            json=payload,
            timeout=10,
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Logged relationship combination result: {combination_hash}")
            return True
        else:
            logger.warning(f"Failed to log combination result: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"Error logging combination result: {e}")
        return False


def get_search_progress(
    n_cols: int,
    dataset_hash: Optional[str] = None,
) -> Dict[str, any]:
    """
    Get search progress (how many combinations tried, percentage of space covered).
    
    Returns:
        Dict with:
        - 'n_tried': Number of combinations tried
        - 'estimated_space_size': Estimated total search space size
        - 'coverage_percent': Percentage of space covered
        - 'should_continue': Whether to continue searching
    """
    tried_hashes = get_tried_combinations(n_cols, dataset_hash)
    n_tried = len(tried_hashes)
    
    # Estimate search space size
    # Rough estimate: 2^4 (enable flags) * 7 (max_pairwise_ratios) * 5 (target_seq_len) * 4 (n_factors)
    # = 2^4 * 7 * 5 * 4 = 16 * 140 = 2240 combinations
    estimated_space_size = 2240
    
    coverage_percent = (n_tried / estimated_space_size) * 100 if estimated_space_size > 0 else 0
    should_continue = coverage_percent < 50.0  # Stop at 50%
    
    return {
        'n_tried': n_tried,
        'estimated_space_size': estimated_space_size,
        'coverage_percent': coverage_percent,
        'should_continue': should_continue,
    }


def select_next_combinations(
    n_cols: int,
    n_combinations: int = 10,
    dataset_hash: Optional[str] = None,
) -> Tuple[List[RelationshipFeatureConfig], Dict[str, any]]:
    """
    Select next combinations to try, checking progress and excluding already-tried.
    
    Returns:
        Tuple of (combinations, progress_info)
    """
    # Get progress
    progress = get_search_progress(n_cols, dataset_hash)
    
    # Check if we should continue
    if not progress['should_continue']:
        logger.info(
            f"✅ Relationship feature search complete: {progress['coverage_percent']:.1f}% "
            f"coverage ({progress['n_tried']}/{progress['estimated_space_size']} combinations)"
        )
        return [], progress
    
    # Get already-tried combinations
    tried_hashes = get_tried_combinations(n_cols, dataset_hash)
    
    # Generate new combinations
    combinations = generate_relationship_combinations(
        n_cols=n_cols,
        n_combinations=n_combinations,
        exclude_combinations=tried_hashes,
    )
    
    logger.info(
        f"🔍 Relationship feature search: {progress['coverage_percent']:.1f}% coverage "
        f"({progress['n_tried']}/{progress['estimated_space_size']} tried). "
        f"Generated {len(combinations)} new combinations."
    )
    
    return combinations, progress

