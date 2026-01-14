#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration variables for OCSF integration"""

from regscale.core.app.utils.variables import RsVariablesMeta, RsVariableType


class OCSFVariables(metaclass=RsVariablesMeta):
    """
    OCSF Integration Configuration Variables

    These variables can be set in init.yaml or as environment variables.
    Environment variables use uppercase with OCSF_ prefix (e.g., OCSF_VALIDATE_SCHEMA).
    """

    # File format configuration
    ocsfInputFormat: RsVariableType(str, "json|csv|parquet", default="json", required=False)  # type: ignore # noqa: F722,F821
    ocsfOutputFormat: RsVariableType(str, "json|jsonl", default="json", required=False)  # type: ignore # noqa: F722,F821

    # Validation configuration
    ocsfValidateSchema: RsVariableType(bool, "true|false", default=True, required=False)  # type: ignore # noqa: F722,F821
    ocsfSchemaVersion: RsVariableType(str, "1.6.0", default="1.6.0", required=False)  # type: ignore # noqa: F722,F821

    # Processing configuration
    ocsfBatchSize: RsVariableType(int, "100", default=100, required=False)  # type: ignore # noqa: F722,F821
    ocsfMaxWorkers: RsVariableType(int, "10", default=10, required=False)  # type: ignore # noqa: F722,F821

    # Mapping configuration
    ocsfMapToIssues: RsVariableType(bool, "true|false", default=True, required=False)  # type: ignore # noqa: F722,F821
    ocsfMapToAssets: RsVariableType(bool, "true|false", default=True, required=False)  # type: ignore # noqa: F722,F821
    ocsfMapToEvidence: RsVariableType(bool, "true|false", default=False, required=False)  # type: ignore # noqa: F722,F821

    # Field mapping configuration
    ocsfControlField: RsVariableType(str, "affectedControls", default="affectedControls", required=False)  # type: ignore # noqa: F722,F821
    ocsfAssetField: RsVariableType(str, "assetIdentifier", default="assetIdentifier", required=False)  # type: ignore # noqa: F722,F821

    # Event class filters (comma-separated list of OCSF event class IDs)
    ocsfEventClassFilter: RsVariableType(str, "2001,2003,2004", default=None, required=False)  # type: ignore # noqa: F722,F821

    # Source system identification
    ocsfSourceSystem: RsVariableType(str, "AWS Security Lake", default=None, required=False)  # type: ignore # noqa: F722,F821

    # Evidence configuration
    ocsfAttachRawEvents: RsVariableType(bool, "true|false", default=True, required=False)  # type: ignore # noqa: F722,F821
    ocsfEvidenceTitle: RsVariableType(str, "OCSF Security Events", default="OCSF Security Events", required=False)  # type: ignore # noqa: F722,F821

    @classmethod
    def get_event_class_filters(cls) -> list:
        """
        Parse and return event class filters as a list of integers

        :return: List of OCSF event class IDs to filter
        :rtype: list
        """
        if not cls.ocsfEventClassFilter:
            return []
        return [int(ec.strip()) for ec in cls.ocsfEventClassFilter.split(",") if ec.strip().isdigit()]
