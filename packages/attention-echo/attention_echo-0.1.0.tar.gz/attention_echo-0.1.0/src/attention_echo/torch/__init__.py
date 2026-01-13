"""PyTorch integration for AttentionEcho."""

try:
    import torch
except ImportError:
    raise ImportError(
        "PyTorch is required for this module. "
        "Install with: pip install attention-echo[torch]"
    )

from attention_echo.torch.layers import EchoAttention, EchoMultiHeadAttention

__all__ = ["EchoAttention", "EchoMultiHeadAttention"]
