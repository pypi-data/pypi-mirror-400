# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""jux-keygen: Generate cryptographic keys for signing JUnit XML reports."""

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import configargparse
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import NameOID
from rich.console import Console

from pytest_jux.errors import (
    FileAlreadyExistsError,
    FilePermissionError,
    InvalidArgumentError,
)

# Type alias for private keys
PrivateKeyTypes = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey

console = Console()


def generate_rsa_key(key_size: int) -> rsa.RSAPrivateKey:
    """Generate an RSA private key.

    Args:
        key_size: RSA key size in bits (2048, 3072, or 4096)

    Returns:
        RSA private key

    Raises:
        ValueError: If key_size is not valid
    """
    if key_size not in (2048, 3072, 4096):
        raise ValueError(f"Key size must be 2048, 3072, or 4096 bits, got {key_size}")

    return rsa.generate_private_key(
        public_exponent=65537,  # F4
        key_size=key_size,
    )


def generate_ecdsa_key(curve_name: str) -> ec.EllipticCurvePrivateKey:
    """Generate an ECDSA private key.

    Args:
        curve_name: Curve name (P-256, P-384, or P-521)

    Returns:
        ECDSA private key

    Raises:
        ValueError: If curve_name is not supported
    """
    curves = {
        "P-256": ec.SECP256R1(),
        "P-384": ec.SECP384R1(),
        "P-521": ec.SECP521R1(),
    }

    if curve_name not in curves:
        raise ValueError(
            f"Unsupported curve: {curve_name}. "
            f"Supported curves: {', '.join(curves.keys())}"
        )

    return ec.generate_private_key(curves[curve_name])


def save_key(key: PrivateKeyTypes, output_path: Path) -> None:
    """Save private key to file with secure permissions.

    Args:
        key: Private key to save
        output_path: Path to save key file

    Raises:
        PermissionError: If unable to set secure file permissions
        OSError: If unable to write file
    """
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize key to PEM format
    pem_data = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Write key to file
    output_path.write_bytes(pem_data)

    # Set secure file permissions (owner read/write only)
    output_path.chmod(0o600)


def generate_self_signed_cert(
    key: PrivateKeyTypes,
    cert_path: Path,
    subject_name: str = "CN=pytest-jux",
    days_valid: int = 365,
) -> None:
    """Generate a self-signed X.509 certificate.

    Args:
        key: Private key for the certificate
        cert_path: Path to save certificate file
        subject_name: Certificate subject (RFC 4514 format)
        days_valid: Number of days the certificate is valid

    Raises:
        OSError: If unable to write certificate file
    """
    # Parse subject name (simple RFC 4514 parsing)
    # For now, just use the CN if provided, otherwise use default
    if "=" in subject_name:
        # Parse CN=value format
        cn_value = subject_name.split("=", 1)[1]
    else:
        cn_value = subject_name

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, cn_value),
        ]
    )

    # Generate certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(UTC))
        .not_valid_after(datetime.now(UTC) + timedelta(days=days_valid))
        .sign(key, hashes.SHA256())
    )

    # Save certificate to file
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    cert_path.write_bytes(cert_pem)


def create_parser() -> configargparse.ArgumentParser:
    """Create argument parser for jux-keygen command.

    Returns:
        Configured argument parser

    Note:
        This function is called by sphinx-argparse-cli for documentation generation.
    """
    epilog = """
examples:
  Generate RSA-2048 key (development):
    jux-keygen --type rsa --bits 2048 --output ~/.ssh/jux/dev-key.pem

  Generate RSA-4096 key with certificate (production):
    jux-keygen --type rsa --bits 4096 --output ~/.ssh/jux/prod-key.pem \\
      --cert --subject "CN=My Organization CI/CD" --days-valid 365

  Generate ECDSA-P256 key (performance-critical):
    jux-keygen --type ecdsa --curve P-256 --output ~/.ssh/jux/ecdsa-key.pem

  Generate key with auto-generated certificate:
    jux-keygen --output ~/.ssh/jux/signing-key.pem --cert

security notes:
  - Private keys are saved with 0600 permissions (owner read/write only)
  - Self-signed certificates are for development/testing only
  - For production, use proper PKI/CA-signed certificates
  - Never commit private keys to version control

see also:
  jux-sign    Sign JUnit XML reports
  jux-verify  Verify signed reports
  jux-config  Manage configuration

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/keygen/
"""

    parser = configargparse.ArgumentParser(
        description="Generate cryptographic signing keys for JUnit XML reports.\n\n"
        "Supports RSA (2048/3072/4096-bit) and ECDSA (P-256/P-384/P-521) keys. "
        "Keys are saved in PEM format with secure file permissions (0600). "
        "Optionally generates self-signed X.509 certificates for development use.",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )

    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        help="Configuration file path (default: ~/.jux/config)",
    )

    parser.add_argument(
        "--type",
        choices=["rsa", "ecdsa"],
        default="rsa",
        help="Key algorithm: 'rsa' (default, widely compatible) or 'ecdsa' (faster, smaller)",
    )

    parser.add_argument(
        "--bits",
        type=int,
        choices=[2048, 3072, 4096],
        default=2048,
        help="RSA key size in bits (applies to RSA keys only). "
        "Use 2048 for development, 4096 for production. Default: 2048",
    )

    parser.add_argument(
        "--curve",
        choices=["P-256", "P-384", "P-521"],
        default="P-256",
        help="ECDSA curve name (applies to ECDSA keys only). "
        "P-256 (default) provides 128-bit security, P-384 provides 192-bit security",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output file path for private key (PEM format). "
        "Parent directories will be created if they don't exist. "
        "Example: ~/.ssh/jux/signing-key.pem",
        metavar="PATH",
    )

    parser.add_argument(
        "--cert",
        action="store_true",
        help="Generate a self-signed X.509 certificate alongside the private key. "
        "Certificate will be saved as <output>.crt (e.g., signing-key.pem.crt). "
        "Self-signed certificates are suitable for development/testing only",
    )

    parser.add_argument(
        "--subject",
        default="CN=pytest-jux",
        help="X.509 certificate subject in RFC 4514 format (used with --cert). "
        "Example: 'CN=My Organization CI/CD'. Default: 'CN=pytest-jux'",
        metavar="DN",
    )

    parser.add_argument(
        "--days-valid",
        type=int,
        default=365,
        help="Certificate validity period in days (used with --cert). "
        "Default: 365 days (1 year)",
        metavar="DAYS",
    )

    return parser


def main() -> int:
    """Main entry point for jux-keygen command.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()

    # Get debug mode from environment
    debug = os.getenv("JUX_DEBUG") == "1"

    try:
        args = parser.parse_args()

        # Check if output file already exists
        if args.output.exists():
            raise FileAlreadyExistsError(
                args.output,
                command_hint="Currently, jux-keygen does not support --force. "
                "Remove the file manually or choose a different path.",
            )

        # Validate arguments (defensive - argparse should already validate these)
        if args.type == "rsa" and args.bits not in (2048, 3072, 4096):  # pragma: no cover
            raise InvalidArgumentError(
                "--bits",
                f"Invalid RSA key size: {args.bits}",
                valid_values=["2048", "3072", "4096"],
            )

        if args.type == "ecdsa" and args.curve not in ("P-256", "P-384", "P-521"):  # pragma: no cover
            raise InvalidArgumentError(
                "--curve",
                f"Invalid ECDSA curve: {args.curve}",
                valid_values=["P-256", "P-384", "P-521"],
            )

        # Generate key
        console.print(f"[bold]Generating {args.type.upper()} key...[/bold]")

        key: PrivateKeyTypes
        if args.type == "rsa":
            key = generate_rsa_key(args.bits)
            console.print(f"  Key size: {args.bits} bits")
        else:  # ecdsa
            key = generate_ecdsa_key(args.curve)
            console.print(f"  Curve: {args.curve}")

        # Save private key
        save_key(key, args.output)
        console.print(f"  [green]✓[/green] Private key saved: {args.output}")

        # Generate certificate if requested
        if args.cert:
            cert_path = args.output.with_suffix(".crt")
            generate_self_signed_cert(key, cert_path, args.subject, args.days_valid)
            console.print(f"  [green]✓[/green] Certificate saved: {cert_path}")
            console.print(
                "  [yellow]⚠[/yellow] Self-signed certificate - "
                "NOT suitable for production use"
            )

        console.print("\n[green]Key generation complete![/green]")
        return 0

    except FileAlreadyExistsError as e:
        # File already exists
        e.print_error()
        return 1

    except InvalidArgumentError as e:  # pragma: no cover
        # Invalid argument (defensive - argparse should catch invalid arguments)
        e.print_error()
        return 1

    except ValueError as e:
        # Convert ValueError to InvalidArgumentError
        InvalidArgumentError(
            "key generation",
            str(e),
        ).print_error()
        return 1

    except PermissionError:
        # Convert PermissionError to FilePermissionError
        FilePermissionError(
            args.output if hasattr(args, "output") else Path("."),
            operation="write",
        ).print_error()
        return 1

    except Exception as e:
        # Handle unexpected errors in non-debug mode
        if debug:
            raise
        from rich.console import Console
        console_err = Console(stderr=True)
        console_err.print("[red]Unexpected error:[/red]")
        console_err.print(f"  {type(e).__name__}: {e}")
        console_err.print("\n[yellow]This is likely a bug in pytest-jux[/yellow]")
        console_err.print("Please report this at:")
        console_err.print("  https://github.com/jrjsmrtn/pytest-jux/issues")
        console_err.print("\nInclude the error message above and the command you ran.")
        console_err.print("\n[dim]Tip: Run with JUX_DEBUG=1 for more details[/dim]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
