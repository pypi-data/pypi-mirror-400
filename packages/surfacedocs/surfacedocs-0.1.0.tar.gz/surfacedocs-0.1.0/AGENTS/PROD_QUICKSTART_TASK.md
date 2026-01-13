# Task: Update Quickstart Examples to Production

## Status: COMPLETE

## Objective

Update all quickstart examples to use the production SurfaceDocs instance and verify they work end-to-end.

## Context

- Production environment is now live
- All quickstart examples currently point to dev instance
- Need to verify SDK works against prod before PyPI publish

## Production Credentials

```
API Key: sd_live_RrJPC6LqO0CqSqnGeNnm93RHlXa8x6iS
Base URL: https://ingress.surfacedocs.dev
Folder ID: xEQ5xO0wt0g4Oj5cm07X
```

---

## Files to Update

```
packages/surfacedocs-python/examples/
├── quickstart_openai.py
├── quickstart_anthropic.py
├── quickstart_gemini.py (was quickstart.py)
└── e2e_gemini.py
```

---

## Changes Required

### 1. Update `quickstart_openai.py`

```python
docs = SurfaceDocs(
    api_key="sd_live_RrJPC6LqO0CqSqnGeNnm93RHlXa8x6iS",
    base_url="https://ingress.surfacedocs.dev",
)
result = docs.save(response.choices[0].message.content, folder_id="xEQ5xO0wt0g4Oj5cm07X")
```

### 2. Update `quickstart_anthropic.py`

```python
docs = SurfaceDocs(
    api_key="sd_live_RrJPC6LqO0CqSqnGeNnm93RHlXa8x6iS",
    base_url="https://ingress.surfacedocs.dev",
)
result = docs.save(tool_use.input, folder_id="xEQ5xO0wt0g4Oj5cm07X")
```

### 3. Update `quickstart_gemini.py`

```python
docs = SurfaceDocs(
    api_key="sd_live_RrJPC6LqO0CqSqnGeNnm93RHlXa8x6iS",
    base_url="https://ingress.surfacedocs.dev",
)
result = docs.save(response.text, folder_id="xEQ5xO0wt0g4Oj5cm07X")
```

### 4. Update `e2e_gemini.py`

```python
SURFACEDOCS_API_KEY = "sd_live_RrJPC6LqO0CqSqnGeNnm93RHlXa8x6iS"
SURFACEDOCS_BASE_URL = "https://ingress.surfacedocs.dev"
SURFACEDOCS_FOLDER_ID = "xEQ5xO0wt0g4Oj5cm07X"
```

---

## Verification

Run each example and verify:

```bash
cd packages/surfacedocs-python

# Set LLM API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...

# Run each quickstart
python examples/quickstart_openai.py
python examples/quickstart_anthropic.py
python examples/quickstart_gemini.py
python examples/e2e_gemini.py
```

For each:
1. Script runs without errors
2. Document URL is printed
3. URL points to `app.surfacedocs.dev` (prod viewer)
4. Document renders correctly at the URL
5. Document appears in folder `xEQ5xO0wt0g4Oj5cm07X`

---

## Definition of Done

- [x] `quickstart_openai.py` updated and verified
- [x] `quickstart_anthropic.py` updated and verified
- [x] `quickstart_gemini.py` updated and verified
- [x] `e2e_gemini.py` updated and verified
- [x] All documents visible in prod viewer
- [x] All documents in correct folder

## Verification Results

All examples ran successfully against production:

| Example | Document URL |
|---------|-------------|
| quickstart_openai.py | https://app.surfacedocs.dev/d/doc_ZOHQwKlg6d6L |
| quickstart_anthropic.py | https://app.surfacedocs.dev/d/doc_F3DSvWQkh3Ml |
| quickstart_gemini.py | https://app.surfacedocs.dev/d/doc_P6M4eP4gck92 |
| e2e_gemini.py | https://app.surfacedocs.dev/d/doc_e5qaPqi05a9h |

All documents saved to folder `xEQ5xO0wt0g4Oj5cm07X` in production.
