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
