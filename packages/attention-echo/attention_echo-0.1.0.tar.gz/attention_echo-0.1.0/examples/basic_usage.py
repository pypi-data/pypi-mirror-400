#!/usr/bin/env python3
"""Basic usage example for AttentionEcho with NumPy."""

import numpy as np
from attention_echo import AttentionEchoCache, EchoConfig


def main():
    """Demonstrate basic AttentionEcho usage."""
    print("=" * 60)
    print("AttentionEcho - Basic Usage Example")
    print("=" * 60)
    
    config = EchoConfig(
        capacity=100,
        similarity_threshold=0.80,
        adjustment_strength=0.1,
    )
    cache = AttentionEchoCache(config)
    
    np.random.seed(42)
    hidden_dim = 64
    
    system_prompt = np.random.randn(10, hidden_dim)
    system_prompt = system_prompt / np.linalg.norm(system_prompt, axis=-1, keepdims=True)
    
    print("\n[Request 1] System prompt + 'What is Python?'")
    print("-" * 40)
    
    query1_unique = np.random.randn(3, hidden_dim)
    query1 = np.vstack([system_prompt, query1_unique])
    key1 = query1 + np.random.randn(*query1.shape) * 0.1
    value1 = np.random.randn(*query1.shape)
    
    output1, meta1 = cache.attention_with_echo(
        query=query1,
        key=key1,
        value=value1,
        prefix_length=10,
        prefix_embeddings=system_prompt,
    )
    
    print(f"  Echo hit:        {meta1['echo_hit']}")
    print(f"  Compute mode:    {meta1['compute_mode']}")
    print(f"  Tokens computed: {meta1['tokens_computed']}")
    print(f"  Output shape:    {output1.shape}")
    
    print("\n[Request 2] Same system prompt + 'What is JavaScript?'")
    print("-" * 40)
    
    similar_prompt = system_prompt * 1.02 + np.random.randn(*system_prompt.shape) * 0.01
    query2_unique = np.random.randn(4, hidden_dim)
    query2 = np.vstack([similar_prompt, query2_unique])
    key2 = query2 + np.random.randn(*query2.shape) * 0.1
    value2 = np.random.randn(*query2.shape)
    
    output2, meta2 = cache.attention_with_echo(
        query=query2,
        key=key2,
        value=value2,
        prefix_length=10,
        prefix_embeddings=similar_prompt,
    )
    
    print(f"  Echo hit:        {meta2['echo_hit']}")
    print(f"  Similarity:      {meta2['similarity']:.3f}")
    print(f"  Compute mode:    {meta2['compute_mode']}")
    print(f"  Tokens echoed:   {meta2['tokens_echoed']}")
    print(f"  Tokens computed: {meta2['tokens_computed']}")
    print(f"  Output shape:    {output2.shape}")
    
    print("\n[Request 3] DIFFERENT system prompt")
    print("-" * 40)
    
    different_prompt = np.random.randn(10, hidden_dim)
    query3 = np.vstack([different_prompt, np.random.randn(2, hidden_dim)])
    key3 = query3 + np.random.randn(*query3.shape) * 0.1
    value3 = np.random.randn(*query3.shape)
    
    output3, meta3 = cache.attention_with_echo(
        query=query3,
        key=key3,
        value=value3,
        prefix_length=10,
        prefix_embeddings=different_prompt,
    )
    
    print(f"  Echo hit:        {meta3['echo_hit']}")
    print(f"  Similarity:      {meta3['similarity']:.3f}")
    print(f"  Compute mode:    {meta3['compute_mode']}")
    print(f"  Tokens computed: {meta3['tokens_computed']}")
    
    print("\n" + "=" * 60)
    print("Cache Statistics")
    print("=" * 60)
    stats = cache.stats
    print(f"  Total lookups:   {stats['total_lookups']}")
    print(f"  Cache hits:      {stats['hits']}")
    print(f"  Cache misses:    {stats['misses']}")
    print(f"  Hit rate:        {stats['hit_rate']:.1%}")
    print(f"  Cache size:      {stats['cache_size']}/{stats['capacity']}")
    print(f"  Ops saved:       {stats['ops_saved']:,}")
    
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    main()
