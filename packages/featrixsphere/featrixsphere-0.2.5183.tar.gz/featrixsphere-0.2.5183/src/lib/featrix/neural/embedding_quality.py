"""
Embedding Space Quality Assessment

Provides comprehensive metrics to evaluate embedding space quality:
- Overall Quality Score
- Separation (class separation quality)
- Clustering (similarity grouping quality)
- Data Interpolation (smoothness and interpolation quality)
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def compute_embedding_quality_metrics(
    embeddings: torch.Tensor,
    labels: Optional[List[Any]] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, float]:
    """
    Compute comprehensive quality metrics for an embedding space.
    
    Args:
        embeddings: Tensor of shape (n_samples, d_model) - embedding vectors
        labels: Optional list of labels for each sample (for separation metrics)
        metadata: Optional metadata dict with additional info
        
    Returns:
        Dict with quality scores:
        - overall_score: Combined quality score [0, 1]
        - separation_score: Class separation quality [0, 1]
        - clustering_score: Clustering quality [0, 1]
        - interpolation_score: Interpolation smoothness [0, 1]
        - detailed_metrics: Dict with detailed sub-metrics
    """
    embeddings_np = embeddings.detach().cpu().numpy() if isinstance(embeddings, torch.Tensor) else embeddings
    n_samples, d_model = embeddings_np.shape
    
    results = {
        'overall_score': 0.0,
        'separation_score': 0.0,
        'clustering_score': 0.0,
        'interpolation_score': 0.0,
        'detailed_metrics': {}
    }
    
    # 1. SEPARATION METRICS (if labels provided)
    if labels is not None and len(set(labels)) > 1:
        separation_metrics = compute_separation_metrics(embeddings_np, labels)
        results['separation_score'] = separation_metrics['score']
        results['detailed_metrics']['separation'] = separation_metrics
    else:
        results['separation_score'] = 0.5  # Neutral if no labels
        results['detailed_metrics']['separation'] = {'score': 0.5, 'note': 'No labels provided'}
    
    # 2. CLUSTERING METRICS
    clustering_metrics = compute_clustering_metrics(embeddings_np)
    results['clustering_score'] = clustering_metrics['score']
    results['detailed_metrics']['clustering'] = clustering_metrics
    
    # 3. INTERPOLATION METRICS
    interpolation_metrics = compute_interpolation_metrics(embeddings_np)
    results['interpolation_score'] = interpolation_metrics['score']
    results['detailed_metrics']['interpolation'] = interpolation_metrics
    
    # 4. OVERALL SCORE (weighted combination)
    weights = {
        'separation': 0.3,
        'clustering': 0.35,
        'interpolation': 0.35
    }
    results['overall_score'] = (
        weights['separation'] * results['separation_score'] +
        weights['clustering'] * results['clustering_score'] +
        weights['interpolation'] * results['interpolation_score']
    )
    
    return results


def compute_separation_metrics(embeddings: np.ndarray, labels: List[Any]) -> Dict[str, float]:
    """
    Compute class separation quality metrics.
    
    Metrics:
    - Silhouette score: How well separated are different classes
    - Between-class distance: Average distance between class centroids
    - Within-class compactness: How tight are samples within each class
    """
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import LabelEncoder
    
    # Encode labels to numeric
    le = LabelEncoder()
    labels_encoded = le.fit_transform(labels)
    n_classes = len(le.classes_)
    
    if n_classes < 2:
        return {'score': 0.5, 'note': 'Need at least 2 classes for separation metrics'}
    
    # Silhouette score (higher is better, range [-1, 1], normalize to [0, 1])
    try:
        silhouette = silhouette_score(embeddings, labels_encoded)
        silhouette_normalized = (silhouette + 1) / 2  # Map [-1, 1] to [0, 1]
    except Exception as e:
        logger.warning(f"Could not compute silhouette score: {e}")
        silhouette_normalized = 0.5
    
    # Between-class distance (average distance between class centroids)
    class_centroids = {}
    for class_id in range(n_classes):
        class_mask = labels_encoded == class_id
        if class_mask.sum() > 0:
            class_centroids[class_id] = embeddings[class_mask].mean(axis=0)
    
    if len(class_centroids) < 2:
        between_class_dist = 0.0
    else:
        centroid_pairs = []
        for i, c1 in class_centroids.items():
            for j, c2 in class_centroids.items():
                if i < j:
                    dist = np.linalg.norm(c1 - c2)
                    centroid_pairs.append(dist)
        between_class_dist = np.mean(centroid_pairs) if centroid_pairs else 0.0
    
    # Within-class compactness (inverse of average within-class std)
    within_class_stds = []
    for class_id in range(n_classes):
        class_mask = labels_encoded == class_id
        if class_mask.sum() > 1:
            class_embeddings = embeddings[class_mask]
            class_std = np.mean(np.std(class_embeddings, axis=0))
            within_class_stds.append(class_std)
    
    avg_within_class_std = np.mean(within_class_stds) if within_class_stds else 1.0
    compactness = 1.0 / (1.0 + avg_within_class_std)  # Normalize to [0, 1]
    
    # Combined separation score
    # Higher between-class distance and lower within-class std = better separation
    separation_score = (
        0.5 * silhouette_normalized +
        0.3 * min(1.0, between_class_dist / 2.0) +  # Normalize assuming max dist ~2.0 for normalized embeddings
        0.2 * compactness
    )
    
    return {
        'score': float(separation_score),
        'silhouette_score': float(silhouette_normalized),
        'between_class_distance': float(between_class_dist),
        'within_class_compactness': float(compactness),
        'n_classes': int(n_classes)
    }


def compute_clustering_metrics(embeddings: np.ndarray) -> Dict[str, float]:
    """
    Compute clustering quality metrics.
    
    Metrics:
    - Inertia (within-cluster sum of squares) - lower is better
    - Calinski-Harabasz index - higher is better
    - Density: How well distributed are the embeddings
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import calinski_harabasz_score
    
    n_samples = embeddings.shape[0]
    
    # Use optimal number of clusters (sqrt of samples, capped)
    n_clusters = min(int(np.sqrt(n_samples)), 10, n_samples // 2)
    n_clusters = max(2, n_clusters)  # At least 2 clusters
    
    if n_samples < n_clusters:
        return {'score': 0.5, 'note': 'Not enough samples for clustering'}
    
    try:
        # KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # Inertia (within-cluster sum of squares) - normalize
        inertia = kmeans.inertia_
        # Normalize by number of samples and dimensions
        inertia_normalized = 1.0 / (1.0 + inertia / (n_samples * embeddings.shape[1]))
        
        # Calinski-Harabasz score (higher is better)
        try:
            ch_score = calinski_harabasz_score(embeddings, cluster_labels)
            # Normalize (typical range is 0-1000+, normalize to [0, 1])
            ch_normalized = min(1.0, ch_score / 100.0)
        except Exception:
            ch_normalized = 0.5
        
        # Density: Average distance to nearest neighbors
        from sklearn.neighbors import NearestNeighbors
        n_neighbors = min(5, n_samples - 1)
        if n_neighbors > 0:
            nn = NearestNeighbors(n_neighbors=n_neighbors + 1)  # +1 to exclude self
            nn.fit(embeddings)
            distances, _ = nn.kneighbors(embeddings)
            avg_neighbor_dist = np.mean(distances[:, 1:])  # Exclude self (distance 0)
            # Lower distance = higher density = better
            density_score = 1.0 / (1.0 + avg_neighbor_dist)
        else:
            density_score = 0.5
        
        clustering_score = (
            0.4 * inertia_normalized +
            0.3 * ch_normalized +
            0.3 * density_score
        )
        
        return {
            'score': float(clustering_score),
            'inertia_normalized': float(inertia_normalized),
            'calinski_harabasz_normalized': float(ch_normalized),
            'density_score': float(density_score),
            'n_clusters': int(n_clusters)
        }
        
    except Exception as e:
        logger.warning(f"Could not compute clustering metrics: {e}")
        return {'score': 0.5, 'error': str(e)}


def compute_interpolation_metrics(embeddings: np.ndarray) -> Dict[str, float]:
    """
    Compute interpolation/smoothness quality metrics.
    
    Metrics:
    - Smoothness: How smooth is the embedding manifold
    - Local linearity: How well can we interpolate between nearby points
    - Manifold quality: How well-structured is the embedding space
    """
    n_samples = embeddings.shape[0]
    
    if n_samples < 3:
        return {'score': 0.5, 'note': 'Not enough samples for interpolation metrics'}
    
    # 1. Local linearity: For each point, check if neighbors form a linear structure
    from sklearn.neighbors import NearestNeighbors
    
    n_neighbors = min(5, n_samples - 1)
    if n_neighbors < 2:
        return {'score': 0.5, 'note': 'Not enough neighbors for interpolation'}
    
    nn = NearestNeighbors(n_neighbors=n_neighbors + 1)
    nn.fit(embeddings)
    distances, indices = nn.kneighbors(embeddings)
    
    linearity_scores = []
    for i in range(min(100, n_samples)):  # Sample up to 100 points for efficiency
        neighbor_indices = indices[i, 1:]  # Exclude self
        neighbor_embeddings = embeddings[neighbor_indices]
        center = embeddings[i]
        
        # Check if neighbors are roughly collinear with center
        # Compute angles between vectors from center to neighbors
        vectors = neighbor_embeddings - center
        if len(vectors) >= 2:
            # Normalize vectors
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            normalized = vectors / norms
            
            # Compute pairwise cosine similarities (should be high for collinear points)
            if len(normalized) >= 2:
                cos_sims = []
                for j in range(len(normalized)):
                    for k in range(j + 1, len(normalized)):
                        cos_sim = np.dot(normalized[j], normalized[k])
                        cos_sims.append(cos_sim)
                
                if cos_sims:
                    # High cosine similarity = more collinear = better local linearity
                    avg_cos_sim = np.mean(cos_sims)
                    linearity_scores.append((avg_cos_sim + 1) / 2)  # Map [-1, 1] to [0, 1]
    
    avg_linearity = np.mean(linearity_scores) if linearity_scores else 0.5
    
    # 2. Smoothness: Check variance of distances to neighbors
    # Smooth manifold should have consistent neighbor distances
    neighbor_dist_vars = []
    for i in range(min(100, n_samples)):
        neighbor_dists = distances[i, 1:]  # Exclude self
        if len(neighbor_dists) > 1:
            dist_var = np.var(neighbor_dists)
            # Lower variance = smoother = better
            smoothness = 1.0 / (1.0 + dist_var)
            neighbor_dist_vars.append(smoothness)
    
    avg_smoothness = np.mean(neighbor_dist_vars) if neighbor_dist_vars else 0.5
    
    # 3. Manifold quality: Check if embeddings are well-distributed
    # Use variance of embedding norms (should be moderate, not too high or too low)
    embedding_norms = np.linalg.norm(embeddings, axis=1)
    norm_mean = np.mean(embedding_norms)
    norm_std = np.std(embedding_norms)
    
    # Good manifold: moderate variance (not collapsed, not too spread)
    # Normalize: std/mean should be around 0.1-0.3 for good quality
    cv = norm_std / (norm_mean + 1e-8)  # Coefficient of variation
    manifold_quality = 1.0 - min(1.0, abs(cv - 0.2) / 0.2)  # Peak at cv=0.2
    
    interpolation_score = (
        0.4 * avg_linearity +
        0.3 * avg_smoothness +
        0.3 * manifold_quality
    )
    
    return {
        'score': float(interpolation_score),
        'local_linearity': float(avg_linearity),
        'smoothness': float(avg_smoothness),
        'manifold_quality': float(manifold_quality),
        'norm_cv': float(cv)
    }


def compare_embedding_spaces(
    embeddings1: torch.Tensor,
    embeddings2: torch.Tensor,
    labels: Optional[List[Any]] = None,
    metadata1: Optional[Dict] = None,
    metadata2: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Compare two embedding spaces and compute difference scores.
    
    Args:
        embeddings1: First embedding space (n_samples, d_model)
        embeddings2: Second embedding space (n_samples, d_model)
        labels: Optional labels for separation metrics
        metadata1: Optional metadata for first space
        metadata2: Optional metadata for second space
        
    Returns:
        Dict with comparison metrics:
        - quality_scores_1: Quality metrics for first space
        - quality_scores_2: Quality metrics for second space
        - difference_score: Overall difference between spaces [0, 1]
        - embedding_difference: Direct embedding comparison metrics
        - recommendations: Suggestions based on comparison
    """
    # Compute quality metrics for both spaces
    quality1 = compute_embedding_quality_metrics(embeddings1, labels, metadata1)
    quality2 = compute_embedding_quality_metrics(embeddings2, labels, metadata2)
    
    # Direct embedding comparison
    emb1_np = embeddings1.detach().cpu().numpy() if isinstance(embeddings1, torch.Tensor) else embeddings1
    emb2_np = embeddings2.detach().cpu().numpy() if isinstance(embeddings2, torch.Tensor) else embeddings2
    
    # Ensure same shape
    min_samples = min(emb1_np.shape[0], emb2_np.shape[0])
    emb1_np = emb1_np[:min_samples]
    emb2_np = emb2_np[:min_samples]
    
    # Cosine similarity between corresponding embeddings
    cos_sims = []
    for i in range(min_samples):
        e1 = emb1_np[i]
        e2 = emb2_np[i]
        norm1 = np.linalg.norm(e1)
        norm2 = np.linalg.norm(e2)
        if norm1 > 0 and norm2 > 0:
            cos_sim = np.dot(e1, e2) / (norm1 * norm2)
            cos_sims.append(cos_sim)
    
    avg_cosine_sim = np.mean(cos_sims) if cos_sims else 0.0
    
    # Euclidean distance between embeddings
    euclidean_dists = np.linalg.norm(emb1_np - emb2_np, axis=1)
    avg_euclidean_dist = np.mean(euclidean_dists)
    
    # Difference score: 1 - similarity (higher = more different)
    difference_score = 1.0 - (avg_cosine_sim + 1) / 2  # Map [-1, 1] to [0, 1]
    
    # Generate recommendations
    recommendations = []
    
    if quality1['overall_score'] > quality2['overall_score']:
        recommendations.append(f"Space 1 has better overall quality ({quality1['overall_score']:.3f} vs {quality2['overall_score']:.3f})")
    elif quality2['overall_score'] > quality1['overall_score']:
        recommendations.append(f"Space 2 has better overall quality ({quality2['overall_score']:.3f} vs {quality1['overall_score']:.3f})")
    
    if quality1['separation_score'] > quality2['separation_score']:
        recommendations.append(f"Space 1 has better class separation ({quality1['separation_score']:.3f} vs {quality2['separation_score']:.3f})")
    
    if quality1['clustering_score'] > quality2['clustering_score']:
        recommendations.append(f"Space 1 has better clustering ({quality1['clustering_score']:.3f} vs {quality2['clustering_score']:.3f})")
    
    if quality1['interpolation_score'] > quality2['interpolation_score']:
        recommendations.append(f"Space 1 has better interpolation ({quality1['interpolation_score']:.3f} vs {quality2['interpolation_score']:.3f})")
    
    if avg_cosine_sim > 0.9:
        recommendations.append("Embeddings are very similar (cosine sim > 0.9)")
    elif avg_cosine_sim < 0.5:
        recommendations.append("Embeddings are quite different (cosine sim < 0.5)")
    
    return {
        'quality_scores_1': quality1,
        'quality_scores_2': quality2,
        'difference_score': float(difference_score),
        'embedding_difference': {
            'avg_cosine_similarity': float(avg_cosine_sim),
            'avg_euclidean_distance': float(avg_euclidean_dist),
            'cosine_similarity_range': [float(np.min(cos_sims)), float(np.max(cos_sims))] if cos_sims else [0.0, 0.0]
        },
        'recommendations': recommendations
    }


