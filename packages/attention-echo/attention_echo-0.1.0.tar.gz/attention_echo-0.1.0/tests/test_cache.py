"""Tests for AttentionEchoCache."""

import pytest
import numpy as np
from attention_echo import AttentionEchoCache, EchoConfig


class TestAttentionEchoCache:
    """Tests for AttentionEchoCache."""
    
    @pytest.fixture
    def cache(self):
        """Create a cache with test configuration."""
        config = EchoConfig(
            capacity=10,
            similarity_threshold=0.8,
        )
        return AttentionEchoCache(config)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        hidden_dim = 32
        seq_len = 10
        prefix_len = 6
        
        return {
            "query": np.random.randn(seq_len, hidden_dim),
            "key": np.random.randn(seq_len, hidden_dim),
            "value": np.random.randn(seq_len, hidden_dim),
            "prefix_embeddings": np.random.randn(prefix_len, hidden_dim),
            "prefix_length": prefix_len,
        }
    
    def test_cache_miss_on_first_request(self, cache, sample_data):
        """Test that first request is a cache miss."""
        output, meta = cache.attention_with_echo(**sample_data)
        
        assert meta["echo_hit"] is False
        assert meta["compute_mode"] == "full"
        assert meta["tokens_computed"] == sample_data["query"].shape[0]
        assert output.shape == sample_data["value"].shape
    
    def test_cache_hit_on_similar_request(self, cache, sample_data):
        """Test cache hit with similar prefix."""
        cache.attention_with_echo(**sample_data)
        
        similar_embeddings = sample_data["prefix_embeddings"] * 1.01
        sample_data["prefix_embeddings"] = similar_embeddings
        
        output, meta = cache.attention_with_echo(**sample_data)
        
        assert meta["echo_hit"] is True
        assert meta["similarity"] > 0.8
        assert meta["tokens_echoed"] > 0
    
    def test_cache_miss_on_different_request(self, cache, sample_data):
        """Test cache miss with very different prefix."""
        cache.attention_with_echo(**sample_data)
        
        different_embeddings = np.random.randn(*sample_data["prefix_embeddings"].shape)
        sample_data["prefix_embeddings"] = different_embeddings
        
        output, meta = cache.attention_with_echo(**sample_data)
        
        assert meta["echo_hit"] is False
    
    def test_cache_stats(self, cache, sample_data):
        """Test cache statistics tracking."""
        cache.attention_with_echo(**sample_data)
        
        similar_embeddings = sample_data["prefix_embeddings"] * 1.01
        sample_data["prefix_embeddings"] = similar_embeddings
        cache.attention_with_echo(**sample_data)
        
        stats = cache.stats
        
        assert stats["total_lookups"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["cache_size"] == 1
    
    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        config = EchoConfig(capacity=2)
        cache = AttentionEchoCache(config)
        
        np.random.seed(42)
        
        for i in range(3):
            embeddings = np.random.randn(5, 32)
            data = {
                "query": np.random.randn(10, 32),
                "key": np.random.randn(10, 32),
                "value": np.random.randn(10, 32),
                "prefix_embeddings": embeddings,
                "prefix_length": 5,
            }
            cache.attention_with_echo(**data)
        
        assert len(cache) == 2
    
    def test_clear_cache(self, cache, sample_data):
        """Test clearing the cache."""
        cache.attention_with_echo(**sample_data)
        
        assert len(cache) > 0
        
        cache.clear()
        
        assert len(cache) == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0
    
    def test_semantic_key_computation(self, cache):
        """Test semantic key generation."""
        embeddings = np.random.randn(10, 64)
        
        key = cache.compute_semantic_key(embeddings)
        
        assert key.shape == (cache.config.hash_dim,)
        assert np.allclose(np.linalg.norm(key), 1.0, atol=1e-6)
    
    def test_output_shape(self, cache, sample_data):
        """Test that output shape matches value shape."""
        output, _ = cache.attention_with_echo(**sample_data)
        
        assert output.shape == sample_data["value"].shape
    
    def test_repr(self, cache, sample_data):
        """Test string representation."""
        cache.attention_with_echo(**sample_data)
        
        repr_str = repr(cache)
        
        assert "AttentionEchoCache" in repr_str
        assert "size=" in repr_str
        assert "hit_rate=" in repr_str


class TestUtils:
    """Tests for utility functions."""
    
    def test_cosine_similarity(self):
        """Test cosine similarity computation."""
        from attention_echo import cosine_similarity
        
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        
        assert np.isclose(cosine_similarity(a, b), 1.0)
        
        b = np.array([0.0, 1.0, 0.0])
        assert np.isclose(cosine_similarity(a, b), 0.0, atol=1e-6)
        
        b = np.array([-1.0, 0.0, 0.0])
        assert np.isclose(cosine_similarity(a, b), -1.0)
    
    def test_normalize(self):
        """Test L2 normalization."""
        from attention_echo import normalize
        
        x = np.array([3.0, 4.0])
        
        normalized = normalize(x)
        
        assert np.isclose(np.linalg.norm(normalized), 1.0)
        assert np.allclose(normalized, np.array([0.6, 0.8]))
