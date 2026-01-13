#!/usr/bin/env python3
"""Benchmark AttentionEcho performance."""

import time
import numpy as np
from attention_echo import AttentionEchoCache, EchoConfig


def benchmark_attention_echo(
    num_requests: int = 100,
    seq_length: int = 512,
    prefix_length: int = 256,
    hidden_dim: int = 768,
    similarity_ratio: float = 0.8,
) -> dict:
    """Run performance benchmark.
    
    Args:
        num_requests: Number of requests to simulate.
        seq_length: Total sequence length.
        prefix_length: Length of cacheable prefix.
        hidden_dim: Hidden dimension.
        similarity_ratio: Ratio of requests with similar prefixes.
        
    Returns:
        Dictionary with benchmark results.
    """
    config = EchoConfig(
        capacity=1000,
        similarity_threshold=0.85,
    )
    cache = AttentionEchoCache(config)
    
    np.random.seed(42)
    
    num_unique_prefixes = max(1, int(num_requests * (1 - similarity_ratio)))
    base_prefixes = [
        np.random.randn(prefix_length, hidden_dim) 
        for _ in range(num_unique_prefixes)
    ]
    
    echo_times = []
    standard_times = []
    
    for i in range(num_requests):
        base_prefix = base_prefixes[i % num_unique_prefixes]
        noise = np.random.randn(*base_prefix.shape) * 0.05
        prefix = base_prefix + noise
        
        suffix = np.random.randn(seq_length - prefix_length, hidden_dim)
        query = np.vstack([prefix, suffix])
        key = query + np.random.randn(*query.shape) * 0.1
        value = np.random.randn(*query.shape)
        
        start = time.perf_counter()
        output, meta = cache.attention_with_echo(
            query=query,
            key=key,
            value=value,
            prefix_length=prefix_length,
            prefix_embeddings=prefix,
        )
        echo_time = time.perf_counter() - start
        echo_times.append(echo_time)
        
        start = time.perf_counter()
        scale = 1.0 / np.sqrt(hidden_dim)
        scores = (query @ key.T) * scale
        mask = np.triu(np.ones((seq_length, seq_length)), k=1) * -1e9
        scores = scores + mask
        exp_scores = np.exp(scores - scores.max(axis=-1, keepdims=True))
        attn_weights = exp_scores / exp_scores.sum(axis=-1, keepdims=True)
        standard_output = attn_weights @ value
        standard_time = time.perf_counter() - start
        standard_times.append(standard_time)
    
    stats = cache.stats
    
    avg_echo = np.mean(echo_times) * 1000
    avg_standard = np.mean(standard_times) * 1000
    speedup = avg_standard / avg_echo if avg_echo > 0 else 0
    
    return {
        "num_requests": num_requests,
        "seq_length": seq_length,
        "prefix_length": prefix_length,
        "similarity_ratio": similarity_ratio,
        "avg_echo_time_ms": avg_echo,
        "avg_standard_time_ms": avg_standard,
        "speedup": speedup,
        "cache_hit_rate": stats["hit_rate"],
        "ops_saved": stats["ops_saved"],
    }


def main():
    """Run benchmarks with different configurations."""
    print("=" * 70)
    print("AttentionEcho Performance Benchmark")
    print("=" * 70)
    
    configs = [
        {"similarity_ratio": 0.9, "prefix_length": 256},
        {"similarity_ratio": 0.7, "prefix_length": 256},
        {"similarity_ratio": 0.5, "prefix_length": 256},
        {"similarity_ratio": 0.9, "prefix_length": 512},
        {"similarity_ratio": 0.9, "prefix_length": 128},
    ]
    
    results = []
    for cfg in configs:
        print(f"\nRunning: similarity={cfg['similarity_ratio']:.0%}, "
              f"prefix_len={cfg['prefix_length']}...")
        
        result = benchmark_attention_echo(
            num_requests=50,
            seq_length=512,
            prefix_length=cfg["prefix_length"],
            similarity_ratio=cfg["similarity_ratio"],
        )
        results.append(result)
    
    print("\n" + "=" * 70)
    print("Results Summary")
    print("=" * 70)
    print(f"{'Similarity':<12} {'Prefix':<8} {'Echo (ms)':<12} "
          f"{'Standard (ms)':<14} {'Speedup':<10} {'Hit Rate':<10}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['similarity_ratio']:<12.0%} "
              f"{r['prefix_length']:<8} "
              f"{r['avg_echo_time_ms']:<12.3f} "
              f"{r['avg_standard_time_ms']:<14.3f} "
              f"{r['speedup']:<10.2f}x "
              f"{r['cache_hit_rate']:<10.1%}")
    
    print("\n✓ Benchmark complete!")


if __name__ == "__main__":
    main()
