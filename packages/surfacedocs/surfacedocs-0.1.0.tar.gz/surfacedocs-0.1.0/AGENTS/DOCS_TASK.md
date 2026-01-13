# Task: Documentation

## Status: COMPLETE

## Objective

Write user-facing documentation: README with examples, docstrings, and LICENSE.

## Context

- All code and tests complete
- README is primary documentation (shown on PyPI)
- Reference: `plans/python-sdk-spec.md`

---

## Deliverables

1. `README.md` - Full documentation with examples
2. Docstrings on all public APIs
3. `LICENSE` - MIT license (verify exists)

---

## README.md

```markdown
# SurfaceDocs Python SDK

Save LLM-generated documents to [SurfaceDocs](https://surfacedocs.dev).

## Installation

```bash
pip install surfacedocs
```

## Quick Start

```python
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT
from openai import OpenAI

# Initialize clients
openai = OpenAI()
docs = SurfaceDocs(api_key="sd_live_...")

# Generate a document with your LLM
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Document our REST API authentication flow"},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "surfacedocs_document",
            "schema": DOCUMENT_SCHEMA,
        },
    },
)

# Save to SurfaceDocs
result = docs.save(response.choices[0].message.content)
print(result.url)  # https://app.surfacedocs.dev/d/abc123
```

## What's Included

The SDK provides three exports:

| Export | Type | Purpose |
|--------|------|---------|
| `DOCUMENT_SCHEMA` | dict | JSON schema for LLM structured output |
| `SYSTEM_PROMPT` | str | Instructions for LLM to generate documents |
| `SurfaceDocs` | class | HTTP client to save documents |

## API Reference

### SurfaceDocs

```python
from surfacedocs import SurfaceDocs

# Initialize with API key
client = SurfaceDocs(api_key="sd_live_...")

# Or use environment variable
# export SURFACEDOCS_API_KEY=sd_live_...
client = SurfaceDocs()
```

#### save(content, folder_id=None)

Save a document from LLM output.

```python
# From JSON string
result = client.save(response.choices[0].message.content)

# From dict
result = client.save({
    "title": "My Document",
    "blocks": [{"type": "paragraph", "content": "Hello world"}]
})

# To specific folder
result = client.save(content, folder_id="folder_abc123")
```

#### save_raw(title, blocks, folder_id=None, metadata=None)

Save a document with explicit parameters.

```python
result = client.save_raw(
    title="API Documentation",
    blocks=[
        {"type": "heading", "content": "Authentication", "metadata": {"level": 1}},
        {"type": "paragraph", "content": "Use Bearer tokens for auth."},
        {"type": "code", "content": "curl -H 'Authorization: Bearer ...'", "metadata": {"language": "bash"}},
    ],
    metadata={"source": "doc-generator", "version": "1.0"},
)
```

#### SaveResult

Both methods return a `SaveResult`:

```python
result.id        # "doc_abc123"
result.url       # "https://app.surfacedocs.dev/d/doc_abc123"
result.folder_id # "folder_xyz"
```

### DOCUMENT_SCHEMA

JSON schema dict for LLM structured output. Pass directly to your LLM provider.

```python
from surfacedocs import DOCUMENT_SCHEMA

# OpenAI
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "surfacedocs_document",
            "schema": DOCUMENT_SCHEMA,
        },
    },
)

# Anthropic
response = anthropic.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[...],
    tools=[{
        "name": "create_document",
        "description": "Create a structured document",
        "input_schema": DOCUMENT_SCHEMA,
    }],
    tool_choice={"type": "tool", "name": "create_document"},
)
```

### SYSTEM_PROMPT

System prompt string to instruct LLMs on document format.

```python
from surfacedocs import SYSTEM_PROMPT

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Document the login flow"},
]
```

## Block Types

Documents are composed of blocks:

| Type | Description | Metadata |
|------|-------------|----------|
| `heading` | Section header | `level` (1-6) |
| `paragraph` | Body text | - |
| `code` | Code block | `language` (optional) |
| `list` | Bullet/numbered list | `listType` ("bullet" or "ordered") |
| `quote` | Block quote | - |
| `table` | Markdown table | - |
| `image` | Image | `url` (required), `alt` (optional) |
| `divider` | Horizontal rule | - |

Text content supports inline markdown: `**bold**`, `*italic*`, `` `code` ``, `[link](url)`

## Error Handling

```python
from surfacedocs import SurfaceDocs, SurfaceDocsError, AuthenticationError, ValidationError

try:
    result = client.save(content)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid document: {e}")
except SurfaceDocsError as e:
    print(f"API error: {e}")
```

## Environment Variables

```bash
# API key (alternative to passing in code)
export SURFACEDOCS_API_KEY=sd_live_...

# Override base URL (for testing)
export SURFACEDOCS_BASE_URL=https://ingress.dev.surfacedocs.dev
```

The SDK auto-detects environment from API key prefix:
- `sd_live_*` → Production
- `sd_test_*` → Development

## Examples

### OpenAI

```python
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT
from openai import OpenAI

openai = OpenAI()
docs = SurfaceDocs()

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Write documentation for user authentication"},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "document", "schema": DOCUMENT_SCHEMA},
    },
)

result = docs.save(response.choices[0].message.content)
print(f"Saved: {result.url}")
```

### Anthropic

```python
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT
import anthropic

client = anthropic.Anthropic()
docs = SurfaceDocs()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": "Write documentation for user authentication"},
    ],
    tools=[{
        "name": "create_document",
        "description": "Create a structured document",
        "input_schema": DOCUMENT_SCHEMA,
    }],
    tool_choice={"type": "tool", "name": "create_document"},
)

tool_use = next(b for b in response.content if b.type == "tool_use")
result = docs.save(tool_use.input)
print(f"Saved: {result.url}")
```

### Manual Document

```python
from surfacedocs import SurfaceDocs

docs = SurfaceDocs()

result = docs.save_raw(
    title="Meeting Notes",
    blocks=[
        {"type": "heading", "content": "Action Items", "metadata": {"level": 1}},
        {"type": "list", "content": "- Review PR #123\n- Update docs", "metadata": {"listType": "bullet"}},
        {"type": "divider", "content": ""},
        {"type": "paragraph", "content": "Next meeting: Monday 10am"},
    ],
    metadata={"source": "meeting-bot"},
)
```

## License

MIT
```

---

## Docstrings

Ensure all public APIs have docstrings:

- `SurfaceDocs.__init__`
- `SurfaceDocs.save`
- `SurfaceDocs.save_raw`
- `SaveResult` class
- All exception classes
- Module-level docstrings for `schema.py` and `prompt.py`

---

## Verification

```bash
# README renders correctly
python -m readme_renderer README.md

# Or just check it's valid markdown
cat README.md
```

---

## Definition of Done

- [x] `README.md` with installation, quick start, API reference, examples
- [x] OpenAI example in README
- [x] Anthropic example in README
- [x] Block types documented
- [x] Error handling documented
- [x] All public APIs have docstrings
- [x] `LICENSE` file exists (MIT)
