#!/usr/bin/env python3
"""Simulate multi-user serving scenario with AttentionEcho."""

import numpy as np
from dataclasses import dataclass
from typing import List
from attention_echo import AttentionEchoCache, EchoConfig


@dataclass
class Request:
    """Simulated user request."""
    user_id: str
    system_prompt: str
    user_query: str


def create_embedding(text: str, hidden_dim: int = 64) -> np.ndarray:
    """Create a deterministic embedding for text.
    
    Uses hash of text to seed random generator for reproducibility.
    """
    seed = hash(text) % (2**32)
    rng = np.random.RandomState(seed)
    emb = rng.randn(len(text.split()), hidden_dim)
    return emb / np.linalg.norm(emb, axis=-1, keepdims=True)


def simulate_serving(requests: List[Request], cache: AttentionEchoCache) -> dict:
    """Simulate serving multiple requests.
    
    Returns statistics about cache performance.
    """
    hidden_dim = 64
    results = []
    
    for req in requests:
        system_emb = create_embedding(req.system_prompt, hidden_dim)
        query_emb = create_embedding(req.user_query, hidden_dim)
        
        full_emb = np.vstack([system_emb, query_emb])
        seq_len = full_emb.shape[0]
        prefix_len = system_emb.shape[0]
        
        query = full_emb
        key = full_emb + np.random.randn(*full_emb.shape) * 0.05
        value = np.random.randn(*full_emb.shape)
        
        output, meta = cache.attention_with_echo(
            query=query,
            key=key,
            value=value,
            prefix_length=prefix_len,
            prefix_embeddings=system_emb,
        )
        
        results.append({
            "user_id": req.user_id,
            "echo_hit": meta["echo_hit"],
            "similarity": meta.get("similarity", 0),
            "tokens_echoed": meta.get("tokens_echoed", 0),
            "tokens_computed": meta["tokens_computed"],
        })
    
    return results


def main():
    """Run multi-user serving simulation."""
    print("=" * 60)
    print("AttentionEcho - Multi-User Serving Simulation")
    print("=" * 60)
    
    system_prompts = {
        "assistant": "You are a helpful AI assistant. You provide accurate and helpful responses.",
        "coder": "You are an expert programmer. Help with coding questions and debugging.",
        "translator": "You are a professional translator. Translate text accurately.",
    }
    
    requests = [
        Request("user1", system_prompts["assistant"], "What is machine learning?"),
        Request("user2", system_prompts["assistant"], "Explain neural networks."),
        Request("user3", system_prompts["coder"], "How do I reverse a string in Python?"),
        Request("user4", system_prompts["assistant"], "What are transformers?"),
        Request("user5", system_prompts["coder"], "Explain recursion."),
        Request("user6", system_prompts["assistant"], "What is deep learning?"),
        Request("user7", system_prompts["translator"], "Translate hello to French."),
        Request("user8", system_prompts["coder"], "What is a binary tree?"),
        Request("user9", system_prompts["assistant"], "How does attention work?"),
        Request("user10", system_prompts["translator"], "Translate goodbye to Spanish."),
    ]
    
    config = EchoConfig(
        capacity=100,
        similarity_threshold=0.70,
    )
    cache = AttentionEchoCache(config)
    
    print("\nProcessing requests...")
    print("-" * 60)
    
    results = simulate_serving(requests, cache)
    
    for i, (req, result) in enumerate(zip(requests, results)):
        status = "✓ HIT" if result["echo_hit"] else "✗ MISS"
        prompt_type = next(k for k, v in system_prompts.items() if v == req.system_prompt)
        print(f"  [{i+1:2}] {req.user_id:<8} ({prompt_type:<10}) - {status} "
              f"(sim: {result['similarity']:.2f})")
    
    print("\n" + "=" * 60)
    print("Summary by System Prompt Type")
    print("=" * 60)
    
    for prompt_type, prompt_text in system_prompts.items():
        prompt_results = [
            r for r, req in zip(results, requests) 
            if req.system_prompt == prompt_text
        ]
        hits = sum(1 for r in prompt_results if r["echo_hit"])
        total = len(prompt_results)
        hit_rate = hits / total if total > 0 else 0
        print(f"  {prompt_type:<12}: {hits}/{total} hits ({hit_rate:.0%})")
    
    print("\n" + "=" * 60)
    print("Cache Statistics")
    print("=" * 60)
    stats = cache.stats
    print(f"  Overall hit rate:  {stats['hit_rate']:.1%}")
    print(f"  Cache size:        {stats['cache_size']}")
    print(f"  Ops saved:         {stats['ops_saved']:,}")
    
    print("\n✓ Simulation complete!")


if __name__ == "__main__":
    main()
