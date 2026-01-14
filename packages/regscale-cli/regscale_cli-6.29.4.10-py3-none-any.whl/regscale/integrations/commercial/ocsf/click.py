#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands for OCSF integration"""

import logging

import click

from regscale.integrations.commercial.ocsf.scanner import OCSFIntegration
from regscale.integrations.commercial.ocsf.variables import OCSFVariables
from regscale.models.app_models.click import regscale_id, regscale_module

logger = logging.getLogger("regscale")


@click.group()
def ocsf():
    """OCSF (Open Cybersecurity Schema Framework) integration commands"""
    pass


@ocsf.command(name="ingest")
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to OCSF events file (JSON or JSONL format)",
)
@regscale_id(help="RegScale parent ID (typically SSP ID) to associate findings with")
@regscale_module(required=False, default="securityplans")
@click.option(
    "--create-issues/--no-create-issues",
    default=True,
    help="Create RegScale Issues from OCSF findings (default: enabled)",
)
@click.option(
    "--create-assets/--no-create-assets",
    default=True,
    help="Create RegScale Assets from OCSF resources (default: enabled)",
)
@click.option(
    "--validate-schema/--no-validate-schema",
    default=True,
    help="Validate events against OCSF schema (default: enabled)",
)
@click.option(
    "--schema-version",
    "-v",
    default="1.6.0",
    help="OCSF schema version to validate against (default: 1.6.0)",
)
def ingest(
    file: str,
    regscale_id: int,
    regscale_module: str,
    create_issues: bool,
    create_assets: bool,
    validate_schema: bool,
    schema_version: str,
):
    """
    Ingest OCSF events from a file and create RegScale entities.

    Reads OCSF-formatted security events from JSON or JSONL files and creates:
    - RegScale Issues from compliance/vulnerability/detection findings
    - RegScale Assets from affected resources

    The command maps OCSF findings to Issues using:
    - affectedControls field for compliance control mappings
    - assetIdentifier field for affected resource identifiers
    """
    logger.info("Starting OCSF ingestion from file: %s", file)

    scanner = OCSFIntegration(
        plan_id=regscale_id,
        parent_module=regscale_module,
        validate_schema=validate_schema,
        schema_version=schema_version,
    )

    try:
        result = scanner.ingest_file(file, create_issues=create_issues, create_assets=create_assets)

        issues_count = len(result.get("issues", []))
        assets_count = len(result.get("assets", []))

        logger.info("OCSF Ingestion Complete:")
        logger.info("  Created/Updated Issues: %d", issues_count)
        logger.info("  Created/Updated Assets: %d", assets_count)

        if issues_count > 0:
            logger.info("Issues have been linked to %s #%d", regscale_module, regscale_id)
            logger.info("  - Compliance controls mapped to affectedControls field")
            logger.info("  - Affected resources mapped to assetIdentifier field")

    except Exception as e:
        logger.error("OCSF ingestion failed: %s", str(e), exc_info=True)
        raise click.Abort()


@ocsf.command(name="validate")
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to OCSF events file to validate",
)
@click.option(
    "--schema-version",
    "-v",
    default="1.6.0",
    help="OCSF schema version to validate against (default: 1.6.0)",
)
def validate(file: str, schema_version: str):
    """
    Validate OCSF events file without creating RegScale entities.

    Performs validation checks on OCSF-formatted events including:
    - JSON/JSONL syntax validation
    - Required OCSF base fields verification
    - Event class identification
    - Resource and finding structure validation
    """
    logger.info("Validating OCSF events file: %s", file)

    scanner = OCSFIntegration(plan_id=0, validate_schema=True, schema_version=schema_version)

    try:
        result = scanner.validate_file(file)

        if result.get("valid"):
            logger.info("Validation Successful!")
            logger.info("  Total Events: %d", result.get("total_events", 0))
            logger.info("  Valid Events: %d", result.get("parsed_events", 0))
            logger.info("  Invalid Events: %d", result.get("invalid_events", 0))

            event_classes = result.get("event_classes", {})
            if event_classes:
                logger.info("Event Classes Found:")
                for class_uid, count in event_classes.items():
                    class_name = _get_event_class_name(class_uid)
                    logger.info("  - %s (%s): %d events", class_name, class_uid, count)
        else:
            logger.error("Validation Failed!")
            logger.error("  Error: %s", result.get("error", "Unknown error"))
            raise click.Abort()

    except Exception as e:
        logger.error("OCSF validation failed: %s", str(e), exc_info=True)
        raise click.Abort()


@ocsf.command(name="convert")
@click.option(
    "--file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to source file to convert",
)
@click.option(
    "--source-format",
    "-s",
    required=True,
    type=click.Choice(["json", "csv"], case_sensitive=False),
    help="Source file format",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Path to output OCSF-formatted file",
)
@click.option(
    "--output-format",
    "-of",
    default="json",
    type=click.Choice(["json", "jsonl"], case_sensitive=False),
    help="Output format (default: json)",
)
def convert(file: str, source_format: str, output: str, output_format: str):
    """
    Convert security data to OCSF format.

    NOTE: This is a placeholder command for future implementation.
    Full conversion requires understanding of source data schemas.
    """
    logger.info("OCSF Conversion Tool")
    logger.info("  Source: %s (%s)", file, source_format)
    logger.info("  Output: %s (%s)", output, output_format)
    logger.info("Note: Conversion functionality coming soon.")
    logger.info("For now, please ensure your input data is already in OCSF format.")


@ocsf.command(name="evidence-attach")
@click.option(
    "--log-file",
    "-f",
    required=True,
    type=click.Path(exists=True),
    help="Path to OCSF log file to attach as evidence",
)
@click.option(
    "--evidence-id",
    "-e",
    required=True,
    type=int,
    help="RegScale Evidence ID to attach file to",
)
@click.option(
    "--title",
    "-t",
    default="OCSF Security Events",
    help="Title for the evidence attachment (default: 'OCSF Security Events')",
)
def evidence_attach(log_file: str, evidence_id: int, title: str):
    """
    Attach OCSF log file as evidence to a RegScale Evidence record.

    This provides proof of log delivery and security event tracking
    for compliance purposes (FedRAMP, NIST, etc.).
    """
    from regscale.models import File

    logger.info("Attaching OCSF log file %s to Evidence #%d", log_file, evidence_id)

    try:
        # Upload file as evidence
        File.upload_file_to_parent(file_path=log_file, parent_id=evidence_id, parent_module="evidence", title=title)

        logger.info("OCSF Log File Attached Successfully")
        logger.info("  Evidence ID: %d", evidence_id)
        logger.info("  File: %s", log_file)
        logger.info("  Title: %s", title)
        logger.info("This attachment provides audit evidence of security event logs.")

    except Exception as e:
        logger.error("Failed to attach evidence: %s", str(e), exc_info=True)
        raise click.Abort()


def _get_event_class_name(class_uid: int) -> str:
    """
    Get human-readable event class name from class UID

    :param int class_uid: OCSF class UID
    :return: Event class name
    :rtype: str
    """
    class_names = {
        2001: "Vulnerability Finding",
        2003: "Compliance Finding",
        2004: "Detection Finding",
        3002: "Authentication",
        4001: "Network Activity",
        4002: "HTTP Activity",
        4003: "DNS Activity",
        4007: "SSH Activity",
        1001: "File Activity",
        1007: "Process Activity",
    }

    return class_names.get(class_uid, f"Class {class_uid}")
