"""Utility functions for AttentionEcho."""

import numpy as np
from numpy.typing import NDArray


def normalize(x: NDArray[np.floating]) -> NDArray[np.floating]:
    """L2 normalize a vector or batch of vectors.
    
    Args:
        x: Input array of shape (..., dim).
        
    Returns:
        Normalized array of the same shape.
    """
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / (norm + 1e-8)


def cosine_similarity(a: NDArray[np.floating], b: NDArray[np.floating]) -> float:
    """Compute cosine similarity between two vectors.
    
    Args:
        a: First vector of shape (dim,).
        b: Second vector of shape (dim,).
        
    Returns:
        Cosine similarity in range [-1, 1].
    """
    a_norm = normalize(a.flatten())
    b_norm = normalize(b.flatten())
    return float(np.dot(a_norm, b_norm))


def softmax(x: NDArray[np.floating], axis: int = -1) -> NDArray[np.floating]:
    """Compute softmax along an axis.
    
    Args:
        x: Input array.
        axis: Axis to compute softmax over.
        
    Returns:
        Softmax output of same shape as input.
    """
    x_max = np.max(x, axis=axis, keepdims=True)
    exp_x = np.exp(x - x_max)
    return exp_x / (np.sum(exp_x, axis=axis, keepdims=True) + 1e-8)


def mean_pool(embeddings: NDArray[np.floating], axis: int = 0) -> NDArray[np.floating]:
    """Mean pool embeddings along an axis.
    
    Args:
        embeddings: Input embeddings of shape (seq_len, dim).
        axis: Axis to pool over.
        
    Returns:
        Pooled embedding of shape (dim,).
    """
    return np.mean(embeddings, axis=axis)
