# Python SDK Orchestration

This document outlines the implementation plan for the SurfaceDocs Python SDK. Each phase has a corresponding task file that can be handed off to a separate agent session.

---

## Overview

**What:** Minimal Python SDK for pushing LLM-generated documents to SurfaceDocs
**Package Name:** `surfacedocs`
**Target:** PyPI (pip install surfacedocs)
**Design Philosophy:** Users handle their own LLM calls; we provide schema, prompt, and client

---

## Three Exports

The SDK provides exactly three things:

| Export | Type | Purpose |
|--------|------|---------|
| `DOCUMENT_SCHEMA` | dict | JSON schema for LLM structured output |
| `SYSTEM_PROMPT` | str | Instructions for LLM to generate proper documents |
| `SurfaceDocs` | class | HTTP client to save documents |

---

## Implementation Phases

### Phase 1: Project Setup
**Task File:** `SETUP_TASK.md`
**Effort:** Small

- Initialize Python package structure with `pyproject.toml`
- Configure for modern Python packaging (PEP 517/518)
- Set up basic directory structure
- Add development dependencies (pytest, respx)
- Create `__init__.py` with public exports

**Deliverable:** Empty package that can be installed locally with `pip install -e .`

---

### Phase 2: Schema Definition
**Task File:** `SCHEMA_TASK.md`
**Effort:** Small

- Define `DOCUMENT_SCHEMA` as JSON schema dict
- Include all block types (heading, paragraph, code, list, quote, table, image, divider)
- Match ingress-api validation requirements
- Export from `schema.py`

**Deliverable:** `DOCUMENT_SCHEMA` that works with OpenAI's `response_format` and Anthropic's `tools`

---

### Phase 3: System Prompt
**Task File:** `PROMPT_TASK.md`
**Effort:** Small

- Define `SYSTEM_PROMPT` string constant
- Include document structure example
- Document all block types and their metadata
- Keep it concise but complete
- Export from `prompt.py`

**Deliverable:** `SYSTEM_PROMPT` that instructs LLMs to generate valid documents

---

### Phase 4: HTTP Client
**Task File:** `CLIENT_TASK.md`
**Effort:** Medium

- Implement `SurfaceDocs` class with httpx
- `save(content, folder_id=None)` - accepts JSON string or dict
- `save_raw(title, blocks, folder_id=None, metadata=None)` - explicit params
- Auto-detect base URL from API key prefix (sd_live_ vs sd_test_)
- Return `SaveResult` with id, url, folder_id
- Support `SURFACEDOCS_API_KEY` env var fallback

**Deliverable:** Working client that can save documents to ingress-api

---

### Phase 5: Exception Handling
**Task File:** `EXCEPTIONS_TASK.md`
**Effort:** Small

- Define exception hierarchy:
  - `SurfaceDocsError` (base)
  - `AuthenticationError`
  - `ValidationError`
  - `FolderNotFoundError`
- Map HTTP status codes to exceptions
- Include helpful error messages

**Deliverable:** Clean exception types for SDK users

---

### Phase 6: Tests
**Task File:** `TESTS_TASK.md`
**Effort:** Medium

- Unit tests for schema validation
- Unit tests for client (mock HTTP with respx)
- Test error handling paths
- Test env var fallback
- Test URL auto-detection

**Deliverable:** Test suite with >80% coverage

---

### Phase 7: Documentation
**Task File:** `DOCS_TASK.md`
**Effort:** Small

- Write README.md with:
  - Installation
  - Quick start (OpenAI example)
  - API reference
  - Anthropic example
- Add docstrings to public API
- Include LICENSE file (MIT)

**Deliverable:** README ready for PyPI

---

### Phase 8: Publishing Prep
**Task File:** `PUBLISH_TASK.md`
**Effort:** Small

- Verify `pyproject.toml` metadata is complete
- Build package with `python -m build`
- Test install from built wheel
- Create PyPI account (if needed)
- Generate API token
- Document publish process

**Deliverable:** Package ready to publish (but not published yet)

---

## Task Execution Order

```
Phase 1: Setup ─────────────────┐
                                │
Phase 2: Schema ────────────────┤
                                ├──► Core exports ready
Phase 3: Prompt ────────────────┤
                                │
Phase 4: Client ────────────────┼──► Functional SDK
                                │
Phase 5: Exceptions ────────────┤
                                │
Phase 6: Tests ─────────────────┼──► Quality verified
                                │
Phase 7: Docs ──────────────────┼──► User-ready
                                │
Phase 8: Publishing ────────────┘──► Ready to publish
```

Phases 2-3 can run in parallel. Phase 4 depends on 2-3. Phase 5 can run with 4. Phase 6 depends on 4-5.

---

## Reference Documents

- `plans/python-sdk-spec.md` - Detailed SDK specification
- `services/ingress-api/src/main.py` - API endpoint implementation
- `plans/firestore-schema-spec.md` - Document/block schema

---

## Project Structure

```
packages/surfacedocs-python/
├── AGENTS/
│   ├── ORCHESTRATION.md      # This file
│   ├── SETUP_TASK.md
│   ├── SCHEMA_TASK.md
│   ├── PROMPT_TASK.md
│   ├── CLIENT_TASK.md
│   ├── EXCEPTIONS_TASK.md
│   ├── TESTS_TASK.md
│   ├── DOCS_TASK.md
│   └── PUBLISH_TASK.md
├── src/
│   └── surfacedocs/
│       ├── __init__.py       # Public exports
│       ├── client.py         # SurfaceDocs class
│       ├── schema.py         # DOCUMENT_SCHEMA
│       ├── prompt.py         # SYSTEM_PROMPT
│       └── exceptions.py     # Exception classes
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_schema.py
│   └── conftest.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## Dependencies

**Runtime:**
- `httpx>=0.26.0` - HTTP client

**Development:**
- `pytest>=7.4.0` - Testing
- `respx>=0.20.0` - HTTP mocking
- `build` - Package building

**NOT required:**
- Pydantic (plain dicts for simplicity)
- Any LLM libraries (user brings their own)

---

## Success Criteria

SDK is ready for publishing when:
- [ ] `pip install .` works locally
- [ ] All three exports work (`DOCUMENT_SCHEMA`, `SYSTEM_PROMPT`, `SurfaceDocs`)
- [ ] Can save a document to dev ingress-api
- [ ] Tests pass
- [ ] README has working examples
- [ ] `python -m build` produces wheel and sdist
- [ ] Built package installs correctly

---

## Publishing (Future)

When ready to publish:

```bash
# Build
python -m build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ surfacedocs

# Upload to PyPI
twine upload dist/*
```

Requirements:
- PyPI account at pypi.org
- API token from PyPI account settings
- `twine` installed (`pip install twine`)
