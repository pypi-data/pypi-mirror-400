"""Tests for EchoConfig."""

import pytest
from attention_echo import EchoConfig


class TestEchoConfig:
    """Tests for EchoConfig validation."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = EchoConfig()
        
        assert config.capacity == 1000
        assert config.similarity_threshold == 0.85
        assert config.max_prefix_length == 2048
        assert config.adjustment_strength == 0.1
        assert config.enable_jacobian is True
        assert config.hash_dim == 128
        assert config.eviction_policy == "lru"
        assert config.per_layer is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = EchoConfig(
            capacity=500,
            similarity_threshold=0.9,
            max_prefix_length=1024,
        )
        
        assert config.capacity == 500
        assert config.similarity_threshold == 0.9
        assert config.max_prefix_length == 1024
    
    def test_invalid_capacity(self):
        """Test that invalid capacity raises error."""
        with pytest.raises(ValueError, match="capacity must be positive"):
            EchoConfig(capacity=0)
        
        with pytest.raises(ValueError, match="capacity must be positive"):
            EchoConfig(capacity=-1)
    
    def test_invalid_similarity_threshold(self):
        """Test that invalid similarity_threshold raises error."""
        with pytest.raises(ValueError, match="similarity_threshold"):
            EchoConfig(similarity_threshold=-0.1)
        
        with pytest.raises(ValueError, match="similarity_threshold"):
            EchoConfig(similarity_threshold=1.5)
    
    def test_invalid_adjustment_strength(self):
        """Test that invalid adjustment_strength raises error."""
        with pytest.raises(ValueError, match="adjustment_strength"):
            EchoConfig(adjustment_strength=-0.1)
        
        with pytest.raises(ValueError, match="adjustment_strength"):
            EchoConfig(adjustment_strength=1.5)
    
    def test_invalid_hash_dim(self):
        """Test that invalid hash_dim raises error."""
        with pytest.raises(ValueError, match="hash_dim must be positive"):
            EchoConfig(hash_dim=0)
