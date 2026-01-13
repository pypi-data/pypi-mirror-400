"""Pytest fixtures for SurfaceDocs SDK tests."""

import pytest
import respx
from httpx import Response


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "sd_test_abc123"


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
