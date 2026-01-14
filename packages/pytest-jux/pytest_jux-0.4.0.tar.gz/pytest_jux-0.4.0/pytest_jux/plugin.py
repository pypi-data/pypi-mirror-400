# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""pytest plugin hooks for Jux test report signing and publishing.

This module implements the pytest plugin hooks for capturing JUnit XML
reports, signing them with XMLDSig, and publishing them to the Jux API.
"""

import os
from pathlib import Path

import pytest
from lxml import etree

from pytest_jux.api_client import JuxAPIClient
from pytest_jux.canonicalizer import compute_canonical_hash, load_xml
from pytest_jux.config import ConfigurationManager, StorageMode
from pytest_jux.signer import load_private_key, sign_xml
from pytest_jux.storage import ReportStorage


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add plugin command-line options.

    Args:
        parser: pytest command-line parser
    """
    group = parser.getgroup("jux", "Jux test report signing and publishing")
    group.addoption(
        "--jux-sign",
        action="store_true",
        default=False,
        help="Enable signing of JUnit XML reports",
    )
    group.addoption(
        "--jux-key",
        action="store",
        default=None,
        help="Path to private key for signing (PEM format)",
    )
    group.addoption(
        "--jux-cert",
        action="store",
        default=None,
        help="Path to X.509 certificate for signing (PEM format, optional)",
    )
    group.addoption(
        "--jux-publish",
        action="store_true",
        default=False,
        help="Publish signed reports to Jux API",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure plugin based on command-line options and configuration files.

    Loads configuration from configuration files and merges with command-line
    options. Command-line options take precedence over configuration files.

    Args:
        config: pytest configuration object

    Raises:
        pytest.UsageError: If configuration is invalid
    """
    # Load configuration from files (CLI > env > files > defaults)
    config_manager = ConfigurationManager()

    # Load from environment variables
    config_manager.load_from_env()

    # Load from config files (in precedence order)
    # User-level config (XDG Base Directory compliant)
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        user_config = Path(xdg_config_home) / "jux" / "config"
    else:
        user_config = Path.home() / ".config" / "jux" / "config"

    if user_config.exists():
        config_manager.load_from_file(user_config)

    # Project-level configs
    project_configs = [Path(".jux.conf"), Path("pytest.ini")]
    for config_file in project_configs:
        if config_file.exists() and config_file.suffix in [".conf", ".ini"]:
            config_manager.load_from_file(config_file)

    # Command-line options override configuration files
    cli_sign = config.getoption("jux_sign")
    cli_key = config.getoption("jux_key")
    cli_cert = config.getoption("jux_cert")
    cli_publish = config.getoption("jux_publish")

    # Merge configuration (CLI takes precedence)
    jux_sign = cli_sign if cli_sign else config_manager.get("jux_sign")
    jux_key = cli_key if cli_key else config_manager.get("jux_key_path")
    jux_cert = cli_cert if cli_cert else config_manager.get("jux_cert_path")
    jux_publish = cli_publish if cli_publish else config_manager.get("jux_publish")

    # Enable plugin if any functionality is requested (CLI or config file)
    jux_enabled = config_manager.get("jux_enabled") or jux_sign or jux_publish

    # Storage configuration (from config files only, no CLI options yet)
    jux_storage_mode = config_manager.get("jux_storage_mode")
    jux_storage_path = config_manager.get("jux_storage_path")

    # API configuration (Jux API v1.0.0)
    jux_api_url = config_manager.get("jux_api_url")
    jux_bearer_token = config_manager.get("jux_bearer_token")
    jux_api_timeout = config_manager.get("jux_api_timeout")
    jux_api_max_retries = config_manager.get("jux_api_max_retries")

    # Store merged configuration in config object for later use
    config._jux_enabled = jux_enabled  # type: ignore[attr-defined]
    config._jux_sign = jux_sign  # type: ignore[attr-defined]
    config._jux_key_path = jux_key  # type: ignore[attr-defined]
    config._jux_cert_path = jux_cert  # type: ignore[attr-defined]
    config._jux_publish = jux_publish  # type: ignore[attr-defined]
    config._jux_storage_mode = jux_storage_mode  # type: ignore[attr-defined]
    config._jux_storage_path = jux_storage_path  # type: ignore[attr-defined]
    config._jux_api_url = jux_api_url  # type: ignore[attr-defined]
    config._jux_bearer_token = jux_bearer_token  # type: ignore[attr-defined]
    config._jux_api_timeout = jux_api_timeout  # type: ignore[attr-defined]
    config._jux_api_max_retries = jux_api_max_retries  # type: ignore[attr-defined]

    # Validate configuration if plugin is enabled
    if jux_enabled:
        if jux_sign:
            if not jux_key:
                raise pytest.UsageError(
                    "Error: jux_sign is enabled but jux_key_path is not configured. "
                    "Specify --jux-key or set jux_key_path in configuration file."
                )

            # Verify key file exists
            key_path = Path(jux_key)
            if not key_path.exists():
                raise pytest.UsageError(f"Error: Key file not found: {jux_key}")

            # If certificate provided, verify it exists
            if jux_cert:
                cert_path = Path(jux_cert)
                if not cert_path.exists():
                    raise pytest.UsageError(
                        f"Error: Certificate file not found: {jux_cert}"
                    )


def pytest_metadata(metadata: dict[str, str]) -> None:
    """Add pytest-jux environment metadata to pytest-metadata.

    This hook is called by pytest-metadata during test session startup.
    We capture environment metadata and inject it into the metadata dict,
    but only if keys don't already exist (user CLI metadata takes precedence).

    Metadata is stored in JUnit XML <properties> elements and is included
    in the XMLDSig signature, ensuring cryptographic provenance.

    All jux metadata uses the "jux:" prefix to avoid conflicts with other
    plugins or user-provided metadata.

    Args:
        metadata: pytest-metadata's metadata dictionary (mutable)

    Example:
        Running pytest with:
            pytest --metadata build_number 12345

        Results in XML properties:
            <property name="build_number" value="12345"/>  <!-- User metadata -->
            <property name="project" value="my-project"/>  <!-- Project name (mandatory) -->
            <property name="jux:hostname" value="ci-runner"/>  <!-- Jux metadata -->
            <property name="jux:timestamp" value="2025-10-24T12:34:56+00:00"/>
            <property name="git:commit" value="abc123..."/>  <!-- Git metadata -->
            <property name="ci:provider" value="github"/>  <!-- CI metadata -->
            <property name="env:GITHUB_SHA" value="abc123..."/>  <!-- Env vars -->
    """
    from pytest_jux.metadata import capture_metadata

    # Capture jux environment metadata
    jux_meta = capture_metadata()

    # Add metadata with "jux:" prefix if not already present
    # User-provided metadata (CLI --metadata) takes precedence
    if "jux:hostname" not in metadata:
        metadata["jux:hostname"] = jux_meta.hostname

    if "jux:username" not in metadata:
        metadata["jux:username"] = jux_meta.username

    if "jux:platform" not in metadata:
        metadata["jux:platform"] = jux_meta.platform

    if "jux:python_version" not in metadata:
        metadata["jux:python_version"] = jux_meta.python_version

    if "jux:pytest_version" not in metadata:
        metadata["jux:pytest_version"] = jux_meta.pytest_version

    if "jux:pytest_jux_version" not in metadata:
        metadata["jux:pytest_jux_version"] = jux_meta.pytest_jux_version

    if "jux:timestamp" not in metadata:
        metadata["jux:timestamp"] = jux_meta.timestamp

    if "project" not in metadata:
        metadata["project"] = jux_meta.project_name

    # Add git metadata (auto-detected from repository)
    if jux_meta.git_commit and "git:commit" not in metadata:
        metadata["git:commit"] = jux_meta.git_commit

    if jux_meta.git_branch and "git:branch" not in metadata:
        metadata["git:branch"] = jux_meta.git_branch

    if jux_meta.git_status and "git:status" not in metadata:
        metadata["git:status"] = jux_meta.git_status

    if jux_meta.git_remote and "git:remote" not in metadata:
        metadata["git:remote"] = jux_meta.git_remote

    # Add CI metadata (auto-detected from CI environment)
    if jux_meta.ci_provider and "ci:provider" not in metadata:
        metadata["ci:provider"] = jux_meta.ci_provider

    if jux_meta.ci_build_id and "ci:build_id" not in metadata:
        metadata["ci:build_id"] = jux_meta.ci_build_id

    if jux_meta.ci_build_url and "ci:build_url" not in metadata:
        metadata["ci:build_url"] = jux_meta.ci_build_url

    # Add optional environment variables with env: prefix
    if jux_meta.env:
        for env_key, env_value in jux_meta.env.items():
            metadata_key = f"env:{env_key}"
            if metadata_key not in metadata:
                metadata[metadata_key] = env_value


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Sign and store JUnit XML report after test session completes.

    This hook is called after the test session finishes. If the plugin is enabled
    and a JUnit XML report was generated, it:
    1. Signs the report (if signing is enabled)
    2. Stores the report (signed or unsigned) according to storage mode

    Note: Environment metadata is captured by pytest_metadata() hook and included
    in the JUnit XML <properties> elements before signing. The XMLDSig signature
    covers all metadata, ensuring cryptographic provenance.

    Args:
        session: pytest session object
        exitstatus: pytest exit status code
    """
    # Check if plugin is enabled
    if not getattr(session.config, "_jux_enabled", False):
        return

    # Check if JUnit XML report was configured
    xmlpath = getattr(session.config.option, "xmlpath", None)
    if not xmlpath:
        return

    # Load the generated JUnit XML
    xml_path = Path(xmlpath)
    if not xml_path.exists():
        # XML file wasn't generated (no tests ran, etc.)
        return

    # Get configuration
    jux_sign = getattr(session.config, "_jux_sign", False)
    jux_publish = getattr(session.config, "_jux_publish", False)
    key_path_str = getattr(session.config, "_jux_key_path", None)
    cert_path_str = getattr(session.config, "_jux_cert_path", None)
    storage_mode = getattr(session.config, "_jux_storage_mode", None)
    storage_path = getattr(session.config, "_jux_storage_path", None)
    api_url = getattr(session.config, "_jux_api_url", None)
    bearer_token = getattr(session.config, "_jux_bearer_token", None)
    api_timeout = getattr(session.config, "_jux_api_timeout", 30)
    api_max_retries = getattr(session.config, "_jux_api_max_retries", 3)

    try:
        tree = load_xml(xml_path)

        # Sign the XML if signing is enabled
        if jux_sign and key_path_str:
            # Load private key
            key = load_private_key(Path(key_path_str))

            # Load certificate if provided
            cert: str | bytes | None = None
            if cert_path_str:
                cert = Path(cert_path_str).read_bytes()

            # Sign the XML
            tree = sign_xml(tree, key, cert)

            # Write signed XML back to file
            with open(xml_path, "wb") as f:
                f.write(
                    etree.tostring(
                        tree,
                        xml_declaration=True,
                        encoding="utf-8",
                        pretty_print=True,
                    )
                )

        # Compute canonical hash
        canonical_hash = compute_canonical_hash(tree)

        # Store the report if storage is configured
        # Only store locally for LOCAL, BOTH, and CACHE modes
        should_store_locally = storage_mode in [
            StorageMode.LOCAL,
            StorageMode.BOTH,
            StorageMode.CACHE,
        ]

        if should_store_locally and storage_path:
            # Convert XML tree to bytes for storage
            xml_bytes = etree.tostring(
                tree, xml_declaration=True, encoding="utf-8", pretty_print=True
            )

            # Initialize storage
            storage = ReportStorage(storage_path=Path(storage_path))

            # Store the report (metadata is already embedded in XML properties)
            storage.store_report(xml_content=xml_bytes, canonical_hash=canonical_hash)

        # Publish to API if configured
        # Publish for API, BOTH, and CACHE modes
        should_publish_to_api = (jux_publish or storage_mode in [
            StorageMode.API,
            StorageMode.BOTH,
            StorageMode.CACHE,
        ]) and api_url

        if should_publish_to_api:
            # Type narrowing: api_url must be str at this point (checked in should_publish_to_api)
            if not isinstance(api_url, str):
                # This should never happen due to should_publish_to_api check
                return  # pragma: no cover

            # Convert XML tree to string for API publishing
            xml_string = etree.tostring(
                tree, xml_declaration=True, encoding="utf-8", pretty_print=True
            ).decode("utf-8")

            try:
                # Initialize API client
                client = JuxAPIClient(
                    api_url=api_url,
                    bearer_token=bearer_token,
                    timeout=api_timeout,
                    max_retries=api_max_retries,
                )

                # Publish report to Jux API v1.0.0
                response = client.publish_report(xml_string)

                # Log success (visible in pytest output)
                import warnings
                warnings.warn(
                    f"Report published to Jux API: test_run_id={response.test_run.id}, "
                    f"success_rate={response.test_run.success_rate}%",
                    stacklevel=2,
                )

            except Exception as api_error:
                # Handle API errors based on storage mode
                if storage_mode == StorageMode.API:
                    # API mode: fail if API publishing fails
                    import warnings
                    warnings.warn(
                        f"Failed to publish report to Jux API (API mode): {api_error}",
                        stacklevel=2,
                    )
                elif storage_mode == StorageMode.CACHE:
                    # CACHE mode: queue for later (graceful degradation)
                    import warnings
                    warnings.warn(
                        f"Failed to publish report to Jux API, queued locally (CACHE mode): {api_error}",
                        stacklevel=2,
                    )
                    # Note: Report already stored locally above
                else:
                    # BOTH mode: warn but continue (local copy exists)
                    import warnings
                    warnings.warn(
                        f"Failed to publish report to Jux API, local copy saved (BOTH mode): {api_error}",
                        stacklevel=2,
                    )

    except Exception as e:
        # Report error but don't fail the test run
        import warnings

        warnings.warn(f"Failed to process JUnit XML report: {e}", stacklevel=2)
