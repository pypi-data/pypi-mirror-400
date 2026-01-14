#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium Compliance Finding Model.

Transforms Tanium Comply finding data to RegScale Issue format.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("regscale")


@dataclass
class TaniumComplianceFinding:
    """
    Represents a Tanium compliance finding from the Comply module.

    Maps Tanium compliance data to RegScale Issue model fields.
    """

    tanium_id: str
    rule_id: str
    rule_title: Optional[str] = None
    rule_description: Optional[str] = None
    benchmark: Optional[str] = None
    benchmark_version: Optional[str] = None
    status: str = "Unknown"
    severity: Optional[str] = None
    category: Optional[str] = None
    check_type: Optional[str] = None
    check_command: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    fix_text: Optional[str] = None
    endpoint_id: Optional[int] = None
    endpoint_name: Optional[str] = None
    assessment_date: Optional[str] = None
    ccis: List[str] = field(default_factory=list)
    nist_controls: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_tanium_data(cls, data: Dict[str, Any]) -> "TaniumComplianceFinding":
        """
        Create TaniumComplianceFinding from Tanium API response data.

        Args:
            data: Raw compliance finding data from Tanium Comply API

        Returns:
            TaniumComplianceFinding instance
        """
        return cls(
            tanium_id=str(data.get("id", "")),
            rule_id=data.get("ruleId", ""),
            rule_title=data.get("ruleTitle"),
            rule_description=data.get("ruleDescription"),
            benchmark=data.get("benchmark"),
            benchmark_version=data.get("benchmarkVersion"),
            status=data.get("status", "Unknown"),
            severity=data.get("severity"),
            category=data.get("category"),
            check_type=data.get("checkType"),
            check_command=data.get("checkCommand"),
            expected_value=data.get("expectedValue"),
            actual_value=data.get("actualValue"),
            fix_text=data.get("fixText"),
            endpoint_id=data.get("endpointId"),
            endpoint_name=data.get("endpointName"),
            assessment_date=data.get("assessmentDate"),
            ccis=data.get("ccis", []),
            nist_controls=data.get("nistControls", []),
            raw_data=data,
        )

    def is_compliant(self) -> bool:
        """
        Check if the finding indicates compliance.

        Returns:
            True if compliant (Pass), False otherwise
        """
        status_upper = self.status.upper() if self.status else ""
        return status_upper in ["PASS", "PASSED", "COMPLIANT", "NOT_APPLICABLE", "NA"]

    def get_regscale_status(self) -> str:
        """
        Map Tanium status to RegScale IssueStatus.

        Returns:
            RegScale issue status string (Open, Closed)
        """
        if self.is_compliant():
            return "Closed"
        return "Open"

    def get_regscale_severity(self) -> str:
        """
        Map Tanium severity/category to RegScale severity.

        Uses DISA STIG category mapping if available.

        Returns:
            RegScale severity string (Critical, High, Medium, Low)
        """
        # Try DISA STIG category mapping first
        category_severity = self._map_category_to_severity()
        if category_severity:
            return category_severity

        # Fall back to explicit severity mapping
        return self._map_severity_to_regscale()

    def _map_category_to_severity(self) -> Optional[str]:
        """Map DISA STIG category to severity (check more specific patterns first)."""
        if not self.category:
            return None
        category_upper = self.category.upper()
        # Order matters: check CAT III before CAT II before CAT I
        category_mappings = [("CAT III", "Medium"), ("CAT II", "High"), ("CAT I", "Critical")]
        for pattern, severity in category_mappings:
            if pattern in category_upper:
                return severity
        return None

    def _map_severity_to_regscale(self) -> str:
        """Map explicit severity value to RegScale severity."""
        if not self.severity:
            return "Medium"  # Default for unknown severity
        severity_map = {"CRITICAL": "Critical", "HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}
        return severity_map.get(self.severity.upper(), "Medium")

    def get_nist_controls(self) -> List[str]:
        """
        Get NIST control IDs associated with this finding.

        Returns:
            List of NIST control IDs
        """
        return self.nist_controls.copy()

    def get_cci_ids(self) -> List[str]:
        """
        Get CCI IDs associated with this finding.

        Returns:
            List of CCI IDs
        """
        return self.ccis.copy()

    def get_unique_identifier(self) -> str:
        """
        Generate unique identifier for this finding.

        Returns:
            Unique identifier string
        """
        endpoint_part = str(self.endpoint_id) if self.endpoint_id else "unknown"
        return "tanium-compliance-%s-%s" % (self.rule_id, endpoint_part)

    def to_regscale_issue(self, parent_id: int, parent_module: str) -> Dict[str, Any]:
        """
        Convert to RegScale Issue dictionary format.

        Args:
            parent_id: RegScale parent record ID
            parent_module: RegScale parent module name

        Returns:
            Dictionary suitable for creating RegScale Issue
        """
        issue_dict = {
            "parentId": parent_id,
            "parentModule": parent_module,
            "title": self._build_title(),
            "description": self._build_description(),
            "severity": self.get_regscale_severity(),
            "status": self.get_regscale_status(),
            "issueOwnerId": "",  # Will be set by caller or default
            "dateCreated": self.assessment_date,
            "otherTrackingNumber": self.get_unique_identifier(),
        }

        # Add remediation info if available
        if self.fix_text:
            issue_dict["recommendation"] = self.fix_text

        return issue_dict

    def _build_title(self) -> str:
        """Build issue title."""
        title_parts = []

        if self.rule_id:
            title_parts.append("[%s]" % self.rule_id)

        if self.rule_title:
            title_parts.append(self.rule_title)
        elif self.rule_description:
            # Truncate description for title if no title available
            desc = self.rule_description[:100]
            if len(self.rule_description) > 100:
                desc = desc + "..."
            title_parts.append(desc)

        if self.endpoint_name:
            title_parts.append("- %s" % self.endpoint_name)

        return " ".join(title_parts) if title_parts else "Compliance Finding"

    def _build_description(self) -> str:
        """Build issue description with Tanium compliance details."""
        parts = ["<h3>Tanium Compliance Finding</h3>"]
        parts.extend(self._build_basic_info_section())
        parts.extend(self._build_rule_description_section())
        parts.extend(self._build_check_details_section())
        parts.extend(self._build_fix_text_section())
        parts.extend(self._build_control_mappings_section())
        parts.extend(self._build_endpoint_section())
        return "\n".join(parts)

    def _build_basic_info_section(self) -> List[str]:
        """Build the basic info section of the description."""
        parts = ["<p>"]
        if self.benchmark:
            benchmark_info = (
                "%s %s" % (self.benchmark, self.benchmark_version) if self.benchmark_version else self.benchmark
            )
            parts.append("<strong>Benchmark:</strong> %s<br>" % benchmark_info)
        if self.rule_id:
            parts.append("<strong>Rule ID:</strong> %s<br>" % self.rule_id)
        if self.category:
            parts.append("<strong>Category:</strong> %s<br>" % self.category)
        parts.append("<strong>Status:</strong> %s<br>" % self.status)
        parts.append("</p>")
        return parts

    def _build_rule_description_section(self) -> List[str]:
        """Build the rule description section."""
        if not self.rule_description:
            return []
        return ["<h4>Rule Description</h4>", "<p>%s</p>" % self.rule_description]

    def _build_check_details_section(self) -> List[str]:
        """Build the check details section with expected/actual values."""
        if not self.expected_value and not self.actual_value:
            return []
        parts = ["<h4>Check Details</h4>", "<ul>"]
        if self.expected_value:
            parts.append("<li><strong>Expected:</strong> %s</li>" % self.expected_value)
        if self.actual_value:
            parts.append("<li><strong>Actual:</strong> %s</li>" % self.actual_value)
        parts.append("</ul>")
        return parts

    def _build_fix_text_section(self) -> List[str]:
        """Build the remediation section."""
        if not self.fix_text:
            return []
        return ["<h4>Remediation</h4>", "<p>%s</p>" % self.fix_text]

    def _build_control_mappings_section(self) -> List[str]:
        """Build the control mappings section."""
        if not self.nist_controls and not self.ccis:
            return []
        parts = ["<h4>Control Mappings</h4>", "<ul>"]
        if self.nist_controls:
            parts.append("<li><strong>NIST Controls:</strong> %s</li>" % ", ".join(self.nist_controls))
        if self.ccis:
            parts.append("<li><strong>CCIs:</strong> %s</li>" % ", ".join(self.ccis))
        parts.append("</ul>")
        return parts

    def _build_endpoint_section(self) -> List[str]:
        """Build the endpoint info section."""
        if not self.endpoint_name:
            return []
        return ["<p><strong>Affected Endpoint:</strong> %s</p>" % self.endpoint_name]
