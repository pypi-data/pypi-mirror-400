#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FedRAMP CLI commands module.

This module provides reorganized CLI commands for FedRAMP integrations,
organized into logical subgroups:
- fedramp ssp: SSP import/export commands
- fedramp ciscrm: CIS/CRM workbook commands
- fedramp poam: POAM import/export commands
- fedramp inventory: Inventory management commands

Backward compatibility aliases are provided for legacy command names.
"""

import glob
import logging
from datetime import date, datetime
from typing import Literal, Optional

import click
from dateutil.relativedelta import relativedelta

from regscale.core.app.utils.regscale_utils import check_module_id, error_and_exit
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models import Asset

logger = logging.getLogger("regscale")


# =============================================================================
# Main FedRAMP Group
# =============================================================================


@click.group()
def fedramp():
    """FedRAMP integration commands for SSP, CIS/CRM, POAM, and inventory management."""


# =============================================================================
# SSP Subgroup
# =============================================================================


@fedramp.group(name="ssp")
def ssp():
    """SSP (System Security Plan) import and export commands."""


@ssp.command(name="import-docx", context_settings={"show_default": True})
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the full file path of the FedRAMP (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP document.",
)
@click.option(
    "--base_fedramp_profile",
    "-pn",
    type=click.STRING,
    required=False,
    help="Enter the name of the RegScale FedRAMP profile to use.",
    default="FedRAMP - High",
)
@click.option(
    "--base_fedramp_profile_id",
    "-p",
    type=click.INT,
    required=False,
    help="Enter the ID of the RegScale FedRAMP profile to use.",
)
@click.option(
    "--appendix_a_file_path",
    "-a",
    type=click.Path(exists=True),
    required=False,
    prompt="Enter the full file path of the FedRAMP Appendix A (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP Appendix A document, used during Rev5 version import.",
)
@click.option(
    "--save_data",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to save the data as a JSON file.",
)
@click.option(
    "--add_missing",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to create missing controls from profile in the SSP.",
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
def ssp_import_docx(
    file_path: click.Path,
    base_fedramp_profile: click.STRING,
    base_fedramp_profile_id: Optional[click.STRING],
    save_data: click.BOOL,
    add_missing: click.BOOL,
    appendix_a_file_path: click.Path,
    version: Literal["rev4", "rev5", "4", "5"],
):
    """
    Import a FedRAMP SSP from a DOCX file into RegScale.

    Supports both Rev4 and Rev5 FedRAMP templates.
    """
    if "4" in version:
        from regscale.integrations.public.fedramp.fedramp_docx import process_fedramp_docx

        logger.info("Processing FedRAMP Rev4 document %s.", file_path)
        process_fedramp_docx(file_path, base_fedramp_profile, base_fedramp_profile_id, save_data, add_missing)
    elif "5" in version:
        from regscale.integrations.public.fedramp.fedramp_five import process_fedramp_docx_v5

        if not base_fedramp_profile_id:
            from regscale.integrations.public.fedramp.fedramp_common import find_profile_by_name

            profile = find_profile_by_name(base_fedramp_profile) or {}
            base_fedramp_profile_id = profile.get("id")
            if not base_fedramp_profile_id:
                error_and_exit(
                    f"Unable to find profile with name {base_fedramp_profile}. "
                    "Please provide a profile ID by using the -p flag."
                )

        process_fedramp_docx_v5(file_path, base_fedramp_profile_id, save_data, add_missing, appendix_a_file_path)


@ssp.command(name="import-oscal")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file name of the FedRAMP JSON document to process.",
    help="RegScale will process and load the FedRAMP document.",
)
@click.option(
    "--submission_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
    required=True,
    prompt="Enter the submission date of this FedRAMP document.",
    help=f"Submission date, default is today: {date.today()}.",
)
@click.option(
    "--expiration_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str((datetime.now() + relativedelta(years=3)).date()),
    required=True,
    prompt="Enter the expiration date of this FedRAMP document.",
    help=f"Expiration date, default is {str((datetime.now() + relativedelta(years=3)).date())}.",
)
def ssp_import_oscal(file_path, submission_date, expiration_date):
    """
    [BETA] Import a FedRAMP OSCAL SSP JSON file into RegScale.
    """
    from regscale.integrations.public.fedramp.fedramp_common import process_fedramp_oscal_ssp

    if not expiration_date:
        today_dt = date.today()
        expiration_date = date(today_dt.year + 3, today_dt.month, today_dt.day)

    process_fedramp_oscal_ssp(file_path, submission_date, expiration_date)


@ssp.command(name="import-xml")
@click.option(
    "--file-path",
    "-f",
    type=click.Path(exists=True),
    help="File to upload to RegScale.",
    required=True,
)
@click.option(
    "--catalogue_id",
    "-c",
    type=click.INT,
    help="The RegScale ID # of the catalogue to use for controls in the profile.",
    required=True,
)
def ssp_import_xml(file_path: click.Path, catalogue_id: click.INT):
    """
    Import a FedRAMP Rev4/Rev5 SSP XML file into RegScale.
    """
    from collections import deque

    from regscale.integrations.public.fedramp.import_fedramp_r4_ssp import parse_and_load_xml_rev4
    from regscale.integrations.public.fedramp.ssp_logger import SSPLogger

    ssp_logger = SSPLogger()
    ssp_logger.info(event_msg="Importing FedRAMP SSP XML into RegScale")
    parse_generator = parse_and_load_xml_rev4(None, str(file_path), catalogue_id)
    deque(parse_generator, maxlen=1)


@ssp.command(name="import-appendix", context_settings={"show_default": True})
@click.option(
    "--appendix_a_file_path",
    "-a",
    type=click.Path(exists=True),
    required=False,
    prompt="Enter the full file path of the FedRAMP Appendix A (.docx) document to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP Appendix A document.",
)
@click.option(
    "--base_fedramp_profile_id",
    "-p",
    type=click.INT,
    required=True,
    help="The RegScale FedRAMP profile ID to use.",
)
@click.option(
    "--add_missing",
    type=click.BOOL,
    default=False,
    required=False,
    help="Whether to create missing controls from profile in the SSP.",
)
@click.option("--regscale_id", "-i", help="Regscale id to push inventory to in RegScale.", required=True)
def ssp_import_appendix(
    appendix_a_file_path: str,
    base_fedramp_profile_id: int,
    add_missing: click.BOOL,
    regscale_id: int,
):
    """
    Import a FedRAMP Appendix A DOCX file into an existing RegScale SSP.
    """
    from regscale.integrations.public.fedramp.fedramp_five import load_appendix_a as _load_appendix_a

    _load_appendix_a(
        appendix_a_file_name=appendix_a_file_path,
        parent_id=regscale_id,
        profile_id=base_fedramp_profile_id,
        add_missing=add_missing,
    )


# =============================================================================
# CIS/CRM Subgroup
# =============================================================================


@fedramp.group(name="ciscrm")
def ciscrm():
    """CIS/CRM (Customer Implementation Summary / Customer Responsibility Matrix) commands."""


@ciscrm.command(name="import", context_settings={"show_default": True})
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="The file path to the FedRAMP CIS CRM .xlsx file.",
    prompt="FedRAMP CIS CRM .xlsx file location",
    required=True,
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
@click.option(
    "--cis_sheet_name",
    "-cis",
    type=click.STRING,
    help="CIS sheet name in the FedRAMP CIS CRM .xlsx to parse.",
    prompt="CIS Sheet Name",
    default="CIS Worksheet",
    required=True,
)
@click.option(
    "--profile_id",
    "-p",
    type=click.INT,
    help=(
        "The ID number from RegScale of the Profile. (This will generate the control implementations "
        "for a new Security Plan)"
    ),
    prompt="Enter RegScale Profile ID",
    required=True,
)
@click.option(
    "--crm_sheet_name",
    "-crm",
    type=click.STRING,
    help="CRM sheet name in the FedRAMP CIS CRM .xlsx to parse.",
    required=False,
)
@click.option(
    "--leveraged_auth_id",
    "-l",
    type=click.INT,
    help="RegScale Leveraged Authorization ID #, if none provided, one will be created.",
    required=False,
    default=0,
)
def ciscrm_import(
    file_path: click.Path,
    version: str,
    cis_sheet_name: str,
    crm_sheet_name: Optional[click.STRING],
    profile_id: int,
    leveraged_auth_id: int = 0,
):
    """
    Import a FedRAMP CIS/CRM workbook into a new RegScale Security Plan.

    Supports both Rev4 and Rev5 FedRAMP CIS/CRM workbook formats.
    """
    from regscale.integrations.public.fedramp.fedramp_cis_crm import parse_and_import_ciscrm

    version_literal: Literal["rev4", "rev5", "4", "5"] = version  # type: ignore
    parse_and_import_ciscrm(
        file_path=file_path,
        version=version_literal,
        cis_sheet_name=cis_sheet_name,
        crm_sheet_name=crm_sheet_name,
        profile_id=profile_id,
        leveraged_auth_id=leveraged_auth_id,
    )


# =============================================================================
# POAM Subgroup
# =============================================================================


@fedramp.group(name="poam")
def poam():
    """POAM (Plan of Action and Milestones) import and export commands."""


@poam.command(name="export", context_settings={"show_default": True})
@click.option(
    "--ssp_id",
    "-s",
    type=click.STRING,
    required=True,
    prompt="Enter the SSP ID to export POAMs from",
    help="The RegScale SSP ID to export POAMs from",
)
@click.option(
    "--output_file",
    "-o",
    type=click.STRING,
    required=True,
    prompt="Enter the output file path (xlsx)",
    help="The output file path for the POAM export (xlsx format)",
)
@click.option(
    "--template_path",
    "-t",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=False,
    help="Path to the FedRAMP POAM template Excel file (defaults to ./templates/FedRAMP-POAM-Template.xlsx)",
)
@click.option(
    "--point_of_contact",
    "-p",
    type=click.STRING,
    required=False,
    default="",
    help="Point of Contact name for POAMs (defaults to empty string)",
)
def poam_export(ssp_id: str, output_file: str, template_path: Optional[click.Path], point_of_contact: str):
    """
    Export FedRAMP Rev5 POAM to an Excel file.

    Includes dynamic POAM ID generation, KEV date determination,
    deviation status mapping, and Excel formatting for Rev5 template.
    """
    from pathlib import Path

    from regscale.integrations.public.fedramp.poam_export_v5 import export_poam_v5 as export_func

    logger.info("Exporting FedRAMP Rev 5 POAM for SSP %s", ssp_id)

    template = Path(template_path) if template_path else None
    export_func(ssp_id=ssp_id, output_file=output_file, template_path=template, point_of_contact=point_of_contact)


@poam.command(name="import", context_settings={"show_default": True})
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file path containing FedRAMP (.xlsx) POAM workbook to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP POAMs as RegScale issues.",
)
@regscale_id()
@regscale_module()
@click.option(
    "--poam_id_column",
    "-pc",
    type=click.STRING,
    help="The column name containing the POAM ID.",
    required=False,
    default="POAM ID",
)
@click.option(
    "--resolve_empty_status_date",
    "-rs",
    type=click.Choice(["CURRENT_DATE", "USE_NEIGHBOR"], case_sensitive=False),
    default="CURRENT_DATE",
    help="Choose between 'CURRENT_DATE' (default) or 'USE_NEIGHBOR'.",
)
def poam_import(
    file_path: click.Path, regscale_id: int, regscale_module: str, poam_id_column: str, resolve_empty_status_date: str
) -> None:
    """
    Import a FedRAMP POAM workbook into RegScale issues.

    Supports both POA&M Items and Configuration Findings tabs.
    """
    import warnings

    from regscale.integrations.public.fedramp.poam.scanner import FedrampPoamIntegration

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    if not check_module_id(parent_id=regscale_id, parent_module=regscale_module):
        error_and_exit(f"RegScale ID {regscale_id} is not a valid member of {regscale_module}.")

    existing_assets = Asset.get_all_by_parent(parent_id=regscale_id, parent_module=regscale_module)
    if not existing_assets:
        error_msg = (
            f"No assets found in {regscale_module} #{regscale_id}. "
            "Please import inventory first using 'regscale fedramp inventory import' "
            "before importing POAMs."
        )
        error_and_exit(error_msg)

    integration = FedrampPoamIntegration(plan_id=regscale_id, file_path=str(file_path))
    integration.poam_id_header = poam_id_column
    integration.file_path = str(file_path)

    integration.sync_assets(
        plan_id=regscale_id,
        file_path=str(file_path),
        poam_sheets=integration.poam_sheets,
        workbook=integration.workbook,
        validators=integration.validators,
    )

    integration.sync_findings(
        plan_id=regscale_id,
        file_path=str(file_path),
        poam_sheets=integration.poam_sheets,
        workbook=integration.workbook,
        validators=integration.validators,
        resolve_empty_status_date=resolve_empty_status_date,
        close_outdated_findings=False,
    )

    if integration.workbook:
        integration.workbook.close()


# =============================================================================
# Inventory Subgroup
# =============================================================================


@fedramp.group(name="inventory")
def inventory():
    """Inventory workbook import commands."""


@inventory.command(name="import", context_settings={"show_default": True})
@click.option(
    "--path",
    "-f",
    type=click.Path(exists=True, dir_okay=True),
    help="The File OR Folder Path to the inventory .xlsx files.",
    prompt="Inventory .xlsx folder location",
    required=True,
)
@click.option(
    "--sheet_name",
    "-s",
    type=click.STRING,
    help="Sheet name in the inventory .xlsx file to parse.",
    default="Inventory",
    required=False,
)
@click.option(
    "--regscale_id",
    "-i",
    type=click.INT,
    help="RegScale Record ID to update.",
    prompt="RegScale Record ID",
    required=True,
)
@click.option(
    "--regscale_module",
    "-m",
    type=click.STRING,
    help="RegScale Module for the provided ID.",
    prompt="RegScale Record Module",
    required=True,
)
@click.option(
    "--version",
    "-rev",
    type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False),
    help="FedRAMP revision version.",
    prompt="Rev4 or Rev5",
    required=True,
)
def inventory_import(
    path: click.Path,
    sheet_name: str,
    regscale_id: int,
    regscale_module: str,
    version: Literal["rev4", "rev5", "4", "5"],
):
    """
    Import a FedRAMP inventory workbook into RegScale.

    Supports both single files and directories containing multiple .xlsx files.
    """
    import os
    from pathlib import Path

    from regscale.integrations.public.fedramp.import_workbook import upload

    link_path = Path(path)
    if link_path.is_dir():
        files = glob.glob(str(link_path) + os.sep + "*.xlsx")
        if not files:
            logger.warning("No files found in the folder.")
            return
        for file in files:
            try:
                upload(
                    inventory=file,
                    sheet_name=sheet_name,
                    record_id=regscale_id,
                    module=regscale_module,
                    version=version,
                )
            except Exception as e:
                logger.error("Failed to parse inventory from %s: %s", file, e)
                continue
    elif link_path.is_file():
        try:
            upload(
                inventory=str(link_path),
                sheet_name=sheet_name,
                record_id=regscale_id,
                module=regscale_module,
                version=version,
            )
        except Exception as e:
            logger.error("Failed to parse inventory from %s: %s", link_path, e)


# =============================================================================
# DRF Command (standalone)
# =============================================================================


@fedramp.command(name="import-drf")
@click.option(
    "--file_path",
    "-f",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=True,
    prompt="Enter the file path containing FedRAMP (.xlsx) DRF workbook to ingest to RegScale.",
    help="RegScale will process and load the FedRAMP DRF as RegScale issues.",
)
@regscale_id()
@regscale_module()
def import_drf(file_path: click.Path, regscale_id: int, regscale_module: str) -> None:
    """
    Import a FedRAMP DRF (Deviation Request Form) document to RegScale issues.
    """
    import warnings

    from regscale.models.integration_models.drf import DRF

    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    if not check_module_id(parent_id=regscale_id, parent_module=regscale_module):
        error_and_exit(f"RegScale ID {regscale_id} is not a valid member of {regscale_module}.")
    DRF(file_path=file_path, module_id=regscale_id, module=regscale_module)


# =============================================================================
# Backward Compatibility Aliases (Hidden)
# =============================================================================


@fedramp.command(name="load_fedramp_docx", hidden=True, context_settings={"show_default": True})
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=False, file_okay=True), required=True)
@click.option("--base_fedramp_profile", "-pn", type=click.STRING, required=False, default="FedRAMP - High")
@click.option("--base_fedramp_profile_id", "-p", type=click.INT, required=False)
@click.option("--appendix_a_file_path", "-a", type=click.Path(exists=True), required=False)
@click.option("--save_data", type=click.BOOL, default=False, required=False)
@click.option("--add_missing", type=click.BOOL, default=False, required=False)
@click.option("--version", "-rev", type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False), required=True)
@click.pass_context
def load_fedramp_docx_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp ssp import-docx' instead."""
    logger.warning("DEPRECATED: 'load_fedramp_docx' is deprecated. Use 'regscale fedramp ssp import-docx' instead.")
    ctx.invoke(ssp_import_docx, **kwargs)


@fedramp.command(name="load_fedramp_oscal", hidden=True)
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=False, file_okay=True), required=True)
@click.option("--submission_date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today()), required=True)
@click.option(
    "--expiration_date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str((datetime.now() + relativedelta(years=3)).date()),
    required=True,
)
@click.pass_context
def load_fedramp_oscal_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp ssp import-oscal' instead."""
    logger.warning("DEPRECATED: 'load_fedramp_oscal' is deprecated. Use 'regscale fedramp ssp import-oscal' instead.")
    ctx.invoke(ssp_import_oscal, **kwargs)


@fedramp.command(name="import_fedramp_ssp_xml", hidden=True)
@click.option("--file-path", "-f", type=click.Path(exists=True), required=True)
@click.option("--catalogue_id", "-c", type=click.INT, required=True)
@click.pass_context
def import_fedramp_ssp_xml_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp ssp import-xml' instead."""
    logger.warning("DEPRECATED: 'import_fedramp_ssp_xml' is deprecated. Use 'regscale fedramp ssp import-xml' instead.")
    ctx.invoke(ssp_import_xml, **kwargs)


@fedramp.command(name="load_fedramp_appendix_a", hidden=True, context_settings={"show_default": True})
@click.option("--appendix_a_file_path", "-a", type=click.Path(exists=True), required=False)
@click.option("--base_fedramp_profile_id", "-p", type=click.INT, required=True)
@click.option("--add_missing", type=click.BOOL, default=False, required=False)
@click.option("--regscale_id", "-i", required=True)
@click.pass_context
def load_fedramp_appendix_a_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp ssp import-appendix' instead."""
    logger.warning(
        "DEPRECATED: 'load_fedramp_appendix_a' is deprecated. Use 'regscale fedramp ssp import-appendix' instead."
    )
    ctx.invoke(ssp_import_appendix, **kwargs)


@fedramp.command(name="import-cis-crm", hidden=True, context_settings={"show_default": True})
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=False, file_okay=True), required=True)
@click.option("--version", "-rev", type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False), required=True)
@click.option("--cis_sheet_name", "-cis", type=click.STRING, default="CIS Worksheet", required=True)
@click.option("--profile_id", "-p", type=click.INT, required=True)
@click.option("--crm_sheet_name", "-crm", type=click.STRING, required=False)
@click.option("--leveraged_auth_id", "-l", type=click.INT, required=False, default=0)
@click.pass_context
def import_ciscrm_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp ciscrm import' instead."""
    logger.warning("DEPRECATED: 'import-cis-crm' is deprecated. Use 'regscale fedramp ciscrm import' instead.")
    ctx.invoke(ciscrm_import, **kwargs)


@fedramp.command(name="export_poam_v5", hidden=True, context_settings={"show_default": True})
@click.option("--ssp_id", "-s", type=click.STRING, required=True)
@click.option("--output_file", "-o", type=click.STRING, required=True)
@click.option("--template_path", "-t", type=click.Path(exists=True, dir_okay=False, file_okay=True), required=False)
@click.option("--point_of_contact", "-p", type=click.STRING, required=False, default="")
@click.pass_context
def export_poam_v5_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp poam export' instead."""
    logger.warning("DEPRECATED: 'export_poam_v5' is deprecated. Use 'regscale fedramp poam export' instead.")
    ctx.invoke(poam_export, **kwargs)


@fedramp.command(name="import-poam", hidden=True, context_settings={"show_default": True})
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=False, file_okay=True), required=True)
@regscale_id()
@regscale_module()
@click.option("--poam_id_column", "-pc", type=click.STRING, required=False, default="POAM ID")
@click.option(
    "--resolve_empty_status_date",
    "-rs",
    type=click.Choice(["CURRENT_DATE", "USE_NEIGHBOR"], case_sensitive=False),
    default="CURRENT_DATE",
)
@click.pass_context
def import_poam_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp poam import' instead."""
    logger.warning("DEPRECATED: 'import-poam' is deprecated. Use 'regscale fedramp poam import' instead.")
    ctx.invoke(poam_import, **kwargs)


@fedramp.command(name="import_fedramp_inventory", hidden=True, context_settings={"show_default": True})
@click.option("--path", "-f", type=click.Path(exists=True, dir_okay=True), required=True)
@click.option("--sheet_name", "-s", type=click.STRING, default="Inventory", required=False)
@click.option("--regscale_id", "-i", type=click.INT, required=True)
@click.option("--regscale_module", "-m", type=click.STRING, required=True)
@click.option("--version", "-rev", type=click.Choice(["rev4", "rev5", "4", "5"], case_sensitive=False), required=True)
@click.pass_context
def import_fedramp_inventory_compat(ctx, **kwargs):
    """DEPRECATED: Use 'regscale fedramp inventory import' instead."""
    logger.warning(
        "DEPRECATED: 'import_fedramp_inventory' is deprecated. Use 'regscale fedramp inventory import' instead."
    )
    ctx.invoke(inventory_import, **kwargs)
