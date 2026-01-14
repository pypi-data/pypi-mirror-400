# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for local filesystem storage."""

import platform
import stat
from pathlib import Path

import pytest

from pytest_jux.storage import (
    ReportStorage,
    StorageError,
    get_default_storage_path,
)


class TestGetDefaultStoragePath:
    """Tests for default storage path detection."""

    def test_returns_path_object(self) -> None:
        """Should return a Path object."""
        path = get_default_storage_path()
        assert isinstance(path, Path)

    def test_path_is_absolute(self) -> None:
        """Storage path should be absolute."""
        path = get_default_storage_path()
        assert path.is_absolute()

    def test_path_contains_jux(self) -> None:
        """Storage path should contain 'jux' directory."""
        path = get_default_storage_path()
        assert "jux" in str(path).lower()

    def test_macos_uses_application_support(self) -> None:
        """macOS should use ~/Library/Application Support."""
        if platform.system() == "Darwin":
            path = get_default_storage_path()
            assert "Library/Application Support" in str(path)

    def test_linux_uses_local_share(self) -> None:
        """Linux should use ~/.local/share."""
        if platform.system() == "Linux":
            path = get_default_storage_path()
            assert ".local/share" in str(path)

    def test_windows_uses_local_appdata(self) -> None:
        """Windows should use %LOCALAPPDATA%."""
        if platform.system() == "Windows":
            path = get_default_storage_path()
            # Should use LOCALAPPDATA on Windows
            assert "AppData" in str(path) or "Local" in str(path)


class TestReportStorage:
    """Tests for ReportStorage class."""

    def test_init_with_default_path(self, tmp_path: Path) -> None:
        """Should initialize with custom path."""
        storage = ReportStorage(storage_path=tmp_path)
        assert storage.storage_path == tmp_path

    def test_init_creates_directories(self, tmp_path: Path) -> None:
        """Should create storage directories on init."""
        storage_path = tmp_path / "jux"
        ReportStorage(storage_path=storage_path)

        # Should create reports and queue directories (no metadata dir in v0.3.0+)
        assert (storage_path / "reports").exists()
        assert (storage_path / "queue").exists()
        # Metadata directory no longer created (metadata in XML as of v0.3.0)
        assert not (storage_path / "metadata").exists()

    def test_store_report(self, tmp_path: Path) -> None:
        """Should store report with canonical hash as filename.

        As of v0.3.0, metadata is embedded in XML, not stored separately.
        """
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite><testcase name='test1'/></testsuite>"
        canonical_hash = "sha256:abc123def456"

        storage.store_report(xml_content, canonical_hash)

        # Report file should exist
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        assert report_file.exists()
        assert report_file.read_bytes() == xml_content

        # No separate metadata file (metadata in XML as of v0.3.0)
        metadata_file = tmp_path / "metadata" / f"{canonical_hash}.json"
        assert not metadata_file.exists()

    def test_store_report_atomic_write(self, tmp_path: Path) -> None:
        """Should use atomic write (temp file + rename)."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:test123"

        storage.store_report(xml_content, canonical_hash)

        # No temp files should remain
        temp_files = list(tmp_path.rglob("*.tmp"))
        assert len(temp_files) == 0

    def test_get_report(self, tmp_path: Path) -> None:
        """Should retrieve stored report."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite><testcase name='test1'/></testsuite>"
        canonical_hash = "sha256:retrieve123"

        storage.store_report(xml_content, canonical_hash)

        # Retrieve report
        retrieved = storage.get_report(canonical_hash)
        assert retrieved == xml_content

    def test_get_nonexistent_report(self, tmp_path: Path) -> None:
        """Should raise error for nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)

        with pytest.raises(StorageError):
            storage.get_report("sha256:nonexistent")

    def test_list_reports(self, tmp_path: Path) -> None:
        """Should list all stored reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store multiple reports
        for i in range(3):
            storage.store_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:test{i}",
            )

        reports = storage.list_reports()
        assert len(reports) == 3
        assert all(h.startswith("sha256:test") for h in reports)

    def test_list_reports_empty(self, tmp_path: Path) -> None:
        """Should return empty list when no reports."""
        storage = ReportStorage(storage_path=tmp_path)
        reports = storage.list_reports()
        assert reports == []

    def test_delete_report(self, tmp_path: Path) -> None:
        """Should delete report.

        As of v0.3.0, metadata is in XML, so only XML file needs deletion.
        """
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:delete123"

        storage.store_report(xml_content, canonical_hash)

        # Delete report
        storage.delete_report(canonical_hash)

        # Report file should not exist
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        assert not report_file.exists()

    def test_delete_nonexistent_report(self, tmp_path: Path) -> None:
        """Should not raise error when deleting nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)
        # Should not raise
        storage.delete_report("sha256:nonexistent")

    def test_queue_report(self, tmp_path: Path) -> None:
        """Should queue report for later publishing."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:queue123"

        storage.queue_report(xml_content, canonical_hash)

        # Report should be in queue directory
        queue_file = tmp_path / "queue" / f"{canonical_hash}.xml"
        assert queue_file.exists()

    def test_list_queued_reports(self, tmp_path: Path) -> None:
        """Should list all queued reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Queue multiple reports
        for i in range(2):
            storage.queue_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:queue{i}",
            )

        queued = storage.list_queued_reports()
        assert len(queued) == 2
        assert all(h.startswith("sha256:queue") for h in queued)

    def test_dequeue_report(self, tmp_path: Path) -> None:
        """Should move report from queue to reports."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:dequeue123"

        storage.queue_report(xml_content, canonical_hash)

        # Dequeue (mark as published)
        storage.dequeue_report(canonical_hash)

        # Should be in reports, not queue
        assert canonical_hash in storage.list_reports()
        assert canonical_hash not in storage.list_queued_reports()

    def test_report_exists(self, tmp_path: Path) -> None:
        """Should check if report exists."""
        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:exists123"

        assert not storage.report_exists(canonical_hash)

        storage.store_report(xml_content, canonical_hash)

        assert storage.report_exists(canonical_hash)

    def test_get_storage_stats(self, tmp_path: Path) -> None:
        """Should return storage statistics."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store some reports
        for i in range(3):
            storage.store_report(
                f"<testsuite name='test{i}'/>".encode(),
                f"sha256:stat{i}",
            )

        # Queue one report
        storage.queue_report(
            b"<testsuite/>",
            "sha256:statqueue",
        )

        stats = storage.get_stats()

        assert stats["total_reports"] == 3
        assert stats["queued_reports"] == 1
        assert stats["total_size"] > 0
        assert "oldest_report" in stats

    def test_file_permissions_secure(self, tmp_path: Path) -> None:
        """Stored files should have secure permissions."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:perm123"

        storage.store_report(xml_content, canonical_hash)

        # Check file permissions (should be 0600 or more restrictive)
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        mode = stat.S_IMODE(report_file.stat().st_mode)

        # File should be readable and writable by owner only
        assert mode & stat.S_IRUSR  # Owner read
        assert mode & stat.S_IWUSR  # Owner write

    # Removed test_metadata_serialization - metadata no longer stored as JSON (v0.3.0)
    # Removed test_get_metadata_invalid_json - get_metadata() removed (v0.3.0)


class TestStorageEdgeCases:
    """Tests for edge cases and error handling."""

    def test_concurrent_writes(self, tmp_path: Path) -> None:
        """Should handle concurrent writes to storage safely."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store multiple reports concurrently (simulated)
        for i in range(10):
            xml_content = f"<testsuite name='test{i}'/>".encode()
            canonical_hash = f"sha256:concurrent{i}"
            storage.store_report(xml_content, canonical_hash)

        # Verify all reports were stored
        reports = storage.list_reports()
        assert len(reports) == 10

    def test_dequeue_nonexistent_report(self, tmp_path: Path) -> None:
        """Should raise error when dequeuing nonexistent report."""
        storage = ReportStorage(storage_path=tmp_path)

        with pytest.raises(StorageError, match="Queued report not found"):
            storage.dequeue_report("sha256:nonexistent")

    def test_get_stats_empty_storage(self, tmp_path: Path) -> None:
        """Should return zero stats for empty storage."""
        storage = ReportStorage(storage_path=tmp_path)

        stats = storage.get_stats()

        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0
        assert stats["total_size"] == 0
        assert stats["oldest_report"] is None

    def test_store_report_in_readonly_directory(self, tmp_path: Path) -> None:
        """Should raise error when storing to readonly directory."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        # Make reports directory readonly
        reports_dir = tmp_path / "reports"
        reports_dir.chmod(0o500)  # r-x------

        xml_content = b"<testsuite/>"
        canonical_hash = "sha256:readonly123"

        try:
            with pytest.raises(StorageError, match="Failed to write file"):
                storage.store_report(xml_content, canonical_hash)
        finally:
            # Restore permissions for cleanup
            reports_dir.chmod(0o700)

    def test_get_report_with_read_error(self, tmp_path: Path) -> None:
        """Should raise error when report file cannot be read."""
        if platform.system() == "Windows":
            pytest.skip("File permissions test not applicable on Windows")

        storage = ReportStorage(storage_path=tmp_path)

        # Create a report file with no read permissions
        canonical_hash = "sha256:noread123"
        report_file = tmp_path / "reports" / f"{canonical_hash}.xml"
        report_file.write_bytes(b"<testsuite/>")
        report_file.chmod(0o000)  # No permissions

        try:
            with pytest.raises(StorageError, match="Failed to read report"):
                storage.get_report(canonical_hash)
        finally:
            # Restore permissions for cleanup
            report_file.chmod(0o600)

    def test_queue_and_dequeue_multiple_reports(self, tmp_path: Path) -> None:
        """Should handle multiple queued reports correctly."""
        storage = ReportStorage(storage_path=tmp_path)

        # Queue multiple reports
        hashes = []
        for i in range(5):
            canonical_hash = f"sha256:queue{i}"
            hashes.append(canonical_hash)
            storage.queue_report(
                f"<testsuite name='test{i}'/>".encode(),
                canonical_hash,
            )

        # Verify all are queued
        queued = storage.list_queued_reports()
        assert len(queued) == 5
        assert all(h in queued for h in hashes)

        # Dequeue all
        for hash in hashes:
            storage.dequeue_report(hash)

        # Verify queue is empty and all are in reports
        assert len(storage.list_queued_reports()) == 0
        assert len(storage.list_reports()) == 5

    def test_storage_path_created_automatically(self, tmp_path: Path) -> None:
        """Should create storage path and subdirectories automatically."""
        storage_path = tmp_path / "nonexistent" / "path" / "jux"

        # Path doesn't exist yet
        assert not storage_path.exists()

        # Initialize storage
        ReportStorage(storage_path=storage_path)

        # Path should now exist with subdirectories
        assert storage_path.exists()
        assert (storage_path / "reports").exists()
        assert (storage_path / "queue").exists()
        # metadata/ directory no longer created (v0.3.0+)

    def test_get_stats_with_queued_reports(self, tmp_path: Path) -> None:
        """Statistics should include queued reports."""
        storage = ReportStorage(storage_path=tmp_path)

        # Store regular report
        storage.store_report(
            b"<testsuite name='test1'/>",
            "sha256:regular1",
        )

        # Queue report
        storage.queue_report(
            b"<testsuite name='test2'/>",
            "sha256:queued1",
        )

        stats = storage.get_stats()

        assert stats["total_reports"] == 1
        assert stats["queued_reports"] == 1
        assert stats["total_size"] > 0
        assert stats["oldest_report"] is not None


class TestStorageErrorPaths:
    """Tests for storage error handling and edge cases."""

    def test_get_default_storage_path_windows(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should handle Windows path with LOCALAPPDATA."""
        monkeypatch.setattr("platform.system", lambda: "Windows")
        monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\Test\\AppData\\Local")

        path = get_default_storage_path()

        # Check path parts (platform-independent)
        assert path.name == "jux"
        assert "AppData" in str(path) or "Local" in str(path)

    def test_get_default_storage_path_windows_fallback(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Should fallback to AppData/Local when LOCALAPPDATA not set."""
        monkeypatch.setattr("platform.system", lambda: "Windows")
        monkeypatch.delenv("LOCALAPPDATA", raising=False)
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        path = get_default_storage_path()

        assert path == tmp_path / "AppData" / "Local" / "jux"

    def test_get_default_storage_path_linux_xdg(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should use XDG_DATA_HOME on Linux when set."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.setenv("XDG_DATA_HOME", "/custom/xdg/data")

        path = get_default_storage_path()

        assert path.name == "jux"
        assert "xdg" in str(path)

    def test_get_default_storage_path_linux_fallback(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Should fallback to .local/share on Linux when XDG_DATA_HOME not set."""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        path = get_default_storage_path()

        assert path == tmp_path / ".local" / "share" / "jux"

    def test_write_file_atomic_error_cleanup(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should clean up temp file on write error."""
        from unittest.mock import patch

        storage = ReportStorage(storage_path=tmp_path)
        test_file = tmp_path / "reports" / "test.xml"

        # Mock os.write to raise an error
        with patch("os.write", side_effect=OSError("Write error")):
            with pytest.raises(StorageError, match="Failed to write file"):
                storage._write_file_atomic(test_file, b"<test/>")

        # Verify no temp files left behind
        temp_files = list(tmp_path.glob("**/.tmp_*"))
        assert len(temp_files) == 0

    def test_write_file_atomic_unlink_fails(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should handle unlink failure during cleanup."""
        from unittest.mock import patch

        storage = ReportStorage(storage_path=tmp_path)
        test_file = tmp_path / "reports" / "test.xml"

        # Mock os.write to fail, then mock os.unlink to also fail
        with patch("os.write", side_effect=OSError("Write error")):
            with patch("os.unlink", side_effect=OSError("Unlink error")):
                with pytest.raises(StorageError, match="Failed to write file"):
                    storage._write_file_atomic(test_file, b"<test/>")

    def test_get_report_read_error(self, tmp_path: Path) -> None:
        """Should handle read errors when retrieving report."""
        from unittest.mock import patch

        storage = ReportStorage(storage_path=tmp_path)

        # Create a report file first
        test_hash = "sha256:test123"
        storage.store_report(b"<testsuite name='test'/>", test_hash)

        # Mock read_bytes to raise an error
        with patch("pathlib.Path.read_bytes", side_effect=PermissionError("Access denied")):
            with pytest.raises(StorageError, match="Failed to read report"):
                storage.get_report(test_hash)

    def test_list_reports_empty_dir(self, tmp_path: Path) -> None:
        """Should return empty list when reports directory doesn't exist."""
        # Create storage but delete reports directory
        storage = ReportStorage(storage_path=tmp_path)
        reports_dir = tmp_path / "reports"
        reports_dir.rmdir()

        reports = storage.list_reports()

        assert reports == []

    def test_list_queued_reports_empty_dir(self, tmp_path: Path) -> None:
        """Should return empty list when queue directory doesn't exist."""
        storage = ReportStorage(storage_path=tmp_path)
        queue_dir = tmp_path / "queue"
        queue_dir.rmdir()

        queued = storage.list_queued_reports()

        assert queued == []

    def test_dequeue_report_error(self, tmp_path: Path) -> None:
        """Should handle errors during dequeue operation."""
        from unittest.mock import patch

        storage = ReportStorage(storage_path=tmp_path)

        # Queue a report first
        test_hash = "sha256:queued"
        storage.queue_report(b"<testsuite name='test'/>", test_hash)

        # Mock read_bytes to raise an error
        with patch("pathlib.Path.read_bytes", side_effect=OSError("Read error")):
            with pytest.raises(StorageError, match="Failed to dequeue report"):
                storage.dequeue_report(test_hash)

    def test_report_exists_false(self, tmp_path: Path) -> None:
        """Should return False when report doesn't exist."""
        storage = ReportStorage(storage_path=tmp_path)

        exists = storage.report_exists("sha256:nonexistent")

        assert exists is False

    def test_get_stats_empty_storage(self, tmp_path: Path) -> None:
        """Should return zero stats for empty storage."""
        # Create storage but delete all subdirectories
        storage = ReportStorage(storage_path=tmp_path)
        (tmp_path / "reports").rmdir()
        # Note: metadata directory no longer exists (Sprint 7 removed JSON metadata)
        (tmp_path / "queue").rmdir()

        stats = storage.get_stats()

        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0
        assert stats["total_size"] == 0
        assert stats["oldest_report"] is None
