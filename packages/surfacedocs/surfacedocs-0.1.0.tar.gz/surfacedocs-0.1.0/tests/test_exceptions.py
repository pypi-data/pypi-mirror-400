"""Tests for SDK exceptions."""

import pytest

from surfacedocs import (
    SurfaceDocsError,
    AuthenticationError,
    ValidationError,
    FolderNotFoundError,
)
from surfacedocs.exceptions import (
    SurfaceDocsError as DirectSurfaceDocsError,
    AuthenticationError as DirectAuthenticationError,
    ValidationError as DirectValidationError,
    FolderNotFoundError as DirectFolderNotFoundError,
)


class TestSurfaceDocsError:
    """Test the base SurfaceDocsError exception."""

    def test_inherits_from_exception(self):
        """SurfaceDocsError should inherit from Exception."""
        assert issubclass(SurfaceDocsError, Exception)

    def test_can_be_raised(self):
        """SurfaceDocsError should be raisable."""
        with pytest.raises(SurfaceDocsError):
            raise SurfaceDocsError("test error")

    def test_message_is_preserved(self):
        """Error message should be preserved."""
        try:
            raise SurfaceDocsError("custom message")
        except SurfaceDocsError as e:
            assert str(e) == "custom message"

    def test_can_catch_as_exception(self):
        """Should be catchable as generic Exception."""
        with pytest.raises(Exception):
            raise SurfaceDocsError("test")


class TestAuthenticationError:
    """Test the AuthenticationError exception."""

    def test_inherits_from_surfacedocs_error(self):
        """AuthenticationError should inherit from SurfaceDocsError."""
        assert issubclass(AuthenticationError, SurfaceDocsError)

    def test_can_be_raised(self):
        """AuthenticationError should be raisable."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("invalid key")

    def test_catchable_as_surfacedocs_error(self):
        """Should be catchable as SurfaceDocsError."""
        with pytest.raises(SurfaceDocsError):
            raise AuthenticationError("invalid key")

    def test_message_is_preserved(self):
        """Error message should be preserved."""
        try:
            raise AuthenticationError("bad api key")
        except AuthenticationError as e:
            assert str(e) == "bad api key"


class TestValidationError:
    """Test the ValidationError exception."""

    def test_inherits_from_surfacedocs_error(self):
        """ValidationError should inherit from SurfaceDocsError."""
        assert issubclass(ValidationError, SurfaceDocsError)

    def test_can_be_raised(self):
        """ValidationError should be raisable."""
        with pytest.raises(ValidationError):
            raise ValidationError("invalid document")

    def test_catchable_as_surfacedocs_error(self):
        """Should be catchable as SurfaceDocsError."""
        with pytest.raises(SurfaceDocsError):
            raise ValidationError("invalid document")

    def test_message_is_preserved(self):
        """Error message should be preserved."""
        try:
            raise ValidationError("missing title")
        except ValidationError as e:
            assert str(e) == "missing title"


class TestFolderNotFoundError:
    """Test the FolderNotFoundError exception."""

    def test_inherits_from_surfacedocs_error(self):
        """FolderNotFoundError should inherit from SurfaceDocsError."""
        assert issubclass(FolderNotFoundError, SurfaceDocsError)

    def test_can_be_raised(self):
        """FolderNotFoundError should be raisable."""
        with pytest.raises(FolderNotFoundError):
            raise FolderNotFoundError("folder not found")

    def test_catchable_as_surfacedocs_error(self):
        """Should be catchable as SurfaceDocsError."""
        with pytest.raises(SurfaceDocsError):
            raise FolderNotFoundError("folder not found")

    def test_message_is_preserved(self):
        """Error message should be preserved."""
        try:
            raise FolderNotFoundError("folder_123 not found")
        except FolderNotFoundError as e:
            assert str(e) == "folder_123 not found"


class TestExceptionImports:
    """Test that exceptions can be imported correctly."""

    def test_import_surfacedocs_error_from_package(self):
        """SurfaceDocsError should be importable from main package."""
        assert SurfaceDocsError is DirectSurfaceDocsError

    def test_import_authentication_error_from_package(self):
        """AuthenticationError should be importable from main package."""
        assert AuthenticationError is DirectAuthenticationError

    def test_import_validation_error_from_package(self):
        """ValidationError should be importable from main package."""
        assert ValidationError is DirectValidationError

    def test_import_folder_not_found_error_from_package(self):
        """FolderNotFoundError should be importable from main package."""
        assert FolderNotFoundError is DirectFolderNotFoundError


class TestExceptionHierarchy:
    """Test the exception hierarchy for proper catch ordering."""

    def test_catch_all_with_base_error(self):
        """All SDK errors should be catchable with SurfaceDocsError."""
        errors = [
            AuthenticationError("auth"),
            ValidationError("validation"),
            FolderNotFoundError("folder"),
        ]
        for error in errors:
            with pytest.raises(SurfaceDocsError):
                raise error

    def test_specific_catch_before_generic(self):
        """Specific exceptions should be catchable before generic."""
        caught_type = None
        try:
            raise AuthenticationError("test")
        except AuthenticationError:
            caught_type = "specific"
        except SurfaceDocsError:
            caught_type = "generic"
        assert caught_type == "specific"
