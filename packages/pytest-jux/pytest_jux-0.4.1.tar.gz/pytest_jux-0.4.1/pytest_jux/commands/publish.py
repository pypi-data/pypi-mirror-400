# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""jux-publish: Manually publish signed JUnit XML reports to Jux API.

This command allows manual publishing of:
- Single XML report files
- All queued reports from offline cache
- Supports dry-run mode to preview actions
"""

import json
import os
import sys
from pathlib import Path

import configargparse
from rich.console import Console

from pytest_jux.api_client import JuxAPIClient
from pytest_jux.storage import ReportStorage, get_default_storage_path

console = Console()
console_err = Console(stderr=True)


def create_parser() -> configargparse.ArgumentParser:
    """Create argument parser for jux-publish command.

    Returns:
        Configured argument parser

    Note:
        This function is called by sphinx-argparse-cli for documentation generation.
    """
    epilog = """
examples:
  Publish single report:
    jux-publish --file report.xml --api-url https://jux.example.com/api/v1

  Publish all queued reports:
    jux-publish --queue --api-url https://jux.example.com/api/v1

  Dry-run (show what would be published):
    jux-publish --queue --dry-run

  Publish with authentication:
    export JUX_BEARER_TOKEN=your-token
    jux-publish --queue --api-url https://jux.example.com/api/v1

  JSON output for scripting:
    jux-publish --queue --json

usage patterns:
  CI/CD workflow (publish after tests):
    pytest --junitxml=report.xml
    jux-sign -i report.xml -o signed.xml --key $CI_KEY
    jux-publish --file signed.xml --api-url $JUX_API_URL

  Offline workflow (sync cached reports):
    # Reports were cached during offline test runs
    jux-publish --queue --api-url https://jux.example.com/api/v1

  Preview before publishing:
    jux-publish --queue --dry-run --verbose

see also:
  jux-sign    Sign JUnit XML reports
  jux-cache   Manage local report cache
  jux-verify  Verify signed reports

For detailed documentation, see:
  https://docs.pytest-jux.org/reference/cli/publish/
"""

    parser = configargparse.ArgumentParser(
        description="Publish signed JUnit XML test reports to Jux API.\n\n"
        "Supports publishing single files or processing the offline queue. "
        "Reports must be signed with jux-sign before publishing. "
        "Use --dry-run to preview what would be published.",
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

    # Input source (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "-f",
        "--file",
        type=Path,
        help="Path to signed JUnit XML file to publish",
        metavar="FILE",
    )
    source_group.add_argument(
        "-q",
        "--queue",
        action="store_true",
        help="Publish all reports from offline queue",
    )

    # API configuration
    parser.add_argument(
        "--api-url",
        type=str,
        required=True,
        env_var="JUX_API_URL",
        help="Jux API base URL (e.g., https://jux.example.com/api/v1). "
        "Can also be set via JUX_API_URL environment variable",
        metavar="URL",
    )

    parser.add_argument(
        "--bearer-token",
        type=str,
        env_var="JUX_BEARER_TOKEN",
        help="Bearer token for API authentication. "
        "Not required for localhost. "
        "Can also be set via JUX_BEARER_TOKEN environment variable",
        metavar="TOKEN",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        env_var="JUX_API_TIMEOUT",
        help="API request timeout in seconds (default: 30)",
        metavar="SECONDS",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        env_var="JUX_API_MAX_RETRIES",
        help="Maximum retry attempts for transient failures (default: 3)",
        metavar="N",
    )

    # Storage configuration
    parser.add_argument(
        "--storage-path",
        type=Path,
        env_var="JUX_STORAGE_PATH",
        help="Custom storage path for queue (default: platform-specific)",
        metavar="PATH",
    )

    # Output options
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be published without actually publishing",
    )

    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed progress information",
    )

    return parser


def publish_single_file(
    file_path: Path,
    client: JuxAPIClient,
    dry_run: bool = False,
    verbose: bool = False,
    json_output: bool = False,
) -> tuple[bool, dict]:
    """Publish a single XML file to Jux API.

    Args:
        file_path: Path to signed XML file
        client: Configured JuxAPIClient
        dry_run: If True, don't actually publish
        verbose: Show detailed progress
        json_output: Prepare result for JSON output

    Returns:
        Tuple of (success, result_dict)
    """
    result: dict = {
        "file": str(file_path),
        "success": False,
        "error": None,
        "test_run_id": None,
    }

    if not file_path.exists():
        result["error"] = f"File not found: {file_path}"
        return False, result

    try:
        xml_content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result["error"] = f"Failed to read file: {e}"
        return False, result

    if dry_run:
        result["success"] = True
        result["dry_run"] = True
        if verbose and not json_output:
            console.print(f"  [yellow]Would publish:[/yellow] {file_path}")
        return True, result

    try:
        response = client.publish_report(xml_content)
        result["success"] = True
        result["test_run_id"] = response.test_run.id
        result["message"] = response.message

        if verbose and not json_output:
            console.print(f"  [green]✓[/green] Published: {file_path}")
            console.print(f"    Test run ID: {response.test_run.id}")
            console.print(f"    Success rate: {response.test_run.success_rate}%")

        return True, result

    except Exception as e:
        result["error"] = str(e)
        if verbose and not json_output:
            console.print(f"  [red]✗[/red] Failed: {file_path}")
            console.print(f"    Error: {e}")
        return False, result


def publish_queue(
    storage: ReportStorage,
    client: JuxAPIClient,
    dry_run: bool = False,
    verbose: bool = False,
    json_output: bool = False,
) -> tuple[int, int, list[dict]]:
    """Publish all queued reports to Jux API.

    Args:
        storage: ReportStorage instance
        client: Configured JuxAPIClient
        dry_run: If True, don't actually publish
        verbose: Show detailed progress
        json_output: Prepare results for JSON output

    Returns:
        Tuple of (success_count, failure_count, results_list)
    """
    queued_hashes = storage.list_queued_reports()
    results: list[dict] = []
    success_count = 0
    failure_count = 0

    if not queued_hashes:
        return 0, 0, results

    for report_hash in queued_hashes:
        result: dict = {
            "hash": report_hash,
            "success": False,
            "error": None,
            "test_run_id": None,
        }

        try:
            # Read queued report
            queue_file = storage.storage_path / "queue" / f"{report_hash}.xml"
            xml_content = queue_file.read_text(encoding="utf-8")
        except Exception as e:
            result["error"] = f"Failed to read queued report: {e}"
            failure_count += 1
            results.append(result)
            if verbose and not json_output:
                console.print(f"  [red]✗[/red] Failed to read: {report_hash}")
            continue

        if dry_run:
            result["success"] = True
            result["dry_run"] = True
            success_count += 1
            results.append(result)
            if verbose and not json_output:
                console.print(f"  [yellow]Would publish:[/yellow] {report_hash}")
            continue

        try:
            response = client.publish_report(xml_content)
            result["success"] = True
            result["test_run_id"] = response.test_run.id
            result["message"] = response.message
            success_count += 1

            # Dequeue report (move from queue to reports)
            storage.dequeue_report(report_hash)

            if verbose and not json_output:
                console.print(f"  [green]✓[/green] Published: {report_hash}")
                console.print(f"    Test run ID: {response.test_run.id}")

        except Exception as e:
            result["error"] = str(e)
            failure_count += 1
            if verbose and not json_output:
                console.print(f"  [red]✗[/red] Failed: {report_hash}")
                console.print(f"    Error: {e}")

        results.append(result)

    return success_count, failure_count, results


def main(args: list[str] | None = None) -> int:
    """Main entry point for jux-publish command.

    Args:
        args: Command line arguments (for testing). If None, uses sys.argv.

    Returns:
        Exit code:
        - 0: All reports published successfully
        - 1: All reports failed to publish
        - 2: Partial success (some failed)
    """
    parser = create_parser()

    # Get debug mode from environment
    debug = os.getenv("JUX_DEBUG") == "1"

    try:
        parsed_args = parser.parse_args(args)

        # Initialize API client
        client = JuxAPIClient(
            api_url=parsed_args.api_url,
            bearer_token=parsed_args.bearer_token,
            timeout=parsed_args.timeout,
            max_retries=parsed_args.max_retries,
        )

        json_result: dict = {
            "success": False,
            "dry_run": parsed_args.dry_run,
            "published": 0,
            "failed": 0,
            "results": [],
        }

        if parsed_args.file:
            # Single file mode
            if not parsed_args.json and not parsed_args.dry_run:
                console.print(
                    f"[bold]Publishing report:[/bold] {parsed_args.file}"
                )

            success, result = publish_single_file(
                file_path=parsed_args.file,
                client=client,
                dry_run=parsed_args.dry_run,
                verbose=parsed_args.verbose,
                json_output=parsed_args.json,
            )

            json_result["results"].append(result)

            if success:
                json_result["success"] = True
                json_result["published"] = 1

                if parsed_args.json:
                    print(json.dumps(json_result, indent=2))
                elif not parsed_args.verbose:
                    if parsed_args.dry_run:
                        console.print("[yellow]Dry run:[/yellow] Would publish 1 report")
                    else:
                        console.print(
                            "[green]✓[/green] Report published successfully"
                        )
                        if result.get("test_run_id"):
                            console.print(f"  Test run ID: {result['test_run_id']}")

                return 0
            else:
                json_result["failed"] = 1

                if parsed_args.json:
                    print(json.dumps(json_result, indent=2))
                elif not parsed_args.verbose:
                    console.print("[red]✗[/red] Failed to publish report")
                    if result.get("error"):
                        console.print(f"  Error: {result['error']}")

                return 1

        elif parsed_args.queue:
            # Queue mode
            storage_path = parsed_args.storage_path or get_default_storage_path()
            storage = ReportStorage(storage_path=storage_path)

            queued_count = len(storage.list_queued_reports())

            if queued_count == 0:
                if parsed_args.json:
                    json_result["success"] = True
                    json_result["message"] = "No reports in queue"
                    print(json.dumps(json_result, indent=2))
                else:
                    console.print("[yellow]No reports in queue[/yellow]")
                return 0

            if not parsed_args.json and not parsed_args.dry_run:
                console.print(
                    f"[bold]Publishing {queued_count} queued report(s)...[/bold]"
                )

            success_count, failure_count, results = publish_queue(
                storage=storage,
                client=client,
                dry_run=parsed_args.dry_run,
                verbose=parsed_args.verbose,
                json_output=parsed_args.json,
            )

            json_result["published"] = success_count
            json_result["failed"] = failure_count
            json_result["results"] = results
            json_result["success"] = failure_count == 0

            if parsed_args.json:
                print(json.dumps(json_result, indent=2))
            elif not parsed_args.verbose:
                if parsed_args.dry_run:
                    console.print(
                        f"[yellow]Dry run:[/yellow] Would publish {queued_count} report(s)"
                    )
                else:
                    if failure_count == 0:
                        console.print(
                            f"[green]✓[/green] All {success_count} report(s) published successfully"
                        )
                    elif success_count == 0:
                        console.print(
                            f"[red]✗[/red] All {failure_count} report(s) failed to publish"
                        )
                    else:
                        console.print(
                            f"[yellow]⚠[/yellow] Published {success_count}, failed {failure_count}"
                        )

            # Exit codes
            if failure_count == 0:
                return 0  # All success
            elif success_count == 0:
                return 1  # All failed
            else:
                return 2  # Partial success

        return 0

    except SystemExit:
        # Re-raise SystemExit from argparse
        raise

    except Exception as e:
        # Handle unexpected errors
        if debug:
            raise

        if parsed_args.json if "parsed_args" in dir() else False:
            error_result = {
                "success": False,
                "error": str(e),
            }
            print(json.dumps(error_result, indent=2))
        else:
            console_err.print("[red]Unexpected error:[/red]")
            console_err.print(f"  {type(e).__name__}: {e}")
            console_err.print("\n[yellow]This is likely a bug in pytest-jux[/yellow]")
            console_err.print("Please report this at:")
            console_err.print("  https://github.com/jrjsmrtn/pytest-jux/issues")
            console_err.print("\n[dim]Tip: Run with JUX_DEBUG=1 for more details[/dim]")

        return 1


if __name__ == "__main__":
    sys.exit(main())
