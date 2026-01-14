#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from pathlib import Path
from typing import List, Optional
from rich.progress import track
from regscale.models.regscale_models import ClassificationType, ClassifiedRecord
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.core.app.utils.app_utils import save_to_json
from regscale.integrations.public.csam.csam_common import (
    retrieve_from_csam,
    retrieve_ssps_custom_form_map,
    CSAM_FIELD_NAME,
    SSP_BASIC_TAB,
)

logger = logging.getLogger("regscale")
missing_info_types = []


def import_csam_info_types(import_ids: Optional[List[int]] = None):
    """
    Import the Information Types from CSAM
    Into RegScale
    """
    # Get existing ssps by CSAM Id
    logger.info("Retrieving Inventory map from RegScale...")
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    logger.info("Building map of RegScale Info Types...")
    info_type_map = ClassificationType.get_infotypes_map() or {}

    for index in track(
        range(len(plans)),
        description=f"Importing {len(plans)} info_types...",
    ):
        regscale_ssp_id = plans[index]
        results = []
        system_id = ssp_map.get(regscale_ssp_id)

        results = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/infotypes",
        )

        if not results:
            logger.debug(f"No info types found for CSAM id: {system_id}, RegScale id: {regscale_ssp_id}")
            continue

        update_info_types(results=results, classification_map=info_type_map, ssp=regscale_ssp_id)

    # Handle missing Info Types
    handle_missing(missing=missing_info_types)


def update_info_types(results: list, classification_map: dict, ssp: int):
    """
    For each set of retrieved information types from CSAM
    Create a ClassifiedRecords entry for the given SSP

    :param results: list of info types from CSAM
    :param ssp: id of RegScale SSP
    """
    # Get the existing classifiedRecords for the SSP
    existing = ClassifiedRecord.get_all_by_parent(parent_id=ssp, parent_module="securityplans")
    existing_map = {x.classificationTypeId for x in existing}

    for info_type in results:
        # Find the ClassificationType record in the map
        csam_info_type = f"{info_type.get('businessArea')}: {info_type.get('dataType')}"
        csam_info_type = csam_info_type.strip()
        info_type_id = classification_map.get(csam_info_type)
        # If no match, continue
        if not info_type_id:
            missing_info_types.append(info_type)
            continue

        # If already exists, continue
        if info_type_id in existing_map:
            continue

        ClassifiedRecord(
            parentRecordId=ssp,
            parentModule="securityplans",
            classificationTypeId=info_type_id,
            adjustedConfidentiality=info_type.get("confidentiality"),
            adjustedAvailability=info_type.get("availability"),
            adjustedIntegrity=info_type.get("integrity"),
        ).create()


def handle_missing(missing: list):
    """
    Save missing info types in format for
    upload to RegScale

    :param missing: list of missing info types
    """
    # Format missing list into infotype object
    missing_info_types = []
    unique_missing = {}
    for info in missing:
        title = f"{info.get('businessArea')}: {info.get('dataType')}"
        title = title.strip()
        new_type = {
            "family": info.get("businessArea"),
            "identifier": None,
            "title": title,
            "confidentiality": info.get("confidentiality"),
            "availability": info.get("availability"),
            "integrity": info.get("integrity"),
            "description": "Imported from CSAM",
        }
        if new_type.get("title") not in unique_missing:
            missing_info_types.append(new_type)
            unique_missing = {x["title"] for x in missing_info_types}

    # Write out the file

    if len(missing_info_types) > 0:
        logger.warning(f"There were {len(missing_info_types)} info types not found in RegScale.")
        logger.warning("Creating file missing_info_types.json.  Load this via the RegScale API to add these.")
        file_name = Path("missing_info_types.json")
        save_to_json(file=file_name, data=missing_info_types, output_log=True)
