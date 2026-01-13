"""Magic OCR MCP Server - FastMCP v2 implementation."""

import logging
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastmcp import FastMCP
from .tools import ocr_image
from ..config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get configuration to display in instructions
config = get_config()

# Initialize FastMCP server
mcp = FastMCP(
    "Magic OCR Server",
    instructions="""
    OCR tool for extracting text from images.

    Usage: ocr_image(image[, mode])

    Parameters:
    - image: (required) ABSOLUTE file path (e.g., /Users/name/image.png),
      URL (https://...), or base64 string.
      Prefer absolute path or URL over base64. Do NOT use relative paths.
    - mode: 'plain' | 'markdown' (default: plain)
    - provider: 'gemini' | 'openai' | 'gcp'
    - model: model name
    - system_prompt: custom system prompt
    - user_prompt: custom user prompt

    All optional parameters have optimized defaults.
    Only override when user explicitly requests a specific value.
    """
)

# Register OCR tool
mcp.tool(ocr_image)


def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting Magic OCR MCP Server with provider: {config.provider}")
    mcp.run()


if __name__ == "__main__":
    main()
