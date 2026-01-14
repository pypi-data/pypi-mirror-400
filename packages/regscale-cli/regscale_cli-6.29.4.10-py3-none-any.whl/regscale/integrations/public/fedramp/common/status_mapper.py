"""
Unified status mapping for FedRAMP integration.

This module consolidates the status mapping logic that was previously
duplicated across fedramp_five.py, fedramp_cis_crm.py, and appendix_parser.py.

Following SOLID principles:
- Single Responsibility: Only handles status mapping
- Open/Closed: Mapping can be extended via constants without modifying class
"""

from collections import Counter
from typing import Dict, List, Optional

from regscale.integrations.public.fedramp.constants import (
    CHECKBOX_CHARS,
    ImplementationStatus,
    LOWER_STATUSES,
    STATUS_KEYWORDS,
    STATUS_TO_REGSCALE_MAP,
)

# Constant for aggregated fully implemented status (not in ImplementationStatus enum)
FULLY_IMPLEMENTED = "Fully Implemented"


class StatusMapper:
    """
    Maps implementation statuses between FedRAMP document formats and RegScale.

    Consolidates status mapping from multiple sources into a single utility class.
    All methods are classmethods to allow stateless usage.
    """

    # Mapping from various FedRAMP status strings to normalized RegScale values
    # Use enum values to avoid duplicated literals
    _STATUS_NORMALIZATION: Dict[str, str] = {
        # Standard statuses (exact match)
        "implemented": ImplementationStatus.IMPLEMENTED.value,
        "partially implemented": ImplementationStatus.PARTIALLY_IMPLEMENTED.value,
        "planned": ImplementationStatus.PLANNED.value,
        "not applicable": "N/A",
        "n/a": "N/A",
        "alternative implementation": "Alternative",
        "alternative": "Alternative",
        "not implemented": ImplementationStatus.NOT_IMPLEMENTED.value,
        "inherited": ImplementationStatus.INHERITED.value,
        "in remediation": ImplementationStatus.IN_REMEDIATION.value,
        "archived": ImplementationStatus.ARCHIVED.value,
        "risk accepted": ImplementationStatus.RISK_ACCEPTED.value,
        # RegScale enum value mappings
        "fully implemented": ImplementationStatus.IMPLEMENTED.value,
    }

    @classmethod
    def to_regscale(cls, status: str) -> str:
        """
        Map a FedRAMP status string to its RegScale equivalent.

        :param str status: The status string from FedRAMP document
        :return: The normalized RegScale status string
        :rtype: str
        """
        if not status:
            return ImplementationStatus.NOT_IMPLEMENTED.value

        normalized = status.strip().lower()

        # Check normalization map
        if normalized in cls._STATUS_NORMALIZATION:
            return cls._STATUS_NORMALIZATION[normalized]

        # Check if it's an ImplementationStatus enum value
        for impl_status in ImplementationStatus:
            if normalized == impl_status.value.lower():
                return STATUS_TO_REGSCALE_MAP.get(impl_status, impl_status.value)

        # Return original if no mapping found
        return status

    @classmethod
    def from_checkbox_text(cls, text: str) -> Optional[str]:
        """
        Extract and normalize status from checkbox-prefixed text.

        Handles text like "☒ Implemented" or "✓ Planned" and extracts
        the status portion.

        :param str text: Text potentially containing checkbox and status
        :return: Normalized status string or None if not recognized
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

        # Try to match against known statuses
        cleaned_lower = cleaned.lower()

        # Direct match in normalization map
        if cleaned_lower in cls._STATUS_NORMALIZATION:
            return cls._STATUS_NORMALIZATION[cleaned_lower]

        # Check against STATUS_KEYWORDS
        for status, keywords in STATUS_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() == cleaned_lower:
                    return status

        # Check against ImplementationStatus enum values
        for impl_status in ImplementationStatus:
            if cleaned_lower == impl_status.value.lower():
                return impl_status.value

        return None

    @classmethod
    def aggregate_statuses(cls, statuses: List[str]) -> str:
        """
        Aggregate multiple part statuses into a single control status.

        This is used when a control has multiple parts (Part a, Part b, etc.)
        and we need to determine the overall control status.

        Logic:
        - If all statuses are the same, return that status
        - If all are "Implemented", return "Fully Implemented"
        - If any are "Partially Implemented", return "Partially Implemented"
        - If mix of statuses, return "Partially Implemented"
        - If empty, return "Not Implemented"

        :param List[str] statuses: List of status strings to aggregate
        :return: The aggregated status
        :rtype: str
        """
        if not statuses:
            return ImplementationStatus.NOT_IMPLEMENTED.value

        # Normalize all statuses first
        normalized = [cls.normalize_status(s) for s in statuses]

        # Count occurrences
        counter = Counter(normalized)

        # Single unique status
        if len(counter) == 1:
            single_status = normalized[0]
            # "Implemented" becomes "Fully Implemented" when aggregated
            if single_status == ImplementationStatus.IMPLEMENTED.value:
                return FULLY_IMPLEMENTED
            return single_status

        # Check for "Partially Implemented" explicitly
        if ImplementationStatus.PARTIALLY_IMPLEMENTED.value in counter:
            return ImplementationStatus.PARTIALLY_IMPLEMENTED.value

        # Mixed statuses = Partially Implemented
        return ImplementationStatus.PARTIALLY_IMPLEMENTED.value

    @classmethod
    def normalize_status(cls, status: str) -> str:
        """
        Normalize a status string to its canonical form.

        Handles case variations and whitespace.

        :param str status: Status string to normalize
        :return: Normalized status string
        :rtype: str
        """
        if not status:
            return ImplementationStatus.NOT_IMPLEMENTED.value

        cleaned = status.strip()
        lower = cleaned.lower()

        # Check normalization map
        if lower in cls._STATUS_NORMALIZATION:
            return cls._STATUS_NORMALIZATION[lower]

        # Check against ImplementationStatus enum values
        for impl_status in ImplementationStatus:
            if lower == impl_status.value.lower():
                return impl_status.value

        # Return original with cleaned whitespace
        return cleaned
