"""
Unified responsibility/origination mapping for FedRAMP integration.

This module consolidates the responsibility and origination mapping logic that was
previously duplicated across fedramp_five.py, fedramp_cis_crm.py, and appendix_parser.py.

Following SOLID principles:
- Single Responsibility: Only handles responsibility/origination mapping
- Open/Closed: Mapping can be extended via constants without modifying class
"""

import re
from typing import Dict, List, Optional, Tuple

from regscale.integrations.public.fedramp.constants import (
    CHECKBOX_CHARS,
    ControlOrigination,
    LOWER_ORIGINATIONS,
)


class ResponsibilityMapper:
    """
    Maps responsibility/origination between FedRAMP document formats and RegScale.

    Consolidates responsibility mapping from multiple sources into a single utility class.
    All methods are classmethods to allow stateless usage.
    """

    # Mapping from FedRAMP origination strings to RegScale values
    # The FedRAMP document uses slightly different wording than RegScale in some cases
    _ORIGINATION_NORMALIZATION: Dict[str, str] = {
        "service provider corporate": "Service Provider Corporate",
        "service provider system specific": "Service Provider System Specific",
        "service provider hybrid (corporate and system specific)": "Service Provider Hybrid (Corporate and System Specific)",
        "configured by customer (customer system specific)": "Configured by Customer (Customer System Specific)",
        # FedRAMP uses "Customer System Specific" but RegScale uses "Customer Specific"
        "provided by customer (customer system specific)": "Provided by Customer (Customer Specific)",
        "shared (service provider and customer responsibility)": "Shared (Service Provider and Customer Responsibility)",
        "inherited from pre-existing fedramp authorization": "Inherited from pre-existing FedRAMP Authorization",
    }

    # Precompile patterns for customer responsibility extraction from part content
    _CUSTOMER_RESPONSIBILITY_PATTERNS = [
        # Pattern with HTML tags
        re.compile(
            r"(?:<[^>]*>)*\s*"
            r"(?:Federal\s+)?Customer(?:\s+(?:Agency|Organization))?\s+Responsibilit(?:y|ies)"
            r"(?:<[^>]*>)*\s*:?\s*"
            r"(.*?)(?=(?:<[^>]*>)*\s*(?:Service\s+Provider|CSP|Cloud|Test\s+Case|Provider)\s+Responsibilit|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Simple pattern without HTML
        re.compile(
            r"(?:Federal\s+)?Customer(?:\s+(?:Agency|Organization))?\s+Responsibilit(?:y|ies)\s*:?\s*"
            r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Test\s+Case|Provider)\s+Responsibilit|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Agency-specific patterns
        re.compile(
            r"Agency\s+Responsibilit(?:y|ies)\s*:?\s*"
            r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+Responsibilit|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Tenant responsibility pattern
        re.compile(
            r"Tenant\s+(?:Responsibilit(?:y|ies)|Implementation)\s*:?\s*"
            r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Customer Implementation Statement pattern
        re.compile(
            r"(?:Federal\s+)?Customer\s+Implementation(?:\s+Statement)?\s*:?\s*"
            r"(.*?)(?=(?:Service\s+Provider|CSP|Cloud|Provider)\s+|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
    ]

    _CLOUD_RESPONSIBILITY_PATTERNS = [
        # Pattern with HTML tags
        re.compile(
            r"(?:<[^>]*>)*\s*"
            r"(?:Service\s+Provider|CSP|Cloud(?:\s+Service\s+Provider)?|Test\s+Case)\s+Responsibilit(?:y|ies)"
            r"(?:<[^>]*>)*\s*:?\s*"
            r"(.*?)(?=(?:<[^>]*>)*\s*(?:Federal\s+)?(?:Customer|Agency|Tenant)"
            r"(?:\s+(?:Agency|Organization))?\s+Responsibilit|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Simple pattern without HTML
        re.compile(
            r"(?:Service\s+Provider|CSP|Cloud(?:\s+Service\s+Provider)?|Test\s+Case)\s+Responsibilit(?:y|ies)\s*:?\s*"
            r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)"
            r"(?:\s+(?:Agency|Organization))?\s+Responsibilit|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Provider Implementation Statement pattern
        re.compile(
            r"(?:Service\s+)?Provider\s+Implementation(?:\s+Statement)?\s*:?\s*"
            r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)\s+|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Cloud Provider Responsibility pattern
        re.compile(
            r"Cloud\s+Provider\s+Responsibilit(?:y|ies)\s*:?\s*"
            r"(.*?)(?=(?:Federal\s+)?(?:Customer|Agency|Tenant)\s+|Part\s+[a-z]:|$)",
            re.IGNORECASE | re.DOTALL,
        ),
    ]

    @classmethod
    def to_regscale(cls, origination: Optional[str]) -> str:
        """
        Map a FedRAMP origination string to its RegScale equivalent.

        :param Optional[str] origination: The origination string from FedRAMP document
        :return: The normalized RegScale origination string
        :rtype: str
        """
        if not origination:
            return ""

        # Handle comma-separated values
        if "," in origination:
            origination_values = [o.strip() for o in origination.split(",")]
            return ",".join([cls.to_regscale(o) for o in origination_values])

        normalized = origination.strip().lower()

        # Check normalization map
        if normalized in cls._ORIGINATION_NORMALIZATION:
            return cls._ORIGINATION_NORMALIZATION[normalized]

        # Check if it's a ControlOrigination enum value
        for orig in ControlOrigination:
            if normalized == orig.value.lower():
                return cls._ORIGINATION_NORMALIZATION.get(normalized, orig.value)

        # Return original with cleaned whitespace if no mapping found
        return origination.strip()

    @classmethod
    def from_checkbox_text(cls, text: str) -> Optional[str]:
        """
        Extract and normalize origination from checkbox-prefixed text.

        Handles text like "☒ Service Provider Corporate" and extracts
        the origination portion.

        :param str text: Text potentially containing checkbox and origination
        :return: Normalized origination string or None if not recognized
        :rtype: Optional[str]
        """
        if not text:
            return None

        # Remove checkbox characters and clean whitespace
        cleaned = text.strip()
        for char in CHECKBOX_CHARS:
            cleaned = cleaned.replace(char, "")
        cleaned = cleaned.strip()

        if not cleaned:
            return None

        # Try to match against known originations
        cleaned_lower = cleaned.lower()

        # Direct match in normalization map
        if cleaned_lower in cls._ORIGINATION_NORMALIZATION:
            return cls._ORIGINATION_NORMALIZATION[cleaned_lower]

        # Check against ControlOrigination enum values
        for orig in ControlOrigination:
            if cleaned_lower == orig.value.lower():
                return orig.value

        # Check partial match against known originations
        for orig in ControlOrigination:
            if orig.value.lower() in cleaned_lower or cleaned_lower in orig.value.lower():
                return orig.value

        return None

    @classmethod
    def get_selected_originations(cls, text: str) -> List[str]:
        """
        Get list of selected/checked originations from checkbox text.

        Parses text containing multiple checkbox lines and returns
        the originations that are checked/selected.

        :param str text: Multi-line text with checkbox originations
        :return: List of selected origination strings
        :rtype: List[str]
        """
        if not text:
            return []

        selected = []
        lines = text.split("\n")

        # Characters that indicate a checked/selected checkbox
        checked_chars = {"☒", "☑", "✓", "✔", "✅", "x", "X"}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a checked checkbox
            first_char = line[0] if line else ""
            if first_char in checked_chars:
                origination = cls.from_checkbox_text(line)
                if origination and origination not in selected:
                    selected.append(origination)

        return selected

    @classmethod
    def extract_from_part(cls, part_content: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract customer and cloud responsibility statements from part content.

        FedRAMP v5 SSP documents often have responsibility sections within each part,
        such as "Federal Customer Responsibility" and "Service Provider Responsibility".

        :param Optional[str] part_content: The content of a control implementation part
        :return: A tuple of (customer_responsibility, cloud_responsibility) text
        :rtype: Tuple[Optional[str], Optional[str]]
        """
        customer_responsibility = None
        cloud_responsibility = None

        if not part_content:
            return customer_responsibility, cloud_responsibility

        # Extract customer responsibility
        for pattern in cls._CUSTOMER_RESPONSIBILITY_PATTERNS:
            match = pattern.search(part_content)
            if match:
                extracted = match.group(1).strip()
                # Clean up HTML tags for plain text
                cleaned = re.sub(r"<[^>]+>", " ", extracted)
                cleaned = re.sub(r"\s+", " ", cleaned).strip()
                if cleaned and len(cleaned) > 10:  # Must have meaningful content
                    customer_responsibility = cleaned
                    break

        # Extract cloud/service provider responsibility
        for pattern in cls._CLOUD_RESPONSIBILITY_PATTERNS:
            match = pattern.search(part_content)
            if match:
                extracted = match.group(1).strip()
                # Clean up HTML tags for plain text
                cleaned = re.sub(r"<[^>]+>", " ", extracted)
                cleaned = re.sub(r"\s+", " ", cleaned).strip()
                if cleaned and len(cleaned) > 10:  # Must have meaningful content
                    cloud_responsibility = cleaned
                    break

        return customer_responsibility, cloud_responsibility

    @classmethod
    def normalize_origination(cls, origination: Optional[str]) -> str:
        """
        Normalize an origination string to its canonical form.

        Handles case variations and whitespace.

        :param Optional[str] origination: Origination string to normalize
        :return: Normalized origination string
        :rtype: str
        """
        if not origination:
            return ""

        cleaned = origination.strip()
        lower = cleaned.lower()

        # Check normalization map
        if lower in cls._ORIGINATION_NORMALIZATION:
            return cls._ORIGINATION_NORMALIZATION[lower]

        # Check against ControlOrigination enum values
        for orig in ControlOrigination:
            if lower == orig.value.lower():
                return orig.value

        # Check against LOWER_ORIGINATIONS for partial matching
        for i, lower_orig in enumerate(LOWER_ORIGINATIONS):
            if lower == lower_orig:
                return list(ControlOrigination)[i].value

        # Return original with cleaned whitespace
        return cleaned
