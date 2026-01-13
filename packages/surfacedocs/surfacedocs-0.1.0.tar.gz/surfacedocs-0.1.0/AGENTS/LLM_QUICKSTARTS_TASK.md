# Task: LLM Provider Quick Start Examples

## Status: COMPLETE

## Objective

Create working quick start examples for OpenAI and Anthropic that use structured output (not prompt-based JSON). Verify all examples work end-to-end with the SurfaceDocs dev environment.

## Context

- Gemini example complete using `response_schema` (see `examples/quickstart.py`)
- OpenAI supports structured output via `response_format` with JSON schema
- Anthropic supports structured output via `tools` with `tool_choice`
- All examples must use native structured output - NO prompt-based "return JSON" hacks
- SDK exports: `DOCUMENT_SCHEMA`, `GEMINI_DOCUMENT_SCHEMA`, `SYSTEM_PROMPT`, `SurfaceDocs`

## Credentials

```
SURFACEDOCS_API_KEY: sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX
SURFACEDOCS_BASE_URL: https://ingress.dev.surfacedocs.dev
SURFACEDOCS_FOLDER_ID: VZW8T4l44jOuVEZ4952w
```

---

## Deliverables

Create three example files:

```
packages/surfacedocs-python/examples/
├── quickstart_openai.py    # OpenAI with response_format
├── quickstart_anthropic.py # Anthropic with tools
└── quickstart_gemini.py    # Already exists - verify still works
```

---

## OpenAI Example: `quickstart_openai.py`

```python
#!/usr/bin/env python3
"""Quick start: OpenAI → SurfaceDocs using structured output."""
import os
from openai import OpenAI
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

client = OpenAI()  # Uses OPENAI_API_KEY env var

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Write a quick guide on Python virtual environments."},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "surfacedocs_document",
            "strict": True,
            "schema": DOCUMENT_SCHEMA,
        },
    },
)

docs = SurfaceDocs(
    api_key="sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX",
    base_url="https://ingress.dev.surfacedocs.dev",
)
result = docs.save(response.choices[0].message.content, folder_id="VZW8T4l44jOuVEZ4952w")
print(f"Saved: {result.url}")
```

**Key points:**
- Uses `response_format` with `type: "json_schema"`
- Set `strict: True` for guaranteed schema compliance
- Response is in `response.choices[0].message.content` as JSON string

---

## Anthropic Example: `quickstart_anthropic.py`

```python
#!/usr/bin/env python3
"""Quick start: Anthropic → SurfaceDocs using tool use."""
import os
import anthropic
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": "Write a quick guide on Python virtual environments."},
    ],
    tools=[
        {
            "name": "create_document",
            "description": "Create a structured document for SurfaceDocs",
            "input_schema": DOCUMENT_SCHEMA,
        }
    ],
    tool_choice={"type": "tool", "name": "create_document"},
)

# Extract tool use result
tool_use = next(block for block in response.content if block.type == "tool_use")

docs = SurfaceDocs(
    api_key="sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX",
    base_url="https://ingress.dev.surfacedocs.dev",
)
result = docs.save(tool_use.input, folder_id="VZW8T4l44jOuVEZ4952w")
print(f"Saved: {result.url}")
```

**Key points:**
- Uses `tools` array with `input_schema`
- Force tool use with `tool_choice={"type": "tool", "name": "create_document"}`
- Response is in `tool_use.input` as a dict (not string)

---

## Schema Compatibility Notes

Different providers have different JSON schema support:

| Provider | Schema Support | Notes |
|----------|---------------|-------|
| OpenAI | Full JSON Schema | Use `DOCUMENT_SCHEMA` with `strict: True` |
| Anthropic | Full JSON Schema | Use `DOCUMENT_SCHEMA` in `input_schema` |
| Gemini | Limited | Use `GEMINI_DOCUMENT_SCHEMA` (no `additionalProperties`) |

If OpenAI or Anthropic reject the schema, you may need to create provider-specific versions like we did for Gemini.

---

## Setup & Run

```bash
cd packages/surfacedocs-python

# Install SDK and providers
pip install -e .
pip install openai anthropic

# Set API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Run examples
python examples/quickstart_openai.py
python examples/quickstart_anthropic.py
python examples/quickstart_gemini.py  # Verify still works
```

---

## Verification

For each example:
1. Script runs without errors
2. Document URL is printed
3. Visit URL - document renders correctly
4. Document has proper structure (heading, paragraphs, etc.)
5. Document appears in folder `VZW8T4l44jOuVEZ4952w`

---

## Troubleshooting

**OpenAI schema rejection:**
- Try removing `additionalProperties` from schema
- Check if any nested objects need `required` arrays
- OpenAI strict mode is picky about schema format

**Anthropic tool not called:**
- Ensure `tool_choice` forces the specific tool
- Check `response.stop_reason` - should be `tool_use`

**Schema drift:**
- If you modify the schema for one provider, consider if changes should apply to all
- Document any provider-specific schemas in `schema.py`

---

## Definition of Done

- [x] `quickstart_openai.py` created and working
- [x] `quickstart_anthropic.py` created and working
- [x] `quickstart_gemini.py` verified still working
- [x] All three save documents successfully
- [x] All three use native structured output (not prompt hacks)
- [x] Any schema compatibility issues documented (OpenAI requires `OPENAI_DOCUMENT_SCHEMA`)
- [ ] README updated with all three examples (optional)

## Completion Notes

All three quickstart examples are working:

- **OpenAI**: Uses `OPENAI_DOCUMENT_SCHEMA` (created new schema for strict mode compatibility)
  - Output: https://dev.surfacedocs.dev/d/doc_Dxb7-2bgVCjP
- **Anthropic**: Uses `DOCUMENT_SCHEMA` with tool use
  - Output: https://dev.surfacedocs.dev/d/doc_L8KkwMe8lHJ4
- **Gemini**: Uses `GEMINI_DOCUMENT_SCHEMA`
  - Output: https://dev.surfacedocs.dev/d/doc_XF7kO3JiHgmP

### Schema Compatibility

OpenAI's strict mode requires `additionalProperties: false` and all properties listed in `required` arrays at every level. Created `OPENAI_DOCUMENT_SCHEMA` to meet these requirements.
