# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for pytest_jux package initialization."""

import pytest_jux


class TestPackageInit:
    """Tests for package-level attributes and imports."""

    def test_version_defined(self) -> None:
        """Should have __version__ defined."""
        assert hasattr(pytest_jux, "__version__")
        assert isinstance(pytest_jux.__version__, str)
        assert len(pytest_jux.__version__) > 0

    def test_author_defined(self) -> None:
        """Should have __author__ defined."""
        assert hasattr(pytest_jux, "__author__")
        assert isinstance(pytest_jux.__author__, str)

    def test_email_defined(self) -> None:
        """Should have __email__ defined."""
        assert hasattr(pytest_jux, "__email__")
        assert isinstance(pytest_jux.__email__, str)
        assert "@" in pytest_jux.__email__

    def test_all_exports(self) -> None:
        """Should define __all__ with expected exports."""
        assert hasattr(pytest_jux, "__all__")
        assert isinstance(pytest_jux.__all__, list)
        assert "__version__" in pytest_jux.__all__

    def test_pytest_hooks_exported(self) -> None:
        """Should export pytest hooks when available."""
        # If plugin module is available, hooks should be exported
        if "pytest_addoption" in pytest_jux.__all__:
            assert hasattr(pytest_jux, "pytest_addoption")
            assert hasattr(pytest_jux, "pytest_configure")
