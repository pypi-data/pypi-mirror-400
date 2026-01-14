"""
Shared constants for FedRAMP integration.

This module consolidates all status, origination, and pattern constants
that were previously duplicated across fedramp_five.py, fedramp_cis_crm.py,
appendix_parser.py, and markdown_appendix_parser.py.

Following SOLID principles - this is the Single Source of Truth for all
FedRAMP-related constants.
"""

from enum import Enum
from typing import Dict, List


class ImplementationStatus(str, Enum):
    """
    Control implementation statuses used in FedRAMP documents.

    These map to RegScale's ControlImplementationStatus values.
    Using str inheritance allows direct string comparison and serialization.
    """

    IMPLEMENTED = "Implemented"
    PARTIALLY_IMPLEMENTED = "Partially Implemented"
    PLANNED = "Planned"
    IN_REMEDIATION = "In Remediation"
    INHERITED = "Inherited"
    ALTERNATIVE = "Alternative Implementation"
    NOT_APPLICABLE = "Not Applicable"
    ARCHIVED = "Archived"
    RISK_ACCEPTED = "Risk Accepted"
    NOT_IMPLEMENTED = "Not Implemented"


class ControlOrigination(str, Enum):
    """
    Control origination types used in FedRAMP documents.

    These indicate who is responsible for implementing a control.
    """

    SERVICE_PROVIDER_CORPORATE = "Service Provider Corporate"
    SERVICE_PROVIDER_SYSTEM_SPECIFIC = "Service Provider System Specific"
    SERVICE_PROVIDER_HYBRID = "Service Provider Hybrid (Corporate and System Specific)"
    CONFIGURED_BY_CUSTOMER = "Configured by Customer (Customer System Specific)"
    PROVIDED_BY_CUSTOMER = "Provided by Customer (Customer System Specific)"
    SHARED = "Shared (Service Provider and Customer Responsibility)"
    INHERITED_FEDRAMP = "Inherited from pre-existing FedRAMP Authorization"


# Default values - reference enum values to avoid duplicated literals
DEFAULT_STATUS = ImplementationStatus.NOT_IMPLEMENTED.value
DEFAULT_ORIGINATION = ControlOrigination.SERVICE_PROVIDER_CORPORATE.value

# Visual checkbox characters commonly found in FedRAMP DOCX documents
CHECKBOX_CHARS: List[str] = [
    "☒",
    "☑",
    "☑️",
    "✓",
    "✔",
    "✔️",
    "✅",
    "⬜",
    "▣",
    "■",
    "□",
    "⊠",
    "⊗",
    "×",
    "🗹",
    "✗",
    "✘",
    "⌧",
    "🗸",
    "⬛",
    "▪",
    "◼",
    "◾",
]

# All positive keywords indicating a checkbox is selected
# Includes visual characters, text values, and accessibility variants
POSITIVE_KEYWORDS: List[str] = [
    # Boolean/simple values
    "yes",
    "true",
    "1",
    "True",
    "Yes",
    # Unicode checkboxes
    "☒",
    "☑",
    "☑️",
    "✓",
    "✔",
    "✔️",
    "✅",
    "⬜",
    "▣",
    "■",
    "□",
    "⊠",
    "⊗",
    "×",
    # Additional Unicode variants
    "🗹",
    "✗",
    "✘",
    "⌧",
    "🗸",
    "⬛",
    "▪",
    "◼",
    "◾",
    # Text variants
    "x",
    "X",
    "[x]",
    "[X]",
    "(x)",
    "(X)",
    "checked",
    "selected",
    "chosen",
    # Accessibility variants
    "marked",
    "enabled",
    "active",
    "on",
]

# Keywords that map to each implementation status
# Used for fuzzy matching in document parsing
# Reference enum values to avoid duplicated literals
STATUS_KEYWORDS: Dict[str, List[str]] = {
    ImplementationStatus.IMPLEMENTED.value: ["implemented", "complete", "done", "yes", "☒", "1"],
    ImplementationStatus.PARTIALLY_IMPLEMENTED.value: [
        "partially implemented",
        "incomplete",
        "partially done",
        "partial",
        "in process",
        "In process",
        "☒",
        "1",
    ],
    ImplementationStatus.PLANNED.value: ["planned", "scheduled", "Planned", "☒", "1"],
    ImplementationStatus.ALTERNATIVE.value: [
        "alternative implementation",
        "alternative",
        "Equivalent",
        "☒",
        "1",
    ],
    ImplementationStatus.NOT_APPLICABLE.value: [
        "not applicable",
        "irrelevant",
        "not relevant",
        "no",
        "☒",
        "1",
        "n/a",
        "N/A",
    ],
    ImplementationStatus.IN_REMEDIATION.value: ["in remediation", "remediation", "remediating"],
    ImplementationStatus.INHERITED.value: ["inherited", "inherits"],
    ImplementationStatus.ARCHIVED.value: ["archived"],
    ImplementationStatus.RISK_ACCEPTED.value: ["risk accepted", "accepted risk"],
    ImplementationStatus.NOT_IMPLEMENTED.value: ["not implemented", "unimplemented", "missing"],
}

# SSP Section identifiers - standardized keys for document sections
SSP_SECTIONS: Dict[str, str] = {
    "SYSTEM_DESCRIPTION": "System Description",
    "AUTHORIZATION_BOUNDARY": "Authorization Boundary",
    "NETWORK_ARCHITECTURE": "System and Network Architecture",
    "DATA_FLOW": "Data Flows",
    "ENVIRONMENT": "System Environment and Inventory",
    "LAWS_AND_REGULATIONS": "Applicable Laws, Regulations, Standards, and Guidance",
    "CATEGORIZATION_JUSTIFICATION": "Security Categorization",
    "SYSTEM_FUNCTION": "System Function or Purpose",
}

# Mapping from ImplementationStatus enum to RegScale status strings
STATUS_TO_REGSCALE_MAP: Dict[ImplementationStatus, str] = {
    ImplementationStatus.IMPLEMENTED: "Implemented",
    ImplementationStatus.PARTIALLY_IMPLEMENTED: "Partially Implemented",
    ImplementationStatus.PLANNED: "Planned",
    ImplementationStatus.IN_REMEDIATION: "In Remediation",
    ImplementationStatus.INHERITED: "Inherited",
    ImplementationStatus.ALTERNATIVE: "Alternative",
    ImplementationStatus.NOT_APPLICABLE: "N/A",
    ImplementationStatus.ARCHIVED: "Archived",
    ImplementationStatus.RISK_ACCEPTED: "Risk Accepted",
    ImplementationStatus.NOT_IMPLEMENTED: "Not Implemented",
}

# Mapping from ControlOrigination enum to simplified RegScale responsibility strings
ORIGINATION_TO_REGSCALE_MAP: Dict[ControlOrigination, str] = {
    ControlOrigination.SERVICE_PROVIDER_CORPORATE: "Provider",
    ControlOrigination.SERVICE_PROVIDER_SYSTEM_SPECIFIC: "Provider (System Specific)",
    ControlOrigination.SERVICE_PROVIDER_HYBRID: "Hybrid",
    ControlOrigination.PROVIDED_BY_CUSTOMER: "Customer",
    ControlOrigination.CONFIGURED_BY_CUSTOMER: "Customer Configured",
    ControlOrigination.SHARED: "Shared",
    ControlOrigination.INHERITED_FEDRAMP: "Inherited",
}

# Lowercase versions for case-insensitive matching
LOWER_STATUSES: List[str] = [s.value.lower() for s in ImplementationStatus]
LOWER_ORIGINATIONS: List[str] = [o.value.lower() for o in ControlOrigination]

# Key identifiers used in Appendix A parsing
CONTROL_ORIGIN_KEY = "Control Origination"
CONTROL_SUMMARY_KEY = "Control Summary Information"
STATEMENT_CHECK = "what is the solution and how is it implemented"
