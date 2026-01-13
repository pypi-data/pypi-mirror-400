# ai_token_chunker

**Defensive preflight layer for LLM API calls**

A production-grade Python utility library that prevents token/context length overflow, byte size violations, image payload limits, and provider-specific constraint violations before making LLM API calls.

## Why This Exists

Python AI backends (FastAPI, Celery, batch jobs) regularly fail due to:

- Token/context length overflow
- Byte size violations
- Image payload limits
- Provider-specific constraints
- Silent truncation across LLM APIs

This library acts as a **defensive preflight layer** that validates and chunks your prompts before sending them to LLM APIs, ensuring your requests will be accepted.

## Comparison with Tokenizers

**This is NOT a tokenizer.**

- **Tokenizers** (like `tiktoken`, `transformers`) count exact tokens using model-specific vocabularies
- **This library** uses heuristics (1 token ≈ 4 characters) and enforces byte/character limits
- **Why heuristics?** Zero external dependencies, works offline, deterministic behavior
- **When to use this:** Preflight validation and chunking before API calls
- **When to use tokenizers:** When you need exact token counts for billing or precise limits

## Design Goals

- ✅ Zero external runtime dependencies
- ✅ Python 3.9+
- ✅ Deterministic behavior
- ✅ No network calls
- ✅ No tokenizers (heuristics only)
- ✅ Backend-safe (FastAPI, workers, batch jobs)
- ✅ Fail fast with descriptive errors

## Installation

```bash
pip install ai_token_chunker
```

## Quick Start

```python
from ai_token_chunker import chunk_prompt

# Simple text chunking
result = chunk_prompt(
    provider="openai",
    model="gpt-4",
    input="Your long text here..."
)

print(f"Created {result['metadata']['total_chunks']} chunks")
for chunk in result['chunks']:
    print(f"Chunk {chunk['index']}: {len(chunk['text'])} chars")
```

## Usage Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from ai_token_chunker import chunk_prompt, LimitExceededError

app = FastAPI()

@app.post("/chat")
async def chat(provider: str, model: str, prompt: str):
    try:
        result = chunk_prompt(
            provider=provider,
            model=model,
            input=prompt
        )
        # Process chunks...
        return {"chunks": len(result["chunks"])}
    except LimitExceededError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Limit exceeded: {e.limit_name}"
        )
```

### With Images

```python
import base64

# Load image
with open("image.png", "rb") as f:
    image_bytes = f.read()

result = chunk_prompt(
    provider="openai",
    model="gpt-4",
    input="Describe this image",
    images=[image_bytes]
)

# Or use base64
image_b64 = base64.b64encode(image_bytes).decode()
result = chunk_prompt(
    provider="openai",
    model="gpt-4",
    input="Describe this image",
    images=[f"data:image/png;base64,{image_b64}"]
)
```

### Error Handling

```python
from ai_token_chunker import (
    chunk_prompt,
    ProviderNotSupportedError,
    LimitExceededError,
    ImageLimitError,
    InvalidInputError
)

try:
    result = chunk_prompt(
        provider="openai",
        model="gpt-4",
        input=text,
        images=images
    )
except ProviderNotSupportedError as e:
    print(f"Provider not supported: {e.provider}")
except LimitExceededError as e:
    print(f"Limit exceeded: {e.limit_name}")
    print(f"Actual: {e.actual}, Allowed: {e.allowed}")
except ImageLimitError as e:
    print(f"Image limit exceeded: {e.limit_name}")
except InvalidInputError as e:
    print(f"Invalid input: {e}")
```

## API Reference

### `chunk_prompt()`

```python
def chunk_prompt(
    provider: str,
    model: str | None,
    input: str,
    images: list | None = None,
    options: dict | None = None
) -> dict
```

**Parameters:**

- `provider` (str): Provider name (e.g., "openai", "anthropic", "google")
- `model` (str | None): Optional model name (e.g., "gpt-4", "claude-3-sonnet")
- `input` (str): Input text to chunk
- `images` (list | None): Optional list of images (bytes, base64 str, or dict)
- `options` (dict | None): Optional additional options (reserved for future use)

**Returns:**

```python
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
```

## Supported Providers

| Provider | Default Model | Max Tokens | Max Images |
|----------|--------------|------------|------------|
| OpenAI | GPT-4 Turbo | 128,000 | 10 |
| Anthropic | Claude 3.5 Sonnet | 200,000 | 20 |
| Google | Gemini Pro | 32,000 | 16 |
| Mistral | Mistral Large | 32,000 | 0 |
| Cohere | Default | 4,096 | 0 |
| Groq | Mixtral | 32,768 | 0 |
| Azure OpenAI | GPT-4 Turbo | 128,000 | 10 |
| AWS Bedrock | Claude | 200,000 | 20 |
| Together AI | Default | 32,000 | 0 |
| Ollama | Default | 32,768 | 0 |

*Limits are heuristics and may vary by model and region. Always check provider documentation for exact limits.*

## Image Formats

Images can be provided in multiple formats:

```python
# Bytes
images = [image_bytes]

# Base64 string
images = [base64_string]

# Base64 data URL
images = ["data:image/png;base64,<data>"]

# Dict format
images = [{"data": image_bytes, "mime": "image/png"}]
images = [{"data": base64_string, "mime": "image/jpeg"}]
```

## Token & Size Estimation

- **1 token ≈ 4 characters** (heuristic)
- Byte size is always enforced before token heuristics
- Uses `len(text.encode("utf-8"))` for byte size
- Images are counted separately

## Error Codes

All exceptions have a `.code` property for machine handling:

- `PROVIDER_NOT_SUPPORTED`: Provider is not in the supported list
- `LIMIT_EXCEEDED`: Text limits (tokens, chars, bytes) exceeded
- `IMAGE_LIMIT_ERROR`: Image count or size limits exceeded
- `INVALID_INPUT`: Input format is invalid

## Philosophy

- **Predictable > clever**: Simple heuristics over complex algorithms
- **Explicit limits > magic**: Clear provider limits, no hidden behavior
- **Defensive programming**: Fail fast with descriptive errors
- **Production-first**: Suitable for async and sync backends

## Limitations

⚠️ **This is a safety layer, not a tokenizer.**

- Token counts are estimates (heuristic: 1 token ≈ 4 chars)
- Actual token counts may vary by model and provider
- Always validate against provider documentation for exact limits
- This library prevents obvious violations, not edge cases

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

This is a minimal, focused library. Contributions should maintain:

- Zero external dependencies
- Deterministic behavior
- Production-grade error handling
- Clear, explicit limits

