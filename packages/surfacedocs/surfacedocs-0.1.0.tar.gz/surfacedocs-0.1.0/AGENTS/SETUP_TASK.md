# Task: Python SDK Project Setup

## Status: COMPLETE

## Objective

Initialize the Python package structure for the SurfaceDocs SDK with modern packaging standards.

## Context

- Package name: `surfacedocs`
- Target: PyPI publication
- Python version: >=3.9
- Single runtime dependency: httpx
- Reference spec: `plans/python-sdk-spec.md`

---

## Deliverables

Create the following structure:

```
packages/surfacedocs-python/
├── src/
│   └── surfacedocs/
│       ├── __init__.py       # Public exports (empty for now)
│       ├── client.py         # Placeholder
│       ├── schema.py         # Placeholder
│       ├── prompt.py         # Placeholder
│       └── exceptions.py     # Placeholder
├── tests/
│   ├── __init__.py
│   └── conftest.py           # pytest fixtures
├── pyproject.toml            # Package config
├── README.md                 # Basic readme
└── LICENSE                   # MIT license
```

---

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "surfacedocs"
version = "0.1.0"
description = "Python SDK for SurfaceDocs - Save LLM-generated documents"
readme = "README.md"
license = "MIT"
requires-python = ">=3.9"
authors = [
    { name = "SurfaceDocs", email = "hello@surfacedocs.dev" }
]
keywords = ["llm", "documentation", "ai", "sdk"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "respx>=0.20.0",
    "build",
]

[project.urls]
Homepage = "https://surfacedocs.dev"
Documentation = "https://surfacedocs.dev/docs"
Repository = "https://github.com/surfacedocs/surfacedocs-python"

[tool.hatch.build.targets.wheel]
packages = ["src/surfacedocs"]
```

---

## __init__.py

```python
"""SurfaceDocs Python SDK - Save LLM-generated documents."""

from surfacedocs.schema import DOCUMENT_SCHEMA
from surfacedocs.prompt import SYSTEM_PROMPT
from surfacedocs.client import SurfaceDocs
from surfacedocs.exceptions import (
    SurfaceDocsError,
    AuthenticationError,
    ValidationError,
    FolderNotFoundError,
)

__version__ = "0.1.0"

__all__ = [
    "DOCUMENT_SCHEMA",
    "SYSTEM_PROMPT",
    "SurfaceDocs",
    "SurfaceDocsError",
    "AuthenticationError",
    "ValidationError",
    "FolderNotFoundError",
    "__version__",
]
```

---

## Placeholder Files

Each module should have a placeholder that raises NotImplementedError:

**schema.py:**
```python
"""JSON schema for LLM structured output."""

DOCUMENT_SCHEMA: dict = {}  # TODO: Implement in SCHEMA_TASK
```

**prompt.py:**
```python
"""System prompt for LLM document generation."""

SYSTEM_PROMPT: str = ""  # TODO: Implement in PROMPT_TASK
```

**client.py:**
```python
"""HTTP client for saving documents."""

class SurfaceDocs:
    """SurfaceDocs API client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        raise NotImplementedError("TODO: Implement in CLIENT_TASK")
```

**exceptions.py:**
```python
"""SDK exceptions."""

class SurfaceDocsError(Exception):
    """Base exception for SDK errors."""
    pass

class AuthenticationError(SurfaceDocsError):
    """Invalid or missing API key."""
    pass

class ValidationError(SurfaceDocsError):
    """Invalid document structure."""
    pass

class FolderNotFoundError(SurfaceDocsError):
    """Specified folder doesn't exist."""
    pass
```

---

## Verification

After setup, verify:

```bash
cd packages/surfacedocs-python
pip install -e ".[dev]"
python -c "from surfacedocs import DOCUMENT_SCHEMA, SYSTEM_PROMPT, SurfaceDocs; print('OK')"
```

---

## Definition of Done

- [x] Directory structure created
- [x] pyproject.toml with all metadata
- [x] __init__.py with exports
- [x] Placeholder modules created
- [x] exceptions.py fully implemented
- [x] Package installs locally with `pip install -e .`
- [x] Import statement works (even if NotImplementedError on use)
- [x] MIT LICENSE file added
- [x] Basic README.md added
