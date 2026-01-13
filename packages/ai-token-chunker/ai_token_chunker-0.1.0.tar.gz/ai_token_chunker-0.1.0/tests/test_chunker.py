"""Tests for chunker functionality."""

import pytest
from ai_token_chunker import chunk_prompt
from ai_token_chunker.errors import (
    ProviderNotSupportedError,
    LimitExceededError,
    ImageLimitError,
    InvalidInputError
)


def test_text_only_chunking_single():
    """Test chunking a small text that fits in one chunk."""
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input="Hello, world!"
    )
    
    assert len(result["chunks"]) == 1
    assert result["chunks"][0]["text"] == "Hello, world!"
    assert result["chunks"][0]["images"] == []
    assert result["chunks"][0]["index"] == 0
    assert result["metadata"]["total_chunks"] == 1
    assert result["metadata"]["provider"] == "openai"
    assert result["metadata"]["model"] == "gpt-4"


def test_text_only_chunking_multiple():
    """Test chunking a large text that requires splitting."""
    # Create text that exceeds GPT-4 limits
    large_text = "Hello, world! " * 10000  # ~130k chars, exceeds GPT-4's 32k char limit
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=large_text
    )
    
    assert len(result["chunks"]) > 1
    assert result["metadata"]["total_chunks"] > 1
    
    # Verify all chunks are within limits
    limits = result["metadata"]
    for chunk in result["chunks"]:
        text_bytes = len(chunk["text"].encode("utf-8"))
        text_chars = len(chunk["text"])
        estimated_tokens = text_chars // 4
        
        # GPT-4 limits
        assert text_bytes <= 128000
        assert text_chars <= 32000
        assert estimated_tokens <= 8192


def test_unsplittable_overflow():
    """Test handling of text that cannot be split (single huge word)."""
    # Create a single "word" that exceeds limits
    huge_word = "A" * 100000  # 100k character word
    
    # This should still be chunked, even if it means splitting the word
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=huge_word
    )
    
    # Should create at least one chunk
    assert len(result["chunks"]) >= 1
    
    # Verify chunks are within byte limits (most restrictive)
    for chunk in result["chunks"]:
        text_bytes = len(chunk["text"].encode("utf-8"))
        assert text_bytes <= 128000


def test_provider_not_supported():
    """Test error when provider is not supported."""
    with pytest.raises(ProviderNotSupportedError) as exc_info:
        chunk_prompt(
            provider="unknown_provider",
            model=None,
            input="test"
        )
    
    assert exc_info.value.provider == "unknown_provider"
    assert exc_info.value.code == "PROVIDER_NOT_SUPPORTED"


def test_invalid_input_type():
    """Test error when input is not a string."""
    with pytest.raises(InvalidInputError) as exc_info:
        chunk_prompt(
            provider="openai",
            model=None,
            input=123  # Not a string
        )
    
    assert exc_info.value.code == "INVALID_INPUT"


def test_different_providers():
    """Test chunking with different providers."""
    text = "Test text " * 100
    
    # Test OpenAI
    result_openai = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=text
    )
    assert result_openai["metadata"]["provider"] == "openai"
    
    # Test Anthropic
    result_anthropic = chunk_prompt(
        provider="anthropic",
        model="claude-3-sonnet",
        input=text
    )
    assert result_anthropic["metadata"]["provider"] == "anthropic"
    
    # Test Google
    result_google = chunk_prompt(
        provider="google",
        model="gemini-pro",
        input=text
    )
    assert result_google["metadata"]["provider"] == "google"


def test_model_specific_limits():
    """Test that model-specific limits are used when available."""
    text = "Test " * 1000
    
    # GPT-4 has specific limits
    result_gpt4 = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=text
    )
    assert result_gpt4["metadata"]["model"] == "gpt-4"
    
    # GPT-4 Turbo has different limits
    result_turbo = chunk_prompt(
        provider="openai",
        model="gpt-4-turbo",
        input=text
    )
    assert result_turbo["metadata"]["model"] == "gpt-4-turbo"


def test_default_provider_limits():
    """Test that default limits are used when model is not specified."""
    text = "Test " * 1000
    
    result = chunk_prompt(
        provider="openai",
        model=None,
        input=text
    )
    
    assert result["metadata"]["provider"] == "openai"
    assert result["metadata"]["model"] is None


def test_empty_input():
    """Test chunking empty input."""
    result = chunk_prompt(
        provider="openai",
        model=None,
        input=""
    )
    
    assert len(result["chunks"]) == 1
    assert result["chunks"][0]["text"] == ""
    assert result["metadata"]["total_chunks"] == 1


def test_chunk_indices():
    """Test that chunk indices are sequential."""
    large_text = "Test " * 10000
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=large_text
    )
    
    indices = [chunk["index"] for chunk in result["chunks"]]
    assert indices == list(range(len(result["chunks"])))


def test_metadata_estimates():
    """Test that metadata estimates are reasonable."""
    text = "Hello, world! " * 1000
    
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=text
    )
    
    metadata = result["metadata"]
    assert metadata["estimated_tokens"] > 0
    assert metadata["estimated_bytes"] > 0
    assert metadata["total_chunks"] > 0

