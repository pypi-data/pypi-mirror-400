# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for XML canonicalization and hashing."""

from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.canonicalizer import (
    canonicalize_xml,
    compute_canonical_hash,
    load_xml,
)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def simple_xml(fixtures_dir: Path) -> Path:
    """Return path to simple JUnit XML fixture."""
    return fixtures_dir / "junit_xml" / "simple.xml"


@pytest.fixture
def passing_xml(fixtures_dir: Path) -> Path:
    """Return path to passing tests JUnit XML fixture."""
    return fixtures_dir / "junit_xml" / "passing.xml"


@pytest.fixture
def failing_xml(fixtures_dir: Path) -> Path:
    """Return path to failing test JUnit XML fixture."""
    return fixtures_dir / "junit_xml" / "failing.xml"


@pytest.fixture
def namespaced_xml(fixtures_dir: Path) -> Path:
    """Return path to namespaced JUnit XML fixture."""
    return fixtures_dir / "junit_xml" / "namespaced.xml"


class TestLoadXML:
    """Tests for XML loading functionality."""

    def test_load_xml_from_file(self, simple_xml: Path) -> None:
        """Test loading XML from file path."""
        tree = load_xml(simple_xml)
        assert tree is not None
        assert isinstance(tree, etree._Element)
        assert tree.tag == "testsuites"

    def test_load_xml_from_string(self) -> None:
        """Test loading XML from string."""
        xml_string = '<?xml version="1.0"?><root><child>test</child></root>'
        tree = load_xml(xml_string)
        assert tree is not None
        assert tree.tag == "root"
        assert tree.find("child").text == "test"

    def test_load_xml_from_bytes(self) -> None:
        """Test loading XML from bytes."""
        xml_bytes = b'<?xml version="1.0"?><root><child>test</child></root>'
        tree = load_xml(xml_bytes)
        assert tree is not None
        assert tree.tag == "root"

    def test_load_xml_invalid(self) -> None:
        """Test loading invalid XML raises exception."""
        with pytest.raises(etree.XMLSyntaxError):
            load_xml("<invalid>xml<")

    def test_load_xml_nonexistent_file(self) -> None:
        """Test loading nonexistent file raises exception."""
        with pytest.raises(FileNotFoundError):
            load_xml(Path("/nonexistent/file.xml"))


class TestCanonicalizeXML:
    """Tests for XML canonicalization functionality."""

    def test_canonicalize_simple(self, simple_xml: Path) -> None:
        """Test canonicalization of simple XML."""
        tree = load_xml(simple_xml)
        canonical = canonicalize_xml(tree)

        assert canonical is not None
        assert isinstance(canonical, bytes)
        assert b"<testsuites>" in canonical
        assert b"<testsuite" in canonical

    def test_canonicalize_with_namespaces(self, namespaced_xml: Path) -> None:
        """Test canonicalization preserves namespaces correctly."""
        tree = load_xml(namespaced_xml)
        canonical = canonicalize_xml(tree)

        assert canonical is not None
        # Canonical form should include namespace declarations
        assert b"xmlns=" in canonical or b"http://junit.org/junit4" in canonical

    def test_canonicalize_whitespace_normalization(self) -> None:
        """Test that C14N preserves significant whitespace correctly.

        Note: C14N preserves whitespace between elements (significant whitespace).
        Different whitespace produces different canonical forms, which is correct
        per the C14N specification.
        """
        xml1 = """<root>
        <child>value</child>
        </root>"""

        xml2 = "<root><child>value</child></root>"

        tree1 = load_xml(xml1)
        tree2 = load_xml(xml2)

        canonical1 = canonicalize_xml(tree1)
        canonical2 = canonicalize_xml(tree2)

        # C14N preserves whitespace, so these will be different
        assert canonical1 != canonical2

        # But canonicalizing the same XML twice gives same result
        assert canonical1 == canonicalize_xml(load_xml(xml1))
        assert canonical2 == canonicalize_xml(load_xml(xml2))

    def test_canonicalize_attribute_order(self) -> None:
        """Test that attribute order is normalized in canonical form."""
        xml1 = '<root attr1="a" attr2="b" attr3="c"/>'
        xml2 = '<root attr3="c" attr1="a" attr2="b"/>'
        xml3 = '<root attr2="b" attr3="c" attr1="a"/>'

        tree1 = load_xml(xml1)
        tree2 = load_xml(xml2)
        tree3 = load_xml(xml3)

        canonical1 = canonicalize_xml(tree1)
        canonical2 = canonicalize_xml(tree2)
        canonical3 = canonicalize_xml(tree3)

        # Canonical forms should be identical despite attribute order
        assert canonical1 == canonical2 == canonical3

    def test_canonicalize_comments_excluded(self) -> None:
        """Test that comments are excluded from canonical form by default."""
        xml_with_comment = (
            """<?xml version="1.0"?><root><!-- comment --><child>value</child></root>"""
        )
        xml_without_comment = (
            """<?xml version="1.0"?><root><child>value</child></root>"""
        )

        tree1 = load_xml(xml_with_comment)
        tree2 = load_xml(xml_without_comment)

        canonical1 = canonicalize_xml(tree1, with_comments=False)
        canonical2 = canonicalize_xml(tree2, with_comments=False)

        # Canonical forms should be identical (comments excluded, no whitespace differences)
        assert canonical1 == canonical2
        assert b"<!--" not in canonical1

        # With comments=True, comment should be preserved
        canonical_with_comments = canonicalize_xml(tree1, with_comments=True)
        assert b"<!--" in canonical_with_comments

    def test_canonicalize_xml_declaration_excluded(self) -> None:
        """Test that XML declaration is excluded from canonical form."""
        tree = load_xml('<?xml version="1.0" encoding="UTF-8"?><root/>')
        canonical = canonicalize_xml(tree)

        # XML declaration should not be in canonical form
        assert not canonical.startswith(b"<?xml")

    def test_canonicalize_with_exclusive_c14n(self) -> None:
        """Test exclusive canonicalization option."""
        tree = load_xml("<root><child>value</child></root>")

        canonical_inclusive = canonicalize_xml(tree, exclusive=False)
        canonical_exclusive = canonicalize_xml(tree, exclusive=True)

        # Both should produce valid output (may differ in namespace handling)
        assert canonical_inclusive is not None
        assert canonical_exclusive is not None


class TestComputeCanonicalHash:
    """Tests for canonical hash computation."""

    def test_compute_hash_simple(self, simple_xml: Path) -> None:
        """Test hash computation for simple XML."""
        tree = load_xml(simple_xml)
        hash_value = compute_canonical_hash(tree)

        assert hash_value is not None
        assert isinstance(hash_value, str)
        # SHA-256 produces 64 hex characters
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_compute_hash_deterministic(self, simple_xml: Path) -> None:
        """Test that hash computation is deterministic."""
        tree = load_xml(simple_xml)

        hash1 = compute_canonical_hash(tree)
        hash2 = compute_canonical_hash(tree)

        assert hash1 == hash2

    def test_compute_hash_different_content(
        self, simple_xml: Path, passing_xml: Path
    ) -> None:
        """Test that different XML produces different hashes."""
        tree1 = load_xml(simple_xml)
        tree2 = load_xml(passing_xml)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 != hash2

    def test_compute_hash_identical_content(self) -> None:
        """Test that identical XML produces identical hashes.

        Note: C14N preserves whitespace, so XML must be truly identical
        (not just semantically equivalent) to produce the same hash.
        """
        xml1 = load_xml("<root><child>value</child></root>")
        xml2 = load_xml("<root><child>value</child></root>")  # Exact copy

        hash1 = compute_canonical_hash(xml1)
        hash2 = compute_canonical_hash(xml2)

        # Hashes should be identical for exact copies
        assert hash1 == hash2

        # Different whitespace produces different hashes (C14N preserves whitespace)
        xml3 = load_xml("<root>  <child>value</child>  </root>")
        hash3 = compute_canonical_hash(xml3)
        assert hash1 != hash3

    def test_compute_hash_algorithm_sha256(self) -> None:
        """Test that SHA-256 algorithm is used."""
        tree = load_xml("<root>test</root>")
        hash_value = compute_canonical_hash(tree, algorithm="sha256")

        # SHA-256 produces 64 hex characters
        assert len(hash_value) == 64

    def test_compute_hash_with_fixtures(
        self, simple_xml: Path, passing_xml: Path, failing_xml: Path
    ) -> None:
        """Test hash computation with all test fixtures."""
        tree_simple = load_xml(simple_xml)
        tree_passing = load_xml(passing_xml)
        tree_failing = load_xml(failing_xml)

        hash_simple = compute_canonical_hash(tree_simple)
        hash_passing = compute_canonical_hash(tree_passing)
        hash_failing = compute_canonical_hash(tree_failing)

        # All hashes should be unique
        assert hash_simple != hash_passing
        assert hash_simple != hash_failing
        assert hash_passing != hash_failing

        # All should be valid SHA-256 hashes
        for hash_val in [hash_simple, hash_passing, hash_failing]:
            assert len(hash_val) == 64
            assert all(c in "0123456789abcdef" for c in hash_val)


class TestDuplicateDetection:
    """Tests for duplicate detection using canonical hashes."""

    def test_detect_duplicate_reports(self) -> None:
        """Test that duplicate XML reports produce same hash."""
        xml_content = """<?xml version="1.0"?>
        <testsuites>
            <testsuite name="test" tests="1">
                <testcase name="test_one" time="0.001"/>
            </testsuite>
        </testsuites>"""

        # Load same content twice
        tree1 = load_xml(xml_content)
        tree2 = load_xml(xml_content)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        # Should detect as duplicate
        assert hash1 == hash2

    def test_detect_modified_report(self) -> None:
        """Test that modified XML reports produce different hash."""
        xml1 = """<testsuites>
            <testsuite name="test" tests="1" time="0.123">
                <testcase name="test_one" time="0.001"/>
            </testsuite>
        </testsuites>"""

        xml2 = """<testsuites>
            <testsuite name="test" tests="1" time="0.999">
                <testcase name="test_one" time="0.001"/>
            </testsuite>
        </testsuites>"""

        tree1 = load_xml(xml1)
        tree2 = load_xml(xml2)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        # Should detect as different (time attribute changed)
        assert hash1 != hash2


class TestErrorHandling:
    """Tests for error handling in canonicalization."""

    def test_canonicalize_invalid_tree_type(self) -> None:
        """Test that canonicalize_xml raises TypeError for non-Element input."""
        with pytest.raises(TypeError, match="Expected lxml Element"):
            canonicalize_xml("not an element")

    def test_compute_hash_unsupported_algorithm(self) -> None:
        """Test that unsupported hash algorithm raises ValueError."""
        tree = load_xml("<root/>")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            compute_canonical_hash(tree, algorithm="invalid_algorithm_xyz")

    def test_compute_hash_with_md5(self) -> None:
        """Test hash computation with MD5 algorithm."""
        tree = load_xml("<root>test</root>")
        hash_value = compute_canonical_hash(tree, algorithm="md5")

        # MD5 produces 32 hex characters
        assert len(hash_value) == 32
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_compute_hash_with_sha512(self) -> None:
        """Test hash computation with SHA-512 algorithm."""
        tree = load_xml("<root>test</root>")
        hash_value = compute_canonical_hash(tree, algorithm="sha512")

        # SHA-512 produces 128 hex characters
        assert len(hash_value) == 128
        assert all(c in "0123456789abcdef" for c in hash_value)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_xml(self) -> None:
        """Test handling of minimal empty XML."""
        tree = load_xml("<root/>")
        canonical = canonicalize_xml(tree)
        hash_value = compute_canonical_hash(tree)

        assert canonical is not None
        assert hash_value is not None

    def test_deeply_nested_xml(self) -> None:
        """Test handling of deeply nested XML structures."""
        xml = "<root>"
        for i in range(50):
            xml += f"<level{i}>"
        xml += "<leaf>value</leaf>"
        for i in range(49, -1, -1):
            xml += f"</level{i}>"
        xml += "</root>"

        tree = load_xml(xml)
        canonical = canonicalize_xml(tree)
        hash_value = compute_canonical_hash(tree)

        assert canonical is not None
        assert hash_value is not None

    def test_large_xml_file(self) -> None:
        """Test handling of large XML content."""
        # Generate large XML with many test cases
        xml = '<?xml version="1.0"?><testsuites><testsuite name="large" tests="1000">'
        for i in range(1000):
            xml += f'<testcase name="test_{i}" time="0.001"/>'
        xml += "</testsuite></testsuites>"

        tree = load_xml(xml)
        canonical = canonicalize_xml(tree)
        hash_value = compute_canonical_hash(tree)

        assert canonical is not None
        assert hash_value is not None
        assert len(hash_value) == 64

    def test_special_characters_in_content(self) -> None:
        """Test handling of special characters in XML content."""
        xml = """<root>
            <child attr="&lt;&gt;&amp;&quot;&apos;">
                Text with &lt;special&gt; &amp; characters
            </child>
        </root>"""

        tree = load_xml(xml)
        canonical = canonicalize_xml(tree)
        hash_value = compute_canonical_hash(tree)

        assert canonical is not None
        assert hash_value is not None

    def test_unicode_content(self) -> None:
        """Test handling of Unicode characters in XML."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <child>Hello 世界 🌍 Здравствуй мир</child>
        </root>"""

        tree = load_xml(xml)
        canonical = canonicalize_xml(tree)
        hash_value = compute_canonical_hash(tree)

        assert canonical is not None
        assert hash_value is not None
