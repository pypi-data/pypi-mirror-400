"""Provider limit definitions and validation."""

from typing import Dict, Optional
from .errors import LimitExceededError, ImageLimitError


class ProviderLimits:
    """Provider-specific limits."""
    
    def __init__(
        self,
        max_tokens: int,
        max_chars: int,
        max_bytes: int,
        max_images: int = 0,
        image_byte_limit: int = 0
    ):
        self.max_tokens = max_tokens
        self.max_chars = max_chars
        self.max_bytes = max_bytes
        self.max_images = max_images
        self.image_byte_limit = image_byte_limit
    
    def validate_text(
        self,
        text: str,
        provider: str,
        model: Optional[str] = None
    ) -> None:
        """Validate text against limits."""
        text_bytes = len(text.encode("utf-8"))
        text_chars = len(text)
        estimated_tokens = text_chars // 4
        
        if text_bytes > self.max_bytes:
            raise LimitExceededError(
                f"Text byte size ({text_bytes}) exceeds limit ({self.max_bytes})",
                provider=provider,
                model=model,
                limit_name="max_bytes",
                actual=text_bytes,
                allowed=self.max_bytes
            )
        
        if text_chars > self.max_chars:
            raise LimitExceededError(
                f"Text character count ({text_chars}) exceeds limit ({self.max_chars})",
                provider=provider,
                model=model,
                limit_name="max_chars",
                actual=text_chars,
                allowed=self.max_chars
            )
        
        if estimated_tokens > self.max_tokens:
            raise LimitExceededError(
                f"Estimated tokens ({estimated_tokens}) exceeds limit ({self.max_tokens})",
                provider=provider,
                model=model,
                limit_name="max_tokens",
                actual=estimated_tokens,
                allowed=self.max_tokens
            )
    
    def validate_images(
        self,
        image_count: int,
        image_bytes: int,
        provider: str,
        model: Optional[str] = None
    ) -> None:
        """Validate images against limits."""
        # If max_images is 0, no images are allowed
        if self.max_images == 0 and image_count > 0:
            raise ImageLimitError(
                f"Provider does not support images (max_images=0), but {image_count} image(s) provided",
                provider=provider,
                model=model,
                limit_name="max_images",
                actual=image_count,
                allowed=0
            )
        
        if self.max_images > 0 and image_count > self.max_images:
            raise ImageLimitError(
                f"Image count ({image_count}) exceeds limit ({self.max_images})",
                provider=provider,
                model=model,
                limit_name="max_images",
                actual=image_count,
                allowed=self.max_images
            )
        
        if self.image_byte_limit > 0 and image_bytes > self.image_byte_limit:
            raise ImageLimitError(
                f"Total image bytes ({image_bytes}) exceeds limit ({self.image_byte_limit})",
                provider=provider,
                model=model,
                limit_name="image_byte_limit",
                actual=image_bytes,
                allowed=self.image_byte_limit
            )

