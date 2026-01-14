#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prisma Cloud CSV Integration Helper Functions

This module provides reusable helper functions for the Prisma Cloud CSV-based
integration with RegScale. These functions handle validation, parsing, and
data transformation for Prisma Cloud vulnerability scan exports.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from regscale.models.regscale_models.issue import IssueSeverity

# Initialize logger
logger = logging.getLogger(__name__)


# ============================================================================
# Validation Functions
# ============================================================================


def validate_cve_format(cve: Optional[str]) -> Optional[str]:
    """
    Validate CVE format and return uppercase version if valid.

    CVE format must match: CVE-YYYY-NNNN (where NNNN is 4+ digits)
    Examples: CVE-2024-1234, CVE-2023-12345

    Args:
        cve: CVE string to validate (e.g., "cve-2024-1234")

    Returns:
        Uppercase CVE string if valid, None otherwise

    Examples:
        >>> validate_cve_format("cve-2024-1234")
        "CVE-2024-1234"
        >>> validate_cve_format("invalid")
        None
    """
    if not cve:
        return None

    # CVE pattern: CVE-YYYY-NNNN (4+ digits for ID)
    cve_pattern = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

    cve_upper = cve.upper().strip()
    if cve_pattern.match(cve_upper):
        return cve_upper
    else:
        logger.debug(f"Invalid CVE format: {cve}")
        return None


def validate_cvss_score(cvss: Optional[float]) -> Optional[float]:
    """
    Validate CVSS score is within valid range (0.0-10.0).

    Args:
        cvss: CVSS score to validate

    Returns:
        Valid CVSS score (0.0-10.0) or None if invalid

    Examples:
        >>> validate_cvss_score(7.5)
        7.5
        >>> validate_cvss_score(11.0)
        None
    """
    if cvss is None:
        return None

    try:
        score = float(cvss)
        if 0.0 <= score <= 10.0:
            return score
        else:
            logger.warning(f"CVSS score out of range (0-10): {cvss}")
            return None
    except (ValueError, TypeError):
        logger.warning(f"Invalid CVSS score format: {cvss}")
        return None


def validate_required_fields(row_data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required fields are present and non-empty in row data.

    Args:
        row_data: Dictionary of CSV row data
        required_fields: List of field names that must be present

    Returns:
        Tuple of (is_valid: bool, missing_fields: List[str])

    Examples:
        >>> validate_required_fields({"hostname": "test"}, ["hostname", "ip"])
        (False, ["ip"])
    """
    missing_fields = []

    for field in required_fields:
        value = row_data.get(field)
        if not value or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field)

    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields


# ============================================================================
# CVSS to Severity Mapping
# ============================================================================


def map_cvss_to_severity(cvss_score: Optional[float]) -> IssueSeverity:
    """
    Map CVSS v3 score to RegScale IssueSeverity enum.

    Mapping based on CVSS v3 severity ratings:
    - 0.0: None
    - 0.1-3.9: Low
    - 4.0-6.9: Medium
    - 7.0-8.9: High
    - 9.0-10.0: Critical

    Args:
        cvss_score: CVSS v3 score (0.0-10.0)

    Returns:
        RegScale IssueSeverity enum value

    Examples:
        >>> map_cvss_to_severity(7.5)
        IssueSeverity.High
        >>> map_cvss_to_severity(None)
        IssueSeverity.NotAssigned
    """
    if cvss_score is None:
        return IssueSeverity.NotAssigned

    validated_score = validate_cvss_score(cvss_score)
    if validated_score is None:
        return IssueSeverity.NotAssigned

    # Use threshold comparison instead of direct float equality
    if validated_score < 0.1:
        return IssueSeverity.NotAssigned
    elif validated_score < 4.0:
        return IssueSeverity.Low
    elif validated_score < 7.0:
        return IssueSeverity.Moderate
    elif validated_score < 9.0:
        return IssueSeverity.High
    elif validated_score <= 10.0:
        return IssueSeverity.Critical
    else:
        return IssueSeverity.NotAssigned


# ============================================================================
# String Parsing Functions
# ============================================================================


def split_comma_separated_values(value: Optional[str]) -> List[str]:
    """
    Split comma-separated string into list of trimmed, non-empty values.

    Args:
        value: Comma-separated string (e.g., "host1.com, host2.com, host3.com")

    Returns:
        List of trimmed, non-empty strings

    Examples:
        >>> split_comma_separated_values("host1, host2, host3")
        ["host1", "host2", "host3"]
        >>> split_comma_separated_values(None)
        []
    """
    if not value:
        return []

    if not isinstance(value, str):
        return []

    # Split by comma, strip whitespace, filter empty strings
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


def parse_operating_system(os_string: Optional[str]) -> Optional[str]:
    """
    Parse and normalize operating system string from Prisma Cloud.

    Handles various OS formats:
    - "Ubuntu 20.04.6 LTS" -> "Ubuntu 20.04 LTS"
    - "Alpine Linux v3.14" -> "Alpine Linux 3.14"
    - "Red Hat Enterprise Linux 8.5" -> "RHEL 8.5"

    Args:
        os_string: Raw OS string from Prisma Cloud

    Returns:
        Normalized OS string or None if invalid

    Examples:
        >>> parse_operating_system("Ubuntu 20.04.6 LTS")
        "Ubuntu 20.04 LTS"
    """
    if not os_string or not isinstance(os_string, str):
        return None

    os_normalized = os_string.strip()

    # Remove patch versions (e.g., 20.04.6 -> 20.04)
    # Use lookahead assertion to prevent backtracking vulnerability
    # Pattern: (number.number).number followed by whitespace or end of string
    os_normalized = re.sub(r"(\d+\.\d+)\.\d+(?=\s|$)", r"\1", os_normalized)

    # Remove "v" prefix from versions (e.g., v3.14 -> 3.14)
    os_normalized = re.sub(r"\bv(\d+)", r"\1", os_normalized)

    # Abbreviate Red Hat Enterprise Linux
    os_normalized = os_normalized.replace("Red Hat Enterprise Linux", "RHEL")

    return os_normalized if os_normalized else None


def extract_fqdn(hostname: Optional[str]) -> Optional[str]:
    """
    Extract and validate FQDN from hostname string.

    Valid FQDN must contain at least one dot and valid characters.
    Examples: "host.example.com", "web-server.prod.company.io"

    Args:
        hostname: Hostname or FQDN string

    Returns:
        FQDN if valid, None otherwise

    Examples:
        >>> extract_fqdn("web-server-01.example.com")
        "web-server-01.example.com"
        >>> extract_fqdn("localhost")
        None
    """
    if not hostname or not isinstance(hostname, str):
        return None

    hostname = hostname.strip().lower()

    # FQDN must contain at least one dot
    if "." not in hostname:
        return None

    # Basic FQDN validation pattern - optimized to prevent backtracking
    # Split validation into parts to avoid nested quantifiers
    parts = hostname.split(".")

    # Each label must be 1-63 chars, start/end with alphanumeric, contain only alphanumeric or hyphen
    label_pattern = re.compile(r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$", re.IGNORECASE)

    # Validate each label
    if all(label_pattern.match(part) for part in parts if part):
        return hostname
    else:
        logger.debug(f"Invalid FQDN format: {hostname}")
        return None


def determine_asset_identifier(
    hostname: Optional[str], ip_address: Optional[str], image_id: Optional[str], other_tracking_number: Optional[str]
) -> Optional[str]:
    """
    Determine the best identifier for an asset based on available fields.

    Priority order:
    1. Other tracking number (Prisma Cloud resource ID)
    2. Image ID (for container images)
    3. Hostname (for VMs/hosts)
    4. IP address (fallback)

    Args:
        hostname: Asset hostname or FQDN
        ip_address: Asset IP address
        image_id: Container image ID/digest
        other_tracking_number: Prisma Cloud tracking number

    Returns:
        Best available identifier or None

    Examples:
        >>> determine_asset_identifier("host.com", "10.0.1.1", None, "prisma-123")
        "prisma-123"
    """
    if other_tracking_number and other_tracking_number.strip():
        return other_tracking_number.strip()

    if image_id and image_id.strip():
        return image_id.strip()

    if hostname and hostname.strip():
        return hostname.strip()

    if ip_address and ip_address.strip():
        return ip_address.strip()

    return None


def truncate_description(description: Optional[str], max_length: int = 5000) -> Optional[str]:
    """
    Truncate description to maximum length with ellipsis if needed.

    Args:
        description: Description text to truncate
        max_length: Maximum allowed length (default: 5000)

    Returns:
        Truncated description or None if input is None

    Examples:
        >>> truncate_description("A" * 6000, max_length=100)
        "AAAA...AAAA (truncated from 6000 chars)"
    """
    if description is None:
        return None

    if not isinstance(description, str):
        description = str(description)

    if len(description) <= max_length:
        return description

    # Truncate and add ellipsis
    truncated = description[: max_length - 50]
    truncated += f"... (truncated from {len(description)} chars)"

    return truncated


# ============================================================================
# Asset Property Building
# ============================================================================


def _build_container_asset_properties(
    properties: Dict[str, Any],
    image_name: Optional[str],
    image_id: Optional[str],
    asset_type: Optional[str],
    asset_category: Optional[str],
) -> None:
    """Helper to build container-specific asset properties."""
    properties.update(
        {
            "asset_type": asset_type or "Container Image",
            "asset_category": asset_category or "Software",
        }
    )

    if image_name:
        properties["name"] = image_name

    if image_id:
        properties["other_tracking_number"] = image_id
        properties["identifier"] = image_id


def _build_host_asset_properties(
    properties: Dict[str, Any],
    hostname: str,
    ip_address: Optional[str],
    asset_type: Optional[str],
    asset_category: Optional[str],
) -> None:
    """Helper to build host/VM-specific asset properties."""
    properties.update(
        {
            "asset_type": asset_type or "Virtual Machine (VM)",
            "asset_category": asset_category or "Server",
        }
    )

    if ip_address:
        properties["ip_address"] = ip_address

    # Extract FQDN if hostname looks like one
    fqdn = extract_fqdn(hostname)
    if fqdn:
        properties["fqdn"] = fqdn


def build_asset_properties(
    hostname: str,
    ip_address: Optional[str] = None,
    distro: Optional[str] = None,
    image_name: Optional[str] = None,
    image_id: Optional[str] = None,
    scanning_tool: str = "Prisma",
    asset_type: Optional[str] = None,
    asset_category: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build complete asset property dictionary from CSV row data.

    Supports both host/VM assets and container image assets.

    Args:
        hostname: Asset hostname or container image name
        ip_address: IP address (for hosts)
        distro: Operating system/distribution
        image_name: Container image name (for containers)
        image_id: Container image ID/digest (for containers)
        scanning_tool: Name of scanning tool (default: "Prisma")
        asset_type: Asset type override
        asset_category: Asset category override
        **kwargs: Additional properties to include

    Returns:
        Dictionary of asset properties ready for IntegrationAsset

    Examples:
        >>> build_asset_properties(
        ...     hostname="web-server-01.example.com",
        ...     ip_address="10.0.1.50",
        ...     distro="Ubuntu 20.04 LTS"
        ... )
        {
            "name": "web-server-01.example.com",
            "ipAddress": "10.0.1.50",
            "operatingSystem": "Ubuntu 20.04 LTS",
            ...
        }
    """
    properties = {
        "name": hostname,
        "scanning_tool": scanning_tool,
    }

    # Determine if this is a container or host asset
    is_container = bool(image_name or image_id)

    if is_container:
        _build_container_asset_properties(properties, image_name, image_id, asset_type, asset_category)
    else:
        _build_host_asset_properties(properties, hostname, ip_address, asset_type, asset_category)

    # Common properties
    if distro:
        normalized_os = parse_operating_system(distro)
        if normalized_os:
            properties["operating_system"] = normalized_os

    # Determine best identifier
    identifier = determine_asset_identifier(
        hostname=hostname,
        ip_address=ip_address,
        image_id=image_id,
        other_tracking_number=kwargs.get("other_tracking_number"),
    )
    if identifier:
        properties["identifier"] = identifier

    # Add any additional properties from kwargs
    for key, value in kwargs.items():
        if key not in properties and value is not None:
            properties[key] = value

    return properties


# ============================================================================
# Finding Property Building
# ============================================================================


def _build_remediation_text(
    recommendation: Optional[str], fixed_version: Optional[str], package_name: Optional[str]
) -> Optional[str]:
    """Helper to build remediation recommendation text."""
    if recommendation:
        return truncate_description(recommendation, max_length=2000)
    elif fixed_version:
        # Generate recommendation from fixed version
        if package_name:
            return f"Update {package_name} to version {fixed_version} or later"
        else:
            return f"Update to version {fixed_version} or later"
    return None


def _build_package_extra_data(
    package_name: Optional[str], package_version: Optional[str], fixed_version: Optional[str]
) -> Dict[str, Any]:
    """Helper to build package information dictionary for extra_data."""
    extra_data = {}
    if package_name:
        extra_data["package_name"] = package_name
    if package_version:
        extra_data["package_version"] = package_version
    if fixed_version:
        extra_data["fixed_version"] = fixed_version
    return extra_data


def build_finding_properties(
    cve: str,
    cvss_score: Optional[float],
    title: Optional[str] = None,
    description: Optional[str] = None,
    recommendation: Optional[str] = None,
    package_name: Optional[str] = None,
    package_version: Optional[str] = None,
    fixed_version: Optional[str] = None,
    asset_identifier: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build complete finding property dictionary from CSV row data.

    Args:
        cve: CVE identifier (e.g., "CVE-2024-1234")
        cvss_score: CVSS v3 score (0.0-10.0)
        title: Finding title (defaults to CVE if not provided)
        description: Vulnerability description
        recommendation: Remediation recommendation
        package_name: Affected package name
        package_version: Current package version
        fixed_version: Fixed package version
        asset_identifier: Parent asset identifier
        **kwargs: Additional properties to include

    Returns:
        Dictionary of finding properties ready for IntegrationFinding

    Examples:
        >>> build_finding_properties(
        ...     cve="CVE-2024-1234",
        ...     cvss_score=7.5,
        ...     package_name="openssl",
        ...     package_version="1.1.1u"
        ... )
        {
            "cve": "CVE-2024-1234",
            "cvssV3Score": 7.5,
            "severity": IssueSeverity.High,
            ...
        }
    """
    # Validate CVE format
    validated_cve = validate_cve_format(cve)
    if not validated_cve:
        logger.warning(f"Invalid CVE format: {cve}")
        validated_cve = cve  # Keep original if validation fails

    # Validate CVSS score and map to severity
    validated_cvss = validate_cvss_score(cvss_score)
    severity = map_cvss_to_severity(validated_cvss)

    properties = {
        "cve": validated_cve,
        "plugin_id": validated_cve,  # Use CVE as plugin ID
        "title": title or validated_cve,
        "category": "Vulnerability",
        "severity": severity,
    }

    # Add CVSS score if valid
    if validated_cvss is not None:
        properties["cvss_v3_score"] = validated_cvss

    # Add description (truncated if needed)
    if description:
        properties["description"] = truncate_description(description, max_length=5000)

    # Add remediation guidance
    remediation = _build_remediation_text(recommendation, fixed_version, package_name)
    if remediation:
        properties["recommendation_for_mitigation"] = remediation

    # Add package information to extra_data
    extra_data = _build_package_extra_data(package_name, package_version, fixed_version)
    if extra_data:
        properties["extra_data"] = extra_data

    # Add asset identifier for linking
    if asset_identifier:
        properties["asset_identifier"] = asset_identifier

    # Add plugin name (combination of CVE and package)
    if package_name:
        properties["plugin_name"] = f"{validated_cve} in {package_name}"
    else:
        properties["plugin_name"] = validated_cve

    # Add any additional properties from kwargs
    for key, value in kwargs.items():
        if key not in properties and value is not None:
            properties[key] = value

    return properties


# ============================================================================
# Software Inventory Parsing
# ============================================================================


def parse_software_package(
    package_data: Dict[str, Any], asset_identifier: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Parse software package information from CSV row or package data.

    Args:
        package_data: Dictionary containing package information
                     (name, version, license, etc.)
        asset_identifier: Parent asset identifier for grouping

    Returns:
        Dictionary of software package properties or None if invalid

    Examples:
        >>> parse_software_package({
        ...     "name": "openssl",
        ...     "version": "1.1.1u",
        ...     "license": "Apache-2.0"
        ... })
        {
            "name": "openssl",
            "version": "1.1.1u",
            "license": "Apache-2.0",
            ...
        }
    """
    if not package_data:
        return None

    name = package_data.get("name") or package_data.get("packageName")
    version = package_data.get("version") or package_data.get("packageVersion")

    # Minimum required fields
    if not name:
        logger.debug("Software package missing required 'name' field")
        return None

    properties = {
        "name": str(name).strip(),
        "version": str(version).strip() if version else "unknown",
    }

    # Optional fields
    if "license" in package_data and package_data["license"]:
        properties["license"] = str(package_data["license"]).strip()

    if "description" in package_data and package_data["description"]:
        properties["description"] = truncate_description(package_data["description"], max_length=500)

    if "vendor" in package_data and package_data["vendor"]:
        properties["vendor"] = str(package_data["vendor"]).strip()

    # Link to parent asset
    if asset_identifier:
        properties["assetIdentifier"] = asset_identifier

    return properties


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Validation
    "validate_cve_format",
    "validate_cvss_score",
    "validate_required_fields",
    # CVSS Mapping
    "map_cvss_to_severity",
    # String Parsing
    "split_comma_separated_values",
    "parse_operating_system",
    "extract_fqdn",
    "determine_asset_identifier",
    "truncate_description",
    # Property Building
    "build_asset_properties",
    "build_finding_properties",
    # Software Inventory
    "parse_software_package",
]
