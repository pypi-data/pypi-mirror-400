"""Main chunking logic."""

from typing import List, Dict, Optional, Union
from .providers import get_provider_limits
from .image import process_images
from .utils import (
    estimate_tokens,
    get_text_bytes,
    get_image_bytes,
    split_text_safely
)
from .errors import LimitExceededError, InvalidInputError


def chunk_prompt(
    provider: str,
    model: Optional[str],
    input: str,
    images: Optional[List[Union[bytes, str, Dict]]] = None,
    options: Optional[Dict] = None
) -> Dict:
    """
    Chunk a prompt into provider-compliant pieces.
    
    Args:
        provider: Provider name (e.g., "openai", "anthropic")
        model: Optional model name (e.g., "gpt-4", "claude-3-sonnet")
        input: Input text to chunk
        images: Optional list of images (bytes, base64 str, or dict)
        options: Optional dict with additional options
    
    Returns:
        {
            "chunks": [
                {
                    "text": str,
                    "images": list,
                    "index": int
                }
            ],
            "metadata": {
                "provider": str,
                "model": str | None,
                "total_chunks": int,
                "estimated_tokens": int,
                "estimated_bytes": int
            }
        }
    
    Raises:
        ProviderNotSupportedError: If provider is not supported
        LimitExceededError: If limits are exceeded
        ImageLimitError: If image limits are exceeded
        InvalidInputError: If input is invalid
    """
    if not isinstance(input, str):
        raise InvalidInputError(f"Input must be a string, got {type(input)}")
    
    if options is None:
        options = {}
    
    # Get provider limits
    limits = get_provider_limits(provider, model)
    
    # Process images
    processed_images = process_images(images, provider, model)
    
    # Validate images against limits
    if processed_images:
        image_count = len(processed_images)
        total_image_bytes = get_image_bytes(processed_images)
        limits.validate_images(image_count, total_image_bytes, provider, model)
    
    # Calculate text-only limits (accounting for images if needed)
    # For simplicity, we'll chunk text independently and attach images to chunks
    # In practice, images might reduce available text space, but we use conservative limits
    
    # Validate that input text itself doesn't exceed limits
    # If it does, we'll need to split it
    text_bytes = get_text_bytes(input)
    text_chars = len(input)
    text_tokens = estimate_tokens(input)
    
    # Check if we can fit everything in one chunk
    can_fit_single = (
        text_bytes <= limits.max_bytes and
        text_chars <= limits.max_chars and
        text_tokens <= limits.max_tokens
    )
    
    if can_fit_single:
        # Single chunk
        chunks = [{
            "text": input,
            "images": processed_images,
            "index": 0
        }]
    else:
        # Need to split text
        text_chunks = split_text_safely(
            input,
            limits.max_bytes,
            limits.max_chars,
            limits.max_tokens
        )
        
        chunks = []
        for idx, text_chunk in enumerate(text_chunks):
            # Attach images only to first chunk
            chunk_images = processed_images if idx == 0 else []
            
            chunks.append({
                "text": text_chunk,
                "images": chunk_images,
                "index": idx
            })
    
    # Calculate metadata
    total_tokens = sum(estimate_tokens(chunk["text"]) for chunk in chunks)
    total_bytes = sum(get_text_bytes(chunk["text"]) for chunk in chunks)
    if processed_images:
        total_bytes += get_image_bytes(processed_images)
    
    return {
        "chunks": chunks,
        "metadata": {
            "provider": provider,
            "model": model,
            "total_chunks": len(chunks),
            "estimated_tokens": total_tokens,
            "estimated_bytes": total_bytes
        }
    }

