# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""User-friendly error handling for pytest-jux CLI commands.

This module provides structured error handling with:
- Clear, actionable error messages
- Error codes for programmatic handling
- Suggestions for fixing common problems
- Consistent formatting across all commands
"""

import sys
from enum import Enum
from pathlib import Path
from typing import NoReturn

from rich.console import Console

console_err = Console(stderr=True)


class ErrorCode(Enum):
    """Error codes for programmatic error handling."""

    # File errors (1xx)
    FILE_NOT_FOUND = 101
    FILE_PERMISSION_DENIED = 102
    FILE_ALREADY_EXISTS = 103
    DIRECTORY_NOT_FOUND = 104

    # Key/Certificate errors (2xx)
    KEY_NOT_FOUND = 201
    KEY_INVALID_FORMAT = 202
    KEY_PERMISSION_DENIED = 203
    CERT_NOT_FOUND = 211
    CERT_INVALID_FORMAT = 212
    CERT_EXPIRED = 213

    # XML errors (3xx)
    XML_PARSE_ERROR = 301
    XML_INVALID_STRUCTURE = 302
    XML_SIGNATURE_MISSING = 303
    XML_SIGNATURE_INVALID = 304

    # Configuration errors (4xx)
    CONFIG_NOT_FOUND = 401
    CONFIG_INVALID_SYNTAX = 402
    CONFIG_INVALID_VALUE = 403
    CONFIG_MISSING_REQUIRED = 404

    # Storage errors (5xx)
    STORAGE_NOT_FOUND = 501
    STORAGE_PERMISSION_DENIED = 502
    STORAGE_FULL = 503
    REPORT_NOT_FOUND = 511

    # Generic errors (9xx)
    INVALID_ARGUMENT = 901
    OPERATION_FAILED = 902
    UNEXPECTED_ERROR = 999


class JuxError(Exception):
    """Base exception for pytest-jux errors with user-friendly messaging."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        suggestions: list[str] | None = None,
        details: str | None = None,
    ):
        """Initialize error with user-friendly information.

        Args:
            message: Main error message (what went wrong)
            error_code: Error code for programmatic handling
            suggestions: List of actionable suggestions for fixing the error
            details: Additional technical details (optional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details

    def format_error(self) -> str:
        """Format error message for CLI display.

        Returns:
            Formatted error message with suggestions
        """
        lines = [f"[red]Error:[/red] {self.message}"]

        if self.details:
            lines.append(f"\n{self.details}")

        if self.suggestions:
            lines.append("\n[yellow]Possible solutions:[/yellow]")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        lines.append(f"\n[dim]Error code: {self.error_code.name}[/dim]")

        return "\n".join(lines)

    def print_error(self) -> None:
        """Print formatted error to stderr."""
        console_err.print(self.format_error())

    def print_and_exit(self, exit_code: int = 1) -> NoReturn:
        """Print formatted error and exit.

        Args:
            exit_code: Exit code (default: 1)
        """
        self.print_error()
        sys.exit(exit_code)


# File errors


class FileNotFoundError(JuxError):
    """File not found error with suggestions."""

    def __init__(self, file_path: Path, file_type: str = "file"):
        """Initialize file not found error.

        Args:
            file_path: Path to missing file
            file_type: Type of file (for better messaging)
        """
        suggestions = [
            f"Check that the {file_type} path is correct",
            f"Verify the {file_type} exists at the specified location",
        ]

        if file_type in ("key", "private key"):
            suggestions.append(f"Generate a new key: jux-keygen --output {file_path}")
        elif file_type == "certificate":
            suggestions.append("Generate certificate with key: jux-keygen --cert")

        super().__init__(
            message=f"{file_type.capitalize()} not found",
            error_code=ErrorCode.FILE_NOT_FOUND,
            suggestions=suggestions,
            details=f"Path: {file_path}",
        )


class FilePermissionError(JuxError):
    """File permission denied error."""

    def __init__(self, file_path: Path, operation: str = "access"):
        """Initialize permission error.

        Args:
            file_path: Path to file
            operation: Operation that failed (read, write, execute)
        """
        super().__init__(
            message=f"Permission denied: cannot {operation} file",
            error_code=ErrorCode.FILE_PERMISSION_DENIED,
            suggestions=[
                f"Check file permissions: ls -la {file_path}",
                f"Ensure you have {operation} access to the file",
                "Run with appropriate user permissions",
            ],
            details=f"Path: {file_path}",
        )


class FileAlreadyExistsError(JuxError):
    """File already exists error."""

    def __init__(self, file_path: Path, command_hint: str | None = None):
        """Initialize file exists error.

        Args:
            file_path: Path to existing file
            command_hint: Hint for forcing overwrite (e.g., "--force")
        """
        suggestions = [
            "Choose a different output path",
            "Remove the existing file first",
        ]

        if command_hint:
            suggestions.append(f"Use {command_hint} to overwrite existing file")

        super().__init__(
            message="File already exists",
            error_code=ErrorCode.FILE_ALREADY_EXISTS,
            suggestions=suggestions,
            details=f"Path: {file_path}",
        )


# Key/Certificate errors


class KeyNotFoundError(FileNotFoundError):
    """Private key not found error."""

    def __init__(self, key_path: Path):
        """Initialize key not found error.

        Args:
            key_path: Path to missing key
        """
        super().__init__(key_path, file_type="private key")


class KeyInvalidFormatError(JuxError):
    """Invalid key format error."""

    def __init__(self, key_path: Path, expected_format: str = "PEM"):
        """Initialize invalid key format error.

        Args:
            key_path: Path to invalid key
            expected_format: Expected key format
        """
        super().__init__(
            message=f"Invalid key format (expected {expected_format})",
            error_code=ErrorCode.KEY_INVALID_FORMAT,
            suggestions=[
                f"Ensure key is in {expected_format} format",
                "Generate a new key: jux-keygen --output <path>",
                "Convert key to PEM format using openssl",
            ],
            details=f"Path: {key_path}",
        )


class CertNotFoundError(FileNotFoundError):
    """Certificate not found error."""

    def __init__(self, cert_path: Path):
        """Initialize certificate not found error.

        Args:
            cert_path: Path to missing certificate
        """
        super().__init__(cert_path, file_type="certificate")


class CertInvalidFormatError(JuxError):
    """Invalid certificate format error."""

    def __init__(self, cert_path: Path):
        """Initialize invalid certificate format error.

        Args:
            cert_path: Path to invalid certificate
        """
        super().__init__(
            message="Invalid certificate format (expected PEM)",
            error_code=ErrorCode.CERT_INVALID_FORMAT,
            suggestions=[
                "Ensure certificate is in PEM format",
                "Generate new certificate: jux-keygen --cert",
                "Convert certificate to PEM format using openssl",
            ],
            details=f"Path: {cert_path}",
        )


# XML errors


class XMLParseError(JuxError):
    """XML parsing error."""

    def __init__(self, xml_path: Path | None, parse_error: str):
        """Initialize XML parse error.

        Args:
            xml_path: Path to XML file (None for stdin)
            parse_error: Parse error message
        """
        source = str(xml_path) if xml_path else "stdin"

        super().__init__(
            message="Failed to parse XML file",
            error_code=ErrorCode.XML_PARSE_ERROR,
            suggestions=[
                "Verify the file contains valid XML",
                "Check for syntax errors in the XML",
                "Ensure the file is a valid JUnit XML report",
            ],
            details=f"Source: {source}\nError: {parse_error}",
        )


class XMLSignatureMissingError(JuxError):
    """XML signature missing error."""

    def __init__(self, xml_path: Path | None):
        """Initialize signature missing error.

        Args:
            xml_path: Path to XML file (None for stdin)
        """
        source = str(xml_path) if xml_path else "stdin"

        super().__init__(
            message="XML file is not signed (no signature found)",
            error_code=ErrorCode.XML_SIGNATURE_MISSING,
            suggestions=[
                "Sign the report first: jux-sign --input <file> --key <key>",
                "Verify you're using the correct (signed) report file",
                "Check that signing completed successfully",
            ],
            details=f"Source: {source}",
        )


class XMLSignatureInvalidError(JuxError):
    """XML signature invalid error."""

    def __init__(self, reason: str):
        """Initialize signature invalid error.

        Args:
            reason: Reason why signature is invalid
        """
        super().__init__(
            message="Signature verification failed",
            error_code=ErrorCode.XML_SIGNATURE_INVALID,
            suggestions=[
                "Ensure you're using the correct certificate",
                "Check that the report hasn't been modified after signing",
                "Verify the signing key matches the verification certificate",
                "Re-sign the report if it has been tampered with",
            ],
            details=f"Reason: {reason}",
        )


# Configuration errors


class ConfigNotFoundError(JuxError):
    """Configuration file not found error."""

    def __init__(self, config_path: Path):
        """Initialize config not found error.

        Args:
            config_path: Path to missing config
        """
        super().__init__(
            message="Configuration file not found",
            error_code=ErrorCode.CONFIG_NOT_FOUND,
            suggestions=[
                "Create configuration: jux-config init",
                "Use environment variables: export JUX_KEY_PATH=<path>",
                "Specify options via command-line arguments",
            ],
            details=f"Path: {config_path}",
        )


class ConfigInvalidSyntaxError(JuxError):
    """Configuration syntax error."""

    def __init__(self, config_path: Path, syntax_error: str):
        """Initialize config syntax error.

        Args:
            config_path: Path to config file
            syntax_error: Syntax error description
        """
        super().__init__(
            message="Configuration file has invalid syntax",
            error_code=ErrorCode.CONFIG_INVALID_SYNTAX,
            suggestions=[
                "Check TOML syntax: https://toml.io/",
                "Validate configuration: jux-config validate",
                "Re-initialize configuration: jux-config init --force",
            ],
            details=f"Path: {config_path}\nError: {syntax_error}",
        )


# Storage errors


class StorageNotFoundError(JuxError):
    """Storage directory not found error."""

    def __init__(self, storage_path: Path):
        """Initialize storage not found error.

        Args:
            storage_path: Path to storage directory
        """
        super().__init__(
            message="Storage directory not found",
            error_code=ErrorCode.STORAGE_NOT_FOUND,
            suggestions=[
                "Storage will be created automatically on first use",
                f"Create manually: mkdir -p {storage_path}",
                "Check storage path configuration",
            ],
            details=f"Path: {storage_path}",
        )


class ReportNotFoundError(JuxError):
    """Report not found in cache."""

    def __init__(self, report_hash: str):
        """Initialize report not found error.

        Args:
            report_hash: Canonical hash of missing report
        """
        super().__init__(
            message="Report not found in cache",
            error_code=ErrorCode.REPORT_NOT_FOUND,
            suggestions=[
                "Check the report hash is correct",
                "List all cached reports: jux-cache list",
                "The report may have been cleaned up (check age)",
            ],
            details=f"Hash: {report_hash}",
        )


# Generic errors


class InvalidArgumentError(JuxError):
    """Invalid command-line argument error."""

    def __init__(self, argument: str, reason: str, valid_values: list[str] | None = None):
        """Initialize invalid argument error.

        Args:
            argument: Argument name
            reason: Why it's invalid
            valid_values: List of valid values (optional)
        """
        suggestions = [f"Check the {argument} value is correct"]

        if valid_values:
            suggestions.append(f"Valid values: {', '.join(valid_values)}")
            suggestions.append("Run with --help for more information")

        details = f"Argument: {argument}\nReason: {reason}"
        if valid_values:
            details += f"\nValid values: {', '.join(valid_values)}"

        super().__init__(
            message=f"Invalid argument: {argument}",
            error_code=ErrorCode.INVALID_ARGUMENT,
            suggestions=suggestions,
            details=details,
        )


def handle_unexpected_error(error: Exception, debug: bool = False) -> NoReturn:
    """Handle unexpected errors with user-friendly messaging.

    Args:
        error: The unexpected exception
        debug: If True, show full traceback

    Raises:
        SystemExit: Always exits with code 1
    """
    if debug:
        # In debug mode, show full traceback
        raise error

    # User-friendly error message
    console_err.print("[red]Unexpected error:[/red]")
    console_err.print(f"  {type(error).__name__}: {error}")
    console_err.print("\n[yellow]This is likely a bug in pytest-jux[/yellow]")
    console_err.print("Please report this at:")
    console_err.print("  https://github.com/jrjsmrtn/pytest-jux/issues")
    console_err.print("\nInclude the error message above and the command you ran.")
    console_err.print("\n[dim]Tip: Run with JUX_DEBUG=1 for more details[/dim]")

    sys.exit(1)
