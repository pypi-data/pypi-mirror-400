#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium Vulnerability Model.

Transforms Tanium Comply vulnerability data to RegScale Vulnerability format.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("regscale")


@dataclass
class TaniumVulnerability:
    """
    Represents a Tanium vulnerability from the Comply module.

    Maps Tanium vulnerability data to RegScale Vulnerability model fields.
    """

    tanium_id: str
    cve_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    published_date: Optional[str] = None
    last_modified_date: Optional[str] = None
    affected_endpoint_count: int = 0
    affected_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    solution: Optional[str] = None
    references: List[str] = field(default_factory=list)
    exploit_available: bool = False
    patch_available: bool = False
    affected_products: List[str] = field(default_factory=list)
    first_detected: Optional[str] = None
    last_detected: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_tanium_data(cls, data: Dict[str, Any]) -> "TaniumVulnerability":
        """
        Create TaniumVulnerability from Tanium API response data.

        Args:
            data: Raw vulnerability data from Tanium Comply API

        Returns:
            TaniumVulnerability instance
        """
        # Parse CVSS score, handling invalid values
        cvss_score = data.get("cvssScore")
        if cvss_score is not None:
            try:
                cvss_score = float(cvss_score)
            except (ValueError, TypeError):
                logger.warning("Invalid CVSS score value: %s", cvss_score)
                cvss_score = None

        return cls(
            tanium_id=str(data.get("id", "")),
            cve_id=data.get("cveId"),
            title=data.get("title"),
            description=data.get("description"),
            severity=data.get("severity"),
            cvss_score=cvss_score,
            cvss_vector=data.get("cvssVector"),
            published_date=data.get("publishedDate"),
            last_modified_date=data.get("lastModifiedDate"),
            affected_endpoint_count=data.get("affectedEndpointCount", 0),
            affected_endpoints=data.get("affectedEndpoints", []),
            solution=data.get("solution"),
            references=data.get("references", []),
            exploit_available=data.get("exploitAvailable", False),
            patch_available=data.get("patchAvailable", False),
            affected_products=data.get("affectedProducts", []),
            first_detected=data.get("firstDetected"),
            last_detected=data.get("lastDetected"),
            raw_data=data,
        )

    def get_regscale_severity(self) -> str:
        """
        Map Tanium severity to RegScale VulnerabilitySeverity.

        Uses explicit severity if available, otherwise derives from CVSS score.

        Returns:
            RegScale severity string (Critical, High, Medium, Low, Informational)
        """
        # Try explicit severity mapping first
        severity_from_explicit = self._map_explicit_severity()
        if severity_from_explicit:
            return severity_from_explicit

        # Fall back to CVSS score mapping
        return self._map_cvss_to_severity()

    def _map_explicit_severity(self) -> Optional[str]:
        """Map explicit severity value to RegScale severity."""
        if not self.severity:
            return None
        severity_map = {
            "CRITICAL": "Critical",
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low",
            "INFORMATIONAL": "Informational",
        }
        return severity_map.get(self.severity.upper())

    def _map_cvss_to_severity(self) -> str:
        """Map CVSS score to RegScale severity."""
        if self.cvss_score is None:
            return "Informational"
        # CVSS thresholds: Critical >= 9.0, High >= 7.0, Medium >= 4.0, Low > 0
        cvss_thresholds = [(9.0, "Critical"), (7.0, "High"), (4.0, "Medium"), (0, "Low")]
        for threshold, severity in cvss_thresholds:
            if self.cvss_score >= threshold:
                return severity
        return "Informational"

    def get_unique_identifier(self) -> str:
        """
        Generate unique identifier for this vulnerability.

        Returns:
            Unique identifier string
        """
        if self.cve_id:
            return "tanium-vuln-%s-%s" % (self.cve_id, self.tanium_id)
        return "tanium-vuln-%s" % self.tanium_id

    def to_regscale_vulnerability(self, parent_id: int, parent_module: str) -> Dict[str, Any]:
        """
        Convert to RegScale Vulnerability dictionary format.

        Args:
            parent_id: RegScale parent record ID
            parent_module: RegScale parent module name

        Returns:
            Dictionary suitable for creating RegScale Vulnerability
        """
        vuln_dict = {
            "parentId": parent_id,
            "parentModule": parent_module,
            "cve": self.cve_id or "",
            "title": self.title or self.cve_id or "Unknown Vulnerability",
            "severity": self.get_regscale_severity(),
            "description": self._build_description(),
            "plugInName": "Tanium Comply",
            "plugInId": self.tanium_id,
            "exploitAvailable": self.exploit_available,
            "status": "Open",
        }

        # Add CVSS score if available
        if self.cvss_score is not None:
            vuln_dict["cvsSv3BaseScore"] = self.cvss_score
        if self.cvss_vector:
            vuln_dict["cvsSv3BaseVector"] = self.cvss_vector

        # Add dates
        if self.first_detected:
            vuln_dict["firstSeen"] = self.first_detected
        if self.last_detected:
            vuln_dict["lastSeen"] = self.last_detected

        # Add solution/remediation
        if self.solution:
            vuln_dict["plugInText"] = self.solution

        return vuln_dict

    def _build_description(self) -> str:
        """Build vulnerability description with Tanium details."""
        parts = []

        if self.description:
            parts.append(self.description)

        if self.affected_endpoint_count > 0:
            parts.append("Affected Endpoints: %s" % self.affected_endpoint_count)

        if self.affected_products:
            parts.append("Affected Products: %s" % ", ".join(self.affected_products[:5]))

        if self.solution:
            parts.append("Solution: %s" % self.solution)

        if self.references:
            parts.append("References: %s" % ", ".join(self.references[:3]))

        return "\n\n".join(parts) if parts else "Vulnerability detected by Tanium Comply"

    def get_affected_endpoint_ids(self) -> List[int]:
        """
        Get list of affected endpoint IDs.

        Returns:
            List of endpoint IDs
        """
        return [ep.get("id") for ep in self.affected_endpoints if ep.get("id")]
