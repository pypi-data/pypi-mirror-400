"""Unit tests for Prisma modules helper functions."""

import pytest

from regscale.integrations.commercial.prisma_modules import (
    build_asset_properties,
    build_finding_properties,
    extract_fqdn,
    map_cvss_to_severity,
    parse_operating_system,
    parse_software_package,
    split_comma_separated_values,
    truncate_description,
    validate_cve_format,
    validate_cvss_score,
)
from regscale.models.regscale_models import IssueSeverity


class TestValidation:
    """Test validation functions."""

    def test_validate_cve_format_valid(self):
        """Test CVE format validation with valid CVEs."""
        assert validate_cve_format("CVE-2024-1234") == "CVE-2024-1234"
        assert validate_cve_format("cve-2023-12345") == "CVE-2023-12345"
        assert validate_cve_format("CVE-2022-123456") == "CVE-2022-123456"

    def test_validate_cve_format_invalid(self):
        """Test CVE format validation with invalid CVEs."""
        assert validate_cve_format("INVALID") is None
        assert validate_cve_format("CVE-2024") is None
        assert validate_cve_format("CVE-2024-123") is None  # Too few digits
        assert validate_cve_format("") is None
        assert validate_cve_format(None) is None

    def test_validate_cvss_score_valid(self):
        """Test CVSS score validation with valid scores."""
        assert validate_cvss_score(0.0) == 0.0
        assert validate_cvss_score(5.5) == 5.5
        assert validate_cvss_score(10.0) == 10.0
        assert validate_cvss_score("7.5") == 7.5
        assert validate_cvss_score("9.8") == 9.8

    def test_validate_cvss_score_invalid(self):
        """Test CVSS score validation with invalid scores."""
        assert validate_cvss_score(-1.0) is None
        assert validate_cvss_score(10.1) is None
        assert validate_cvss_score("invalid") is None
        assert validate_cvss_score(None) is None


class TestCVSSMapping:
    """Test CVSS to severity mapping."""

    def test_map_cvss_to_severity_thresholds(self):
        """Test CVSS score to severity mapping at various thresholds."""
        assert map_cvss_to_severity(0.0) == IssueSeverity.NotAssigned
        assert map_cvss_to_severity(0.1) == IssueSeverity.Low
        assert map_cvss_to_severity(3.9) == IssueSeverity.Low
        assert map_cvss_to_severity(4.0) == IssueSeverity.Moderate
        assert map_cvss_to_severity(6.9) == IssueSeverity.Moderate
        assert map_cvss_to_severity(7.0) == IssueSeverity.High
        assert map_cvss_to_severity(8.9) == IssueSeverity.High
        assert map_cvss_to_severity(9.0) == IssueSeverity.Critical
        assert map_cvss_to_severity(10.0) == IssueSeverity.Critical

    def test_map_cvss_to_severity_none(self):
        """Test CVSS mapping with None value."""
        assert map_cvss_to_severity(None) == IssueSeverity.NotAssigned


class TestStringParsing:
    """Test string parsing functions."""

    def test_split_comma_separated_values(self):
        """Test splitting comma-separated values."""
        assert split_comma_separated_values("host1, host2, host3") == ["host1", "host2", "host3"]
        assert split_comma_separated_values("single") == ["single"]
        assert split_comma_separated_values("") == []
        assert split_comma_separated_values(None) == []
        assert split_comma_separated_values("  spaced  ,  values  ") == ["spaced", "values"]

    def test_parse_operating_system_patch_removal(self):
        """Test OS string parsing removes patch versions correctly."""
        # This is the key test for the regex backtracking fix
        assert parse_operating_system("Ubuntu 20.04.6 LTS") == "Ubuntu 20.04 LTS"
        assert parse_operating_system("CentOS 7.9.2009") == "CentOS 7.9"
        assert parse_operating_system("Debian 11.8") == "Debian 11.8"  # No patch, unchanged

    def test_parse_operating_system_v_prefix_removal(self):
        """Test OS string parsing removes 'v' prefix from versions."""
        assert parse_operating_system("Alpine Linux v3.14") == "Alpine Linux 3.14"
        assert parse_operating_system("Alpine v3.18.0") == "Alpine 3.18"

    def test_parse_operating_system_rhel_abbreviation(self):
        """Test OS string parsing abbreviates Red Hat Enterprise Linux."""
        assert parse_operating_system("Red Hat Enterprise Linux 8.5") == "RHEL 8.5"
        assert parse_operating_system("Red Hat Enterprise Linux 9.2.1") == "RHEL 9.2"

    def test_parse_operating_system_invalid(self):
        """Test OS string parsing with invalid inputs."""
        assert parse_operating_system(None) is None
        assert parse_operating_system("") is None
        assert parse_operating_system(123) is None

    def test_extract_fqdn_valid(self):
        """Test FQDN extraction with valid hostnames."""
        assert extract_fqdn("web-server-01.example.com") == "web-server-01.example.com"
        assert extract_fqdn("host.domain.local") == "host.domain.local"
        assert extract_fqdn("TEST.EXAMPLE.COM") == "test.example.com"

    def test_extract_fqdn_invalid(self):
        """Test FQDN extraction with invalid hostnames."""
        assert extract_fqdn("localhost") is None  # No dot
        assert extract_fqdn("-invalid.com") is None  # Starts with hyphen
        assert extract_fqdn("invalid-.com") is None  # Ends with hyphen
        assert extract_fqdn(None) is None
        assert extract_fqdn("") is None

    def test_truncate_description(self):
        """Test description truncation."""
        short = "Short description"
        assert truncate_description(short, 1000) == short

        long = "A" * 6000
        truncated = truncate_description(long, 100)
        # Function truncates to max_length - 50, then adds message
        # So total length will be less than max_length
        assert len(truncated) <= 100
        assert "truncated from 6000 chars" in truncated

        assert truncate_description(None) is None


class TestAssetProperties:
    """Test asset property building functions."""

    def test_build_asset_properties_host(self):
        """Test building properties for host/VM assets."""
        props = build_asset_properties(
            hostname="web-server-01.example.com",
            ip_address="10.0.1.50",
            distro="Ubuntu 20.04 LTS",
        )

        assert props["name"] == "web-server-01.example.com"
        assert props["ip_address"] == "10.0.1.50"
        assert props["operating_system"] == "Ubuntu 20.04 LTS"
        assert props["asset_type"] == "Virtual Machine (VM)"
        assert props["asset_category"] == "Server"
        assert props["fqdn"] == "web-server-01.example.com"

    def test_build_asset_properties_container(self):
        """Test building properties for container image assets."""
        props = build_asset_properties(
            hostname="nginx",
            image_name="nginx:1.21",
            image_id="sha256:abc123",
        )

        assert props["name"] == "nginx:1.21"
        assert props["asset_type"] == "Container Image"
        assert props["asset_category"] == "Software"
        assert props["other_tracking_number"] == "sha256:abc123"


class TestFindingProperties:
    """Test finding property building functions."""

    def test_build_finding_properties_basic(self):
        """Test building basic finding properties."""
        props = build_finding_properties(
            cve="CVE-2024-1234",
            cvss_score=7.5,
            title="Test Vulnerability",
            description="Test description",
        )

        assert props["cve"] == "CVE-2024-1234"
        assert props["cvss_v3_score"] == 7.5
        assert props["severity"] == IssueSeverity.High
        assert props["title"] == "Test Vulnerability"
        assert props["description"] == "Test description"

    def test_build_finding_properties_with_package(self):
        """Test building finding properties with package information."""
        props = build_finding_properties(
            cve="CVE-2024-5678",
            cvss_score=9.1,
            package_name="openssl",
            package_version="1.1.1u",
            fixed_version="1.1.1v",
        )

        assert props["severity"] == IssueSeverity.Critical
        assert "extra_data" in props
        assert props["extra_data"]["package_name"] == "openssl"
        assert props["extra_data"]["package_version"] == "1.1.1u"
        assert props["extra_data"]["fixed_version"] == "1.1.1v"
        assert "Update openssl to version 1.1.1v" in props["recommendation_for_mitigation"]


class TestSoftwarePackage:
    """Test software package parsing."""

    def test_parse_software_package_valid(self):
        """Test parsing valid software package data."""
        package_data = {
            "name": "openssl",
            "version": "1.1.1u",
            "license": "Apache-2.0",
        }

        result = parse_software_package(package_data)
        assert result["name"] == "openssl"
        assert result["version"] == "1.1.1u"
        assert result["license"] == "Apache-2.0"

    def test_parse_software_package_missing_name(self):
        """Test parsing package with missing name."""
        package_data = {
            "version": "1.0.0",
        }

        assert parse_software_package(package_data) is None

    def test_parse_software_package_no_version(self):
        """Test parsing package with no version."""
        package_data = {
            "name": "test-package",
        }

        result = parse_software_package(package_data)
        assert result["name"] == "test-package"
        assert result["version"] == "unknown"
