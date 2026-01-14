"""
Qualys URL transformation utilities.

Handles proper URL transformations for different Qualys API services across all platforms.
Based on https://www.qualys.com/platform-identification
"""

import logging
import re
from typing import Tuple
from urllib.parse import urlparse

logger = logging.getLogger("regscale")

# Domain constants
QUALYS_COM_DOMAIN = "qualys.com"


def transform_to_gateway_url(base_url: str) -> str:
    """
    Transform Qualys base URL to gateway URL for Container Security and Asset Inventory APIs.

    Supports all Qualys platforms (US1-4, EU1-3, IN1, CA1, AE1, UK1, AU1, KSA1, etc.)

    Examples:
        https://qualysguard.qualys.com -> https://gateway.qg1.apps.qualys.com
        https://qualysapi.qualys.com -> https://gateway.qg1.apps.qualys.com
        https://qualysguard.qg2.apps.qualys.com -> https://gateway.qg2.apps.qualys.com
        https://qualysapi.qg3.apps.qualys.eu -> https://gateway.qg3.apps.qualys.eu

    :param str base_url: The Qualys base URL (qualysguard or qualysapi format)
    :return: Gateway URL for Container Security/Asset Inventory APIs
    :rtype: str
    """
    parsed = urlparse(base_url)
    hostname = parsed.hostname or ""

    # Pattern: qualysguard or qualysapi, optional platform (qg1-qg4), apps subdomain, domain
    # Examples:
    #   qualysguard.qualys.com (US1 - legacy)
    #   qualysguard.qg2.apps.qualys.com (US2)
    #   qualysapi.qg3.apps.qualys.eu (EU3)

    # Handle legacy US1 format (qualysguard.qualys.com or qualysapi.qualys.com)
    if hostname in [f"qualysguard.{QUALYS_COM_DOMAIN}", f"qualysapi.{QUALYS_COM_DOMAIN}"]:
        gateway_hostname = f"gateway.qg1.apps.{QUALYS_COM_DOMAIN}"
        logger.debug("URL Transform: %s -> %s (US1 legacy format)", hostname, gateway_hostname)
        return f"{parsed.scheme}://{gateway_hostname}"

    # Modern format: subdomain.platform.apps.domain
    # Replace qualysguard or qualysapi with gateway, preserve platform and domain
    if "qualysguard" in hostname:
        gateway_hostname = hostname.replace("qualysguard", "gateway")
    elif "qualysapi" in hostname:
        gateway_hostname = hostname.replace("qualysapi", "gateway")
    else:
        # Already a gateway URL or unknown format
        logger.warning("URL Transform: Unrecognized format %s, returning as-is", hostname)
        return base_url

    logger.debug("URL Transform: %s -> %s", hostname, gateway_hostname)
    return f"{parsed.scheme}://{gateway_hostname}"


def transform_to_api_url(base_url: str) -> str:
    """
    Transform Qualys base URL to API URL for VMDR, WAS, and Policy Compliance APIs.

    Most APIs use the standard qualysguard or qualysapi format without transformation.
    This function ensures the URL is in the correct format.

    Examples:
        https://qualysguard.qualys.com -> https://qualysapi.qualys.com (US1)
        https://qualysguard.qg2.apps.qualys.com -> https://qualysapi.qg2.apps.qualys.com (US2)
        https://gateway.qg3.apps.qualys.eu -> https://qualysapi.qg3.apps.qualys.eu (EU3)

    :param str base_url: The Qualys base URL
    :return: API URL for VMDR/WAS/Policy APIs
    :rtype: str
    """
    parsed = urlparse(base_url)
    hostname = parsed.hostname or ""

    # Handle legacy US1 format
    if hostname == f"qualysguard.{QUALYS_COM_DOMAIN}":
        api_hostname = f"qualysapi.{QUALYS_COM_DOMAIN}"
        logger.debug("URL Transform: %s -> %s (US1 API format)", hostname, api_hostname)
        return f"{parsed.scheme}://{api_hostname}"

    # Modern format: Replace qualysguard or gateway with qualysapi
    if "qualysguard" in hostname:
        api_hostname = hostname.replace("qualysguard", "qualysapi")
    elif "gateway" in hostname:
        api_hostname = hostname.replace("gateway", "qualysapi")
    elif "qualysapi" in hostname:
        # Already in API format
        return base_url
    else:
        logger.warning("URL Transform: Unrecognized format %s, returning as-is", hostname)
        return base_url

    logger.debug("URL Transform: %s -> %s", hostname, api_hostname)
    return f"{parsed.scheme}://{api_hostname}"


def parse_qualys_platform(base_url: str) -> Tuple[str, str, str]:
    """
    Parse Qualys URL to extract platform information.

    :param str base_url: The Qualys base URL
    :return: Tuple of (platform_id, subdomain, domain) e.g. ('US2', 'qg2', 'qualys.com')
    :rtype: Tuple[str, str, str]
    """
    parsed = urlparse(base_url)
    hostname = parsed.hostname or ""

    # Legacy US1 format
    if QUALYS_COM_DOMAIN in hostname and "apps" not in hostname:
        return ("US1", "qg1", QUALYS_COM_DOMAIN)

    # Extract platform from hostname (e.g., qg2, qg3, qg4)
    platform_match = re.search(r"\.qg(\d)\.apps\.", hostname)
    if platform_match:
        platform_num = platform_match.group(1)
        # Determine region from domain suffix
        if ".qualys.eu" in hostname:
            platform_id = f"EU{platform_num}"
            domain = "qualys.eu"
        elif ".qualys.in" in hostname:
            platform_id = f"IN{platform_num}"
            domain = "qualys.in"
        elif ".qualys.ca" in hostname:
            platform_id = f"CA{platform_num}"
            domain = "qualys.ca"
        elif ".qualys.ae" in hostname:
            platform_id = f"AE{platform_num}"
            domain = "qualys.ae"
        elif ".qualys.co.uk" in hostname:
            platform_id = f"UK{platform_num}"
            domain = "qualys.co.uk"
        elif ".qualys.com.au" in hostname:
            platform_id = f"AU{platform_num}"
            domain = "qualys.com.au"
        elif ".qualysksa.com" in hostname:
            platform_id = f"KSA{platform_num}"
            domain = "qualysksa.com"
        else:
            # Default to US
            platform_id = f"US{platform_num}"
            domain = QUALYS_COM_DOMAIN

        return (platform_id, f"qg{platform_num}", domain)

    # Unable to parse
    logger.warning("Unable to parse platform from URL: %s", hostname)
    return ("UNKNOWN", "unknown", "unknown")


# API Version Constants - ordered from newest to oldest for fallback
CONTAINER_SECURITY_API_VERSIONS = ["v1.3", "v1.2", "v1.1", "v1.0"]
WAS_API_VERSIONS = ["4.0", "3.0", "2.0"]
POLICY_COMPLIANCE_API_VERSIONS = ["4.0", "3.0", "2.0"]
CLOUDVIEW_API_VERSIONS = ["v2", "v1"]


def get_api_versions(api_type: str) -> list:
    """
    Get supported API versions for a given Qualys API type, ordered newest to oldest.

    :param str api_type: API type (container_security, was, policy_compliance, cloudview)
    :return: List of version strings to try, newest first
    :rtype: list
    """
    version_map = {
        "container_security": CONTAINER_SECURITY_API_VERSIONS,
        "was": WAS_API_VERSIONS,
        "policy_compliance": POLICY_COMPLIANCE_API_VERSIONS,
        "cloudview": CLOUDVIEW_API_VERSIONS,
    }

    versions = version_map.get(api_type, [])
    if not versions:
        logger.warning("Unknown API type: %s, no version fallback available", api_type)
    return versions
