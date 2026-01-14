#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCSF to RegScale Model Mapper"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from regscale.integrations.control_matcher import ControlMatcher
from regscale.models.regscale_models.asset import Asset, AssetCategory, AssetStatus, AssetType
from regscale.models.regscale_models.issue import Issue, IssueSeverity, IssueStatus

logger = logging.getLogger("regscale")


class OCSFMapper:
    """Maps OCSF events to RegScale models"""

    def __init__(self, plan_id: int, parent_module: str = "securityplans"):
        """
        Initialize OCSF Mapper

        :param int plan_id: RegScale parent ID (typically SSP ID)
        :param str parent_module: RegScale parent module name
        """
        self.plan_id = plan_id
        self.parent_module = parent_module
        self.control_matcher = ControlMatcher()
        logger.info("Initialized OCSF Mapper for %s #%d", parent_module, plan_id)

    def map_to_issue(self, ocsf_event: Dict[str, Any], parsed_data: Dict[str, Any]) -> Issue:
        """
        Map OCSF event to RegScale Issue

        :param Dict[str, Any] ocsf_event: Original OCSF event
        :param Dict[str, Any] parsed_data: Parsed OCSF data from OCSFParser
        :return: RegScale Issue model
        :rtype: Issue
        """
        finding = ocsf_event.get("finding", {})
        finding_info = ocsf_event.get("finding_info", {})

        # Extract basic info
        title = finding.get("title") or finding_info.get("title", "OCSF Security Finding")
        description = finding.get("desc") or finding_info.get("desc", "")
        finding_uid = parsed_data.get("finding_uid") or ocsf_event.get("metadata", {}).get("uid")

        # Map severity
        severity = parsed_data.get("severity", IssueSeverity.NotAssigned.value)

        # Map affected controls
        controls = parsed_data.get("compliance_controls", [])
        affected_controls = ", ".join(controls) if controls else None

        # Map affected assets
        resources = parsed_data.get("resources", [])
        asset_identifiers = self._extract_asset_identifiers(resources)
        asset_identifier = "\n".join(asset_identifiers) if asset_identifiers else None

        # Extract timestamps
        time_dt = self._parse_ocsf_timestamp(ocsf_event.get("time"))
        date_created = time_dt.strftime("%Y-%m-%dT%H:%M:%S") if time_dt else None
        date_first_detected = date_created

        # Store raw OCSF event in notes
        raw_event_json = json.dumps(ocsf_event, indent=2)

        issue = Issue(
            title=title[:255] if title else "OCSF Security Finding",  # Limit title length
            description=description,
            severityLevel=severity,
            status=IssueStatus.Open.value,
            parentId=self.plan_id,
            parentModule=self.parent_module,
            otherIdentifier=finding_uid,
            affectedControls=affected_controls,
            assetIdentifier=asset_identifier,
            dateCreated=date_created,
            dateFirstDetected=date_first_detected,
            identification="Security Control Assessment",
            notes=f"OCSF Event Class: {parsed_data.get('class_uid')}\n\nRaw OCSF Event:\n{raw_event_json}",
        )

        logger.debug(
            "Mapped OCSF event %s to Issue: %s (controls: %s, assets: %d)",
            finding_uid,
            title[:50],
            affected_controls,
            len(asset_identifiers),
        )

        return issue

    def map_to_asset(
        self, resource: Dict[str, Any], plan_id: int, parent_module: str = "securityplans"
    ) -> Optional[Asset]:
        """
        Map OCSF resource object to RegScale Asset

        :param Dict[str, Any] resource: OCSF resource object
        :param int plan_id: RegScale parent ID
        :param str parent_module: RegScale parent module
        :return: RegScale Asset model or None
        :rtype: Optional[Asset]
        """
        if not resource:
            return None

        # Extract resource details
        uid = resource.get("uid")
        name = resource.get("name", uid or "Unknown Resource")
        resource_type = resource.get("type", "Other")

        # Determine asset type and category
        asset_type, asset_category = self._map_resource_type(resource_type)

        # Extract identifiers
        cloud_provider = resource.get("cloud_provider")
        region = resource.get("region")
        labels = resource.get("labels", {})

        # Build description
        description_parts = []
        if resource.get("desc"):
            description_parts.append(resource["desc"])
        if cloud_provider:
            description_parts.append(f"Cloud Provider: {cloud_provider}")
        if region:
            description_parts.append(f"Region: {region}")

        description = " | ".join(description_parts) if description_parts else None

        # Create notes with OCSF resource data
        notes_data = {"ocsf_resource": resource, "labels": labels}
        notes = json.dumps(notes_data, indent=2)

        asset = Asset(
            name=name[:255] if name else "OCSF Resource",
            assetType=asset_type,
            assetCategory=asset_category,
            status=AssetStatus.Active.value,
            parentId=plan_id,
            parentModule=parent_module,
            otherTrackingNumber=uid,
            description=description[:1000] if description else None,
            notes=notes,
        )

        logger.debug("Mapped OCSF resource %s to Asset: %s", uid, name[:50])

        return asset

    def map_resources_to_assets(
        self, resources: List[Dict[str, Any]], plan_id: int, parent_module: str = "securityplans"
    ) -> List[Asset]:
        """
        Map list of OCSF resources to RegScale Assets

        :param List[Dict[str, Any]] resources: List of OCSF resource objects
        :param int plan_id: RegScale parent ID
        :param str parent_module: RegScale parent module
        :return: List of RegScale Asset models
        :rtype: List[Asset]
        """
        assets = []
        for resource in resources:
            asset = self.map_to_asset(resource, plan_id, parent_module)
            if asset:
                assets.append(asset)

        logger.info("Mapped %d OCSF resources to Assets", len(assets))
        return assets

    def _extract_asset_identifiers(self, resources: List[Dict[str, Any]]) -> List[str]:
        """
        Extract asset identifiers from OCSF resources

        :param List[Dict[str, Any]] resources: List of OCSF resource objects
        :return: List of asset identifiers
        :rtype: List[str]
        """
        identifiers = []
        for resource in resources:
            uid = resource.get("uid")
            if uid:
                identifiers.append(str(uid))

        return identifiers

    def _map_resource_type(self, ocsf_type: str) -> tuple:
        """
        Map OCSF resource type to RegScale Asset type and category

        :param str ocsf_type: OCSF resource type
        :return: Tuple of (AssetType, AssetCategory)
        :rtype: tuple
        """
        type_lower = ocsf_type.lower() if ocsf_type else ""

        # Map to Asset Type and Category
        if "vm" in type_lower or "virtual" in type_lower or "instance" in type_lower:
            return AssetType.VM.value, AssetCategory.Hardware.value
        elif "server" in type_lower:
            return AssetType.PhysicalServer.value, AssetCategory.Hardware.value
        elif "container" in type_lower:
            return AssetType.Other.value, AssetCategory.Software.value
        elif "lambda" in type_lower or "function" in type_lower:
            return AssetType.Other.value, AssetCategory.Software.value
        elif "database" in type_lower or "db" in type_lower:
            return AssetType.Other.value, AssetCategory.Software.value
        elif "storage" in type_lower or "bucket" in type_lower:
            return AssetType.Other.value, AssetCategory.Hardware.value
        elif "network" in type_lower:
            return AssetType.NetworkRouter.value, AssetCategory.Hardware.value
        else:
            return AssetType.Other.value, AssetCategory.Hardware.value

    def _parse_ocsf_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """
        Parse OCSF timestamp to datetime object

        OCSF timestamps are Unix epoch milliseconds

        :param Any timestamp: OCSF timestamp (int or string)
        :return: Datetime object or None
        :rtype: Optional[datetime]
        """
        if timestamp is None:
            return None

        try:
            if isinstance(timestamp, str):
                timestamp = int(timestamp)

            # OCSF uses milliseconds since epoch - use UTC to match OCSF standards
            from datetime import timezone

            return datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc).replace(tzinfo=None)
        except (ValueError, TypeError) as e:
            logger.warning("Failed to parse OCSF timestamp %s: %s", timestamp, str(e))
            return None

    def format_controls_for_regscale(self, control_ids: List[str]) -> str:
        """
        Format control IDs for RegScale affectedControls field using control_matcher

        Uses ControlMatcher to properly parse OCSF control formats like "NIST-800-53:SC-28"
        and normalize them to RegScale standard format like "SC-28"

        :param List[str] control_ids: List of control identifiers (may include OCSF format with framework prefix)
        :return: Comma-separated control string
        :rtype: str
        """
        if not control_ids:
            return ""

        # Parse control IDs using control_matcher to handle OCSF format
        parsed_controls = []
        for control_id in control_ids:
            parsed = self.control_matcher.parse_control_id(control_id)
            if parsed:
                parsed_controls.append(parsed)
            else:
                # If parsing fails, fall back to simple colon split
                if ":" in control_id:
                    parsed_controls.append(control_id.split(":")[-1].strip())
                else:
                    parsed_controls.append(control_id.strip())

        return ", ".join(sorted(set(parsed_controls)))
