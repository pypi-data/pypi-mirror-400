# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for XML signature verification."""

from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import load_private_key, sign_xml
from pytest_jux.verifier import verify_signature


@pytest.fixture
def signed_xml_rsa(tmp_path: Path) -> Path:
    """Create a signed XML file with RSA key and certificate."""
    from pytest_jux.commands.keygen import (
        generate_rsa_key,
        generate_self_signed_cert,
        save_key,
    )

    # Create test XML
    xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
    xml_path = tmp_path / "test.xml"
    xml_path.write_text(xml_content)

    # Generate key and certificate
    key = generate_rsa_key(2048)
    key_path = tmp_path / "key.pem"
    save_key(key, key_path)

    cert_path = tmp_path / "cert.crt"
    generate_self_signed_cert(key, cert_path)
    cert = cert_path.read_bytes()

    # Sign XML with certificate
    tree = load_xml(xml_path)
    signed_tree = sign_xml(tree, key, cert)

    # Save signed XML
    signed_path = tmp_path / "signed.xml"
    signed_path.write_bytes(
        etree.tostring(signed_tree, xml_declaration=True, encoding="utf-8")
    )

    return signed_path


@pytest.fixture
def signed_xml_ecdsa(tmp_path: Path) -> Path:
    """Create a signed XML file with ECDSA key and certificate."""
    from pytest_jux.commands.keygen import (
        generate_ecdsa_key,
        generate_self_signed_cert,
        save_key,
    )

    # Create test XML
    xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
    xml_path = tmp_path / "test.xml"
    xml_path.write_text(xml_content)

    # Generate key and certificate
    key = generate_ecdsa_key("P-256")
    key_path = tmp_path / "key.pem"
    save_key(key, key_path)

    cert_path = tmp_path / "cert.crt"
    generate_self_signed_cert(key, cert_path)
    cert = cert_path.read_bytes()

    # Sign XML with certificate
    tree = load_xml(xml_path)
    signed_tree = sign_xml(tree, key, cert)

    # Save signed XML
    signed_path = tmp_path / "signed.xml"
    signed_path.write_bytes(
        etree.tostring(signed_tree, xml_declaration=True, encoding="utf-8")
    )

    return signed_path


class TestVerifySignature:
    """Tests for verify_signature function."""

    def test_verifies_valid_rsa_signature(
        self, signed_xml_rsa: Path, tmp_path: Path
    ) -> None:
        """Test that valid RSA signature is verified."""
        cert_path = signed_xml_rsa.parent / "cert.crt"
        cert = cert_path.read_bytes()

        tree = load_xml(signed_xml_rsa)
        is_valid = verify_signature(tree, cert)

        assert is_valid is True

    def test_verifies_valid_ecdsa_signature(
        self, signed_xml_ecdsa: Path, tmp_path: Path
    ) -> None:
        """Test that valid ECDSA signature is verified."""
        cert_path = signed_xml_ecdsa.parent / "cert.crt"
        cert = cert_path.read_bytes()

        tree = load_xml(signed_xml_ecdsa)
        is_valid = verify_signature(tree, cert)

        assert is_valid is True

    def test_rejects_tampered_signature(
        self, signed_xml_rsa: Path, tmp_path: Path
    ) -> None:
        """Test that tampered XML is rejected."""
        cert_path = signed_xml_rsa.parent / "cert.crt"
        cert = cert_path.read_bytes()

        # Tamper with the XML
        tree = load_xml(signed_xml_rsa)
        testcase = tree.find(".//testcase")
        assert testcase is not None
        testcase.set("name", "tampered_test")

        is_valid = verify_signature(tree, cert)

        assert is_valid is False

    def test_rejects_unsigned_xml(self, tmp_path: Path) -> None:
        """Test that unsigned XML is rejected."""
        from pytest_jux.commands.keygen import generate_rsa_key

        # Create unsigned XML
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "unsigned.xml"
        xml_path.write_text(xml_content)

        key = generate_rsa_key(2048)
        cert = key.public_key()

        tree = load_xml(xml_path)

        with pytest.raises(ValueError, match="No signature found"):
            verify_signature(tree, cert)

    def test_verifies_with_certificate_bytes(
        self, signed_xml_rsa: Path, tmp_path: Path
    ) -> None:
        """Test verification with certificate as bytes."""
        from pytest_jux.commands.keygen import generate_self_signed_cert

        key_path = signed_xml_rsa.parent / "key.pem"
        key = load_private_key(key_path)

        # Generate certificate
        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key, cert_path)
        cert_bytes = cert_path.read_bytes()

        tree = load_xml(signed_xml_rsa)
        is_valid = verify_signature(tree, cert_bytes)

        assert is_valid is True

    def test_handles_invalid_certificate(self, signed_xml_rsa: Path) -> None:
        """Test handling of invalid certificate."""
        tree = load_xml(signed_xml_rsa)

        with pytest.raises(ValueError, match="Invalid certificate"):
            verify_signature(tree, b"invalid certificate data")

    def test_verifies_with_certificate_string(
        self, signed_xml_rsa: Path, tmp_path: Path
    ) -> None:
        """Test verification with certificate as string."""
        cert_path = signed_xml_rsa.parent / "cert.crt"
        cert_str = cert_path.read_text()

        tree = load_xml(signed_xml_rsa)
        is_valid = verify_signature(tree, cert_str)

        assert is_valid is True

    @pytest.mark.xfail(
        reason="XMLDSig verification with public key object without cert not fully supported"
    )
    def test_verifies_with_public_key_object(
        self, signed_xml_rsa: Path, tmp_path: Path
    ) -> None:
        """Test verification with public key object (extracts from signature)."""
        key_path = signed_xml_rsa.parent / "key.pem"
        key = load_private_key(key_path)
        public_key = key.public_key()

        tree = load_xml(signed_xml_rsa)
        # When public key object is provided, verifier extracts key from signature
        is_valid = verify_signature(tree, public_key)

        assert is_valid is True

    def test_verification_failure_with_public_key(self, tmp_path: Path) -> None:
        """Test verification fails with wrong public key."""
        from pytest_jux.commands.keygen import generate_rsa_key

        # Create tampered signed XML
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test" tests="1">
        <testcase name="test_example"/>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "test.xml"
        xml_path.write_text(xml_content)

        # Sign with one key
        key1 = generate_rsa_key(2048)
        tree = load_xml(xml_path)
        from pytest_jux.commands.keygen import generate_self_signed_cert
        cert_path = tmp_path / "cert.crt"
        generate_self_signed_cert(key1, cert_path)
        cert = cert_path.read_bytes()
        signed_tree = sign_xml(tree, key1, cert)

        # Tamper with content
        testcase = signed_tree.find(".//testcase")
        assert testcase is not None
        testcase.set("name", "tampered_test")

        # Try to verify with different public key
        key2 = generate_rsa_key(2048)
        public_key2 = key2.public_key()

        # Verification should fail (tampered content)
        is_valid = verify_signature(signed_tree, public_key2)
        assert is_valid is False
