"""Tests for DOCUMENT_SCHEMA."""

import json

import pytest

from surfacedocs import DOCUMENT_SCHEMA
from surfacedocs.schema import DOCUMENT_SCHEMA as SCHEMA_DIRECT


class TestDocumentSchemaStructure:
    """Test the basic structure of DOCUMENT_SCHEMA."""

    def test_schema_is_dict(self):
        """Schema should be a dictionary."""
        assert isinstance(DOCUMENT_SCHEMA, dict)

    def test_schema_type_is_object(self):
        """Schema type should be 'object'."""
        assert DOCUMENT_SCHEMA["type"] == "object"

    def test_schema_has_properties(self):
        """Schema should have properties."""
        assert "properties" in DOCUMENT_SCHEMA
        assert isinstance(DOCUMENT_SCHEMA["properties"], dict)

    def test_schema_has_required_fields(self):
        """Schema should define required fields."""
        assert "required" in DOCUMENT_SCHEMA
        assert DOCUMENT_SCHEMA["required"] == ["title", "blocks"]


class TestTitleProperty:
    """Test the title property in the schema."""

    def test_title_exists(self):
        """Title property should exist."""
        assert "title" in DOCUMENT_SCHEMA["properties"]

    def test_title_is_string(self):
        """Title should be a string type."""
        title = DOCUMENT_SCHEMA["properties"]["title"]
        assert title["type"] == "string"

    def test_title_has_max_length(self):
        """Title should have maxLength constraint."""
        title = DOCUMENT_SCHEMA["properties"]["title"]
        assert title["maxLength"] == 500

    def test_title_has_description(self):
        """Title should have a description."""
        title = DOCUMENT_SCHEMA["properties"]["title"]
        assert "description" in title


class TestMetadataProperty:
    """Test the metadata property in the schema."""

    def test_metadata_exists(self):
        """Metadata property should exist."""
        assert "metadata" in DOCUMENT_SCHEMA["properties"]

    def test_metadata_is_object(self):
        """Metadata should be an object type."""
        metadata = DOCUMENT_SCHEMA["properties"]["metadata"]
        assert metadata["type"] == "object"

    def test_metadata_has_source(self):
        """Metadata should have source property."""
        metadata = DOCUMENT_SCHEMA["properties"]["metadata"]
        assert "source" in metadata["properties"]
        assert metadata["properties"]["source"]["type"] == "string"

    def test_metadata_has_tags(self):
        """Metadata should have tags property."""
        metadata = DOCUMENT_SCHEMA["properties"]["metadata"]
        assert "tags" in metadata["properties"]
        tags = metadata["properties"]["tags"]
        assert tags["type"] == "array"
        assert tags["items"]["type"] == "string"

    def test_metadata_allows_additional_properties(self):
        """Metadata should allow additional properties."""
        metadata = DOCUMENT_SCHEMA["properties"]["metadata"]
        assert metadata["additionalProperties"] is True


class TestBlocksProperty:
    """Test the blocks property in the schema."""

    def test_blocks_exists(self):
        """Blocks property should exist."""
        assert "blocks" in DOCUMENT_SCHEMA["properties"]

    def test_blocks_is_array(self):
        """Blocks should be an array type."""
        blocks = DOCUMENT_SCHEMA["properties"]["blocks"]
        assert blocks["type"] == "array"

    def test_blocks_has_description(self):
        """Blocks should have a description."""
        blocks = DOCUMENT_SCHEMA["properties"]["blocks"]
        assert "description" in blocks

    def test_blocks_has_items(self):
        """Blocks should define items."""
        blocks = DOCUMENT_SCHEMA["properties"]["blocks"]
        assert "items" in blocks
        assert isinstance(blocks["items"], dict)


class TestBlockItemSchema:
    """Test the block item schema within blocks."""

    @pytest.fixture
    def block_item(self):
        """Get the block item schema."""
        return DOCUMENT_SCHEMA["properties"]["blocks"]["items"]

    def test_block_item_is_object(self, block_item):
        """Block item should be an object."""
        assert block_item["type"] == "object"

    def test_block_item_has_type_property(self, block_item):
        """Block item should have type property."""
        assert "type" in block_item["properties"]

    def test_block_item_has_content_property(self, block_item):
        """Block item should have content property."""
        assert "content" in block_item["properties"]

    def test_block_item_has_metadata_property(self, block_item):
        """Block item should have metadata property."""
        assert "metadata" in block_item["properties"]

    def test_block_item_required_fields(self, block_item):
        """Block item should require type and content."""
        assert block_item["required"] == ["type", "content"]


class TestBlockTypes:
    """Test the block type enum values."""

    @pytest.fixture
    def block_type_enum(self):
        """Get the block type enum values."""
        return DOCUMENT_SCHEMA["properties"]["blocks"]["items"]["properties"]["type"]["enum"]

    def test_has_heading_type(self, block_type_enum):
        """Should include heading block type."""
        assert "heading" in block_type_enum

    def test_has_paragraph_type(self, block_type_enum):
        """Should include paragraph block type."""
        assert "paragraph" in block_type_enum

    def test_has_code_type(self, block_type_enum):
        """Should include code block type."""
        assert "code" in block_type_enum

    def test_has_list_type(self, block_type_enum):
        """Should include list block type."""
        assert "list" in block_type_enum

    def test_has_quote_type(self, block_type_enum):
        """Should include quote block type."""
        assert "quote" in block_type_enum

    def test_has_table_type(self, block_type_enum):
        """Should include table block type."""
        assert "table" in block_type_enum

    def test_has_image_type(self, block_type_enum):
        """Should include image block type."""
        assert "image" in block_type_enum

    def test_has_divider_type(self, block_type_enum):
        """Should include divider block type."""
        assert "divider" in block_type_enum

    def test_has_exactly_eight_types(self, block_type_enum):
        """Should have exactly 8 block types."""
        assert len(block_type_enum) == 8

    def test_all_expected_types(self, block_type_enum):
        """Should have all expected block types."""
        expected = ["heading", "paragraph", "code", "list", "quote", "table", "image", "divider"]
        assert sorted(block_type_enum) == sorted(expected)


class TestSchemaJsonSerialization:
    """Test that the schema can be serialized to JSON."""

    def test_schema_is_json_serializable(self):
        """Schema should be serializable to JSON."""
        json_str = json.dumps(DOCUMENT_SCHEMA)
        assert isinstance(json_str, str)

    def test_schema_roundtrip(self):
        """Schema should survive JSON roundtrip."""
        json_str = json.dumps(DOCUMENT_SCHEMA)
        parsed = json.loads(json_str)
        assert parsed == DOCUMENT_SCHEMA


class TestSchemaImports:
    """Test that schema can be imported correctly."""

    def test_import_from_package(self):
        """Should be importable from main package."""
        from surfacedocs import DOCUMENT_SCHEMA as pkg_schema
        assert pkg_schema is not None
        assert isinstance(pkg_schema, dict)

    def test_import_from_module(self):
        """Should be importable from schema module."""
        assert SCHEMA_DIRECT is not None
        assert isinstance(SCHEMA_DIRECT, dict)

    def test_imports_are_same_object(self):
        """Both imports should reference the same object."""
        assert DOCUMENT_SCHEMA is SCHEMA_DIRECT
