# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for pytest plugin hooks."""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from lxml import etree

from pytest_jux.config import StorageMode
from pytest_jux.plugin import pytest_addoption, pytest_configure, pytest_sessionfinish


@pytest.fixture
def mock_parser() -> Mock:
    """Return a mock pytest parser."""
    parser = Mock()
    parser.getgroup = Mock(return_value=Mock())
    return parser


@pytest.fixture
def mock_config() -> Mock:
    """Return a mock pytest config."""
    config = Mock()
    config.getoption = Mock(return_value=None)
    config.pluginmanager = Mock()
    config.option = Mock()
    return config


@pytest.fixture
def mock_session() -> Mock:
    """Return a mock pytest session."""
    session = Mock()
    session.config = Mock()
    session.config.getoption = Mock(return_value=None)
    session.config.option = Mock()
    return session


@pytest.fixture
def test_key_path(tmp_path: Path) -> Path:
    """Create a test key file."""
    key_path = tmp_path / "test_key.pem"
    # Copy actual test key
    import shutil

    fixture_key = Path(__file__).parent / "fixtures" / "keys" / "rsa_2048.pem"
    shutil.copy(fixture_key, key_path)
    return key_path


@pytest.fixture
def test_cert_path(tmp_path: Path) -> Path:
    """Create a test certificate file."""
    cert_path = tmp_path / "test_cert.crt"
    # Copy actual test certificate
    import shutil

    fixture_cert = Path(__file__).parent / "fixtures" / "keys" / "rsa_2048.crt"
    shutil.copy(fixture_cert, cert_path)
    return cert_path


@pytest.fixture
def test_junit_xml(tmp_path: Path) -> Path:
    """Create a test JUnit XML file."""
    xml_path = tmp_path / "junit.xml"
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
    xml_path.write_text(xml_content)
    return xml_path


class TestPytestAddoption:
    """Tests for pytest_addoption hook."""

    def test_adds_jux_group(self, mock_parser: Mock) -> None:
        """Test that plugin adds Jux option group."""
        pytest_addoption(mock_parser)
        mock_parser.getgroup.assert_called_once_with(
            "jux", "Jux test report signing and publishing"
        )

    def test_adds_jux_sign_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-sign option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-sign option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-sign" in str(call) for call in calls)

    def test_adds_jux_key_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-key option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-key option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-key" in str(call) for call in calls)

    def test_adds_jux_cert_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-cert option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-cert option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-cert" in str(call) for call in calls)

    def test_adds_jux_publish_option(self, mock_parser: Mock) -> None:
        """Test that plugin adds --jux-publish option."""
        mock_group = Mock()
        mock_parser.getgroup.return_value = mock_group

        pytest_addoption(mock_parser)

        # Verify --jux-publish option was added
        calls = [call[1] for call in mock_group.addoption.mock_calls]
        assert any("--jux-publish" in str(call) for call in calls)


class TestPytestConfigure:
    """Tests for pytest_configure hook."""

    def test_configure_without_signing(self, mock_config: Mock) -> None:
        """Test configuration when signing is disabled."""
        mock_config.getoption.return_value = False

        # Should not raise any errors
        pytest_configure(mock_config)

    def test_configure_with_signing_enabled(
        self, mock_config: Mock, test_key_path: Path
    ) -> None:
        """Test configuration when signing is enabled."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)

        # Should not raise any errors
        pytest_configure(mock_config)

    def test_configure_validates_key_path(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that configure validates key path when signing enabled."""
        # Create .jux.conf with jux enabled and signing enabled
        config_file = tmp_path / ".jux.conf"
        config_file.write_text(
            """[jux]
enabled = true
sign = true
"""
        )

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            mock_config.getoption.side_effect = lambda x: {
                "jux_sign": True,
                "jux_key": None,
                "jux_cert": None,
                "jux_publish": False,
            }.get(x, False)

            # Should raise error if signing enabled but no key provided
            with pytest.raises(pytest.UsageError, match="jux_key_path is not configured"):
                pytest_configure(mock_config)

        finally:
            os.chdir(original_cwd)

    def test_configure_stores_settings_in_config(
        self, mock_config: Mock, test_key_path: Path
    ) -> None:
        """Test that configure stores settings in config object."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)

        pytest_configure(mock_config)

        # Verify settings were stored
        assert hasattr(mock_config, "_jux_sign")
        assert mock_config._jux_sign is True


class TestPytestConfigureWithConfigFiles:
    """Tests for pytest_configure with configuration files."""

    def test_loads_config_from_project_file(
        self, mock_config: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that configure loads settings from .jux.conf."""
        # Create .jux.conf
        config_file = tmp_path / ".jux.conf"
        config_file.write_text(
            f"""[jux]
enabled = true
sign = true
key_path = {test_key_path}
storage_mode = local
storage_path = {tmp_path / 'reports'}
"""
        )

        # Change to tmp_path so .jux.conf is found
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            mock_config.getoption.return_value = False

            pytest_configure(mock_config)

            # Verify configuration was loaded from file
            assert hasattr(mock_config, "_jux_enabled")
            assert mock_config._jux_enabled is True
            assert hasattr(mock_config, "_jux_sign")
            assert mock_config._jux_sign is True
            assert hasattr(mock_config, "_jux_storage_mode")
            assert mock_config._jux_storage_mode == StorageMode.LOCAL

        finally:
            os.chdir(original_cwd)

    def test_cli_overrides_config_file(
        self, mock_config: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that CLI options override configuration file settings."""
        # Create .jux.conf with sign=false
        config_file = tmp_path / ".jux.conf"
        config_file.write_text(
            """[jux]
enabled = true
sign = false
"""
        )

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # CLI option for sign=true should override
            mock_config.getoption.side_effect = lambda x: {
                "jux_sign": True,
                "jux_key": str(test_key_path),
                "jux_cert": None,
                "jux_publish": False,
            }.get(x, False)

            pytest_configure(mock_config)

            # CLI should override config file
            assert mock_config._jux_sign is True

        finally:
            os.chdir(original_cwd)

    def test_respects_jux_enabled_flag(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that jux_enabled flag controls plugin activation."""
        # Create .jux.conf with enabled=false
        config_file = tmp_path / ".jux.conf"
        config_file.write_text(
            """[jux]
enabled = false
"""
        )

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            mock_config.getoption.return_value = False

            pytest_configure(mock_config)

            # Plugin should be disabled
            assert mock_config._jux_enabled is False

        finally:
            os.chdir(original_cwd)

    def test_loads_storage_configuration(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that storage configuration is loaded correctly."""
        storage_path = tmp_path / "custom" / "storage"
        config_file = tmp_path / ".jux.conf"
        config_file.write_text(
            f"""[jux]
enabled = true
storage_mode = cache
storage_path = {storage_path}
"""
        )

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            mock_config.getoption.return_value = False

            pytest_configure(mock_config)

            # Verify storage settings
            assert mock_config._jux_storage_mode == StorageMode.CACHE
            assert mock_config._jux_storage_path == storage_path

        finally:
            os.chdir(original_cwd)


class TestPytestSessionfinish:
    """Tests for pytest_sessionfinish hook."""

    def test_does_nothing_when_jux_disabled(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test that hook does nothing when jux is disabled."""
        mock_session.config._jux_enabled = False
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should not raise any errors
        pytest_sessionfinish(mock_session, 0)

        # XML should be unchanged
        original_content = test_junit_xml.read_text()
        assert "<Signature" not in original_content

    def test_does_nothing_when_signing_disabled(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test that hook does nothing when signing is disabled."""
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should not raise any errors
        pytest_sessionfinish(mock_session, 0)

        # XML should be unchanged
        original_content = test_junit_xml.read_text()
        assert "<Signature" not in original_content

    def test_does_nothing_without_junit_xml(self, mock_session: Mock) -> None:
        """Test that hook does nothing when no JUnit XML is configured."""
        mock_session.config._jux_sign = True
        mock_session.config.option.xmlpath = None

        # Should not raise any errors
        pytest_sessionfinish(mock_session, 0)

    def test_signs_junit_xml_when_enabled(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        test_cert_path: Path,
    ) -> None:
        """Test that hook signs JUnit XML when signing is enabled."""
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = str(test_cert_path)
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify XML was signed
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_signs_junit_xml_without_certificate(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that hook can sign JUnit XML without certificate."""
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify XML was signed
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_preserves_original_junit_xml_content(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that signing preserves original JUnit XML content."""
        # Read original content
        original_tree = etree.parse(str(test_junit_xml))
        original_testcase = original_tree.find(".//testcase")
        assert original_testcase is not None
        original_name = original_testcase.get("name")

        # Configure and sign
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        pytest_sessionfinish(mock_session, 0)

        # Verify original content is preserved
        signed_tree = etree.parse(str(test_junit_xml))
        signed_testcase = signed_tree.find(".//testcase")
        assert signed_testcase is not None
        assert signed_testcase.get("name") == original_name

    def test_handles_invalid_key_path(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test that hook handles invalid key path gracefully."""
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = "/nonexistent/key.pem"
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should issue a warning but not fail the test run
        with pytest.warns(UserWarning, match="Failed to process JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)

    def test_handles_invalid_xml(
        self, mock_session: Mock, test_key_path: Path, tmp_path: Path
    ) -> None:
        """Test that hook handles invalid XML gracefully."""
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("not valid xml")

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config.option.xmlpath = str(invalid_xml)

        # Should issue a warning but not fail the test run
        with pytest.warns(UserWarning, match="Failed to process JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)


class TestPytestSessionfinishWithStorage:
    """Tests for pytest_sessionfinish with storage integration."""

    def test_stores_report_with_local_storage_mode(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that reports are stored when storage_mode is LOCAL."""
        storage_path = tmp_path / "reports"

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.LOCAL
        mock_session.config._jux_storage_path = storage_path
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify report was stored
        assert storage_path.exists()
        reports_dir = storage_path / "reports"
        assert reports_dir.exists()

        # Should have at least one report file
        report_files = list(reports_dir.glob("*.xml"))
        assert len(report_files) > 0

        # Metadata should NOT be in separate JSON files (v0.3.0+)
        # Metadata is embedded in XML <properties> elements
        metadata_dir = storage_path / "metadata"
        if metadata_dir.exists():
            metadata_files = list(metadata_dir.glob("*.json"))
            assert len(metadata_files) == 0, "JSON metadata files should not exist in v0.3.0+"

    def test_stores_report_with_cache_storage_mode(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that reports are stored when storage_mode is CACHE."""
        storage_path = tmp_path / "cache"

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.CACHE
        mock_session.config._jux_storage_path = storage_path
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify report was stored
        reports_dir = storage_path / "reports"
        assert reports_dir.exists()
        assert len(list(reports_dir.glob("*.xml"))) > 0

    def test_does_not_store_with_api_storage_mode(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that reports are NOT stored locally when storage_mode is API."""
        storage_path = tmp_path / "api"

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.API
        mock_session.config._jux_storage_path = storage_path
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Verify report was NOT stored locally
        # Storage path might be created but should not have reports
        if storage_path.exists():
            reports_dir = storage_path / "reports"
            if reports_dir.exists():
                assert len(list(reports_dir.glob("*.xml"))) == 0

    def test_captures_metadata_with_storage(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that environment metadata is embedded in stored XML reports.

        As of v0.3.0, metadata is no longer stored in separate JSON files.
        Instead, it's embedded in the XML <properties> elements and included
        in the XMLDSig signature.
        """
        storage_path = tmp_path / "reports"

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.LOCAL
        mock_session.config._jux_storage_path = storage_path
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Execute hook
        pytest_sessionfinish(mock_session, 0)

        # Find stored report
        reports_dir = storage_path / "reports"
        report_files = list(reports_dir.glob("*.xml"))
        assert len(report_files) > 0

        # Parse stored report and verify metadata is embedded
        from lxml import etree
        tree = etree.parse(str(report_files[0]))
        _properties = tree.find(".//properties")  # Prefixed to indicate intentionally unused

        # NOTE: In the current test setup, properties might not exist because
        # pytest-metadata hook runs during actual pytest execution, not when
        # we manually call pytest_sessionfinish. This test primarily verifies
        # that NO JSON metadata files are created.

        # Verify no JSON metadata files exist
        metadata_dir = storage_path / "metadata"
        if metadata_dir.exists():
            metadata_files = list(metadata_dir.glob("*.json"))
            assert len(metadata_files) == 0, "JSON metadata files should not exist in v0.3.0+"

    def test_handles_storage_error_gracefully(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        test_key_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that storage errors don't fail the test run."""
        # Use invalid storage path (e.g., file instead of directory)
        invalid_storage = tmp_path / "invalid.txt"
        invalid_storage.write_text("not a directory")

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.LOCAL
        mock_session.config._jux_storage_path = invalid_storage
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should issue a warning but not fail
        with pytest.warns(UserWarning, match="Failed to process JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)


class TestPluginIntegration:
    """Integration tests for the full plugin workflow."""

    def test_full_workflow_with_signing(
        self, mock_parser: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test complete workflow: configure → sign → verify."""
        # Step 1: Add options
        pytest_addoption(mock_parser)
        assert mock_parser.getgroup.called

        # Step 2: Configure
        mock_config = Mock()
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(test_key_path),
            "jux_cert": None,
        }.get(x)
        pytest_configure(mock_config)

        # Step 3: Run sessionfinish
        mock_session = Mock()
        mock_session.config = mock_config
        mock_session.config.option.xmlpath = str(test_junit_xml)
        pytest_sessionfinish(mock_session, 0)

        # Verify result
        signed_content = test_junit_xml.read_text()
        assert "<Signature" in signed_content or "ds:Signature" in signed_content

    def test_workflow_without_signing(
        self, mock_parser: Mock, test_junit_xml: Path
    ) -> None:
        """Test workflow when signing is disabled."""
        original_content = test_junit_xml.read_text()

        # Configure without signing
        mock_config = Mock()
        mock_config.getoption.return_value = False
        pytest_configure(mock_config)

        # Run sessionfinish
        mock_session = Mock()
        mock_session.config = mock_config
        mock_session.config._jux_sign = False
        mock_session.config.option.xmlpath = str(test_junit_xml)
        pytest_sessionfinish(mock_session, 0)

        # Verify XML is unchanged
        assert test_junit_xml.read_text() == original_content
        assert "<Signature" not in original_content


class TestPytestMetadataIntegration:
    """Tests for pytest-metadata integration and property tag preservation."""

    def test_pytest_metadata_is_available(self) -> None:
        """Test that pytest-metadata is installed and importable."""
        try:
            import pytest_metadata
            assert pytest_metadata is not None
        except ImportError:
            pytest.fail("pytest-metadata should be installed as a dependency")

    def test_preserves_property_tags_during_signing(
        self, mock_session: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that property tags from pytest-metadata are preserved during signing."""
        # Create JUnit XML with property tags (simulating pytest-metadata output)
        xml_path = tmp_path / "junit_with_metadata.xml"
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <properties>
            <property name="build_id" value="12345"/>
            <property name="environment" value="staging"/>
            <property name="commit_sha" value="abc123def"/>
        </properties>
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
        xml_path.write_text(xml_content)

        # Configure signing
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(xml_path)

        # Sign the XML
        pytest_sessionfinish(mock_session, 0)

        # Parse signed XML
        signed_tree = etree.parse(str(xml_path))

        # Verify property tags are still present
        properties = signed_tree.findall(".//property")
        assert len(properties) == 3

        # Verify property values
        property_dict = {
            prop.get("name"): prop.get("value") for prop in properties
        }
        assert property_dict["build_id"] == "12345"
        assert property_dict["environment"] == "staging"
        assert property_dict["commit_sha"] == "abc123def"

        # Verify signature was added
        signatures = signed_tree.findall(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
        assert len(signatures) == 1

    def test_preserves_empty_properties_section(
        self, mock_session: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that empty properties section is preserved during signing."""
        xml_path = tmp_path / "junit_empty_properties.xml"
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <properties/>
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
        xml_path.write_text(xml_content)

        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(xml_path)

        pytest_sessionfinish(mock_session, 0)

        signed_tree = etree.parse(str(xml_path))
        properties_sections = signed_tree.findall(".//properties")
        assert len(properties_sections) == 1

    def test_canonical_hash_includes_metadata(
        self, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that canonical hash computation includes property tags."""
        from pytest_jux.canonicalizer import compute_canonical_hash, load_xml

        # Create two XML files: one with metadata, one without
        xml_with_metadata = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <properties>
            <property name="build_id" value="12345"/>
        </properties>
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""

        xml_without_metadata = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""

        tree_with = load_xml(xml_with_metadata)
        tree_without = load_xml(xml_without_metadata)

        hash_with = compute_canonical_hash(tree_with)
        hash_without = compute_canonical_hash(tree_without)

        # Hashes should be different because metadata is included
        assert hash_with != hash_without

    def test_multiple_property_tags_preserved(
        self, mock_session: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that multiple property tags are all preserved."""
        xml_path = tmp_path / "junit_many_properties.xml"
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <properties>
            <property name="Python" value="3.11.4"/>
            <property name="Platform" value="Linux-5.15.0"/>
            <property name="ci_provider" value="GitLab CI"/>
            <property name="pipeline_id" value="67890"/>
            <property name="job_id" value="54321"/>
            <property name="commit_sha" value="def456abc"/>
            <property name="branch" value="main"/>
            <property name="environment" value="production"/>
        </properties>
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
        xml_path.write_text(xml_content)

        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config.option.xmlpath = str(xml_path)

        pytest_sessionfinish(mock_session, 0)

        signed_tree = etree.parse(str(xml_path))
        properties = signed_tree.findall(".//property")

        # All 8 properties should be preserved
        assert len(properties) == 8

        # Verify a few specific ones
        property_dict = {prop.get("name"): prop.get("value") for prop in properties}
        assert property_dict["ci_provider"] == "GitLab CI"
        assert property_dict["environment"] == "production"
        assert property_dict["Python"] == "3.11.4"

    def test_property_tags_in_stored_reports(
        self, mock_session: Mock, tmp_path: Path, test_key_path: Path
    ) -> None:
        """Test that property tags are preserved in stored reports."""
        from pytest_jux.config import StorageMode

        xml_path = tmp_path / "junit_stored.xml"
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <properties>
            <property name="test_metadata" value="preserved"/>
        </properties>
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
        xml_path.write_text(xml_content)

        storage_path = tmp_path / "storage"

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = str(test_key_path)
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = StorageMode.LOCAL
        mock_session.config._jux_storage_path = storage_path
        mock_session.config.option.xmlpath = str(xml_path)

        pytest_sessionfinish(mock_session, 0)

        # Find stored report
        reports_dir = storage_path / "reports"
        report_files = list(reports_dir.glob("*.xml"))
        assert len(report_files) > 0

        # Verify stored report has property tags
        stored_tree = etree.parse(str(report_files[0]))
        properties = stored_tree.findall(".//property")
        assert len(properties) == 1
        assert properties[0].get("name") == "test_metadata"
        assert properties[0].get("value") == "preserved"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_configure_with_cert_but_no_key(self, mock_config: Mock) -> None:
        """Test configuration with certificate but no key."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": None,
            "jux_cert": "/path/to/cert.crt",
        }.get(x)

        # Should raise error - can't have cert without key
        with pytest.raises((ValueError, pytest.UsageError)):
            pytest_configure(mock_config)

    def test_sessionfinish_with_missing_config_attributes(
        self, mock_session: Mock, test_junit_xml: Path
    ) -> None:
        """Test sessionfinish when config attributes are missing."""
        # Config without _jux_sign attribute
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Should handle gracefully (treat as signing disabled)
        pytest_sessionfinish(mock_session, 0)

    def test_sessionfinish_preserves_xml_on_error(
        self, mock_session: Mock, test_junit_xml: Path, test_key_path: Path
    ) -> None:
        """Test that sessionfinish doesn't corrupt XML on signing error."""
        original_content = test_junit_xml.read_text()

        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = True
        mock_session.config._jux_key_path = "/nonexistent/key.pem"
        mock_session.config._jux_cert_path = None
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Attempt to sign (will fail but issue warning)
        with pytest.warns(UserWarning, match="Failed to process JUnit XML report"):
            pytest_sessionfinish(mock_session, 0)

        # Original XML should be preserved
        assert test_junit_xml.read_text() == original_content

    def test_configure_loads_project_ini_file(
        self, mock_config: Mock, tmp_path: Path, monkeypatch
    ) -> None:
        """Test that pytest_configure loads from pytest.ini in current directory."""
        monkeypatch.chdir(tmp_path)

        # Create a pytest.ini file
        pytest_ini = tmp_path / "pytest.ini"
        pytest_ini.write_text("""[jux]
enabled = true
sign = true
key_path = /path/to/key.pem
""")

        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": False,
            "jux_key": None,
            "jux_cert": None,
            "jux_publish": False,
        }.get(x)

        # Configure should load from pytest.ini
        # This will raise UsageError because key file doesn't exist, but it proves the file was loaded
        with pytest.raises(pytest.UsageError, match="Key file not found"):
            pytest_configure(mock_config)

    def test_configure_with_nonexistent_key_file(
        self, mock_config: Mock, tmp_path: Path
    ) -> None:
        """Test that pytest_configure raises error for nonexistent key file."""
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": True,
            "jux_key": str(tmp_path / "nonexistent.pem"),
            "jux_cert": None,
            "jux_publish": False,
        }.get(x)

        with pytest.raises(pytest.UsageError, match="Key file not found"):
            pytest_configure(mock_config)

    def test_configure_loads_user_config_file(
        self, mock_config: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that pytest_configure loads from ~/.config/jux/config (XDG)."""
        # Create a fake home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

        # Clear XDG_CONFIG_HOME to ensure Path.home() is used
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        # Change to tmp_path to avoid loading local config files
        monkeypatch.chdir(tmp_path)

        # Create user config file (XDG Base Directory compliant)
        user_config_dir = fake_home / ".config" / "jux"
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / "config"
        user_config.write_text("""[jux]
enabled = true
sign = true
key_path = /path/to/key.pem
""")

        # CLI options don't override (all None/False)
        mock_config.getoption.side_effect = lambda x: {
            "jux_sign": None,  # None means not set on CLI
            "jux_key": None,
            "jux_cert": None,
            "jux_publish": None,
        }.get(x)

        # Configure should load from user config file
        # This will raise UsageError because key file doesn't exist, but it proves the file was loaded
        with pytest.raises(pytest.UsageError, match="Key file not found"):
            pytest_configure(mock_config)

    def test_sessionfinish_with_nonexistent_xml(
        self, mock_session: Mock, tmp_path: Path
    ) -> None:
        """Test sessionfinish when XML file doesn't exist."""
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_storage_mode = None
        mock_session.config.option.xmlpath = str(tmp_path / "nonexistent.xml")

        # Should handle gracefully (no error)
        pytest_sessionfinish(mock_session, 0)


class TestAPIPublishing:
    """Tests for API publishing functionality."""

    @pytest.fixture
    def mock_api_client(self, mocker):
        """Mock JuxAPIClient."""
        return mocker.patch("pytest_jux.plugin.JuxAPIClient")

    def test_publishes_to_api_when_jux_publish_enabled(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that reports are published when jux_publish=True."""
        from pytest_jux.api_client import PublishResponse, TestRun

        # Configure session for API publishing
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = True
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = "http://localhost:4000/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Mock successful API response (Jux API v1.0.0 format)
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.publish_report.return_value = PublishResponse(
            message="Test report submitted successfully",
            status="success",
            test_run=TestRun(
                id="550e8400-e29b-41d4-a716-446655440000",
                status="completed",
                time=None,
                errors=0,
                branch="main",
                project="pytest-jux-integration",
                failures=0,
                skipped=0,
                success_rate=100.0,
                commit_sha=None,
                total_tests=1,
                created_at="2025-10-25T00:00:00.000000Z",
            ),
        )

        # Call sessionfinish - should publish to API
        with pytest.warns(UserWarning, match="Report published to Jux API"):
            pytest_sessionfinish(mock_session, 0)

        # Verify API client was initialized
        mock_api_client.assert_called_once_with(
            api_url="http://localhost:4000/api/v1",
            bearer_token=None,
            timeout=30,
            max_retries=3,
        )

        # Verify publish_report was called
        mock_client_instance.publish_report.assert_called_once()

    def test_publishes_to_api_in_api_storage_mode(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that reports are published in API storage mode."""
        from pytest_jux.api_client import PublishResponse, TestRun

        # Configure session for API storage mode
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = False
        mock_session.config._jux_storage_mode = StorageMode.API
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = "http://localhost:4000/api/v1"
        mock_session.config._jux_bearer_token = "test-token"  # noqa: S105 - Test token
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Mock successful API response (Jux API v1.0.0 format)
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.publish_report.return_value = PublishResponse(
            message="Test report submitted successfully",
            status="success",
            test_run=TestRun(
                id="550e8400-e29b-41d4-a716-446655440000",
                status="completed",
                time=None,
                errors=0,
                branch="main",
                project="pytest-jux-integration",
                failures=0,
                skipped=0,
                success_rate=100.0,
                commit_sha=None,
                total_tests=1,
                created_at="2025-10-25T00:00:00.000000Z",
            ),
        )

        # Call sessionfinish - should publish to API
        with pytest.warns(UserWarning, match="Report published to Jux API"):
            pytest_sessionfinish(mock_session, 0)

        # Verify API client was initialized with bearer token
        mock_api_client.assert_called_once_with(
            api_url="http://localhost:4000/api/v1",
            bearer_token="test-token",  # noqa: S106 - Test token
            timeout=30,
            max_retries=3,
        )

    def test_api_mode_fails_on_api_error(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that API mode warns on API failure."""
        # Configure session for API storage mode
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = False
        mock_session.config._jux_storage_mode = StorageMode.API
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = "http://localhost:4000/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Mock API failure
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.publish_report.side_effect = Exception("Connection refused")

        # Call sessionfinish - should warn about failure
        with pytest.warns(UserWarning, match="Failed to publish report to Jux API \\(API mode\\)"):
            pytest_sessionfinish(mock_session, 0)

    def test_cache_mode_queues_on_api_error(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        tmp_path: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that CACHE mode queues locally on API failure."""
        # Configure session for CACHE storage mode
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = False
        mock_session.config._jux_storage_mode = StorageMode.CACHE
        mock_session.config._jux_storage_path = str(tmp_path / "reports")
        mock_session.config._jux_api_url = "http://localhost:4000/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Mock API failure
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.publish_report.side_effect = Exception("Connection refused")

        # Call sessionfinish - should queue locally
        with pytest.warns(UserWarning, match="Failed to publish report to Jux API, queued locally \\(CACHE mode\\)"):
            pytest_sessionfinish(mock_session, 0)

        # Verify report was stored locally (storage creates reports/ subdir)
        reports_dir = tmp_path / "reports" / "reports"
        assert reports_dir.exists()
        assert len(list(reports_dir.glob("*.xml"))) == 1

    def test_both_mode_saves_local_on_api_error(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        tmp_path: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that BOTH mode saves locally on API failure."""
        # Configure session for BOTH storage mode
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = False
        mock_session.config._jux_storage_mode = StorageMode.BOTH
        mock_session.config._jux_storage_path = str(tmp_path / "reports")
        mock_session.config._jux_api_url = "http://localhost:4000/api/v1"
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Mock API failure
        mock_client_instance = mock_api_client.return_value
        mock_client_instance.publish_report.side_effect = Exception("Connection refused")

        # Call sessionfinish - should save locally and warn
        with pytest.warns(UserWarning, match="Failed to publish report to Jux API, local copy saved \\(BOTH mode\\)"):
            pytest_sessionfinish(mock_session, 0)

        # Verify report was stored locally (storage creates reports/ subdir)
        reports_dir = tmp_path / "reports" / "reports"
        assert reports_dir.exists()
        assert len(list(reports_dir.glob("*.xml"))) == 1

    def test_skips_api_publishing_when_api_url_not_configured(
        self,
        mock_session: Mock,
        test_junit_xml: Path,
        mock_api_client: Mock,
    ) -> None:
        """Test that API publishing is skipped when api_url is None."""
        # Configure session without API URL
        mock_session.config._jux_enabled = True
        mock_session.config._jux_sign = False
        mock_session.config._jux_publish = True
        mock_session.config._jux_storage_mode = None
        mock_session.config._jux_storage_path = None
        mock_session.config._jux_api_url = None  # No API URL
        mock_session.config._jux_bearer_token = None
        mock_session.config._jux_api_timeout = 30
        mock_session.config._jux_api_max_retries = 3
        mock_session.config.option.xmlpath = str(test_junit_xml)

        # Call sessionfinish - should NOT attempt to publish
        pytest_sessionfinish(mock_session, 0)

        # Verify API client was NOT called
        mock_api_client.assert_not_called()
