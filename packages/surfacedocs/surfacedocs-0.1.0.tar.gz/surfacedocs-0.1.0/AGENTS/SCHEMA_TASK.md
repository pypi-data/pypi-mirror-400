# Task: Document Schema Definition

## Status: COMPLETE

## Objective

Implement `DOCUMENT_SCHEMA` - the JSON schema dict that users pass to LLMs for structured output.

## Context

- Package structure already created (SETUP_TASK complete)
- Schema must work with OpenAI's `response_format` and Anthropic's `tools`
- Must match ingress-api validation requirements
- Reference: `plans/python-sdk-spec.md`, `services/ingress-api/src/main.py`

---

## Deliverable

Update `src/surfacedocs/schema.py` with the complete `DOCUMENT_SCHEMA` dict.

---

## Schema Structure

```python
DOCUMENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Document title",
            "maxLength": 500
        },
        "metadata": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Identifier for the agent/system that created this document"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization"
                }
            },
            "additionalProperties": True
        },
        "blocks": {
            "type": "array",
            "description": "Content blocks that make up the document",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["heading", "paragraph", "code", "list", "quote", "table", "image", "divider"],
                        "description": "Block type"
                    },
                    "content": {
                        "type": "string",
                        "description": "Block content (markdown for text, code for code blocks, etc.)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Block-specific metadata (level for headings, language for code, etc.)"
                    }
                },
                "required": ["type", "content"]
            }
        }
    },
    "required": ["title", "blocks"]
}
```

---

## Block Type Metadata

Document these in comments:

| Block Type | metadata fields |
|------------|-----------------|
| heading | `level` (1-6) |
| paragraph | (none) |
| code | `language` (optional) |
| list | `listType` ("bullet" or "ordered") |
| quote | (none) |
| table | (none - content is markdown table) |
| image | `url` (required), `alt` (optional) |
| divider | (none) |

---

## Verification

```python
# Test with OpenAI format
from surfacedocs import DOCUMENT_SCHEMA
import json

# Should be valid JSON schema
json.dumps(DOCUMENT_SCHEMA)

# Should have required structure
assert DOCUMENT_SCHEMA["type"] == "object"
assert "title" in DOCUMENT_SCHEMA["properties"]
assert "blocks" in DOCUMENT_SCHEMA["properties"]
assert DOCUMENT_SCHEMA["required"] == ["title", "blocks"]
```

---

## Definition of Done

- [x] `DOCUMENT_SCHEMA` fully implemented in `schema.py`
- [x] All 8 block types defined in enum
- [x] Block metadata documented in comments
- [x] Schema is valid JSON (can be serialized)
- [x] Import works: `from surfacedocs import DOCUMENT_SCHEMA`
