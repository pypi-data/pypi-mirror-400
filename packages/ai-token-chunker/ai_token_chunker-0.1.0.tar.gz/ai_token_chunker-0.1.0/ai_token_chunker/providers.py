"""Provider definitions and limit configurations."""

from typing import Dict, Optional
from .limits import ProviderLimits
from .errors import ProviderNotSupportedError


# Provider limit definitions
# These are heuristics based on common provider limits
# Actual limits may vary by model and region

PROVIDER_LIMITS: Dict[str, Dict[str, ProviderLimits]] = {
    "openai": {
        "default": ProviderLimits(
            max_tokens=128000,  # GPT-4 Turbo
            max_chars=500000,
            max_bytes=2000000,
            max_images=10,
            image_byte_limit=20000000  # 20MB
        ),
        "gpt-4": ProviderLimits(
            max_tokens=8192,
            max_chars=32000,
            max_bytes=128000,
            max_images=10,
            image_byte_limit=20000000
        ),
        "gpt-4-turbo": ProviderLimits(
            max_tokens=128000,
            max_chars=500000,
            max_bytes=2000000,
            max_images=10,
            image_byte_limit=20000000
        ),
        "gpt-3.5-turbo": ProviderLimits(
            max_tokens=16385,
            max_chars=65000,
            max_bytes=260000,
            max_images=0,
            image_byte_limit=0
        ),
    },
    "google": {
        "default": ProviderLimits(
            max_tokens=32000,  # Gemini Pro
            max_chars=128000,
            max_bytes=512000,
            max_images=16,
            image_byte_limit=20000000
        ),
        "gemini-pro": ProviderLimits(
            max_tokens=32000,
            max_chars=128000,
            max_bytes=512000,
            max_images=16,
            image_byte_limit=20000000
        ),
        "gemini-pro-vision": ProviderLimits(
            max_tokens=16000,
            max_chars=64000,
            max_bytes=256000,
            max_images=16,
            image_byte_limit=20000000
        ),
    },
    "anthropic": {
        "default": ProviderLimits(
            max_tokens=200000,  # Claude 3.5 Sonnet
            max_chars=800000,
            max_bytes=3200000,
            max_images=20,
            image_byte_limit=50000000  # 50MB
        ),
        "claude-3-opus": ProviderLimits(
            max_tokens=200000,
            max_chars=800000,
            max_bytes=3200000,
            max_images=20,
            image_byte_limit=50000000
        ),
        "claude-3-sonnet": ProviderLimits(
            max_tokens=200000,
            max_chars=800000,
            max_bytes=3200000,
            max_images=20,
            image_byte_limit=50000000
        ),
        "claude-3-haiku": ProviderLimits(
            max_tokens=200000,
            max_chars=800000,
            max_bytes=3200000,
            max_images=20,
            image_byte_limit=50000000
        ),
    },
    "mistral": {
        "default": ProviderLimits(
            max_tokens=32000,
            max_chars=128000,
            max_bytes=512000,
            max_images=0,
            image_byte_limit=0
        ),
        "mistral-large": ProviderLimits(
            max_tokens=32000,
            max_chars=128000,
            max_bytes=512000,
            max_images=0,
            image_byte_limit=0
        ),
    },
    "cohere": {
        "default": ProviderLimits(
            max_tokens=4096,
            max_chars=16000,
            max_bytes=64000,
            max_images=0,
            image_byte_limit=0
        ),
    },
    "groq": {
        "default": ProviderLimits(
            max_tokens=32768,  # Mixtral
            max_chars=130000,
            max_bytes=520000,
            max_images=0,
            image_byte_limit=0
        ),
    },
    "azure": {
        "default": ProviderLimits(
            max_tokens=128000,  # Azure OpenAI GPT-4 Turbo
            max_chars=500000,
            max_bytes=2000000,
            max_images=10,
            image_byte_limit=20000000
        ),
    },
    "bedrock": {
        "default": ProviderLimits(
            max_tokens=200000,  # Claude on Bedrock
            max_chars=800000,
            max_bytes=3200000,
            max_images=20,
            image_byte_limit=50000000
        ),
    },
    "together": {
        "default": ProviderLimits(
            max_tokens=32000,
            max_chars=128000,
            max_bytes=512000,
            max_images=0,
            image_byte_limit=0
        ),
    },
    "ollama": {
        "default": ProviderLimits(
            max_tokens=32768,  # Common local model limit
            max_chars=130000,
            max_bytes=520000,
            max_images=0,
            image_byte_limit=0
        ),
    },
}


def get_provider_limits(provider: str, model: Optional[str] = None) -> ProviderLimits:
    """
    Get limits for a provider and optional model.
    
    Args:
        provider: Provider name (e.g., "openai", "anthropic")
        model: Optional model name (e.g., "gpt-4", "claude-3-sonnet")
    
    Returns:
        ProviderLimits instance
    
    Raises:
        ProviderNotSupportedError: If provider is not supported
    """
    provider_lower = provider.lower()
    
    if provider_lower not in PROVIDER_LIMITS:
        raise ProviderNotSupportedError(provider)
    
    provider_config = PROVIDER_LIMITS[provider_lower]
    
    # Try model-specific limits first
    if model:
        model_lower = model.lower()
        if model_lower in provider_config:
            return provider_config[model_lower]
    
    # Fall back to default
    if "default" in provider_config:
        return provider_config["default"]
    
    # Should not happen, but handle gracefully
    raise ProviderNotSupportedError(f"{provider} (no default limits configured)")

