"""OpenAI OCR provider implementation."""

import logging
import base64
from typing import Optional
from openai import AsyncOpenAI, APIError, APIStatusError, AuthenticationError, RateLimitError

from ..base import BaseOCRClient, OCRClientError
from ..config import Config, ConfigError

logger = logging.getLogger(__name__)


OPENAI_ERROR_MAP = {
    401: "Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable.\nGet your API key from https://platform.openai.com/api-keys",
    403: "OpenAI API access forbidden. Please check your account permissions.",
    429: "OpenAI API rate limit exceeded. Please wait a moment and try again.",
    500: "OpenAI API server error. Please try again later.",
    503: "OpenAI API service unavailable. Please try again later.",
}


class OpenAIOCRClient(BaseOCRClient):
    """OCR client using OpenAI Vision API."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize OpenAI OCR client.

        Args:
            config: Configuration instance. If None, uses default config.
        """
        from ..config import get_config
        config = config or get_config()

        # Initialize base class with config (sets up prompts & temperature)
        super().__init__(config)

        try:
            self.config.ensure_credentials("openai")
        except ConfigError as exc:
            raise OCRClientError(str(exc)) from exc

        # Initialize OpenAI client (using openai_base_url)
        base_url = self.config.openai_base_url
        self.client = AsyncOpenAI(
            api_key=self.config.openai_api_key,
            base_url=base_url
        )

        logger.info(f"Initialized OpenAI OCR client with model: {self.config.openai_model}, base_url: {base_url}")

    def _build_messages(self, image_url: str):
        """Build OpenAI chat messages for OCR request."""
        messages = []

        if self.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        )

        return messages

    async def _create_chat_completion(self, image_url: str):
        """Create a chat completion for the given image URL."""
        messages = self._build_messages(image_url)
        temperature = self.config.get_effective_temperature("openai")
        return await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            temperature=temperature,
        )

    def _handle_api_error(self, e: Exception) -> None:
        """Handle OpenAI API errors uniformly."""
        if isinstance(e, AuthenticationError):
            status_code = getattr(e, "status_code", 401) or 401
            logger.error("OpenAI authentication error (status=%s): %s", status_code, e)
            raise OCRClientError(OPENAI_ERROR_MAP.get(status_code, OPENAI_ERROR_MAP[401])) from e
        if isinstance(e, RateLimitError):
            status_code = getattr(e, "status_code", 429) or 429
            logger.error("OpenAI rate limit error (status=%s): %s", status_code, e)
            raise OCRClientError(OPENAI_ERROR_MAP.get(status_code, OPENAI_ERROR_MAP[429])) from e
        if isinstance(e, (APIStatusError, APIError)):
            status_code = getattr(e, "status_code", None)
            error_code = getattr(e, "code", None)
            logger.error("OpenAI API error (status=%s, code=%s): %s", status_code or "unknown", error_code, e)
            if error_code == "insufficient_quota":
                raise OCRClientError("OpenAI API quota exceeded. Please check your billing details.") from e
            if status_code in OPENAI_ERROR_MAP:
                raise OCRClientError(OPENAI_ERROR_MAP[status_code]) from e
            raise OCRClientError(f"Failed to process image with OpenAI API (status {status_code or 'unknown'}).") from e
        if isinstance(e, OCRClientError):
            raise
        logger.error("Unexpected OpenAI API error: %s", e)
        raise OCRClientError(f"Failed to process image with OpenAI API: {str(e)}") from e

    async def _call_api(self, image_bytes: bytes, mime_type: str):
        """Call OpenAI Vision API."""
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:{mime_type};base64,{base64_image}"

            logger.info(f"Sending OCR request to OpenAI API ({mime_type})")

            return await self._create_chat_completion(image_url)
        except Exception as e:
            self._handle_api_error(e)

    def _extract_response_text(self, response) -> str:
        """Extract text from OpenAI response."""
        # Handle string response (some proxies return plain text)
        if isinstance(response, str):
            if not response.strip():
                logger.warning("OpenAI API returned empty response")
                raise OCRClientError("OpenAI API returned empty response. The image may not contain any text.")
            return response

        # Handle dict response (some proxies return dict instead of object)
        if isinstance(response, dict):
            choices = response.get("choices", [])
            if choices and choices[0].get("message", {}).get("content"):
                return choices[0]["message"]["content"]
            logger.warning("OpenAI API returned empty response (dict)")
            raise OCRClientError("OpenAI API returned empty response. The image may not contain any text.")

        # Standard OpenAI response object
        if not response.choices or not response.choices[0].message.content:
            logger.warning("OpenAI API returned empty response")
            raise OCRClientError("OpenAI API returned empty response. The image may not contain any text.")

        return response.choices[0].message.content

    async def extract_text_from_url(self, image_url: str) -> str:
        """Extract text from image URL using OpenAI's native URL support."""
        logger.info("Sending OCR request to OpenAI API with URL: %s", image_url)

        try:
            response = await self._create_chat_completion(image_url)

            text = self._extract_response_text(response)
            logger.info(f"OCR completed: {len(text)} characters extracted")
            return text.strip()
        except Exception as e:
            self._handle_api_error(e)

    @property
    def provider_name(self) -> str:
        """Return the name of the OCR provider."""
        return "OpenAI"

    @property
    def model_name(self) -> str:
        """Return the model name being used."""
        return self.config.openai_model
