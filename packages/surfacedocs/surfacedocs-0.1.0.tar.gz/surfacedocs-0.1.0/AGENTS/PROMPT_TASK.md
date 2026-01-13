# Task: System Prompt Definition

## Status: COMPLETE

## Objective

Implement `SYSTEM_PROMPT` - the instruction string users include in LLM messages to generate valid documents.

## Context

- SETUP_TASK and SCHEMA_TASK complete
- Prompt must instruct LLMs to output JSON matching `DOCUMENT_SCHEMA`
- Should be concise but complete
- Reference: `plans/python-sdk-spec.md`

---

## Deliverable

Update `src/surfacedocs/prompt.py` with the complete `SYSTEM_PROMPT` string.

---

## Prompt Content

```python
SYSTEM_PROMPT: str = """When asked to create documentation, respond with a JSON document using this structure:

{
  "title": "Document title",
  "metadata": {
    "source": "agent-name",
    "tags": ["optional", "tags"]
  },
  "blocks": [
    {"type": "heading", "content": "Section Header", "metadata": {"level": 1}},
    {"type": "paragraph", "content": "Body text with **bold** and *italic*."},
    {"type": "code", "content": "print('hello')", "metadata": {"language": "python"}},
    {"type": "list", "content": "- Item 1\\n- Item 2", "metadata": {"listType": "bullet"}},
    {"type": "quote", "content": "A notable quote."},
    {"type": "table", "content": "| Col1 | Col2 |\\n|------|------|\\n| a | b |"},
    {"type": "divider", "content": ""}
  ]
}

Block types:
- heading: Section header (metadata.level: 1-6)
- paragraph: Body text with inline markdown
- code: Code block (metadata.language optional)
- list: Markdown list (metadata.listType: "bullet" or "ordered")
- quote: Block quote
- table: Markdown table format
- image: Image (metadata.url required, metadata.alt optional)
- divider: Horizontal rule

Text fields support inline markdown: **bold**, *italic*, `code`, [link](url)"""
```

---

## Usage Examples

Include comments showing how users will use this:

```python
# OpenAI
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Document the authentication flow"},
]

# Anthropic
response = client.messages.create(
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": "Document the authentication flow"}],
    ...
)
```

---

## Verification

```python
from surfacedocs import SYSTEM_PROMPT

# Should be a non-empty string
assert isinstance(SYSTEM_PROMPT, str)
assert len(SYSTEM_PROMPT) > 100

# Should mention key block types
assert "heading" in SYSTEM_PROMPT
assert "paragraph" in SYSTEM_PROMPT
assert "code" in SYSTEM_PROMPT

# Should include JSON example
assert "{" in SYSTEM_PROMPT
assert '"blocks"' in SYSTEM_PROMPT
```

---

## Definition of Done

- [x] `SYSTEM_PROMPT` implemented in `prompt.py`
- [x] JSON example included in prompt
- [x] All 8 block types documented
- [x] Metadata fields explained for each block type
- [x] Import works: `from surfacedocs import SYSTEM_PROMPT`
