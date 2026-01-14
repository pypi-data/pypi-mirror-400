#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCSF Event Parser and Validator"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from regscale.models.regscale_models.issue import IssueSeverity

logger = logging.getLogger("regscale")


class OCSFParser:
    """Parser for OCSF-formatted security events"""

    # OCSF Event Class definitions
    VULNERABILITY_FINDING = 2001
    COMPLIANCE_FINDING = 2003
    DETECTION_FINDING = 2004
    AUTHENTICATION = 3002
    NETWORK_ACTIVITY = 4001

    # Required base event fields
    REQUIRED_BASE_FIELDS = [
        "activity_id",
        "category_uid",
        "class_uid",
        "severity_id",
        "time",
        "type_uid",
    ]

    def __init__(self, validate_schema: bool = True, schema_version: str = "1.6.0"):
        """
        Initialize OCSF Parser

        :param bool validate_schema: Whether to validate against OCSF schema
        :param str schema_version: OCSF schema version to validate against
        """
        self.validate_schema = validate_schema
        self.schema_version = schema_version
        logger.info("Initialized OCSF Parser (schema version: %s, validation: %s)", schema_version, validate_schema)

    def parse_event(self, event_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse a single OCSF event

        :param Union[str, Dict[str, Any]] event_data: OCSF event as JSON string or dict
        :return: Parsed OCSF event dictionary
        :rtype: Dict[str, Any]
        :raises ValueError: If event is invalid
        """
        if isinstance(event_data, str):
            try:
                event = json.loads(event_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON event data: {e}")
        else:
            event = event_data

        if self.validate_schema:
            self._validate_base_fields(event)

        return event

    def parse_events(self, events_data: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Parse multiple OCSF events

        :param Union[str, List[Dict[str, Any]]] events_data: OCSF events as JSON string or list
        :return: List of parsed OCSF events
        :rtype: List[Dict[str, Any]]
        """
        if isinstance(events_data, str):
            try:
                events = json.loads(events_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON events data: {e}")
        else:
            events = events_data

        if not isinstance(events, list):
            events = [events]

        parsed_events = []
        for idx, event in enumerate(events):
            try:
                parsed_event = self.parse_event(event)
                parsed_events.append(parsed_event)
            except ValueError as e:
                logger.warning("Skipping invalid event at index %d: %s", idx, str(e))
                continue

        logger.info("Parsed %d OCSF events (skipped %d invalid)", len(parsed_events), len(events) - len(parsed_events))
        return parsed_events

    def _validate_base_fields(self, event: Dict[str, Any]) -> None:
        """
        Validate required OCSF base fields

        :param Dict[str, Any] event: OCSF event to validate
        :raises ValueError: If required fields are missing
        :rtype: None
        """
        missing_fields = [field for field in self.REQUIRED_BASE_FIELDS if field not in event]

        if missing_fields:
            raise ValueError(f"Missing required OCSF base fields: {', '.join(missing_fields)}")

    def get_event_class(self, event: Dict[str, Any]) -> int:
        """
        Get OCSF event class UID from event

        :param Dict[str, Any] event: OCSF event
        :return: Event class UID
        :rtype: int
        """
        return event.get("class_uid", 0)

    def get_event_category(self, event: Dict[str, Any]) -> int:
        """
        Get OCSF event category UID from event

        :param Dict[str, Any] event: OCSF event
        :return: Event category UID
        :rtype: int
        """
        return event.get("category_uid", 0)

    def is_vulnerability_finding(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is a Vulnerability Finding (2001)

        :param Dict[str, Any] event: OCSF event
        :return: True if vulnerability finding
        :rtype: bool
        """
        return self.get_event_class(event) == self.VULNERABILITY_FINDING

    def is_compliance_finding(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is a Compliance Finding (2003)

        :param Dict[str, Any] event: OCSF event
        :return: True if compliance finding
        :rtype: bool
        """
        return self.get_event_class(event) == self.COMPLIANCE_FINDING

    def is_detection_finding(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is a Detection Finding (2004)

        :param Dict[str, Any] event: OCSF event
        :return: True if detection finding
        :rtype: bool
        """
        return self.get_event_class(event) == self.DETECTION_FINDING

    def is_authentication_event(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is an Authentication event (3002)

        :param Dict[str, Any] event: OCSF event
        :return: True if authentication event
        :rtype: bool
        """
        return self.get_event_class(event) == self.AUTHENTICATION

    def is_network_activity(self, event: Dict[str, Any]) -> bool:
        """
        Check if event is a Network Activity event (4001)

        :param Dict[str, Any] event: OCSF event
        :return: True if network activity event
        :rtype: bool
        """
        return self.get_event_class(event) == self.NETWORK_ACTIVITY

    def extract_severity(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Extract and normalize severity from OCSF event

        OCSF severity_id values:
        0: Unknown, 1: Informational, 2: Low, 3: Medium, 4: High, 5: Critical, 6: Fatal

        :param Dict[str, Any] event: OCSF event
        :return: Normalized severity string for RegScale
        :rtype: Optional[str]
        """
        severity_id = event.get("severity_id", 0)

        severity_map = {
            0: IssueSeverity.NotAssigned.value,
            1: IssueSeverity.NotAssigned.value,
            2: IssueSeverity.Low.value,
            3: IssueSeverity.Moderate.value,
            4: IssueSeverity.High.value,
            5: IssueSeverity.Critical.value,
            6: IssueSeverity.Critical.value,
        }

        return severity_map.get(severity_id, IssueSeverity.NotAssigned.value)

    def extract_finding_uid(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Extract unique finding identifier from OCSF event

        :param Dict[str, Any] event: OCSF event
        :return: Finding UID
        :rtype: Optional[str]
        """
        finding = event.get("finding", {})
        if isinstance(finding, dict):
            return finding.get("uid")
        return None

    def extract_resources(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract affected resources from OCSF event

        :param Dict[str, Any] event: OCSF event
        :return: List of resource objects
        :rtype: List[Dict[str, Any]]
        """
        resources = event.get("resources", [])
        if not isinstance(resources, list):
            return []
        return resources

    def extract_vulnerabilities(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract vulnerability details from OCSF event

        :param Dict[str, Any] event: OCSF event
        :return: List of vulnerability objects
        :rtype: List[Dict[str, Any]]
        """
        vulnerabilities = event.get("vulnerabilities", [])
        if not isinstance(vulnerabilities, list):
            return []
        return vulnerabilities

    def extract_compliance_controls(self, event: Dict[str, Any]) -> List[str]:
        """
        Extract compliance control identifiers from OCSF event

        :param Dict[str, Any] event: OCSF event
        :return: List of control identifiers
        :rtype: List[str]
        """
        controls = []

        # Check finding.compliance field
        finding = event.get("finding", {})
        if isinstance(finding, dict):
            compliance = finding.get("compliance", {})
            if isinstance(compliance, dict):
                control_ids = compliance.get("control_ids", [])
                if isinstance(control_ids, list):
                    controls.extend([str(c) for c in control_ids if c])

        # Check top-level compliance field
        top_compliance = event.get("compliance", {})
        if isinstance(top_compliance, dict):
            control_ids = top_compliance.get("control_ids", [])
            if isinstance(control_ids, list):
                controls.extend([str(c) for c in control_ids if c])

        return list(set(controls))  # Remove duplicates

    def format_for_regscale(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format OCSF event for RegScale ingestion

        :param Dict[str, Any] event: OCSF event
        :return: Formatted event data for RegScale
        :rtype: Dict[str, Any]
        """
        return {
            "ocsf_event": event,
            "class_uid": self.get_event_class(event),
            "category_uid": self.get_event_category(event),
            "severity": self.extract_severity(event),
            "finding_uid": self.extract_finding_uid(event),
            "resources": self.extract_resources(event),
            "vulnerabilities": self.extract_vulnerabilities(event),
            "compliance_controls": self.extract_compliance_controls(event),
        }
