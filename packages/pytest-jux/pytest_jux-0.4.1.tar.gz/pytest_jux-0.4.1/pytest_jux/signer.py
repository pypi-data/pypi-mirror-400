# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""XML digital signature generation for JUnit XML reports.

This module provides functionality to sign JUnit XML reports using
XML Digital Signatures (XMLDSig) with RSA or ECDSA keys.
"""

from pathlib import Path

import signxml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from lxml import etree
from signxml import XMLSigner, XMLVerifier

# Type alias for private keys
PrivateKey = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey  # pragma: no cover


def load_private_key(source: str | bytes | Path) -> PrivateKey:
    """Load private key from various sources.

    Supports RSA and ECDSA keys in PEM format.

    Args:
        source: Key source - can be:
            - Path to PEM file
            - PEM string
            - PEM bytes

    Returns:
        Private key object (RSA or ECDSA)

    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If key data is invalid or unsupported format
    """
    # Load key data
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"Key file not found: {source}")
        key_data = source.read_bytes()
    elif isinstance(source, str):
        key_data = source.encode("utf-8")
    else:
        key_data = source

    # Parse private key
    try:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,  # Assume unencrypted keys for testing
        )
    except Exception as e:
        raise ValueError(f"Failed to load private key: {e}") from e

    # Verify it's a supported key type
    if not isinstance(private_key, rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey):
        raise ValueError(
            f"Unsupported key type: {type(private_key)}. "
            "Only RSA and ECDSA keys are supported."
        )

    return private_key


def sign_xml(
    tree: etree._Element,
    private_key: PrivateKey,
    cert: str | bytes | None = None,
) -> etree._Element:
    """Sign XML with XMLDSig enveloped signature.

    Adds an enveloped XMLDSig signature to the XML document using
    the provided private key. The signature is placed as a child
    of the root element.

    The signature includes:
    - SignedInfo: Canonicalization and signature method info
    - SignatureValue: The actual signature bytes
    - KeyInfo: Information about the signing key (included if cert provided)

    Args:
        tree: XML element tree to sign
        private_key: RSA or ECDSA private key for signing
        cert: Optional X.509 certificate in PEM or DER format.
              If provided, includes certificate in signature for verification.

    Returns:
        Signed XML element tree with Signature element added

    Raises:
        TypeError: If tree is not an lxml element
        ValueError: If signing fails
    """
    if not isinstance(tree, etree._Element):
        raise TypeError(f"Expected lxml Element, got {type(tree)}")

    # Create XML signer
    signer = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm="rsa-sha256"
        if isinstance(private_key, rsa.RSAPrivateKey)
        else "ecdsa-sha256",
        digest_algorithm="sha256",
    )

    try:
        # Sign the XML
        # signxml modifies the tree in-place and returns it
        if cert is not None:
            # Convert bytes to string if needed (signxml expects str or list)
            cert_str = cert.decode("utf-8") if isinstance(cert, bytes) else cert
            signed_root = signer.sign(tree, key=private_key, cert=cert_str)
        else:
            signed_root = signer.sign(tree, key=private_key)
        return signed_root
    except Exception as e:
        raise ValueError(f"Failed to sign XML: {e}") from e


def verify_signature(tree: etree._Element) -> bool:
    """Verify XMLDSig signature in signed XML.

    Verifies the XML digital signature embedded in the XML document.
    Returns True if the signature is valid, False otherwise.

    Args:
        tree: Signed XML element tree

    Returns:
        True if signature is valid, False otherwise
    """
    if not isinstance(tree, etree._Element):
        return False

    # Check if XML has a signature
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature is None:
        return False

    # Verify the signature
    # Note: XMLDSig verification uses the embedded certificate in the signature
    verifier = XMLVerifier()
    try:
        # Verify signature (raises exception if invalid)
        # This validates the cryptographic signature is correct
        verifier.verify(etree.tostring(tree))
        return True
    except Exception:
        # Any exception means signature is invalid
        return False
