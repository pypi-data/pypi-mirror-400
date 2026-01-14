#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium data models for API responses and data transformation.
"""

from regscale.integrations.commercial.tanium.models.assets import TaniumEndpoint
from regscale.integrations.commercial.tanium.models.vulnerabilities import TaniumVulnerability
from regscale.integrations.commercial.tanium.models.compliance import TaniumComplianceFinding

__all__ = [
    "TaniumEndpoint",
    "TaniumVulnerability",
    "TaniumComplianceFinding",
]
