"""PyTorch attention layers with AttentionEcho support.

IMPORTANT: AttentionEcho is an INFERENCE-ONLY optimization. The echo path
converts tensors to NumPy and back, which breaks gradient flow. These layers
should only be used during inference with torch.no_grad() or model.eval().
"""

from __future__ import annotations

import warnings
from typing import Optional, Dict, Any, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from attention_echo.config import EchoConfig
from attention_echo.cache import AttentionEchoCache


class EchoAttention(nn.Module):
    """Single-head attention with AttentionEcho caching.
    
    Drop-in replacement for standard scaled dot-product attention with
    automatic pattern caching and reuse.
    
    WARNING: This is an INFERENCE-ONLY optimization. The echo path breaks
    gradient flow. Use with torch.no_grad() or model.eval().
    
    Example:
        >>> attention = EchoAttention(hidden_dim=768)
        >>> with torch.no_grad():
        ...     output = attention(query, key, value, prefix_length=10)
        >>> print(attention.cache.stats)
    """
    
    def __init__(
        self,
        hidden_dim: int,
        config: Optional[EchoConfig] = None,
        layer_id: int = 0,
    ) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        self.config = config or EchoConfig()
        self.layer_id = layer_id
        self.cache = AttentionEchoCache(self.config)
        self.scale = hidden_dim ** -0.5
        self._warned_grad = False
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        prefix_length: int = 0,
        prefix_embeddings: Optional[torch.Tensor] = None,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        batch_size, seq_len, _ = query.shape
        
        if prefix_embeddings is None:
            prefix_embeddings = query[:, :prefix_length]
        
        if batch_size == 1 and prefix_length > 0:
            if query.requires_grad and not self._warned_grad:
                warnings.warn(
                    "EchoAttention is inference-only. Gradients will not flow "
                    "through the echo path. Use torch.no_grad() for inference.",
                    UserWarning,
                    stacklevel=2
                )
                self._warned_grad = True
            
            output, metadata = self._forward_with_echo(
                query.squeeze(0),
                key.squeeze(0),
                value.squeeze(0),
                prefix_length,
                prefix_embeddings.squeeze(0),
                attn_mask,
            )
            return output.unsqueeze(0), metadata
        
        output, metadata = self._forward_standard(query, key, value, attn_mask)
        return output, metadata
    
    @torch.no_grad()
    def _forward_with_echo(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        prefix_length: int,
        prefix_embeddings: torch.Tensor,
        attn_mask: Optional[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        device = query.device
        dtype = query.dtype
        
        q_np = query.cpu().numpy()
        k_np = key.cpu().numpy()
        v_np = value.cpu().numpy()
        emb_np = prefix_embeddings.cpu().numpy()
        
        output_np, metadata = self.cache.attention_with_echo(
            query=q_np,
            key=k_np,
            value=v_np,
            prefix_length=prefix_length,
            prefix_embeddings=emb_np,
            layer_id=self.layer_id,
            scale=self.scale,
        )
        
        output = torch.from_numpy(output_np).to(device=device, dtype=dtype)
        return output, metadata
    
    def _forward_standard(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attn_mask: Optional[torch.Tensor],
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        scores = torch.matmul(query, key.transpose(-2, -1)) * self.scale
        
        if attn_mask is not None:
            scores = scores + attn_mask
        
        attn_weights = F.softmax(scores, dim=-1)
        output = torch.matmul(attn_weights, value)
        
        metadata = {
            "echo_hit": False,
            "compute_mode": "standard",
            "tokens_computed": query.shape[-2],
        }
        
        return output, metadata


class EchoMultiHeadAttention(nn.Module):
    """Multi-head attention with AttentionEcho support.
    
    WARNING: This is an INFERENCE-ONLY optimization. The echo path breaks
    gradient flow. Use with torch.no_grad() or model.eval().
    """
    
    def __init__(
        self,
        hidden_dim: int,
        num_heads: int,
        config: Optional[EchoConfig] = None,
        layer_id: int = 0,
        dropout: float = 0.0,
        bias: bool = True,
    ) -> None:
        super().__init__()
        
        if hidden_dim % num_heads != 0:
            raise ValueError(
                f"hidden_dim ({hidden_dim}) must be divisible by num_heads ({num_heads})"
            )
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        self.config = config or EchoConfig()
        self.layer_id = layer_id
        
        self.q_proj = nn.Linear(hidden_dim, hidden_dim, bias=bias)
        self.k_proj = nn.Linear(hidden_dim, hidden_dim, bias=bias)
        self.v_proj = nn.Linear(hidden_dim, hidden_dim, bias=bias)
        self.out_proj = nn.Linear(hidden_dim, hidden_dim, bias=bias)
        
        self.dropout = nn.Dropout(dropout)
        
        self._head_caches = [
            AttentionEchoCache(self.config) for _ in range(num_heads)
        ]
        self.scale = self.head_dim ** -0.5
        self._warned_grad = False
    
    @property
    def cache(self) -> AttentionEchoCache:
        return self._head_caches[0]
    
    def get_stats(self) -> Dict[str, Any]:
        total_hits = sum(c.stats["hits"] for c in self._head_caches)
        total_misses = sum(c.stats["misses"] for c in self._head_caches)
        total_ops = sum(c.stats["ops_saved"] for c in self._head_caches)
        total_lookups = total_hits + total_misses
        
        return {
            "hits": total_hits,
            "misses": total_misses,
            "total_lookups": total_lookups,
            "hit_rate": total_hits / total_lookups if total_lookups > 0 else 0.0,
            "ops_saved": total_ops,
            "num_heads": self.num_heads,
        }
    
    def forward(
        self,
        hidden_states: torch.Tensor,
        prefix_length: int = 0,
        attention_mask: Optional[torch.Tensor] = None,
        use_echo: bool = True,
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        batch_size, seq_len, _ = hidden_states.shape
        
        query = self.q_proj(hidden_states)
        key = self.k_proj(hidden_states)
        value = self.v_proj(hidden_states)
        
        query = query.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        key = key.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        if use_echo and batch_size == 1 and prefix_length > 0:
            if hidden_states.requires_grad and not self._warned_grad:
                warnings.warn(
                    "EchoMultiHeadAttention is inference-only. Gradients will not "
                    "flow through the echo path. Use torch.no_grad() for inference.",
                    UserWarning,
                    stacklevel=2
                )
                self._warned_grad = True
            
            output, metadata = self._forward_with_echo_vectorized(
                query.squeeze(0),
                key.squeeze(0),
                value.squeeze(0),
                prefix_length,
                hidden_states.squeeze(0)[:prefix_length],
            )
            output = output.unsqueeze(0)
        else:
            scores = torch.matmul(query, key.transpose(-2, -1)) * self.scale
            
            if attention_mask is not None:
                scores = scores + attention_mask
            
            attn_weights = F.softmax(scores, dim=-1)
            attn_weights = self.dropout(attn_weights)
            
            output = torch.matmul(attn_weights, value)
            
            metadata = {
                "echo_hit": False,
                "compute_mode": "standard",
            }
        
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.hidden_dim)
        output = self.out_proj(output)
        
        return output, metadata
    
    @torch.no_grad()
    def _forward_with_echo_vectorized(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        prefix_length: int,
        prefix_embeddings: torch.Tensor,
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        num_heads, seq_len, head_dim = query.shape
        device = query.device
        dtype = query.dtype
        
        q_np = query.cpu().numpy()
        k_np = key.cpu().numpy()
        v_np = value.cpu().numpy()
        emb_np = prefix_embeddings.cpu().numpy()
        
        outputs = np.empty((num_heads, seq_len, head_dim), dtype=np.float32)
        all_hits = True
        total_echoed = 0
        total_computed = 0
        
        for h in range(num_heads):
            out_np, meta = self._head_caches[h].attention_with_echo(
                query=q_np[h],
                key=k_np[h],
                value=v_np[h],
                prefix_length=prefix_length,
                prefix_embeddings=emb_np,
                layer_id=self.layer_id * 100 + h,
                scale=self.scale,
            )
            
            outputs[h] = out_np
            all_hits = all_hits and meta.get("echo_hit", False)
            total_echoed += meta.get("tokens_echoed", 0)
            total_computed += meta.get("tokens_computed", 0)
        
        output = torch.from_numpy(outputs).to(device=device, dtype=dtype)
        
        metadata = {
            "echo_hit": all_hits,
            "tokens_echoed": total_echoed // num_heads,
            "tokens_computed": total_computed // num_heads,
            "compute_mode": "echo" if all_hits else "partial_echo",
        }
        
        return output, metadata
    
    def clear_cache(self) -> None:
        for cache in self._head_caches:
            cache.clear()
