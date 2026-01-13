"""JSON schema for LLM structured output.

This schema is designed to work with:
- OpenAI's response_format (json_schema)
- Anthropic's tools (input_schema)
- Google Gemini's response_schema

Block Type Metadata:
    heading     - level: int (1-6)
    paragraph   - (none)
    code        - language: str (optional, e.g., "python", "javascript")
    list        - listType: str ("bullet" or "ordered")
    quote       - (none)
    table       - (none - content is markdown table format)
    image       - url: str (required), alt: str (optional)
    divider     - (none)
"""

DOCUMENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Document title",
            "maxLength": 500,
        },
        "metadata": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Identifier for the agent/system that created this document",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization",
                },
            },
            "additionalProperties": True,
        },
        "blocks": {
            "type": "array",
            "description": "Content blocks that make up the document",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "heading",
                            "paragraph",
                            "code",
                            "list",
                            "quote",
                            "table",
                            "image",
                            "divider",
                        ],
                        "description": "Block type",
                    },
                    "content": {
                        "type": "string",
                        "description": "Block content (markdown for text, code for code blocks, etc.)",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Block-specific metadata. For headings: level (1-6) is REQUIRED - use 1 for main sections, 2 for subsections, 3 for sub-subsections. For code: language for syntax highlighting. For lists: listType ('bullet' or 'ordered').",
                    },
                },
                "required": ["type", "content"],
            },
        },
    },
    "required": ["title", "blocks"],
}

# OpenAI-compatible schema (strict mode requires additionalProperties: false and all properties required)
OPENAI_DOCUMENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Document title",
        },
        "metadata": {
            "type": "object",
            "properties": {
                "source": {
                    "type": ["string", "null"],
                    "description": "Identifier for the agent/system that created this document",
                },
                "tags": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization",
                },
            },
            "required": ["source", "tags"],
            "additionalProperties": False,
        },
        "blocks": {
            "type": "array",
            "description": "Content blocks that make up the document",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "heading",
                            "paragraph",
                            "code",
                            "list",
                            "quote",
                            "table",
                            "image",
                            "divider",
                        ],
                        "description": "Block type",
                    },
                    "content": {
                        "type": "string",
                        "description": "Block content (markdown for text, code for code blocks, etc.)",
                    },
                    "metadata": {
                        "type": ["object", "null"],
                        "description": "Block-specific metadata. For headings: level is REQUIRED. For code: language for syntax highlighting. For lists: listType.",
                        "properties": {
                            "level": {
                                "type": ["integer", "null"],
                                "description": "REQUIRED for heading blocks. Use 1 for main sections, 2 for subsections, 3 for sub-subsections. Always use proper hierarchy (don't skip levels).",
                            },
                            "language": {
                                "type": ["string", "null"],
                                "description": "Programming language for syntax highlighting (e.g., 'python', 'javascript'). Only for code blocks.",
                            },
                            "listType": {
                                "type": ["string", "null"],
                                "enum": ["bullet", "ordered", None],
                                "description": "List type, only for list blocks",
                            },
                            "url": {
                                "type": ["string", "null"],
                                "description": "Image URL, only for image blocks",
                            },
                            "alt": {
                                "type": ["string", "null"],
                                "description": "Image alt text, only for image blocks",
                            },
                        },
                        "required": ["level", "language", "listType", "url", "alt"],
                        "additionalProperties": False,
                    },
                },
                "required": ["type", "content", "metadata"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "metadata", "blocks"],
    "additionalProperties": False,
}

# Gemini-compatible schema (no additionalProperties, explicit metadata fields)
GEMINI_DOCUMENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Document title",
        },
        "blocks": {
            "type": "array",
            "description": "Content blocks that make up the document",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "heading",
                            "paragraph",
                            "code",
                            "list",
                            "quote",
                            "table",
                            "image",
                            "divider",
                        ],
                        "description": "Block type",
                    },
                    "content": {
                        "type": "string",
                        "description": "Block content (markdown for text, code for code blocks, etc.)",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Block-specific metadata",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "REQUIRED for heading blocks. Use 1 for main sections, 2 for subsections, 3 for sub-subsections. Always use proper hierarchy (don't skip levels).",
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language for syntax highlighting (e.g., 'python', 'javascript'). Only for code blocks.",
                            },
                            "listType": {
                                "type": "string",
                                "enum": ["bullet", "ordered"],
                                "description": "List style. Only for list blocks.",
                            },
                        },
                    },
                },
                "required": ["type", "content"],
            },
        },
    },
    "required": ["title", "blocks"],
}
