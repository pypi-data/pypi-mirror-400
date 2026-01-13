"""Image handling utilities."""

import base64
from typing import Union, List, Dict, Optional, Tuple
from .errors import InvalidInputError, ImageLimitError


def normalize_image(image: Union[bytes, str, Dict]) -> Tuple[bytes, str]:
    """
    Normalize image input to (bytes, mime_type).
    
    Accepts:
    - bytes: raw image bytes
    - str: base64 encoded string or data URL
    - dict: {"data": bytes | str, "mime": str}
    
    Returns:
    - (bytes, mime_type)
    """
    if isinstance(image, bytes):
        # Try to infer mime type from magic bytes
        mime = _infer_mime_type(image)
        return image, mime
    
    if isinstance(image, str):
        # Handle base64 data URL or plain base64 string
        if image.startswith("data:"):
            # data:image/png;base64,<data>
            parts = image.split(",", 1)
            if len(parts) != 2:
                raise InvalidInputError(f"Invalid data URL format: {image}")
            
            mime_part = parts[0]
            data_part = parts[1]
            
            # Extract mime type
            if ";" in mime_part:
                mime = mime_part.split(";")[0].replace("data:", "")
            else:
                mime = mime_part.replace("data:", "")
            
            try:
                image_bytes = base64.b64decode(data_part)
            except Exception as e:
                raise InvalidInputError(f"Failed to decode base64 data: {e}")
            
            return image_bytes, mime
        else:
            # Plain base64 string
            try:
                image_bytes = base64.b64decode(image)
                mime = _infer_mime_type(image_bytes)
                return image_bytes, mime
            except Exception as e:
                raise InvalidInputError(f"Failed to decode base64 string: {e}")
    
    if isinstance(image, dict):
        if "data" not in image:
            raise InvalidInputError("Image dict must contain 'data' key")
        
        data = image["data"]
        mime = image.get("mime", "application/octet-stream")
        
        if isinstance(data, bytes):
            return data, mime
        elif isinstance(data, str):
            # Decode base64 string
            if data.startswith("data:"):
                # Extract base64 part from data URL
                parts = data.split(",", 1)
                if len(parts) != 2:
                    raise InvalidInputError(f"Invalid data URL format: {data}")
                data = parts[1]
            
            try:
                image_bytes = base64.b64decode(data)
                return image_bytes, mime
            except Exception as e:
                raise InvalidInputError(f"Failed to decode base64 data: {e}")
        else:
            raise InvalidInputError(f"Image data must be bytes or str, got {type(data)}")
    
    raise InvalidInputError(f"Unsupported image type: {type(image)}")


def _infer_mime_type(data: bytes) -> str:
    """Infer MIME type from image magic bytes."""
    if len(data) < 4:
        return "application/octet-stream"
    
    # PNG
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    
    # JPEG
    if data[:2] == b'\xff\xd8':
        return "image/jpeg"
    
    # GIF
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    
    # WebP
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "image/webp"
    
    # Default
    return "application/octet-stream"


def process_images(
    images: Optional[List[Union[bytes, str, Dict]]],
    provider: str,
    model: Optional[str] = None
) -> List[Dict[str, Union[bytes, str]]]:
    """
    Process and normalize a list of images.
    
    Returns:
    - List of {"data": bytes, "mime": str}
    """
    if images is None:
        return []
    
    if not isinstance(images, list):
        raise InvalidInputError(f"Images must be a list, got {type(images)}")
    
    processed = []
    total_bytes = 0
    
    for idx, image in enumerate(images):
        try:
            image_bytes, mime = normalize_image(image)
            image_size = len(image_bytes)
            total_bytes += image_size
            
            processed.append({
                "data": image_bytes,
                "mime": mime
            })
        except InvalidInputError:
            raise
        except Exception as e:
            raise InvalidInputError(
                f"Failed to process image at index {idx}: {e}",
                provider=provider,
                model=model
            )
    
    return processed

