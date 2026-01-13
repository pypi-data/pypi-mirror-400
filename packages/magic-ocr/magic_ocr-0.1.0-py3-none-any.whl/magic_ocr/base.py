"""Base OCR client interface."""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from .config import Config
from .prompts import PromptTemplate


class OCRClientError(Exception):
    """Base exception for OCR client errors."""
    pass


logger = logging.getLogger(__name__)


class BaseOCRClient(ABC):
    """Abstract base class for OCR client implementations."""

    def __init__(self, config: Config):
        """Initialize OCR client with configuration.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.user_prompt = self._build_user_prompt()
        self.system_prompt = self._build_system_prompt()

    def _build_user_prompt(self) -> str:
        """Build user prompt based on configuration."""
        if self.config.user_prompt:
            return self.config.user_prompt
        return PromptTemplate.get_user_prompt(self.config.prompt_mode)

    def _build_system_prompt(self) -> Optional[str]:
        """Build system prompt based on configuration."""
        if self.config.system_prompt:
            return self.config.system_prompt
        return PromptTemplate.get_system_prompt(self.config.prompt_mode)

    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str:
        """Extract text from image using template method pattern.

        Args:
            image_bytes: Image data as bytes
            mime_type: MIME type (e.g., 'image/png')

        Returns:
            Extracted text

        Raises:
            OCRClientError: If OCR fails
        """
        logger.debug(f"Processing {mime_type}: {len(image_bytes)} bytes")

        try:
            response = await self._call_api(image_bytes, mime_type)
            text = self._extract_response_text(response)

            logger.info(f"OCR completed: {len(text)} characters extracted")
            return text.strip()

        except OCRClientError:
            raise
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise

    @abstractmethod
    async def _call_api(self, image_bytes: bytes, mime_type: str):
        """Call provider-specific API. Implemented by subclasses."""
        pass

    @abstractmethod
    def _extract_response_text(self, response) -> str:
        """Extract text from API response. Implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the OCR provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name being used."""
        pass
