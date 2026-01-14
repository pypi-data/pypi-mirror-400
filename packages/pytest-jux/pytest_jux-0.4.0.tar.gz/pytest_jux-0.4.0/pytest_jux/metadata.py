# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Environment metadata capture for test reports.

This module captures environment metadata (hostname, username, platform, etc.)
which is then injected into JUnit XML <properties> elements via the
pytest_metadata hook in plugin.py.

Metadata captured by this module is:
- Embedded in JUnit XML as <properties> elements
- Included in XMLDSig signature (cryptographically bound)
- No longer stored in separate JSON sidecar files (as of v0.3.0)

Usage:
    The metadata is automatically captured and added to test reports when
    pytest-jux is enabled. No manual intervention is required.

    For custom usage:
        from pytest_jux.metadata import capture_metadata

        metadata = capture_metadata()
        print(f"Running on: {metadata.hostname}")
"""

import getpass
import json
import os
import platform
import socket
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class EnvironmentMetadata:
    """Environment metadata for test execution."""

    hostname: str
    username: str
    platform: str
    python_version: str
    pytest_version: str
    pytest_jux_version: str
    timestamp: str
    project_name: str  # Project name (mandatory)
    env: dict[str, str] | None = None
    # Git metadata (auto-detected)
    git_commit: str | None = None
    git_branch: str | None = None
    git_status: str | None = None  # "clean" or "dirty"
    git_remote: str | None = None
    # CI metadata (auto-detected)
    ci_provider: str | None = None  # "github", "gitlab", "jenkins", etc.
    ci_build_id: str | None = None
    ci_build_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        data = asdict(self)
        # Remove env if None
        if data.get("env") is None:
            data.pop("env", None)
        return data

    def to_json(self, indent: int | None = None) -> str:
        """Convert metadata to JSON string.

        Args:
            indent: JSON indentation level (None for compact)

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)

    def __eq__(self, other: object) -> bool:
        """Check equality with another EnvironmentMetadata instance.

        Args:
            other: Object to compare with

        Returns:
            True if equal, False otherwise
        """
        if not isinstance(other, EnvironmentMetadata):
            return NotImplemented

        return (
            self.hostname == other.hostname
            and self.username == other.username
            and self.platform == other.platform
            and self.python_version == other.python_version
            and self.pytest_version == other.pytest_version
            and self.pytest_jux_version == other.pytest_jux_version
            and self.timestamp == other.timestamp
            and self.project_name == other.project_name
            and self.env == other.env
            and self.git_commit == other.git_commit
            and self.git_branch == other.git_branch
            and self.git_status == other.git_status
            and self.git_remote == other.git_remote
            and self.ci_provider == other.ci_provider
            and self.ci_build_id == other.ci_build_id
            and self.ci_build_url == other.ci_build_url
        )

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            String representation of metadata
        """
        return f"EnvironmentMetadata(hostname={self.hostname!r}, username={self.username!r}, timestamp={self.timestamp!r})"


def _run_git_command(args: list[str]) -> str | None:
    """Run a git command and return output, or None if git not available or fails.

    Args:
        args: Git command arguments (e.g., ["rev-parse", "HEAD"])

    Returns:
        Command output stripped of whitespace, or None on failure
    """
    try:
        result = subprocess.run(  # noqa: S603 - Safe: controlled git command with no user input
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _capture_git_info() -> tuple[str | None, str | None, str | None, str | None]:
    """Auto-detect git repository information.

    Returns:
        Tuple of (commit_hash, branch_name, status, remote_url)
        Each element is None if not available
    """
    # Check if we're in a git repo
    if _run_git_command(["rev-parse", "--git-dir"]) is None:
        return None, None, None, None

    # Get commit hash
    commit = _run_git_command(["rev-parse", "HEAD"])

    # Get branch name
    branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])

    # Get working tree status (clean/dirty)
    status_output = _run_git_command(["status", "--porcelain"])
    status = "clean" if status_output == "" else "dirty" if status_output else None

    # Get remote URL (sanitized to remove credentials)
    # Try common remote names in order: origin, home, upstream, github, gitlab
    remote = None
    for remote_name in ["origin", "home", "upstream", "github", "gitlab"]:
        remote = _run_git_command(["config", "--get", f"remote.{remote_name}.url"])
        if remote:
            break

    if remote:
        # Sanitize URL to remove credentials
        # Convert https://user:pass@host/repo to https://host/repo
        # Convert git@host:repo to git@host:repo (already safe)
        import re
        remote = re.sub(r"https://[^@]+@", "https://", remote)

    return commit, branch, status, remote


def _capture_ci_info() -> tuple[str | None, str | None, str | None, dict[str, str]]:
    """Auto-detect CI provider and capture standard metadata.

    Returns:
        Tuple of (provider_name, build_id, build_url, env_vars_dict)
    """
    env_vars: dict[str, str] = {}

    # GitHub Actions
    if os.getenv("GITHUB_ACTIONS"):
        provider = "github"
        build_id = os.getenv("GITHUB_RUN_ID")
        repo = os.getenv("GITHUB_REPOSITORY", "")
        server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        build_url = f"{server}/{repo}/actions/runs/{build_id}" if build_id and repo else None

        # Capture standard GitHub env vars
        for var in ["GITHUB_SHA", "GITHUB_REF", "GITHUB_ACTOR", "GITHUB_WORKFLOW", "GITHUB_RUN_NUMBER"]:
            if os.getenv(var):
                env_vars[var] = os.environ[var]

        return provider, build_id, build_url, env_vars

    # GitLab CI
    elif os.getenv("GITLAB_CI"):
        provider = "gitlab"
        build_id = os.getenv("CI_PIPELINE_ID")
        build_url = os.getenv("CI_PIPELINE_URL")

        # Capture standard GitLab env vars
        for var in ["CI_COMMIT_SHA", "CI_COMMIT_BRANCH", "CI_COMMIT_TAG", "CI_JOB_ID", "CI_JOB_NAME", "CI_PROJECT_PATH"]:
            if os.getenv(var):
                env_vars[var] = os.environ[var]

        return provider, build_id, build_url, env_vars

    # Jenkins
    elif os.getenv("JENKINS_URL"):
        provider = "jenkins"
        build_id = os.getenv("BUILD_ID")
        build_url = os.getenv("BUILD_URL")

        # Capture standard Jenkins env vars
        for var in ["GIT_COMMIT", "GIT_BRANCH", "JOB_NAME", "BUILD_NUMBER"]:
            if os.getenv(var):
                env_vars[var] = os.environ[var]

        return provider, build_id, build_url, env_vars

    # Travis CI
    elif os.getenv("TRAVIS"):
        provider = "travis"
        build_id = os.getenv("TRAVIS_BUILD_ID")
        build_url = os.getenv("TRAVIS_BUILD_WEB_URL")

        # Capture standard Travis env vars
        for var in ["TRAVIS_COMMIT", "TRAVIS_BRANCH", "TRAVIS_JOB_ID", "TRAVIS_BUILD_NUMBER"]:
            if os.getenv(var):
                env_vars[var] = os.environ[var]

        return provider, build_id, build_url, env_vars

    # CircleCI
    elif os.getenv("CIRCLECI"):
        provider = "circleci"
        build_id = os.getenv("CIRCLE_BUILD_NUM")
        build_url = os.getenv("CIRCLE_BUILD_URL")

        # Capture standard CircleCI env vars
        for var in ["CIRCLE_SHA1", "CIRCLE_BRANCH", "CIRCLE_JOB", "CIRCLE_WORKFLOW_ID"]:
            if os.getenv(var):
                env_vars[var] = os.environ[var]

        return provider, build_id, build_url, env_vars

    # Not in a recognized CI environment
    return None, None, None, {}


def _capture_project_name() -> str:
    """Capture project name with multiple fallback strategies.

    Strategies (in order):
    1. Git remote URL - Extract repository name from git remote
    2. pyproject.toml - Read project name from Python project metadata
    3. Environment variable - Check JUX_PROJECT_NAME
    4. Directory basename - Fall back to current directory name

    Returns:
        Project name (never None, always returns a string)
    """
    # Strategy 1: Extract from git remote URL
    git_remote = _run_git_command(["config", "--get", "remote.origin.url"])
    if not git_remote:
        # Try other common remote names
        for remote_name in ["home", "upstream", "github", "gitlab"]:
            git_remote = _run_git_command(["config", "--get", f"remote.{remote_name}.url"])
            if git_remote:
                break

    if git_remote:
        # Extract repo name from URL
        # Examples:
        # https://github.com/owner/repo.git -> repo
        # git@github.com:owner/repo.git -> repo
        # ssh://user@host:port/path/repo.git -> repo
        import re
        match = re.search(r'/([^/]+?)(\.git)?$', git_remote)
        if match:
            return match.group(1)

    # Strategy 2: Read from pyproject.toml
    try:
        from pathlib import Path
        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                # Try [project] section first (PEP 621)
                if "project" in data and "name" in data["project"]:
                    return str(data["project"]["name"])
                # Fall back to [tool.poetry] section
                if "tool" in data and "poetry" in data["tool"] and "name" in data["tool"]["poetry"]:
                    return str(data["tool"]["poetry"]["name"])
    except Exception:  # noqa: S110 - Intentionally silent, fallback to other strategies
        pass

    # Strategy 3: Environment variable
    project_name = os.getenv("JUX_PROJECT_NAME")
    if project_name:
        return project_name

    # Strategy 4: Current directory basename (always works)
    from pathlib import Path
    return Path.cwd().name


def capture_metadata(
    include_env_vars: list[str] | None = None,
) -> EnvironmentMetadata:
    """Capture current environment metadata.

    Args:
        include_env_vars: List of environment variable names to capture.
                         If None, no env vars are captured.

    Returns:
        EnvironmentMetadata instance with current environment information
    """
    # Capture basic system information
    hostname = socket.gethostname()
    username = getpass.getuser()
    platform_info = platform.platform()
    python_version = sys.version

    # Capture pytest version
    try:
        import pytest

        pytest_version = pytest.__version__
    except (ImportError, AttributeError):
        pytest_version = "unknown"

    # Capture pytest-jux version
    try:
        from pytest_jux import __version__

        pytest_jux_version = __version__
    except (ImportError, AttributeError):
        pytest_jux_version = "unknown"

    # Generate ISO 8601 timestamp in UTC
    timestamp = datetime.now(UTC).isoformat()

    # Auto-detect project name
    project_name = _capture_project_name()

    # Auto-detect git metadata
    git_commit, git_branch, git_status, git_remote = _capture_git_info()

    # Auto-detect CI provider and metadata
    ci_provider, ci_build_id, ci_build_url, ci_env_vars = _capture_ci_info()

    # Merge CI env vars with explicitly requested ones
    env_dict: dict[str, str] | None = None
    if ci_env_vars or include_env_vars:
        env_dict = ci_env_vars.copy() if ci_env_vars else {}
        if include_env_vars:
            for var_name in include_env_vars:
                if var_name in os.environ:
                    # User-requested vars take precedence over CI auto-detected
                    env_dict[var_name] = os.environ[var_name]

    return EnvironmentMetadata(
        hostname=hostname,
        username=username,
        platform=platform_info,
        python_version=python_version,
        pytest_version=pytest_version,
        pytest_jux_version=pytest_jux_version,
        timestamp=timestamp,
        project_name=project_name,
        # Keep empty dict if user explicitly requested vars (even if none found)
        # Only None if no vars requested at all
        env=env_dict if (env_dict or include_env_vars) else None,
        git_commit=git_commit,
        git_branch=git_branch,
        git_status=git_status,
        git_remote=git_remote,
        ci_provider=ci_provider,
        ci_build_id=ci_build_id,
        ci_build_url=ci_build_url,
    )
