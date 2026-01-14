#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium Scanner Integration for RegScale.

This module provides the TaniumScanner class that fetches assets, vulnerabilities,
and compliance findings from Tanium and syncs them to RegScale.
"""

import logging
from typing import Any, Dict, Generator, Iterator, List, Optional

from regscale.core.app.application import Application
from regscale.integrations.commercial.tanium.tanium_api_client import (
    TaniumAPIClient,
    TaniumAPIException,
)
from regscale.integrations.commercial.tanium.models.assets import TaniumEndpoint
from regscale.integrations.commercial.tanium.models.vulnerabilities import TaniumVulnerability
from regscale.integrations.commercial.tanium.models.compliance import TaniumComplianceFinding
from regscale.integrations.commercial.tanium.variables import TaniumVariables
from regscale.integrations.scanner_integration import (
    IntegrationAsset,
    IntegrationFinding,
    ScannerIntegration,
    ScannerIntegrationType,
)
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


def endpoint_to_integration_asset(endpoint: TaniumEndpoint) -> IntegrationAsset:
    """
    Convert TaniumEndpoint to IntegrationAsset.

    Args:
        endpoint: TaniumEndpoint instance

    Returns:
        IntegrationAsset for use with ScannerIntegration
    """
    return IntegrationAsset(
        name=endpoint.computer_name,
        identifier=endpoint.get_unique_identifier(),
        asset_type=endpoint.get_asset_type(),
        asset_category="Hardware",
        ip_address=endpoint.ip_address or "",
        mac_address=endpoint.mac_address or "",
        fqdn=endpoint._build_fqdn(),
        operating_system=endpoint.get_operating_system_category(),
        serial_number=endpoint.serial_number or "",
        manufacturer=endpoint.manufacturer or "",
        model=endpoint.model or "",
        description=endpoint._build_description(),
        is_virtual=endpoint.is_virtual,
    )


def vulnerability_to_integration_finding(
    vuln: TaniumVulnerability,
    asset_identifier: str = "",
) -> IntegrationFinding:
    """
    Convert TaniumVulnerability to IntegrationFinding.

    Args:
        vuln: TaniumVulnerability instance
        asset_identifier: Optional asset identifier

    Returns:
        IntegrationFinding for use with ScannerIntegration
    """
    severity = _map_severity_to_regscale(vuln.get_regscale_severity())

    return IntegrationFinding(
        control_labels=[],
        title=vuln.title or vuln.cve_id or "Tanium Vulnerability",
        category="Vulnerability",
        plugin_name="Tanium Comply",
        severity=severity,
        description=vuln._build_description(),
        status=regscale_models.IssueStatus.Open,
        cve=vuln.cve_id,
        cvss_v3_score=vuln.cvss_score,
        cvss_v3_vector=vuln.cvss_vector,
        asset_identifier=asset_identifier,
        external_id=vuln.tanium_id,
        first_seen=vuln.first_detected,
        last_seen=vuln.last_detected,
        remediation=vuln.solution,
    )


def compliance_to_integration_finding(
    finding: TaniumComplianceFinding,
) -> IntegrationFinding:
    """
    Convert TaniumComplianceFinding to IntegrationFinding.

    Args:
        finding: TaniumComplianceFinding instance

    Returns:
        IntegrationFinding for use with ScannerIntegration
    """
    severity = _map_severity_to_regscale(finding.get_regscale_severity())
    status = regscale_models.IssueStatus.Closed if finding.is_compliant() else regscale_models.IssueStatus.Open

    # Build asset identifier if endpoint info available
    asset_identifier = ""
    if finding.endpoint_id:
        asset_identifier = "tanium-%s-%s" % (finding.endpoint_id, finding.endpoint_name or "")

    return IntegrationFinding(
        control_labels=finding.get_nist_controls(),
        title=finding._build_title(),
        category="Compliance",
        plugin_name="Tanium Comply",
        severity=severity,
        description=finding._build_description(),
        status=status,
        rule_id=finding.rule_id,
        cci_ref=",".join(finding.get_cci_ids()) if finding.get_cci_ids() else None,
        asset_identifier=asset_identifier,
        external_id=finding.tanium_id,
        remediation=finding.fix_text,
    )


def _map_severity_to_regscale(severity: str) -> regscale_models.IssueSeverity:
    """
    Map severity string to RegScale IssueSeverity enum.

    Args:
        severity: Severity string (Critical, High, Medium, Low)

    Returns:
        RegScale IssueSeverity enum value
    """
    severity_map = {
        "Critical": regscale_models.IssueSeverity.Critical,
        "High": regscale_models.IssueSeverity.High,
        "Medium": regscale_models.IssueSeverity.Moderate,
        "Low": regscale_models.IssueSeverity.Low,
        "Informational": regscale_models.IssueSeverity.Low,
    }
    return severity_map.get(severity, regscale_models.IssueSeverity.Moderate)


class TaniumScanner(ScannerIntegration):
    """
    Tanium Scanner Integration for RegScale.

    Fetches assets, vulnerabilities, and compliance findings from Tanium
    and syncs them to RegScale.
    """

    title = "Tanium"
    type = ScannerIntegrationType.VULNERABILITY

    def __init__(self, *args, **kwargs):
        """
        Initialize the Tanium Scanner Integration.

        Args:
            *args: Arguments to pass to parent class
            **kwargs: Keyword arguments to pass to parent class
        """
        super().__init__(*args, **kwargs)

        self.app = Application()

        # Initialize API client
        self.api_client = TaniumAPIClient(
            base_url=TaniumVariables.taniumUrl,
            api_token=TaniumVariables.taniumToken,
            verify_ssl=TaniumVariables.taniumVerifySsl,
            timeout=TaniumVariables.taniumTimeout,
            protocols=TaniumVariables.taniumProtocols,
        )

        # Cache for endpoint data
        self._endpoint_cache: Dict[int, TaniumEndpoint] = {}

    def fetch_assets(self, **kwargs) -> Generator[IntegrationAsset, None, None]:
        """
        Fetch assets (endpoints) from Tanium.

        Yields:
            IntegrationAsset objects for each Tanium endpoint
        """
        logger.info("Fetching assets from Tanium...")

        try:
            endpoints = self.api_client.get_all_endpoints()
        except TaniumAPIException as e:
            logger.error("Failed to fetch endpoints from Tanium: %s", str(e))
            return

        if not endpoints:
            logger.warning("No endpoints found in Tanium")
            return

        self.num_assets_to_process = len(endpoints)
        logger.info("Processing %s endpoints from Tanium", len(endpoints))

        for endpoint_data in endpoints:
            try:
                endpoint = TaniumEndpoint.from_tanium_data(endpoint_data)
                # Cache endpoint for vulnerability/finding mapping
                self._endpoint_cache[endpoint.tanium_id] = endpoint
                yield endpoint_to_integration_asset(endpoint)
            except Exception as e:
                logger.warning(
                    "Failed to process endpoint %s: %s",
                    endpoint_data.get("computerName", "Unknown"),
                    str(e),
                )

    def fetch_findings(self, **kwargs) -> Generator[IntegrationFinding, None, None]:
        """
        Fetch findings from Tanium.

        Yields vulnerabilities and optionally compliance findings.

        Yields:
            IntegrationFinding objects for each finding
        """
        logger.info("Fetching findings from Tanium...")

        # Fetch vulnerabilities
        yield from self._fetch_vulnerabilities()

        # Optionally fetch compliance findings
        include_compliance = kwargs.get("include_compliance", True)
        if include_compliance:
            yield from self._fetch_compliance_findings()

    def _fetch_vulnerabilities(self) -> Generator[IntegrationFinding, None, None]:
        """
        Fetch vulnerabilities from Tanium Comply module.

        Yields:
            IntegrationFinding objects for each vulnerability
        """
        logger.info("Fetching vulnerabilities from Tanium Comply...")

        try:
            vulnerabilities = self.api_client.get_all_vulnerabilities()
        except TaniumAPIException as e:
            logger.error("Failed to fetch vulnerabilities from Tanium: %s", str(e))
            return

        if not vulnerabilities:
            logger.info("No vulnerabilities found in Tanium")
            return

        findings_count = 0

        for vuln_data in vulnerabilities:
            try:
                vuln = TaniumVulnerability.from_tanium_data(vuln_data)

                # Create finding for each affected endpoint or a single finding if no endpoints
                affected_endpoints = vuln.get_affected_endpoint_ids()

                if affected_endpoints:
                    for endpoint_id in affected_endpoints:
                        endpoint = self._endpoint_cache.get(endpoint_id)
                        asset_identifier = ""
                        if endpoint:
                            asset_identifier = endpoint.get_unique_identifier()
                        yield vulnerability_to_integration_finding(vuln, asset_identifier)
                        findings_count += 1
                else:
                    yield vulnerability_to_integration_finding(vuln)
                    findings_count += 1

            except Exception as e:
                logger.warning(
                    "Failed to process vulnerability %s: %s",
                    vuln_data.get("cveId", "Unknown"),
                    str(e),
                )

        self.num_findings_to_process = findings_count
        logger.info("Processed %s vulnerability findings from Tanium", findings_count)

    def _fetch_compliance_findings(self) -> Generator[IntegrationFinding, None, None]:
        """
        Fetch compliance findings from Tanium Comply module.

        Only yields non-compliant findings (status=Fail).

        Yields:
            IntegrationFinding objects for each compliance finding
        """
        logger.info("Fetching compliance findings from Tanium Comply...")

        try:
            # Only fetch failing compliance findings
            findings = self.api_client.get_compliance_findings(status="Fail")
        except TaniumAPIException as e:
            logger.error("Failed to fetch compliance findings from Tanium: %s", str(e))
            return

        if not findings:
            logger.info("No compliance findings found in Tanium")
            return

        for finding_data in findings:
            try:
                finding = TaniumComplianceFinding.from_tanium_data(finding_data)

                # Skip compliant findings
                if finding.is_compliant():
                    continue

                yield compliance_to_integration_finding(finding)

            except Exception as e:
                logger.warning(
                    "Failed to process compliance finding %s: %s",
                    finding_data.get("ruleId", "Unknown"),
                    str(e),
                )

        logger.info("Processed compliance findings from Tanium")
