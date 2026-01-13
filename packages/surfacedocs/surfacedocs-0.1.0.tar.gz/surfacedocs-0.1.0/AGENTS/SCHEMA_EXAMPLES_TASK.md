# Task: Update Examples to Use Gemini Structured Output

## Status: COMPLETE

## Objective

Update `e2e_gemini.py` and `quickstart.py` to use Gemini's native `response_schema` parameter instead of prompt-based JSON generation.

## Context

- Gemini API supports native JSON schema via `response_schema` parameter
- This guarantees valid JSON output, no parsing/cleanup needed
- Cleaner code, more reliable results
- Reference: https://ai.google.dev/gemini-api/docs/structured-output

## Files to Update

- `packages/surfacedocs-python/examples/e2e_gemini.py`
- `packages/surfacedocs-python/examples/quickstart.py`

---

## Updated e2e_gemini.py

```python
#!/usr/bin/env python3
"""
End-to-end test: Generate a document with Gemini and save to SurfaceDocs.

Usage:
    export GEMINI_API_KEY=your_key
    python examples/e2e_gemini.py
"""

import os
from google import genai
from google.genai import types

from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

# Configuration
SURFACEDOCS_API_KEY = "sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX"
SURFACEDOCS_BASE_URL = "https://ingress.dev.surfacedocs.dev"
SURFACEDOCS_FOLDER_ID = "VZW8T4l44jOuVEZ4952w"


def main():
    # Initialize Gemini
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Set GEMINI_API_KEY environment variable")

    client = genai.Client(api_key=gemini_api_key)

    # Prompt for document generation
    prompt = """
Create a document about "Python Best Practices for API Development".
Include:
- A heading
- 2-3 paragraphs of content
- A code example
- A bullet list of key takeaways
"""

    print("Generating document with Gemini (using structured output)...")

    # Use native JSON schema - guarantees valid JSON output
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=DOCUMENT_SCHEMA,
        ),
    )

    # No JSON parsing needed - response.text is guaranteed valid JSON
    document = response.parsed  # or json.loads(response.text)

    print(f"\nDocument title: {document.get('title')}")
    print(f"Block count: {len(document.get('blocks', []))}")
    for i, block in enumerate(document.get('blocks', [])):
        print(f"  Block {i+1}: {block.get('type')}")

    # Save to SurfaceDocs
    print("\nSaving to SurfaceDocs...")
    docs = SurfaceDocs(api_key=SURFACEDOCS_API_KEY, base_url=SURFACEDOCS_BASE_URL)

    result = docs.save(
        content=document,
        folder_id=SURFACEDOCS_FOLDER_ID,
    )

    print(f"\n✓ Document saved successfully!")
    print(f"  ID: {result.id}")
    print(f"  URL: {result.url}")
    print(f"  Folder: {result.folder_id}")


if __name__ == "__main__":
    main()
```

---

## Updated quickstart.py

```python
#!/usr/bin/env python3
"""Minimal example: LLM output → SurfaceDocs in ~10 lines."""
import os
from google import genai
from google.genai import types
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Write a quick guide on Python virtual environments.",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=DOCUMENT_SCHEMA,
    ),
)

docs = SurfaceDocs(api_key="sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX", base_url="https://ingress.dev.surfacedocs.dev")
result = docs.save(response.text, folder_id="VZW8T4l44jOuVEZ4952w")
print(result.url)
```

---

## Key Changes

1. **Import `types` from google.genai** for `GenerateContentConfig`
2. **Use `config=types.GenerateContentConfig(...)`** instead of just `contents`
3. **Set `response_mime_type="application/json"`** to enable JSON mode
4. **Pass `response_schema=DOCUMENT_SCHEMA`** for guaranteed schema compliance
5. **Move system prompt to `system_instruction`** parameter
6. **Remove JSON parsing/cleanup code** - response is guaranteed valid
7. **Use `response.parsed`** or `json.loads(response.text)` directly

---

## Benefits

- **Guaranteed valid JSON** - no more parsing errors or markdown code block cleanup
- **Schema enforcement** - output always matches DOCUMENT_SCHEMA structure
- **Cleaner code** - remove try/catch for JSON parsing
- **Simpler prompts** - don't need "Return only JSON" instructions

---

## Run & Verify

```bash
cd packages/surfacedocs-python
export GEMINI_API_KEY=your_key

# Test e2e
python examples/e2e_gemini.py

# Test quickstart
python examples/quickstart.py
```

Both should produce valid documents without JSON parsing errors.

---

## Definition of Done

- [x] `e2e_gemini.py` updated to use `response_schema`
- [x] `quickstart.py` updated to use `response_schema`
- [x] JSON parsing/cleanup code removed
- [x] Both scripts run successfully
- [x] Documents saved to SurfaceDocs correctly

## Implementation Notes

- Added `GEMINI_DOCUMENT_SCHEMA` to `surfacedocs.schema` - a Gemini-compatible schema without `additionalProperties` (which Gemini API doesn't support)
- Exported `GEMINI_DOCUMENT_SCHEMA` from the SDK
- Updated both examples to use `GEMINI_DOCUMENT_SCHEMA` with `types.GenerateContentConfig`
