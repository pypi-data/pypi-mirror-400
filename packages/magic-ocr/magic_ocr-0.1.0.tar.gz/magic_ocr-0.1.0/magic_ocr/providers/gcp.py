"""Google Cloud Vision API OCR provider implementation."""

import logging
from typing import Optional
from google.cloud import vision_v1
from google.api_core import exceptions as google_exceptions
import os

from ..base import BaseOCRClient, OCRClientError
from ..config import Config, ConfigError

logger = logging.getLogger(__name__)


GCP_ERROR_MAP = {
    "UNAUTHENTICATED": "Invalid GCP credentials. Please check your GCP_API_KEY or GCP_CREDENTIALS.\nGet credentials from https://console.cloud.google.com/",
    "PERMISSION_DENIED": "GCP Vision API access denied. Enable the Vision API at https://console.cloud.google.com/apis/library/vision.googleapis.com",
    "RESOURCE_EXHAUSTED": "GCP Vision API quota exceeded. Please wait or check your quota.",
    "INTERNAL": "GCP Vision API server error. Please try again later.",
    "UNAVAILABLE": "GCP Vision API service unavailable. Please try again later.",
}


class GCPVisionOCRClient(BaseOCRClient):
    """OCR client using Google Cloud Vision API."""

    def __init__(self, config: Optional[Config] = None, model: Optional[str] = None):
        """
        Initialize GCP Vision OCR client.

        Args:
            config: Configuration instance. If None, uses default config.
            model: OCR model type ('text' or 'document'). If None, uses config default.
        """
        from ..config import get_config
        config = config or get_config()

        # Initialize base class with config (sets up prompts & temperature)
        super().__init__(config)

        self.model = model or self.config.gcp_model

        if self.model not in ["text", "document"]:
            raise OCRClientError(f"Invalid GCP model: {self.model}. Must be 'text' or 'document'.")

        try:
            self.config.ensure_credentials("gcp")
        except ConfigError as exc:
            raise OCRClientError(str(exc)) from exc

        # Initialize Vision API client
        self._init_client()

        logger.info(f"Initialized GCP Vision OCR client with model: {self.model}")

    def _build_feature(self) -> vision_v1.Feature:
        """Build the Vision API feature based on the selected model."""
        if self.model == "document":
            logger.info("Sending DOCUMENT_TEXT_DETECTION request to GCP Vision API")
            return vision_v1.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)

        logger.info("Sending TEXT_DETECTION request to GCP Vision API")
        return vision_v1.Feature(type_=vision_v1.Feature.Type.TEXT_DETECTION)

    async def _annotate_image(self, image: vision_v1.Image):
        """Send a single-image request via batch_annotate_images."""
        feature = self._build_feature()
        request = vision_v1.AnnotateImageRequest(image=image, features=[feature])

        batch_response = await self.client.batch_annotate_images(requests=[request])
        if not batch_response.responses:
            raise OCRClientError("GCP Vision API returned empty batch response")

        return batch_response.responses[0]

    def _handle_api_error(self, e: Exception) -> None:
        """Handle GCP Vision API errors uniformly."""
        if isinstance(e, google_exceptions.GoogleAPIError):
            status = getattr(e, "grpc_status_code", None) or getattr(e, "code", None)
            status_name = getattr(status, "name", None) if status else None
            if not status_name and status:
                status_name = str(status)

            logger.error("GCP Vision API error (code=%s): %s", status_name or "unknown", e)

            if status_name in GCP_ERROR_MAP:
                raise OCRClientError(GCP_ERROR_MAP[status_name]) from e

            raise OCRClientError("Failed to process image with GCP Vision API. Please try again later.") from e
        if isinstance(e, OCRClientError):
            raise
        logger.error("Unexpected GCP Vision API error: %s", e)
        raise OCRClientError(f"Failed to process image with GCP Vision API: {str(e)}") from e

    def _init_client(self):
        """Initialize the Vision API async client with appropriate credentials."""
        # Set up credentials
        if self.config.gcp_credentials:
            # Use service account credentials file
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config.gcp_credentials
            self.client = vision_v1.ImageAnnotatorAsyncClient()
            logger.debug(f"Using GCP credentials from: {self.config.gcp_credentials}")
        elif self.config.gcp_api_key:
            # Use API key
            from google.api_core import client_options as client_options_lib

            client_options = client_options_lib.ClientOptions(
                api_key=self.config.gcp_api_key
            )
            self.client = vision_v1.ImageAnnotatorAsyncClient(client_options=client_options)
            logger.debug("Using GCP API key authentication")
        else:
            # Fall back to ADC (Application Default Credentials)
            self.client = vision_v1.ImageAnnotatorAsyncClient()
            logger.debug("Using GCP Application Default Credentials")

    async def _call_api(self, image_bytes: bytes, mime_type: str):
        """Call GCP Vision API."""
        try:
            # Prepare image
            image = vision_v1.Image(content=image_bytes)
            return await self._annotate_image(image)
        except Exception as e:
            self._handle_api_error(e)

    def _extract_response_text(self, response) -> str:
        """Extract text from GCP Vision response."""
        # Check for errors
        if response.error.message:
            logger.error("GCP Vision API error: %s", response.error.message)
            raise OCRClientError(f"GCP Vision API error: {response.error.message}")

        # Extract text based on model type
        if self.model == "document":
            # DOCUMENT_TEXT_DETECTION returns full_text_annotation
            if not response.full_text_annotation or not response.full_text_annotation.text:
                logger.warning("GCP Vision API returned empty document text annotation")
                raise OCRClientError("GCP Vision API returned empty response. The image may not contain any text.")
            return response.full_text_annotation.text
        else:  # text
            # TEXT_DETECTION returns text_annotations
            if not response.text_annotations:
                logger.warning("GCP Vision API returned empty text annotations")
                raise OCRClientError("GCP Vision API returned empty response. The image may not contain any text.")
            # First annotation contains the full detected text
            return response.text_annotations[0].description

    async def extract_text_from_url(self, image_url: str) -> str:
        """Extract text from image URL using GCP Vision's native URL support.

        Supports both Cloud Storage URIs (gs://) and HTTP/HTTPS URLs.
        Note: Google recommends using gs:// for production reliability.
        """
        logger.info("Sending OCR request to GCP Vision API with URL: %s", image_url)

        try:
            # Prepare image source
            image = vision_v1.Image()
            image.source.image_uri = image_url

            response = await self._annotate_image(image)
            text = self._extract_response_text(response)
            logger.info(f"OCR completed: {len(text)} characters extracted")
            return text.strip()
        except Exception as e:
            self._handle_api_error(e)

    @property
    def provider_name(self) -> str:
        """Return the name of the OCR provider."""
        return "GCP Vision"

    @property
    def model_name(self) -> str:
        """Return the model name being used."""
        return f"{self.model.upper()}_DETECTION"
