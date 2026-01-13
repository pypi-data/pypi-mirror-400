"""Configuration management for Magic OCR."""

import os
from pathlib import Path
from typing import Optional, Literal
from dotenv import load_dotenv
from .prompts import PromptMode

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)


ProviderType = Literal["gemini", "openai", "gcp"]
ThinkingLevel = Literal["minimal", "low", "medium", "high"]  # minimal/medium only for Flash
MediaResolution = Literal["auto", "low", "medium", "high", "ultra_high"]


PROVIDER_CONFIG = {
    "openai": (
        "openai_api_key",
        "OpenAI API key not configured. Please set OPENAI_API_KEY.",
    ),
    "gemini": (
        "gemini_api_key",
        "Gemini API key not configured. Please set GEMINI_API_KEY.",
    ),
    "gcp": (
        "gcp_credentials",
        "GCP credentials not configured. Please set GCP_API_KEY or GCP_CREDENTIALS.",
    ),
}


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Configuration settings for Magic OCR."""

    def __init__(self):
        # Provider selection
        self.provider: ProviderType = os.getenv("OCR_PROVIDER", "gemini").lower()
        if self.provider not in ["gemini", "openai", "gcp"]:
            raise ConfigError(
                f"Invalid OCR_PROVIDER: {self.provider}. Must be 'gemini', 'openai', or 'gcp'."
            )

        # Gemini configuration
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        self.gemini_base_url: Optional[str] = os.getenv("GEMINI_BASE_URL")
        # API version: auto (v1alpha for Gemini 3 official, v1beta for proxy), v1alpha, v1beta
        self.gemini_api_version: Optional[str] = os.getenv("GEMINI_API_VERSION", "auto")

        # Gemini 3 specific settings
        # Default: high thinking for best OCR accuracy
        # Note: 'minimal' and 'medium' only supported by Gemini 3 Flash
        thinking_level_str = os.getenv("GEMINI_THINKING_LEVEL", "high").lower()
        if thinking_level_str in ("minimal", "low", "medium", "high"):
            self.gemini_thinking_level: Optional[ThinkingLevel] = thinking_level_str
        elif thinking_level_str == "auto":
            self.gemini_thinking_level = None  # Use model default (high)
        else:
            raise ConfigError(
                f"Invalid GEMINI_THINKING_LEVEL: {thinking_level_str}. "
                "Must be 'auto', 'minimal', 'low', 'medium', or 'high'."
            )

        # Default: high resolution for best OCR quality on images
        # low: 280 tokens (image), medium: 560, high: 1120, ultra_high: max
        media_res_str = os.getenv("GEMINI_MEDIA_RESOLUTION", "high").lower()
        if media_res_str in ("low", "medium", "high", "ultra_high"):
            self.gemini_media_resolution: Optional[MediaResolution] = media_res_str
        elif media_res_str == "auto":
            self.gemini_media_resolution = None
        else:
            raise ConfigError(
                f"Invalid GEMINI_MEDIA_RESOLUTION: {media_res_str}. "
                "Must be 'auto', 'low', 'medium', 'high', or 'ultra_high'."
            )

        # OpenAI configuration
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        # GCP Vision configuration
        self.gcp_api_key: Optional[str] = os.getenv("GCP_API_KEY")
        self.gcp_credentials: Optional[str] = os.getenv("GCP_CREDENTIALS")
        self.gcp_model: str = os.getenv("GCP_MODEL", "document")  # "text" or "document"

        # OCR prompt mode (only plain/markdown)
        mode_str = os.getenv("OCR_MODE", "plain").lower()
        if mode_str in ("plain", "plaintext"):
            self.prompt_mode: PromptMode = PromptMode.PLAINTEXT
        elif mode_str == "markdown":
            self.prompt_mode = PromptMode.MARKDOWN
        else:
            raise ConfigError(
                f"Invalid OCR_MODE: {mode_str}. Must be 'plain' or 'markdown'."
            )

        # Optional prompt overrides (None -> use presets)
        self.user_prompt: Optional[str] = None
        self.system_prompt: Optional[str] = None

        # Model parameters
        # Note: Gemini 3 recommends temperature=1.0, but for OCR tasks lower values
        # provide more deterministic output. Use "auto" to let model-specific defaults apply.
        temperature_str = os.getenv("OCR_TEMPERATURE", "auto")
        if temperature_str.lower() == "auto":
            self.temperature: Optional[float] = None  # Use model-specific default
        else:
            try:
                self.temperature = float(temperature_str)
                if not (0.0 <= self.temperature <= 2.0):
                    raise ConfigError(f"OCR_TEMPERATURE must be between 0.0 and 2.0, got {self.temperature}")
            except ValueError:
                raise ConfigError(f"Invalid OCR_TEMPERATURE: {temperature_str}. Must be 'auto' or a float between 0.0 and 2.0.")

    def is_gemini3_model(self) -> bool:
        """Check if current Gemini model is a Gemini 3 series model."""
        return self.gemini_model.startswith("gemini-3")

    def get_effective_temperature(self, provider: str) -> float:
        """Get effective temperature for provider, applying model-specific defaults."""
        if self.temperature is not None:
            return self.temperature
        # Gemini 3 recommends 1.0
        if provider == "gemini" and self.is_gemini3_model():
            return 1.0
        return 0.1  # Default for other models

    def ensure_credentials(self, provider: str) -> None:
        """Validate credentials for specific provider.

        Args:
            provider: Provider name ('openai', 'gemini', or 'gcp')

        Raises:
            ConfigError: If required credentials are missing
        """
        if provider not in PROVIDER_CONFIG:
            raise ConfigError(f"Unknown provider: {provider}")

        # Special handling for GCP (needs either API key or credentials file)
        if provider == "gcp":
            if not self.gcp_api_key and not self.gcp_credentials:
                raise ConfigError(PROVIDER_CONFIG["gcp"][1])
            return

        field_name, error_msg = PROVIDER_CONFIG[provider]
        if not getattr(self, field_name, None):
            raise ConfigError(error_msg)


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the singleton configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config():
    """Reset the configuration singleton (useful for testing)."""
    global _config
    _config = None


# For convenience, also export the config instance directly
settings = get_config()
