"""Gemini OCR provider implementation using the new google-genai SDK."""

import logging
from typing import Optional

import httpx
from google import genai
from google.genai import types

from ..base import BaseOCRClient, OCRClientError
from ..config import Config, ConfigError
from ..prompts import PromptTemplate
from ..utils import get_mime_type

logger = logging.getLogger(__name__)


def _is_gemini3(model_name: str) -> bool:
    """Check if model is Gemini 3 series."""
    return model_name.startswith("gemini-3")


def _is_gemini3_flash(model_name: str) -> bool:
    """Check if model is Gemini 3 Flash (supports minimal/medium thinking)."""
    return "gemini-3-flash" in model_name


class GeminiOCRClient(BaseOCRClient):
    """OCR client using Google Gemini API (new google-genai SDK)."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Gemini OCR client.

        Args:
            config: Configuration instance. If None, uses default config.
        """
        from ..config import get_config
        config = config or get_config()

        # Check if using Gemini 3 BEFORE calling super().__init__
        self._is_gemini3 = _is_gemini3(config.gemini_model)
        self._is_gemini3_flash = _is_gemini3_flash(config.gemini_model)

        # Initialize base class with config (sets up prompts)
        super().__init__(config)

        try:
            self.config.ensure_credentials("gemini")
        except ConfigError as exc:
            raise OCRClientError(str(exc)) from exc

        # Gemini 3 specific settings
        self._thinking_level = self.config.gemini_thinking_level
        self._media_resolution = self.config.gemini_media_resolution

        # Build http_options
        http_options_kwargs = {}
        if self.config.gemini_base_url:
            http_options_kwargs["base_url"] = self.config.gemini_base_url

        # API version: auto means v1alpha for official API, v1beta for proxy
        api_version = self.config.gemini_api_version
        if api_version == "auto":
            if self.config.gemini_base_url:
                # Proxy: use v1beta (more compatible)
                api_version = "v1beta"
            elif self._is_gemini3:
                # Official API + Gemini 3: use v1alpha for full features
                api_version = "v1alpha"
            else:
                api_version = None  # Use SDK default

        if api_version and api_version != "auto":
            http_options_kwargs["api_version"] = api_version

        # Initialize genai Client
        client_kwargs = {"api_key": self.config.gemini_api_key}
        if http_options_kwargs:
            client_kwargs["http_options"] = types.HttpOptions(**http_options_kwargs)
        self.client = genai.Client(**client_kwargs)

        log_msg = f"Initialized Gemini OCR client with model: {self.config.gemini_model}"
        if self.config.gemini_base_url:
            log_msg += f", base_url: {self.config.gemini_base_url}"
        if api_version:
            log_msg += f", api_version: {api_version}"
        if self._is_gemini3:
            log_msg += f" (Gemini 3, thinking={self._thinking_level or 'default'}"
            if self._media_resolution:
                log_msg += f", resolution={self._media_resolution}"
            log_msg += ")"
        logger.info(log_msg)

    def _build_user_prompt(self) -> str:
        """Build user prompt, using Gemini 3 optimized version if applicable."""
        if self.config.user_prompt:
            return self.config.user_prompt
        return PromptTemplate.get_user_prompt(self.config.prompt_mode, gemini3=self._is_gemini3)

    def _build_system_prompt(self) -> Optional[str]:
        """Build system prompt, using Gemini 3 optimized version if applicable."""
        if self.config.system_prompt:
            return self.config.system_prompt
        return PromptTemplate.get_system_prompt(self.config.prompt_mode, gemini3=self._is_gemini3)

    def _build_generation_config(self) -> types.GenerateContentConfig:
        """Build generation config with Gemini 3 support."""
        config_kwargs = {}

        # Temperature: Gemini 3 recommends 1.0 (default)
        effective_temp = self.config.get_effective_temperature("gemini")
        config_kwargs["temperature"] = effective_temp

        # System instruction
        if self.system_prompt:
            config_kwargs["system_instruction"] = self.system_prompt

        # Gemini 3: thinking_config support
        # Values: "low", "high" for Pro; "minimal", "low", "medium", "high" for Flash
        if self._is_gemini3 and self._thinking_level:
            # Validate thinking level for model type
            valid_levels = ["low", "high"]
            if self._is_gemini3_flash:
                valid_levels = ["minimal", "low", "medium", "high"]

            if self._thinking_level in valid_levels:
                config_kwargs["thinking_config"] = types.ThinkingConfig(
                    thinking_level=self._thinking_level
                )
            else:
                logger.warning(
                    f"thinking_level '{self._thinking_level}' not supported for this model, ignoring"
                )

        # Gemini 3: media_resolution support (requires v1alpha API)
        # Tokens: low=280 (img)/70 (video), medium=560/70, high=1120/280
        if self._is_gemini3 and self._media_resolution:
            resolution_map = {
                "low": "media_resolution_low",
                "medium": "media_resolution_medium",
                "high": "media_resolution_high",
                # Note: ultra_high cannot be set globally, only per-part
            }
            if self._media_resolution in resolution_map:
                config_kwargs["media_resolution"] = resolution_map[self._media_resolution]
            elif self._media_resolution == "ultra_high":
                logger.warning("ultra_high resolution cannot be set globally, using high")
                config_kwargs["media_resolution"] = "media_resolution_high"

        return types.GenerateContentConfig(**config_kwargs)

    async def _call_api(self, image_bytes: bytes, mime_type: str):
        """Call Gemini API."""
        try:
            # Build content parts
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            text_part = types.Part.from_text(text=self.user_prompt)

            logger.info(f"Sending OCR request to Gemini API ({mime_type})")

            generation_config = self._build_generation_config()

            response = await self.client.aio.models.generate_content(
                model=self.config.gemini_model,
                contents=[text_part, image_part],
                config=generation_config
            )
            return response

        except Exception as e:
            if isinstance(e, OCRClientError):
                raise

            error_msg = str(e).lower()
            if "unauthenticated" in error_msg or "invalid api key" in error_msg:
                raise OCRClientError(
                    "Invalid Gemini API key. Please check your GEMINI_API_KEY.\n"
                    "Get your API key from https://ai.google.dev/"
                ) from e
            if "permission denied" in error_msg:
                raise OCRClientError("Gemini API access denied. Please check your account permissions.") from e
            if "rate limit" in error_msg or "resource exhausted" in error_msg:
                raise OCRClientError("Gemini API rate limit exceeded. Please wait a moment and try again.") from e

            logger.error("Gemini API error: %s", e)
            raise OCRClientError(f"Failed to process image with Gemini API: {str(e)}") from e

    def _extract_response_text(self, response) -> str:
        """Extract text from Gemini response."""
        if not response.text:
            logger.warning("Gemini API returned empty response")
            raise OCRClientError("Gemini API returned empty response. The image may not contain any text.")

        return response.text

    async def extract_text_from_url(self, image_url: str) -> str:
        """Download an image from a URL and run OCR with Gemini."""
        logger.info("Downloading image for OCR from URL: %s", image_url)

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as http_client:
                response = await http_client.get(image_url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Failed to download image from URL %s: %s", image_url, exc)
            raise OCRClientError(f"Failed to download image from URL: {exc}") from exc

        if not response.content:
            logger.error("No content returned for URL %s", image_url)
            raise OCRClientError("Downloaded image is empty.")

        mime_type = response.headers.get("content-type", "").split(";", 1)[0].strip()

        if not mime_type.startswith("image/"):
            try:
                mime_type = get_mime_type(response.content)
            except ValueError as exc:
                logger.error("Unable to determine MIME type for URL %s: %s", image_url, exc)
                raise OCRClientError("Failed to determine image MIME type from URL response.") from exc

        return await self.extract_text(response.content, mime_type)

    @property
    def provider_name(self) -> str:
        """Return the name of the OCR provider."""
        return "Gemini"

    @property
    def model_name(self) -> str:
        """Return the model name being used."""
        return self.config.gemini_model
