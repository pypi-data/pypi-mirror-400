# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""CLI command for inspecting JUnit XML reports."""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import configargparse
from lxml import etree
from rich.console import Console
from rich.table import Table

from pytest_jux.canonicalizer import canonicalize_xml, load_xml

console = Console()
console_err = Console(stderr=True)


def extract_statistics(tree: etree._Element) -> dict[str, int]:
    """Extract test statistics from JUnit XML.

    Args:
        tree: XML element tree

    Returns:
        Dictionary with test statistics (tests, failures, errors, skipped)
    """
    stats = {
        "tests": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
    }

    # Find all testsuite elements
    testsuites = tree.findall(".//testsuite")

    for suite in testsuites:
        # Extract attributes (default to 0 if not present)
        stats["tests"] += int(suite.get("tests", "0"))
        stats["failures"] += int(suite.get("failures", "0"))
        stats["errors"] += int(suite.get("errors", "0"))
        stats["skipped"] += int(suite.get("skipped", "0"))

    return stats


def calculate_canonical_hash(tree: etree._Element) -> str:
    """Calculate SHA-256 hash of canonical XML.

    Args:
        tree: XML element tree

    Returns:
        SHA-256 hash (hex string)
    """
    canonical = canonicalize_xml(tree)
    return hashlib.sha256(canonical).hexdigest()


def is_signed(tree: etree._Element) -> bool:
    """Check if XML has a signature.

    Args:
        tree: XML element tree

    Returns:
        True if signature is present, False otherwise
    """
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    return signature is not None


def create_parser() -> configargparse.ArgumentParser:
    """Create argument parser for jux-inspect command.

    Returns:
        Configured argument parser

    Note:
        This function is called by sphinx-argparse-cli for documentation generation.
    """
    epilog = """
examples:
  Inspect test report (interactive):
    jux-inspect --input junit.xml

  Inspect signed report:
    jux-inspect -i signed.xml

  Inspect with JSON output (for automation):
    jux-inspect -i junit.xml --json

  Inspect from stdin:
    cat junit.xml | jux-inspect

  Extract canonical hash for duplicate detection:
    jux-inspect -i junit.xml --json | jq -r '.canonical_hash'

  Check if report is signed:
    jux-inspect -i report.xml --json | jq -r '.signed'

usage patterns:
  Quick summary:
    jux-inspect -i junit.xml
    # Shows: tests, failures, errors, skipped, passed, hash, signature status

  Automated processing:
    hash=$(jux-inspect -i junit.xml --json | jq -r '.canonical_hash')
    echo "Report hash: $hash"

  Duplicate detection:
    hash1=$(jux-inspect -i report1.xml --json | jq -r '.canonical_hash')
    hash2=$(jux-inspect -i report2.xml --json | jq -r '.canonical_hash')
    if [ "$hash1" = "$hash2" ]; then
      echo "Reports are identical (duplicate)"
    fi

  Batch inspection:
    for file in reports/*.xml; do
      echo "=== $file ==="
      jux-inspect -i "$file"
    done

output (interactive mode):
  Test Report Summary
    Tests:    100
    Failures: 2
    Errors:   0
    Skipped:  5
    Passed:   93

  Canonical Hash: 1a2b3c4d...5e6f7g8h
  Signature:      Present

output (JSON mode):
  {
    "tests": 100,
    "failures": 2,
    "errors": 0,
    "skipped": 5,
    "passed": 93,
    "canonical_hash": "1a2b3c4d5e6f7g8h...",
    "signed": true
  }

see also:
  jux-sign    Sign reports
  jux-verify  Verify signatures
  jux-cache   Manage report cache

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/inspect/
"""

    parser = configargparse.ArgumentParser(
        description="Inspect JUnit XML test reports and display statistics.\n\n"
        "Analyzes test reports to show test counts, pass/fail statistics, canonical hash "
        "for duplicate detection, and signature status. Supports both signed and unsigned "
        "reports. Outputs human-readable summary or JSON for automation.",
        default_config_files=["~/.jux/config", "/etc/jux/config"],
        formatter_class=configargparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        help="Input JUnit XML report file to inspect. "
        "If not specified, reads from standard input (stdin). "
        "Can be signed or unsigned report",
        metavar="FILE",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output inspection results in JSON format. "
        "Returns test statistics, canonical hash, and signature status. "
        "Useful for automated processing and duplicate detection",
    )

    return parser


def main() -> int:
    """Inspect JUnit XML report.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Read XML from file or stdin
        if args.input:
            if not args.input.exists():
                console_err.print(
                    f"[red]Error:[/red] Input file not found: {args.input}"
                )
                return 1
            tree = load_xml(args.input)
        else:
            xml_content = sys.stdin.read()
            tree = etree.fromstring(xml_content.encode("utf-8"))

        # Extract information
        stats = extract_statistics(tree)
        canonical_hash = calculate_canonical_hash(tree)
        signed = is_signed(tree)

        # Output result
        if args.json:
            result: dict[str, Any] = {
                "tests": stats["tests"],
                "failures": stats["failures"],
                "errors": stats["errors"],
                "skipped": stats["skipped"],
                "passed": stats["tests"]
                - stats["failures"]
                - stats["errors"]
                - stats["skipped"],
                "canonical_hash": canonical_hash,
                "signed": signed,
            }
            print(json.dumps(result))
        else:
            # Human-readable output with Rich
            console.print("\n[bold]Test Report Summary[/bold]\n")

            # Create table for statistics
            table = Table(show_header=False, box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold")

            table.add_row("Tests", str(stats["tests"]))
            table.add_row("Failures", str(stats["failures"]))
            table.add_row("Errors", str(stats["errors"]))
            table.add_row("Skipped", str(stats["skipped"]))
            passed = (
                stats["tests"] - stats["failures"] - stats["errors"] - stats["skipped"]
            )
            table.add_row("Passed", str(passed))

            console.print(table)

            console.print(
                f"\n[bold]Canonical Hash:[/bold] {canonical_hash[:16]}...{canonical_hash[-16:]}"
            )

            if signed:
                console.print("[bold]Signature:[/bold] [green]Present[/green]")
            else:
                console.print("[bold]Signature:[/bold] [yellow]None[/yellow]")

            console.print()

        return 0

    except Exception as e:
        if args.json:
            result = {
                "error": str(e),
            }
            print(json.dumps(result))
        else:
            console_err.print(f"[red]Error:[/red] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
