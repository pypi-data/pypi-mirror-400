"""Tests for prompt template system."""

import pytest
from magic_ocr.prompts import PromptMode, PromptTemplate


class TestPromptMode:
    def test_enum_values(self):
        assert PromptMode.MARKDOWN == "markdown"
        assert PromptMode.PLAINTEXT == "plaintext"


class TestPromptTemplate:
    def test_markdown_system_user(self):
        system_prompt = PromptTemplate.get_system_prompt(PromptMode.MARKDOWN)
        user_prompt = PromptTemplate.get_user_prompt(PromptMode.MARKDOWN)
        assert system_prompt and "Markdown" in system_prompt
        assert "LaTeX" in user_prompt and "table" in user_prompt.lower()

    def test_plaintext_system_user(self):
        system_prompt = PromptTemplate.get_system_prompt(PromptMode.PLAINTEXT)
        user_prompt = PromptTemplate.get_user_prompt(PromptMode.PLAINTEXT)
        assert system_prompt and "plain" in system_prompt.lower()
        assert "layout" in user_prompt.lower()

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            PromptTemplate.get_system_prompt("bad")
        with pytest.raises(ValueError):
            PromptTemplate.get_user_prompt("bad")
