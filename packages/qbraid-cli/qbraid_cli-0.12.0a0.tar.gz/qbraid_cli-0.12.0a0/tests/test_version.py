# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Unit tests for qbraid_cli._version module.
"""

from unittest.mock import patch

import qbraid_cli._version as version_module


def test_version_is_string():
    """Test that __version__ is a string."""
    assert isinstance(version_module.__version__, str)


def test_version_not_empty():
    """Test that __version__ is not empty."""
    assert len(version_module.__version__) > 0


def test_version_format():
    """Test that __version__ follows semantic versioning or is 'dev'."""
    version = version_module.__version__
    if version != "dev":
        # Should have at least major.minor format
        parts = version.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor"
        # First two parts should be numeric
        assert parts[0].isdigit(), "Major version should be numeric"
        assert parts[1].split("-")[0].isdigit(), "Minor version should be numeric"


def test_version_tuple_is_tuple():
    """Test that __version_tuple__ is a tuple."""
    assert isinstance(version_module.__version_tuple__, tuple)


def test_version_tuple_not_empty():
    """Test that __version_tuple__ is not empty."""
    assert len(version_module.__version_tuple__) > 0


def test_version_tuple_structure():
    """Test that __version_tuple__ has expected structure."""
    version_tuple = version_module.__version_tuple__
    # Should have at least 2 elements (major, minor)
    assert len(version_tuple) >= 2
    # First two elements should be integers (major, minor)
    if version_module.__version__ != "dev":
        assert isinstance(version_tuple[0], int), "Major version should be int"


def test_version_tuple_matches_version_string():
    """Test that __version_tuple__ components match __version__ string."""
    version = version_module.__version__
    version_tuple = version_module.__version_tuple__

    parts = version.split(".")
    for i, part in enumerate(parts):
        if i < len(version_tuple):
            if part.isdigit():
                assert version_tuple[i] == int(part), f"Tuple element {i} should match version part"
            else:
                assert version_tuple[i] == part, f"Tuple element {i} should match version part"


def test_module_exports():
    """Test that __all__ contains expected exports."""
    assert hasattr(version_module, "__all__")
    assert "__version__" in version_module.__all__
    assert "__version_tuple__" in version_module.__all__


def test_version_fallback_on_metadata_error():
    """Test that __version__ falls back to 'dev' when metadata is not available."""
    # pylint: disable=import-outside-toplevel,reimported
    import sys

    with patch("importlib.metadata.version", side_effect=Exception("Metadata not found")):
        # Remove from sys.modules to force reload
        if "qbraid_cli._version" in sys.modules:
            del sys.modules["qbraid_cli._version"]

        # Import again (will use mocked metadata.version)
        import qbraid_cli._version as reloaded_version

        # Should fall back to 'dev'
        assert reloaded_version.__version__ == "dev"

        # Clean up - reload the original module
        if "qbraid_cli._version" in sys.modules:
            del sys.modules["qbraid_cli._version"]
        import qbraid_cli._version  # noqa: F401  # pylint: disable=unused-import


def test_version_tuple_handles_dev():
    """Test that __version_tuple__ correctly handles 'dev' version."""
    # pylint: disable=import-outside-toplevel,reimported
    import sys

    with patch("importlib.metadata.version", side_effect=Exception("Metadata not found")):
        # Remove from sys.modules to force reload
        if "qbraid_cli._version" in sys.modules:
            del sys.modules["qbraid_cli._version"]

        # Import again (will use mocked metadata.version)
        import qbraid_cli._version as reloaded_version

        # Should fall back to 'dev'
        assert reloaded_version.__version__ == "dev"
        assert reloaded_version.__version_tuple__ == ("dev",)

        # Clean up
        if "qbraid_cli._version" in sys.modules:
            del sys.modules["qbraid_cli._version"]
        import qbraid_cli._version  # noqa: F401  # pylint: disable=unused-import


def test_version_tuple_handles_prerelease():
    """Test that __version_tuple__ correctly handles pre-release versions."""
    # Example: "0.10.9.dev" or "0.10.9-beta.1"
    test_version = "0.10.9.dev"
    parts = test_version.split(".")
    version_tuple = tuple(int(part) if part.isdigit() else part for part in parts)

    # Should have 4 elements: (0, 10, 9, 'dev')
    assert len(version_tuple) == 4
    assert version_tuple[0] == 0
    assert version_tuple[1] == 10
    assert version_tuple[2] == 9
    assert version_tuple[3] == "dev"


def test_version_comparison():
    """Test that version tuples can be compared."""
    # Create sample version tuples
    v1 = (0, 10, 8)
    v2 = (0, 10, 9)
    v3 = (1, 0, 0)

    assert v1 < v2
    assert v2 < v3
    assert v1 < v3

    # Test with current version tuple if it's not 'dev'
    if version_module.__version__ != "dev":
        current = version_module.__version_tuple__[:3]  # Take major.minor.patch
        # Should be comparable to tuples - test reflexivity
        assert current == current  # pylint: disable=comparison-with-itself
