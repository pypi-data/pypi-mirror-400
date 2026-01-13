"""Tests for package initialization and exports."""

import pytest


class TestPackageImports:
    """Test that all public API is importable from the package."""

    def test_import_document_schema(self):
        """DOCUMENT_SCHEMA should be importable."""
        from surfacedocs import DOCUMENT_SCHEMA
        assert DOCUMENT_SCHEMA is not None

    def test_import_system_prompt(self):
        """SYSTEM_PROMPT should be importable."""
        from surfacedocs import SYSTEM_PROMPT
        assert SYSTEM_PROMPT is not None

    def test_import_surfacedocs_client(self):
        """SurfaceDocs client should be importable."""
        from surfacedocs import SurfaceDocs
        assert SurfaceDocs is not None

    def test_import_save_result(self):
        """SaveResult should be importable."""
        from surfacedocs import SaveResult
        assert SaveResult is not None

    def test_import_surfacedocs_error(self):
        """SurfaceDocsError should be importable."""
        from surfacedocs import SurfaceDocsError
        assert SurfaceDocsError is not None

    def test_import_authentication_error(self):
        """AuthenticationError should be importable."""
        from surfacedocs import AuthenticationError
        assert AuthenticationError is not None

    def test_import_validation_error(self):
        """ValidationError should be importable."""
        from surfacedocs import ValidationError
        assert ValidationError is not None

    def test_import_folder_not_found_error(self):
        """FolderNotFoundError should be importable."""
        from surfacedocs import FolderNotFoundError
        assert FolderNotFoundError is not None

    def test_import_version(self):
        """__version__ should be importable."""
        from surfacedocs import __version__
        assert __version__ is not None


class TestVersion:
    """Test package version."""

    def test_version_is_string(self):
        """Version should be a string."""
        from surfacedocs import __version__
        assert isinstance(__version__, str)

    def test_version_format(self):
        """Version should follow semver format."""
        from surfacedocs import __version__
        parts = __version__.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_version_value(self):
        """Version should be 0.1.0."""
        from surfacedocs import __version__
        assert __version__ == "0.1.0"


class TestAllExports:
    """Test the __all__ exports list."""

    def test_all_is_defined(self):
        """__all__ should be defined."""
        import surfacedocs
        assert hasattr(surfacedocs, "__all__")

    def test_all_is_list(self):
        """__all__ should be a list."""
        import surfacedocs
        assert isinstance(surfacedocs.__all__, list)

    def test_all_contains_document_schema(self):
        """__all__ should include DOCUMENT_SCHEMA."""
        import surfacedocs
        assert "DOCUMENT_SCHEMA" in surfacedocs.__all__

    def test_all_contains_system_prompt(self):
        """__all__ should include SYSTEM_PROMPT."""
        import surfacedocs
        assert "SYSTEM_PROMPT" in surfacedocs.__all__

    def test_all_contains_surfacedocs(self):
        """__all__ should include SurfaceDocs."""
        import surfacedocs
        assert "SurfaceDocs" in surfacedocs.__all__

    def test_all_contains_save_result(self):
        """__all__ should include SaveResult."""
        import surfacedocs
        assert "SaveResult" in surfacedocs.__all__

    def test_all_contains_exceptions(self):
        """__all__ should include all exceptions."""
        import surfacedocs
        assert "SurfaceDocsError" in surfacedocs.__all__
        assert "AuthenticationError" in surfacedocs.__all__
        assert "ValidationError" in surfacedocs.__all__
        assert "FolderNotFoundError" in surfacedocs.__all__

    def test_all_contains_version(self):
        """__all__ should include __version__."""
        import surfacedocs
        assert "__version__" in surfacedocs.__all__

    def test_all_exports_are_accessible(self):
        """All items in __all__ should be accessible."""
        import surfacedocs
        for name in surfacedocs.__all__:
            assert hasattr(surfacedocs, name), f"{name} not accessible"

    def test_all_has_expected_count(self):
        """__all__ should have exactly 9 exports."""
        import surfacedocs
        assert len(surfacedocs.__all__) == 9


class TestModuleDocstring:
    """Test module documentation."""

    def test_module_has_docstring(self):
        """Module should have a docstring."""
        import surfacedocs
        assert surfacedocs.__doc__ is not None

    def test_docstring_mentions_surfacedocs(self):
        """Docstring should mention SurfaceDocs."""
        import surfacedocs
        assert "SurfaceDocs" in surfacedocs.__doc__
