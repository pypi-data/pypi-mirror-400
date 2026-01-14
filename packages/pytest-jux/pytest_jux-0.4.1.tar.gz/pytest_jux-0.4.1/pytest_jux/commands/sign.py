# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""jux-sign: Sign JUnit XML reports with XML digital signatures."""

import os
import sys
from pathlib import Path

import configargparse
from lxml import etree
from rich.console import Console

from pytest_jux.canonicalizer import load_xml
from pytest_jux.errors import (
    CertNotFoundError,
    FileNotFoundError,
    FilePermissionError,
    KeyInvalidFormatError,
    KeyNotFoundError,
    XMLParseError,
)
from pytest_jux.signer import load_private_key, sign_xml

console = Console()
console_err = Console(stderr=True)


def create_parser() -> configargparse.ArgumentParser:
    """Create argument parser for jux-sign command.

    Returns:
        Configured argument parser

    Note:
        This function is called by sphinx-argparse-cli for documentation generation.
    """
    epilog = """
examples:
  Sign report with RSA key:
    jux-sign --input junit.xml --output signed.xml --key ~/.ssh/jux/dev-key.pem

  Sign with environment variable for key:
    export JUX_KEY_PATH=~/.ssh/jux/prod-key.pem
    jux-sign -i junit.xml -o signed.xml

  Sign with certificate (for verification):
    jux-sign -i junit.xml -o signed.xml --key key.pem --cert cert.pem

  Pipe through standard input/output:
    cat junit.xml | jux-sign --key key.pem > signed.xml

  Sign in-place (overwrite input):
    jux-sign -i junit.xml -o junit.xml --key key.pem

usage patterns:
  Development workflow:
    pytest --junitxml=junit.xml
    jux-sign -i junit.xml -o signed.xml --key ~/.ssh/jux/dev-key.pem
    jux-verify signed.xml

  CI/CD workflow:
    pytest --junitxml=junit.xml
    jux-sign -i junit.xml -o signed.xml --key $CI_SIGNING_KEY

  Batch signing:
    for file in tests/results/*.xml; do
      jux-sign -i "$file" -o "${file%.xml}_signed.xml" --key key.pem
    done

see also:
  jux-keygen  Generate signing keys
  jux-verify  Verify signed reports
  jux-inspect Inspect report contents

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/sign/
"""

    parser = configargparse.ArgumentParser(
        description="Sign JUnit XML test reports with XMLDSig digital signatures.\n\n"
        "Creates cryptographically signed reports that prove authenticity and integrity. "
        "Supports RSA and ECDSA keys in PEM format. The signature is embedded directly "
        "in the XML report (enveloped signature). Signed reports can be verified with "
        "'jux-verify' to detect tampering or forgery.",
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
        "-i",
        "--input",
        type=Path,
        help="Input JUnit XML report file to sign. "
        "If not specified, reads from standard input (stdin). "
        "File must contain valid JUnit XML",
        metavar="FILE",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for signed XML report. "
        "If not specified, writes to standard output (stdout). "
        "Can be same as input to sign in-place",
        metavar="FILE",
    )

    parser.add_argument(
        "--key",
        type=Path,
        required=True,
        env_var="JUX_KEY_PATH",
        help="Path to private key file in PEM format (RSA or ECDSA). "
        "Required for signing. Can also be set via JUX_KEY_PATH environment variable. "
        "Example: ~/.ssh/jux/signing-key.pem",
        metavar="PATH",
    )

    parser.add_argument(
        "--cert",
        type=Path,
        env_var="JUX_CERT_PATH",
        help="Path to X.509 certificate file in PEM format (optional). "
        "If provided, certificate is embedded in signature for easier verification. "
        "Can also be set via JUX_CERT_PATH environment variable",
        metavar="PATH",
    )

    return parser


def main() -> int:
    """Main entry point for jux-sign command.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()

    # Get debug mode from environment
    debug = os.getenv("JUX_DEBUG") == "1"

    try:
        args = parser.parse_args()

        # Validate key file exists
        if not args.key.exists():
            raise KeyNotFoundError(args.key)

        # Validate certificate file if provided
        if args.cert and not args.cert.exists():
            raise CertNotFoundError(args.cert)

        # Validate input file if provided
        if args.input and not args.input.exists():
            raise FileNotFoundError(args.input, file_type="input XML file")

        # Determine if we're in quiet mode (outputting to stdout)
        quiet = args.output is None

        # Read input XML
        if args.input:
            if not quiet:
                console.print(f"[bold]Reading XML:[/bold] {args.input}")
            tree = load_xml(args.input)
        else:
            # Read from stdin
            if not quiet:
                console.print("[bold]Reading XML from stdin...[/bold]")
            xml_content = sys.stdin.read()
            try:
                tree = etree.fromstring(xml_content.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                raise XMLParseError(None, str(e)) from e

        # Load private key
        if not quiet:
            console.print(f"[bold]Loading private key:[/bold] {args.key}")
        try:
            key = load_private_key(args.key)
        except ValueError as e:
            raise KeyInvalidFormatError(args.key) from e

        # Load certificate if provided
        cert: bytes | None = None
        if args.cert:
            if not quiet:
                console.print(f"[bold]Loading certificate:[/bold] {args.cert}")
            try:
                cert = args.cert.read_bytes()
            except PermissionError as e:
                raise FilePermissionError(args.cert, operation="read") from e

        # Sign XML
        if not quiet:
            console.print("[bold]Signing XML...[/bold]")
        signed_tree = sign_xml(tree, key, cert)

        # Serialize signed XML
        signed_xml = etree.tostring(
            signed_tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=True,
        )

        # Write output
        if args.output:
            console.print(f"[bold]Writing signed XML:[/bold] {args.output}")
            try:
                args.output.write_bytes(signed_xml)
            except PermissionError as e:
                raise FilePermissionError(args.output, operation="write") from e
            console.print("[green]✓[/green] Successfully signed XML")
        else:
            # Write to stdout
            sys.stdout.buffer.write(signed_xml)
            sys.stdout.buffer.flush()

        return 0

    except etree.XMLSyntaxError as e:
        # XML parsing error
        xml_path = args.input if hasattr(args, "input") and args.input else None
        XMLParseError(xml_path, str(e)).print_error()
        return 1

    except ValueError:
        # Key loading or signing error
        KeyInvalidFormatError(
            args.key if hasattr(args, "key") else Path("unknown")
        ).print_error()
        return 1

    except PermissionError:
        # Permission error
        path = args.output if hasattr(args, "output") and args.output else Path(".")
        FilePermissionError(path, operation="write").print_error()
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
