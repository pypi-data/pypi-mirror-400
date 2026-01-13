"""Utility functions for image processing and validation."""

import base64
import os
from io import BytesIO
from typing import Literal, Tuple
from PIL import Image


def read_image_file(file_path: str) -> Tuple[bytes, str]:
    """
    Read an image file and return its bytes and MIME type.

    Args:
        file_path: Path to the image file

    Returns:
        A tuple of (image_bytes, mime_type)

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
        ValueError: If the file is not a valid image
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    # Check if file is readable
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Permission denied reading file: {file_path}")

    try:
        # Read the file
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # Determine MIME type using Pillow
        mime_type = get_mime_type(image_bytes)

        return image_bytes, mime_type

    except Exception as e:
        if isinstance(e, (FileNotFoundError, PermissionError, ValueError)):
            raise
        raise ValueError(f"Failed to read image file: {str(e)}")


def decode_base64_image(base64_string: str) -> Tuple[bytes, str]:
    """
    Decode a Base64 encoded image string and return its bytes and MIME type.

    Args:
        base64_string: Base64 encoded image string

    Returns:
        A tuple of (image_bytes, mime_type)

    Raises:
        ValueError: If the Base64 string is malformed or not a valid image
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if "," in base64_string and base64_string.startswith("data:"):
            base64_string = base64_string.split(",", 1)[1]

        # Decode Base64 string
        image_bytes = base64.b64decode(base64_string, validate=True)

        # Determine MIME type
        mime_type = get_mime_type(image_bytes)

        return image_bytes, mime_type

    except base64.binascii.Error as e:
        raise ValueError(f"Invalid Base64 encoding: {str(e)}")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to decode Base64 image: {str(e)}")


def get_mime_type(image_bytes: bytes) -> str:
    """
    Determine the MIME type of image data using Pillow.

    Args:
        image_bytes: The image data as bytes

    Returns:
        The MIME type string (e.g., 'image/png', 'image/jpeg')

    Raises:
        ValueError: If the data is not a valid image
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        format_lower = image.format.lower() if image.format else None

        # Map PIL formats to MIME types
        mime_type_map = {
            "png": "image/png",
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif",
            "bmp": "image/bmp",
            "tiff": "image/tiff",
            "mpo": "image/jpeg",  # Multi-Picture Object (3D images, treat as JPEG)
        }

        mime_type = mime_type_map.get(format_lower)
        if not mime_type:
            raise ValueError(f"Unsupported image format: {image.format}")

        return mime_type

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Invalid image data: {str(e)}")


def detect_image_input_type(image_input: str) -> Literal["file_path", "url", "base64"]:
    """Classify image input as file path, URL, or Base64 string."""
    stripped_input = image_input.strip()

    if not stripped_input:
        raise ValueError("Image input is empty.")

    if stripped_input.startswith(("http://", "https://")):
        return "url"

    if os.path.isfile(stripped_input):
        return "file_path"

    if stripped_input.startswith("data:"):
        return "base64"

    try:
        base64.b64decode(stripped_input, validate=True)
        return "base64"
    except (base64.binascii.Error, ValueError) as exc:
        raise ValueError("Unable to determine image input type.") from exc
