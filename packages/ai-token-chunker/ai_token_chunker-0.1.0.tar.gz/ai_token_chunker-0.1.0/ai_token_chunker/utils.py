"""Utility functions for token and size estimation."""

from typing import List, Dict


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using heuristic: 1 token ≈ 4 characters.
    
    This is a rough heuristic, not an exact tokenizer.
    """
    return len(text) // 4


def get_text_bytes(text: str) -> int:
    """Get UTF-8 byte size of text."""
    return len(text.encode("utf-8"))


def get_image_bytes(images: List[Dict]) -> int:
    """Get total byte size of images."""
    return sum(len(img.get("data", b"")) for img in images)


def split_text_safely(
    text: str,
    max_bytes: int,
    max_chars: int,
    max_tokens: int
) -> List[str]:
    """
    Split text into chunks that respect all limits.
    
    Attempts to split at word boundaries when possible.
    Falls back to character-level splitting if needed.
    """
    chunks = []
    remaining = text
    
    while remaining:
        # Start with the full remaining text
        chunk = remaining
        
        # Check if we need to split
        chunk_bytes = get_text_bytes(chunk)
        chunk_chars = len(chunk)
        chunk_tokens = estimate_tokens(chunk)
        
        if chunk_bytes <= max_bytes and chunk_chars <= max_chars and chunk_tokens <= max_tokens:
            # Chunk fits, we're done
            chunks.append(chunk)
            break
        
        # Need to split - try to find a good split point
        # Start from a safe position (leave room for limits)
        target_bytes = max_bytes
        target_chars = max_chars
        target_tokens = max_tokens
        
        # Binary search for split point
        low = 0
        high = len(remaining)
        split_point = high // 2
        
        while low < high:
            candidate = remaining[:split_point]
            cand_bytes = get_text_bytes(candidate)
            cand_chars = len(candidate)
            cand_tokens = estimate_tokens(candidate)
            
            if cand_bytes <= target_bytes and cand_chars <= target_chars and cand_tokens <= target_tokens:
                # Can go further
                low = split_point + 1
            else:
                # Too big, need to go back
                high = split_point
            
            split_point = (low + high) // 2
        
        # Try to split at word boundary near split_point
        actual_split = split_point
        
        # Look for word boundary (space, newline) within reasonable distance
        search_start = max(0, split_point - 100)
        search_end = min(len(remaining), split_point + 100)
        
        # Prefer splitting at newlines
        newline_pos = remaining.rfind("\n", search_start, search_end)
        if newline_pos > search_start:
            actual_split = newline_pos + 1
        else:
            # Try splitting at space
            space_pos = remaining.rfind(" ", search_start, search_end)
            if space_pos > search_start:
                actual_split = space_pos + 1
        
        # Ensure we don't create empty chunks
        if actual_split == 0:
            actual_split = split_point
        
        # Extract chunk
        chunk = remaining[:actual_split]
        remaining = remaining[actual_split:]
        
        # Final validation
        chunk_bytes = get_text_bytes(chunk)
        chunk_chars = len(chunk)
        chunk_tokens = estimate_tokens(chunk)
        
        if chunk_bytes > max_bytes or chunk_chars > max_chars or chunk_tokens > max_tokens:
            # Still too big, force character-level split
            # This should be rare
            force_split = min(
                len(chunk),
                max_bytes // 4,  # Conservative byte-based split
                max_chars,
                max_tokens * 4
            )
            if force_split == 0:
                force_split = 1  # At least one character
            
            chunk = remaining[:force_split]
            remaining = remaining[force_split:]
        
        chunks.append(chunk)
    
    return chunks

