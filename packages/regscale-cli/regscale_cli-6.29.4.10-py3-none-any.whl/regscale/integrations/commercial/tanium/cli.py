#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium CLI commands for RegScale.

This module provides Click commands for syncing Tanium data to RegScale.
"""

import logging
import sys

import click

from regscale.models import regscale_id

logger = logging.getLogger("regscale")

# Log message constants to avoid duplication
LOG_TARGET_REGSCALE_ID = "Target RegScale ID: %s"
LOG_ERROR_SYNCING_ASSETS = "Error syncing assets: %s"
LOG_ERROR_SYNCING_FINDINGS = "Error syncing findings: %s"
LOG_ERROR_DURING_SYNC = "Error during sync: %s"


@click.group()
def tanium():
    """
    Tanium Integration.

    Commands for syncing assets, vulnerabilities, and compliance findings
    from Tanium to RegScale.
    """
    pass


@tanium.command(name="test_connection")
def test_connection():
    """
    Test connection to Tanium API.

    Verifies that the configured Tanium credentials are valid
    and the API is accessible.
    """
    try:
        from regscale.integrations.commercial.tanium.tanium_api_client import (
            TaniumAPIClient,
            TaniumAPIException,
        )
        from regscale.integrations.commercial.tanium.variables import TaniumVariables

        logger.info("Testing connection to Tanium...")

        client = TaniumAPIClient(
            base_url=TaniumVariables.taniumUrl,
            api_token=TaniumVariables.taniumToken,
            verify_ssl=TaniumVariables.taniumVerifySsl,
            timeout=TaniumVariables.taniumTimeout,
            protocols=TaniumVariables.taniumProtocols,
        )

        if client.test_connection():
            server_info = client.get_server_info()
            version = server_info.get("version", "Unknown")
            logger.info("Successfully connected to Tanium")
            logger.info("Tanium Server Version: %s", version)
            click.echo("Successfully connected to Tanium (version: %s)" % version)
        else:
            logger.error("Failed to connect to Tanium")
            click.echo("Failed to connect to Tanium", err=True)
            sys.exit(1)

    except TaniumAPIException as e:
        logger.error("Tanium API error: %s", str(e))
        click.echo("Error connecting to Tanium: %s" % str(e), err=True)
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error testing Tanium connection: %s", str(e))
        click.echo("Error: %s" % str(e), err=True)
        sys.exit(1)


@tanium.command(name="sync_assets")
@regscale_id(help="RegScale will create and update assets as children of this record.")
def sync_assets(regscale_id: int):
    """
    Sync Tanium endpoints to RegScale assets.

    Fetches all endpoints from Tanium and synchronizes them as assets
    into the specified RegScale record.
    """
    try:
        from regscale.integrations.commercial.tanium.scanner import TaniumScanner
        from regscale.integrations.commercial.tanium.tanium_api_client import (
            TaniumAPIException,
        )

        logger.info("Starting Tanium asset synchronization...")
        logger.info(LOG_TARGET_REGSCALE_ID, regscale_id)

        scanner = TaniumScanner(plan_id=regscale_id)
        scanner.sync_assets(plan_id=regscale_id)

        logger.info("Tanium asset synchronization complete.")
        click.echo("Tanium asset synchronization complete.")

    except TaniumAPIException as e:
        logger.error("Tanium API error during asset sync: %s", str(e))
        click.echo(LOG_ERROR_SYNCING_ASSETS % str(e), err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(LOG_ERROR_SYNCING_ASSETS, str(e), exc_info=True)
        click.echo(LOG_ERROR_SYNCING_ASSETS % str(e), err=True)
        sys.exit(1)


@tanium.command(name="sync_findings")
@regscale_id(help="RegScale will create and update findings as children of this record.")
@click.option(
    "--include_compliance/--no-include_compliance",
    default=True,
    help="Include compliance findings from Tanium Comply (default: True).",
)
def sync_findings(regscale_id: int, include_compliance: bool):
    """
    Sync Tanium vulnerabilities and compliance findings to RegScale.

    Fetches vulnerabilities from Tanium and optionally compliance findings
    from Tanium Comply, then synchronizes them as findings into the
    specified RegScale record.
    """
    try:
        from regscale.integrations.commercial.tanium.scanner import TaniumScanner
        from regscale.integrations.commercial.tanium.tanium_api_client import (
            TaniumAPIException,
        )

        logger.info("Starting Tanium findings synchronization...")
        logger.info(LOG_TARGET_REGSCALE_ID, regscale_id)
        logger.info("Include compliance findings: %s", include_compliance)

        scanner = TaniumScanner(plan_id=regscale_id)
        scanner.sync_findings(plan_id=regscale_id, include_compliance=include_compliance)

        logger.info("Tanium findings synchronization complete.")
        click.echo("Tanium findings synchronization complete.")

    except TaniumAPIException as e:
        logger.error("Tanium API error during findings sync: %s", str(e))
        click.echo(LOG_ERROR_SYNCING_FINDINGS % str(e), err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(LOG_ERROR_SYNCING_FINDINGS, str(e), exc_info=True)
        click.echo(LOG_ERROR_SYNCING_FINDINGS % str(e), err=True)
        sys.exit(1)


@tanium.command(name="sync_all")
@regscale_id(help="RegScale will create and update assets and findings as children of this record.")
@click.option(
    "--include_compliance/--no-include_compliance",
    default=True,
    help="Include compliance findings from Tanium Comply (default: True).",
)
def sync_all(regscale_id: int, include_compliance: bool):
    """
    Sync all Tanium data to RegScale.

    Synchronizes both assets (endpoints) and findings (vulnerabilities
    and compliance findings) from Tanium to the specified RegScale record.
    """
    try:
        from regscale.integrations.commercial.tanium.scanner import TaniumScanner
        from regscale.integrations.commercial.tanium.tanium_api_client import (
            TaniumAPIException,
        )

        logger.info("Starting full Tanium synchronization...")
        logger.info(LOG_TARGET_REGSCALE_ID, regscale_id)

        scanner = TaniumScanner(plan_id=regscale_id)

        # Sync assets first
        logger.info("Syncing assets...")
        scanner.sync_assets(plan_id=regscale_id)

        # Then sync findings
        logger.info("Syncing findings...")
        scanner.sync_findings(plan_id=regscale_id, include_compliance=include_compliance)

        logger.info("Full Tanium synchronization complete.")
        click.echo("Full Tanium synchronization complete.")

    except TaniumAPIException as e:
        logger.error("Tanium API error during sync: %s", str(e))
        click.echo(LOG_ERROR_DURING_SYNC % str(e), err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(LOG_ERROR_DURING_SYNC, str(e), exc_info=True)
        click.echo(LOG_ERROR_DURING_SYNC % str(e), err=True)
        sys.exit(1)
