# Task: End-to-End Test with Gemini

## Status: COMPLETE

## Objective

Write and run an e2e test script that uses Google Gemini to generate a document and saves it to the SurfaceDocs dev environment.

## Context

- SDK is complete (SETUP, SCHEMA, PROMPT, CLIENT, TESTS, DOCS done)
- Need to verify real API integration works
- Use Gemini as the LLM (user has Gemini API access)
- Push to dev SurfaceDocs instance

## Credentials

```
SURFACEDOCS_API_KEY: sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX
SURFACEDOCS_FOLDER_ID: VZW8T4l44jOuVEZ4952w
GEMINI_API_KEY: (use from environment or user will provide)
```

---

## Deliverable

Create `examples/e2e_gemini.py`:

```python
#!/usr/bin/env python3
"""
End-to-end test: Generate a document with Gemini and save to SurfaceDocs.

Usage:
    export GEMINI_API_KEY=your_key
    python examples/e2e_gemini.py
"""

import os
import json
import google.generativeai as genai

from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

# Configuration
SURFACEDOCS_API_KEY = "sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX"
SURFACEDOCS_FOLDER_ID = "VZW8T4l44jOuVEZ4952w"


def main():
    # Initialize Gemini
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Set GEMINI_API_KEY environment variable")

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Build prompt for Gemini
    # Gemini doesn't have native JSON schema mode like OpenAI, so we include
    # the schema in the prompt and ask for JSON output
    prompt = f"""
{SYSTEM_PROMPT}

Now, create a document about "Python Best Practices for API Development".
Include:
- A heading
- 2-3 paragraphs of content
- A code example
- A bullet list of key takeaways

Respond with ONLY the JSON document, no other text.
"""

    print("Generating document with Gemini...")
    response = model.generate_content(prompt)

    # Extract JSON from response
    response_text = response.text.strip()

    # Handle markdown code blocks if present
    if response_text.startswith("```"):
        # Remove ```json and ``` markers
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    print(f"Gemini response:\n{response_text[:500]}...")

    # Parse and validate
    try:
        document = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Raw response: {response_text}")
        raise

    print(f"\nDocument title: {document.get('title')}")
    print(f"Block count: {len(document.get('blocks', []))}")

    # Save to SurfaceDocs
    print("\nSaving to SurfaceDocs...")
    client = SurfaceDocs(api_key=SURFACEDOCS_API_KEY)

    result = client.save(
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

## Setup

```bash
cd packages/surfacedocs-python

# Install the SDK locally
pip install -e .

# Install Gemini SDK
pip install google-generativeai

# Set Gemini API key
export GEMINI_API_KEY=your_gemini_key_here

# Create examples directory
mkdir -p examples

# Run the test
python examples/e2e_gemini.py
```

---

## Expected Output

```
Generating document with Gemini...
Gemini response:
{
  "title": "Python Best Practices for API Development",
  "blocks": [
    {"type": "heading", "content": "Introduction", "metadata": {"level": 1}},
    ...
  ]
}...

Document title: Python Best Practices for API Development
Block count: 6

Saving to SurfaceDocs...

✓ Document saved successfully!
  ID: doc_abc123
  URL: https://app.surfacedocs.dev/d/doc_abc123
  Folder: VZW8T4l44jOuVEZ4952w
```

---

## Verification

After running:

1. Check the URL prints correctly
2. Visit the URL in browser to see the document
3. Verify document appears in the specified folder
4. Check all block types rendered correctly

---

## Definition of Done

- [x] `examples/e2e_gemini.py` created
- [x] Script runs without errors
- [x] Document successfully saved to SurfaceDocs
- [x] Document visible at returned URL
- [x] Document contains expected blocks (heading, paragraphs, code, list)
