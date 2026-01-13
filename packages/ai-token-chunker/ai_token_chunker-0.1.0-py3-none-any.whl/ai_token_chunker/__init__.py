"""ai_token_chunker - Defensive preflight layer for LLM API calls."""

from .chunker import chunk_prompt
from .errors import (
    ChunkerError,
    ProviderNotSupportedError,
    LimitExceededError,
    ImageLimitError,
    InvalidInputError
)

__version__ = "0.1.0"

__all__ = [
    "chunk_prompt",
    "ChunkerError",
    "ProviderNotSupportedError",
    "LimitExceededError",
    "ImageLimitError",
    "InvalidInputError",
]

