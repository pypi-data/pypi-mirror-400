# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""
pytest-jux: A pytest plugin for signing and publishing JUnit XML test reports.

This plugin integrates with pytest to automatically:
1. Sign JUnit XML test reports using XML digital signatures (XMLDSig)
2. Calculate canonical hashes for duplicate detection
3. Publish signed reports to a Jux REST API backend
"""

__version__ = "0.3.0"
__author__ = "Georges Martin"
__email__ = "jrjsmrtn@gmail.com"

# Import plugin hooks when plugin module is available
try:  # pragma: no cover
    from pytest_jux.plugin import pytest_addoption, pytest_configure

    __all__ = ["pytest_addoption", "pytest_configure", "__version__"]
except ImportError:  # pragma: no cover
    # Plugin module not yet implemented
    __all__ = ["__version__"]
