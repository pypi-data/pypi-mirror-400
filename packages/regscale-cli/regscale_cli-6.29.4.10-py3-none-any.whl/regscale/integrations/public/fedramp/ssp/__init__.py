"""
FedRAMP SSP (System Security Plan) import module.

This module provides classes for importing FedRAMP SSP documents into RegScale,
including the main orchestrator and supporting parsers/handlers.
"""

from regscale.integrations.public.fedramp.ssp.importer import FedRAMPSSPImporter

__all__ = ["FedRAMPSSPImporter"]
