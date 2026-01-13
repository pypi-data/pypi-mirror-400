"""System prompt for LLM document generation.

This prompt instructs LLMs to output JSON documents matching DOCUMENT_SCHEMA.

Usage with OpenAI:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Document the authentication flow"},
    ]

Usage with Anthropic:
    response = client.messages.create(
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Document the authentication flow"}],
        ...
    )
"""

SYSTEM_PROMPT: str = """When asked to create documentation, respond with a JSON document using this structure:

{
  "title": "Document title",
  "metadata": {
    "source": "agent-name",
    "tags": ["optional", "tags"]
  },
  "blocks": [
    {"type": "heading", "content": "Main Section", "metadata": {"level": 1}},
    {"type": "paragraph", "content": "Body text with **bold** and *italic*."},
    {"type": "heading", "content": "Subsection", "metadata": {"level": 2}},
    {"type": "paragraph", "content": "More content under the subsection."},
    {"type": "heading", "content": "Sub-subsection", "metadata": {"level": 3}},
    {"type": "code", "content": "print('hello')", "metadata": {"language": "python"}},
    {"type": "list", "content": "- Item 1\\n- Item 2", "metadata": {"listType": "bullet"}},
    {"type": "quote", "content": "A notable quote."},
    {"type": "table", "content": "| Col1 | Col2 |\\n|------|------|\\n| a | b |"},
    {"type": "divider", "content": ""}
  ]
}

Block types:
- heading: Section header. ALWAYS include metadata.level (1-6). Use proper hierarchy:
  - Level 1: Main sections (e.g., "Getting Started", "API Reference")
  - Level 2: Subsections within a main section
  - Level 3: Sub-subsections for detailed breakdowns
  - Never skip levels (don't go from 1 to 3 directly)
- paragraph: Body text with inline markdown
- code: Code block (metadata.language recommended, e.g., "python", "javascript", "bash")
- list: Markdown list (metadata.listType: "bullet" or "ordered")
- quote: Block quote
- table: Markdown table format
- image: Image (metadata.url required, metadata.alt optional)
- divider: Horizontal rule

Text fields support inline markdown: **bold**, *italic*, `code`, [link](url)"""
