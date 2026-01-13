"""Prompt templates.

Two modes only:
- MARKDOWN: extract and express structure with Markdown (tables/formulas/sections)
- PLAINTEXT: plain text extraction preserving paragraphs and line breaks

Gemini 3 best practices (https://ai.google.dev/gemini-api/docs/gemini-3):
- Use concise, direct instructions
- Avoid complex prompt engineering (Gemini 3 handles reasoning natively)
- Place specific instructions after context data
"""

from enum import Enum
from typing import Optional


class PromptMode(str, Enum):
    """OCR prompt modes."""
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"


class PromptTemplate:
    """Prompt templates for different OCR scenarios."""

    # Markdown mode - for technical documents, academic papers
    MARKDOWN_SYSTEM = (
        "You are a helpful assistant that can accurately extract and convert "
        "content from images into clean Markdown format."
    )

    MARKDOWN_USER = """Accurately extract all content from the image including:
- Text (preserve original languages)
- Mathematical equations (convert to LaTeX)
- Tables (format as Markdown tables)
- Document structure (use headings and sections)

Convert everything to clean Markdown format while:
1. Maintaining original language(s) and layout
2. Preserving exact numerical values and symbols
3. Using $$ LaTeX $$ for equations
4. Creating Markdown tables for tabular data
5. Never adding interpretations or explanations"""

    # Plaintext mode - for general text extraction
    PLAINTEXT_SYSTEM = (
        "You are a helpful assistant that can accurately extract and convert "
        "content from images into clean plaintext."
    )

    PLAINTEXT_USER = """Please accurately identify the text content in the image:
- Preserve the original language (retain the original arrangement in multilingual contexts)
- Keep all special symbols, numbers, and punctuation
- Maintain the original layout structure (paragraphs, line breaks, indentations, etc.)"""

    # Gemini 3 optimized prompts - more concise and direct
    # Gemini 3 prefers simple, clear instructions without complex prompt engineering
    GEMINI3_MARKDOWN_SYSTEM = "Extract image content to Markdown format."

    GEMINI3_MARKDOWN_USER = """Extract all text from this image to Markdown:
- Preserve original languages and layout
- Convert equations to LaTeX ($$...$$)
- Format tables as Markdown
- Use headings for structure
- No explanations, only extracted content"""

    GEMINI3_PLAINTEXT_SYSTEM = "Extract image content as plain text."

    GEMINI3_PLAINTEXT_USER = """Extract all text from this image:
- Preserve original languages, symbols, numbers
- Maintain layout (paragraphs, line breaks)
- No explanations, only extracted content"""

    # Prompt mapping for easy lookup
    _PROMPTS = {
        PromptMode.MARKDOWN: (MARKDOWN_SYSTEM, MARKDOWN_USER),
        PromptMode.PLAINTEXT: (PLAINTEXT_SYSTEM, PLAINTEXT_USER),
    }

    # Gemini 3 optimized prompts
    _GEMINI3_PROMPTS = {
        PromptMode.MARKDOWN: (GEMINI3_MARKDOWN_SYSTEM, GEMINI3_MARKDOWN_USER),
        PromptMode.PLAINTEXT: (GEMINI3_PLAINTEXT_SYSTEM, GEMINI3_PLAINTEXT_USER),
    }

    @classmethod
    def get_system_prompt(cls, mode: PromptMode, gemini3: bool = False) -> Optional[str]:
        """Return system prompt for the given mode.

        Args:
            mode: Prompt mode (MARKDOWN or PLAINTEXT)
            gemini3: If True, return Gemini 3 optimized prompt
        """
        prompts = cls._GEMINI3_PROMPTS if gemini3 else cls._PROMPTS
        if mode not in prompts:
            raise ValueError(f"Unknown prompt mode: {mode}")
        return prompts[mode][0]

    @classmethod
    def get_user_prompt(cls, mode: PromptMode, gemini3: bool = False) -> str:
        """Return user prompt for the given mode.

        Args:
            mode: Prompt mode (MARKDOWN or PLAINTEXT)
            gemini3: If True, return Gemini 3 optimized prompt
        """
        prompts = cls._GEMINI3_PROMPTS if gemini3 else cls._PROMPTS
        if mode not in prompts:
            raise ValueError(f"Unknown prompt mode: {mode}")
        return prompts[mode][1]
