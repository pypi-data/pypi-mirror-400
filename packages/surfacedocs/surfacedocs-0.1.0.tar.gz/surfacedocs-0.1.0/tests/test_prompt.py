"""Tests for SYSTEM_PROMPT."""

import pytest

from surfacedocs import SYSTEM_PROMPT
from surfacedocs.prompt import SYSTEM_PROMPT as PROMPT_DIRECT


class TestSystemPrompt:
    """Test the SYSTEM_PROMPT constant."""

    def test_prompt_exists(self):
        """SYSTEM_PROMPT should exist."""
        assert SYSTEM_PROMPT is not None

    def test_prompt_is_string(self):
        """SYSTEM_PROMPT should be a string."""
        assert isinstance(SYSTEM_PROMPT, str)

    def test_prompt_is_not_empty(self):
        """SYSTEM_PROMPT should not be empty."""
        assert len(SYSTEM_PROMPT) > 0

    def test_prompt_has_minimum_length(self):
        """SYSTEM_PROMPT should be at least 100 characters."""
        assert len(SYSTEM_PROMPT) > 100


class TestPromptJsonExample:
    """Test that prompt includes JSON example."""

    def test_contains_json_structure(self):
        """Prompt should include JSON example with braces."""
        assert "{" in SYSTEM_PROMPT
        assert "}" in SYSTEM_PROMPT

    def test_contains_title_field(self):
        """Prompt should mention title field."""
        assert '"title"' in SYSTEM_PROMPT

    def test_contains_blocks_field(self):
        """Prompt should mention blocks field."""
        assert '"blocks"' in SYSTEM_PROMPT

    def test_contains_metadata_field(self):
        """Prompt should mention metadata field."""
        assert '"metadata"' in SYSTEM_PROMPT


class TestPromptBlockTypes:
    """Test that all block types are documented in prompt."""

    def test_contains_heading_type(self):
        """Prompt should document heading block type."""
        assert "heading" in SYSTEM_PROMPT

    def test_contains_paragraph_type(self):
        """Prompt should document paragraph block type."""
        assert "paragraph" in SYSTEM_PROMPT

    def test_contains_code_type(self):
        """Prompt should document code block type."""
        assert "code" in SYSTEM_PROMPT

    def test_contains_list_type(self):
        """Prompt should document list block type."""
        assert "list" in SYSTEM_PROMPT

    def test_contains_quote_type(self):
        """Prompt should document quote block type."""
        assert "quote" in SYSTEM_PROMPT

    def test_contains_table_type(self):
        """Prompt should document table block type."""
        assert "table" in SYSTEM_PROMPT

    def test_contains_image_type(self):
        """Prompt should document image block type."""
        assert "image" in SYSTEM_PROMPT

    def test_contains_divider_type(self):
        """Prompt should document divider block type."""
        assert "divider" in SYSTEM_PROMPT


class TestPromptMetadataFields:
    """Test that metadata fields are explained."""

    def test_heading_level_documented(self):
        """Heading level metadata should be documented."""
        assert "level" in SYSTEM_PROMPT

    def test_code_language_documented(self):
        """Code language metadata should be documented."""
        assert "language" in SYSTEM_PROMPT

    def test_list_type_documented(self):
        """List type metadata should be documented."""
        assert "listType" in SYSTEM_PROMPT
        assert "bullet" in SYSTEM_PROMPT
        assert "ordered" in SYSTEM_PROMPT

    def test_image_url_documented(self):
        """Image url metadata should be documented."""
        assert "url" in SYSTEM_PROMPT


class TestPromptMarkdownSupport:
    """Test that inline markdown support is documented."""

    def test_bold_documented(self):
        """Bold markdown should be documented."""
        assert "**bold**" in SYSTEM_PROMPT

    def test_italic_documented(self):
        """Italic markdown should be documented."""
        assert "*italic*" in SYSTEM_PROMPT

    def test_inline_code_documented(self):
        """Inline code markdown should be documented."""
        assert "`code`" in SYSTEM_PROMPT

    def test_link_documented(self):
        """Link markdown should be documented."""
        assert "[link](url)" in SYSTEM_PROMPT


class TestPromptImports:
    """Test prompt import paths."""

    def test_import_from_package(self):
        """SYSTEM_PROMPT should be importable from main package."""
        from surfacedocs import SYSTEM_PROMPT as PkgPrompt
        assert PkgPrompt is not None

    def test_import_from_module(self):
        """SYSTEM_PROMPT should be importable from prompt module."""
        assert PROMPT_DIRECT is not None

    def test_imports_are_same_object(self):
        """Both imports should reference the same object."""
        assert SYSTEM_PROMPT is PROMPT_DIRECT


class TestPromptModuleDocstring:
    """Test prompt module documentation."""

    def test_module_has_docstring(self):
        """Prompt module should have a docstring."""
        from surfacedocs import prompt
        assert prompt.__doc__ is not None

    def test_module_docstring_mentions_llm(self):
        """Module docstring should mention LLM."""
        from surfacedocs import prompt
        assert "LLM" in prompt.__doc__
