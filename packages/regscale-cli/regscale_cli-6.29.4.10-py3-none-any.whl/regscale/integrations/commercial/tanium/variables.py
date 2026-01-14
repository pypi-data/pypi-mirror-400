#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tanium Variables for RegScale CLI configuration.

This module defines configuration variables for the Tanium integration,
following the RegScale variable pattern using RsVariablesMeta metaclass.
"""

from regscale.core.app.utils.variables import RsVariableType, RsVariablesMeta


class TaniumVariables(metaclass=RsVariablesMeta):
    """
    Tanium configuration variables.

    These variables are read from the RegScale init.yaml configuration file
    or from environment variables. They control the Tanium API integration.

    Attributes:
        taniumEnabled: Enable/disable the Tanium integration
        taniumUrl: Base URL of the Tanium server
        taniumToken: API token for Tanium authentication
        taniumTimeout: Request timeout in seconds
        taniumVerifySsl: Whether to verify SSL certificates
        taniumProtocols: Allowed protocols (comma-separated: https, http). Defaults to 'https' only.
    """

    # Enable/disable the integration
    taniumEnabled: RsVariableType(  # type: ignore # noqa: F722,F821
        bool,
        "True",
        required=False,
        default=False,
    )

    # Tanium server URL
    taniumUrl: RsVariableType(  # type: ignore # noqa: F722,F821
        str,
        "https://tanium.example.com",
        required=False,
    )

    # API token for authentication (session header)
    taniumToken: RsVariableType(  # type: ignore # noqa: F722,F821
        str,
        "token-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
        required=False,
        sensitive=True,
    )

    # Request timeout in seconds
    taniumTimeout: RsVariableType(  # type: ignore # noqa: F722,F821
        int,
        "30",
        required=False,
        default=30,
    )

    # SSL verification
    taniumVerifySsl: RsVariableType(  # type: ignore # noqa: F722,F821
        bool,
        "True",
        required=False,
        default=True,
    )

    # Allowed protocols for requests (comma-separated: https, http)
    taniumProtocols: RsVariableType(  # type: ignore # noqa: F722,F821
        str,
        "https",
        required=False,
        default="https",
    )
