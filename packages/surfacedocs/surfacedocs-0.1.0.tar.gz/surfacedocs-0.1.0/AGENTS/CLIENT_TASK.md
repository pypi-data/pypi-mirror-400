# Task: HTTP Client Implementation

## Status: COMPLETE

## Objective

Implement the `SurfaceDocs` client class that saves documents to the ingress API.

## Context

- SETUP_TASK, SCHEMA_TASK, PROMPT_TASK complete
- Client uses httpx for HTTP requests
- Must call `POST /v1/documents` on ingress-api
- Reference: `plans/python-sdk-spec.md`, `services/ingress-api/src/main.py`

---

## Deliverable

Update `src/surfacedocs/client.py` with the complete `SurfaceDocs` class.

---

## API Endpoint

```
POST /v1/documents
Host: ingress.surfacedocs.dev (prod) or ingress.dev.surfacedocs.dev (dev)
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "title": "Document title",
  "folder_id": "optional_folder_id",
  "content_type": "markdown",
  "metadata": {"source": "agent-name"},
  "blocks": [...]
}

Response 201:
{
  "id": "doc_abc123",
  "url": "https://app.surfacedocs.dev/d/doc_abc123",
  "folder_id": "folder_xyz",
  "title": "Document title",
  "block_count": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Implementation

```python
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx

from surfacedocs.exceptions import (
    AuthenticationError,
    FolderNotFoundError,
    SurfaceDocsError,
    ValidationError,
)


@dataclass
class SaveResult:
    """Result from saving a document."""
    id: str
    url: str
    folder_id: str


class SurfaceDocs:
    """SurfaceDocs API client."""

    PROD_URL = "https://ingress.surfacedocs.dev"
    DEV_URL = "https://ingress.dev.surfacedocs.dev"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize the SurfaceDocs client.

        Args:
            api_key: API key (sd_live_xxx or sd_test_xxx).
                     Falls back to SURFACEDOCS_API_KEY env var.
            base_url: Override API URL. Auto-detected from key prefix if not set.
        """
        self.api_key = api_key or os.environ.get("SURFACEDOCS_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required. Pass api_key or set SURFACEDOCS_API_KEY.")

        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = self._detect_base_url(self.api_key)

        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _detect_base_url(self, api_key: str) -> str:
        """Detect base URL from API key prefix."""
        if api_key.startswith("sd_test_"):
            return self.DEV_URL
        return self.PROD_URL

    def save(
        self,
        content: str | dict[str, Any],
        folder_id: str | None = None,
    ) -> SaveResult:
        """
        Save a document from LLM output.

        Args:
            content: JSON string or dict from LLM response
            folder_id: Target folder (defaults to user's root folder)

        Returns:
            SaveResult with document ID and URL
        """
        # Parse content if string
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {e}")
        else:
            data = content

        # Extract fields
        title = data.get("title")
        blocks = data.get("blocks")
        metadata = data.get("metadata")

        if not title:
            raise ValidationError("Document must have a title")
        if not blocks:
            raise ValidationError("Document must have blocks")

        return self.save_raw(
            title=title,
            blocks=blocks,
            folder_id=folder_id,
            metadata=metadata,
        )

    def save_raw(
        self,
        title: str,
        blocks: list[dict[str, Any]],
        folder_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SaveResult:
        """
        Save a document with explicit parameters.

        Args:
            title: Document title
            blocks: List of block dicts
            folder_id: Target folder (defaults to user's root folder)
            metadata: Optional metadata dict

        Returns:
            SaveResult with document ID and URL
        """
        payload: dict[str, Any] = {
            "title": title,
            "blocks": blocks,
            "content_type": "markdown",
        }

        if folder_id:
            payload["folder_id"] = folder_id
        if metadata:
            payload["metadata"] = metadata

        response = self._client.post("/v1/documents", json=payload)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> SaveResult:
        """Handle API response and map errors."""
        if response.status_code == 201:
            data = response.json()
            return SaveResult(
                id=data["id"],
                url=data["url"],
                folder_id=data["folder_id"],
            )

        # Error handling
        try:
            error_data = response.json()
            detail = error_data.get("detail", str(error_data))
        except Exception:
            detail = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {detail}")
        elif response.status_code == 403:
            raise AuthenticationError(f"Access denied: {detail}")
        elif response.status_code == 404:
            raise FolderNotFoundError(f"Folder not found: {detail}")
        elif response.status_code == 422:
            raise ValidationError(f"Validation error: {detail}")
        else:
            raise SurfaceDocsError(f"API error ({response.status_code}): {detail}")

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> SurfaceDocs:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
```

---

## Verification

```python
from surfacedocs import SurfaceDocs, SurfaceDocsError

# Should raise without API key
try:
    client = SurfaceDocs()
except SurfaceDocsError:
    print("Correctly raised error without API key")

# Should detect dev URL
import os
os.environ["SURFACEDOCS_API_KEY"] = "sd_test_fake"
client = SurfaceDocs()
assert client.base_url == "https://ingress.dev.surfacedocs.dev"

# Should detect prod URL
client = SurfaceDocs(api_key="sd_live_fake")
assert client.base_url == "https://ingress.surfacedocs.dev"

# Context manager should work
with SurfaceDocs(api_key="sd_test_fake") as client:
    assert client.api_key == "sd_test_fake"
```

---

## Definition of Done

- [x] `SurfaceDocs` class implemented in `client.py`
- [x] `SaveResult` dataclass implemented
- [x] `save()` method accepts string or dict
- [x] `save_raw()` method accepts explicit params
- [x] API key from constructor or env var
- [x] Base URL auto-detected from key prefix
- [x] Error responses mapped to exception types
- [x] Context manager support (`with` statement)
- [x] Import works: `from surfacedocs import SurfaceDocs`
