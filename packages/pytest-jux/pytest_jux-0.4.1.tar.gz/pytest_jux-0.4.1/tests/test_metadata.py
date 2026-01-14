# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for environment metadata capture."""

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_jux.metadata import EnvironmentMetadata, capture_metadata


class TestEnvironmentMetadata:
    """Tests for EnvironmentMetadata class."""

    def test_capture_basic_metadata(self) -> None:
        """Should capture basic environment metadata."""
        metadata = capture_metadata()

        assert metadata.hostname is not None
        assert isinstance(metadata.hostname, str)
        assert len(metadata.hostname) > 0

        assert metadata.username is not None
        assert isinstance(metadata.username, str)
        assert len(metadata.username) > 0

        assert metadata.platform is not None
        assert isinstance(metadata.platform, str)
        assert len(metadata.platform) > 0

        assert metadata.python_version is not None
        assert isinstance(metadata.python_version, str)
        assert len(metadata.python_version) > 0

    def test_timestamp_format(self) -> None:
        """Timestamp should be in ISO 8601 format with UTC timezone."""
        metadata = capture_metadata()

        assert metadata.timestamp is not None
        # Should be ISO 8601 format with timezone
        # Example: 2025-10-17T10:30:00+00:00 or 2025-10-17T10:30:00Z
        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})"
        assert re.match(iso_pattern, metadata.timestamp)

        # Parse and verify it's UTC
        dt = datetime.fromisoformat(metadata.timestamp.replace("Z", "+00:00"))
        assert dt.tzinfo is not None

    def test_pytest_version_captured(self) -> None:
        """Should capture pytest version."""
        metadata = capture_metadata()

        assert metadata.pytest_version is not None
        assert isinstance(metadata.pytest_version, str)
        # Pytest version format: X.Y.Z
        assert re.match(r"\d+\.\d+\.\d+", metadata.pytest_version)

    def test_pytest_jux_version_captured(self) -> None:
        """Should capture pytest-jux version."""
        metadata = capture_metadata()

        assert metadata.pytest_jux_version is not None
        assert isinstance(metadata.pytest_jux_version, str)
        # pytest-jux version format: X.Y.Z
        assert re.match(r"\d+\.\d+\.\d+", metadata.pytest_jux_version)

    def test_python_version_format(self) -> None:
        """Python version should include version number."""
        metadata = capture_metadata()

        # Should contain something like "3.11.14" or similar
        assert re.search(r"3\.\d+\.\d+", metadata.python_version)

    def test_platform_contains_os_info(self) -> None:
        """Platform should contain OS information."""
        metadata = capture_metadata()

        # Should contain OS name (Linux, Darwin/macOS, Windows, etc.)
        platform_lower = metadata.platform.lower()
        assert any(
            os_name in platform_lower
            for os_name in ["linux", "darwin", "macos", "windows"]
        )

    def test_metadata_to_dict(self) -> None:
        """Should convert metadata to dictionary."""
        metadata = capture_metadata()
        data = metadata.to_dict()

        assert isinstance(data, dict)
        assert "hostname" in data
        assert "username" in data
        assert "platform" in data
        assert "python_version" in data
        assert "pytest_version" in data
        assert "pytest_jux_version" in data
        assert "timestamp" in data

    def test_metadata_to_json(self) -> None:
        """Should convert metadata to JSON."""
        metadata = capture_metadata()
        json_str = metadata.to_json()

        assert isinstance(json_str, str)

        # Parse JSON to verify it's valid
        data = json.loads(json_str)
        assert "hostname" in data
        assert "username" in data
        assert "timestamp" in data

    def test_metadata_with_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should capture environment variables when specified."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("CI_JOB_ID", "12345")
        monkeypatch.setenv("CI_COMMIT_SHA", "abc123")

        metadata = capture_metadata(
            include_env_vars=["CI", "CI_JOB_ID", "CI_COMMIT_SHA"]
        )

        assert metadata.env is not None
        assert isinstance(metadata.env, dict)
        assert metadata.env["CI"] == "true"
        assert metadata.env["CI_JOB_ID"] == "12345"
        assert metadata.env["CI_COMMIT_SHA"] == "abc123"

    def test_metadata_env_vars_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should handle missing environment variables gracefully."""
        # Request env vars that don't exist
        metadata = capture_metadata(include_env_vars=["NONEXISTENT_VAR"])

        assert metadata.env is not None
        assert isinstance(metadata.env, dict)
        # Missing vars should not be included
        assert "NONEXISTENT_VAR" not in metadata.env

    def test_metadata_env_vars_optional(self) -> None:
        """Environment variables should be optional."""
        metadata = capture_metadata()

        # env should be None or empty dict when not requested
        assert metadata.env is None or metadata.env == {}

    def test_metadata_to_dict_with_env_vars(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dictionary representation should include env vars."""
        monkeypatch.setenv("CI", "true")

        metadata = capture_metadata(include_env_vars=["CI"])
        data = metadata.to_dict()

        assert "env" in data
        assert data["env"]["CI"] == "true"

    def test_metadata_excludes_none_env(self) -> None:
        """Dictionary should not include env key when env is None."""
        metadata = capture_metadata()
        data = metadata.to_dict()

        # env should not be in dict if None
        if metadata.env is None:
            assert "env" not in data or data["env"] is None

    def test_timestamp_is_recent(self) -> None:
        """Timestamp should be recent (within last few seconds)."""
        metadata = capture_metadata()

        timestamp_dt = datetime.fromisoformat(metadata.timestamp.replace("Z", "+00:00"))
        now = datetime.now(UTC)

        # Timestamp should be within last 10 seconds
        diff = (now - timestamp_dt).total_seconds()
        assert 0 <= diff < 10

    def test_multiple_captures_same_non_time_fields(self) -> None:
        """Multiple captures should have same non-time fields."""
        metadata1 = capture_metadata()
        metadata2 = capture_metadata()

        # Non-time fields should be identical
        assert metadata1.hostname == metadata2.hostname
        assert metadata1.username == metadata2.username
        assert metadata1.platform == metadata2.platform
        assert metadata1.python_version == metadata2.python_version
        assert metadata1.pytest_version == metadata2.pytest_version
        assert metadata1.pytest_jux_version == metadata2.pytest_jux_version

        # Timestamps might differ slightly
        # Just verify both exist
        assert metadata1.timestamp is not None
        assert metadata2.timestamp is not None

    def test_metadata_equality(self) -> None:
        """Should support equality comparison."""
        metadata1 = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            project_name="test-project",
            env=None,
        )

        metadata2 = EnvironmentMetadata(
            hostname="test-host",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            project_name="test-project",
            env=None,
        )

        assert metadata1 == metadata2

    def test_metadata_inequality(self) -> None:
        """Should detect differences in metadata."""
        metadata1 = EnvironmentMetadata(
            hostname="test-host-1",
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            project_name="test-project",
            env=None,
        )

        metadata2 = EnvironmentMetadata(
            hostname="test-host-2",  # Different hostname
            username="test-user",
            platform="Test-Platform",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.4",
            timestamp="2025-10-17T10:30:00Z",
            project_name="test-project",
            env=None,
        )

        assert metadata1 != metadata2

    def test_metadata_repr(self) -> None:
        """Should have useful string representation."""
        metadata = capture_metadata()
        repr_str = repr(metadata)

        assert "EnvironmentMetadata" in repr_str
        assert metadata.hostname in repr_str

    def test_env_vars_filtered(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should only capture requested environment variables."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("SECRET_TOKEN", "secret123")
        monkeypatch.setenv("PUBLIC_VAR", "public")

        # Only request CI and PUBLIC_VAR
        metadata = capture_metadata(include_env_vars=["CI", "PUBLIC_VAR"])

        assert metadata.env is not None
        assert "CI" in metadata.env
        assert "PUBLIC_VAR" in metadata.env
        # SECRET_TOKEN should not be captured
        assert "SECRET_TOKEN" not in metadata.env

    def test_json_serialization_with_complex_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Should correctly serialize complex environment variables."""
        monkeypatch.setenv("COMPLEX_VAR", "value with spaces")
        monkeypatch.setenv("UNICODE_VAR", "unicode: 你好")

        metadata = capture_metadata(include_env_vars=["COMPLEX_VAR", "UNICODE_VAR"])
        json_str = metadata.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["env"]["COMPLEX_VAR"] == "value with spaces"
        assert data["env"]["UNICODE_VAR"] == "unicode: 你好"

    def test_direct_dataclass_construction(self) -> None:
        """Should allow direct construction of EnvironmentMetadata."""
        # This tests the dataclass definition itself
        metadata = EnvironmentMetadata(
            hostname="test.example.com",
            username="testuser",
            platform="Linux-5.10.0",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.0",
            timestamp="2025-10-19T10:00:00Z",
            project_name="test-project",
            env={"CI": "true"},
        )

        assert metadata.hostname == "test.example.com"
        assert metadata.username == "testuser"
        assert metadata.project_name == "test-project"
        assert metadata.env == {"CI": "true"}

    def test_dataclass_with_none_env(self) -> None:
        """Should handle None env in dataclass."""
        metadata = EnvironmentMetadata(
            hostname="test.example.com",
            username="testuser",
            platform="Linux-5.10.0",
            python_version="3.11.0",
            pytest_version="8.0.0",
            pytest_jux_version="0.1.0",
            timestamp="2025-10-19T10:00:00Z",
            project_name="test-project",
            env=None,
        )

        assert metadata.env is None
        data = metadata.to_dict()
        assert "env" not in data or data.get("env") is None

    def test_pytest_version_attribute_error(self) -> None:
        """Should handle pytest version AttributeError gracefully."""
        # Mock pytest module without __version__ attribute
        import types

        mock_pytest = types.ModuleType("pytest")
        # Don't set __version__ to trigger AttributeError

        with patch.dict(sys.modules, {"pytest": mock_pytest}):
            metadata = capture_metadata()
            # Should default to "unknown" when __version__ is missing
            assert metadata.pytest_version == "unknown"

    def test_pytest_jux_version_attribute_error(self) -> None:
        """Should handle pytest_jux version AttributeError gracefully."""
        # Mock pytest_jux module without __version__ attribute
        import types

        mock_jux = types.ModuleType("pytest_jux")
        # Don't set __version__ to trigger AttributeError

        with patch.dict(sys.modules, {"pytest_jux": mock_jux}):
            metadata = capture_metadata()
            # Should default to "unknown" when __version__ is missing
            assert metadata.pytest_jux_version == "unknown"


class TestGitMetadata:
    """Tests for git metadata auto-detection."""

    def test_git_metadata_captured_in_repo(self) -> None:
        """Should capture git metadata when in a git repository."""
        metadata = capture_metadata()

        # We're running in a git repo, so these should be captured
        assert metadata.git_commit is not None
        assert isinstance(metadata.git_commit, str)
        assert len(metadata.git_commit) == 40  # Full SHA-1 hash

        assert metadata.git_branch is not None
        assert isinstance(metadata.git_branch, str)
        assert len(metadata.git_branch) > 0

        assert metadata.git_status in ["clean", "dirty"]

        # Remote may or may not be present depending on setup
        if metadata.git_remote:
            assert isinstance(metadata.git_remote, str)

    def test_git_metadata_none_outside_repo(self, tmp_path) -> None:
        """Should return None for git metadata outside a git repository."""
        import os

        from pytest_jux.metadata import capture_metadata

        # Change to non-git directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            metadata = capture_metadata()

            # Should all be None outside git repo
            assert metadata.git_commit is None
            assert metadata.git_branch is None
            assert metadata.git_status is None
            assert metadata.git_remote is None
        finally:
            os.chdir(original_cwd)

    def test_git_commit_format(self) -> None:
        """Git commit should be a valid SHA-1 hash."""
        metadata = capture_metadata()

        if metadata.git_commit:
            # Should be 40-character hex string
            assert re.match(r"^[0-9a-f]{40}$", metadata.git_commit)

    def test_git_status_values(self) -> None:
        """Git status should be 'clean' or 'dirty'."""
        metadata = capture_metadata()

        if metadata.git_status:
            assert metadata.git_status in ["clean", "dirty"]

    @patch("pytest_jux.metadata._run_git_command")
    def test_git_remote_credential_sanitization(self, mock_git) -> None:
        """Should sanitize credentials from git remote URLs."""
        from pytest_jux.metadata import _capture_git_info

        # Mock git commands to return URL with credentials
        def mock_command(args):
            if args == ["rev-parse", "--git-dir"]:
                return ".git"
            elif args == ["rev-parse", "HEAD"]:
                return "a" * 40
            elif args == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return "main"
            elif args == ["status", "--porcelain"]:
                return ""
            elif len(args) >= 2 and args[0] == "config" and args[1] == "--get":
                # Return URL with credentials for any remote
                return "https://user:password@github.com/owner/repo.git"
            return None

        mock_git.side_effect = mock_command

        _, _, _, remote = _capture_git_info()

        # Credentials should be removed
        assert remote == "https://github.com/owner/repo.git"
        assert "user" not in remote
        assert "password" not in remote

    @patch("pytest_jux.metadata._run_git_command")
    def test_git_multi_remote_fallback(self, mock_git) -> None:
        """Should try multiple remote names if origin doesn't exist."""
        from pytest_jux.metadata import _capture_git_info

        # Mock git commands - origin doesn't exist, but home does
        def mock_command(args):
            if args == ["rev-parse", "--git-dir"]:
                return ".git"
            elif args == ["rev-parse", "HEAD"]:
                return "a" * 40
            elif args == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return "main"
            elif args == ["status", "--porcelain"]:
                return ""
            elif args == ["config", "--get", "remote.origin.url"]:
                return None  # origin doesn't exist
            elif args == ["config", "--get", "remote.home.url"]:
                return "ssh://git@server/repo.git"
            return None

        mock_git.side_effect = mock_command

        _, _, _, remote = _capture_git_info()

        # Should have found 'home' remote
        assert remote == "ssh://git@server/repo.git"


class TestProjectNameCapture:
    """Tests for project name capture with multiple fallback strategies."""

    def test_project_name_from_git_remote(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test project name extraction from git remote URL."""

        from pytest_jux.metadata import _capture_project_name

        def mock_run_git_command(args: list[str]) -> str | None:
            if args[0] == "config" and args[1] == "--get":
                if "remote.origin.url" in args[2]:
                    return "https://github.com/owner/my-project.git"
            return None

        monkeypatch.setattr("pytest_jux.metadata._run_git_command", mock_run_git_command)

        project_name = _capture_project_name()
        assert project_name == "my-project"

    def test_project_name_from_pyproject_toml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test project name from pyproject.toml [project] section."""
        from pytest_jux.metadata import _capture_project_name

        # Create pyproject.toml with project name
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "my-awesome-project"
version = "1.0.0"
""")

        # Mock git to return None (no git repo)
        def mock_run_git_command(args: list[str]) -> str | None:
            return None

        monkeypatch.setattr("pytest_jux.metadata._run_git_command", mock_run_git_command)
        monkeypatch.chdir(tmp_path)

        project_name = _capture_project_name()
        assert project_name == "my-awesome-project"

    def test_project_name_from_environment_variable(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test project name from JUX_PROJECT_NAME environment variable."""
        from pytest_jux.metadata import _capture_project_name

        # Mock git to return None
        def mock_run_git_command(args: list[str]) -> str | None:
            return None

        monkeypatch.setattr("pytest_jux.metadata._run_git_command", mock_run_git_command)
        monkeypatch.setenv("JUX_PROJECT_NAME", "env-project-name")
        monkeypatch.chdir(tmp_path)

        project_name = _capture_project_name()
        assert project_name == "env-project-name"

    def test_project_name_from_directory_basename(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test project name falls back to directory basename."""
        from pytest_jux.metadata import _capture_project_name

        # Mock git to return None
        def mock_run_git_command(args: list[str]) -> str | None:
            return None

        monkeypatch.setattr("pytest_jux.metadata._run_git_command", mock_run_git_command)

        # Create a directory with a specific name
        test_dir = tmp_path / "fallback-project"
        test_dir.mkdir()
        monkeypatch.chdir(test_dir)

        project_name = _capture_project_name()
        assert project_name == "fallback-project"

    def test_project_name_captured_in_metadata(self) -> None:
        """Test that project name is always captured in metadata."""
        from pytest_jux.metadata import capture_metadata

        metadata = capture_metadata()

        # Project name should always be present
        assert metadata.project_name is not None
        assert len(metadata.project_name) > 0


class TestCIMetadata:
    """Tests for CI provider auto-detection."""

    def test_ci_metadata_none_in_local_env(self) -> None:
        """Should return None for CI metadata in local development."""
        # Ensure we're not in a CI environment
        import os
        ci_vars = ["GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", "TRAVIS", "CIRCLECI"]
        for var in ci_vars:
            os.environ.pop(var, None)

        metadata = capture_metadata()

        # Should all be None in local environment
        assert metadata.ci_provider is None
        assert metadata.ci_build_id is None
        assert metadata.ci_build_url is None

    @patch.dict("os.environ", {
        "GITHUB_ACTIONS": "true",
        "GITHUB_RUN_ID": "123456",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_SHA": "abcdef123456",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_ACTOR": "testuser",
    })
    def test_github_actions_detection(self) -> None:
        """Should detect GitHub Actions CI environment."""
        metadata = capture_metadata()

        assert metadata.ci_provider == "github"
        assert metadata.ci_build_id == "123456"
        assert metadata.ci_build_url == "https://github.com/owner/repo/actions/runs/123456"

        # Should capture standard GitHub env vars
        assert metadata.env is not None
        assert "GITHUB_SHA" in metadata.env
        assert metadata.env["GITHUB_SHA"] == "abcdef123456"
        assert "GITHUB_REF" in metadata.env
        assert "GITHUB_ACTOR" in metadata.env

    @patch.dict("os.environ", {
        "GITLAB_CI": "true",
        "CI_PIPELINE_ID": "789",
        "CI_PIPELINE_URL": "https://gitlab.com/owner/repo/-/pipelines/789",
        "CI_COMMIT_SHA": "fedcba654321",
        "CI_COMMIT_BRANCH": "main",
        "CI_JOB_ID": "456",
    })
    def test_gitlab_ci_detection(self) -> None:
        """Should detect GitLab CI environment."""
        metadata = capture_metadata()

        assert metadata.ci_provider == "gitlab"
        assert metadata.ci_build_id == "789"
        assert metadata.ci_build_url == "https://gitlab.com/owner/repo/-/pipelines/789"

        # Should capture standard GitLab env vars
        assert metadata.env is not None
        assert "CI_COMMIT_SHA" in metadata.env
        assert "CI_COMMIT_BRANCH" in metadata.env
        assert "CI_JOB_ID" in metadata.env

    @patch.dict("os.environ", {
        "JENKINS_URL": "https://jenkins.example.com",
        "BUILD_ID": "42",
        "BUILD_URL": "https://jenkins.example.com/job/test/42",
        "GIT_COMMIT": "1234567890abcdef",
        "GIT_BRANCH": "develop",
        "JOB_NAME": "test-job",
    })
    def test_jenkins_detection(self) -> None:
        """Should detect Jenkins CI environment."""
        metadata = capture_metadata()

        assert metadata.ci_provider == "jenkins"
        assert metadata.ci_build_id == "42"
        assert metadata.ci_build_url == "https://jenkins.example.com/job/test/42"

        # Should capture standard Jenkins env vars
        assert metadata.env is not None
        assert "GIT_COMMIT" in metadata.env
        assert "GIT_BRANCH" in metadata.env
        assert "JOB_NAME" in metadata.env

    @patch.dict("os.environ", {
        "TRAVIS": "true",
        "TRAVIS_BUILD_ID": "999",
        "TRAVIS_BUILD_WEB_URL": "https://travis-ci.org/owner/repo/builds/999",
        "TRAVIS_COMMIT": "abcd1234",
        "TRAVIS_BRANCH": "feature-branch",
    })
    def test_travis_ci_detection(self) -> None:
        """Should detect Travis CI environment."""
        metadata = capture_metadata()

        assert metadata.ci_provider == "travis"
        assert metadata.ci_build_id == "999"
        assert metadata.ci_build_url == "https://travis-ci.org/owner/repo/builds/999"

        # Should capture standard Travis env vars
        assert metadata.env is not None
        assert "TRAVIS_COMMIT" in metadata.env
        assert "TRAVIS_BRANCH" in metadata.env

    @patch.dict("os.environ", {
        "CIRCLECI": "true",
        "CIRCLE_BUILD_NUM": "88",
        "CIRCLE_BUILD_URL": "https://circleci.com/gh/owner/repo/88",
        "CIRCLE_SHA1": "fedcba9876",
        "CIRCLE_BRANCH": "staging",
    })
    def test_circleci_detection(self) -> None:
        """Should detect CircleCI environment."""
        metadata = capture_metadata()

        assert metadata.ci_provider == "circleci"
        assert metadata.ci_build_id == "88"
        assert metadata.ci_build_url == "https://circleci.com/gh/owner/repo/88"

        # Should capture standard CircleCI env vars
        assert metadata.env is not None
        assert "CIRCLE_SHA1" in metadata.env
        assert "CIRCLE_BRANCH" in metadata.env

    @patch.dict("os.environ", {
        "GITHUB_ACTIONS": "true",
        "GITHUB_RUN_ID": "123",
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_SHA": "abc123",
    })
    def test_ci_env_vars_merge_with_user_vars(self) -> None:
        """CI env vars should merge with user-requested env vars."""
        # Request additional env var
        metadata = capture_metadata(include_env_vars=["PATH"])

        assert metadata.env is not None

        # Should have CI-detected vars
        assert "GITHUB_SHA" in metadata.env

        # Should also have user-requested vars
        assert "PATH" in metadata.env

    @patch.dict("os.environ", {
        "GITHUB_ACTIONS": "true",
        "GITHUB_RUN_ID": "123",
        "GITHUB_SHA": "auto_detected",
        "CUSTOM_VAR": "custom_value",
    })
    def test_user_env_vars_precedence(self) -> None:
        """User-requested env vars should take precedence over CI auto-detected."""
        # Request GITHUB_SHA explicitly (already auto-detected by CI)
        metadata = capture_metadata(include_env_vars=["GITHUB_SHA", "CUSTOM_VAR"])

        assert metadata.env is not None

        # User-requested should take precedence
        assert metadata.env["GITHUB_SHA"] == "auto_detected"
        assert metadata.env["CUSTOM_VAR"] == "custom_value"
