"""AttentionEcho: Cross-request attention pattern reuse for LLM inference optimization."""

from attention_echo.config import EchoConfig
from attention_echo.cache import AttentionEchoCache, EchoEntry
from attention_echo.utils import cosine_similarity, normalize

__version__ = "0.1.0"
__all__ = [
    "EchoConfig",
    "AttentionEchoCache",
    "EchoEntry",
    "cosine_similarity",
    "normalize",
]
