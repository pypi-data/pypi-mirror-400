"""Tests for image handling."""

import base64
import pytest
from ai_token_chunker import chunk_prompt
from ai_token_chunker.errors import ImageLimitError, InvalidInputError


def create_test_image_bytes() -> bytes:
    """Create a minimal valid PNG image."""
    # Minimal 1x1 PNG
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )


def test_image_bytes():
    """Test chunking with image as bytes."""
    image_bytes = create_test_image_bytes()
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[image_bytes]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 1
    assert result["chunks"][0]["images"][0]["data"] == image_bytes
    assert result["chunks"][0]["images"][0]["mime"] == "image/png"


def test_image_base64_string():
    """Test chunking with image as base64 string."""
    image_bytes = create_test_image_bytes()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[base64_str]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 1
    assert result["chunks"][0]["images"][0]["data"] == image_bytes


def test_image_data_url():
    """Test chunking with image as data URL."""
    image_bytes = create_test_image_bytes()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{base64_str}"
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[data_url]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 1
    assert result["chunks"][0]["images"][0]["data"] == image_bytes
    assert result["chunks"][0]["images"][0]["mime"] == "image/png"


def test_image_dict():
    """Test chunking with image as dict."""
    image_bytes = create_test_image_bytes()
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[{"data": image_bytes, "mime": "image/png"}]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 1
    assert result["chunks"][0]["images"][0]["data"] == image_bytes
    assert result["chunks"][0]["images"][0]["mime"] == "image/png"


def test_image_dict_base64():
    """Test chunking with image dict containing base64 string."""
    image_bytes = create_test_image_bytes()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[{"data": base64_str, "mime": "image/png"}]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 1
    assert result["chunks"][0]["images"][0]["data"] == image_bytes


def test_multiple_images():
    """Test chunking with multiple images."""
    image_bytes = create_test_image_bytes()
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[image_bytes, image_bytes, image_bytes]
    )
    
    assert len(result["chunks"]) == 1
    assert len(result["chunks"][0]["images"]) == 3


def test_image_count_overflow():
    """Test error when image count exceeds limit."""
    image_bytes = create_test_image_bytes()
    
    # OpenAI GPT-4 allows max 10 images
    # Create 11 images
    images = [image_bytes] * 11
    
    with pytest.raises(ImageLimitError) as exc_info:
        chunk_prompt(
            provider="openai",
            model="gpt-4",
            input="Test text",
            images=images
        )
    
    assert exc_info.value.code == "IMAGE_LIMIT_ERROR"
    assert exc_info.value.limit_name == "max_images"
    assert exc_info.value.actual == 11
    assert exc_info.value.allowed == 10


def test_image_byte_limit_overflow():
    """Test error when total image bytes exceed limit."""
    # Create a large image (exceeds OpenAI's 20MB limit)
    large_image = b"x" * 21000000  # 21MB
    
    with pytest.raises(ImageLimitError) as exc_info:
        chunk_prompt(
            provider="openai",
            model="gpt-4",
            input="Test text",
            images=[large_image]
        )
    
    assert exc_info.value.code == "IMAGE_LIMIT_ERROR"
    assert exc_info.value.limit_name == "image_byte_limit"


def test_invalid_image_type():
    """Test error when image type is invalid."""
    with pytest.raises(InvalidInputError) as exc_info:
        chunk_prompt(
            provider="openai",
            model="gpt-4",
            input="Test text",
            images=[123]  # Invalid type
        )
    
    assert exc_info.value.code == "INVALID_INPUT"


def test_invalid_image_dict():
    """Test error when image dict is invalid."""
    with pytest.raises(InvalidInputError) as exc_info:
        chunk_prompt(
            provider="openai",
            model="gpt-4",
            input="Test text",
            images=[{"invalid": "dict"}]
        )
    
    assert exc_info.value.code == "INVALID_INPUT"


def test_invalid_base64():
    """Test error when base64 string is invalid."""
    with pytest.raises(InvalidInputError) as exc_info:
        chunk_prompt(
            provider="openai",
            model="gpt-4",
            input="Test text",
            images=["invalid_base64!!!"]
        )
    
    assert exc_info.value.code == "INVALID_INPUT"


def test_images_with_text_chunking():
    """Test that images are only attached to first chunk when text is split."""
    image_bytes = create_test_image_bytes()
    large_text = "Test " * 20000  # Large text that will definitely be split (exceeds GPT-4's 32k char limit)
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=large_text,
        images=[image_bytes]
    )
    
    # Should have multiple chunks
    assert len(result["chunks"]) > 1
    
    # First chunk should have images
    assert len(result["chunks"][0]["images"]) == 1
    
    # Other chunks should not have images
    for chunk in result["chunks"][1:]:
        assert len(chunk["images"]) == 0


def test_no_images():
    """Test chunking with None images."""
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=None
    )
    
    assert len(result["chunks"]) == 1
    assert result["chunks"][0]["images"] == []


def test_empty_images_list():
    """Test chunking with empty images list."""
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Test text",
        images=[]
    )
    
    assert len(result["chunks"]) == 1
    assert result["chunks"][0]["images"] == []


def test_provider_without_image_support():
    """Test that providers without image support still work."""
    image_bytes = create_test_image_bytes()
    
    # Mistral doesn't support images
    with pytest.raises(ImageLimitError):
        chunk_prompt(
            provider="mistral",
            model=None,
            input="Test text",
            images=[image_bytes]
        )

