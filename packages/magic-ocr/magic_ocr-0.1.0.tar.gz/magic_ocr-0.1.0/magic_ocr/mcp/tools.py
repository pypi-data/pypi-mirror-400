"""MCP OCR tools."""

import copy
import logging
from typing import Optional

from ..utils import read_image_file, decode_base64_image, detect_image_input_type
from ..config import get_config
from ..prompts import PromptMode
from .. import get_ocr_client

logger = logging.getLogger(__name__)


async def ocr_image(
    image: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    mode: Optional[str] = None,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
) -> str:
    """Extract text from image (file/URL/base64).

    Args:
        image: Absolute file path (e.g., /Users/name/image.png), URL (https://...),
            or base64 string. Prefer absolute path or URL over base64.
            Do NOT use relative paths.
        provider: OCR provider ('gemini', 'openai', 'gcp')
        model: Model name (e.g., 'gemini-3-flash-preview', 'gpt-4o')
        mode: Output mode ('plain' or 'markdown')
        system_prompt: Custom system prompt
        user_prompt: Custom user prompt

    Note:
        All optional parameters have optimized defaults.
        Only override when user explicitly requests a specific value.
    """
    logger.info("OCR request")

    try:
        # Detect input type
        input_type = detect_image_input_type(image)
        logger.info(f"Detected input type: {input_type}")

        # Load config and create a copy to avoid modifying global state
        config = copy.copy(get_config())

        # mode: map to PromptMode, default 'plain'
        if mode is not None:
            m = mode.strip().lower()
            if m in ("plain", "plaintext"):
                config.prompt_mode = PromptMode.PLAINTEXT
            elif m == "markdown":
                config.prompt_mode = PromptMode.MARKDOWN
            else:
                logger.warning(f"Invalid mode: {mode}, using default 'plain'")
                config.prompt_mode = PromptMode.PLAINTEXT

        # optional prompt overrides
        if system_prompt is not None:
            config.system_prompt = system_prompt
        if user_prompt is not None:
            config.user_prompt = user_prompt

        client = get_ocr_client(provider=provider, config=config, model=model)
        logger.info(f"Using {client.provider_name} OCR with model: {client.model_name}")

        # Route to appropriate handler
        if input_type == "url":
            text = await client.extract_text_from_url(image)
        elif input_type == "file_path":
            image_bytes, mime_type = read_image_file(image)
            text = await client.extract_text(image_bytes, mime_type)
        else:  # base64
            image_bytes, mime_type = decode_base64_image(image)
            text = await client.extract_text(image_bytes, mime_type)

        logger.info(f"OCR completed: {len(text)} characters extracted")
        return text

    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise
