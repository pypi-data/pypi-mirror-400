#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter ID utility functions for FedRAMP integrations.

This module provides functions to convert between legacy Rev4 parameter formats
and modern OSCAL parameter ID formats to ensure consistency across imports.
"""

import re
from typing import Optional


def convert_legacy_to_oscal_param_id(control_id: str, param_number: int) -> str:
    """
    Convert legacy Rev4 parameter format to OSCAL format.

    Examples:
        >>> convert_legacy_to_oscal_param_id("ac-1", 1)
        'ac-01_odp.01'
        >>> convert_legacy_to_oscal_param_id("ac-2", 3)
        'ac-02_odp.03'
        >>> convert_legacy_to_oscal_param_id("AC-2(1)", 1)
        'ac-02.1_odp.01'
        >>> convert_legacy_to_oscal_param_id("si-12", 10)
        'si-12_odp.10'

    :param str control_id: Control ID (e.g., "ac-1", "AC-2", "ac-2(1)")
    :param int param_number: Parameter number (1-indexed)
    :return: OSCAL-formatted parameter ID
    :rtype: str
    """
    # Normalize control ID to lowercase
    normalized = control_id.lower().strip()

    # Remove spaces
    normalized = normalized.replace(" ", "")

    # Handle parentheses - convert AC-2(1) to ac-02.1
    normalized = normalized.replace("(", ".").replace(")", "")

    # Split on dash to get family and number
    match = re.match(r"([a-z]+)-(\d+)(\..*)?", normalized)
    if match:
        family = match.group(1)
        number = match.group(2).zfill(2)  # Pad to 2 digits
        enhancement = match.group(3) or ""
        control_base = f"{family}-{number}{enhancement}"
    else:
        # Fallback if pattern doesn't match
        control_base = normalized

    # Format parameter with OSCAL convention
    param_str = str(param_number).zfill(2)
    param_id = f"{control_base}_odp.{param_str}"

    return param_id


def parse_oscal_param_id(param_id: str) -> Optional[dict]:
    """
    Parse an OSCAL parameter ID into its components.

    Examples:
        >>> parse_oscal_param_id("ac-01_odp.01")
        {'control_id': 'ac-01', 'param_number': 1, 'format': 'oscal'}
        >>> parse_oscal_param_id("ac-1_prm_3")
        {'control_id': 'ac-1', 'param_number': 3, 'format': 'legacy'}

    :param str param_id: Parameter ID to parse
    :return: Dictionary with control_id, param_number, and format, or None if invalid
    :rtype: Optional[dict]
    """
    if not param_id:
        return None

    param_id = param_id.strip().lower()

    # Try OSCAL format first: ac-01_odp.01
    oscal_match = re.match(r"([a-z]+-\d+(?:\.\d+)?)_odp\.(\d+)", param_id)
    if oscal_match:
        return {
            "control_id": oscal_match.group(1),
            "param_number": int(oscal_match.group(2)),
            "format": "oscal",
        }

    # Try legacy format: ac-1_prm_1
    legacy_match = re.match(r"([a-z]+-\d+(?:\.\d+)?)_prm_(\d+)", param_id)
    if legacy_match:
        return {
            "control_id": legacy_match.group(1),
            "param_number": int(legacy_match.group(2)),
            "format": "legacy",
        }

    return None


def normalize_parameter_id(param_id: str) -> str:
    """
    Normalize a parameter ID to OSCAL format, converting legacy format if needed.

    Examples:
        >>> normalize_parameter_id("ac-1_prm_1")
        'ac-01_odp.01'
        >>> normalize_parameter_id("ac-01_odp.01")
        'ac-01_odp.01'

    :param str param_id: Parameter ID in any recognized format
    :return: OSCAL-formatted parameter ID
    :rtype: str
    """
    parsed = parse_oscal_param_id(param_id)
    if not parsed:
        return param_id  # Return as-is if unparseable

    if parsed["format"] == "oscal":
        return param_id  # Already in OSCAL format

    # Convert legacy to OSCAL
    return convert_legacy_to_oscal_param_id(parsed["control_id"], parsed["param_number"])


def format_parameter_name(fedramp_control: str, param_number: int) -> str:
    """
    Format parameter name using OSCAL convention.

    This replaces the legacy format_parameter_name function to use OSCAL format
    instead of the old _prm_ format. This ensures consistency with NIST 800-53 Rev5
    and FedRAMP Rev5 OSCAL documents.

    Examples:
        >>> format_parameter_name("ac-1", 1)
        'ac-01_odp.01'
        >>> format_parameter_name("AC-2", 3)
        'ac-02_odp.03'
        >>> format_parameter_name("ac-2(1)", 1)
        'ac-02.1_odp.01'

    :param str fedramp_control: Root control name from catalog (e.g., "ac-1", "AC-2(1)")
    :param int param_number: Number of parameter (1-indexed)
    :return: Formatted parameter name in OSCAL format
    :rtype: str
    """
    return convert_legacy_to_oscal_param_id(fedramp_control, param_number)
