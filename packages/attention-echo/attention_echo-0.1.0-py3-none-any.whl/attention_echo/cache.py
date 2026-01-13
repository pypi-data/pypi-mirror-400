"""Core AttentionEcho cache implementation."""

from __future__ import annotations

import time
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, List, Any

import numpy as np
from numpy.typing import NDArray

from attention_echo.config import EchoConfig
from attention_echo.utils import normalize, cosine_similarity, softmax, mean_pool


@dataclass
class EchoEntry:
    """A cached attention pattern entry.
    
    Attributes:
        semantic_key: Semantic hash of the prefix embeddings.
        query_embedding: Mean query embedding used to compute this pattern.
        attention_pattern: The cached attention weights.
        jacobian: Optional Jacobian for first-order adjustment.
        prefix_length: Number of tokens this pattern covers.
        layer_id: Which transformer layer this pattern is from.
        hit_count: Number of times this entry was used.
        created_at: Unix timestamp when entry was created.
    """
    
    semantic_key: NDArray[np.floating]
    query_embedding: NDArray[np.floating]
    attention_pattern: NDArray[np.floating]
    jacobian: Optional[NDArray[np.floating]] = None
    prefix_length: int = 0
    layer_id: int = 0
    hit_count: int = 0
    created_at: float = field(default_factory=time.time)


class AttentionEchoCache:
    """Cache that stores and retrieves attention patterns by semantic similarity.
    
    This is the core of AttentionEcho. Instead of caching KV tensors (like prefix
    caching), we cache the actual attention PATTERNS and adjust them for new queries.
    
    Thread-safe implementation with LRU eviction.
    
    Example:
        >>> config = EchoConfig(capacity=100, similarity_threshold=0.85)
        >>> cache = AttentionEchoCache(config)
        >>> 
        >>> # First request - compute and cache
        >>> output1, meta1 = cache.attention_with_echo(q1, k1, v1, 10, emb1)
        >>> print(meta1['echo_hit'])  # False
        >>> 
        >>> # Second request with similar prefix - cache hit!
        >>> output2, meta2 = cache.attention_with_echo(q2, k2, v2, 10, emb2)
        >>> print(meta2['echo_hit'])  # True
    """
    
    def __init__(self, config: Optional[EchoConfig] = None) -> None:
        """Initialize the cache.
        
        Args:
            config: Cache configuration. Uses defaults if not provided.
        """
        self.config = config or EchoConfig()
        self._cache: OrderedDict[str, EchoEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
    
    def compute_semantic_key(
        self, 
        embeddings: NDArray[np.floating]
    ) -> NDArray[np.floating]:
        """Compute a semantic hash from prefix embeddings.
        
        Uses mean pooling followed by normalization to create a fixed-size
        semantic key that similar prefixes will map to similar values.
        
        Args:
            embeddings: Token embeddings of shape (seq_len, hidden_dim).
            
        Returns:
            Semantic key of shape (hash_dim,).
        """
        if embeddings.size == 0:
            return np.zeros(self.config.hash_dim, dtype=np.float64)
        
        pooled = mean_pool(embeddings, axis=0)
        
        norm = np.linalg.norm(pooled)
        if norm < 1e-8:
            return np.zeros(self.config.hash_dim, dtype=np.float64)
        pooled = pooled / norm
        
        input_dim = len(pooled)
        if input_dim > self.config.hash_dim:
            pooled = pooled[:self.config.hash_dim]
        elif input_dim < self.config.hash_dim:
            repeat_times = (self.config.hash_dim + input_dim - 1) // input_dim
            pooled = np.tile(pooled, repeat_times)[:self.config.hash_dim]
            pooled = normalize(pooled)
        
        return pooled
    
    def find_echo(
        self, 
        query_key: NDArray[np.floating],
        layer_id: int = 0
    ) -> Tuple[Optional[EchoEntry], float]:
        """Find a similar cached attention pattern.
        
        Searches the cache for patterns with semantic keys similar to the query.
        Uses cosine similarity with configurable threshold.
        
        Args:
            query_key: Semantic key of the new request's prefix.
            layer_id: Transformer layer ID (if per_layer caching enabled).
            
        Returns:
            Tuple of (best matching entry or None, similarity score).
        """
        best_entry: Optional[EchoEntry] = None
        best_similarity = 0.0
        
        with self._lock:
            for cache_key, entry in self._cache.items():
                if self.config.per_layer and entry.layer_id != layer_id:
                    continue
                    
                sim = cosine_similarity(query_key, entry.semantic_key)
                
                if sim > best_similarity and sim >= self.config.similarity_threshold:
                    best_similarity = sim
                    best_entry = entry
            
            if best_entry is not None:
                self._stats.hits += 1
                best_entry.hit_count += 1
                key_str = self._key_to_str(best_entry.semantic_key)
                self._cache.move_to_end(key_str)
            else:
                self._stats.misses += 1
        
        return best_entry, best_similarity
    
    def apply_echo(
        self,
        cached_entry: EchoEntry,
        new_query: NDArray[np.floating],
        similarity: float
    ) -> NDArray[np.floating]:
        """Apply the echo transform to adjust a cached pattern for a new query.
        
        Uses first-order Taylor expansion to adjust the cached attention pattern
        based on the difference between the new and cached queries.
        
        Args:
            cached_entry: The cached attention pattern entry.
            new_query: Mean query embedding for the new request.
            similarity: Cosine similarity between old and new.
            
        Returns:
            Adjusted attention pattern.
        """
        pattern = cached_entry.attention_pattern.copy()
        old_query = cached_entry.query_embedding
        
        new_q_flat = new_query.flatten()
        old_q_flat = old_query.flatten()
        min_len = min(len(new_q_flat), len(old_q_flat))
        query_diff = new_q_flat[:min_len] - old_q_flat[:min_len]
        
        jacobian_applied = False
        if cached_entry.jacobian is not None and self.config.enable_jacobian:
            jacobian = cached_entry.jacobian
            head_dim = jacobian.shape[0]
            
            if head_dim == min_len and jacobian.shape[1:] == pattern.shape:
                adjustment = np.tensordot(query_diff, jacobian, axes=1)
                adjustment = adjustment * self.config.adjustment_strength
                pattern = pattern + adjustment
                jacobian_applied = True
        
        if not jacobian_applied:
            scale = 1.0 - (1.0 - similarity) * 0.3
            pattern = pattern * scale
        
        pattern = np.clip(pattern, 0, None)
        row_sums = pattern.sum(axis=-1, keepdims=True)
        pattern = pattern / (row_sums + 1e-8)
        
        n_tokens = pattern.shape[0]
        self._stats.ops_saved += n_tokens * n_tokens
        
        return pattern
    
    def store(
        self,
        semantic_key: NDArray[np.floating],
        query_embedding: NDArray[np.floating],
        attention_pattern: NDArray[np.floating],
        jacobian: Optional[NDArray[np.floating]] = None,
        prefix_length: int = 0,
        layer_id: int = 0
    ) -> None:
        """Store an attention pattern in the cache.
        
        Args:
            semantic_key: Semantic hash of the prefix.
            query_embedding: Mean query embedding.
            attention_pattern: The attention weights to cache.
            jacobian: Optional Jacobian for adjustment.
            prefix_length: Number of tokens in the prefix.
            layer_id: Transformer layer ID.
        """
        entry = EchoEntry(
            semantic_key=semantic_key.copy(),
            query_embedding=query_embedding.copy(),
            attention_pattern=attention_pattern.copy(),
            jacobian=jacobian.copy() if jacobian is not None else None,
            prefix_length=prefix_length,
            layer_id=layer_id,
            hit_count=0,
            created_at=time.time()
        )
        
        key_str = self._key_to_str(semantic_key)
        
        with self._lock:
            if len(self._cache) >= self.config.capacity:
                if self.config.eviction_policy == "lru":
                    self._cache.popitem(last=False)
                else:
                    self._evict_lfu()
            
            self._cache[key_str] = entry
    
    def attention_with_echo(
        self,
        query: NDArray[np.floating],
        key: NDArray[np.floating],
        value: NDArray[np.floating],
        prefix_length: int,
        prefix_embeddings: NDArray[np.floating],
        layer_id: int = 0,
        scale: Optional[float] = None
    ) -> Tuple[NDArray[np.floating], Dict[str, Any]]:
        """Compute attention with optional echo reuse.
        
        This is the main entry point for using AttentionEcho.
        
        Args:
            query: Query tensor of shape (seq_len, head_dim).
            key: Key tensor of shape (seq_len, head_dim).
            value: Value tensor of shape (seq_len, head_dim).
            prefix_length: How many tokens are "prefix" (cacheable).
            prefix_embeddings: Embeddings of prefix tokens.
            layer_id: Transformer layer ID.
            scale: Attention scale factor. Defaults to 1/sqrt(head_dim).
            
        Returns:
            Tuple of (attention output, metadata dict).
            
        Raises:
            ValueError: If input shapes are incompatible.
        """
        if query.ndim != 2:
            raise ValueError(f"query must be 2D (seq_len, head_dim), got shape {query.shape}")
        if key.ndim != 2:
            raise ValueError(f"key must be 2D (seq_len, head_dim), got shape {key.shape}")
        if value.ndim != 2:
            raise ValueError(f"value must be 2D (seq_len, head_dim), got shape {value.shape}")
        
        seq_len, head_dim = query.shape
        
        if key.shape[0] != seq_len:
            raise ValueError(
                f"query and key must have same seq_len, got {seq_len} and {key.shape[0]}"
            )
        if value.shape[0] != seq_len:
            raise ValueError(
                f"query and value must have same seq_len, got {seq_len} and {value.shape[0]}"
            )
        if key.shape[1] != head_dim:
            raise ValueError(
                f"query and key must have same head_dim, got {head_dim} and {key.shape[1]}"
            )
        
        scale = scale or (1.0 / np.sqrt(head_dim))
        
        prefix_length = min(prefix_length, self.config.max_prefix_length, seq_len)
        
        semantic_key = self.compute_semantic_key(prefix_embeddings)
        echo_entry, similarity = self.find_echo(semantic_key, layer_id)
        
        metadata: Dict[str, Any] = {
            "echo_hit": echo_entry is not None,
            "similarity": similarity,
            "layer_id": layer_id,
        }
        
        if echo_entry is not None:
            prefix_pattern = self.apply_echo(
                echo_entry,
                mean_pool(query[:prefix_length]),
                similarity
            )
            
            attn_weights = np.zeros((seq_len, seq_len))
            
            cached_len = min(prefix_length, prefix_pattern.shape[0])
            attn_weights[:cached_len, :cached_len] = prefix_pattern[:cached_len, :cached_len]
            
            if seq_len > cached_len:
                new_q = query[cached_len:]
                scores = (new_q @ key.T) * scale
                
                mask = np.triu(np.ones((seq_len - cached_len, seq_len)), k=cached_len + 1)
                scores = scores - mask * 1e9
                
                new_weights = softmax(scores)
                attn_weights[cached_len:, :] = new_weights
            
            metadata["tokens_echoed"] = cached_len
            metadata["tokens_computed"] = seq_len - cached_len
            metadata["compute_mode"] = "echo"
            
        else:
            scores = (query @ key.T) * scale
            
            mask = np.triu(np.ones((seq_len, seq_len)), k=1)
            scores = scores - mask * 1e9
            
            attn_weights = softmax(scores)
            
            if prefix_length > 0:
                prefix_query = query[:prefix_length]
                prefix_key = key[:prefix_length]
                query_mean = mean_pool(prefix_query)
                prefix_pattern = attn_weights[:prefix_length, :prefix_length]
                
                jacobian = None
                if self.config.enable_jacobian:
                    jacobian = self._compute_jacobian(
                        prefix_query, prefix_key, prefix_pattern, scale
                    )
                
                self.store(
                    semantic_key=semantic_key,
                    query_embedding=query_mean,
                    attention_pattern=prefix_pattern,
                    jacobian=jacobian,
                    prefix_length=prefix_length,
                    layer_id=layer_id
                )
            
            metadata["tokens_echoed"] = 0
            metadata["tokens_computed"] = seq_len
            metadata["compute_mode"] = "full"
        
        output = attn_weights @ value
        
        return output, metadata
    
    def _key_to_str(self, key: NDArray[np.floating]) -> str:
        """Convert numpy key to hashable string.
        
        Uses SHA-256 hash of the key bytes to ensure fixed-length output
        while avoiding collisions from truncation.
        """
        import hashlib
        key_bytes = key.astype(np.float32).tobytes()
        return hashlib.sha256(key_bytes).hexdigest()
    
    def _evict_lfu(self) -> None:
        """Evict the least frequently used entry."""
        if not self._cache:
            return
        
        min_hits = float("inf")
        min_key = None
        
        for key, entry in self._cache.items():
            if entry.hit_count < min_hits:
                min_hits = entry.hit_count
                min_key = key
        
        if min_key is not None:
            del self._cache[min_key]
    
    def _compute_jacobian(
        self,
        query: NDArray[np.floating],
        key: NDArray[np.floating],
        attention_pattern: NDArray[np.floating],
        scale: float
    ) -> NDArray[np.floating]:
        """Compute the Jacobian of attention pattern w.r.t. mean query.
        
        The Jacobian allows first-order Taylor expansion adjustment when
        reusing cached patterns for slightly different queries.
        
        For softmax attention: A = softmax(Q @ K.T * scale)
        The derivative of A w.r.t. Q involves the softmax Jacobian.
        
        We compute a simplified approximation: the sensitivity of the 
        mean-pooled attention pattern to changes in the mean query.
        
        Args:
            query: Query tensor of shape (prefix_len, head_dim).
            key: Key tensor of shape (prefix_len, head_dim).
            attention_pattern: Attention weights of shape (prefix_len, prefix_len).
            scale: Attention scale factor.
            
        Returns:
            Jacobian of shape (head_dim, prefix_len, prefix_len).
        """
        prefix_len, head_dim = query.shape
        
        jacobian = np.zeros((head_dim, prefix_len, prefix_len), dtype=np.float32)
        
        for i in range(prefix_len):
            a_i = attention_pattern[i]
            for d in range(head_dim):
                grad = scale * key[:, d] * a_i * (1 - a_i)
                for j in range(prefix_len):
                    if j != i:
                        grad[j] -= scale * key[j, d] * a_i[i] * a_i[j]
                jacobian[d, i, :] = grad / prefix_len
        
        return jacobian
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        with self._lock:
            total = self._stats.hits + self._stats.misses
            hit_rate = self._stats.hits / total if total > 0 else 0.0
            
            return {
                "hits": self._stats.hits,
                "misses": self._stats.misses,
                "total_lookups": total,
                "hit_rate": hit_rate,
                "cache_size": len(self._cache),
                "capacity": self.config.capacity,
                "ops_saved": self._stats.ops_saved,
            }
    
    def clear(self) -> None:
        """Clear all cached entries and reset stats."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)
    
    def __repr__(self) -> str:
        stats = self.stats
        return (
            f"AttentionEchoCache("
            f"size={stats['cache_size']}/{stats['capacity']}, "
            f"hit_rate={stats['hit_rate']:.2%})"
        )


@dataclass
class CacheStats:
    """Statistics for cache performance tracking."""
    
    hits: int = 0
    misses: int = 0
    ops_saved: int = 0
