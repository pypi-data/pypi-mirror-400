"""Magic OCR - Multi-provider OCR library with MCP server support."""

from .base import BaseOCRClient, OCRClientError
from .config import Config, get_config, reset_config, ProviderType
from .prompts import PromptMode, PromptTemplate
from .providers import GeminiOCRClient, OpenAIOCRClient, GCPVisionOCRClient
from .utils import read_image_file, decode_base64_image, get_mime_type

__version__ = "0.1.0"

__all__ = [
    "BaseOCRClient",
    "OCRClientError",
    "Config",
    "get_config",
    "reset_config",
    "ProviderType",
    "PromptMode",
    "PromptTemplate",
    "GeminiOCRClient",
    "OpenAIOCRClient",
    "GCPVisionOCRClient",
    "read_image_file",
    "decode_base64_image",
    "get_mime_type",
]


def get_ocr_client(provider: str = None, config: Config = None, model: str = None) -> BaseOCRClient:
    """
    Factory function to get an OCR client instance.

    Args:
        provider: Provider name ('gemini', 'openai', or 'gcp'). If None, uses config default.
        config: Configuration instance. If None, uses default config.
        model: Model name to use. For GCP: 'text' or 'document'. For others: model identifier.

    Returns:
        An instance of the appropriate OCR client

    Raises:
        ValueError: If provider is invalid
        OCRClientError: If client initialization fails
    """
    if config is None:
        config = get_config()

    provider = provider or config.provider

    factories = {
        "gemini": lambda: GeminiOCRClient(config),
        "openai": lambda: OpenAIOCRClient(config),
        "gcp": lambda: GCPVisionOCRClient(config, model=model),
    }

    try:
        return factories[provider]()
    except KeyError:
        raise ValueError(f"Unknown provider: {provider}. Must be 'gemini', 'openai', or 'gcp'.") from None
