#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to convert legacy parameter IDs to OSCAL format.

This script updates existing Parameter and ControlParameter records in RegScale
to use the new OSCAL parameter ID format (_odp.) instead of the legacy format (_prm_).
"""

import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

from rich.console import Console
from rich.progress import track
from rich.table import Table

from regscale.core.app.api import Api
from regscale.integrations.public.fedramp.parameter_utils import normalize_parameter_id, parse_oscal_param_id

logger = logging.getLogger("regscale")
console = Console()


def _should_skip_parameter(param_id: str, record_id: int) -> bool:
    """
    Check if a parameter should be skipped during migration.

    :param str param_id: Parameter ID to check
    :param int record_id: Record ID for logging
    :return: True if parameter should be skipped
    :rtype: bool
    """
    if not param_id or not record_id:
        return True

    parsed = parse_oscal_param_id(param_id)
    if not parsed:
        logger.debug("Skipping unparseable parameter ID: %s", param_id)
        return True

    if parsed["format"] == "oscal":
        return True

    return False


def _update_parameter_record(
    api: Api, record_id: int, param_data: dict, new_param_id: str, field_name: str, dry_run: bool
) -> Tuple[bool, Optional[str]]:
    """
    Update a parameter record with new OSCAL format ID.

    :param Api api: API client instance
    :param int record_id: Record ID to update
    :param dict param_data: Parameter data
    :param str new_param_id: New OSCAL format parameter ID
    :param str field_name: Field name to update (parameterId or name)
    :param bool dry_run: If True, only log what would change
    :return: Tuple of (success, error_message)
    :rtype: Tuple[bool, Optional[str]]
    """
    old_param_id = param_data.get(field_name, "")
    endpoint = "controlParameter" if field_name == "parameterId" else "parameter"

    if dry_run:
        logger.info("[DRY RUN] Would update %s #%s: %s -> %s", endpoint.title(), record_id, old_param_id, new_param_id)
        return True, None

    param_data[field_name] = new_param_id
    update_url = urljoin(api.config["domain"], f"/api/{endpoint}/{record_id}")
    update_response = api.put(update_url, json=param_data)

    if update_response.ok:
        logger.info("Updated %s #%s: %s -> %s", endpoint.title(), record_id, old_param_id, new_param_id)
        return True, None

    error_msg = (
        f"Failed to update {endpoint.title()} #{record_id}: {update_response.status_code} - {update_response.text}"
    )
    logger.error(error_msg)
    return False, error_msg


def migrate_control_parameters(tenant_id: int, dry_run: bool = True) -> Tuple[int, int, List[str]]:
    """
    Migrate ControlParameter records from legacy to OSCAL format.

    ControlParameters are the base parameter definitions attached to security controls
    in the catalog. These define what parameters exist for each control.

    :param int tenant_id: Tenant ID to migrate parameters for
    :param bool dry_run: If True, only report what would change without updating
    :return: Tuple of (updated_count, skipped_count, error_list)
    :rtype: Tuple[int, int, List[str]]
    """
    api = Api()
    updated_count = 0
    skipped_count = 0
    errors = []

    logger.info("Fetching ControlParameter records for tenant %s...", tenant_id)

    # Get all control parameters for the tenant
    url = urljoin(api.config["domain"], f"/api/controlParameter/tenant/{tenant_id}")
    response = api.get(url)

    if not response.ok:
        error_msg = f"Failed to fetch control parameters: {response.status_code} - {response.text}"
        logger.error(error_msg)
        return 0, 0, [error_msg]

    control_params = response.json()
    logger.info("Found %s ControlParameter records", len(control_params))

    for param in track(control_params, description="Migrating ControlParameters..."):
        param_id = param.get("parameterId", "")
        record_id = param.get("id")

        if _should_skip_parameter(param_id, record_id):
            skipped_count += 1
            continue

        # Convert to OSCAL format
        new_param_id = normalize_parameter_id(param_id)
        success, error_msg = _update_parameter_record(api, record_id, param, new_param_id, "parameterId", dry_run)

        if success:
            updated_count += 1
        else:
            errors.append(error_msg)

    return updated_count, skipped_count, errors


def _fetch_parameters_for_ssp(api: Api, ssp_id: int) -> Tuple[List[dict], Optional[str]]:
    """
    Fetch all parameters for a specific SSP.

    :param Api api: API client instance
    :param int ssp_id: Security Plan ID
    :return: Tuple of (parameters_list, error_message)
    :rtype: Tuple[List[dict], Optional[str]]
    """
    logger.info("Fetching Parameter records for SSP #%s...", ssp_id)

    # Get control implementations for this SSP
    impl_url = urljoin(api.config["domain"], f"/api/controlImplementation/getAllByPlan/{ssp_id}")
    impl_response = api.get(impl_url)

    if not impl_response.ok:
        error_msg = f"Failed to fetch control implementations: {impl_response.status_code}"
        logger.error(error_msg)
        return [], error_msg

    implementations = impl_response.json()
    logger.info("Found %s control implementations", len(implementations))

    # Get parameters for each implementation
    all_params = []
    for impl in implementations:
        impl_id = impl.get("id")
        param_url = urljoin(api.config["domain"], f"/api/parameter/implementation/{impl_id}")
        param_response = api.get(param_url)

        if param_response.ok:
            params = param_response.json()
            all_params.extend(params if isinstance(params, list) else [params])

    return all_params, None


def _fetch_all_parameters(api: Api) -> Tuple[List[dict], Optional[str]]:
    """
    Fetch all parameters from the system.

    :param Api api: API client instance
    :return: Tuple of (parameters_list, error_message)
    :rtype: Tuple[List[dict], Optional[str]]
    """
    logger.info("Fetching all Parameter records...")
    url = urljoin(api.config["domain"], "/api/parameter")
    response = api.get(url)

    if not response.ok:
        error_msg = f"Failed to fetch parameters: {response.status_code}"
        logger.error(error_msg)
        return [], error_msg

    return response.json(), None


def migrate_implementation_parameters(ssp_id: Optional[int] = None, dry_run: bool = True) -> Tuple[int, int, List[str]]:
    """
    Migrate Parameter records (implementation parameters) from legacy to OSCAL format.

    Parameters are the implementation-specific values for control parameters,
    attached to ControlImplementation records within a Security Plan.

    :param Optional[int] ssp_id: If provided, only migrate parameters for this SSP
    :param bool dry_run: If True, only report what would change without updating
    :return: Tuple of (updated_count, skipped_count, error_list)
    :rtype: Tuple[int, int, List[str]]
    """
    api = Api()
    updated_count = 0
    skipped_count = 0
    errors = []

    # Fetch parameters based on scope
    if ssp_id:
        all_params, error_msg = _fetch_parameters_for_ssp(api, ssp_id)
    else:
        all_params, error_msg = _fetch_all_parameters(api)

    if error_msg:
        return 0, 0, [error_msg]

    logger.info("Found %s Parameter records to process", len(all_params))

    for param in track(all_params, description="Migrating Parameters..."):
        param_name = param.get("name", "")
        record_id = param.get("id")

        if _should_skip_parameter(param_name, record_id):
            skipped_count += 1
            continue

        # Convert to OSCAL format
        new_param_name = normalize_parameter_id(param_name)
        success, error_msg = _update_parameter_record(api, record_id, param, new_param_name, "name", dry_run)

        if success:
            updated_count += 1
        else:
            errors.append(error_msg)

    return updated_count, skipped_count, errors


def preview_migration_impact(ssp_id: Optional[int] = None, tenant_id: Optional[int] = None) -> Dict:
    """
    Preview the impact of parameter migration without making changes.

    :param Optional[int] ssp_id: If provided, analyze parameters for this SSP
    :param Optional[int] tenant_id: If provided, analyze control parameters for this tenant
    :return: Dictionary with migration statistics
    :rtype: Dict
    """
    console.print("\n[bold cyan]Parameter Migration Impact Analysis[/bold cyan]\n")

    results = {"control_parameters": {}, "implementation_parameters": {}}

    if tenant_id:
        console.print(f"[yellow]Analyzing ControlParameters for Tenant #{tenant_id}...[/yellow]")
        cp_updated, cp_skipped, cp_errors = migrate_control_parameters(tenant_id=tenant_id, dry_run=True)
        results["control_parameters"] = {"updated": cp_updated, "skipped": cp_skipped, "errors": len(cp_errors)}

    if ssp_id or not tenant_id:
        context = f"SSP #{ssp_id}" if ssp_id else "all SSPs"
        console.print(f"[yellow]Analyzing Implementation Parameters for {context}...[/yellow]")
        p_updated, p_skipped, p_errors = migrate_implementation_parameters(ssp_id=ssp_id, dry_run=True)
        results["implementation_parameters"] = {"updated": p_updated, "skipped": p_skipped, "errors": len(p_errors)}

    # Display results table
    table = Table(title="Migration Impact Summary", show_header=True, header_style="bold magenta")
    table.add_column("Parameter Type", style="cyan")
    table.add_column("Will Update", justify="right", style="green")
    table.add_column("Will Skip", justify="right", style="yellow")
    table.add_column("Errors", justify="right", style="red")

    if results["control_parameters"]:
        cp = results["control_parameters"]
        table.add_row("ControlParameters", str(cp["updated"]), str(cp["skipped"]), str(cp["errors"]))

    if results["implementation_parameters"]:
        ip = results["implementation_parameters"]
        table.add_row("Implementation Parameters", str(ip["updated"]), str(ip["skipped"]), str(ip["errors"]))

    console.print(table)
    console.print("\n[bold green]This was a dry run. No changes were made.[/bold green]\n")

    return results


def run_migration(ssp_id: Optional[int] = None, tenant_id: Optional[int] = None, confirm: bool = False) -> None:
    """
    Execute the parameter migration from legacy to OSCAL format.

    :param Optional[int] ssp_id: If provided, only migrate parameters for this SSP
    :param Optional[int] tenant_id: If provided, migrate control parameters for this tenant
    :param bool confirm: If False, will prompt for confirmation before migrating
    :rtype: None
    """
    console.print("\n[bold red]WARNING: This will modify parameter IDs in your RegScale environment![/bold red]\n")

    if not confirm:
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            console.print("[yellow]Migration cancelled.[/yellow]")
            return

    console.print("\n[bold cyan]Starting Parameter Migration[/bold cyan]\n")

    total_updated = 0
    total_skipped = 0
    all_errors = []

    if tenant_id:
        console.print(f"[yellow]Migrating ControlParameters for Tenant #{tenant_id}...[/yellow]")
        cp_updated, cp_skipped, cp_errors = migrate_control_parameters(tenant_id=tenant_id, dry_run=False)
        total_updated += cp_updated
        total_skipped += cp_skipped
        all_errors.extend(cp_errors)
        console.print(f"[green]Updated {cp_updated} ControlParameters, skipped {cp_skipped}[/green]\n")

    if ssp_id or not tenant_id:
        context = f"SSP #{ssp_id}" if ssp_id else "all SSPs"
        console.print(f"[yellow]Migrating Implementation Parameters for {context}...[/yellow]")
        p_updated, p_skipped, p_errors = migrate_implementation_parameters(ssp_id=ssp_id, dry_run=False)
        total_updated += p_updated
        total_skipped += p_skipped
        all_errors.extend(p_errors)
        console.print(f"[green]Updated {p_updated} Parameters, skipped {p_skipped}[/green]\n")

    # Display final summary
    console.print("\n[bold cyan]Migration Complete[/bold cyan]\n")
    console.print(f"Total Updated: [green]{total_updated}[/green]")
    console.print(f"Total Skipped: [yellow]{total_skipped}[/yellow]")
    console.print(f"Total Errors: [red]{len(all_errors)}[/red]")

    if all_errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in all_errors[:10]:  # Show first 10 errors
            console.print(f"  - {error}")
        if len(all_errors) > 10:
            console.print(f"  ... and {len(all_errors) - 10} more errors")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate parameter IDs from legacy to OSCAL format")
    parser.add_argument("--ssp-id", type=int, help="Migrate parameters for a specific SSP ID")
    parser.add_argument("--tenant-id", type=int, help="Migrate control parameters for a specific tenant ID")
    parser.add_argument("--preview", action="store_true", help="Preview migration impact without making changes")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    if args.preview:
        preview_migration_impact(ssp_id=args.ssp_id, tenant_id=args.tenant_id)
    else:
        run_migration(ssp_id=args.ssp_id, tenant_id=args.tenant_id, confirm=args.confirm)
