"""Tests for SurfaceDocs client."""

import json
import os

import httpx
import pytest
import respx

from surfacedocs import (
    SaveResult,
    SurfaceDocs,
    AuthenticationError,
    FolderNotFoundError,
    SurfaceDocsError,
    ValidationError,
)
from surfacedocs.client import SaveResult as DirectSaveResult
from surfacedocs.client import SurfaceDocs as DirectSurfaceDocs


class TestSurfaceDocsClient:
    """Test the SurfaceDocs client class."""

    def test_client_class_exists(self):
        """SurfaceDocs class should exist."""
        assert SurfaceDocs is not None

    def test_client_is_class(self):
        """SurfaceDocs should be a class."""
        assert isinstance(SurfaceDocs, type)

    def test_client_raises_without_api_key(self):
        """Client should raise AuthenticationError without API key."""
        # Clear env var if set
        env_key = os.environ.pop("SURFACEDOCS_API_KEY", None)
        try:
            with pytest.raises(AuthenticationError):
                SurfaceDocs()
        finally:
            if env_key:
                os.environ["SURFACEDOCS_API_KEY"] = env_key

    def test_client_accepts_api_key(self):
        """Client should accept api_key parameter."""
        client = SurfaceDocs(api_key="sd_test_abc123")
        assert client.api_key == "sd_test_abc123"
        client.close()

    def test_client_reads_env_var(self):
        """Client should read API key from environment."""
        old_val = os.environ.get("SURFACEDOCS_API_KEY")
        os.environ["SURFACEDOCS_API_KEY"] = "sd_test_from_env"
        try:
            client = SurfaceDocs()
            assert client.api_key == "sd_test_from_env"
            client.close()
        finally:
            if old_val:
                os.environ["SURFACEDOCS_API_KEY"] = old_val
            else:
                os.environ.pop("SURFACEDOCS_API_KEY", None)


class TestBaseUrlDetection:
    """Test base URL auto-detection from API key prefix."""

    def test_dev_url_for_test_key(self):
        """Should use dev URL for sd_test_ prefixed keys."""
        client = SurfaceDocs(api_key="sd_test_abc123")
        assert client.base_url == SurfaceDocs.DEV_URL
        client.close()

    def test_prod_url_for_live_key(self):
        """Should use prod URL for sd_live_ prefixed keys."""
        client = SurfaceDocs(api_key="sd_live_abc123")
        assert client.base_url == SurfaceDocs.PROD_URL
        client.close()

    def test_prod_url_for_unknown_prefix(self):
        """Should default to prod URL for unknown prefixes."""
        client = SurfaceDocs(api_key="some_other_key")
        assert client.base_url == SurfaceDocs.PROD_URL
        client.close()

    def test_custom_base_url(self):
        """Should use custom base URL when provided."""
        client = SurfaceDocs(api_key="sd_test_abc", base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"
        client.close()

    def test_custom_base_url_strips_trailing_slash(self):
        """Should strip trailing slash from custom base URL."""
        client = SurfaceDocs(api_key="sd_test_abc", base_url="https://custom.api.com/")
        assert client.base_url == "https://custom.api.com"
        client.close()


class TestContextManager:
    """Test context manager support."""

    def test_context_manager_returns_client(self):
        """Context manager should return client instance."""
        with SurfaceDocs(api_key="sd_test_abc123") as client:
            assert isinstance(client, SurfaceDocs)
            assert client.api_key == "sd_test_abc123"

    def test_context_manager_closes_client(self):
        """Context manager should close client on exit."""
        with SurfaceDocs(api_key="sd_test_abc123") as client:
            # Client is open
            assert client._client is not None
        # After context, client should be closed (no error thrown)


class TestSaveResult:
    """Test the SaveResult dataclass."""

    def test_save_result_exists(self):
        """SaveResult class should exist."""
        assert SaveResult is not None

    def test_save_result_is_dataclass(self):
        """SaveResult should be a dataclass."""
        from dataclasses import is_dataclass
        assert is_dataclass(SaveResult)

    def test_save_result_has_fields(self):
        """SaveResult should have id, url, folder_id fields."""
        result = SaveResult(id="doc_123", url="https://example.com/d/doc_123", folder_id="folder_456")
        assert result.id == "doc_123"
        assert result.url == "https://example.com/d/doc_123"
        assert result.folder_id == "folder_456"


class TestSaveMethod:
    """Test the save() method."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        c = SurfaceDocs(api_key="sd_test_abc123")
        yield c
        c.close()

    def test_save_raises_on_invalid_json_string(self, client):
        """save() should raise ValidationError on invalid JSON string."""
        with pytest.raises(ValidationError) as exc_info:
            client.save("not valid json")
        assert "Invalid JSON" in str(exc_info.value)

    def test_save_raises_on_missing_title(self, client):
        """save() should raise ValidationError when title is missing."""
        with pytest.raises(ValidationError) as exc_info:
            client.save({"blocks": [{"type": "paragraph", "content": "test"}]})
        assert "title" in str(exc_info.value)

    def test_save_raises_on_missing_blocks(self, client):
        """save() should raise ValidationError when blocks is missing."""
        with pytest.raises(ValidationError) as exc_info:
            client.save({"title": "Test"})
        assert "blocks" in str(exc_info.value)

    def test_save_raises_on_empty_blocks(self, client):
        """save() should raise ValidationError when blocks is empty."""
        with pytest.raises(ValidationError) as exc_info:
            client.save({"title": "Test", "blocks": []})
        assert "blocks" in str(exc_info.value)

    @respx.mock
    def test_save_with_dict(self, client):
        """save() should accept dict content."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "doc_123",
                    "url": "https://app.surfacedocs.dev/d/doc_123",
                    "folder_id": "folder_456",
                    "title": "Test Doc",
                    "block_count": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )
        result = client.save({
            "title": "Test Doc",
            "blocks": [{"type": "paragraph", "content": "Hello"}],
        })
        assert result.id == "doc_123"
        assert result.url == "https://app.surfacedocs.dev/d/doc_123"

    @respx.mock
    def test_save_with_json_string(self, client):
        """save() should accept JSON string content."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "doc_123",
                    "url": "https://app.surfacedocs.dev/d/doc_123",
                    "folder_id": "folder_456",
                    "title": "Test Doc",
                    "block_count": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )
        content = json.dumps({
            "title": "Test Doc",
            "blocks": [{"type": "paragraph", "content": "Hello"}],
        })
        result = client.save(content)
        assert result.id == "doc_123"


class TestSaveRawMethod:
    """Test the save_raw() method."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        c = SurfaceDocs(api_key="sd_test_abc123")
        yield c
        c.close()

    @respx.mock
    def test_save_raw_basic(self, client):
        """save_raw() should save document with basic params."""
        route = respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "doc_123",
                    "url": "https://app.surfacedocs.dev/d/doc_123",
                    "folder_id": "folder_root",
                    "title": "Test Doc",
                    "block_count": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )
        result = client.save_raw(
            title="Test Doc",
            blocks=[{"type": "paragraph", "content": "Hello"}],
        )
        assert result.id == "doc_123"
        assert result.folder_id == "folder_root"

        # Verify request payload
        request = route.calls.last.request
        body = json.loads(request.content)
        assert body["title"] == "Test Doc"
        assert body["blocks"] == [{"type": "paragraph", "content": "Hello"}]
        assert body["content_type"] == "markdown"
        assert "folder_id" not in body

    @respx.mock
    def test_save_raw_with_folder_id(self, client):
        """save_raw() should include folder_id when provided."""
        route = respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "doc_123",
                    "url": "https://app.surfacedocs.dev/d/doc_123",
                    "folder_id": "folder_custom",
                    "title": "Test Doc",
                    "block_count": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )
        result = client.save_raw(
            title="Test Doc",
            blocks=[{"type": "paragraph", "content": "Hello"}],
            folder_id="folder_custom",
        )
        assert result.folder_id == "folder_custom"

        request = route.calls.last.request
        body = json.loads(request.content)
        assert body["folder_id"] == "folder_custom"

    @respx.mock
    def test_save_raw_with_metadata(self, client):
        """save_raw() should include metadata when provided."""
        route = respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": "doc_123",
                    "url": "https://app.surfacedocs.dev/d/doc_123",
                    "folder_id": "folder_root",
                    "title": "Test Doc",
                    "block_count": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                },
            )
        )
        client.save_raw(
            title="Test Doc",
            blocks=[{"type": "paragraph", "content": "Hello"}],
            metadata={"source": "test-agent", "tags": ["test"]},
        )

        request = route.calls.last.request
        body = json.loads(request.content)
        assert body["metadata"] == {"source": "test-agent", "tags": ["test"]}


class TestErrorHandling:
    """Test API error handling."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        c = SurfaceDocs(api_key="sd_test_abc123")
        yield c
        c.close()

    @respx.mock
    def test_401_raises_authentication_error(self, client):
        """401 response should raise AuthenticationError."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                401,
                json={"error": {"code": "unauthorized", "message": "Invalid API key"}},
            )
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.save_raw(title="Test", blocks=[{"type": "paragraph", "content": "x"}])
        assert "Authentication failed" in str(exc_info.value)

    @respx.mock
    def test_403_raises_authentication_error(self, client):
        """403 response should raise AuthenticationError."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                403,
                json={"error": {"code": "forbidden", "message": "Access denied"}},
            )
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.save_raw(title="Test", blocks=[{"type": "paragraph", "content": "x"}])
        assert "Access denied" in str(exc_info.value)

    @respx.mock
    def test_404_raises_folder_not_found_error(self, client):
        """404 response should raise FolderNotFoundError."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                404,
                json={"error": {"code": "not_found", "message": "Folder not found"}},
            )
        )
        with pytest.raises(FolderNotFoundError) as exc_info:
            client.save_raw(
                title="Test",
                blocks=[{"type": "paragraph", "content": "x"}],
                folder_id="nonexistent",
            )
        assert "Folder not found" in str(exc_info.value)

    @respx.mock
    def test_422_raises_validation_error(self, client):
        """422 response should raise ValidationError."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                422,
                json={"error": {"code": "validation_error", "message": "Invalid block type"}},
            )
        )
        with pytest.raises(ValidationError) as exc_info:
            client.save_raw(title="Test", blocks=[{"type": "invalid", "content": "x"}])
        assert "Validation error" in str(exc_info.value)

    @respx.mock
    def test_500_raises_surfacedocs_error(self, client):
        """500 response should raise SurfaceDocsError."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(
                500,
                json={"error": {"code": "internal_error", "message": "Server error"}},
            )
        )
        with pytest.raises(SurfaceDocsError) as exc_info:
            client.save_raw(title="Test", blocks=[{"type": "paragraph", "content": "x"}])
        assert "API error (500)" in str(exc_info.value)

    @respx.mock
    def test_non_json_error_response(self, client):
        """Should handle non-JSON error responses."""
        respx.post("https://ingress.dev.surfacedocs.dev/v1/documents").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(SurfaceDocsError) as exc_info:
            client.save_raw(title="Test", blocks=[{"type": "paragraph", "content": "x"}])
        assert "Internal Server Error" in str(exc_info.value)


class TestClientImports:
    """Test client import paths."""

    def test_import_surfacedocs_from_package(self):
        """SurfaceDocs should be importable from main package."""
        from surfacedocs import SurfaceDocs as PkgClient
        assert PkgClient is not None

    def test_import_surfacedocs_from_module(self):
        """SurfaceDocs should be importable from client module."""
        assert DirectSurfaceDocs is not None

    def test_surfacedocs_imports_are_same_class(self):
        """Both SurfaceDocs imports should reference the same class."""
        assert SurfaceDocs is DirectSurfaceDocs

    def test_import_save_result_from_package(self):
        """SaveResult should be importable from main package."""
        from surfacedocs import SaveResult as PkgResult
        assert PkgResult is not None

    def test_import_save_result_from_module(self):
        """SaveResult should be importable from client module."""
        assert DirectSaveResult is not None

    def test_save_result_imports_are_same_class(self):
        """Both SaveResult imports should reference the same class."""
        assert SaveResult is DirectSaveResult


class TestClientDocstring:
    """Test client documentation."""

    def test_client_has_docstring(self):
        """SurfaceDocs class should have a docstring."""
        assert SurfaceDocs.__doc__ is not None

    def test_init_has_docstring(self):
        """__init__ should have a docstring."""
        assert SurfaceDocs.__init__.__doc__ is not None

    def test_save_has_docstring(self):
        """save() should have a docstring."""
        assert SurfaceDocs.save.__doc__ is not None

    def test_save_raw_has_docstring(self):
        """save_raw() should have a docstring."""
        assert SurfaceDocs.save_raw.__doc__ is not None

    def test_init_has_signature(self):
        """__init__ should have type annotations."""
        import inspect
        sig = inspect.signature(SurfaceDocs.__init__)
        params = list(sig.parameters.keys())
        assert "api_key" in params
        assert "base_url" in params
