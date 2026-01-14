# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""XML canonicalization and hashing for JUnit XML reports.

This module provides functionality to canonicalize JUnit XML reports using
the XML Canonicalization (C14N) algorithm and compute cryptographic hashes
of the canonical form for duplicate detection.
"""

import hashlib
from pathlib import Path
from typing import cast  # pragma: no cover

from lxml import etree


def load_xml(source: str | bytes | Path) -> etree._Element:
    """Load XML from various sources.

    Args:
        source: XML source - can be:
            - Path to XML file
            - XML string
            - XML bytes

    Returns:
        Parsed XML element tree root

    Raises:
        FileNotFoundError: If file path doesn't exist
        etree.XMLSyntaxError: If XML is malformed
    """
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"XML file not found: {source}")
        with open(source, "rb") as f:
            return etree.parse(f).getroot()

    if isinstance(source, str):
        source = source.encode("utf-8")

    return etree.fromstring(source)


def canonicalize_xml(
    tree: etree._Element,
    exclusive: bool = False,
    with_comments: bool = False,
) -> bytes:
    """Canonicalize XML using C14N algorithm.

    Converts XML to canonical form (C14N) which normalizes:
    - Whitespace
    - Attribute order
    - Namespace declarations
    - Comments (excluded by default)

    This ensures that semantically equivalent XML produces identical
    canonical output, enabling reliable duplicate detection via hashing.

    Args:
        tree: XML element tree to canonicalize
        exclusive: Use exclusive canonicalization (default: False)
        with_comments: Include comments in canonical form (default: False)

    Returns:
        Canonical XML as bytes

    Raises:
        TypeError: If tree is not an lxml element
    """
    if not isinstance(tree, etree._Element):
        raise TypeError(f"Expected lxml Element, got {type(tree)}")

    # etree.tostring with method="c14n" always returns bytes
    return cast(
        bytes,
        etree.tostring(
            tree,
            method="c14n",
            exclusive=exclusive,
            with_comments=with_comments,
        ),
    )


def compute_canonical_hash(
    tree: etree._Element,
    algorithm: str = "sha256",
) -> str:
    """Compute cryptographic hash of canonical XML.

    Canonicalizes the XML and computes a cryptographic hash of the
    canonical form. This hash can be used for:
    - Duplicate detection
    - Content verification
    - Change detection

    Args:
        tree: XML element tree to hash
        algorithm: Hash algorithm to use (default: "sha256")

    Returns:
        Hexadecimal hash digest string

    Raises:
        ValueError: If hash algorithm is not supported
        TypeError: If tree is not an lxml element
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    canonical = canonicalize_xml(tree)
    hasher = hashlib.new(algorithm)
    hasher.update(canonical)

    return hasher.hexdigest()
