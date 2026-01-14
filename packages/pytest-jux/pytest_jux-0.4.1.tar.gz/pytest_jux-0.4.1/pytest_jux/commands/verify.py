# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""CLI command for verifying XML signature."""

import json
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
    XMLParseError,
    XMLSignatureInvalidError,
    XMLSignatureMissingError,
)
from pytest_jux.verifier import verify_signature

console = Console()
console_err = Console(stderr=True)


def create_parser() -> configargparse.ArgumentParser:
    """Create argument parser for jux-verify command.

    Returns:
        Configured argument parser

    Note:
        This function is called by sphinx-argparse-cli for documentation generation.
    """
    epilog = """
examples:
  Verify signed report (interactive):
    jux-verify --input signed.xml --cert ~/.ssh/jux/dev-cert.pem

  Verify with environment variable for certificate:
    export JUX_CERT_PATH=~/.ssh/jux/prod-cert.pem
    jux-verify -i signed.xml

  Verify in quiet mode (exit code only):
    jux-verify -i signed.xml --cert cert.pem --quiet
    echo $?  # 0 = valid, 1 = invalid

  Verify with JSON output (for automation):
    jux-verify -i signed.xml --cert cert.pem --json
    # Output: {"valid": true}

  Verify from stdin:
    cat signed.xml | jux-verify --cert cert.pem

usage patterns:
  CI/CD verification:
    jux-verify -i signed.xml --cert $CI_CERT_PATH --quiet || exit 1
    echo "Report verified successfully"

  Batch verification:
    for file in reports/*.xml; do
      if jux-verify -i "$file" --cert cert.pem --quiet; then
        echo "✓ $file"
      else
        echo "✗ $file FAILED"
      fi
    done

  Automated verification with JSON:
    result=$(jux-verify -i signed.xml --cert cert.pem --json)
    valid=$(echo "$result" | jq -r '.valid')
    if [ "$valid" = "true" ]; then
      echo "Signature verified"
    fi

exit codes:
  0  Signature is valid
  1  Signature is invalid or error occurred

see also:
  jux-sign    Sign JUnit XML reports
  jux-inspect Inspect signed reports
  jux-keygen  Generate signing keys

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/verify/
"""

    parser = configargparse.ArgumentParser(
        description="Verify XMLDSig digital signatures on signed JUnit XML reports.\n\n"
        "Validates the cryptographic signature to ensure report authenticity and integrity. "
        "Checks that the report was signed with the private key corresponding to the "
        "provided certificate and has not been modified since signing. Returns exit code 0 "
        "for valid signatures, 1 for invalid or errors.",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input signed XML report file to verify. "
        "If not specified, reads from standard input (stdin). "
        "File must contain a valid XMLDSig signature",
        metavar="FILE",
    )

    parser.add_argument(
        "--cert",
        type=Path,
        required=True,
        env_var="JUX_CERT_PATH",
        help="Path to X.509 certificate file in PEM format. "
        "Public certificate used to verify the signature. Must correspond to the "
        "private key used for signing. Can also be set via JUX_CERT_PATH environment variable",
        metavar="PATH",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode - suppress all output. "
        "Only exit code indicates success (0) or failure (1). "
        "Useful for automated scripts and CI/CD pipelines",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output verification result in JSON format. "
        "Returns {'valid': true/false} or {'valid': false, 'error': 'message'}. "
        "Useful for programmatic processing and automation",
    )

    return parser


def main() -> int:
    """Verify XML digital signature.

    Returns:
        Exit code (0 for valid signature, 1 for invalid/error)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Get debug mode from environment
    debug = os.getenv("JUX_DEBUG") == "1"

    try:
        # Validate input file if provided
        if args.input and not args.input.exists():
            if args.json:
                print(json.dumps({"valid": False, "error": "Input file not found"}))
                return 1
            elif not args.quiet:
                FileNotFoundError(args.input, file_type="input XML file").print_error()
            return 1

        # Validate certificate file
        if not args.cert.exists():
            if args.json:
                print(json.dumps({"valid": False, "error": "Certificate not found"}))
                return 1
            elif not args.quiet:
                CertNotFoundError(args.cert).print_error()
            return 1

        # Read XML from file or stdin
        if args.input:
            try:
                tree = load_xml(args.input)
            except etree.XMLSyntaxError as e:
                if args.json:
                    print(json.dumps({"valid": False, "error": f"XML parse error: {e}"}))
                    return 1
                elif not args.quiet:
                    XMLParseError(args.input, str(e)).print_error()
                return 1
        else:
            xml_content = sys.stdin.read()
            try:
                tree = etree.fromstring(xml_content.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                if args.json:
                    print(json.dumps({"valid": False, "error": f"XML parse error: {e}"}))
                    return 1
                elif not args.quiet:
                    XMLParseError(None, str(e)).print_error()
                return 1

        # Read certificate
        cert = args.cert.read_bytes()

        # Verify signature
        try:
            is_valid = verify_signature(tree, cert)
        except ValueError as e:
            error_msg = str(e)
            # Check if signature is missing
            if "signature" in error_msg.lower() and "not found" in error_msg.lower():
                if args.json:
                    print(json.dumps({"valid": False, "error": "Signature not found"}))
                    return 1
                elif not args.quiet:
                    xml_path = args.input if args.input else None
                    XMLSignatureMissingError(xml_path).print_error()
                return 1
            else:
                # Signature invalid
                if args.json:
                    print(json.dumps({"valid": False, "error": error_msg}))
                    return 1
                elif not args.quiet:
                    XMLSignatureInvalidError(error_msg).print_error()
                return 1

        # Output result
        if args.json:
            result = {
                "valid": is_valid,
            }
            print(json.dumps(result))
        elif not args.quiet:
            if is_valid:
                console.print("[green]✓[/green] Signature is valid")
            else:
                console.print("[red]✗[/red] Signature is invalid")

        return 0 if is_valid else 1

    except Exception as e:
        if args.json:
            error_result: dict[str, bool | str] = {
                "valid": False,
                "error": str(e),
            }
            print(json.dumps(error_result))
        elif not args.quiet:
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
