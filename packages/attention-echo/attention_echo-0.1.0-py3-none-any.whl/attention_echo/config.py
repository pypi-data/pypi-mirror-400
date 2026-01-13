"""Configuration for AttentionEcho cache."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class EchoConfig:
    """Configuration for the AttentionEcho cache.
    
    Attributes:
        capacity: Maximum number of patterns to cache.
        similarity_threshold: Minimum cosine similarity for a cache hit (0.0 to 1.0).
        max_prefix_length: Maximum prefix length to cache patterns for.
        adjustment_strength: Strength of the pattern adjustment (0.0 to 1.0).
        enable_jacobian: Whether to use Jacobian-based adjustment.
        hash_dim: Dimension of semantic hash keys.
        eviction_policy: Cache eviction policy ('lru' or 'lfu').
        per_layer: Whether to maintain separate caches per transformer layer.
    """
    
    capacity: int = 1000
    similarity_threshold: float = 0.85
    max_prefix_length: int = 2048
    adjustment_strength: float = 0.1
    enable_jacobian: bool = True
    hash_dim: int = 128
    eviction_policy: Literal["lru", "lfu"] = "lru"
    per_layer: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.capacity <= 0:
            raise ValueError(f"capacity must be positive, got {self.capacity}")
        
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError(
                f"similarity_threshold must be between 0 and 1, got {self.similarity_threshold}"
            )
        
        if not 0.0 <= self.adjustment_strength <= 1.0:
            raise ValueError(
                f"adjustment_strength must be between 0 and 1, got {self.adjustment_strength}"
            )
        
        if self.hash_dim <= 0:
            raise ValueError(f"hash_dim must be positive, got {self.hash_dim}")
        
        if self.max_prefix_length <= 0:
            raise ValueError(f"max_prefix_length must be positive, got {self.max_prefix_length}")
