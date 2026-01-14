# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Local filesystem storage for signed test reports."""

import os
import platform
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


class StorageError(Exception):
    """Raised when storage operations fail."""

    pass


def get_default_storage_path() -> Path:
    """Get platform-appropriate default storage path following XDG Base Directory.

    Returns:
        Path: Absolute path to default storage directory

    Examples:
        - macOS: ~/Library/Application Support/jux
        - Linux: ~/.local/share/jux
        - Windows: %LOCALAPPDATA%/jux
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        # Use LOCALAPPDATA if available, otherwise fall back to AppData/Local
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            base = Path(local_appdata)
        else:
            base = Path.home() / "AppData" / "Local"
    else:  # Linux and other Unix-like systems
        # Follow XDG Base Directory Specification
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            base = Path(xdg_data_home)
        else:
            base = Path.home() / ".local" / "share"

    return base / "jux"


class ReportStorage:
    """Manages local filesystem storage for test reports and metadata."""

    def __init__(self, storage_path: Path | None = None) -> None:
        """Initialize report storage.

        Args:
            storage_path: Custom storage directory path.
                         If None, uses platform default.
        """
        self.storage_path = storage_path or get_default_storage_path()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "reports").mkdir(exist_ok=True)
        (self.storage_path / "queue").mkdir(exist_ok=True)

    def _write_file_atomic(self, path: Path, content: bytes, mode: int = 0o600) -> None:
        """Write file atomically using temp file + rename.

        Args:
            path: Target file path
            content: File content
            mode: File permissions (Unix only)

        Raises:
            StorageError: If write operation fails
        """
        try:
            # Create temp file in same directory to ensure same filesystem
            fd, temp_path = tempfile.mkstemp(
                dir=path.parent, prefix=".tmp_", suffix=".tmp"
            )
            try:
                # Write content
                os.write(fd, content)
                os.close(fd)

                # Set permissions (Unix only)
                if platform.system() != "Windows":
                    os.chmod(temp_path, mode)

                # Atomic rename
                os.replace(temp_path, path)
            except Exception:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise
        except Exception as e:
            raise StorageError(f"Failed to write file {path}: {e}") from e

    def store_report(self, xml_content: bytes, canonical_hash: str) -> None:
        """Store test report.

        Metadata is embedded in the XML content as <properties> elements
        and is cryptographically signed with XMLDSig.

        Args:
            xml_content: JUnit XML content (includes metadata and signature)
            canonical_hash: Canonical hash identifier

        Raises:
            StorageError: If storage operation fails
        """
        # Store report XML (includes embedded metadata in <properties>)
        report_file = self.storage_path / "reports" / f"{canonical_hash}.xml"
        self._write_file_atomic(report_file, xml_content)

    def get_report(self, canonical_hash: str) -> bytes:
        """Retrieve stored report.

        Args:
            canonical_hash: Canonical hash identifier

        Returns:
            Report XML content

        Raises:
            StorageError: If report doesn't exist or read fails
        """
        report_file = self.storage_path / "reports" / f"{canonical_hash}.xml"
        if not report_file.exists():
            raise StorageError(f"Report not found: {canonical_hash}")

        try:
            return report_file.read_bytes()
        except Exception as e:
            raise StorageError(f"Failed to read report {canonical_hash}: {e}") from e

    def queue_report(self, xml_content: bytes, canonical_hash: str) -> None:
        """Queue report for later publishing (offline mode).

        Metadata is embedded in the XML content as <properties> elements.

        Args:
            xml_content: JUnit XML content (includes metadata and signature)
            canonical_hash: Canonical hash identifier

        Raises:
            StorageError: If queuing operation fails
        """
        # Store report in queue directory (includes embedded metadata)
        queue_file = self.storage_path / "queue" / f"{canonical_hash}.xml"
        self._write_file_atomic(queue_file, xml_content)

    def list_reports(self) -> list[str]:
        """List all stored report hashes.

        Returns:
            List of canonical hash identifiers
        """
        reports_dir = self.storage_path / "reports"
        if not reports_dir.exists():
            return []

        return [
            f.stem for f in reports_dir.glob("*.xml") if f.is_file() and f.stem != ""
        ]

    def list_queued_reports(self) -> list[str]:
        """List all queued report hashes.

        Returns:
            List of canonical hash identifiers
        """
        queue_dir = self.storage_path / "queue"
        if not queue_dir.exists():
            return []

        return [f.stem for f in queue_dir.glob("*.xml") if f.is_file() and f.stem != ""]

    def dequeue_report(self, canonical_hash: str) -> None:
        """Move report from queue to reports (mark as published).

        Args:
            canonical_hash: Canonical hash identifier

        Raises:
            StorageError: If dequeue operation fails
        """
        queue_file = self.storage_path / "queue" / f"{canonical_hash}.xml"

        if not queue_file.exists():
            raise StorageError(f"Queued report not found: {canonical_hash}")

        try:
            # Read queued report (includes embedded metadata)
            xml_content = queue_file.read_bytes()

            # Store in reports directory
            self.store_report(xml_content, canonical_hash)

            # Remove from queue
            queue_file.unlink()
        except Exception as e:
            raise StorageError(f"Failed to dequeue report {canonical_hash}: {e}") from e

    def delete_report(self, canonical_hash: str) -> None:
        """Delete report.

        Metadata is embedded in the XML file, so only the XML file needs to be deleted.

        Args:
            canonical_hash: Canonical hash identifier

        Note:
            Does not raise error if report doesn't exist
        """
        report_file = self.storage_path / "reports" / f"{canonical_hash}.xml"

        # missing_ok=True silently ignores if file doesn't exist
        report_file.unlink(missing_ok=True)

    def report_exists(self, canonical_hash: str) -> bool:
        """Check if report exists in storage.

        Args:
            canonical_hash: Canonical hash identifier

        Returns:
            True if report exists, False otherwise
        """
        report_file = self.storage_path / "reports" / f"{canonical_hash}.xml"
        return report_file.exists()

    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics:
                - total_reports: Number of stored reports
                - queued_reports: Number of queued reports
                - total_size: Total storage size in bytes
                - oldest_report: Timestamp of oldest report
        """
        stats: dict[str, Any] = {
            "total_reports": 0,
            "queued_reports": 0,
            "total_size": 0,
            "oldest_report": None,
        }

        # Count reports
        reports_dir = self.storage_path / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*.xml"))
            stats["total_reports"] = len(report_files)

            # Calculate total size
            for f in report_files:
                if f.is_file():
                    stats["total_size"] += f.stat().st_size

            # Find oldest report
            if report_files:
                oldest = min(report_files, key=lambda f: f.stat().st_mtime)
                stats["oldest_report"] = datetime.fromtimestamp(
                    oldest.stat().st_mtime
                ).isoformat()

        # Count queued reports
        queue_dir = self.storage_path / "queue"
        if queue_dir.exists():
            queued_files = list(queue_dir.glob("*.xml"))
            stats["queued_reports"] = len(queued_files)

            # Add queue size to total
            for f in queued_files:
                if f.is_file():
                    stats["total_size"] += f.stat().st_size

        return stats
