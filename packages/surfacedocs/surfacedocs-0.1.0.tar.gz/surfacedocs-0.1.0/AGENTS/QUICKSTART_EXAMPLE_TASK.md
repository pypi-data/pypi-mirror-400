# Task: Minimal Quick Start Example

## Status: NOT STARTED

## Objective

Create the simplest possible example showing LLM → SurfaceDocs in minimal lines of code.

## Context

- E2E test complete, SDK works
- Need a dead-simple example for README/docs
- Skip all validation, error handling, etc.
- Goal: Show the value prop in <20 lines

## Credentials

```
SURFACEDOCS_API_KEY: sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX
SURFACEDOCS_FOLDER_ID: VZW8T4l44jOuVEZ4952w
```

---

## Deliverable

Create `examples/quickstart.py`:

```python
#!/usr/bin/env python3
"""Minimal example: LLM output → SurfaceDocs in ~10 lines."""

import google.generativeai as genai
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT

genai.configure(api_key="YOUR_GEMINI_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content(
    f"{SYSTEM_PROMPT}\n\nWrite a quick guide on Python virtual environments. Return only JSON."
)

docs = SurfaceDocs(api_key="sd_live_JBycgl5WHhtzVyeB9jQf7172dKvq06FX")
result = docs.save(response.text, folder_id="VZW8T4l44jOuVEZ4952w")

print(result.url)
```

---

## Run

```bash
cd packages/surfacedocs-python
pip install -e . google-generativeai
python examples/quickstart.py
```

---

## Definition of Done

- [ ] `examples/quickstart.py` created
- [ ] Script is under 15 lines (excluding comments/imports)
- [ ] Script runs and prints URL
- [ ] Document visible at URL
