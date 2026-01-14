#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from pathlib import Path
from typing import List, Optional
from rich.progress import track
from regscale.models.regscale_models import SecurityPlan
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.integrations.public.csam.csam_common import (
    retrieve_from_csam,
    retrieve_ssps_custom_form_map,
    retrieve_custom_form_ssps_map,
    CSAM_FIELD_NAME,
    SSP_BASIC_TAB,
)

logger = logging.getLogger("regscale")


def import_csam_parent_child(import_ids: Optional[List[int]] = None):
    """
    Import the Fisma Rollups from CSAM
    Into RegScale
    """
    # Get existing ssps by CSAM Id
    logger.info("Retrieving SSPs from RegScale...")
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )
    csam_map = retrieve_custom_form_ssps_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    all_results = []

    # Parse each SSP
    for index in track(
        range(len(plans)),
        description=f"Checking {len(plans)} Fisma Rollups...",
    ):
        regscale_ssp_id = plans[index]
        results = []
        system_id = ssp_map.get(regscale_ssp_id)

        results = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/FISMArollup",
        )

        if not results:
            logger.debug(f"No FISMA Rollup found for CSAM id: {system_id}, RegScale id: {regscale_ssp_id}")
            continue

        all_results.extend(results)
    process_parent_child(results=all_results, csam_map=csam_map)


def process_parent_child(results: list, csam_map: dict):
    """
    Parse the results from CSAM and create parent/child relationships

    :param results: list of CSAM Fisma Rollup Records
    :param csam_map: map of CSAM to RegScale Id
    """

    for index in track(range(len(results)), description=f"Loading {len(results)} FISMA Rollups..."):
        result = results[index]

        parent_ssp = csam_map.get(str(result.get("parentSystemID")))
        child_ssp = csam_map.get(str(result.get("childSystemID")))
        if not child_ssp:
            continue
        child_obj = SecurityPlan.get_object(object_id=child_ssp)
        if child_obj:
            child_obj.parentId = parent_ssp
            child_obj.parentModule = "securityplans"
            child_obj.save()
