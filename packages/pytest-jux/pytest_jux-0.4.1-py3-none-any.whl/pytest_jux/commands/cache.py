# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Cache management command for pytest-jux."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from lxml import etree

from pytest_jux.storage import ReportStorage, StorageError, get_default_storage_path


def extract_metadata_from_xml(report_xml: bytes) -> dict[str, str]:
    """Extract metadata from XML <properties> elements.

    Args:
        report_xml: JUnit XML report bytes

    Returns:
        Dictionary of metadata key-value pairs
    """
    try:
        root = etree.fromstring(report_xml)
        properties = root.find(".//properties")

        if properties is None:
            return {}

        metadata = {}
        for prop in properties.findall("property"):
            name = prop.get("name")
            value = prop.get("value")
            if name and value:
                metadata[name] = value

        return metadata
    except Exception:
        return {}


def cmd_list(args: argparse.Namespace) -> int:
    """List all cached reports.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        reports = storage.list_reports()

        if args.json:
            # JSON output
            report_data = []
            for report_hash in reports:
                try:
                    report_xml = storage.get_report(report_hash)
                    metadata = extract_metadata_from_xml(report_xml)
                    report_file = storage_path / "reports" / f"{report_hash}.xml"
                    report_data.append(
                        {
                            "hash": report_hash,
                            "timestamp": metadata.get("jux:timestamp", "N/A"),
                            "hostname": metadata.get("jux:hostname", "N/A"),
                            "size": report_file.stat().st_size
                            if report_file.exists()
                            else 0,
                        }
                    )
                except StorageError:
                    # Skip reports that can't be read
                    continue

            output = {"reports": report_data, "total": len(report_data)}
            print(json.dumps(output, indent=2))
        else:
            # Text output
            if not reports:
                print("No cached reports found.")
            else:
                print(f"Cached Reports ({len(reports)} total):")
                print()
                for report_hash in reports:
                    try:
                        report_xml = storage.get_report(report_hash)
                        metadata = extract_metadata_from_xml(report_xml)
                        print(f"  {report_hash}")
                        print(f"    Timestamp: {metadata.get('jux:timestamp', 'N/A')}")
                        print(f"    Hostname:  {metadata.get('jux:hostname', 'N/A')}")
                        print(f"    Username:  {metadata.get('jux:username', 'N/A')}")
                        print()
                    except StorageError:
                        print(f"  {report_hash} (cannot read report)")
                        print()

        return 0

    except Exception as e:
        print(f"Error listing reports: {e}", file=sys.stderr)
        return 1


def cmd_show(args: argparse.Namespace) -> int:
    """Show details for a specific cached report.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        report_hash = args.hash

        # Get report and extract metadata from XML
        report_xml = storage.get_report(report_hash)
        metadata = extract_metadata_from_xml(report_xml)

        if args.json:
            # JSON output
            output = {
                "hash": report_hash,
                "metadata": metadata,
                "report": report_xml.decode("utf-8"),
                "size": len(report_xml),
            }
            print(json.dumps(output, indent=2))
        else:
            # Text output
            print(f"Report: {report_hash}")
            print()
            print("Metadata:")
            print(f"  Hostname:       {metadata.get('jux:hostname', 'N/A')}")
            print(f"  Username:       {metadata.get('jux:username', 'N/A')}")
            print(f"  Platform:       {metadata.get('jux:platform', 'N/A')}")
            print(f"  Python Version: {metadata.get('jux:python_version', 'N/A')}")
            print(f"  pytest Version: {metadata.get('jux:pytest_version', 'N/A')}")
            print(f"  Timestamp:      {metadata.get('jux:timestamp', 'N/A')}")

            # Show environment variables (jux:env: prefix)
            env_vars = {k[8:]: v for k, v in metadata.items() if k.startswith("jux:env:")}
            if env_vars:
                print("  Environment:")
                for key, value in env_vars.items():
                    print(f"    {key}: {value}")

            print()
            print(f"Report Content ({len(report_xml)} bytes):")
            print(report_xml.decode("utf-8"))

        return 0

    except StorageError:
        print(f"Error: Report not found: {args.hash}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error showing report: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Show cache statistics.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        stats = storage.get_stats()

        if args.json:
            # JSON output
            print(json.dumps(stats, indent=2))
        else:
            # Text output
            print("Cache Statistics:")
            print()
            print(f"  Total Reports:  {stats['total_reports']}")
            print(f"  Queued Reports: {stats['queued_reports']}")
            print(f"  Total Size:     {_format_size(stats['total_size'])}")
            if stats["oldest_report"]:
                print(f"  Oldest Report:  {stats['oldest_report']}")
            else:
                print("  Oldest Report:  (none)")

        return 0

    except Exception as e:
        print(f"Error getting statistics: {e}", file=sys.stderr)
        return 1


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean old cached reports.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        storage_path = (
            Path(args.storage_path) if args.storage_path else get_default_storage_path()
        )
        storage = ReportStorage(storage_path=storage_path)

        cutoff_time = datetime.now() - timedelta(days=args.days)
        cutoff_timestamp = cutoff_time.timestamp()

        reports = storage.list_reports()
        reports_to_delete = []

        # Find reports older than cutoff
        for report_hash in reports:
            report_file = storage_path / "reports" / f"{report_hash}.xml"
            if report_file.exists():
                mtime = report_file.stat().st_mtime
                if mtime < cutoff_timestamp:
                    reports_to_delete.append(report_hash)

        if args.dry_run:
            # Dry run - show what would be deleted
            if reports_to_delete:
                print(f"Dry run: Would remove {len(reports_to_delete)} report(s):")
                for report_hash in reports_to_delete:
                    print(f"  {report_hash}")
            else:
                print(f"Dry run: No reports older than {args.days} days found.")
        else:
            # Actually delete
            if reports_to_delete:
                for report_hash in reports_to_delete:
                    storage.delete_report(report_hash)
                print(
                    f"Removed {len(reports_to_delete)} report(s) older than {args.days} days."
                )
            else:
                print(f"No reports older than {args.days} days found.")

        return 0

    except Exception as e:
        print(f"Error cleaning cache: {e}", file=sys.stderr)
        return 1


def _format_size(size_bytes: int) -> str:
    """Format byte size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} PB"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for cache command.

    Returns:
        Configured ArgumentParser
    """
    epilog = """
examples:
  List all cached reports:
    jux-cache list

  Show cache statistics:
    jux-cache stats

  Show specific report details:
    jux-cache show 1a2b3c4d5e6f...

  Clean old reports (older than 30 days):
    jux-cache clean --days 30

  Dry-run cleanup (preview what would be deleted):
    jux-cache clean --days 30 --dry-run

  Use custom storage path:
    jux-cache list --storage-path /mnt/data/pytest-jux

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/cache/
"""

    parser = argparse.ArgumentParser(
        prog="jux-cache",
        description="Manage pytest-jux report cache.\n\n"
        "View, inspect, and clean up locally cached signed test reports. "
        "Reports are stored by canonical hash for duplicate detection. "
        "Supports listing, statistics, cleanup, and detailed inspection.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--storage-path",
        type=str,
        help="Custom storage directory path (default: ~/.local/share/pytest-jux). "
        "Override default XDG storage location",
        metavar="PATH",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Cache management subcommands",
        metavar="COMMAND",
    )

    # List subcommand
    parser_list = subparsers.add_parser(
        "list",
        help="List all cached reports with metadata",
        description="Display all reports stored in the cache with their hashes, "
        "timestamps, and metadata. Use --json for machine-readable output.",
    )
    parser_list.add_argument(
        "--json",
        action="store_true",
        help="Output report list in JSON format for automation",
    )

    # Show subcommand
    parser_show = subparsers.add_parser(
        "show",
        help="Show detailed information for a specific report",
        description="Display complete report contents and metadata for a given canonical hash.",
    )
    parser_show.add_argument(
        "hash",
        help="Report canonical hash (SHA-256 hex string, can be abbreviated)",
        metavar="HASH",
    )
    parser_show.add_argument(
        "--json",
        action="store_true",
        help="Output report details in JSON format",
    )

    # Stats subcommand
    parser_stats = subparsers.add_parser(
        "stats",
        help="Display cache storage statistics",
        description="Show cache size, report count, oldest/newest reports, and disk usage.",
    )
    parser_stats.add_argument(
        "--json",
        action="store_true",
        help="Output statistics in JSON format",
    )

    # Clean subcommand
    parser_clean = subparsers.add_parser(
        "clean",
        help="Remove old reports from cache",
        description="Delete reports older than the specified number of days. "
        "Use --dry-run to preview what would be deleted without actually removing files.",
    )
    parser_clean.add_argument(
        "--days",
        type=int,
        required=True,
        help="Remove reports older than N days (required)",
        metavar="N",
    )
    parser_clean.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files that would be deleted without actually removing them. "
        "Shows report hashes and timestamps for review",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for cache command.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 = success, 1 = error, 2 = usage error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    # Dispatch to subcommand handler
    if args.command == "list":
        return cmd_list(args)
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "clean":
        return cmd_clean(args)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
