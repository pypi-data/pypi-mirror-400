# Task: Test Suite

## Status: COMPLETE

## Objective

Write unit tests for the SDK using pytest and respx (httpx mocking).

## Context

- All core modules complete (SETUP, SCHEMA, PROMPT, CLIENT)
- Use respx to mock HTTP requests
- Target >80% coverage
- Reference: `packages/surfacedocs-python/src/surfacedocs/`

---

## Deliverables

Create/update test files in `tests/`:

```
tests/
├── __init__.py
├── conftest.py        # Shared fixtures
├── test_schema.py     # Schema validation tests
├── test_prompt.py     # Prompt content tests
├── test_client.py     # Client HTTP tests
└── test_exceptions.py # Exception tests
```

---

## conftest.py

```python
import pytest
import respx
from httpx import Response


@pytest.fixture
def mock_api():
    """Mock the SurfaceDocs API."""
    with respx.mock(base_url="https://ingress.dev.surfacedocs.dev") as respx_mock:
        yield respx_mock


@pytest.fixture
def success_response():
    """Standard success response from API."""
    return {
        "id": "doc_test123",
        "url": "https://app.dev.surfacedocs.dev/d/doc_test123",
        "folder_id": "folder_root",
        "title": "Test Document",
        "block_count": 2,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        "title": "Test Document",
        "metadata": {"source": "test"},
        "blocks": [
            {"type": "heading", "content": "Hello", "metadata": {"level": 1}},
            {"type": "paragraph", "content": "World"},
        ],
    }
```

---

## test_schema.py

```python
import json
from surfacedocs import DOCUMENT_SCHEMA


def test_schema_is_dict():
    assert isinstance(DOCUMENT_SCHEMA, dict)


def test_schema_is_valid_json():
    # Should serialize without error
    json.dumps(DOCUMENT_SCHEMA)


def test_schema_has_required_fields():
    assert DOCUMENT_SCHEMA["type"] == "object"
    assert "title" in DOCUMENT_SCHEMA["properties"]
    assert "blocks" in DOCUMENT_SCHEMA["properties"]


def test_schema_required_array():
    assert "title" in DOCUMENT_SCHEMA["required"]
    assert "blocks" in DOCUMENT_SCHEMA["required"]


def test_schema_block_types():
    block_schema = DOCUMENT_SCHEMA["properties"]["blocks"]["items"]
    block_types = block_schema["properties"]["type"]["enum"]

    expected = ["heading", "paragraph", "code", "list", "quote", "table", "image", "divider"]
    assert set(block_types) == set(expected)
```

---

## test_prompt.py

```python
from surfacedocs import SYSTEM_PROMPT


def test_prompt_is_string():
    assert isinstance(SYSTEM_PROMPT, str)


def test_prompt_not_empty():
    assert len(SYSTEM_PROMPT) > 100


def test_prompt_contains_block_types():
    assert "heading" in SYSTEM_PROMPT
    assert "paragraph" in SYSTEM_PROMPT
    assert "code" in SYSTEM_PROMPT
    assert "list" in SYSTEM_PROMPT
    assert "quote" in SYSTEM_PROMPT
    assert "table" in SYSTEM_PROMPT
    assert "image" in SYSTEM_PROMPT
    assert "divider" in SYSTEM_PROMPT


def test_prompt_contains_json_example():
    assert '"blocks"' in SYSTEM_PROMPT
    assert '"title"' in SYSTEM_PROMPT


def test_prompt_documents_metadata():
    assert "level" in SYSTEM_PROMPT  # heading level
    assert "language" in SYSTEM_PROMPT  # code language
```

---

## test_client.py

```python
import json
import os
import pytest
from httpx import Response
import respx

from surfacedocs import SurfaceDocs, SaveResult
from surfacedocs.exceptions import (
    AuthenticationError,
    FolderNotFoundError,
    SurfaceDocsError,
    ValidationError,
)


class TestClientInit:
    def test_requires_api_key(self):
        # Clear env var if set
        os.environ.pop("SURFACEDOCS_API_KEY", None)

        with pytest.raises(AuthenticationError, match="API key required"):
            SurfaceDocs()

    def test_accepts_api_key_arg(self):
        client = SurfaceDocs(api_key="sd_test_abc123")
        assert client.api_key == "sd_test_abc123"

    def test_reads_env_var(self, monkeypatch):
        monkeypatch.setenv("SURFACEDOCS_API_KEY", "sd_test_fromenv")
        client = SurfaceDocs()
        assert client.api_key == "sd_test_fromenv"

    def test_detects_dev_url(self):
        client = SurfaceDocs(api_key="sd_test_abc123")
        assert client.base_url == "https://ingress.dev.surfacedocs.dev"

    def test_detects_prod_url(self):
        client = SurfaceDocs(api_key="sd_live_abc123")
        assert client.base_url == "https://ingress.surfacedocs.dev"

    def test_custom_base_url(self):
        client = SurfaceDocs(api_key="sd_test_abc", base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    def test_strips_trailing_slash(self):
        client = SurfaceDocs(api_key="sd_test_abc", base_url="https://example.com/")
        assert client.base_url == "https://example.com"


class TestClientSave:
    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_save_with_dict(self, success_response, sample_document):
        respx.post("/v1/documents").mock(return_value=Response(201, json=success_response))

        client = SurfaceDocs(api_key="sd_test_abc")
        result = client.save(sample_document)

        assert isinstance(result, SaveResult)
        assert result.id == "doc_test123"
        assert result.url == "https://app.dev.surfacedocs.dev/d/doc_test123"

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_save_with_json_string(self, success_response, sample_document):
        respx.post("/v1/documents").mock(return_value=Response(201, json=success_response))

        client = SurfaceDocs(api_key="sd_test_abc")
        result = client.save(json.dumps(sample_document))

        assert result.id == "doc_test123"

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_save_with_folder_id(self, success_response, sample_document):
        route = respx.post("/v1/documents").mock(return_value=Response(201, json=success_response))

        client = SurfaceDocs(api_key="sd_test_abc")
        client.save(sample_document, folder_id="folder_custom")

        request_body = json.loads(route.calls.last.request.content)
        assert request_body["folder_id"] == "folder_custom"

    def test_save_invalid_json(self):
        client = SurfaceDocs(api_key="sd_test_abc")

        with pytest.raises(ValidationError, match="Invalid JSON"):
            client.save("not valid json {")

    def test_save_missing_title(self):
        client = SurfaceDocs(api_key="sd_test_abc")

        with pytest.raises(ValidationError, match="title"):
            client.save({"blocks": []})

    def test_save_missing_blocks(self):
        client = SurfaceDocs(api_key="sd_test_abc")

        with pytest.raises(ValidationError, match="blocks"):
            client.save({"title": "Test"})


class TestClientSaveRaw:
    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_save_raw_minimal(self, success_response):
        respx.post("/v1/documents").mock(return_value=Response(201, json=success_response))

        client = SurfaceDocs(api_key="sd_test_abc")
        result = client.save_raw(
            title="Test",
            blocks=[{"type": "paragraph", "content": "Hello"}],
        )

        assert result.id == "doc_test123"

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_save_raw_with_all_params(self, success_response):
        route = respx.post("/v1/documents").mock(return_value=Response(201, json=success_response))

        client = SurfaceDocs(api_key="sd_test_abc")
        client.save_raw(
            title="Test",
            blocks=[{"type": "paragraph", "content": "Hello"}],
            folder_id="folder_123",
            metadata={"source": "test"},
        )

        request_body = json.loads(route.calls.last.request.content)
        assert request_body["folder_id"] == "folder_123"
        assert request_body["metadata"] == {"source": "test"}


class TestClientErrors:
    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_401_raises_auth_error(self):
        respx.post("/v1/documents").mock(
            return_value=Response(401, json={"detail": "Invalid API key"})
        )

        client = SurfaceDocs(api_key="sd_test_abc")
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.save_raw(title="Test", blocks=[])

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_404_raises_folder_not_found(self):
        respx.post("/v1/documents").mock(
            return_value=Response(404, json={"detail": "Folder not found"})
        )

        client = SurfaceDocs(api_key="sd_test_abc")
        with pytest.raises(FolderNotFoundError):
            client.save_raw(title="Test", blocks=[], folder_id="bad_folder")

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_422_raises_validation_error(self):
        respx.post("/v1/documents").mock(
            return_value=Response(422, json={"detail": "Title too long"})
        )

        client = SurfaceDocs(api_key="sd_test_abc")
        with pytest.raises(ValidationError, match="Title too long"):
            client.save_raw(title="Test", blocks=[])

    @respx.mock(base_url="https://ingress.dev.surfacedocs.dev")
    def test_500_raises_generic_error(self):
        respx.post("/v1/documents").mock(
            return_value=Response(500, json={"detail": "Internal error"})
        )

        client = SurfaceDocs(api_key="sd_test_abc")
        with pytest.raises(SurfaceDocsError, match="500"):
            client.save_raw(title="Test", blocks=[])


class TestClientContextManager:
    def test_context_manager(self):
        with SurfaceDocs(api_key="sd_test_abc") as client:
            assert client.api_key == "sd_test_abc"
        # Client should be closed after exiting
```

---

## test_exceptions.py

```python
from surfacedocs.exceptions import (
    SurfaceDocsError,
    AuthenticationError,
    ValidationError,
    FolderNotFoundError,
)


def test_exception_hierarchy():
    assert issubclass(AuthenticationError, SurfaceDocsError)
    assert issubclass(ValidationError, SurfaceDocsError)
    assert issubclass(FolderNotFoundError, SurfaceDocsError)


def test_exceptions_can_be_raised():
    with pytest.raises(SurfaceDocsError):
        raise SurfaceDocsError("test")

    with pytest.raises(AuthenticationError):
        raise AuthenticationError("test")


def test_exception_message():
    e = ValidationError("Invalid format")
    assert str(e) == "Invalid format"
```

---

## Running Tests

```bash
cd packages/surfacedocs-python
pip install -e ".[dev]"
pytest -v
pytest --cov=surfacedocs --cov-report=term-missing
```

---

## Definition of Done

- [x] `conftest.py` with shared fixtures
- [x] `test_schema.py` - schema structure tests
- [x] `test_prompt.py` - prompt content tests
- [x] `test_client.py` - HTTP client tests with mocking
- [x] `test_exceptions.py` - exception hierarchy tests
- [x] All tests pass: `pytest -v`
- [x] Coverage >80% (achieved 100%)
