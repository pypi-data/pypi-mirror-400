#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Classification Types in the application"""

from typing import Optional, Union

from pydantic import ConfigDict
from regscale.models.regscale_models.regscale_model import RegScaleModel


class ClassificationType(RegScaleModel):
    _module_slug = "classificationTypes"

    id: Optional[int] = None
    family: Optional[str] = None
    identifier: Optional[str] = None
    title: str
    confidentiality: str = "Low"
    availability: str = "Low"
    integrity: str = "Low"
    description: Optional[str]

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Components model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            list="/api/{model_slug}",
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
            export="/api/{model_slug}/export",
            group_by_family="/api/{model_slug}/groupByFamily",
        )

    @staticmethod
    def get_infotypes_map() -> dict:
        info_list = ClassificationType.get_list()
        info_list_map = {}

        if not len(info_list):
            return info_list

        for item in info_list:
            info_list_map[item.title] = item.id
        return info_list_map
