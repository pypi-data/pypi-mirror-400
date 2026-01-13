#!/usr/bin/env python3
"""
Embedding Space I/O Utilities

Simple utility functions for saving and loading embedding spaces.
No dependencies on redis, job_manager, or other heavy infrastructure.
"""

def write_embedded_space(es, local_path: str):
    """
    Save embedding space as pickle file.
    Wrapper around write_embedding_space_pickle for backward compatibility.
    
    Args:
        es: EmbeddingSpace object to save
        local_path: Directory path where to save embedded_space.pickle
    """
    from featrix.neural.embedding_space_utils import write_embedding_space_pickle
    write_embedding_space_pickle(es, local_path)
    return









