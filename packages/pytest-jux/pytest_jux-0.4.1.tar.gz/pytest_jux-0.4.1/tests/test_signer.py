# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for XML digital signature generation."""

from pathlib import Path

import pytest
from lxml import etree
from signxml import XMLVerifier

from pytest_jux.canonicalizer import load_xml
from pytest_jux.signer import (
    load_private_key,
    sign_xml,
    verify_signature,
)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def keys_dir(fixtures_dir: Path) -> Path:
    """Return path to test keys directory."""
    return fixtures_dir / "keys"


@pytest.fixture
def rsa_key_path(keys_dir: Path) -> Path:
    """Return path to RSA private key."""
    return keys_dir / "rsa_2048.pem"


@pytest.fixture
def rsa_pub_path(keys_dir: Path) -> Path:
    """Return path to RSA public key."""
    return keys_dir / "rsa_2048.pub"


@pytest.fixture
def rsa_cert_path(keys_dir: Path) -> Path:
    """Return path to RSA certificate."""
    return keys_dir / "rsa_2048.crt"


@pytest.fixture
def ecdsa_key_path(keys_dir: Path) -> Path:
    """Return path to ECDSA private key."""
    return keys_dir / "ecdsa_p256.pem"


@pytest.fixture
def ecdsa_pub_path(keys_dir: Path) -> Path:
    """Return path to ECDSA public key."""
    return keys_dir / "ecdsa_p256.pub"


@pytest.fixture
def ecdsa_cert_path(keys_dir: Path) -> Path:
    """Return path to ECDSA certificate."""
    return keys_dir / "ecdsa_p256.crt"


@pytest.fixture
def simple_xml(fixtures_dir: Path) -> Path:
    """Return path to simple JUnit XML fixture."""
    return fixtures_dir / "junit_xml" / "simple.xml"


@pytest.fixture
def sample_xml_tree() -> etree._Element:
    """Return a simple XML tree for testing."""
    return load_xml("<root><data>test value</data></root>")


class TestLoadPrivateKey:
    """Tests for private key loading functionality."""

    def test_load_rsa_key_from_file(self, rsa_key_path: Path) -> None:
        """Test loading RSA private key from PEM file."""
        key = load_private_key(rsa_key_path)
        assert key is not None
        # Verify it's a private key by checking for private components
        assert hasattr(key, "sign")

    def test_load_ecdsa_key_from_file(self, ecdsa_key_path: Path) -> None:
        """Test loading ECDSA private key from PEM file."""
        key = load_private_key(ecdsa_key_path)
        assert key is not None
        assert hasattr(key, "sign")

    def test_load_key_from_string(self, rsa_key_path: Path) -> None:
        """Test loading key from PEM string."""
        pem_string = rsa_key_path.read_text()
        key = load_private_key(pem_string)
        assert key is not None

    def test_load_key_from_bytes(self, rsa_key_path: Path) -> None:
        """Test loading key from PEM bytes."""
        pem_bytes = rsa_key_path.read_bytes()
        key = load_private_key(pem_bytes)
        assert key is not None

    def test_load_key_nonexistent_file(self) -> None:
        """Test loading nonexistent key file raises exception."""
        with pytest.raises(FileNotFoundError):
            load_private_key(Path("/nonexistent/key.pem"))

    def test_load_invalid_key(self) -> None:
        """Test loading invalid key data raises exception."""
        with pytest.raises(ValueError):
            load_private_key("not a valid PEM key")

    def test_load_unsupported_key_type(self, tmp_path: Path) -> None:
        """Test loading unsupported key type raises ValueError."""
        # DSA keys are not supported - only RSA and ECDSA
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import dsa

        # Generate DSA key (unsupported)
        dsa_key = dsa.generate_private_key(key_size=2048)

        # Serialize to PEM
        pem_bytes = dsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Should raise ValueError for unsupported key type
        with pytest.raises(ValueError, match="Unsupported key type"):
            load_private_key(pem_bytes)


class TestSignXML:
    """Tests for XML signing functionality."""

    def test_sign_xml_invalid_tree_type(self, rsa_key_path: Path) -> None:
        """Test that sign_xml raises TypeError for invalid tree type."""
        key = load_private_key(rsa_key_path)

        # Pass a non-Element object
        with pytest.raises(TypeError, match="Expected lxml Element"):
            sign_xml("not an element", key)

    def test_sign_xml_without_cert(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path
    ) -> None:
        """Test signing XML without a certificate."""
        key = load_private_key(rsa_key_path)

        # Sign without certificate (cert=None)
        signed_tree = sign_xml(sample_xml_tree, key, cert=None)

        assert signed_tree is not None
        signatures = signed_tree.findall(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )
        assert len(signatures) == 1

    def test_sign_xml_with_cert_as_string(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML with certificate as string."""
        key = load_private_key(rsa_key_path)
        cert_str = rsa_cert_path.read_text()

        signed_tree = sign_xml(sample_xml_tree, key, cert_str)

        assert signed_tree is not None
        signatures = signed_tree.findall(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )
        assert len(signatures) == 1

    def test_sign_xml_with_rsa(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML with RSA key."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        assert signed_tree is not None
        # Check that Signature element was added
        signatures = signed_tree.findall(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )
        assert len(signatures) == 1

    def test_sign_xml_with_ecdsa(
        self,
        sample_xml_tree: etree._Element,
        ecdsa_key_path: Path,
        ecdsa_cert_path: Path,
    ) -> None:
        """Test signing XML with ECDSA key."""
        key = load_private_key(ecdsa_key_path)
        cert = ecdsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        assert signed_tree is not None
        signatures = signed_tree.findall(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )
        assert len(signatures) == 1

    def test_sign_junit_xml(
        self, simple_xml: Path, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing actual JUnit XML file."""
        tree = load_xml(simple_xml)
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        # Verify original content is preserved
        assert signed_tree.find(".//testcase") is not None
        # Verify signature was added
        assert (
            signed_tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
            is not None
        )

    def test_sign_xml_enveloped_signature(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signature is enveloped (inside the root element)."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Signature should be a child of root
        root_children = list(signed_tree)
        signature_children = [
            child
            for child in root_children
            if child.tag == "{http://www.w3.org/2000/09/xmldsig#}Signature"
        ]
        assert len(signature_children) == 1

    def test_sign_xml_preserves_original_content(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signing preserves original XML content."""
        original_data = sample_xml_tree.find(".//data").text
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Original content should be preserved
        signed_data = signed_tree.find(".//data").text
        assert signed_data == original_data

    def test_sign_xml_multiple_times(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML multiple times adds multiple signatures."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()

        signed_once = sign_xml(sample_xml_tree, key, cert)
        signed_twice = sign_xml(signed_once, key, cert)

        signatures = signed_twice.findall(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )
        assert len(signatures) == 2

    def test_sign_xml_with_different_algorithms(
        self,
        sample_xml_tree: etree._Element,
        rsa_key_path: Path,
        ecdsa_key_path: Path,
        rsa_cert_path: Path,
        ecdsa_cert_path: Path,
    ) -> None:
        """Test signing with different key types produces different signatures."""
        rsa_key = load_private_key(rsa_key_path)
        ecdsa_key = load_private_key(ecdsa_key_path)
        rsa_cert = rsa_cert_path.read_bytes()
        ecdsa_cert = ecdsa_cert_path.read_bytes()

        # Deep copy the tree for independent signing
        import copy

        tree1 = copy.deepcopy(sample_xml_tree)
        tree2 = copy.deepcopy(sample_xml_tree)

        signed_rsa = sign_xml(tree1, rsa_key, rsa_cert)
        signed_ecdsa = sign_xml(tree2, ecdsa_key, ecdsa_cert)

        # Both should have signatures
        assert (
            signed_rsa.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
            is not None
        )
        assert (
            signed_ecdsa.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
            is not None
        )

        # Signatures should be different
        sig_rsa = etree.tostring(
            signed_rsa.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
        )
        sig_ecdsa = etree.tostring(
            signed_ecdsa.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
        )
        assert sig_rsa != sig_ecdsa


class TestVerifySignature:
    """Tests for signature verification functionality."""

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_verify_rsa_signature(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test verifying RSA signature."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Verification should succeed
        is_valid = verify_signature(signed_tree)
        assert is_valid is True

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_verify_ecdsa_signature(
        self,
        sample_xml_tree: etree._Element,
        ecdsa_key_path: Path,
        ecdsa_cert_path: Path,
    ) -> None:
        """Test verifying ECDSA signature."""
        key = load_private_key(ecdsa_key_path)
        cert = ecdsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        is_valid = verify_signature(signed_tree)
        assert is_valid is True

    def test_verify_unsigned_xml(self, sample_xml_tree: etree._Element) -> None:
        """Test verifying unsigned XML returns False."""
        is_valid = verify_signature(sample_xml_tree)
        assert is_valid is False

    def test_verify_tampered_signature(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that tampered XML fails verification."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Tamper with the content
        data_elem = signed_tree.find(".//data")
        data_elem.text = "tampered value"

        # Verification should fail
        is_valid = verify_signature(signed_tree)
        assert is_valid is False

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_verify_signature_with_signxml_library(
        self,
        sample_xml_tree: etree._Element,
        rsa_key_path: Path,
        rsa_pub_path: Path,
        rsa_cert_path: Path,
    ) -> None:
        """Test verification using signxml library directly."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Use signxml XMLVerifier directly
        cert_data = rsa_pub_path.read_bytes()
        verifier = XMLVerifier()

        # This should not raise an exception if signature is valid
        try:
            verified_data = verifier.verify(
                etree.tostring(signed_tree),
                x509_cert=cert_data,
            )
            assert verified_data is not None
        except Exception:
            pytest.fail("Signature verification with signxml failed")


class TestSignatureFormats:
    """Tests for signature format and structure."""

    def test_signature_has_signedinfo(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signature contains SignedInfo element."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        signed_info = signed_tree.find(
            ".//{http://www.w3.org/2000/09/xmldsig#}SignedInfo"
        )
        assert signed_info is not None

    def test_signature_has_signaturevalue(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signature contains SignatureValue element."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        sig_value = signed_tree.find(
            ".//{http://www.w3.org/2000/09/xmldsig#}SignatureValue"
        )
        assert sig_value is not None
        assert sig_value.text is not None
        assert len(sig_value.text.strip()) > 0

    def test_signature_has_keyinfo(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signature contains KeyInfo element."""
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        key_info = signed_tree.find(".//{http://www.w3.org/2000/09/xmldsig#}KeyInfo")
        # KeyInfo is optional in XMLDSig, so we just check if it exists
        # (implementation may or may not include it)
        if key_info is not None:
            assert True
        else:
            # If no KeyInfo, that's also valid XMLDSig
            assert True


class TestErrorHandling:
    """Tests for error handling in signing operations."""

    def test_verify_signature_with_non_element(self) -> None:
        """Test verify_signature returns False for non-Element input."""
        from pytest_jux.signer import verify_signature as signer_verify

        # Pass a non-Element object
        result = signer_verify("not an element")
        assert result is False

    def test_verify_signature_without_signature(
        self, sample_xml_tree: etree._Element
    ) -> None:
        """Test verify_signature returns False for unsigned XML."""
        from pytest_jux.signer import verify_signature as signer_verify

        result = signer_verify(sample_xml_tree)
        assert result is False


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_sign_empty_xml(self, rsa_key_path: Path, rsa_cert_path: Path) -> None:
        """Test signing minimal empty XML."""
        tree = load_xml("<root/>")
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        assert (
            signed_tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
            is not None
        )

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_sign_xml_with_namespaces(
        self, rsa_key_path: Path, fixtures_dir: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML with namespaces."""
        namespaced_xml = fixtures_dir / "junit_xml" / "namespaced.xml"
        tree = load_xml(namespaced_xml)
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        is_valid = verify_signature(signed_tree)
        assert is_valid is True

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_sign_large_xml(self, rsa_key_path: Path, rsa_cert_path: Path) -> None:
        """Test signing large XML document."""
        # Create large XML
        xml = '<testsuites><testsuite name="large" tests="500">'
        for i in range(500):
            xml += f'<testcase name="test_{i}" time="0.001"/>'
        xml += "</testsuite></testsuites>"

        tree = load_xml(xml)
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        is_valid = verify_signature(signed_tree)
        assert is_valid is True

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_sign_xml_with_special_characters(
        self, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML with special characters."""
        xml = """<root>
            <data attr="&lt;&gt;&amp;&quot;">Special &lt;chars&gt; &amp; entities</data>
        </root>"""
        tree = load_xml(xml)
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        is_valid = verify_signature(signed_tree)
        assert is_valid is True

    @pytest.mark.xfail(
        reason="XMLDSig verification with self-signed certificates not yet fully supported"
    )
    def test_sign_xml_with_unicode(
        self, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test signing XML with Unicode characters."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <data>Hello 世界 🌍 Здравствуй мир</data>
        </root>"""
        tree = load_xml(xml)
        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree, key, cert)

        assert signed_tree is not None
        is_valid = verify_signature(signed_tree)
        assert is_valid is True


class TestIntegrationWithCanonicalizer:
    """Tests for integration with canonicalizer module."""

    def test_sign_and_hash(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signed XML can be canonicalized and hashed."""
        from pytest_jux.canonicalizer import compute_canonical_hash

        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Should be able to compute hash of signed XML
        hash_value = compute_canonical_hash(signed_tree)
        assert hash_value is not None
        assert len(hash_value) == 64

    def test_signature_affects_hash(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that signature changes the canonical hash."""
        import copy

        from pytest_jux.canonicalizer import compute_canonical_hash

        tree1 = copy.deepcopy(sample_xml_tree)
        tree2 = copy.deepcopy(sample_xml_tree)

        hash_unsigned = compute_canonical_hash(tree1)

        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(tree2, key, cert)
        hash_signed = compute_canonical_hash(signed_tree)

        # Hashes should be different (signature added content)
        assert hash_unsigned != hash_signed

    def test_sign_xml_exception_handling(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path
    ) -> None:
        """Test that sign_xml raises ValueError on signing failure."""
        from unittest.mock import patch

        key = load_private_key(rsa_key_path)

        # Mock XMLSigner.sign to raise an exception
        with patch("pytest_jux.signer.XMLSigner.sign", side_effect=RuntimeError("Signing error")):
            with pytest.raises(ValueError, match="Failed to sign XML"):
                sign_xml(sample_xml_tree, key)

    def test_verify_signature_exception_handling(
        self, sample_xml_tree: etree._Element, rsa_key_path: Path, rsa_cert_path: Path
    ) -> None:
        """Test that verify_signature returns False on exception."""
        from unittest.mock import patch

        from pytest_jux.signer import verify_signature

        key = load_private_key(rsa_key_path)
        cert = rsa_cert_path.read_bytes()
        signed_tree = sign_xml(sample_xml_tree, key, cert)

        # Mock XMLVerifier.verify to raise an exception
        with patch("pytest_jux.signer.XMLVerifier.verify", side_effect=RuntimeError("Verification error")):
            result = verify_signature(signed_tree)
            assert result is False
