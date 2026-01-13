"""SurfaceDocs Python SDK - Save LLM-generated documents."""

from surfacedocs.schema import DOCUMENT_SCHEMA, GEMINI_DOCUMENT_SCHEMA, OPENAI_DOCUMENT_SCHEMA
from surfacedocs.prompt import SYSTEM_PROMPT
from surfacedocs.client import SaveResult, SurfaceDocs
from surfacedocs.exceptions import (
    SurfaceDocsError,
    AuthenticationError,
    ValidationError,
    FolderNotFoundError,
)

__version__ = "0.1.0"

__all__ = [
    "DOCUMENT_SCHEMA",
    "GEMINI_DOCUMENT_SCHEMA",
    "OPENAI_DOCUMENT_SCHEMA",
    "SYSTEM_PROMPT",
    "SaveResult",
    "SurfaceDocs",
    "SurfaceDocsError",
    "AuthenticationError",
    "ValidationError",
    "FolderNotFoundError",
    "__version__",
]
