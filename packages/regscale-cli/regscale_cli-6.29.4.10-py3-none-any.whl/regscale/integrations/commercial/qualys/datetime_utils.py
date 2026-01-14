"""
Centralized datetime parsing utilities for Qualys integration.

This module provides a single source of truth for parsing datetime values from various Qualys APIs
(VMDR, Total Cloud, WAS, Container Security) into ISO 8601 format expected by RegScale.
"""

import logging
from datetime import datetime
from typing import Optional

from dateutil.parser import ParserError, parse as dateutil_parse

logger = logging.getLogger("regscale")

# Standard datetime formats used across Qualys APIs
QUALYS_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # Target format for RegScale


def parse_qualys_datetime(datetime_str: str, fallback: str = "") -> str:
    """
    Parse any Qualys datetime format to ISO 8601 format expected by RegScale.

    Uses dateutil.parser for flexible datetime parsing that handles most formats automatically.
    This is more robust than manual format matching and handles edge cases better.

    Args:
        datetime_str: Datetime string from Qualys API (any common format)
        fallback: Return value on parse error (default: empty string)

    Returns:
        ISO 8601 formatted datetime string (YYYY-MM-DDTHH:MM:SSZ)

    Examples:
        >>> parse_qualys_datetime("12/14/2025 10:09")
        "2025-12-14T10:09:00Z"

        >>> parse_qualys_datetime("2025-12-14T10:09:00")
        "2025-12-14T10:09:00Z"

        >>> parse_qualys_datetime("2025-12-14T10:09:00Z")
        "2025-12-14T10:09:00Z"

        >>> parse_qualys_datetime("invalid", fallback="N/A")
        "N/A"
    """
    if not datetime_str:
        return fallback

    try:
        # Use dateutil.parser for flexible datetime parsing
        # This handles most datetime formats automatically without explicit format strings
        dt = dateutil_parse(datetime_str)
        # Always return with Z suffix for consistency
        return dt.strftime(QUALYS_DATETIME_FORMAT)
    except ParserError as e:
        # Log warning and return fallback on parse failure
        logger.warning("Failed to parse datetime '%s': %s. Using fallback: %s", datetime_str, e, fallback)
        return fallback or datetime_str


def normalize_qualys_datetime(datetime_str: str) -> str:
    """
    DEPRECATED: Use parse_qualys_datetime() directly instead.

    This wrapper exists only for backwards compatibility with existing code
    in total_cloud_helpers.py and was_helpers.py.
    Future refactoring should replace calls to this function with parse_qualys_datetime().

    Args:
        datetime_str: Datetime string from Qualys API (e.g., "12/14/2025 10:09")

    Returns:
        ISO format datetime string (e.g., "2025-12-14T10:09:00Z")
    """
    return parse_qualys_datetime(datetime_str, fallback="")


def convert_container_timestamp(timestamp) -> str:
    """
    DEPRECATED: Use parse_qualys_datetime() directly for string timestamps.

    This wrapper exists only for backwards compatibility with existing code in __init__.py.
    It handles Unix timestamps (int/float) and string timestamps.
    Future refactoring should replace calls to this function with parse_qualys_datetime() for strings
    and direct datetime conversion for Unix timestamps.

    Handles various timestamp formats from Container Security API:
    - ISO 8601 with Z: "2025-12-14T10:09:00Z"
    - ISO 8601 without Z: "2025-12-14T10:09:00"
    - Unix timestamp (int/float): 1702553340
    - MM/DD/YYYY format: "12/14/2025 10:09"

    Args:
        timestamp: Timestamp from Container Security API (str, int, or float)

    Returns:
        ISO 8601 formatted datetime string, or empty string on error

    Example:
        >>> convert_container_timestamp("2025-12-14T10:09:00")
        "2025-12-14T10:09:00Z"

        >>> convert_container_timestamp(1702553340)
        "2023-12-14T10:09:00Z"
    """
    if not timestamp:
        return ""

    # Handle Unix timestamp (int or float)
    if isinstance(timestamp, (int, float)):
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime(QUALYS_DATETIME_FORMAT)
        except (ValueError, OSError) as e:
            logger.warning("Failed to convert Unix timestamp %s: %s", timestamp, e)
            return ""

    # Handle string timestamps
    if isinstance(timestamp, str):
        return parse_qualys_datetime(timestamp, fallback="")

    logger.warning("Unexpected timestamp type: %s (value: %s)", type(timestamp), timestamp)
    return ""
