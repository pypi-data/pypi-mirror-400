#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from pathlib import Path
from typing import List, Optional
from rich.progress import track
from regscale.models.regscale_models import InterConnection, User
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.integrations.public.csam.csam_common import (
    retrieve_from_csam,
    retrieve_ssps_custom_form_map,
    CSAM_FIELD_NAME,
    SSP_BASIC_TAB,
)

logger = logging.getLogger("regscale")


def import_csam_interconnections(import_ids: Optional[List[int]] = None):
    """
    Import the interconnections from CSAM
    Into RegScale
    """
    # Get existing ssps by CSAM Id
    logger.info("Retrieving SSPs from RegScale...")
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    # Get a list of users and create a map to id
    logger.info("Building a map of existing users... ")
    users = User.get_all()
    user_map = {}
    for user in users:
        name = f"{user.lastName}, {user.firstName}"
        user_map[name] = user.id

    # Parse each SSP
    for index in track(
        range(len(plans)),
        description=f"Importing {len(plans)} interconnections...",
    ):
        regscale_ssp_id = plans[index]
        results = []
        system_id = ssp_map.get(regscale_ssp_id)

        results = retrieve_from_csam(
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/interconnections",
        )

        if not results:
            logger.debug(f"No interconnections found for CSAM id: {system_id}, RegScale id: {regscale_ssp_id}")
            continue

        update_interconnections(results=results, ssp=regscale_ssp_id, user_map=user_map)


def update_interconnections(results: list, ssp: int, user_map: dict):
    """
    Process each result from the csam call
    Create RegScale Interconnections

    :param results: list of interconnections from CSAM
    :param ssp: id of SSP
    :param user_map: map of existing users to ids
    """

    # Get existing interconnections
    existing = InterConnection.get_all_by_parent(parent_id=ssp, parent_module="securityplans")
    existing_map = {x.name: x.id for x in existing}

    # Parse csam results
    for result in results:
        # Skip inactive
        if not result.get("isActive"):
            continue

        match = existing_map.get(result.get("connectedSystemName"))
        if match:
            existing_int = InterConnection.get_object(object_id=match)

            # Update with new details
            existing_int.agreementDate = result.get("dateAdded")
            existing_int.expirationDate = result.get("expirartionDate") or "2030-12-31"
            existing_int.dataDirection = result.get("transferType")
            existing_int.connectionType = (
                "Virtual Private Network (VPN)"
                if result.get("transferMethod") == "VPN"
                else "Internet or Firewall Rule"
            )
            existing_int.description = result.get("description")

            existing_int.save()
        else:
            new_int = InterConnection(
                name=result.get("connectedSystemName")[:449],
                authorizationType="Interconnect Security Agreement (ISA)",
                categorization="Moderate",
                connectionType=(
                    "Virtual Private Network (VPN)"
                    if result.get("transferMethod") == "VPN"
                    else "Internet or Firewall Rule"
                ),
                interconnectOwnerId=user_map.get(result.get("primaryAuthorizingOfficial"))
                or RegScaleModel.get_user_id(),
                status="Approved",
                agreementDate=result.get("dateAdded"),
                expirationDate=result.get("expirartionDate") or "2030-12-31",
                aoId=user_map.get(result.get("primaryAuthorizingOfficial")) or RegScaleModel.get_user_id(),
                parentId=ssp,
                parentModule="securityplans",
                dataDirection=result.get("transferType"),
                description=result.get("description"),
                organization="external",
            )
            new_int.create()
