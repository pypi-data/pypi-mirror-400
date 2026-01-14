#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCSF Scanner Integration for RegScale CLI"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from regscale.core.app.application import Application
from regscale.integrations.commercial.ocsf.mapper import OCSFMapper
from regscale.integrations.commercial.ocsf.parser import OCSFParser
from regscale.integrations.commercial.ocsf.variables import OCSFVariables
from regscale.integrations.integration.integration import Integration
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue

logger = logging.getLogger("regscale")


class OCSFIntegration(Integration):
    """
    OCSF (Open Cybersecurity Schema Framework) Integration

    Ingests OCSF-formatted security events and maps them to RegScale entities
    """

    def __init__(
        self,
        plan_id: int,
        parent_module: str = "securityplans",
        validate_schema: bool = True,
        schema_version: str = "1.6.0",
    ):
        """
        Initialize OCSF Integration

        :param int plan_id: RegScale parent ID (typically SSP ID)
        :param str parent_module: RegScale parent module name
        :param bool validate_schema: Whether to validate against OCSF schema
        :param str schema_version: OCSF schema version
        """
        super().__init__(plan_id=plan_id, parent_module=parent_module)

        self.parser = OCSFParser(validate_schema=validate_schema, schema_version=schema_version)
        self.mapper = OCSFMapper(plan_id=plan_id, parent_module=parent_module)

        self.validate_schema = validate_schema
        self.schema_version = schema_version
        self.plan_id = plan_id
        self.parent_module = parent_module

        logger.info(
            "Initialized OCSF Integration for %s #%d (schema: %s, validation: %s)",
            parent_module,
            plan_id,
            schema_version,
            validate_schema,
        )

    def authenticate(self, **kwargs):
        """
        OCSF integration does not require authentication
        Events are read from files
        """
        pass

    def ingest_file(
        self, file_path: str, create_issues: bool = True, create_assets: bool = True
    ) -> Dict[str, List[Union[Issue, Asset]]]:
        """
        Ingest OCSF events from a file

        :param str file_path: Path to OCSF events file (JSON, JSONL, CSV)
        :param bool create_issues: Create RegScale Issues from findings
        :param bool create_assets: Create RegScale Assets from resources
        :return: Dictionary with created issues and assets
        :rtype: Dict[str, List[Union[Issue, Asset]]]
        """
        logger.info("Ingesting OCSF events from file: %s", file_path)

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file based on extension
        if path.suffix in [".json", ".jsonl"]:
            events = self._read_json_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        return self.process_events(events, create_issues=create_issues, create_assets=create_assets)

    def process_events(
        self, events: List[Dict[str, Any]], create_issues: bool = True, create_assets: bool = True
    ) -> Dict[str, List[Union[Issue, Asset]]]:
        """
        Process OCSF events and create RegScale entities

        :param List[Dict[str, Any]] events: List of OCSF events
        :param bool create_issues: Create RegScale Issues
        :param bool create_assets: Create RegScale Assets
        :return: Dictionary with created issues and assets
        :rtype: Dict[str, List[Union[Issue, Asset]]]
        """
        logger.info("Processing %d OCSF events", len(events))

        # Parse and filter events
        parsed_events = self._parse_and_filter_events(events)

        # Map events to RegScale entities
        issues, assets = self._map_events_to_entities(parsed_events, create_issues, create_assets)

        logger.info("Mapped %d OCSF events to %d Issues and %d Assets", len(parsed_events), len(issues), len(assets))

        # Create/update entities in RegScale
        return self._create_entities_in_regscale(issues, assets)

    def _parse_and_filter_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and filter OCSF events

        :param List[Dict[str, Any]] events: Raw OCSF events
        :return: Parsed and filtered events
        :rtype: List[Dict[str, Any]]
        """
        parsed_events = self.parser.parse_events(events)
        logger.info("Successfully parsed %d OCSF events", len(parsed_events))

        event_class_filters = OCSFVariables.get_event_class_filters()
        if event_class_filters:
            parsed_events = [e for e in parsed_events if e.get("class_uid") in event_class_filters]
            logger.info("Filtered to %d events based on event class filters", len(parsed_events))

        return parsed_events

    def _map_events_to_entities(
        self, parsed_events: List[Dict[str, Any]], create_issues: bool, create_assets: bool
    ) -> tuple[List[Issue], List[Asset]]:
        """
        Map OCSF events to RegScale Issues and Assets

        :param List[Dict[str, Any]] parsed_events: Parsed OCSF events
        :param bool create_issues: Whether to create issues
        :param bool create_assets: Whether to create assets
        :return: Tuple of issues and assets
        :rtype: tuple[List[Issue], List[Asset]]
        """
        issues = []
        assets = []

        for event in parsed_events:
            parsed_data = self.parser.format_for_regscale(event)

            if create_issues:
                issue = self._try_create_issue(event, parsed_data)
                if issue:
                    issues.append(issue)

            if create_assets:
                event_assets = self._try_create_assets(parsed_data)
                assets.extend(event_assets)

        return issues, assets

    def _try_create_issue(self, event: Dict[str, Any], parsed_data: Dict[str, Any]) -> Optional[Issue]:
        """
        Try to create an Issue from an OCSF event

        :param Dict[str, Any] event: OCSF event
        :param Dict[str, Any] parsed_data: Parsed event data
        :return: Issue if created, None otherwise
        :rtype: Optional[Issue]
        """
        if not self._should_create_issue(event):
            return None

        try:
            return self.mapper.map_to_issue(event, parsed_data)
        except Exception as e:
            logger.error("Failed to map OCSF event to Issue: %s", str(e), exc_info=True)
            return None

    def _try_create_assets(self, parsed_data: Dict[str, Any]) -> List[Asset]:
        """
        Try to create Assets from OCSF event resources

        :param Dict[str, Any] parsed_data: Parsed event data
        :return: List of created assets
        :rtype: List[Asset]
        """
        resources = parsed_data.get("resources", [])
        if not resources:
            return []

        try:
            return self.mapper.map_resources_to_assets(resources, self.plan_id, self.parent_module)
        except Exception as e:
            logger.error("Failed to map OCSF resources to Assets: %s", str(e), exc_info=True)
            return []

    def _create_entities_in_regscale(
        self, issues: List[Issue], assets: List[Asset]
    ) -> Dict[str, List[Union[Issue, Asset]]]:
        """
        Create or update entities in RegScale

        :param List[Issue] issues: Issues to create/update
        :param List[Asset] assets: Assets to create/update
        :return: Dictionary with created issues and assets
        :rtype: Dict[str, List[Union[Issue, Asset]]]
        """
        result = {"issues": [], "assets": []}

        if issues:
            result["issues"] = self._create_or_update_issues(issues)

        if assets:
            result["assets"] = self._create_or_update_assets(assets)

        return result

    def _should_create_issue(self, event: Dict[str, Any]) -> bool:
        """
        Determine if an OCSF event should create a RegScale Issue

        :param Dict[str, Any] event: OCSF event
        :return: True if issue should be created
        :rtype: bool
        """
        # Create issues for findings (vulnerability, compliance, detection)
        class_uid = event.get("class_uid", 0)
        return class_uid in [
            OCSFParser.VULNERABILITY_FINDING,
            OCSFParser.COMPLIANCE_FINDING,
            OCSFParser.DETECTION_FINDING,
        ]

    def _read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read OCSF events from JSON or JSONL file

        :param str file_path: Path to JSON/JSONL file
        :return: List of OCSF events
        :rtype: List[Dict[str, Any]]
        """
        events = []
        path = Path(file_path)

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix == ".jsonl":
                # Read JSONL (one JSON object per line)
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError as e:
                        logger.warning("Skipping invalid JSON at line %d: %s", line_num, str(e))
            else:
                # Read standard JSON (single array or object)
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        events = data
                    else:
                        events = [data]
                except json.JSONDecodeError as e:
                    logger.error("Failed to parse JSON file %s: %s", file_path, str(e))
                    raise

        logger.info("Read %d events from %s", len(events), file_path)
        return events

    def _create_or_update_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Create or update Issues in RegScale

        :param List[Issue] issues: List of Issue models
        :return: List of created/updated Issues
        :rtype: List[Issue]
        """
        logger.info("Creating/updating %d Issues in RegScale", len(issues))

        # Use create_or_update from base class
        results = []
        for issue in issues:
            try:
                created_issue = issue.create_or_update()
                results.append(created_issue)
            except Exception as e:
                logger.error("Failed to create/update issue %s: %s", issue.otherIdentifier, str(e))

        logger.info("Successfully created/updated %d Issues", len(results))
        return results

    def _create_or_update_assets(self, assets: List[Asset]) -> List[Asset]:
        """
        Create or update Assets in RegScale

        :param List[Asset] assets: List of Asset models
        :return: List of created/updated Assets
        :rtype: List[Asset]
        """
        logger.info("Creating/updating %d Assets in RegScale", len(assets))

        # Use create_or_update from base class
        results = []
        for asset in assets:
            try:
                created_asset = asset.create_or_update()
                results.append(created_asset)
            except Exception as e:
                logger.error("Failed to create/update asset %s: %s", asset.otherTrackingNumber, str(e))

        logger.info("Successfully created/updated %d Assets", len(results))
        return results

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate OCSF events file without creating entities

        :param str file_path: Path to OCSF events file
        :return: Validation results
        :rtype: Dict[str, Any]
        """
        logger.info("Validating OCSF events file: %s", file_path)

        try:
            events = self._read_json_file(file_path)
            parsed_events = self.parser.parse_events(events)

            validation_result = {
                "valid": True,
                "total_events": len(events),
                "parsed_events": len(parsed_events),
                "invalid_events": len(events) - len(parsed_events),
                "event_classes": self._get_event_class_counts(parsed_events),
                "file_path": file_path,
            }

            logger.info(
                "Validation complete: %d/%d events valid",
                validation_result["parsed_events"],
                validation_result["total_events"],
            )

            return validation_result

        except Exception as e:
            logger.error("Validation failed: %s", str(e))
            return {"valid": False, "error": str(e), "file_path": file_path}

    def _get_event_class_counts(self, events: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Get counts of events by event class

        :param List[Dict[str, Any]] events: List of OCSF events
        :return: Dictionary of event class counts
        :rtype: Dict[int, int]
        """
        counts = {}
        for event in events:
            class_uid = event.get("class_uid", 0)
            counts[class_uid] = counts.get(class_uid, 0) + 1
        return counts
